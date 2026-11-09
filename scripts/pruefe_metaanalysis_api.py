"""Prueft GET /api/metaanalysis des Live-Dashboards gegen eine DB-Kopie.

Der Endpunkt rechnet `build_analysis()` direkt auf `study_effects` - kein
Orchestrator-Lauf, kein Modell, kein Netz. Der Orchestrator wird deshalb
durch ein Stub-Objekt ersetzt, das nur `db` und `current_topic` traegt; der
HTTP-Pfad (Routing, JSON-Serialisierung) ist der echte.

Geprueft wird, ob die neuen RVE-Felder durch die API kommen:
`rve.rows`, `rve.rows_collapsed`, `rve_re.available`, `rve_re.rows`.

Exit 0: alle erwarteten Felder vorhanden. Exit 1: mindestens eines fehlt
oder der Endpunkt meldet einen Fehler.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/pruefe_metaanalysis_api.py [db-pfad]
"""

import json
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VORGABE = "data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db"
MACE = "major adverse cardiovascular"


def kopie(path: Path) -> Path:
    ziel = Path(tempfile.mkdtemp(prefix="api_kopie_")) / "kopie.db"
    shutil.copy2(path, ziel)
    return ziel


def main() -> int:
    pfad = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / VORGABE
    if not pfad.is_file():
        print(f"DB nicht gefunden: {pfad}")
        return 1

    ziel = kopie(pfad)
    from research_agent.database import Database
    from research_agent.dashboard.server import DashboardServer

    db = Database(str(ziel))
    stub = SimpleNamespace(db=db, current_topic="", running=False,
                           paused=False, parallel_stats={})
    srv = DashboardServer(host="127.0.0.1", port=0)
    try:
        srv.start(stub)
        port = srv.server.server_address[1]
        url = f"http://127.0.0.1:{port}/api/metaanalysis"
        with urllib.request.urlopen(url, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    finally:
        srv.stop()
        close = getattr(db, "close", None)
        if callable(close):
            close()
        shutil.rmtree(ziel.parent, ignore_errors=True)

    print(f"GET {url}")
    print(f"topic={data.get('topic')!r} effect_rows={data.get('effect_rows')} "
          f"usable={data.get('usable')}")
    if data.get("error"):
        print(f"FEHLER im Endpunkt: {data['error']}")
        return 1

    groups = data.get("groups") or {}
    if not groups:
        print("FEHLER: keine Gruppen im Payload")
        return 1

    mit_rve = {k: g for k, g in groups.items() if (g.get("rve") or {}).get("rows") is not None}
    mit_re = {k: g for k, g in groups.items() if (g.get("rve_re") or {}).get("available")}
    print(f"Gruppen: {len(groups)}; mit rve.rows: {len(mit_rve)}; "
          f"rve_re verfuegbar: {len(mit_re)}")

    fehlt = []
    for name, g in mit_rve.items():
        rve = g.get("rve") or {}
        for feld in ("rows", "rows_collapsed", "M"):
            if rve.get(feld) is None:
                fehlt.append(f"{name}.rve.{feld}")
        re = g.get("rve_re") or {}
        if re.get("available"):
            for feld in ("rows", "rows_collapsed", "pooled", "ci_low", "ci_high"):
                if re.get(feld) is None:
                    fehlt.append(f"{name}.rve_re.{feld}")

    treffer = [k for k in groups if MACE in k.lower()]
    for name in treffer:
        g = groups[name]
        rve, re_ = g.get("rve") or {}, g.get("rve_re") or {}
        print(f"\n{name}")
        print(f"  k={g.get('k')} M={rve.get('M')} "
              f"rows={rve.get('rows')} rows_collapsed={rve.get('rows_collapsed')} "
              f"single_cluster={g.get('single_cluster')}")
        print(f"  rve: pooled={rve.get('pooled')} "
              f"ci=[{rve.get('ci_low')}, {rve.get('ci_high')}]")
        print(f"  rve_re: available={re_.get('available')} "
              f"pooled={re_.get('pooled')} "
              f"ci=[{re_.get('ci_low')}, {re_.get('ci_high')}] "
              f"tau2={re_.get('tau2')}")

    if fehlt:
        print(f"\nFEHLT ({len(fehlt)}): " + ", ".join(fehlt[:10]))
        return 1
    if not treffer:
        print("\nHinweis: MACE-Gruppe nicht im Payload gefunden")
    print("\nErgebnis: neue RVE-Felder kommen durch die API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
