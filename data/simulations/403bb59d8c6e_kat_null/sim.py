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

# Design parameters derived from the protocol description
N_SNPS_TOTAL = 1_000_000
N_SNPS_MHC = 10_000
N_SNPS_BG = N_SNPS_TOTAL - N_SNPS_MHC
H2 = 0.2  # Heritability per trait
SAMPLE_SIZE = 500_000  # Per trait

def run(seed, noise):
    rng = np.random.default_rng(seed)
    
    # 1. Simulate Background Effects (990k SNPs)
    # Correlation 0.05, small effects
    # We need to scale effects such that total rg becomes 0.3 when MHC is added.
    # For simplicity in this simulation, we generate standardized effect sizes.
    # The "noise" parameter from sim_params will scale the sampling error (Z-score noise).
    
    # Background covariance matrix
    cov_bg = [[1.0, 0.05], [0.05, 1.0]]
    bg_effects = rng.multivariate_normal([0, 0], cov_bg, size=N_SNPS_BG)
    
    # Scale background effects to be "small" relative to MHC
    # Let's assume background contributes very little to the total correlation initially
    bg_scale = 0.01
    bg_effects *= bg_scale
    
    # 2. Simulate MHC Hotspot Effects (10k SNPs)
    # Correlation 0.9, large effects
    cov_mhc = [[1.0, 0.9], [0.9, 1.0]]
    mhc_effects = rng.multivariate_normal([0, 0], cov_mhc, size=N_SNPS_MHC)
    
    # Scale MHC effects to be "large"
    mhc_scale = 0.5
    mhc_effects *= mhc_scale
    
    # Combine effects
    all_effects = np.vstack([bg_effects, mhc_effects])
    
    # Calculate true genetic correlation of the simulated architecture to verify setup
    # (Optional sanity check, not strictly needed for the output metric)
    
    # 3. Generate Z-scores with Sampling Noise
    # Z = beta / se + epsilon
    # se approx sqrt(1 / (N * h2 / M))? 
    # Simplified: Z ~ N(beta * sqrt(N), 1) if beta is standardized appropriately.
    # Here we treat 'noise' from sim_params as a multiplier on the standard error of the estimate.
    # Standard error of Z under null is 1. We add noise * N(0,1).
    
    # Effective signal strength factor
    signal_strength = np.sqrt(SAMPLE_SIZE) 
    
    z1 = (all_effects[:, 0] * signal_strength) + (rng.standard_normal(N_SNPS_TOTAL) * noise)
    z2 = (all_effects[:, 1] * signal_strength) + (rng.standard_normal(N_SNPS_TOTAL) * noise)
    
    # 4. Estimate Genetic Correlation (Method of Moments on Z-scores)
    # rg_est = sum(z1 * z2) / sqrt(sum(z1^2) * sum(z2^2)) ? 
    # Or simpler: correlation of z-scores across SNPs.
    # Given large N, correlation of Z scores approximates genetic correlation if noise is uncorrelated.
    
    # Full estimate
    rg_full = np.corrcoef(z1, z2)[0, 1]
    
    # Excluded estimate (remove last 10k SNPs which are the MHC hotspot in our construction)
    z1_excl = z1[:N_SNPS_BG]
    z2_excl = z2[:N_SNPS_BG]
    
    if np.std(z1_excl) == 0 or np.std(z2_excl) == 0:
        rg_excl = 0.0
    else:
        rg_excl = np.corrcoef(z1_excl, z2_excl)[0, 1]
    
    # The prediction metric is the estimated rg after excluding MHC.
    # The hypothesis claims this should drop below 0.1.
    estimate = rg_excl
    
    # Statistical Test:
    # We test if the excluded rg is significantly different from 0? 
    # Or test the difference? The protocol says "Success if rg_excluded < 0.1".
    # To get a p-value for the "falsification" context:
    # Null hypothesis: rg_excl >= 0.1 (Falsification holds)
    # Alternative: rg_excl < 0.1 (Prediction holds)
    # We can use a Fisher Z-transformation to test if rg_excl is significantly < 0.1.
    
    # Fisher Z transform
    def fisher_z(r):
        return 0.5 * np.log((1 + r) / (1 - r))
    
    def fisher_r(z):
        return (np.exp(2 * z) - 1) / (np.exp(2 * z) + 1)

    # Standard error of Fisher Z approx 1/sqrt(N_snps - 3)
    se_z = 1.0 / np.sqrt(N_SNPS_BG - 3)
    
    z_obs = fisher_z(rg_excl)
    z_null = fisher_z(0.1) # Testing against the threshold 0.1
    
    # One-sided test: is observed significantly less than 0.1?
    # Z_stat = (z_obs - z_null) / se_z
    z_stat = (z_obs - z_null) / se_z
    
    # P-value for H1: rg < 0.1 (left-tailed)
    p_value = stats.norm.cdf(z_stat)
    
    return estimate, float(p_value)

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
val_mean = float(np.mean(values))
p_median = float(np.median(p_values))

# 95% CI over replication estimates
ci_low = float(np.percentile(values, 2.5))
ci_high = float(np.percentile(values, 97.5))

sig_share = sum(1 for p in p_values if p < ALPHA) / len(p_values)
# Direction share: fraction where estimate < 0.1 (predicted direction)
dir_share = sum(1 for v in values if v < 0.1) / len(values)

result = {
    "n": N,
    "metric": "Genetic correlation (rg) estimated from z-scores (MHC excluded)",
    "test": "One-sided test of rg_excl < 0.1",
    "alpha": ALPHA,
    "seed": SEED,
    "replications": REPLICATIONS,
    "value": val_mean,
    "ci_low": ci_low,
    "ci_high": ci_high,
    "p_value": p_median,
    "values": values,
    "p_values": p_values,
    "significant_share": sig_share,
    "direction_share": dir_share,
    "sensitivity": sensitivity
}

print(json.dumps(result))