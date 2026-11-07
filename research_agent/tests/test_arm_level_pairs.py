"""Tests fuer Arme aus getrennten Mittelwert- und Streuungsspalten.

Viele Tabellen schreiben je Arm zwei Spalten: ``Melatonin Mean`` und
``Melatonin SD``. Vorher verlangte der Arm-Rechner beides in einer Zelle und
verwarf solche Zeilen als "kein Mittelwert mit eindeutiger Streuung in zwei
Spalten" - das war der groesste Einzelposten der SOL-Ausbeute.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from research_agent.meta.arm_level import arms_from_row, convert_row

HEADER = ["Outcome", "Melatonin Mean", "Melatonin SD", "Placebo Mean",
          "Placebo SD", "Melatonin n", "Placebo n"]
CELLS = ["Sleep onset latency (min)", "38.2", "4.1", "45.1", "4.7", "60", "60"]


class SeparateColumnsTest(unittest.TestCase):
    def test_two_arms_from_mean_and_sd_columns(self):
        arms, reason = arms_from_row(HEADER, CELLS)
        self.assertEqual(reason, "", reason)
        self.assertEqual([round(a.mean, 1) for a in arms], [38.2, 45.1])
        self.assertEqual([round(a.sd, 1) for a in arms], [4.1, 4.7])
        self.assertEqual([a.n for a in arms], [60, 60])
        self.assertEqual([a.sd_source for a in arms], ["sd", "sd"])

    def test_row_becomes_a_hedges_g(self):
        result = convert_row(HEADER, CELLS, outcome="Sleep onset latency")
        self.assertTrue(result.get("ok"), result.get("reason"))
        self.assertEqual(result["effect_type"] if "effect_type" in result else "g", "g")
        self.assertLess(result["effect"], 0)   # 38.2 < 45.1

    def test_se_columns_are_converted_through_sqrt_n(self):
        header = ["Outcome", "Melatonin Mean", "Melatonin SE", "Placebo Mean",
                  "Placebo SE", "Melatonin n", "Placebo n"]
        cells = ["SOL", "38.2", "0.53", "45.1", "0.61", "60", "60"]
        arms, reason = arms_from_row(header, cells)
        self.assertEqual(reason, "", reason)
        self.assertEqual([a.sd_source for a in arms], ["se", "se"])
        self.assertAlmostEqual(arms[0].sd, 0.53 * 60 ** 0.5, places=6)

    def test_range_in_the_spread_column_is_not_paired(self):
        # "4.1 to 5.2" ist ein Intervall, keine Einzelstreuung.
        cells = ["SOL", "38.2", "4.1 to 5.2", "45.1", "4.7", "60", "60"]
        arms, reason = arms_from_row(HEADER, cells)
        self.assertEqual(arms, [])
        self.assertIn("Streuung", reason)

    def test_single_cell_arm_still_wins_over_pairing(self):
        header = ["Outcome", "Melatonin (mean ± SD)", "Placebo (mean ± SD)",
                  "Melatonin n", "Placebo n"]
        cells = ["SOL", "38.2 ± 4.1", "45.1 ± 4.7", "60", "60"]
        arms, reason = arms_from_row(header, cells)
        self.assertEqual(reason, "", reason)
        self.assertEqual(len(arms), 2)

    def test_without_n_the_pairing_is_refused(self):
        header = ["Outcome", "Melatonin Mean", "Melatonin SD", "Placebo Mean",
                  "Placebo SD"]
        cells = ["SOL", "38.2", "4.1", "45.1", "4.7"]
        arms, reason = arms_from_row(header, cells)
        self.assertEqual(arms, [])
        self.assertIn("Fallzahl", reason)


if __name__ == "__main__":
    unittest.main()
