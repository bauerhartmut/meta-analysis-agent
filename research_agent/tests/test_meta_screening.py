"""Tests for the review frame: a frozen protocol and recorded decisions.

A count of pooled studies is only traceable if someone can see what was excluded
and why, and whether the criteria existed before the numbers were known. These
tests check exactly that: the protocol does not move once written, an invalid
decision cannot enter the table, and the PRISMA-style numbers follow the rows
instead of being guessed.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.screening import (
    DECISION_EXCLUDE, DECISION_INCLUDE, decided_source_ids, prisma_counts,
    protocol_path, record_automatic_decisions, record_decision, write_protocol,
)


class ScreeningTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="meta_screening_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        # A file database under <tmp>/data keeps the protocol inside the sandbox:
        # protocol_path() puts it next to the database's parent directory.
        self.db_path = os.path.join(self.tmp, "data", "research.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.db = Database(self.db_path)

    def source(self, sid, relevance=0.6, scored=1):
        self.db.save_source({
            "id": sid, "title": f"Paper {sid}", "url": f"https://example.org/{sid}",
            "author": "Doe, Jane", "publication_date": "2024-01-01",
            "source_type": "paper", "relevance": relevance,
            "relevance_scored": scored, "date_added": "2026-01-01T00:00:00Z",
        })

    def fulltext(self, sid, chars=4000):
        self.db.save_source_text(sid, "x " * (chars // 2), kind="html")


class TestProtocol(ScreeningTest):
    def test_protocol_is_written_once_and_never_overwritten(self):
        first = write_protocol(self.db, "embryo selection", "## Frage (PICO)\nA vs B")
        self.assertTrue(first["written"])
        second = write_protocol(self.db, "embryo selection", "## Frage (PICO)\nC vs D")
        self.assertFalse(second["written"])
        text = Path(protocol_path(self.db, "embryo selection")).read_text(encoding="utf-8")
        self.assertIn("A vs B", text)
        self.assertNotIn("C vs D", text)

    def test_empty_protocol_file_does_not_count_as_frozen(self):
        path = protocol_path(self.db, "topic")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        result = write_protocol(self.db, "topic", "## Frage (PICO)\nreal")
        self.assertTrue(result["written"])
        self.assertIn("real", path.read_text(encoding="utf-8"))


class TestDecisions(ScreeningTest):
    def test_an_unknown_decision_becomes_an_exclusion_not_an_inclusion(self):
        self.source("s1")
        row = record_decision(self.db, "topic", "s1", "maybe", reason="unclear")
        self.assertEqual(row["decision"], DECISION_EXCLUDE)
        self.assertEqual(decided_source_ids(self.db, "topic")["s1"]["reason"], "unclear")

    def test_a_later_decision_wins(self):
        self.source("s1")
        record_decision(self.db, "topic", "s1", DECISION_EXCLUDE, "no full text")
        record_decision(self.db, "topic", "s1", DECISION_INCLUDE, "full text found")
        self.assertEqual(
            decided_source_ids(self.db, "topic")["s1"]["decision"], DECISION_INCLUDE
        )

    def test_automatic_decisions_use_the_gate_and_need_a_real_text(self):
        self.source("high", relevance=0.8)
        self.source("low", relevance=0.1)
        self.source("unscored", relevance=0.9, scored=0)
        self.source("abstract_only", relevance=0.7)
        self.fulltext("high")
        # An abstract is not a document: a number read from it would not be poolable.
        self.db.save_source_text("abstract_only", "y " * 2000, kind="abstract")

        written = record_automatic_decisions(self.db, "topic", min_relevance=0.25)
        self.assertEqual(written[DECISION_INCLUDE], 1)
        self.assertEqual(written[DECISION_EXCLUDE], 1)
        decided = decided_source_ids(self.db, "topic")
        self.assertEqual(decided["high"]["decision"], DECISION_INCLUDE)
        self.assertEqual(decided["low"]["decision"], DECISION_EXCLUDE)
        self.assertNotIn("unscored", decided)
        self.assertNotIn("abstract_only", decided)

        # Running it again writes nothing: a decision is made once.
        again = record_automatic_decisions(self.db, "topic", min_relevance=0.25)
        self.assertEqual(again, {DECISION_INCLUDE: 0, DECISION_EXCLUDE: 0})


class TestPrismaCounts(ScreeningTest):
    def test_counts_follow_the_rows_and_name_every_exclusion_reason(self):
        self.source("in1", relevance=0.8)
        self.source("in2", relevance=0.7)
        self.source("out1", relevance=0.6)
        self.source("out2", relevance=0.6)
        record_decision(self.db, "topic", "out1", DECISION_EXCLUDE, "kein Volltext")
        record_decision(self.db, "topic", "out2", DECISION_EXCLUDE, "kein Volltext")
        self.db.save_study_effect({
            "id": "e1", "source_id": "in1", "outcome": "cog",
            "effect_type": "smd", "effect": 0.3, "se": 0.1, "ci_level": 0.95,
            "quote": "effect 0.30 (unit: SD)", "quote_start": 0, "quote_end": 24,
            "disputed": 0, "rejection_reason": "", "created_at": "2026-01-01T00:00:00Z",
        })
        self.db.save_study_effect({
            "id": "e2", "source_id": "in1", "outcome": "cog",
            "effect_type": "smd", "effect": 0.5, "se": 0.2, "ci_level": 0.95,
            "quote": "effect 0.50 (unit: SD)", "quote_start": 0, "quote_end": 24,
            "disputed": 1, "rejection_reason": "", "created_at": "2026-01-01T00:00:00Z",
        })

        counts = prisma_counts(self.db, "topic", min_relevance=0.25, min_studies=2)
        self.assertEqual(counts["sources"], 4)
        self.assertEqual(counts["excluded"], 2)
        self.assertEqual(counts["excluded_reasons"], {"kein Volltext": 2})
        self.assertEqual(counts["included"], 2)
        self.assertEqual(counts["effects"], 2)
        self.assertEqual(counts["effects_with_source"], 1)
        self.assertEqual(counts["effects_poolable"], 1)
        self.assertEqual(counts["effects_disputed"], 1)
        self.assertEqual(counts["sources_without_effects"], 1)

    def test_review_rows_are_counted_but_not_as_studies(self):
        self.source("in1", relevance=0.8)
        self.source("in2", relevance=0.8)
        self.db.save_study_effect({
            "id": "e1", "source_id": "in1", "outcome": "cog",
            "effect_type": "smd", "effect": 0.3, "se": 0.1, "ci_level": 0.95,
            "design": "randomized controlled trial",
            "quote": "effect 0.30 (unit: SD)", "quote_start": 0, "quote_end": 24,
            "disputed": 0, "rejection_reason": "", "created_at": "2026-01-01T00:00:00Z",
        })
        self.db.save_study_effect({
            "id": "e2", "source_id": "in2", "outcome": "cog",
            "effect_type": "smd", "effect": -2.0, "se": 0.4, "ci_level": 0.95,
            "design": "Network Meta-Analysis",
            "quote": "pooled estimate -2.00 (unit: SD)", "quote_start": 0,
            "quote_end": 30,
            "disputed": 0, "rejection_reason": "", "created_at": "2026-01-01T00:00:00Z",
        })

        counts = prisma_counts(self.db, "topic", min_relevance=0.25)
        self.assertEqual(counts["effects"], 2)
        self.assertEqual(counts["effects_aggregate"], 1)
        # Only the trial is usable for the pool; the review's aggregate is not.
        self.assertEqual(counts["effects_poolable_primary"], 1)

    def test_no_decisions_is_a_count_of_zero_not_a_crash(self):
        counts = prisma_counts(self.db, "topic")
        self.assertEqual(counts["sources"], 0)
        self.assertEqual(counts["included"], 0)
        self.assertEqual(counts["excluded_reasons"], {})


if __name__ == "__main__":
    unittest.main()
