"""Tests fuer Paket E: der Bericht darf keinen Pool behaupten, den es nicht gibt.

Strukturell geprueft, nicht per Satz-Regex: der gepoolte Abschnitt entsteht aus
dem Pool-Ergebnis. Fehlt der Pool, muss der Bericht das an der Abschnittsspitze
sagen und darf keine Zeile mit gepooltem Effekt samt Intervall enthalten.
"""

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from research_agent.database import Database
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
