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
