"""Tests fuer den Leser direkter Effektspalten (meta/effect_columns.py)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.effect_columns import (
    effects_from_row,
    header_effect_kind,
    parse_effect_cell,
    store_direct_effects,
)


class TestHeader(unittest.TestCase):
    def test_hedges_g_with_ci(self):
        self.assertEqual(header_effect_kind("Hedges g (95% CI)")[:2], ("g", 0.95))

    def test_odds_ratio_with_ci(self):
        self.assertEqual(header_effect_kind("OR (95% CI)")[:2], ("or", 0.95))

    def test_adjusted_is_flagged(self):
        kind, level, adjusted = header_effect_kind("Adjusted OR (95% CI)")
        self.assertEqual((kind, level, adjusted), ("or", 0.95, True))

    def test_risk_and_hazard_ratio(self):
        self.assertEqual(header_effect_kind("RR (95% CI)")[0], "rr")
        self.assertEqual(header_effect_kind("HR (95% CI)")[0], "hr")

    def test_other_confidence_level(self):
        self.assertEqual(header_effect_kind("OR (90% CI)")[1], 0.90)

    def test_column_without_ci_is_not_an_effect_column(self):
        # ohne Intervall kein Standardfehler -> nicht poolbar
        self.assertEqual(header_effect_kind("Hedges g")[0], "")

    def test_mean_difference_with_ci(self):
        self.assertEqual(header_effect_kind("Mean difference (95% CI)")[:2],
                         ("mean_diff", 0.95))
        self.assertEqual(header_effect_kind("Difference in means (95% CI)")[0],
                         "mean_diff")
        self.assertEqual(header_effect_kind("MD (95% CI)")[0], "mean_diff")
        self.assertEqual(header_effect_kind("Difference (95% CI)")[0],
                         "mean_diff")

    def test_adjusted_mean_difference_is_flagged(self):
        kind, _, adjusted = header_effect_kind("Adjusted mean difference (95% CI)")
        self.assertEqual((kind, adjusted), ("mean_diff", True))

    def test_standardized_mean_difference_stays_smd(self):
        # "standardized mean difference" enthaelt "mean difference", ist aber
        # eine standardisierte Skala und darf nicht roh gepoolt werden.
        self.assertEqual(header_effect_kind("Standardized mean difference (95% CI)")[0],
                         "smd")

    def test_baseline_difference_is_not_a_treatment_effect(self):
        self.assertEqual(header_effect_kind("Baseline difference (95% CI)")[0], "")

    def test_mean_without_difference_is_not_an_effect(self):
        self.assertEqual(header_effect_kind("Mean (SD)")[0], "")
        self.assertEqual(header_effect_kind("Mean difference")[0], "")

    def test_p_value_and_median_are_not_effects(self):
        self.assertEqual(header_effect_kind("P value")[0], "")
        self.assertEqual(header_effect_kind("Median (IQR)")[0], "")
        self.assertEqual(header_effect_kind("No. of pairs")[0], "")


class TestCell(unittest.TestCase):
    def test_round_brackets_with_to(self):
        self.assertEqual(parse_effect_cell("-0.22 (-0.32 to -0.17)"),
                         (-0.22, -0.32, -0.17))

    def test_unicode_minus_and_en_dash(self):
        # Unicode-Minus und Gedankenstrich duerfen das Intervall nicht zerstoeren.
        self.assertEqual(parse_effect_cell("\u22120.22 (\u22120.32 \u2013 \u22120.17)"),
                         (-0.22, -0.32, -0.17))
        self.assertEqual(parse_effect_cell("2.78 (1.80\u20134.30)"),
                         (2.78, 1.80, 4.30))

    def test_comma_range(self):
        self.assertEqual(parse_effect_cell("1.38 (0.91, 2.11)"),
                         (1.38, 0.91, 2.11))

    def test_point_outside_interval_is_refused(self):
        self.assertIsNone(parse_effect_cell("5.0 (1.0-2.0)"))

    def test_point_without_interval_is_refused(self):
        self.assertIsNone(parse_effect_cell("0.42"))

    def test_p_value_is_not_a_measurement(self):
        self.assertIsNone(parse_effect_cell("<.001 (<.001 to .01)"))


class TestRows(unittest.TestCase):
    HEADER = ["Outcome", "OR (95% CI)", "P value", "Adjusted OR (95% CI)", "P value"]

    def test_two_effect_columns_in_one_row(self):
        cells = ["Short sleep duration", "2.78 (1.80\u20134.30)", "<.001",
                 "2.37 (1.50\u20133.76)", "<.001"]
        found, reason = effects_from_row(self.HEADER, cells, quote="row")
        self.assertEqual(reason, "", reason)
        self.assertEqual(len(found), 2)
        self.assertEqual([e["effect"] for e in found], [2.78, 2.37])
        self.assertEqual([e["adjusted"] for e in found], [0, 1])
        self.assertEqual({e["effect_type"] for e in found}, {"or"})

    def test_header_cell_count_mismatch_is_refused(self):
        # Zusammengefasste Kopfzellen (colspan) verschieben jede Zahl.
        header = ["Outcome", "No. of pairs", "Median (IQR)", "Hedges g (95% CI)",
                  "P value"]
        cells = ["Stage REM", "342", "16.7 (11.6 to 22.0)",
                 "19.0 (14.6 to 23.2)", "-0.22 (-0.32 to -0.17)", "<.001", ".003"]
        found, reason = effects_from_row(header, cells, quote="row")
        self.assertEqual(found, [])
        self.assertIn("passt nicht", reason)

    def test_row_without_effect_column(self):
        found, reason = effects_from_row(
            ["Outcome", "Mean (SD)", "Median (IQR)"],
            ["x", "10.0 (2.0)", "9.0 (8.0 to 10.0)"], quote="row")
        self.assertEqual(found, [])
        self.assertIn("keine Effektspalte", reason)

    def test_effect_column_without_readable_interval(self):
        found, reason = effects_from_row(
            ["Outcome", "OR (95% CI)"], ["x", "2.78"], quote="row")
        self.assertEqual(found, [])
        self.assertIn("Intervall", reason)


class TestMeanDiffStore(unittest.TestCase):
    TEXT = ("Results\n|Sleep onset latency|-12.4 (-18.9\u2013-5.9)|<.001|\n")
    HEADER = ["Outcome", "Mean difference (95% CI)", "P value"]
    CELLS = ["Sleep onset latency", "-12.4 (-18.9\u2013-5.9)", "<.001"]

    def test_negative_mean_difference_is_stored_on_raw_scale(self):
        db = Database(":memory:")
        text_id = db.save_source_text("s1", self.TEXT, kind="xml")["id"]
        quote = "|Sleep onset latency|-12.4 (-18.9\u2013-5.9)|<.001|"
        found, reason = effects_from_row(self.HEADER, self.CELLS, quote=quote)
        self.assertEqual(reason, "", reason)
        self.assertEqual(found[0]["effect_type"], "mean_diff")
        stored, rejected = store_direct_effects(db, "s1", text_id, self.TEXT, found)
        self.assertEqual(rejected, [])
        row = stored[0]
        self.assertAlmostEqual(row["effect"], -12.4)
        self.assertAlmostEqual(row["se"], (18.9 - 5.9) / 3.919928, places=6)
        self.assertEqual(row["unit"], "Mitteldifferenz (Rohskala)")
        self.assertTrue(row["direction"])
        self.assertEqual(row["n"], None)


class TestStore(unittest.TestCase):
    TEXT = ("Results\n|Short sleep duration|2.78 (1.80\u20134.30)|<.001|"
            "2.37 (1.50\u20133.76)|<.001|\n")
    HEADER = ["Outcome", "OR (95% CI)", "P value", "Adjusted OR (95% CI)", "P value"]
    CELLS = ["Short sleep duration", "2.78 (1.80\u20134.30)", "<.001",
             "2.37 (1.50\u20133.76)", "<.001"]

    def setUp(self):
        self.db = Database(":memory:")
        self.text_id = self.db.save_source_text("s1", self.TEXT, kind="xml")["id"]

    def _candidates(self, quote):
        found, reason = effects_from_row(self.HEADER, self.CELLS, quote=quote)
        self.assertEqual(reason, "", reason)
        return found

    def test_verified_quote_is_stored_with_derived_se(self):
        quote = "|Short sleep duration|2.78 (1.80\u20134.30)|<.001|2.37 (1.50\u20133.76)|<.001|"
        stored, rejected = store_direct_effects(
            self.db, "s1", self.text_id, self.TEXT, self._candidates(quote))
        self.assertEqual(rejected, [])
        self.assertEqual(len(stored), 2)
        rows = self.db.get_study_effects(source_id="s1")
        crude = [r for r in rows if r["adjusted"] == 0][0]
        adjusted = [r for r in rows if r["adjusted"] == 1][0]
        self.assertAlmostEqual(crude["effect"], 2.78)
        self.assertAlmostEqual(adjusted["effect"], 2.37)
        # SE = (hi - lo) / (2 * 1.959964)
        self.assertAlmostEqual(crude["se"], (4.30 - 1.80) / 3.919928, places=6)
        self.assertGreaterEqual(crude["quote_start"], 0)
        self.assertEqual(crude["extractor"], "effect-column/1")

    def test_unverifiable_quote_is_not_stored(self):
        quote = "|Short sleep duration|9.99 (1.00\u20132.00)|<.001|9.99 (1.00\u20132.00)|<.001|"
        stored, rejected = store_direct_effects(
            self.db, "s1", self.text_id, self.TEXT,
            [dict(e, quote=quote) for e in self._candidates(
                "|Short sleep duration|2.78 (1.80\u20134.30)|<.001|2.37 (1.50\u20133.76)|<.001|")])
        self.assertEqual(stored, [])
        self.assertTrue(rejected)
        self.assertEqual(self.db.get_study_effects(source_id="s1"), [])

    def test_negative_odds_ratio_is_rejected_by_plausibility(self):
        bad = {
            "effect_type": "or", "effect": -2.0, "ci_low": -2.5, "ci_high": -1.5,
            "ci_level": 0.95, "adjusted": 0, "quote": self.TEXT.splitlines()[1],
            "outcome": "x", "comparison": "OR (95% CI)", "ok": True,
        }
        stored, rejected = store_direct_effects(
            self.db, "s1", self.text_id, self.TEXT, [bad])
        self.assertEqual(stored, [])
        self.assertEqual(len(rejected), 1)
        self.assertIn("positiv", rejected[0]["reason"])


if __name__ == "__main__":
    unittest.main()
