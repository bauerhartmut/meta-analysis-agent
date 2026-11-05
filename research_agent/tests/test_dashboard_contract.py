"""Contract-Test: Server-Dualität per gemeinsamer Routentabelle.

Claude-Vorschlag 9: Zwei Server teilen die UI, aber nicht alle Endpunkte.
Dieser Test hindert das Steinwurf-Wiederauftreten:
- Beide Server beantworten ``GET /api/capabilities`` aus EINER Quelle
  (api_manifest.py).
- Jede Route, die die UI (``app.js``) aufruft, ist im Manifest bekannt
  (readonly / control / live-only) - sonst wuerde das UI ins Blindpdf-Raten
  über 404 return.
- Der Standalone antwortet für live-only-Endpunkte mit ``supported:false``
  statt Daten oder 404.
Der Test ist statisch (Quelltext-Analyse, kein Serverstart) und bleibt
schnell - echte 200er-Lauefe laufen im Dashboard-Handcheck.
"""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from research_agent.dashboard.api_manifest import (
    READONLY_APIS, CONTROL_APIS, LIVE_ONLY_APIS, capabilities,
)

DASH = os.path.join(os.path.dirname(__file__), "..", "dashboard")
SERVER_LIVE = os.path.join(DASH, "server.py")
SERVER_STANDALONE = os.path.join(DASH, "standalone_server.py")
APP_JS = os.path.join(DASH, "templates", "app.js")

_MANIFEST_ROUTES = set(READONLY_APIS) | set(CONTROL_APIS) | set(LIVE_ONLY_APIS)


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _app_js_routes():
    text = _read(APP_JS)
    hits = set(re.findall(r"/api/[a-zA-Z-]+(?:/\$\{[^}]+\})?", text))
    routes = set()
    for hit in hits:
        # Der Praefix-Endpunkt wird in app.js OHNE Schraegstrich notiert
        # (API + '/api/hypothesis/' + id) - normalisiere auf die Manifest-
        # Form mit trailing slash.
        if hit.rstrip("/") == "/api/hypothesis":
            routes.add("/api/hypothesis/")
        elif not hit.endswith("/"):
            routes.add(hit)
    return routes


class TestManifestIntegrity(unittest.TestCase):
    def test_capability_standalone_markiert_live_only(self):
        caps = capabilities("standalone")
        self.assertEqual(caps["server"], "standalone")
        self.assertEqual(set(caps["live_only"]), set(LIVE_ONLY_APIS))
        self.assertNotIn("all_apis", caps)

    def test_capability_live_listet_alles(self):
        caps = capabilities("live")
        self.assertEqual(caps["server"], "live")
        self.assertEqual(
            set(caps["all_apis"]),
            set(READONLY_APIS) | set(CONTROL_APIS) | set(LIVE_ONLY_APIS))

    def test_keine_route_doppelt_vergeben(self):
        # Ein Endpunkt darf nicht gleichzeitig readonly UND live-only
        # sein (sonst ratet das UI in die falsche Schicht).
        self.assertFalse(set(READONLY_APIS) & set(LIVE_ONLY_APIS))
        self.assertFalse(set(CONTROL_APIS) & set(LIVE_ONLY_APIS))
        self.assertFalse(set(READONLY_APIS) & set(CONTROL_APIS))


class TestServerKohaerenz(unittest.TestCase):
    def test_beide_server_beantworten_capabilities(self):
        live = _read(SERVER_LIVE)
        standalone = _read(SERVER_STANDALONE)
        self.assertIn("/api/capabilities", live)
        self.assertIn("/api/capabilities", standalone)
        self.assertIn("api_manifest", standalone)

    def test_standalone_antwortet_live_only_ehrlich_nicht_404(self):
        text = _read(SERVER_STANDALONE)
        self.assertIn("_LIVE_ONLY_APIS", text)
        self.assertIn("\"supported\": False", text)

    def test_live_server_hat_alle_readonly_routes(self):
        text = _read(SERVER_LIVE)
        for route in READONLY_APIS:
            if route == "/api/hypothesis/":
                self.assertIn("/api/hypothesis/", text)
            else:
                self.assertIn(f'"{route}"', text)


class TestAppJsContract(unittest.TestCase):
    def test_jede_app_js_route_ist_im_manifest(self):
        routes = _app_js_routes()
        unknown = sorted(routes - _MANIFEST_ROUTES)
        self.assertEqual(
            unknown, [],
            f"app.js ruft Ende nicht aus dem Manifest: {unknown}")

    def test_app_js_fraegt_capabilities_und_schirm(self):
        text = _read(APP_JS)
        self.assertIn("/api/capabilities", text)
        self.assertIn("liveOnly('/api/parallel-stats')", text)
        self.assertIn("liveOnly('/api/coverage')", text)
        self.assertIn("liveOnly('/api/metaanalysis')", text)


if __name__ == "__main__":
    unittest.main()
