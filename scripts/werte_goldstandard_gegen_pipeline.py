"""Wertet den Goldstandard gegen die Pipeline-Extraktion aus.

Ohne Modellaufrufe: liest die Annotationsdatei und die vorhandenen
study_effects aus den Lauf-Datenbanken (read-only).

Beispiel:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/werte_goldstandard_gegen_pipeline.py \
        --gold data/golden_effects/goldstandard_consensus.json \
        --out data/golden_effects/abgleich_pipeline.json \
        --md docs/internal/goldstandard_pipeline_abgleich_20261110.md

Ohne --gold wird consensus genommen, falls vorhanden, sonst A.
Dokumente ohne Zeile und ohne no_effect_reason gelten als offen und werden
nicht gewertet (sonst waere die Precision systematisch falsch).
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.goldstandard_abgleich import werte  # noqa: E402

STANDARD_DBS = sorted(ROOT.glob("data/research-*.db"))


def lade_gold(pfad: Path):
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    effekte, annotiert = {}, set()
    for doc in daten["documents"]:
        fid = doc["document_id"]
        effekte[fid] = doc.get("effects") or []
        if effekte[fid] or str(doc.get("no_effect_reason") or "").strip():
            annotiert.add(fid)
    return effekte, annotiert, daten


def db_liste(zusatz: list) -> list:
    pfade = [p for p in STANDARD_DBS if "usage" not in p.name]
    pfade.append(ROOT / "data/harness_local.db")
    pfade.extend(Path(z) for z in zusatz)
    gesehen, ergebnis = set(), []
    for p in pfade:
        p = p if p.is_absolute() else ROOT / p
        if p.exists() and p not in gesehen:
            gesehen.add(p)
            ergebnis.append(p)
    return ergebnis


def lade_pipeline(docs: list, dbs: list, nur_akzeptiert: bool):
    verbindungen = {p: sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True)
                    for p in dbs}
    treffer_db = {}
    ergebnis = {}
    for doc in docs:
        fid = doc["document_id"]
        db = next((p for p in dbs
                   if verbindungen[p].execute(
                       "select 1 from source_texts where id = ? limit 1", (fid,)).fetchone()),
                  None)
        if db is None:
            ergebnis[fid] = []
            continue
        treffer_db[fid] = db.name
        sql = ("select e.id, e.outcome, e.comparison, e.effect_type, e.effect, "
               "e.ci_low, e.ci_high, e.se, e.quote, e.quote_start, e.disputed, "
               "e.rejection_reason "
               "from study_effects e join source_texts t on e.source_text_id = t.id "
               "where t.id = ? and e.effect is not null")
        if nur_akzeptiert:
            sql += " and coalesce(e.rejection_reason,'') = '' and coalesce(e.disputed,0) = 0"
        zeilen = verbindungen[db].execute(sql, (fid,)).fetchall()
        ergebnis[fid] = [{"id": z[0], "outcome": z[1], "comparison": z[2],
                          "effect_type": z[3], "effect": z[4], "ci_low": z[5],
                          "ci_high": z[6], "se": z[7], "quote": z[8],
                          "quote_start": z[9], "disputed": z[10],
                          "rejection_reason": z[11]}
                         for z in zeilen]
    for con in verbindungen.values():
        con.close()
    return ergebnis, treffer_db


def bericht_text(ergebnis: dict, gold_datei: str, quelle: dict) -> str:
    g = ergebnis["gesamt"]
    zeilen = [
        f"Goldstandard: {gold_datei}",
        f"Dokumente: {quelle['n_dokumente']} | annotiert: {g['n_annotiert']} | offen: {g['n_offen']}",
        f"Pipelinezeilen: {g['pipeline_zeilen']} | Toleranz: {ergebnis['stufen']['toleranz']:.0%} | Schwelle: {ergebnis['stufen']['schwelle']:.2f}",
    ]
    if not g["n_annotiert"]:
        zeilen.append("Keine Annotation: es gibt nichts auszuwerten. Die Pipeline-Zahlen stehen nur als Baseline.")
        return "\n".join(zeilen)

    def p(x):
        return "n/a" if x is None else f"{100 * x:.0f} %"

    def a(x):
        return "n/a" if x is None else f"{x:.2f}"

    zeilen += [
        "",
        "| Schicht | TP | FP | FN | Precision | Recall | Typ | Wert | Poolbar | Ausbeute |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name, s in ergebnis["schichten"].items():
        zeilen.append(f"| {name} | {s['tp']} | {s['fp']} | {s['fn']} | {p(s['precision'])} | "
                      f"{p(s['recall'])} | {p(s['typquote'])} | {p(s['wertquote'])} | "
                      f"{p(s['poolbare_quote'])} | {a(s['ausbeute_poolbar'])} |")
    zeilen.append(f"| **gesamt** | {g['tp']} | {g['fp']} | {g['fn']} | {p(g['precision'])} | "
                  f"{p(g['recall'])} | {p(g['typquote'])} | {p(g['wertquote'])} | "
                  f"{p(g['poolbare_quote'])} | {a(g['ausbeute_poolbar'])} |")
    return "\n".join(zeilen)


def main(argv: list) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", default="")
    parser.add_argument("--docs", default="data/golden_effects/documents.json")
    parser.add_argument("--out", default="data/golden_effects/abgleich_pipeline.json")
    parser.add_argument("--md", default="")
    parser.add_argument("--db", action="append", default=[])
    parser.add_argument("--schwelle", type=float, default=0.55)
    parser.add_argument("--toleranz", type=float, default=0.01)
    parser.add_argument("--nur-akzeptiert", action="store_true")
    args = parser.parse_args(argv)

    if args.gold:
        gold_pfad = ROOT / args.gold
    else:
        consensus = ROOT / "data/golden_effects/goldstandard_consensus.json"
        gold_pfad = consensus if consensus.exists() else ROOT / "data/golden_effects/goldstandard_A.json"
    if not gold_pfad.exists():
        print(f"Goldstandard fehlt: {gold_pfad}")
        return 1

    docs = json.loads((ROOT / args.docs).read_text(encoding="utf-8"))["documents"]
    gold_docs, annotiert, gold_roh = lade_gold(gold_pfad)
    dbs = db_liste(args.db)
    pipe_docs, treffer_db = lade_pipeline(docs, dbs, args.nur_akzeptiert)
    ergebnis = werte(gold_docs, pipe_docs, docs, annotiert,
                     schwelle=args.schwelle, toleranz=args.toleranz)
    ergebnis["gold_datei"] = str(gold_pfad.relative_to(ROOT))
    ergebnis["datenbanken"] = [p.name for p in dbs]
    ergebnis["nur_akzeptiert"] = args.nur_akzeptiert
    ergebnis["ohne_db"] = [d["document_id"] for d in docs if d["document_id"] not in treffer_db]

    text = bericht_text(ergebnis, str(gold_pfad.relative_to(ROOT)),
                        {"n_dokumente": len(docs)})
    print(text)
    ziel = ROOT / args.out
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"\nBericht: {ziel.relative_to(ROOT)}")

    if args.md:
        md = f"""# Goldstandard gegen Pipeline: Abgleich (2026-11-10)

