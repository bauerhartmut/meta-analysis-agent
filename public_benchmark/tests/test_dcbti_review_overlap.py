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
    comparison = match.compare_timepoints(
        "Woche 1 post-treatment", "10 weeks post-treatment"
    )
    assert comparison["match"] is False
    assert comparison["difference_weeks"] == 9.0


def test_week_comparison_handles_missing_number() -> None:
    comparison = match.compare_timepoints("post-treatment", "10 weeks post-treatment")
    assert comparison["match"] is None
    assert "kein Post-Treatment-Zeitpunkt" in comparison["reason"]


def test_week_comparison_converts_months() -> None:
    comparison = match.compare_timepoints(
        "6 months post-treatment", "24 weeks post-treatment"
    )
    assert comparison["our"]["post_treatment_weeks"] == [26.07]
    assert comparison["review"]["post_treatment_weeks"] == [24.0]
    assert comparison["match"] is False


def test_week_comparison_accepts_overlapping_range() -> None:
    comparison = match.compare_timepoints(
        "9-10 weeks post-treatment", "10 weeks post-treatment"
    )
    assert comparison["match"] is True


def test_parse_separates_post_treatment_from_follow_up() -> None:
    parsed = match.parse_timepoints(
        "Post 6 weeks Follow up 6 months, 12 months"
    )
    assert parsed["post_treatment_weeks"] == [6.0]
    assert parsed["follow_up_weeks"] == [26.07, 52.14]


def test_follow_up_cannot_rescue_a_post_treatment_mismatch() -> None:
    comparison = match.compare_timepoints(
        "10 weeks post-treatment",
        "Post 6 weeks; Follow up 10 weeks",
    )
    assert comparison["review"]["post_treatment_weeks"] == [6.0]
    assert comparison["review"]["follow_up_weeks"] == [10.0]
    assert comparison["ignored_follow_up_weeks"] == [10.0]
    assert comparison["match"] is False


def test_follow_up_only_is_not_comparable() -> None:
    comparison = match.compare_timepoints(
        "10 weeks post-treatment", "Follow up 10 weeks"
    )
    assert comparison["match"] is None


def test_mid_treatment_is_separate_from_post_treatment() -> None:
    parsed = match.parse_timepoints("Mid 4 weeks Post 8 weeks")
    assert parsed["other_weeks"] == [4.0]
    assert parsed["post_treatment_weeks"] == [8.0]
    assert parsed["status"] == "parsed"


def test_multiple_post_treatment_values_are_flagged() -> None:
    parsed = match.parse_timepoints("Post 6 weeks and post 10 weeks")
    assert parsed["post_treatment_weeks"] == [6.0, 10.0]
    assert parsed["ambiguous_post_treatment"] is True
    comparison = match.compare_timepoints(
        "10 weeks post-treatment", "Post 6 weeks and post 10 weeks"
    )
    assert comparison["match"] is True
    assert comparison["matched_post_weeks"] == {"our": 10.0, "review": 10.0}


def test_missing_marker_is_not_treated_as_post_treatment() -> None:
    parsed = match.parse_timepoints("10 weeks")
    assert parsed["status"] == "no_marker"
    assert parsed["post_treatment_weeks"] == []
    assert parsed["other_weeks"] == [10.0]
    comparison = match.compare_timepoints("10 weeks post-treatment", "10 weeks")
    assert comparison["match"] is None


def test_median_and_pm_values_are_uncertain_not_unparsed() -> None:
    parsed = match.parse_timepoints("follow-up (median 5.8 ± 2.5 years)")
    assert parsed["follow_up_weeks"] == []
    assert parsed["weeks"] == []
    assert parsed["uncertain_weeks"] == [302.41]
    assert parsed["status"] == "uncertain"

    mixed = match.parse_timepoints(
        "Post 10 weeks; follow-up median 5.8 ± 2.5 years"
    )
    assert mixed["post_treatment_weeks"] == [10.0]
    assert mixed["follow_up_weeks"] == []
    assert mixed["weeks"] == [10.0]
    assert mixed["uncertain_weeks"] == [302.41]
    assert mixed["status"] == "parsed"

    median_only = match.parse_timepoints(
        "10 weeks post-treatment, median follow-up 5.8 years"
    )
    assert median_only["post_treatment_weeks"] == [10.0]
    assert median_only["follow_up_weeks"] == []
    assert median_only["uncertain_weeks"] == [302.41]

    with_period = match.parse_timepoints(
        "Post 10 weeks. Follow-up median 5.8 ± 2.5 years"
    )
    assert with_period["post_treatment_weeks"] == [10.0]
    assert with_period["follow_up_weeks"] == []
    assert with_period["uncertain_weeks"] == [302.41]

    comparison = match.compare_timepoints(
        "10 weeks post-treatment", "follow-up (median 5.8 ± 2.5 years)"
    )
    assert comparison["match"] is None
    assert "unsichere" in comparison["reason"]


def test_pm_keeps_central_post_value_and_does_not_store_dispersion() -> None:
    parsed = match.parse_timepoints("Post 10 weeks ± 2 weeks")
    assert parsed["post_treatment_weeks"] == [10.0]
    assert parsed["uncertain_weeks"] == []
    assert parsed["status"] == "parsed"
    assert "± 2 weeks" in parsed["raw"]

    suffixed = match.parse_timepoints("10 weeks post-treatment ± 2 weeks")
    assert suffixed["post_treatment_weeks"] == [10.0]
    assert suffixed["uncertain_weeks"] == []
    assert suffixed["status"] == "parsed"


def test_pm_without_median_keeps_raw_text_only() -> None:
    parsed = match.parse_timepoints("follow-up 5.8 ± 2.5 years")
    assert parsed["follow_up_weeks"] == []
    assert parsed["uncertain_weeks"] == []
    assert parsed["status"] == "uncertain"
    assert "5.8 ± 2.5 years" in parsed["raw"]

    comparison = match.compare_timepoints(
        "10 weeks post-treatment", "follow-up 5.8 ± 2.5 years"
    )
    assert comparison["match"] is None
    assert "unsichere" in comparison["reason"]


def test_suffix_follow_up_is_not_counted_as_post_treatment() -> None:
    for text, expected_post in (
        ("6 weeks post-treatment, 12 weeks follow-up", [6.0]),
        ("Post 6 weeks, 12 weeks follow-up", [6.0]),
        ("10 weeks post-treatment and 12 weeks follow-up", [10.0]),
    ):
        parsed = match.parse_timepoints(text)
        assert parsed["post_treatment_weeks"] == expected_post
        assert parsed["follow_up_weeks"] == [12.0]


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
