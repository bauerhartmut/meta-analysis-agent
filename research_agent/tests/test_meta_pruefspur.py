"""Der Bericht muss die Pruefspur der Doppellesung ausweisen.

Zwei Zahlen, die nicht verwechselt werden duerfen: verworfene Kopien (eine
Doppelzaehlung, die nicht passiert ist) und poolbare Zeilen aus Pass B ohne
Gegenlesung (im Pool, aber ungeprueft).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.report import _pruefspur_counts


class TestPruefspur(unittest.TestCase):
    def test_zaehlt_kopien_und_nicht_gegengelesene_getrennt(self):
        analysis = {
            "groups": {"cognition|hedges_g": {"rows": [
                {"extraction_pass": 1},
                {"extraction_pass": 2},
            ]}},
            "excluded": [
                {"reason": "zweite Lesung (Zwilling der Erstlesung)"},
                {"reason": "Doppel-Extraktion widersprüchlich"},
            ],
        }
        self.assertEqual(_pruefspur_counts(analysis), (1, 1))

    def test_fehlendes_passfeld_ist_erstlesung(self):
        analysis = {
            "groups": {"g|hedges_g": {"rows": [
                {"extraction_pass": None},
                {"extraction_pass": 1},
                {},
            ]}},
            "excluded": [],
        }
        self.assertEqual(_pruefspur_counts(analysis), (0, 0))

    def test_dritte_lesung_zaehlt_als_nicht_gegengelesen(self):
        analysis = {"groups": {"g|hedges_g": {"rows": [
            {"extraction_pass": 3},
        ]}}, "excluded": []}
        self.assertEqual(_pruefspur_counts(analysis), (0, 1))

    def test_leere_analyse(self):
        self.assertEqual(_pruefspur_counts({}), (0, 0))


if __name__ == "__main__":
    unittest.main()
