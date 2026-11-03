"""Which stored rows are primary studies and which are reviews of them.

A pooled estimate from a meta-analysis is not another study. It is already a
combination of primary studies, so pooling it next to those studies enters the
same participants twice and lets the review's own model decide how loud they
speak. Measured on a real run, six of eight stored rows came from overviews and
the pool came out at -1.15 with an interval of -11.6 to 9.3, pulled down by a
network meta-analysis reporting SMD -2.02 - a number no trial of that field
supports.

The classification is deterministic and lives here rather than in one of its
callers, because pooling, the PRISMA counts and the coverage counter all have to
apply the same rule; three slightly different regexes would be three different
answers to "how many studies do we have".

Two deliberate limits:

* Only positive evidence excludes. An empty or unrecognised design stays a
  primary study - a missing field is a gap in the extraction, not a finding, and
  dropping rows for silence would hide them instead of counting them.
* The test is on the design label only. A row whose design reads
  "randomized controlled trial (meta-analysis of 37 RCTs)" is excluded: what it
  reports is the review's aggregate, not its own sample.
"""

from __future__ import annotations

import re

_AGGREGATE_DESIGN = re.compile(
    r"meta[\s\-_]?analy"        # meta-analysis, metaanalysis, meta analysis
    r"|systematic review"
    r"|scoping review"
    r"|umbrella review"
    r"|narrative review"
    r"|literature review"
    r"|pooled analysis"
    r"|quantitative synthesis",
    re.IGNORECASE,
)


# Auftrag v2 §2.2: the study design decides the variance semantics. Within-
# subject designs (crossover, repeated measures) pool on paired contrasts; an
# SE that came from an independent-groups formula would be too narrow here.
# The extractor never calculates, so every stored SE is verbatim from the text
# - but the PAIRED FAMILY is still marked, because a paired row sources its
# precision for a different estimand (the within-pair difference), and the
# pool must be able to say what mixture it holds instead of treating every row
# as independent. Categorisation is deterministic on the design label alone;
# order matters: the specific families are matched before the generic "RCT".
DESIGN_CATEGORIES_ORDER = (
    ("crossover_rct", re.compile(
        r"cros[s\- ]{0,2}over|within[-\s]?subject|within[-\s]?pair|paired"
        r"|repeated[-\s]?measures|messwiederholung", re.IGNORECASE)),
    ("cluster_rct", re.compile(r"cluster.random", re.IGNORECASE)),
    ("factorial", re.compile(r"factorial|faktoriell|2\s*[x×]\s*2", re.IGNORECASE)),
    ("multi_arm", re.compile(
        r"(?:multi|three|four|3|4)[-\s]?arm", re.IGNORECASE)),
    ("quasi_experimental", re.compile(
        r"quasi.experimental|pretest.posttest|non\.?randomi[sz]ed"
        r"|nonequivalent", re.IGNORECASE)),
    ("parallel_rct", re.compile(
        r"randomi[sz]ed|randomised|r\.c\.t", re.IGNORECASE)),
    ("observational", re.compile(
        r"cross.sectional|cohort|case.control|longitudinal|observational"
        r"|registry|survey", re.IGNORECASE)),
)

DESIGN_CATEGORY_LABELS = {
    "crossover_rct": "Crossover/Messwiederholung (paarig)",
    "cluster_rct": "Cluster-RCT",
    "factorial": "faktorielles Design",
    "multi_arm": "mehrarmige Studie",
    "quasi_experimental": "quasi-experimentell (nicht randomisiert)",
    "parallel_rct": "Parallelgruppen-RCT",
    "observational": "beobachtende Studie",
    "": "nicht klassifizierbar",
}

PAIRED_CATEGORIES = ("crossover_rct",)


def classify_design(design: str) -> str:
    """One of DESIGN_CATEGORY_LABELS' keys (or '' when nothing matched)."""
    text = str(design or "").strip()
    for category, pattern in DESIGN_CATEGORIES_ORDER:
        if pattern.search(text):
            return category
    return ""


def is_paired_design(design: str) -> bool:
    """True for the within-subject family: its precision belongs to a
    within-pair contrast, never to an independent-groups formula."""
    return classify_design(design) in PAIRED_CATEGORIES


def aggregate_design(design: str) -> str:
    """The review design a row's ``design`` names, or '' for a primary study."""
    text = str(design or "").strip()
    if not text:
        return ""
    match = _AGGREGATE_DESIGN.search(text)
    return match.group(0).strip().lower() if match else ""


def is_primary_study(row: dict) -> bool:
    """True when the row reports its own sample, not a combination of others."""
    return not aggregate_design(str((row or {}).get("design") or ""))
