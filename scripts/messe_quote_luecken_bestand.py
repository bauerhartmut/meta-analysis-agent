"""E4b - wie oft steht im Bestand mehr CI-Klammern in der Quote als Zeilen?

Read-only Diagnose nach der Projektregel: Jede Datenbank wird zuerst kopiert
(auch eine mitgeschriebene WAL), gelesen wird nur die Kopie, danach wird sie
geloescht. Keine Modellaufrufe, keine Schreibzugriffe auf eine Originaldatei.

Gemessen wird mit `quote_gaps.audit_rows`: Zeilen einer Quelle werden nach
ihrer Quote gruppiert; nennt eine Quote mehr Konfidenzintervalle als es Zeilen
aus ihr gibt, ist das eine Luecke.

Die Gruppen werden getrennt ausgewiesen, weil derselbe Inhalt mehrfach als
Datei vorliegt (z.B. `data/research-*.db` und `data/bench/regreports/...`).
Eine Summe ueber alle Dateien ist deshalb keine Fallzahl.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/messe_quote_luecken_bestand.py
"""

import json
import shutil
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.meta.quote_gaps import audit_rows, summarize  # noqa: E402

VALIDIERUNG = ROOT / "data" / "bench" / "validierung"
KOPIEN = VALIDIERUNG / "_e4_kopien"
OUT_JSON = VALIDIERUNG / "e4_bestand_20261108.json"
OUT_MD = VALIDIERUNG / "e4_bestand_20261108.md"

WANTED = ("quote", "effect", "ci_low", "ci_high", "rejection_reason",
          "source_id", "outcome", "extractor")


