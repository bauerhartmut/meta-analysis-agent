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
    
    # Design parameters derived from the protocol description
    n_snps = 10000
    n_causal = 500
    
    # Effect sizes from protocol
    # We scale the direct effect by the user-provided EFFECT parameter to satisfy the "scales with effect" requirement.
    # The protocol states direct effect is 0.1 for a baseline correlation of ~0.3.
    # We interpret EFFECT=1.0 as the standard scenario (direct=0.1), EFFECT=0.0 as null (direct=0.0).
    base_direct_effect = 0.1
    direct_effect_g = base_direct_effect * EFFECT
    
    effect_g_m = 0.5
    effect_m_c = 0.8
    effect_m_h = 0.8
    
    # 1. Generate G (Genotypes): N x n_snps matrix of standardized variants
    # Using standard normal for simplicity, representing standardized genotypes
    G = rng.standard_normal((N, n_snps))
    
    # 2. Generate M (Microbiome)
    # M is influenced by a subset of G (first n_causal SNPs)
    G_causal = G[:, :n_causal]
    # Sum of effects
    genetic_component_m = np.sum(G_causal * effect_g_m, axis=1)
    # Add noise to M. Scale noise to maintain signal-to-noise ratio roughly consistent with protocol intent
    # Protocol implies strong mediation, so M should be well-predicted by G_causal.
    # Variance of signal: n_causal * 0.5^2 = 500 * 0.25 = 125.
    # We add noise scaled by the input 'noise' parameter.
    noise_m = rng.standard_normal(N) * noise * 5.0 # Scaling factor to make 'noise' parameter meaningful
    M = genetic_component_m + noise_m
    
    # 3. Generate C (Cognition) and H (Health)
    # Both are influenced by M (mediation) and directly by G (direct pleiotropy)
    
    # Mediation component
    med_c = M * effect_m_c
    med_h = M * effect_m_h
    
    # Direct component (only from causal SNPs for simplicity, or all? Protocol says "same G variants")
    # "The same G variants also have a small direct effect"
    direct_c = np.sum(G_causal * direct_effect_g, axis=1)
    direct_h = np.sum(G_causal * direct_effect_g, axis=1)
    
    # Noise for C and H
    # To achieve initial correlation ~0.3 when EFFECT=1, we need to balance variances.
    # But the key is that the *change* in correlation is the metric.
    # We add noise scaled by the input 'noise' parameter.
    noise_c = rng.standard_normal(N) * noise * 10.0
    noise_h = rng.standard_normal(N) * noise * 10.0
    
    C = med_c + direct_c + noise_c
    H = med_h + direct_h + noise_h
    
    # Standardize phenotypes for correlation analysis
    C = (C - np.mean(C)) / np.std(C)
    H = (H - np.mean(H)) / np.std(H)
    M = (M - np.mean(M)) / np.std(M)
    
    # Create a genetic score (G_score) to represent the aggregate genetic influence
    # Using the sum of the causal SNPs as the score
    G_score = np.sum(G_causal, axis=1)
    G_score = (G_score - np.mean(G_score)) / np.std(G_score)
    
    # --- Analysis Step 1: Raw Association ---
    # We look at the association between C and H, or rather the genetic correlation proxy.
    # The protocol says: "Calculate the raw genetic correlation... without M"
    # And "Metric: The difference in the correlation coefficient (Raw - Adjusted)"
    # Actually, the prediction is about the correlation between C and H being driven by G via M.
    # Let's interpret the "genetic correlation" here as the correlation between C and H 
    # that is attributable to genetics. 
    # However, the simplest interpretation of "adjusting for M reduces correlation between C and H"
    # is to look at corr(C, H) vs partial_corr(C, H | M).
    # But the protocol mentions "regression coefficient of G-score on C predicting H".
    # Let's stick to the most robust interpretation of the mediation hypothesis:
    # Does M explain the correlation between C and H?
    # Raw correlation between C and H
    raw_corr, _ = stats.pearsonr(C, H)
    
    # --- Analysis Step 2: Adjusted Association ---
    # Partial correlation between C and H controlling for M
    # Or: Regress C on M, Regress H on M, then correlate residuals.
    res_C = stats.linregress(M, C).resid
    res_H = stats.linregress(M, H).resid
    
    adj_corr, _ = stats.pearsonr(res_C, res_H)
    
    # Metric: Change in correlation
    metric_value = raw_corr - adj_corr
    
    # Significance Test:
    # We need to test if the "mediation" is significant.
    # The protocol says: "significance tested via t-test on the residual correlation"
    # This is slightly ambiguous. Usually, we test if the reduction is significant.
    # Alternatively, we test if the adjusted correlation is significantly different from zero?
    # No, the prediction is "reduce ... to non-significance".
    # The falsification is "does not significantly alter".
    # So we test if the *difference* (metric_value) is significantly different from 0.
    # How to get a p-value for the difference in correlations?
    # A common approach in simulation checks is to test the path significance or use a bootstrap.
    # Given constraints, let's use a proxy: The significance of the M->C and M->H paths ensures mediation.
    # But the prompt asks for a specific test structure.
    # Let's re-read: "significance tested via t-test on the residual correlation".
    # Maybe it means: Test if the residual correlation (adj_corr) is significantly different from the raw?
    # Or test if adj_corr is 0?
    # Let's assume the test is on the *mediation effect*.
    # If EFFECT=0, direct_effect_g=0. Then C and H are only connected via M (which is connected to G).
    # Wait, if direct_effect_g=0, C and H are STILL correlated because M affects both.
    # The hypothesis is "Microbiome-Mediated Horizontal Pleiotropy drives the observed genetic correlation".
    # If we remove M, the correlation due to G should vanish IF the only link was via M.
    # In our model: G -> M -> C and G -> M -> H.
    # If we control for M, the path G->M->C/H is blocked.
    # But C and H are still correlated because they share M as a common cause?
    # No, if we control for M, the correlation induced by M should disappear.
    # The "Direct effect" creates a correlation NOT mediated by M.
    # So:
    # Raw Corr(C,H) ~ Corr(M-induced) + Corr(Direct-induced)
    # Adj Corr(C,H) | M ~ Corr(Direct-induced) (since M-induced is removed)
    # Metric = Raw - Adj ~ Corr(M-induced).
    # If EFFECT=0 (no direct effect), then Adj Corr should be 0 (noise only).
    # Raw Corr should be high (due to M).
    # Metric should be high (~Raw).
    # If EFFECT is large, Adj Corr is large. Metric is smaller?
    # Wait, the prediction says: "reduce ... from ~0.3 to non-significance".
    # This implies the Raw is ~0.3 (driven by M) and Adj is ~0.
    # This happens if the Direct effect is 0 (or very small).
    # The falsification: "Controlling ... does not significantly alter ... (remains ~0.3)".
    # This implies if the mechanism is wrong, M doesn't explain the correlation.
    #
    # So, if EFFECT=0 (no direct pleiotropy), the entire correlation is mediated by M.
    # Removing M should kill the correlation. Metric = Raw - 0 = Raw (large).
    # If the hypothesis is false (M is irrelevant), then Raw ~ Adj, Metric ~ 0.
    #
    # How to test significance of the metric?
    # We can test if the adjusted correlation is significantly different from the raw correlation.
    # Or simpler: Test if the adjusted correlation is zero? No, that tests the remainder.
    # We need to test if the *reduction* is significant.
    # In the context of the "known-answer test" failure described:
    # "no effect means no finding": If EFFECT=0, we expect a "finding" (rejection of null that metric=0).
    # Wait, the user says: "no effect means no finding: 4/5 runs significant at effect 0".
    # This implies that when EFFECT=0, the code was returning "significant" (p < 0.05).
    # But the expectation for a valid test under the NULL hypothesis (no effect of interest) is