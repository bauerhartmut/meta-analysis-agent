"""Independent statistical reproduction (order §7.3 Abnahme).

CLI that recomputes every pool from the stored effect rows in one topic
database and writes the results as flat artifacts (CSV rows + JSON groups),
deliverable to external reference scripts (metafor/R) without any agent
runtime. Within this process the calculations come from the same tested
engine (meta.pooling) - the *independent* part of the Abnahme is the external
re-implementation against the exported CSV, which the roadmap keeps as an
explicit open item.

Usage:
    python -m research_agent.evals.stat_repro data/research-<topic>-<hash>.db \\
        --out data/baseline/<name>-pools.json
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from ..meta.pooling import build_analysis, POOL_VERSION

logger = logging.getLogger(__name__)


def _load_rows(db_path: str) -> List[Dict[str, Any]]:
    """Stored effect rows as plain dicts (readonly; the DB never changes)."""
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM study_effects ORDER BY outcome_key, created_at"
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def recompute(db_path: str) -> Dict[str, Any]:
    rows = _load_rows(db_path)
    analysis = build_analysis(rows)
    flat: List[Dict[str, Any]] = []
    for key, group in (analysis.get("groups") or {}).items():
        for row in group.get("rows") or []:
            flat.append({
                "group": key,
                "label": row.get("label"),
                "source_id": row.get("source_id"),
                "study_id": row.get("study_id"),
                "doi": row.get("doi"),
                "outcome": row.get("outcome"),
                "scale": row.get("scale"),
                "est": row.get("est"),
                "se": row.get("se"),
                "adjusted": row.get("adjusted"),
                "time_point": row.get("time_point"),
                "disputed": row.get("disputed"),
            })
    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "db": db_path,
        "pool_version": POOL_VERSION,
        "n_rows": len(rows),
        "n_pool_rows": len(flat),
        "rows": flat,
        "groups": {
            k: {kk: vv for kk, vv in g.items() if kk != "rows"}
            for k, g in (analysis.get("groups") or {}).items()
        },
        "excluded": analysis.get("excluded") or [],
        "off_target": analysis.get("off_target") or [],
    }


def export_csv(result: Dict[str, Any], path: Path) -> None:
    if not result["rows"]:
        return
    fields = list(result["rows"][0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(result["rows"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Statistical reproduction from stored effect rows (§7.3)")
    parser.add_argument("db", type=str)
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()
    result = recompute(args.db)
    out_path = args.out or (
        "data/baseline/" + Path(args.db).stem + "-pools.json")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    export_csv(result, Path(out_path).with_suffix(".csv"))
    print(f"[stat_repro] pool_version={result['pool_version']} "
          f"rows={result['n_rows']} pool_rows={result['n_pool_rows']} "
          f"groups={len(result['groups'])}")
    print(f"[stat_repro] written: {out_path} (+ csv)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
