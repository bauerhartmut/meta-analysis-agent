"""Auftrag v2 §6: Evidenz-Kategorien - die Konfidenz kommt aus Zeilen.

Die Tests pinnen die deterministische Regel: ohne Evidenzzeile ist eine
Hypothese spekulativ, Widerspruch deckelt die Konfidenz, und nichts hier
hängt am LLM-Tonfall.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.meta.evidence import (
    CATEGORY_LABELS, classify_hypothesis, evidence_category, evidence_confidence,
)


def row(kind: str) -> dict:
    return {"evidence_type": kind}


class EvidenceCategoryTest(unittest.TestCase):
    def test_no_rows_is_speculative(self):
        self.assertEqual(evidence_category([]), "spekulativ")
        self.assertEqual(evidence_category([row("neutral")]), "spekulativ")

    def test_single_support_is_supported_but_unsicher(self):
        self.assertEqual(
            evidence_category([row("supports")]), "evidenzgestuetzt_unsicher")

    def test_two_supports_are_belegt(self):
        self.assertEqual(
            evidence_category([row("supports"), row("supports")]),
            "empirisch_belegt")

    def test_any_contradiction_with_support_is_contradictory(self):
        self.assertEqual(
            evidence_category([row("contradicts"),
                               row("supports"), row("supports")]),
            "widerspruechlich_ungeklaert")

    def test_pure_contradiction_is_evidence_not_speculation(self):
        # Eine widersprechende Zeile ist Evidenz (negativ): geprüft wurde,
        # und NICHT bestätigt - Kategorie 'widersprüchlich/ungeklärt',
        # Konfidenz am Boden, nicht spekulativ.
        self.assertEqual(
            evidence_category([row("contradicts")]),
            "widerspruechlich_ungeklaert")
        self.assertEqual(evidence_confidence([row("contradicts")]), 0.05)


class EvidenceConfidenceTest(unittest.TestCase):
    def test_no_rows_means_no_claim(self):
        self.assertIsNone(evidence_confidence([]))
        self.assertIsNone(evidence_confidence([row("neutral")]))

    def test_single_support_never_over_070(self):
        self.assertEqual(evidence_confidence([row("supports")]), 0.7)

    def test_two_supports_belegaufen(self):
        # s=2, c=0: conf = 0.5 + 0.45*(2/2) = 0.95
        self.assertEqual(
            evidence_confidence([row("supports"), row("supports")]), 0.95)

    def test_contradiction_caps_at_060(self):
        # s=3, c=1: raw conf = 0.5 + 0.45*0.5 = 0.725 -> Kappe 0.60
        self.assertEqual(
            evidence_confidence(
                [row("supports")] * 3 + [row("contradicts")]), 0.6)

    def test_pure_contradiction_hits_the_floor(self):
        self.assertEqual(evidence_confidence([row("contradicts")]), 0.05)

    def test_classify_hypothesis_bundle(self):
        head = classify_hypothesis({"confidence": 0.90}, [row("supports")])
        self.assertEqual(head["category"], "evidenzgestuetzt_unsicher")
        self.assertEqual(head["evidence_confidence"], 0.7)
        self.assertEqual(head["model_confidence"], 0.90)
        self.assertEqual(CATEGORY_LABELS["spekulativ"], "Spekulativ / theoretisch")


if __name__ == "__main__":
    unittest.main()
