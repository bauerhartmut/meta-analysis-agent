"""Tests fuer den externen Benchmark.

Geprueft werden Normalisierung, Abweichungsklassen, Kategorien, Armvertauschung
und die Behandlung unvollstaendiger Referenzen. Es werden keine Modelle
gestartet und keine produktiven Daten geschrieben.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import run_external_benchmark as bench  # noqa: E402


def yun_row(record_id: int = 1, outcome_type: str = "continuous") -> dict:
    values = (
        {
            "intervention_group_size": 30.0,
            "comparator_group_size": 28.0,
            "intervention_mean": 12.5,
            "comparator_mean": 9.5,
            "intervention_standard_deviation": 3.2,
            "comparator_standard_deviation": 2.8,
        }
        if outcome_type == "continuous"
        else {
            "intervention_group_size": 30.0,
            "comparator_group_size": 28.0,
            "intervention_events": 12.0,
            "comparator_events": 5.0,
        }
    )
    return {
        "record_id": record_id,
        "source": "yun2024",
        "study_id": "PMC1",
        "split": "test",
        "outcome_type": outcome_type,
        "ico": {"intervention": "dCBT-I", "comparator": "waitlist", "outcome": "ISI"},
        "curated_values": values,
        "reference_values": values,
        "audit_status": "verified_exact",
        "audit_method": "exact_pair_match",
        "audit_reason": "exact_arm_value_pair_match",
        "source_text_path": "x.md",
    }


def prediction(record_id: int = 1) -> dict:
    return {
        "record_id": record_id,
        "outcome_type": "continuous",
        "intervention_n": 30,
        "comparator_n": 28,
        "intervention_mean": 12.5,
        "comparator_mean": 9.5,
        "intervention_sd": 3.2,
        "comparator_sd": 2.8,
        "intervention_events": None,
        "comparator_events": None,
        "source_note": "",
    }


def test_normalize_maps_curated_values_and_flags_unavailable_dimensions() -> None:
    row = yun_row()
    row["reference_values"] = dict(row["curated_values"], intervention_mean=99.0)
    normalized = bench.normalize_reference(row)

    assert normalized["values"]["intervention_mean"] == 12.5
    assert normalized["original_reference_values"]["intervention_mean"] == 99.0
    assert normalized["provenance"]["value_source"] == "curated_values"
    assert normalized["usable_for_numeric_benchmark"] is True
    assert "timepoint" in normalized["unavailable_fields"]
    assert "source_span" in normalized["unavailable_fields"]


@pytest.mark.parametrize(
    ("reference", "predicted", "expected"),
    [
        (12.5, 12.5, "exakt"),
        (12.5, 12.51, "rundung_zulaessig"),
        (0.25, 25, "skalierung_prozent_anteil"),
        (12.5, 13.5, "abweichender_wert"),
    ],
)
def test_classify_value(reference: float, predicted: float, expected: str) -> None:
    values = {
        "intervention_n": 100.0,
        "intervention_sd": reference,
        "comparator_n": 100.0,
    }
    assert bench.classify_value("intervention_sd", reference, predicted, values) == expected


def test_classify_detects_sd_se_confusion() -> None:
    values = {"intervention_n": 100.0}
    assert bench.classify_value("intervention_sd", 10.0, 1.0, values) == "sd_se_verwechslung"


def test_record_with_all_exact_values_is_category_1() -> None:
    reference = bench.normalize_reference(yun_row())
    record = bench.compare_record(reference, prediction())

    assert record["category"] == bench.CATEGORY_1
    assert record["counts"]["exakt"] == 6
    assert record["n_comparable"] == 6


def test_missing_value_is_category_2() -> None:
    reference = bench.normalize_reference(yun_row())
    pred = prediction()
    pred["intervention_mean"] = None

    record = bench.compare_record(reference, pred)
    assert record["category"] == bench.CATEGORY_2
    assert record["category_reason"] == "fehlender_wert"
    assert record["counts"]["fehlender_wert"] == 1


def test_wrong_value_is_category_2() -> None:
    reference = bench.normalize_reference(yun_row())
    pred = prediction()
    pred["comparator_sd"] = 9.9

    record = bench.compare_record(reference, pred)
    assert record["category"] == bench.CATEGORY_2
    assert record["fields"]["comparator_sd"]["status"] == "abweichender_wert"


def test_no_output_is_category_3() -> None:
    reference = bench.normalize_reference(yun_row())
    record = bench.compare_record(reference, None)

    assert record["category"] == bench.CATEGORY_3
    assert record["category_reason"] == "keine_ausgabe_fuer_diesen_lauf"


def test_incomplete_reference_is_category_3_and_not_an_error() -> None:
    row = yun_row()
    row["curated_values"] = dict(row["curated_values"], comparator_mean=None)
    reference = bench.normalize_reference(row)

    record = bench.compare_record(reference, prediction())
    assert record["category"] == bench.CATEGORY_3
    assert record["fields"]["comparator_mean"]["status"] == "referenz_unvollstaendig"


def test_arm_swap_is_suspected() -> None:
    reference = bench.normalize_reference(yun_row())
    pred = prediction()
    pred.update({
        "intervention_n": 28,
        "comparator_n": 30,
        "intervention_mean": 9.5,
        "comparator_mean": 12.5,
        "intervention_sd": 2.8,
        "comparator_sd": 3.2,
    })

    record = bench.compare_record(reference, pred)
    assert record["swap_suspected"] is True
    assert record["category"] == bench.CATEGORY_2


def test_summary_keeps_categories_and_field_metrics_consistent() -> None:
    rows = [bench.normalize_reference(yun_row(1))]
    summary = bench.summarize_agent(rows, {1: prediction()}, "c1_pipeline")

    assert summary["expected_fields_total"] == 6
    assert summary["exact_fields"] == 6
    assert summary["wrong_fields"] == 0
    assert summary["missing_fields"] == 0
    assert summary["category_counts"][bench.CATEGORY_1] == 1
    assert summary["category_counts"][bench.CATEGORY_3] == 0
    assert summary["field_errors"] == []


def test_rounding_is_acceptable_but_reported_in_csv() -> None:
    reference = bench.normalize_reference(yun_row())
    pred = prediction()
    pred["intervention_mean"] = 12.51

    record = bench.compare_record(reference, pred)
    assert record["category"] == bench.CATEGORY_1
    errors = bench.errors_from_records([record], "c1_pipeline")
    assert len(errors) == 1
    assert errors[0]["deviation_type"] == "rundung_zulaessig"
    assert errors[0]["review_category"] == bench.CATEGORY_1


def test_consistent_percent_scaling_is_acceptable() -> None:
    row = yun_row()
    row["curated_values"] = {
        "intervention_group_size": 30.0,
        "comparator_group_size": 28.0,
        "intervention_mean": 0.82,
        "comparator_mean": 0.92,
        "intervention_standard_deviation": 0.05,
        "comparator_standard_deviation": 0.07,
    }
    reference = bench.normalize_reference(row)
    pred = prediction()
    pred.update({
        "intervention_mean": 82,
        "comparator_mean": 92,
        "intervention_sd": 5,
        "comparator_sd": 7,
    })

    record = bench.compare_record(reference, pred)
    assert record["category"] == bench.CATEGORY_1
    assert record["counts"]["skalierung_zulaessig"] == 4


def test_isolated_scale_deviation_stays_an_error() -> None:
    row = yun_row()
    row["curated_values"] = dict(row["curated_values"], comparator_standard_deviation=7.5)
    reference = bench.normalize_reference(row)
    pred = prediction()
    pred["comparator_sd"] = 0.07

    record = bench.compare_record(reference, pred)
    assert record["category"] == bench.CATEGORY_2
    assert record["fields"]["comparator_sd"]["status"] == "abweichender_wert"


def test_ab_comparison_absent_without_two_inputs(tmp_path: Path) -> None:
    reference_path = tmp_path / "reference.jsonl"
    reference_path.write_text("{}\n", encoding="utf-8")
    output_path = tmp_path / "out.jsonl"
    output_path.write_text("{}\n", encoding="utf-8")
    result = bench.build_result(
        [yun_row()],
        {"c1_pipeline": {1: prediction()}},
        reference_path=reference_path,
        output_paths={"c1_pipeline": output_path},
    )
    assert result["ab_comparison"]["available"] is False
    assert "keine separate B-Ausgabe" in result["ab_comparison"]["reason"]


def test_ab_comparison_counts_agreement(tmp_path: Path) -> None:
    reference_path = tmp_path / "reference.jsonl"
    reference_path.write_text("{}\n", encoding="utf-8")
    output_path = tmp_path / "out.jsonl"
    output_path.write_text("{}\n", encoding="utf-8")
    result = bench.build_result(
        [yun_row()],
        {"agent_a": {1: prediction()}, "agent_b": {1: prediction()}},
        reference_path=reference_path,
        output_paths={"agent_a": output_path, "agent_b": output_path},
    )
    assert result["ab_comparison"]["available"] is True
    assert result["ab_comparison"]["both_category_1"] == 1
