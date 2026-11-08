"""Holt den Q2-Korpus fuer den Melatonin/SOL-Test.

Netzanteil bewusst klein: eine esearch-Anfrage, efetch fuer Metadaten,
danach efetch nur fuer die Dokumente mit PMC-Volltext. Alles andere wird als
"Zugang offen" protokolliert und nicht weiter verfolgt.
"""

from __future__ import annotations

import html
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path("data/bench/sol2")
XML_DIR = OUT / "xml"
OUT.mkdir(parents=True, exist_ok=True)
XML_DIR.mkdir(exist_ok=True)

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
Q_STRICT = (
    'melatonin[tiab] AND ("sleep onset latency"[tiab] OR "sleep latency"[tiab]) '
    "AND randomized controlled trial[pt]"
)
PAUSE = 0.5


def get(url: str, tries: int = 4) -> str:
    last: Exception | None = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "research-agent/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read().decode("utf-8", "replace")
        except Exception as exc:  # noqa: BLE001 - Netzfehler sollen geloggt, nicht verschluckt werden
            last = exc
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{url} fehlgeschlagen: {last}")


def esearch(term: str, retmax: int = 500) -> tuple[int, list[str]]:
    url = (
        f"{EUTILS}/esearch.fcgi?db=pubmed&retmode=json&retmax={retmax}"
        f"&term={urllib.parse.quote(term)}"
    )
    data = json.loads(get(url))["esearchresult"]
    return int(data["count"]), list(data.get("idlist", []))


def strip_tags(value: str) -> str:
    text = re.sub(r"<[^>]+>", "", value)
    return html.unescape(" ".join(text.split()))


def parse_pubmed(xml: str) -> list[dict]:
    records: list[dict] = []
    for block in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", xml, re.S):
        pmid = re.search(r"<PMID[^>]*>(\d+)</PMID>", block)
        title = re.search(r"<ArticleTitle>(.*?)</ArticleTitle>", block, re.S)
        year = re.search(r"<PubDate>.*?<Year>(\d{4})</Year>", block, re.S)
        doi = re.search(r'<ArticleId IdType="doi">([^<]+)</ArticleId>', block)
        pmc = re.search(r'<ArticleId IdType="pmc">([^<]+)</ArticleId>', block)
        journal = re.search(r"<Title>(.*?)</Title>", block, re.S)
        records.append(
            {
                "pmid": pmid.group(1) if pmid else None,
                "pmc": pmc.group(1) if pmc else None,
                "doi": doi.group(1) if doi else None,
                "title": strip_tags(title.group(1)) if title else "",
                "journal": strip_tags(journal.group(1)) if journal else "",
                "year": year.group(1) if year else None,
            }
        )
    return records


def main() -> int:
    count, ids = esearch(Q_STRICT)
    print(f"esearch: {count} Treffer, {len(ids)} IDs")
    time.sleep(PAUSE)

    records: list[dict] = []
    for start in range(0, len(ids), 100):
        chunk = ids[start : start + 100]
        print(f"efetch Metadaten {start + 1}-{start + len(chunk)}")
        records.extend(parse_pubmed(get(f"{EUTILS}/efetch.fcgi?db=pubmed&retmode=xml&id={','.join(chunk)}")))
        time.sleep(PAUSE)

    print(f"Metadaten gelesen: {len(records)}")

    log: list[dict] = []
    fetched = 0
    for rec in records:
        pmc = rec.get("pmc")
        if not pmc:
            log.append({"pmid": rec["pmid"], "pmc": None, "status": "kein PMC"})
            continue
        target = XML_DIR / f"{pmc}.xml"
        if target.exists() and target.stat().st_size > 1000:
            rec["xml"] = str(target)
            log.append({"pmid": rec["pmid"], "pmc": pmc, "status": "vorhanden"})
            continue
        url = f"{EUTILS}/efetch.fcgi?db=pmc&retmode=xml&id={pmc}"
        try:
            body = get(url)
        except RuntimeError as exc:
            log.append({"pmid": rec["pmid"], "pmc": pmc, "status": f"fehler: {exc}"[:200]})
            continue
        if "<pmc-articleset" in body and len(body) > 2000:
            target.write_text(body, encoding="utf-8")
            rec["xml"] = str(target)
            fetched += 1
            log.append({"pmid": rec["pmid"], "pmc": pmc, "status": "geholt", "bytes": len(body)})
        else:
            log.append({"pmid": rec["pmid"], "pmc": pmc, "status": "leer"} )
        time.sleep(PAUSE)

    for rec in records:
        rec.setdefault("xml", None)

    (OUT / "manifest_q2.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT / "fetch_log.json").write_text(
        json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    haben = sum(1 for r in records if r["xml"])
    print(f"Volltext-XML: {haben} von {len(records)} (neu geholt: {fetched})")
    print(f"ohne PMC: {sum(1 for r in records if not r['pmc'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
