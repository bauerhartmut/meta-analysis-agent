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

# Read sensitivity grid from sim_params if available, otherwise default to protocol standard
if hasattr(P, 'GRID') and P.GRID:
    SENSITIVITY_MULTIPLIERS = P.GRID
else:
    SENSITIVITY_MULTIPLIERS = [0.5, 2.0]

def run_study(seed, noise_scale):
    """
    Simulates the full study design:
    1. Generate data with context-dependent penetrance (Effect in Low-SES, Null in High-SES).
    2. Run Pooled, Stratified (Low/High), and Interaction models.
    3. Returns the primary metric (Low-SES effect estimate and p-value) for aggregation,
       plus internal checks for the falsification condition.
    """
    rng = np.random.default_rng(seed)
    
    # 1. Generate Data
    # G: Standardized genetic instrument
    G = rng.standard_normal(N)
    
    # E: Binary environmental moderator (0=High SES, 1=Low SES), 50% split
    E = rng.integers(0, 2, size=N)
    
    # Y: Outcome
    # True effect: EFFECT in Low-SES (E=1), 0.0 in High-SES (E=0)
    # Model: Y = (EFFECT * G * E) + Noise
    true_effect_vector = EFFECT * E * G
    noise = rng.standard_normal(N) * noise_scale
    Y = true_effect_vector + noise
    
    # Prepare design matrices
    # Interaction term
    GxE = G * E
    
    # --- Model A: Pooled OLS (Y ~ G) ---
    # We expect this to be non-significant due to dilution
    slope_pooled, intercept_pooled, r_pooled, p_pooled, std_err_pooled = stats.linregress(G, Y)
    
    # --- Model B: Stratified Analysis ---
    # Low SES (E=1)
    mask_low = (E == 1)
    if np.sum(mask_low) > 2:
        slope_low, _, _, p_low, _ = stats.linregress(G[mask_low], Y[mask_low])
    else:
        slope_low, p_low = 0.0, 1.0
        
    # High SES (E=0)
    mask_high = (E == 0)
    if np.sum(mask_high) > 2:
        slope_high, _, _, p_high, _ = stats.linregress(G[mask_high], Y[mask_high])
    else:
        slope_high, p_high = 0.0, 1.0
        
    # --- Model C: Interaction Model (Y ~ G + E + G*E) ---
    # Using OLS via scipy.linalg or manual calculation for full control, 
    # but stats.ols is not direct. We use matrix algebra for the interaction test.
    # Design matrix X: [1, G, E, GxE]
    X = np.column_stack((np.ones(N), G, E, GxE))
    try:
        # Solve normal equations: (X'X)^-1 X'Y
        coeffs, residuals, rank, s = np.linalg.lstsq(X, Y, rcond=None)
        # Coeffs: [intercept, beta_G, beta_E, beta_GxE]
        beta_gxe = coeffs[3]
        
        # Calculate standard error for beta_GxE
        # Var(beta) = sigma^2 * (X'X)^-1
        if rank == X.shape[1]:
            XtX_inv = np.linalg.inv(X.T @ X)
            mse = np.sum((Y - X @ coeffs)**2) / (N - rank)
            se_gxe = np.sqrt(mse * XtX_inv[3, 3])
            t_stat_gxe = beta_gxe / se_gxe
            p_interaction = 2 * (1 - stats.t.cdf(np.abs(t_stat_gxe), N - rank))
        else:
            p_interaction = 1.0
    except np.linalg.LinAlgError:
        p_interaction = 1.0
        beta_gxe = 0.0

    # Falsification Check (Internal Logic)
    # Hypothesis holds if: Pooled NS, Low Sig, High NS, Interaction Sig.
    # Falsified if: Effects identical (Low ~ High) OR Interaction NS.
    is_falsified = False
    if p_interaction >= ALPHA:
        is_falsified = True
    if abs(slope_low - slope_high) < 0.01: # Approximate equality check
        is_falsified = True
        
    # The protocol asks to report the "value" and "p_value" for the aggregation.
    # Based on the claim "stratifying by SES reveals the effect in low-SES groups",
    # the primary metric for the replication loop is the Low-SES effect.
    return slope_low, p_low

# Run Replications
values = []
p_values = []

for i in range(REPLICATIONS):
    # Each replication uses seed + i
    v, p = run_study(SEED + i, NOISE)
    values.append(v)
    p_values.append(p)

# Sensitivity Analysis
sensitivity = []
for mult in SENSITIVITY_MULTIPLIERS:
    # Sensitivity runs use the base seed (or seed + 0) with modified noise
    v, p = run_study(SEED, NOISE * mult)
    sensitivity.append({
        "noise_multiplier": mult,
        "value": v,
        "p_value": p
    })

# Aggregation Statistics
mean_value = float(np.mean(values))
median_p = float(np.median(p_values))

# 95% CI of the estimates (using percentile method)
ci_low = float(np.percentile(values, 2.5))
ci_high = float(np.percentile(values, 97.5))

significant_share = sum(1 for p in p_values if p < ALPHA) / len(p_values)
# Direction share: fraction where effect is positive (predicted sign)
direction_share = sum(1 for v in values if v > 0) / len(values)

# Construct Output
output = {
    "n": N,
    "metric": "Low-SES Effect Size",
    "test": "Stratified OLS with Interaction Check",
    "alpha": ALPHA,
    "seed": SEED,
    "replications": REPLICATIONS,
    "value": mean_value,
    "ci_low": ci_low,
    "ci_high": ci_high,
    "p_value": median_p,
    "values": values,
    "p_values": p_values,
    "significant_share": significant_share,
    "direction_share": direction_share,
    "sensitivity": sensitivity
}

print(json.dumps(output))