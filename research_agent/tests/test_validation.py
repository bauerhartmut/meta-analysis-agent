"""Phase 7: deterministic validation layer (release gate).

The layer re-verifies the machine's own evidence chain over stored data:
every stored effect span must reproduce with the same locator (locate_quote)
over the stored document text, poolable rows must carry a verbatim span,
disputed/rejected rows are counted (not re-judged), and RoB coverage gaps
surface as warnings - never as a fitted or LLM-backed judgement.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.validation import (
    STATUS_BLOCKED, STATUS_MACHINE_VALIDATED, STATUS_NEEDS_REVIEW,
    record_validation, release_gate_status, run_validation,
)
from research_agent.research.fulltext import locate_quote

DOC = ("Patients on the programme needed fewer sick days in week 8, "
       "and weight loss averaged two kilograms by follow-up.")
QUOTE = "needed fewer sick days in week 8."


def _mk_db(tmp, name="research.db"):
    db_path = os.path.join(tmp, "data", name)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return db_path, Database(db_path)


def _seed_source(db, source_id="src1", text=DOC):
    # The RoB-coverage query has a chars >= 3000 gate for real documents;
    # the stored marker (not the short fixture text) must pass it.
    db._insert("sources", {
        "id": source_id, "title": "Trial A",
        "relevance": 0.9, "relevance_scored": 1,
        "relevance_unjudgeable": 0, "date_added": "2026-01-01",
    })
    text_id = f"txt_{source_id}"
    db._insert("source_texts", {
        "id": text_id, "source_id": source_id, "kind": "fulltext",
        "chars": 4000, "text": text, "created_at": "2026-01-01",
    })
    return source_id, text_id


def _seed_spanned_effect(db, source_id, text, text_id, effect_id="eff1"):
    """Store the quote exactly the extractor would: via locate_quote."""
    span = locate_quote(text, QUOTE)
    assert span is not None, "fixture quote must verify in the fixture text"
    db.save_study_effect({
        "id": effect_id, "source_id": source_id,
        "outcome": "sick_days", "effect": -1.4, "se": 0.5,
        "quote": QUOTE, "quote_start": span.start, "quote_end": span.end,
        "source_text_id": text_id, "extractor": "meta-extraction/2",
        "created_at": "2026-01-01",
    })
    return (span.start, span.end)


def _seed_raw_effect(db, source_id, text_id, effect_id, *, start=-1, end=-1,
                     quote="", disputed=0, rejection_reason="", with_se=True):
    row = {
        "id": effect_id, "source_id": source_id,
        "outcome": "sick_days", "effect": -1.4,
        "quote": quote, "quote_start": start, "quote_end": end,
        "source_text_id": text_id, "extractor": "meta-extraction/2",
        "created_at": "2026-01-01",
    }
    if with_se:
        row["se"] = 0.5
    if disputed:
        row["disputed"] = 1
    if rejection_reason:
        row["rejection_reason"] = rejection_reason
    db.save_study_effect(row)


class ValidationStatusTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="validation_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.db_path, self.db = _mk_db(self.tmp)

    def test_clean_corpus_is_machine_validated(self):
        _seed_source(self.db)
        _seed_spanned_effect(self.db, "src1", DOC, "txt_src1")
        self.db.save_bias_assessment({
            "source_id": "src1", "design": "rct", "instrument": "rob2",
            "domains": "[]", "overall": "high",
            "assessor": "rob_assessor_v1", "created_at": "",
        })
        result = run_validation(self.db)
        self.assertEqual(result["status"], STATUS_MACHINE_VALIDATED,
                         msg=f"unexpected verdict: {result}")
        self.assertEqual(result["checks"]["effect_quotes"]["checked"], 1)
        self.assertEqual(result["checks"]["disputed"]["disputed"], 0)

    def test_quote_mismatch_blocks(self):
        _seed_source(self.db)
        _seed_raw_effect(self.db, "src1", "txt_src1", "bad1",
                         start=5, end=20, quote="WRONG QUOTED SPAN")
        result = run_validation(self.db)
        self.assertEqual(result["status"], STATUS_BLOCKED)
        self.assertTrue(any(b["rule"] == "quote_mismatch"
                            for b in result["blockers"]))

    def test_poolable_effect_without_quote_blocks(self):
        _seed_source(self.db)
        _seed_raw_effect(self.db, "src1", "txt_src1", "noq",
                         quote="", with_se=True)
        result = run_validation(self.db)
        self.assertEqual(result["status"], STATUS_BLOCKED)
        self.assertTrue(any(
            b["rule"] == "poolable_effect_without_verbatim_quote"
            for b in result["blockers"]))
        self.assertEqual(
            result["checks"]["effect_quotes"]["unquoted_poolable"], 1)

    def test_unquoted_rejected_row_is_counted_not_blocking(self):
        _seed_source(self.db)
        _seed_raw_effect(self.db, "src1", "txt_src1", "rejected",
                         quote="",
                         rejection_reason="kein Effektwert gelesen",
                         with_se=True)
        result = run_validation(self.db)
        self.assertEqual(result["status"], STATUS_NEEDS_REVIEW)
        self.assertEqual(result["checks"]["effect_quotes"]["unsupported"], 1)
        self.assertTrue(any(w["rule"] == "effects_without_rob"
                            for w in result["warnings"]))

    def test_lost_text_body_blocks(self):
        _seed_source(self.db)
        _seed_raw_effect(self.db, "src1", "txt_lost", "orphan1",
                         start=5, end=35, quote="needed fewer sick days")
        result = run_validation(self.db)
        self.assertEqual(result["status"], STATUS_BLOCKED)
        self.assertTrue(any(b["rule"] == "poolable_quote_text_missing"
                            for b in result["blockers"]))

    def test_missing_rob_warns_only(self):
        _seed_source(self.db)
        _seed_spanned_effect(self.db, "src1", DOC, "txt_src1")
        result = run_validation(self.db)
        self.assertEqual(result["status"], STATUS_NEEDS_REVIEW)
        self.assertTrue(any(w["rule"] == "effects_without_rob"
                            for w in result["warnings"]))

    def test_double_pass_disputes_counted(self):
        _seed_source(self.db)
        _seed_raw_effect(self.db, "src1", "txt_src1", "d1",
                         quote="", disputed=1)
        _seed_raw_effect(self.db, "src1", "txt_src1", "r1",
                         quote="",
                         rejection_reason="Unbekannter Effekttyp")
        result = run_validation(self.db)
        # Neither row is poolable (disputed / rejected), so neither can
        # hurt a pool: counted, not judged.
        self.assertEqual(result["checks"]["disputed"]["disputed"], 1)
        self.assertEqual(result["checks"]["disputed"]["rejected"], 1)
        self.assertEqual(result["status"], STATUS_NEEDS_REVIEW)


class GateClassificationTest(unittest.TestCase):
    def test_status_order(self):
        self.assertEqual(release_gate_status([{"rule": "x"}], []),
                         STATUS_BLOCKED)
        self.assertEqual(release_gate_status([], [{"rule": "y"}]),
                         STATUS_NEEDS_REVIEW)
        self.assertEqual(release_gate_status([], []),
                         STATUS_MACHINE_VALIDATED)


class ValidationStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="validation_store_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.db_path, self.db = _mk_db(self.tmp)

    def test_verdicts_are_append_only(self):
        first = record_validation(self.db, {
            "status": STATUS_BLOCKED,
            "blockers": [{"rule": "a"}], "warnings": [], "checks": {}})
        second = record_validation(self.db, {
            "status": STATUS_MACHINE_VALIDATED,
            "blockers": [], "warnings": [], "checks": {}})
        latest = self.db.get_latest_validation()
        self.assertEqual(latest["id"], second["id"])
        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(latest["status"], STATUS_MACHINE_VALIDATED)


class ReadOnlyAdapterTest(unittest.TestCase):
    """The CLI path validates a real database without writing to it."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="validation_ro_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_adapter_readonly_verdict(self):
        from research_agent.meta.validation import _ReadOnlyAdapter
        db_path, db = _mk_db(self.tmp, name="real.db")
        _seed_source(db)
        _seed_spanned_effect(db, "src1", DOC, "txt_src1")
        adapter = _ReadOnlyAdapter(db_path)
        result = run_validation(adapter)
        self.assertEqual(result["status"], STATUS_NEEDS_REVIEW)

    def test_adapter_reads_fulltext_files(self):
        # Real databases store bodies in fulltext/<sha>.txt: the adapter
        # must read the file, not only the (empty) row column.
        from research_agent.meta.validation import _ReadOnlyAdapter
        db_path, db = _mk_db(self.tmp, name="files.db")
        db.save_source_text("src1", "fulltext", DOC, origin_url="u")
        text_id = db.get_source_text_for_source("src1")["id"]
        row = db.get_source_text(text_id)
        self.assertTrue(row["path"], msg="file-backed text expected")
        _seed_raw_effect(db, "src1", text_id, "f1", start=5, end=40,
                         quote=DOC[5:40])
        adapter = _ReadOnlyAdapter(db_path)
        result = run_validation(adapter)
        self.assertEqual(result["checks"]["effect_quotes"]["checked"], 1)
        self.assertFalse(any(b["rule"] == "quote_text_missing"
                             for b in result["blockers"]))


if __name__ == "__main__":
    unittest.main()
