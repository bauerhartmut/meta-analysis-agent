"""Tests fuer dataset_manifest.json des Cross-Validation-Experiments."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT = BENCH_ROOT / "evaluation" / "multi_model_cross_validation"
MANIFEST = OUT / "dataset_manifest.json"


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def test_manifest_is_draft_without_reference() -> None:
    payload = _manifest()
    assert payload["status"] == "draft_pending_annotation"
    assert payload["reference"]["status"] == "pending"
    assert payload["reference"]["path"] is None
    assert payload["freeze"]["frozen"] is False
    assert payload["records"] is None


def test_manifest_counts_and_hashes() -> None:
    payload = _manifest()
    assert payload["article_counts"] == {"primary": 25, "reserve": 10}
    assert len(payload["articles"]) == 35
    for article in payload["articles"]:
        assert len(article["input_sha256"]) == 64
        assert article["reserved_for"] == "crossval_exploration"


def test_manifest_disjointness_is_verified() -> None:
    payload = _manifest()
    assert payload["disjointness"]["verified"] is True
    assert payload["disjointness"]["g5_overlap"] == []
    assert payload["disjointness"]["yun_overlap"] == []


def test_manifest_schema_hash_matches_file() -> None:
    payload = _manifest()
    digest = hashlib.sha256((OUT / "schema_v1.json").read_bytes()).hexdigest()
    assert payload["schema"]["sha256"] == digest
