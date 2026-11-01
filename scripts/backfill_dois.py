#!/usr/bin/env python3
"""Fill `sources.doi` for databases written before the column existed.

The DOI is what a forest-plot row and the same-cohort duplicate check hang on.
Deriving it from the URL at read time was not enough: the URL differs between
providers, so the same study could look like two studies.

Usage:
    python scripts/backfill_dois.py data/research-<slug>-<hash>.db [more.db ...]
    python scripts/backfill_dois.py --all          # every data/research*.db

Reports what it wrote, and never guesses: a source without a DOI in its URL keeps
an empty value.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from research_agent.database import Database
from research_agent.research.extractor import ContentExtractor

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("backfill_dois")


def backfill(path: str) -> dict:
    db = Database(path)
    rows = db._get_all("sources")
    written = 0
    without = 0
    for row in rows:
        if (row.get("doi") or "").strip():
            continue
        doi = ContentExtractor.doi_from_url(row.get("url") or "")
        if not doi:
            without += 1
            continue
        db._update("sources", row["id"], {"doi": doi})
        written += 1
    return {"path": path, "sources": len(rows), "written": written,
            "without_doi": without}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("databases", nargs="*", help="database files to migrate")
    parser.add_argument("--all", action="store_true",
                        help="every data/research*.db next to the project root")
    args = parser.parse_args()

    targets = list(args.databases)
    if args.all or not targets:
        root = Path(__file__).resolve().parent.parent / "data"
        targets = [str(p) for p in sorted(root.glob("research*.db"))]

    if not targets:
        logger.info("No databases found.")
        return 0

    for path in targets:
        if not Path(path).exists():
            logger.warning(f"Missing, skipped: {path}")
            continue
        result = backfill(path)
        logger.info(
            f"{result['path']}: {result['written']} DOI(s) written, "
            f"{result['without_doi']} source(s) without a DOI in the URL "
            f"(of {result['sources']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
