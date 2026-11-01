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
    
    # Parameters from protocol
    n_snps = 1000
    n_valid = 100
    n_pleio = 100
    n_null = 800
    
    true_causal = EFFECT # 0.05
    pleio_corr = 0.3
    
    # 1. Generate Genotypes (G) ~ N(0,1) for N individuals x M SNPs
    # To save memory and time, we generate summary statistics directly or simulate efficiently.
    # Given N=50,000 and M=1,000, full matrix is 50M floats (~400MB), acceptable but tight.
    # We will simulate the GWAS summary statistics (Z-scores) which is standard for such power calcs,
    # OR simulate individual data if strictly required by "draw groups". 
    # The prompt says "draw the groups from the stated design". Let's simulate individual data to be safe.
    
    G = rng.standard_normal((N, n_snps))
    
    # 2. Define Effects
    # Valid: affect Health (Y1) only.
    # Pleio: affect Health (Y1) and Cognition (Y2).
    # Null: affect neither.
    
    # Effect sizes on Health (Y1)
    # Let's assume small effects for polygenic background, but we need specific instruments.
    # For simplicity in this simulation, we assign fixed effect sizes for the instrument sets.
    beta_g_y1 = np.zeros(n_snps)
    beta_g_y2 = np.zeros(n_snps) # Direct effect on Y2 (pleiotropy)
    
    # Assign effects to valid instruments (first 100)
    beta_g_y1[:n_valid] = 0.05 # Arbitrary strength for instruments
    
    # Assign effects to pleiotropic instruments (next 100)
    # They affect Y1 and Y2. Correlation 0.3 implies covariance structure.
    # Let's say effect on Y1 is similar, and direct effect on Y2 creates the correlation.
    beta_g_y1[n_valid:n_valid+n_pleio] = 0.05
    # Direct effect on Y2 to induce correlation. 
    # If Var(Y1) ~ 1, Var(Y2) ~ 1. Cov = 0.3.
    # We set direct effect such that it contributes to correlation.
    beta_g_y2[n_valid:n_valid+n_pleio] = 0.05 
    
    # 3. Generate Phenotypes
    # Y1 (Health) = G * beta_g_y1 + noise1
    # Y2 (Cognition) = Y1 * true_causal + G * beta_g_y2 + noise2
    
    noise1 = rng.standard_normal(N) * noise
    noise2 = rng.standard_normal(N) * noise
    
    Y1 = G @ beta_g_y1 + noise1
    Y2 = Y1 * true_causal + (G @ beta_g_y2) + noise2
    
    # 4. Apply Selection Bias (G+Y dependency)
    # Inclusion prob depends on G (specifically pleiotropic ones?) and Y.
    # Protocol: "inclusion probability depends on both Genotype (G) and Outcome (Y)"
    # Let's create a selection score S.
    # High selection for high Y2 and specific G patterns to induce bias.
    # Simple model: P(select) = logistic(a*Y2 + b*G_pleio_sum)
    
    # Sum of pleiotropic Gs
    G_pleio_sum = np.sum(G[:, n_valid:n_valid+n_pleio], axis=1)
    
    # Selection probability
    # We want to bias the sample such that standard methods fail.
    # Strong selection on Y2 and G_pleio.
    logit_p = 0.5 * Y2 + 0.5 * G_pleio_sum
    probs = 1 / (1 + np.exp(-logit_p))
    
    # To get a reasonable sample size or just mask? 
    # Protocol says "N=50,000 individuals... impose selection bias".
    # Usually this means we select a subset. But if N is fixed in sim_params, 
    # maybe we re-weight or the N in sim_params is the *selected* N?
    # "We simulate a GWAS scenario with N=50,000 individuals." -> This is likely the starting pool.
    # But sim_params.N is the only N we have. Let's assume sim_params.N is the final analyzed sample size
    # and we generate a larger pool then select, OR we generate N and apply weights.
    # Given the constraint "Read every number from sim_params", and N=50000 in protocol matches typical GWAS.
    # If we generate 50k and select 10%, N_eff drops.
    # Let's assume the provided N is the target analyzed N, so we generate a larger pool?
    # No, we cannot invent numbers. We must use P.N.
    # Interpretation: The study is performed on N individuals who have ALREADY been selected.
    # So we simulate the selection process implicitly by generating data with the biased distribution?
    # OR: We generate N, apply selection, and if we drop data, we have less power.
    # Let's try: Generate N, calculate selection probs, sample indices without replacement to keep N constant? 
    # No, that doesn't make sense.
    # Alternative: The "N" in sim_params is the size of the dataset we analyze. 
    # We simulate the bias by generating data where the correlation structure reflects the selection.
    # HOWEVER, the most faithful interpretation of "impose selection bias" in a simulation script 
    # where N is fixed is to generate a larger population and subset, but we can't invent the larger size.
    # Let's assume we generate N, and the "selection" is modeled as a weighting scheme or 
    # we simply generate N from the conditional distribution P(G,Y | Selected).
    # Approximation: Generate N, compute selection scores, and resample with replacement based on weights?
    # Or simpler: Just generate N, and the "bias" is inherent in the error term correlation induced by conditioning?
    # Let's do this: Generate N. Calculate selection probability. Resample N indices with probabilities proportional to P(select).
    # This maintains N but shifts the distribution.
    
    indices = rng.choice(N, size=N, p=probs/probs.sum())
    G_sel = G[indices]
    Y1_sel = Y1[indices]
    Y2_sel = Y2[indices]
    
    # 5. GWAS Summary Statistics Calculation
    # For each SNP, regress Y on G.
    # We need Z-scores or Beta/SE for MPD and IVW.
    
    betas_y1 = np.zeros(n_snps)
    ses_y1 = np.zeros(n_snps)
    betas_y2 = np.zeros(n_snps)
    ses_y2 = np.zeros(n_snps)
    
    for j in range(n_snps):
        g_vec = G_sel[:, j]
        # Simple linear regression: beta = cov(g,y)/var(g)
        # var(g) should be ~1
        var_g = np.var(g_vec, ddof=1)
        
        cov1 = np.cov(g_vec, Y1_sel, ddof=1)[0, 1]
        betas_y1[j] = cov1 / var_g
        ses_y1[j] = noise / np.sqrt(N * var_g) # Approx SE
        
        cov2 = np.cov(g_vec, Y2_sel, ddof=1)[0, 1]
        betas_y2[j] = cov2 / var_g
        ses_y2[j] = noise / np.sqrt(N * var_g)
        
    # Z-scores
    z1 = betas_y1 / ses_y1
    z2 = betas_y2 / ses_y2
    
    # 6. MPD Method (Multivariate Pleiotropy Detection simulation)
    # Protocol: "MPD methods systematically underestimate... reject valid instruments"
    # We need a heuristic for MPD rejection.
    # Typical MPD flags SNPs with heterogeneous effects or high residual in multivariate model.
    # Simplified MPD: Reject if |Z2| is large relative to expectation given Z1? 
    # Or if the SNP is an outlier in the joint distribution?
    # The claim is that it rejects VALID instruments due to bias.
    # Valid instruments should only affect Y1. In unbiased data, Z2 should be ~0 (only via causal path).
    # In selected data, spurious correlation makes Z2 non-zero for valid instruments.
    # MPD sees Z2 != 0 and flags as pleiotropic -> Rejects.
    
    # Heuristic: Reject if |Z2| > threshold (e.g., 1.96) OR if residual from IVW line is large.
    # Let's use a simple threshold on Z2 as a proxy for "detected pleiotropy".
    # Standard MPD might use a chi-sq test for heterogeneity.
    # Here: If |Z2| > 1.96, mark as invalid.
    
    rejected_mask = np.abs(z2) > 1.96
    
    # Calculate False Positive Rate (rejection of valid instruments)
    # Valid indices: 0 to 99
    valid_indices = np.arange