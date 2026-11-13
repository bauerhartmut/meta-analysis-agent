"""Shared rules for a human review decision.

These checks are intentionally stricter than a status flag.  A field is only
approved when it has a present value and a stored evidence row that actually
contains that value in the named field.  The same helper is used by the review
store, the finalizer and the pooling gate.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .compare import evidence_supports


def has_value(value: Any) -> bool:
    """A zero is a valid value; an absent or blank value is not."""
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    return True


def evidence_for_value(record: Dict[str, Any], field: str, value: Any,
                       evidence_id: str = "") -> Optional[Dict[str, Any]]:
    """Return stored evidence only if it supports the value for this field."""
    key = str(evidence_id or "").strip()
    if not key:
        return None
    evidence = (record.get("evidence") or {}).get(key)
    if not evidence:
        return None
    declared = str(evidence.get("field") or "")
    if declared and declared != field:
        return None
    if not evidence_supports(evidence, field, value):
        return None
    return evidence


def field_is_verified(record: Dict[str, Any], name: str) -> bool:
    """Check the full approval condition, not only the status label."""
    entry = (record.get("fields") or {}).get(name) or {}
    if str(entry.get("status")) != "verified":
        return False
    # A documented "not reported" is allowed without a numeric value.
    if entry.get("reported") is False:
        return True
    value = entry.get("final_value")
    if not has_value(value):
        return False
    return evidence_for_value(
        record, name, value, str(entry.get("evidence_id") or "")
    ) is not None
