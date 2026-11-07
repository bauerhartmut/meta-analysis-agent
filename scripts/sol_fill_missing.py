"""Fehlende SOL-XML parallel nachladen (dieselbe Manifest-Liste).

Der sequenzielle Download im Suchskript wartet je Dokument auf die Antwort;
bei ~1000 Dokumenten dauert das fast zwei Stunden. Dieses Skript holt
dieselben Eintraege aus ``data/bench/sol/manifest_all.json`` mit sechs
gleichzeitigen Anfragen nach. Bereits vorhandene Dateien werden
uebersprungen, daher kann es neben dem Suchskript laufen.

Kein neuer Suchlauf: es wird ausschliesslich die vorhandene Manifest-Liste
abgearbeitet.

Aufruf:
    .venv/bin/python.exe scripts/sol_fill_missing.py [--workers 6]
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE = Path("data/bench/sol")
XML = BASE / "xml"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
UA = "Mozilla/5.0 (Research Agent; Academic Use)"


def fetch(entry: dict) -> str:
    target = XML / f"{entry['pmc']}.xml"
    if target.exists() and target.stat().st_size > 500:
        return "present"
    for attempt in range(3):
        try:
            request = urllib.request.Request(
                EPMC.format(pmcid=entry["pmc"]), headers={"User-Agent": UA})
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read()
            if body and b"<article" in body[:4000]:
                target.write_bytes(body)
                return "loaded"
            return "bad-body"
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 503) and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            return f"http{exc.code}"
        except Exception:
            time.sleep(1)
            continue
    return "failed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    manifest = json.loads((BASE / "manifest_all.json").read_text(encoding="utf-8"))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(fetch, manifest))
    print(json.dumps(dict(Counter(results)), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
