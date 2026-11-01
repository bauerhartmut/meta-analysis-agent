import json
import numpy as np
from scipy import stats
import sim_params as P

N = P.N
EFFECT = P.EFFECT
NOISE = P.NOISE
ALPHA = P.ALPHA
SEED = P.SEED
REPLICATIONS = P.REPLICATIONS

# Constants for the simulation design based on the protocol
N_VARIANTS = 100
BETA_BASE = 0.1  # Base instrument strength
LAMBDA_DECAY = 0.02  # Decay rate
AGE_YOUNG = 20
AGE_OLD = 60

def get_instrument_strength(age):
    """Calculate instrument strength based on temporal decay model."""
    return BETA_BASE * np.exp(-LAMBDA_DECAY * age)

def run(seed, noise):
    rng = np.random.default_rng(seed)
    
    # Generate genetic variants (G) for N individuals
    # Assuming additive model, G ~ Binomial(2, 0.5) standardized
    G = rng.binomial(2, 0.5, size=(N, N_VARIANTS)).astype(float)
    G = (G - G.mean(axis=0)) / G.std(axis=0)
    
    # Calculate effective instrument strengths for the two scenarios
    # Scenario A: Young Exposure (Strong instruments) -> Outcome at Old
    beta_x_young = get_instrument_strength(AGE_YOUNG)
    # Scenario B: Old Exposure (Weak instruments due to decay) -> Outcome at Old
    beta_x_old = get_instrument_strength(AGE_OLD)
    
    # True causal effect
    beta_y = EFFECT
    
    # --- Scenario 1: Young Exposure (Aligned: Exp@20, Out@60) ---
    # X_young = G * beta_x_young + noise_x
    noise_x_young = rng.normal(0, noise, size=(N, N_VARIANTS))
    # We simulate summary statistics by regressing X on G and Y on G individually
    # But for IVW MR, we need beta_XG and beta_YG for each variant.
    
    # Generate Phenotypes
    # X_young (per variant contribution is handled in GWAS step)
    # To simplify for summary stat simulation:
    # G_j -> X_j with strength beta_x
    # X_total -> Y with strength EFFECT
    
    # Let's generate individual level data for X and Y to compute GWAS betas accurately
    # X is a sum of genetic effects + noise. 
    # However, the protocol implies the *measurement* of X decays, or the genetic effect on X decays.
    # "Instrument strength (beta_X) is modeled with a 'temporal decay factor'"
    # So X_young = Sum(G_j * beta_x_young_j) + Error? 
    # The protocol says "100 independent genetic variants". Let's assume equal base strength.
    
    # Construct X and Y for Young Exposure Scenario
    # X_young = G @ (beta_x_young * ones) + noise
    # Actually, usually beta_X varies per SNP. Let's assume fixed base strength for simplicity or random.
    # Protocol: "beta_X(age) = beta_base * exp(-lambda * age)". Implies uniform decay.
    
    weights_young = np.full(N_VARIANTS, beta_x_young)
    weights_old = np.full(N_VARIANTS, beta_x_old)
    
    # Generate X for Young Scenario
    X_young = G @ weights_young + rng.normal(0, noise, size=N)
    # Generate X for Old Scenario (Same G, different measurement/decay)
    X_old = G @ weights_old + rng.normal(0, noise, size=N)
    
    # Generate Y (always at age 60, caused by the underlying exposure)
    # The causal effect is on the exposure. If exposure is measured poorly (old), 
    # does it affect Y? The claim is "decay of early-life exposure variants".
    # This implies the biological driver is the early life exposure, but we measure it late.
    # Or the genetic effect on the phenotype X decays.
    # "True causal effect of Exposure (X) on Outcome (Y) is fixed at 0.05 SD"
    # If X is the mediator, Y = X_true * EFFECT + noise.
    # If the genetic effect on X decays, then X_old is a weaker proxy for the causal pathway?
    # Let's assume Y is caused by the "true" exposure which correlates with G via the young strength?
    # No, standard MR: G -> X -> Y.
    # If G->X decays, then the observed X_old has less variance explained by G.
    # But Y is caused by X. Which X? The current X? Or the accumulated X?
    # Protocol: "dilutes instrumental variable strength... leading to underestimation".
    # This suggests: G -> X_old (weak), X_old -> Y (causal). 
    # If we use G to predict X_old, the ratio beta_YG / beta_XG should still be EFFECT if no pleiotropy.
    # UNLESS the "decay" implies the causal pathway itself is obscured or the measurement error in X_old
    # attenuates the GWAS beta_X, but beta_Y (G->Y) also drops proportionally?
    # Wait, the claim is "underestimation ... compared to longitudinal designs".
    # In Two-Sample MR: Estimate = Sum(beta_YG * beta_XG) / Sum(beta_XG^2) (IVW slope).
    # If both betas drop proportionally, the ratio is constant.
    # The claim relies on "Temporal misalignment".
    # Hypothesis: G affects X strongly at young age. X(young) causes Y(old).
    # If we measure X at old age, the G->X(old) link is weak (decay).
    # But G->Y(old) link remains strong because it was mediated by X(young).
    # Therefore:
    # beta_XG (measured old) is small.
    # beta_YG (measured old) is large (reflecting X(young) effect).
    # Ratio beta_YG / beta_XG becomes HUGE? 
    # Or does the claim say "underestimation"?
    # "dilutes instrumental variable strength ... leading to underestimation"
    # Maybe the noise in X_old (due to decay of signal) increases variance, biasing towards null?
    # Or perhaps the "decay" means the genetic effect literally disappears, so G no longer predicts X_old,
    # but if Y was caused by X_young, G still predicts Y.
    # If G predicts Y (via X_young) but does NOT predict X_old (due to decay), then the MR estimate (beta_Y/beta_X)
    # would be inflated, not underestimated.
    
    # Let's re-read carefully: "underestimation of causal effects compared to longitudinal designs aligning young exposure with old outcome."
    # Maybe the "Cross-sectional" design (Exp@60, Out@60) yields underestimation?
    # If X_old is the only thing causing Y_old (i.e. current exposure matters, not past), then:
    # G -> X_old (weak). X_old -> Y_old (EFFECT).
    # Then beta_YG = beta_XG * EFFECT. Ratio is EFFECT. No bias.
    
    # Alternative interpretation: The "decay" introduces measurement error.
    # X_observed = X_true + error. As signal decays, error dominates.
    # Weak instrument bias in finite samples tends towards the confounded observational estimate (often 0 in sims).
    # With weak instruments (Old Exposure), the IV estimate is biased towards 0 (underestimation).
    # With strong instruments (Young Exposure), the IV estimate is consistent.
    # This fits "underestimation".
    
    # Simulation Plan:
    # 1. Generate G.
    # 2. Generate X_true (driven by G with strong effect).
    # 3. Generate Y (driven by X_true with EFFECT).
    # 4. Scenario Young: Measure X ~ X_true (high correlation). GWAS(X) strong, GWAS(Y) strong. Ratio ~ EFFECT.
    # 5. Scenario Old: Measure X_obs = X_true * decay_factor + noise_inflation? 
    #    Or simply: The genetic effect size on the measured phenotype is smaller.
    #    If we simulate summary stats:
    #    beta_XG_young = large. beta_YG_young = large * EFFECT. Ratio = EFFECT.
    #    beta_XG_old = small (due to decay). beta_YG_old = small * EFFECT? 
    #    If beta_YG also scales down, ratio is same.
    #    BUT, if Y is caused by the *cumulative* or *early* exposure, then beta_YG reflects the strong early link.
    #    While beta_XG (measured late) reflects the weak late link.
    #    Then Ratio = (Strong * EFFECT) / Weak = OVERESTIMATION.
    
    # Let's stick to the "Weak Instrument Bias" interpretation which leads to underestimation in finite samples
    # or if the "decay" implies the relevance of the instrument is lost relative to noise.
    # Actually, let's look at the "Falsification": "estimates remain constant or decrease when restricting... to younger cohorts".
    # Prediction: Young > Old. (Young is closer to true 0.05, Old is underestimated < 0.05).
    # This implies Old scenario yields small estimates.
    # How? If G->X is weak, and we do IVW, the estimate is noisy and biased to null in finite sample?
    # Or maybe the "decay" means the causal effect itself is diluted in the cross-sectional snapshot?
    
    # Let's implement the specific mechanism: