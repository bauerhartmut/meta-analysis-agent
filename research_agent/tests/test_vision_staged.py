"""Gestaffelte Doppelleitung (Claude-Vorschlag 4): Ganzseite vs. Haelften.

Zumo, dass die zweite Lesung NICHT aus derselben Rasterung liest (kor-
relierte Naemlich-Fehler): Pass A Ganzseite, Pass B Ober- + Unterhaelfte
in Lesereihenfolge. Zeilenanzahl-Stand: eine Halblage schneidet Zeile
weg = ganze Seite disputed, genau wie bei compare_double_read.
"""

import tempfile

import asyncio
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from research_agent.research.vision_table import (
    compare_double_read, evidence_from_staged, png_bytes, read_double_staged,
    _split_halves,
)


class _Reader:
    """Liefert je Aufruf die naechste Lesung aus einer FIFO-Tabelle.

    Reihenfolge deterministisch: [Ganzseite, Oberhaelfte, Unterhaelfte]
    fuer die gestaffelte Lesung. Konvention: eine Zeile taucht NUR in der
    Bildhaelfte auf, in der sie auch liegt - so verhaelt sich das echte
    Modell auf geschnittenen Bildern auch.
    """

    def __init__(self, queue, model_name="fake"):
        self._queue = [list(q) for q in queue]
        self.model_name = model_name

    async def read_once(self, image_png):
        rows = self._queue.pop(0) if self._queue else []
        return [dict(r) for r in rows]


def _fake_array(height=400, width=100):
    return np.zeros((height, width, 3), dtype=np.uint8)


class TestSplitHalves(unittest.TestCase):
    def test_halbierung_hoehe(self):
        arr = _fake_array(400)
        upper, lower = _split_halves(arr)
        self.assertEqual(upper.shape[0], 200)
        self.assertEqual(lower.shape[0], 200)


def _full_row(label, raw_eff, raw_se, eff, sev):
    """Konvention: jede Zahl ist belegt (auch CI) - keine Halblesung."""
    return {"label": label, "effect": eff, "se": sev, "ci_low": -0.2,
            "ci_high": 0.8, "raw_effect": raw_eff, "raw_se": raw_se,
            "raw_ci_low": "-0,2", "raw_ci_high": "0,8"}


class TestStagedLesung(unittest.TestCase):
    def test_gerade_zahlen_verified(self):
        a_row = _full_row("a", "0,53", "0,1", 0.53, 0.1)
        b_row = _full_row("b", "0.7", "0.2", 0.7, 0.2)
        # Queues: Ganzseite [a,b] | Oberhaelfte [a] | Unterhaelfte [b]
        reader = _Reader([[dict(a_row), dict(b_row)],
                          [dict(a_row)], [dict(b_row)]])
        confirmed, counts = asyncio.get_event_loop_policy().new_event_loop() \
            .run_until_complete(read_double_staged(_fake_array(), reader))
        self.assertEqual(len(confirmed), 2)
        self.assertFalse(any(counts))
        self.assertEqual(confirmed[0].get("_vision_status"), "verified")

    def test_haelfte_schneidet_zeile_weg_disputed(self):
        a = [_full_row("a", "0,53", "0,1", 0.53, 0.1),
             _full_row("b", "0.7", "0.2", 0.7, 0.2)]
        b = [_full_row("a", "0,53", "0,1", 0.53, 0.1)]
        reader = _Reader([[dict(r) for r in a], [dict(r) for r in b], []])
        confirmed, counts = asyncio.get_event_loop_policy().new_event_loop() \
            .run_until_complete(read_double_staged(_fake_array(), reader))
        # Zeilenanzahl-Divergenz: nichts wird paarenweise geduldet
        self.assertEqual(confirmed, [])
        self.assertEqual(counts, [3])  # 2 + 1, wie beim Ganzen

    def test_evidence_from_staged_traegt_belegkette(self):
        row = [_full_row("a", "0,53", "0,1", 0.53, 0.1)]
        reader = _Reader([[dict(r) for r in row], [dict(r) for r in row]], [])
        # read_table_evidence-Hashes lesen echte Bytes: kleines Fake-PDF
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.close()
        try:
            ev = asyncio.get_event_loop_policy().new_event_loop() \
                .run_until_complete(evidence_from_staged(
                    tmp.name, 1, _fake_array(), reader))
        finally:
            os.unlink(tmp.name)
        self.assertEqual(ev["evidence_kind"], "vision_read")
        self.assertEqual(ev["second_reading"], "haelften")
        self.assertIn("pdf_hash", ev)
        self.assertIn("crop_hash", ev)


if __name__ == "__main__":
    unittest.main()
