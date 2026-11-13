"""Tests fuer die Goldstandard-Adapter und den Ueberschneidungsbericht."""

from __future__ import annotations

import json
from pathlib import Path

BENCH = Path(__file__).resolve().parents[1]
CROSSVAL = BENCH / "evaluation" / "multi_model_cross_validation"
GOLD = CROSSVAL / "goldstandard_datasets"


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_eururology_counts_match_manifest() -> None:
    manifest = json.loads((GOLD / "eururology_v1" / "manifest.json").read_text(encoding="utf-8"))
    records = _jsonl(GOLD / "eururology_v1" / "records.jsonl")
    assert len(records) == manifest["records"]
    assert manifest["records_binary"] + manifest["records_continuous"] == manifest["records"]
    assert manifest["gold_columns_consistent_across_workbooks"] is True
    assert manifest["duplicate_record_ids"] == 0


def test_eururology_records_have_values_and_arms() -> None:
    records = _jsonl(GOLD / "eururology_v1" / "records.jsonl")
    for row in records:
        assert row["source"] == "eururology_osf_8fzps"
        assert [arm["arm_id"] for arm in row["arms"]] == ["arm_1", "arm_2"]
        assert any(value is not None for arm in row["arms"] for key, value in arm.items() if key != "arm_id")
        assert row["provenance"]["page"] is None
        assert row["provenance"]["source_cell_or_location"] is None
        assert row["timepoint_id"] is None


def test_eururology_keeps_missing_cells_as_null() -> None:
    records = _jsonl(GOLD / "eururology_v1" / "records.jsonl")
    with_missing = [row for row in records if row["missing_gold_fields"]]
    assert with_missing, "fehlende Zellen muessen markiert sein"
    for row in with_missing:
        assert set(row["missing_gold_fields"]).issubset(
            {"R1_rct", "N1_rct", "R2_rct", "N2_rct", "Mean1_RCT", "SD1_RCT", "N1_RCT", "Mean2_RCT", "SD2_RCT", "N2_RCT"}
        )


def test_pico_corpus_has_no_outcome_link() -> None:
    manifest = json.loads((GOLD / "pico_corpus_v1" / "manifest.json").read_text(encoding="utf-8"))
    records = _jsonl(GOLD / "pico_corpus_v1" / "records.jsonl")
    assert len(records) == manifest["records"] == 5024
    assert manifest["outcome_linked"] is False
    assert all(row["outcome_id"] is None for row in records)
    assert all(row["provenance"]["source_cell_or_location"].startswith("chars ") for row in records)


def test_overlap_report_declares_independence() -> None:
    report = json.loads((CROSSVAL / "dataset_overlap_report.json").read_text(encoding="utf-8"))
    assert report["verdict"]["eururology_independent"] is True
    assert report["verdict"]["pico_independent"] is True
    assert report["verdict"]["glass_independent"] is True
    assert report["eururology"]["overlap_yun_pmcid"] == []
    assert report["eururology"]["overlap_g5_pmcid"] == []
