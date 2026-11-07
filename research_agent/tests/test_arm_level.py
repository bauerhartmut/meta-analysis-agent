"""Tests fuer den Arm-Deskriptiva-Umrechner (meta/arm_level.py).

Erwartungswerte sind von Hand nach den Formeln in Hedges & Olkin (1985)
gerechnet, nicht mit dem Modul selbst erzeugt.
"""

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.arm_level import (
    ArmStats,
    arms_from_row,
    cohens_d,
    convert_row,
    hedges_correction,
    parse_mean_spread,
    parse_number,
    sd_from_ci,
    sd_from_se,
    se_of_g,
    smd_from_arms,
    store_arm_level_effects,
)


class TestNumbers(unittest.TestCase):
    def test_decimal_comma_and_unicode_minus(self):
        self.assertAlmostEqual(parse_number("\u22120,42"), -0.42)
        self.assertAlmostEqual(parse_number("1,234.5"), 1234.5)
        self.assertAlmostEqual(parse_number("391.8"), 391.8)

    def test_p_value_bounds_are_not_measurements(self):
        self.assertIsNone(parse_number("<.001"))
        self.assertIsNone(parse_number("> 3"))

    def test_sd_from_se(self):
        # SE 1.0 bei n=25 -> SD = 1.0 * sqrt(25) = 5.0
        self.assertAlmostEqual(sd_from_se(1.0, 25), 5.0)
        self.assertIsNone(sd_from_se(0, 25))
        self.assertIsNone(sd_from_se(1.0, 1))

    def test_sd_from_ci(self):
        # 95 %-CI 11.6 bis 22.0, z=1.959964, n=100
        # SE = 10.4 / 3.919928 = 2.653126; SD = SE * 10 = 26.53126
        self.assertAlmostEqual(sd_from_ci(11.6, 22.0, 100), 26.5313, places=3)


class TestSpread(unittest.TestCase):
    def test_plus_minus_is_sd(self):
        self.assertEqual(parse_mean_spread("15.6 \u00b1 16.0"),
                         (15.6, 16.0, "sd"))

    def test_labeled_se(self):
        self.assertEqual(parse_mean_spread("7.21 (SE 1.13)"),
                         (7.21, 1.13, "se"))

    def test_parenthesised_range_is_ci(self):
        result = parse_mean_spread("16.7 (11.6 to 22.0)")
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0], 16.7)
        self.assertEqual(result[2], "ci")

    def test_bare_number_in_parentheses_is_ambiguous(self):
        # (11.6) kann SD, SE, IQR oder Messfehler sein - kein Raten.
        self.assertIsNone(parse_mean_spread("16.7 (11.6)"))

    def test_header_role_resolves_bare_number(self):
        self.assertEqual(parse_mean_spread("16.7 (11.6)", role="sd"),
                         (16.7, 11.6, "sd"))


class TestFormulas(unittest.TestCase):
    def test_cohens_d_symmetric_spread(self):
        # m1=10, m2=12, SD 2/2, n 20/20 -> d = -1.0
        self.assertAlmostEqual(cohens_d(10, 2, 20, 12, 2, 20), -1.0)

    def test_hedges_correction_matches_hand_value(self):
        # J = 1 - 3/(4*40 - 9) = 1 - 3/151 = 0.9801325
        self.assertAlmostEqual(hedges_correction(20, 20), 0.980132, places=6)

    def test_se_of_g_hand_value(self):
        # g = -0.980132, n1+n2 = 40
        # SE = sqrt(40/400 + 0.960659/80) = sqrt(0.1120082) = 0.334676
        g = -1.0 * 0.9801324503311258
        self.assertAlmostEqual(se_of_g(g, 20, 20), 0.334676, places=6)

    def test_smd_from_arms_composes_correctly(self):
        a1 = ArmStats(label="Melatonin", n=20, mean=10.0, sd=2.0)
        a2 = ArmStats(label="Placebo", n=20, mean=12.0, sd=2.0)
        effect = smd_from_arms(a1, a2)
        self.assertIsNotNone(effect)
        self.assertAlmostEqual(effect.effect, -0.980132, places=6)
        self.assertAlmostEqual(effect.se, 0.334676, places=6)
        self.assertEqual(effect.n_total, 40)

    def test_incomplete_arm_gives_nothing(self):
        a1 = ArmStats(label="A", n=20, mean=10.0, sd=2.0)
        a2 = ArmStats(label="B", n=20, mean=12.0, sd=0.0)
        self.assertIsNone(smd_from_arms(a1, a2))

    def test_small_n_is_refused(self):
        self.assertIsNone(cohens_d(10, 2, 1, 12, 2, 20))


