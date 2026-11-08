"""Tests fuer die Stichprobenziehung der SOL-Sichtung (Obergrenze, Paket A).

Geprueft werden die reinen Funktionen: die Auswahl muss bei gleichem Seed
reproduzierbar sein, der Zensus vollstaendig in der Liste landen und die
Hochrechnung konservativ bleiben. Die Daten selbst (Manifest, Mess-DBs) sind
gitignored; die Tests laufen deshalb auf kleinen Attrappen.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import sample_sol_candidates as sampler  # noqa: E402


class TestSelection(unittest.TestCase):
    def test_pick_is_reproducible_for_the_same_seed(self):
        pool = [f"PMC{i}" for i in range(50)]
        self.assertEqual(sampler.pick(pool, 10, "abc"),
                         sampler.pick(list(reversed(pool)), 10, "abc"))

    def test_a_different_seed_gives_a_different_sample(self):
        pool = [f"PMC{i}" for i in range(50)]
        self.assertNotEqual(sampler.pick(pool, 10, "abc"),
                            sampler.pick(pool, 10, "xyz"))

    def test_the_sample_is_a_subset_of_the_pool_and_never_larger(self):
        pool = [f"PMC{i}" for i in range(7)]
        chosen = sampler.pick(pool, 30, "seed")
        self.assertEqual(len(chosen), 7)
        self.assertTrue(set(chosen) <= set(pool))


class TestUpperBound(unittest.TestCase):
    def test_zero_hits_at_sixty_is_near_the_rule_of_three(self):
        # Exakt (Clopper-Pearson): 1 - 0.05 ** (1/60) = 4,87 %. Die Regel der
        # Drei (3/n = 5,0 %) ist die Naeherung, nicht der Wert.
        self.assertAlmostEqual(sampler.upper_bound(0, 60), 0.0487, places=3)
        self.assertAlmostEqual(sampler.upper_bound(0, 60),
                               1 - 0.05 ** (1 / 60), places=6)

    def test_the_bound_grows_with_hits_and_stays_in_range(self):
        self.assertLess(sampler.upper_bound(0, 60), sampler.upper_bound(2, 60))
        self.assertLess(sampler.upper_bound(2, 60), sampler.upper_bound(10, 60))
        for hits in (0, 1, 5):
            value = sampler.upper_bound(hits, 60)
            self.assertTrue(0.0 < value <= 1.0)

    def test_an_empty_sample_has_no_usable_bound(self):
        self.assertEqual(sampler.upper_bound(0, 0), 1.0)


class TestClassification(unittest.TestCase):
    def test_sol_labels_are_recognised(self):
        for label in ("SOL", "sleep onset latency", "Sleep latency",
                      "sleep-onset", "Einschlaflatenz"):
            self.assertTrue(sampler.matches(sampler.SOL_PATTERN, label), label)
        for label in ("total sleep time", "WASO", "Schlafqualitaet"):
            self.assertFalse(sampler.matches(sampler.SOL_PATTERN, label), label)

    def test_rows_are_counted_by_outcome_and_poolability(self):
        rows = [
            {"outcome": "Sleep onset latency", "_poolable": True},
            {"outcome": "SOL", "_poolable": False},
            {"outcome": "Total sleep time", "_poolable": True},
        ]
        stats = sampler.classify_document(rows, "Melatonin and sleep onset")
        self.assertEqual(stats["stored_rows"], 3)
        self.assertEqual(stats["sol_rows"], 2)
        self.assertEqual(stats["sol_poolable"], 1)
        self.assertTrue(stats["title_names_sleep"])


class TestBuild(unittest.TestCase):
    def args(self):
        manifest = [
            {"pmc": "PMC1", "doi": "10.1/a", "title": "Melatonin and sleep onset", "year": "2020"},
            {"pmc": "PMC2", "doi": "10.1/b", "title": "Something else", "year": "2021"},
            {"pmc": "PMC3", "doi": "10.1/c", "title": "Sleep latency trial", "year": "2022"},
            {"pmc": "PMC4", "doi": "10.1/d", "title": "Unrelated", "year": "2023"},
            {"pmc": "PMC5", "doi": "10.1/e", "title": "Noise", "year": "2023"},
        ]
        funnel = [
            {"pmc": "PMC1", "doi": "10.1/a", "sol_kandidat": True, "tabellen": 2, "zeilen": 9, "kandidaten": 1},
            {"pmc": "PMC2", "doi": "10.1/b", "sol_kandidat": True, "tabellen": 1, "zeilen": 4, "kandidaten": 1},
            {"pmc": "PMC3", "doi": "10.1/c", "sol_kandidat": True, "tabellen": 3, "zeilen": 7, "kandidaten": 0},
            {"pmc": "PMC4", "doi": "10.1/d", "sol_kandidat": True, "tabellen": 1, "zeilen": 2, "kandidaten": 0},
            {"pmc": "PMC5", "doi": "10.1/e", "sol_kandidat": False, "tabellen": 1, "zeilen": 1, "kandidaten": 0},
        ]
        rows = {
            "10.1/a": [{"outcome": "Sleep onset latency", "_poolable": True}],
            "10.1/b": [{"outcome": "Total sleep time", "_poolable": True}],
        }
        return manifest, funnel, rows

    def test_census_holds_every_document_with_sol_rows_and_samples_the_rest(self):
        manifest, funnel, rows = self.args()
        result = sampler.build(manifest, funnel, rows, {"PMC2"}, "seed", 1, 1)
        # A = poolbarer SOL-Effekt, B = SOL-Zeile nicht poolbar,
        # C = Effektzeilen ohne SOL-Label, D = Titel
        self.assertEqual([i["pmc"] for i in result["auswahl"]["A"]], ["PMC1"])
        self.assertEqual([i["pmc"] for i in result["auswahl"]["C"]], ["PMC2"])
        self.assertEqual([i["pmc"] for i in result["auswahl"]["D"]], ["PMC3"])
        self.assertEqual(len(result["auswahl"]["E"]), 1)  # PMC4 von einem Kandidaten
        self.assertEqual(len(result["auswahl"]["X"]), 1)  # PMC5 als Fehlerprobe
        self.assertTrue(result["auswahl"]["C"][0]["bereits_gelesen"])

    def test_the_projection_never_undercounts_the_census(self):
        manifest, funnel, rows = self.args()
        result = sampler.build(manifest, funnel, rows, set(), "seed", 1, 0)
        h = result["hochrechnung"]
        self.assertEqual(h["kandidaten"], 4)
        self.assertEqual(h["zensus"], 3)
        self.assertGreaterEqual(h["obergrenze_dokumente"], h["bekannt_poolbar"])

    def test_a_tiny_rest_is_fully_sighted_instead_of_extrapolated(self):
        manifest, funnel, rows = self.args()
        result = sampler.build(manifest, funnel, rows, set(), "seed", 60, 30)
        self.assertEqual(result["hochrechnung"]["rest_stichprobe"], 1)
        self.assertEqual(result["hochrechnung"]["rest_gesamt"], 1)


if __name__ == "__main__":
    unittest.main()
