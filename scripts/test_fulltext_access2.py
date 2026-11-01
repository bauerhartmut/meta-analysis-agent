#!/usr/bin/env python3
"""Second probe: deliberately search PubMed in PAYWALLED journals
(Springer, Wiley/Sage/T&F), follow DOIs, and try to actually download
the publisher PDF to check TU-IP authentication end-to-end.
Read-only: nothing is stored, only checked whether the PDF arrives."""
import json
import re
import urllib.request
import urllib.error
import urllib.parse

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def req(url, timeout=30, referer=None):
    headers = dict(UA)
    if referer:
        headers["Referer"] = referer
    r = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        return resp.status, resp.read(), resp.geturl()


def get_text(url, timeout=30):
    st, data, final = req(url, timeout)
    return st, data.decode("utf-8", "ignore"), final


# 1) PubMed - nur Zeitschriften, die das klassische Lizenzmodell haben
QUERY = (
    '(("Sports Med"[Journal]) OR ("J Health Psychol"[Journal]) '
    'OR ("Psychosom Med"[Journal]) OR ("Depress Anxiety"[Journal]) '
    'OR ("J Affect Disord"[Journal]) OR ("Psychiatry Res"[Journal]))'
    ' AND (exercise OR "physical activity") AND depression'
)
st, s, _ = get_text(
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    "?db=pubmed&retmode=json&retmax=12&term=" + urllib.parse.quote(QUERY, safe="")
)
ids = json.loads(s)["esearchresult"]["idlist"]
st, s, _ = get_text(
    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    "?db=pubmed&retmode=json&id=" + ",".join(ids)
)
res = json.loads(s)["result"]
docs = []
for i in ids:
    d = res[i]
    doi = next((x["value"] for x in d.get("articleids", []) if x["idtype"] == "doi"), None)
    if doi:
        docs.append((doi, d.get("source", ""), d["title"][:60]))
    if len(docs) >= 8:
        break

print("=== Kandidaten aus Lizenzpublikum (DOI | journal | titel) ===")
for doi, src, t in docs:
    print(f"{doi} | {src} | {t}")
print()

# 2) Landingpage + PDF-Download-Versuch
for doi, src, title in docs:
    print(f"--- {doi} ({src}) | {title}")
    try:
        st, html, final = get_text("https://doi.org/" + doi)
    except urllib.error.HTTPError as e:
        print(f"    Landeseite: HTTP {e.code} (verlagsseitig abgelehnt)")
        continue
    except Exception as e:
        print(f"    Landeseite fehlgeschlagen: {type(e).__name__}")
        continue
    host = re.sub(r"^https?://", "", final.split("/")[0])
    # PDF-Link finden (absolut oder relativ)
    m = re.search(r'href="([^"]*?(?:\.pdf|pdfdirect)[^"]*)"', html, re.I)
    pdf_url = None
    if m:
        p = m.group(1)
        pdf_url = p if p.startswith("http") else "https://" + host + p
    if not pdf_url and "link.springer.com" in host:
        pdf_url = "https://link.springer.com/content/pdf/" + doi + ".pdf"
    print(f"    Landing HTTP {st}, {len(html)} bytes | {host}")
    if not pdf_url:
        print("    kein PDF-Link gefunden")
        continue
    # PDF holen
    try:
        st2, data, final2 = req(pdf_url, referer=final)
        head = data[:8]
        is_pdf = head.startswith(b"%PDF")
        size = len(data)
        note = "PDF!" if is_pdf else f"kein PDF (head={head[:16]!r}, vermutlich HTML-Abrechnungsseite)"
        print(f"    PDF-Download: HTTP {st2}, {size} bytes | {note}")
    except urllib.error.HTTPError as e:
        print(f"    PDF-Download: HTTP {e.code} -> NICHT lizenziert/gebremst")
    except Exception as e:
        print(f"    PDF-Download fehlgeschlagen: {type(e).__name__}")
