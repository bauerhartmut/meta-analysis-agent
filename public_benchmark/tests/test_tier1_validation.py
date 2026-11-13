"""Tests fuer den externen Validierungssatz (Stufe 1) und seine Auswertung."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BENCH = Path(__file__).resolve().parents[1]
CROSSVAL = BENCH / "evaluation" / "multi_model_cross_validation"
SCRIPT = BENCH / "scripts" / "goldstandard" / "evaluate_tier1.py"


def _records() -> list[dict]:
    path = CROSSVAL / "tier1_validation_set_v1.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_set_manifest_matches_records() -> None:
    manifest = json.loads((CROSSVAL / "tier1_validation_set_v1.json").read_text(encoding="utf-8"))
    records = _records()
    assert len(records) == manifest["records"] == 185
    assert manifest["records_by_dataset"] == {"eururology": 104, "glass_trialreviewbench": 81}
    assert sum(len(row["cells"]) for row in records) == manifest["cells"] == 744
    assert manifest["records_without_cells"] == 0


def test_arms_only_for_eururology() -> None:
    for row in _records():
        if row["dataset"] == "eururology":
            assert all(cell["arm"] in {"arm_1", "arm_2"} for cell in row["cells"])
        else:
            assert all(cell["arm"] is None for cell in row["cells"])


def test_evaluator_counts_swaps_and_missing(tmp_path: Path) -> None:
    records = [row for row in _records() if row["dataset"] == "eururology"][:4]
    predictions = []
    expected_swaps = 0
    for index, record in enumerate(records):
        cells = []
        for cell in record["cells"]:
            value = cell["value"]
            if index == 0:
                cells.append({"cell_id": cell["cell_id"], "value": value})
                continue
            other_arm = "arm_2" if cell["arm"] == "arm_1" else "arm_1"
            counterpart_id = f"{other_arm}.{cell['cell_id'].split('.', 1)[1]}"
            counterpart = next(
                (c for c in record["cells"] if c["cell_id"] == counterpart_id), None
            )
            if cell["cell_id"].endswith("events") and counterpart is not None:
                cells.append({"cell_id": cell["cell_id"], "value": counterpart["value"]})
                if counterpart["value"] != value:
                    expected_swaps += 1
            else:
                cells.append({"cell_id": cell["cell_id"], "value": value})
        predictions.append({"record_id": record["record_id"], "cells": cells})

    path = tmp_path / "pred.jsonl"
    path.write_text("\n".join(json.dumps(row) for row in predictions) + "\n", encoding="utf-8")
    out = tmp_path / "result.json"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--predictions", str(path), "--out", str(out), "--bootstrap", "20"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr

    stats = json.loads(out.read_text(encoding="utf-8"))["per_dataset"]["eururology"]
    predicted_cells = sum(len(record["cells"]) for record in records)
    assert stats["cells"] == 486
    assert stats["missing"] == 486 - predicted_cells
    assert stats["correct"] + stats["wrong"] == predicted_cells
    assert stats["wrong"] == expected_swaps
    assert stats["arm_swaps"] == expected_swaps
    assert stats["records_complete"] == 1
    assert "cell_accuracy_bootstrap" in stats
