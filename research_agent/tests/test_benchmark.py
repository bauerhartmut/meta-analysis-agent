"""Goldstandard-Abgleich (Auftragsv2 §9.2/§9.3): der Benchmark-Runner prüft
die Run-DB gegen data/goldstandard/goldstandard.csv — Pool-Abweichung mit
den festen Pflegeblatt-Toleranzen, Decken-Warnung für die Studienauswahl,
Extraktionsdeckung — alles Read-only, nichts wird still verifiziert."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.benchmark import (
    format_benchmark_lines,
    load_benchmark_entries,
    resolve_benchmark_csv,
    run_benchmark,
)
from research_agent.models import gen_id


def _seed_effect(db, value, se=0.10, outcome="reaction time",
                 outcome_key="reaction_time"):
    db.save_study_effect({
        "id": gen_id(),
        "source_id": gen_id(),
        "outcome": outcome,
        "outcome_key": outcome_key,
        "comparison": "caffeine vs placebo",
        "effect_type": "smd",
        "effect": value,
        "se": se,
        "ci_low": round(value - 1.96 * se, 3),
        "ci_high": round(value + 1.96 * se, 3),
        "n": 40,
        "design": "randomised crossover trial",
        "population": "healthy adults",
        "quote": "pooled effect text for the seeded reading",
        "quote_start": 0,
        "quote_end": 40,
    })


def _entry_csv(path, rows):
    header = ("id,frage,outcome,autoren,doi,skala,wert,ci_unten,ci_ober,k,"
              "population,verifizierungszustand,zitat,gelesen_via,verwendung")
    body = header + "\n" + "\n".join(rows) + "\n"
    path.write_text(body, encoding="utf-8")


class TestBenchmarkRunner(unittest.TestCase):
    def setUp(self):
        db = Database(":memory:")
        # Pool nahe dem Kløve-Referenzwert (0.28): 4 Zeilen, gleiche SE.
        self.db = db
        for value in (0.25, 0.30, 0.29, 0.28):
            _seed_effect(db, value)
        # Eine Zeile ohne Wert: zählt in die Eyefraud-Rate, nicht in den Pool.
        self.db.save_study_effect({
            "id": gen_id(), "source_id": gen_id(),
            "outcome": "reaction time", "outcome_key": "reaction_time",
            "effect_type": "smd", "effect": None, "se": None,
            "quote": "qualitative reading", "quote_start": -1,
        })

    def _entries(self):
        # Eine aktuelle Fake-Fundusliste (Struktur wie goldstandard.csv).
        return [
            {"id": "e_rt_ok", "frage": "f", "outcome": "Reaktionszeit",
             "skala": "Hedges_g", "wert": "0.28", "ci_unten": "0.21",
             "ci_ober": "0.36", "k": "31",
             "verifizierungszustand": "menschlich verifiziert"},
            {"id": "e_rt_far", "frage": "f", "outcome": "Reaktionszeit",
             "skala": "Hedges_g", "wert": "1.50", "ci_unten": "1.30",
             "ci_ober": "1.70", "k": "10",
             "verifizierungszustand": "agent-geprüft"},
            {"id": "e_acc", "frage": "f", "outcome": "Genauigkeit",
             "skala": "Hedges_g", "wert": "0.27", "ci_unten": "0.17",
             "ci_ober": "0.37", "k": "31",
             "verifizierungszustand": "menschlich verifiziert"},
            {"id": "e_richtung", "frage": "f", "outcome": "Reaktionszeit",
             "skala": "ES", "wert": "", "verifizierungszustand": "agent-geprüft"},
        ]

    def test_pass_when_delta_small_and_ci_overlaps(self):
        bench = run_benchmark(self.db, entries=self._entries())
        by_id = {r["id"]: r for r in bench["results"]}
        rt = by_id["e_rt_ok"]
        self.assertEqual(rt["verdict"], "pass")
        self.assertAlmostEqual(rt["lauf_wert"], 0.28, places=2)
        self.assertTrue(rt["verified"])
        # Decken-Warnung: der Fundus (k=31) deckt weit mehr ab als der Lauf (4):
        self.assertIn("Decken-Warnung", rt.get("note", ""))

    def test_unverified_deviation_is_not_a_hard_fail(self):
        bench = run_benchmark(self.db, entries=self._entries())
        by_id = {r["id"]: r for r in bench["results"]}
        far = by_id["e_rt_far"]
        self.assertEqual(far["verdict"], "abweichung")
        self.assertFalse(far["verified"])
        # Kein harter FAIL: die Referenz ist nicht menschlich verifiziert.
        self.assertEqual(bench["hard_fails"], 0)

    def test_verified_deviation_counts_as_hard_fail(self):
        entries = self._entries()
        entries[1]["verifizierungszustand"] = "menschlich verifiziert"
        bench = run_benchmark(self.db, entries=entries)
        self.assertEqual(bench["hard_fails"], 1)

    def test_outcome_without_pooled_group_is_reported(self):
        bench = run_benchmark(self.db, entries=self._entries())
        by_id = {r["id"]: r for r in bench["results"]}
        # "Genauigkeit" ist im Lauf nicht gepoolt (nur Reaction-time-Zeilen).
        self.assertEqual(by_id["e_acc"]["verdict"], "kein_gepools")

    def test_direction_only_entry_needs_no_numbers(self):
        bench = run_benchmark(self.db, entries=self._entries())
        by_id = {r["id"]: r for r in bench["results"]}
        self.assertEqual(by_id["e_richtung"]["verdict"], "kein_vergleich")

    def test_extraction_coverage_counts_valueless_rows(self):
        bench = run_benchmark(self.db, entries=self._entries())
        # 4 Zeilen mit Wert (alle mit SE) + 1 Zeile ohne Wert:
        self.assertEqual(bench["n_with_value"], 4)
        self.assertEqual(bench["n_with_precision"], 4)
        self.assertAlmostEqual(bench["extraction_coverage"], 1.0)

    def test_format_lines_reflect_the_counts(self):
        bench = run_benchmark(self.db, entries=self._entries())
        lines = format_benchmark_lines(bench)
        head = lines[0]
        self.assertIn("pass", head)
        self.assertIn("grenzwertig", head)
        # Der nicht verifizierte Ausreißer trägt den Informationssstempel:
        self.assertTrue(any("e_rt_far" in ln and "nicht menschlich verifiziert" in ln
                            for ln in lines))

    def test_missing_fundus_marks_unavailable(self):
        bench = run_benchmark(self.db, entries=[])
        self.assertFalse(bench["available"])


class TestFundusResolution(unittest.TestCase):
    def test_in_memory_db_has_no_fundus_path(self):
        self.assertIsNone(resolve_benchmark_csv(Database(":memory:")))

    def test_fundus_next_to_the_db_file_is_found(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_file = root / "research-x.db"
            Database(str(db_file))  # erzeugt Datei + Verbrauchbare Pfadbasis
            gs_dir = root / "goldstandard"
            gs_dir.mkdir()
            target = gs_dir / "goldstandard.csv"
            _entry_csv(target, ["e1,f,o,a,doi,Hedges_g,0.28,0.21,0.36,31,pop,"
                                "menschlich verifiziert,q,src,verw"])
            found = resolve_benchmark_csv(_ReadOnlyStub(str(db_file)))
            self.assertEqual(found, target)

    def test_load_entries_is_tolerant(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "goldstandard.csv"
            _entry_csv(target, [
                "e1,f,o,a,doi,Hedges_g,0.28,0.21,0.36,31,pop,"
                "menschlich verifiziert,q,src,verw",
                "e2,f,o,a,doi,SMD,,,,,,,,",
            ])
            entries = load_benchmark_entries(target)
            self.assertEqual(len(entries), 2)
            self.assertAlmostEqual(entries[0]["wert_num"], 0.28)
            self.assertIsNone(entries[1]["wert_num"])  # Zeile ohne Zahl: kein stiller Verlust


class _ReadOnlyStub:
    """Trägt nur db_path/_is_memory — genug für resolve_benchmark_csv."""

    def __init__(self, db_path):
        self.db_path = db_path
        self._is_memory = db_path == ":memory:"


if __name__ == "__main__":
    unittest.main()
