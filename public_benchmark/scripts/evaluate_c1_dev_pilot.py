"""C1-Dev-Pilot gegen die eingefrorene Referenz auswerten.

Der Evaluator liest die Modellausgabe und erst hier die Referenz. Er zählt
exakte Treffer, mittlere absolute Abweichung, Abdeckung sowie fehlende,
falsche und halluzinierte Felder. Referenzwerte werden nie an das Modell
zurückgegeben.

Aufruf:
    PYTHONIOENCODING=utf-8 .venv/bin/python.exe \
        public_benchmark/scripts/evaluate_c1_dev_pilot.py \
        --run-id c1_dev_20261111
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
PILOT_ROOT = BENCH_ROOT / "evaluation" / "c1_pilot"
REFERENCE_PATH = PILOT_ROOT / "dev_reference.jsonl"
INPUT_PATH = PILOT_ROOT / "dev_input.jsonl"
OUTPUT_ROOT = PILOT_ROOT / "runs"

# Modellfeld -> Referenzfeld
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
    "continuous": {
        "intervention_n", "comparator_n", "intervention_mean",
        "intervention_sd", "comparator_mean", "comparator_sd",
    },
    "binary": {
        "intervention_n", "comparator_n",
        "intervention_events", "comparator_events",
    },
}
ALL_FIELDS = list(FIELD_MAP)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def as_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def evaluate(run_id: str, *, input_path: Path = INPUT_PATH,
             reference_path: Path = REFERENCE_PATH,
             output_path: Path | None = None,
             test_mode: bool = False) -> dict[str, Any]:
    if output_path is None:
        output_path = OUTPUT_ROOT / run_id / "dev_output.jsonl"
    if not output_path.exists():
        raise FileNotFoundError(output_path)

    inputs = load_jsonl(input_path)
    references = {int(row["record_id"]): row for row in load_jsonl(reference_path)}
    outputs = {int(row["record_id"]): row for row in load_jsonl(output_path)}

    input_by_id = {int(row["record_id"]): row for row in inputs}
    if set(input_by_id) != set(references):
        raise ValueError("Dev-Eingabe und Referenz enthalten nicht dieselben IDs")

    field_stats = {
        field: {
            "expected": 0, "present": 0, "exact": 0, "missing": 0,
            "wrong": 0, "abs_diff_sum": 0.0, "paired": 0,
        }
        for field in ALL_FIELDS
    }
    field_stats["_hallucinated"] = {"count": 0}
    rows_report: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    expected_total = 0
    expected_present = 0
    null_expected_total = 0
    null_correct = 0
    hallucinated = 0
    parse_error_ids: list[int] = []

    for record_id in sorted(references):
        reference = references[record_id]
        input_record = input_by_id[record_id]
        output = outputs.get(record_id, {})
        outcome_type = input_record["outcome_type"]
        expected_fields = EXPECTED_BY_TYPE[outcome_type]
        ref_values = reference["reference_values"]

        row = {
            "record_id": record_id,
            "outcome_type": outcome_type,
            "audit_status": reference["audit_status"],
            "expected_fields": len(expected_fields),
            "exact_fields": 0,
            "missing_fields": 0,
            "wrong_fields": 0,
            "hallucinated_fields": 0,
            "schema_error": "",
        }

        if output.get("outcome_type") != outcome_type:
            row["schema_error"] = (
                f"outcome_type {output.get('outcome_type')!r} statt {outcome_type!r}"
            )
            parse_error_ids.append(record_id)
        if output.get("source_note") == "MODEL_OUTPUT_UNPARSEABLE":
            parse_error_ids.append(record_id)

        for field in ALL_FIELDS:
            ref_field = FIELD_MAP[field]
            ref_raw = ref_values.get(ref_field)
            ref_value = as_number(ref_raw)
            pred_raw = output.get(field)
            pred_value = as_number(pred_raw)
            expected = field in expected_fields

            if expected:
                expected_total += 1
                stats = field_stats[field]
                stats["expected"] += 1
                if pred_value is None:
                    stats["missing"] += 1
                    row["missing_fields"] += 1
                    errors.append({
                        "record_id": record_id, "field": field,
                        "category": "fehlend", "reference": ref_value,
                        "prediction": pred_raw, "abs_diff": None,
                    })
                else:
                    expected_present += 1
                    stats["present"] += 1
                    diff = abs(pred_value - ref_value) if ref_value is not None else None
                    if ref_value is not None and diff is not None and diff < 1e-9:
                        stats["exact"] += 1
                        row["exact_fields"] += 1
                    else:
                        stats["wrong"] += 1
                        row["wrong_fields"] += 1
                        errors.append({
                            "record_id": record_id, "field": field,
                            "category": "falsch", "reference": ref_value,
                            "prediction": pred_raw, "abs_diff": diff,
                        })
                    if diff is not None:
                        stats["paired"] += 1
                        stats["abs_diff_sum"] += diff
            else:
                null_expected_total += 1
                if pred_value is None:
                    null_correct += 1
                else:
                    hallucinated += 1
                    row["hallucinated_fields"] += 1
                    errors.append({
                        "record_id": record_id, "field": field,
                        "category": "halluziniert", "reference": None,
                        "prediction": pred_raw, "abs_diff": None,
                    })

        rows_report.append(row)

    field_summary = {}
    for field, stats in field_stats.items():
        if field == "_hallucinated":
            field_summary[field] = stats
            continue
        field_summary[field] = {
            **stats,
            "exact_rate": round(stats["exact"] / stats["expected"], 4)
            if stats["expected"] else None,
            "coverage": round(stats["present"] / stats["expected"], 4)
            if stats["expected"] else None,
            "mae": round(stats["abs_diff_sum"] / stats["paired"], 4)
            if stats["paired"] else None,
        }

    paired_diffs = [
        error["abs_diff"] for error in errors
        if error["category"] == "falsch" and error["abs_diff"] is not None
    ]
    # Exakte Treffer tragen eine Differenz von 0 zur MAE bei.
    all_abs_diffs = paired_diffs + [0.0] * sum(
        stats["exact"] for field, stats in field_stats.items()
        if field != "_hallucinated"
    )

    summary = {
        "run_id": run_id,
        "records": len(references),
        "records_with_output": len(outputs),
        "audit_status": {
            status: sum(
                1 for row in references.values()
                if row["audit_status"] == status
            )
            for status in sorted({row["audit_status"] for row in references.values()})
        },
        "expected_fields_total": expected_total,
        "expected_fields_present": expected_present,
        "coverage": round(expected_present / expected_total, 4),
        "exact_fields": sum(
            stats["exact"] for field, stats in field_stats.items()
            if field != "_hallucinated"
        ),
        "exact_rate": round(
            sum(stats["exact"] for field, stats in field_stats.items()
                if field != "_hallucinated") / expected_total, 4
        ),
        "missing_fields": sum(
            stats["missing"] for field, stats in field_stats.items()
            if field != "_hallucinated"
        ),
        "wrong_fields": sum(
            stats["wrong"] for field, stats in field_stats.items()
            if field != "_hallucinated"
        ),
        "hallucinated_fields": hallucinated,
        "null_expected_total": null_expected_total,
        "null_correct": null_correct,
        "null_discipline": round(null_correct / null_expected_total, 4),
        "mae_paired_all": round(
            sum(all_abs_diffs) / len(all_abs_diffs), 4
        ) if all_abs_diffs else None,
        "schema_or_parse_error_records": sorted(set(parse_error_ids)),
        "records_all_expected_exact": sorted(
            row["record_id"] for row in rows_report
            if row["exact_fields"] == row["expected_fields"]
            and not row["schema_error"]
        ),
        "field_summary": field_summary,
        "records_detail": rows_report,
        "errors": errors,
    }
    if test_mode:
        summary["test_mode"] = True
    return summary


def render_markdown(summary: dict[str, Any],
                    title: str = "C1-Dev-Pilot: Ergebnis",
                    note: str = "Der Testsplit wurde nicht gelesen und nicht verwendet.") -> str:
    lines = [
        f"# {title}",
        "",
        f"Run: `{summary['run_id']}`",
        "",
        "## Kopfzahlen",
        "",
        f"- Records mit Ausgabe: **{summary['records_with_output']}/{summary['records']}**",
        f"- Erwartete Felder: **{summary['expected_fields_total']}**",
        f"- Abdeckung: **{summary['expected_fields_present']}/{summary['expected_fields_total']}** "
        f"({summary['coverage']:.1%})",
        f"- Exakte Treffer: **{summary['exact_fields']}/{summary['expected_fields_total']}** "
        f"({summary['exact_rate']:.1%})",
        f"- Fehlend: **{summary['missing_fields']}**; falsch: **{summary['wrong_fields']}**; "
        f"halluziniert: **{summary['hallucinated_fields']}**",
        f"- MAE über alle gepaarten erwarteten Felder: **{summary['mae_paired_all']}**",
        f"- Null-Disziplin auf nicht erwarteten Feldern: "
        f"**{summary['null_correct']}/{summary['null_expected_total']}** "
        f"({summary['null_discipline']:.1%})",
        f"- Records mit vollständig exakten Erwartungsfeldern: "
        f"**{len(summary['records_all_expected_exact'])}/{summary['records']}**",
        f"- Schema-/Parse-Fehler: **{len(summary['schema_or_parse_error_records'])}** "
        f"({', '.join(map(str, summary['schema_or_parse_error_records'])) or 'keine'})",
        "",
        "## Feldebene",
        "",
        "| Feld | erwartet | vorhanden | exakt | fehlend | falsch | MAE |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for field, stats in summary["field_summary"].items():
        if field == "_hallucinated":
            continue
        lines.append(
            f"| `{field}` | {stats['expected']} | {stats['present']} | "
            f"{stats['exact']} | {stats['missing']} | {stats['wrong']} | "
            f"{stats['mae'] if stats['mae'] is not None else '-'} |"
        )

    lines += [
        "",
        "## Fehlerliste",
        "",
        "| Record | Feld | Kategorie | Referenz | Modell | absolute Differenz |",
        "|---:|---|---|---:|---:|---:|",
    ]
    if summary["errors"]:
        for error in summary["errors"]:
            diff = "-" if error["abs_diff"] is None else f"{error['abs_diff']:.6g}"
            lines.append(
                f"| {error['record_id']} | `{error['field']}` | {error['category']} | "
                f"{error['reference'] if error['reference'] is not None else 'null'} | "
                f"{error['prediction'] if error['prediction'] is not None else 'null'} | "
                f"{diff} |"
            )
    else:
        lines.append("| - | - | keine | - | - | - |")

    lines += [
        "",
        "## Einordnung",
        "",
        "- `exakt` bedeutet numerische Gleichheit des ausgegebenen Werts mit der Referenz.",
        "- `fehlend` bedeutet: Referenzwert vorhanden, Modellwert `null`.",
        "- `falsch` bedeutet: beide Werte vorhanden, aber nicht numerisch gleich.",
        "- `halluziniert` bedeutet: Feld ist für diesen Outcome-Typ nicht erwartet, "
        "das Modell liefert trotzdem einen Wert.",
        "- Die MAE wird nur über gepaarte Werte gebildet; fehlende Werte werden nicht "
        "durch 0 oder Schätzungen ersetzt.",
        f"- {note}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="c1_dev_20261111")
    args = parser.parse_args()

    summary = evaluate(args.run_id)
    run_dir = OUTPUT_ROOT / args.run_id
    summary_path = run_dir / "dev_evaluation.json"
    report_path = run_dir / "dev_evaluation.md"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path.write_text(render_markdown(summary), encoding="utf-8")

    print(f"Records: {summary['records_with_output']}/{summary['records']}")
    print(
        f"Exakt: {summary['exact_fields']}/{summary['expected_fields_total']} "
        f"({summary['exact_rate']:.1%}), Abdeckung {summary['coverage']:.1%}, "
        f"MAE {summary['mae_paired_all']}"
    )
    print(
        f"Fehlend {summary['missing_fields']}, falsch {summary['wrong_fields']}, "
        f"halluziniert {summary['hallucinated_fields']}"
    )
    print(f"JSON: {summary_path}")
    print(f"Bericht: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