class TestRows(unittest.TestCase):
    def test_row_with_n_columns_converts(self):
        header = ["Outcome", "n", "Melatonin mean (SD)", "Placebo mean (SD)", "n"]
        cells = ["Sleep onset", "20", "10.0 (2.0)", "12.0 (2.0)", "20"]
        arms, reason = arms_from_row(header, cells)
        self.assertEqual(reason, "", reason)
        self.assertEqual([a.n for a in arms], [20, 20])
        self.assertEqual([a.mean for a in arms], [10.0, 12.0])

    def test_single_total_n_is_not_enough(self):
        header = ["Characteristic", "N", "Melatonin % (95% CI)", "Placebo % (95% CI)"]
        cells = ["Stage REM", "342", "16.7 (11.6 to 22.0)", "19.0 (14.6 to 23.2)"]
        arms, reason = arms_from_row(header, cells)
        self.assertEqual(arms, [])
        self.assertIn("Fallzahl", reason)

    def test_median_with_iqr_is_not_converted(self):
        # Median/IQR sind keine Mittelwertdifferenz; die SMD-Formel gilt dafuer nicht.
        header = ["Outcome", "No. of pairs", "Median (IQR)", "Median (IQR)"]
        cells = ["Stage REM", "342", "16.7 (11.6 to 22.0)", "19.0 (14.6 to 23.2)"]
        arms, reason = arms_from_row(header, cells)
        self.assertEqual(arms, [])
        self.assertIn("Median", reason)

    def test_direct_ratio_column_is_not_an_arm(self):
        header = ["Outcome", "OR (95% CI)", "P value"]
        cells = ["Short sleep duration", "2.78 (1.80-4.30)", "<.001"]
        arms, reason = arms_from_row(header, cells)
        self.assertEqual(arms, [])
        self.assertIn("OR/RR/HR", reason)

    def test_more_than_two_arms_is_refused(self):
        # Acht Wertspalten (Gruppen oder Zeitpunkte) sind kein Zwei-Arm-Vergleich.
        header = ["Analyte"] + [f"Group {i}" for i in range(1, 5)]
        cells = ["Melatonin"] + [f"{i}.0 ± 2.0" for i in range(1, 5)]
        arms, reason = arms_from_row(header, cells)
        self.assertEqual(arms, [])
        self.assertIn("genau zwei", reason)

    def test_convert_row_keeps_quote(self):
        header = ["Group", "n", "Mean (SD)", "n", "Mean (SD)"]
        cells = ["x", "20", "10.0 (2.0)", "20", "12.0 (2.0)"]
        result = convert_row(header, cells, outcome="Latency",
                             quote="|x|20|10.0 (2.0)|20|12.0 (2.0)")
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["outcome"], "Latency")
        self.assertEqual(result["n"], 40)


