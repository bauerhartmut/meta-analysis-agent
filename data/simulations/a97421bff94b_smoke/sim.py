import json
import numpy as np
from scipy import stats
import sim_params as P

ALT = 'greater' if P.COMPARISON == 'at_least' else 'less'

def run_trial(rng, n, noise, effect, elderly_only):
    """
    Simulate a single trial with latency-dependent mechanism.
    Population: Age ~ Uniform(40, 90).
    Effect exists only if Age >= 65.
    If elderly_only=True, filter to Age >= 65.
    Returns: (estimate, p_value, ci_contains_effect)
    """
    # Generate ages
    ages = rng.uniform(40, 90, n)
    
    # Determine mask for effective treatment based on latency
    # Mechanism: Effect is 0 for Age < 65, and 'effect' for Age >= 65
    effective_mask = ages >= 65
    
    if elderly_only:
        # Filter population to elderly only
        valid_indices = effective_mask
        n_valid = np.sum(valid_indices)
        if n_valid == 0:
            # Edge case: no elderly in sample (unlikely with n=1000+ but possible)
            return None, 1.0, False
        
        # Subsample logic: we need n_valid observations for the test? 
        # The prompt implies "Elderly-Only" analysis uses the subset.
        # To keep variance comparable or just follow the design:
        # We use the available elderly individuals.
        current_n = n_valid
        current_ages = ages[valid_indices]
        # In this subgroup, ALL are effective (since we filtered Age >= 65)
        group_effects = np.full(current_n, effect)
    else:
        # All-Age analysis
        current_n = n
        current_ages = ages
        # Effect is diluted: only those >= 65 have the effect
        group_effects = np.where(effective_mask, effect, 0.0)

    # Generate Outcome Y = Noise + Effect + Error
    # Design: Two groups? The hypothesis mentions "instrument strength" and "GWAS/MR".
    # Usually involves Genotype (G) and Outcome (Y).
    # Simplified to match the "two groups" skeleton but adapted for the mechanism:
    # Let's simulate G (0 or 1) and Y.
    # G ~ Binomial(2, 0.3) or just 0/1 for t-test simplicity? 
    # The skeleton uses ttest_ind(group1, group2).
    # Let's map G=0 to group1, G=1 to group2.
    
    # Generate Genotypes
    genotypes = rng.binomial(1, 0.5, current_n) # Simplified to 0/1 for t-test
    
    # Calculate Y
    # Y = (Effect * G * I(Age>=65)) + Noise
    # Note: In elderly_only, I(Age>=65) is always 1.
    # In all-age, it varies.
    
    noise_vals = rng.normal(0.0, noise, current_n)
    y_vals = (group_effects * genotypes) + noise_vals
    
    # Split into groups for t-test
    group0 = y_vals[genotypes == 0]
    group1 = y_vals[genotypes == 1]
    
    if len(group0) < 2 or len(group1) < 2:
        return None, 1.0, False

    # Perform t-test
    t_res = stats.ttest_ind(group1, group0, equal_var=False)
    estimate = float(group1.mean() - group0.mean())
    p_val = float(t_res.pvalue)
    
    # Confidence Interval
    # Using pooled SE approximation or Welch's CI manually if needed, 
    # but scipy ttest doesn't return CI directly in older versions.
    # Let's compute Welch CI manually.
    n0, n1 = len(group0), len(group1)
    v0, v1 = group0.var(ddof=1), group1.var(ddof=1)
    se = np.sqrt(v0/n0 + v1/n1)
    df = (v0/n0 + v1/n1)**2 / ((v0/n0)**2/(n0-1) + (v1/n1)**2/(n1-1))
    t_crit = stats.t.ppf(1 - P.ALPHA/2, df)
    ci_low = estimate - t_crit * se
    ci_high = estimate + t_crit * se
    
    ci_contains = (ci_low <= effect <= ci_high)
    
    return estimate, p_val, ci_contains

