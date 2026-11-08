"""Messen, ob colspan-verworfene Tabellenzeilen ueberhaupt Effektspalten tragen.

Hintergrund: Die Leser verwerfen Zeilen, deren Kopf- und Zellenzahl
auseinanderfaellt (``colspan``/``rowspan``). Offen war, ob ein
Spaltenaufloeser oder ein Vision-Lauf diese Zeilen retten koennte. Dieses
Skript beantwortet die Vorfrage ohne Netz und ohne Modell: traegt die
Kopfzeile einer solchen Zeile ueberhaupt eine Effektbezeichnung?

Aufruf:
    .venv/bin/python.exe scripts/measure_colspan_rows.py \
        --xml-dir data/bench/sol/xml_fetch_ncbi data/bench/sol/xml_q1 \
        --out data/bench/sol/colspan_messung_20261108.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.research.jats_tables import parse_jats  # noqa: E402

# Eine Effektbezeichnung als ganzes Wort; "CI" allein zaehlt mit, weil
# "g (95% CI)" die haeufigste Form ist - falsche Positive werden im Bericht
# einzeln geprueft, nicht weggerechnet.
EFFECT = re.compile(r"\b(g|smd|d|or|rr|hr|beta|mean\s?diff|md|ci)\b", re.I)


def scan(directory: Path) -> dict:
    total = with_effect = 0
    samples = []
    per_file = Counter()
    for path in sorted(directory.glob("*.xml")):
        for table in parse_jats(path):
            header = " | ".join(table.header)
            has_effect = bool(EFFECT.search(header))
            for row in table.rows:
                if len(table.header) == len(row.cells):
                    continue
                total += 1
                per_file[path.stem] += 1
                if has_effect:
                    with_effect += 1
                    if len(samples) < 10:
                        samples.append({
                            "pmc": path.stem,
                            "caption": (table.caption or table.label or "")[:160],
                            "header": header[:200],
                            "cells": " | ".join(row.cells)[:200],
                            "header_cols": len(table.header),
                            "cell_cols": len(row.cells),
                        })
    return {"dir": str(directory), "xml": len(list(directory.glob("*.xml"))),
            "mismatch_rows": total, "with_effect_header": with_effect,
            "files": dict(per_file.most_common(10)), "samples": samples}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml-dir", nargs="+",
                        default=["data/bench/sol/xml_fetch_ncbi", "data/bench/sol/xml_q1"])
    parser.add_argument("--out", default="data/bench/sol/colspan_messung_20261108.json")
    args = parser.parse_args(argv)

    results = []
    for item in args.xml_dir:
        directory = Path(item) if Path(item).is_absolute() else ROOT / item
        if not directory.is_dir():
            results.append({"dir": str(directory), "error": "Verzeichnis fehlt"})
            continue
        results.append(scan(directory))

    summary = {
        "mismatch_rows": sum(r.get("mismatch_rows", 0) for r in results),
        "with_effect_header": sum(r.get("with_effect_header", 0) for r in results),
        "dirs": results,
    }
    Path(args.out).write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("mismatch_rows", "with_effect_header")},
                     ensure_ascii=False))
    for item in results:
        if "error" in item:
            print(f"{item['dir']}: {item['error']}")
        else:
            print(f"{item['dir']}: {item['xml']} XML, {item['mismatch_rows']} Mismatch, "
                  f"{item['with_effect_header']} mit Effektkopf")
    print(f"JSON: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
