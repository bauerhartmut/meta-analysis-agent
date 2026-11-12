#!/usr/bin/env python3
"""Export the P0 Europe PMC candidate frame.

Reads the local Yun/Freeze PMCIDs, queries Europe PMC once for the
pre-registered September 2026 frame, and writes all hits plus the
article-disjoint subset. No model call, no full-text download, no test access.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "evaluation" / "c1_pilot"
OUT = PILOT / "holdout_p0_20261112"
YUN_PATH = ROOT / "processed_data" / "yun_ico_records.jsonl"
FREEZE_PATH = ROOT / "processed_data" / "yun_c1_frozen_275.jsonl"
DEV_PATH = ROOT / "processed_data" / "yun_c1_dev_26.jsonl"
TEST_PATH = ROOT / "processed_data" / "yun_c1_test_249.jsonl"

BASE_QUERY = (
    '(OPEN_ACCESS:Y) AND (HAS_FT:Y) '
    'AND (PUB_TYPE:"Randomized Controlled Trial") AND (LANG:"eng")'
)
FRAME = "FIRST_PDATE:[2026-09-01 TO 2026-09-30]"
QUERY = f"{BASE_QUERY} AND ({FRAME})"
SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
PAGE_SIZE = 200
MAX_PAGES = 5


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"missing required file: {path}")
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def normalize_pmcid(value: object) -> str:
    text = str(value or "").strip().upper()
    if text.startswith("PMC"):
        text = text[3:]
    return f"PMC{text}" if text.isdigit() else ""


def known_pmcids(path: Path) -> set[str]:
    ids: set[str] = set()
    for row in read_jsonl(path):
        pmcid = normalize_pmcid(row.get("pmcid") or row.get("study_id"))
        if pmcid:
            ids.add(pmcid)
    return ids


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_pmcid(row: dict) -> str:
    pmcid = normalize_pmcid(row.get("pmcid"))
    if pmcid:
        return pmcid
    fulltext = row.get("fullTextIdList") or {}
    values = fulltext.get("fullTextId") if isinstance(fulltext, dict) else None
    if isinstance(values, list):
        for value in values:
            pmcid = normalize_pmcid(value)
            if pmcid:
                return pmcid
    return ""


def wait_for_response(params: dict) -> dict:
    response = requests.get(
        SEARCH_URL,
        params=params,
        timeout=90,
        headers={"User-Agent": "meta-analysis-agent/c1-p0"},
    )
    response.raise_for_status()
    return response.json()


def fetch_all() -> tuple[list[dict], int, str]:
    params = {
        "query": QUERY,
        "format": "json",
        "resultType": "core",
        "pageSize": PAGE_SIZE,
        "sort": "P_PDATE_D desc",
        "cursorMark": "*",
    }
    first = wait_for_response(params)
    hit_count = int(first.get("hitCount") or 0)
    rows: list[dict] = []
    page = first
    for page_number in range(1, MAX_PAGES + 1):
        batch = (page.get("resultList") or {}).get("result") or []
        print(
            f"page {page_number}: {len(batch)} records "
            f"({len(rows) + len(batch)}/{hit_count})",
            flush=True,
        )
        rows.extend(batch)
        cursor = page.get("nextCursorMark") or ""
        if not batch or len(rows) >= hit_count or not cursor:
            break
        if page_number == MAX_PAGES:
            raise SystemExit(
                f"query returned more than {MAX_PAGES * PAGE_SIZE} results; "
                "narrow the frame before exporting"
            )
        params["cursorMark"] = cursor
        page = wait_for_response(params)
    return rows, hit_count, QUERY


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    yun = known_pmcids(YUN_PATH)
    freeze = known_pmcids(FREEZE_PATH)
    dev = known_pmcids(DEV_PATH)
    test = known_pmcids(TEST_PATH)
    all_known = yun | freeze | dev | test

    rows, hit_count, query = fetch_all()
    normalized: list[dict] = []
    for row in rows:
        pmcid = extract_pmcid(row)
        pub_types = (row.get("pubTypeList") or {}).get("pubType") or []
        if isinstance(pub_types, str):
            pub_types = [pub_types]
        normalized.append(
            {
                "pmcid": pmcid,
                "pmid": str(row.get("pmid") or ""),
                "doi": str(row.get("doi") or ""),
                "title": str(row.get("title") or ""),
                "authors": str(row.get("authorString") or ""),
                "journal": str(
                    row.get("journalTitle")
                    or ((row.get("journalInfo") or {}).get("journal") or {}).get("title")
                    or ""
                ),
                "pub_year": str(row.get("pubYear") or ""),
                "first_publication_date": str(row.get("firstPublicationDate") or ""),
                "pub_types": pub_types,
                "is_open_access": row.get("isOpenAccess"),
                "in_epmc": row.get("inEPMC"),
                "has_pdf": row.get("hasPDF"),
                "abstract": str(row.get("abstractText") or ""),
                "article_disjoint": bool(pmcid) and pmcid not in all_known,
                "known_overlap": bool(pmcid) and pmcid in all_known,
            }
        )

    all_path = OUT / "candidates_all.jsonl"
    with all_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in normalized:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    disjoint = [row for row in normalized if row["article_disjoint"]]
    disjoint_path = OUT / "candidates.jsonl"
    with disjoint_path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in disjoint:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    with_pmcid = [row for row in normalized if row["pmcid"]]
    unique = {row["pmcid"] for row in with_pmcid}
    abstract_coverage = sum(bool(row["abstract"].strip()) for row in normalized)
    journal_coverage = sum(bool(row["journal"].strip()) for row in normalized)
    missing_pmcid = [row for row in normalized if not row["pmcid"]]
    overlaps = {
        "yun": len({row["pmcid"] for row in with_pmcid} & yun),
        "freeze": len({row["pmcid"] for row in with_pmcid} & freeze),
        "dev": len({row["pmcid"] for row in with_pmcid} & dev),
        "test": len({row["pmcid"] for row in with_pmcid} & test),
    }
    overlap_rows = [row for row in normalized if row["known_overlap"]]
    summary = {
        "frame_id": "p0_europepmc_202609",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "source": "Europe PMC REST API / PMC Open Access Subset",
        "search_url": SEARCH_URL,
        "page_size": PAGE_SIZE,
        "sort": "P_PDATE_D desc",
        "hit_count": hit_count,
        "returned_records": len(normalized),
        "unique_pmcid_articles": len(unique),
        "records_without_pmcid": len(missing_pmcid),
        "known_article_sets": {
            "yun": len(yun),
            "freeze": len(freeze),
            "dev": len(dev),
            "test": len(test),
            "union": len(all_known),
        },
        "overlap_with_known": overlaps,
        "overlap_articles": len({row["pmcid"] for row in overlap_rows}),
        "article_disjoint_articles": len({row["pmcid"] for row in disjoint}),
        "duplicate_pmcid_records": len(with_pmcid) - len(unique),
        "abstract_coverage": abstract_coverage,
        "journal_coverage": journal_coverage,
        "by_year": dict(Counter(row["pub_year"] for row in normalized)),
        "files": {
            "all": str(all_path.relative_to(PILOT)),
            "disjoint": str(disjoint_path.relative_to(PILOT)),
            "all_sha256": sha256(all_path),
            "disjoint_sha256": sha256(disjoint_path),
        },
        "limitations": [
            "Nur Query-Label 'Randomized Controlled Trial'; kein Abstract- oder Volltextscreening.",
            "Keine Prüfung auf Parallelgruppen, zwei Arme oder extrahierbare N/Mean/SD/Events.",
            "Kein Modelllauf, kein Holdout-Freeze, keine Annotation.",
        ],
    }
    summary_path = OUT / "candidate_summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    disjoint_check = {
        "frame_id": summary["frame_id"],
        "checked_at": summary["generated_at"],
        "known_article_sets": summary["known_article_sets"],
        "overlap_with_known": summary["overlap_with_known"],
        "overlap_articles": summary["overlap_articles"],
        "article_disjoint_articles": summary["article_disjoint_articles"],
        "candidate_file": summary["files"]["disjoint"],
        "candidate_file_sha256": summary["files"]["disjoint_sha256"],
    }
    (OUT / "article_disjoint_check.json").write_text(
        json.dumps(disjoint_check, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    md_lines = [
        "# P0-Kandidatenexport September 2026",
        "",
        f"Query: `{query}`",
        "",
        "| Kennzahl | Wert |",
        "|---|---:|",
        f"| Europe-PMC-Treffer | {hit_count} |",
        f"| Exportierte Records | {len(normalized)} |",
        f"| Eindeutige PMCIDs | {len(unique)} |",
        f"| Ohne PMCID | {len(missing_pmcid)} |",
        f"| Abstract vorhanden | {abstract_coverage} |",
        f"| Journal vorhanden | {journal_coverage} |",
        f"| Überschneidung Yun | {overlaps['yun']} |",
        f"| Überschneidung Freeze | {overlaps['freeze']} |",
        f"| Überschneidung Dev | {overlaps['dev']} |",
        f"| Überschneidung Test | {overlaps['test']} |",
        f"| **Artikeldisjunkt** | **{summary['article_disjoint_articles']}** |",
        "",
        "Die Zählung ist eine Artikelzählung nach PMCID. Ein Abstract- oder",
        "Volltextscreening auf Parallelgruppen und extrahierbare Armwerte ist",
        "noch nicht erfolgt. Es gab keinen Modelllauf.",
        "",
    ]
    (OUT / "candidate_summary.md").write_text(
        "\n".join(md_lines), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
