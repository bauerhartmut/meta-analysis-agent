import json
import numpy as np
from scipy import stats
from scipy.optimize import minimize
import sim_params as P

N = P.N
EFFECT = P.EFFECT
NOISE = P.NOISE
ALPHA = P.ALPHA
SEED = P.SEED
REPLICATIONS = P.REPLICATIONS

def run(seed, noise):
    rng = np.random.default_rng(seed)
    
    # Generate latent cognitive score C ~ N(0, 1)
    C = rng.normal(0, 1, N)
    
    # Generate genetic variants G ~ N(0, 1)
    G = rng.normal(0, 1, N)
    
    # Determine threshold at 75th percentile of C
    threshold = np.percentile(C, 75)
    
    # Pleiotropic effect: ZERO if C > threshold, NON-ZERO (linear slope = EFFECT) if C <= threshold
    pleiotropy = np.where(C <= threshold, EFFECT * G, 0.0)
    
    # Outcome Y: null direct causal effect of G on Y, only pleiotropy + noise
    # Y = pleiotropy + noise_term
    noise_term = rng.normal(0, noise, N)
    Y = pleiotropy + noise_term
    
    # (a) Calculate overall genetic correlation between G and Y
    corr, _ = stats.pearsonr(G, Y)
    
    # (b) Stratified regression in top/bottom quartiles of C
    q25 = np.percentile(C, 25)
    q75 = np.percentile(C, 75)
    
    # Bottom quartile: C <= q25
    mask_bottom = C <= q25
    G_bottom = G[mask_bottom]
    Y_bottom = Y[mask_bottom]
    
    if len(G_bottom) > 2:
        slope_bottom, _, _, _, _ = stats.linregress(G_bottom, Y_bottom)
    else:
        slope_bottom = 0.0
        
    # Top quartile: C >= q75
    mask_top = C >= q75
    G_top = G[mask_top]
    Y_top = Y[mask_top]
    
    if len(G_top) > 2:
        slope_top, _, _, _, _ = stats.linregress(G_top, Y_top)
    else:
        slope_top = 0.0
        
    # Stratified Effect Size Difference (Bottom Quartile - Top Quartile)
    strat_diff = slope_bottom - slope_top
    
    # (c) Fit linear vs. fractional polynomial models to G-Y relationship conditional on C
    # We compare AIC of linear model vs a model that includes the threshold interaction
    # Linear model: Y ~ G
    # Non-linear (threshold) model: Y ~ G * I(C <= threshold)
    
    # Linear model residuals
    slope_lin, intercept_lin, _, _, _ = stats.linregress(G, Y)
    Y_pred_lin = intercept_lin + slope_lin * G
    rss_lin = np.sum((Y - Y_pred_lin) ** 2)
    k_lin = 2  # intercept, slope
    aic_lin = N * np.log(rss_lin / N) + 2 * k_lin
    
    # Non-linear model: Y = beta0 + beta1 * G * I(C <= threshold) + error
    # This is equivalent to fitting separate intercepts/slopes but we force 0 effect above threshold for G
    # Actually, let's fit: Y = b0 + b1 * (G * mask) + error
    mask = (C <= threshold).astype(float)
    X = G * mask
    
    # Simple regression for the non-linear term
    # We need to handle the case where X might be all zeros (unlikely with continuous C)
    if np.std(X) > 1e-9:
        slope_nl, intercept_nl, _, _, _ = stats.linregress(X, Y)
        Y_pred_nl = intercept_nl + slope_nl * X
        rss_nl = np.sum((Y - Y_pred_nl) ** 2)
        k_nl = 2
        aic_nl = N * np.log(rss_nl / N) + 2 * k_nl
    else:
        aic_nl = aic_lin # Fallback if no variation in mask
        
    # Metric: Difference in AIC (Linear - Non-linear)
    # Positive value means Non-linear is better (lower AIC)
    aic_diff = aic_lin - aic_nl
    
    # Combined metric: Weighted sum or just the AIC diff as primary indicator of non-linearity
    # The prompt asks for "Difference in AIC ... and Stratified Effect Size Difference"
    # We will return the AIC difference as the primary 'value' for the study metric
    # as it directly tests the "better fit by non-linear models" prediction.
    estimate = aic_diff
    
    # Test statistic: Likelihood Ratio Test approximation or just using the AIC diff significance
    # Since we need a p-value, let's perform a formal test for the interaction term
    # Model 1 (Null): Y ~ G
    # Model 2 (Alt): Y ~ G + G*I(C<=thresh)
    
    # Design matrix for Null
    X_null = np.vstack([np.ones(N), G]).T
    # Design matrix for Alt
    X_alt = np.vstack([np.ones(N), G, X]).T
    
    # Fit Null
    beta_null, _, _, _ = np.linalg.lstsq(X_null, Y, rcond=None)
    rss_null = np.sum((Y - X_null @ beta_null) ** 2)
    
    # Fit Alt
    beta_alt, _, _, _ = np.linalg.lstsq(X_alt, Y, rcond=None)
    rss_alt = np.sum((Y - X_alt @ beta_alt) ** 2)
    
    # LRT statistic
    if rss_alt > 0:
        lr_stat = N * np.log(rss_null / rss_alt)
        # Degrees of freedom = 1 (one extra parameter)
        p_value = 1 - stats.chi2.cdf(lr_stat, 1)
    else:
        p_value = 1.0
        
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
value_mean = float(np.mean(values))
p_value_median = float(np.median(p_values))

# 95% CI over replication estimates
ci_low = float(np.percentile(values, 2.5))
ci_high = float(np.percentile(values, 97.5))

significant_share = float(np.mean([1 if p < ALPHA else 0 for p in p_values]))
# Direction share: prediction is non-linear fit is better, so AIC_diff > 0
direction_share = float(np.mean([1 if v > 0 else 0 for v in values]))

result = {
    "n": N,
    "metric": "AIC_diff",
    "test": "LRT",
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