"""OpenAlex als zweite OA-Quelle fuer die 83 Zugangsliste-Dokumente.

Europe PMC listet fuer die 83 kein OA-PDF. OpenAlex kennt zusaetzlich
Repositorien- und Preprint-Kopien (``locations``). Nur als ``is_oa``
markierte PDFs werden geladen; keine Paywall.

Ausgabe: ``data/bench/sol2/oa_openalex_20261108.json``, Texte unter
``data/bench/sol2/volltext``.
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path("data/bench/sol2")
TXT = OUT / "volltext"
TXT.mkdir(parents=True, exist_ok=True)
PAUSE = 0.3
SOL = re.compile(r"sleep[- ]onset|sleep[- ]latency|\bSOL\b", re.I)
UA = "Mozilla/5.0 (research-agent; contact: local)"


def get(url: str, binary: bool = False, tries: int = 3):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read() if binary else resp.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(str(last))


def candidates(work: dict) -> list[str]:
    urls = []
    best = work.get("best_oa_location") or {}
    if best.get("pdf_url"):
        urls.append(best["pdf_url"])
    for loc in work.get("locations") or []:
        if loc.get("is_oa") and loc.get("pdf_url"):
            urls.append(loc["pdf_url"])
    seen, out = set(), []
    for url in urls:
        if url not in seen:
            seen.add(url)
            out.append(url)
    return out


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
        url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}"
        try:
            work = json.loads(get(url))
        except Exception as exc:  # noqa: BLE001
            entry["status"] = f"abfrage fehler: {exc}"[:140]
            log.append(entry)
            time.sleep(PAUSE)
            continue
        entry["is_oa"] = bool((work.get("open_access") or {}).get("is_oa"))
        urls = candidates(work)
        if not urls:
            entry["status"] = "kein OA-PDF"
            log.append(entry)
            time.sleep(PAUSE)
            continue
        entry["pdf_urls"] = urls[:3]
        got = False
        for pdf_url in urls[:2]:
            target = TXT / f"{pmid}.pdf"
            try:
                blob = get(pdf_url, binary=True)
                if len(blob) < 2000 or not blob.startswith(b"%PDF"):
                    continue
                target.write_bytes(blob)
                from pypdf import PdfReader
                text = "\n".join((p.extract_text() or "") for p in PdfReader(str(target)).pages)
                if len(text) < 500:
                    continue
                (TXT / f"{pmid}.txt").write_text(text, encoding="utf-8")
                entry.update({"status": "geholt", "pdf_url": pdf_url,
                              "bytes": len(blob), "text_chars": len(text),
                              "sol_stellen": len(SOL.findall(text))})
                got = True
                break
            except Exception:  # noqa: BLE001
                continue
        if not got:
            entry["status"] = "download/lies fehlgeschlagen"
        else:
            print(f"[{index}/{len(rows)}] {pmid} geholt, {entry['text_chars']} Zeichen, "
                  f"SOL {entry['sol_stellen']}")
        log.append(entry)
        time.sleep(PAUSE)

    (OUT / "oa_openalex_20261108.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    counts = {}
    for entry in log:
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    print("Status:", counts)
    print("Geholt:", sum(1 for e in log if e["status"] == "geholt"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
