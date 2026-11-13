#!/usr/bin/env python3
"""Bewertet die Extraktionslaeufe auf dem externen Validierungssatz.

Die GLASS-Golddaten fuehren je Record Felder wie ``HR``, ``Events``,
``Total``, ``n`` ohne feste Reihenfolge. Deshalb wird je Record ein
Multiset-Vergleich gemacht: jede Goldzelle (Feld, Wert) sucht eine
Vorhersagezelle mit demselben Feld und demselben Wert. Reihenfolge und
Zeilenanzahl spielen keine Rolle, doppelte Felder werden als Zellen gezaehlt.

Ausgabe: ``tier1_scores.json`` und eine Tabelle auf der Konsole.
"""

from __future__ import annotations

import argparse
import difflib
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

CROSSVAL = Path(__file__).resolve().parents[2] / "evaluation" / "multi_model_cross_validation"
SET = CROSSVAL / "tier1_validation_set_v1.jsonl"
RUN = CROSSVAL / "runs" / "tier1_20261113" / "predictions.jsonl"
OUT = CROSSVAL / "tier1_scores.json"


def close(a: Any, b: Any) -> bool:
    try:
        x, y = float(a), float(b)
    except (TypeError, ValueError):
        return False
    return abs(x - y) <= max(1e-6, 1e-6 * abs(y))


def gold_cells(record: dict[str, Any]) -> list[tuple[str, float]]:
    return [
        (cell["label"], float(cell["value"]))
        for cell in record["cells"]
        if isinstance(cell["value"], (int, float)) and cell["arm"] is None
    ]


def predicted_cells(rows: list[dict[str, Any]]) -> list[tuple[str, float]]:
    cells = []
    for row in rows:
        for key, value in row.items():
            if isinstance(value, bool) or value is None:
                continue
            try:
                cells.append((key, float(str(value).replace(",", "."))))
            except (TypeError, ValueError):
                continue
    return cells


def score(records: list[dict[str, Any]], predictions: dict[tuple[str, str], dict[str, Any]], model: str):
    per_record = {}
    for record in records:
        entry = predictions.get((record["record_id"], model))
        gold = gold_cells(record)
        if not gold:
            continue
        if entry is None:
            per_record[record["record_id"]] = {
                "study": record["study_id"],
                "gold": len(gold),
                "predicted": 0,
                "matched": 0,
                "answered": False,
            }
            continue
        predicted = predicted_cells(entry.get("rows") or [])
        remaining = Counter(gold)
        matched = 0
        for field, value in predicted:
            for candidate, count in list(remaining.items()):
                if count and candidate[0] == field and close(value, candidate[1]):
                    remaining[candidate] -= 1
                    matched += 1
                    break
        per_record[record["record_id"]] = {
            "study": record["study_id"],
            "gold": len(gold),
            "predicted": len(predicted),
            "matched": matched,
            "answered": bool(entry.get("rows")),
        }
    return per_record


IDENT_KEYS = ("study", "name")


