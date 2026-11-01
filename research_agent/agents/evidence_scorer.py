"""
Evidence Quality Scorer - Objective evaluation of research evidence.

Scores studies on:
1. Study Design Quality (RCT > Cohort > Case-Control > Case Report > Expert Opinion)
2. Sample Size Impact (larger = more reliable)
3. Effect Size Significance (practical significance)
4. Methodological Rigor (blinding, controls, peer review)
5. Source Credibility (journal impact, replication status)

This replaces subjective "supports/contradicts" with nuanced evidence weighting.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Study design hierarchy (higher = better)
STUDY_DESIGN_SCORES = {
    "meta_analysis": 1.0,
    "systematic_review": 0.95,
    "rct": 0.9,           # Randomized Controlled Trial
    "randomized": 0.9,
    "cohort": 0.75,
    "prospective": 0.75,
    "longitudinal": 0.7,
    "cross_sectional": 0.5,
    "case_control": 0.6,
    "case_series": 0.3,
    "case_report": 0.2,
    "expert_opinion": 0.1,
    "editorial": 0.1,
    "commentary": 0.1,
    "preprint": 0.4,
    "review": 0.7,
    "twin_study": 0.8,
    "gwas": 0.85,
}

# Keywords indicating methodological features
QUALITY_POSITIVE_KEYWORDS = [
    "randomized", "double-blind", "placebo-controlled", "peer-reviewed",
    "replicated", "large-scale", "population-based", "prospective",
    "longitudinal", "meta-analysis", "systematic review", "pre-registered",
    "blinded", "controlled", "cohort study", "multi-center",
    "dose-response", "statistically significant", "confidence interval",
    "effect size", "power analysis", "adjusted for confounders",
]

QUALITY_NEGATIVE_KEYWORDS = [
    "preliminary", "small sample", "anecdotal", "uncontrolled",
    "retrospective", "self-reported", "survivorship bias", "cherry-picked",
    "correlation only", "no control group", "selection bias",
    "publication bias", "p-hacking", "underpowered", "confounded",
    "conflict of interest", "industry funded", "retracted",
]


class EvidenceScorer:
    """Scores evidence quality on multiple dimensions."""

    def score_study_design(self, text: str) -> Tuple[float, str]:
        """
        Detect study design from text and return quality score.
        Returns (score, detected_design).
        """
        text_lower = text.lower()

        # Check for specific designs in order of specificity
        design_patterns = [
            (r"meta.analysis", "meta_analysis"),
            (r"systematic.review", "systematic_review"),
            (r"randomized.control|randomised.control|rct\b", "rct"),
            (r"double.blind|placebo.control", "rct"),
            (r"gwas|genome.wide.association", "gwas"),
            (r"twin.study|twin.analysis|twin.data", "twin_study"),
            (r"cohort.study|prospective.cohort", "cohort"),
            (r"longitudinal.study", "longitudinal"),
            (r"cross.sectional", "cross_sectional"),
            (r"case.control", "case_control"),
            (r"case.report|case.series", "case_report"),
            (r"preprint", "preprint"),
            (r"expert.opinion|editorial|commentary", "expert_opinion"),
        ]

        for pattern, design in design_patterns:
            if re.search(pattern, text_lower):
                return STUDY_DESIGN_SCORES.get(design, 0.5), design

        return 0.4, "unknown"

    def score_sample_size(self, text: str) -> Tuple[float, str]:
        """
        Extract sample size and score it.
        Returns (score, description).
        """
        text_lower = text.lower()

        # Try to find explicit sample sizes
        patterns = [
            (r"n\s*=\s*([\d,]+)", 1.0),
            (r"sample\s*(?:size|of)\s*:?\s*([\d,]+)", 1.0),
            (r"([\d,]+)\s*(?:participants|subjects|individuals|participants)", 1.0),
            (r"([\d,]+)\s*(?:patients|cases|controls)", 1.0),
            (r"([\d,]+)\s*(?:twins|pairs)", 1.0),
            (r"([\d,]+)\s*(?:snps|loci|variants)", 0.8),
            (r"([\d,]+)\s*individuals", 1.0),
        ]

        for pattern, confidence in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    n = int(match.group(1).replace(",", ""))
                    if n >= 100000:
                        return 1.0, f"Very large (n={n:,})"
                    elif n >= 10000:
                        return 0.9, f"Large (n={n:,})"
                    elif n >= 1000:
                        return 0.75, f"Moderate (n={n:,})"
                    elif n >= 100:
                        return 0.5, f"Small (n={n:,})"
                    elif n >= 30:
                        return 0.3, f"Very small (n={n:,})"
                    else:
                        return 0.15, f"Tiny (n={n:,})"
                except ValueError:
                    continue

        # Heuristic based on descriptive terms
        large_terms = ["large-scale", "population-based", "large cohort",
                       "nationwide", "international", "multi-center"]
        medium_terms = ["cohort", "registered", "moderate"]
        small_terms = ["small", "pilot", "preliminary", "few", "limited"]

        for term in large_terms:
            if term in text_lower:
                return 0.8, f"Large-scale (heuristic)"

        for term in small_terms:
            if term in text_lower:
                return 0.3, f"Small (heuristic)"

        return 0.5, "Unknown size"

    def score_effect_size(self, text: str) -> Tuple[float, str]:
        """
        Extract and evaluate effect sizes.
        Returns (score, description).
        """
        text_lower = text.lower()

        # Heritability estimates (h² or h2) - common in genetics
        h2_match = re.search(r"h\s*(?:²|2)\s*[=:]\s*([\d.]+)", text_lower)
        if h2_match:
            try:
                h2 = float(h2_match.group(1))
                if h2 > 0.8:
                    return 1.0, f"Very high heritability (h²={h2})"
                elif h2 > 0.6:
                    return 0.85, f"High heritability (h²={h2})"
                elif h2 > 0.4:
                    return 0.7, f"Moderate heritability (h²={h2})"
                elif h2 > 0.2:
                    return 0.5, f"Low heritability (h²={h2})"
                else:
                    return 0.3, f"Very low heritability (h²={h2})"
            except ValueError:
                pass

        # Cohen's d or effect size
        d_match = re.search(r"(?:cohen'?s?\s*)?d\s*[=:]\s*([\d.]+)", text_lower)
        if d_match:
            try:
                d = float(d_match.group(1))
                if d >= 0.8:
                    return 1.0, f"Large effect (d={d})"
                elif d >= 0.5:
                    return 0.75, f"Medium effect (d={d})"
                elif d >= 0.2:
                    return 0.5, f"Small effect (d={d})"
                else:
                    return 0.3, f"Negligible effect (d={d})"
            except ValueError:
                pass

        # Odds ratios
        or_match = re.search(r"odds?\s*ratio\s*[=:]\s*([\d.]+)", text_lower)
        if or_match:
            try:
                or_val = float(or_match.group(1))
                if or_val >= 3.0:
                    return 0.9, f"Strong association (OR={or_val})"
                elif or_val >= 1.5:
                    return 0.6, f"Moderate association (OR={or_val})"
                else:
                    return 0.3, f"Weak association (OR={or_val})"
            except ValueError:
                pass

        # p-values
        p_match = re.search(r"p\s*[<>=]\s*([\d.]+)", text_lower)
        if p_match:
            try:
                p = float(p_match.group(1))
                if p < 0.001:
                    return 0.8, f"Very significant (p<0.001)"
                elif p < 0.01:
                    return 0.7, f"Significant (p<0.01)"
                elif p < 0.05:
                    return 0.5, f"Significant (p<0.05)"
                else:
                    return 0.2, f"Not significant (p={p})"
            except ValueError:
                pass

        # Fallback: look for qualitative descriptions
        strong_terms = ["strong", "significant", "robust", "consistent", "clear"]
        weak_terms = ["weak", "modest", "small", "marginal", "tenuous"]

        for term in strong_terms:
            if term in text_lower:
                return 0.65, f"Strong (qualitative)"

        for term in weak_terms:
            if term in text_lower:
                return 0.35, f"Weak (qualitative)"

        return 0.5, "Effect size not reported"

    def score_methodological_rigor(self, text: str) -> Tuple[float, str]:
        """Score methodological quality indicators."""
        text_lower = text.lower()
        score = 0.5  # Base score
        features = []

        # Positive indicators
        for keyword in QUALITY_POSITIVE_KEYWORDS:
            if keyword in text_lower:
                score += 0.05
                features.append(f"+{keyword}")

        # Negative indicators
        for keyword in QUALITY_NEGATIVE_KEYWORDS:
            if keyword in text_lower:
                score -= 0.08
                features.append(f"-{keyword}")

        # Cap between 0 and 1
        score = max(0.0, min(1.0, score))

        desc = f"Rigor score: {score:.2f}"
        if features:
            desc += f" ({', '.join(features[:5])})"

        return score, desc

    def score_source_credibility(self, source_info: Dict) -> Tuple[float, str]:
        """Score source credibility based on metadata."""
        score = 0.5
        factors = []

        source_type = source_info.get("source_type", "").lower()

        # Source type scoring
        type_scores = {
            "arxiv": 0.6,       # Preprint, not peer-reviewed
            "pubmed": 0.8,      # Peer-reviewed medical
            "semantic_scholar": 0.7,
            "openalex": 0.7,
            "web": 0.4,
            "duckduckgo": 0.3,
        }
        if source_type in type_scores:
            score = type_scores[source_type]
            factors.append(f"type:{source_type}")

        # Check for known high-quality sources
        title = source_info.get("title", "").lower()
        url = source_info.get("url", "").lower()

        high_quality = [
            "nature", "science", "lancet", "nejm", "bmj", "jama",
            "cell", "pnas", "psychological science", "intelligence",
            "behavior genetics", "twin research", "genome biology",
            "american journal of human genetics", "nature genetics",
        ]
        for journal in high_quality:
            if journal in title or journal in url:
                score = min(1.0, score + 0.2)
                factors.append(f"journal:{journal}")
                break

        return score, f"Credibility: {score:.2f} ({', '.join(factors)})" if factors else f"Credibility: {score:.2f}"

    def compute_composite_score(
        self,
        text: str,
        source_info: Optional[Dict] = None,
        evidence_type: str = "neutral",
    ) -> Dict:
        """
        Compute comprehensive evidence quality score.
        
        Returns dict with:
        - composite_score: weighted average (0.0 to 1.0)
        - study_design: (score, description)
        - sample_size: (score, description)
        - effect_size: (score, description)
        - rigor: (score, description)
        - credibility: (score, description)
        - quality_label: 'high', 'moderate', 'low', 'very_low'
        - confidence_modifier: how much to adjust belief (multiplier)
        """
        design_score, design_desc = self.score_study_design(text)
        sample_score, sample_desc = self.score_sample_size(text)
        effect_score, effect_desc = self.score_effect_size(text)
        rigor_score, rigor_desc = self.score_methodological_rigor(text)

        cred_score, cred_desc = 0.5, "No source info"
        if source_info:
            cred_score, cred_desc = self.score_source_credibility(source_info)

        # Weighted composite
        composite = (
            design_score * 0.25
            + sample_score * 0.20
            + effect_score * 0.20
            + rigor_score * 0.15
            + cred_score * 0.20
        )

        # Evidence type adjustment
        if evidence_type == "contradicts":
            # Contradicting evidence from high-quality studies is MORE valuable
            composite = min(1.0, composite * 1.15)
        elif evidence_type == "supports":
            # Confirmation bias check: supporting evidence slightly discounted
            composite = composite * 0.95

        # Quality label
        if composite >= 0.8:
            quality_label = "high"
            confidence_modifier = 1.2
        elif composite >= 0.6:
            quality_label = "moderate"
            confidence_modifier = 1.0
        elif composite >= 0.4:
            quality_label = "low"
            confidence_modifier = 0.7
        else:
            quality_label = "very_low"
            confidence_modifier = 0.4

        return {
            "composite_score": round(composite, 3),
            "study_design": {"score": design_score, "description": design_desc},
            "sample_size": {"score": sample_score, "description": sample_desc},
            "effect_size": {"score": effect_score, "description": effect_desc},
            "rigor": {"score": rigor_score, "description": rigor_desc},
            "credibility": {"score": cred_score, "description": cred_desc},
            "quality_label": quality_label,
            "confidence_modifier": confidence_modifier,
        }

    def score_evidence_batch(
        self, evidence_list: List[Dict], source_cache: Optional[Dict] = None
    ) -> List[Dict]:
        """Score a batch of evidence items and return enhanced records."""
        source_cache = source_cache or {}
        scored = []

        for ev in evidence_list:
            content = ev.get("content", "")
            source_id = ev.get("source_id", "")
            evidence_type = ev.get("evidence_type", "neutral")
            source_info = source_cache.get(source_id, {})

            scores = self.compute_composite_score(
                content, source_info=source_info, evidence_type=evidence_type
            )

            # Merge scores into evidence record
            enhanced = dict(ev)
            enhanced["quality_scores"] = scores
            enhanced["weighted_strength"] = (
                ev.get("strength", 0.5) * scores["confidence_modifier"]
            )
            scored.append(enhanced)

        return scored
