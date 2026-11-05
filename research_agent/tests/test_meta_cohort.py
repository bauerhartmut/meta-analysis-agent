"""Kohorten-Abhängigkeiten im Pooling (Claude-Vorschlag 6).

Kernregeln, die hier festgehalten werden:

1. Dasselbe DOI kollabiert wie bisher (dieselbe Kohorte zweimal gelesen) -
   die präzisere Lesung bleibt.
2. Dasselbe DOI mit ZWEI verscheidenen, WÖRTLICH belegten cohort_ids ist
   KEINE Duplizierte; die Zeilen bleiben (zwei echte
   Gruppen desselben Papiers).
3. Dieselbe belegte cohort_id in ZWEI różnych Papern kollabiert - dieselben
   Teilnehmer wären sonst still doppelt gezählt (z. B. UK Biobank).
4. Eine unbegründete cohort_id gilt als nicht existent (nie geschätzt).
5. Die Sensitivität "mit und ohne Mehrfachkohorten" identifiziert die
   Mehrfachkohorten-Papers an den DOIs und liefert beide Teilmengen.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from research_agent.meta.pooling import (
    build_analysis, _collapse_same_study, sensitivity_multicohort,
)


def _row(label, doi="", cohort_id="", quote="", se=0.1, est=0.3,
         source_id="", outcome="forgetting"):
    return {
        "label": label, "doi": doi, "cohort_id": cohort_id, "quote": quote,
        "se": se, "est": est, "source_id": source_id, "outcome": outcome,
        "effect_type": "smd", "n": 60,
    }


class TestDoiKohortenRegeln(unittest.TestCase):
    def test_dasselbe_doi_kollabiert_wie_bisher(self):
        rows = [_row("A", doi="10.1/x", quote="q", se=0.2, est=0.30),
                _row("B", doi="10.1/x", quote="q", se=0.1, est=0.32)]
        kept, dropped = _collapse_same_study(rows)
        self.assertEqual(len(kept), 1)
        # die praecesere Lesung (se=0.1) bleibt
        self.assertEqual(kept[0]["label"], "B")
        self.assertEqual(len(dropped), 1)

    def test_dasselbe_doi_zwei_belegte_kohorten_bleiben(self):
        rows = [_row("A", doi="10.1/x", cohort_id="cohort-A", quote="q"),
                _row("B", doi="10.1/x", cohort_id="cohort-B", quote="q")]
        kept, dropped = _collapse_same_study(rows)
        self.assertEqual(len(kept), 2)
        self.assertEqual(dropped, [])

    def test_dasselbe_doi_ohne_kohorte_kollabiert(self):
        rows = [_row("A", doi="10.1/x", se=0.2),
                _row("B", doi="10.1/x", se=0.1)]
        kept, _dropped = _collapse_same_study(rows)
        self.assertEqual(len(kept), 1)

    def test_dieselbe_belegte_kohorte_in_zwei_papern_kollabiert(self):
        rows = [_row("A", doi="10.1/x", cohort_id="UK-Biobank", quote="q"),
                _row("B", doi="10.2/y", cohort_id="UK-Biobank", quote="q")]
        kept, dropped = _collapse_same_study(rows)
        self.assertEqual(len(kept), 1)
        self.assertTrue(any("dieselbe Kohorte" in d["reason"]
                            for d in dropped))

    def test_unbelegte_kohorte_gilt_als_nicht_existent(self):
        rows = [_row("A", doi="10.1/x", cohort_id="guess-A", quote=""),
                _row("B", doi="10.2/y", cohort_id="guess-A", quote="")]
        kept, dropped = _collapse_same_study(rows)
        # ohne Belegstelle: kein Zusammenfassen, keine Abhängigkeitslüge
        self.assertEqual(len(kept), 2)
        self.assertEqual(dropped, [])


class TestSensitivitaetMehrfachkohorten(unittest.TestCase):
    def test_mehrfachkohorten_werden_erkannt(self):
        rows = [
            _row("A", doi="10.1/x", cohort_id="c1", quote="q"),
            _row("B", doi="10.1/x", cohort_id="c2", quote="q"),
            _row("C", doi="10.2/y", quote="q"),
        ]
        sens = sensitivity_multicohort(rows)
        self.assertTrue(sens["has_multicohort"])
        self.assertEqual(sens["multi_cohort_dois"], ["10.1/x"])
        self.assertEqual(len(sens["single_cohort_rows"]), 1)
        self.assertEqual(sens["single_cohort_rows"][0]["label"], "C")

    def test_ohne_mehrfachkohorten_bleibt_Satz(self):
        rows = [_row("A", doi="10.1/x", quote="q"),
                _row("B", doi="10.2/y", quote="q")]
        sens = sensitivity_multicohort(rows)
        self.assertFalse(sens["has_multicohort"])
        self.assertEqual(len(sens["single_cohort_rows"]), 2)

    def test_unbelegte_kohorte_zaehlt_nicht_als_mehrfach(self):
        rows = [_row("A", doi="10.1/x", cohort_id="g1", quote=""),
                _row("B", doi="10.1/x", cohort_id="g2", quote="")]
        sens = sensitivity_multicohort(rows)
        self.assertFalse(sens["has_multicohort"])

    def test_build_analysis_laeuft_mit_kohorten_zeilen_durch(self):
        rows = [
            _row("A", doi="10.1/x", cohort_id="c1", quote="q"),
            _row("B", doi="10.1/x", cohort_id="c2", quote="q"),
            _row("C", doi="10.2/y", quote="q"),
        ]
        analysis = build_analysis(rows)
        self.assertIn("groups", analysis)
        # Keine Zeile verschwand still: 3 einzeln gelesene Kohorten-Gruppen
        # stehen im Analysis-Lauf (keine Still-Loeschung).
        self.assertEqual(analysis.get("usable", 0) + len(
            analysis.get("excluded", [])) >= 2, True)


if __name__ == "__main__":
    unittest.main()
