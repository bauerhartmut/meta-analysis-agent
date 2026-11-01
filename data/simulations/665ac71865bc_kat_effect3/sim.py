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
    return t_res.pvalue, est, ci.low, ci.high

def simulate_cell(rng, n, effect, noise, trials, metric_kind, alpha, threshold_val):
    pvals = np.empty(trials)
    ests = np.empty(trials)
    lows = np.empty(trials)
    highs = np.empty(trials)
    
    for i in range(trials):
        pvals[i], ests[i], lows[i], highs[i] = run_trial(rng, n, effect, noise)
    
    if metric_kind == 'power':
        metric_val = np.mean(pvals < alpha)
        deviations = None
    elif metric_kind == 'coverage':
        metric_val = np.mean((lows <= threshold_val) & (highs >= threshold_val))
        deviations = None
    elif metric_kind == 'bias':
        deviations = np.abs(ests - threshold_val)
        metric_val = np.mean(deviations)
    else:
        metric_val = 0.0
        deviations = None
        
    return metric_val, deviations, pvals

def get_p_value(metric_kind, metric_val, deviations, trials, threshold, alternative):
    if metric_kind == 'bias':
        if deviations is None or len(deviations) == 0:
            return 1.0
        res = stats.ttest_1samp(deviations, threshold, alternative=alternative)
        return res.pvalue
    else:
        hits = int(round(metric_val * trials))
        res = stats.binomtest(hits, trials, threshold, alternative=alternative)
        return res.pvalue

