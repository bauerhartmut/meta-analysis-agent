import json
import numpy as np
from scipy import stats
import sim_params as P

ALT = 'greater' if P.COMPARISON == 'at_least' else 'less'

def run_mr_trial(rng, n_snps, n_sample, true_beta, noise_scale):
    """
    Simulate a single Two-Sample MR trial with heavy-tailed exposure architecture.
    Returns: (standard_reject, hc_reject, standard_est, hc_se)
    """
    # 1. Generate SNP effects on exposure (Heavy-tailed Pareto as per protocol)
    # Pareto alpha=1.5. Scale set to ensure variance heterogeneity.
    # We generate absolute values and random signs.
    alpha_pareto = 1.5
    # Generate Pareto distributed values (x_m = 1)
    pareto_vals = rng.pareto(alpha_pareto, n_snps)
    signs = rng.choice([-1, 1], n_snps)
    gamma = signs * pareto_vals
    
    # Normalize exposure effects to have a reasonable scale relative to noise
    # This prevents the total variance from exploding uncontrollably while keeping heavy tails
    gamma = gamma / np.std(gamma) * 0.1 
    
    # 2. Generate Summary Statistics
    # Two-sample design: Split sample or independent samples. 
    # Protocol says N=500,000 for both. We treat them as independent GWAS.
    
    # Exposure GWAS (N_exp = n_sample)
    # Z_exp ~ N(gamma * sqrt(N), 1) approx for standardized traits
    # Or more explicitly: beta_hat_exp = gamma + error
    se_exp = 1.0 / np.sqrt(n_sample)
    beta_hat_exp = gamma + rng.normal(0, se_exp, n_snps)
    
    # Outcome GWAS (N_out = n_sample)
    # True effect: beta_out = gamma * true_beta
    # beta_hat_out = gamma * true_beta + error
    se_out = 1.0 / np.sqrt(n_sample)
    beta_hat_out = gamma * true_beta + rng.normal(0, se_out, n_snps)
    
    # 3. IVW Estimation
    # We filter out weak instruments (optional but standard), here we use all as per simple protocol
    # Weights for standard IVW: w_i = 1 / Var(beta_out_i) approx 1 / (se_out^2) 
    # However, in ratio estimator context: Var(ratio) depends on exposure strength.
    # Standard IVW assumes homogeneity of variance in the ratio estimates relative to weights.
    # Weight w_i = 1 / se_out_i^2 (since se_out is constant here, weights are uniform)
    # But the protocol mentions "induced variance of the ratio estimator is heteroscedastic due to exposure's heavy tail".
    # The ratio estimator for SNP i is r_i = beta_hat_out_i / beta_hat_exp_i.
    # Its variance is approx (1/beta_hat_exp_i^2) * Var(beta_hat_out) + ...
    # So the true variance of the ratio depends heavily on gamma (via beta_hat_exp).
    
    ratios = beta_hat_out / beta_hat_exp
    
    # Standard IVW: Uses weights based on outcome SE only (ignoring exposure uncertainty/heteroscedasticity induced by gamma)
    # Since se_out is constant, standard IVW is effectively the unweighted mean of ratios (or weighted by constant)
    # Actually, standard IVW usually weights by 1/se_out^2. If se_out is constant, it's a simple mean.
    # Let's compute the standard IVW estimate and its naive SE.
    
    # Naive SE for IVW (assuming fixed exposure effects or ignoring their variance contribution to heteroscedasticity)
    # Var(beta_ivw) = 1 / sum(w_i) where w_i = 1/se_out^2
    w_naive = np.ones(n_snps) / (se_out ** 2)
    beta_ivw_std = np.sum(w_naive * ratios) / np.sum(w_naive)
    se_ivw_std = np.sqrt(1.0 / np.sum(w_naive))
    
    z_std = beta_ivw_std / se_ivw_std
    p_std = 2 * (1 - stats.norm.cdf(abs(z_std))) # Two-sided usually, but protocol implies detection
    # Protocol says "rejection (p<0.05)". Assuming two-sided test for effect != 0 unless specified.
    # However, power is often one-sided if direction is known. Let's stick to standard two-sided for robustness 
    # unless the "at_least/at_most" comparison implies direction. The metric is just "rejection".
    reject_std = p_std < P.ALPHA
    
    # HC-IVW: Heteroscedasticity-Consistent (HC3) standard errors
    # We treat the ratio estimates as observations with heteroscedastic errors.
    # Model: r_i = beta_true + epsilon_i
    # OLS estimate is the same (mean of ratios if weights uniform, or weighted mean)
    # Let's use the weighted mean from above as the point estimate (it's the efficient estimator under homoscedasticity)
    # But for HC SE, we calculate the sandwich estimator.
    
    # Residuals
    residuals = ratios - beta_ivw_std
    
    # HC3 Variance Estimator for weighted mean (or just mean if we view it as OLS with weights)
    # For a simple mean (or weighted mean with fixed weights), the HC3 variance is:
    # Var_HC = sum( (w_i * (r_i - beta)^2 * (1 / (1 - h_ii))^2 ) ) / (sum(w_i))^2 ?
    # Actually, for IVW, it's often formulated as a regression through origin.
    # Simpler approach for "HC-IVW" in MR context: 
    # Estimate SE using the empirical variance of the weighted ratios, accounting for the leverage.
    # Leverage h_ii for weighted mean: h_ii = w_i / sum(w_j).
    
    h_ii = w_naive / np.sum(w_naive)
    # HC3 adjustment factor: 1 / (1 - h_ii)^2
    hc3_factors = 1.0 / (1.0 - h_ii) ** 2
    
    # Sandwich variance: sum( w_i^2 * residual_i^2 * hc3_factor_i ) / (sum(w_i))^2
    # Note: The influence of observation i on the mean is proportional to w_i.
    # The variance of the estimator is sum( (partial/partial_y_i)^2 * Var(y_i) )
    # Here we estimate Var(y_i) by residual^2 * hc3_factor.
    
    numerator = np.sum( (w_naive ** 2) * (residuals ** 2) * hc3_factors )
    denominator = (np.sum(w_naive) ** 2)
    var_hc3 = numerator / denominator
    se_hc3 = np.sqrt(var_hc3)
    
    z_hc3 = beta_ivw_std / se_hc3
    p_hc3 = 2 * (1 - stats.norm.cdf(abs(z_hc3)))
    reject_hc3 = p_hc3 < P.ALPHA
    
    return reject_std, reject_hc3, beta_ivw_std, se_hc3

