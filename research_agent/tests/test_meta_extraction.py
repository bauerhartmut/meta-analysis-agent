"""Tests for reading effect sizes out of papers.

The properties under test are the ones a pooled estimate depends on: the quote is
verified against the document, the confidence level is read rather than assumed, a
missing standard error stays missing, impossible numbers are rejected with a
reason, and two disagreeing readings are marked instead of averaged.
"""

import asyncio
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.config import Config
from research_agent.database import Database
from research_agent.meta.extraction import (
    EXTRACTOR_VERSION, EffectExtractor, check_plausibility, compare_extraction_passes,
    derive_se, infer_effect_type,
)

TEXT = (
    "Abstract\n"
    "We studied cognition and health in a cohort.\n\n"
    "Methods\n"
    "Participants were recruited from two registers.\n\n"
    "Results\n"
    "The standardized mean difference in cognition was 0.42 (SE 0.10) between groups. "
    "The odds ratio for mortality was 1.35 (95 % CI 1.10 to 1.65). "
    "Heritability was estimated at 0.31 (95 % CI 0.24 to 0.38).\n\n"
    "Discussion\n"
    "These findings are consistent with earlier work.\n"
)


def _effect_payload(**overrides):
    payload = {
        "outcome": "cognition",
        "comparison": "selection vs control",
        "effect_type": "smd",
        "effect": 0.42,
        "se": 0.10,
        "ci_low": None,
        "ci_high": None,
        "ci_level": 0.95,
        "n": 1200,
        "events": None,
        "design": "cohort",
        "population": "adults",
        "moderators": {"age": "middle"},
        "direction": "higher cognition is better",
        "unit": "SD",
        "quote": "The standardized mean difference in cognition was 0.42 (SE 0.10) between groups.",
    }
    payload.update(overrides)
    return payload


class _FakeLLM:
    """Returns the queued payloads in order, one per call."""

    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.calls = 0

    async def chat_json(self, messages, **kwargs):
        self.calls += 1
        if not self.payloads:
            return []
        payload = self.payloads.pop(0)
        return payload


