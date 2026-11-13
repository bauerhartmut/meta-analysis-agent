#!/usr/bin/env python3
"""Retrieve the 30 approved P0 shortlist full texts as Europe PMC XML.

Network is used only for the approved shortlist. Raw XML stays in the ignored
data/fulltext_inbox tree; the committed manifest records URL, status, bytes and
SHA-256. No PDF fallback, no reserve cases, no model.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public_benchmark" / "evaluation" / "c1_pilot" / "holdout_p0_20261112"
PRIORITY = OUT / "fulltext_candidate_priority_v1.json"
RAW_DIR = ROOT / "data" / "fulltext_inbox" / "p0_20261113_xml"
MANIFEST = OUT / "fulltext_retrieval_manifest_v1.json"
SUMMARY = OUT / "fulltext_retrieval_v1.md"
ENDPOINT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
USER_AGENT = "meta-analysis-agent-p0-retrieval/1.0"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def article_title(root: ET.Element) -> str:
    for elem in root.iter():
        if local_name(elem.tag) == "article-title":
            text = " ".join("".join(elem.itertext()).split())
            if text:
                return text
    return ""


def fetch(pmcid: str) -> tuple[int, bytes, str, str, str]:
    url = ENDPOINT.format(pmcid=pmcid)
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.1",
        },
    )
    last_error = ""
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = response.read()
                return (
                    response.status,
                    body,
                    response.headers.get("Content-Type", ""),
                    response.geturl(),
                    "",
                )
        except urllib.error.HTTPError as exc:
            body = exc.read()
            if exc.code == 429 or 500 <= exc.code < 600:
                last_error = f"HTTP {exc.code}"
                time.sleep(2 ** attempt)
                continue
            return exc.code, body, exc.headers.get("Content-Type", ""), url, f"HTTP {exc.code}"
        except Exception as exc:  # noqa: BLE001 - recorded per item
            last_error = f"{type(exc).__name__}: {exc}"
            time.sleep(2 ** attempt)
    return 0, b"", "", url, last_error


def main() -> None:
    priority = json.loads(PRIORITY.read_text(encoding="utf-8"))
    shortlist = priority["shortlist_30"]
    if len(shortlist) != 30:
        raise SystemExit(f"expected 30 shortlist rows, got {len(shortlist)}")
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    started = datetime.now(timezone.utc).isoformat()
    records = []
    for index, row in enumerate(shortlist, 1):
        pmcid = row["pmcid"]
        path = RAW_DIR / f"{pmcid}.xml"
        status, body, content_type, final_url, error = fetch(pmcid)
        root_name = ""
        title = ""
        if status == 200 and body:
            try:
                root = ET.fromstring(body)
                root_name = local_name(root.tag)
                if root_name != "article":
                    error = f"unexpected XML root: {root_name}"
                else:
                    title = article_title(root)
            except ET.ParseError as exc:
                error = f"XML parse error: {exc}"
        elif status == 200:
            error = "empty response"

        digest = hashlib.sha256(body).hexdigest() if body else ""
        if status == 200 and root_name == "article" and not error:
            temp = path.with_suffix(".xml.part")
            temp.write_bytes(body)
            temp.replace(path)
            saved = True
        else:
            saved = False

        records.append(
            {
                "rank": index,
                "pmcid": pmcid,
                "doi": row.get("doi", ""),
                "url": final_url,
                "http_status": status,
                "content_type": content_type,
                "bytes": len(body),
                "sha256": digest,
                "xml_root": root_name,
                "article_title": title,
                "local_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "saved": saved,
                "error": error,
            }
        )
        print(f"{index:02d}/30 {pmcid} http={status} bytes={len(body)} saved={saved} {error}")
        if index < len(shortlist):
            time.sleep(1.2)

    success = [row for row in records if row["saved"]]
    failed = [row for row in records if not row["saved"]]
    manifest = {
        "retrieval_id": "p0_fulltext_xml_v1",
        "started_at": started,
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "status": "complete" if not failed else "partial",
        "source": "Europe PMC fullTextXML",
        "endpoint": ENDPOINT,
        "shortlist_source": str(PRIORITY.relative_to(ROOT)).replace("\\", "/"),
        "shortlist_count": len(shortlist),
        "attempted": len(records),
        "saved": len(success),
        "failed": len(failed),
        "total_bytes": sum(row["bytes"] for row in records),
        "model_used": False,
        "network_used": True,
        "pdf_retrieved": False,
        "records": records,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# P0-Volltextabruf: 30 Shortlist-Artikel als Europe-PMC-XML",
        "",
        f"Stand: {started[:10]}",
        f"Status: **{manifest['status'].upper()}**; XML zuerst, keine PDFs.",
        "",
        f"- Shortlist: **{len(shortlist)}**",
        f"- erfolgreich gespeichert: **{len(success)}**",
        f"- fehlgeschlagen: **{len(failed)}**",
        f"- Bytes gesamt: **{manifest['total_bytes']}**",
        "- Ablage: `data/fulltext_inbox/p0_20261113_xml/` (gitignoriert)",
        "- Manifest: `fulltext_retrieval_manifest_v1.json`",
        "",
        "| Rang | PMC | HTTP | Bytes | XML-Wurzel | Gespeichert | Fehler |",
        "|---:|---|---:|---:|---|---|---|",
    ]
    for row in records:
        lines.append(
            f"| {row['rank']} | {row['pmcid']} | {row['http_status']} | {row['bytes']} | "
            f"{row['xml_root'] or '-'} | {'ja' if row['saved'] else 'nein'} | {row['error'] or '-'} |"
        )
    lines += [
        "",
        "Kein PDF-Abruf, kein Reservefall, kein Modelllauf. Die XML-Dateien sind",
        "Rohdaten und werden nicht committet; das Manifest ist die versionierte",
        "Provenienz.",
        "",
    ]
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ["status", "attempted", "saved", "failed", "total_bytes"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
