"""Listet Wert- und Zitat-Zwillinge der Pipeline-Zeilen als Pruefliste.

Read-only, ohne Modellaufruf. Je Duplikat stehen Dokument, Outcome,
Effektgroesse, Zitat, Grund und die Zeile, die im Abgleich stehen bleibt.
Die Liste ist fuer die Annotatoren gedacht: Sie sehen, welche Zeile als
Original zaehlt und ob die Doppelung fachlich plausibel ist.

Beispiel:
    .venv/bin/python.exe scripts/liste_goldstandard_duplikate.py \
        --out data/golden_effects/duplikate.json \
        --md docs/internal/goldstandard_duplikate_20261110.md
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.goldstandard_abgleich import dedupe_details, ist_poolbar  # noqa: E402


def db_liste(zusatz: list) -> list:
    pfade = [p for p in sorted(ROOT.glob("data/research-*.db")) if "usage" not in p.name]
    pfade.append(ROOT / "data/harness_local.db")
    pfade.extend(Path(z) for z in zusatz)
    gesehen, ergebnis = set(), []
    for p in pfade:
        p = p if p.is_absolute() else ROOT / p
        if p.exists() and p not in gesehen:
            gesehen.add(p)
            ergebnis.append(p)
    return ergebnis


def lade(docs: list, dbs: list):
    verbindungen = {p: sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True)
                    for p in dbs}
    ergebnis = []
    for doc in docs:
        fid = doc["document_id"]
        zeilen = []
        for p in dbs:
            con = verbindungen[p]
            if not con.execute("select 1 from source_texts where id = ? limit 1",
                               (fid,)).fetchone():
                continue
            # Alte Lauf-DBs haben nicht jede Spalte (z. B. kein study_id).
            # Nur vorhandene selektieren, fehlende bleiben None.
            vorhanden = {r[1] for r in con.execute("pragma table_info(study_effects)")}
            felder = ("id", "outcome", "comparison", "effect_type", "effect",
                      "se", "ci_low", "ci_high", "quote", "quote_start",
                      "quote_end", "disputed", "rejection_reason")
            spalten = [s for s in felder if s in vorhanden]
            rows = con.execute(
                f"select {', '.join('e.' + s for s in spalten)} "
                "from study_effects e join source_texts t on e.source_text_id = t.id "
                "where t.id = ? and e.effect is not null order by e.id", (fid,))
            for z in rows:
                roh = dict(zip(spalten, z))
                zeilen.append({s: roh.get(s) for s in felder})
            break
        behalten, details = dedupe_details(zeilen)
        ergebnis.append({
            "document_id": fid,
            "stratum": doc.get("stratum"),
            "titel": doc.get("title") or doc.get("titel")
                     or Path(str(doc.get("path") or "")).name,
            "zeilen": len(zeilen),
            "unique": len(behalten),
            "duplikate": len(details),
            "details": [{
                "id": d["zeile"]["id"],
                "original_id": d["original"]["id"],
                "grund": d["grund"],
                "outcome": d["zeile"]["outcome"],
                "effect_type": d["zeile"]["effect_type"],
                "effect": d["zeile"]["effect"],
                "ci_low": d["zeile"]["ci_low"],
                "ci_high": d["zeile"]["ci_high"],
                "poolbar": ist_poolbar(d["zeile"]),
                "quote": d["zeile"]["quote"],
                "quote_start": d["zeile"]["quote_start"],
                "original_effect": d["original"]["effect"],
                "original_outcome": d["original"]["outcome"],
            } for d in details],
        })
    for con in verbindungen.values():
        con.close()
    return ergebnis


def _kurz(text, n=150) -> str:
    sauber = " ".join(str(text or "").split())
    return sauber if len(sauber) <= n else sauber[: n - 1] + "…"


def _zahl(x) -> str:
    return "n/a" if x is None else f"{x:.3g}"


def markdown(ergebnis: list, zeilen: int, unique: int) -> str:
    details = [(d, x) for d in ergebnis for x in d["details"]]
    nach_grund = {"wert": 0, "zitat": 0}
    for _, x in details:
        nach_grund[x["grund"]] = nach_grund.get(x["grund"], 0) + 1
    betroffen = [d for d in ergebnis if d["duplikate"]]
    text = [
        "# Goldstandard: Duplikate in den Pipeline-Zeilen (2026-11-10)",
        "",
        "Read-only, kein Modellaufruf. Dedupe-Regel wie im Pooling: Zwilling ist",
        "gleiche Quelle plus gleicher Effekt (9 Stellen, SE) oder gleicher",
        "normalisierter Zitattext (erste 200 Zeichen). Die erste Zeile bleibt.",
        "",
        f"**{zeilen} Zeilen, {unique} unique, {len(details)} Duplikate** "
        f"({nach_grund.get('wert', 0)} Wert-Zwillinge, "
        f"{nach_grund.get('zitat', 0)} Zitat-Zwillinge) in "
        f"{len(betroffen)} von {len(ergebnis)} Dokumenten.",
        "",
        "Prueffrage je Zeile: Ist die Doppelung eine echte zweite Lesung oder",
        "eine andere Aussage mit gleichem Wert/Beleg? Nur im zweiten Fall darf",
        "die Zeile fachlich stehen bleiben; der Abgleich zaehlt sie dennoch",
        "einmal, weil das Pooling sie ebenfalls einmal zaehlt.",
        "",
        "| Dokument | Stratum | Dup-ID | Original-ID | Grund | Outcome | Typ | Effekt | KI | poolbar | Zitat |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for doc, x in details:
        ki = (f"{_zahl(x['ci_low'])}-{_zahl(x['ci_high'])}"
              if x["ci_low"] is not None and x["ci_high"] is not None else "n/a")
        text.append(
            f"| {doc['document_id'][:10]} | {doc['stratum']} | {str(x['id'])[:10]} | "
            f"{str(x['original_id'])[:10]} | {'Wert' if x['grund'] == 'wert' else 'Zitat'} | "
            f"{_kurz(x['outcome'], 70)} | {x['effect_type']} | {_zahl(x['effect'])} | "
            f"{ki} | {'ja' if x['poolbar'] else 'nein'} | {_kurz(x['quote'])} |")
    text += ["", "## Betroffene Dokumente", ""]
    for doc in betroffen:
        text.append(f"- `{doc['document_id']}` ({doc['stratum']}, {doc['titel']}): "
                    f"{doc['zeilen']} Zeilen, {doc['duplikate']} Duplikate")
    text += ["", "Volle Zitate und IDs: `data/golden_effects/duplikate.json`.", ""]
    return "\n".join(text)


def main(argv: list) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", default="data/golden_effects/documents.json")
    parser.add_argument("--out", default="data/golden_effects/duplikate.json")
    parser.add_argument("--md", default="docs/internal/goldstandard_duplikate_20261110.md")
    parser.add_argument("--db", action="append", default=[])
    args = parser.parse_args(argv)

    docs = json.loads((ROOT / args.docs).read_text(encoding="utf-8"))["documents"]
    dbs = db_liste(args.db)
    ergebnis = lade(docs, dbs)
    zeilen = sum(d["zeilen"] for d in ergebnis)
    unique = sum(d["unique"] for d in ergebnis)
    dup = sum(d["duplikate"] for d in ergebnis)

    print(f"Dokumente: {len(ergebnis)} | Zeilen: {zeilen} | unique: {unique} | Duplikate: {dup}")
    for doc in ergebnis:
        if doc["duplikate"]:
            print(f"  {doc['document_id'][:10]} {doc['stratum']:<16} "
                  f"{doc['duplikate']} Duplikat(e) bei {doc['zeilen']} Zeilen")

    ziel = ROOT / args.out
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps({"dokumente": ergebnis, "zeilen": zeilen,
                                "unique": unique, "duplikate": dup},
                               ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"JSON: {ziel.relative_to(ROOT)}")
    if args.md:
        md = ROOT / args.md
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(markdown(ergebnis, zeilen, unique), encoding="utf-8")
        print(f"Markdown: {md.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
