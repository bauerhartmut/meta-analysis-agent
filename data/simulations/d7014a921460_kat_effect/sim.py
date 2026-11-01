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
    
    L = 10000
    T = 10
    r_mate = 0.4
    h2 = 0.5
    
    G1 = rng.normal(0, 1, (N, L))
    G2 = rng.normal(0, 1, (N, L))
    
    b1 = rng.normal(0, 1, L) / np.sqrt(L)
    b2 = rng.normal(0, 1, L) / np.sqrt(L)
    
    for _ in range(T):
        A1 = G1 @ b1
        A2 = G2 @ b2
        
        E1 = rng.normal(0, np.sqrt((1-h2)/h2), N)
        E2 = rng.normal(0, np.sqrt((1-h2)/h2), N)
        
        P1 = A1 + E1
        P2 = A2 + E2
        
        P1_s = (P1 - np.mean(P1)) / np.std(P1)
        P2_s = (P2 - np.mean(P2)) / np.std(P2)
        P_avg = (P1_s + P2_s) / 2
        
        idx = np.argsort(P_avg)
        G1_sorted = G1[idx]
        G2_sorted = G2[idx]
        
        G1_next = np.empty_like(G1)
        G2_next = np.empty_like(G2)
        
        for i in range(0, N, 2):
            if i + 1 >= N:
                G1_next[i] = G1_sorted[i]
                G2_next[i] = G2_sorted[i]
                continue
            
            p1, p2 = G1_sorted[i], G1_sorted[i+1]
            m1, m2 = G2_sorted[i], G2_sorted[i+1]
            
            mask1 = rng.random(L) < 0.5
            c1 = np.where(mask1, p1, p2)
            c2 = np.where(mask1, p2, p1)
            
            mask2 = rng.random(L) < 0.5
            d1 = np.where(mask2, m1, m2)
            d2 = np.where(mask2, m2, m1)
            
            G1_next[i] = c1
            G1_next[i+1] = c2
            G2_next[i] = d1
            G2_next[i+1] = d2
            
        G1 = G1_next
        G2 = G2_next
    
    A1_final = G1 @ b1
    A2_final = G2 @ b2
    
    estimate = np.corrcoef(A1_final, A2_final)[0, 1]
    
    t_stat, p = stats.ttest_1samp([estimate], popmean=0.0)
    
    return float(estimate), float(p)

values, p_values = [], []
for i in range(REPLICATIONS):
    v, p = run(SEED + i, NOISE)
    values.append(v)
    p_values.append(p)

sensitivity = []
for mult in (0.5, 2.0):
    v, p = run(SEED, NOISE * mult)
    sensitivity.append({'noise_multiplier': mult, 'value': v, 'p_value': p})

val_arr = np.array(values)
value_mean = float(np.mean(val_arr))
ci_low = float(np.percentile(val_arr, 2.5))
ci_high = float(np.percentile(val_arr, 97.5))
p_median = float(np.median(p_values))
sig_share = float(np.mean([1 if p < ALPHA else 0 for p in p_values]))
dir_share = float(np.mean([1 if v > 0 else 0 for v in values]))

result = {
    "n": N,
    "metric": "Pearson correlation coefficient between additive genetic values",
    "test": "One-sample t-test against null 0",
    "alpha": ALPHA,
    "seed": SEED,
    "replications": REPLICATIONS,
    "value": value_mean,
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