def cell(seed, n, noise, elderly_only):
    """
    Run TRIALS inner studies for a specific configuration.
    Returns: cell_info, deviations_list (for bias), hits (for power/coverage)
    """
    rng = np.random.default_rng(seed)
    
    estimates = []
    deviations = []
    hits = 0
    coverage_hits = 0
    
    for _ in range(P.TRIALS):
        res = run_trial(rng, n, noise, P.EFFECT, elderly_only)
        if res[0] is None:
            continue
            
        est, p_val, ci_cont = res
        estimates.append(est)
        deviations.append(abs(est - P.EFFECT))
        
        if P.METRIC_KIND == 'power':
            if p_val < P.ALPHA:
                hits += 1
        elif P.METRIC_KIND == 'coverage':
            if ci_cont:
                coverage_hits += 1
    
    # Compute metric
    if P.METRIC_KIND == 'bias':
        metric_val = float(np.mean(deviations))
        return {'n': n, 'metric': metric_val, 'trials': len(deviations)}, deviations
    elif P.METRIC_KIND == 'power':
        metric_val = hits / len(estimates) if estimates else 0.0
        return {'n': n, 'metric': metric_val, 'trials': len(estimates)}, None
    elif P.METRIC_KIND == 'coverage':
        metric_val = coverage_hits / len(estimates) if estimates else 0.0
        return {'n': n, 'metric': metric_val, 'trials': len(estimates)}, None
    
    return {'n': n, 'metric': 0.0, 'trials': 0}, []

def threshold_p(hits_count, deviations_list, total_trials):
    """Compute p-value for the threshold test."""
    if P.METRIC_KIND == 'bias':
        if len(deviations_list) < 2:
            return 1.0
        t_res = stats.ttest_1samp(deviations_list, P.THRESHOLD, alternative=ALT)
        return float(t_res.pvalue)
    else:
        # Power or Coverage: Binomial test
        # hits_count is the number of successes in total_trials
        bt = stats.binomtest(int(hits_count), total_trials, P.THRESHOLD, alternative=ALT)
        return float(bt.pvalue)

