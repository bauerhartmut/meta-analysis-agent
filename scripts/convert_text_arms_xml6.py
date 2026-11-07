"""Fliesstext-Arme ("mean +- SD", n im Satz) aus JATS-XML in Hedges g.

Wendet ``research_agent/meta/arm_text.py`` auf jeden Satz jedes Dokuments
der Manifest-Liste an. Gespeichert wird nur, was beide Arme mit Fallzahl
belegt, das Gate besteht und dessen Zitat woertlich im Dokument steht.

Aufruf:
    .venv/bin/python.exe scripts/convert_text_arms_xml6.py \
        --manifest data/bench/sol/manifest_all.json \
        --xml-dir data/bench/sol/xml \
        --db data/bench/sol/text_arms.db
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
from research_agent.meta.arm_text import (  # noqa: E402
    convert_sentence,
    split_sentences,
    store_text_arm_effects,
)

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
    parser.add_argument("--db", default="data/bench/xml6/text_arms.db")
    parser.add_argument("--json", default="data/bench/xml6/text_arms_20261107.json")
    parser.add_argument("--md", default="data/bench/xml6/text_arms_20261107.md")
    args = parser.parse_args(argv)

    sources = list(DOCUMENTS)
    if args.manifest:
        raw = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        sources = [(str(entry["doi"]), str(entry["pmc"])) for entry in raw]

    xml_dir = Path(args.xml_dir)
    db_path = Path(args.db)
    if db_path.exists():
        db_path.unlink()
    db = Database(str(db_path))

    documents, totals, missing = [], Counter(), []
    for doi, pmc in sources:
        xml_path = xml_dir / f"{pmc}.xml"
        if not xml_path.exists():
            missing.append(pmc)
            continue
        xml = xml_path.read_text(encoding="utf-8", errors="replace")
        text = _xml_to_text(xml)
        source_id = f"doi:{doi}"
        row = db.save_source_text(
            source_id, text, kind="xml",
            origin_url=f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML",
        )
        text_id = (row or {}).get("id", "")

        sentences = split_sentences(text)
        candidates, reasons = [], Counter()
        for _start, _end, sentence in sentences:
            candidate = convert_sentence(sentence)
            if candidate.get("ok"):
                candidates.append(candidate)
            else:
                reasons[candidate.get("reason") or "unbekannt"] += 1

        stored, rejected = store_text_arm_effects(
            db, source_id, text_id, text, candidates)
        for entry in rejected:
            reasons[entry.get("reason") or "unbekannt"] += 1

        totals.update({
            "sentences": len(sentences),
            "candidates": len(candidates),
            "stored": len(stored),
            "rejected": len(rejected),
        })
        documents.append({
            "doi": doi,
            "pmc": pmc,
            "sentences": len(sentences),
            "candidates": len(candidates),
            "stored": len(stored),
            "rejected": len(rejected),
            "reasons": dict(reasons.most_common()),
            "effects": [
                {
                    "outcome": item.get("outcome"),
                    "effect": round(float(item["effect"]), 6),
                    "se": round(float(item["se"]), 6),
                    "n": item["n"],
                    "time_point": item.get("time_point"),
                    "arms": json.loads(item.get("moderators") or "{}").get("arms", []),
                    "quote": str(item.get("quote") or "")[:300],
                }
                for item in stored
            ],
        })

    totals["missing_xml"] = len(missing)
    report = {
        "generated": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "documents": documents,
        "totals": dict(totals),
        "missing_xml": missing,
    }
    out = Path(args.json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    all_reasons = Counter()
    for doc in documents:
        all_reasons.update(doc["reasons"])
    lines = [
        "# Fliesstext-Arme -> Hedges g", "",
        f"Stand: {report['generated']}. Leser: `research_agent/meta/arm_text.py` "
        "(deterministisch, kein LLM). Gespeichert wird nur, wenn beide Arme "
        "Fallzahl und SD tragen, das Gate besteht und das Zitat woertlich im "
        "Dokument steht.", "",
        "| Kennzahl | Wert |", "|---|---:|",
        f"| Dokumente | {len(documents)} |",
        f"| Saetze geprueft | {totals['sentences']} |",
        f"| Kandidaten | {totals['candidates']} |",
        f"| **gespeichert** | **{totals['stored']}** |",
        f"| verworfen (Store) | {totals['rejected']} |",
        f"| fehlende XML | {totals['missing_xml']} |", "",
        "## Warum Saetze abgelehnt wurden", "",
    ]
    for reason, count in all_reasons.most_common():
        lines.append(f"- {count:5d}  {reason}")
    lines += ["", "## Gespeicherte Effekte", ""]
    for doc in documents:
        if not doc["effects"]:
            continue
        lines.append(f"### {doc['doi']}")
        lines.append("")
        lines.append("| Outcome | g | SE | n | Zeitpunkt | Arme |")
        lines.append("|---|---:|---:|---:|---|---|")
        for effect in doc["effects"]:
            arms = "; ".join(
                f"{a.get('label', '')[:28]}: {a.get('mean')} +- {a.get('sd')} (n={a.get('n')})"
                for a in effect["arms"])
            lines.append(f"| {str(effect['outcome'])[:40]} | {effect['effect']} | "
                         f"{effect['se']} | {effect['n']} | "
                         f"{effect.get('time_point') or '-'} | {arms} |")
        lines.append("")
    Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(dict(totals), ensure_ascii=False))
    for reason, count in all_reasons.most_common(12):
        print(f"  {count:5d}  {reason}")
    print(f"JSON: {args.json}")
    print(f"MD:   {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
