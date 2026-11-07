"""Tests fuer den Veraenderungswert-Leser (meta/arm_change.py).

Die Erwartungswerte sind von Hand nach den Formeln gerechnet. Wichtigster
Punkt: bei gemeldeter Veraenderung darf rho das Ergebnis nicht veraendern,
bei prae/post muss es das - und genau das wird geprueft.
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.arm_change import (
    DEFAULT_RHO,
    RHO_GRID,
    ChangeArm,
    change_candidates,
    convert_sentence,
    sensitivity,
    smd_of_change,
    store_change_effects,
)


class TestChangeArm(unittest.TestCase):
    def test_reported_change_ignores_rho(self):
        arm = ChangeArm(label="melatonin", n=20, delta=-13.8, sd_reported=6.1)
        for rho in RHO_GRID:
            self.assertAlmostEqual(arm.sd_change(rho), 6.1)

    def test_prepost_sd_depends_on_rho(self):
        arm = ChangeArm(label="melatonin", n=20, delta=-13.8,
                        pre_sd=9.4, post_sd=7.2)
        # rho = 0: sqrt(88.36 + 51.84) = sqrt(140.2)
        self.assertAlmostEqual(arm.sd_change(0.0), math.sqrt(140.2), places=6)
        # rho = 0.5: sqrt(140.2 - 9.4*7.2) = sqrt(72.52)
        self.assertAlmostEqual(arm.sd_change(0.5), math.sqrt(72.52), places=6)
        self.assertLess(arm.sd_change(0.5), arm.sd_change(0.0))

    def test_reported_effect_is_exact(self):
        a1 = ChangeArm(label="melatonin", n=20, delta=-13.8, sd_reported=6.1)
        a2 = ChangeArm(label="placebo", n=20, delta=-3.6, sd_reported=7.4)
        result = smd_of_change(a1, a2)
        # d = -10.2 / sqrt((19*37.21 + 19*54.76)/38) = -10.2 / sqrt(45.985)
        pooled = math.sqrt((19 * 6.1 ** 2 + 19 * 7.4 ** 2) / 38)
        self.assertAlmostEqual(result["d"], -10.2 / pooled, places=6)

    def test_sensitivity_brackets_primary(self):
        a1 = ChangeArm(label="melatonin", n=20, delta=-13.8, pre_sd=9.4, post_sd=7.2)
        a2 = ChangeArm(label="placebo", n=20, delta=-3.6, pre_sd=8.8, post_sd=8.1)
        rows = sensitivity(a1, a2)
        self.assertEqual([row["rho"] for row in rows], list(RHO_GRID))
        values = [row["g"] for row in rows]
        # Groesseres rho -> kleinere Change-SD -> groesserer Betrag von g
        # (g ist hier negativ, die Werte werden also kleiner).
        magnitudes = [abs(value) for value in values]
        self.assertEqual(magnitudes, sorted(magnitudes))
        primary = smd_of_change(a1, a2, DEFAULT_RHO)["g"]
        self.assertAlmostEqual(values[RHO_GRID.index(DEFAULT_RHO)], primary, places=6)


class TestSentences(unittest.TestCase):
    PREPOST = ("Sleep onset latency decreased from 32.1 +- 9.4 to 18.3 +- 7.2 "
               "min in the melatonin group (n = 20) and from 31.5 +- 8.8 to "
               "27.9 +- 8.1 min in the placebo group (n = 20).")
    REPORTED = ("The change in SOL was -13.8 +- 6.1 min with melatonin "
                "(n = 20) and -3.6 +- 7.4 min with placebo (n = 20).")

    def test_prepost_sentence_converts_with_grid(self):
        result = convert_sentence(self.PREPOST)
        self.assertTrue(result["ok"], result.get("reason"))
        self.assertEqual(result["moderators"]["change_model"], "prepost")
        self.assertEqual(len(result["moderators"]["sensitivity"]), len(RHO_GRID))
        self.assertAlmostEqual(result["n"], 40)

    def test_reported_sentence_has_no_grid(self):
        result = convert_sentence(self.REPORTED)
        self.assertTrue(result["ok"], result.get("reason"))
        self.assertEqual(result["moderators"]["change_model"], "reported")
        self.assertEqual(result["moderators"]["sensitivity"], [])

    def test_decrease_makes_change_negative(self):
        arm = convert_sentence("SOL decreased by 13.8 +- 6.1 min with melatonin "
                               "(n = 20) and by 3.6 +- 7.4 min with placebo (n = 20).")
        # Ohne Vorzeichen im Satz: "decreased" macht die Veraenderung negativ.
        self.assertTrue(arm["ok"], arm.get("reason"))
        self.assertLess(arm["arms"][0]["mean"], 0)

    def test_missing_n_is_refused(self):
        sentence = ("SOL decreased from 32.1 +- 9.4 to 18.3 +- 7.2 min in the "
                    "melatonin group and from 31.5 +- 8.8 to 27.9 +- 8.1 min in "
                    "the placebo group.")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])
        self.assertIn("Fallzahl", result["reason"])

    def test_single_arm_is_refused(self):
        result = convert_sentence(
            "SOL decreased from 32.1 +- 9.4 to 18.3 +- 7.2 min in melatonin (n = 20).")
        self.assertFalse(result["ok"])

    def test_median_is_refused(self):
        sentence = ("SOL decreased from 32.1 +- 9.4 to 18.3 +- 7.2 min in "
                    "melatonin (n = 20) and from 31.5 +- 8.8 to 27.9 +- 8.1 in "
                    "placebo (n = 20); values are median.")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])
        self.assertIn("Median", result["reason"])

    def test_demographic_outcome_is_refused(self):
        sentence = ("Age decreased from 48.3 +- 13.3 to 47.9 +- 12.9 years in "
                    "the melatonin group (n = 22) and from 56.9 +- 12.9 to "
                    "56.4 +- 12.4 years in the standard group (n = 11).")
        result = convert_sentence(sentence)
        self.assertFalse(result["ok"])
        self.assertIn("demografische", result["reason"])

    def test_table_row_is_skipped(self):
        text = ("Study|Group|n|Change|SD\n"
                + self.REPORTED + "\n")
        candidates = change_candidates(text)
        self.assertEqual(len(candidates), 1)
        self.assertNotIn("|", candidates[0]["quote"])


class TestStore(unittest.TestCase):
    TEXT = ("Results. The change in SOL was -13.8 +- 6.1 min with melatonin "
            "(n = 20) and -3.6 +- 7.4 min with placebo (n = 20).")

    def setUp(self):
        self.db = Database(":memory:")
        self.text_id = self.db.save_source_text("s1", self.TEXT, kind="xml")["id"]

    def test_stored_with_change_extractor_and_rho(self):
        candidates = change_candidates(self.TEXT)
        stored, rejected = store_change_effects(
            self.db, "s1", self.text_id, self.TEXT, candidates)
        self.assertEqual(rejected, [])
        self.assertEqual(len(stored), 1)
        rows = self.db.get_study_effects(source_id="s1")
        self.assertEqual(rows[0]["extractor"], "arm-change/1")
        import json
        moderators = json.loads(rows[0]["moderators"])
        self.assertEqual(moderators["change_model"], "reported")
        self.assertIsNone(moderators["rho"])

    def test_unverifiable_quote_is_not_stored(self):
        candidates = change_candidates(self.TEXT)
        candidates[0]["quote"] = "The change in SOL was -99.9 +- 1.0 min"
        stored, rejected = store_change_effects(
            self.db, "s1", self.text_id, self.TEXT, candidates)
        self.assertEqual(stored, [])
        self.assertIn("Zitat", rejected[0]["reason"])


if __name__ == "__main__":
    unittest.main()
