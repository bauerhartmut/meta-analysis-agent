"""Tests fuer die cluster-robuste Varianz mit Random-Effects-Gewichten.

Die Referenzwerte sind von Hand gerechnet, nicht aus der Implementierung
abgeschrieben - sonst prueft der Test nur, dass die Formel zu sich selbst
konsistent ist.
"""

from __future__ import annotations

import unittest

from research_agent.meta.rve_weights import random_effects_rve, weight_share


class RandomEffectsRVETest(unittest.TestCase):

    def test_tau2_zero_equals_fixed_effects(self):
        # y = (0, 1), v = (0.25, 1.0), je ein Cluster, tau2 = 0.
        # FE: w = (4, 1), W = 5, theta = 1/5 = 0.2
        # D1 = 4 * (0 - 0.2) = -0.8, D2 = 1 * (1 - 0.2) = 0.8
        # Var = (1.28 / 25) * 2 = 0.1024, se = 0.32
        result = random_effects_rve([0.0, 1.0], [0.25, 1.0],
                                    [[0], [1]], tau2=0.0, t_crit=1.96)
        self.assertTrue(result["available"])
        self.assertAlmostEqual(result["pooled"], 0.2, places=12)
        self.assertAlmostEqual(result["se"], 0.32, places=12)
        self.assertAlmostEqual(result["ci_low"], 0.2 - 1.96 * 0.32, places=12)

    def test_unequal_variances_with_tau2(self):
        # tau2 = 0.75: w = (1.0, 0.5714285714), W = 1.5714285714
        # theta = 0.5714285714 / 1.5714285714 = 0.3636363636
        # D1 = -0.3636363636, D2 = +0.3636363636
        # Var = (32/121) / (121/49) * 2 = 3136/14641, se = 56/121
        result = random_effects_rve([0.0, 1.0], [0.25, 1.0],
                                    [[0], [1]], tau2=0.75, t_crit=1.96)
        self.assertTrue(result["available"])
        self.assertAlmostEqual(result["pooled"], 4.0 / 11.0, places=12)
        self.assertAlmostEqual(result["se"], 56.0 / 121.0, places=12)
        self.assertEqual(result["tau2"], 0.75)

    def test_heterogeneity_widens_the_interval(self):
        # Dieselben Daten, mehr tau2 -> weniger Gewicht auf der praezisen
        # Zeile -> Punkt wandert zur ungenauen, Intervall wird breiter.
        fe = random_effects_rve([0.0, 1.0], [0.25, 1.0],
                                [[0], [1]], tau2=0.0, t_crit=1.96)
        re = random_effects_rve([0.0, 1.0], [0.25, 1.0],
                                [[0], [1]], tau2=2.0, t_crit=1.96)
        self.assertGreater(re["pooled"], fe["pooled"])
        self.assertGreater(re["ci_high"] - re["ci_low"],
                           fe["ci_high"] - fe["ci_low"])

    def test_equal_variances_leave_point_and_se_at_tau2(self):
        # Referenzfall aus test_meta_pooling.RVETest: gleiche Varianzen,
        # deshalb aendert tau2 nur die Skala der Gewichte, nicht theta/se.
        y, v = [1.0, 2.0, 3.0, 5.0], [1.0] * 4
        fe = random_effects_rve(y, v, [[0, 1], [2, 3]], tau2=0.0, t_crit=1.0)
        re = random_effects_rve(y, v, [[0, 1], [2, 3]], tau2=1.0, t_crit=1.0)
        self.assertAlmostEqual(fe["pooled"], 2.75, places=12)
        self.assertAlmostEqual(re["pooled"], 2.75, places=12)
        self.assertAlmostEqual(fe["se"], 1.25, places=12)
        self.assertAlmostEqual(re["se"], 1.25, places=12)

    def test_single_cluster_reports_unavailable(self):
        result = random_effects_rve([1.0, 2.0], [1.0, 1.0],
                                    [[0, 1]], tau2=0.5, t_crit=12.7)
        self.assertFalse(result["available"])
        self.assertIn("mindestens 2", result["reason"])
        self.assertIsNotNone(result["pooled"])

    def test_negative_tau2_is_refused(self):
        with self.assertRaises(ValueError):
            random_effects_rve([1.0], [1.0], [[0]], tau2=-0.1, t_crit=1.96)

    def test_mismatched_lengths_are_refused(self):
        with self.assertRaises(ValueError):
            random_effects_rve([1.0, 2.0], [1.0], [[0], [1]], tau2=0.0,
                               t_crit=1.96)

    def test_cluster_weight_shares_sum_to_one(self):
        shares = weight_share([1.0, 2.0, 3.0], [1.0, 1.0, 1.0],
                              [[0, 1], [2]], tau2=1.0)
        self.assertAlmostEqual(sum(shares), 1.0, places=12)
        # Cluster mit zwei Zeilen traegt doppelt so viel Information.
        self.assertAlmostEqual(shares[0], 2.0 / 3.0, places=12)


if __name__ == "__main__":
    unittest.main()
