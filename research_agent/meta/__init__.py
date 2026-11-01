"""Quantitative synthesis of published studies.

The pieces are deliberately separate:

* :mod:`research_agent.meta.extraction` reads effect sizes out of a paper and
  stores them with the sentence they came from.
* :mod:`research_agent.meta.pooling` combines stored numbers (random effects,
  heterogeneity, subgroups, bias checks) and knows nothing about the model.
* :mod:`research_agent.meta.screening` keeps the review frame: a frozen protocol
  and recorded inclusion/exclusion decisions, so a count of pooled studies can be
  traced back.
* :mod:`research_agent.meta.targets` turns the research question into the outcome
  measures the synthesis is aimed at, so rows about the same construct end up in
  one group instead of two groups of one study each.

What this is not: a systematic review. There is no registration, no risk-of-bias
instrument and no human double coding - the limitations section of the report says
so instead of implying otherwise.
"""

from .extraction import EffectExtractor, check_plausibility, derive_se
from .grade import grade_group
from .risk_of_bias import (
    VERSION as ROB_ASSESSOR_VERSION, BiasAssessor, domains_for_design,
    overall_rating,
)
from .pooling import build_analysis, egger, forest_table, leave_one_out, pool, subgroups
from .screening import (
    build_protocol, prisma_counts, protocol_path, record_automatic_decisions,
    record_decision, write_protocol,
)
from .targets import (
    build_targets, canonical_outcome, coverage, load_targets, save_targets,
    target_labels,
)

__all__ = [
    "EffectExtractor", "check_plausibility", "derive_se",
    "build_analysis", "pool", "subgroups", "leave_one_out", "egger", "forest_table",
    "build_protocol", "write_protocol", "protocol_path", "record_decision",
    "record_automatic_decisions", "prisma_counts",
    "build_targets", "canonical_outcome", "coverage", "load_targets",
    "save_targets", "target_labels",
]
