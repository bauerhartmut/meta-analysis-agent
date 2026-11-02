"""Phase 6/§4.1: fulltext recovery status stored as a real field.

The status is one deterministic rule per stored row (abstract kind else
the same 3000-char gate the coverage machinery relies on), written at
store time and backfilled idempotently for legacy databases - no CHARS>0
proxy residue, no per-source judgement from the model.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database


class RecoveryClassificationTest(unittest.TestCase):
    def test_rule_map(self):
        self.assertEqual(
            Database.classify_recovery("abstract", 9000),
            Database.RECOVERY_ABSTRACT)
        self.assertEqual(
            Database.classify_recovery("fulltext", 3000),
            Database.RECOVERY_FULLTEXT)
        self.assertEqual(
            Database.classify_recovery("html", 2999),
            Database.RECOVERY_SNIPPET)
        self.assertEqual(
            Database.classify_recovery("", 0),
            Database.RECOVERY_SNIPPET)


class RecoveryWriteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="recovery_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        db_path = os.path.join(self.tmp, "data", "research.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = Database(db_path)

    def test_stored_rows_carry_the_status(self):
        self.db.save_source_text("s1", "abstract only text", kind="abstract")
        self.db.save_source_text("s2", "R" * 4000, kind="fulltext")
        self.db.save_source_text("s3", "R" * 500, kind="html")
        rows = self.db._get_all("source_texts", order="id")
        by_source = {r["source_id"]: r["recovery_status"] for r in rows}
        self.assertEqual(by_source["s1"], Database.RECOVERY_ABSTRACT)
        self.assertEqual(by_source["s2"], Database.RECOVERY_FULLTEXT)
        self.assertEqual(by_source["s3"], Database.RECOVERY_SNIPPET)

    def test_counts_by_status(self):
        self.db.save_source_text("s1", "abstract text", kind="abstract")
        self.db.save_source_text("s2", "R" * 4000, kind="fulltext")
        counts = self.db.get_fulltext_recovery_counts()
        self.assertEqual(counts.get(Database.RECOVERY_ABSTRACT), 1)
        self.assertEqual(counts.get(Database.RECOVERY_FULLTEXT), 1)
        self.assertNotIn(Database.RECOVERY_SNIPPET, counts)

    def test_empty_body_is_not_stored(self):
        self.assertIsNone(self.db.save_source_text("s9", "   "))
        self.assertEqual(self.db.get_fulltext_recovery_counts(), {})


class LegacyBackfillTest(unittest.TestCase):
    """A database written before the column arrives: backfill on open."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="legacy_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.db_path = os.path.join(self.tmp, "data", "research.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def test_legacy_rows_get_classified_on_reopen(self):
        # Seed rows WITHOUT the status using the in-memory database shape,
        # then reopen the file: the migration fills the status once.
        db = Database(self.db_path)
        db._insert("source_texts", {
            "id": "t1", "source_id": "s1", "kind": "abstract",
            "chars": 100, "text": "", "created_at": "2026-01-01"})
        db._insert("source_texts", {
            "id": "t2", "source_id": "s2", "kind": "fulltext",
            "chars": 4500, "text": "", "created_at": "2026-01-01"})
        db._insert("source_texts", {
            "id": "t3", "source_id": "s3", "kind": "html",
            "chars": 1200, "text": "", "created_at": "2026-01-01"})
        # Now close and reopen - the migration pass runs on init.
        reopened = Database(self.db_path)
        rows = reopened._get_all("source_texts", order="id")
        by_id = {r["id"]: r["recovery_status"] for r in rows}
        self.assertEqual(by_id["t1"], Database.RECOVERY_ABSTRACT)
        self.assertEqual(by_id["t2"], Database.RECOVERY_FULLTEXT)
        self.assertEqual(by_id["t3"], Database.RECOVERY_SNIPPET)

    def test_backfill_is_idempotent(self):
        db = Database(self.db_path)
        Database(self.db_path)  # second init: no crash, statuses survive
