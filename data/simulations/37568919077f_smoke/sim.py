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

def run(seed, noise):
    rng = np.random.default_rng(seed)
    
    # Parameters for the simulation
    n_snps = 100
    n_samples = N
    true_effect = EFFECT
    lambda_decay = 0.02  # Decay rate
    
    # Generate SNP effects on Exposure (base strength)
    # Assume small effects for many SNPs
    beta_base = rng.normal(0, 0.1, n_snps)
    
    # Scenario 1: Old Exposure (Age 60) -> High decay
    age_old = 60
    decay_old = np.exp(-lambda_decay * age_old)
    beta_x_old = beta_base * decay_old
    
    # Scenario 2: Young Exposure (Age 20) -> Low decay
    age_young = 20
    decay_young = np.exp(-lambda_decay * age_young)
    beta_x_young = beta_base * decay_young
    
    # Generate Genotypes (0, 1, 2) for n_samples
    # Using a simple binomial approximation for MAF=0.5
    G = rng.binomial(2, 0.5, (n_samples, n_snps))
    
    # --- Simulate Old Exposure Scenario (Exp@60, Out@60) ---
    # X_old = G * beta_x_old + noise_x
    noise_x_old = rng.normal(0, noise, (n_samples, n_snps)) # Per-SNP noise component or total? 
    # Let's model total exposure noise
    # X = sum(G * beta) + epsilon
    # To keep variance stable, we scale noise. 
    # Simpler approach: Generate X directly based on genetic score + noise
    
    # Genetic Scores
    GS_old = G @ beta_x_old
    GS_young = G @ beta_x_young
    
    # Exposure Realizations
    # Scale noise to ensure reasonable F-statistics roughly
    # Var(GS) approx n_snps * 0.5 * var(beta)
    # We add noise such that heritability is low but detectable
    X_old = GS_old + rng.normal(0, noise, n_samples)
    X_young = GS_young + rng.normal(0, noise, n_samples)
    
    # Outcome (Always at Age 60, so depends on true causal effect of exposure)
    # Y = X * true_effect + noise_y
    # Note: The claim is about the *estimation* via MR using summary stats.
    # We simulate individual data then compute summary stats for IVW.
    
    Y_old = X_old * true_effect + rng.normal(0, noise, n_samples)
    Y_young = X_young * true_effect + rng.normal(0, noise, n_samples) # Same Y process, different X input? 
    # Actually, the protocol says: "Outcome Y is always sampled at age 60".
    # If the causal mechanism is X(60) -> Y(60), then for the Young Exposure scenario (Exp@20, Out@60),
    # we are testing if the instrument (Exp@20) predicts Y(60) via the causal path.
    # However, the simulation description says: "MR effect estimates will be significantly larger when using exposure data from younger cohorts... compared to ... same later age".
    # This implies we treat X_young as the exposure variable in the GWAS, and Y as the outcome.
    # But biologically, if X decays, X_young is a bad proxy for X_60 which causes Y.
    # WAIT: The hypothesis claims: "decay ... dilutes IV strength ... leading to underestimation".
    # So: 
    # Case A (Old/Aligned): Exp@60, Out@60. Instrument strength is LOW (decayed). Estimate should be biased/weak? 
    #   Actually, if X@60 causes Y@60, and we use G to instrument X@60, the strength is beta_x_old.
    # Case B (Young/Aligned?): The prompt says "Exposure data from younger cohorts ... and outcome data from older cohorts".
    #   This is Exp@20, Out@60.
    #   If the true causal effect is X(60)->Y(60), and X(20) is just a noisy/decayed version of the latent trait?
    #   Let's re-read carefully: "beta_X(age) = beta_base * exp(-lambda * age)".
    #   This implies the effect of the SNP on the measured exposure decreases with age.
    #   So G -> X@20 is STRONG. G -> X@60 is WEAK.
    #   True causal effect: X -> Y is 0.05.
    #   If we do MR with (G->X@20, G->Y@60): 
    #     We assume X@20 is the exposure. But does X@20 cause Y@60? 
    #     The prompt implies the "Temporal misalignment" causes the issue.
    #     Interpretation for simulation: 
    #     We want to show that using Strong Instruments (Young) gives a better/closer estimate than Weak Instruments (Old).
    #     Why would Old be worse? Weak instrument bias tends to bias towards the null (in finite samples) or increase variance.
    #     Or perhaps the "decay" means the relevance is lost, so the MR estimate becomes unstable or biased.
    #     Let's stick to the mechanical definition:
    #     1. Generate G.
    #     2. Generate X_young (strong G->X), X_old (weak G->X).
    #     3. Generate Y based on TRUE underlying exposure? 
    #        If the true model is X(60) -> Y(60), then:
    #        Y = X_old * EFFECT + noise.
    #        Now we run MR:
    #        Scenario 1 (Old): Instrument G, Exposure X_old, Outcome Y. (Strong relevance? No, G->X_old is weak).
    #        Scenario 2 (Young): Instrument G, Exposure X_young, Outcome Y. (Strong relevance G->X_young).
    #        But does X_young cause Y? Only if X_young correlates with X_old.
    #        Since both are generated from G + noise, they are correlated via G.
    #        IVW Estimate = Sum(G->Y * G->X) / Sum(G->X^2)? No, Sum(G->Y * G->X) / Sum(G->X^2) is for single SNP?
    #        IVW = Sum( (beta_Y_j / beta_X_j) * w_j ) / Sum(w_j) where w_j = 1/se^2.
    #        Simplified for simulation: 
    #        We calculate summary stats: beta_X_j (effect of SNP j on X), beta_Y_j (effect of SNP j on Y).
    #        Then IVW = sum(beta_Y_j * beta_X_j / var_j) / sum(beta_X_j^2 / var_j).
    #        Assuming equal variance/se for simplicity in this toy model: IVW ~ sum(beta_Y * beta_X) / sum(beta_X^2).
    
    # Let's compute summary statistics for each SNP
    # We need beta_X_old, beta_X_young, and beta_Y (effect of SNP on Y)
    # Y depends on X_old (since Y is at 60).
    # Y = X_old * EFFECT + e_y = (G*beta_x_old + e_x_old)*EFFECT + e_y
    # So true beta_Y_j = beta_x_old[j] * EFFECT.
    
    # Calculate observed betas from simulated data (regress X on G, Y on G for each SNP)
    # To save time, we can use the known generating parameters plus sampling noise?
    # No, must simulate data and estimate to get correct noise properties.
    
    def get_summary_stats(G, X, Y):
        n_snps = G.shape[1]
        beta_x = np.zeros(n_snps)
        beta_y = np.zeros(n_snps)
        se_x = np.zeros(n_snps)
        se_y = np.zeros(n_snps)
        
        for j in range(n_snps):
            g = G[:, j]
            if np.var(g) == 0: continue
            
            # Regress X on g
            slope_x, _, _, _, _ = stats.linregress(g, X)
            beta_x[j] = slope_x
            
            # Regress Y on g
            slope_y, _, _, _, _ = stats.linregress(g, Y)
            beta_y[j] = slope_y
            
        return beta_x, beta_y

    # Generate Y based on X_old (the biologically relevant exposure at age 60)
    Y = X_old * true_effect + rng.normal(0, noise, n_samples)
    
    # Scenario 1: Old Exposure (Exp@60, Out@60)
    # Instrument: G, Exposure: X_old, Outcome: Y
    bx_old, by_old = get_summary_stats(G, X_old, Y)
    
    # Scenario 2: Young Exposure (Exp@20, Out@60)
    # Instrument: G, Exposure: X_young, Outcome: Y (same Y as above)
    bx_young, by_young = get_summary_stats(G, X_young, Y)
    
    # Filter for valid SNPs (non-zero variance in G, handled by linregress but check div by zero)
    valid