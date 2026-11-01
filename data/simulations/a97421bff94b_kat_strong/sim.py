import json
import numpy as np
from scipy import stats
import sim_params as P

ALT = 'greater' if P.COMPARISON == 'at_least' else 'less'

def run_inner_trials(seed, n, noise, effect):
    """
    Runs TRIALS inner studies for a given sample size n, noise, and effect.
    Returns:
        - metric_val: The computed metric (power, coverage, or bias) for this cell.
        - deviations: List of absolute deviations (|estimate - effect|) for each trial (needed for bias test).
        - hits: Number of successes (needed for power/coverage test).
    """
    rng = np.random.default_rng(seed)
    
    # Generate all data at once for speed: shape (TRIALS, n)
    # Group 1: Mean 0, Std Noise
    group1 = rng.normal(0.0, noise, size=(P.TRIALS, n))
    # Group 2: Mean Effect, Std Noise
    group2 = rng.normal(effect, noise, size=(P.TRIALS, n))
    
    # Compute statistics for each trial
    # Means
    mean1 = np.mean(group1, axis=1)
    mean2 = np.mean(group2, axis=1)
    est = mean2 - mean1
    
    # Variances (ddof=1 for sample variance)
    var1 = np.var(group1, axis=1, ddof=1)
    var2 = np.var(group2, axis=1, ddof=1)
    
    # Standard Error of the difference
    se = np.sqrt(var1/n + var2/n)
    
    # T-statistic
    t_stat = est / se
    
    # Degrees of freedom (Welch's approximation)
    # df = (s1^2/n1 + s2^2/n2)^2 / [ (s1^2/n1)^2/(n1-1) + (s2^2/n2)^2/(n2-1) ]
    num = (var1/n + var2/n)**2
    den = (var1/n)**2 / (n-1) + (var2/n)**2 / (n-1)
    df = num / den
    
    # Two-sided p-values
    # Using survival function for precision: 2 * min(cdf, sf)
    # Since t_dist is symmetric, p = 2 * (1 - cdf(|t|))
    p_values = 2 * stats.t.sf(np.abs(t_stat), df)
    
    # Confidence Intervals (95%)
    # t_crit for 95% CI (two-sided alpha=0.05 -> 0.975 quantile)
    t_crit = stats.t.ppf(0.975, df)
    ci_low = est - t_crit * se
    ci_high = est + t_crit * se
    
    deviations = np.abs(est - effect)
    
    if P.METRIC_KIND == 'power':
        successes = (p_values < P.ALPHA).sum()
        metric_val = successes / P.TRIALS
        return metric_val, deviations, successes
        
    elif P.METRIC_KIND == 'coverage':
        # Check if EFFECT is within [ci_low, ci_high]
        covered = (ci_low <= effect) & (effect <= ci_high)
        successes = covered.sum()
        metric_val = successes / P.TRIALS
        return metric_val, deviations, successes
        
    elif P.METRIC_KIND == 'bias':
        metric_val = np.mean(deviations)
        return metric_val, deviations, None
        
    return 0.0, deviations, None

def compute_threshold_p_value(hits, deviations):
    """Computes the p-value for the threshold test."""
    if P.METRIC_KIND == 'bias':
        # One-sample t-test on deviations against THRESHOLD
        # deviations is an array of length TRIALS
        res = stats.ttest_1samp(deviations, P.THRESHOLD, alternative=ALT)
        return res.pvalue
    else:
        # Binomial test on hits
        res = stats.binomtest(int(hits), P.TRIALS, P.THRESHOLD, alternative=ALT)
        return res.pvalue

