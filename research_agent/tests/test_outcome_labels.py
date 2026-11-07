"""Tests fuer die Outcome-Normalisierung (meta/outcome_labels.py)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.meta.outcome_labels import normalize_outcome
from research_agent.meta.pooling import build_analysis


class TestNormalize(unittest.TestCase):
    def test_unit_and_acronym_variants_collapse(self):
        self.assertEqual(normalize_outcome("Sleep onset latency, min"),
                         normalize_outcome("Sleep latency (min)"))
        self.assertEqual(normalize_outcome("SOL, min"),
                         normalize_outcome("Sleep latency (min)"))
        self.assertEqual(normalize_outcome("Total sleep time (min)"),
                         normalize_outcome("Total sleep time, min"))
        self.assertEqual(normalize_outcome("Sleep efficiency (%)"),
                         normalize_outcome("Sleep efficiency, %"))

    def test_acronym_in_parentheses_is_kept(self):
        self.assertEqual(normalize_outcome("WASO, min"),
                         normalize_outcome("Wake after sleep onset (min)"))
        self.assertEqual(normalize_outcome("PSQI score"),
                         normalize_outcome("Overall sleep quality (PSQI)"))
        self.assertEqual(normalize_outcome("ESS"),
                         normalize_outcome("Excessive daytime sleepiness (ESS)"))

    def test_percentage_and_time_stay_apart(self):
        # Derselbe Endpunkt in % und in Minuten ist nicht dieselbe Skala.
        self.assertNotEqual(normalize_outcome("% Stage N1"),
                            normalize_outcome("Stage N1 time (min)"))
        self.assertNotEqual(normalize_outcome("Sleep efficiency (%)"),
                            normalize_outcome("Sleep efficiency, min"))

    def test_different_endpoints_are_not_merged(self):
        self.assertNotEqual(normalize_outcome("REM latency, min"),
                            normalize_outcome("Sleep onset latency, min"))
        self.assertNotEqual(normalize_outcome("Total sleep time (min)"),
                            normalize_outcome("REM sleep time (min)"))
        self.assertNotEqual(normalize_outcome("Overall sleep quality"),
                            normalize_outcome("PSQI score"))

    def test_unknown_label_is_only_lowercased(self):
        self.assertEqual(normalize_outcome("AHI, events/h"),
                         "ahi events_per_hour")
        self.assertEqual(normalize_outcome(""), "")

    def test_reported_anchor_labels(self):
        # Genau die Wortlaute aus dem SOL-Korpus, die sich widersprachen.
        self.assertEqual(normalize_outcome("Sleep onset latency, min"),
                         "sleep onset latency min")
        self.assertEqual(normalize_outcome("Sleep latency (min)"),
                         "sleep onset latency min")


def _row(source_id: str, outcome: str, effect: float) -> dict:
    return {
        "source_id": source_id,
        "study_id": source_id,
        "outcome": outcome,
        "effect_type": "g",
        "effect": effect,
        "se": 0.1,
        "adjusted": 0,
    }


class TestGrouping(unittest.TestCase):
    def test_two_studies_with_different_labels_form_one_group(self):
        result = build_analysis([
            _row("s1", "Sleep onset latency, min", -0.22),
            _row("s2", "Sleep latency (min)", -0.18),
        ])
        self.assertEqual(len(result["groups"]), 1, list(result["groups"]))
        analysis = next(iter(result["groups"].values()))
        self.assertEqual(analysis["k"], 2)
        self.assertEqual(analysis["outcome"], "sleep onset latency min")

    def test_units_still_split_the_group(self):
        result = build_analysis([
            _row("s1", "% Stage N1", -0.05),
            _row("s2", "Stage N1 time (min)", -6.07),
        ])
        self.assertEqual(len(result["groups"]), 2, list(result["groups"]))


if __name__ == "__main__":
    unittest.main()
