#!/usr/bin/env python3
"""Document access routes for the 36 P0 includes without fetching anything.

Uses only local candidate metadata and local inbox filenames. All articles are
Open Access and in Europe PMC; the plan records the exact XML endpoint and
whether a PDF is advertised. No network call, no model call.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "evaluation" / "c1_pilot"
OUT = PILOT / "holdout_p0_20261112"
SIGNOFF = OUT / "manual_review_signoff_v1.json"
CANDIDATES = OUT / "candidates.jsonl"
INBOX = ROOT.parent / "data" / "fulltext_inbox"
JSON_PATH = OUT / "fulltext_access_plan_v1.json"
CSV_PATH = OUT / "fulltext_access_plan_v1.csv"
MD_PATH = OUT / "fulltext_access_plan_v1.md"


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


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

    rows = []
    for row in includes:
        candidate = candidates[row["pmcid"]]
        local_names = [name for name in inbox_names(row["doi"]) if (INBOX / name).exists()]
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
                "recommended_route": "europepmc_fulltext_xml",
                "local_inbox_files": local_names,
                "local_status": "present" if local_names else "not_present",
                "network_required": True,
                "fetch_status": "not_started",
                "notes": (
                    "PDF laut Metadaten vorhanden; XML ist der primäre Extraktionsweg."
                    if candidate.get("has_pdf") == "Y"
                    else "Kein PDF laut Metadaten; XML ist der einzige vorgesehene Weg."
                ),
            }
        )

    rows.sort(key=lambda row: ({"hoch": 0, "mittel": 1, "niedrig": 2}[row["priority"]], row["pmcid"]))
    payload = {
        "plan_id": "p0_fulltext_access_v1",
        "created_at": "2026-11-12",
        "status": "ready_for_approved_fetch",
        "records": len(rows),
        "network_fetch_performed": False,
        "model_used": False,
        "summary": {
            "articles": len(rows),
            "open_access": sum(row["is_open_access"] for row in rows),
            "in_epmc": sum(row["in_epmc"] for row in rows),
            "pdf_advertised": sum(row["has_pdf"] for row in rows),
            "local_present": sum(row["local_status"] == "present" for row in rows),
            "xml_route": sum(row["recommended_route"] == "europepmc_fulltext_xml" for row in rows),
            "pdf_without_xml_route": sum(
                row["has_pdf"] and row["recommended_route"] != "europepmc_fulltext_xml" for row in rows
            ),
        },
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
            "local_inbox_files",
            "network_required",
            "fetch_status",
            "notes",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, "local_inbox_files": ";".join(row["local_inbox_files"])})

    lines = [
        "# Volltext-Zugriffsplan: 36 P0-Einschlüsse",
        "",
        "Stand: 2026-11-12",
        "Status: **BEREIT FÜR FREIGEGEBENEN ABRUF**; es wurde nichts heruntergeladen.",
        "",
        "Alle 36 Artikel sind laut den lokalen Kandidatenmetadaten Open Access und in",
        "Europe PMC. Der primäre Weg ist `fullTextXML`; 33 Artikel haben zusätzlich",
        "ein PDF-Flag. Drei Artikel haben kein PDF-Flag, aber einen XML-Weg.",
        "",
        "| Merkmal | Anzahl |",
        "|---|---:|",
        f"| Artikel | **{len(rows)}** |",
        f"| Open Access | **{payload['summary']['open_access']}** |",
        f"| in Europe PMC | **{payload['summary']['in_epmc']}** |",
        f"| PDF laut Metadaten | **{payload['summary']['pdf_advertised']}** |",
        f"| lokal vorhanden | **{payload['summary']['local_present']}** |",
        "",
        "## Artikel",
        "",
        "| PMC | DOI | Prio | OA | EPMC | PDF | Lokal | Route |",
        "|---|---|---:|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| [{row['pmcid']}]({row['pmc_page_url']}) | `{row['doi']}` | "
            f"{row['priority']} | {'ja' if row['is_open_access'] else 'nein'} | "
            f"{'ja' if row['in_epmc'] else 'nein'} | {'ja' if row['has_pdf'] else 'nein'} | "
            f"{row['local_status']} | {row['recommended_route']} |"
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
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