def main():
    rng_master = np.random.default_rng(P.SEED)
    
    rep_values = []
    rep_p_values = []
    
    # Storage for averaging cells over replications
    # Key: (n, elderly_only_flag), Value: list of metrics
    cell_metrics_accumulator = {}
    
    # We need to run the REFERENCE_N cell specifically for the main metric
    # But the grid loop must run for all N.
    # The hypothesis requires comparing Elderly-Only vs All-Age.
    # However, the protocol says "Read every number from sim_params".
    # The sim_params defines one GRID, one REFERENCE_N.
    # The hypothesis implies the "variable" is the difference or the specific Elderly-Only power.
    # Given the reviewer's complaint: "fails to implement Elderly-Only vs All-Age comparison".
    # And "The script only runs one simulation per grid cell".
    # We must interpret the "cell" definition. 
    # If the hypothesis is about Elderly-Only recovering signal, the primary metric should likely be 
    # the power in the Elderly-Only stratum. 
    # OR, we run both and the "value" is the difference?
    # The prompt skeleton computes "value" from the cell at REFERENCE_N.
    # Let's assume the "treatment" here is the stratification. 
    # To satisfy "compare", we might need to output both or define the metric as the gain.
    # BUT, the skeleton structure is rigid: "For each n in GRID run TRIALS... compute metric".
    # If we change the metric to be "Power(Elderly) - Power(All)", that's a derived metric.
    # Let's look at the reviewer: "The simulation must... compare subgroups".
    # Maybe the GRID represents different scenarios, but the core fix is inside the trial.
    # Actually, the most faithful fix to "measure the variable described" (which is the recovery of signal in elderly)
    # is to set the simulation to run the Elderly-Only analysis as the primary readout for the hypothesis,
    # OR run both and report the contrast.
    # Given the strict JSON output format expecting a single "value" per replication derived from REFERENCE_N cell:
    # Let's assume the intended experiment is: The "Effect" we are measuring is the Power in the Elderly-Only group.
    # Why? Because the claim is "Elderly-only analyses recover the signal".
    # The falsification is "Power is identical or lower".
    # So we test if Power(Elderly) > Threshold.
    # However, to explicitly show the comparison requested ("vs all-age"), we should probably include 
    # the All-Age metric in the detailed cells output or ensure the design reflects the contrast.
    # Let's modify the `cell` function to accept a mode.
    # But the loop structure iterates `for n in GRID`.
    # How do we fit two modes (All-Age, Elderly) into one GRID loop?
    # Option A: Run both modes for every N. Store both. The "value" for the replication is based on the Elderly mode at REFERENCE_N.
    # Option B: The GRID itself represents the modes? No, GRID is sample sizes.
    # Let's go with Option A: For each N, we simulate BOTH All-Age and Elderly-Only.
    # The "cells" output will contain entries for both (maybe distinguished by a label or just n?).
    # Wait, the output format for cells is `[{"n": ..., "metric": ..., "trials": ...}]`. It doesn't have a "mode" key.
    # This suggests we might need to pick ONE mode per run, or the problem implies we only care about the Elderly one now.
    # Re-reading reviewer: "fails to implement the 'Elderly-Only' vs 'All-Age' comparison required to test the claim."
    # If I only output Elderly, I haven't shown the comparison in the results.
    # Perhaps the "metric" for the cell IS the difference? 
    # "Power(Elderly) - Power(All-Age)".
    # If metric = difference, then:
    # - Value = Mean(Difference) at REFERENCE_N.
    # - Threshold test: Is Difference > 0? (Or > some threshold).
    # This perfectly captures the comparison.
    # Let's adopt this: The metric for a given N is (Metric_Elderly - Metric_AllAge).
    # For Bias: (Bias_AllAge - Bias_Elderly) ? No, Bias is absolute error. 
    # If the claim is about Power, let's stick to the METRIC_KIND provided.
    # If METRIC_KIND is Power, Cell_Metric = Power_Elderly - Power_AllAge.
    # If METRIC_KIND is Coverage, Cell_Metric = Cov_Elderly - Cov_AllAge.
    # If METRIC_KIND is Bias, Cell_Metric = Bias_AllAge - Bias_Elderly (so positive means Elderly is better/less biased).
    # This satisfies the "comparison" requirement within the single metric framework.
    
    # Adjusted Plan:
    # Inside `cell`, run both modes. Compute metric for each. Return the difference.
    # Also need to track deviations for the threshold test if metric is bias?
    # If metric is difference of means (power/coverage), the "hits" for binomtest?
    # Wait, the threshold test logic in skeleton:
    # Power/Coverage: binomtest(hits, TRIALS, THRESHOLD). This implies the inner unit is a Bernoulli trial?
    # But if our metric is a difference of proportions, it's continuous.
    # The skeleton assumes the metric is computed as a share (power) or mean (bias) over TRIALS.
    # And the threshold test is on the AGGREGATE of the TRIALS?
    # No, look at skeleton:
    # `obs += float(t.pvalue < P.ALPHA)` -> obs is count of successes in TRIALS.
    # `metric = obs / TRIALS`.
    # `threshold_p`: `stats.binomtest(int(hits), TRIALS, ...)` where hits = obs * TRIALS?
    # Actually, the skeleton passes `hits` (which is `obs` in my head, but `obs` was count) to binomtest.
    # Wait, `obs` in skeleton is the count. `metric` is proportion.
    # Then `threshold_p` takes `hits` (the count) and `TRIALS`.
    # If I change metric to Difference, I can't use binomtest directly on the difference.
    # The hypothesis test in the skeleton is: "Is the proportion of successes > THRESHOLD?"
    # If I change the metric to a difference, the statistical test logic in the skeleton (binomtest) becomes invalid.
    # UNLESS: The "inner study" is defined as a pair (All-Age, Elderly) and the "success" is "Elderly > All-Age"?
    # That fits!
    # Redefine inner trial success:
    # For Power: Success = (Power_Elderly_trial > Power_AllAge_trial)? No, power is a population property, not