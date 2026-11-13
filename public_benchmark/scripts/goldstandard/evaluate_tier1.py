#!/usr/bin/env python3
"""Bewertet Modellexraktionen gegen den externen Validierungssatz (Stufe 1).

Eingabe: Vorhersagen als JSONL, je Zeile entweder

    {"record_id": "...", "cell_id": "...", "value": 12.5}

oder gebuendelt

    {"record_id": "...", "cells": [{"cell_id": "...", "value": 12.5}, ...]}

Ausgewertet wird je Datensatz: exakte Zelltreffer, Record-Genauigkeit
(alle Zellen richtig), fehlende und zusaetzliche Zellen sowie Armvertauschungen
(nur European Urology, weil dort beide Arme bekannt sind).
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

CROSSVAL = Path(__file__).resolve().parents[2] / "evaluation" / "multi_model_cross_validation"
DEFAULT_SET = CROSSVAL / "tier1_validation_set_v1.jsonl"


def same(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return a is b
    try:
        return abs(float(a) - float(b)) < 1e-6
    except (TypeError, ValueError):
        return str(a).strip().lower() == str(b).strip().lower()


def load_predictions(path: Path) -> dict[str, dict[str, Any]]:
    predictions: dict[str, dict[str, Any]] = defaultdict(dict)
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        record_id = row["record_id"]
        if "cells" in row:
            for cell in row["cells"]:
                predictions[record_id][cell["cell_id"]] = cell.get("value")
        else:
            predictions[record_id][row["cell_id"]] = row.get("value")
    return predictions


def swap_count(reference: dict[str, Any], prediction: dict[str, Any]) -> int:
    """Zaehlt Zellen, deren Wert exakt zum anderen Arm gehoert."""
    arms = {cell["arm"] for cell in reference.values() if cell.get("arm")}
    if len(arms) != 2:
        return 0
    swaps = 0
    for cell_id, predicted in prediction.items():
        ref_cell = reference.get(cell_id)
        if ref_cell is None or ref_cell.get("arm") is None:
            continue
        if same(predicted, ref_cell["value"]):
            continue
        other_arm = ({"arm_1", "arm_2"} - {ref_cell["arm"]}).pop()
        counterpart = f"{other_arm}.{cell_id.split('.', 1)[1]}"
        other_cell = reference.get(counterpart)
        if other_cell and same(predicted, other_cell["value"]) and not same(
            other_cell["value"], ref_cell["value"]
        ):
            swaps += 1
    return swaps


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--set", type=Path, default=DEFAULT_SET)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--bootstrap", type=int, default=0)
    args = parser.parse_args()

    records = [
        json.loads(line) for line in args.set.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    predictions = load_predictions(args.predictions)

    stats: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for record in records:
        dataset = record["dataset"]
        reference = {cell["cell_id"]: cell for cell in record["cells"]}
        predicted = predictions.get(record["record_id"], {})
        stats[dataset]["records"] += 1
        stats[dataset]["cells"] += len(reference)
        correct = 0
        for cell_id, cell in reference.items():
            if cell_id not in predicted:
                stats[dataset]["missing"] += 1
            elif same(predicted[cell_id], cell["value"]):
                stats[dataset]["correct"] += 1
                correct += 1
            else:
                stats[dataset]["wrong"] += 1
        stats[dataset]["extra"] += sum(1 for cell_id in predicted if cell_id not in reference)
        if reference and correct == len(reference):
            stats[dataset]["records_complete"] += 1
        stats[dataset]["arm_swaps"] += swap_count(reference, predicted)

    payload: dict[str, Any] = {"predictions": str(args.predictions), "per_dataset": {}}
    for dataset, values in sorted(stats.items()):
        cells = values["cells"]
        payload["per_dataset"][dataset] = {
            **values,
            "cell_accuracy": round(values["correct"] / cells, 4) if cells else None,
            "record_accuracy": round(values["records_complete"] / values["records"], 4)
            if values["records"]
            else None,
            "coverage": round((cells - values["missing"]) / cells, 4) if cells else None,
        }
    if args.bootstrap:
        for dataset in payload["per_dataset"]:
            interval = cluster_bootstrap(records, predictions, dataset, args.bootstrap)
            if interval:
                payload["per_dataset"][dataset]["cell_accuracy_bootstrap"] = interval

    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cluster_bootstrap(
    records: list[dict[str, Any]],
    predictions: dict[str, dict[str, Any]],
    dataset: str,
    rounds: int,
    seed: int = 20261113,
) -> dict[str, float] | None:
    """Zellgenauigkeit mit Cluster-Resampling auf Studienebene."""
    subset = [row for row in records if row["dataset"] == dataset]
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in subset:
        clusters[row["study_id"]].append(row)
    keys = sorted(clusters)
    if len(keys) < 3:
        return None
    rng = random.Random(seed)
    values = []
    for _ in range(rounds):
        sample = [rng.choice(keys) for _ in keys]
        correct = total = 0
        for key in sample:
            for row in clusters[key]:
                predicted = predictions.get(row["record_id"], {})
                for cell in row["cells"]:
                    total += 1
                    if cell["cell_id"] in predicted and same(
                        predicted[cell["cell_id"]], cell["value"]
                    ):
                        correct += 1
        if total:
            values.append(correct / total)
    if not values:
        return None
    values.sort()
    return {
        "rounds": len(values),
        "clusters": len(keys),
        "lower": round(values[int(0.025 * len(values))], 4),
        "upper": round(values[min(len(values) - 1, int(0.975 * len(values)))], 4),
    }


if __name__ == "__main__":
    raise SystemExit(main())