Kein Modellaufruf. Quelle: `{gold_pfad.relative_to(ROOT)}`, Datenbanken:
{", ".join(p.name for p in dbs)}.

```
{text}
```

## Was gezaehlt wird

- **TP**: Goldzeile und Pipelinezeile wurden gepaart.
- **FP**: Pipelinezeile ohne Goldzeile.
- **FN**: Goldzeile ohne Pipelinezeile.
- **Precision** = TP / (TP + FP), **Recall** = TP / (TP + FN).
- **Typquote** = gepaarte Zeilen mit gleichem `effect_type` / TP.
- **Wertquote** = gepaarte Zeilen mit Effekt innerhalb {args.toleranz:.0%} / TP.
- **Poolbar** = Anteil der Pipelinezeilen mit `Database.POOLABLE`
  (`disputed=0`, kein `rejection_reason`, `quote_start >= 0`, SE oder KI).
- **Ausbeute** = poolbare Pipelinezeilen je annotiertem Volltext.

Die Ausbeute zaehlt nur Zeilen **annotierter** Dokumente; offene Dokumente
liefern keine Quote. `nur_akzeptiert` aendert die Poolbarkeit nicht, weil
die POOLABLE-Definition Verworfenes und Strittiges ohnehin ausschliesst.

Gepaart wird greedy nach Aehnlichkeit aus Outcome-Tokens, Vergleich,
Effekttyp und Wertnaehe; Schwelle {args.schwelle:.2f}. Das ist eine
nachvollziehbare Heuristik, kein semantisches Urteil. Dokumente ohne Zeile
und ohne Begruendung gelten als **offen** und werden nicht gewertet.

## Stand

{("Ausgewertet: " + str(ergebnis["gesamt"]["n_annotiert"]) + " Dokumente, "
  + str(ergebnis["gesamt"]["n_offen"]) + " offen.") if ergebnis["gesamt"]["n_annotiert"]
 else "Noch keine Annotation. Der Bericht ist eine Baseline ueber die Pipeline-Zeilen, keine Guetemessung."}

Die Datei wird nach jeder Annotation neu erzeugt.
"""
        md_pfad = ROOT / args.md
        md_pfad.parent.mkdir(parents=True, exist_ok=True)
        md_pfad.write_text(md, encoding="utf-8")
        print(f"Markdown: {md_pfad.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
