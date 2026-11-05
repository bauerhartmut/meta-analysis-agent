"""Seed the local fulltext corpus for a harness dry-run (legal OA sources).

Sucht Studien zu einem Thema (Titel-Schlagwoerter, open access, Volltext
vorhanden), laedt die Volltext-XMLs herunter und legt sie als
``data/fulltext_inbox/<doi>.xml`` ab - genau die Quelle, die der
Coverage-Manager vor jedem Netzversuch serviert. Metadaten landen
(register_study) plus Download-Status (record_status) in der Harness-DB.

Routen in dieser Reihenfolge:
1. EuropePMC (Suche + fullTextXML) - erste Wahl, aber der Endpunkt
   503t zeitweise ohne Retry-After.
2. NCBI E-utilities (esearch db=pmc + efetch retmode=xml) - Rueckfall,
   selbe JATS-XML-Quelle, keine Key noetig (<=3 Anfragen/s).

Usage:
    python scripts/seed_local_corpus.py --db data/harness_local.db --n 12
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
UA = {"User-Agent": "meta-analysis-agent-harness-seed/1.0"}


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def sanitize_doi(doi: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "-", doi or "").strip("-")


# ---------------------------------------------------------------- EuropePMC #
def europepmc_search(query: str, n: int) -> list:
    url = (BASE + "/search?query=" + urllib.parse.quote(query)
           + f"&format=json&pageSize={n}&page=1")
    payload = json.loads(_get(url).decode("utf-8"))
    return payload.get("resultList", {}).get("result", [])


def europepmc_xml(pmcid: str) -> bytes | None:
    try:
        return _get(f"{BASE}/PMC/{pmcid}/fullTextXML")
    except Exception as exc:
        print(f"  ! Download fehlgeschlagen ({pmcid}): {exc}")
        return None


# --------------------------------------------------------------- E-utilities #
def eutils_ids(query: str, n: int) -> list[int]:
    url = (EUTILS + "/esearch.fcgi?db=pmc&retmode=json&retmax=" + str(n)
           + "&term=" + urllib.parse.quote(query))
    payload = json.loads(_get(url).decode("utf-8"))
    return [int(x) for x in payload.get("esearchresult", {}).get("idlist", [])]


def eutils_xml(pmc_numeric_id: int) -> bytes | None:
    url = (EUTILS + f"/efetch.fcgi?db=pmc&id={pmc_numeric_id}&retmode=xml")
    try:
        return _get(url)
    except Exception as exc:
        print(f"  ! Download fehlgeschlagen ({pmc_numeric_id}): {exc}")
        return None


def jats_meta(xml_bytes: bytes) -> dict:
    """Zieht Titel/Journal/Jahr/DOIs/Autoren aus einem JATS-Artikel."""
    root = ET.fromstring(xml_bytes)

    def ids(kind: str) -> str:
        for el in root.iter("article-id"):
            # EuropePMC nennt es pub-type, NCBI-E-utilities pub-id-type.
            kind_attr = (el.attrib.get("pub-id-type") or
                         el.attrib.get("pub-type") or "").lower()
            if kind_attr.endswith(kind):
                return (el.text or "").strip().removeprefix("doi:")
        return ""

    title = next((el for el in root.iter("article-title")), None)
    journal = next((el for el in root.iter("journal-title")), None)
    year = next((el for el in root.iter("pub-date") if el.find("year") is not None), None)
    authors = []
    for contrib in root.iter("contrib"):
        name = contrib.find("name")
        if name is not None:
            family = (name.findtext("family") or "").strip()
            given = (name.findtext("given") or "").strip()
            if family:
                authors.append((family + ", " + given).strip(", "))
    return {
        "title": "".join(title.itertext()).strip() if title is not None else "",
        "journal": "".join(journal.itertext()).strip() if journal is not None else "",
        "year": int(year.findtext("year") or 0) if year is not None else 0,
        "doi": ids("doi"),
        "pmid": ids("pmid"),
        "pmcid": "PMC" + ids("pmcid").replace("PMC", "") if ids("pmcid") else "PMC" + ids("pmc"),
        "authors": authors[:8],
    }


# ------------------------------------------------------------------- Seeding #
def register_and_record(mgr, hit: dict, xml_bytes: bytes, inbox: Path) -> bool:
    doi = (hit.get("doi") or "").strip()
    if not doi:
        print(f"  - ohne DOI uebersprungen: {hit.get('title', '')[:60]}")
        return False
    target = inbox / (sanitize_doi(doi) + ".xml")
    if not (target.exists() and target.stat().st_size > 200):
        target.write_bytes(xml_bytes)
        print(f"  -> {doi} ({len(xml_bytes)} Bytes) {hit.get('title', '')[:50]}")
    else:
        print(f"  -> {doi} schon in der Inbox")
    mgr.register_study(
        doi=doi, title=hit.get("title", ""), authors=hit.get("authors") or [],
        year=int(hit.get("year") or 0), journal=hit.get("journal", ""),
        pmid=hit.get("pmid", ""), pmcid=hit.get("pmcid", ""), oa_status="open",
    )
    mgr.record_status(doi, "DOWNLOADED", "seeded via pmc fullTextXML")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", default="data/harness_local.db")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--sleep", type=float, default=0.4,
                    help="Pause zwischen Downloads (Sekunden)")
    ap.add_argument("--query", default=(
        'TITLE:"melatonin" AND TITLE:"sleep" AND HAS_FULLTEXT:y '
        "AND OPEN_ACCESS:y AND FIRST_PDATE:[2015 TO 2026]"))
    args = ap.parse_args()

    from research_agent.coverage.manager import CoverageManager

    mgr = CoverageManager(args.db)
    inbox = Path(mgr.inbox_dir)
    inbox.mkdir(parents=True, exist_ok=True)
    print(f"DB: {args.db}\nInbox: {inbox}")

    ok = failed = 0
    try:
        hits = europepmc_search(args.query, args.n)
        print(f"EuropePMC: {len(hits)} Treffer\nSuche: {args.query[:70]}...")
        for hit in hits:
            doi = (hit.get("doi") or "").strip()
            xml = europepmc_xml(hit.get("pmcid", "")) if hit.get("pmcid") else None
            if xml is None:
                failed += 1
                continue
            if register_and_record(mgr, {
                "doi": doi, "title": (hit.get("title") or "").strip(),
                "authors": [a.strip() for a in (hit.get("authorString") or "").split(",")][:8],
                "year": int(hit.get("pubYear") or 0),
                "journal": (hit.get("journalTitle") or "").strip(),
                "pmid": (hit.get("pmid") or "").strip(),
                "pmcid": (hit.get("pmcid") or "").strip(),
            }, xml, inbox):
                ok += 1
            time.sleep(args.sleep)
    except Exception as exc:
        print(f"EuropePMC nicht erreichbar ({exc}) - weiche auf E-utilities aus.")

    if ok == 0:
        equery = '(melatonin[Title] AND sleep[Title])'
        ids = eutils_ids(equery, args.n)
        print(f"E-utilities-Rueckfall: {len(ids)} PMCs")
        for i, numeric_id in enumerate(ids, start=1):
            xml = eutils_xml(numeric_id)
            if xml is None:
                failed += 1
                continue
            try:
                hit = jats_meta(xml)
            except Exception as exc:
                print(f"  ! JATS unlesbar ({numeric_id}): {exc}")
                failed += 1
                continue
            if register_and_record(mgr, hit, xml, inbox):
                ok += 1
            time.sleep(max(args.sleep, 0.4))

    print(f"\nFertig: {ok} Studien in der Inbox, {failed} Fehler.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
