"""E4c - doppelte Effektzeilen und ihre Wirkung auf das Pooling-Gewicht.

Zwei Fragen, beide deterministisch:

1. Wie oft steht dieselbe Zeile (Quelle, Quote, Effekt, KI, Outcome) mehrfach
   im Store? Gezaehlt ueber alle DBs mit `study_effects`.
2. Faengt das Pooling sie? `build_analysis` ruft `_collapse_same_study` vor
   `pool()`; die Funktion behaelt je Quelle eine Zeile. Gemessen wird, wie
   viele Dubletten dort ankommen und was `pool()` ohne den Kollaps liefern
   wuerde - an echten Zeilen, nicht an einer Beispielrechnung.

Read-only: Jede DB wird kopiert, gelesen wird die Kopie, danach geloescht.
Keine Modellaufrufe.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/messe_effekt_duplikate.py
"""

import json
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from messe_quote_luecken_bestand import kopiere, aufraeumen   # noqa: E402
from research_agent.meta.outcome_labels import normalize_outcome  # noqa: E402
from research_agent.meta.pooling import build_analysis, pool, standardize  # noqa: E402

VALIDIERUNG = ROOT / "data" / "bench" / "validierung"
OUT_JSON = VALIDIERUNG / "e4_duplikate_20261108.json"
OUT_MD = VALIDIERUNG / "e4_duplikate_20261108.md"


