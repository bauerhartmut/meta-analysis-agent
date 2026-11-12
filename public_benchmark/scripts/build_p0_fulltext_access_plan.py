#!/usr/bin/env python3
"""Document access routes for the 36 P0 includes without fetching anything.

Checks three local stores:
  * data/fulltext/*.txt (content match by DOI, PMCID or normalized title)
  * data/fulltext_metadata/*.json (DOI, title or filename match)
  * data/fulltext_inbox/* (DOI filename variants)

No network call, no model call. A miss is recorded as "no local match", not as
proof that the article does not exist anywhere else.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
PILOT = ROOT / "evaluation" / "c1_pilot"
OUT = PILOT / "holdout_p0_20261112"
SIGNOFF = OUT / "manual_review_signoff_v1.json"
CANDIDATES = OUT / "candidates.jsonl"
FULLTEXT = PROJECT / "data" / "fulltext"
METADATA = PROJECT / "data" / "fulltext_metadata"
INBOX = PROJECT / "data" / "fulltext_inbox"
JSON_PATH = OUT / "fulltext_access_plan_v1.json"
CSV_PATH = OUT / "fulltext_access_plan_v1.csv"
MD_PATH = OUT / "fulltext_access_plan_v1.md"


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def norm_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").lower()).strip()


def rel(path: Path) -> str:
    return str(path.relative_to(PROJECT))


def inbox_names(doi: str) -> list[str]:
    names = []
    for separator in ("-", "_"):
        for extension in (".xml", ".pdf"):
            names.append(doi.replace("/", separator).replace(":", separator) + extension)
    return names


def main() -> None:
    signoff = json.loads(SIGNOFF.read_text(encoding="utf-8"))
    includes = [row for row in signoff["rows"] if row["decision"] == "include_for_fulltext"]
    candidates = {row["pmcid"]: row for row in read_jsonl(CANDIDATES)}
    if len(includes) != 36:
        raise SystemExit(f"expected 36 includes, got {len(includes)}")

    fulltext_docs = []
    for path in sorted(FULLTEXT.glob("*.txt")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        fulltext_docs.append(
            {
                "path": path,
                "lower": text.lower(),
                "key": norm_key(text),
            }
        )

    metadata_docs = []
    for path in sorted(METADATA.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        metadata_docs.append(
            {
                "path": path,
                "doi": str(data.get("doi") or "").lower().strip(),
                "title": norm_key(data.get("title") or ""),
                "status": data.get("status") or "",
            }
        )

    rows = []
    for row in includes:
        candidate = candidates[row["pmcid"]]
        doi = row["doi"].lower().strip()
        pmcid = row["pmcid"].lower().strip()
        title = norm_key(row["title"])

        fulltext_matches = []
        for doc in fulltext_docs:
            methods = []
            if doi and doi in doc["lower"]:
                methods.append("doi")
            if pmcid and pmcid in doc["lower"]:
                methods.append("pmcid")
            if title and title in doc["key"]:
                methods.append("title")
            if methods:
                fulltext_matches.append(
                    {"path": rel(doc["path"]), "methods": methods}
                )

        metadata_matches = []
        metadata_filename = doi.replace("/", "_").replace(":", "_") + ".json"
        for doc in metadata_docs:
            methods = []
            if doi and doc["doi"] == doi:
                methods.append("doi")
            if title and doc["title"] == title:
                methods.append("title")
            if doc["path"].name == metadata_filename:
                methods.append("filename")
            if methods:
                metadata_matches.append(
                    {
                        "path": rel(doc["path"]),
                        "methods": methods,
                        "status": doc["status"],
                    }
                )

        inbox_matches = [
            rel(INBOX / name) for name in inbox_names(row["doi"]) if (INBOX / name).exists()
        ]
        local_paths = sorted(
            {match["path"] for match in fulltext_matches}
            | {match["path"] for match in metadata_matches}
            | set(inbox_matches)
        )
        local_present = bool(local_paths)

        rows.append(
            {
                "pmcid": row["pmcid"],
                "doi": row["doi"],
                "title": row["title"],
                "priority": row["priority"],
                "is_open_access": candidate.get("is_open_access") == "Y",
                "in_epmc": candidate.get("in_epmc") == "Y",
                "has_pdf": candidate.get("has_pdf") == "Y",
                "pmc_page_url": f"https://pmc.ncbi.nlm.nih.gov/articles/{row['pmcid']}/",
                "epmc_xml_url": (
                    "https://www.ebi.ac.uk/europepmc/webservices/rest/"
                    f"{row['pmcid']}/fullTextXML"
                ),
                "recommended_route": "local_fulltext" if local_present else "europepmc_fulltext_xml",
                "local_status": "present" if local_present else "not_present",
                "local_paths": local_paths,
                "fulltext_matches": fulltext_matches,
                "metadata_matches": metadata_matches,
                "local_inbox_files": inbox_matches,
                "network_required": not local_present,
                "fetch_status": "not_needed" if local_present else "not_started",
                "notes": (
                    "Lokaler Treffer vorhanden; vor Extraktion Version und Lizenz prüfen."
                    if local_present
                    else (
                        "Kein lokaler Treffer in fulltext, Metadaten oder Inbox; "
                        "XML-Abruf erst nach Freigabe."
                    )
                ),
            }
        )

    rows.sort(key=lambda row: ({"hoch": 0, "mittel": 1, "niedrig": 2}[row["priority"]], row["pmcid"]))
    summary = {
        "articles": len(rows),
        "open_access": sum(row["is_open_access"] for row in rows),
        "in_epmc": sum(row["in_epmc"] for row in rows),
        "pdf_advertised": sum(row["has_pdf"] for row in rows),
        "local_present": sum(row["local_status"] == "present" for row in rows),
        "fulltext_matches": sum(bool(row["fulltext_matches"]) for row in rows),
        "metadata_matches": sum(bool(row["metadata_matches"]) for row in rows),
        "inbox_matches": sum(bool(row["local_inbox_files"]) for row in rows),
        "xml_route": sum(row["recommended_route"] == "europepmc_fulltext_xml" for row in rows),
        "checked_fulltext_files": len(fulltext_docs),
        "checked_metadata_records": len(metadata_docs),
        "checked_inbox_files": len(list(INBOX.glob("*"))) if INBOX.exists() else 0,
    }
    payload = {
        "plan_id": "p0_fulltext_access_v1",
        "created_at": "2026-11-12",
        "status": "ready_for_approved_fetch" if summary["local_present"] < len(rows) else "local_complete",
        "records": len(rows),
        "network_fetch_performed": False,
        "model_used": False,
        "locations_checked": [
            "data/fulltext",
            "data/fulltext_metadata",
            "data/fulltext_inbox",
        ],
        "match_rule": {
            "fulltext": "DOI, PMCID oder normalisierter Titel im Text",
            "metadata": "DOI, normalisierter Titel oder DOI-Dateiname",
            "inbox": "DOI-Dateiname mit Bindestrich oder Unterstrich, XML/PDF",
        },
        "summary": summary,
        "articles": rows,
    }
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        fields = [
            "pmcid",
            "doi",
            "title",
            "priority",
            "is_open_access",
            "in_epmc",
            "has_pdf",
            "pmc_page_url",
            "epmc_xml_url",
            "recommended_route",
            "local_status",
            "local_paths",
            "fulltext_matches",
            "metadata_matches",
            "local_inbox_files",
            "network_required",
            "fetch_status",
            "notes",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **row,
                    "local_paths": ";".join(row["local_paths"]),
                    "fulltext_matches": ";".join(
                        f"{item['path']} ({','.join(item['methods'])})"
                        for item in row["fulltext_matches"]
                    ),
                    "metadata_matches": ";".join(
                        f"{item['path']} ({','.join(item['methods'])})"
                        for item in row["metadata_matches"]
                    ),
                    "local_inbox_files": ";".join(row["local_inbox_files"]),
                }
            )

    lines = [
        "# Volltext-Zugriffsplan: 36 P0-Einschlüsse",
        "",
        "Stand: 2026-11-12",
        "Status: **BEREIT FÜR FREIGEGEBENEN ABRUF**; es wurde nichts heruntergeladen.",
        "",
        "Geprüft wurden drei lokale Bestände:",
        "",
        f"- `data/fulltext`: {summary['checked_fulltext_files']} Textdateien",
        f"- `data/fulltext_metadata`: {summary['checked_metadata_records']} JSON-Datensätze",
        f"- `data/fulltext_inbox`: {summary['checked_inbox_files']} Dateien",
        "",
        "| Merkmal | Anzahl |",
        "|---|---:|",
        f"| Artikel | **{len(rows)}** |",
        f"| Open Access | **{summary['open_access']}** |",
        f"| in Europe PMC | **{summary['in_epmc']}** |",
        f"| PDF laut Metadaten | **{summary['pdf_advertised']}** |",
        f"| lokaler Treffer gesamt | **{summary['local_present']}** |",
        f"| Treffer in `data/fulltext` | **{summary['fulltext_matches']}** |",
        f"| Treffer in Metadaten | **{summary['metadata_matches']}** |",
        f"| Treffer in Inbox | **{summary['inbox_matches']}** |",
        "",
        "Ein fehlender Treffer ist kein Nachweis der Abwesenheit in anderen Caches;",
        "die geprüften Pfade und Suchregeln stehen im JSON.",
        "",
        "## Artikel",
        "",
        "| PMC | DOI | Prio | OA | EPMC | PDF | Fulltext | Metadaten | Inbox | Lokal | Route |",
        "|---|---|---:|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| [{row['pmcid']}]({row['pmc_page_url']}) | `{row['doi']}` | "
            f"{row['priority']} | {'ja' if row['is_open_access'] else 'nein'} | "
            f"{'ja' if row['in_epmc'] else 'nein'} | {'ja' if row['has_pdf'] else 'nein'} | "
            f"{'ja' if row['fulltext_matches'] else 'nein'} | "
            f"{'ja' if row['metadata_matches'] else 'nein'} | "
            f"{'ja' if row['local_inbox_files'] else 'nein'} | "
            f"{'ja' if row['local_status'] == 'present' else 'nein'} | "
            f"{row['recommended_route']} |"
        )
    lines.extend(
        [
            "",
            "## Abrufregel",
            "",
            "- Kein Abruf ohne ausdrückliche Freigabe; der Plan selbst startet keinen Netzverkehr.",
            "- Ein Abruf ist ein Netzlauf und wird vorab als solcher dokumentiert.",
            "- XML ist die Primärquelle; PDF nur als Ergänzung, wenn Tabellen im XML fehlen.",
            "- Nach dem Abruf werden Dateien und SHA-256 lokal dokumentiert; keine Modellausgabe wird als Volltextbeleg verwendet.",
            "",
            "Kein Modelllauf, kein Volltextabruf.",
            "",
        ]
    )
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
