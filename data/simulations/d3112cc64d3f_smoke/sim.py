import json
import numpy as np
from scipy import stats
import sim_params as P

ALT = 'greater' if P.COMPARISON == 'at_least' else 'less'

def run_trial(rng, n, effect, noise):
    g1 = rng.normal(0.0, noise, n)
    g2 = rng.normal(effect, noise, n)
    t_res = stats.ttest_ind(g1, g2, equal_var=False)
    est = g2.mean() - g1.mean()
    ci = t_res.confidence_interval(0.95)
    sig = 1 if t_res.pvalue < P.ALPHA else 0
    cov = 1 if ci.low <= effect <= ci.high else 0
    dev = abs(est - effect)
    return sig, cov, dev

def simulate_cell(rng, n, noise):
    sigs = np.zeros(P.TRIALS, dtype=int)
    covs = np.zeros(P.TRIALS, dtype=int)
    devs = np.zeros(P.TRIALS)
    
    batch_size = min(1000, P.TRIALS)
    for i in range(0, P.TRIALS, batch_size):
        end = min(i + batch_size, P.TRIALS)
        count = end - i
        g1 = rng.normal(0.0, noise, (count, n))
        g2 = rng.normal(P.EFFECT, noise, (count, n))
        
        means1 = g1.mean(axis=1)
        means2 = g2.mean(axis=1)
        stds1 = g1.std(axis=1, ddof=1)
        stds2 = g2.std(axis=1, ddof=1)
        
        se = np.sqrt(stds1**2/n + stds2**2/n)
        t_vals = (means2 - means1) / se
        dfs = (stds1**2/n + stds2**2/n)**2 / ((stds1**2/n)**2/(n-1) + (stds2**2/n)**2/(n-1))
        
        # Two-sided p-value
        p_vals = 2 * (1 - stats.t.cdf(np.abs(t_vals), dfs))
        
        sigs[i:end] = (p_vals < P.ALPHA).astype(int)
        
        # CI
        crit = stats.t.ppf(1 - P.ALPHA/2, dfs)
        low = (means2 - means1) - crit * se
        high = (means2 - means1) + crit * se
        covs[i:end] = ((low <= P.EFFECT) & (P.EFFECT <= high)).astype(int)
        devs[i:end] = np.abs((means2 - means1) - P.EFFECT)
        
    if P.METRIC_KIND == 'power':
        metric_val = np.mean(sigs)
        test_data = sigs
    elif P.METRIC_KIND == 'coverage':
        metric_val = np.mean(covs)
        test_data = covs
    else: # bias
        metric_val = np.mean(devs)
        test_data = devs
        
    return metric_val, test_data

def get_p_value(test_data):
    if P.METRIC_KIND == 'bias':
        res = stats.ttest_1samp(test_data, P.THRESHOLD, alternative=ALT)
        return res.pvalue
    else:
        hits = int(np.sum(test_data))
        res = stats.binomtest(hits, P.TRIALS, P.THRESHOLD, alternative=ALT)
        return res.pvalue

