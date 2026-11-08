"""PDF-Volltexte durch die bestehende Extraktionskette schicken (offline).

Gedacht fuer die bestellten Artikel: sobald sie als PDF in
``data/bench/sol2/volltext/`` liegen, laufen dieselben deterministischen Leser
darauf wie auf den XML - ohne Umbau.

Kette je PDF:
  1. Text auslesen (pypdf, wie im Coverage-Manager).
  2. Fliesstext-Arme: ``meta/arm_text.py`` (mean +- SD mit n im Satz).
  3. Textbloecke: ``research/table_extractor.find_table_blocks``; deren Zeilen
     gehen durch ``meta/effect_columns.effects_from_row`` (direkte Effekte).

Kein Modell, kein Netz. Gespeichert wird nur mit woertlichem Zitat.

Aufruf:
    .venv/bin/python.exe scripts/read_pdf_corpus.py --dir data/bench/sol2/volltext
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _pdf_to_text  # noqa: E402
from research_agent.database import Database  # noqa: E402
from research_agent.meta.arm_text import (  # noqa: E402
    store_text_arm_effects,
    text_arm_candidates,
)
from research_agent.meta.effect_columns import (  # noqa: E402
    effects_from_row,
    store_direct_effects,
)
from research_agent.meta.outcome_labels import normalize_outcome  # noqa: E402
from research_agent.research.table_extractor import find_table_blocks  # noqa: E402

POOLABLE = {"g", "smd", "mean_diff"}


def is_sol(label: str) -> bool:
    """True, wenn der Outcome-Name die Einschaflatenz meint."""
    text = normalize_outcome(label) or ""
    return "sleep onset latency" in text or bool(re.search(r"\bsol\b", text))


def rows_from_block(body: str) -> tuple[list[str], list[list[str]]]:
    """(Kopf, Zeilen) aus einem Textblock - Pipes oder Spaltenabstaende."""
    lines = [line for line in str(body or "").splitlines() if line.strip()]
    if len(lines) < 2:
        return [], []
    if any("|" in line for line in lines):
        rows = [[cell.strip() for cell in line.strip().strip("|").split("|")]
                for line in lines]
    else:
        rows = [re.split(r"\s{2,}", line.strip()) for line in lines]
    return rows[0], rows[1:]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default="data/bench/sol2/volltext")
    parser.add_argument("--db", default="data/bench/sol2/pdf.db")
    parser.add_argument("--json", default="data/bench/sol2/pdf.json")
    parser.add_argument("--md", default="data/bench/sol2/pdf.md")
    parser.add_argument("--max", type=int, default=20)
    parser.add_argument("--min-chars", type=int, default=2000)
    args = parser.parse_args(argv)

    pdfs = sorted(Path(args.dir).glob("*.pdf"))[: max(1, args.max)]
    db_path = Path(args.db)
    if db_path.exists():
        db_path.unlink()
    db = Database(str(db_path))

    documents, problems = [], Counter()
    for pdf in pdfs:
        text = _pdf_to_text(pdf) or ""
        if len(text) < args.min_chars:
            documents.append({"file": pdf.name, "chars": len(text),
                              "error": "zu wenig Text"})
            problems["zu wenig Text (Scan oder kaputt)"] += 1
            continue
        source_id = f"pdf:{pdf.stem}"
        row = db.save_source_text(source_id, text, kind="pdf", origin_url=pdf.name)
        text_id = (row or {}).get("id", "")

        arm_candidates = text_arm_candidates(text)
        stored_arm, rejected_arm = store_text_arm_effects(
            db, source_id, text_id, text, arm_candidates)
        for entry in rejected_arm:
            problems[str(entry.get("reason"))[:60]] += 1

        direct_candidates = []
        blocks = find_table_blocks(text)
        for block in blocks:
            header, rows = rows_from_block(block.body)
            if not rows:
                continue
            for cells in rows:
                found, reason = effects_from_row(header, cells, block.body,
                                                 caption=block.caption)
                if found:
                    direct_candidates.extend(found)
                else:
                    problems[str(reason)[:60]] += 1
        stored_direct, rejected_direct = store_direct_effects(
            db, source_id, text_id, text, direct_candidates)
        for entry in rejected_direct:
            problems[str(entry.get("reason"))[:60]] += 1

        all_rows = list(stored_arm) + list(stored_direct)
        sol_rows = [r for r in all_rows if is_sol(str(r.get("outcome") or ""))]
        documents.append({
            "file": pdf.name, "chars": len(text), "source": source_id,
            "arm_candidates": len(arm_candidates), "arm_stored": len(stored_arm),
            "blocks": len(blocks), "direct_candidates": len(direct_candidates),
            "direct_stored": len(stored_direct),
            "rows": len(all_rows), "sol_rows": len(sol_rows),
            "sol_poolable": sum(1 for r in sol_rows
                                if r.get("effect_type") in POOLABLE),
            "sol": [{"outcome": r.get("outcome"), "type": r.get("effect_type"),
                     "effect": r.get("effect"), "unit": r.get("unit")}
                    for r in sol_rows],
        })

    ok = [d for d in documents if "error" not in d]
    report = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "directory": str(args.dir),
        "pdfs": len(pdfs),
        "readable": len(ok),
        "rows": sum(d["rows"] for d in ok),
        "sol_rows": sum(d["sol_rows"] for d in ok),
        "k_sol_poolable": sum(1 for d in ok if d["sol_poolable"]),
        "problems": dict(problems.most_common(12)),
        "documents": documents,
    }
    Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2),
                               encoding="utf-8")

    lines = [
        "# PDF-Volltexte durch die Kette", "",
        f"Stand: {report['generated']}. Verzeichnis: `{args.dir}`. "
        "Deterministisch, kein Netz, kein Modell.", "",
        "| Kennzahl | Wert |", "|---|---:|",
        f"| PDFs gefunden | {report['pdfs']} |",
        f"| lesbar | {report['readable']} |",
        f"| gespeicherte Zeilen | {report['rows']} |",
        f"| davon Einschaflatenz | {report['sol_rows']} |",
        f"| **k (PDFs mit poolbarer SOL-Zeile)** | **{report['k_sol_poolable']}** |",
        "", "## Je PDF", "",
        "| Datei | Zeichen | Arme | Bloecke | direkte Effekte | Zeilen | SOL |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for doc in documents:
        if "error" in doc:
            lines.append(f"| {doc['file']} | {doc['chars']} | - | - | - | - | - |")
            continue
        lines.append(f"| {doc['file']} | {doc['chars']} | {doc['arm_stored']} | "
                     f"{doc['blocks']} | {doc['direct_stored']} | {doc['rows']} | "
                     f"{doc['sol_rows']} |")
    lines += ["", "## Ablehnungsgruende", ""]
    for reason, count in problems.most_common(10):
        lines.append(f"- {count:5d}  {reason}")
    lines += [
        "", "## Grenzen", "",
        "- PDF-Text hat keine Tabellenstruktur; Zwei-Arm-Tabellen werden nur",
        "  gelesen, wenn ihre Zeilen als Textblock erkennbar sind.",
        "- Gescannte PDFs ohne Textebene liefern nichts; das steht als",
        "  'zu wenig Text' im Bericht.",
    ]
    Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"pdfs={report['pdfs']} lesbar={report['readable']} zeilen={report['rows']} "
          f"sol={report['sol_rows']} k={report['k_sol_poolable']}")
    for reason, count in problems.most_common(6):
        print(f"  {count:5d}  {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
