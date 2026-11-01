#!/usr/bin/env python3
"""Read-only test: fetch real RCTs from PubMed (exercise + depression),
follow their DOIs to the publisher landing pages, and look for
access markers to see whether licensed full text is reachable."""
import json
import re
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "ignore"), r.geturl()


# 1) PubMed: RCTs im Themenfeld mit DOI
st, s, _ = get(
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    "?db=pubmed&retmode=json&retmax=10"
    "&term=(exercise+OR+%22physical+activity%22)+AND+depression"
    "+AND+randomized+controlled+trial"
)
ids = json.loads(s)["esearchresult"]["idlist"]
st, s, _ = get(
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    "?db=pubmed&retmode=json&id=" + ",".join(ids)
)
res = json.loads(s)["result"]
docs = []
for i in ids:
    d = res[i]
    doi = next((x["value"] for x in d.get("articleids", []) if x["idtype"] == "doi"), None)
    if doi:
        docs.append((doi, d.get("source", ""), d["title"][:70]))
    if len(docs) >= 6:
        break

print("=== Kandidaten (DOI | journal | titel) ===")
for doi, src, t in docs:
    print(f"{doi} | {src} | {t}")
print()

# 2) DOI-Landingpage je Verlagsseite pruefen
MARKERS = {
    "springer": ["download pdf", "access provided by", "purchase pdf"],
    "wiley": ["download pdf", "pdf options", "purchase", "access options"],
    "sage": ["downloadpdf", "access options", "sign in password"],
    "tandfonline": ["download citation", "purchase", "institutional login"],
    "nature": ["download pdf", "purchase pdf", "access this article"],
    "apa": ["purchase", "sign in"],
}

for doi, src, title in docs:
    print(f"--- {doi} ({src}) | {title}")
    try:
        st, html, final_url = get("https://doi.org/" + doi)
    except Exception as e:  # HTTPError, URLError, Timeout...
        code = getattr(e, "code", "")
        print(f"    ABFRAGE FEHLGESCHLAGEN: {type(e).__name__} {code}")
        continue
    low = html.lower()
    shown = []
    for k, ms in MARKERS.items():
        for mm in ms:
            if mm in low:
                shown.append(f"{k}:{mm}")
                break
    has_abstract = "abstract" in low
    # PDF-Link direkt? (Bestaetigung, dass PDF angebunden ist)
    pdf_link = ""
    m = re.search(r'href="([^"]*?\.pdf[^"]*)"', low)
    if m:
        pdf_link = m.group(1)
    print(
        f"    HTTP {st}, {len(html)} bytes | host {re.sub(r'^https?://', '', final_url.split('/')[0])}"
    )
    print(f"    abstract: {has_abstract} | PDF-Link: {pdf_link[:80] or 'keiner'} | Marker: {', '.join(shown[:5]) if shown else 'keine'}")
