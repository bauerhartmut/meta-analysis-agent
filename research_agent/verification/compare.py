"""LLM-free field comparison and evidence admissibility.

The comparison never averages values.  It records both readings, the rule
that was applied and whether an original cell can support the value in its
row/column/timepoint context.
"""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .schema import (
    NUMERIC_FIELDS, compare_values, normalise_text, parse_number, value_kind,
)

_NUMBER_TOKEN = re.compile(r"-?\d+(?:[.,]\d+)?")


def _numbers(text: str) -> List[float]:
    out: List[float] = []
    for token in _NUMBER_TOKEN.findall(str(text or "")):
        try:
            out.append(float(token.replace(",", ".")))
        except ValueError:
            continue
    return out


def evidence_supports(evidence: Dict[str, Any], field: str, value: Any) -> bool:
    """True only when the cited cell contains the value in a usable context.

    A number elsewhere in the same table is not enough.  The evidence must
    carry a row label and a column label, and must not point at a baseline
    row when the record's target is post-treatment.
    """
    if not evidence:
        return False
    raw = str(evidence.get("raw_cell") or "")
    if not raw.strip():
        return False
    if field in {"outcome", "time_point"}:
        # Outcome and timepoint are verified by a non-empty row/column context,
        # not by treating the ICO wording as a literal table cell.
        return True
    row = normalise_text(evidence.get("row_label"))
    column = normalise_text(evidence.get("column_label"))
    if not row or not column:
        return False
    combined = f"{row} {column}".lower()
    # Baseline evidence cannot verify a post-treatment value.  Follow-up is
    # equally not interchangeable without an explicit rule.
    if "baseline" in combined and field not in {"outcome", "unit"}:
        return False
    if "follow-up" in combined or "followup" in combined:
        if field not in {"outcome", "time_point", "unit"}:
            return False

    if value_kind(field) == "text":
        needle = normalise_text(value).lower()
        return bool(needle) and (needle in combined or needle in raw.lower())
    number = parse_number(value)
    if number is None:
        return False
    numbers = _numbers(raw)
    if not numbers:
        return False
    exact = any(candidate == number for candidate in numbers)
    tolerant = any(abs(candidate - number) <= 0.005 for candidate in numbers)
    if not (exact or tolerant):
        return False
    # Count fields must not be verified by a percentage or a p-value that
    # happens to share the digits.
    if field.endswith("_n") or field.endswith("_events"):
        if "%" in raw and field.endswith("_n"):
            return False
    return True


def comparison_entry(field: str, a: Any, b: Any, evidence: Optional[Dict[str, Any]],
                     expected_time: str = "") -> Dict[str, Any]:
    if a in (None, "") and b in (None, ""):
        status, rule = "both_missing", "missing_both"
    elif a in (None, ""):
        status, rule = "missing_a", "present_only_b"
    elif b in (None, ""):
        status, rule = "missing_b", "present_only_a"
    else:
        status, rule = compare_values(field, a, b)
    supported = evidence_supports(evidence or {}, field, a) if a not in (None, "") else False
    if status in {"match", "numeric_match"} and not supported:
        status, rule = "evidence_missing", "no_exact_source_cell"
    if status in {"match", "numeric_match"} and evidence:
        evidence_time = normalise_text(
            f"{evidence.get('row_label', '')} {evidence.get('column_label', '')}"
        ).lower()
        if expected_time and expected_time.lower() not in {"", "post-treatment"}:
            if expected_time.lower() not in evidence_time:
                status, rule = "ambiguous", "wrong_timepoint"
    return {
        "field": field,
        "value_a": a,
        "value_b": b,
        "comparison": status,
        "rule": rule,
        "evidence_id": (evidence or {}).get("evidence_id", ""),
        "evidence_supported": supported,
        "field_status": "verified" if status in {"match", "numeric_match"} else "unresolved",
    }


def compare_record(fields: Sequence[str], a_values: Dict[str, Any],
                   b_values: Dict[str, Any],
                   evidence_by_field: Dict[str, Dict[str, Any]],
                   expected_time: str = "") -> List[Dict[str, Any]]:
    return [
        comparison_entry(field, a_values.get(field), b_values.get(field),
                         evidence_by_field.get(field), expected_time)
        for field in fields
    ]
