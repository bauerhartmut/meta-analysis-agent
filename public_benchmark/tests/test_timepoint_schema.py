"""Tests fuer die Uebernahme der Zeitpunktsegmente ins Extraktionsschema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BENCH_ROOT / "scripts"))

import segment_timepoint_schema as schema  # noqa: E402

SCHEMA_PATH = BENCH_ROOT.parent / "docs" / "internal" / "goldstandard_schema.json"


def _effect() -> dict:
    return {
        "effect_id": "abc12345-01",
        "outcome_verbatim": "Insomnia Severity Index",
        "outcome_normalized": "ISI",
        "comparison_verbatim": "dCBT-I vs. TAU",
        "effect_type": "md",
        "effect": -3.2,
        "ci_low": -5.1,
        "ci_high": -1.3,
        "quote": "ISI difference -3.2 (95% CI -5.1 to -1.3)",
        "quote_start": 0,
        "quote_end": 44,
        "design_verbatim": "randomised controlled trial",
        "certainty": "high",
        "is_primary": True,
        "time_point": "10 weeks post-treatment",
    }


def test_schema_exposes_structured_timepoint_segments() -> None:
    data = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    effect = data["$defs"]["effect"]
    segments = effect["properties"]["time_point_segments"]
    assert "time_point_segments" not in effect["required"]
    assert set(segments["required"]) == {
        "status",
        "post_treatment_weeks",
        "follow_up_weeks",
        "other_weeks",
        "ambiguous_post_treatment",
    }


def test_segmentation_preserves_outcome_values(tmp_path: Path) -> None:
    original = _effect()
    source = tmp_path / "goldstandard.json"
    target = tmp_path / "goldstandard_segmentiert.json"
    source.write_text(
        json.dumps(
            {
                "dataset": "goldstandard_effects",
                "documents": [{"document_id": "abc12345", "effects": [original]}],
            }
        ),
        encoding="utf-8",
    )

    counts = schema.segment_file(source, target)
    result = json.loads(target.read_text(encoding="utf-8"))
    effect = result["documents"][0]["effects"][0]

    assert counts["parsed"] == 1
    for field, value in original.items():
        assert effect[field] == value
    assert effect["time_point_segments"] == {
        "status": "parsed",
        "post_treatment_weeks": [10.0],
        "follow_up_weeks": [],
        "other_weeks": [],
        "ambiguous_post_treatment": False,
        "raw": "10 weeks post-treatment",
    }