def _norm(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", str(text).lower()).split())


def _identifier(row: dict[str, Any]) -> str:
    for key, value in row.items():
        if key.lower() in IDENT_KEYS and isinstance(value, str) and value.strip():
            return _norm(value)
    return ""


def _similar(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    left_tokens, right_tokens = set(left.split()), set(right.split())
    if left_tokens and right_tokens:
        overlap = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
        if overlap >= 0.6:
            return overlap
    return difflib.SequenceMatcher(None, left, right).ratio()


def _numeric(row: dict[str, Any]) -> dict[str, float]:
    values = {}
    for key, value in row.items():
        if isinstance(value, bool) or value is None:
            continue
        try:
            values[key] = float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            continue
    return values


EFFECT_KEYS = ("HR", "OR", "RR", "CR", "DCR", "ORR", "ODDS_RATIO", "ODDS RATIO", "RISK_RATIO")


def _best_match(gold_rows: list[dict[str, Any]], pred_rows: list[dict[str, Any]]) -> dict[int, int]:
    """Ordnet Goldzeilen den Vorhersagezeilen zu.

    Anker ist die Uebereinstimmung numerischer Zellen, weil die Modelle die
    Zeilen anders benennen als der Goldstandard. Effektgroessen zaehlen doppelt,
    ein aehnlicher Studienname gibt einen kleinen Zusatzpunkt. Ohne mindestens
    eine uebereinstimmende Zahl gibt es keine Zuordnung.
    """
    pairs: dict[int, int] = {}
    used: set[int] = set()
    for index, gold in enumerate(gold_rows):
        gold_values = _numeric(gold)
        target = _identifier(gold)
        scored = []
        for position, pred in enumerate(pred_rows):
            if position in used:
                continue
            pred_values = _numeric(pred)
            shared = [key for key in gold_values if key in pred_values and close(pred_values[key], gold_values[key])]
            if not shared:
                continue
            score = len(shared) + sum(1 for key in shared if key.upper() in EFFECT_KEYS)
            score += 0.5 * _similar(target, _identifier(pred)) if target else 0.0
            scored.append((score, position))
        scored.sort(reverse=True)
        if scored:
            pairs[index] = scored[0][1]
            used.add(scored[0][1])
    return pairs


def score_aligned(records, predictions, model: str) -> dict[str, Any]:
    hits = wrong = missing = extra = 0
    records_total = records_matched = records_exact = 0
    for record in records:
        entry = predictions.get((record["record_id"], model))
        gold_rows = [row.get("fields", row) for row in record.get("rows") or []]
        if not gold_rows:
            continue
        records_total += 1
        pred_rows = entry.get("rows") or [] if entry else []
        pairs = _best_match(gold_rows, pred_rows) if pred_rows else {}
        if pairs:
            records_matched += 1
        record_ok = bool(pairs) and len(pairs) == len(gold_rows)
        for index, gold in enumerate(gold_rows):
            gold_values = _numeric(gold)
            position = pairs.get(index)
            if position is None:
                missing += len(gold_values)
                record_ok = False
                continue
            pred_values = _numeric(pred_rows[position])
            for key, value in gold_values.items():
                if key in pred_values:
                    if close(pred_values[key], value):
                        hits += 1
                    else:
                        wrong += 1
                        record_ok = False
                else:
                    missing += 1
                    record_ok = False
            extra += sum(1 for key in pred_values if key not in gold_values)
        paired = set(pairs.values())
        for position, pred in enumerate(pred_rows):
            if position not in paired:
                extra += len(_numeric(pred))
                record_ok = False
        if record_ok:
            records_exact += 1
    gold_total = hits + wrong + missing
    return {
        "records": records_total,
        "records_with_alignment": records_matched,
        "alignment_rate": round(records_matched / records_total, 4) if records_total else None,
        "gold_cells": gold_total,
        "matched_cells": hits,
        "wrong_cells": wrong,
        "missing_cells": missing,
        "extra_cells": extra,
        "recall": round(hits / gold_total, 4) if gold_total else None,
        "precision": round(hits / (hits + wrong + extra), 4) if (hits + wrong + extra) else None,
        "conditional_accuracy": round(hits / (hits + wrong), 4) if (hits + wrong) else None,
        "record_exact": records_exact,
        "record_exact_rate": round(records_exact / records_total, 4) if records_total else None,
    }


def bootstrap(per_record: dict[str, dict[str, Any]], rounds: int, seed: int = 20261113) -> dict[str, float]:
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in per_record.values():
        clusters[row["study"]].append(row)
    keys = sorted(clusters)
    rng = random.Random(seed)
    values = []
    for _ in range(rounds):
        sample = [rng.choice(keys) for _ in keys]
        gold = sum(row["gold"] for key in sample for row in clusters[key])
        matched = sum(row["matched"] for key in sample for row in clusters[key])
        if gold:
            values.append(matched / gold)
    values.sort()
    return {
        "rounds": len(values),
        "clusters": len(keys),
        "lower": round(values[int(0.025 * len(values))], 4),
        "upper": round(values[min(len(values) - 1, int(0.975 * len(values)))], 4),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set", type=Path, default=SET)
    parser.add_argument("--predictions", type=Path, default=RUN)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--bootstrap", type=int, default=1000)
    parser.add_argument(
        "--aligned",
        action="store_true",
        help="zusaetzlich zeilenweise Auswertung mit Studiennamen-Abgleich",
    )
    parser.add_argument(
        "--common",
        action="store_true",
        help="nur Records, die von allen Modellen beantwortet wurden",
    )
    args = parser.parse_args()

    records = [
        json.loads(line) for line in args.set.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    records = [row for row in records if row["dataset"] == "glass_trialreviewbench"]
    entries = []
    for line in args.predictions.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    predictions = {(row["record_id"], row["model"]): row for row in entries}
    models = sorted({row["model"] for row in entries})

    if args.common:
        answered = [
            {record_id for (record_id, model), row in predictions.items() if row.get("rows") and model == m}
            for m in models
        ]
        common = set.intersection(*answered) if answered else set()
        records = [row for row in records if row["record_id"] in common]

    payload: dict[str, Any] = {
        "run": str(args.predictions),
        "records_in_set": len(records),
        "common_subset": args.common,
        "models": {},
    }
    for model in models:
        per_record = score(records, predictions, model)
        gold = sum(row["gold"] for row in per_record.values())
        predicted = sum(row["predicted"] for row in per_record.values())
        matched = sum(row["matched"] for row in per_record.values())
        answered = sum(1 for row in per_record.values() if row["answered"])
        gold_answered = sum(row["gold"] for row in per_record.values() if row["answered"])
        matched_answered = sum(row["matched"] for row in per_record.values() if row["answered"])
        exact = sum(
            1
            for row in per_record.values()
            if row["answered"] and row["matched"] == row["gold"] and row["predicted"] == row["gold"]
        )
        errors = [
            row for row in entries if row["model"] == model and (row.get("http_status") != 200 or row.get("parse_error"))
        ]
        payload["models"][model] = {
            "records": len(per_record),
            "answered": answered,
            "gold_cells": gold,
            "predicted_cells": predicted,
            "matched_cells": matched,
            "recall": round(matched / gold, 4) if gold else None,
            "gold_cells_answered": gold_answered,
            "recall_answered": round(matched_answered / gold_answered, 4) if gold_answered else None,
            "precision": round(matched / predicted, 4) if predicted else None,
            "f1": round(2 * matched / (gold + predicted), 4) if gold and predicted else None,
            "record_exact": exact,
            "record_exact_rate": round(exact / len(per_record), 4) if per_record else None,
            "failed_calls": len(errors),
            "bootstrap_recall": bootstrap(per_record, args.bootstrap) if args.bootstrap else None,
        }
        if args.aligned:
            payload["models"][model]["aligned"] = score_aligned(records, predictions, model)

    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{'Modell':10} {'Records':>8} {'beantw.':>8} {'Recall':>8} {'Prec':>8} {'Zellen':>7} {'exakt':>6}")
    for model, values in payload["models"].items():
        print(
            f"{model:10} {values['records']:>8} {values['answered']:>8} "
            f"{str(values['recall']):>8} {str(values['precision']):>8} "
            f"{values['matched_cells']:>7} {values['record_exact']:>6}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
