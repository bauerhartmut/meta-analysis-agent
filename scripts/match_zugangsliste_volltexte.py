"""Die 83 Dokumente der Zugangsliste gegen die lokalen Volltexte matchen.

Zwei Quellen: ``data/bench/sol/fulltext`` (1093 PMC-Texte) und
``data/bench/sol2/fulltext`` (34 Texte). Die Zuordnung laeuft ueber PMID und
DOI, die im Metadatenkopf jeder Textdatei stehen - kein Raten ueber Titel.

Ausgabe: welche der 83 lokal liegen, mit Datei, Groesse und Position des
ersten SOL-Treffers. Read-only.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

DIRS = [Path("data/bench/sol/fulltext"), Path("data/bench/sol2/fulltext")]
OUT = Path("data/bench/sol2/match_volltexte_20261108.json")
SOL = re.compile(r"sleep[- ]onset|sleep[- ]latency|\bSOL\b", re.I)


def main() -> int:
    rows = list(csv.DictReader(
        open("data/bench/sol2/zugangsliste_20261108.csv", encoding="utf-8")))
    texts = []
    for directory in DIRS:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.txt")):
            head = path.read_text(encoding="utf-8", errors="replace")[:6000]
            texts.append((path, head))
    print(f"Texte im Korpus: {len(texts)}")

    matched, missing = [], []
    for row in rows:
        pmid = (row.get("pmid") or "").strip()
        doi = (row.get("doi") or "").strip().lower()
        hit = None
        for path, head in texts:
            low = head.lower()
            if pmid and re.search(rf"(?<!\d){re.escape(pmid)}(?!\d)", head):
                hit = (path, head, "pmid")
                break
            if doi and doi in low:
                hit = (path, head, "doi")
                break
        entry = {
            "prioritaet": row.get("prioritaet"),
            "pmid": pmid,
            "doi": row.get("doi"),
            "jahr": row.get("jahr"),
            "titel": row.get("titel"),
        }
        if hit is None:
            entry["status"] = "fehlt"
            missing.append(entry)
        else:
            path, head, how = hit
            match = SOL.search(head)
            entry.update({
                "status": "gefunden",
                "datei": str(path),
                "bytes": path.stat().st_size,
                "match_ueber": how,
                "sol_treffer": bool(match),
                "sol_kontext": (head[max(0, match.start() - 120):match.end() + 120]
                                if match else ""),
            })
            matched.append(entry)

    payload = {
        "liste": len(rows),
        "korpus_texte": len(texts),
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
    for e in missing:
        print(f"  FEHLT {e['prioritaet']} {e['pmid']} {e['titel'][:70]}")
    print(f"JSON: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
