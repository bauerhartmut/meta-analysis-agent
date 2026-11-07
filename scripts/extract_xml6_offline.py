"""Sechs JATS-Volltexte offline durch die Extraktionskette schicken.

Der Test beantwortet die Frage hinter dem DOI-Backfill: Wie viele poolbare
Effekte mit SE/CI und nachpruefbarem Zitat entstehen wirklich aus den
XML-Dokumenten, die `check_xml_availability.py` als tabellenreich gemeldet
hat?

Die Kette ist dieselbe wie im Orchestrator (orchestrator.py, Phase
Effekt-Extraktion):

    _xml_to_text  ->  save_source_text
    blocks_from_jats  ->  save_extracted_tables
    augment_document_text  ->  Effekt-Extraktor (zwei unabhaengige Lesungen)

Kein Netzlauf, keine Suche, keine neue Studie: die XML-Dateien liegen unter
``data/bench/xml6/``. Nur der Extraktor spricht mit dem LLM-Backend.

Poolbar heisst hier exakt wie in ``meta/validation.py`` und
``meta/pooling.py``: nicht strittig, kein Ablehnungsgrund, SE oder beide
CI-Grenzen vorhanden und das Zitat im gespeicherten Dokument auffindbar.

Aufruf:
    .venv/bin/python.exe scripts/extract_xml6_offline.py --dry-run
    .venv/bin/python.exe scripts/extract_xml6_offline.py \
        --json data/bench/xml6/extraktion_20261107.json \
        --md data/bench/xml6/extraktion_20261107.md
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _xml_to_text  # noqa: E402
from research_agent.database import Database  # noqa: E402
from research_agent.meta.extraction import EffectExtractor  # noqa: E402
from research_agent.research.fulltext import locate_quote, split_sections  # noqa: E402
from research_agent.research.jats_tables import blocks_from_jats  # noqa: E402
from research_agent.research.table_extractor import (  # noqa: E402
    augment_document_text,
)

# Die sechs Dokumente aus data/bench/backfill/xml_nach_backfill_20261107.json,
# die mindestens eine Tabellenzeile mit CI tragen.
DOCUMENTS = [
    ("10.1001/jamanetworkopen.2026.26983", "PMC13448793"),
    ("10.3389/fnut.2026.1890075", "PMC13520769"),
    ("10.3390/healthcare13020180", "PMC11765054"),
    ("10.3390/ijms27146320", "PMC13409838"),
    ("10.3390/medicina62040662", "PMC13117668"),
    ("10.5888/pcd20.230198", "PMC10756651"),
]

TOPIC = "does melatonin improve sleep onset latency"


def _num(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _poolable(row: dict, text: str) -> tuple[bool, str]:
    """Spiegelt die Pooling-Regel: Praezision, kein Streit, belegtes Zitat."""
    if int(row.get("disputed") or 0) != 0:
        return False, "disputed"
    if str(row.get("rejection_reason") or "").strip():
        return False, "rejected"
    has_se = _num(row.get("se")) is not None
    has_ci = _num(row.get("ci_low")) is not None and _num(row.get("ci_high")) is not None
    if not (has_se or has_ci):
        return False, "no_precision"
    quote = str(row.get("quote") or "").strip()
    if not quote:
        return False, "no_quote"
    span = locate_quote(text, quote)
    if not span:
        return False, "quote_not_found"
    return True, "poolable"


def _prepare(db: Database, doi: str, pmc: str, xml_dir: Path) -> dict:
    """XML -> Text + Bloecke, wie im Orchestrator, aber ohne Netzzugriff."""
    xml_path = xml_dir / f"{pmc}.xml"
    xml = xml_path.read_text(encoding="utf-8", errors="replace")
    text = _xml_to_text(xml)
    source_id = f"doi:{doi}"
    sections = split_sections(text)
    row = db.save_source_text(
        source_id, text, kind="xml",
        origin_url=f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML",
        sections=sections,
    )
    jats_blocks = blocks_from_jats(xml)
    if jats_blocks and row:
        db.save_extracted_tables(source_id, row["id"], jats_blocks)
    text_for_llm, text_blocks = augment_document_text(text)
    if text_blocks and row:
        db.save_extracted_tables(source_id, row["id"],
                                 [b.to_dict() for b in text_blocks])
    stat_rows = sum(len(b.get("effect_cells") or []) for b in jats_blocks)
    return {
        "source_id": source_id,
        "text_id": (row or {}).get("id", ""),
        "text": text,
        "text_for_llm": text_for_llm,
        "sections": sections,
        "chars": len(text),
        "jats_blocks": len(jats_blocks),
        "jats_stat_rows": stat_rows,
        "text_blocks": len(text_blocks),
    }


async def _run_document(db: Database, doc: dict) -> dict:
    from research_agent.llm.engine import LLMEngine

    extractor = EffectExtractor(LLMEngine(), db, double_pass=True)
    await extractor.extract(
        doc["source_id"], doc["text_for_llm"], topic=TOPIC,
        sections=doc["sections"], source_text_id=doc["text_id"],
    )
    rows = db.get_study_effects(source_id=doc["source_id"]) or []

    verdicts = []
    for row in rows:
        ok, reason = _poolable(row, doc["text"])
        verdicts.append({
            "outcome": row.get("outcome") or "",
            "effect_type": row.get("effect_type") or "",
            "effect": row.get("effect"),
            "se": row.get("se"),
            "ci_low": row.get("ci_low"),
            "ci_high": row.get("ci_high"),
            "disputed": int(row.get("disputed") or 0),
            "rejection_reason": row.get("rejection_reason") or "",
            "poolable": ok,
            "reason": reason,
            "quote": str(row.get("quote") or "")[:220],
        })
    return {
        "doi": doc["source_id"].replace("doi:", ""),
        "chars": doc["chars"],
        "jats_blocks": doc["jats_blocks"],
        "jats_stat_rows": doc["jats_stat_rows"],
        "text_blocks": doc["text_blocks"],
        "rows": len(rows),
        "poolable": sum(1 for v in verdicts if v["poolable"]),
        "with_se": sum(1 for v in verdicts if v["se"] not in (None, "")),
        "with_ci": sum(1 for v in verdicts
                       if v["ci_low"] not in (None, "") and v["ci_high"] not in (None, "")),
        "disputed": sum(1 for v in verdicts if v["disputed"]),
        "rejected": sum(1 for v in verdicts if v["reason"] == "rejected"),
        "unverified_quote": sum(1 for v in verdicts if v["reason"] == "quote_not_found"),
        "effects": verdicts,
    }


def _write_md(path: Path, report: dict) -> None:
    totals = report["totals"]
    lines = [
        "# Extraktion der sechs XML-Dokumente (offline)",
        "",
        f"Stand: {report['generated']}. Kette: `_xml_to_text` -> "
        "`save_source_text` -> `blocks_from_jats`/`augment_document_text` -> "
        "`EffectExtractor` (zwei unabhaengige Lesungen). Kein Netzlauf, nur "
        "die XML-Dateien aus `data/bench/xml6/`.",
        "",
        "Poolbar = nicht strittig, kein Ablehnungsgrund, SE oder beide "
        "CI-Grenzen, Zitat per `locate_quote` im gespeicherten Text belegt.",
        "",
        "| DOI | Zeichen | JATS-Blöcke | stat. Zeilen | Effektzeilen | poolbar | mit SE | mit CI |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for doc in report["documents"]:
        if "error" in doc:
            lines.append(f"| {doc['doi']} | - | - | - | - | - | - | - |")
            continue
        lines.append(
            f"| {doc['doi']} | {doc['chars']} | {doc['jats_blocks']} | "
            f"{doc['jats_stat_rows']} | {doc['rows']} | {doc['poolable']} | "
            f"{doc['with_se']} | {doc['with_ci']} |")
    lines += [
        f"| **Summe** | | {totals['jats_blocks']} | {totals['jats_stat_rows']} | "
        f"**{totals['rows']}** | **{totals['poolable']}** | {totals['with_se']} | "
        f"{totals['with_ci']} |",
        "",
        f"Strittig: {totals['disputed']} | abgelehnt: {totals['rejected']} | "
        f"Zitat nicht auffindbar: {totals['unverified_quote']}",
        "",
        "## Einzelne Zeilen",
        "",
    ]
    for doc in report["documents"]:
        if "error" in doc or not doc["effects"]:
            continue
        lines.append(f"### {doc['doi']}")
        lines.append("")
        lines.append("| Outcome | Typ | Effekt | SE | CI | poolbar | Grund |")
        lines.append("|---|---|---:|---:|---|---|---|")
        for e in doc["effects"]:
            ci = ""
            if e["ci_low"] not in (None, "") and e["ci_high"] not in (None, ""):
                ci = f"{e['ci_low']}–{e['ci_high']}"
            lines.append(
                f"| {(e['outcome'] or '')[:44]} | {e['effect_type']} | "
                f"{e['effect']} | {e['se'] or ''} | {ci} | "
                f"{'ja' if e['poolable'] else 'nein'} | {e['reason']} |")
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml-dir", default="data/bench/xml6")
    parser.add_argument("--db", default="data/bench/xml6/extract.db")
    parser.add_argument("--json", default="data/bench/xml6/extraktion_20261107.json")
    parser.add_argument("--md", default="data/bench/xml6/extraktion_20261107.md")
    parser.add_argument("--dry-run", action="store_true",
                        help="nur Text/Blöcke vorbereiten, kein LLM-Aufruf")
    args = parser.parse_args(argv)

    import datetime as dt
    xml_dir = Path(args.xml_dir)
    db_path = Path(args.db)
    if db_path.exists():
        db_path.unlink()
    db = Database(str(db_path))

    prepared, report_docs = [], []
    for doi, pmc in DOCUMENTS:
        try:
            doc = _prepare(db, doi, pmc, xml_dir)
        except Exception as exc:  # ein kaputtes Dokument stoppt die Messung nicht
            report_docs.append({"doi": doi, "pmc": pmc, "error": f"{exc}"})
            continue
        prepared.append(doc)
        report_docs.append({
            "doi": doi, "pmc": pmc, "chars": doc["chars"],
            "jats_blocks": doc["jats_blocks"], "jats_stat_rows": doc["jats_stat_rows"],
            "text_blocks": doc["text_blocks"], "rows": 0, "poolable": 0,
            "with_se": 0, "with_ci": 0, "disputed": 0, "rejected": 0,
            "unverified_quote": 0, "effects": [],
        })

    if not args.dry_run:
        for doc, entry in zip(prepared, [d for d in report_docs if "error" not in d]):
            try:
                result = asyncio.run(_run_document(db, doc))
            except Exception as exc:
                entry["error"] = f"{exc}"
                traceback.print_exc()
                continue
            entry.update({k: v for k, v in result.items()
                          if k not in ("doi", "chars", "jats_blocks",
                                       "jats_stat_rows", "text_blocks")})

    ok = [d for d in report_docs if "error" not in d]
    totals = {key: sum(d.get(key, 0) for d in ok)
              for key in ("jats_blocks", "jats_stat_rows", "rows", "poolable",
                          "with_se", "with_ci", "disputed", "rejected",
                          "unverified_quote")}
    report = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "topic": TOPIC,
        "dry_run": bool(args.dry_run),
        "documents": report_docs,
        "totals": totals,
    }
    out = Path(args.json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_md(Path(args.md), report)
    print(json.dumps(totals, ensure_ascii=False))
    for doc in ok:
        print(f"  {doc['doi']}: {doc['rows']} Zeilen, {doc['poolable']} poolbar, "
              f"{doc['with_se']} SE, {doc['with_ci']} CI")
    print(f"JSON: {args.json}")
    print(f"MD:   {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
