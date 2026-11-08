"""E4d - was verwirft `_collapse_same_study` wirklich?

E4c hat gezaehlt: `build_analysis` verwirft in den Themen-DBs 39 Zeilen vor
dem Pool. Offen ist, ob darunter nur Kopien sind oder auch unabhaengige Arme
und Kontraste, die das Pooling dann verliert.

Die Kollaps-Logik wird hier nachgebaut (doi -> source_id -> study_id ->
cohort_id, die praezisere Zeile bleibt) und mit der echten Zahl aus
`build_analysis` abgeglichen. Jedes verworfene Paar wird klassifiziert:

  exakte_dublette        gleiche Quelle, Quote, Effekt, KI, Outcome
  gleicher_wert          gleicher Effekt und gleiches KI, andere Quote
  anderer_effekt         anderer Punktwert - unabhaengiger Arm/Kontrast

Read-only auf Kopien, keine Modellaufrufe.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/klassifiziere_kollaps.py
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
    _split_pool_conditions, build_analysis, standardize,
)

VALIDIERUNG = ROOT / "data" / "bench" / "validierung"
OUT_JSON = VALIDIERUNG / "e4_kollaps_20261108.json"
OUT_MD = VALIDIERUNG / "e4_kollaps_20261108.md"

INF = float("inf")


def lies(path: Path, index: int) -> list:
    dest = kopiere(path, index)
    conn = None
    try:
        conn = sqlite3.connect(dest, timeout=10)
        conn.row_factory = sqlite3.Row
        rows = [dict(r) for r in conn.execute("SELECT * FROM study_effects")]
    finally:
        if conn is not None:
            conn.close()
        aufraeumen(dest)
    return rows


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


def kollabiere(rows: list):
    """Nachbau von `_collapse_same_study`, zusaetzlich mit den Paaren."""
    kept, pairs = [], []
    by_doi, by_source, by_study, by_cohort = {}, {}, {}, {}

    def se_of(row):
        value = row.get("se")
        return float(value) if value else INF

    for row in rows:
        doi = str(row.get("doi") or "").strip().lower()
        source_id = str(row.get("source_id") or "").strip()
        study_id = str(row.get("study_id") or "").strip()
        cohort = str(row.get("cohort_id") or "").strip()
        if cohort and not str(row.get("quote") or "").strip():
            cohort = ""
        position, reason = None, ""
        if (doi and doi in by_doi
                and not (cohort
                         and str(kept[by_doi[doi]].get("cohort_id") or "").strip()
                         and cohort != str(kept[by_doi[doi]].get("cohort_id") or "").strip())):
            position, reason = by_doi[doi], f"doi:{doi}"
        elif source_id and source_id in by_source:
            position, reason = by_source[source_id], "quelle"
        elif study_id and study_id in by_study:
            position, reason = by_study[study_id], "studie"
        elif cohort and cohort in by_cohort:
            position, reason = by_cohort[cohort], "kohorte"

        if position is None:
            kept.append(row)
            index = len(kept) - 1
            if doi:
                by_doi[doi] = index
            if source_id:
                by_source[source_id] = index
            if study_id:
                by_study[study_id] = index
            if cohort:
                by_cohort[cohort] = index
            continue

        first = kept[position]
        if se_of(row) < se_of(first):
            kept[position] = row
            pairs.append({"behalten": row, "verworfen": first, "grund": reason})
            if doi:
                by_doi[doi] = position
            if source_id:
                by_source[source_id] = position
            if study_id:
                by_study[study_id] = position
        else:
            pairs.append({"behalten": first, "verworfen": row, "grund": reason})
    return kept, pairs


def wert(row, key):
    value = row.get(key)
    return None if value is None else round(float(value), 6)


def klasse(paar: dict) -> str:
    a, b = paar["behalten"], paar["verworfen"]
    identisch = all([
        str(a.get("source_id") or "") == str(b.get("source_id") or ""),
        " ".join(str(a.get("quote") or "").split())
        == " ".join(str(b.get("quote") or "").split()),
        wert(a, "effect") == wert(b, "effect"),
        wert(a, "ci_low") == wert(b, "ci_low"),
        wert(a, "ci_high") == wert(b, "ci_high"),
        " ".join(str(a.get("outcome") or "").split()).lower()
        == " ".join(str(b.get("outcome") or "").split()).lower(),
    ])
    if identisch:
        return "exakte_dublette"
    if (wert(a, "effect") == wert(b, "effect")
            and wert(a, "ci_low") == wert(b, "ci_low")
            and wert(a, "ci_high") == wert(b, "ci_high")):
        return "gleicher_wert"
    return "anderer_effekt"


def kurz(row) -> dict:
    return {
        "effect": wert(row, "effect"),
        "ci": [wert(row, "ci_low"), wert(row, "ci_high")],
        "outcome": " ".join(str(row.get("outcome") or "").split()),
        "quote": " ".join(str(row.get("quote") or "").split())[:180],
    }


def main() -> int:
    themen = sorted(p for p in (ROOT / "data").rglob("*.db")
                    if "-usage" not in p.name and gruppe(p) == "themen")
    zaehler = {"exakte_dublette": 0, "gleicher_wert": 0, "anderer_effekt": 0}
    gruende = {}
    details, db_zeilen = [], []
    kollabiert_laut_analysis = 0

    for index, path in enumerate(themen):
        try:
            probe = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True,
                                    timeout=5)
            tables = {r[0] for r in probe.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            probe.close()
        except Exception as exc:                      # noqa: BLE001
            print(f"FEHLER {path}: {exc}")
            continue
        if "study_effects" not in tables:
            continue
        rows = lies(path, index)
        analysis = build_analysis(rows)
        kollabiert_laut_analysis += len([
            e for e in analysis["excluded"]
            if "mehrfach" in str(e.get("reason") or "")
            or "abhängige" in str(e.get("reason") or "")])

        standard = standardisiere(rows)
        groups = {}
        for row in standard:
            groups.setdefault((row["outcome_group"], row["scale"]), []).append(row)
        paare = []
        for (_outcome, _scale), group_rows in groups.items():
            for _label, sub_rows in _split_pool_conditions(group_rows):
                _kept, pairs = kollabiere(sub_rows)
                paare.extend(pairs)

        for paar in paare:
            art = klasse(paar)
            zaehler[art] += 1
            gruende[paar["grund"].split(":")[0]] = (
                gruende.get(paar["grund"].split(":")[0], 0) + 1)
            if art != "exakte_dublette":
                details.append({
                    "datei": path.relative_to(ROOT).as_posix(),
                    "art": art,
                    "outcome": paar["behalten"].get("outcome_group"),
                    "grund": paar["grund"],
                    "behalten": kurz(paar["behalten"]),
                    "verworfen": kurz(paar["verworfen"]),
                })
        db_zeilen.append({
            "datei": path.relative_to(ROOT).as_posix(),
            "verworfen_hier": len(paare),
            "kollabiert_laut_analysis": len([
                e for e in analysis["excluded"]
                if "mehrfach" in str(e.get("reason") or "")
                or "abhängige" in str(e.get("reason") or "")]),
        })

    gesamt = sum(zaehler.values())
    print(f"{len(themen)} Themen-DBs, {gesamt} verworfene Zeilen "
          f"(analysis: {kollabiert_laut_analysis})")
    print(f"  exakte Dubletten: {zaehler['exakte_dublette']}")
    print(f"  gleicher Wert, andere Quote: {zaehler['gleicher_wert']}")
    print(f"  anderer Effekt (Kontrast): {zaehler['anderer_effekt']}")
    print(f"  Gruende: {gruende}")
    for d in details[:8]:
        print(f"  {d['art']}: {d['outcome']} | behalten {d['behalten']['effect']} "
              f"vs verworfen {d['verworfen']['effect']}")

    ergebnis = {
        "test": "E4d-kollaps",
        "stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "modellaufrufe": 0,
        "tokens": 0,
        "themen_dbs": len(themen),
        "verworfen_gesamt": gesamt,
        "kollabiert_laut_analysis": kollabiert_laut_analysis,
        "zaehlung": zaehler,
        "gruende": gruende,
        "dateien": db_zeilen,
        "details": details,
    }
    OUT_JSON.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    md = [
        "# E4d - was verwirft der Kollaps?",
        "",
        f"Stand: {time.strftime('%Y-%m-%d %H:%M')} · Modellaufrufe: 0 · Tokens: 0",
        "",
        f"Nachbau der Kollaps-Logik auf den {len(themen)} Themen-DBs: "
        f"{gesamt} verworfene Zeilen, `build_analysis` nennt "
        f"{kollabiert_laut_analysis}. Die Differenz waere ein Fehler im "
        f"Nachbau, nicht im Pooling.",
        "",
        "| Klasse | Zeilen | Bedeutung |",
        "|---|---:|---|",
        f"| exakte Dublette | {zaehler['exakte_dublette']} | gleiche Quelle, "
        "Quote, Effekt, KI, Outcome - Kollaps korrekt |",
        f"| gleicher Wert | {zaehler['gleicher_wert']} | Effekt und KI gleich, "
        "andere Belegstelle |",
        f"| anderer Effekt | {zaehler['anderer_effekt']} | unabhaengiger "
        "Arm/Kontrast - Informationsverlust |",
        "",
    ]
    if details:
        md += [
            "## Die nicht exakten Faelle",
            "",
            "| Datei | Art | Outcome | behalten | verworfen |",
            "|---|---|---|---|---|",
        ]
        for d in details:
            md.append(
                f"| `{d['datei'].split('/')[-1]}` | {d['art']} | "
                f"{d['outcome']} | {d['behalten']['effect']} "
                f"[{d['behalten']['ci'][0]}; {d['behalten']['ci'][1]}] | "
                f"{d['verworfen']['effect']} "
                f"[{d['verworfen']['ci'][0]}; {d['verworfen']['ci'][1]}] |")
        md += ["", "### Belege", ""]
        for d in details[:8]:
            md.append(f"- `{d['datei'].split('/')[-1]}` ({d['art']}): "
                      f"behalten: {d['behalten']['quote']}")
            md.append(f"  verworfen: {d['verworfen']['quote']}")
    md += [
        "",
        "## Einordnung",
        "",
        "Exakte Dubletten sind ein Speicherfehler ohne Erkenntnisverlust: Der",
        "Kollaps entfernt sie richtigerweise. Bei `anderer_effekt` behaelt das",
        "Pooling eine Zeile und verwirft eine unabhaengige Schaetzung - das ist",
        "die bewusste Unabhaengigkeitsregel (eine Quelle zaehlt einmal), kostet",
        "aber Information und ist mit dem RVE-Pfad (`pool_rve`) bereits als",
        "Alternative vorhanden.",
    ]
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"\nJSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"MD:   {OUT_MD.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
