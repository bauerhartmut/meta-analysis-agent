"""Tests for the aim of a synthesis: which outcomes the question is about.

The failure these tests guard against is quiet and looks like success: 40 papers
read, 40 effect rows stored, and no pooled number, because every paper used its
own name for the same construct and each group held exactly one study.

What is checked here:

* the derivation keeps a usable aim and discards an unusable one (never invents),
* the aim is written once and cannot be re-aimed later,
* a reading is mapped onto the aim deterministically (exact, alias, containment),
* the prompt names the aim, so the model does not have to guess the vocabulary,
* pooling groups by the aim, not by the wording, and counts what lies beside it,
* dependent rows (same study, same outcome) count once.
"""

import asyncio
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.extraction import EffectExtractor
from research_agent.meta.pooling import build_analysis
from research_agent.meta.targets import (
    build_targets, canonical_outcome, coverage, load_targets, normalize_targets,
    save_targets, target_labels,
)

TARGETS = {
    "version": "meta-targets/1",
    "question": "Is the cognition-health association causal?",
    "population": "adults of European ancestry",
    "outcomes": [
        {
            "label": "cognitive ability",
            "aliases": ["IQ", "cognitive test score", "general cognitive ability"],
            "direction": "higher = better cognition",
            "scale": "smd",
        },
        {
            "label": "all-cause mortality",
            "aliases": ["death", "mortality"],
            "direction": "higher = more deaths",
            "scale": "hr",
        },
    ],
    "exclusion": ["animal studies"],
}


class FakeLLM:
    def __init__(self, payload):
        self.payload = payload
        self.calls = 0

    async def chat_json(self, messages, temperature=0.2, max_tokens=900):
        self.calls += 1
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class TestDerivation(unittest.TestCase):
    def test_a_list_of_strings_is_accepted_as_outcomes(self):
        targets = normalize_targets(["cognitive ability", "mortality"])
        self.assertEqual(target_labels(targets), ["cognitive ability", "mortality"])

    def test_json_text_is_parsed(self):
        targets = normalize_targets(json.dumps({"outcomes": [{"label": "IQ"}]}))
        self.assertEqual(target_labels(targets), ["IQ"])

    def test_duplicates_and_empty_labels_are_dropped(self):
        targets = normalize_targets({
            "outcomes": [
                {"label": "IQ", "aliases": ["iq", "IQ"]},
                {"label": "iq"},
                {"label": "  "},
            ]
        })
        self.assertEqual(target_labels(targets), ["IQ"])
        self.assertEqual(targets["outcomes"][0]["aliases"], [])

    def test_garbage_yields_no_targets_instead_of_a_guess(self):
        for payload in (None, 42, "not json", {"outcomes": []}, {"outcomes": [42]}):
            self.assertEqual(normalize_targets(payload), {})

    def test_the_derivation_prompt_asks_for_related_endpoints(self):
        # v2 of the aim: the Mediterranean run pooled k = 2 while 21 poolable
        # rows sat beside a narrow three-outcome aim. The prompt now asks for
        # closely related endpoints as their OWN outcomes (no alias merging,
        # which would pool different constructs) and excludes exposure
        # metadata (adherence scores, reliability) up front.
        class _Capture:
            messages = None

            async def chat_json(self, messages, temperature=0.2, max_tokens=900):
                self.messages = messages
                return {"outcomes": []}

        llm = _Capture()
        asyncio.run(
            build_targets(llm, "Mediterranean diet and cardiovascular risk"))
        content = llm.messages[0]["content"]

        self.assertIn("CLOSELY RELATED", content)
        self.assertIn("own outcome", content)
        self.assertIn("MEDAS", content)
        self.assertIn("test-retest", content)

    def test_the_version_reports_the_prompt_generation(self):
        targets = normalize_targets({"outcomes": [{"label": "blood pressure"}]})
        self.assertEqual(targets["version"], "meta-targets/2")

    def test_at_most_six_outcomes(self):
        targets = normalize_targets(
            {"outcomes": [{"label": f"outcome {i}"} for i in range(10)]}
        )
        self.assertEqual(len(targets["outcomes"]), 6)

    def test_build_targets_keeps_the_question_and_tolerates_a_dead_model(self):
        llm = FakeLLM({"outcomes": [{"label": "cognitive ability"}]})
        targets = asyncio.run(_build(llm, "cognition and health"))
        self.assertEqual(target_labels(targets), ["cognitive ability"])
        self.assertEqual(targets["question"], "cognition and health")

        dead = FakeLLM(RuntimeError("backend down"))
        self.assertEqual(asyncio.run(_build(dead, "cognition and health")), {})

    def test_the_asked_question_beats_the_one_the_model_writes_back(self):
        # Measured on the real model: asked about a broad topic, it returned a
        # narrow falsification test as its own "question" - an aim that would
        # exclude most of the corpus.
        targets = normalize_targets(
            {"question": "Falsification test for one cohort",
             "outcomes": [{"label": "cognitive ability"}]},
            question="cognition and health",
        )
        self.assertEqual(targets["question"], "cognition and health")


