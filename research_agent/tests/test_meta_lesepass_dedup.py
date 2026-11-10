"""Eine Doppel-Extraktion ist eine Pruefung, kein zweiter Effekt.

Zwei Lesungen derselben Textstelle tragen dieselbe Zahl mit demselben SE.
Beide poolbar zu lassen verdoppelt das Gewicht und macht das Intervall zu
schmal. Diese Tests halten die Gegenregel fest: nur die tragende Lesung geht
in den Pool, eine bestaetigte Zweitlesung wird vorher zur tragenden.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.meta.extraction import resolve_third_attempt
from research_agent.meta.pooling import build_analysis, standardize


def _row(pass_no, **extra):
    row = {
        "effect_type": "smd", "effect": 0.4, "se": 0.1,
        "outcome": "cognition", "comparison": "vs placebo",
        "direction": "higher", "unit": "points", "population": "adults",
        "design": "rct", "quote_start": 0, "quote": "SMD 0.4",
        "study_id": "s1", "source_id": "src1",
        "extraction_pass": pass_no, "disputed": 0,
    }
    row.update(extra)
    return row


class TestPoolFilter(unittest.TestCase):
    def test_zweite_lesung_ist_nicht_poolbar(self):
        _, _, _, reason = standardize(_row(2))
        self.assertIn("zweite Lesung", reason)

    def test_erstlesung_bleibt_poolbar(self):
        est, se, _, reason = standardize(_row(1))
        self.assertEqual(reason, "")
        self.assertAlmostEqual(est, 0.4)

    def test_zeile_ohne_passfeld_gilt_als_erstlesung(self):
        row = _row(1)
        row.pop("extraction_pass")
        self.assertEqual(standardize(row)[3], "")

    def test_dritte_lesung_ist_eine_klaerungshilfe(self):
        _, _, _, reason = standardize(_row(3))
        self.assertIn("zweite Lesung", reason)

    def test_doppellesung_erzeugt_keinen_zweiten_arm(self):
        analysis = build_analysis([_row(1), _row(2)])
        self.assertEqual(len(analysis["groups"]), 1)
        group = next(iter(analysis["groups"].values()))
        self.assertEqual(group["k"], 1)
        gruende = [e["reason"] for e in analysis["excluded"]]
        self.assertTrue(any("zweite Lesung" in g for g in gruende), gruende)

    def test_zwei_studien_bleiben_zwei(self):
        analysis = build_analysis([_row(1, study_id="s1", source_id="a"),
                                   _row(1, study_id="s2", source_id="b")])
        group = next(iter(analysis["groups"].values()))
        self.assertEqual(group["k"], 2)


class TestBestaetigteZweitlesung(unittest.TestCase):
    def _paar(self):
        first = _row(1, se=0.1, disputed=1)
        second = _row(2, se=0.2, disputed=1)
        return first, second

    def test_bestaetigte_zweitlesung_wird_zur_tragenden_lesung(self):
        first, second = self._paar()
        out = resolve_third_attempt([first], [second], [dict(second)])
        self.assertEqual(out["second_confirmed"], 1)
        self.assertEqual(second["disputed"], 0)
        self.assertEqual(second["extraction_pass"], 1)
        self.assertEqual(standardize(second)[3], "")
        self.assertIn("Doppel-Extraktion", standardize(first)[3])

    def test_bestaetigte_erstlesung_bleibt_allein(self):
        first, second = self._paar()
        out = resolve_third_attempt([first], [second], [dict(first)])
        self.assertEqual(out["first_confirmed"], 1)
        self.assertEqual(first["disputed"], 0)
        self.assertEqual(standardize(first)[3], "")
        self.assertIn("Doppel-Extraktion", standardize(second)[3])

    def test_ungeklaert_bleibt_beides_draussen(self):
        first, second = self._paar()
        out = resolve_third_attempt([first], [second],
                                    [_row(3, se=0.3, effect=0.9)])
        self.assertEqual(out["unresolved"], 1)
        self.assertIn("Doppel-Extraktion", standardize(first)[3])
        self.assertIn("Doppel-Extraktion", standardize(second)[3])


if __name__ == "__main__":
    unittest.main()
