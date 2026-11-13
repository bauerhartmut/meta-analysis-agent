"""Prueft Fallmix, Volltextverfuegbarkeit und Dublettenfreiheit der Auswahl v2.

Der Test liest nur die erzeugten Artefakte; er ruft kein Modell und kein Netz
auf. Lokale XML-Dateien liegen in einem ignorierten Ordner und werden hier
nicht vorausgesetzt, nur ihre Manifest-Hashes.
"""

from __future__ import annotations

import json
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT = BENCH_ROOT / "evaluation" / "multi_model_cross_validation"
SELECTION = OUT / "candidate_shortlist_v2.json"
PROFILE = OUT / "fallmix_profile_v1.json"
AVAILABILITY = OUT / "fulltext_availability_v1.json"

MIN_CONTINUOUS = 10
MIN_BINARY = 10
MIN_BOTH = 5
MIN_MULTIARM = 2
ALLOWED_REASONS = {"no_arm_data", "duplicate_trial", "review_or_summary", "no_fulltext"}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _selection() -> dict:
    return _load(SELECTION)


def _profile() -> dict:
    return _load(PROFILE)


def _profiles_by_pmcid() -> dict[str, dict]:
    return {row["pmcid"]: row for row in _profile()["profiles"]}


def test_selection_has_primary_and_reserve() -> None:
    payload = _selection()
    primary = [row for row in payload["articles"] if row["role"] == "primary"]
    reserve = [row for row in payload["articles"] if row["role"] == "reserve"]
    assert len(primary) == 25
    assert len(reserve) == 10
    assert payload["status"] == "selected_pending_annotation"


def test_selection_is_unique_and_ranked() -> None:
    payload = _selection()
    pmcids = [row["pmcid"] for row in payload["articles"]]
    assert len(set(pmcids)) == len(pmcids)
    positions = [row["position"] for row in payload["articles"]]
    assert positions == sorted(positions)


def test_selected_articles_are_available_with_hash() -> None:
    payload = _selection()
    records = {row["pmcid"]: row for row in _load(AVAILABILITY)["records"]}
    for row in payload["articles"]:
        record = records[row["pmcid"]]
        assert record["saved"] is True
        assert len(record["sha256"]) == 64
        assert row["sha256"] == record["sha256"]


def test_no_duplicate_trials_among_selected() -> None:
    payload = _selection()
    profiles = _profiles_by_pmcid()
    seen: dict[str, str] = {}
    for row in payload["articles"]:
        profile = profiles[row["pmcid"]]
        assert "duplicate_trial" not in profile["reasons"]
        for registry in profile["registry_ids"]:
            assert registry not in seen, f"{registry} doppelt: {seen.get(registry)} / {row['pmcid']}"
            seen[registry] = row["pmcid"]


def test_case_mix_covers_continuous_binary_and_multiarm() -> None:
    mix = _profile()["case_mix_primary"]
    assert mix["articles"] == 25
    assert mix["continuous_signal"] >= MIN_CONTINUOUS
    assert mix["binary_signal"] >= MIN_BINARY
    assert mix["both_signals"] >= MIN_BOTH
    assert mix["multiarm"] >= MIN_MULTIARM


def test_case_mix_reports_supplements() -> None:
    mix = _profile()["case_mix_primary"]
    # Supplemente sind fuer dieses Experiment relevant, aber kein Muss fuer
    # jeden Artikel; der Test haelt nur fest, dass sie erfasst werden.
    assert "with_supplement" in mix
    assert 0 <= mix["with_supplement"] <= mix["articles"]


def test_excluded_articles_have_documented_reason() -> None:
    payload = _selection()
    selected = {row["pmcid"] for row in payload["articles"]}
    for profile in _profile()["profiles"]:
        for reason in profile["reasons"]:
            assert reason in ALLOWED_REASONS
        if profile["reasons"]:
            assert profile["pmcid"] not in selected
            assert profile["selected"] == ""


def test_selection_matches_profile_order() -> None:
    payload = _selection()
    profiles = _profile()["profiles"]
    suitable = [row["pmcid"] for row in profiles if not row["reasons"]]
    expected = suitable[:25] + suitable[25:35]
    assert [row["pmcid"] for row in payload["articles"]] == expected
