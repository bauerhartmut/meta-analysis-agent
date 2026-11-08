"""E4e - Wirkung der Exposition im Kollaps-Schluessel.

Drei Modi, damit die Aenderung belegt und nicht behauptet wird:

    vorher     Gruppen-Zahlen mit der aktuellen Kollaps-Logik
    nachher    dasselbe nach dem lokalen Patch in `pooling.py`
    vergleich  beide JSONs nebeneinander, nur geaenderte Gruppen

Read-only auf Kopien, keine Modellaufrufe. `pooling.py` ist gitignored; der
Patch bleibt lokal und wird nie committet.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/messe_kollaps_exposition.py vorher
    .venv/bin/python.exe scripts/messe_kollaps_exposition.py nachher
    .venv/bin/python.exe scripts/messe_kollaps_exposition.py vergleich
"""

import json
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from messe_quote_luecken_bestand import kopiere, aufraeumen   # noqa: E402
from messe_effekt_duplikate import gruppe                     # noqa: E402
from research_agent.meta.pooling import build_analysis        # noqa: E402

VALIDIERUNG = ROOT / "data" / "bench" / "validierung"
MODI = ("vorher", "nachher")
MODUS = sys.argv[1] if len(sys.argv) > 1 else "vorher"


def themen_dbs() -> list:
    return sorted(p for p in (ROOT / "data").rglob("*.db")
                  if "-usage" not in p.name and gruppe(p) == "themen")


def lies(path: Path, index: int) -> list:
    dest = kopiere(path, index)
    conn = None
    try:
        conn = sqlite3.connect(dest, timeout=10)
        conn.row_factory = sqlite3.Row
        return [dict(r) for r in conn.execute("SELECT * FROM study_effects")]
    finally:
        if conn is not None:
            conn.close()
        aufraeumen(dest)


def messen() -> dict:
    ergebnisse = []
    for index, path in enumerate(themen_dbs()):
        try:
            probe = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True,
                                    timeout=5)
            tables = {r[0] for r in probe.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            probe.close()
        except Exception:                              # noqa: BLE001
            continue
        if "study_effects" not in tables:
            continue
        analysis = build_analysis(lies(path, index))
        for name, group in analysis["groups"].items():
            ergebnisse.append({
                "datei": path.relative_to(ROOT).as_posix(),
                "gruppe": name,
                "k": int(group.get("k") or 0),
                "pooled": group.get("pooled"),
                "ci_low": group.get("ci_low"),
                "ci_high": group.get("ci_high"),
                "tau2": group.get("tau2"),
                "zeilen": len(group.get("rows") or []),
            })
    return {
        "stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "modus": MODUS,
        "modellaufrufe": 0,
        "tokens": 0,
        "gruppen": ergebnisse,
    }


def vergleichen() -> int:
    vorher = json.loads((VALIDIERUNG / "e4e_vorher_20261108.json")
                        .read_text(encoding="utf-8"))
    nachher = json.loads((VALIDIERUNG / "e4e_nachher_20261108.json")
                         .read_text(encoding="utf-8"))
    a = {(g["datei"], g["gruppe"]): g for g in vorher["gruppen"]}
    b = {(g["datei"], g["gruppe"]): g for g in nachher["gruppen"]}
    keys = sorted(set(a) | set(b))
    zeilen = []
    for key in keys:
        alt, neu = a.get(key), b.get(key)
        if alt is None or neu is None:
            zeilen.append({"datei": key[0], "gruppe": key[1],
                           "nur": "vorher" if neu is None else "nachher"})
            continue
        if (alt["k"], alt["pooled"], alt["tau2"]) == (neu["k"], neu["pooled"],
                                                      neu["tau2"]):
            continue
        zeilen.append({
            "datei": key[0], "gruppe": key[1],
            "k_vorher": alt["k"], "k_nachher": neu["k"],
            "pooled_vorher": alt["pooled"], "pooled_nachher": neu["pooled"],
            "ci_vorher": [alt["ci_low"], alt["ci_high"]],
            "ci_nachher": [neu["ci_low"], neu["ci_high"]],
            "tau2_vorher": alt["tau2"], "tau2_nachher": neu["tau2"],
        })

    print(f"{len(zeilen)} von {len(keys)} Gruppen geaendert")
    for z in zeilen:
        if "nur" in z:
            print(f"  {z['gruppe']} ({z['nur']})")
            continue
        print(f"  {z['gruppe']}: k {z['k_vorher']}->{z['k_nachher']}, "
              f"pooled {z['pooled_vorher']}->{z['pooled_nachher']}")

    def zahl(value):
        return "-" if value is None else f"{float(value):.3f}"

    def ci_text(ci):
        if not ci or ci[0] is None or ci[1] is None:
            return "-"
        return f"[{float(ci[0]):.3f}; {float(ci[1]):.3f}]"

    md = [
        "# E4e - Kollaps-Schluessel mit Exposition: Wirkung",
        "",
        f"Stand: {time.strftime('%Y-%m-%d %H:%M')} · Modellaufrufe: 0 · Tokens: 0",
        "",
        "Vergleich derselben Gruppen vor und nach dem lokalen Patch. Nur",
        "Gruppen, deren k, Punktschaetzer oder tau2 sich aendern, stehen hier.",
        "",
        f"Geaendert: {len(zeilen)} von {len(keys)} Gruppen.",
        "",
        "| Gruppe | k vorher | k nachher | gepoolt vorher | 95%-KI vorher | "
        "gepoolt nachher | 95%-KI nachher |",
        "|---|---:|---:|---:|---|---:|---|",
    ]
    for z in zeilen:
        if "nur" in z:
            continue
        md.append(
            f"| {z['gruppe']} | {z['k_vorher']} | {z['k_nachher']} | "
            f"{zahl(z['pooled_vorher'])} | {ci_text(z['ci_vorher'])} | "
            f"{zahl(z['pooled_nachher'])} | {ci_text(z['ci_nachher'])} |")
    md += [
        "",
        "Lesart: Steigt k, bleibt eine Zeile erhalten, die der alte Schluessel",
        "verworfen hat. Aendert sich der Punktschaetzer, war die verworfene",
        "Zeile eine andere Exposition und nicht eine Dublette.",
    ]
    (VALIDIERUNG / "e4e_vergleich_20261108.md").write_text(
        "\n".join(md) + "\n", encoding="utf-8")
    (VALIDIERUNG / "e4e_vergleich_20261108.json").write_text(
        json.dumps({"stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "modellaufrufe": 0, "tokens": 0,
                    "geaendert": zeilen,
                    "gruppen_gesamt": len(keys)}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\nMD:   data/bench/validierung/e4e_vergleich_20261108.md")
    return 0


def main() -> int:
    if MODUS == "vergleich":
        return vergleichen()
    if MODUS not in MODI:
        print(f"Modus muss einer von {MODI} oder 'vergleich' sein")
        return 2
    ergebnis = messen()
    out = VALIDIERUNG / f"e4e_{MODUS}_20261108.json"
    out.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"{len(ergebnis['gruppen'])} Gruppen, Modus {MODUS}")
    print(f"JSON: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
