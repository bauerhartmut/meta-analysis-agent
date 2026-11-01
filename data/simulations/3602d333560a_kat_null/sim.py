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
    n_snps = 100
    G = rng.normal(0, 1, size=(N, n_snps))
    w_m = rng.normal(0, 1, n_snps)
    M = G @ w_m + rng.normal(0, noise, N)
    w_y1 = rng.normal(0, 1, n_snps)
    Y1 = G @ w_y1 + rng.normal(0, noise, N)
    beta_true = EFFECT
    Y2 = beta_true * M + rng.normal(0, noise, N)
    
    G_mean = G.mean(axis=0)
    G_std = G.std(axis=0)
    G_std[G_std == 0] = 1.0
    G_z = (G - G_mean) / G_std
    
    G_sum = G_z.sum(axis=1)
    
    X_naive = np.column_stack((np.ones(N), G_sum))
    beta_naive = np.linalg.lstsq(X_naive, Y2, rcond=None)[0][1]
    
    X_adj = np.column_stack((np.ones(N), G_sum, M))
    beta_adj = np.linalg.lstsq(X_adj, Y2, rcond=None)[0][1]
    
    estimate = beta_naive - beta_adj
    se = noise / np.sqrt(N)
    t_stat = estimate / se if se > 0 else 0.0
    p = 2 * (1 - stats.norm.cdf(abs(t_stat)))
    return estimate, float(p)

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
value = float(np.mean(val_arr))
ci_low = float(np.percentile(val_arr, 2.5))
ci_high = float(np.percentile(val_arr, 97.5))
p_value = float(np.median(p_values))
significant_share = float(np.mean([1 if p < ALPHA else 0 for p in p_values]))
direction_share = float(np.mean([1 if v > 0 else 0 for v in values]))

result = {
    "n": N,
    "metric": "Difference in causal effect estimates (Naive Beta - Adjusted Beta)",
    "test": "Two-sided z-test on attenuation",
    "alpha": ALPHA,
    "seed": SEED,
    "replications": REPLICATIONS,
    "value": value,
    "ci_low": ci_low,
    "ci_high": ci_high,
    "p_value": p_value,
    "values": values,
    "p_values": p_values,
    "significant_share": significant_share,
    "direction_share": direction_share,
    "sensitivity": sensitivity
}

print(json.dumps(result))