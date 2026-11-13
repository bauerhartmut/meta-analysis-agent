#!/usr/bin/env python3
"""Holt die Volltexte der Cross-Validation-Auswahl als Europe-PMC-XML.

Nur die 35 ausgewaehlten Artikel (25 primaer, 10 Reserve), kein PDF-Fallback,
kein Reservekontingent, kein Modell. Roh-XML bleibt in der ignorierten
``data/fulltext_inbox``-Ablage; das Manifest haelt URL, Status, Bytes und
SHA-256 fest.

Ausgabe:
- ``fulltext_availability_v1.json``
- ``fulltext_availability_v1.md``
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

BENCH_ROOT = Path(__file__).resolve().parents[1]
ROOT = BENCH_ROOT.parent
OUT_DIR = BENCH_ROOT / "evaluation" / "multi_model_cross_validation"
SHORTLIST = OUT_DIR / "candidate_shortlist_v1.json"
POOL = OUT_DIR / "candidate_pool_v1.json"
EXTRA_FOR_REPLACEMENT = 15
RAW_DIR = ROOT / "data" / "fulltext_inbox" / "crossval_v1"
MANIFEST = OUT_DIR / "fulltext_availability_v1.json"
SUMMARY = OUT_DIR / "fulltext_availability_v1.md"

ENDPOINT = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
USER_AGENT = "meta-analysis-agent-crossval-retrieval/1.0"
PAUSE_SECONDS = 1.2


def targets() -> list[dict]:
    """Auswahl plus Ersatzkontingent in Rangfolge.

    Die ersten 35 stammen aus der eingefrorenen Auswahl v1, die naechsten
    ``EXTRA_FOR_REPLACEMENT`` aus dem gerankten Pool. Mehr wird nicht geladen,
    damit der Abruf nicht unbemerkt auf den ganzen Pool waechst.
    """
    selection = json.loads(SHORTLIST.read_text(encoding="utf-8"))
    pool = json.loads(POOL.read_text(encoding="utf-8"))["articles"]
    chosen = {row["pmcid"] for row in selection["articles"]}
    rows = [
        {**row, "batch": "initial", "role": row["role"]}
        for row in selection["articles"]
    ]
    extra = [row for row in pool if row["pmcid"] not in chosen][:EXTRA_FOR_REPLACEMENT]
    rows += [{**row, "batch": "replacement", "role": "replacement"} for row in extra]
    return rows


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def article_title(root: ET.Element) -> str:
    for elem in root.iter():
        if local_name(elem.tag) == "article-title":
            text = " ".join("".join(elem.itertext()).split())
            if text:
                return text
    return ""


def fetch(pmcid: str) -> tuple[int, bytes, str, str]:
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
                return (
                    response.status,
                    response.read(),
                    response.headers.get("Content-Type", ""),
                    "",
                )
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}"
            if exc.code in (404, 400):
                break
            time.sleep(2 ** attempt)
        except Exception as exc:  # noqa: BLE001 - Netzfehler sammeln, nicht abbrechen
            last_error = f"{type(exc).__name__}: {exc}"
            time.sleep(2 ** attempt)
    return 0, b"", "", last_error or "unbekannter Fehler"


def main() -> int:
    articles = targets()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    records = []
    for row in articles:
        pmcid = row["pmcid"]
        local_path = RAW_DIR / f"{pmcid}.xml"
        fetched_now = False
        if local_path.exists() and local_path.stat().st_size > 0:
            # Bereits abgerufen: nicht erneut laden, Hash bleibt derselbe.
            body = local_path.read_bytes()
            status, content_type, error = 200, "application/xml", ""
        else:
            status, body, content_type, error = fetch(pmcid)
            fetched_now = True
        saved = bool(body) and status == 200
        digest = ""
        root_name = ""
        title = ""
        if saved:
            local_path.write_bytes(body)
            digest = hashlib.sha256(body).hexdigest()
            try:
                root = ET.fromstring(body)
                root_name = local_name(root.tag)
                title = article_title(root)
            except ET.ParseError as exc:
                saved = False
                error = f"XML-Parsefehler: {exc}"
        records.append(
            {
                "position": row["position"],
                "role": row["role"],
                "batch": row.get("batch", "initial"),
                "fetched_now": fetched_now,
                "pmcid": pmcid,
                "doi": row.get("doi", ""),
                "url": ENDPOINT.format(pmcid=pmcid),
                "http_status": status,
                "content_type": content_type,
                "bytes": len(body),
                "sha256": digest,
                "xml_root": root_name,
                "article_title": title,
                "local_path": str(local_path.relative_to(ROOT)).replace("\\", "/"),
                "saved": saved,
                "error": error,
            }
        )
        print(f"{pmcid}: {'ok' if saved else 'FEHLER ' + error} ({len(body)} Bytes)")
        if fetched_now:
            time.sleep(PAUSE_SECONDS)

    available = [row for row in records if row["saved"]]
    payload = {
        "retrieval_id": "crossval_fulltext_v1",
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "complete" if len(available) == len(records) else "partial",
        "source": "Europe PMC fullTextXML",
        "endpoint": ENDPOINT,
        "requested": len(records),
        "saved": len(available),
        "failed": len(records) - len(available),
        "total_bytes": sum(row["bytes"] for row in records),
        "model_used": False,
        "network_used": True,
        "pdf_retrieved": False,
        "records": records,
    }
    MANIFEST.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Cross-Validation: Volltextverfuegbarkeit v1",
        "",
        f"Stand: {payload['created'][:10]}",
        f"Status: **{payload['status']}**",
        "Quelle: Europe PMC `fullTextXML`, kein PDF-Fallback, kein Modell.",
        "",
        "| Kennzahl | Wert |",
        "|---|---:|",
        f"| angefordert | {payload['requested']} |",
        f"| abgerufen | {payload['saved']} |",
        f"| fehlgeschlagen | {payload['failed']} |",
        f"| Bytes gesamt | {payload['total_bytes']} |",
        "",
        "| # | Rolle | PMCID | Status | Bytes | SHA-256 |",
        "|---:|---|---|---|---:|---|",
    ]
    for row in records:
        state = "ok" if row["saved"] else f"FEHLER: {row['error']}"
        lines.append(
            f"| {row['position']} | {row['role']} | {row['pmcid']} | {state} | "
            f"{row['bytes']} | {row['sha256'][:16]} |"
        )
    lines.append("")
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")

    print(f"\nabgerufen {payload['saved']}/{payload['requested']}")
    return 0 if payload["saved"] == payload["requested"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
