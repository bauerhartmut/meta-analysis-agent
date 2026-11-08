"""Tests for the single-cluster gate.

The property: a pooled result whose rows come from one source keeps its point
estimate but loses every interval, because there is no second independent unit
to estimate uncertainty from. A pool with two or more clusters must pass
through untouched.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.meta.pool_gates import single_cluster_gate


def _analysis(clusters, k=3, pooled=0.3):
    return {
        "k": k, "pooled": pooled, "se": 0.1,
        "ci_low": 0.1, "ci_high": 0.5,
        "fixed_ci_low": 0.12, "fixed_ci_high": 0.48,
        "pi_low": 0.0, "pi_high": 0.6,
        "rve": {"available": clusters >= 2, "M": clusters},
    }


class TestSingleClusterGate(unittest.TestCase):
    def test_one_cluster_removes_every_interval(self):
        result = single_cluster_gate(_analysis(1))
        self.assertTrue(result["single_cluster"])
        self.assertIn("M=1", result["single_cluster_note"])
        for field in ("ci_low", "ci_high", "fixed_ci_low", "fixed_ci_high",
                      "pi_low", "pi_high"):
            self.assertIsNone(result[field], field)

    def test_point_estimate_survives_as_a_sighting(self):
        result = single_cluster_gate(_analysis(1, pooled=0.42))
        self.assertEqual(result["pooled"], 0.42)

    def test_two_clusters_pass_through(self):
        result = single_cluster_gate(_analysis(2))
        self.assertNotIn("single_cluster", result)
        self.assertEqual(result["ci_low"], 0.1)
        self.assertEqual(result["pi_high"], 0.6)

    def test_missing_rve_is_not_gated(self):
        analysis = _analysis(1)
        analysis.pop("rve")
        result = single_cluster_gate(analysis)
        self.assertNotIn("single_cluster", result)
        self.assertEqual(result["ci_low"], 0.1)

    def test_single_row_pool_is_not_marked(self):
        # k = 1 already has no interval; the gate is about clusters, not k.
        result = single_cluster_gate(_analysis(1, k=1, pooled=None))
        self.assertNotIn("single_cluster", result)

    def test_note_is_appended(self):
        analysis = _analysis(1)
        analysis["note"] = "vorher"
        result = single_cluster_gate(analysis)
        self.assertTrue(result["note"].startswith("vorher"))
        self.assertIn("Scheinpraezision", result["note"])


if __name__ == "__main__":
    unittest.main()
