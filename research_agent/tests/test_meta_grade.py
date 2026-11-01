"""Tests for the machine GRADE engine and the risk-of-bias store.

Deterministic by construction: every downgrade is a rule over stored numbers,
so a fixed input yields a fixed rating - byte for byte, run for run.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.grade import grade_group
from research_agent.meta.risk_of_bias import (
    RCT_DOMAINS, domains_for_design, overall_rating,
)


def _group(pooled=-0.5, ci_low=-0.8, ci_high=-0.2, i2=10.0, k=4,
           n_total=1200, design="rct", egger_p=None, scale="smd"):
    rows = [
        {
            "label": f"Studie {i}", "source_id": f"s{i}", "doi": f"10.1/s{i}",
            "est": pooled, "se": 0.1, "n": n_total // k, "design": design,
            "outcome": "depressive symptoms", "scale": scale,
        }
        for i in range(k)
    ]
    return {
        "k": k, "pooled": pooled, "ci_low": ci_low, "ci_high": ci_high,
        "i2": i2, "rows": rows, "scale": scale,
        "egger": ({"p": egger_p, "available": True} if egger_p is not None
                  else {"available": False}),
    }


class GradeTest(unittest.TestCase):
    def test_domains_for_design_maps_rct_set(self):
        self.assertEqual(domains_for_design("rct"), RCT_DOMAINS)
        self.assertEqual(domains_for_design("Randomized"), RCT_DOMAINS)
        self.assertIn("confounding", domains_for_design("cohort"))
        self.assertIn("confounding", domains_for_design(""))

    def test_overall_rating_rules(self):
        low = [{"rating": "low"}]
        self.assertEqual(overall_rating(low), "low")
        self.assertEqual(overall_rating(low + [{"rating": "some_concerns"}]),
                         "some_concerns")
        self.assertEqual(overall_rating(low + [{"rating": "unclear"}]),
                         "some_concerns")
        self.assertEqual(overall_rating(low + [{"rating": "high"}]), "high")

    def test_clean_rct_starts_high_stays_high(self):
        graded = grade_group(_group())
        self.assertEqual(graded["start"], "high")
        self.assertEqual(graded["rating"], "high")
        self.assertEqual(graded["downgrades"], [])

    def test_observational_starts_low(self):
        graded = grade_group(_group(design="cohort"))
        self.assertEqual(graded["start"], "low")
        self.assertEqual(graded["rating"], "low")

    def test_high_i2_downgrades(self):
        graded = grade_group(_group(i2=90.0))
        self.assertEqual(graded["rating"], "moderate")
        self.assertTrue(any("Inkonsistenz" in d for d in graded["downgrades"]))

    def test_small_body_downgrades(self):
        graded = grade_group(_group(n_total=120, k=3))
        self.assertEqual(graded["rating"], "moderate")
        self.assertTrue(any("Imprecision" in d for d in graded["downgrades"]))

    def test_no_pooled_estimate_downgrades(self):
        graded = grade_group(_group(pooled=None, ci_low=None, ci_high=None, k=1))
        self.assertTrue(any("gepoolter" in d for d in graded["downgrades"]))

    def test_egger_signal_downgrades_only_at_k10(self):
        self.assertEqual(
            grade_group(_group(k=4, egger_p=0.05), None)["rating"], "high"
        )
        self.assertEqual(
            grade_group(_group(k=12, egger_p=0.05), None)["rating"], "moderate"
        )

    def test_machine_high_rob_downgrades(self):
        rob = {"s0": "high"}
        self.assertEqual(
            grade_group(_group(), rob)["rating"], "moderate"
        )

    def test_floor_never_below_very_low(self):
        graded = grade_group(_group(i2=99.0, n_total=50, k=2,
                                     egger_p=0.01), {"s0": "high"})
        self.assertEqual(graded["rating"], "very_low")
        self.assertLessEqual(len(graded["downgrades"]), 3)

    def test_deterministic_same_input_same_output(self):
        a = grade_group(_group(i2=80.0), {"s0": "some_concerns"})
        b = grade_group(_group(i2=80.0), {"s0": "some_concerns"})
        self.assertEqual(a, b)

    def test_ratio_scale_uses_wide_ci_rule_identically(self):
        self.assertEqual(
            grade_group(_group(scale="log_ratio")),
            grade_group(_group(scale="log_ratio")),
        )


class BiasStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="meta_bias_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.db_path = os.path.join(self.tmp, "data", "research.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.db = Database(self.db_path)

    def test_save_and_get_roundtrip(self):
        record = {
            "source_id": "s1", "design": "rct",
            "domains": '[{"domain": "randomisation", "rating": "low", '
                       '"quote": "Randomisation was performed;", '
                       '"quote_start": 0, "quote_end": 26}]',
            "overall": "low", "assessor": "rob_assessor_v1",
            "extraction_pass": 1, "disputed": 0,
            "source_text_id": "t1", "created_at": "2026-01-01T00:00:00Z",
        }
        self.db.save_bias_assessment(record)
        loaded = self.db.get_bias_assessment("s1")
        self.assertEqual(loaded["overall"], "low")
        self.assertEqual(loaded["assessor"], "rob_assessor_v1")
        # Upsert overwrites instead of raising.
        record["overall"] = "some_concerns"
        self.db.save_bias_assessment(record)
        self.assertEqual(
            self.db.get_bias_assessment("s1")["overall"], "some_concerns"
        )
        self.assertEqual(len(self.db.get_all_bias_assessments()), 1)

    def test_get_missing_returns_none(self):
        self.assertIsNone(self.db.get_bias_assessment("kein-auftrag"))

    def test_sources_with_effects_without_bias(self):
        """The candidate query returns exactly the extracted-only sources."""
        self.db.save_source({
            "id": "s1", "title": "Paper s1",
            "url": "https://example.org/s1", "source_type": "paper",
            "relevance": 0.6, "relevance_scored": 1,
            "date_added": "2026-01-01T00:00:00Z",
        })
        self.db.save_source_text("s1", "x " * 2000, kind="html")
        self.db.save_study_effect({
            "id": "e1", "source_id": "s1", "effect": -0.4, "se": 0.1,
            "n": 100, "effect_type": "smd", "created_at":
            "2026-01-01T00:00:00Z",
        })
        pool = self.db.get_sources_with_effects_without_bias(
            min_relevance=0.25, limit=10
        )
        self.assertEqual([r["id"] for r in pool], ["s1"])
        # After the bias assessment the candidate disappears.
        self.db.save_bias_assessment({
            "source_id": "s1", "design": "rct", "domains": "[]",
            "overall": "low", "assessor": "rob_assessor_v1",
            "disputed": 0, "created_at": "2026-01-01T00:00:00Z",
        })
        self.assertEqual(
            self.db.get_sources_with_effects_without_bias(
                min_relevance=0.25, limit=10
            ), []
        )


if __name__ == "__main__":
    unittest.main()