def main():
    rng_master = np.random.default_rng(P.SEED)
    
    # Storage for replication-level results
    rep_values = []
    rep_p_values = []
    
    # Storage for grid cell averages (accumulated over replications)
    # Key: n, Value: {'sum_metric': float, 'count': int}
    grid_accumulators = {n: {'sum_metric': 0.0, 'count': 0} for n in P.GRID}
    
    # Sensitivity storage: {noise_factor: [values]}
    sens_results = {0.5: [], 2.0: []}
    
    for r in range(P.REPLICATIONS):
        # Determine seed for this replication
        rep_seed = int(rng_master.integers(0, 2**31))
        
        rep_val = None
        rep_p = None
        
        # Process standard grid
        for n in P.GRID:
            # Run inner trials
            metric_val, deviations, hits = run_inner_trials(rep_seed, n, P.NOISE, P.EFFECT)
            
            # Accumulate for grid average
            grid_accumulators[n]['sum_metric'] += metric_val
            grid_accumulators[n]['count'] += 1
            
            # If this is the reference cell, store replication value and compute p-value
            if n == P.REFERENCE_N:
                rep_val = metric_val
                if P.METRIC_KIND == 'bias':
                    rep_p = compute_threshold_p_value(None, deviations)
                else:
                    rep_p = compute_threshold_p_value(hits, None)
        
        # Store replication results
        rep_values.append(rep_val)
        rep_p_values.append(rep_p)
        
        # Sensitivity Analysis: Reference N with modified noise
        for factor in [0.5, 2.0]:
            sens_noise = P.NOISE * factor
            s_metric, s_devs, s_hits = run_inner_trials(rep_seed, P.REFERENCE_N, sens_noise, P.EFFECT)
            
            if P.METRIC_KIND == 'bias':
                s_p = compute_threshold_p_value(None, s_devs)
            else:
                s_p = compute_threshold_p_value(s_hits, None)
            
            sens_results[factor].append({'metric': s_metric, 'p_value': s_p})

    # --- Post-processing ---
    
    rep_values = np.array(rep_values)
    rep_p_values = np.array(rep_p_values)
    
    # Mean value over replications
    mean_value = float(np.mean(rep_values))
    
    # 95% CI over replication values (using percentile method for simplicity and robustness)
    ci_low = float(np.percentile(rep_values, 2.5))
    ci_high = float(np.percentile(rep_values, 97.5))
    
    # Median p-value over replications
    median_p = float(np.median(rep_p_values))
    
    # Direction share: share of replications where value meets threshold condition
    if P.COMPARISON == 'at_least':
        direction_mask = rep_values >= P.THRESHOLD
    else:
        direction_mask = rep_values <= P.THRESHOLD
    direction_share = float(np.mean(direction_mask))
    
    # Significant share: share of replications with p < ALPHA
    significant_share = float(np.mean(rep_p_values < P.ALPHA))
    
    # Grid cells output (averaged over replications)
    cells_output = []
    sorted_grid = sorted(P.GRID)
    for n in sorted_grid:
        acc = grid_accumulators[n]
        avg_metric = acc['sum_metric'] / acc['count']
        cells_output.append({
            "n": n,
            "metric": avg_metric,
            "trials": P.TRIALS
        })
    
    # Trend calculation
    # Predicted direction: 
    # Power/Coverage should rise with N (positive trend)
    # Bias should fall with N (negative trend)
    if len(P.GRID) < 2:
        trend = None
    else:
        expected_increasing = (P.METRIC_KIND in ['power', 'coverage'])
        steps = len(sorted_grid) - 1
        matching_steps = 0
        
        for i in range(steps):
            n1, n2 = sorted_grid[i], sorted_grid[i+1]
            m1 = grid_accumulators[n1]['sum_metric'] / grid_accumulators[n1]['count']
            m2 = grid_accumulators[n2]['sum_metric'] / grid_accumulators[n2]['count']
            
            if expected_increasing:
                if m2 >= m1:
                    matching_steps += 1
            else: # Bias, expected decreasing
                if m2 <= m1:
                    matching_steps += 1
        
        trend = matching_steps / steps

    # Sensitivity output
    sensitivity_output = {}
    for factor, vals in sens_results.items():
        avg_met = np.mean([v['metric'] for v in vals])
        avg_p = np.median([v['p_value'] for v in vals])
        sensitivity_output[str(factor)] = {
            "noise_factor": factor,
            "metric": float(avg_met),
            "p_value": float(avg_p)
        }

    result = {
        "n": P.REFERENCE_N,
        "metric": P.METRIC_KIND,
        "test": f"binomtest" if P.METRIC_KIND != 'bias' else "ttest_1samp",
        "alpha": P.ALPHA,
        "seed": P.SEED,
        "replications": P.REPLICATIONS,
        "value": mean_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": median_p,
        "values": rep_values.tolist(),
        "p_values": rep_p_values.tolist(),
        "significant_share": significant_share,
        "direction_share": direction_share,
        "sensitivity": sensitivity_output,
        "cells": cells_output,
        "grid": P.GRID,
        "trend": trend
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()