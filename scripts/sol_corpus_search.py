"""Zwei Suchen zu Sleep onset latency, Treffer-XML laden, Korpus bauen.

Budget laut AGENTS.md: hoechstens zwei Suchen. Genau die werden gefahren:

1. Europe PMC: ``melatonin AND "sleep onset latency" AND (randomized OR
   randomised) AND OPEN_ACCESS:y`` - liefert DOI und PMCID direkt, also den
   Korpus fuer die deterministischen Leser.
2. Crossref: ``melatonin sleep onset latency randomized trial`` - Gegenprobe,
   wie viele der wichtigsten Arbeiten Europe PMC ebenfalls findet und ob eine
   Metaanalyse als Seed dabei ist. Crossref liefert keinen PMCID; aus dieser
   Suche wird nichts geladen.

Danach: XML fuer jeden Treffer mit PMCID von Europe PMC ``fullTextXML``
laden (resumierbar), Manifest ``[{doi, pmc}]`` schreiben.

Die Suche ist kein Lauf des Orchestrators: kein LLM, keine Zyklen.

Aufruf:
    .venv/bin/python.exe scripts/sol_corpus_search.py --download
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EPMC_XML = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
CROSSREF = "https://api.crossref.org/works"
UA = "Mozilla/5.0 (Research Agent; Academic Use)"
MAILTO = "research@freebuff.ai"

QUERY_EPMC = ('melatonin AND "sleep onset latency" AND (randomized OR randomised) '
              'AND OPEN_ACCESS:y')
QUERY_CROSSREF = "melatonin sleep onset latency randomized trial"


def _get(url: str, timeout: int = 45, attempts: int = 3) -> tuple[int, bytes]:
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 503) and attempt < attempts:
                time.sleep(5 * attempt)
                continue
            return exc.code, b""
        except Exception:
            if attempt < attempts:
                time.sleep(2 * attempt)
                continue
            return 0, b""
    return 0, b""


def search_europepmc(page_size: int = 100, pages: int = 1) -> dict:
    """Treffer ueber ``cursorMark`` blaettern - dieselbe Query, mehr Seiten."""
    records: list[dict] = []
    seen: set[str] = set()
    hit_count = 0
    status = 0
    pages_read = 0
    cursor = "*"
    for _ in range(max(1, pages)):
        params = urllib.parse.urlencode({
            "query": QUERY_EPMC, "format": "json", "pageSize": page_size,
            "resultType": "core", "sort": "P_PDATE_D desc", "cursorMark": cursor,
        })
        status, body = _get(f"{EPMC_SEARCH}?{params}")
        if status != 200 or not body:
            break
        try:
            payload = json.loads(body.decode("utf-8", "ignore"))
        except ValueError:
            break
        hit_count = hit_count or int(payload.get("hitCount") or 0)
        result = payload.get("resultList", {}).get("result", []) or []
        pages_read += 1
        for item in result:
            key = str(item.get("pmcid") or item.get("id") or item.get("doi") or "")
            if not key or key in seen:
                continue
            seen.add(key)
            records.append({
                "pmcid": str(item.get("pmcid") or "").strip(),
                "doi": str(item.get("doi") or "").strip(),
                "title": str(item.get("title") or "").strip(),
                "year": str(item.get("pubYear") or ""),
                "journal": str(item.get("journalTitle") or ""),
                "isOpenAccess": str(item.get("isOpenAccess") or ""),
            })
        next_cursor = str(payload.get("nextCursorMark") or "")
        if not result or not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor
        time.sleep(0.3)
    return {
        "query": QUERY_EPMC,
        "status": status,
        "hitCount": hit_count,
        "returned": len(records),
        "pages": pages_read,
        "records": records,
    }


def search_crossref(rows: int = 100) -> dict:
    params = urllib.parse.urlencode({
        "query.bibliographic": QUERY_CROSSREF, "rows": rows,
        "select": "DOI,title,type,issued", "mailto": MAILTO,
    })
    status, body = _get(f"{CROSSREF}?{params}")
    items = []
    if status == 200 and body:
        try:
            items = (json.loads(body.decode("utf-8", "ignore"))
                     .get("message", {}) or {}).get("items", []) or []
        except ValueError:
            items = []
    records = [{
        "doi": str(item.get("DOI") or "").lower().strip(),
        "title": (item.get("title") or [""])[0] if item.get("title") else "",
        "type": str(item.get("type") or ""),
    } for item in items]
    return {"query": QUERY_CROSSREF, "status": status, "returned": len(records),
            "records": records}


def build_manifest(epmc: dict, crossref: dict) -> dict:
    by_pmcid: dict[str, dict] = {}
    for rec in epmc["records"]:
        pmcid = rec["pmcid"]
        if not pmcid.startswith("PMC"):
            continue
        entry = by_pmcid.setdefault(pmcid, {"pmc": pmcid, "doi": rec["doi"],
                                            "title": rec["title"],
                                            "year": rec["year"]})
        if not entry["doi"] and rec["doi"]:
            entry["doi"] = rec["doi"]
    crossref_dois = {r["doi"] for r in crossref["records"] if r["doi"]}
    epmc_dois = {entry["doi"].lower() for entry in by_pmcid.values() if entry["doi"]}
    overlap = sorted(crossref_dois & epmc_dois)
    meta_analyses = [r for r in crossref["records"]
                     if "meta-analysis" in r["title"].lower()
                     or "systematic review" in r["title"].lower()]
    return {
        "manifest": sorted(by_pmcid.values(), key=lambda e: e["pmc"]),
        "stats": {
            "epmc_hits": epmc.get("hitCount", 0),
            "epmc_returned": epmc.get("returned", 0),
            "epmc_with_pmcid": len(by_pmcid),
            "epmc_without_doi": sum(1 for e in by_pmcid.values() if not e["doi"]),
            "crossref_returned": crossref.get("returned", 0),
            "crossref_overlap_epmc": len(overlap),
            "crossref_meta_analyses": len(meta_analyses),
        },
        "crossref_overlap": overlap[:20],
        "crossref_meta_analysis_titles": [r["title"] for r in meta_analyses[:5]],
    }


def download(manifest: list[dict], xml_dir: Path, sleep: float = 0.2) -> dict:
    xml_dir.mkdir(parents=True, exist_ok=True)
    loaded = present = failed = 0
    failures: list[dict] = []
    for number, entry in enumerate(manifest, start=1):
        target = xml_dir / f"{entry['pmc']}.xml"
        if target.exists() and target.stat().st_size > 500:
            present += 1
            continue
        status, body = _get(EPMC_XML.format(pmcid=entry["pmc"]))
        if status == 200 and body and b"<article" in body[:4000]:
            target.write_bytes(body)
            loaded += 1
        else:
            failed += 1
            failures.append({"pmc": entry["pmc"], "status": status})
        if number % 20 == 0:
            print(f"  ... {number}/{len(manifest)} (geladen {loaded}, "
                  f"vorhanden {present}, Fehler {failed})", flush=True)
        time.sleep(sleep)
    return {"loaded": loaded, "present": present, "failed": failed,
            "failures": failures[:20]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", default="data/bench/sol")
    ap.add_argument("--download", action="store_true",
                    help="XML der Treffer laden (Netz)")
    ap.add_argument("--pages", type=int, default=1,
                    help="Seiten zu je 100 Treffern (1 = wie bisher)")
    ap.add_argument("--manifest-out", default="",
                    help="Manifest-Ziel; leer = <base>/manifest.json")
    ap.add_argument("--sleep", type=float, default=0.2)
    args = ap.parse_args(argv)

    base = Path(args.base)
    base.mkdir(parents=True, exist_ok=True)

    epmc = search_europepmc(pages=args.pages)
    (base / "search_europepmc.json").write_text(
        json.dumps(epmc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Europe PMC: hitCount {epmc.get('hitCount')} | zurueck "
          f"{epmc.get('returned')}", flush=True)

    crossref = search_crossref()
    (base / "search_crossref.json").write_text(
        json.dumps(crossref, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Crossref: zurueck {crossref.get('returned')}", flush=True)

    built = build_manifest(epmc, crossref)
    manifest_path = Path(args.manifest_out) if args.manifest_out else base / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(built["manifest"], ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(built["stats"], ensure_ascii=False))

    if args.download:
        result = download(built["manifest"], base / "xml", args.sleep)
        print(json.dumps(result, ensure_ascii=False))

    payload = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "stats": built["stats"],
        "crossref_overlap": built["crossref_overlap"],
        "crossref_meta_analysis_titles": built["crossref_meta_analysis_titles"],
        "download": result if args.download else {},
    }
    (base / "search_summary.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