def cell(seed, n, noise, metric_kind_override=None):
    """
    Run TRIALS for a specific sample size n.
    Returns cell stats and lists of estimates/deviations if needed for bias.
    """
    rng = np.random.default_rng(seed)
    m_kind = metric_kind_override if metric_kind_override else P.METRIC_KIND
    
    rejects_std = []
    rejects_hc = []
    estimates = []
    
    # We need to track BOTH methods to compare them as per protocol
    # But the global METRIC_KIND might be 'power'. The protocol specifically asks to compare Standard vs HC.
    # The script must output the metric defined in sim_params, but the simulation MUST include both methods.
    # If METRIC_KIND is 'power', we likely care about the HC power vs Standard power.
    # However, the output format requires a single 'metric' per cell.
    # The Protocol Prediction: "Standard IVW power < 40%, HC-IVW > 70%".
    # The Falsification: "Standard >= 80% OR HC no improvement".
    # The sim_params likely sets METRIC_KIND to 'power'. Which power? 
    # Given the claim is about HC recovering power, and the falsification checks Standard, 
    # we should probably return the HC power as the primary metric if the claim is about HC success,
    # OR we need to structure the output to reflect the comparison.
    # BUT the skeleton returns a single 'metric'. 
    # Let's assume the user sets METRIC_KIND to evaluate the SUCCESS of the proposed method (HC).
    # OR, if the test is about the failure of Standard, maybe it's Standard.
    # Let's look at the "threshold" and "comparison". 
    # Prediction: HC > 70%. Threshold 0.8? Comparison 'at_most'? 
    # Wait, the provided JSON in the prompt has: "threshold": 0.8, "comparison": "at_most".
    # And Falsification: "Standard IVW achieves >= 80%".
    # This implies the test is checking if Standard Power is TOO HIGH (falsifying the "power desert" claim).
    # So the metric being tested against the threshold is likely the STANDARD power.
    # If Standard Power >= 0.8, the claim of a "power desert" is false.
    # So we will compute both, but the 'metric' returned for the cell will be the STANDARD power 
    # because the falsification condition targets it.
    # HOWEVER, the claim also says HC recovers power. 
    # Let's re-read carefully: "Falsification: Standard IVW achieves >= 80% ... OR HC-IVW shows no significant power improvement".
    # The primary metric for the "power desert" claim is the low power of standard methods.
    # So we track Standard Power as the main metric for the threshold test.
    
    for _ in range(P.TRIALS):
        r_std, r_hc, est, se = run_mr_trial(rng, n_snps=1000, n_sample=n, true_beta=P.EFFECT, noise_scale=noise)
        rejects_std.append(r_std)
        rejects_hc.append(r_hc)
        estimates.append(est)
        
    power_std = np.mean(rejects_std)
    power_hc = np.mean(rejects_hc)
    
    # Store HC power in a way we can access later? 
    # The skeleton returns one metric. We'll return Standard Power as it's the one being tested against the "desert" claim (low power).
    # If the claim is "Power < 40%", and we test "at_most 0.8", that's a weak test. 
    # Actually, if the claim is "Power < 40%", and we observe 80%, we falsify.
    # So the metric is Standard Power.
    
    cell_data = {'n': n, 'metric': float(power_std), 'trials': P.TRIALS}
    
    # We also need to return HC power for the "no improvement" check? 
    # The skeleton doesn't support returning two metrics per cell easily.
    # But the reviewer said: "fails to compare 'Standard IVW' against 'HC-IVW'".
    # We can store the HC power in the 'cells' list as an extra field or just ensure the simulation logic includes it.
    # The output JSON has a 'cells' array. We can add 'hc_metric' there.
    cell_data['hc_metric'] = float(power_hc)
    
    # For bias/coverage logic (if applicable, though protocol is power)
    deviations = [abs(e - P.EFFECT) for e in estimates]
    
    if m_kind == 'bias':
        return cell_data, deviations
    return cell_data, None

