"""Tests fuer schema_v1.json und den Annotation-Validator."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT = BENCH_ROOT / "evaluation" / "multi_model_cross_validation"
SCHEMA_PATH = OUT / "schema_v1.json"
RELEASE_V6C = BENCH_ROOT / "evaluation" / "c1_pilot" / "release_v6c.json"

sys.path.insert(0, str(BENCH_ROOT / "scripts"))

from validate_crossval_annotation import load_schema, validate_record  # noqa: E402

REQUIRED_VALUE_FIELDS = [
    "value",
    "unit",
    "source_document",
    "page",
    "table_or_section",
    "source_context",
    "source_cell_or_location",
    "arm_id",
    "outcome_id",
    "timepoint_id",
    "assignment_confidence",
    "verification_status",
    "uncertainty_note",
]


def _schema() -> dict:
    return load_schema(SCHEMA_PATH)


def _valid_record() -> dict:
    schema = _schema()
    record = copy.deepcopy(schema["example"])
    record["arms"][0]["n"] = 30
    record["values"][0]["value"] = 12.5
    record["values"][0]["verification_status"] = "parsed_from_cell"
    record["values"][0]["assignment_confidence"] = "high"
    record["values"][0]["page"] = "4"
    return record


def test_schema_has_all_six_conflict_categories() -> None:
    categories = _schema()["conflict_categories"]
    assert sorted(categories) == ["C1", "C2", "C3", "C4", "C5", "C6"]
    for name in ("unanimity", "two_vs_one", "three_way", "missing_value",
                 "source_conflict", "structural_conflict"):
        assert any(name in text for text in categories.values())


def test_value_required_fields_match_contract() -> None:
    assert _schema()["value_required"] == REQUIRED_VALUE_FIELDS


def test_valid_record_passes() -> None:
    assert validate_record(_valid_record(), _schema()) == []


def test_missing_provenance_fails() -> None:
    record = _valid_record()
    del record["values"][0]["page"]
    errors = validate_record(record, _schema())
    assert any("page" in error for error in errors)


def test_unresolvable_arm_fails() -> None:
    record = _valid_record()
    record["values"][0]["arm_id"] = "arm_9"
    errors = validate_record(record, _schema())
    assert any("arm_id nicht aufloesbar" in error for error in errors)


def test_low_confidence_requires_note() -> None:
    record = _valid_record()
    record["values"][0]["assignment_confidence"] = "low"
    record["values"][0]["uncertainty_note"] = "  "
    errors = validate_record(record, _schema())
    assert any("uncertainty_note" in error for error in errors)


def test_value_must_be_number() -> None:
    record = _valid_record()
    record["values"][0]["value"] = "12,5"
    errors = validate_record(record, _schema())
    assert any("keine Zahl" in error for error in errors)


def test_unknown_page_requires_insufficient_status() -> None:
    record = _valid_record()
    record["values"][0]["page"] = "unbekannt"
    record["values"][0]["verification_status"] = "parsed_from_cell"
    errors = validate_record(record, _schema())
    assert any("Seite unbekannt" in error for error in errors)


def test_missing_values_are_allowed_as_null() -> None:
    record = _valid_record()
    record["values"][0]["value"] = None
    record["values"][0]["verification_status"] = "insufficient_evidence"
    record["values"][0]["uncertainty_note"] = "Wert nicht berichtet"
    record["values"][0]["page"] = "unbekannt"
    assert validate_record(record, _schema()) == []


def test_v6_prompt_hash_is_unchanged() -> None:
    release = json.loads(RELEASE_V6C.read_text(encoding="utf-8"))
    assert (
        release["candidate"]["prompt_sha256_all"]
        == "d0300215ff6bfd9dfbb81664f3cadaf19fa5bc3c019cce40db09c6e3524dca14"
    )
