"""Ein Fehler in der Zieldefinition darf nicht wie eine leere Auswertung aussehen.

Der Betriebstest vom 2026-11-09 zeigte: Eine fehlerhafte Zieldefinition
(``review_targets.outcomes`` als Liste von Strings statt Objekten mit
``label``) fuehrte zu HTTP 200 mit ``groups: {}`` und einem ``error``-Feld im
Body. Im Dashboard sah das aus wie "keine Studien" - der Unterschied zwischen
einer Stoerung und einer duennen Datenlage war nur im Body erkennbar.

Dieser Test haelt fest, dass der Fall als 500 ankommt, waehrend ein intaktes
Ziel und ein Thema ohne Ziele weiterhin 200 liefern. Echter Serverstart auf
einer temporaeren Datei-DB, damit der HTTP-Pfad geprueft wird und nicht nur
der Rueckgabewert.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from research_agent.dashboard.server import DashboardServer
from research_agent.database import Database


class MetaanalysisFehlerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="meta_error_")
        self.db = Database(os.path.join(self.tmp, "t.db"))
        self.srv = None

    def tearDown(self):
        if self.srv is not None:
            self.srv.stop()
        close = getattr(self.db, "close", None)
        if callable(close):
            close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _start(self, topic, targets=None):
        if targets is not None:
            self.db.save_review_targets(topic, targets)
        stub = SimpleNamespace(
            db=self.db, current_topic=topic, running=False, paused=False,
            parallel_stats={},
        )
        self.srv = DashboardServer(host="127.0.0.1", port=0)
        self.srv.start(stub)
        port = self.srv.server.server_address[1]
        return f"http://127.0.0.1:{port}/api/metaanalysis"

    def test_kaputte_zieldefinition_kommt_als_500(self):
        url = self._start("thema", {"outcomes": ["kein objekt"]})
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(url, timeout=30)
        self.assertEqual(ctx.exception.code, 500)
        body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertIn("error", body)
        self.assertEqual(body.get("groups"), {})

    def test_intakte_zieldefinition_bleibt_200(self):
        url = self._start(
            "thema", {"outcomes": [{"label": "x", "aliases": []}]})
        with urllib.request.urlopen(url, timeout=30) as response:
            self.assertEqual(response.status, 200)
            body = json.loads(response.read().decode("utf-8"))
        self.assertNotIn("error", body)

    def test_ohne_thema_bleibt_200(self):
        url = self._start("")
        with urllib.request.urlopen(url, timeout=30) as response:
            self.assertEqual(response.status, 200)


if __name__ == "__main__":
    unittest.main()
