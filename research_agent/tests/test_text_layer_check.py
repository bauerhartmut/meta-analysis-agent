"""Textlayer-Gegenprobe (Sprint-30-Rest, Claude-Vorschlag 3): Hat die PDF
einen Textlayer, gilt er als DRITTE Quelle gegen beide Modelllesungen -
Abweichung -> disputed, nie mitteln, nie still korrigiert.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from research_agent.research.vision_table import (
    normalise_number_text, text_layer_check,
)


def _row(raw_effect="-0.53", raw_se="0,1", est=-0.53, se=0.1, disputed=False):
    d = {"label": "x", "raw_effect": raw_effect, "raw_se": raw_se,
         "effect": est, "se": se, "ci_low": -0.7, "ci_high": -0.3,
         "raw_ci_low": "-0,7", "raw_ci_high": "-0,3", "_disputed": disputed}
    if disputed:
        d["_vision_status"] = "disputed"
    return d


class TestZahlenGrenzen(unittest.TestCase):
    def test_genau_treffer_mit_komma_im_text(self):
        text = "Intervention group: -0.53 (SE 0.1), p = 0.42"
        rows = text_layer_check([_row()], text)
        self.assertFalse(rows[0]["_disputed"])
        self.assertEqual(rows[0]["_text_layer_check"]["missing_in_text"], [])

    def test_zeichenfalsche_lesung_wird_disputed(self):
        # Lesung -0.53, Textlayer sagt -0.58: Abweichung bleibt disputed
        text = "Intervention group: -0.58 (SE 0.1), p = 0.42"
        rows = text_layer_check([_row(raw_effect="-0.53", est=-0.53)], text)
        self.assertTrue(rows[0]["_disputed"])
        self.assertEqual(rows[0]["_vision_status"], "disputed")
        self.assertEqual(
            rows[0]["_text_layer_check"]["missing_in_text"],
            ["raw_effect"])


class TestTeilzaehler(unittest.TestCase):
    def test_teilzeichenkette_ist_kein_treffer(self):
        # Lesung 0.53, Text hat 0.532: keine Pseudo-Uebereinstimmung
        text = "reported slope 0.532 (SE 0.1)"
        rows = text_layer_check([_row(raw_effect="0.53", est=0.53)], text)
        self.assertTrue(rows[0]["_disputed"])


class TestStatusbreiten(unittest.TestCase):
    def test_disputed_bleibt_disputed(self):
        text = "Intervention group: -0.53 (SE 0.10)"
        rows = text_layer_check([_row(disputed=True)], text)
        self.assertTrue(rows[0]["_disputed"])
        self.assertEqual(rows[0]["_vision_status"], "disputed")
        # keine Nachclaerung auf einer bereits disputed Zeile
        self.assertNotIn("_text_layer_check", rows[0])

    def test_leerer_text_aendert_nichts(self):
        rows = text_layer_check([_row()], "")
        self.assertFalse(rows[0].get("_disputed"))
        self.assertNotIn("_text_layer_check", rows[0])

    def test_unicode_minus_normalisiert(self):
        text = "effect \u2212 0.53 with SE 0.1"
        rows = text_layer_check([_row()], text)
        self.assertFalse(rows[0]["_disputed"])


if __name__ == "__main__":
    unittest.main()
