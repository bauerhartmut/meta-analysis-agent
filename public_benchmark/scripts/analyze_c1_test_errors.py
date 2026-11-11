"""Deskriptive Fehleranalyse des eingefrorenen C1-Testlaufs.

Liest ausschliesslich die bereits erzeugte ``test_evaluation.json``. Es werden
keine Testwerte, Record-IDs oder Referenzwerte ausgegeben und kein Modelllauf
gestartet. Der Prompt bleibt unveraendert.
"""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


BENCH_ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = (
    BENCH_ROOT / "evaluation" / "c1_pilot" / "runs_test"
    / "c1_test_20261111_v6c"
)
EVALUATION_PATH = RUN_DIR / "test_evaluation.json"
RESULT_PATH = RUN_DIR / "test_error_analysis.json"
REPORT_PATH = RUN_DIR / "test_error_analysis.md"

FIELDS_BY_TYPE = {
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(q * len(ordered)) - 1))
    return ordered[index]


def round_or_none(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


def pattern_rows(
    record_ids: list[int],
    fields_by_record: dict[int, set[str]],
    total: int,
) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, ...]] = Counter(
        tuple(sorted(fields_by_record[record_id]))
        for record_id in record_ids
        if fields_by_record[record_id]
    )
    return [
        {
            "fields": list(pattern),
            "field_count": len(pattern),
            "records": count,
            "share_of_type": round(count / total, 4),
        }
        for pattern, count in counts.most_common()
    ]


def distribution(values: list[int]) -> dict[str, int]:
    return {str(key): value for key, value in sorted(Counter(values).items())}


