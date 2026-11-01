"""Phase 2 study-level model tests (order §5.1/§5.2)."""

import shutil
import tempfile
import unittest
from pathlib import Path

from research_agent.database import Database
from research_agent.meta.studies import (
    ensure_study_schema, link_publication_to_study, mark_overlap_candidate,
    overlap_open_counts, register_publication, register_study,
    resolve_overlap)


class StudyModelTest(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        ensure_study_schema(self.db)

    def test_schema_is_additive_and_idempotent(self):
        # twice runs fine (order §14: no breaking migration)
        ensure_study_schema(self.db)
        with self.db._conn() as conn:
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        self.assertTrue({"meta_studies", "meta_publications",
                         "meta_overlap_candidates"} <= tables)
        # the additive column exists on study_effects
        with self.db._conn() as conn:
            cols = [r[1] for r in
                    conn.execute("PRAGMA table_info(study_effects)").fetchall()]
        self.assertIn("study_id", cols)

    def test_effect_rows_default_to_unclaimed_study(self):
        self.db.save_study_effect({
            "id": "e9", "source_id": "x1", "outcome": "bp",
            "effect_type": "smd", "effect": -0.4, "se": 0.1,
        })
        with self.db._conn() as conn:
            row = conn.execute(
                "SELECT study_id FROM study_effects WHERE id='e9'").fetchone()
        self.assertEqual(row[0], "")

    def test_link_requires_rationale_and_moves_rows_once(self):
        register_study(self.db, "coh-A", design="rct",
                       recruitment="community", follow_up="12 months")
        register_publication(self.db, "pub-1", doi="10.2/pub",
                             title="A trial", year=2019, source_id="x1")
        self.db.save_study_effect({
            "id": "e1", "source_id": "x1", "outcome": "bp",
            "effect_type": "smd", "effect": -0.4, "se": 0.1,
        })
        with self.assertRaises(ValueError):
            link_publication_to_study(self.db, "pub-1", "coh-A", "")
        link_publication_to_study(self.db, "pub-1", "coh-A",
                                  "same cohort: same authors, one centre, "
                                  "12-month follow-up in both papers")
        with self.db._conn() as conn:
            eff = conn.execute(
                "SELECT study_id FROM study_effects WHERE id='e1'").fetchone()[0]
        self.assertEqual(eff, "coh-A")

    def test_overlap_candidates_never_auto_resolved(self):
        register_study(self.db, "coh-A", design="rct")
        register_study(self.db, "coh-B", design="rct")
        cid = mark_overlap_candidate(
            self.db, "coh-A", "coh-B", doi_a="10.2/a", doi_b="10.2/b",
            reason="same trial registry ID in both abstracts")
        self.assertEqual(overlap_open_counts(self.db).get("candidate"), 1)
        # resolution without rationale/decision-maker is refused
        with self.assertRaises(ValueError):
            resolve_overlap(self.db, cid, "confirmed_same_cohort", "", "")
        self.assertTrue(resolve_overlap(
            self.db, cid, "confirmed_same_cohort",
            "author statement + recruitment dates overlap",
            decided_by="human-review"))
        self.assertEqual(
            overlap_open_counts(self.db).get("confirmed_same_cohort"), 1)
        self.assertNotIn("candidate", overlap_open_counts(self.db))


if __name__ == "__main__":
    unittest.main()
