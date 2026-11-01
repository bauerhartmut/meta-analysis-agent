import json
import numpy as np
from scipy import stats
import sim_params as P

ALT = 'greater' if P.COMPARISON == 'at_least' else 'less'

def run_trial(rng, n, noise, effect, selection_func):
    """
    Simulates one trial of the collider bias study.
    1. Generate population with independent G_cog, G_health.
    2. Apply selection probability S based on G scores.
    3. Calculate observed genetic correlation and MR estimate in selected sample.
    Returns: (mr_estimate, genetic_correlation, absolute_deviation_mr)
    """
    # We need to oversample to ensure we get 'n' selected participants after filtering
    # Selection probability can be low depending on the function, so we generate a large pool.
    # A safe factor is 10x or until we have enough.
    target = n
    factor = 15
    current_n = int(target * factor)
    
    while True:
        # Generate independent genetic scores (standard normal)
        g_cog = rng.standard_normal(current_n)
        g_health = rng.standard_normal(current_n)
        
        # True effect is 0 per protocol ("null true effect"), but we pass 'effect' for completeness
        # Phenotypes: Y_health = 0 * G_cog + error (Null causal effect)
        # However, the protocol mentions "0.05 SD biased effect" as the *prediction* of the bias.
        # The true causal effect in the population is 0.
        true_causal_effect = 0.0
        
        # Generate phenotypes with noise
        # Cognition phenotype (X) driven by G_cog
        x = g_cog + rng.standard_normal(current_n) * noise
        # Health phenotype (Y) driven by G_health (and potentially X if causal, but here causal is 0)
        y = true_causal_effect * x + g_health + rng.standard_normal(current_n) * noise
        
        # Calculate selection probability S
        # Protocol: "selection probability S based on the interaction or sum of these scores"
        # To induce strong collider bias creating positive correlation from independent sources:
        # Select if (G_cog + G_health) is high, or similar mechanism.
        # Let's use a logistic function of the sum or product to create a smooth probability.
        # Using sum: S = 1 / (1 + exp(-(g_cog + g_health - threshold)))
        # To get ~0.3 correlation and 0.05 bias, the selection needs to be strong on the upper tail.
        # Let's define S based on the sum exceeding a quantile or a logistic curve.
        # Protocol says: "high G_cog AND high G_health increases participation" -> Interaction/Sum.
        
        z = g_cog + g_health
        # Normalize z to have mean 0, std sqrt(2) approx 1.414. 
        # Let's set a threshold that selects roughly top 20-30% to ensure n is reachable but bias is strong.
        # Using a logistic function centered at 1.0 (approx top 25% of sum dist)
        probs = 1.0 / (1.0 + np.exp(-(z - 1.0)))
        
        selected_mask = rng.random(current_n) < probs
        n_selected = np.sum(selected_mask)
        
        if n_selected >= target:
            # Take exactly 'n' samples from the selected ones
            selected_indices = np.where(selected_mask)[0][:target]
            g_cog_sel = g_cog[selected_indices]
            g_health_sel = g_health[selected_indices]
            x_sel = x[selected_indices]
            y_sel = y[selected_indices]
            break
        else:
            # Increase pool size and retry
            factor *= 2
            current_n = int(target * factor)

    # Calculate Genetic Correlation (r_g) in selected sample
    # Since G_cog and G_health are the direct genetic scores, we compute correlation between them
    # in the selected sample. In the population they are independent (r=0).
    if np.std(g_cog_sel) == 0 or np.std(g_health_sel) == 0:
        r_g = 0.0
    else:
        r_g = np.corrcoef(g_cog_sel, g_health_sel)[0, 1]
        if np.isnan(r_g):
            r_g = 0.0

    # Calculate MR Estimate (IVW slope)
    # IVW slope = Cov(G, Y) / Cov(G, X) where G is the instrument for X (G_cog)
    # Simple regression of Y on X using G_cog as instrument? 
    # Actually, in a simple one-sample MR with one instrument: beta_IV = Cov(G_cog, Y) / Cov(G_cog, X)
    cov_gy = np.cov(g_cog_sel, y_sel, ddof=1)[0, 1]
    cov_gx = np.cov(g_cog_sel, x_sel, ddof=1)[0, 1]
    
    if abs(cov_gx) < 1e-12:
        mr_estimate = 0.0
    else:
        mr_estimate = cov_gy / cov_gx

    # The metric for "bias" kind in this context:
    # Protocol prediction: "reproduce ... 0.05 SD biased effect".
    # So the estimate should be around 0.05.
    # The "deviation" for the bias metric calculation in the skeleton is |estimate - EFFECT|.
    # Here EFFECT (from sim_params) is set to 0.05 in the protocol JSON ("effect": 0.05).
    # Wait, the protocol says "true causal effect is zero" but prediction is 0.05.
    # The sim_params.EFFECT is the "true effect" in the skeleton description, but in this specific
    # collider study, the "EFFECT" parameter in sim_params likely represents the *predicted* biased value
    # we are testing against (0.05), or the user sets EFFECT=0.0 (true) and THRESHOLD=0.05?
    # Let's re-read the skeleton requirement: "bias = mean(|estimate - EFFECT|)".
    # And the protocol JSON has "effect": 0.05. This suggests EFFECT in sim_params is the target value (0.05).
    # So we calculate deviation from 0.05.
    deviation = abs(mr_estimate - P.EFFECT)

    return mr_estimate, r_g, deviation