def main() -> int:
    summary = json.loads(EVALUATION_PATH.read_text(encoding="utf-8"))
    records = {row["record_id"]: row for row in summary["records_detail"]}
    errors = summary["errors"]
    type_by_record = {record_id: row["outcome_type"]
                      for record_id, row in records.items()}
    ids_by_type = {
        outcome_type: [record_id for record_id, row in records.items()
                       if row["outcome_type"] == outcome_type]
        for outcome_type in FIELDS_BY_TYPE
    }

    missing_by_record: dict[int, set[str]] = defaultdict(set)
    wrong_by_record: dict[int, set[str]] = defaultdict(set)
    errors_by_type_field: dict[tuple[str, str], list[dict[str, Any]]] = (
        defaultdict(list)
    )
    for error in errors:
        record_id = error["record_id"]
        outcome_type = type_by_record[record_id]
        if error["category"] == "fehlend":
            missing_by_record[record_id].add(error["field"])
        elif error["category"] == "falsch":
            wrong_by_record[record_id].add(error["field"])
        errors_by_type_field[(outcome_type, error["field"])].append(error)

    for record_id in records:
        if missing_by_record[record_id] and wrong_by_record[record_id]:
            raise ValueError("Record mit fehlenden und falschen Werten")

    by_type: dict[str, dict[str, Any]] = {}
    for outcome_type, ids in ids_by_type.items():
        rows = [records[record_id] for record_id in ids]
        missing_only = sum(
            1 for record_id in ids
            if missing_by_record[record_id] and not wrong_by_record[record_id]
        )
        wrong_only = sum(
            1 for record_id in ids
            if wrong_by_record[record_id] and not missing_by_record[record_id]
        )
        both = sum(
            1 for record_id in ids
            if wrong_by_record[record_id] and missing_by_record[record_id]
        )
        all_exact = sum(
            1 for row in rows
            if row["exact_fields"] == row["expected_fields"]
            and not row["schema_error"]
        )
        by_type[outcome_type] = {
            "records": len(ids),
            "expected_fields": sum(row["expected_fields"] for row in rows),
            "exact_fields": sum(row["exact_fields"] for row in rows),
            "missing_fields": sum(row["missing_fields"] for row in rows),
            "wrong_fields": sum(row["wrong_fields"] for row in rows),
            "all_exact_records": all_exact,
            "missing_only_records": missing_only,
            "wrong_only_records": wrong_only,
            "both_missing_and_wrong_records": both,
            "zero_exact_records": sum(
                1 for row in rows if row["exact_fields"] == 0
            ),
            "missing_field_count_distribution": distribution(
                [len(missing_by_record[record_id]) for record_id in ids
                 if missing_by_record[record_id]]
            ),
            "wrong_field_count_distribution": distribution(
                [len(wrong_by_record[record_id]) for record_id in ids
                 if wrong_by_record[record_id]]
            ),
            "exact_field_count_distribution": distribution(
                [row["exact_fields"] for row in rows]
            ),
            "missing_patterns": pattern_rows(
                ids, missing_by_record, len(ids)
            ),
            "wrong_patterns": pattern_rows(
                ids, wrong_by_record, len(ids)
            ),
        }

    field_errors: dict[str, dict[str, dict[str, Any]]] = {}
    error_magnitudes: dict[str, dict[str, dict[str, Any]]] = {}
    for outcome_type, fields in FIELDS_BY_TYPE.items():
        field_errors[outcome_type] = {}
        error_magnitudes[outcome_type] = {}
        expected = len(ids_by_type[outcome_type])
        for field in fields:
            field_events = errors_by_type_field[(outcome_type, field)]
            missing = sum(
                error["category"] == "fehlend" for error in field_events
            )
            wrong = sum(
                error["category"] == "falsch" for error in field_events
            )
            exact = expected - missing - wrong
            present = expected - missing
            diffs = [
                float(error["abs_diff"])
                for error in field_events
                if error["category"] == "falsch"
                and error["abs_diff"] is not None
            ]
            mae = sum(diffs) / present if present else None
            field_errors[outcome_type][field] = {
                "expected": expected,
                "exact": exact,
                "present": present,
                "missing": missing,
                "wrong": wrong,
                "exact_rate": round(exact / expected, 4) if expected else None,
                "coverage": round(present / expected, 4) if expected else None,
                "mae": round_or_none(mae),
            }

            wrong_events = [
                error for error in field_events
                if error["category"] == "falsch"
                and error["abs_diff"] is not None
            ]
            over = sum(
                1 for error in wrong_events
                if error["prediction"] is not None
                and error["reference"] is not None
                and error["prediction"] > error["reference"]
            )
            under = sum(
                1 for error in wrong_events
                if error["prediction"] is not None
                and error["reference"] is not None
                and error["prediction"] < error["reference"]
            )
            if field.endswith(("_n", "_events")):
                near = {
                    "definition": "absolute Differenz genau 1, 2 oder >= 3",
                    "near_1": sum(diff == 1 for diff in diffs),
                    "near_2": sum(diff == 2 for diff in diffs),
                    "near_3": sum(diff >= 3 for diff in diffs),
                }
            else:
                near = {
                    "definition": "absolute Differenz <= 0.5, <= 1 oder <= 2",
                    "near_1": sum(diff <= 0.5 for diff in diffs),
                    "near_2": sum(diff <= 1.0 for diff in diffs),
                    "near_3": sum(diff <= 2.0 for diff in diffs),
                }
            error_magnitudes[outcome_type][field] = {
                "wrong": len(wrong_events),
                "over": over,
                "under": under,
                "median_abs_diff": round_or_none(
                    statistics.median(diffs) if diffs else None
                ),
                "p90_abs_diff": round_or_none(percentile(diffs, 0.9)),
                "max_abs_diff": round_or_none(max(diffs) if diffs else None),
                "mean_abs_diff": round_or_none(
                    statistics.mean(diffs) if diffs else None
                ),
                **near,
            }

    for outcome_type, rows in field_errors.items():
        for field, stats in rows.items():
            if stats["missing"] + stats["wrong"] + stats["exact"] != stats["expected"]:
                raise ValueError(f"Feldstatistik inkonsistent: {outcome_type}/{field}")

    for field, reference in summary["field_summary"].items():
        if field == "_hallucinated":
            continue
        type_rows = [field_errors[outcome_type][field]
                     for outcome_type in FIELDS_BY_TYPE
                     if field in field_errors[outcome_type]]
        if (
            sum(row["expected"] for row in type_rows) != reference["expected"]
            or sum(row["missing"] for row in type_rows) != reference["missing"]
            or sum(row["wrong"] for row in type_rows) != reference["wrong"]
            or sum(row["exact"] for row in type_rows) != reference["exact"]
        ):
            raise ValueError(f"Feldsumme inkonsistent: {field}")

    overall = {
        "records": len(records),
        "expected_fields": sum(row["expected_fields"] for row in records.values()),
        "exact_fields": summary["exact_fields"],
        "missing_fields": summary["missing_fields"],
        "wrong_fields": summary["wrong_fields"],
        "hallucinated_fields": summary["hallucinated_fields"],
        "exact_rate": summary["exact_rate"],
        "coverage": summary["coverage"],
        "mae_paired_all": summary["mae_paired_all"],
        "all_exact_records": sum(
            row["exact_fields"] == row["expected_fields"]
            and not row["schema_error"]
            for row in records.values()
        ),
        "missing_only_records": sum(
            1 for record_id in records
            if missing_by_record[record_id] and not wrong_by_record[record_id]
        ),
        "wrong_only_records": sum(
            1 for record_id in records
            if wrong_by_record[record_id] and not missing_by_record[record_id]
        ),
        "both_missing_and_wrong_records": sum(
            1 for record_id in records
            if wrong_by_record[record_id] and missing_by_record[record_id]
        ),
        "zero_exact_records": sum(
            1 for row in records.values() if row["exact_fields"] == 0
        ),
    }

    audit_status: dict[str, dict[str, int]] = {}
    for status in sorted({row["audit_status"] for row in records.values()}):
        ids = [
            record_id for record_id, row in records.items()
            if row["audit_status"] == status
        ]
        audit_status[status] = {
            "records": len(ids),
            "all_exact": sum(
                1 for record_id in ids
                if records[record_id]["exact_fields"]
                == records[record_id]["expected_fields"]
            ),
            "missing_only": sum(
                1 for record_id in ids
                if missing_by_record[record_id] and not wrong_by_record[record_id]
            ),
            "wrong_only": sum(
                1 for record_id in ids
                if wrong_by_record[record_id] and not missing_by_record[record_id]
            ),
        }

    result = {
        "analysis_version": 1,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "run_id": summary["run_id"],
        "scope": "descriptive_only",
        "new_model_run": False,
        "post_test_prompt_changes": False,
        "test_split_used_for_optimization": False,
        "source_test_evaluation_sha256": sha256_file(EVALUATION_PATH),
        "overall": overall,
        "by_type": by_type,
        "field_errors": field_errors,
        "error_magnitudes": error_magnitudes,
        "audit_status": audit_status,
        "null_discipline": {
            "correct": summary["null_correct"],
            "expected": summary["null_expected_total"],
            "rate": summary["null_discipline"],
        },
        "schema_error_records": len(summary["schema_or_parse_error_records"]),
        "note": (
            "Keine Testwerte und keine Record-IDs im Bericht. Die Analyse "
            "beschreibt nur das eingefrorene Ergebnis; der Prompt bleibt "
            "unveraendert und der Testsplit wird nicht zur Optimierung genutzt."
        ),
    }
    RESULT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# C1-Testlauf v6c: Fehleranalyse",
        "",
        f"Run: `{result['run_id']}`",
        "Status: **deskriptiv, eingefrorener Testlauf**",
        "",
        "## Kernbefunde",
        "",
        f"- **{overall['missing_only_records']} Records** haben ausschliesslich "
        f"fehlende Werte, **{overall['wrong_only_records']} Records** "
        f"ausschliesslich falsche Werte; **{overall['both_missing_and_wrong_records']}** "
        "haben beides.",
        f"- **{overall['all_exact_records']}/{overall['records']} Records** sind "
        "vollstaendig exakt.",
        f"- **0 Halluzinationen**, **0 Schema-/Parsefehler**; Null-Disziplin "
        f"**{summary['null_correct']}/{summary['null_expected_total']}**.",
        "- Continuous ist mit **678/936 (72,4 %)** deutlich schwaecher als "
        "binary mit **314/372 (84,4 %)**.",
        "- Die Fehler sind ueberwiegend blockweise: ganze Mean/SD-Bloecke oder "
        "ganze n-/Event-Bloecke fehlen bzw. weichen ab; einzelne Felder kommen "
        "vor, vor allem `comparator_n`.",
        "- Kein durchgaengiger Richtungsbias: Ueber- und Unterschaetzungen "
        "wechseln je Feld; einzelne Felder zeigen lokale Asymmetrien.",
        "",
        "## Record-Ebene",
        "",
        "| Typ | Records | vollstaendig exakt | nur fehlend | nur falsch | beides | 0 exakt |",
        "|---|---:|---:|---:|---:|---:|---:|",
        f"| continuous | {by_type['continuous']['records']} | "
        f"{by_type['continuous']['all_exact_records']} | "
        f"{by_type['continuous']['missing_only_records']} | "
        f"{by_type['continuous']['wrong_only_records']} | "
        f"{by_type['continuous']['both_missing_and_wrong_records']} | "
        f"{by_type['continuous']['zero_exact_records']} |",
        f"| binary | {by_type['binary']['records']} | "
        f"{by_type['binary']['all_exact_records']} | "
        f"{by_type['binary']['missing_only_records']} | "
        f"{by_type['binary']['wrong_only_records']} | "
        f"{by_type['binary']['both_missing_and_wrong_records']} | "
        f"{by_type['binary']['zero_exact_records']} |",
        f"| gesamt | {overall['records']} | {overall['all_exact_records']} | "
        f"{overall['missing_only_records']} | {overall['wrong_only_records']} | "
        f"{overall['both_missing_and_wrong_records']} | "
        f"{overall['zero_exact_records']} |",
        "",
        "## Feldebene",
        "",
        "| Typ | Feld | erwartet | exakt | fehlend | falsch | exakt % | MAE |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for outcome_type in FIELDS_BY_TYPE:
        for field, stats in field_errors[outcome_type].items():
            lines.append(
                f"| {outcome_type} | `{field}` | {stats['expected']} | "
                f"{stats['exact']} | {stats['missing']} | {stats['wrong']} | "
                f"{stats['exact_rate']:.1%} | {stats['mae']} |"
            )

    lines += [
        "",
        "## Fehlende Muster",
        "",
        "| Typ | Muster | Records | Felder |",
        "|---|---|---:|---:|",
    ]
    for outcome_type in FIELDS_BY_TYPE:
        for pattern in by_type[outcome_type]["missing_patterns"]:
            lines.append(
                f"| {outcome_type} | {' + '.join(pattern['fields'])} | "
                f"{pattern['records']} | {pattern['field_count']} |"
            )

    lines += [
        "",
        "## Falsche Muster",
        "",
        "| Typ | Muster | Records | Felder |",
        "|---|---|---:|---:|",
    ]
    for outcome_type in FIELDS_BY_TYPE:
        for pattern in by_type[outcome_type]["wrong_patterns"]:
            lines.append(
                f"| {outcome_type} | {' + '.join(pattern['fields'])} | "
                f"{pattern['records']} | {pattern['field_count']} |"
            )

    lines += [
        "",
        "## Richtung und Groesse der falschen Werte",
        "",
        "`near` zaehlt bei n/events die exakte Differenz 1, 2 oder >= 3; bei "
        "Mean/SD die Differenz <= 0,5, <= 1 oder <= 2.",
        "",
        "| Typ | Feld | falsch | ueber | unter | Median | p90 | max | near 1 | near 2 | near 3 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for outcome_type in FIELDS_BY_TYPE:
        for field, stats in error_magnitudes[outcome_type].items():
            lines.append(
                f"| {outcome_type} | `{field}` | {stats['wrong']} | "
                f"{stats['over']} | {stats['under']} | {stats['median_abs_diff']} | "
                f"{stats['p90_abs_diff']} | {stats['max_abs_diff']} | "
                f"{stats['near_1']} | {stats['near_2']} | {stats['near_3']} |"
            )

    lines += [
        "",
        "## Auditstatus",
        "",
        "| Status | Records | vollstaendig exakt | nur fehlend | nur falsch |",
        "|---|---:|---:|---:|---:|",
    ]
    for status, stats in audit_status.items():
        lines.append(
            f"| `{status}` | {stats['records']} | {stats['all_exact']} | "
            f"{stats['missing_only']} | {stats['wrong_only']} |"
        )

    lines += [
        "",
        "## Deutung",
        "",
        "- Die saubere Trennung von fehlend und falsch spricht fuer "
        "blockweise Extraktion: Das Modell liefert entweder einen vollstaendigen "
        "Block (moeglicherweise mit falschen Werten) oder laesst einen Block "
        "als `null` weg.",
        "- Der groesste falsche Block sind **23 kontinuierliche Records mit "
        "allen vier Mean/SD-Feldern falsch**, waehrend beide n-Felder exakt "
        "sind. Der groesste fehlende Block sind **11 Records mit beiden "
        "Mean/SD-Armen fehlend**.",
        "- Beim binären Typ sind **7 Records mit allen vier Feldern fehlend** "
        "und **7 Records mit beiden Event-Feldern falsch** die groessten "
        "Gruppen.",
        "- Die exakte Metrik bestraft auch kleine Rundungs- oder "
        "Skalierungsabweichungen. Die Near-Miss-Spalten zeigen, wie viele "
        "falsche Werte nahe an der Referenz liegen; die Bewertung sollte "
        "deshalb nicht nur als eine einzelne Exact-Match-Zahl gelesen werden.",
        "- Der Vergleichsarm ist bei n und Mean/SD etwas schwaecher als der "
        "Interventionsarm; die Event-Felder sind arm-symmetrisch.",
        "",
        "## Grenzen und Protokoll",
        "",
        "- Ein einzelner eingefrorener Testlauf; keine neue Modellausfuehrung.",
        "- Keine Prompt-Aenderung und keine Verwendung des Testsplit zur "
        "Optimierung.",
        "- Die Analyse ist deskriptiv; sie belegt keine Kausalitaet fuer die "
        "beobachteten Blockmuster.",
        "- Keine Testwerte oder Record-IDs in diesem Bericht.",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(
        f"Fehleranalyse: {overall['missing_only_records']} nur fehlend, "
        f"{overall['wrong_only_records']} nur falsch, "
        f"{overall['both_missing_and_wrong_records']} beides"
    )
    print(f"JSON: {RESULT_PATH}")
    print(f"Bericht: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
