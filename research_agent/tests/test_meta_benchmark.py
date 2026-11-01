"""Deterministic tests for the meta-benchmark harness (order §12)."""

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

from research_agent.evals.meta_benchmark import (
    evaluate_case, is_holdout, load_reference_cases, run_benchmark,
    validate_reference_case, _passes_thresholds, DEFAULT_THRESHOLDS)

_SCHEMA = """
CREATE TABLE sources (
    id TEXT PRIMARY KEY, title TEXT DEFAULT '', url TEXT DEFAULT '',
    content_hash TEXT DEFAULT '', relevance REAL DEFAULT 0.0,
    relevance_scored INTEGER DEFAULT 0, doi TEXT DEFAULT '',
    evaluated INTEGER DEFAULT 0);
CREATE TABLE screening (
    id TEXT PRIMARY KEY, topic TEXT DEFAULT '', source_id TEXT DEFAULT '',
    decision TEXT DEFAULT '', reason TEXT DEFAULT '', decided_by TEXT DEFAULT '',
    created_at TEXT DEFAULT '');
CREATE TABLE source_texts (
    id TEXT PRIMARY KEY, source_id TEXT DEFAULT '', kind TEXT DEFAULT 'html',
    origin_url TEXT DEFAULT '', chars INTEGER DEFAULT 0, pages INTEGER DEFAULT 0,
    path TEXT DEFAULT '', text TEXT DEFAULT '', sections TEXT DEFAULT '[]',
    page_offsets TEXT DEFAULT '[]', created_at TEXT DEFAULT '');
CREATE TABLE study_effects (
    id TEXT PRIMARY KEY, source_id TEXT DEFAULT '', hypothesis_id TEXT DEFAULT '',
    outcome TEXT DEFAULT '', outcome_key TEXT DEFAULT '', comparison TEXT DEFAULT '',
    effect_type TEXT DEFAULT '', effect REAL, se REAL, ci_low REAL, ci_high REAL,
    ci_level REAL DEFAULT 0.95, n INTEGER, events INTEGER, design TEXT DEFAULT '',
    population TEXT DEFAULT '', moderators TEXT DEFAULT '{}', direction TEXT DEFAULT '',
    unit TEXT DEFAULT '', quote TEXT DEFAULT '', quote_start INTEGER DEFAULT -1,
    quote_end INTEGER DEFAULT -1, source_text_id TEXT DEFAULT '', section TEXT DEFAULT '',
    page INTEGER DEFAULT -1, extractor TEXT DEFAULT '', extraction_pass INTEGER DEFAULT 1,
    disputed INTEGER DEFAULT 0, rejection_reason TEXT DEFAULT '',
    created_at TEXT DEFAULT '');
"""


class BenchmarkHarnessTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.tmp.name
        self.tmp.close()
        conn = sqlite3.connect(self.db_path)
        conn.executescript(_SCHEMA)
        # a source matching a gold-include study, and one extra included that
        # is not gold-relevant (precision cost) plus one excluded gold-relevant
        conn.execute("INSERT INTO sources (id, doi) VALUES ('x1', '10.1/p1')")
        conn.execute("INSERT INTO sources (id, doi) VALUES ('x3', '10.3/p3')")
        # gold include matched correctly + a wrong include to test precision
        conn.execute(
            "INSERT INTO screening (id, source_id, decision) VALUES "
            "('sc1','x1','include')")
        conn.execute(
            "INSERT INTO screening (id, source_id, decision) VALUES "
            "('sc3','x3','include')")
        # a fulltext body for x1
        conn.execute("INSERT INTO source_texts (id, source_id, chars)"
                     " VALUES ('t1','x1', 3000)")
        # exact effect row + a wrong-direction row for a second gold study
        conn.execute(
            "INSERT INTO study_effects (id, source_id, outcome, effect, "
            "quote_start, disputed, rejection_reason) VALUES "
            "('e1','x1','kognition', 0.42, 5, 0, '')")
        conn.execute(
            "INSERT INTO study_effects (id, source_id, outcome, effect, "
            "quote_start, disputed, rejection_reason) VALUES "
            "('e2','x3','kognition', +0.9, 4, 0, '')")
        conn.commit()
        conn.close()

        self.ref_case = {
            "case_id": "case_dev_fixture_001",
            "topic": "synthetic",
            "studies": [
                {"study_id": "s1", "doi": "10.1/p1", "gold": "include",
                 "available": True,
                 "extracted_effects": [{"outcome": "kognition", "effect": 0.42,
                                        "direction_gold": "positive"}]},
                {"study_id": "s2", "doi": "10.2/p2", "gold": "include",
                 "available": False, "extracted_effects": []},
                {"study_id": "s3", "doi": "10.3/p3", "gold": "outside",
                 "extracted_effects": []},
            ],
            "thresholds": DEFAULT_THRESHOLDS,
        }
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(self.ref_case, f)
            self.ref_path = f.name

    def tearDown(self):
        os.unlink(self.db_path)
        os.unlink(self.ref_path)

    # ------------------------------------------------ validation
    def test_validator_catches_missing_fields(self):
        errs = validate_reference_case({"case_id": "x", "topic": "t"})
        self.assertTrue(any("studies" in e for e in errs))
        bad_case = {"case_id": "x", "topic": "t",
                    "studies": [{"study_id": "s", "doi": "10.9/x", "gold": "nope"}]}
        errs = validate_reference_case(bad_case)
        self.assertTrue(any("gold must be" in e for e in errs))

    def test_loader_rejects_invalid_cases(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"case_id": "bad"}, f)
            p = f.name
        try:
            cases, rejected = load_reference_cases([p])
            self.assertEqual(cases, [])
            self.assertTrue(rejected and "missing case field" in rejected[0])
        finally:
            os.unlink(p)

    # ------------------------------------------------ holdout determinism
    def test_holdout_split_is_deterministic(self):
        self.assertEqual(is_holdout("case_a"), is_holdout("case_a"))
        # Stable split; over ids 0000..2999 at least one lands in the band,
        # and the membership never changes on a second call.
        hold = [f"case_{i:04d}" for i in range(3000) if is_holdout(f"case_{i:04d}")]
        self.assertTrue(hold)
        self.assertTrue(is_holdout(hold[0]))

    # ------------------------------------------------ metrics
    def test_screening_recall_precision_fulltext(self):
        res = evaluate_case(self.ref_case, self.db_path)
        s = res["screening"]
        # gold include studies are s1 and s2; the DB only ever has s1 ->
        # s2 missing is an honest miss: recall = 1/2. The order definition
        # (§12) counts this as "agent did not find the relevant study".
        self.assertEqual(s["recall"], 0.5)
        # precision lowered by the wrongly included x3 (gold "outside")
        self.assertTrue(s["precision"] < 1.0)
        f = res["fulltext_retrieval"]
        # available gold-included studies: s1 only, and it has fulltext
        self.assertEqual(f["rate"], 1.0)
        self.assertEqual(f["retrieved"], 1)

    def test_extraction_exact_and_provenance(self):
        res = evaluate_case(self.ref_case, self.db_path)
        e = res["extraction"]
        # one gold effect check (s1) matches exactly and has provenance
        self.assertEqual(e["extraction_checks"], 1)
        self.assertEqual(e["exact"], 1.0)
        self.assertEqual(e["provenance"], 1.0)

    def test_critical_error_counts_when_direction_flips(self):
        # make x3 gold-relevant with flipped direction; direction gold negative
        case: Dict[str, Any] = json.loads(json.dumps(self.ref_case))
        case["studies"][2]["gold"] = "include"
        case["studies"][2]["extracted_effects"] = [
            {"outcome": "kognition", "effect": -1.0, "direction_gold": "negative"}]
        res = evaluate_case(case, self.db_path)
        # the DB rows for x3 carry effect = +0.9 -> opposite sign: critical
        crit = res["extraction"]["critical_errors"]
        self.assertTrue(any("wrong direction" in c for c in crit))

    def test_threshold_blockers(self):
        bad = {"thresholds": DEFAULT_THRESHOLDS,
               "screening": {"recall": 0.5},
               "extraction": {"critical_error_count": 2}}
        ok, blockers = _passes_thresholds(bad)
        self.assertFalse(ok)
        self.assertTrue(any("screening_recall" in b for b in blockers))
        self.assertTrue(any("critical_errors" in b for b in blockers))

    def test_run_benchmark_partitioning(self):
        res = run_benchmark([self.ref_path], self.db_path)
        self.assertEqual(res["cases_loaded"], 1)
        self.assertIn("dev", res)
        self.assertIn("holdout", res)
        part = ("holdout" if is_holdout(self.ref_case["case_id"]) else "dev")
        bucket = res[part]
        self.assertEqual(bucket["cases"], 1)
        self.assertEqual(bucket["critical_error_total"], 0)


if __name__ == "__main__":
    unittest.main()
