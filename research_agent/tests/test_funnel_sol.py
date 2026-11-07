"""Tests fuer den Ausbeute-Funnel (Paket A).

Geprueft wird die Zaehlmechanik, nicht die Extraktion: der Funnel darf das
Verhalten der Leser nicht veraendern, also prueft er deren Rueckgaben. Die
Tests laufen deshalb ohne Korpus; der Endpunkt-Test gegen die Mess-DBs wird
uebersprungen, wenn die Daten fehlen (sie sind gitignored).
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import funnel_sol  # noqa: E402


class TestGates(unittest.TestCase):
    def test_reasons_are_folded_into_gates(self):
        self.assertEqual(funnel_sol.gate_of("Design: Baseline-Zeile"), "design")
        self.assertEqual(funnel_sol.gate_of("Median statt Mittelwert"), "median")
        self.assertEqual(funnel_sol.gate_of("nur SEM angegeben"), "sem_se")
        self.assertEqual(funnel_sol.gate_of("Kopfzeile passt nicht"), "tabellenrest")
        self.assertEqual(funnel_sol.gate_of("Alter nur als Spanne"), "demografie")
        self.assertEqual(funnel_sol.gate_of("etwas ganz anderes"), "sonstig")
        self.assertEqual(funnel_sol.gate_of(""), "unbekannt")

    def test_gate_counts_sum_to_rejections(self):
        reasons = {"Design: Baseline": 3, "Median": 2, "": 1}
        gates = funnel_sol.gates_of(reasons)
        self.assertEqual(sum(gates.values()), 6)


class TestStageSums(unittest.TestCase):
    def test_every_call_is_a_candidate_or_a_rejection(self):
        reader = funnel_sol._empty_reader()
        for _ in range(3):
            funnel_sol._fold(reader, True, outcome="sleep onset latency")
        for reason in ("Design", "Median"):
            funnel_sol._fold(reader, False, reason)
        stats = funnel_sol.summarise_reader(reader, rows_in=5)
        self.assertTrue(stats["sum_ok"])
        self.assertEqual(stats["candidates"], 3)
        self.assertEqual(stats["rejected"], 2)
        self.assertEqual(stats["outcomes"], {"sleep onset latency": 3})

    def test_an_empty_reason_is_counted_as_unknown_not_dropped(self):
        reader = funnel_sol._empty_reader()
        funnel_sol._fold(reader, False, "")
        stats = funnel_sol.summarise_reader(reader, rows_in=1)
        self.assertEqual(stats["reasons"], {"unbekannt": 1})
        self.assertTrue(stats["sum_ok"])

    def test_a_lost_row_is_reported_as_inconsistent(self):
        reader = funnel_sol._empty_reader()
        funnel_sol._fold(reader, True)
        stats = funnel_sol.summarise_reader(reader, rows_in=3)
        self.assertFalse(stats["sum_ok"])


class TestLossRanking(unittest.TestCase):
    def stages(self, **values):
        base = {"manifest": 10, "dokumente": 10, "fehlend": 0,
                "sol_kandidaten": 4, "tabellen": 20, "zeilen": 100,
                "saetze": 500, "kandidaten": 10, "gespeichert": 6,
                "poolbar": 2}
        base.update(values)
        return base

    def test_only_comparable_stages_form_a_loss(self):
        ranking = funnel_sol.loss_ranking(self.stages())
        pairs = [(row["from"], row["to"]) for row in ranking]
        self.assertEqual(pairs, [("dokumente", "sol_kandidaten"),
                                 ("zeilen", "kandidaten"),
                                 ("kandidaten", "gespeichert"),
                                 ("gespeichert", "poolbar")])
        by_pair = {(row["from"], row["to"]): row for row in ranking}
        self.assertEqual(by_pair[("zeilen", "kandidaten")]["lost"], 90)
        self.assertAlmostEqual(by_pair[("zeilen", "kandidaten")]["lost_share"], 0.9)

    def test_the_biggest_absolute_loss_wins(self):
        top = funnel_sol.biggest_loss(funnel_sol.loss_ranking(self.stages()))
        self.assertEqual((top["from"], top["to"]), ("zeilen", "kandidaten"))

    def test_no_loss_means_no_top_entry(self):
        stages = self.stages(zeilen=10, kandidaten=10, gespeichert=10,
                             poolbar=10, sol_kandidaten=10)
        self.assertIsNone(funnel_sol.biggest_loss(funnel_sol.loss_ranking(stages)))

    def test_a_zero_input_yields_no_share_instead_of_a_division_error(self):
        ranking = funnel_sol.loss_ranking(self.stages(gespeichert=0, poolbar=0))
        top = [r for r in ranking if r["to"] == "poolbar"][0]
        self.assertIsNone(top["lost_share"])


class TestReportWriting(unittest.TestCase):
    def test_markdown_names_every_stage_and_the_biggest_loss(self):
        stages = {"manifest": 1059, "dokumente": 1056, "fehlend": 3,
                  "sol_kandidaten": 400, "tabellen": 2000, "zeilen": 42396,
                  "saetze": 315857, "kandidaten": 523, "gespeichert": 523,
                  "poolbar": 5}
        report = {
            "generated": "2026-11-08T00:00:00",
            "stages": stages,
            "loss_ranking": funnel_sol.loss_ranking(stages),
            "readers": {"arm_tabelle": funnel_sol.summarise_reader(
                funnel_sol._empty_reader(), rows_in=0)},
            "open": ["Obergrenze nicht gemessen"],
        }
        report["biggest_loss"] = funnel_sol.biggest_loss(report["loss_ranking"])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "funnel.md"
            funnel_sol.write_markdown(report, path)
            text = path.read_text(encoding="utf-8")
        self.assertIn("| Tabellenzeilen | 42396 |", text)
        self.assertIn("zeilen -> kandidaten", text)
        self.assertIn("Obergrenze nicht gemessen", text)

    def test_json_roundtrip_keeps_the_stage_numbers(self):
        stages = {"manifest": 2, "dokumente": 2, "fehlend": 0,
                  "sol_kandidaten": 1, "tabellen": 0, "zeilen": 0,
                  "saetze": 0, "kandidaten": 0, "gespeichert": 0, "poolbar": 0}
        payload = {"stages": stages,
                   "loss_ranking": funnel_sol.loss_ranking(stages)}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "funnel.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            loaded = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(loaded["stages"]["manifest"], 2)


class TestEndpointsAgainstDbs(unittest.TestCase):
    """Stufe 8 muss die Zahlen der Mess-DBs treffen (uebersprungen ohne Daten)."""

    SOL = ROOT / "data" / "bench" / "sol"

    def test_stored_endpoint_matches_the_arm_db(self):
        db = self.SOL / "arm_all.db"
        if not db.is_file():
            self.skipTest("arm_all.db fehlt (gitignored)")
        from research_agent.database import Database
        rows = Database(str(db)).get_study_effects() or []
        counted = funnel_sol._db_rows({"arm": str(db)}, "stored")
        self.assertEqual(counted, len(rows))

    def test_poolable_endpoint_is_a_subset_of_stored(self):
        db = self.SOL / "arm_all.db"
        if not db.is_file():
            self.skipTest("arm_all.db fehlt (gitignored)")
        stored = funnel_sol._db_rows({"arm": str(db)}, "stored")
        poolable = funnel_sol._db_rows({"arm": str(db)}, "poolable")
        self.assertLessEqual(poolable, stored)


if __name__ == "__main__":
    unittest.main()
