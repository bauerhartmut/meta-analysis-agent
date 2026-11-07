"""Change-Score-Arme ("mean change +- SD") aus JATS-XML in Hedges g.

Zwei Modelle (siehe ``research_agent/meta/arm_change.py``):
  * ``reported`` - der Satz nennt die Veraenderung selbst, g ist exakt.
  * ``prepost``  - der Satz nennt prae und post; die Change-SD haengt von
    der Korrelation ab, die gespeichert wird (rho = 0.5) samt
    Sensitivitaetsgrid.

Aufruf:
    .venv/bin/python.exe scripts/convert_change_arms_xml6.py \
        --manifest data/bench/sol/manifest_all.json \
        --xml-dir data/bench/sol/xml \
        --db data/bench/sol/change_arms.db
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
from research_agent.meta.arm_change import (  # noqa: E402
    DEFAULT_RHO,
    RHO_GRID,
    change_candidates,
    convert_sentence,
    split_sentences,
    store_change_effects,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml-dir", default="data/bench/sol/xml")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--db", default="data/bench/sol/change_arms.db")
    parser.add_argument("--json", default="data/bench/sol/change_arms_20261107.json")
    parser.add_argument("--md", default="data/bench/sol/change_arms_20261107.md")
    args = parser.parse_args(argv)

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

        stored, rejected = store_change_effects(
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
                    "model": json.loads(item.get("moderators") or "{}").get("change_model"),
                    "rho": json.loads(item.get("moderators") or "{}").get("rho"),
                    "sensitivity": json.loads(item.get("moderators") or "{}").get("sensitivity", []),
                    "arms": json.loads(item.get("moderators") or "{}").get("arms", []),
                    "quote": str(item.get("quote") or "")[:300],
                }
                for item in stored
            ],
        })

    totals["missing_xml"] = len(missing)
    report = {
        "generated": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "rho_assumed": DEFAULT_RHO,
        "rho_grid": list(RHO_GRID),
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
    by_model = Counter()
    for doc in documents:
        for effect in doc["effects"]:
            by_model[effect["model"]] += 1
    lines = [
        "# Veraenderungswerte -> Hedges g (rho offengelegt)", "",
        f"Stand: {report['generated']}. Leser: `research_agent/meta/arm_change.py`.",
        f"Bei Prae/Post-Werten ist die Change-SD von rho abhaengig; gespeichert "
        f"wird rho = {DEFAULT_RHO}, das Grid steht je Zeile.", "",
        "| Kennzahl | Wert |", "|---|---:|",
        f"| Dokumente | {len(documents)} |",
        f"| Saetze geprueft | {totals['sentences']} |",
        f"| Kandidaten | {totals['candidates']} |",
        f"| **gespeichert** | **{totals['stored']}** |",
        f"| davon gemeldete Veraenderung | {by_model.get('reported', 0)} |",
        f"| davon prae/post gerechnet | {by_model.get('prepost', 0)} |", "",
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
        for effect in doc["effects"]:
            lines.append(f"* `{effect['outcome'][:50]}` | g = {effect['effect']} "
                         f"(SE {effect['se']}, n = {effect['n']}, Modell "
                         f"{effect['model']})")
            for arm in effect["arms"]:
                lines.append(f"  - {arm.get('label')}: change = {arm.get('mean')}, "
                             f"SD = {arm.get('sd')} ({arm.get('sd_source')}), "
                             f"n = {arm.get('n')}")
            if effect["sensitivity"]:
                grid = ", ".join(f"rho={row['rho']}: g={row['g']}"
                                 for row in effect["sensitivity"])
                lines.append(f"  - Sensitivitaet: {grid}")
        lines.append("")
    Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(dict(totals), ensure_ascii=False))
    print(f"Modelle: {dict(by_model)}")
    for reason, count in all_reasons.most_common(10):
        print(f"  {count:5d}  {reason}")
    print(f"JSON: {args.json}")
    print(f"MD:   {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
