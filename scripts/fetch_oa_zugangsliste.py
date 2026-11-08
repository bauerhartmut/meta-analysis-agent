"""Open-Access-Status der 83 Zugangsliste-Dokumente pruefen und OA-PDFs holen.

Die 83 sind die Dokumente ohne PMC-Volltext (siehe ``fetch_log.json``). Ein
Teil davon ist bei den Verlagen offen zugaenglich; Europe PMC listet diese
unter ``fullTextUrlList``. Nur als "Open access" markierte URLs werden
geladen - keine Paywall, keine Umgehung.

Ablauf je Dokument (ein Lauf, sequenziell, 0,4 s Pause):
  1. Europe PMC search nach DOI, resultType=core
  2. OA-PDF-URL aus fullTextUrlList (falls vorhanden)
  3. PDF laden, Text mit pypdf extrahieren
  4. SOL-Stellen mit Kontext sammeln

Ausgabe: ``data/bench/sol2/oa_status_20261108.json`` und die Texte unter
``data/bench/sol2/volltext/``.
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
OUT = Path("data/bench/sol2")
TXT = OUT / "volltext"
TXT.mkdir(parents=True, exist_ok=True)
PAUSE = 0.4
SOL = re.compile(r"sleep[- ]onset|sleep[- ]latency|\bSOL\b", re.I)


def get(url: str, binary: bool = False, tries: int = 3):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-agent/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read() if binary else resp.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(str(last))


def oa_pdf_url(record: dict) -> str | None:
    urls = ((record.get("fullTextUrlList") or {}).get("fullTextUrl") or [])
    for entry in urls:
        if str(entry.get("availability", "")).lower().startswith("open") \
                and str(entry.get("documentStyle", "")).lower() == "pdf":
            return entry.get("url")
    for entry in urls:
        if str(entry.get("availability", "")).lower().startswith("open"):
            return entry.get("url")
    return None


def main() -> int:
    rows = list(csv.DictReader(
        open("data/bench/sol2/zugangsliste_20261108.csv", encoding="utf-8")))
    log = []
    for index, row in enumerate(rows, start=1):
        doi = (row.get("doi") or "").strip()
        pmid = (row.get("pmid") or "").strip()
        entry = {"pmid": pmid, "doi": doi, "prioritaet": row.get("prioritaet"),
                 "titel": row.get("titel")}
        if not doi:
            entry["status"] = "keine DOI"
            log.append(entry)
            continue
        query = f'DOI:"{doi}"'
        url = f"{BASE}?query={urllib.parse.quote(query)}&resultType=core&format=json"
        try:
            data = json.loads(get(url))
        except Exception as exc:  # noqa: BLE001
            entry["status"] = f"abfrage fehler: {exc}"[:160]
            log.append(entry)
            time.sleep(PAUSE)
            continue
        results = (data.get("resultList") or {}).get("result") or []
        if not results:
            entry["status"] = "nicht gefunden"
            log.append(entry)
            time.sleep(PAUSE)
            continue
        rec = results[0]
        entry["europepmc_source"] = rec.get("source")
        entry["europepmc_id"] = rec.get("id")
        entry["has_pmc"] = bool(rec.get("pmcid"))
        pdf = oa_pdf_url(rec)
        if not pdf:
            entry["status"] = "kein OA-PDF"
            log.append(entry)
            time.sleep(PAUSE)
            continue
        entry["pdf_url"] = pdf
        target = TXT / f"{pmid}.pdf"
        try:
            blob = get(pdf, binary=True)
            target.write_bytes(blob)
        except Exception as exc:  # noqa: BLE001
            entry["status"] = f"download fehler: {exc}"[:160]
            log.append(entry)
            time.sleep(PAUSE)
            continue
        text = ""
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(target))
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
            (TXT / f"{pmid}.txt").write_text(text, encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            entry["status"] = f"pdf nicht lesbar: {exc}"[:160]
            log.append(entry)
            time.sleep(PAUSE)
            continue
        hits = [m.start() for m in SOL.finditer(text)]
        entry.update({
            "status": "geholt",
            "bytes": len(blob),
            "text_chars": len(text),
            "sol_stellen": len(hits),
        })
        log.append(entry)
        print(f"[{index}/{len(rows)}] {pmid} geholt, {len(text)} Zeichen, "
              f"SOL-Stellen {len(hits)}")
        time.sleep(PAUSE)

    (OUT / "oa_status_20261108.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = {}
    for entry in log:
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    print("Status:", counts)
    print("OA-Geholt:", sum(1 for e in log if e["status"] == "geholt"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