async def _build(llm, topic):
    from research_agent.meta.targets import build_targets

    return await build_targets(llm, topic)


class TestDesignProperties(unittest.TestCase):
    """Measured on the real model: asked about a power question, it offered
    "Statistical power" and "Causal effect estimate" as outcomes. Those are
    answers the run computes itself, not variables a paper reports in a table."""

    def test_power_and_effect_estimates_are_not_outcomes(self):
        targets = normalize_targets({"outcomes": [
            {"label": "Statistical power"},
            {"label": "Causal effect estimate"},
            {"label": "Sample size requirement"},
            {"label": "General cognitive ability"},
        ]})
        self.assertEqual(target_labels(targets), ["General cognitive ability"])

    def test_a_measured_construct_containing_bias_survives(self):
        targets = normalize_targets({"outcomes": [{"label": "Attentional bias"}]})
        self.assertEqual(target_labels(targets), ["Attentional bias"])

    def test_only_design_properties_yield_no_aim_at_all(self):
        self.assertEqual(
            normalize_targets({"outcomes": [{"label": "Statistical power"}]}), {}
        )


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="meta_targets_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.db = Database(":memory:")

    def test_targets_are_written_once(self):
        first = save_targets(self.db, "topic a", TARGETS)
        self.assertTrue(first["written"])
        second = save_targets(self.db, "topic a", {
            "outcomes": [{"label": "something else"}]
        })
        self.assertFalse(second["written"])
        self.assertEqual(target_labels(load_targets(self.db, "topic a")),
                         ["cognitive ability", "all-cause mortality"])

    def test_an_empty_aim_is_not_stored(self):
        self.assertFalse(save_targets(self.db, "topic b", {"outcomes": []})["written"])
        self.assertEqual(load_targets(self.db, "topic b"), {})

    def test_topics_do_not_share_an_aim(self):
        save_targets(self.db, "topic a", TARGETS)
        self.assertEqual(load_targets(self.db, "topic b"), {})


class TestCanonicalisation(unittest.TestCase):
    def test_exact_label_and_alias(self):
        self.assertEqual(canonical_outcome("Cognitive Ability", TARGETS),
                         "cognitive ability")
        self.assertEqual(canonical_outcome("IQ", TARGETS), "cognitive ability")

    def test_punctuation_and_spacing_do_not_matter(self):
        self.assertEqual(canonical_outcome("  cognitive   ability.", TARGETS),
                         "cognitive ability")

    def test_containment_maps_a_longer_wording(self):
        self.assertEqual(
            canonical_outcome("general cognitive ability (z-score)", TARGETS),
            "cognitive ability",
        )

    def test_a_short_alias_never_swallows_a_label(self):
        # "IQ" is two characters: containment would match "IQ in ..." and much
        # else, so only an exact hit is accepted.
        self.assertEqual(canonical_outcome("IQ decline", TARGETS), "")

    def test_an_unrelated_outcome_has_no_key(self):
        self.assertEqual(canonical_outcome("blood pressure", TARGETS), "")
        self.assertEqual(canonical_outcome("", TARGETS), "")

    def test_no_targets_means_no_canonicalisation(self):
        self.assertEqual(canonical_outcome("IQ", {}), "")


class TestExtractionAiming(unittest.TestCase):
    def setUp(self):
        self.extractor = EffectExtractor(llm=None, db=None)

    def test_the_prompt_names_the_targets_and_their_aliases(self):
        messages = self.extractor._messages("text", "cognition", None,
                                            targets=TARGETS)
        system = messages[0]["content"]
        self.assertIn("cognitive ability", system)
        self.assertIn("IQ", system)
        self.assertIn("higher = better cognition", system)
        self.assertIn("cognitive ability", messages[1]["content"])

    def test_without_targets_the_prompt_asks_for_a_free_label(self):
        messages = self.extractor._messages("text", "cognition", None)
        self.assertNotIn("use the label EXACTLY", messages[0]["content"])
        self.assertNotIn("Outcomes of interest", messages[1]["content"])

    def test_a_reading_is_stored_with_its_target_key(self):
        row = self.extractor._normalize(
            {"outcome": "general cognitive ability (z)", "effect_type": "smd",
             "effect": 0.2, "se": 0.05},
            TARGETS,
        )
        self.assertEqual(row["outcome"], "general cognitive ability (z)")
        self.assertEqual(row["outcome_key"], "cognitive ability")

    def test_a_reading_beside_the_target_keeps_an_empty_key(self):
        row = self.extractor._normalize(
            {"outcome": "blood pressure", "effect_type": "smd",
             "effect": 0.2, "se": 0.05},
            TARGETS,
        )
        self.assertEqual(row["outcome_key"], "")


def _row(index, outcome_key, outcome, se, source_id=None, doi="", effect=0.3,
         effect_type="smd"):
    return {
        "id": f"e{index}",
        "source_id": source_id if source_id is not None else f"s{index}",
        "doi": doi,
        "outcome": outcome,
        "outcome_key": outcome_key,
        "effect_type": effect_type,
        "effect": effect,
        "se": se,
        "ci_level": 0.95,
        "disputed": 0,
        "rejection_reason": "",
        "design": "cohort",
        "title": f"Paper {index}",
    }


