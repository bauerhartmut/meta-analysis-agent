"""Zwei Betriebsfragen aus betriebspruefung_matrix_20261109.md, lokal geprueft.

Test A - Reagiert /api/metaanalysis auf current_topic?
  Derselbe Server, drei Zustaende: ohne Thema, mit Thema 1, mit einem zweiten
  Thema, dessen Ziel auf ein Outcome zeigt, das Thema 1 nicht fuehrt.
  Zusaetzlich wird eine Effektzeile mit einem Outcome angelegt, den keines der
  beiden Themen kennt.

Test B - Verfaelscht gleichzeitiges Schreiben das Lesen?
  200 Effektzeilen schreiben, waehrend 200 GETs auf /api/metaanalysis laufen,
  auf einer DB-Kopie mit WAL.

Beide Tests laufen auf Kopien; die Original-DB wird nur gelesen. Kein Netz,
kein Modellaufruf.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/pruefe_betrieb_20261109.py --beide
    .venv/bin/python.exe scripts/pruefe_betrieb_20261109.py --themen
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sqlite3
import statistics
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VORGABE = "data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db"
THEMA_2 = "Betriebstest: zweites Thema ohne eigene Effektzeilen"


def kopie(path: Path) -> Path:
    ziel = Path(tempfile.mkdtemp(prefix="betrieb_")) / "kopie.db"
    shutil.copy2(path, ziel)
    return ziel


def starte(db) -> tuple[object, SimpleNamespace, str]:
    from research_agent.dashboard.server import DashboardServer

    stub = SimpleNamespace(
        db=db, current_topic="", running=False, paused=False, parallel_stats={},
        get_status=lambda: {"running": False, "paused": False, "topic": ""},
    )
    srv = DashboardServer(host="127.0.0.1", port=0)
    srv.start(stub)
    port = srv.server.server_address[1]
    return srv, stub, f"http://127.0.0.1:{port}/api/metaanalysis"


def hole(url: str, timeout: float = 120.0) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def thema_aus_db(pfad: Path) -> str:
    conn = sqlite3.connect(pfad)
    try:
        row = conn.execute(
            "SELECT topic FROM research_sessions WHERE topic != '' LIMIT 1"
        ).fetchone()
        if row:
            return row[0]
        row = conn.execute("SELECT topic FROM review_targets LIMIT 1").fetchone()
        return row[0] if row else ""
    finally:
        conn.close()


def test_themen(pfad: Path) -> int:
    thema_1 = thema_aus_db(pfad)
    if not thema_1:
        print("FEHLER: kein Thema in der Kopie gefunden")
        return 1

    from research_agent.database import Database

    ziel = kopie(pfad)
    db = Database(str(ziel))
    srv, stub, url = starte(db)
    try:
        conn = sqlite3.connect(ziel)
        try:
            quellen = [r[0] for r in conn.execute(
                "SELECT id FROM sources LIMIT 3").fetchall()]
            jetzt = dt.datetime.now(dt.timezone.utc).isoformat()
            for i, source_id in enumerate(quellen):
                conn.execute(
                    "INSERT INTO screening (id, topic, source_id, decision, reason,"
                    " decided_by, created_at) VALUES (?,?,?,?,?,?,?)",
                    (f"bt_screen_{i}", THEMA_2, source_id, "exclude",
                     "Betriebstest", "test", jetzt),
                )
            conn.commit()
        finally:
            conn.close()

        # Eine Effektzeile, deren Outcome zu keinem der beiden Themen gehoert.
        jetzt = dt.datetime.now(dt.timezone.utc).isoformat()
        db.save_study_effect({
            "id": "bt_effect_ohne_thema",
            "source_id": quellen[0] if quellen else "x",
            "outcome": "betriebstest ohne thema",
            "outcome_key": "betriebstest ohne thema",
            "effect_type": "md", "effect": 0.5, "se": 0.1, "ci_level": 0.95,
            "design": "randomized controlled trial",
            "quote": "effect 0.50 (unit: min)", "quote_start": 0, "quote_end": 24,
            "disputed": 0, "rejection_reason": "", "created_at": jetzt,
        })

        stub.current_topic = ""
        ohne = hole(url)
        stub.current_topic = thema_1
        eins = hole(url)

        g_ohne = ohne.get("groups") or {}
        g1 = eins.get("groups") or {}
        kandidat_gruppe = next(
            (k for k in g_ohne
             if k not in g1 and "betriebstest" not in k.lower()),
            None,
        )
        # Gruppennamen tragen ein Merkmalssuffix ("[log_ratio]"); das Ziel
        # braucht den reinen Label.
        kandidat = (kandidat_gruppe or "").rsplit(" [", 1)[0] or None

        # Thema 2 bekommt ein Ziel, das auf ein vorhandenes Outcome zeigt.
        conn = sqlite3.connect(ziel)
        try:
            payload = json.dumps({
                "version": "meta-targets/2",
                "question": THEMA_2,
                "population": "Adults",
                "comparison": "Betriebstest",
                "outcomes": ([{
                    "label": kandidat,
                    "aliases": [],
                    "direction": "higher = worse",
                    "scale": "hr",
                }] if kandidat else []),
                "exclusion": [],
                "created_at": jetzt,
            })
            conn.execute(
                "INSERT INTO review_targets (topic, payload, created_at) VALUES (?,?,?)",
                (THEMA_2, payload, jetzt),
            )
            conn.commit()
        finally:
            conn.close()

        stub.current_topic = THEMA_2
        zwei = hole(url)
        g2 = zwei.get("groups") or {}

        exotisch = [k for k in g_ohne if "betriebstest" in k.lower()]

        print("Test A - current_topic in drei Zustaenden")
        print(f"  Thema 1: {thema_1!r}")
        print(f"  Thema 2: {THEMA_2!r}, Ziel: {kandidat!r}")
        print(f"  Gruppen ohne Thema: {len(g_ohne)}")
        print(f"  Gruppen Thema 1: {len(g1)} {sorted(g1)[:3]}")
        print(f"  Gruppen Thema 2: {len(g2)} {sorted(g2)[:3]}")
        print(f"  Outcome ohne Themenbezug, sichtbar ohne Thema: {exotisch}")
        print(f"  PRISMA Thema 1: {eins.get('prisma')}")
        print(f"  PRISMA Thema 2: {zwei.get('prisma')}")
        print(f"  off_target: ohne {len(ohne.get('off_target') or [])}, "
              f"Thema 1 {len(eins.get('off_target') or [])}, "
              f"Thema 2 {len(zwei.get('off_target') or [])}")
        print(f"  excluded: ohne {len(ohne.get('excluded') or [])}, "
              f"Thema 1 {len(eins.get('excluded') or [])}, "
              f"Thema 2 {len(zwei.get('excluded') or [])}")

        fehler = 0
        for name, payload_ in (("ohne Thema", ohne), ("Thema 1", eins),
                               ("Thema 2", zwei)):
            if payload_.get("error"):
                print(f"  FEHLER {name}: {payload_['error']}")
                fehler += 1
        if not g_ohne or not g1:
            print("  FEHLER: leere Gruppenliste")
            fehler += 1
        if kandidat and not g2:
            print("  HINWEIS: Thema 2 hat ein Ziel, aber keine Gruppe mit k >= 2; "
                  "eine einzelne Zielzeile bildet keinen Pool")
        if zwei.get("prisma") == eins.get("prisma") and len(g2) == len(g1):
            print("  FEHLER: Thema 2 aendert die Antwort nicht")
            fehler += 1
        if not (0 < len(g1) < len(g_ohne)):
            print("  FEHLER: Thema 1 filtert die Gruppen nicht")
            fehler += 1
        if set(g1) - set(g_ohne):
            print("  HINWEIS: Gruppennamen unter Thema 1 weichen von der Ansicht "
                  "ohne Thema ab (das Ziel-Label wird vorangestellt)")
        print(f"  Ergebnis: {'OK' if fehler == 0 else 'FEHLER'}")
        return fehler
    finally:
        srv.stop()
        close = getattr(db, "close", None)
        if callable(close):
            close()
        shutil.rmtree(ziel.parent, ignore_errors=True)


def test_nebenlaeufig(pfad: Path, n: int) -> int:
    from research_agent.database import Database

    ziel = kopie(pfad)
    db = Database(str(ziel))
    srv, stub, url = starte(db)
    schreib_fehler: list[str] = []
    schreib_ok = 0
    fertig = threading.Event()

    conn = sqlite3.connect(ziel)
    try:
        quellen = [r[0] for r in conn.execute("SELECT id FROM sources LIMIT 20")]
    finally:
        conn.close()

    def schreiber() -> None:
        nonlocal schreib_ok
        wdb = Database(str(ziel))
        for i in range(n):
            try:
                wdb.save_study_effect({
                    "id": f"bt_write_{i}",
                    "source_id": quellen[i % len(quellen)] if quellen else "x",
                    "outcome": "betriebstest schreiblast",
                    "outcome_key": "betriebstest schreiblast",
                    "effect_type": "md", "effect": -1.0, "se": 0.5,
                    "ci_level": 0.95,
                    "design": "randomized controlled trial",
                    "quote": "effect -1.00 (unit: min)",
                    "quote_start": 0, "quote_end": 24,
                    "disputed": 0, "rejection_reason": "",
                    "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                })
                schreib_ok += 1
            except Exception as exc:  # noqa: BLE001 - Fehler werden gezaehlt
                schreib_fehler.append(f"{type(exc).__name__}: {exc}")
        fertig.set()

    start = time.perf_counter()
    thread = threading.Thread(target=schreiber, daemon=True)
    thread.start()

    lese_ok = 0
    lese_fehler: list[str] = []
    latenzen: list[float] = []
    versuche = 0
    while not fertig.is_set() or versuche < n:
        versuche += 1
        t0 = time.perf_counter()
        try:
            data = hole(url, timeout=120.0)
            if data.get("error"):
                lese_fehler.append(f"payload error: {data['error']}")
            else:
                lese_ok += 1
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            lese_fehler.append(f"{type(exc).__name__}: {exc}")
        latenzen.append((time.perf_counter() - t0) * 1000.0)
        if versuche >= n * 4:
            break

    thread.join(timeout=120)
    dauer = time.perf_counter() - start

    conn = sqlite3.connect(ziel)
    try:
        geschrieben = conn.execute(
            "SELECT COUNT(*) FROM study_effects WHERE id LIKE 'bt_write_%'"
        ).fetchone()[0]
    finally:
        conn.close()

    srv.stop()
    close = getattr(db, "close", None)
    if callable(close):
        close()
    shutil.rmtree(ziel.parent, ignore_errors=True)

    print("Test B - Schreiben waehrend Lesen")
    print(f"  Schreibvorgaenge: {schreib_ok}/{n} ok, {len(schreib_fehler)} Fehler")
    print(f"  Lesevorgaenge: {lese_ok}/{versuche} ok, {len(lese_fehler)} Fehler")
    print(f"  Zeilen in der Kopie: {geschrieben}")
    print(f"  Dauer: {dauer:.1f} s")
    if latenzen:
        geordnet = sorted(latenzen)
        p95 = geordnet[max(0, int(len(geordnet) * 0.95) - 1)]
        print(f"  Latenz min/median/p95/max: {min(latenzen):.0f} / "
              f"{statistics.median(latenzen):.0f} / {p95:.0f} / "
              f"{max(latenzen):.0f} ms")
    for text in (schreib_fehler + lese_fehler)[:5]:
        print(f"  FEHLER {text}")

    gesperrt = any("locked" in t.lower() for t in schreib_fehler + lese_fehler)
    print(f"  'database is locked': {gesperrt}")
    fehler_gesamt = len(schreib_fehler) + len(lese_fehler) + (n - geschrieben)
    print(f"  Ergebnis: {'OK' if fehler_gesamt == 0 else 'FEHLER'}")
    return 1 if fehler_gesamt else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("db", nargs="?", default=VORGABE)
    parser.add_argument("--themen", action="store_true")
    parser.add_argument("--nebenlaeufig", action="store_true")
    parser.add_argument("--beide", action="store_true")
    parser.add_argument("--n", type=int, default=200)
    args = parser.parse_args()

    pfad = Path(args.db)
    if not pfad.is_absolute():
        pfad = ROOT / pfad
    if not pfad.is_file():
        print(f"DB nicht gefunden: {pfad}")
        return 1

    codes = []
    if args.themen or args.beide:
        codes.append(test_themen(pfad))
    if args.nebenlaeufig or args.beide:
        codes.append(test_nebenlaeufig(pfad, args.n))
    if not codes:
        parser.print_help()
        return 2
    return 0 if all(c == 0 for c in codes) else 1


if __name__ == "__main__":
    raise SystemExit(main())
