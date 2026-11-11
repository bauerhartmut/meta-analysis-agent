"""Unabhaengige Pruefung der C1-Testprojektion gegen den Freeze.

Der Pruefer importiert weder Projektor noch Runner. Er vergleicht die
projizierten Dateien direkt mit dem eingefrorenen Datensatz und schreibt
nur Zaehlungen und Hashes in den Bericht, keine Testwerte.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BENCH_ROOT.parent
PILOT_ROOT = BENCH_ROOT / "evaluation" / "c1_pilot"
FROZEN_PATH = BENCH_ROOT / "processed_data" / "yun_c1_frozen_275.jsonl"
FREEZE_MANIFEST_PATH = BENCH_ROOT / "validation" / "c1_freeze_manifest.json"
PROJECTION_DIR = PILOT_ROOT / "test_locked"
INPUT_PATH = PROJECTION_DIR / "test_input.jsonl"
REFERENCE_PATH = PROJECTION_DIR / "test_reference.jsonl"
PROJECTION_MANIFEST_PATH = PROJECTION_DIR / "test_projection_manifest.json"
DEV_INPUT_PATH = PILOT_ROOT / "dev_input.jsonl"
REPORT_PATH = PILOT_ROOT / "test_projection_verification.json"
REPORT_MD_PATH = PILOT_ROOT / "test_projection_verification.md"

INPUT_FIELDS = {
    "record_id", "study_id", "pmcid", "split", "outcome_type", "ico",
    "source_text_path",
}
REFERENCE_FIELDS = {
    "record_id", "study_id", "pmcid", "split", "outcome_type",
    "reference_values", "curated_values", "audit_status", "audit_reason",
    "correction",
}
REFERENCE_ONLY = {
    "reference_values", "curated_values", "audit_status", "audit_reason",
    "correction", "annotator_notes", "missing_fields", "audit_method",
}
ICO_FIELDS = {"intervention", "comparator", "outcome"}
EXPECTED_RECORDS = 249
EXPECTED_ARTICLES = 64
EXPECTED_TYPES = {"continuous": 156, "binary": 93}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_exists(path_text: str) -> bool:
    for base in (REPO_ROOT, BENCH_ROOT):
        if (base / path_text).exists():
            return True
    return False


def main() -> int:
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    if not all(path.exists() for path in (
        FROZEN_PATH, FREEZE_MANIFEST_PATH, INPUT_PATH, REFERENCE_PATH,
        PROJECTION_MANIFEST_PATH,
    )):
        print("ABBRUCH: Projektion oder Freeze-Datei fehlt.")
        return 2

    freeze = json.loads(FREEZE_MANIFEST_PATH.read_text(encoding="utf-8"))
    projection = json.loads(PROJECTION_MANIFEST_PATH.read_text(encoding="utf-8"))
    frozen = load_jsonl(FROZEN_PATH)
    test_source = [row for row in frozen if row.get("split") == "test"]
    inputs = load_jsonl(INPUT_PATH)
    references = load_jsonl(REFERENCE_PATH)
    dev_ids = {int(row["record_id"]) for row in load_jsonl(DEV_INPUT_PATH)}

    freeze_hash = sha256_file(FROZEN_PATH)
    input_hash = sha256_file(INPUT_PATH)
    reference_hash = sha256_file(REFERENCE_PATH)

    add("freeze_sha256", freeze_hash == freeze["files"]["processed_data/yun_c1_frozen_275.jsonl"]["sha256"])
    add("projection_records", len(inputs) == EXPECTED_RECORDS)
    add("reference_records", len(references) == EXPECTED_RECORDS)
    add("source_records", len(test_source) == EXPECTED_RECORDS)
    add("projection_input_sha256", projection.get("input_sha256") == input_hash)
    add("projection_reference_sha256", projection.get("reference_sha256") == reference_hash)
    add("projection_frozen_sha256", projection.get("frozen_sha256") == freeze_hash)

    input_ids = [int(row["record_id"]) for row in inputs]
    reference_ids = [int(row["record_id"]) for row in references]
    add("input_ids_unique", len(set(input_ids)) == EXPECTED_RECORDS)
    add("reference_ids_unique", len(set(reference_ids)) == EXPECTED_RECORDS)
    add("input_reference_same_ids", set(input_ids) == set(reference_ids))
    add("no_dev_test_id_overlap", not (set(input_ids) & dev_ids))

    add("input_schema", all(set(row) == INPUT_FIELDS for row in inputs))
    add("reference_schema", all(set(row) == REFERENCE_FIELDS for row in references))
    add("input_split_test", all(row.get("split") == "test" for row in inputs))
    add("reference_split_test", all(row.get("split") == "test" for row in references))
    add("input_ico_schema", all(set(row.get("ico", {})) == ICO_FIELDS for row in inputs))
    add("no_reference_fields_in_input",
        all(not (set(row) & REFERENCE_ONLY) for row in inputs))

    articles = {str(row["pmcid"]) for row in inputs}
    type_counts = dict(Counter(row["outcome_type"] for row in inputs))
    add("article_count", len(articles) == EXPECTED_ARTICLES)
    add("type_counts", type_counts == EXPECTED_TYPES)
    add("expected_fields_1308", EXPECTED_TYPES["continuous"] * 6 + EXPECTED_TYPES["binary"] * 4 == 1308)

    source_by_id = {int(row["record_id"]): row for row in test_source}
    input_by_id = {int(row["record_id"]): row for row in inputs}
    reference_by_id = {int(row["record_id"]): row for row in references}
    input_mismatches = sum(
        1 for record_id, source in source_by_id.items()
        if input_by_id.get(record_id) != {field: source[field] for field in INPUT_FIELDS}
    )
    reference_mismatches = sum(
        1 for record_id, source in source_by_id.items()
        if reference_by_id.get(record_id) != {field: source.get(field) for field in REFERENCE_FIELDS}
    )
    add("input_matches_freeze", input_mismatches == 0, f"{input_mismatches} Abweichungen")
    add("reference_matches_freeze", reference_mismatches == 0, f"{reference_mismatches} Abweichungen")

    missing_sources = sum(
        1 for row in inputs if not resolve_exists(str(row["source_text_path"]))
    )
    add("source_paths_exist", missing_sources == 0, f"{missing_sources} fehlend")

    policy = projection.get("test_policy", {})
    add("test_policy_locked", policy.get("locked") is True)
    add("reference_not_loaded_by_runner", policy.get("reference_loaded_by_runner") is False)
    add("no_prompt_optimization", policy.get("used_for_prompt_optimization") is False)

    passed = all(check["passed"] for check in checks)
    report = {
        "verified_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "status": "passed" if passed else "failed",
        "checks": checks,
        "counts": {
            "records": len(inputs),
            "articles": len(articles),
            "by_type": type_counts,
            "expected_fields": EXPECTED_TYPES["continuous"] * 6 + EXPECTED_TYPES["binary"] * 4,
        },
        "hashes": {
            "freeze_sha256": freeze_hash,
            "input_sha256": input_hash,
            "reference_sha256": reference_hash,
        },
        "note": "Nur Zaehlungen und Hashes; keine Testwerte im Bericht.",
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# C1-Testprojektion: Prüfbericht",
        "",
        f"Stand: {report['verified_at']}",
        f"Status: **{report['status'].upper()}**",
        "",
        "| Prüfung | Ergebnis |",
        "|---|---|",
    ]
    for check in checks:
        detail = f" ({check['detail']})" if check["detail"] else ""
        lines.append(f"| `{check['name']}` | {'OK' if check['passed'] else 'FEHLER'}{detail} |")
    lines += [
        "",
        "## Zählungen",
        "",
        f"- Records: {len(inputs)}",
        f"- Artikel: {len(articles)}",
        f"- Typen: {type_counts}",
        f"- Erwartete Felder: {report['counts']['expected_fields']}",
        "",
        "## Hashes",
        "",
        f"- Freeze: `{freeze_hash}`",
        f"- Test-Input: `{input_hash}`",
        f"- Test-Referenz: `{reference_hash}`",
        "",
        "Der Testsplit wurde für die Projektion gelesen, aber nicht für"
        " Prompt-Optimierung oder einen Modelllauf verwendet.",
        "",
    ]
    REPORT_MD_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(
        f"Projektion: {len(inputs)} Records, {len(articles)} Artikel, "
        f"Typen {type_counts}, Status {report['status'].upper()}"
    )
    print(f"Input-SHA256: {input_hash}")
    print(f"Referenz-SHA256: {reference_hash}")
    print(f"Bericht: {REPORT_PATH}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
