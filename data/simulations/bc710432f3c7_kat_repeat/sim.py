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
    
    # Design parameters derived from the protocol description
    n_snps = 10000
    n_causal = 500
    
    # Effect sizes from protocol
    effect_g_m = 0.5
    effect_m_c = 0.8
    effect_m_h = 0.8
    effect_g_direct = 0.1
    
    # 1. Generate G (Genotypes): N x n_snps matrix of standard normals
    G = rng.normal(0, 1, size=(N, n_snps))
    
    # 2. Generate M (Microbiome): Influenced by first n_causal SNPs
    # M = sum(G_causal * effect_g_m) + noise_m
    # We need to scale noise to maintain signal strength relative to protocol assumptions
    # Protocol implies strong mediation. Let's construct M directly.
    G_causal = G[:, :n_causal]
    signal_m = np.sum(G_causal * effect_g_m, axis=1)
    # Scale noise to achieve reasonable variance properties, protocol says noise param is global
    # We interpret 'noise' as a multiplier for the residual variance of the outcomes C and H
    # to test sensitivity. The structural noise for M is kept constant to preserve the mechanism.
    noise_m = rng.normal(0, 1, size=N) 
    M = signal_m + noise_m
    
    # 3. Generate C (Cognition) and H (Health)
    # C = M * effect_m_c + G_direct * effect_g_direct + noise_c
    # H = M * effect_m_h + G_direct * effect_g_direct + noise_h
    
    # Direct effect from the same causal SNPs
    signal_direct_c = np.sum(G_causal * effect_g_direct, axis=1)
    signal_direct_h = np.sum(G_causal * effect_g_direct, axis=1)
    
    # Outcome noise scaled by the input 'noise' parameter
    noise_c = rng.normal(0, 1, size=N) * noise
    noise_h = rng.normal(0, 1, size=N) * noise
    
    C = (M * effect_m_c) + signal_direct_c + noise_c
    H = (M * effect_m_h) + signal_direct_h + noise_h
    
    # Standardize variables for correlation interpretation
    C = (C - np.mean(C)) / np.std(C)
    H = (H - np.mean(H)) / np.std(H)
    M = (M - np.mean(M)) / np.std(M)
    
    # Create a genetic score (G_score) based on the causal SNPs to represent genetic liability
    # This simplifies the "genetic correlation" estimation to a regression problem as per protocol
    # "regression coefficient of G-score on C predicting H"
    G_score = np.sum(G_causal, axis=1)
    G_score = (G_score - np.mean(G_score)) / np.std(G_score)
    
    # Step 2: Raw association (Genetic correlation proxy)
    # Regress H on G_score and C? Protocol says: "regression coefficient of G-score on C predicting H"
    # This phrasing is slightly ambiguous. It likely means: 
    # Model 1: H ~ G_score (Raw genetic effect on Health)
    # OR Model 1: H ~ C (Phenotypic correlation driven by genetics)
    # Given "genetic correlation between cognition and health", we usually look at the correlation 
    # induced by G. 
    # Let's follow the specific instruction: "Adjusting for the microbiome mediator... reduce estimated genetic correlation".
    # We will estimate the effect of the Genetic Score on Health, which is confounded/mediated by Cognition/Microbiome?
    # Actually, the protocol says: "correlation between cognition and health".
    # Let's estimate the correlation between C and H that is attributable to G.
    # Simplest interpretation consistent with "adjusting for M":
    # Model A: H ~ C (Total association). But this includes environmental noise.
    # Model B: H ~ G_score (Direct genetic effect on H).
    # The protocol mentions: "regression coefficient of G-score on C predicting H". 
    # This sounds like a path: G -> C -> H? No, G -> M -> C and G -> M -> H.
    # Let's calculate the coefficient of G_score in predicting H (Raw).
    # Then calculate the coefficient of G_score in predicting H adjusting for M (Adjusted).
    # Wait, the prediction says: "reduce ... correlation between cognition and health".
    # So the metric is the correlation between C and H.
    # Raw: Corr(C, H). Adjusted: Partial Corr(C, H | M).
    # Let's stick to the text: "Metric: The difference in the correlation coefficient (Raw - Adjusted)".
    # Raw = Pearson(C, H). Adjusted = Partial(C, H | M).
    
    # Raw Correlation
    r_raw, _ = stats.pearsonr(C, H)
    
    # Adjusted (Partial Correlation controlling for M)
    # Residualize C on M
    slope_cm, _, _, _, _ = stats.linregress(M, C)
    C_resid = C - (slope_cm * M)
    
    # Residualize H on M
    slope_hm, _, _, _, _ = stats.linregress(M, H)
    H_resid = H - (slope_hm * M)
    
    r_adj, _ = stats.pearsonr(C_resid, H_resid)
    
    # Metric: Change in correlation
    estimate = r_raw - r_adj
    
    # Significance test: Is the adjusted correlation significantly different from 0?
    # Or is the *change* significant? The falsification says "correlation remains ~0.3".
    # So we test if r_adj is significant (i.e., if the mediation was incomplete).
    # Using t-test for partial correlation significance: t = r * sqrt((n-2-k)/(1-r^2))
    # k = number of controls = 1 (M)
    df = N - 2 - 1
    if abs(r_adj) >= 1.0:
        p_val = 0.0
    else:
        t_stat = r_adj * np.sqrt(df / (1 - r_adj**2))
        p_val = 2 * stats.t.sf(np.abs(t_stat), df)
    
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
val_mean = float(np.mean(values))
p_median = float(np.median(p_values))

# 95% CI over replication estimates
ci_low = float(np.percentile(values, 2.5))
ci_high = float(np.percentile(values, 97.5))

sig_share = sum(1 for p in p_values if p < ALPHA) / len(p_values)
# Direction share: expecting positive change (reduction)
dir_share = sum(1 for v in values if v > 0) / len(values)

result = {
    "n": N,
    "metric": "Change in genetic correlation coefficient (beta_raw - beta_adjusted)",
    "test": "Linear regression with and without covariate adjustment; significance tested via t-test on the residual correlation.",
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