"""Arm-Deskriptiva aus den sechs XML-Dokumenten in Hedges g umrechnen.

Wendet ``research_agent/meta/arm_level.py`` auf jede JATS-Tabellenzeile der
sechs Dokumente an: Mittelwert, SD/SE/95 %-CI und n je Arm werden gelesen,
daraus g (mit SE) gerechnet, und gespeichert wird nur, was vollstaendig
belegt ist und dessen Zitat woertlich im gespeicherten Text steht.

Read-only gegenueber den Lauf-DBs: die Zeilen landen in einer eigenen
Mess-DB unter ``data/bench/xml6/arm_level.db``.

Aufruf:
    .venv/bin/python.exe scripts/convert_arm_level_xml6.py
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _xml_to_text  # noqa: E402
from research_agent.database import Database  # noqa: E402
from research_agent.meta.arm_level import convert_row, store_arm_level_effects  # noqa: E402
from research_agent.research.jats_tables import _pipe_row, parse_jats  # noqa: E402

DOCUMENTS = [
    ("10.1001/jamanetworkopen.2026.26983", "PMC13448793"),
    ("10.3389/fnut.2026.1890075", "PMC13520769"),
    ("10.3390/healthcare13020180", "PMC11765054"),
    ("10.3390/ijms27146320", "PMC13409838"),
    ("10.3390/medicina62040662", "PMC13117668"),
    ("10.5888/pcd20.230198", "PMC10756651"),
]


def _outcome_label(cells, caption: str) -> str:
    for cell in cells:
        text = str(cell or "").strip()
        if text and not any(ch.isdigit() for ch in text):
            return text[:90]
    return (caption or "")[:90]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml-dir", default="data/bench/xml6")
    parser.add_argument("--db", default="data/bench/xml6/arm_level.db")
    parser.add_argument("--json", default="data/bench/xml6/arm_level_20261107.json")
    parser.add_argument("--md", default="data/bench/xml6/arm_level_20261107.md")
    args = parser.parse_args(argv)

    xml_dir = Path(args.xml_dir)
    db_path = Path(args.db)
    if db_path.exists():
        db_path.unlink()
    db = Database(str(db_path))

    documents, totals = [], Counter()
    for doi, pmc in DOCUMENTS:
        xml = (xml_dir / f"{pmc}.xml").read_text(encoding="utf-8", errors="replace")
        text = _xml_to_text(xml)
        source_id = f"doi:{doi}"
        row = db.save_source_text(
            source_id, text, kind="xml",
            origin_url=f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML",
        )
        text_id = (row or {}).get("id", "")

        table_rows = attempts = 0
        candidates, reasons = [], Counter()
        for table in parse_jats(xml_dir / f"{pmc}.xml"):
            label = (table.label or "") + " " + (table.caption or "")
            for table_row in table.rows:
                table_rows += 1
                quote = _pipe_row(table_row.cells)
                candidate = convert_row(
                    table.header, table_row.cells,
                    outcome=_outcome_label(table_row.cells, label),
                    quote=quote,
                )
                if candidate.get("ok"):
                    attempts += 1
                    candidates.append(candidate)
                else:
                    reasons[candidate.get("reason") or "unbekannt"] += 1

        stored, rejected = store_arm_level_effects(
            db, source_id, text_id, text, candidates)
        for entry in rejected:
            reasons[entry.get("reason") or "unbekannt"] += 1

        totals.update({
            "table_rows": table_rows,
            "convertible": attempts,
            "stored": len(stored),
            "rejected": len(rejected),
        })
        documents.append({
            "doi": doi,
            "pmc": pmc,
            "table_rows": table_rows,
            "convertible": attempts,
            "stored": len(stored),
            "rejected": len(rejected),
            "reasons": dict(reasons.most_common()),
            "effects": [
                {
                    "outcome": item.get("outcome"),
                    "effect": round(float(item["effect"]), 6),
                    "se": round(float(item["se"]), 6),
                    "n": item["n"],
                    "arms": json.loads(item.get("moderators") or "{}").get("arms", []),
                    "quote": str(item.get("quote") or "")[:200],
                }
                for item in stored
            ],
        })

    report = {
        "generated": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "documents": documents,
        "totals": dict(totals),
    }
    out = Path(args.json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Arm-Deskriptiva -> Hedges g (sechs XML-Dokumente)",
        "",
        f"Stand: {report['generated']}. Rechner: "
        "`research_agent/meta/arm_level.py` (deterministisch, kein LLM). "
        "Gespeichert wird nur, wenn beide Arme n und Streuung tragen und das "
        "Zitat woertlich im Dokument steht.",
        "",
        "| DOI | Tabellenzeilen | umrechenbar | gespeichert | verworfen |",
        "|---|---:|---:|---:|---:|",
    ]
    for doc in documents:
        lines.append(f"| {doc['doi']} | {doc['table_rows']} | {doc['convertible']} | "
                     f"{doc['stored']} | {doc['rejected']} |")
    lines += [
        f"| **Summe** | {totals['table_rows']} | {totals['convertible']} | "
        f"**{totals['stored']}** | {totals['rejected']} |",
        "",
        "## Warum Zeilen verworfen wurden",
        "",
    ]
    all_reasons = Counter()
    for doc in documents:
        all_reasons.update(doc["reasons"])
    for reason, count in all_reasons.most_common():
        lines.append(f"- {count:4d}  {reason}")
    lines += ["", "## Gespeicherte Effekte", ""]
    for doc in documents:
        if not doc["effects"]:
            continue
        lines.append(f"### {doc['doi']}")
        lines.append("")
        lines.append("| Outcome | g | SE | n | Arme |")
        lines.append("|---|---:|---:|---:|---|")
        for effect in doc["effects"]:
            arms = "; ".join(
                f"{a.get('label', '')[:28]}: {a.get('mean')} ± {a.get('sd')} "
                f"(n={a.get('n')}, {a.get('sd_source')})"
                for a in effect["arms"])
            lines.append(f"| {effect['outcome'][:40]} | {effect['effect']} | "
                         f"{effect['se']} | {effect['n']} | {arms} |")
        lines.append("")
    Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(dict(totals), ensure_ascii=False))
    for reason, count in all_reasons.most_common():
        print(f"  {count:4d}  {reason}")
    print(f"JSON: {args.json}")
    print(f"MD:   {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
