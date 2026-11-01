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
    """
    Simulates GWAS summary statistics for two traits to estimate genetic correlation.
    
    Architecture:
    - Background: 990,000 SNPs with small independent effects (true rg = 0.05).
    - MHC Hotspot: 10,000 SNPs with large correlated effects designed to drive total rg.
    
    The 'EFFECT' parameter from sim_params controls the magnitude of the MHC contribution.
    If EFFECT is 0, the MHC region contributes no correlation, leaving only the background (0.05).
    If EFFECT is > 0, the MHC region drives the total correlation up (targeting ~0.3 when EFFECT=1.0).
    
    The metric is the method-of-moments genetic correlation estimated from z-scores.
    The test compares the full estimate vs the excluded estimate, but the returned 'value'
    is the estimated genetic correlation of the EXCLUDED set (to test if it drops below 0.1).
    However, per the prompt's requirement to return a single value/p-value for the study,
    we will structure the return as:
      - estimate: The genetic correlation of the EXCLUDED set (the primary claim test).
      - p-value: Testing if the excluded rg is significantly different from the background (0.05) 
                 OR testing if the reduction is significant. 
                 
    Actually, looking at the standard scientific output required:
    "value" = mean estimate over replications.
    "p_value" = median p-value.
    
    Let's refine the specific hypothesis test for the p-value.
    Claim: Excluding MHC reduces rg to < 0.1.
    Falsification: rg_excluded >= 0.1.
    
    We will calculate rg_full and rg_excluded.
    The returned 'value' will be rg_excluded.
    The returned 'p_value' will be from a test checking if rg_excluded is significantly less than 0.1?
    No, usually we test against the null of no difference or a specific value.
    Given the "known-answer test failed" message in the prompt ("no effect means no finding"),
    it implies that when EFFECT=0, the result should be non-significant regarding the "drop" or 
    the value should be consistent with the background.
    
    Let's stick to the most robust interpretation:
    We estimate rg_excluded.
    We perform a Z-test to see if rg_excluded is significantly greater than the background truth (0.05)?
    Or simply return the estimate and a p-value for the hypothesis that rg_excluded == 0?
    
    Let's re-read the failure mode: "5/5 runs significant at effect 0".
    This implies the previous code was finding a "significant drop" or "significant effect" even when none existed.
    If EFFECT=0, the MHC region has no special correlation. The whole genome is just background (rg=0.05).
    Removing a random chunk (MHC) should leave rg ~ 0.05.
    If the test claims "rg dropped to < 0.1", and the result is 0.05, that is a "success" of the claim?
    Wait, the claim is "Inflation... is driven by MHC".
    If EFFECT=0, there is no inflation. The claim is false (or rather, the premise is false).
    The prediction is "Excluding MHC will reduce rg... to below 0.1".
    If EFFECT=0, rg_full is ~0.05. rg_excluded is ~0.05.
    Did it reduce to below 0.1? Yes, it was already there.
    But the *causal claim* ("driven by") is what's being tested.
    
    Let's look at the "Falsification condition": "Removing immune-related loci does not significantly alter the genetic correlation".
    So the statistical test should be: Is rg_full significantly different from rg_excluded?
    Or: Is the drop (rg_full - rg_excluded) significantly greater than 0?
    
    If EFFECT=0: rg_full ~ 0.05, rg_excluded ~ 0.05. Drop ~ 0. Test should be non-significant.
    If EFFECT=1.0: rg_full ~ 0.3, rg_excluded ~ 0.05. Drop ~ 0.25. Test should be significant.
    
    This matches the failure description: "no effect means no finding".
    So:
    Value = rg_excluded (or the drop? The prompt says "estimate is centred on zero without an effect").
    If the estimate is centered on zero without an effect, the metric is likely the DROP (rg_full - rg_excluded).
    Let's assume the metric returned is the DROP in genetic correlation.
    Null hypothesis: Drop = 0.
    Alternative: Drop > 0.
    
    Implementation details:
    Total SNPs = 1,000,000.
    MHC = 10,000.
    Background = 990,000.
    h2 = 0.2 for both. N = 500,000.
    Sampling variance of z-score ~ 1.
    Var(beta_hat) = Var(beta) + 1/N_eff? 
    Actually, z = beta_hat / se. se ~ 1/sqrt(N).
    Let's simulate z-scores directly.
    z = sqrt(N * h2 / M) * effect_vector + noise.
    
    Background correlation = 0.05.
    MHC correlation = driven by EFFECT.
    Target total rg = 0.3 when EFFECT=1.0.
    rg_total = (sum(cov_i)) / sqrt(sum(var_i_x) * sum(var_i_y)).
    Since variances are normalized by design usually in these sims, rg is average correlation weighted by variance.
    Let's simplify:
    Generate true effects (beta_x, beta_y) for all SNPs.
    Background: bivariate normal, rho=0.05.
    MHC: bivariate normal, rho_high. Scale determined by EFFECT.
    If EFFECT=0, MHC rho = 0.05 (same as background).
    If EFFECT=1.0, MHC rho is set such that total rg = 0.3.
    
    Then generate observed z-scores: z = beta * sqrt(N) + epsilon, where epsilon ~ N(0,1).
    Estimate rg using method of moments: sum(zx * zy) / (M * 1) ? 
    Actually, E[zx*zy] = N * cov(beta_x, beta_y) + 0 (noise independent).
    So sum(zx*zy)/N approximates sum(cov).
    We need to normalize by variances.
    E[zx^2] = N * var(beta_x) + 1.
    rg_est = sum(zx*zy) / sqrt( (sum(zx^2)-M) * (sum(zy^2)-M) ).
    
    Let's code this.
    """
    
    rng = np.random.default_rng(seed)
    
    M_total = 1000000
    M_mhc = 10000
    M_bg = M_total - M_mhc
    
    h2 = 0.2
    # Effective N for z-score scaling. Assuming N=500,000 is the sample size per trait.
    # Z = beta * sqrt(N) / se_beta? 
    # Standard GWAS: z ~ N(beta * sqrt(N), 1) if beta is standardized and h2 is small?
    # More precisely: var(z) = N * h2 / M + 1.
    # Let's scale effects such that sum(var(beta)) = h2.
    # var(beta_per_snp) = h2 / M.
    # Then expected chi2 = N * h2 / M + 1.
    
    scale_bg = np.sqrt(h2 / M_bg)
    
    # Background effects
    # Cov matrix for background: [[1, 0.05], [0.05, 1]] * var_beta
    # We generate standard normals and correlate them.
    z_bg_x = rng.standard_normal(M_bg)
    z_bg_y = rng.standard_normal(M_bg)
    # Induce correlation 0.05
    # y = rho * x + sqrt(1-rho^2) * e
    rho_bg = 0.05
    z_bg_y_corr = rho_bg * z_bg_x + np.sqrt(1 - rho_bg**2) * z_bg_y
    
    beta_bg_x = z_bg_x * scale_bg
    beta_bg_y = z_bg_y_corr * scale_bg
    
    # MHC effects
    # If EFFECT == 0, rho_mhc = rho_bg.
    # If EFFECT > 0, we need to calculate rho_mhc to achieve total rg = 0.3.
    # Total Cov = M_bg * cov_bg + M_mhc * cov_mhc
    # Total Var X = M_bg * var_bg + M_mhc * var_mhc
    # Assuming var_bg = var_mhc = h2/M_total? No, MHC effects are "large".
    # The prompt says: "MHC Hotspot ... with large, highly correlated effects ... scaled to drive total observed genetic correlation to exactly 0.3".
    # It doesn't explicitly say the variance per SNP is larger, just that the correlation is