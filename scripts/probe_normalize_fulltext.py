"""Normalisierung gegen echte Volltexte pruefen (read-only, offline).

Die PDF-Kette wendet ``meta/pdf_text.normalize`` auf jeden Dokumenttext an.
Dieses Skript misst, was dabei mit echtem Text passiert: Zahlen, Tabellenzeilen,
Textbloecke und Fliesstext-Kandidaten vor und nach der Normalisierung.

Geprueft werden die 34 geloesten Volltexte in ``data/bench/sol2/fulltext``.
Ein harter Fehler ist jede Aenderung an einer Zahl; weiche Warnungen sind
verlorene Tabellenzeilen oder Bloecke, weil dort Struktur verloren gehen kann.

Aufruf:
    .venv/bin/python.exe scripts/probe_normalize_fulltext.py
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.meta.arm_text import text_arm_candidates  # noqa: E402
from research_agent.meta.pdf_text import normalize  # noqa: E402
from research_agent.research.table_extractor import find_table_blocks  # noqa: E402

NUM = r"\d+(?:[.,]\d+)?"
TABULAR = r"\s{2,}|\|"


def measure(text: str) -> dict:
    """Kennzahlen eines Texts, die die Normalisierung nicht aendern darf."""
    blocks = find_table_blocks(text)
    block_rows = sum(len([l for l in b.body.splitlines() if l.strip()])
                     for b in blocks)
    return {
        "chars": len(text),
        "lines": text.count("\n") + 1,
        "numbers": Counter(__import__("re").findall(NUM, text)),
        "tabular_lines": sum(1 for l in text.splitlines()
                            if __import__("re").search(TABULAR, l)),
        "blocks": len(blocks),
        "block_rows": block_rows,
        "arm_candidates": len(text_arm_candidates(text)),
    }


def compare(before: dict, after: dict) -> list[str]:
    """Harte und weiche Abweichungen benennen."""
    problems = []
    if before["numbers"] != after["numbers"]:
        lost = before["numbers"] - after["numbers"]
        added = after["numbers"] - before["numbers"]
        problems.append(f"ZAHLEN geaendert (verloren {sum(lost.values())}, "
                        f"dazu {sum(added.values())})")
    if after["tabular_lines"] < before["tabular_lines"]:
        problems.append(f"Tabellenzeilen {before['tabular_lines']} -> "
                        f"{after['tabular_lines']}")
    if after["blocks"] < before["blocks"]:
        problems.append(f"Bloecke {before['blocks']} -> {after['blocks']}")
    if after["block_rows"] < before["block_rows"]:
        problems.append(f"Blockzeilen {before['block_rows']} -> {after['block_rows']}")
    if after["arm_candidates"] < before["arm_candidates"]:
        problems.append(f"Arm-Kandidaten {before['arm_candidates']} -> "
                        f"{after['arm_candidates']}")
    return problems


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data/bench/sol2/fulltext")
    ap.add_argument("--json",
                    default="data/bench/sol2/normalisierung_echte_texte_20261108.json")
    args = ap.parse_args(argv[1:])

    files = sorted(Path(args.dir).glob("*.txt"))
    if not files:
        print(f"keine .txt in {args.dir}")
        return 2

    rows, hard, soft = [], 0, 0
    for path in files:
        raw = path.read_text(encoding="utf-8", errors="replace")
        norm = normalize(raw)
        before, after = measure(raw), measure(norm)
        problems = compare(before, after)
        if any(p.startswith("ZAHLEN") for p in problems):
            hard += 1
        elif problems:
            soft += 1
        rows.append({
            "file": path.name,
            "chars": before["chars"],
            "lines": [before["lines"], after["lines"]],
            "tabular_lines": [before["tabular_lines"], after["tabular_lines"]],
            "blocks": [before["blocks"], after["blocks"]],
            "block_rows": [before["block_rows"], after["block_rows"]],
            "arm_candidates": [before["arm_candidates"], after["arm_candidates"]],
            "problems": problems,
        })

    summary = {
        "dir": str(args.dir),
        "files": len(files),
        "hard_failures": hard,
        "files_with_warnings": soft,
        "chars_total": sum(r["chars"] for r in rows),
        "tabular_lines_lost": sum(r["tabular_lines"][0] - r["tabular_lines"][1] for r in rows),
        "blocks_lost": sum(r["blocks"][0] - r["blocks"][1] for r in rows),
        "rows_lost": sum(r["block_rows"][0] - r["block_rows"][1] for r in rows),
        "arm_before": sum(r["arm_candidates"][0] for r in rows),
        "arm_after": sum(r["arm_candidates"][1] for r in rows),
    }
    Path(args.json).write_text(
        json.dumps({"summary": summary, "files": rows}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    print(f"dateien={summary['files']} zeichen={summary['chars_total']} "
          f"harte_fehler={hard} warnungen={soft}")
    print(f"tabellenzeilen verloren={summary['tabular_lines_lost']} "
          f"bloecke verloren={summary['blocks_lost']} "
          f"blockzeilen verloren={summary['rows_lost']} "
          f"arm_kandidaten {summary['arm_before']} -> {summary['arm_after']}")
    for row in rows:
        if row["problems"]:
            print(f"  {row['file']}: {'; '.join(row['problems'])}")
    return 0 if hard == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
