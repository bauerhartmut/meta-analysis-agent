#!/usr/bin/env python3
"""Merge two source rows that are the same work, and drop exact duplicate evidence.

Four runs sharing one database left almost no structural duplicates, because
every insert is keyed: sources dedupe by URL, work items by (kind, ref_id), facts
by content. What does remain is the older, unrelated case: the same paper stored
twice because two providers hand out different URLs for it (Europe PMC and PubMed
for the same PMID). That is one work, not two - and while it stays split, its
facts are split with it and the effect extraction reads it twice.

This script merges one such pair, repointing every row that hangs off the dropped
source, then deletes the extra evidence row whose id nothing references. It
prints each change; nothing is approximated. Run it with the agent stopped - the
merge must not race a cycle that is writing the same tables.

Usage:
    python scripts/merge_duplicate_source.py --keep <id> --drop <id> [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from research_agent.config import get_config
from research_agent.database import Database


def _repoint_fact_sources(db, keep: str, drop: str) -> int:
    """facts.source_ids is a JSON list; replace one id, keep the order."""
    changed = 0
    rows = db._get_all("facts", where="source_ids LIKE ?", params=(f"%{drop}%",))
    for row in rows:
        try:
            ids = json.loads(row.get("source_ids") or "[]")
        except (TypeError, ValueError):
            continue
        if not isinstance(ids, list) or drop not in ids:
            continue
        merged = []
        for value in ids:
            target = keep if value == drop else value
            if target not in merged:
                merged.append(target)
        with db._conn() as conn:
            conn.execute("UPDATE facts SET source_ids = ? WHERE id = ?",
                         (json.dumps(merged), row["id"]))
        changed += 1
    return changed


def _dedupe_screening(db, keep: str, drop: str) -> int:
    with db._conn() as conn:
        conn.execute("UPDATE screening SET source_id = ? WHERE source_id = ?", (keep, drop))
        rows = conn.execute(
            """SELECT topic, source_id, COUNT(*) n FROM screening
               WHERE source_id = ? GROUP BY topic, source_id HAVING COUNT(*) > 1""",
            (keep,),
        ).fetchall()
        removed = 0
        for topic, source_id, _n in rows:
            keep_row = conn.execute(
                """SELECT id FROM screening WHERE topic = ? AND source_id = ?
                   ORDER BY created_at ASC LIMIT 1""",
                (topic, source_id),
            ).fetchone()
            if not keep_row:
                continue
            removed += conn.execute(
                """DELETE FROM screening WHERE topic = ? AND source_id = ?
                   AND id <> ?""",
                (topic, source_id, keep_row["id"]),
            ).rowcount
        return removed


def _dedupe_work_items(db, keep: str, drop: str) -> int:
    """Move the dropped source's work items over, or drop them when they collide.

    ``work_items`` is unique on (topic, kind, ref_id), so a plain UPDATE fails as
    soon as both sources have an item of the same kind - which is the normal case
    for two copies of one paper. The finished item wins: it carries the result.
    """
    moved = 0
    with db._conn() as conn:
        rows = conn.execute("SELECT * FROM work_items WHERE ref_id = ?",
                            (drop,)).fetchall()
        for row in rows:
            existing = conn.execute(
                """SELECT id, status FROM work_items
                   WHERE topic = ? AND kind = ? AND ref_id = ?""",
                (row["topic"], row["kind"], keep),
            ).fetchone()
            if existing is None:
                conn.execute("UPDATE work_items SET ref_id = ? WHERE id = ?",
                             (keep, row["id"]))
                moved += 1
                continue
            if row["status"] == "done" and existing["status"] != "done":
                conn.execute("DELETE FROM work_items WHERE id = ?", (existing["id"],))
                conn.execute("UPDATE work_items SET ref_id = ? WHERE id = ?",
                             (keep, row["id"]))
                moved += 1
            else:
                conn.execute("DELETE FROM work_items WHERE id = ?", (row["id"],))
        return moved


def merge(db, keep: str, drop: str, dry_run: bool) -> dict:
    source = db.get_source(keep)
    other = db.get_source(drop)
    if not source or not other:
        raise SystemExit("one of the source ids does not exist")

    facts = db._get_all("facts", where="source_ids LIKE ?", params=(f"%{drop}%",))
    texts = db._get_all("source_texts", where="source_id = ?", params=(drop,))
    evidence = db._get_all("evidence", where="source_id = ?", params=(drop,))
    effects = db._get_all("study_effects", where="source_id = ?", params=(drop,))
    items = db._get_all("work_items", where="ref_id = ?", params=(drop,))

    report = {
        "keep": {"id": keep, "url": source.get("url"), "facts": 0},
        "drop": {"id": drop, "url": other.get("url")},
        "facts_repointed": len(facts),
        "source_texts_repointed": len(texts),
        "evidence_repointed": len(evidence),
        "study_effects_repointed": len(effects),
        "work_items_repointed": len(items),
        "dry_run": dry_run,
    }
    if dry_run:
        return report

    report["facts_changed"] = _repoint_fact_sources(db, keep, drop)
    with db._conn() as conn:
        conn.execute("UPDATE source_texts SET source_id = ? WHERE source_id = ?",
                     (keep, drop))
        conn.execute("UPDATE evidence SET source_id = ? WHERE source_id = ?",
                     (keep, drop))
        conn.execute("UPDATE study_effects SET source_id = ? WHERE source_id = ?",
                     (keep, drop))
        conn.execute("DELETE FROM sources WHERE id = ?", (drop,))
    report["work_items_removed"] = _dedupe_work_items(db, keep, drop)
    report["screening_removed"] = _dedupe_screening(db, keep, drop)
    return report


def drop_duplicate_evidence(db, dry_run: bool) -> dict:
    """Remove evidence rows whose id nothing references and whose content repeats.

    A hypothesis keeps evidence ids in a JSON list, so deleting a row that is
    referenced there would leave a dangling id behind. Only unreferenced copies
    are removed.
    """
    removed = []
    with db._conn() as conn:
        rows = conn.execute(
            """SELECT hypothesis_id, source_id, evidence_type, content,
                      GROUP_CONCAT(id) ids, COUNT(*) n
               FROM evidence GROUP BY 1, 2, 3, 4 HAVING COUNT(*) > 1"""
        ).fetchall()
        for row in rows:
            ids = (row["ids"] or "").split(",")
            for eid in ids[1:]:
                referenced = conn.execute(
                    """SELECT COUNT(*) n FROM hypotheses
                       WHERE supporting_evidence LIKE ? OR contradicting_evidence LIKE ?""",
                    (f"%{eid}%", f"%{eid}%"),
                ).fetchone()["n"]
                if referenced:
                    continue
                if not dry_run:
                    conn.execute("DELETE FROM evidence WHERE id = ?", (eid,))
                removed.append({"id": eid, "hypothesis_id": row["hypothesis_id"]})
    return {"removed": removed, "dry_run": dry_run}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", required=True, help="source id that survives")
    parser.add_argument("--drop", required=True, help="duplicate source id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--evidence", action="store_true",
                        help="also remove unreferenced duplicate evidence rows")
    parser.add_argument("--topic", default="", help="topic whose database to open")
    args = parser.parse_args()

    config = get_config()
    path = config.database_for_topic(args.topic) if args.topic \
        else config.database_url
    db = Database(path)
    print("database:", path)
    print(json.dumps(merge(db, args.keep, args.drop, args.dry_run),
                     ensure_ascii=False, indent=1))
    if args.evidence:
        print(json.dumps(drop_duplicate_evidence(db, args.dry_run),
                         ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
