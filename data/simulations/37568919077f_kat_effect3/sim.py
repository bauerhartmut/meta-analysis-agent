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
LAMBDA_DECAY = 0.02  # Decay rate per year
AGE_YOUNG = 20
AGE_OLD = 60
TRUE_EFFECT = EFFECT

def run(seed, noise):
    rng = np.random.default_rng(seed)
    
    # Generate base instrument strengths (beta_base) for 100 variants
    # Assuming small effects, drawn from a normal distribution
    beta_base = rng.normal(0.05, 0.01, N_VARIANTS)
    
    # Calculate decay factors
    decay_young = np.exp(-LAMBDA_DECAY * AGE_YOUNG)
    decay_old = np.exp(-LAMBDA_DECAY * AGE_OLD)
    
    # Scenario 1: Young Exposure (Strong Instruments) -> Old Outcome
    # Instrument strength: beta_X_young = beta_base * decay_young
    beta_X_young = beta_base * decay_young
    # Outcome association: beta_Y = beta_X * TRUE_EFFECT + noise_instrument
    # In a perfect IV scenario without horizontal pleiotropy, beta_Y = beta_X * TRUE_EFFECT
    # We add sampling noise to the summary statistics based on 'noise' parameter and N
    se_beta = noise / np.sqrt(N)
    
    # Simulate GWAS summary statistics for Young Exposure
    # True signal
    true_beta_Y_young = beta_X_young * TRUE_EFFECT
    # Observed with noise
    hat_beta_X_young = beta_X_young + rng.normal(0, se_beta, N_VARIANTS)
    hat_beta_Y_young = true_beta_Y_young + rng.normal(0, se_beta, N_VARIANTS)
    
    # Scenario 2: Old Exposure (Weak Instruments due to decay) -> Old Outcome
    # Instrument strength: beta_X_old = beta_base * decay_old
    beta_X_old = beta_base * decay_old
    true_beta_Y_old = beta_X_old * TRUE_EFFECT
    
    # Observed with noise
    hat_beta_X_old = beta_X_old + rng.normal(0, se_beta, N_VARIANTS)
    hat_beta_Y_old = true_beta_Y_old + rng.normal(0, se_beta, N_VARIANTS)
    
    # Perform Two-Sample MR (Inverse Variance Weighted)
    # IVW estimate = sum(w_i * beta_Y_i) / sum(w_i), where w_i = 1/se_X_i^2
    # For simplicity in this simulation, we assume equal SE for X in both groups for weighting
    # or use the standard ratio estimate averaged. 
    # Standard IVW: regressing beta_Y on beta_X with intercept 0, weights 1/se_X^2.
    # Since se_X is constant in our simulation setup (approx), simple ratio mean or weighted mean works.
    # Let's use the standard IVW formula: sum(beta_X * beta_Y / var_X) / sum(beta_X^2 / var_X)
    # Here var_X is the squared standard error of the exposure estimate.
    var_X = se_beta**2
    
    # MR Estimate Young
    weights_young = 1.0 / var_X
    mr_est_young = np.sum(weights_young * hat_beta_X_young * hat_beta_Y_young) / np.sum(weights_young * hat_beta_X_young**2)
    
    # MR Estimate Old
    weights_old = 1.0 / var_X
    mr_est_old = np.sum(weights_old * hat_beta_X_old * hat_beta_Y_old) / np.sum(weights_old * hat_beta_X_old**2)
    
    # The metric defined in the protocol is the difference: Young - Old
    # Prediction: Young should be closer to true effect (less biased by weak instrument bias towards null)
    # Actually, weak instruments bias towards the null (0). So Old estimate should be smaller than Young.
    # Difference = Young - Old should be positive if the hypothesis holds.
    estimate = mr_est_young - mr_est_old
    
    # Statistical Test: 
    # The prompt asks for a t-test comparing distributions. 
    # Since we only have one aggregate estimate per replication in this function, 
    # we interpret the "test" as testing if the difference is significantly > 0 
    # using the variability of the variants as the sample distribution for this single run's internal test?
    # No, the outer loop handles replications. 
    # Inside `run`, we must return a single estimate and a p-value.
    # The protocol says: "One-sample t-test comparing the distribution of MR estimates from the 'Young Exposure' condition against the 'Old Exposure' condition across replications".
    # This implies the t-test happens AFTER the replications are collected.
    # However, the skeleton requires `run` to return `estimate` and `p`.
    # In the context of a single replication returning a p-value, we usually perform a test on the variants within that replication
    # to see if the difference in estimates derived from subsets of variants is significant, OR
    # we treat the `estimate` as the difference of means and calculate a p-value based on the variance of the ratio estimates across the 100 variants.
    
    # Let's calculate the per-variant ratio estimates (Wald ratios)
    # Avoid division by zero
    mask_young = np.abs(hat_beta_X_young) > 1e-9
    ratios_young = np.zeros(N_VARIANTS)
    ratios_young[mask_young] = hat_beta_Y_young[mask_young] / hat_beta_X_young[mask_young]
    
    mask_old = np.abs(hat_beta_X_old) > 1e-9
    ratios_old = np.zeros(N_VARIANTS)
    ratios_old[mask_old] = hat_beta_Y_old[mask_old] / hat_beta_X_old[mask_old]
    
    # We want to test if the mean of ratios_young is greater than mean of ratios_old.
    # Paired t-test on the variants? Or independent? They share the same beta_base but different noise.
    # Independent t-test on the set of ratio estimates from the 100 variants.
    t_stat, p_val = stats.ttest_ind(ratios_young, ratios_old, alternative='greater')
    
    return estimate, float(p_val)

values, p_values = [], []
for i in range(REPLICATIONS):
    v, p = run(SEED + i, NOISE)
    values.append(v)
    p_values.append(p)

sensitivity = []
for mult in (0.5, 2.0):
    v, p = run(SEED, NOISE * mult)
    sensitivity.append({'noise_multiplier': mult, 'value': v, 'p_value': p})

# Calculate summary statistics
value_mean = float(np.mean(values))
p_value_median = float(np.median(p_values))

# 95% CI over replication estimates
ci_low = float(np.percentile(values, 2.5))
ci_high = float(np.percentile(values, 97.5))

significant_share = float(np.mean([1 if p < ALPHA else 0 for p in p_values]))
# Direction share: fraction where estimate > 0 (predicted direction: Young > Old)
direction_share = float(np.mean([1 if v > 0 else 0 for v in values]))

result = {
    "n": N,
    "metric": "Difference in MR point estimates (Young - Old)",
    "test": "Independent t-test on variant ratio estimates per replication",
    "alpha": ALPHA,
    "seed": SEED,
    "replications": REPLICATIONS,
    "value": value_mean,
    "ci_low": ci_low,
    "ci_high": ci_high,
    "p_value": p_value_median,
    "values": values,
    "p_values": p_values,
    "significant_share": significant_share,
    "direction_share": direction_share,
    "sensitivity": sensitivity
}

print(json.dumps(result))