def gruppe(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("data/bench/"):
        return "pipeline"
    if rel.startswith("data/backups/") or rel.startswith("data/simulations/"):
        return "sonstige"
    return "themen"


def kopiere(path: Path, index: int) -> Path:
    """Dateikopie inklusive nicht-leerer WAL, damit der Stand konsistent ist."""
    KOPIEN.mkdir(parents=True, exist_ok=True)
    dest = KOPIEN / f"{index:03d}_{path.name}"
    shutil.copy2(path, dest)
    for suffix in ("-wal", "-shm"):
        side = Path(str(path) + suffix)
        if side.exists() and side.stat().st_size:
            shutil.copy2(side, Path(str(dest) + suffix))
    return dest


def aufraeumen(dest: Path) -> None:
    for suffix in ("", "-wal", "-shm"):
        Path(str(dest) + suffix).unlink(missing_ok=True)


def messe(path: Path, index: int) -> dict:
    dest = kopiere(path, index)
    try:
        conn = sqlite3.connect(dest, timeout=10)
        conn.row_factory = sqlite3.Row
        columns = {r[1] for r in conn.execute("PRAGMA table_info(study_effects)")}
        cols = [c for c in WANTED if c in columns]
        sql = "SELECT " + ", ".join(f'"{c}"' for c in cols) + " FROM study_effects"
        rows = [dict(r) for r in conn.execute(sql)]
        conn.close()
    finally:
        aufraeumen(dest)

    by_source = {}
    for row in rows:
        by_source.setdefault(str(row.get("source_id") or ""), []).append(row)

    counts = {"quotes": 0, "ok": 0, "luecken": 0, "ohne_zeile": 0,
              "nicht_pruefbar": 0, "tabelle": 0, "zeilen": 0,
              "intervalle": 0, "fehlende_intervalle": 0}
    for source_rows in by_source.values():
        part = summarize(audit_rows(source_rows))
        for key in counts:
            counts[key] += part[key]

    return {
        "datei": path.relative_to(ROOT).as_posix(),
        "gruppe": gruppe(path),
        "spalten": len(columns),
        "zeilen_gesamt": len(rows),
        "mit_quote": sum(1 for r in rows if str(r.get("quote") or "").strip()),
        "quellen": len(by_source),
        "zaehlung": counts,
    }


def main() -> int:
    ergebnisse = []
    fehler = []
    for index, path in enumerate(sorted((ROOT / "data").rglob("*.db"))):
        if "-usage" in path.name:
            continue
        try:
            conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True,
                                   timeout=5)
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            conn.close()
        except Exception as exc:                      # noqa: BLE001
            fehler.append({"datei": path.relative_to(ROOT).as_posix(),
                           "fehler": f"{type(exc).__name__}: {exc}"})
            continue
        if "study_effects" not in tables:
            continue
        try:
            ergebnisse.append(messe(path, index))
        except Exception as exc:                      # noqa: BLE001
            fehler.append({"datei": path.relative_to(ROOT).as_posix(),
                           "fehler": f"{type(exc).__name__}: {exc}"})

    gruppen = {}
    for eintrag in ergebnisse:
        bucket = gruppen.setdefault(eintrag["gruppe"], {
            "dateien": 0, "zeilen": 0, "mit_quote": 0,
            "quotes": 0, "ok": 0, "luecken": 0, "ohne_zeile": 0,
            "nicht_pruefbar": 0, "tabelle": 0, "fehlende_intervalle": 0,
        })
        bucket["dateien"] += 1
        bucket["zeilen"] += eintrag["zeilen_gesamt"]
        bucket["mit_quote"] += eintrag["mit_quote"]
        for key in ("quotes", "ok", "luecken", "ohne_zeile", "nicht_pruefbar",
                    "tabelle", "fehlende_intervalle"):
            bucket[key] += eintrag["zaehlung"][key]

    print(f"{len(ergebnisse)} DBs mit study_effects, {len(fehler)} Fehler")
    for name in ("themen", "pipeline", "sonstige"):
        b = gruppen.get(name)
        if not b:
            continue
        print(f"\n{name}: {b['dateien']} Dateien, {b['zeilen']} Zeilen, "
              f"{b['quotes']} Quotes")
        print(f"  ok {b['ok']}, Luecken {b['luecken']}, ohne Zeile "
              f"{b['ohne_zeile']}, nicht pruefbar {b['nicht_pruefbar']}, "
              f"Tabelle {b['tabelle']}, "
              f"fehlende Intervalle {b['fehlende_intervalle']}")

    luecken = [e for e in ergebnisse if e["zaehlung"]["luecken"]]
    luecken.sort(key=lambda e: -e["zaehlung"]["luecken"])
    print("\nDBs mit Luecken:")
    for eintrag in luecken[:20]:
        z = eintrag["zaehlung"]
        print(f"  {z['luecken']:4d} Luecken / {z['quotes']:4d} Quotes  "
              f"{eintrag['datei']}")

    ergebnis = {
        "test": "E4b-bestand",
        "stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "modellaufrufe": 0,
        "tokens": 0,
        "arbeitsweise": "Dateikopie je DB, gelesen wird nur die Kopie, "
                        "Original nur read-only geoeffnet (Schema-Check)",
        "gruppen": gruppen,
        "dateien": ergebnisse,
        "fehler": fehler,
    }
    OUT_JSON.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    md = [
        "# E4b - Luecken im Bestand: mehr Intervalle in der Quote als Zeilen",
        "",
        f"Stand: {time.strftime('%Y-%m-%d %H:%M')} · Modellaufrufe: 0 · Tokens: 0",
        "",
        "Read-only: Jede DB wurde kopiert, gelesen wurde die Kopie, danach",
        "geloescht. Das Original wurde nur fuer den Schema-Check read-only",
        "geoeffnet.",
        "",
        "## Gruppen (getrennt, weil derselbe Inhalt mehrfach als Datei vorliegt)",
        "",
        "| Gruppe | Dateien | Zeilen | Quotes | ok | Luecken | ohne Zeile | "
        "nicht pruefbar | Tabelle |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in ("themen", "pipeline", "sonstige"):
        b = gruppen.get(name)
        if not b:
            continue
        md.append(f"| {name} | {b['dateien']} | {b['zeilen']} | {b['quotes']} | "
                  f"{b['ok']} | {b['luecken']} | {b['ohne_zeile']} | "
                  f"{b['nicht_pruefbar']} | {b['tabelle']} |")
    md += [
        "",
        "## Dateien mit Luecken",
        "",
        "| Luecken | Quotes | Datei |",
        "|---:|---:|---|",
    ]
    for eintrag in luecken:
        z = eintrag["zaehlung"]
        md.append(f"| {z['luecken']} | {z['quotes']} | `{eintrag['datei']}` |")
    if not luecken:
        md.append("| 0 | - | keine |")
    md += [
        "",
        "## Einordnung",
        "",
        "`Tabelle` ist der Normalfall der Extraktion: Eine Tabellenzeile mischt",
        "Arm-Mittelwerte mit CI und den Effekt nebeneinander, ohne Kopfzeile ist",
        "keine Klammer sicher ein Effektintervall. Solche Quotes werden nicht",
        "beurteilt (dieselbe Grenze wie E1), nicht als Luecke gezaehlt.",
        "`nicht pruefbar` bleibt fuer Fliesstext ohne CI-Angabe. Die Pruefung",
        "meldet eine Luecke nur, wenn die Anzahl der Intervalle die Anzahl der",
        "Zeilen uebersteigt.",
        "",
        "Die Summe ueber alle Dateien ist keine Fallzahl: Themen-DBs liegen",
        "teilweise doppelt (Original und `bench/regreports`), Pipeline-DBs sind",
        "Zwischenstaende derselben Laeufe.",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nJSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"MD:   {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
