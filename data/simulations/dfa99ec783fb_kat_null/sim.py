import json
import numpy as np
from scipy import stats
import sim_params as P

ALT = 'greater' if P.COMPARISON == 'at_least' else 'less'

def run_trial(rng, n, noise, effect):
    # Group 1: N(0, noise), Group 2: N(effect, noise)
    # Using equal_var=False (Welch's t-test) as per skeleton
    a = rng.normal(0.0, noise, n)
    b = rng.normal(effect, noise, n)
    
    t_res = stats.ttest_ind(a, b, equal_var=False)
    est = b.mean() - a.mean()
    
    # Confidence Interval calculation
    # Welch-Satterthwaite degrees of freedom
    v1 = np.var(a, ddof=1) / n
    v2 = np.var(b, ddof=1) / n
    se = np.sqrt(v1 + v2)
    df_num = (v1 + v2)**2
    df_den = (v1**2 / (n - 1)) + (v2**2 / (n - 1))
    df = df_num / df_den if df_den > 0 else 1.0
    
    ci_low = est - stats.t.ppf(1 - P.ALPHA / 2, df) * se
    ci_high = est + stats.t.ppf(1 - P.ALPHA / 2, df) * se
    
    return {
        'pvalue': t_res.pvalue,
        'est': est,
        'ci_low': ci_low,
        'ci_high': ci_high,
        'deviation': abs(est - effect)
    }

def process_cell(seed, n, noise):
    rng = np.random.default_rng(seed)
    
    # Vectorized generation for speed if possible, but logic requires per-trial stats
    # To ensure independence and strict adherence to "TRIALS inner studies", we loop or batch.
    # Given constraints and need for specific stats per trial, a loop is safer for correctness 
    # unless we can fully vectorize the t-test logic. 
    # However, for N up to 500k and TRIALS 2000, pure python loop might be slow.
    # We will use a hybrid: generate all data at once, then compute stats.
    
    # Generate all data: shape (TRIALS, 2, n)
    # Group A
    data_a = rng.normal(0.0, noise, (P.TRIALS, n))
    # Group B
    data_b = rng.normal(P.EFFECT, noise, (P.TRIALS, n))
    
    # Compute means
    mean_a = np.mean(data_a, axis=1)
    mean_b = np.mean(data_b, axis=1)
    est = mean_b - mean_a
    
    # Compute variances (ddof=1)
    var_a = np.var(data_a, axis=1, ddof=1)
    var_b = np.var(data_b, axis=1, ddof=1)
    
    # Standard Error
    se = np.sqrt(var_a / n + var_b / n)
    
    # T-statistic
    t_stat = est / se
    
    # Degrees of freedom (Welch)
    v1 = var_a / n
    v2 = var_b / n
    df_num = (v1 + v2)**2
    df_den = (v1**2 / (n - 1)) + (v2**2 / (n - 1))
    # Avoid division by zero
    df_den = np.where(df_den == 0, 1e-9, df_den)
    df = df_num / df_den
    
    # P-values (two-sided for standard t-test power)
    # stats.t.sf returns survival function (1-cdf). Two-sided = 2 * min(cdf, sf)
    # Or simply 2 * sf(|t|)
    p_values = 2 * stats.t.sf(np.abs(t_stat), df)
    
    # Confidence Intervals
    t_crit = stats.t.ppf(1 - P.ALPHA / 2, df)
    ci_low = est - t_crit * se
    ci_high = est + t_crit * se
    
    # Deviations
    deviations = np.abs(est - P.EFFECT)
    
    # Calculate Metric based on kind
    if P.METRIC_KIND == 'power':
        rejections = (p_values < P.ALPHA).astype(float)
        metric_val = np.mean(rejections)
        extra = None # No need for individual deviations for binom test, just count
        hits = int(np.sum(rejections))
        return {'n': n, 'metric': metric_val, 'trials': P.TRIALS}, hits, None
        
    elif P.METRIC_KIND == 'coverage':
        covered = (ci_low <= P.EFFECT) & (ci_high >= P.EFFECT)
        coverage_flags = covered.astype(float)
        metric_val = np.mean(coverage_flags)
        hits = int(np.sum(coverage_flags))
        return {'n': n, 'metric': metric_val, 'trials': P.TRIALS}, hits, None
        
    elif P.METRIC_KIND == 'bias':
        metric_val = np.mean(deviations)
        # For bias, we need the list of deviations for the t-test later
        return {'n': n, 'metric': metric_val, 'trials': P.TRIALS}, None, deviations
    
    return {'n': n, 'metric': 0.0, 'trials': P.TRIALS}, 0, None

def compute_p_value(hits, deviations):
    if P.METRIC_KIND == 'bias':
        # One-sample t-test against THRESHOLD
        # deviations is an array of length TRIALS
        res = stats.ttest_1samp(deviations, P.THRESHOLD, alternative=ALT)
        return res.pvalue
    else:
        # Binomial test
        res = stats.binomtest(hits, P.TRIALS, P.THRESHOLD, alternative=ALT)
        return res.pvalue

