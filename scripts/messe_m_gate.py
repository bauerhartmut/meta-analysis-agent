"""E4g - welche Gruppen greift das M-Gate?

Zaehlt ueber die Themen-DBs, wie viele gepoolte Gruppen (k >= 2) nur einen
unabhaengigen Cluster haben und deshalb ihr Intervall verlieren. Read-only
auf Kopien, keine Modellaufrufe.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/messe_m_gate.py
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
OUT_JSON = VALIDIERUNG / "e4g_m_gate_20261108.json"
OUT_MD = VALIDIERUNG / "e4g_m_gate_20261108.md"


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


def main() -> int:
    gepoolt, betroffen, offen = 0, [], []
    for index, path in enumerate(sorted(
            p for p in (ROOT / "data").rglob("*.db")
            if "-usage" not in p.name and gruppe(p) == "themen")):
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
            if int(group.get("k") or 0) < 2:
                continue
            gepoolt += 1
            eintrag = {
                "datei": path.relative_to(ROOT).as_posix(),
                "gruppe": name,
                "k": int(group.get("k") or 0),
                "M": (group.get("rve") or {}).get("M"),
                "pooled": group.get("pooled"),
                "ci": [group.get("ci_low"), group.get("ci_high")],
                "single_cluster": bool(group.get("single_cluster")),
            }
            (betroffen if eintrag["single_cluster"] else offen).append(eintrag)

    print(f"{gepoolt} Gruppen mit k >= 2")
    print(f"  M-Gate greift: {len(betroffen)}")
    for e in betroffen:
        print(f"    {e['gruppe']}: k={e['k']}, M={e['M']}, pooled={e['pooled']}, "
              f"KI={e['ci']}")
    print(f"  unveraendert: {len(offen)}")
    for e in offen:
        print(f"    {e['gruppe']}: M={e['M']}, KI={e['ci']}")

    fehler = [e["gruppe"] for e in betroffen if e["ci"] != [None, None]]
    if fehler:
        print(f"FEHLER: Gate hat das KI nicht entfernt: {fehler}")
        return 3

    ergebnis = {
        "test": "E4g-m-gate",
        "stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "modellaufrufe": 0,
        "tokens": 0,
        "gruppen_k2": gepoolt,
        "gate_greift": len(betroffen),
        "unveraendert": len(offen),
        "betroffen": betroffen,
        "gruppen": betroffen + offen,
    }
    OUT_JSON.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    md = [
        "# E4g - Wirkung des M-Gates",
        "",
        f"Stand: {time.strftime('%Y-%m-%d %H:%M')} · Modellaufrufe: 0 · Tokens: 0",
        "",
        f"{gepoolt} Gruppen mit k >= 2; das Gate greift bei "
        f"**{len(betroffen)}**, {len(offen)} bleiben unveraendert.",
        "",
        "## Betroffene Gruppen (Intervall entfernt, Punktschaetzer bleibt)",
        "",
        "| Gruppe | k | M | gepoolt | KI vorher |",
        "|---|---:|---:|---:|---|",
    ]
    for e in betroffen:
        md.append(f"| {e['gruppe']} | {e['k']} | {e['M']} | {e['pooled']} | "
                  f"{e['ci']} |")
    md += [
        "",
        "Die `KI vorher`-Werte stehen hier, weil sie vor dem Gate berechnet",
        "wurden; im Ergebnis traegt die Gruppe jetzt `ci_low = ci_high = None`",
        "und `single_cluster = True`.",
        "",
        "## Unveraendert",
        "",
        "| Gruppe | M | KI |",
        "|---|---:|---|",
    ]
    for e in offen:
        md.append(f"| {e['gruppe']} | {e['M']} | {e['ci']} |")
    md += [
        "",
        "## Grenze",
        "",
        "Das Gate greift nur, wo `pool_rve` gerechnet wurde. Fehlt `rve`,",
        "bleibt der Pool unangetastet - keine Annahme ohne Messung.",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nJSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"MD:   {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
