"""Tests fuer den Fliesstext-Arm-Leser (meta/arm_text.py).

Erwartungswerte sind von Hand nach den Formeln in arm_level.py gerechnet.
Die Tests halten fest, was der Leser NICHT darf: raten, Baseline-Verlaeufe
als Gruppenvergleich lesen, SEM als SD ausgeben, ohne Fallzahl speichern.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.arm_text import (
    arm_mentions,
    convert_sentence,
    split_sentences,
    store_text_arm_effects,
    text_arm_candidates,
)


class TestSentences(unittest.TestCase):
    def test_splits_on_sentence_end(self):
        text = "First result. Second result! Third?"
        self.assertEqual([s for _a, _b, s in split_sentences(text)],
                         ["First result.", "Second result!", "Third?"])

    def test_abbreviation_is_not_a_boundary(self):
        text = "Latency was 18.3 min vs. 27.9 min in controls. That is it."
        parts = [s for _a, _b, s in split_sentences(text)]
        self.assertEqual(len(parts), 2)
        self.assertIn("vs. 27.9", parts[0])

    def test_decimal_point_is_not_a_boundary(self):
        parts = [s for _a, _b, s in split_sentences("SOL 18.3 +- 7.2 min. Done.")]
        self.assertEqual(len(parts), 2)


class TestMentions(unittest.TestCase):
    SENTENCE = ("Sleep onset latency was 18.3 +- 7.2 min in the melatonin group "
                "(n = 20) and 27.9 +- 8.1 min in the placebo group (n = 20).")

    def test_two_mentions_with_labels_and_n(self):
        mentions = arm_mentions(self.SENTENCE)
        self.assertEqual(len(mentions), 2)
        self.assertAlmostEqual(mentions[0].mean, 18.3)
        self.assertAlmostEqual(mentions[0].sd, 7.2)
        self.assertEqual(mentions[0].n, 20)
        self.assertIn("melatonin", mentions[0].label)
        self.assertIn("placebo", mentions[1].label)

    def test_decimal_comma(self):
        mentions = arm_mentions("Melatonin (n = 20) 18,3 \u00b1 7,2 min.")
        self.assertEqual(len(mentions), 1)
        self.assertAlmostEqual(mentions[0].mean, 18.3)

    def test_sd_in_parentheses(self):
        mentions = arm_mentions("Melatonin group (n = 12) 18.3 (SD 7.2) min.")
        self.assertEqual(len(mentions), 1)
        self.assertAlmostEqual(mentions[0].sd, 7.2)

    def test_same_number_twice_is_counted_once(self):
        # "18.3 +- 7.2" wird von beiden Mustern nicht doppelt gezaehlt.
        mentions = arm_mentions("SOL 18.3 +- 7.2 min (SD 7.2).")
        self.assertEqual(len(mentions), 1)


class TestGate(unittest.TestCase):
    SENTENCE = ("Sleep onset latency was 18.3 +- 7.2 min in the melatonin group "
                "(n = 20) and 27.9 +- 8.1 min in the placebo group (n = 20).")

    def test_valid_two_arm_sentence_converts(self):
        result = convert_sentence(self.SENTENCE)
        self.assertTrue(result["ok"], result.get("reason"))
        self.assertEqual(result["n"], 40)
        self.assertIn("sleep onset latency", result["outcome"].lower())

    def test_baseline_sentence_is_refused(self):
        sentence = ("Sleep onset latency decreased from 32.1 to 18.3 +- 7.2 min "
                    "in the melatonin group (n = 20) and from 31.5 to 27.9 +- 8.1 "
                    "min in the placebo group (n = 20).")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])
        self.assertIn("Baseline", result["reason"])

    def test_change_sentence_is_refused(self):
        sentence = ("The change in SOL was -13.8 +- 6.1 min with melatonin (n = 20) "
                    "and -3.6 +- 7.4 min with placebo (n = 20).")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])

    def test_sem_is_not_sd(self):
        sentence = ("SOL was 18.3 +- 1.6 min in melatonin (n = 20) and "
                    "27.9 +- 1.8 min in placebo (n = 20); values are mean SEM.")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])

    def test_missing_n_is_refused(self):
        sentence = ("SOL was 18.3 +- 7.2 min in the melatonin group and "
                    "27.9 +- 8.1 min in the placebo group.")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])
        self.assertIn("Fallzahl", result["reason"])

    def test_cross_sectional_groups_are_refused(self):
        sentence = ("Total sleep time was 404.2 +- 33.9 min in active children "
                    "(n = 174) and 397.3 +- 44.2 min in inactive children (n = 79).")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])
        self.assertIn("Interventionsarm", result["reason"])

    def test_single_arm_sentence_is_refused(self):
        result = convert_sentence("SOL was 18.3 +- 7.2 min in melatonin (n = 20).")
        self.assertFalse(result["ok"])

    def test_median_is_refused(self):
        sentence = ("SOL was 18.3 +- 7.2 min in melatonin (n = 20) and "
                    "27.9 +- 8.1 min in placebo (n = 20); data are median.")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])
        self.assertIn("Median", result["reason"])

    def test_text_candidates_helper_skips_table_rows(self):
        text = ("|18.3 +- 7.2|melatonin (n = 20)|27.9 +- 8.1|placebo (n = 20)|\n"
                "SOL was 18.3 +- 7.2 min in melatonin (n = 20) and 27.9 +- 8.1 "
                "min in placebo (n = 20).")
        candidates = text_arm_candidates(text)
        self.assertEqual(len(candidates), 1)
        self.assertNotIn("|", candidates[0]["quote"])


class TestStore(unittest.TestCase):
    TEXT = ("Results. Sleep onset latency was 18.3 +- 7.2 min in the melatonin "
            "group (n = 20) and 27.9 +- 8.1 min in the placebo group (n = 20).")

    def setUp(self):
        self.db = Database(":memory:")
        self.text_id = self.db.save_source_text("s1", self.TEXT, kind="xml")["id"]

    def test_verified_sentence_is_stored_with_own_extractor(self):
        candidates = text_arm_candidates(self.TEXT)
        stored, rejected = store_text_arm_effects(
            self.db, "s1", self.text_id, self.TEXT, candidates)
        self.assertEqual(rejected, [])
        self.assertEqual(len(stored), 1)
        rows = self.db.get_study_effects(source_id="s1")
        self.assertEqual(rows[0]["extractor"], "arm-text/1")
        self.assertEqual(rows[0]["effect_type"], "g")

    def test_quote_not_in_text_is_not_stored(self):
        candidates = text_arm_candidates(self.TEXT)
        candidates[0]["quote"] = "Sleep onset latency was 99.9 +- 1.0 min"
        stored, rejected = store_text_arm_effects(
            self.db, "s1", self.text_id, self.TEXT, candidates)
        self.assertEqual(stored, [])
        self.assertIn("Zitat", rejected[0]["reason"])


class TestArtifacts(unittest.TestCase):
    """Tabellenreste, Zitationen und Stichprobenbeschreibungen sind keine Arme."""

    def test_design_sentence_is_refused(self):
        sentence = ("103 healthy adults were randomized to one of four treatment "
                    "groups; age was 34.8 +- 9.6 years in the morning group (n = 25) "
                    "and 33.1 +- 8.4 years in the placebo group (n = 26).")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])
        self.assertIn("Designbeschreibung", result["reason"])

    def test_demographic_outcome_is_refused(self):
        sentence = ("Age was 48.3 +- 13.3 years in the treatment group (n = 22) "
                    "and 56.9 +- 12.9 years in the standard group (n = 11).")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])
        self.assertIn("demografische", result["reason"])

    def test_citation_column_is_refused(self):
        sentence = ("Daneshzad et al. reported 57.5 +- 5.0 in the DASH diet group "
                    "(n = 66) and 60.7 +- 6.3 in controls (n = 3941).")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])
        self.assertIn("Tabellen-/Zitationsrest", result["reason"])

    def test_flattened_table_line_is_skipped_entirely(self):
        text = ("Study|Group|n|Mean +- SD|Reference\n"
                "Sleep onset latency was 18.3 +- 7.2 min in the melatonin group "
                "(n = 20) and 27.9 +- 8.1 min in the placebo group (n = 20).\n")
        candidates = text_arm_candidates(text)
        self.assertEqual(len(candidates), 1)
        self.assertNotIn("|", candidates[0]["quote"])

    def test_label_does_not_carry_the_previous_arm(self):
        sentence = ("18.3 +- 7.2 min in the melatonin group (n = 20) and "
                    "27.9 +- 8.1 min in the placebo group (n = 20).")
        mentions = arm_mentions(sentence)
        self.assertEqual([m.label for m in mentions], ["melatonin group", "placebo group"])


if __name__ == "__main__":
    unittest.main()