def main():
    rng_master = np.random.default_rng(P.SEED)
    
    rep_values = []
    rep_p_values = []
    
    # Storage for cell averages over replications
    # Key: n, Value: list of metrics from each replication
    cell_metrics_accumulator = {n: [] for n in P.GRID}
    
    # Sensitivity storage: we need to run specific cells with modified noise
    # But the output requires "sensitivity" key. The prompt says:
    # "SENSITIVITY: repeat the REFERENCE_N cell once at NOISE x 0.5 and once at NOISE x 2.0"
    # And output needs "sensitivity": ... likely a dict or list of results.
    # Let's store them.
    sens_results = []
    
    for r in range(P.REPLICATIONS):
        seed_r = P.SEED + r
        current_rep_value = None
        current_rep_p = None
        
        # We need to process GRID for this replication to get the REFERENCE_N value
        # And also accumulate for cell averages
        
        ref_hits = None
        ref_deviations = None
        
        for n in P.GRID:
            cell_res, hits, devs = process_cell(seed_r, n, P.NOISE)
            cell_metrics_accumulator[n].append(cell_res['metric'])
            
            if n == P.REFERENCE_N:
                ref_hits = hits
                ref_deviations = devs
                current_rep_value = cell_res['metric']
        
        # Compute p-value for this replication's reference cell
        if P.METRIC_KIND == 'bias':
            current_rep_p = compute_p_value(None, ref_deviations)
        else:
            current_rep_p = compute_p_value(ref_hits, None)
            
        rep_values.append(current_rep_value)
        rep_p_values.append(current_rep_p)
        
        # Sensitivity runs for this replication? 
        # "repeat the REFERENCE_N cell once at NOISE x 0.5 and once at NOISE x 2.0, with the same threshold test."
        # Does this mean per replication or once overall? 
        # "Per replication r... SENSITIVITY: repeat..." implies per replication.
        # But the output format asks for "sensitivity" (singular) in the final JSON.
        # Usually sensitivity is an aggregate or a specific check. 
        # Let's interpret: Run the sensitivity checks for the reference cell for each replication, 
        # compute their p-values/metrics, and maybe average them or report the share significant?
        # The prompt says: "Print exactly ONE JSON object... sensitivity".
        # Let's calculate the metric for these sensitivity runs for each replication and store them.
        # We'll store a list of dicts for each replication? Or aggregate?
        # "sensitivity": likely a summary. Let's look at the keys again.
        # "sensitivity": not fully specified structure, but "cells" is a list.
        # Let's assume sensitivity is a dict with keys "low_noise" and "high_noise" containing 
        # the average metric over replications for those conditions? 
        # OR, since the p-value test is part of the replication loop description:
        # "repeat ... with the same threshold test".
        # Maybe we just need to report if these sensitivity runs pass the threshold?
        # Let's compute the metrics for low/high noise for the reference N for each replication
        # and store them to compute a summary (e.g., mean metric).
        
        # Low noise
        res_low, hits_low, devs_low = process_cell(seed_r, P.REFERENCE_N, P.NOISE * 0.5)
        # High noise
        res_high, hits_high, devs_high = process_cell(seed_r, P.REFERENCE_N, P.NOISE * 2.0)
        
        sens_results.append({
            'low': res_low['metric'],
            'high': res_high['metric']
        })

    # Aggregate results
    mean_value = float(np.mean(rep_values))
    median_p = float(np.median(rep_p_values))
    
    # 95% CI over replication values (using percentile)
    ci_low = float(np.percentile(rep_values, 2.5))
    ci_high = float(np.percentile(rep_values, 97.5))
    
    # direction_share: share of replications where value meets the threshold the way COMPARISON says
    # "at_least" -> value >= THRESHOLD? Or strictly >? Usually >=.
    # "at_most" -> value <= THRESHOLD
    if P.COMPARISON == 'at_least':
        direction_met = [1 if v >= P.THRESHOLD else 0 for v in rep_values]
    else:
        direction_met = [1 if v <= P.THRESHOLD else 0 for v in rep_values]
    direction_share = float(np.mean(direction_met))
    
    # significant_share: share of replications with p < ALPHA
    significant_flags = [1 if p < P.ALPHA else 0 for p in rep_p_values]
    significant_share = float(np.mean(significant_flags))
    
    # Cells average over replications
    cells_output = []
    for n in P.GRID:
        avg_metric = float(np.mean(cell_metrics_accumulator[n]))
        cells_output.append({
            "n": n,
            "metric": avg_metric,
            "trials": P.TRIALS
        })
    
    # Trend: share of adjacent grid steps that move as predicted
    # Rising for power/coverage, falling for bias
    # Sort grid just in case, though usually sorted
    sorted_grid = sorted(P.GRID)
    trend_val = None
    if len(sorted_grid) > 1:
        correct_moves = 0
        total_moves = len(sorted_grid) - 1
        for i in range(total_moves):
            n1, n2 = sorted_grid[i], sorted_grid[i+1]
            m1 = np.mean(cell_metrics_accumulator[n1])
            m2 = np.mean(cell_metrics_accumulator[n2])
            
            if P.METRIC_KIND in ['power', 'coverage']:
                # Expect rising: m2 > m1
                if m2 > m1:
                    correct_moves += 1
            elif P.METRIC_KIND == 'bias':
                # Expect falling: m2 < m1
                if m2 < m1:
                    correct_moves += 1
        trend_val = float(correct_moves / total_moves)
    
    # Sensitivity aggregation
    # Let's provide the mean metrics for low and high noise over replications
    sens_low_mean = float(np.mean([s['low'] for s in sens_results]))
    sens_high_mean = float(np.mean([s['high'] for s in sens_results]))
    sensitivity_output = {
        "noise_half": sens_low_mean,
        "noise_double": sens_high_mean
    }

    result = {
        "n": P.REFERENCE_N,
        "metric": P.METRIC_KIND,
        "test": f"one-sided ({ALT})",
        "alpha": P.ALPHA,
        "seed": P.SEED,
        "replications": P.REPLICATIONS,
        "value": mean_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": median_p,
        "values": rep_values,
        "p_values": rep_p_values,
        "significant_share": significant_share,
        "direction_share": direction_share,
        "sensitivity": sensitivity_output,
        "cells": cells_output,
        "grid": P.GRID,
        "trend": trend_val
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()