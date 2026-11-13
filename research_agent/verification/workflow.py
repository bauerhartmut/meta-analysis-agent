"""Assemble one record from two independent readings and decide its status."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .compare import compare_record
from .plausibility import check_fields, hard_errors
from .schema import (
    FIELD_STATUSES, fields_for_record, normalise_text, parse_number,
    required_fields,
)
from .store import VerificationStore


def _evidence_id(record_id: str, field: str, evidence: Dict[str, Any]) -> str:
    body = f"{record_id}|{field}|{evidence.get('evidence_hash', '')}".encode("utf-8")
    return "ev:" + hashlib.sha256(body).hexdigest()[:20]


def _a_timepoint(a: Dict[str, Any], record: Dict[str, Any]) -> str:
    note = str(a.get("source_note") or "")
    week = re.search(r"\b(?:week|wk)\s*(\d{1,2})\b", note, re.I)
    if week:
        return f"week {week.group(1)}"
    if re.search(r"post[-\s]?(?:test|treatment|intervention)", note, re.I):
        return "post-treatment"
    if re.search(r"follow[-\s]?up", note, re.I):
        return "follow-up"
    # C1's pre-registered rule: immediate post-test unless the ICO names a
    # different timepoint.  This is a documented default, not a conversion.
    return "post-treatment"


def _a_values(a: Dict[str, Any], record: Dict[str, Any]) -> Dict[str, Any]:
    values = {
        "intervention_n": a.get("intervention_n"),
        "comparator_n": a.get("comparator_n"),
        "intervention_mean": a.get("intervention_mean"),
        "comparator_mean": a.get("comparator_mean"),
        "intervention_sd": a.get("intervention_sd"),
        "comparator_sd": a.get("comparator_sd"),
        "intervention_events": a.get("intervention_events"),
        "comparator_events": a.get("comparator_events"),
        "outcome": record.get("ico", {}).get("outcome", ""),
        "time_point": _a_timepoint(a, record),
        "unit": a.get("unit") or "",
    }
    return values


def _b_values(b: Dict[str, Any]) -> Dict[str, Any]:
    fields = b.get("fields") or {}
    return {name: (entry or {}).get("value") for name, entry in fields.items()}


def _b_evidence(b: Dict[str, Any], record_id: str) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for field, entry in (b.get("fields") or {}).items():
        evidence = dict((entry or {}).get("evidence") or {})
        if not evidence:
            continue
        evidence["field"] = field
        evidence["evidence_id"] = _evidence_id(record_id, field, evidence)
        evidence["record_id"] = record_id
        out[field] = evidence
    return out


def build_verification(store: VerificationStore, record: Dict[str, Any],
                       a_row: Dict[str, Any], b_result: Dict[str, Any],
                       record_id: Optional[str] = None) -> Dict[str, Any]:
    record_id = record_id or f"c1-{record.get('record_id')}"
    document_hash = str(record.get("document_hash") or "")
    store.register_record(record_id, {
        "document_id": record.get("document_id") or record.get("study_id") or "",
        "document_hash": document_hash,
        "source_path": record.get("source_text_path") or "",
        "outcome_type": record.get("outcome_type") or "continuous",
        "ico": record.get("ico") or {},
        "required_fields": list(required_fields(record.get("outcome_type") or "continuous")),
        "split": record.get("split") or "",
        "source_record_id": record.get("record_id"),
        "spec_version": record.get("spec_version") or "c1-ico/1",
    })
    store.add_extraction(record_id, "A_v6c", {
        "version": a_row.get("extractor") or "c1-test-20261111-v6c",
        "model": "qwen3.5-397b-a17b",
        "prompt_version": "c1-dev-extract-v6",
        "parser_version": "c1-markdown/1",
        "output_hash": hashlib.sha256(
            json.dumps(a_row, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest(),
        "fields": a_row,
    })
    store.add_extraction(record_id, "B_layout", b_result)

    evidence = _b_evidence(b_result, record_id)
    store.add_evidence(record_id, evidence.values())
    a_values = _a_values(a_row, record)
    b_values = _b_values(b_result)

    numeric = list(required_fields(record.get("outcome_type") or "continuous"))
    optional = ["outcome", "time_point"]
    if a_values.get("unit") not in (None, "") or b_values.get("unit") not in (None, ""):
        optional.append("unit")
    comparisons = compare_record(numeric + optional, a_values, b_values,
                                 evidence, expected_time=b_result.get("time_point") or "")
    for item in comparisons:
        store.record_comparison(record_id, item)

    validations = check_fields(record, b_values)
    store.record_validations(record_id, validations)

    unresolved = [
        item for item in comparisons
        if item["field"] in numeric and item["comparison"] not in {"match", "numeric_match"}
    ]
    optional_bad = [
        item for item in comparisons
        if item["field"] in {"outcome", "time_point"}
        and item["comparison"] not in {"match", "numeric_match"}
    ]
    blockers = hard_errors(validations)
    if blockers or unresolved or optional_bad:
        store.set_status(record_id, "cross_checked",
                         "Feldvergleich abgeschlossen; offene Punkte fuer Review")
        store.set_status(record_id, "pending_review",
                         f"{len(unresolved)} numerische und {len(optional_bad)} "
                         f"Kontextfelder offen, {len(blockers)} harte Fehler")
        result_status = "pending_review"
    else:
        store.set_status(record_id, "cross_checked",
                         "beide Extraktionen und Evidenzzellen stimmen ueberein")
        store.set_status(record_id, "verified",
                         "alle Pflichtfelder durch exakte Quellzelle belegt",
                         actor="machine-evidence",
                         basis="automated_exact_evidence")
        result_status = "verified"
    return {
        "record_id": record_id,
        "status": result_status,
        "comparisons": comparisons,
        "validations": validations,
        "unresolved": [item["field"] for item in unresolved + optional_bad],
        "hard_errors": [item["field"] for item in blockers],
    }


def finalize_after_review(store: VerificationStore, record_id: str,
                          reviewer: str) -> str:
    """Recompute a record after human decisions without hiding open fields."""
    record = store.record(record_id)
    required = list(record.get("required_fields")
                    or required_fields(record.get("outcome_type") or "continuous"))
    fields = record.get("fields") or {}
    evidence = record.get("evidence") or {}

    def field_is_verified(name: str) -> bool:
        entry = fields.get(name) or {}
        if str(entry.get("status")) != "verified":
            return False
        # "not reported" is a documented exception, not an approval of a
        # numeric value.
        if entry.get("reported") is False:
            return True
        value = entry.get("final_value")
        if value is None or (isinstance(value, str) and not value.strip()):
            return False
        evidence_id = str(entry.get("evidence_id") or "").strip()
        item = evidence.get(evidence_id)
        if not item:
            return False
        declared = str(item.get("field") or "")
        return not declared or declared == name

    open_fields = [name for name in required if not field_is_verified(name)]
    if open_fields:
        if record.get("status") != "pending_review":
            store.set_status(record_id, "pending_review",
                             f"menschliche Pruefung unvollstaendig: {', '.join(open_fields)}",
                             actor=reviewer)
        return "pending_review"
    if record.get("status") == "rejected":
        return "rejected"
    if record.get("status") == "pending_review":
        store.set_status(record_id, "verified",
                         "alle Pflichtfelder menschlich bestaetigt oder korrigiert",
                         actor=reviewer, basis="human_review")
    return "verified"


def invalidate_on_source_change(store: VerificationStore, record_id: str,
                                current_document_hash: str,
                                current_extraction_hash: str = "") -> bool:
    record = store.record(record_id)
    changed = False
    if current_document_hash and current_document_hash != record.get("document_hash"):
        store.invalidate(record_id, "Dokument-Hash hat sich geaendert")
        changed = True
    extraction = (record.get("extractions") or {}).get("A_v6c") or {}
    old = str(extraction.get("output_hash") or "")
    if current_extraction_hash and old and current_extraction_hash != old:
        store.invalidate(record_id, "Extraktions-Hash hat sich geaendert")
        changed = True
    return changed
