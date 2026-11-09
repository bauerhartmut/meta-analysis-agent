"""Startet den Live-Dashboard-Server mit Stub-Orchestrator auf einer DB-Kopie.

Der Live-Server braucht fuer die Leseendpunkte nur `orchestrator.db` und
`orchestrator.current_topic`. Dieses Skript stellt beides bereit, damit die
Meta-Karte (`/api/metaanalysis`) im Browser gegen den vorhandenen Bestand
gerendert werden kann - ohne Modell, ohne Netz, ohne Schreibzugriff auf die
Original-DB.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/serve_dashboard_stub.py [db-pfad]

Port: DASHBOARD_PORT (Standard 8099). Laeuft bis Ctrl+C.
"""

import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VORGABE = "data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db"


def main() -> int:
    pfad = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / VORGABE
    if not pfad.is_file():
        print(f"DB nicht gefunden: {pfad}", flush=True)
        return 1

    port = int(os.environ.get("DASHBOARD_PORT", "8099"))
    ziel = Path(tempfile.mkdtemp(prefix="stub_kopie_")) / "kopie.db"
    shutil.copy2(pfad, ziel)

    from research_agent.database import Database
    from research_agent.dashboard.server import DashboardServer

    db = Database(str(ziel))
    stub = SimpleNamespace(
        db=db,
        current_topic="",
        running=False,
        paused=False,
        parallel_stats={},
        get_status=lambda: {"running": False, "paused": False, "topic": ""},
    )

    srv = DashboardServer(host="127.0.0.1", port=port)
    srv.start(stub)
    print(f"READY http://127.0.0.1:{port}", flush=True)
    print(f"DB-Kopie: {ziel} (Original unberuehrt)", flush=True)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        srv.stop()
        close = getattr(db, "close", None)
        if callable(close):
            close()
        shutil.rmtree(ziel.parent, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
