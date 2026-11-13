"""Run the bounded 20-record C1 verification pilot.

This is a retrospective engineering check on the consumed 249-record test
split.  It is diagnostic only and must never be reported as an independent
validation of the verification system.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .pipelines import LayoutPipeline, load_pipeline_a
from .store import VerificationStore
from .workflow import build_verification

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "public_benchmark"
TEST_RECORDS = BENCH / "processed_data" / "yun_c1_test_249.jsonl"
A_OUTPUT = BENCH / "evaluation" / "c1_pilot" / "runs_test" / "c1_test_20261111_v6c" / "test_output.jsonl"
OUT_DIR = BENCH / "evaluation" / "verification_pilot"

# Targeted diagnostic sample: corrected value, missing block, wrong block,
# multi-arm, multi-section, complex header, prose-only, cluster table.
PILOT_IDS = [12, 13, 15, 16, 21, 22, 24, 25, 26, 27, 28, 29,
             32, 36, 45, 48, 50, 95, 98, 194]

FIELD_ALIASES = {
    "intervention_group_size": "intervention_n",
    "comparator_group_size": "comparator_n",
    "intervention_mean": "intervention_mean",
    "intervention_standard_deviation": "intervention_sd",
    "comparator_mean": "comparator_mean",
    "comparator_standard_deviation": "comparator_sd",
    "intervention_events": "intervention_events",
    "comparator_events": "comparator_events",
}


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def reference_fields(record: Dict[str, Any]) -> Dict[str, Any]:
    values = record.get("curated_values") or {}
    return {FIELD_ALIASES[key]: value for key, value in values.items()
            if key in FIELD_ALIASES}


def exact_count(values: Dict[str, Any], reference: Dict[str, Any],
                fields: Iterable[str]) -> int:
    count = 0
    for field in fields:
        a, b = values.get(field), reference.get(field)
        if a in (None, "") or b in (None, ""):
            continue
        try:
            if abs(float(a) - float(b)) < 1e-9:
                count += 1
        except (TypeError, ValueError):
            if str(a) == str(b):
                count += 1
    return count


def render_markdown(state: Dict[str, Any], summary: Dict[str, Any]) -> str:
    lines = [
        "# Verifikationspilot: 20 C1-Records",
        "",
        "**Art:** retrospektive technische Fehleranalyse auf dem verbrauchten "
        "249er-Test; keine unabhaengige Validierung.",
        "",
        "## Ergebnis",
        "",
        "| Kennzahl | Wert |",
        "|---|---:|",
        f"| Records | {summary['records']} |",
        f"| automatisch verifiziert | {summary['verified']} |",
        f"| offen fuer menschliche Pruefung | {summary['pending_review']} |",
        f"| abgelehnt | {summary['rejected']} |",
        f"| menschlich geprueft | {summary['human_reviewed']} |",
        f"| Pflichtfelder | {summary['required_fields']} |",
        f"| verifizierte Pflichtfelder | {summary['verified_fields']} |",
        f"| Feldabweichungen | {summary['mismatch_fields']} |",
        f"| fehlende Evidenz | {summary['evidence_missing_fields']} |",
        "",
        "Die automatische Freigabe verlangt **zwei getrennte Lesungen plus eine "
        "exakte Quellzelle mit Zeilen-, Spalten- und Zeitpunktkontext**. "
        "Zwei Modelluebereinstimmungen allein reichen nicht.",
        "",
        "## Einzelrecords",
        "",
        "| Record | Typ | Status | A exakt | B exakt | Offene Felder |",
        "|---|---|---|---:|---:|---|",
    ]
    for record_id, item in state["records"].items():
        values = item.get("diagnostic") or {}
        open_fields = [name for name, field in item.get("fields", {}).items()
                       if field.get("status") != "verified"
                       and name in (item.get("required_fields") or [])]
        lines.append(
            f"| {record_id} | {item.get('outcome_type', '')} | {item.get('status', '')} | "
            f"{values.get('a_exact', '')}/{values.get('required', '')} | "
            f"{values.get('b_exact', '')}/{values.get('required', '')} | "
            f"{', '.join(open_fields) or '-'} |"
        )
    lines += [
        "",
        "## Grenzen",
        "",
        "- Der 249er-Test ist verbraucht und darf nicht als unabhaengiger Nachweis "
        "fuer das neue System gelten.",
        "- Pipeline B lief offline als Layout-Geometrie. Der vorhandene "
        "Vision-Adapter wurde **nicht** aufgerufen; es gab keinen Netzlauf.",
        "- Ohne menschliche Entscheidung bleibt ein Record mit offenen Feldern "
        "`pending_review`; das ist kein Fehler, sondern die Freigaberegel.",
        "- Die Referenzspalte dient nur der Diagnose und wurde nicht zur "
        "Extraktion oder Statusvergabe verwendet.",
        "",
    ]
    return "\n".join(lines)


def build_pilot(out_dir: Path = OUT_DIR) -> Dict[str, Any]:
    records = {int(row["record_id"]): row for row in load_jsonl(TEST_RECORDS)}
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_path = out_dir / "audit.json"
    if audit_path.exists():
        audit_path.unlink()
    store = VerificationStore(str(audit_path))
    summary = {
        "records": 0, "verified": 0, "pending_review": 0, "rejected": 0,
        "human_reviewed": 0, "required_fields": 0, "verified_fields": 0,
        "mismatch_fields": 0, "evidence_missing_fields": 0,
    }
    for record_id in PILOT_IDS:
        record = dict(records[record_id])
        source = ROOT / record["source_text_path"]
        text = source.read_text(encoding="utf-8")
        record["document_id"] = record.get("study_id") or record.get("pmcid")
        record["document_hash"] = hashlib.sha256(source.read_bytes()).hexdigest()
        a_row = load_pipeline_a(record_id, str(A_OUTPUT))
        b_result = LayoutPipeline().extract(record, text, record["document_hash"]).to_dict()
        result = build_verification(store, record, a_row, b_result)
        item = store.record(result["record_id"])
        required = item.get("required_fields") or []
        ref = reference_fields(record)
        a_values = ((item.get("extractions") or {}).get("A_v6c") or {}).get("fields") or {}
        b_values = {
            name: ((entry or {}).get("value"))
            for name, entry in (((item.get("extractions") or {}).get("B_layout") or {})
                                .get("fields") or {}).items()
        }
        item["diagnostic"] = {
            "required": len(required),
            "a_exact": exact_count(a_values, ref, required),
            "b_exact": exact_count(b_values, ref, required),
            "reference": ref,
            "a_values": {name: a_values.get(name) for name in required},
            "b_values": {name: b_values.get(name) for name in required},
        }
        summary["records"] += 1
        summary[result["status"]] = summary.get(result["status"], 0) + 1
        for comparison in result["comparisons"]:
            if comparison["field"] not in required:
                continue
            summary["required_fields"] += 1
            if comparison["field_status"] == "verified":
                summary["verified_fields"] += 1
            elif comparison["comparison"] == "mismatch":
                summary["mismatch_fields"] += 1
            elif comparison["comparison"] == "evidence_missing":
                summary["evidence_missing_fields"] += 1
    summary["human_reviewed"] = store.summary()["human_reviewed"]
    summary["automatic_rate"] = (
        round(summary["verified"] / summary["records"], 4)
        if summary["records"] else 0.0
    )
    state = {
        "schema_version": store.state.get("schema_version"),
        "summary": summary,
        "records": store.state["records"],
        "events": store.events,
    }
    (out_dir / "pilot_20.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "pilot_20.md").write_text(
        render_markdown(state, summary), encoding="utf-8")
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    args = parser.parse_args()
    summary = build_pilot(Path(args.out_dir))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
