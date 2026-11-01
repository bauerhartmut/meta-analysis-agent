import json
import numpy as np
from scipy import stats
import sim_params as P
from typing import List, Dict, Any

ALT = 'greater' if P.COMPARISON == 'at_least' else 'less'

def run_inner_trials(rng: np.random.Generator, n: int, noise: float) -> tuple:
    """
    Runs TRIALS inner studies for a given sample size n and noise level.
    Returns:
      - metric_value: The aggregated metric for this cell (power, coverage, or mean bias).
      - deviations: List of absolute deviations |estimate - EFFECT| for each trial (needed for bias p-value).
      - hits: Count of successes (for power/coverage p-value).
    """
    estimates = []
    hits = 0
    
    # Vectorized generation for speed: Generate all data at once if possible, 
    # but since we need individual CIs and p-values per trial, we loop or batch carefully.
    # Given constraints, we loop over TRIALS but vectorize the group generation within.
    
    for _ in range(P.TRIALS):
        # Group 1: N(0, noise), Group 2: N(EFFECT, noise)
        # Size n for each group
        g1 = rng.normal(0.0, noise, n)
        g2 = rng.normal(P.EFFECT, noise, n)
        
        # Welch's t-test
        t_res = stats.ttest_ind(g1, g2, equal_var=False)
        est = float(g2.mean() - g1.mean())
        estimates.append(est)
        
        ci = t_res.confidence_interval(0.95)
        
        if P.METRIC_KIND == 'power':
            if t_res.pvalue < P.ALPHA:
                hits += 1
        elif P.METRIC_KIND == 'coverage':
            if ci.low <= P.EFFECT <= ci.high:
                hits += 1
    
    deviations = [abs(e - P.EFFECT) for e in estimates]
    
    if P.METRIC_KIND == 'bias':
        metric_val = float(np.mean(deviations))
        return metric_val, deviations, None
    else:
        metric_val = hits / P.TRIALS
        return metric_val, None, hits

def compute_p_value(metric_val, deviations, hits):
    """Computes the p-value for the threshold test based on metric kind."""
    if P.METRIC_KIND == 'bias':
        # t-test on deviations
        res = stats.ttest_1samp(deviations, P.THRESHOLD, alternative=ALT)
        return float(res.pvalue)
    else:
        # binomial test on hits
        res = stats.binomtest(int(hits), P.TRIALS, P.THRESHOLD, alternative=ALT)
        return float(res.pvalue)

