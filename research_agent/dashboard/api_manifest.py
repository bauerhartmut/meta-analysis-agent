"""Zentrale API-Routentabelle beider Dashboard-Server (Claude-Vorschlag 9).

Die zwei Server (Live-Server ``server.py`` mit Steueragent, Standalone-
Server ``standalone_server.py`` rein lesend) teilen die UI, aber bisher
nicht alle Endpunkte — das UI musste 404 als „live only“-Rätsel raten.

Diese Tabelle ist die eine Quelle:
- ``READONLY_APIS``: existieren in BEIDEN Servern mit echten Daten.
- ``CONTROL_APIS``: Steuerung (Start/Pause/Resume/Stop) und Exporte.
  Der Standalone antwortet darauf bewusst mit einer readonly-Hinweismel-
  dung statt Daten — kein Surprise-Verhalten.
- ``LIVE_ONLY_APIS``: nur der Live-Server liefert sie. Der Standalone
  beantwortet sie mit ``supported: false`` (nicht 404), sobald er das
  Manifest kennt; das UI fragt ``GET /api/capabilities`` einmal beim
  Boot und verbegrüßt die Aufrufe für diese Endpunkte, statt Poll-404
  Läufe zu erzeugen.

Die UI (``app.js``) darf nur Routen aufrufen, die hier stehen — der
Contract-Test (``test_dashboard_contract.py``) prüft genau das.
"""

READONLY_APIS = (
    # UI fragt die Sichtbarkeit beim Boot einmal ab - ohne diesen Eintrag
    # wuerde der Contract-Test die Route als unbekannt vermerken.
    "/api/capabilities",
    "/api/status",
    "/api/stats",
    "/api/hypotheses",
    "/api/hypothesis/",  # prefix; app.js: /api/hypothesis/<id>
    "/api/questions",
    "/api/sources",
    "/api/journal",
    "/api/contradictions",
    "/api/rejected",
    "/api/graph",
    "/api/sessions",
    "/api/source-analytics",
    "/api/system-health",
    "/api/errors",
    "/api/confidence-history",
    "/api/llm-stats",
    "/api/health",
)

CONTROL_APIS = (
    "/api/start",
    "/api/pause",
    "/api/resume",
    "/api/stop",
    "/api/dataset",
    "/api/finetune",
)

LIVE_ONLY_APIS = (
    "/api/parallel-stats",
    "/api/coverage",
    "/api/metaanalysis",
)


def capabilities(server: str) -> dict:
    """Payload für GET /api/capabilities — je Server ehrlich gefüllt."""
    base = {
        "server": server,
        "readonly_apis": list(READONLY_APIS),
        "control_apis": list(CONTROL_APIS),
    }
    if server == "standalone":
        base["live_only"] = list(LIVE_ONLY_APIS)
    else:
        base["all_apis"] = (
            list(READONLY_APIS) + list(CONTROL_APIS) + list(LIVE_ONLY_APIS))
    return base
