"""Eine Doppellesung ist eine Pruefung, kein zweiter Effekt.

Zwei Lesungen derselben Textstelle tragen dieselbe Zahl mit demselben SE.
Beide poolbar zu lassen verdoppelt das Gewicht und macht das Intervall zu
schmal. Die Regel greift aber nur, wo die Zweitlesung wirklich eine gueltige
Erstlesung kopiert (Wert oder Quote): eine Zeile, die nur Pass B liest, ist
keine Doppelzaehlung und bleibt poolbar.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.meta.pooling import build_analysis, standardize


def _row(pass_no, **extra):
    row = {
        "effect_type": "smd", "effect": 0.4, "se": 0.1,
        "outcome": "cognition", "comparison": "vs placebo",
        "direction": "higher", "unit": "points", "population": "adults",
        "design": "rct", "quote_start": 0, "quote": "SMD 0.4 (0.2 to 0.6)",
        "study_id": "s1", "source_id": "src1",
        "extraction_pass": pass_no, "disputed": 0,
    }
    row.update(extra)
    return row


def _einzige_gruppe(analysis):
    return next(iter(analysis["groups"].values()))


class TestZwilling(unittest.TestCase):
    def test_zweite_lesung_ohne_zwilling_bleibt_poolbar(self):
        analysis = build_analysis([_row(2, outcome="sleep latency",
                                        quote="SOL -37.5 min")])
        self.assertEqual(_einzige_gruppe(analysis)["k"], 1)
        self.assertEqual(analysis["excluded"], [])

    def test_wert_zwilling_wird_verworfen(self):
        analysis = build_analysis([_row(1), _row(2)])
        self.assertEqual(_einzige_gruppe(analysis)["k"], 1)
        gruende = [e["reason"] for e in analysis["excluded"]]
        self.assertTrue(any("zweite Lesung" in g for g in gruende), gruende)

    def test_zitat_zwilling_wird_verworfen(self):
        # Gleiche Textstelle, anderer Wert: die Erstlesung traegt, die
        # Zweitlesung ist eine Pruefspur und keine zweite Studie.
        analysis = build_analysis([_row(1, effect=0.4, se=0.1),
                                   _row(2, effect=0.9, se=0.2)])
        group = _einzige_gruppe(analysis)
        self.assertEqual(group["k"], 1)
        self.assertAlmostEqual(group["rows"][0]["est"], 0.4)
        self.assertEqual(len(analysis["excluded"]), 1)

    def test_dritte_lesung_mit_zwilling_wird_verworfen(self):
        analysis = build_analysis([_row(1), _row(3)])
        self.assertEqual(_einzige_gruppe(analysis)["k"], 1)
        self.assertEqual(len(analysis["excluded"]), 1)

    def test_zwei_studien_bleiben_zwei(self):
        analysis = build_analysis([_row(1, study_id="s1", source_id="a",
                                        quote="A", effect=0.4),
                                   _row(1, study_id="s2", source_id="b",
                                        quote="B", effect=0.8)])
        self.assertEqual(_einzige_gruppe(analysis)["k"], 2)

    def test_standardize_kennt_keinen_passfilter(self):
        # Der Filter braucht Kontext (gibt es eine Erstlesung?) und sitzt
        # deshalb in build_analysis, nicht in der Zeilenpruefung.
        self.assertEqual(standardize(_row(2))[3], "")

    def test_zeile_ohne_passfeld_gilt_als_erstlesung(self):
        row = _row(1)
        row.pop("extraction_pass")
        self.assertEqual(standardize(row)[3], "")


class TestWiderspruch(unittest.TestCase):
    def test_widerlegte_erstlesung_ist_kein_zwilling(self):
        # Bestaetigte Zweitlesung: die Erstlesung bleibt strittig und draussen,
        # die Zweitlesung darf nicht als Kopie einer ungueltigen Zeile gelten.
        analysis = build_analysis([_row(1, disputed=1), _row(2, disputed=0)])
        self.assertEqual(_einzige_gruppe(analysis)["k"], 1)
        self.assertEqual(len(analysis["excluded"]), 1)
        self.assertIn("Doppel-Extraktion", analysis["excluded"][0]["reason"])

    def test_beide_strittig_ergeben_keinen_pool(self):
        analysis = build_analysis([_row(1, disputed=1), _row(2, disputed=1)])
        self.assertEqual(analysis["groups"], {})
        self.assertEqual(len(analysis["excluded"]), 2)


if __name__ == "__main__":
    unittest.main()
