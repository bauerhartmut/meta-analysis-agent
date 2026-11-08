"""Tests fuer das maschinelle Vorurteil der Zensus-Dokumente.

Geprueft wird die Mustererkennung, nicht die Wahrheit ueber die Studien: das
Skript darf nur sagen, wo ein Mensch zuerst hinsehen soll. Deshalb testen die
Tests die Ableitungsregeln und die Belegsuche, nicht einzelne Paper.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import prejudge_sol_census as pre  # noqa: E402


class TestTextHelpers(unittest.TestCase):
    def test_tags_and_entities_become_plain_text(self):
        self.assertEqual(pre.plain("<p>Schlaf &amp; Licht</p><b>2024</b>"),
                         "Schlaf & Licht 2024")

    def test_a_sol_sentence_is_returned_with_its_numbers(self):
        text = ("Participants slept well. Sleep onset latency decreased by 12.4 min "
                "in the melatonin group compared with placebo.")
        snippet = pre.sol_snippet(text)
        self.assertIn("12.4", snippet)
        self.assertIn("onset latency", snippet)

    def test_without_a_number_there_is_no_evidence_snippet(self):
        self.assertEqual(pre.sol_snippet("Sleep onset latency was assessed."), "")


class TestDetection(unittest.TestCase):
    def test_interventions_are_named(self):
        text = "Melatonin 3 mg versus placebo in a randomised trial."
        self.assertIn("melatonin", pre.detect_interventions(text))
        self.assertIn("rTMS", pre.detect_interventions("We applied rTMS twice daily."))
        self.assertIn("melatonin-agonist",
                      pre.detect_interventions("Tasimelteon was given for jet lag."))

    def test_design_markers_are_named(self):
        designs = pre.detect_design("A randomised, double-blind, placebo-controlled trial.")
        self.assertIn("randomisierte Studie", designs)
        self.assertIn("Placebo-kontrolliert", designs)
        self.assertIn("doppelblind", designs)


class TestSuggestion(unittest.TestCase):
    def test_without_randomisation_the_suggestion_is_no_rct(self):
        self.assertEqual(pre.suggests(["melatonin"], [], 2, 2, "sleep onset 12.4"), "kein RCT")

    def test_melatonin_with_a_poolable_row(self):
        self.assertEqual(
            pre.suggests(["melatonin"], ["randomisierte Studie"], 1, 1, "sleep onset 12.4"),
            "Melatonin: poolbare SOL-Zeile gespeichert")

    def test_melatonin_without_a_poolable_row(self):
        self.assertEqual(
            pre.suggests(["melatonin"], ["randomisierte Studie"], 1, 0, "sleep onset 12.4"),
            "Melatonin: SOL erwaehnt, keine poolbare Zeile")

    def test_an_agonist_is_not_melatonin(self):
        self.assertEqual(
            pre.suggests(["melatonin-agonist"], ["randomisierte Studie"], 1, 1, "sleep onset 9"),
            "Melatonin-Agonist (kein Melatonin)")

    def test_other_interventions_are_named_as_such(self):
        self.assertEqual(
            pre.suggests(["rTMS"], ["randomisierte Studie"], 1, 1, "sleep onset 9"),
            "andere Intervention (kein Melatonin)")

    def test_without_sol_mention_there_is_nothing_to_sight(self):
        self.assertEqual(
            pre.suggests(["melatonin"], ["randomisierte Studie"], 0, 0, ""), "kein SOL im Text")


class TestBuild(unittest.TestCase):
    def test_documents_carry_their_verdict_suggestion_and_evidence(self):
        import tempfile
        tmp = tempfile.mkdtemp()
        xml = Path(tmp) / "PMC1.xml"
        xml.write_text("<article><p>Randomised, placebo-controlled trial. The melatonin "
                       "group had a sleep onset latency 11.2 min shorter.</p></article>",
                       encoding="utf-8")
        sighting = {"auswahl": {
            "A": [{"pmc": "PMC1", "doi": "10.1/a", "year": "2024", "title": "Melatonin trial",
                   "stored_rows": 3, "sol_rows": 1, "sol_poolable": 1}],
            "B": [], "C": [], "D": []}}
        result = pre.build(sighting, {"PMC1": xml})
        doc = result["documents"][0]
        self.assertEqual(doc["suggestion"], "Melatonin: poolbare SOL-Zeile gespeichert")
        self.assertIn("11.2", doc["evidence"])
        self.assertTrue(doc["xml"])
        self.assertEqual(result["with_xml"], 1)

    def test_a_missing_xml_is_marked_instead_of_crashing(self):
        sighting = {"auswahl": {"A": [{"pmc": "PMC9", "title": "No text", "sol_rows": 0,
                                      "sol_poolable": 0}], "B": [], "C": [], "D": []}}
        result = pre.build(sighting, {})
        self.assertFalse(result["documents"][0]["xml"])


if __name__ == "__main__":
    unittest.main()
