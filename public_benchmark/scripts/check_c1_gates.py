#!/usr/bin/env python3
"""Prüft eine C1-Evaluation gegen die Gates G1-G5.

Der Checker ist deterministisch, liest keine Modellausgabe neu und startet
keinen Modelllauf. Schwellen und kritische Felder kommen aus
``c1_acceptance_gates_v1.json``.

Beispiel:
    PYTHONIOENCODING=utf-8 .venv/bin/python.exe \
        public_benchmark/scripts/check_c1_gates.py \
        --evaluation public_benchmark/evaluation/c1_pilot/runs_test/\
c1_test_20261111_v6c/test_evaluation.json \
        --gates public_benchmark/evaluation/c1_pilot/\
c1_acceptance_gates_v1.json \
        --output public_benchmark/evaluation/c1_pilot/\
gate_report_v6c.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON-Objekt erwartet")
    return value


def _share(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _hex_digest(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value.lower()
    )


def check_g1(evaluation: dict[str, Any]) -> dict[str, Any]:
    checks = {
        "records_with_output_equals_records": (
            evaluation.get("records_with_output") == evaluation.get("records")
        ),
        "schema_or_parse_errors": (
            isinstance(evaluation.get("schema_or_parse_error_records"), list)
            and len(evaluation["schema_or_parse_error_records"]) == 0
        ),
        "hallucinated_fields": evaluation.get("hallucinated_fields") == 0,
        "null_discipline": (
            evaluation.get("null_discipline") == 1.0
            and evaluation.get("null_expected_total") == evaluation.get("null_correct")
        ),
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": {
            "records": evaluation.get("records"),
            "records_with_output": evaluation.get("records_with_output"),
            "schema_or_parse_error_records": len(
                evaluation.get("schema_or_parse_error_records") or []
            ),
            "hallucinated_fields": evaluation.get("hallucinated_fields"),
            "null_discipline": evaluation.get("null_discipline"),
            "null_expected_total": evaluation.get("null_expected_total"),
            "null_correct": evaluation.get("null_correct"),
        },
    }


def check_g2(evaluation: dict[str, Any], minimum: float) -> dict[str, Any]:
    records = evaluation.get("records", 0)
    details = evaluation.get("records_detail") or []
    complete = sum(
        1 for row in details
        if isinstance(row, dict) and row.get("missing_fields") == 0
    )
    share = _share(complete, records)
    checks = {
        "records_detail_count_equals_records": len(details) == records,
        "record_completeness_minimum": share >= minimum,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": {
            "records_all_expected_present": complete,
            "records": records,
            "share": round(share, 4),
            "minimum": minimum,
        },
    }


def check_g3(evaluation: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    expected = evaluation.get("expected_fields_total", 0)
    exact = evaluation.get("exact_fields", 0)
    overall = _share(exact, expected)
    checks = gate.get("checks", {})
    minimum = float(checks.get("overall_exact_rate_minimum", 0.95))
    critical_minimum = float(checks.get("per_critical_field_exact_rate_minimum", 0.95))
    critical_fields = list(gate.get("critical_fields") or [])
    field_summary = evaluation.get("field_summary") or {}

    critical = {}
    for field in critical_fields:
        stats = field_summary.get(field)
        rate = stats.get("exact_rate") if isinstance(stats, dict) else None
        critical[field] = {
            "exact_rate": rate,
            "expected": stats.get("expected") if isinstance(stats, dict) else None,
            "exact": stats.get("exact") if isinstance(stats, dict) else None,
            "passed": isinstance(rate, (int, float)) and rate >= critical_minimum,
        }

    checks_out = {
        "overall_exact_rate_minimum": overall >= minimum,
        "all_critical_fields_present": all(
            field in field_summary for field in critical_fields
        ),
        "per_critical_field_exact_rate_minimum": all(
            item["passed"] for item in critical.values()
        ),
    }
    return {
        "passed": all(checks_out.values()),
        "checks": checks_out,
        "metrics": {
            "exact_fields": exact,
            "expected_fields": expected,
            "exact_rate": round(overall, 4),
            "minimum": minimum,
            "critical_minimum": critical_minimum,
            "critical_fields": critical,
            "min_critical_exact_rate": min(
                (item["exact_rate"] for item in critical.values()
                 if isinstance(item["exact_rate"], (int, float))),
                default=None,
            ),
        },
    }


def check_g4(evaluation: dict[str, Any], minimum: float) -> dict[str, Any]:
    records = evaluation.get("records", 0)
    exact_records = len(set(evaluation.get("records_all_expected_exact") or []))
    share = _share(exact_records, records)
    checks = {
        "records_all_expected_exact_minimum": share >= minimum,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "metrics": {
            "records_all_expected_exact": exact_records,
            "records": records,
            "share": round(share, 4),
            "minimum": minimum,
        },
    }


def check_g5(gate: dict[str, Any],
             manifest: dict[str, Any] | None) -> dict[str, Any]:
    if manifest is None:
        return {
            "passed": False,
            "checks": {"holdout_manifest_present": False},
            "metrics": {
                "reason": "no_holdout_manifest",
                "required_holdout_manifest_fields": gate.get(
                    "required_holdout_manifest_fields", {}
                ),
            },
        }

    required = gate.get("required_holdout_manifest_fields", {})
    required_checks = {
        key: manifest.get(key) == expected
        for key, expected in required.items()
    }
    required_strings = (
        "holdout_id", "source", "created_at", "input_path", "reference_path",
        "input_sha256", "reference_sha256", "prompt_sha256",
        "model_config_sha256", "gate_policy_sha256", "record_ids_sha256",
        "approval_id",
    )
    string_checks = {
        key: isinstance(manifest.get(key), str) and bool(manifest.get(key))
        for key in required_strings
    }
    hash_checks = {
        key: _hex_digest(manifest.get(key))
        for key in (
            "input_sha256", "reference_sha256", "prompt_sha256",
            "model_config_sha256", "gate_policy_sha256", "record_ids_sha256",
        )
    }
    status = manifest.get("status")
    status_checks = {
        "status_frozen_or_evaluated": status in ("frozen", "evaluated"),
        "record_count_positive": isinstance(manifest.get("record_count"), int)
        and manifest["record_count"] >= 1,
        "article_count_positive": isinstance(manifest.get("article_count"), int)
        and manifest["article_count"] >= 1,
        "article_ids_present": isinstance(manifest.get("article_ids"), list)
        and len(manifest["article_ids"]) >= 1,
        "source_verification_allowed": manifest.get("source_verification")
        in ("verified_exact", "verified_table", "corrected_with_source"),
        "no_unverifiable_records": (
            isinstance(manifest.get("record_status_distribution"), dict)
            and manifest["record_status_distribution"].get("unverifiable", 0) == 0
        ),
    }
    all_checks = {
        **{f"required_{key}": value for key, value in required_checks.items()},
        **string_checks,
        "hashes_are_sha256": all(hash_checks.values()),
        **status_checks,
    }
    return {
        "passed": all(all_checks.values()),
        "checks": all_checks,
        "metrics": {
            "holdout_id": manifest.get("holdout_id"),
            "status": status,
            "record_count": manifest.get("record_count"),
            "article_count": manifest.get("article_count"),
            "article_ids": manifest.get("article_ids"),
            "consumed_test_reuse_allowed": gate.get(
                "consumed_test_reuse_allowed", False
            ),
            "failed_checks": sorted(
                key for key, value in all_checks.items() if not value
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prüft eine C1-Evaluation gegen die Gates G1-G5."
    )
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--gates", type=Path, required=True)
    parser.add_argument("--holdout-manifest", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        evaluation = load_json(args.evaluation)
        policy = load_json(args.gates)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ABBRUCH: {exc}", file=sys.stderr)
        return 2

    gates = policy.get("gates")
    if not isinstance(gates, dict):
        print("ABBRUCH: Gates-JSON enthält kein gates-Objekt", file=sys.stderr)
        return 2

    manifest = None
    if args.holdout_manifest is not None:
        if not args.holdout_manifest.exists():
            print(
                f"ABBRUCH: Holdout-Manifest fehlt: {args.holdout_manifest}",
                file=sys.stderr,
            )
            return 2
        try:
            manifest = load_json(args.holdout_manifest)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"ABBRUCH: {exc}", file=sys.stderr)
            return 2

    try:
        g1 = check_g1(evaluation)
        g2 = check_g2(
            evaluation,
            float(gates["G2_record_completeness"]["minimum"]),
        )
        g3 = check_g3(evaluation, gates["G3_field_accuracy"])
        g4 = check_g4(
            evaluation,
            float(gates["G4_record_accuracy"]["minimum"]),
        )
        g5 = check_g5(gates["G5_independent_validation"], manifest)
    except (KeyError, TypeError, ValueError) as exc:
        print(f"ABBRUCH: unvollständige Gates- oder Evaluationsdaten: {exc}",
              file=sys.stderr)
        return 2

    report = {
        "policy_id": policy.get("policy_id"),
        "policy_status": policy.get("status"),
        "evaluation_path": str(args.evaluation),
        "gates_path": str(args.gates),
        "holdout_manifest_path": (
            str(args.holdout_manifest) if args.holdout_manifest else None
        ),
        "run_id": evaluation.get("run_id"),
        "all_gates_pass": all(
            item["passed"] for item in (g1, g2, g3, g4, g5)
        ),
        "gates": {
            "G1_integrity": g1,
            "G2_record_completeness": g2,
            "G3_field_accuracy": g3,
            "G4_record_accuracy": g4,
            "G5_independent_validation": g5,
        },
    }

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    labels = {
        "G1_integrity": "G1",
        "G2_record_completeness": "G2",
        "G3_field_accuracy": "G3",
        "G4_record_accuracy": "G4",
        "G5_independent_validation": "G5",
    }
    print(f"Run: {report['run_id']}")
    for key, gate in report["gates"].items():
        state = "PASS" if gate["passed"] else "FAIL"
        print(f"{labels[key]} {state}")
    g2m = g2["metrics"]
    g3m = g3["metrics"]
    g4m = g4["metrics"]
    print(
        f"G2 {g2m['records_all_expected_present']}/{g2m['records']} "
        f"= {g2m['share']:.2%} (min {g2m['minimum']:.0%})"
    )
    print(
        f"G3 {g3m['exact_fields']}/{g3m['expected_fields']} "
        f"= {g3m['exact_rate']:.1%}; kritische Felder min "
        f"{g3m['min_critical_exact_rate']} (min {g3m['critical_minimum']:.0%})"
    )
    print(
        f"G4 {g4m['records_all_expected_exact']}/{g4m['records']} "
        f"= {g4m['share']:.1%} (min {g4m['minimum']:.0%})"
    )
    if report["holdout_manifest_path"] is None:
        print("G5 kein Holdout-Manifest")
    else:
        print(f"G5 Manifest: {report['holdout_manifest_path']}")
    print(f"OVERALL {'PASS' if report['all_gates_pass'] else 'FAIL'}")
    if args.output is not None:
        print(f"Report: {args.output}")
    return 0 if report["all_gates_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