class TestStoreGate(unittest.TestCase):
    TEXT = ("Results\nArm-level table follows.\n"
            "|Melatonin|20|10.0 (2.0)|Placebo|20|12.0 (2.0)|\n")

    def setUp(self):
        self.db = Database(":memory:")
        self.text_id = self.db.save_source_text(
            "s1", self.TEXT, kind="xml")["id"]

    def _candidate(self, quote):
        header = ["Arm", "n", "Mean (SD)", "Arm", "n", "Mean (SD)"]
        cells = quote.strip("|").split("|")
        return convert_row(header, cells, outcome="Sleep onset", quote=quote)

    def test_verified_quote_is_stored(self):
        quote = "|Melatonin|20|10.0 (2.0)|Placebo|20|12.0 (2.0)|"
        stored, rejected = store_arm_level_effects(
            self.db, "s1", self.text_id, self.TEXT, [self._candidate(quote)])
        self.assertEqual(rejected, [])
        self.assertEqual(len(stored), 1)
        rows = self.db.get_study_effects(source_id="s1")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["effect_type"], "g")
        self.assertAlmostEqual(rows[0]["effect"], -0.980132, places=6)
        self.assertGreaterEqual(rows[0]["quote_start"], 0)
        self.assertEqual(rows[0]["extractor"], "arm-level/1")

    def test_unverifiable_quote_is_not_stored(self):
        quote = "|Melatonin|20|99.0 (9.9)|Placebo|20|98.0 (9.9)|"
        stored, rejected = store_arm_level_effects(
            self.db, "s1", self.text_id, self.TEXT, [self._candidate(quote)])
        self.assertEqual(stored, [])
        self.assertEqual(len(rejected), 1)
        self.assertIn("Zitat", rejected[0]["reason"])
        self.assertEqual(self.db.get_study_effects(source_id="s1"), [])

    def test_incomplete_candidate_is_reported_not_stored(self):
        header = ["Arm", "n", "Mean (SD)"]
        cells = ["Melatonin", "20", "10.0 (2.0)"]
        candidate = convert_row(header, cells, outcome="x", quote="|Melatonin|20|10.0 (2.0)|")
        stored, rejected = store_arm_level_effects(
            self.db, "s1", self.text_id, self.TEXT, [candidate])
        self.assertEqual(stored, [])
        self.assertEqual(len(rejected), 1)
        self.assertFalse(candidate["ok"])


if __name__ == "__main__":
    unittest.main()


class TestDesignGate(unittest.TestCase):
    """Baseline-Zeilen und Querschnittsgruppen sind keine Behandlungseffekte."""

    HEADER = ["Outcome", "Day", "Intervention (n = 30) Mean ± SD",
              "Control (n = 30) Mean ± SD", "Welch's t", "p Value"]
    ROW = ["Total sleep time (min)", "0", "322.07 ± 15.28", "334.57 ± 20.12",
           "-2.710", ".009"]

    def test_baseline_day_zero_is_refused(self):
        result = convert_row(self.HEADER, self.ROW, quote="row")
        self.assertFalse(result["ok"])
        self.assertIn("Baseline", result["reason"])

    def test_follow_up_day_is_kept_with_its_time_point(self):
        row = list(self.ROW)
        row[1] = "30"
        result = convert_row(self.HEADER, row, quote="row")
        self.assertTrue(result["ok"], result.get("reason"))
        self.assertEqual(result["time_point"], "day 30")

    def test_baseline_in_row_label_is_refused(self):
        header = ["Outcome", "Intervention (n = 30) Mean ± SD",
                  "Control (n = 30) Mean ± SD"]
        cells = ["Baseline", "322.07 ± 15.28", "334.57 ± 20.12"]
        result = convert_row(header, cells, quote="row")
        self.assertFalse(result["ok"])
        self.assertIn("Baseline", result["reason"])

    def test_cross_sectional_groups_are_refused(self):
        header = ["", "Active children (n = 174) M ± SD",
                  "Inactive children (n = 79) M ± SD", "F", "p", "η2"]
        cells = ["Total sleep time (mins)", "404.17 ± 33.91", "397.32 ± 44.20",
                 "0.805", "0.370", "0.003"]
        result = convert_row(header, cells, quote="row")
        self.assertFalse(result["ok"])
        self.assertIn("Interventionsarm", result["reason"])

    def test_generic_arm_labels_are_not_rejected(self):
        # "Mean (SD)" benennt keine Gruppe - es gibt nichts zu klassifizieren.
        header = ["Group", "n", "Mean (SD)", "n", "Mean (SD)"]
        cells = ["x", "20", "10.0 (2.0)", "20", "12.0 (2.0)"]
        result = convert_row(header, cells, outcome="Latency", quote="row")
        self.assertTrue(result["ok"], result.get("reason"))
