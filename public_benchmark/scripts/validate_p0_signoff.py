#!/usr/bin/env python3
"""Validate the human sign-off list.

Default mode reports progress and exits 0 even while cases are open. Use
--strict to require every case to have reviewer, date and final decision.
No model, no network.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluation" / "c1_pilot" / "holdout_p0_20261112"
CSV_PATH = OUT / "manual_review_signoff_v1.csv"
REQUIRED = {
    "number",
    "pmcid",
    "doi",
    "source_url",
    "title",
    "decision",
    "priority",
    "reviewer",
    "review_date",
    "final_decision",
}
ALLOWED = {"einschluss", "ausschluss", "offen"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    with CSV_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    errors: list[str] = []
    if len(rows) != 65:
        errors.append(f"expected 65 rows, got {len(rows)}")
    if len({row.get("pmcid", "") for row in rows}) != len(rows):
        errors.append("duplicate PMCIDs")
    missing = REQUIRED - set(rows[0]) if rows else REQUIRED
    if missing:
        errors.append(f"missing columns: {sorted(missing)}")
    for row in rows:
        number = row.get("number", "?")
        if not row.get("source_url") or not row.get("doi"):
            errors.append(f"{number}: source_url/doi missing")
        final = (row.get("final_decision") or "").strip()
        if final not in ALLOWED:
            errors.append(f"{number}: final_decision={final!r} not allowed")
        if final != "offen":
            if not (row.get("reviewer") or "").strip() or row["reviewer"] == "offen":
                errors.append(f"{number}: reviewer required for final decision")
            if not DATE_RE.match((row.get("review_date") or "").strip()):
                errors.append(f"{number}: review_date must be YYYY-MM-DD")
            expected = "einschluss" if row.get("decision") == "include_for_fulltext" else "ausschluss"
            if final != expected and not (row.get("human_note") or "").strip():
                errors.append(f"{number}: changed final decision requires human_note")
            if final == "einschluss" and row.get("decision") != "include_for_fulltext":
                errors.append(f"{number}: einschluss contradicts preliminary decision")
            if final == "ausschluss" and row.get("decision") != "exclude":
                errors.append(f"{number}: ausschluss contradicts preliminary decision")
    completed = sum((row.get("final_decision") or "offen") != "offen" for row in rows)
    reviewer_counts = Counter(row.get("reviewer", "offen") for row in rows)
    assisted = reviewer_counts.get("Codebuff assistiert", 0)
    complete = completed == len(rows) and not errors
    summary = {
        "signoff_id": "p0_manual_signoff_v1",
        "status": (
            "complete_assisted_pending_human_review"
            if complete and assisted
            else "complete"
            if complete
            else "pending"
        ),
        "records": len(rows),
        "completed": completed,
        "open": len(rows) - completed,
        "assisted": assisted,
        "human_review_complete": complete and assisted == 0,
        "reviewer_counts": dict(reviewer_counts),
        "preliminary_counts": dict(Counter(row.get("decision", "") for row in rows)),
        "final_counts": dict(Counter(row.get("final_decision", "offen") for row in rows)),
        "errors": errors,
        "model_used": False,
    }
    if args.output:
        Path(args.output).write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors or (args.strict and completed != len(rows)):
        sys.exit(1)


if __name__ == "__main__":
    main()
