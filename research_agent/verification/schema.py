"""Schema and status rules for evidence-based record verification.

The module deliberately contains no model call and no database access.  It is
the single place that decides what a valid status transition is and which
fields a record must carry before it may be called verified.
"""

from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Optional

SCHEMA_VERSION = "record-verification/1"

RECORD_STATUSES = (
    "extracted",
    "cross_checked",
    "pending_review",
    "verified",
    "rejected",
)

FIELD_STATUSES = (
    "extracted",
    "cross_checked",
    "verified",
    "rejected",
    "unresolved",
)

COMPARISON_STATUSES = (
    "match",
    "numeric_match",
    "mismatch",
    "missing_a",
    "missing_b",
    "both_missing",
    "evidence_missing",
    "ambiguous",
)

CONTINUOUS_FIELDS = (
    "intervention_n",
    "intervention_mean",
    "intervention_sd",
    "comparator_n",
    "comparator_mean",
    "comparator_sd",
)

BINARY_FIELDS = (
    "intervention_n",
    "intervention_events",
    "comparator_n",
    "comparator_events",
)

NUMERIC_FIELDS = frozenset({
    "intervention_n", "comparator_n",
    "intervention_mean", "comparator_mean",
    "intervention_sd", "comparator_sd",
    "intervention_events", "comparator_events",
})

COUNT_FIELDS = frozenset({
    "intervention_n", "comparator_n",
    "intervention_events", "comparator_events",
})

TEXT_FIELDS = frozenset({"outcome", "time_point", "unit"})

# A single, explicit comparison tolerance.  It is absolute and intentionally
# tiny: it accepts only a difference that can arise from printing the same
# number with different decimal places (for example 0.333 vs 0.33).  It is not
# a licence to treat 25.4 and 25.44 as the same measurement.
NUMERIC_TOLERANCE = 0.005

FIELD_LABELS = {
    "intervention_n": "Interventionsgruppe N",
    "comparator_n": "Kontrollgruppe N",
    "intervention_mean": "Interventionsgruppe Mittelwert",
    "comparator_mean": "Kontrollgruppe Mittelwert",
    "intervention_sd": "Interventionsgruppe SD",
    "comparator_sd": "Kontrollgruppe SD",
    "intervention_events": "Interventionsgruppe Ereignisse",
    "comparator_events": "Kontrollgruppe Ereignisse",
    "outcome": "Outcome",
    "time_point": "Messzeitpunkt",
    "unit": "Einheit",
}

_RECORD_TRANSITIONS = {
    "extracted": {"cross_checked", "rejected"},
    "cross_checked": {"pending_review", "verified", "rejected"},
    "pending_review": {"verified", "rejected"},
    "verified": {"cross_checked", "pending_review", "rejected"},
    "rejected": {"pending_review"},
}

_FIELD_TRANSITIONS = {
    "extracted": {"cross_checked", "rejected"},
    "cross_checked": {"verified", "rejected", "unresolved"},
    "verified": {"cross_checked", "unresolved", "rejected"},
    "rejected": {"cross_checked", "unresolved"},
    "unresolved": {"cross_checked", "verified", "rejected"},
}


def required_fields(outcome_type: str) -> tuple[str, ...]:
    """The numeric fields a record must account for, by outcome type."""
    return CONTINUOUS_FIELDS if str(outcome_type).lower() == "continuous" else BINARY_FIELDS


def can_transition_record(old: str, new: str) -> bool:
    if old == new:
        return True
    return new in _RECORD_TRANSITIONS.get(str(old), set())


def can_transition_field(old: str, new: str) -> bool:
    if old == new:
        return True
    return new in _FIELD_TRANSITIONS.get(str(old), set())


def transition_record(old: str, new: str) -> str:
    if new not in RECORD_STATUSES:
        raise ValueError(f"unbekannter Recordstatus: {new}")
    if not can_transition_record(old, new):
        raise ValueError(f"unzulaessiger Recordstatuswechsel: {old} -> {new}")
    return new


def transition_field(old: str, new: str) -> str:
    if new not in FIELD_STATUSES:
        raise ValueError(f"unbekannter Feldstatus: {new}")
    if not can_transition_field(old, new):
        raise ValueError(f"unzulaessiger Feldstatuswechsel: {old} -> {new}")
    return new


def parse_number(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def value_kind(field: str) -> str:
    if field in COUNT_FIELDS:
        return "count"
    if field in NUMERIC_FIELDS:
        return "number"
    return "text"


def normalise_text(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def compare_values(field: str, a: Any, b: Any) -> tuple[str, str]:
    """Return (comparison_status, applied_rule) for two extraction values.

    Missingness is handled before this function by the workflow, so this
    compares two present values.  Text is compared case-insensitively after
    whitespace normalisation; counts must be equal integers; numbers may be
    equal within NUMERIC_TOLERANCE.
    """
    kind = value_kind(field)
    if kind == "text":
        left, right = normalise_text(a).casefold(), normalise_text(b).casefold()
        return ("match", "text_normalised_exact") if left == right else (
            "mismatch", "text_normalised_exact")
    left, right = parse_number(a), parse_number(b)
    if left is None or right is None:
        return "ambiguous", "non_numeric_value"
    if kind == "count":
        if not float(left).is_integer() or not float(right).is_integer():
            return "ambiguous", "count_not_integer"
        if int(left) == int(right):
            return "match", "integer_exact"
        return "mismatch", "integer_exact"
    if left == right:
        return "match", "numeric_exact"
    if abs(left - right) <= NUMERIC_TOLERANCE:
        return "numeric_match", f"absolute_tolerance_{NUMERIC_TOLERANCE}"
    return "mismatch", f"absolute_tolerance_{NUMERIC_TOLERANCE}"


def fields_for_record(record: Dict) -> List[str]:
    fields = list(required_fields(record.get("outcome_type", "continuous")))
    for optional in ("outcome", "time_point", "unit"):
        if record.get(optional) not in (None, ""):
            fields.append(optional)
    return fields


def missing_field_reason(value: Any) -> str:
    return "field_missing" if value in (None, "") else ""


def any_unresolved(fields: Iterable[Dict]) -> bool:
    return any(str(field.get("status")) in {"rejected", "unresolved"} for field in fields)
