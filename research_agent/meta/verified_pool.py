"""Hard release gate in front of the existing, unchanged pooling module.

This module does not rewrite `meta.pooling`.  It filters/refuses rows and only
then calls `build_analysis`, so an unverified record cannot enter the primary
pool by accident.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from . import pooling


class UnverifiedRecordError(ValueError):
    """Raised when an unverified record is offered to the primary analysis."""


def _status_for(state: Dict[str, Any], record_id: str) -> Tuple[str, str]:
    record = (state.get("records") or {}).get(record_id)
    if not record:
        return "missing", "kein Verifikationsrecord"
    status = str(record.get("status") or "")
    if status != "verified":
        return status or "unverified", str(record.get("status_reason") or "nicht verifiziert")
    open_fields = [
        name for name in (record.get("required_fields") or [])
        if str((record.get("fields") or {}).get(name, {}).get("status")) != "verified"
    ]
    if open_fields:
        return "pending_review", "offene Pflichtfelder: " + ", ".join(open_fields)
    return "verified", ""


def gate_rows(rows: Iterable[Dict[str, Any]], verification_state: Dict[str, Any],
              id_field: str = "verification_record_id",
              allow_unverified: bool = False) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """Split rows into verified and refused; refusal is loud by default.

    `allow_unverified=True` is for a report that explicitly wants to show the
    refused rows, not for a primary analysis: even then the refused rows are
    returned separately and never passed to pooling.
    """
    accepted: List[Dict[str, Any]] = []
    refused: List[Dict[str, str]] = []
    for row in rows or ():
        # Never infer a verification from a generic record_id: the caller must
        # attach the explicit verification key.  A silent fallback could let a
        # row with the same study ID but no verification slip through.
        record_id = str(row.get(id_field) or "")
        status, reason = _status_for(verification_state, record_id)
        if not record_id:
            status, reason = "missing_id", "Zeile traegt keine Verifikations-ID"
        label = str(row.get("label") or row.get("source_id") or record_id)
        if status == "verified":
            accepted.append(row)
        else:
            refused.append({"record_id": record_id, "label": label,
                            "status": status, "reason": reason})
    if refused and not allow_unverified:
        detail = "; ".join(
            f"{item['record_id']} ({item['status']}: {item['reason']})"
            for item in refused[:5]
        )
        raise UnverifiedRecordError(
            f"Pooling verweigert: {len(refused)} nicht verifizierte Records. {detail}"
        )
    return accepted, refused


def build_verified_analysis(rows: Iterable[Dict[str, Any]],
                            verification_state: Dict[str, Any],
                            outcomes: Optional[Sequence[str]] = None,
                            targets: Optional[Dict] = None,
                            allow_unverified: bool = False) -> Dict[str, Any]:
    """The only supported entry point from verification into pooling."""
    accepted, refused = gate_rows(rows, verification_state,
                                  allow_unverified=allow_unverified)
    analysis = pooling.build_analysis(accepted, outcomes=outcomes, targets=targets)
    analysis["verification_gate"] = {
        "input_rows": len(accepted) + len(refused),
        "verified_rows": len(accepted),
        "refused_rows": len(refused),
        "refused": refused,
        "policy": "only verified records may enter the primary pool",
    }
    return analysis


def verification_report(verification_state: Dict[str, Any]) -> Dict[str, Any]:
    """Transparent counts for the report, including human-review burden."""
    records = list((verification_state.get("records") or {}).values())
    counts = {status: 0 for status in
              ("extracted", "cross_checked", "pending_review", "verified", "rejected")}
    for record in records:
        counts[str(record.get("status") or "extracted")] += 1
    human = sum(1 for record in records if record.get("decisions"))
    return {
        "total_extracted": len(records),
        "cross_checked": counts["cross_checked"] + counts["pending_review"]
        + counts["verified"] + counts["rejected"],
        "verified": counts["verified"],
        "rejected": counts["rejected"],
        "unresolved": counts["pending_review"],
        "human_reviewed": human,
        "human_share": round(human / len(records), 4) if records else 0.0,
        "by_status": counts,
    }
