"""Die 83 Dokumente der Zugangsliste gegen die lokalen XML-Korpora matchen.

Quellen: ``data/bench/sol/xml`` (1056), ``data/bench/sol2/xml`` (31),
``data/bench/xml_all`` (43), ``data/bench/xml6`` (6).

Zuordnung ueber ``<article-id pub-id-type="pmid">`` und
``<article-id pub-id-type="doi">`` - die sind im PMC-XML eindeutig, anders
als der Titel, der auch in zitierenden Reviews steht.

Ausgabe: ``data/bench/sol2/match_xml_20261108.json`` mit gefunden/fehlt und
je Treffer der Zahl der SOL-Stellen im Volltext. Read-only.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

DIRS = [
    Path("data/bench/sol/xml"),
    Path("data/bench/sol2/xml"),
    Path("data/bench/xml_all"),
    Path("data/bench/xml6"),
]
OUT = Path("data/bench/sol2/match_xml_20261108.json")

PMID = re.compile(r'<article-id[^>]*pub-id-type="pmid"[^>]*>\s*(\d+)\s*</article-id>')
DOI = re.compile(r'<article-id[^>]*pub-id-type="doi"[^>]*>\s*([^<\s]+)\s*</article-id>')
SOL = re.compile(r"sleep[- ]onset|sleep[- ]latency|\bSOL\b", re.I)


def main() -> int:
    rows = list(csv.DictReader(
        open("data/bench/sol2/zugangsliste_20261108.csv", encoding="utf-8")))

    index = {}
    files = 0
    for directory in DIRS:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.xml")):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            files += 1
            pmid = PMID.search(text)
            doi = DOI.search(text)
            if pmid:
                index.setdefault(("pmid", pmid.group(1)), path)
            if doi:
                index.setdefault(("doi", doi.group(1).lower()), path)
    print(f"XML gelesen: {files}, Indizes: {len(index)}")

    matched, missing = [], []
    for row in rows:
        pmid = (row.get("pmid") or "").strip()
        doi = (row.get("doi") or "").strip().lower()
        path = index.get(("pmid", pmid)) or index.get(("doi", doi))
        entry = {
            "prioritaet": row.get("prioritaet"),
            "pmid": pmid,
            "doi": row.get("doi"),
            "jahr": row.get("jahr"),
            "titel": row.get("titel"),
        }
        if path is None:
            entry["status"] = "fehlt"
            missing.append(entry)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        plain = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))
        entry.update({
            "status": "gefunden",
            "xml": str(path),
            "bytes": path.stat().st_size,
            "sol_stellen": len(SOL.findall(plain)),
            "tabellen": len(re.findall(r"<table-wrap\b", text)),
        })
        matched.append(entry)

    payload = {
        "liste": len(rows),
        "xml_gelesen": files,
        "gefunden": len(matched),
        "fehlt": len(missing),
        "gefunden_eintraege": matched,
        "fehlende_eintraege": missing,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                   encoding="utf-8")

    by_prio = {}
    for e in matched:
        by_prio[e["prioritaet"]] = by_prio.get(e["prioritaet"], 0) + 1
    print(f"Gefunden: {len(matched)} von {len(rows)} | fehlt: {len(missing)}")
    print("Nach Prioritaet:", by_prio)
    print("\nGefundene mit SOL-Stellen:")
    for e in sorted(matched, key=lambda x: -x["sol_stellen"]):
        print(f"  {e['prioritaet']} {e['pmid']} SOL={e['sol_stellen']:>4} "
              f"Tab={e['tabellen']:>2} {e['titel'][:58]}")
    print(f"JSON: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