def main():
    rng_master = np.random.default_rng(P.SEED)
    rep_values = []
    rep_pvals = []
    grid_metrics = {n: [] for n in P.GRID}
    
    for r in range(P.REPLICATIONS):
        seed_r = int(rng_master.integers(0, 2**31))
        rng_rep = np.random.default_rng(seed_r)
        
        rep_val = None
        rep_pval = None
        rep_devs_ref = None
        
        for n in P.GRID:
            noise_curr = P.NOISE
            if n == P.REFERENCE_N:
                # We need to store the raw data for the reference cell to compute p-value later
                # But we also need to run sensitivity. Let's handle reference separately.
                pass
            
            # Standard run
            val, data = simulate_cell(rng_rep, n, noise_curr)
            grid_metrics[n].append(val)
            
            if n == P.REFERENCE_N:
                rep_val = val
                if P.METRIC_KIND == 'bias':
                    rep_devs_ref = data
                else:
                    rep_devs_ref = data # hits or covs
            
        # Compute p-value for reference
        if rep_devs_ref is not None:
            rep_pval = get_p_value(rep_devs_ref)
        else:
            # Should not happen if REFERENCE_N is in GRID
            rep_pval = 1.0
            
        rep_values.append(rep_val)
        rep_pvals.append(rep_pval)
        
        # Sensitivity for Reference N
        # Run once at NOISE * 0.5
        val_low, _ = simulate_cell(rng_rep, P.REFERENCE_N, P.NOISE * 0.5)
        # Run once at NOISE * 2.0
        val_high, _ = simulate_cell(rng_rep, P.REFERENCE_N, P.NOISE * 2.0)
        
        # We don't store these in the main grid_metrics, but the prompt asks for sensitivity in output
        # "sensitivity": repeat the REFERENCE_N cell once at NOISE x 0.5 and once at NOISE x 2.0, with the same threshold test.
        # The output format doesn't explicitly show where to put sensitivity values, but implies they are part of the process.
        # Looking at required keys: "sensitivity" is a key. Let's assume it's a list of the two metric values or a dict.
        # Re-reading: "sensitivity": repeat ... with the same threshold test.
        # It likely means we report the metric values or the p-values? 
        # Usually sensitivity analysis reports the resulting metric. Let's store the metric values.
        if r == 0:
            # Just to have an example structure if needed, but we need per-replication or aggregate?
            # "sensitivity" key in final JSON. Let's make it a list of dicts for the two conditions averaged over replications?
            # No, the loop is over replications. Let's collect them.
            pass
        # Actually, let's just collect them in a list for this replication if needed, 
        # but the final JSON asks for "sensitivity" (singular). 
        # Let's interpret as the metric values for the two noise levels averaged over replications?
        # Or maybe just the values from the first replication? 
        # "repeat the REFERENCE_N cell once ...". It sounds like part of the replication loop.
        # Let's store them in a list and average at the end.
        if 'sens_low' not in locals(): 
            sens_lows = []
            sens_highs = []
        sens_lows.append(val_low)
        sens_highs.append(val_high)

    # Calculate aggregates
    mean_val = float(np.mean(rep_values))
    ci_low, ci_high = float(np.percentile(rep_values, 2.5)), float(np.percentile(rep_values, 97.5))
    median_pval = float(np.median(rep_pvals))
    
    sig_share = float(np.mean([1 if p < P.ALPHA else 0 for p in rep_pvals]))
    
    if ALT == 'greater':
        dir_share = float(np.mean([1 if v >= P.THRESHOLD else 0 for v in rep_values]))
    else:
        dir_share = float(np.mean([1 if v <= P.THRESHOLD else 0 for v in rep_values]))
        
    # Grid cells average
    cells_out = []
    for n in P.GRID:
        avg_m = float(np.mean(grid_metrics[n]))
        cells_out.append({"n": n, "metric": avg_m, "trials": P.TRIALS})
        
    # Trend
    if len(P.GRID) < 2:
        trend = None
    else:
        correct_steps = 0
        total_steps = 0
        for i in range(len(P.GRID) - 1):
            n1, n2 = P.GRID[i], P.GRID[i+1]
            m1 = np.mean(grid_metrics[n1])
            m2 = np.mean(grid_metrics[n2])
            
            if P.METRIC_KIND == 'bias':
                predicted_increase = False # Bias should fall with N
                if m2 < m1: correct_steps += 1
            else:
                # Power/Coverage should rise with N
                if m2 > m1: correct_steps += 1
            total_steps += 1
        trend = float(correct_steps / total_steps) if total_steps > 0 else None
        
    # Sensitivity output: let's provide the average metric values for low and high noise
    sens_avg_low = float(np.mean(sens_lows))
    sens_avg_high = float(np.mean(sens_highs))
    sensitivity_out = {"noise_half": sens_avg_low, "noise_double": sens_avg_high}

    result = {
        "n": P.REFERENCE_N,
        "metric": P.METRIC_KIND,
        "test": f"one-sided ({ALT})",
        "alpha": P.ALPHA,
        "seed": P.SEED,
        "replications": P.REPLICATIONS,
        "value": mean_val,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": median_pval,
        "values": [float(v) for v in rep_values],
        "p_values": [float(p) for p in rep_pvals],
        "significant_share": sig_share,
        "direction_share": dir_share,
        "sensitivity": sensitivity_out,
        "cells": cells_out,
        "grid": P.GRID,
        "trend": trend
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()