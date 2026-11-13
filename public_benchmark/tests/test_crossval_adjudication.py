"""Tests fuer den verblindeten Adjudikations-Batch und die Auswertung."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = BENCH_ROOT / "scripts"


def _write(path: Path, rows: list[dict]) -> Path:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )
    return path


def _fixtures(tmp_path: Path) -> dict[str, Path]:
    base = [
        # C1: alle gleich
        {"record_id": 1, "field": "intervention_n", "value": 30, "table_or_section": "Table 1"},
        # C2: zwei gleich
        {"record_id": 2, "field": "intervention_mean", "value": 12.5},
        # C3: drei verschieden
        {"record_id": 3, "field": "comparator_sd", "value": 4.2},
        # C4: eines fehlt
        {"record_id": 4, "field": "intervention_events", "value": 8},
        # C6: gleicher Wert, anderer Arm
        {"record_id": 5, "field": "comparator_n", "value": 44, "arm_id": "arm_2"},
    ]
    qwen = [dict(row) for row in base]
    deepseek = [dict(row) for row in base]
    glm = [dict(row) for row in base]

    deepseek[1]["value"] = 12.5
    glm[1]["value"] = 13.0
    deepseek[2]["value"] = 4.4
    glm[2]["value"] = 5.0
    glm[3]["value"] = None
    glm[4]["arm_id"] = "arm_1"

    return {
        "qwen": _write(tmp_path / "qwen.jsonl", qwen),
        "deepseek": _write(tmp_path / "deepseek.jsonl", deepseek),
        "glm": _write(tmp_path / "glm.jsonl", glm),
    }


def _run_batch(tmp_path: Path, fixtures: dict[str, Path], out_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "build_adjudication_batch.py"),
            "--qwen", str(fixtures["qwen"]),
            "--deepseek", str(fixtures["deepseek"]),
            "--glm", str(fixtures["glm"]),
            "--out-dir", str(out_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_batch_categories_and_blinding(tmp_path: Path) -> None:
    fixtures = _fixtures(tmp_path)
    out_dir = tmp_path / "out"
    result = _run_batch(tmp_path, fixtures, out_dir)
    assert result.returncode == 0, result.stderr

    batch_text = (out_dir / "adjudication_batch_v1.jsonl").read_text(encoding="utf-8")
    assert "qwen" not in batch_text.lower()
    assert "deepseek" not in batch_text.lower()
    assert "glm" not in batch_text.lower()

    rows = [json.loads(line) for line in batch_text.splitlines() if line.strip()]
    categories = {int(row["record_id"]): row["category"] for row in rows}
    assert 1 not in categories, "C1 darf nicht im Batch landen"
    assert categories[2] == "C2"
    assert categories[3] == "C3"
    assert categories[4] == "C4"
    assert categories[5] == "C6"
    assert len(rows) == 4

    mapping = json.loads((out_dir / "adjudication_blinding_v1.json").read_text(encoding="utf-8"))
    for key, assignment in mapping["conflicts"].items():
        assert sorted(assignment) == ["candidate_1", "candidate_2", "candidate_3"]
        assert sorted(assignment.values()) == ["deepseek", "glm", "qwen"]


def test_batch_is_deterministic(tmp_path: Path) -> None:
    fixtures = _fixtures(tmp_path)
    first, second = tmp_path / "a", tmp_path / "b"
    assert _run_batch(tmp_path, fixtures, first).returncode == 0
    assert _run_batch(tmp_path, fixtures, second).returncode == 0
    assert (first / "adjudication_batch_v1.jsonl").read_bytes() == (
        second / "adjudication_batch_v1.jsonl"
    ).read_bytes()
    assert (first / "adjudication_blinding_v1.json").read_bytes() == (
        second / "adjudication_blinding_v1.json"
    ).read_bytes()


def test_agreement_counts(tmp_path: Path) -> None:
    fixtures = _fixtures(tmp_path)
    out_dir = tmp_path / "out"
    assert _run_batch(tmp_path, fixtures, out_dir).returncode == 0
    agreement = json.loads((out_dir / "model_agreement_v1.json").read_text(encoding="utf-8"))
    assert agreement["fields_compared"] == 5
    assert agreement["conflicts"] == 4
    assert agreement["categories"]["C1"] == 1