def threshold_p(hits, deviations):
    # hits is the count or proportion? In the loop below we pass the metric (proportion) * TRIALS?
    # No, the binomtest expects integer hits.
    # The cell returns 'metric' as a proportion.
    if P.METRIC_KIND == 'bias':
        return float(stats.ttest_1samp(deviations, P.THRESHOLD, alternative=ALT).pvalue)
    
    # hits should be integer count of successes
    # The caller will pass int(hits_prop * TRIALS)
    return float(stats.binomtest(int(hits), P.TRIALS, P.THRESHOLD, alternative=ALT).pvalue)

def main():
    rng_master = np.random.default_rng(P.SEED)
    seeds = rng_master.integers(0, 2**32 - 1, size=P.REPLICATIONS)
    
    rep_values = []
    rep_p_values = []
    rep_directions = [] # Does value meet threshold condition?
    rep_significants = [] # Is p < ALPHA?
    
    # To store cell averages over replications
    grid_cells_sum = {n: {'metric': 0.0, 'hc_metric': 0.0, 'count': 0} for n in P.GRID}
    
    # Sensitivity storage
    sens_results = []

    for r_idx, seed in enumerate(seeds):
        rep_cell_metrics = {}
        rep_cell_hc_metrics = {}
        ref_deviations = [] # For bias
        ref_hits = 0
        
        # Run all grid cells for this replication
        for n in P.GRID:
            # Determine noise for this run (standard)
            noise = P.NOISE
            c_data, devs = cell(seed + n, n, noise)
            
            rep_cell_metrics[n] = c_data['metric']
            rep_cell_hc_metrics[n] = c_data['hc_metric']
            
            # Accumulate for grid average
            grid_cells_sum[n]['metric'] += c_data['metric']
            grid_cells_sum[n]['hc_metric'] += c_data['hc_metric']
            grid_cells_sum[n]['count']