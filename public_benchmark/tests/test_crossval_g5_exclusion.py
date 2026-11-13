"""Prueft die Cross-Validation-Artikelauswahl gegen G5 und Yun.

Der Test liest nur die erzeugte Auswahl und die eingefrorenen Quellen; er
ruft kein Modell und kein Netz auf.
"""

from __future__ import annotations

import json
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parents[1]
SELECTION = (
    BENCH_ROOT / "evaluation" / "multi_model_cross_validation" / "candidate_shortlist_v1.json"
)
P0_DIR = BENCH_ROOT / "evaluation" / "c1_pilot" / "holdout_p0_20261112"
DECISIONS = P0_DIR / "screening_decisions_v2.jsonl"
SHORTLIST = P0_DIR / "fulltext_retrieval_manifest_v1.json"
YUN_FILES = [
    BENCH_ROOT / "processed_data" / name
    for name in ("yun_c1_frozen_275.jsonl", "yun_c1_dev_26.jsonl", "yun_c1_test_249.jsonl")
]


def _load_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _selection() -> dict:
    return json.loads(SELECTION.read_text(encoding="utf-8"))


def _g5_pmcids() -> set[str]:
    shortlist = {
        row["pmcid"]
        for row in json.loads(SHORTLIST.read_text(encoding="utf-8"))["records"]
    }
    confirmed = {
        row["pmcid"]
        for row in _load_jsonl(DECISIONS)
        if row.get("screening_method") == "manual_assisted_review_v1"
        and row.get("decision") == "include_for_fulltext"
    }
    return shortlist | confirmed


def test_selection_exists_and_counts_match() -> None:
    payload = _selection()
    primary = [row for row in payload["articles"] if row["role"] == "primary"]
    reserve = [row for row in payload["articles"] if row["role"] == "reserve"]
    assert len(primary) == 25
    assert len(reserve) == 10
    assert payload["status"] == "selected_pending_fulltext_check"


def test_selection_is_disjoint_from_g5() -> None:
    payload = _selection()
    chosen = {row["pmcid"] for row in payload["articles"]}
    assert not chosen & _g5_pmcids()


def test_selection_is_disjoint_from_yun() -> None:
    payload = _selection()
    chosen = {row["pmcid"] for row in payload["articles"]}
    yun = set()
    for path in YUN_FILES:
        yun |= {row["pmcid"] for row in _load_jsonl(path)}
    assert not chosen & yun


def test_selected_articles_passed_screening() -> None:
    payload = _selection()
    decisions = {row["pmcid"]: row for row in _load_jsonl(DECISIONS)}
    for row in payload["articles"]:
        assert decisions[row["pmcid"]]["decision"] == "include_for_fulltext"


def test_selection_is_reproducible_by_rank() -> None:
    payload = _selection()
    ranks = [row["rank_sha256"] for row in payload["articles"]]
    assert ranks == sorted(ranks)
    assert len(set(ranks)) == len(ranks)
