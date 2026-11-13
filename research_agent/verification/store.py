"""Append-only audit store for verified records.

No event is overwritten.  Each event carries the hash of its predecessor, so
removing or silently editing an earlier decision breaks the chain.  The
current state is a replay of the events; a snapshot is written for fast
loading, but the journal remains the authority.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .schema import (
    FIELD_STATUSES, RECORD_STATUSES, SCHEMA_VERSION, can_transition_field,
    can_transition_record, transition_field, transition_record,
)
from .review import evidence_for_value, has_value

AUDIT_VERSION = "verification-audit/1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash_event(event: Dict[str, Any]) -> str:
    body = {key: value for key, value in event.items() if key != "hash"}
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


class VerificationStore:
    """In-memory state plus a hash-chained JSON journal."""

    def __init__(self, path: Optional[str] = None):
        self.path = Path(path) if path else None
        self.events: List[Dict[str, Any]] = []
        self.state: Dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "records": {},
        }
        if self.path and self.path.exists():
            self.load()

    # === persistence ===

    def load(self) -> None:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        events = data.get("events") or []
        self.events = []
        self.state = {"schema_version": SCHEMA_VERSION, "records": {}}
        for event in events:
            expected = event.get("prev_hash", "")
            actual_prev = self.events[-1]["hash"] if self.events else ""
            if expected != actual_prev:
                raise ValueError("Audit-Kette unterbrochen: prev_hash passt nicht")
            if _hash_event(event) != event.get("hash"):
                raise ValueError("Audit-Ereignis manipuliert: hash passt nicht")
            self.events.append(event)
            self._apply(event)

    def save(self) -> None:
        if not self.path:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "audit_version": AUDIT_VERSION,
            "schema_version": SCHEMA_VERSION,
            "events": self.events,
            "state": self.state,
        }
        fd, tmp = tempfile.mkstemp(prefix=".verification-", suffix=".json",
                                   dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
            os.replace(tmp, self.path)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)

    def _append(self, event_type: str, record_id: str, payload: Dict[str, Any],
                actor: str = "system") -> Dict[str, Any]:
        previous = self.events[-1]["hash"] if self.events else ""
        event = {
            "seq": len(self.events) + 1,
            "type": event_type,
            "record_id": record_id,
            "actor": actor,
            "created_at": _now(),
            "payload": payload,
            "prev_hash": previous,
        }
        event["hash"] = _hash_event(event)
        self.events.append(event)
        self._apply(event)
        self.save()
        return event

    # === event replay ===

    def _record(self, record_id: str) -> Dict[str, Any]:
        return self.state["records"].setdefault(record_id, {
            "record_id": record_id,
            "status": "extracted",
            "fields": {},
            "extractions": {},
            "evidence": {},
            "comparisons": {},
            "validations": [],
            "decisions": [],
            "created_at": _now(),
        })

    def _apply(self, event: Dict[str, Any]) -> None:
        record_id = event.get("record_id") or ""
        payload = event.get("payload") or {}
        record = self._record(record_id)
        kind = event.get("type")
        if kind == "record_registered":
            record.update(payload)
            record["record_id"] = record_id
            # Replay must preserve the event time, not the time of loading.
            record["created_at"] = event.get("created_at") or record.get("created_at")
            record.setdefault("fields", {})
            record.setdefault("extractions", {})
            record.setdefault("evidence", {})
            record.setdefault("comparisons", {})
            record.setdefault("validations", [])
            record.setdefault("decisions", [])
            record["status"] = "extracted"
        elif kind == "extraction_recorded":
            pipeline = str(payload.get("pipeline") or "")
            record["extractions"][pipeline] = payload
        elif kind == "evidence_recorded":
            for evidence in payload.get("evidence") or []:
                record["evidence"][str(evidence.get("evidence_id"))] = evidence
        elif kind == "comparison_recorded":
            field = str(payload.get("field") or "")
            record["comparisons"][field] = payload
            entry = record["fields"].setdefault(field, {
                "name": field,
                "value_a": payload.get("value_a"),
                "value_b": payload.get("value_b"),
                "final_value": None,
                "reported": True,
                "status": "extracted",
                "comparison": payload.get("comparison"),
                "rule": payload.get("rule"),
                "evidence_id": payload.get("evidence_id") or "",
                "note": "",
            })
            entry.update({
                "value_a": payload.get("value_a"),
                "value_b": payload.get("value_b"),
                "comparison": payload.get("comparison"),
                "rule": payload.get("rule"),
                "evidence_id": payload.get("evidence_id") or "",
                "status": payload.get("field_status", "cross_checked"),
            })
            if entry.get("final_value") is None and payload.get("comparison") in (
                    "match", "numeric_match"):
                entry["final_value"] = payload.get("value_a")
        elif kind == "validation_recorded":
            record["validations"] = list(payload.get("validations") or [])
        elif kind == "status_changed":
            record["status"] = transition_record(
                str(record.get("status") or "extracted"),
                str(payload.get("status") or ""),
            )
            record["status_reason"] = payload.get("reason") or ""
            record["status_at"] = event.get("created_at")
            record["status_by"] = event.get("actor")
            if record["status"] == "verified":
                record["verified_at"] = event.get("created_at")
                record["verified_by"] = event.get("actor")
                record["verification_basis"] = payload.get("basis") or ""
            elif record.get("status") in {"pending_review", "rejected"}:
                record["verified_at"] = ""
                record["verified_by"] = ""
                record["verification_basis"] = ""
        elif kind == "decision_recorded":
            field = str(payload.get("field") or "")
            entry = record["fields"].setdefault(field, {
                "name": field, "status": "unresolved", "final_value": None,
            })
            old = {
                "status": entry.get("status"),
                "final_value": (entry.get("final_value")
                                if entry.get("final_value") is not None
                                else entry.get("value_a")),
                "reported": entry.get("reported", True),
            }
            entry["status"] = transition_field(
                str(entry.get("status") or "extracted"),
                str(payload.get("new_status") or "unresolved"),
            )
            entry["final_value"] = payload.get("new_value")
            entry["reported"] = bool(payload.get("reported", True))
            entry["evidence_id"] = payload.get("evidence_id") or entry.get("evidence_id") or ""
            entry["note"] = payload.get("note") or ""
            entry["verified_by"] = event.get("actor")
            entry["verified_at"] = event.get("created_at")
            record["decisions"].append({
                "field": field,
                "action": payload.get("action"),
                "old": old,
                "new": {
                    "status": entry["status"],
                    "final_value": entry.get("final_value"),
                    "reported": entry.get("reported"),
                },
                "reviewer": payload.get("reviewer") or event.get("actor"),
                "note": payload.get("note") or "",
                "evidence_id": entry.get("evidence_id") or "",
                "created_at": event.get("created_at"),
            })
        elif kind == "record_invalidated":
            record["status"] = "pending_review"
            record["status_reason"] = payload.get("reason") or "Quelle oder Extraktion geaendert"
            record["verified_at"] = ""
            record["verified_by"] = ""
            record["verification_basis"] = ""
            for entry in record["fields"].values():
                if entry.get("status") == "verified":
                    entry["status"] = "cross_checked"

    # === commands ===

    def register_record(self, record_id: str, meta: Dict[str, Any]) -> None:
        if record_id in self.state["records"]:
            raise ValueError(f"Record bereits registriert: {record_id}")
        payload = dict(meta)
        payload.setdefault("document_hash", "")
        payload.setdefault("outcome_type", "continuous")
        payload.setdefault("required_fields", [])
        self._append("record_registered", record_id, payload, actor="pipeline")

    def add_extraction(self, record_id: str, pipeline: str,
                       payload: Dict[str, Any]) -> None:
        self._record(record_id)
        body = dict(payload)
        body["pipeline"] = pipeline
        self._append("extraction_recorded", record_id, body, actor=pipeline)

    def add_evidence(self, record_id: str,
                     evidence: Iterable[Dict[str, Any]]) -> None:
        clean = []
        for index, item in enumerate(evidence or []):
            entry = dict(item)
            entry.setdefault(
                "evidence_id",
                "ev:" + hashlib.sha256(
                    _canonical({"record_id": record_id, "idx": index,
                                "value": item}).encode("utf-8")
                ).hexdigest()[:16],
            )
            clean.append(entry)
        if clean:
            self._append("evidence_recorded", record_id, {"evidence": clean},
                         actor="evidence")

    def record_comparison(self, record_id: str, comparison: Dict[str, Any]) -> None:
        self._append("comparison_recorded", record_id, comparison, actor="compare")

    def record_validations(self, record_id: str,
                           validations: Iterable[Dict[str, Any]]) -> None:
        self._append("validation_recorded", record_id,
                     {"validations": list(validations)}, actor="plausibility")

    def set_status(self, record_id: str, status: str, reason: str,
                   actor: str = "system", basis: str = "") -> None:
        record = self._record(record_id)
        transition_record(str(record.get("status") or "extracted"), status)
        self._append("status_changed", record_id, {
            "status": status, "reason": reason, "basis": basis,
        }, actor=actor)

    def apply_decision(self, record_id: str, field: str, action: str,
                       value: Any = None, reviewer: str = "", note: str = "",
                       evidence_id: str = "", new_status: str = "verified",
                       reported: bool = True) -> None:
        record = self._record(record_id)
        if reviewer.strip() == "":
            raise ValueError("Eine menschliche Entscheidung braucht einen Pruefer.")
        allowed = {"confirm", "correct", "not_reported", "unclear", "reject"}
        if action not in allowed:
            raise ValueError(f"unbekannte Aktion: {action}")
        if action == "reject":
            self.set_status(record_id, "rejected", note or "vom Pruefer abgelehnt",
                            actor=reviewer)
            return
        if field not in record.get("fields", {}):
            raise ValueError(f"Feld nicht im Record: {field}")
        entry = record["fields"][field]
        if action == "unclear":
            new_status = "unresolved"
        elif action == "not_reported":
            new_status = "verified"
            reported = False
            if not note.strip():
                raise ValueError("'nicht berichtet' braucht eine dokumentierte Begruendung.")
        elif action in {"confirm", "correct"}:
            if action == "confirm":
                value = entry.get("final_value")
                if value is None:
                    value = entry.get("value_a")
            candidate_evidence = evidence_id or entry.get("evidence_id") or ""
            valid_evidence = evidence_for_value(
                record, field, value, candidate_evidence)
            # An approval is only possible with a present value and a stored
            # evidence row for this field.  Missing either one leaves the
            # field open and is recorded as an unresolved decision.
            if not has_value(value) or valid_evidence is None:
                new_status = "unresolved"
                evidence_id = ""
            else:
                new_status = "verified"
                evidence_id = str(candidate_evidence).strip()
        self._append("decision_recorded", record_id, {
            "field": field, "action": action, "new_value": value,
            "new_status": new_status, "reported": reported, "reviewer": reviewer,
            "note": note, "evidence_id": evidence_id,
        }, actor=reviewer)

    def invalidate(self, record_id: str, reason: str) -> None:
        record = self._record(record_id)
        if record.get("status") == "verified":
            self._append("record_invalidated", record_id, {"reason": reason},
                         actor="integrity")
        else:
            # Unverified records still need the reason in the journal, but no
            # approval is lost because none existed.
            self._append("record_invalidated", record_id, {"reason": reason},
                         actor="integrity")

    def record(self, record_id: str) -> Dict[str, Any]:
        return self.state["records"][record_id]

    def summary(self) -> Dict[str, int]:
        counts = {status: 0 for status in RECORD_STATUSES}
        for record in self.state["records"].values():
            counts[str(record.get("status") or "extracted")] += 1
        counts["total"] = len(self.state["records"])
        counts["human_reviewed"] = sum(
            1 for record in self.state["records"].values()
            if any(decision.get("reviewer") for decision in record.get("decisions", []))
        )
        return counts
