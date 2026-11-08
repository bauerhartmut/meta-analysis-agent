"""E4f - RVE gegen HKJ in den sechs vom Kollaps betroffenen Gruppen.

Der Patch aus E4e behaelt mehrere Schaetzungen derselben Quelle. Das naive
HKJ-Intervall behandelt sie als unabhaengig und wird dadurch zu schmal. Hier
wird dasselbe Material cluster-robust gerechnet:

    HKJ          pool(kept)                       random effects, t-Intervall
    RVE(study)   pool_rve(sub_rows)               Cluster study_id, Fallback source
    RVE(source)  pool_rve(sub_rows, "source_id")  Cluster immer die Quelle

`sub_rows` sind die Zeilen VOR dem Kollaps - genau die abhaengigen
Schaetzungen, um die es geht. Der RVE-Punktschaetzer ist inverse-variance
fixiert, nicht random effects; verglichen werden deshalb die Intervallbreiten.

Read-only auf Kopien, keine Modellaufrufe.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/vergleiche_rve.py
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
from research_agent.meta.outcome_labels import normalize_outcome  # noqa: E402
from research_agent.meta.pooling import (                    # noqa: E402
    _collapse_same_study, _split_pool_conditions, pool, pool_rve, standardize,
)

VALIDIERUNG = ROOT / "data" / "bench" / "validierung"
OUT_JSON = VALIDIERUNG / "e4f_rve_20261108.json"
OUT_MD = VALIDIERUNG / "e4f_rve_20261108.md"

ZIELE = ("preeclampsia", "incident cardiovascular disease",
         "major adverse cardiovascular", "depressive symptoms", "frailty")


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


def standardisiere(rows: list) -> list:
    out = []
    for row in rows:
        est, se, scale, reason = standardize(row)
        if reason or se is None:
            continue
        item = dict(row)
        item.update({
            "est": float(est), "se": float(se), "scale": scale,
            "outcome_group": normalize_outcome(
                str(row.get("outcome") or "").strip() or "(kein Outcome)"),
            "adjusted": int(row.get("adjusted")
                            if row.get("adjusted") is not None else -1),
            "time_point": " ".join(str(row.get("time_point") or "").split()),
        })
        out.append(item)
    return out


def breite(analysis: dict):
    low, high = analysis.get("ci_low"), analysis.get("ci_high")
    if low is None or high is None:
        return None
    return float(high) - float(low)


def ist_ziel(name: str) -> bool:
    text = name.lower()
    return any(ziel in text for ziel in ZIELE)


def main() -> int:
    ergebnisse, fehler = [], []
    for index, path in enumerate(themen_dbs()):
        try:
            probe = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True,
                                    timeout=5)
            tables = {r[0] for r in probe.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            probe.close()
        except Exception as exc:                      # noqa: BLE001
            fehler.append({"datei": str(path), "fehler": str(exc)})
            continue
        if "study_effects" not in tables:
            continue
        rows = lies(path, index)
        groups = {}
        for row in standardisiere(rows):
            groups.setdefault((row["outcome_group"], row["scale"]), []).append(row)

        for (outcome, scale), group_rows in groups.items():
            for sub_label, sub_rows in _split_pool_conditions(group_rows):
                kept, _dropped = _collapse_same_study(sub_rows)
                hkj = pool(kept)
                if int(hkj.get("k") or 0) < 2:
                    continue
                daten = {
                    "datei": path.relative_to(ROOT).as_posix(),
                    "gruppe": f"{outcome} [{scale}]{sub_label}",
                    "k_hkj": int(hkj.get("k") or 0),
                    "k_zeilen": len(sub_rows),
                    "hkj": {
                        "pooled": hkj.get("pooled"),
                        "ci": [hkj.get("ci_low"), hkj.get("ci_high")],
                        "breite": breite(hkj),
                        "tau2": hkj.get("tau2"),
                    },
                    "rve_study": pool_rve(sub_rows),
                    "rve_source": pool_rve(sub_rows, "source_id"),
                }
                for key in ("rve_study", "rve_source"):
                    daten[key]["breite"] = breite(daten[key])
                ergebnisse.append(daten)

    for eintrag in ergebnisse:
        hkj_b = eintrag["hkj"]["breite"]
        for key in ("rve_study", "rve_source"):
            rve_b = eintrag[key]["breite"]
            eintrag[key]["faktor"] = (round(rve_b / hkj_b, 2)
                                      if hkj_b and rve_b else None)

    ziele = [e for e in ergebnisse if ist_ziel(e["gruppe"])]
    ziele.sort(key=lambda e: e["gruppe"])

    verfuegbar = [e for e in ergebnisse if e["rve_source"].get("available")]
    breiter = [e for e in verfuegbar
               if e["rve_source"]["breite"] and e["hkj"]["breite"]
               and e["rve_source"]["breite"] > e["hkj"]["breite"]]
    faktoren = sorted(e["rve_source"]["faktor"] for e in verfuegbar
                      if e["rve_source"].get("faktor"))
    median = faktoren[len(faktoren) // 2] if faktoren else None

    print(f"{len(ergebnisse)} Gruppen mit k >= 2, {len(ziele)} Zielgruppen")
    for e in ziele:
        print(f"  {e['gruppe']}: k {e['k_hkj']}/{e['k_zeilen']}, "
              f"HKJ-Breite {e['hkj']['breite']}, "
              f"RVE(source) M={e['rve_source'].get('M')} "
              f"Breite {e['rve_source'].get('breite')}")
    print(f"\nRVE(source) verfuegbar: {len(verfuegbar)}/{len(ergebnisse)}; "
          f"breiter als HKJ: {len(breiter)}; Median-Faktor {median}")
    nicht = [e for e in ergebnisse if not e["rve_source"].get("available")]
    print(f"RVE nicht verfuegbar (M<2): {len(nicht)}")
    for e in nicht:
        print(f"  {e['gruppe']}: {e['rve_source'].get('reason')}")

    ergebnis = {
        "test": "E4f-rve",
        "stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "modellaufrufe": 0,
        "tokens": 0,
        "gruppen_gesamt": len(ergebnisse),
        "zielgruppen": len(ziele),
        "rve_source_verfuegbar": len(verfuegbar),
        "rve_breiter_als_hkj": len(breiter),
        "median_faktor": median,
        "rve_nicht_verfuegbar": [
            {"gruppe": e["gruppe"], "grund": e["rve_source"].get("reason")}
            for e in nicht],
        "gruppen": ergebnisse,
        "fehler": fehler,
    }
    OUT_JSON.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    def fmt(value, digits=3):
        return "-" if value is None else f"{float(value):.{digits}f}"

    def ci_text(analysis):
        if analysis.get("ci_low") is None:
            return "-"
        return f"[{fmt(analysis['ci_low'])}; {fmt(analysis['ci_high'])}]"

    md = [
        "# E4f - RVE gegen HKJ in den betroffenen Gruppen",
        "",
        f"Stand: {time.strftime('%Y-%m-%d %H:%M')} · Modellaufrufe: 0 · Tokens: 0",
        "",
        "HKJ = `pool(kept)` nach dem Kollaps (random effects, t-Intervall).",
        "RVE = `pool_rve(sub_rows)` auf den Zeilen VOR dem Kollaps,",
        "cluster-robust (CR0, t auf M-1 df). Punktwerte sind nicht identisch",
        "definiert; verglichen werden die Intervallbreiten.",
        "",
        "## Die sechs Zielgruppen",
        "",
        "| Gruppe | k (HKJ / Zeilen) | HKJ | HKJ-Breite | RVE(study) M | "
        "RVE(study) | RVE(source) M | RVE(source) | Faktor |",
        "|---|---:|---|---:|---:|---|---:|---|---:|",
    ]
    for e in ziele:
        rs, rq = e["rve_study"], e["rve_source"]
        md.append(
            f"| {e['gruppe']} | {e['k_hkj']} / {e['k_zeilen']} | "
            f"{ci_text(e['hkj'])} | {fmt(e['hkj']['breite'])} | "
            f"{rs.get('M', 0)} | {ci_text(rs)} | {rq.get('M', 0)} | "
            f"{ci_text(rq)} | {fmt(rq.get('faktor'), 2)} |")
    md += [
        "",
        "## Alle Gruppen",
        "",
        f"- Gruppen mit k >= 2: {len(ergebnisse)}",
        f"- RVE(source) verfügbar: {len(verfuegbar)} (M >= 2 Cluster)",
        f"- RVE(source) breiter als HKJ: {len(breiter)}",
        f"- Median-Faktor RVE/HKJ: {median}",
        f"- RVE nicht verfügbar (nur ein Cluster): {len(nicht)}",
        "",
        "## Lesart",
        "",
        "Wo `RVE(source) M = 1` steht, stammen alle Zeilen aus einer Quelle:",
        "Ein cluster-robustes Intervall ist dann nicht schätzbar, weil es keine",
        "zweite unabhängige Einheit gibt. Genau diese Gruppen hat der alte",
        "Kollaps auf k = 1 reduziert; der neue Schluessel zeigt die Zeilen,",
        "aber die Unsicherheit bleibt unbeantwortbar.",
        "",
        "Wo M >= 2 und der Faktor deutlich über 1 liegt, war das naive HKJ-KI",
        "zu schmal - die Scheinpräzision aus E4e, jetzt beziffert.",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nJSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"MD:   {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
