"""Tests fuer Paket E: der Bericht darf keinen Pool behaupten, den es nicht gibt.

Strukturell geprueft, nicht per Satz-Regex: der gepoolte Abschnitt entsteht aus
dem Pool-Ergebnis. Fehlt der Pool, muss der Bericht das an der Abschnittsspitze
sagen und darf keine Zeile mit gepooltem Effekt samt Intervall enthalten.
"""

import re
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.screening import DECISION_EXCLUDE, record_decision
from research_agent.report import build_report

_POOLED_LINE = re.compile(r"Gepoolter Effekt \(Random Effects")


class ReportHonestyTest(unittest.TestCase):
    def build(self):
        self.tmp = tempfile.mkdtemp(prefix="report_honesty_")
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))
        db = Database(str(Path(self.tmp) / "run.db"))
        path = build_report(db, "melatonin and sleep onset latency",
                            out_dir=self.tmp)
        return Path(path).read_text(encoding="utf-8")

    def test_k0_report_states_that_nothing_was_pooled(self):
        text = self.build()
        self.assertIn("Kein gepoolter Effekt in diesem Bericht.", text)

    def test_k0_report_has_no_pooled_effect_line(self):
        text = self.build()
        self.assertIsNone(_POOLED_LINE.search(text))

    def test_coverage_line_comes_before_the_first_section(self):
        text = self.build()
        self.assertIn("Zielma\u00df-Abdeckung:", text)
        self.assertLess(text.index("Zielma\u00df-Abdeckung:"),
                        text.index("## Kurzfassung"))


if __name__ == "__main__":
    unittest.main()


class PrismaMatchesDatabaseTest(unittest.TestCase):
    """Die PRISMA-Zeilen im Bericht muessen die Zeilen der Datenbank sein.

    Geprueft wird gegen eine unabhaengige SQL-Zaehlung, nicht gegen die
    Funktion, die den Bericht fuellt: sonst wuerde die Zaehlung sich selbst
    bestaetigen.
    """

    def test_prisma_rows_equal_independent_sql_counts(self):
        tmp = tempfile.mkdtemp(prefix="report_prisma_")
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))
        db_path = Path(tmp) / "run.db"
        db = Database(str(db_path))

        for sid in ("s1", "s2"):
            db.save_source({
                "id": sid, "title": f"Paper {sid}", "url": f"https://doi.org/10.1/{sid}",
                "author": "Doe, Jane", "publication_date": "2024-01-01",
                "source_type": "paper", "relevance": 0.8, "relevance_scored": 1,
                "date_added": "2026-01-01T00:00:00Z",
            })
        for eid, sid, eff, se, disputed in (("e1", "s1", 0.30, 0.10, 0),
                                            ("e2", "s2", 0.50, 0.20, 1)):
            db.save_study_effect({
                "id": eid, "source_id": sid, "outcome": "Kognition",
                "effect_type": "smd", "effect": eff, "se": se, "ci_level": 0.95,
                "quote": f"effect {eff} (unit: SD)", "quote_start": 0,
                "quote_end": 24, "disputed": disputed, "rejection_reason": "",
                "created_at": "2026-01-01T00:00:00Z",
            })
        record_decision(db, "Kognition", "s2", DECISION_EXCLUDE, "kein Volltext")

        path = Path(build_report(db, "Kognition", reason="test", out_dir=tmp))
        text = path.read_text(encoding="utf-8")
        start = text.index("### PRISMA-Durchfluss")
        block = text[start:start + 4000]

        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        n_sources = conn.execute("select count(*) from sources").fetchone()[0]
        n_effects = conn.execute("select count(*) from study_effects").fetchone()[0]
        n_disputed = conn.execute(
            "select count(*) from study_effects where disputed = 1").fetchone()[0]
        conn.close()

        def row(pattern):
            hit = re.search(pattern, block)
            self.assertIsNotNone(hit, f"Zeile fehlt im PRISMA-Block: {pattern}")
            return int(hit.group(1))

        self.assertEqual(row(r"\| Quellen im Bestand \| (\d+) \|"), n_sources)
        self.assertEqual(row(r"\| Effektzeilen gesamt \| (\d+) \|"), n_effects)
        self.assertEqual(row(r"\| davon diskrepant[^|]*\| (\d+) \|"), n_disputed)