class TestPoolingByAim(unittest.TestCase):
    def test_two_wordings_of_one_construct_share_a_pool(self):
        # Exactly the case that produced no pooled number before: the same
        # construct under the model's two names.
        rows = [
            _row(1, "cognitive ability", "fluid intelligence", 0.10),
            _row(2, "cognitive ability", "IQ score", 0.12),
        ]
        analysis = build_analysis(rows, outcomes=["cognitive ability"])
        self.assertEqual(len(analysis["groups"]), 1)
        group = next(iter(analysis["groups"].values()))
        self.assertEqual(group["k"], 2)
        self.assertIsNotNone(group["pooled"])

    def test_rows_beside_the_aim_are_counted_not_pooled(self):
        rows = [
            _row(1, "cognitive ability", "IQ", 0.10),
            _row(2, "cognitive ability", "verbal fluency", 0.11),
            _row(3, "", "blood pressure", 0.20),
        ]
        analysis = build_analysis(rows, outcomes=["cognitive ability"])
        self.assertEqual(next(iter(analysis["groups"].values()))["k"], 2)
        self.assertEqual(len(analysis["off_target"]), 1)
        self.assertIn("nicht im Zielmaß", analysis["off_target"][0]["reason"])
        self.assertEqual(analysis["total"], 3)

    def test_a_key_from_an_older_aim_is_matched_again(self):
        # Rows read under a re-derived goal keep their old key; the reading and
        # its quote do not move, only the group.
        rows = [_row(1, "Cognitive ability", "cognitive ability", 0.10)]
        targets = {"outcomes": [{"label": "General cognitive ability"}]}
        analysis = build_analysis(rows, outcomes=["General cognitive ability"],
                                  targets=targets)
        self.assertEqual(list(analysis["groups"]), ["General cognitive ability [hedges_g]"])
        self.assertEqual(analysis["off_target"], [])

    def test_without_an_aim_nothing_is_dropped(self):
        rows = [_row(1, "", "IQ", 0.10), _row(2, "", "blood pressure", 0.12)]
        analysis = build_analysis(rows)
        self.assertEqual(len(analysis["groups"]), 2)
        self.assertEqual(analysis["off_target"], [])

    def test_dependent_rows_of_one_source_count_once(self):
        rows = [
            _row(1, "cognitive ability", "IQ", 0.20, source_id="s1", effect=0.3),
            _row(2, "cognitive ability", "IQ", 0.10, source_id="s1", effect=0.3),
        ]
        analysis = build_analysis(rows, outcomes=["cognitive ability"])
        group = next(iter(analysis["groups"].values()))
        self.assertEqual(group["k"], 1)
        self.assertEqual(len(analysis["excluded"]), 1)
        self.assertIn("dieselbe Quelle", analysis["excluded"][0]["reason"])
        # The more precise reading survives (se 0.10 beats se 0.20).
        self.assertEqual(group["rows"][0]["se"], 0.10)

    def test_the_same_doi_twice_is_one_study(self):
        rows = [
            _row(1, "cognitive ability", "IQ", 0.10, source_id="s1", doi="10.1/x"),
            _row(2, "cognitive ability", "IQ", 0.12, source_id="s2", doi="10.1/X"),
        ]
        analysis = build_analysis(rows, outcomes=["cognitive ability"])
        group = next(iter(analysis["groups"].values()))
        self.assertEqual(group["k"], 1)
        self.assertIn("doi:10.1/x", analysis["excluded"][0]["reason"])


class TestCoverage(unittest.TestCase):
    def test_counts_on_and_beside_the_aim(self):
        rows = [
            _row(1, "cognitive ability", "IQ", 0.10),
            _row(2, "", "blood pressure", 0.10),
            dict(_row(3, "cognitive ability", "IQ", None), se=None,
                 ci_low=0.1, ci_high=0.3),
        ]
        result = coverage(rows, TARGETS)
        self.assertTrue(result["has_targets"])
        self.assertEqual(result["rows"], 3)
        self.assertEqual(result["on_target"], 2)
        self.assertEqual(result["off_target"], 1)
        self.assertEqual(result["on_target_poolable"], 2)
        self.assertEqual(result["by_outcome"]["cognitive ability"]["rows"], 2)

    def test_without_targets_everything_is_beside_the_aim(self):
        result = coverage([_row(1, "", "IQ", 0.1)], {})
        self.assertFalse(result["has_targets"])
        self.assertEqual(result["off_target"], 1)

    def test_a_review_row_on_the_aim_is_not_counted_as_poolable(self):
        # On target, precise, and still not a study: the coverage line must not
        # promise a poolable row the pool will refuse.
        rows = [
            _row(1, "cognitive ability", "IQ", 0.10),
            dict(_row(2, "cognitive ability", "IQ", 0.10),
                 design="Network Meta-Analysis"),
        ]
        result = coverage(rows, TARGETS)
        self.assertEqual(result["on_target"], 2)
        self.assertEqual(result["on_target_poolable"], 1)


if __name__ == "__main__":
    unittest.main()
