"""C1-Testprojektion: Input und Referenz strikt trennen.

Der Projektor liest den eingefrorenen 275er-Datensatz nur mit
``--approve-test``. Er schreibt zwei getrennte Dateien:

- ``test_input.jsonl``: nur ICO, Quellpfad und Metadaten; keine Referenzwerte
- ``test_reference.jsonl``: Referenzwerte für die spätere Auswertung

Der Test-Input wird vom Runner verwendet; die Referenz wird dort nie geladen.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

BENCH_ROOT = Path(__file__).resolve().parents[1]
PILOT_ROOT = BENCH_ROOT / "evaluation" / "c1_pilot"
DEFAULT_FROZEN = BENCH_ROOT / "processed_data" / "yun_c1_frozen_275.jsonl"
DEFAULT_OUTPUT = PILOT_ROOT / "test_locked"

INPUT_FIELDS = (
    "record_id",
    "study_id",
    "pmcid",
    "split",
    "outcome_type",
    "ico",
    "source_text_path",
)
REFERENCE_FIELDS = (
    "record_id",
    "study_id",
    "pmcid",
    "split",
    "outcome_type",
    "reference_values",
    "curated_values",
    "audit_status",
    "audit_reason",
    "correction",
)
ICO_FIELDS = ("intervention", "comparator", "outcome")
EXPECTED_TEST_RECORDS = 249
EXPECTED_TEST_ARTICLES = 64
EXPECTED_TEST_TYPES = {"continuous": 156, "binary": 93}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def project_row(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Projiziert einen Test-Record ohne Referenzwerte im Input."""
    _require(row.get("split") == "test", "Record ist nicht split=test")
    missing = [field for field in INPUT_FIELDS if field not in row]
    _require(not missing, f"Record {row.get('record_id')}: fehlende Felder {missing}")
    ico = row.get("ico")
    _require(isinstance(ico, dict), f"Record {row.get('record_id')}: ico fehlt")
    _require(set(ico) == set(ICO_FIELDS), "ico hat nicht exakt die drei Felder")
    _require(isinstance(row.get("source_text_path"), str) and row["source_text_path"],
             "source_text_path fehlt")

    input_row = {field: row[field] for field in INPUT_FIELDS}
    _require("reference_values" not in input_row, "Referenz im Test-Input")
    _require("curated_values" not in input_row, "Kuratierung im Test-Input")

    reference_row = {field: row.get(field) for field in REFERENCE_FIELDS}
    _require(isinstance(reference_row["reference_values"], dict),
             "reference_values fehlt")
    return input_row, reference_row