class ExtractionTest(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.text_row = self.db.save_source_text(
            "s1", TEXT, kind="html", origin_url="https://example.org/paper",
        )
        self.db.save_source({
            "id": "s1", "title": "Cognition and health", "author": "Doe, Jane",
            "publication_date": "2024-03-01", "url": "https://doi.org/10.1000/xyz",
            "relevance": 0.7, "relevance_scored": 1,
        })

    def extract(self, payloads, double_pass=True):
        llm = _FakeLLM(payloads)
        extractor = EffectExtractor(llm, self.db, double_pass=double_pass)
        rows = asyncio.run(extractor.extract(
            "s1", TEXT, topic="cognition and health",
            source_text_id=(self.text_row or {}).get("id", ""),
        ))
        return rows, llm.calls

    def test_quote_is_verified_against_the_document(self):
        rows, _ = self.extract([[_effect_payload()]], double_pass=False)

        self.assertEqual(len(rows), 1)
        row = self.db.get_study_effects(source_id="s1")[0]
        self.assertGreaterEqual(row["quote_start"], 0)
        self.assertIn("Results", row["section"] or "")
        self.assertEqual(row["extractor"], EXTRACTOR_VERSION)

    def test_an_invented_quote_is_stored_but_marked_unsupported(self):
        payload = _effect_payload(
            quote="The trial showed an enormous effect of 3.1 standard deviations."
        )
        self.extract([payload], double_pass=False)

        row = self.db.get_study_effects(source_id="s1")[0]
        self.assertEqual(row["quote_start"], -1)
        self.assertEqual(row["source_text_id"], "")

    def test_standard_error_is_derived_from_a_95_percent_interval(self):
        payload = _effect_payload(
            effect_type="smd", effect=0.5, se=None, ci_low=0.1, ci_high=0.9,
            ci_level=0.95, quote="The standardized mean difference in cognition was 0.42 (SE 0.10) between groups.",
        )
        self.extract([payload], double_pass=False)

        row = self.db.get_study_effects(source_id="s1")[0]
        expected = derive_se(0.1, 0.9, 0.95)
        self.assertAlmostEqual(row["se"], expected, places=10)

    def test_a_90_percent_interval_is_not_read_as_95_percent(self):
        base = dict(effect=0.5, se=None, ci_low=0.1, ci_high=0.9)
        self.extract([_effect_payload(ci_level=0.95, **base)], double_pass=False)
        wide = self.db.get_study_effects(source_id="s1")[0]["se"]

        self.db._delete("study_effects", self.db.get_study_effects(source_id="s1")[0]["id"])
        self.extract([_effect_payload(ci_level=0.9, **base)], double_pass=False)
        narrow = self.db.get_study_effects(source_id="s1")[0]["se"]

        # Reading a 90 % interval as 95 % shrinks the standard error by ~16 %, which
        # would silently over-weight the study in the pool.
        self.assertGreater(narrow, wide)
        self.assertAlmostEqual(narrow / wide, 1.96 / 1.6449, places=3)

    def test_missing_precision_stays_missing_and_is_not_poolable(self):
        payload = _effect_payload(se=None, ci_low=None, ci_high=None)
        self.extract([payload], double_pass=False)

        row = self.db.get_study_effects(source_id="s1")[0]
        self.assertIsNone(row["se"])
        self.assertEqual(row["rejection_reason"], "")
        self.assertEqual(self.db.count_study_effects(), 1)
        self.assertEqual(self.db.count_poolable_effects(), 0)

    def test_a_parameter_the_authors_set_is_not_an_estimate(self):
        # Read out of the live run 28.10.: "We set the total effect of education
        # (...) on cognitive decline to -0.05 standardized units" became an
        # effect row of -0.05 without SE - a design parameter of the authors'
        # simulation wearing the shape of a finding.
        reason = check_plausibility(_effect_payload(
            effect=-0.05, se=None,
            quote=("We set the total effect of education (<high school versus "
                   "≥high school) on cognitive decline to −0.05 standardized units"),
        ))

        self.assertIsNotNone(reason)
        self.assertIn("Simulationsannahme", reason)

    def test_an_estimate_with_precision_is_not_mistaken_for_an_assumption(self):
        self.assertIsNone(check_plausibility(_effect_payload()))
        self.assertIsNone(check_plausibility(_effect_payload(
            quote="The effect on cognition was β = -0.05 (95% CI -0.09 to -0.01).",
            effect=-0.05,
        )))

    def test_implausible_readings_are_rejected_with_a_reason(self):
        cases = [
            ({"effect_type": "r", "effect": 1.4, "n": 500}, "außerhalb"),
            ({"effect_type": "or", "effect": 0.0}, "positiv"),
            ({"ci_low": 0.9, "ci_high": 1.5, "effect": 0.2}, "enthält"),
            ({"ci_level": 1.2}, "Konfidenzniveau"),
            ({"n": 0}, "Stichprobengröße"),
            ({"direction": ""}, "Richtung"),
            ({"effect_type": "galaxy"}, "Effekttyp"),
        ]
        for overrides, expected in cases:
            reason = check_plausibility(_effect_payload(**overrides))
            self.assertIsNotNone(reason, f"{overrides} should be rejected")
            self.assertIn(expected, reason)

    def test_rejected_rows_are_stored_with_their_reason(self):
        # A herdability of 1.7 is impossible, but dropping the row silently would
        # hide a reading error - it is stored and counted instead.
        payload = _effect_payload(effect_type="r", effect=1.7, n=900, se=0.05)
        self.extract([payload], double_pass=False)

        row = self.db.get_study_effects(source_id="s1")[0]
        self.assertTrue(row["rejection_reason"])
        self.assertEqual(self.db.count_poolable_effects(), 0)

    def test_two_passes_that_agree_stay_poolable(self):
        rows, calls = self.extract([[_effect_payload()], [_effect_payload()]])

        self.assertEqual(calls, 2)
        self.assertEqual(len(rows), 2)
        self.assertEqual([r.disputed for r in rows], [0, 0])
        self.assertEqual(self.db.count_poolable_effects(), 2)

    def test_two_passes_that_disagree_are_marked_disputed(self):
        rows, _ = self.extract([
            [_effect_payload()],
            [_effect_payload(effect=0.90)],  # same sentence, different number
        ])

        self.assertEqual([r.disputed for r in rows], [1, 1])
        self.assertEqual(self.db.count_poolable_effects(), 0)

    def test_conflict_ratio_is_reported(self):
        first = [_effect_payload()]
        second = [_effect_payload(effect=0.90)]
        comparison = compare_extraction_passes(first, second)

        self.assertEqual(comparison["compared"], 1)
        self.assertEqual(comparison["conflict_ratio"], 1.0)
        self.assertIn("effect", comparison["conflicts"][0])

    def test_readings_of_different_outcomes_are_not_declared_conflicting(self):
        first = [_effect_payload(outcome="cognition")]
        second = [_effect_payload(outcome="mortality", effect=1.2)]
        comparison = compare_extraction_passes(first, second)
        self.assertEqual(comparison["compared"], 0)
        self.assertEqual(comparison["conflict_ratio"], 0.0)

    def test_an_empty_effect_type_is_recovered_from_the_quote(self):
        # Same failure shape as the live Mediterranean run: the model omits
        # `effect_type`, but the quote still names the estimate.
        self.extract([_effect_payload(effect_type="")], double_pass=False)
        row = self.db.get_study_effects(source_id="s1")[0]
        self.assertEqual(row["effect_type"], "smd")
        self.assertEqual(row["rejection_reason"], "")

    def test_infer_effect_type_names_the_estimate_the_quote_names(self):
        self.assertEqual(
            infer_effect_type("MACE (HR 0.72, 95 % CI 0.55 to 0.94)"), "hr")
        self.assertEqual(
            infer_effect_type("the odds ratio for mortality was 1.35"), "or")
        self.assertEqual(infer_effect_type("pearson correlation of 0.3"), "r")
        self.assertEqual(infer_effect_type("") , "")

    def test_an_invented_effect_type_is_still_rejected(self):
        self.extract([_effect_payload(effect_type="galaxy")], double_pass=False)
        row = self.db.get_study_effects(source_id="s1")[0]
        self.assertIn("Effekttyp", row["rejection_reason"])


class SourceIdentityTest(unittest.TestCase):
    def test_doi_column_exists_and_is_filled_by_sources(self):
        db = Database(":memory:")
        db.save_source({"id": "s1", "title": "A paper",
                        "url": "https://doi.org/10.1038/ng.3285",
                        "doi": "10.1038/ng.3285"})
        self.assertEqual(db._get("sources", "s1")["doi"], "10.1038/ng.3285")


class PassComparisonFieldTest(unittest.TestCase):
    def test_unit_design_population_ci_bounds_mark_disputed(self):
        base = {"outcome": "bp", "comparison": "med vs ctrl", "id": "r1",
                "effect": -1.2, "se": 0.3, "ci_low": -1.8, "ci_high": -0.6}
        a = {**base, "unit": "mmHg", "design": "rct", "population": "adults", "n": 400}
        b = {**base, "unit": "mmHg", "design": "rct", "population": "adults", "n": 400}
        out = compare_extraction_passes([a], [b])
        self.assertEqual(out["conflicts"], [])
        # unit disagrees -> both rows carry the dispute, none is averaged
        b2 = {**b, "unit": "ratio"}
        out = compare_extraction_passes([a], [b2])
        self.assertEqual(out["conflicts"], ["bp/?: unit"])
        self.assertEqual(a["disputed"], 1)
        self.assertEqual(b2["disputed"], 1)
        self.assertTrue(out["conflict_ratio"] > 0)

class NormalizerFieldsTest(unittest.TestCase):
    """Phase 4 additive fields ride through normalization (§7.1)."""

    def _normalize(self, item):
        from research_agent.meta.extraction import EffectExtractor
        ex = EffectExtractor(object(), Database(":memory:"), double_pass=False)
        return ex._normalize(item, targets=None)

    def test_adjusted_and_time_point_passthrough(self):
        row = self._normalize({"outcome": "bp", "effect_type": "smd",
                               "effect": -0.4, "se": 0.1,
                               "adjusted": 1, "time_point": " 12-month follow-up "})
        self.assertEqual(row["adjusted"], 1)
        self.assertEqual(row["time_point"], "12-month follow-up")

    def test_adjusted_stays_unknown_without_statement(self):
        row = self._normalize({"outcome": "bp", "effect_type": "smd",
                               "effect": -0.4, "se": 0.1})
        self.assertEqual(row["adjusted"], -1)
        self.assertEqual(row["time_point"], "")

if __name__ == "__main__":
    unittest.main()


class _RecordingLLM:
    """Queues payloads AND keeps every message list it was sent."""

    def __init__(self, payloads):
        self.payloads = list(payloads)
        self.seen = []

    async def chat_json(self, messages, **kwargs):
        self.seen.append(list(messages))
        if not self.payloads:
            return []
        return self.payloads.pop(0)


class PromptSplitTest(unittest.TestCase):
    """Pass A and pass B are separate readers: same hard rules, own framing."""

    def setUp(self):
        self.ex = EffectExtractor(_FakeLLM([]), Database(":memory:"))

    def _system(self, frame, order):
        msgs = self.ex._messages(
            TEXT, "cognition and health", None,
            field_order=order, frame=frame)
        return msgs[0]["content"]

    def test_frames_differ_by_at_least_8_chars(self):
        a = self._system("first", "effect_first")
        b = self._system("second", "precision_first")
        self.assertNotEqual(a, b)
        self.assertGreaterEqual(abs(len(a) - len(b)), 8)

    def test_second_frame_is_independent_reader(self):
        b = self._system("second", "precision_first")
        self.assertIn("INDEPENDENT SECOND READER", b)
        self.assertNotIn(
            "You read effect sizes out of research papers for the topic:",
            b.split("Return a JSON array")[0][:400])

    def test_first_frame_keeps_its_shape(self):
        a = self._system("first", "effect_first")
        self.assertIn("You read effect sizes out of research papers", a)
        self.assertNotIn("INDEPENDENT SECOND READER", a)

    def test_return_contract_identical_both_frames(self):
        a = self._system("first", "effect_first")
        b = self._system("second", "precision_first")
        self.assertIn("Return a JSON array", a)
        self.assertIn("Return a JSON array", b)
        # Same field set as a set; only the (intended) order differs.
        import re
        fa = re.findall(r"[a-z_]+", a.split("Return a JSON array")[1])
        fb = re.findall(r"[a-z_]+", b.split("Return a JSON array")[1])
        self.assertEqual(set(fa), set(fb))

    def test_pass_two_sends_second_frame(self):
        llm = _RecordingLLM([[]])
        extractor = EffectExtractor(llm, Database(":memory:"))
        asyncio.run(extractor._one_pass(
            "s1", TEXT, "cognition and health", None, pass_number=2))
        sent = llm.seen[0][0]["content"]
        self.assertIn("INDEPENDENT SECOND READER", sent)

    def test_double_pass_frames_travel_in_order(self):
        llm = _RecordingLLM([[], []])
        extractor = EffectExtractor(llm, Database(":memory:"), double_pass=True)
        asyncio.run(extractor.extract(
            "s1", TEXT, topic="cognition and health"))
        self.assertEqual(len(llm.seen), 2)
        self.assertNotIn("INDEPENDENT SECOND READER", llm.seen[0][0]["content"])
        self.assertIn("INDEPENDENT SECOND READER", llm.seen[1][0]["content"])

    def test_version_bumped_for_prompt_split(self):
        self.assertEqual(EXTRACTOR_VERSION, "meta-extraction/3")