def cell(seed, n, noise):
    rng = np.random.default_rng(seed)
    
    estimates = [] # Stores MR estimates
    correlations = [] # Stores genetic correlations
    deviations = [] # Stores |MR_estimate - EFFECT|
    
    # We run TRIALS inner studies
    for _ in range(P.TRIALS):
        mr_est, r_g, dev = run_trial(rng, n, noise, P.EFFECT, None)
        estimates.append(mr_est)
        correlations.append(r_g)
        deviations.append(dev)
    
    estimates = np.array(estimates)
    correlations = np.array(correlations)
    deviations = np.array(deviations)
    
    # Determine the primary metric value for this cell based on METRIC_KIND
    # The protocol says metric is "Mean estimated causal effect (beta) and genetic correlation".
    # But the simulation framework expects a single scalar per trial for aggregation?
    # The skeleton computes 'metric' as an aggregate over trials.
    # If METRIC_KIND is 'bias', the skeleton expects the metric to be the mean absolute deviation.
    # However, the prediction is about the *value* of the effect (0.05).
    # Let's align with the skeleton's 'bias' definition: metric = mean(|estimate - EFFECT|).
    # But wait, the hypothesis test is against THRESHOLD (0.05). 
    # If the simulation works, the mean estimate should be 0.05.
    # If METRIC_KIND is 'bias', the skeleton calculates mean(|est - EFFECT|). 
    # If EFFECT=0.05 and the sim produces 0.05, the bias metric (MAD) should be near 0.
    # But the test is "at_least 0.05"? That doesn't fit MAD.
    
    # Re-evaluating based on the specific Protocol JSON provided in the prompt:
    # "metric_kind": "bias", "threshold": 0.05, "comparison": "at_least", "effect": 0.05
    # This implies we are testing if the *estimated effect* is at least 0.05?
    # Or is the "metric" in the JSON output the mean estimated effect?
    # The skeleton code for 'bias' returns `mean(|estimate - EFFECT|)`.
    # If the user wants to test if the bias *exists* and is *at least* 0.05, then the metric should be the mean estimate itself, not the deviation.
    # BUT the skeleton strictly defines: bias = mean(|estimate - EFFECT|).
    # And the test for bias in skeleton: ttest_1samp(deviations, THRESHOLD).
    # This implies we are testing if the *error* is at least 0.05? That contradicts the goal of reproducing a specific bias.
    
    # Let's look at the "Prediction": "reproduce ... 0.05 SD biased effect".
    # If the true effect is 0, and we observe 0.05, the bias is 0.05.
    # If sim_params.EFFECT is the TRUE effect (0.0), then |estimate - 0.0| = estimate.
    # Then mean(|estimate|) = 0.05.
    # And we test if this mean is >= 0.05 (THRESHOLD).
    # This fits perfectly IF sim_params.EFFECT is 0.0.
    # However, the provided JSON has "effect": 0.05.
    # If EFFECT=0.05, and we calculate |estimate - 0.05|, and the estimate is 0.05, the result is 0.
    # Then testing if 0 >= 0.05 fails.
    
    # Hypothesis: The provided JSON in the prompt might have "effect": 0.05 as the *predicted* value,
    # but the code logic assumes EFFECT is the *true* parameter for data generation.
    # The protocol text says: "true causal effect is zero".
    # So inside `run_trial`, I must use 0.0 for the true effect regardless of P.EFFECT?
    # Yes, the protocol design says: "null true effect".
    # So `true_causal_effect = 0.0` in `run_trial` is correct.
    # Now, what is P.EFFECT used for in the skeleton?
    # Skeleton: `deviations.append(abs(est - P.EFFECT))`.
    # If P.EFFECT is 0.05 (from JSON), and our estimate is 0.05, deviation is 0.
    # This seems wrong for the test "at_least 0.05".
    
    # Alternative interpretation: The "bias" metric in the skeleton is generic.
    # For this specific study, we want to measure the *magnitude of the spurious effect*.
    # The spurious effect is `mr_estimate` (since true is 0).
    # So we want to test if `mean(mr_estimate)` >= 0.05.
    # The skeleton forces `deviations = |est - EFFECT|`.
    # If we set EFFECT=0.0 in the params, it works. But the JSON says 0.05.
    # Maybe the JSON "effect" field is the *target* and the code should treat the "true effect" as 0 internally?
    # The skeleton uses P.EFFECT for data generation: `rng.normal(P.EFFECT, noise, n)`.
    # I am NOT using the skeleton's data generation. I am implementing the collider design.
    # In my design, true effect is 0.
    # So `est` is the biased estimate.
    # If I want to test if the bias is >= 0.05, I need the metric to be `mean(est)`.
    # But the skeleton calculates `mean(|est - P.EFFECT|)`.
    # If P.EFFECT is 0.0 (true effect), then `mean(|est - 0|) = mean(est)` (assuming est > 0).
    # Then testing against THRESHOLD=0.05 makes sense.
    # Conclusion: The JSON provided in the prompt might be illustrative or the user expects the code to handle the discrepancy.
    # HOWEVER, the instruction says: "Read every number from sim_params... Never hardcode them".
    # If P.EFFECT is 0.05, and I compute |est - 0.05|, and est is 0.05, I get 0.
    # Then testing 0 >= 0.05 fails.
    # Perhaps the "Prediction" is that the bias *magnitude* is 0.05, so the *deviation from null* is 0.05.
    # If the "null" is 0, then EFFECT should be 0.
    # Let's assume the sim_params.EFFECT in the actual run will be 0.0 (the true effect) for the logic to hold,
    # OR the metric calculation needs to be adapted to the "meta" design type?
    # No, the skeleton is fixed logic for metric calculation.
    # Wait, the reviewer said: "The script hardcodes the logic for a two-sample t-test design... incompatible with 'meta' design type".
    # Maybe for 'meta' design type, the metric calculation is different?
    # The skeleton doesn't branch on design_type for the metric formula.
    # Let's stick to the skeleton's formula: `bias = mean(|estimate - EFFECT|)`.
    # If the study is about reproducing a bias of 0.05 from a null (0), then:
    # True Effect = 0. Estimate = 0