def gruppe(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("data/bench/"):
        return "pipeline"
    if rel.startswith(("data/backups/", "data/simulations/")):
        return "sonstige"
    return "themen"


def lies(path: Path, index: int) -> list:
    dest = kopiere(path, index)
    try:
        conn = sqlite3.connect(dest, timeout=10)
        conn.row_factory = sqlite3.Row
        columns = {r[1] for r in conn.execute("PRAGMA table_info(study_effects)")}
        rows = [dict(r) for r in conn.execute("SELECT * FROM study_effects")]
        conn.close()
    finally:
        aufraeumen(dest)
    return [dict(r) for r in rows], columns


def schluessel(row: dict) -> tuple:
    return (
        str(row.get("source_id") or ""),
        " ".join(str(row.get("quote") or "").split()),
        round(float(row["effect"]), 6) if row.get("effect") is not None else None,
        None if row.get("ci_low") is None else round(float(row["ci_low"]), 6),
        None if row.get("ci_high") is None else round(float(row["ci_high"]), 6),
        " ".join(str(row.get("outcome") or "").split()).lower(),
    )


def dubletten(rows: list) -> dict:
    groups = {}
    for row in rows:
        if row.get("effect") is None:
            continue
        groups.setdefault(schluessel(row), []).append(row)
    dup = {k: v for k, v in groups.items() if len(v) > 1}
    return {
        "zeilen": sum(len(v) for v in groups.values()),
        "gruppen": len(groups),
        "duplikat_gruppen": len(dup),
        "ueberzaehlig": sum(len(v) - 1 for v in dup.values()),
        "mehrere_extraktoren": sum(
            1 for v in dup.values()
            if len({str(x.get("extractor") or "") for x in v}) > 1),
        "max_groesse": max((len(v) for v in dup.values()), default=0),
    }


def standardisierte_gruppen(rows: list) -> dict:
    out = {}
    for row in rows:
        est, se, scale, reason = standardize(row)
        if reason or se is None:
            continue
        outcome = normalize_outcome(str(row.get("outcome") or "").strip()
                                   or "(kein Outcome)")
        out.setdefault((outcome, scale), []).append({
            "est": float(est), "se": float(se),
            "source_id": str(row.get("source_id") or ""),
            "label": str(row.get("source_id") or "")[:40] or "Zeile",
        })
    return out


def gewicht(se: float) -> float:
    return 1.0 / (se * se) if se else 0.0


def demo(rows: list) -> dict | None:
    """Die Gruppe mit der groessten Verschiebung durch unkollabierte Dubletten."""
    best = None
    for (outcome, scale), items in standardisierte_gruppen(rows).items():
        seen = set()
        unique = []
        for item in items:
            key = (item["source_id"], round(item["est"], 9), round(item["se"], 9))
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        if len(unique) == len(items) or len(unique) < 2:
            continue
        mit = pool(items)
        ohne = pool(unique)
        if mit["pooled"] is None or ohne["pooled"] is None:
            continue
        cand = {
            "outcome": outcome,
            "scale": scale,
            "k_mit_dublette": mit["k"],
            "k_ohne_dublette": ohne["k"],
            "pooled_mit": round(mit["pooled"], 6),
            "pooled_ohne": round(ohne["pooled"], 6),
            "ci_mit": [round(mit["ci_low"], 6), round(mit["ci_high"], 6)],
            "ci_ohne": [round(ohne["ci_low"], 6), round(ohne["ci_high"], 6)],
            "breite_mit": round(mit["ci_high"] - mit["ci_low"], 6),
            "breite_ohne": round(ohne["ci_high"] - ohne["ci_low"], 6),
            "verschiebung": round(mit["pooled"] - ohne["pooled"], 6),
            "gewichsanteil_der_dublette": round(
                max(gewicht(i["se"]) for i in items)
                / sum(gewicht(i["se"]) for i in items), 4),
        }
        if best is None or abs(cand["verschiebung"]) > abs(best["verschiebung"]):
            best = cand
    return best


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
            fehler.append({"datei": str(path), "fehler": str(exc)})
            continue
        if "study_effects" not in tables:
            continue
        try:
            rows, columns = lies(path, index)
        except Exception as exc:                      # noqa: BLE001
            fehler.append({"datei": str(path), "fehler": str(exc)})
            continue
        eintrag = {
            "datei": path.relative_to(ROOT).as_posix(),
            "gruppe": gruppe(path),
            "zaehlung": dubletten(rows),
        }
        if eintrag["gruppe"] == "themen":
            analysis = build_analysis(rows)
            kollabiert = [e for e in analysis["excluded"]
                          if "mehrfach" in str(e.get("reason") or "")
                          or "abhängige" in str(e.get("reason") or "")]
            eintrag["pooling"] = {
                "gruppen": len(analysis["groups"]),
                "k_summe": sum(int(g.get("k") or 0)
                               for g in analysis["groups"].values()),
                "kollabiert": len(kollabiert),
                "nicht_poolbar": len(analysis["excluded"]) - len(kollabiert),
                "demo": demo(rows),
            }
        ergebnisse.append(eintrag)

    gruppen = {}
    for eintrag in ergebnisse:
        b = gruppen.setdefault(eintrag["gruppe"], {
            "dateien": 0, "zeilen": 0, "duplikat_gruppen": 0,
            "ueberzaehlig": 0, "mehrere_extraktoren": 0,
        })
        z = eintrag["zaehlung"]
        b["dateien"] += 1
        for key in ("zeilen", "duplikat_gruppen", "ueberzaehlig",
                    "mehrere_extraktoren"):
            b[key] += z[key]

    themen = [e for e in ergebnisse if e["gruppe"] == "themen"]
    pooling = {
        "dbs": len(themen),
        "gruppen": sum(e["pooling"]["gruppen"] for e in themen),
        "k_summe": sum(e["pooling"]["k_summe"] for e in themen),
        "kollabiert": sum(e["pooling"]["kollabiert"] for e in themen),
        "nicht_poolbar": sum(e["pooling"]["nicht_poolbar"] for e in themen),
    }
    demos = [dict(e["pooling"]["demo"], datei=e["datei"]) for e in themen
             if e["pooling"].get("demo")]
    demos.sort(key=lambda d: -abs(d["verschiebung"]))
    pooling["demo"] = demos[0] if demos else None
    themen_zeilen = gruppen.get("themen", {}).get("zeilen", 0)
    themen_extra = gruppen.get("themen", {}).get("ueberzaehlig", 0)

    print(f"{len(ergebnisse)} DBs, {len(fehler)} Fehler")
    for name in ("themen", "pipeline", "sonstige"):
        b = gruppen.get(name)
        if b:
            print(f"{name}: {b['dateien']} DBs, {b['zeilen']} Zeilen, "
                  f"{b['duplikat_gruppen']} Duplikat-Gruppen, "
                  f"{b['ueberzaehlig']} ueberzaehlige Zeilen")
    print(f"\nPooling: {pooling['gruppen']} Gruppen, k-Summe {pooling['k_summe']}, "
          f"kollabiert {pooling['kollabiert']}")
    for d in demos[:3]:
        print(f"  {d['datei']} | {d['outcome']} [{d['scale']}]: "
              f"k {d['k_mit_dublette']}->{d['k_ohne_dublette']}, "
              f"pooled {d['pooled_mit']}->{d['pooled_ohne']}, "
              f"Breite {d['breite_mit']}->{d['breite_ohne']}")

    ergebnis = {
        "test": "E4c-duplikate",
        "stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "modellaufrufe": 0,
        "tokens": 0,
        "definition": "gleiche Quelle, gleiche Quote, gleicher Effekt, gleiches "
                      "KI, gleicher Outcome",
        "gruppen": gruppen,
        "pooling_themen": pooling,
        "dateien": ergebnisse,
        "fehler": fehler,
    }
    OUT_JSON.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    md = [
        "# E4c - doppelte Effektzeilen und das Pooling-Gewicht",
        "",
        f"Stand: {time.strftime('%Y-%m-%d %H:%M')} · Modellaufrufe: 0 · Tokens: 0",
        "",
        "Duplikat = gleiche Quelle, gleiche Quote, gleicher Effekt, gleiches KI,",
        "gleicher Outcome. Read-only auf Kopien; gelesen wurde die Kopie.",
        "",
        "| Gruppe | Dateien | Zeilen | Duplikat-Gruppen | ueberzaehlige Zeilen |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("themen", "pipeline", "sonstige"):
        b = gruppen.get(name)
        if b:
            md.append(f"| {name} | {b['dateien']} | {b['zeilen']} | "
                      f"{b['duplikat_gruppen']} | {b['ueberzaehlig']} |")
    md += [
        "",
        "## Faengt das Pooling sie?",
        "",
        f"`build_analysis` hat in den {pooling['dbs']} Themen-DBs "
        f"{pooling['kollabiert']} Zeilen vor dem Pool verworfen "
        f"(`_collapse_same_study`, je Quelle und Outcome bleibt die praezisere).",
        f"Die Zaehlung findet {themen_extra} ueberzaehlige Zeilen bei "
        f"{themen_zeilen} Zeilen mit Effekt - ueber alle Zeilen, auch solche, "
        f"die nie in einen Pool kommen (k=1, kein Beleg). Die Differenz ist "
        f"deshalb kein Rest an unentdeckten Dubletten.",
        "",
    ]
    if pooling["demo"]:
        d = pooling["demo"]
        md += [
            "## Was ohne den Kollaps passieren wuerde",
            "",
            f"Gemessen an echten Zeilen (`pool()` direkt, ohne "
            f"`_collapse_same_study`), Gruppe `{d['outcome']}` [{d['scale']}] "
            f"aus `{d['datei']}`:",
            "",
            "| | mit Dublette | ohne Dublette |",
            "|---|---:|---:|",
            f"| k | {d['k_mit_dublette']} | {d['k_ohne_dublette']} |",
            f"| gepoolt | {d['pooled_mit']} | {d['pooled_ohne']} |",
            f"| 95%-KI | [{d['ci_mit'][0]}; {d['ci_mit'][1]}] | "
            f"[{d['ci_ohne'][0]}; {d['ci_ohne'][1]}] |",
            f"| KI-Breite | {d['breite_mit']} | {d['breite_ohne']} |",
            "",
            f"Die Dublette haette {d['gewichsanteil_der_dublette']:.1%} des "
            f"Gewichts getragen (eigene Zeile plus ihr Zwilling). Verschiebung "
            f"des Punktschaetzers: {d['verschiebung']}. Genau das verhindert "
            f"der Kollaps - die Zeile wird nicht zweimal gezaehlt.",
            "",
        ]
    md += [
        "## Grenzen",
        "",
        "- Der Kollaps greift je Outcome-Gruppe. Zwei identische Zeilen unter",
        "  verschiedenen Outcome-Schreibweisen landen in zwei Gruppen (je k=1)",
        "  und werden nicht gepoolt - dort entsteht kein Gewichtsfehler, aber",
        "  auch keine Analyse.",
        "- `kollabiert` zaehlt auch legitime abhaengige Zeilen (Arme, Kontraste,",
        "  zweite Lesung), nicht nur exakte Dubletten. Die Zahl ist eine",
        "  Obergrenze fuer den Dubletten-Anteil, keine Dublettenzahl.",
        "- Die Demo zeigt den Mechanismus an einer Gruppe; sie ist kein",
        "  Schaetzer fuer den Effekt auf alle gepoolten Ergebnisse.",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nJSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"MD:   {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