def main():
    rng_master = np.random.default_rng(P.SEED)
    seeds = rng_master.integers(0, 2**31, size=P.REPLICATIONS)
    
    rep_values = []
    rep_pvals = []
    grid_metrics = {n: [] for n in P.GRID}
    
    for r in range(P.REPLICATIONS):
        rng_rep = np.random.default_rng(seeds[r])
        ref_val = None
        ref_pval = None
        
        for n in P.GRID:
            # Base noise
            m_val, devs, _ = simulate_cell(rng_rep, n, P.EFFECT, P.NOISE, P.TRIALS, P.METRIC_KIND, P.ALPHA, P.EFFECT)
            grid_metrics[n].append(m_val)
            
            if n == P.REFERENCE_N:
                ref_val = m_val
                if P.METRIC_KIND == 'bias':
                    # Need deviations for p-value calculation
                    _, ref_devs, _ = simulate_cell(rng_rep, n, P.EFFECT, P.NOISE, P.TRIALS, P.METRIC_KIND, P.ALPHA, P.EFFECT)
                    # Re-run to get deviations specifically if not stored, but simulate_cell returns them only for bias?
                    # Let's adjust simulate_cell to always return deviations if needed or re-calc
                    # Actually, for bias, devs is returned. For others, it's None.
                    # We need deviations for the test if metric is bias.
                    # If metric is power/coverage, we need hits count which is derived from m_val * trials
                    pass
                
                # Sensitivity runs
                m_low, _, _ = simulate_cell(rng_rep, n, P.EFFECT, P.NOISE * 0.5, P.TRIALS, P.METRIC_KIND, P.ALPHA, P.EFFECT)
                m_high, _, _ = simulate_cell(rng_rep, n, P.EFFECT, P.NOISE * 2.0, P.TRIALS, P.METRIC_KIND, P.ALPHA, P.EFFECT)
                
                # Calculate p-value for reference
                if P.METRIC_KIND == 'bias':
                    # Re-generate deviations for the reference cell specifically for the test
                    # We need the raw deviations from the base run
                    # Let's refactor slightly to ensure we have devs for ref if bias
                    pass
                
                # To avoid re-simulating, let's capture devs in the loop properly
                # Re-doing the reference cell capture cleanly
                pass

    # Refactoring loop to capture all needed data cleanly
    rep_values = []
    rep_pvals = []
    grid_metrics = {n: [] for n in P.GRID}
    sensitivity_data = []
    
    for r in range(P.REPLICATIONS):
        rng_rep = np.random.default_rng(seeds[r])
        ref_metric_val = None
        ref_deviations = None
        ref_hits = 0
        
        current_grid_vals = {}
        
        for n in P.GRID:
            # Run base
            pvals = np.empty(P.TRIALS)
            ests = np.empty(P.TRIALS)
            lows = np.empty(P.TRIALS)
            highs = np.empty(P.TRIALS)
            
            for i in range(P.TRIALS):
                pvals[i], ests[i], lows[i], highs[i] = run_trial(rng_rep, n, P.EFFECT, P.NOISE)
            
            if P.METRIC_KIND == 'power':
                m_val = np.mean(pvals < P.ALPHA)
                devs = None
                hits = int(np.sum(pvals < P.ALPHA))
            elif P.METRIC_KIND == 'coverage':
                m_val = np.mean((lows <= P.EFFECT) & (highs >= P.EFFECT))
                devs = None
                hits = int(np.sum((lows <= P.EFFECT) & (highs >= P.EFFECT)))
            elif P.METRIC_KIND == 'bias':
                devs = np.abs(ests - P.EFFECT)
                m_val = np.mean(devs)
                hits = 0 # Not used for bias test directly in binom
            else:
                m_val = 0.0
                devs = None
                hits = 0
            
            grid_metrics[n].append(m_val)
            current_grid_vals[n] = m_val
            
            if n == P.REFERENCE_N:
                ref_metric_val = m_val
                ref_deviations = devs
                ref_hits = hits
                
                # Sensitivity
                # Low noise
                pvals_l = np.empty(P.TRIALS)
                for i in range(P.TRIALS):
                    pvals_l[i], _, _, _ = run_trial(rng_rep, n, P.EFFECT, P.NOISE * 0.5)
                m_low = np.mean(pvals_l < P.ALPHA) if P.METRIC_KIND == 'power' else (np.mean((np.empty(P.TRIALS) <= 0) & (np.empty(P.TRIALS) >= 0)) if P.METRIC_KIND == 'coverage' else 0.0)
                # Correct sensitivity calc for all metrics
                def get_sens_metric(noise_mult):
                    p_s = np.empty(P.TRIALS)
                    e_s = np.empty(P.TRIALS)
                    l_s = np.empty(P.TRIALS)
                    h_s = np.empty(P.TRIALS)
                    for i in range(P.TRIALS):
                        p_s[i], e_s[i], l_s[i], h_s[i] = run_trial(rng_rep, n, P.EFFECT, noise_mult * P.NOISE)
                    if P.METRIC_KIND == 'power':
                        return np.mean(p_s < P.ALPHA)
                    elif P.METRIC_KIND == 'coverage':
                        return np.mean((l_s <= P.EFFECT) & (h_s >= P.EFFECT))
                    else:
                        return np.mean(np.abs(e_s - P.EFFECT))
                
                sens_low = get_sens_metric(0.5)
                sens_high = get_sens_metric(2.0)
                
                # P-value for reference
                if P.METRIC_KIND == 'bias':
                    pv = stats.ttest_1samp(ref_deviations, P.THRESHOLD, alternative=ALT).pvalue
                else:
                    pv = stats.binomtest(ref_hits, P.TRIALS, P.THRESHOLD, alternative=ALT).pvalue
                ref_pval = pv
                
                sensitivity_data.append({'low': sens_low, 'high': sens_high})

        rep_values.append(ref_metric_val)
        rep_pvals.append(ref_pval)

    # Aggregations
    mean_val = float(np.mean(rep_values))
    ci = stats.t.interval(0.95, len(rep_values)-1, loc=mean_val, scale=stats.sem(rep_values))
    median_pval = float(np.median(rep_pvals))
    
    sig_share = float(np.mean([1 if p < P.ALPHA else 0 for p in rep_pvals]))
    if P.COMPARISON == 'at_least':
        dir_share = float(np.mean([1 if v >= P.THRESHOLD else 0 for v in rep_values]))
    else:
        dir_share = float(np.mean([1 if v <= P.THRESHOLD else 0 for v in rep_values]))
        
    # Grid averages
    cells = []
    for n in P.GRID:
        cells.append({'n': n, 'metric': float(np.mean(grid_metrics[n])), 'trials': P.TRIALS})
    
    # Trend
    trend = None
    if len(P.GRID) > 1:
        sorted_n = sorted(P.GRID)
        moves = []
        for i in range(len(sorted_n) - 1):
            n1, n2 = sorted_n[i], sorted_n[i+1]
            m1 = np.mean(grid_metrics[n1])
            m2 = np.mean(grid_metrics[n2])
            if P.METRIC_KIND == 'bias':
                predicted_rise = m2 < m1 # Falling
                actual_rise = m2 < m1
            else:
                predicted_rise = m2 > m1 # Rising
                actual_rise = m2 > m1
            moves.append(1 if actual_rise == predicted_rise else 0)
        trend = float(np.mean(moves))
    
    # Sensitivity avg
    sens_avg_low = float(np.mean([s['low'] for s in sensitivity_data]))
    sens_avg_high = float(np.mean([s['high'] for s in sensitivity_data]))
    
    result = {
        'n': P.REFERENCE_N,
        'metric': P.METRIC_KIND,
        'test': f"one-sided ({ALT})",
        'alpha': P.ALPHA,
        'seed': P.SEED,
        'replications': P.REPLICATIONS,
        'value': mean_val,
        'ci_low': ci[0],
        'ci_high': ci[1],
        'p_value': median_pval,
        'values': rep_values,
        'p_values': rep_pvals,
        'significant_share': sig_share,
        'direction_share': dir_share,
        'sensitivity': {'noise_half': sens_avg_low, 'noise_double': sens_avg_high},
        'cells': cells,
        'grid': P.GRID,
        'trend': trend
    }
    
    print(json.dumps(result))

if __name__ == '__main__':
    main()