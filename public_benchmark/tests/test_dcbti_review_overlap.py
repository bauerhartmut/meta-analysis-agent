"""Tests fuer den Abgleich mit Hwang 2025 und Lee 2023."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import match_dcbti_review_studies as match  # noqa: E402


def study(study_id: str) -> dict:
    studies, _ = match.load_our_studies()
    return next(row for row in studies if row["study_id"] == study_id)


def test_normalize_surname_handles_prefixes() -> None:
    assert match.normalize_surname("de Bruin") == "bruin"
    assert match.normalize_surname("van der Zweerde") == "zweerde"
    assert match.normalize_surname("Tomfohr-Madsen") == "tomfohrmadsen"


def test_project_has_nine_cbti_studies_not_thirty() -> None:
    studies, _ = match.load_our_studies()
    assert len(studies) == 9


def test_freeman_matches_only_lee() -> None:
    freeman = study("freeman_2017")
    assert match.review_matches(freeman, match.REVIEWS["lee2023"])
    assert match.review_matches(freeman, match.REVIEWS["hwang2025"]) == []


def test_freeman_doi_and_pmcid_are_present() -> None:
    freeman = study("freeman_2017")
    assert freeman["doi"] == "10.1016/S2215-0366(17)30328-0"
    assert freeman["pmcid"] == "PMC5614772"


def test_freeman_outcome_timepoint_and_n_overlap() -> None:
    overlap = match.build_overlap(study("freeman_2017"), match.REVIEWS["lee2023"])
    assert overlap["matched"] is True
    assert overlap["outcome_overlap"] == ["ISI"]
    assert overlap["timepoint_match"] is True
    assert overlap["n_ours"] == 3755
    assert overlap["n_match"] is True


def test_chan_2021_is_not_chan_2023() -> None:
    chan = study("chan_2021")
    assert match.review_matches(chan, match.REVIEWS["hwang2025"]) == []


def test_no_unfounded_matches_for_other_studies() -> None:
    for study_id in (
        "morris_2015", "fucito_2017", "de_bruin_2018", "chan_2022",
        "de_bruin_2015", "egbegi_2021", "tomfohr_madsen_2020",
    ):
        row = study(study_id)
        for review in match.REVIEWS.values():
            assert match.review_matches(row, review) == []


def test_parse_timepoints_in_both_word_orders() -> None:
    assert match.parse_timepoints("post-treatment (Woche 10)")["weeks"] == [10.0]
    assert match.parse_timepoints("10 Wochen post-treatment")["weeks"] == [10.0]


def test_week_comparison_does_not_match_substrings() -> None:
    comparison = match.compare_timepoints("Woche 1", "10 weeks")
    assert comparison["match"] is False
    assert comparison["difference_weeks"] == 9.0


def test_week_comparison_handles_missing_number() -> None:
    comparison = match.compare_timepoints("post-treatment", "10 weeks")
    assert comparison["match"] is None
    assert "kein numerischer Wochenwert" in comparison["reason"]


def test_week_comparison_converts_months() -> None:
    comparison = match.compare_timepoints("6 months", "24 weeks")
    assert comparison["our"]["weeks"] == [26.07]
    assert comparison["review"]["weeks"] == [24.0]
    assert comparison["match"] is False


def test_week_comparison_accepts_overlapping_range() -> None:
    comparison = match.compare_timepoints("9-10 weeks", "10 weeks")
    assert comparison["match"] is True


def test_freeman_uses_structured_timepoint_comparison() -> None:
    overlap = match.build_overlap(study("freeman_2017"), match.REVIEWS["lee2023"])
    comparison = overlap["timepoint_comparison"]
    assert comparison["our"]["weeks"] == [10.0]
    assert comparison["review"]["weeks"] == [10.0]
    assert comparison["difference_weeks"] == 0.0
    assert comparison["match"] is True


def test_every_unmatched_study_has_reasons_for_both_reviews() -> None:
    result = match.build_result()
    assert result["unmatched_studies"]
    for study_id in result["unmatched_studies"]:
        assert set(result["exclusion_reasons"][study_id]) == {
            "hwang2025", "lee2023"
        }
        for reason in result["exclusion_reasons"][study_id].values():
            assert reason["criterion"]
            assert reason["reason"]
            assert reason["confidence"] in {"hoch", "mittel", "niedrig"}


def test_thirty_frozen_documents_contain_no_dcbti_study() -> None:
    info = match.inspect_thirty_documents()
    assert info["documents"] == 30
    assert info["dcbti_titles"] == 0