def main():
    rng_master = np.random.default_rng(P.SEED)
    
    # Storage for replication-level results
    rep_values = []
    rep_p_values = []
    
    # Storage for grid cell averages (accumulated over replications)
    # Key: n, Value: {'sum_metric': float, 'count': int}
    grid_accumulators = {n: {'sum_metric': 0.0, 'count': 0} for n in P.GRID}
    
    # Sensitivity storage: store the metric value for sensitivity runs to include in output if needed,
    # though the prompt asks for sensitivity logic to run, the JSON output schema doesn't explicitly 
    # demand sensitivity values in the top level, but implies checking them. 
    # However, looking at the required JSON keys: "sensitivity" is a key. 
    # Let's assume it expects a summary of the sensitivity check or just the fact it was done.
    # Re-reading: "SENSITIVITY: repeat the REFERENCE_N cell once at NOISE x 0.5 and once at NOISE x 2.0, with the same threshold test."
    # And output key: "sensitivity". Usually this implies the results of those tests or a boolean.
    # Given the strict key list, I will compute the metric for these sensitivity cases and store them 
    # in a dict under the "sensitivity" key.
    sensitivity_results = []

    for r in range(P.REPLICATIONS):
        seed_r = int(rng_master.integers(0, 2**31 - 1))
        rng_rep = np.random.default_rng(seed_r)
        
        rep_cell_metrics = {} # n -> metric for this rep
        rep_cell_deviations = {} # n -> deviations (only needed for ref n if bias)
        rep_cell_hits = {} # n -> hits (only needed for ref n if power/coverage)
        
        current_noise = P.NOISE
        
        # We need to run all grid cells for this replication
        for n in P.GRID:
            metric_val, deviations, hits = run_inner_trials(rng_rep, n, current_noise)
            
            rep_cell_metrics[n] = metric_val
            if deviations is not None:
                rep_cell_deviations[n] = deviations
            if hits is not None:
                rep_cell_hits[n] = hits
            
            # Accumulate for grid average
            grid_accumulators[n]['sum_metric'] += metric_val
            grid_accumulators[n]['count'] += 1
        
        # Extract Reference N value for this replication
        ref_n = P.REFERENCE_N
        val = rep_cell_metrics[ref_n]
        rep_values.append(val)
        
        # Compute p-value for this replication's reference cell
        devs = rep_cell_deviations.get(ref_n)
        hts = rep_cell_hits.get(ref_n)
        p_val = compute_p_value(val, devs, hts)
        rep_p_values.append(p_val)
        
        # Sensitivity Runs for this replication (only on REFERENCE_N)
        # Run 1: Noise * 0.5
        sens_noise_low = P.NOISE * 0.5
        m_low, d_low, h_low = run_inner_trials(rng_rep, ref_n, sens_noise_low)
        p_low = compute_p_value(m_low, d_low, h_low)
        
        # Run 2: Noise * 2.0
        sens_noise_high = P.NOISE * 2.0
        m_high, d_high, h_high = run_inner_trials(rng_rep, ref_n, sens_noise_high)
        p_high = compute_p_value(m_high, d_high, h_high)
        
        sensitivity_results.append({
            "noise_factor": [0.5, 2.0],
            "metrics": [m_low, m_high],
            "p_values": [p_low, p_high]
        })

    # Calculate final outputs
    
    # 1. Value: mean over replications
    final_value = float(np.mean(rep_values))
    
    # 2. CI: 95% interval over replication values
    ci_low, ci_high = float(np.percentile(rep_values, 2.5)), float(np.percentile(rep_values, 97.5))
    
    # 3. P-value: median over replications
    final_p_value = float(np.median(rep_p_values))
    
    # 4. Significant share: share of reps with p < ALPHA
    significant_share = float(np.mean([1 if p < P.ALPHA else 0 for p in rep_p_values]))
    
    # 5. Direction share: share of reps where value meets threshold per COMPARISON
    direction_count = 0
    for v in rep_values:
        if P.COMPARISON == 'at_least':
            if v >= P.THRESHOLD:
                direction_count += 1
        else: # at_most
            if v <= P.THRESHOLD:
                direction_count += 1
    direction_share = float(direction_count / P.REPLICATIONS)
    
    # 6. Cells: averaged over replications per grid cell
    cells_output = []
    sorted_grid = sorted(P.GRID)
    for n in sorted_grid:
        acc = grid_accumulators[n]
        avg_metric = acc['sum_metric'] / acc['count']
        cells_output.append({
            "n": int(n),
            "metric": float(avg_metric),
            "trials": P.TRIALS * P.REPLICATIONS # Total trials contributing to this average
        })
    
    # 7. Trend: share of adjacent grid steps moving as predicted
    # Predicted: rising for power/coverage, falling for bias
    trend_val = None
    if len(sorted_grid) > 1:
        correct_steps = 0
        total_steps = len(sorted_grid) - 1
        
        # Extract just the averaged metrics in grid order
        metrics_by_grid = [cells_output[i]['metric'] for i in range(len(cells_output))]
        # Ensure order matches sorted_grid
        # cells_output is already built from sorted_grid
        
        for i in range(total_steps):
            m1 = metrics_by_grid[i]
            m2 = metrics_by_grid[i+1]
            
            if P.METRIC_KIND in ['power', 'coverage']:
                # Expect rising: m2 > m1
                if m2 > m1:
                    correct_steps += 1
            elif P.METRIC_KIND == 'bias':
                # Expect falling: m2 < m1 (bias usually decreases with N)
                if m2 < m1:
                    correct_steps += 1
        
        trend_val = float(correct_steps / total_steps)
    else:
        trend_val = None # Null when only one value

    # 8. Sensitivity: Aggregate sensitivity results? 
    # The prompt says "sensitivity" key. Let's provide the average metrics from sensitivity runs.
    avg_sens_low = float(np.mean([s['metrics'][0] for s in sensitivity_results]))
    avg_sens_high = float(np.mean([s['metrics'][1] for s in sensitivity_results]))
    sensitivity_output = {
        "noise_half": avg_sens_low,
        "noise_double": avg_sens_high
    }

    result = {
        "n": int(P.REFERENCE_N),
        "metric": P.METRIC_KIND,
        "test": f"one-sided ({ALT})",
        "alpha": P.ALPHA,
        "seed": P.SEED,
        "replications": P.REPLICATIONS,
        "value": final_value,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": final_p_value,
        "values": [float(v) for v in rep_values],
        "p_values": [float(p) for p in rep_p_values],
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