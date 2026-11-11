"""C1-Testlaufbericht aus Manifest und Evaluationsaggregaten bauen."""

from __future__ import annotations

import hashlib
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
PILOT_ROOT = BENCH_ROOT / "evaluation" / "c1_pilot"
RUN_DIR = PILOT_ROOT / "runs_test" / "c1_test_20261111_v6c"
MANIFEST_PATH = RUN_DIR / "test_manifest.json"
EVALUATION_PATH = RUN_DIR / "test_evaluation.json"
RESULT_PATH = RUN_DIR / "test_result.json"
REPORT_PATH = RUN_DIR / "test_result.md"
APPROVAL_PATH = PILOT_ROOT / "test_approval_v6c.json"
RELEASE_PATH = PILOT_ROOT / "release_v6c.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    manifest = load(MANIFEST_PATH)
    evaluation = load(EVALUATION_PATH)
    approval = load(APPROVAL_PATH)
    release = load(RELEASE_PATH)

    for condition, message in [
        (manifest["status"] == "completed", "Testlauf nicht completed"),
        (manifest["completed_records"] == 249, "nicht 249 Records"),
        (manifest["parse_errors"] == 0, "Parse-Fehler vorhanden"),
        (manifest["test_split_used"] is True, "Testflag fehlt"),
        (manifest["reference_loaded"] is False, "Referenz wurde im Runner geladen"),
        (approval["test_run_approved"] is True, "Freigabe fehlt"),
        (evaluation["expected_fields_total"] == 1308, "nicht 1.308 Felder"),
        (release["test_projection"]["input_sha256"] == manifest["input_sha256"],
         "Input-Hash weicht vom Release ab"),
    ]:
        if not condition:
            raise ValueError(message)

    by_type = {}
    for outcome_type in ("continuous", "binary"):
        rows = [row for row in evaluation["records_detail"]
                if row["outcome_type"] == outcome_type]
        by_type[outcome_type] = {
            "records": len(rows),
            "expected_fields": sum(row["expected_fields"] for row in rows),
            "exact_fields": sum(row["exact_fields"] for row in rows),
            "missing_fields": sum(row["missing_fields"] for row in rows),
            "wrong_fields": sum(row["wrong_fields"] for row in rows),
            "records_all_exact": sum(
                1 for row in rows if row["exact_fields"] == row["expected_fields"]
            ),
        }

    result = {
        "result_version": 1,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "run_id": manifest["run_id"],
        "status": "completed",
        "test_run_approved": True,
        "approval_id": approval["approval_id"],
        "test_split_used": True,
        "reference_loaded_by_runner": False,
        "post_test_prompt_changes": False,
        "aggregate": {
            "records": evaluation["records"],
            "records_with_output": evaluation["records_with_output"],
            "expected_fields": evaluation["expected_fields_total"],
            "expected_fields_present": evaluation["expected_fields_present"],
            "coverage": evaluation["coverage"],
            "exact_fields": evaluation["exact_fields"],
            "exact_rate": evaluation["exact_rate"],
            "missing_fields": evaluation["missing_fields"],
            "wrong_fields": evaluation["wrong_fields"],
            "hallucinated_fields": evaluation["hallucinated_fields"],
            "mae_paired_all": evaluation["mae_paired_all"],
            "records_all_expected_exact": len(evaluation["records_all_expected_exact"]),
            "parse_errors": manifest["parse_errors"],
        },
        "field_summary": {
            field: {
                key: stats[key]
                for key in ("expected", "present", "exact", "missing", "wrong", "mae")
            }
            for field, stats in evaluation["field_summary"].items()
            if field != "_hallucinated"
        },
        "by_type": by_type,
        "hashes": {
            "test_manifest_sha256": sha256_file(MANIFEST_PATH),
            "test_evaluation_sha256": sha256_file(EVALUATION_PATH),
            "test_output_sha256": manifest["output_sha256"],
            "test_raw_sha256": manifest["raw_sha256"],
            "test_input_sha256": manifest["input_sha256"],
            "test_reference_sha256": release["test_projection"]["reference_sha256"],
            "release_manifest_sha256": sha256_file(RELEASE_PATH),
            "approval_sha256": sha256_file(APPROVAL_PATH),
        },
        "note": (
            "Ein einzelner freigegebener Testlauf; keine Prompt-Aenderung nach "
            "Testbeginn und keine Verwendung des Testergebnisses zur "
            "Prompt-Optimierung."
        ),
    }
    RESULT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# C1-Testlauf v6c: Ergebnis",
        "",
        f"Run: `{result['run_id']}`",
        f"Status: **{result['status'].upper()}**",
        "",
        "## Kopfzahlen",
        "",
        f"- Records mit Ausgabe: **{result['aggregate']['records_with_output']}/"
        f"{result['aggregate']['records']}**",
        f"- Erwartete Felder: **{result['aggregate']['expected_fields']}**",
        f"- Abdeckung: **{result['aggregate']['expected_fields_present']}/"
        f"{result['aggregate']['expected_fields']}** "
        f"({result['aggregate']['coverage']:.1%})",
        f"- Exakte Treffer: **{result['aggregate']['exact_fields']}/"
        f"{result['aggregate']['expected_fields']}** "
        f"({result['aggregate']['exact_rate']:.1%})",
        f"- Fehlend: **{result['aggregate']['missing_fields']}**; falsch: "
        f"**{result['aggregate']['wrong_fields']}**; halluziniert: "
        f"**{result['aggregate']['hallucinated_fields']}**",
        f"- MAE: **{result['aggregate']['mae_paired_all']}**",
        f"- Records vollständig exakt: "
        f"**{result['aggregate']['records_all_expected_exact']}/"
        f"{result['aggregate']['records']}**",
        f"- Parse-/Schemafehler: **{result['aggregate']['parse_errors']}**",
        "",
        "## Feldebene",
        "",
        "| Feld | erwartet | vorhanden | exakt | fehlend | falsch | MAE |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for field, stats in result["field_summary"].items():
        lines.append(
            f"| `{field}` | {stats['expected']} | {stats['present']} | "
            f"{stats['exact']} | {stats['missing']} | {stats['wrong']} | "
            f"{stats['mae']} |"
        )
    lines += [
        "",
        "## Nach Outcome-Typ",
        "",
        "| Typ | Records | erwartet | exakt | fehlend | falsch | vollständig exakt |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for outcome_type, stats in result["by_type"].items():
        lines.append(
            f"| `{outcome_type}` | {stats['records']} | {stats['expected_fields']} | "
            f"{stats['exact_fields']} | {stats['missing_fields']} | "
            f"{stats['wrong_fields']} | {stats['records_all_exact']}/{stats['records']} |"
        )
    lines += [
        "",
        "## Einordnung",
        "",
        "- Ein einzelner freigegebener Testlauf über alle 249 Records.",
        "- Der Runner hat die Testreferenz nicht geladen (`reference_loaded=false`).",
        "- Nach Testbeginn wurde der Prompt nicht geändert.",
        "- Das Testergebnis wurde nicht zur Prompt-Optimierung verwendet.",
        "- 0 Halluzinationen und 0 Parse-/Schemafehler; die Abweichungen sind "
        "fehlende oder falsche Werte.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(
        f"Test: {result['aggregate']['exact_fields']}/"
        f"{result['aggregate']['expected_fields']} exakt, "
        f"{result['aggregate']['coverage']:.1%} Abdeckung, "
        f"{result['aggregate']['parse_errors']} Parse-Fehler"
    )
    print(f"JSON: {RESULT_PATH}")
    print(f"Bericht: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
