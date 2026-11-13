"""Append source evidence for the six review cases without changing values.

The script only adds evidence events to the append-only audit.  It never calls
`record_comparison` or `apply_decision`, so values, field status and record
status remain exactly as they were.

Run from the repository root:
    python scripts/ergaenze_review_evidenzen_20261113.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.verification.store import VerificationStore

AUDIT = ROOT / "public_benchmark" / "evaluation" / "verification_pilot" / "audit.json"
SNAPSHOT = AUDIT.parent / "pilot_20.json"
SOURCE = ROOT / "public_benchmark" / "raw_data" / "yun_llm_meta_analysis" / "evaluation" / "data" / "no_attributes_markdown_files"


def _evidence(record_id: str, field: str, source: str, table_id: str,
              caption: str, row: str, column: str, raw: str,
              line_start: int, excerpt: str) -> Dict[str, Any]:
    digest = hashlib.sha256(
        f"{record_id}|{field}|{raw}|{row}|{column}".encode("utf-8")
    ).hexdigest()[:20]
    return {
        "evidence_id": f"ev:review:{record_id}:{field}",
        "record_id": record_id,
        "field": field,
        "document_id": source.split(".")[0],
        "source_path": f"public_benchmark/raw_data/yun_llm_meta_analysis/evaluation/data/no_attributes_markdown_files/{source}",
        "table_id": table_id,
        "table_caption": caption,
        "row_label": row,
        "column_label": column,
        "raw_cell": raw,
        "line_start": line_start,
        "line_end": line_start,
        "excerpt": excerpt,
        "evidence_hash": digest,
    }


def _pmc2972614(record_id: str, outcome: str, mean_line: int,
                intervention_raw: str, comparator_raw: str,
                mean_row: str) -> List[Dict[str, Any]]:
    source = "PMC2972614.md"
    caption = ("Comparison of mean values of pain severity, ROM and SPADI "
               "scores before and after treatment between the groups")
    excerpt = "Group I and Group II; table 2, Posttreatment"
    return [
        _evidence(record_id, "intervention_n", source, "md:PMC2972614:table2",
                  caption, "Methods: Group I", "N", "Group I (n = 30)", 1,
                  "Group I (n = 30, laser group)"),
        _evidence(record_id, "comparator_n", source, "md:PMC2972614:table2",
                  caption, "Methods: Group II", "N", "Group II (n = 22)", 1,
                  "Group II (n = 22, placebo laser group)"),
        _evidence(record_id, "intervention_mean", source, "md:PMC2972614:table2",
                  caption, mean_row, "Group I", intervention_raw, mean_line,
                  excerpt),
        _evidence(record_id, "intervention_sd", source, "md:PMC2972614:table2",
                  caption, mean_row, "Group I", intervention_raw, mean_line,
                  excerpt),
        _evidence(record_id, "comparator_mean", source, "md:PMC2972614:table2",
                  caption, mean_row, "Group II", comparator_raw, mean_line,
                  excerpt),
        _evidence(record_id, "comparator_sd", source, "md:PMC2972614:table2",
                  caption, mean_row, "Group II", comparator_raw, mean_line,
                  excerpt),
    ]


def _pmc3169777(record_id: str, dose: str, event: int) -> List[Dict[str, Any]]:
    source = "PMC3169777.md"
    caption = "Overview of reported adverse events by treatment"
    excerpt = "Headache row: 0, 0, 0, 2, 1, 2, 5, 3; footnote n = 6 per dose, n = 14 placebo"
    return [
        _evidence(record_id, "intervention_n", source, "md:PMC3169777:ae",
                  caption, "Footnote: number of subjects reporting adverse events",
                  "macitentan", "n = 6 per dose", 21, excerpt),
        _evidence(record_id, "comparator_n", source, "md:PMC3169777:ae",
                  caption, "Footnote: number of subjects reporting adverse events",
                  "placebo", "n = 14", 21, excerpt),
        _evidence(record_id, "intervention_events", source, "md:PMC3169777:ae",
                  caption, "Headache", f"{dose} mg macitentan", str(event), 9,
                  excerpt),
        _evidence(record_id, "comparator_events", source, "md:PMC3169777:ae",
                  caption, "Headache", "placebo", "3", 9, excerpt),
    ]


def _pmc3169777_context(record_id: str) -> List[Dict[str, Any]]:
    source = "PMC3169777.md"
    caption = "Overview of reported adverse events by treatment"
    excerpt = "Headache is listed as an adverse event; treatment period is the single-dose study period."
    return [
        _evidence(record_id, "outcome", source, "md:PMC3169777:ae",
                  caption, "Headache", "Adverse event", "Headache", 9, excerpt),
        _evidence(record_id, "time_point", source, "md:PMC3169777:ae",
                  caption, "Headache", "Treatment period",
                  "Adverse events by treatment", 9, excerpt),
    ]


def _pmc4183415() -> List[Dict[str, Any]]:
    record_id = "c1-98"
    source = "PMC4183415.md"
    caption = "Patient adherence (mean of cluster summaries)"
    excerpt = "Timely completion: control 32.6 (18.4), intervention 33.1 (21.6), cluster N 37/40"
    return [
        _evidence(record_id, "intervention_n", source, "md:PMC4183415:adherence",
                  caption, "Timely completion", "Intervention (N = 40)", "N = 40", 186, excerpt),
        _evidence(record_id, "comparator_n", source, "md:PMC4183415:adherence",
                  caption, "Timely completion", "Control (N = 37)", "N = 37", 186, excerpt),
        _evidence(record_id, "intervention_mean", source, "md:PMC4183415:adherence",
                  caption, "Timely completion", "Intervention", "33.1 (21.6)", 193, excerpt),
        _evidence(record_id, "intervention_sd", source, "md:PMC4183415:adherence",
                  caption, "Timely completion", "Intervention", "33.1 (21.6)", 193, excerpt),
        _evidence(record_id, "comparator_mean", source, "md:PMC4183415:adherence",
                  caption, "Timely completion", "Control", "32.6 (18.4)", 193, excerpt),
        _evidence(record_id, "comparator_sd", source, "md:PMC4183415:adherence",
                  caption, "Timely completion", "Control", "32.6 (18.4)", 193, excerpt),
        _evidence(record_id, "outcome", source, "md:PMC4183415:adherence",
                  caption, "Timely completion", "All doses at appropriate times",
                  "Timely completion; all doses at appropriate times", 193, excerpt),
        _evidence(record_id, "time_point", source, "md:PMC4183415:adherence",
                  caption, "Timely completion", "Follow-up after AL purchase",
                  "Follow-up interview after AL purchase", 193, excerpt),
    ]


def build_entries() -> Dict[str, List[Dict[str, Any]]]:
    entries: Dict[str, List[Dict[str, Any]]] = {
        "c1-21": _pmc2972614(
            "c1-21", "Severity of pain", 32, "3.76±1.45", "4.63±2.10",
            "VAS Posttreatment (mean±SD)",
        ),
        "c1-22": _pmc2972614(
            "c1-22", "SPADI score", 68, "44.33±2.80", "36.39±20.53",
            "SPADI total Posttreatment (mean±SD)",
        ),
        "c1-36": _pmc3169777("c1-36", "600", 5),
        "c1-45": _pmc3169777("c1-45", "0.2", 0) + _pmc3169777_context("c1-45"),
        "c1-48": _pmc3169777("c1-48", "25", 2),
        "c1-50": _pmc3169777("c1-50", "300", 2),
        "c1-98": _pmc4183415(),
    }
    return entries


def field_snapshot(record: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    keys = ("value_a", "value_b", "final_value", "status", "comparison",
            "reported", "evidence_id")
    return {name: {key: field.get(key) for key in keys}
            for name, field in (record.get("fields") or {}).items()}


def append_entries(store: VerificationStore,
                   entries: Dict[str, List[Dict[str, Any]]]) -> Tuple[int, int]:
    added = 0
    existing = 0
    for record_id, items in entries.items():
        record = store.record(record_id)
        known = set((record.get("evidence") or {}).keys())
        missing = [item for item in items if item["evidence_id"] not in known]
        existing += len(items) - len(missing)
        if missing:
            store.add_evidence(record_id, missing)
            added += len(missing)
    return added, existing


def main() -> int:
    store = VerificationStore(str(AUDIT))
    # Diagnostics and the pilot's original registration time are snapshot
    # metadata; the event log itself does not carry them.
    audit_existing = json.loads(AUDIT.read_text(encoding="utf-8"))
    for record_id, record in store.state["records"].items():
        old_record = (audit_existing.get("state", {}).get("records", {})
                      .get(record_id) or {})
        if "diagnostic" in old_record:
            record["diagnostic"] = old_record["diagnostic"]
        if "created_at" in old_record:
            record["created_at"] = old_record["created_at"]
    before = {record_id: field_snapshot(record)
              for record_id, record in store.state["records"].items()}
    before_status = {record_id: record.get("status")
                     for record_id, record in store.state["records"].items()}
    entries = build_entries()
    added, existing = append_entries(store, entries)
    after = {record_id: field_snapshot(record)
             for record_id, record in store.state["records"].items()}
    after_status = {record_id: record.get("status")
                    for record_id, record in store.state["records"].items()}
    if before != after:
        raise SystemExit("FEHLER: Felder oder Werte haben sich veraendert.")
    if before_status != after_status:
        raise SystemExit("FEHLER: Recordstatus hat sich ohne Entscheidung geaendert.")
    pending = [record_id for record_id, record in store.state["records"].items()
               if record.get("status") == "pending_review"]
    expected_pending = {"c1-13", "c1-21", "c1-22", "c1-32", "c1-36",
                        "c1-45", "c1-48", "c1-50", "c1-95", "c1-98", "c1-194"}
    if set(pending) != expected_pending:
        raise SystemExit(f"FEHLER: unerwartete offene Records: {pending}")

    store.save()

    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    # Keep the diagnostics written by the pilot; the store does not know them.
    for record_id, record in store.state["records"].items():
        existing_record = (snapshot.get("records") or {}).get(record_id) or {}
        merged = dict(record)
        if "diagnostic" in existing_record:
            merged["diagnostic"] = existing_record["diagnostic"]
        if "created_at" in existing_record:
            merged["created_at"] = existing_record["created_at"]
        snapshot.setdefault("records", {})[record_id] = merged
    snapshot["events"] = store.events
    SNAPSHOT.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "added_evidence": added,
        "already_present": existing,
        "pending_records": len(pending),
        "verified_records": sum(1 for record in store.state["records"].values()
                                if record.get("status") == "verified"),
        "values_unchanged": before == after,
        "statuses_unchanged": before_status == after_status,
        "events": len(store.events),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