def project_rows(rows: Iterable[dict[str, Any]], *,
                 expected_records: int | None = EXPECTED_TEST_RECORDS,
                 expected_articles: int | None = EXPECTED_TEST_ARTICLES,
                 expected_types: dict[str, int] | None = EXPECTED_TEST_TYPES
                 ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    inputs: list[dict[str, Any]] = []
    references: list[dict[str, Any]] = []
    for row in rows:
        input_row, reference_row = project_row(row)
        inputs.append(input_row)
        references.append(reference_row)

    validate_test_input(inputs, expected_records=expected_records)
    validate_test_reference(references, expected_records=expected_records)

    if expected_articles is not None:
        articles = {str(row["pmcid"]) for row in inputs}
        _require(len(articles) == expected_articles,
                 f"{len(articles)} statt {expected_articles} Test-Artikel")

    if expected_types is not None:
        counts = Counter(row["outcome_type"] for row in inputs)
        _require(dict(counts) == expected_types,
                 f"Test-Typen {dict(counts)} statt {expected_types}")

    return inputs, references


def validate_test_input(records: list[dict[str, Any]], *,
                        expected_records: int | None = EXPECTED_TEST_RECORDS) -> None:
    if expected_records is not None:
        _require(len(records) == expected_records,
                 f"{len(records)} statt {expected_records} Test-Inputs")
    ids: set[int] = set()
    for row in records:
        _require(set(row) == set(INPUT_FIELDS), "Test-Input hat falsche Felder")
        _require(row.get("split") == "test", "Test-Input enthält split != test")
        _require(row.get("outcome_type") in ("continuous", "binary"),
                 "Unbekannter outcome_type")
        _require(set(row.get("ico", {})) == set(ICO_FIELDS), "ICO-Felder falsch")
        record_id = int(row["record_id"])
        _require(record_id not in ids, f"doppelte Test-ID {record_id}")
        ids.add(record_id)


def validate_test_reference(records: list[dict[str, Any]], *,
                            expected_records: int | None = EXPECTED_TEST_RECORDS) -> None:
    if expected_records is not None:
        _require(len(records) == expected_records,
                 f"{len(records)} statt {expected_records} Test-Referenzen")
    ids: set[int] = set()
    for row in records:
        _require(set(row) == set(REFERENCE_FIELDS), "Test-Referenz hat falsche Felder")
        _require(row.get("split") == "test", "Test-Referenz enthält split != test")
        _require(isinstance(row.get("reference_values"), dict),
                 "Test-Referenz ohne reference_values")
        record_id = int(row["record_id"])
        _require(record_id not in ids, f"doppelte Test-Referenz-ID {record_id}")
        ids.add(record_id)


def build_projection(frozen_path: Path, output_dir: Path) -> dict[str, Any]:
    from run_c1_dev_pilot import load_jsonl, sha256_file, write_jsonl_atomic

    rows = [row for row in load_jsonl(frozen_path) if row.get("split") == "test"]
    inputs, references = project_rows(rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    input_path = output_dir / "test_input.jsonl"
    reference_path = output_dir / "test_reference.jsonl"
    write_jsonl_atomic(input_path, inputs)
    write_jsonl_atomic(reference_path, references)

    manifest = {
        "projection_version": 1,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "frozen_path": str(frozen_path.relative_to(BENCH_ROOT)).replace("\\", "/"),
        "frozen_sha256": sha256_file(frozen_path),
        "records": len(inputs),
        "articles": len({row["pmcid"] for row in inputs}),
        "by_type": dict(Counter(row["outcome_type"] for row in inputs)),
        "input_path": str(input_path.relative_to(BENCH_ROOT)).replace("\\", "/"),
        "input_sha256": sha256_file(input_path),
        "reference_path": str(reference_path.relative_to(BENCH_ROOT)).replace("\\", "/"),
        "reference_sha256": sha256_file(reference_path),
        "test_policy": {
            "locked": True,
            "reference_loaded_by_runner": False,
            "used_for_prompt_optimization": False,
        },
    }
    (output_dir / "test_projection_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen", type=Path, default=DEFAULT_FROZEN)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--approve-test", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not args.approve_test:
        print("ABBRUCH: Testprojektion nur mit ausdruecklichem --approve-test.")
        print("Der Testsplit wurde nicht geoeffnet.")
        return 2

    input_path = args.output_dir / "test_input.jsonl"
    reference_path = args.output_dir / "test_reference.jsonl"
    if not args.force and (input_path.exists() or reference_path.exists()):
        print(f"ABBRUCH: {args.output_dir} enthaelt bereits eine Projektion.")
        return 2

    try:
        manifest = build_projection(args.frozen, args.output_dir)
    except (OSError, ValueError, KeyError) as exc:
        print(f"ABBRUCH: {exc}")
        return 3

    print(
        f"Projektion: {manifest['records']} Records, {manifest['articles']} Artikel, "
        f"Typen {manifest['by_type']}"
    )
    print(f"Input-SHA256: {manifest['input_sha256']}")
    print(f"Referenz-SHA256: {manifest['reference_sha256']}")
    print("Referenz ist getrennt; der Runner darf sie nicht laden.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
