#!/usr/bin/env python3
"""Externer Benchmark: numerische Extraktion gegen kuratierte Referenzdaten.

Der Benchmark ist ein eigenstaendiges Modul. Er liest die eingefrorene
Yun-Referenz (``processed_data/yun_c1_frozen_275.jsonl``) und bereits
vorhandene Extraktionsausgaben. Er startet kein Modell, veraendert keine
produktiven Studiendaten und ueberschreibt keine Outcome-Werte.

Standardlauf:
    python public_benchmark/scripts/run_external_benchmark.py

Optionale Agentenvergleiche (A/B) werden nur ausgewertet, wenn beide Dateien
explizit uebergeben werden:
    --agent-a pfad/a.jsonl --agent-b pfad/b.jsonl

Fehlt eine der beiden Dateien, wird der A/B-Vergleich als nicht verfuegbar
ausgewiesen. Es werden keine A/B-Zahlen geschaetzt.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REFERENCE = BENCH_ROOT / "processed_data" / "yun_c1_frozen_275.jsonl"
DEFAULT_OUTPUT = (
    BENCH_ROOT / "evaluation" / "c1_pilot" / "runs_test"
    / "c1_test_20261111_v6c" / "test_output.jsonl"
)
DEFAULT_OUT_DIR = BENCH_ROOT / "external_benchmark"
SOURCE_REGISTRY = BENCH_ROOT / "source_registry.json"

# Unser Feldname -> Feldname in der Yun-Referenz.
FIELD_MAP = {
    "intervention_n": "intervention_group_size",
    "comparator_n": "comparator_group_size",
    "intervention_mean": "intervention_mean",
    "comparator_mean": "comparator_mean",
    "intervention_sd": "intervention_standard_deviation",
    "comparator_sd": "comparator_standard_deviation",
    "intervention_events": "intervention_events",
    "comparator_events": "comparator_events",
}
EXPECTED_BY_TYPE = {
    "continuous": [
        "intervention_n",
        "comparator_n",
        "intervention_mean",
        "comparator_mean",
        "intervention_sd",
        "comparator_sd",
    ],
    "binary": [
        "intervention_n",
        "comparator_n",
        "intervention_events",
        "comparator_events",
    ],
}
ALL_FIELDS = list(FIELD_MAP)
SWAP_MAP = {
    "intervention_n": "comparator_n",
    "comparator_n": "intervention_n",
    "intervention_mean": "comparator_mean",
    "comparator_mean": "intervention_mean",
    "intervention_sd": "comparator_sd",
    "comparator_sd": "intervention_sd",
    "intervention_events": "comparator_events",
    "comparator_events": "intervention_events",
}
# Zwei Nachkommastellen: Abweichungen bis 0,011 gelten als zulaessige Rundung.
ROUNDING_TOLERANCE = 0.011
CATEGORY_1 = "1_automatisch_bestaetigt"
CATEGORY_2 = "2_automatisch_widerspruechlich"
CATEGORY_3 = "3_nicht_extern_validierbar"
UNVERIFIED_DIMENSIONS = ["timepoint", "source_span", "population", "outcome_text"]

DEVIATION_LABELS = {
    "exakt": "exakt",
    "rundung_zulaessig": "zulaessige Rundung",
    "skalierung_prozent_anteil": "Skalierung (Prozent/Anteil) pruefen",
    "skalierung_zulaessig": "zulaessige Skalierung (Prozent/Anteil)",
    "sd_se_verwechslung": "SD/SE-Vertauschung",
    "abweichender_wert": "abweichender Wert",
    "fehlender_wert": "fehlender Wert",
    "halluzinierter_wert": "Wert ohne Referenzfeld",
    "referenz_unvollstaendig": "Referenz unvollstaendig",
    "moegliche_armvertauschung": "moegliche Armvertauschung",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(BENCH_ROOT))
    except ValueError:
        return str(path)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def as_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def normalize_reference(row: dict[str, Any]) -> dict[str, Any]:
    """Ueberfuehrt einen Yun-Record in das einheitliche Referenzschema."""
    raw = row.get("curated_values") or {}
    original = row.get("reference_values") or raw
    values = {field: as_number(raw.get(source)) for field, source in FIELD_MAP.items()}
    return {
        "benchmark_id": f"{row.get('source', 'yun2024')}:{row['record_id']}",
        "record_id": int(row["record_id"]),
        "source": row.get("source", "yun2024"),
        "study_id": row.get("study_id"),
        "split": row.get("split"),
        "outcome_type": row.get("outcome_type"),
        "ico": {
            "intervention": (row.get("ico") or {}).get("intervention"),
            "comparator": (row.get("ico") or {}).get("comparator"),
            "outcome": (row.get("ico") or {}).get("outcome"),
        },
        "values": values,
        "original_reference_values": {
            source: as_number(original.get(source)) for source in FIELD_MAP.values()
        },
        "provenance": {
            "audit_status": row.get("audit_status"),
            "audit_method": row.get("audit_method"),
            "audit_reason": row.get("audit_reason"),
            "source_text_path": row.get("source_text_path"),
            "value_source": "curated_values",
        },
        "available_fields": sorted(field for field, value in values.items() if value is not None),
        "unavailable_fields": [
            field for field, value in values.items() if value is None
        ] + UNVERIFIED_DIMENSIONS,
        "usable_for_numeric_benchmark": sum(
            value is not None for value in values.values()
        ) == len(EXPECTED_BY_TYPE.get(row.get("outcome_type"), [])),
    }


def classify_value(
    field: str,
    reference: float,
    predicted: float,
    record_values: dict[str, float | None],
) -> str:
    if math.isclose(reference, predicted, rel_tol=0.0, abs_tol=1e-9):
        return "exakt"
    diff = abs(reference - predicted)
    if diff <= ROUNDING_TOLERANCE:
        return "rundung_zulaessig"
    if reference != 0 and (
        abs(predicted - reference * 100) <= max(ROUNDING_TOLERANCE, abs(reference * 100) * 0.001)
        or abs(predicted - reference / 100) <= max(ROUNDING_TOLERANCE, abs(reference / 100) * 0.001)
    ):
        return "skalierung_prozent_anteil"
    if field.endswith("_sd"):
        arm_n = as_number(record_values.get(field.replace("_sd", "_n")))
        if arm_n and arm_n > 0:
            if abs(predicted - reference / math.sqrt(arm_n)) <= max(ROUNDING_TOLERANCE, abs(reference) * 0.001):
                return "sd_se_verwechslung"
            if abs(predicted - reference * math.sqrt(arm_n)) <= max(ROUNDING_TOLERANCE, abs(reference) * 0.001):
                return "sd_se_verwechslung"
    return "abweichender_wert"


def arm_swap_suspected(
    predicted: dict[str, Any],
    reference_values: dict[str, float | None],
    expected_fields: list[str],
) -> bool:
    """Prueft, ob die Armwerte systematisch vertauscht wurden."""
    direct = 0
    swapped = 0
    compared = 0
    for field in expected_fields:
        ref = as_number(reference_values.get(field))
        pred = as_number(predicted.get(field))
        swap_ref = as_number(reference_values.get(SWAP_MAP[field]))
        if ref is None or pred is None:
            continue
        compared += 1
        if math.isclose(ref, pred, rel_tol=0.0, abs_tol=ROUNDING_TOLERANCE):
            direct += 1
        if swap_ref is not None and math.isclose(
            swap_ref, pred, rel_tol=0.0, abs_tol=ROUNDING_TOLERANCE
        ):
            swapped += 1
    if compared < 2:
        return False
    return swapped > direct and swapped >= compared - 1


def consistent_scale_representation(
    fields: dict[str, dict[str, Any]],
    expected_fields: list[str],
) -> bool:
    """Erkennt eine durchgaengige Prozent-/Anteilsskalierung aller Armwerte."""
    scale_fields = [
        field for field in expected_fields if field.endswith(("_mean", "_sd"))
    ]
    if len(scale_fields) < 2:
        return False
    ratios: list[float] = []
    for field in scale_fields:
        row = fields.get(field)
        if row is None:
            return False
        reference = as_number(row["reference"])
        predicted = as_number(row["predicted"])
        if not reference or not predicted:
            return False
        ratios.append(predicted / reference)
    return (
        all(abs(ratio - 100) <= 1 for ratio in ratios)
        or all(abs(ratio - 0.01) <= 0.0001 for ratio in ratios)
    )


def compare_record(
    reference: dict[str, Any],
    prediction: dict[str, Any] | None,
) -> dict[str, Any]:
    expected_fields = EXPECTED_BY_TYPE[reference["outcome_type"]]
    result: dict[str, Any] = {
        "record_id": reference["record_id"],
        "study_id": reference["study_id"],
        "outcome_type": reference["outcome_type"],
        "audit_status": reference["provenance"]["audit_status"],
        "has_output": prediction is not None,
        "schema_error": "",
        "fields": {},
        "counts": Counter(),
        "swap_suspected": False,
        "category": CATEGORY_3,
        "category_reason": "",
        "unverified_dimensions": list(UNVERIFIED_DIMENSIONS),
    }
    result["n_comparable"] = sum(
        1 for field in expected_fields if reference["values"].get(field) is not None
    )
    if prediction is None:
        result["category_reason"] = "keine_ausgabe_fuer_diesen_lauf"
        return result

    if prediction.get("outcome_type") != reference["outcome_type"]:
        result["schema_error"] = (
            f"outcome_type {prediction.get('outcome_type')!r} statt "
            f"{reference['outcome_type']!r}"
        )

    for field in ALL_FIELDS:
        ref_value = reference["values"].get(field)
        pred_raw = prediction.get(field)
        pred_value = as_number(pred_raw)
        field_row = {
            "field": field,
            "reference": ref_value,
            "predicted": pred_raw,
            "status": "",
            "abs_diff": None,
        }
        if field not in expected_fields:
            if pred_value is not None:
                field_row["status"] = "halluzinierter_wert"
                field_row["abs_diff"] = None
            else:
                continue
        elif ref_value is None:
            field_row["status"] = "referenz_unvollstaendig"
        elif pred_value is None:
            field_row["status"] = "fehlender_wert"
        else:
            field_row["status"] = classify_value(
                field, ref_value, pred_value, reference["values"]
            )
            field_row["abs_diff"] = round(abs(ref_value - pred_value), 6)
        result["fields"][field] = field_row

    # Eine Faktor-100-Abweichung ist nur dann eine zulaessige Darstellung,
    # wenn alle Armwerte desselben Records konsistent skaliert sind.
    scale_ok = consistent_scale_representation(result["fields"], expected_fields)
    for field_row in result["fields"].values():
        if field_row["status"] == "skalierung_prozent_anteil":
            field_row["status"] = (
                "skalierung_zulaessig" if scale_ok else "abweichender_wert"
            )
    result["counts"] = Counter(
        field_row["status"] for field_row in result["fields"].values()
    )

    result["swap_suspected"] = arm_swap_suspected(
        prediction, reference["values"], expected_fields
    )

    comparable = sum(
        1 for row in result["fields"].values()
        if row["status"] != "referenz_unvollstaendig"
    )
    if comparable == 0:
        result["category"] = CATEGORY_3
        result["category_reason"] = "keine_vergleichbaren_felder"
    elif result["counts"]["abweichender_wert"] or result["counts"]["fehlender_wert"]:
        result["category"] = CATEGORY_2
        result["category_reason"] = (
            "abweichender_wert" if result["counts"]["abweichender_wert"]
            else "fehlender_wert"
        )
    elif result["counts"]["halluzinierter_wert"] or result["schema_error"]:
        result["category"] = CATEGORY_2
        result["category_reason"] = "schema_oder_halluzination"
    elif result["counts"]["referenz_unvollstaendig"]:
        result["category"] = CATEGORY_3
        result["category_reason"] = "referenz_unvollstaendig"
    elif result["swap_suspected"]:
        result["category"] = CATEGORY_2
        result["category_reason"] = "moegliche_armvertauschung"
    else:
        result["category"] = CATEGORY_1
        result["category_reason"] = "numerisch_bestaetigt"
    return result


def summarize_agent(
    reference_rows: list[dict[str, Any]],
    predictions: dict[int, dict[str, Any]],
    agent: str,
) -> dict[str, Any]:
    record_results = [compare_record(ref, predictions.get(ref["record_id"]))
                      for ref in reference_rows]
    field_stats = {
        field: {
            "expected": 0, "present": 0, "exact": 0, "rounding": 0,
            "wrong": 0, "missing": 0, "incomplete_reference": 0,
            "abs_diff_sum": 0.0, "paired": 0,
        }
        for field in ALL_FIELDS
    }
    for record in record_results:
        for field, row in record["fields"].items():
            stats = field_stats[field]
            if row["status"] == "referenz_unvollstaendig":
                stats["incomplete_reference"] += 1
                continue
            stats["expected"] += 1
            if row["status"] == "fehlender_wert":
                stats["missing"] += 1
                continue
            stats["present"] += 1
            if row["status"] == "exakt":
                stats["exact"] += 1
            elif row["status"] == "rundung_zulaessig":
                stats["rounding"] += 1
            elif row["status"] == "skalierung_zulaessig":
                stats["rounding"] += 1
            else:
                stats["wrong"] += 1
            if row["abs_diff"] is not None:
                stats["paired"] += 1
                stats["abs_diff_sum"] += row["abs_diff"]

    field_summary = {}
    for field, stats in field_stats.items():
        field_summary[field] = {
            **stats,
            "exact_rate": round(stats["exact"] / stats["expected"], 4)
            if stats["expected"] else None,
            "acceptable_rate": round(
                (stats["exact"] + stats["rounding"]) / stats["expected"], 4
            ) if stats["expected"] else None,
            "coverage": round(stats["present"] / stats["expected"], 4)
            if stats["expected"] else None,
            "mae": round(stats["abs_diff_sum"] / stats["paired"], 4)
            if stats["paired"] else None,
        }

    categories: dict[str, list[int]] = {CATEGORY_1: [], CATEGORY_2: [], CATEGORY_3: []}
    reasons: Counter[str] = Counter()
    for record in record_results:
        categories[record["category"]].append(record["record_id"])
        reasons[record["category_reason"]] += 1

    expected_total = sum(stats["expected"] for stats in field_stats.values())
    exact_total = sum(stats["exact"] for stats in field_stats.values())
    rounding_total = sum(stats["rounding"] for stats in field_stats.values())
    missing_total = sum(stats["missing"] for stats in field_stats.values())
    wrong_total = sum(stats["wrong"] for stats in field_stats.values())
    impossible_total = sum(
        stats["incomplete_reference"] for stats in field_stats.values()
    )
    paired_total = sum(stats["paired"] for stats in field_stats.values())
    abs_diff_total = sum(stats["abs_diff_sum"] for stats in field_stats.values())

    by_type: dict[str, dict[str, Any]] = {}
    for outcome_type in EXPECTED_BY_TYPE:
        ids = {
            record["record_id"] for record in record_results
            if record["outcome_type"] == outcome_type
        }
        type_fields = [
            field for field in EXPECTED_BY_TYPE[outcome_type]
        ]
        type_expected = sum(field_summary[field]["expected"] for field in type_fields)
        type_exact = sum(field_summary[field]["exact"] for field in type_fields)
        type_rows = [record for record in record_results
                     if record["outcome_type"] == outcome_type]
        by_type[outcome_type] = {
            "records": len(ids),
            "records_with_output": sum(row["has_output"] for row in type_rows),
            "expected_fields": type_expected,
            "exact_fields": type_exact,
            "exact_rate": round(type_exact / type_expected, 4) if type_expected else None,
            "all_exact_records": sum(
                1 for row in type_rows
                if row["has_output"] and not row["schema_error"]
                and row["n_comparable"] > 0
                and row["counts"]["exakt"] == row["n_comparable"]
            ),
            "category_1_records": sum(
                1 for row in type_rows if row["category"] == CATEGORY_1
            ),
            "category_2_records": sum(
                1 for row in type_rows if row["category"] == CATEGORY_2
            ),
            "category_3_records": sum(
                1 for row in type_rows if row["category"] == CATEGORY_3
            ),
        }

    criteria = {
        "study_identification": {
            "status": "nicht_pruefbar",
            "reason": "Der Lauf erhielt die Studie als Input; es gab keine freie Studienidentifikation.",
        },
        "population": {
            "status": "nicht_pruefbar",
            "reason": "Die Referenz annotiert keine Population; der Input enthaelt nur ICO.",
        },
        "intervention": {
            "status": "nicht_pruefbar",
            "reason": "Interventionsname ist im Input vorgegeben und wird nicht extrahiert.",
        },
        "comparator": {
            "status": "nicht_pruefbar",
            "reason": "Comparatorsname ist im Input vorgegeben und wird nicht extrahiert.",
        },
        "outcome": {
            "status": "nicht_pruefbar",
            "reason": "Outcome-Text ist im Input vorgegeben; Precision/Recall/F1 der Outcome-Erkennung sind mit diesem Lauf nicht messbar.",
        },
        "timepoint": {
            "status": "nicht_pruefbar",
            "reason": "Yun hat kein Zeitpunktfeld; die Ausgabe hat kein strukturiertes Zeitpunktfeld.",
        },
        "n": {
            "status": "gemessen",
            "fields": ["intervention_n", "comparator_n"],
        },
        "events": {
            "status": "gemessen",
            "fields": ["intervention_events", "comparator_events"],
        },
        "mean": {
            "status": "gemessen",
            "fields": ["intervention_mean", "comparator_mean"],
        },
        "sd": {
            "status": "gemessen",
            "fields": ["intervention_sd", "comparator_sd"],
        },
        "source": {
            "status": "nicht_pruefbar",
            "reason": "Die Referenz hat keine Evidenzspannen; source_note ist Freitext ohne Referenzabgleich.",
        },
    }

    return {
        "agent": agent,
        "records": len(record_results),
        "records_with_output": sum(row["has_output"] for row in record_results),
        "records_without_output": sum(not row["has_output"] for row in record_results),
        "expected_fields_total": expected_total,
        "exact_fields": exact_total,
        "rounding_fields": rounding_total,
        "acceptable_fields": exact_total + rounding_total,
        "missing_fields": missing_total,
        "wrong_fields": wrong_total,
        "incomplete_reference_fields": impossible_total,
        "exact_rate": round(exact_total / expected_total, 4) if expected_total else None,
        "acceptable_rate": round(
            (exact_total + rounding_total) / expected_total, 4
        ) if expected_total else None,
        "coverage": round(
            sum(stats["present"] for stats in field_stats.values()) / expected_total, 4
        ) if expected_total else None,
        "mae_paired": round(abs_diff_total / paired_total, 4) if paired_total else None,
        "schema_or_parse_error_records": sum(
            1 for row in record_results if row["schema_error"]
        ),
        "suspected_arm_swaps": sum(row["swap_suspected"] for row in record_results),
        "records_all_exact": sum(
            1 for row in record_results
            if row["has_output"] and not row["schema_error"]
            and row["n_comparable"] > 0
            and row["counts"]["exakt"] == row["n_comparable"]
        ),
        "records_all_acceptable": sum(
            1 for row in record_results
            if row["has_output"] and not row["schema_error"]
            and row["n_comparable"] > 0
            and row["counts"]["exakt"] + row["counts"]["rundung_zulaessig"]
            + row["counts"]["skalierung_zulaessig"]
            == row["n_comparable"]
        ),
        "category_counts": {key: len(value) for key, value in categories.items()},
        "category_records": categories,
        "category_reasons": dict(reasons),
        "fields": field_summary,
        "by_type": by_type,
        "criteria": criteria,
        "outcome_detection": {
            "precision": None,
            "recall": None,
            "f1": None,
            "reason": "Outcome-Text war im Input vorgegeben; der Lauf prueft keine freie Outcome-Erkennung.",
        },
        "arm_assignment": {
            "status": "teilweise_pruefbar",
            "suspected_swaps": sum(row["swap_suspected"] for row in record_results),
            "reason": "Armnamen sind im Input vorgegeben; automatisch pruefbar ist nur eine systematische Wertvertauschung.",
        },
        "timepoint_agreement": {
            "status": "nicht_pruefbar",
            "reason": "Kein Zeitpunktfeld in Referenz und Ausgabe.",
        },
        "source_agreement": {
            "status": "nicht_pruefbar",
            "reason": "Keine Referenz-Evidenzspannen; Freitext-Source-Note ist nicht maschinell abgleichbar.",
        },
        "field_errors": errors_from_records(record_results, agent),
        "records_detail": record_results,
    }


def errors_from_records(
    record_results: list[dict[str, Any]], agent: str
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for record in record_results:
        if record["swap_suspected"]:
            errors.append({
                "record_id": record["record_id"],
                "study_id": record["study_id"],
                "outcome_type": record["outcome_type"],
                "agent": agent,
                "field": "*",
                "reference_value": None,
                "predicted_value": None,
                "abs_diff": None,
                "deviation_type": "moegliche_armvertauschung",
                "review_category": CATEGORY_2,
                "note": "Armwerte passen besser zu den vertauschten Referenzarmen.",
            })
        for field, row in record["fields"].items():
            if row["status"] in ("exakt",):
                continue
            if row["status"] == "referenz_unvollstaendig":
                review_category = CATEGORY_3
            elif row["status"] in (
                "rundung_zulaessig", "skalierung_zulaessig",
            ):
                review_category = CATEGORY_1
            else:
                review_category = CATEGORY_2
            errors.append({
                "record_id": record["record_id"],
                "study_id": record["study_id"],
                "outcome_type": record["outcome_type"],
                "agent": agent,
                "field": field,
                "reference_value": row["reference"],
                "predicted_value": row["predicted"],
                "abs_diff": row["abs_diff"],
                "deviation_type": row["status"],
                "review_category": review_category,
                "note": DEVIATION_LABELS.get(row["status"], row["status"]),
            })
    return errors


def build_ab_comparison(agent_a: dict[str, Any], agent_b: dict[str, Any]) -> dict[str, Any]:
    a = {row["record_id"]: row for row in agent_a["records_detail"]}
    b = {row["record_id"]: row for row in agent_b["records_detail"]}
    shared = sorted(set(a) & set(b))
    both_cat1 = sum(
        1 for record_id in shared
        if a[record_id]["category"] == CATEGORY_1
        and b[record_id]["category"] == CATEGORY_1
    )
    only_a = sum(
        1 for record_id in shared
        if a[record_id]["category"] == CATEGORY_1
        and b[record_id]["category"] != CATEGORY_1
    )
    only_b = sum(
        1 for record_id in shared
        if b[record_id]["category"] == CATEGORY_1
        and a[record_id]["category"] != CATEGORY_1
    )
    neither = len(shared) - both_cat1 - only_a - only_b
    field_disagreements = Counter()
    for record_id in shared:
        for field in a[record_id]["fields"]:
            status_a = a[record_id]["fields"][field]["status"]
            status_b = b[record_id]["fields"][field]["status"]
            if status_a != status_b:
                field_disagreements[field] += 1
    return {
        "available": True,
        "shared_records": len(shared),
        "both_category_1": both_cat1,
        "only_a_category_1": only_a,
        "only_b_category_1": only_b,
        "neither_category_1": neither,
        "field_status_disagreements": dict(field_disagreements),
        "note": "Getrennte Ausgaben; keine gemeinsame Einsicht der Agenten.",
    }


def build_result(
    reference_rows: list[dict[str, Any]],
    outputs: dict[str, dict[int, dict[str, Any]]],
    *,
    reference_path: Path,
    output_paths: dict[str, Path],
) -> dict[str, Any]:
    normalized = [normalize_reference(row) for row in reference_rows]
    agents = {
        name: summarize_agent(normalized, predictions, name)
        for name, predictions in outputs.items()
    }
    primary = "c1_pipeline" if "c1_pipeline" in agents else next(iter(agents))
    ab = (
        build_ab_comparison(agents["agent_a"], agents["agent_b"])
        if {"agent_a", "agent_b"} <= set(agents)
        else {
            "available": False,
            "reason": (
                "Kein A/B-Vergleich: Es liegt keine separate B-Ausgabe vor. "
                "Die vorhandene C1-Ausgabe ist ein Pipeline-Lauf, keine "
                "unabhaengige menschliche Zweitannotation."
            ),
        }
    )
    registry = {}
    yun_entry = {}
    if SOURCE_REGISTRY.exists():
        registry = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
        for entry in registry.get("sources", []):
            if entry.get("id") == "yun2024":
                yun_entry = entry
                break

    return {
        "benchmark_version": 1,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scope": "numeric_outcome_validation_only",
        "primary_agent": primary,
        "reference": {
            "source": "Yun et al. 2024",
            "path": display_path(reference_path),
            "sha256": sha256_file(reference_path),
            "records": len(normalized),
            "articles": len({row["study_id"] for row in normalized}),
            "split": dict(Counter(row["split"] for row in normalized)),
            "license": yun_entry.get("license"),
            "repository": yun_entry.get("repository"),
            "git_commit": yun_entry.get("git_commit"),
            "curation": "validation/yun_audit_410.jsonl, 275 usable records",
        },
        "outputs": {
            name: {
                "path": display_path(path),
                "sha256": sha256_file(path),
                "records": len(outputs[name]),
            }
            for name, path in output_paths.items()
        },
        "model_run": False,
        "network_run": False,
        "productive_data_modified": False,
        "ab_comparison": ab,
        "agents": agents,
        "categories": {
            CATEGORY_1: {
                "label": "Automatisch bestaetigt",
                "definition": "Alle vergleichbaren numerischen Felder stimmen exakt, innerhalb der Rundungstoleranz oder als durchgaengig konsistente Prozent-/Anteilsskalierung ueberein; kein Schemafehler, keine moegliche Armvertauschung.",
                "limits": (
                    "Bestaetigt nur die numerischen Felder. Zeitpunkt, Population, "
                    "Outcome-Text und Quellenstelle sind mit Yun nicht pruefbar. "
                    "Keine klinisch-wissenschaftliche Freigabe."
                ),
            },
            CATEGORY_2: {
                "label": "Automatisch widerspruechlich",
                "definition": "Mindestens ein vergleichbarer Wert weicht ab, fehlt oder ist schemawidrig; oder die Armwerte passen besser zu vertauschten Armen.",
                "limits": "Kann zulaessige, aber nicht erkannte Darstellungsform sein; manuelle Einzelfallpruefung.",
            },
            CATEGORY_3: {
                "label": "Nicht extern validierbar",
                "definition": "Keine Ausgabe fuer diesen Lauf, unvollstaendige Referenz oder keine vergleichbaren Felder.",
                "limits": "Kein Fehler der Pipeline; es fehlt die Vergleichsgrundlage.",
            },
        },
        "limitations": [
            "Die Referenz ist eine konsolidierte Annotation, kein unabhaengiger blinder Zweitbewerter.",
            "Yun enthaelt keinen Zeitpunkt, keine Evidenzspanne und keine Populationsannotation.",
            "Der Lauf prueft keine freie Studien-, Arm- oder Outcome-Erkennung, weil die ICO-Vorgabe im Input lag.",
            "Die C1-Ausgabe ist ein einzelner eingefrorener Testlauf, keine A/B-Messung.",
            "Die Referenz selbst kann Fehler enthalten; 1 Record wurde quellenbasiert korrigiert.",
        ],
    }


def write_errors_csv(
    path: Path,
    agents: dict[str, dict[str, Any]],
) -> None:
    fieldnames = [
        "run_id", "record_id", "study_id", "outcome_type", "agent", "field",
        "reference_value", "predicted_value", "abs_diff", "deviation_type",
        "review_category", "note",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for agent in agents.values():
            for error in agent["field_errors"]:
                writer.writerow({
                    "run_id": agent["agent"],
                    "record_id": error["record_id"],
                    "study_id": error["study_id"],
                    "outcome_type": error["outcome_type"],
                    "agent": error["agent"],
                    "field": error["field"],
                    "reference_value": "" if error["reference_value"] is None
                    else error["reference_value"],
                    "predicted_value": "" if error["predicted_value"] is None
                    else error["predicted_value"],
                    "abs_diff": "" if error["abs_diff"] is None else error["abs_diff"],
                    "deviation_type": error["deviation_type"],
                    "review_category": error["review_category"],
                    "note": error["note"],
                })


def render_markdown(result: dict[str, Any]) -> str:
    agent = result["agents"][result["primary_agent"]]
    counts = agent["category_counts"]
    lines = [
        "# Externer Benchmark v1: Numerische Outcome-Extraktion",
        "",
        f"Erstellt: {result['created_at']}",
        "",
        "## Zweck und Abgrenzung",
        "",
        "Dieser Benchmark vergleicht die vorhandene, eingefrorene C1-Ausgabe mit "
        "der kuratierten numerischen Referenz aus Yun et al. 2024. Er startet "
        "kein Modell, veraendert keine produktiven Studiendaten und trifft "
        "keine klinische Eignungsentscheidung. Er ist **keine A/B-Messung**.",
        "",
        "## Datengrundlage",
        "",
        f"- Referenz: `{result['reference']['path']}` "
        f"({result['reference']['records']} Records, "
        f"{result['reference']['articles']} Artikel)",
        f"- Quelle: {result['reference']['source']}, "
        f"Commit `{result['reference']['git_commit']}`",
        f"- Lizenz: {result['reference']['license']}",
    ]
    for name, output in result["outputs"].items():
        lines.append(
            f"- Ausgabe `{name}`: `{output['path']}` ({output['records']} Records)"
        )
    lines += [
        "",
        "## Kopfzahlen",
        "",
        f"- Vergleichbare Records: **{agent['records_with_output']}/{agent['records']}**",
        f"- Erwartete numerische Felder: **{agent['expected_fields_total']}**",
        f"- Exakt: **{agent['exact_fields']}/{agent['expected_fields_total']}** "
        f"({(agent['exact_rate'] or 0):.1%})",
        f"- Mit Rundung/Skalierung akzeptabel: **{agent['acceptable_fields']}"
        f"/{agent['expected_fields_total']}** ({(agent['acceptable_rate'] or 0):.1%})",
        f"- Fehlend: **{agent['missing_fields']}**; abweichend: "
        f"**{agent['wrong_fields']}**; Referenz unvollstaendig: "
        f"**{agent['incomplete_reference_fields']}**",
        f"- Abdeckung: **{(agent['coverage'] or 0):.1%}**; MAE gepaart: "
        f"**{agent['mae_paired']}**",
        f"- Records vollstaendig exakt: **{agent['records_all_exact']}**; "
        f"vollstaendig akzeptabel: **{agent['records_all_acceptable']}**",
        f"- Vermutete Armvertauschungen: **{agent['suspected_arm_swaps']}**",
        "",
        "## Kategorien",
        "",
        "| Kategorie | Records | Bedeutung |",
        "|---|---:|---|",
        f"| 1 automatisch bestaetigt | {counts[CATEGORY_1]} | numerisch exakt oder gerundet, kein Schemafehler |",
        f"| 2 automatisch widerspruechlich | {counts[CATEGORY_2]} | abweichend, fehlend, schemawidrig oder Armvertauschung |",
        f"| 3 nicht extern validierbar | {counts[CATEGORY_3]} | keine Ausgabe, unvollstaendige Referenz oder nicht vergleichbar |",
        "",
        "Kategorie 1 bestaetigt **nur die numerischen Felder**. Zeitpunkt, "
        "Population, Outcome-Text und Quellenstelle bleiben ungeprueft; eine "
        "klinisch-wissenschaftliche Freigabe ist das nicht.",
        "",
        "## Feldebene",
        "",
        "| Feld | erwartet | vorhanden | exakt | Rundung/Skalierung | abweichend | fehlend | exakt % | MAE |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for field, stats in agent["fields"].items():
        lines.append(
            f"| `{field}` | {stats['expected']} | {stats['present']} | "
            f"{stats['exact']} | {stats['rounding']} | {stats['wrong']} | "
            f"{stats['missing']} | {(stats['exact_rate'] or 0):.1%} | "
            f"{stats['mae'] if stats['mae'] is not None else '-'} |"
        )
    lines += [
        "",
        "## Vergleichskriterien",
        "",
        "| Kriterium | Status | Begruendung |",
        "|---|---|---|",
    ]
    for criterion, detail in agent["criteria"].items():
        lines.append(
            f"| {criterion} | {detail['status']} | {detail.get('reason', 'Feldmetriken siehe oben')} |"
        )
    lines += [
        "",
        "## Fehlerklassen",
        "",
        "| Klasse | Anzahl |",
        "|---|---:|",
    ]
    deviation_counts = Counter(
        error["deviation_type"] for error in agent["field_errors"]
    )
    for deviation, count in deviation_counts.most_common():
        lines.append(f"| {DEVIATION_LABELS.get(deviation, deviation)} | {count} |")
    lines += [
        "",
        "Die vollstaendige Einzelliste liegt in "
        "`external_benchmark_errors_v1.csv`.",
        "",
        "## A/B-Vergleich",
        "",
    ]
    if result["ab_comparison"]["available"]:
        ab = result["ab_comparison"]
        lines += [
            f"- Gemeinsame Records: {ab['shared_records']}",
            f"- Beide Kategorie 1: {ab['both_category_1']}",
            f"- Nur A Kategorie 1: {ab['only_a_category_1']}",
            f"- Nur B Kategorie 1: {ab['only_b_category_1']}",
            f"- Keiner Kategorie 1: {ab['neither_category_1']}",
        ]
    else:
        lines.append(result["ab_comparison"]["reason"])
    lines += [
        "",
        "## Grenzen",
        "",
    ]
    lines += [f"- {item}" for item in result["limitations"]]
    lines += [
        "",
        "## Empfehlung",
        "",
        "- Kategorie 1 kann die numerische Sichtpruefung unterstuetzen, aber "
        "nicht die Zeitpunkt-, Quellen- und Populationspruefung ersetzen.",
        "- Kategorie 2 ist die Arbeitsliste fuer die manuelle Pruefung.",
        "- Kategorie 3 braucht eine andere Referenz oder eine menschliche "
        "Erstpruefung; sie ist kein Pipeline-Fehler.",
        "- Vor einer klinisch-wissenschaftlichen Freigabe bleibt eine "
        "fachliche Pruefung von Zeitpunkt, Armzuordnung und Quellenstelle noetig.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--agent-a", type=Path)
    parser.add_argument("--agent-b", type=Path)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    reference_rows = load_jsonl(args.reference)
    outputs: dict[str, dict[int, dict[str, Any]]] = {}
    output_paths: dict[str, Path] = {}
    if args.agent_a and args.agent_b:
        outputs["agent_a"] = {
            int(row["record_id"]): row for row in load_jsonl(args.agent_a)
        }
        outputs["agent_b"] = {
            int(row["record_id"]): row for row in load_jsonl(args.agent_b)
        }
        output_paths["agent_a"] = args.agent_a
        output_paths["agent_b"] = args.agent_b
    else:
        outputs["c1_pipeline"] = {
            int(row["record_id"]): row for row in load_jsonl(args.output)
        }
        output_paths["c1_pipeline"] = args.output

    result = build_result(
        reference_rows, outputs,
        reference_path=args.reference,
        output_paths=output_paths,
    )
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "external_benchmark_results_v1.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (args.out_dir / "external_benchmark_results_v1.md").write_text(
        render_markdown(result), encoding="utf-8",
    )
    write_errors_csv(
        args.out_dir / "external_benchmark_errors_v1.csv",
        result["agents"],
    )

    agent = result["agents"][result["primary_agent"]]
    print(
        f"Records: {agent['records_with_output']}/{agent['records']}; "
        f"exakt {agent['exact_fields']}/{agent['expected_fields_total']} "
        f"({(agent['exact_rate'] or 0):.1%}); Kategorien "
        f"{agent['category_counts']}"
    )
    print(f"JSON: {args.out_dir / 'external_benchmark_results_v1.json'}")
    print(f"CSV:  {args.out_dir / 'external_benchmark_errors_v1.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
