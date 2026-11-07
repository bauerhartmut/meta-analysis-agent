"""Direkte Effektspalten der sechs XML-Dokumente lesen und beziffern.

Wendet ``research_agent/meta/effect_columns.py`` auf jede JATS-Tabellenzeile
an: Spaltenkoepfe wie "Hedges g (95% CI)", "OR (95% CI)" oder
"Adjusted OR (95% CI)" liefern den Effekttyp, die Zelle den Punktwert und
das Intervall, `derive_se` den Standardfehler. Gespeichert wird nur, was
die Zitatpruefung und das Plausibilitaetsgate besteht.

Read-only gegenueber den Lauf-DBs: Ausgabe in ``data/bench/xml6/direct.db``.

Aufruf:
    .venv/bin/python.exe scripts/read_effect_columns_xml6.py
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _xml_to_text  # noqa: E402
from research_agent.database import Database  # noqa: E402
from research_agent.meta.effect_columns import (  # noqa: E402
    effects_from_row,
    store_direct_effects,
)
from research_agent.research.jats_tables import _pipe_row, parse_jats  # noqa: E402

DOCUMENTS = [
    ("10.1001/jamanetworkopen.2026.26983", "PMC13448793"),
    ("10.3389/fnut.2026.1890075", "PMC13520769"),
    ("10.3390/healthcare13020180", "PMC11765054"),
    ("10.3390/ijms27146320", "PMC13409838"),
    ("10.3390/medicina62040662", "PMC13117668"),
    ("10.5888/pcd20.230198", "PMC10756651"),
]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml-dir", default="data/bench/xml6")
    parser.add_argument("--manifest", default="",
                        help="JSON-Liste [{\"doi\": ..., \"pmc\": ...}] statt der sechs Dokumente")
    parser.add_argument("--db", default="data/bench/xml6/direct.db")
    parser.add_argument("--json", default="data/bench/xml6/effect_columns_20261107.json")
    parser.add_argument("--md", default="data/bench/xml6/effect_columns_20261107.md")
    args = parser.parse_args(argv)

    xml_dir = Path(args.xml_dir)
    documents = list(DOCUMENTS)
    if args.manifest:
        raw = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        documents = [(str(entry["doi"]), str(entry["pmc"])) for entry in raw]
    db_path = Path(args.db)
    if db_path.exists():
        db_path.unlink()
    db = Database(str(db_path))

    doc_reports, totals = [], Counter()
    for doi, pmc in documents:
        xml_path = xml_dir / f"{pmc}.xml"
        xml = xml_path.read_text(encoding="utf-8", errors="replace")
        text = _xml_to_text(xml)
        source_id = f"doi:{doi}"
        row = db.save_source_text(
            source_id, text, kind="xml",
            origin_url=f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML",
        )
        text_id = (row or {}).get("id", "")

        table_rows = aligned = 0
        candidates, reasons = [], Counter()
        for table in parse_jats(xml_path):
            for table_row in table.rows:
                table_rows += 1
                if len(table.header) == len(table_row.cells):
                    aligned += 1
                found, reason = effects_from_row(
                    table.header, table_row.cells,
                    quote=_pipe_row(table_row.cells),
                    caption=(table.label or "") + " " + (table.caption or ""))
                if found:
                    candidates.extend(found)
                else:
                    reasons[reason or "unbekannt"] += 1

        stored, rejected = store_direct_effects(db, source_id, text_id, text, candidates)
        for entry in rejected:
            reasons[entry.get("reason") or "unbekannt"] += 1

        kinds = Counter(item["effect_type"] for item in stored)
        totals.update({
            "table_rows": table_rows,
            "aligned_rows": aligned,
            "candidates": len(candidates),
            "stored": len(stored),
            "rejected": len(rejected),
        })
        doc_reports.append({
            "doi": doi,
            "pmc": pmc,
            "table_rows": table_rows,
            "aligned_rows": aligned,
            "candidates": len(candidates),
            "stored": len(stored),
            "rejected": len(rejected),
            "kinds": dict(kinds),
            "reasons": dict(reasons.most_common()),
            "effects": [
                {
                    "outcome": item.get("outcome"),
                    "effect_type": item.get("effect_type"),
                    "effect": item.get("effect"),
                    "se": round(float(item["se"]), 6),
                    "ci": [item.get("ci_low"), item.get("ci_high")],
                    "ci_level": item.get("ci_level"),
                    "adjusted": item.get("adjusted"),
                    "column": item.get("comparison"),
                    "quote": str(item.get("quote") or "")[:200],
                }
                for item in stored
            ],
        })

    report = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "documents": doc_reports,
        "totals": dict(totals),
    }
    out = Path(args.json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Direkte Effektspalten (sechs XML-Dokumente)",
        "",
        f"Stand: {report['generated']}. Leser: "
        "`research_agent/meta/effect_columns.py`, Modell ohne LLM. "
        "SE aus dem berichteten Intervall (`derive_se`).",
        "",
        "| DOI | Tabellenzeilen | Kopf=Zeile | Kandidaten | gespeichert |",
        "|---|---:|---:|---:|---:|",
    ]
    for doc in doc_reports:
        lines.append(f"| {doc['doi']} | {doc['table_rows']} | {doc['aligned_rows']} | "
                     f"{doc['candidates']} | {doc['stored']} |")
    lines += [
        f"| **Summe** | {totals['table_rows']} | {totals['aligned_rows']} | "
        f"{totals['candidates']} | **{totals['stored']}** |",
        "",
        "## Ablehnungsgruende",
        "",
    ]
    all_reasons = Counter()
    for doc in doc_reports:
        all_reasons.update(doc["reasons"])
    for reason, count in all_reasons.most_common():
        lines.append(f"- {count:4d}  {reason}")
    lines += ["", "## Gespeicherte Effekte", ""]
    for doc in doc_reports:
        if not doc["effects"]:
            continue
        lines.append(f"### {doc['doi']}")
        lines.append("")
        lines.append("| Outcome | Typ | Effekt | SE | CI | adjustiert | Spalte |")
        lines.append("|---|---|---:|---:|---|---:|---|")
        for effect in doc["effects"]:
            lines.append(
                f"| {effect['outcome'][:38]} | {effect['effect_type']} | "
                f"{effect['effect']} | {effect['se']} | "
                f"{effect['ci'][0]} bis {effect['ci'][1]} | "
                f"{effect['adjusted']} | {(effect['column'] or '')[:26]} |")
        lines.append("")
    Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(dict(totals), ensure_ascii=False))
    for reason, count in all_reasons.most_common():
        print(f"  {count:4d}  {reason}")
    kinds = Counter()
    for doc in doc_reports:
        kinds.update(doc["kinds"])
    print("  Typen:", dict(kinds))
    print(f"JSON: {args.json}")
    print(f"MD:   {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
