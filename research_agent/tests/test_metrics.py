"""Unit tests for research_agent.metrics (Phase 0, d<Order 01.11.2026).

Deterministic: feed a fixture database with known rows and assert the exact
aggregates. No network, no LLM. The fixture mirrors only the metric-relevant
schema parts; the real schema lives in database.py.
"""

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

from research_agent.metrics import compute_metrics, write_markdown

_SCHEMA = """
CREATE TABLE sources (
    id TEXT PRIMARY KEY, title TEXT DEFAULT '', url TEXT DEFAULT '',
    content_hash TEXT DEFAULT '', relevance REAL DEFAULT 0.0,
    relevance_scored INTEGER DEFAULT 0, relevance_unjudgeable INTEGER DEFAULT 0,
    evaluated INTEGER DEFAULT 0);
CREATE TABLE source_texts (
    id TEXT PRIMARY KEY, source_id TEXT DEFAULT '', kind TEXT DEFAULT 'html',
    origin_url TEXT DEFAULT '', chars INTEGER DEFAULT 0, pages INTEGER DEFAULT 0,
    path TEXT DEFAULT '', text TEXT DEFAULT '', sections TEXT DEFAULT '[]',
    page_offsets TEXT DEFAULT '[]', created_at TEXT DEFAULT '');
CREATE TABLE screening (
    id TEXT PRIMARY KEY, topic TEXT DEFAULT '', source_id TEXT DEFAULT '',
    decision TEXT DEFAULT '', reason TEXT DEFAULT '', decided_by TEXT DEFAULT '',
    created_at TEXT DEFAULT '');
CREATE TABLE hypotheses (
    id TEXT PRIMARY KEY, claim TEXT DEFAULT '', status TEXT DEFAULT 'proposed',
    confidence REAL DEFAULT 0.3);
CREATE TABLE evidence (
    id TEXT PRIMARY KEY, hypothesis_id TEXT DEFAULT '', source_id TEXT DEFAULT '',
    evidence_type TEXT DEFAULT 'supports', content TEXT DEFAULT '',
    strength REAL DEFAULT 0.5);
CREATE TABLE evidence_pairs (
    hypothesis_id TEXT NOT NULL, source_id TEXT NOT NULL,
    verdict TEXT DEFAULT '', reason TEXT DEFAULT '', date_added TEXT DEFAULT '',
    PRIMARY KEY (hypothesis_id, source_id));
CREATE TABLE facts (
    id TEXT PRIMARY KEY, content TEXT DEFAULT '', confidence REAL DEFAULT 0.5,
    source_ids TEXT DEFAULT '[]', date_added TEXT DEFAULT '',
    last_verified TEXT DEFAULT '', topic TEXT DEFAULT '');
CREATE TABLE study_effects (
    id TEXT PRIMARY KEY, source_id TEXT DEFAULT '', outcome_key TEXT DEFAULT '',
    effect REAL, se REAL, disputed INTEGER DEFAULT 0,
    rejection_reason TEXT DEFAULT '', quote_start INTEGER DEFAULT -1,
    source_text_id TEXT DEFAULT '', created_at TEXT DEFAULT '');
CREATE TABLE risk_of_bias (source_id TEXT PRIMARY KEY, design TEXT DEFAULT '');
CREATE TABLE llm_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT DEFAULT '',
    day TEXT DEFAULT '', phase TEXT DEFAULT '', backend TEXT DEFAULT '',
    model TEXT DEFAULT '', prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0, total_tokens INTEGER DEFAULT 0,
    time_ms REAL DEFAULT 0.0, success INTEGER DEFAULT 1);
CREATE TABLE query_stats (
    topic TEXT DEFAULT '', query TEXT DEFAULT '', provider TEXT DEFAULT '',
    attempts INTEGER DEFAULT 0, results INTEGER DEFAULT 0, kept INTEGER DEFAULT 0,
    duplicates INTEGER DEFAULT 0, last_cycle INTEGER DEFAULT 0,
    updated_at TEXT DEFAULT '', PRIMARY KEY (topic, query, provider));
CREATE TABLE research_sessions (
    id TEXT PRIMARY KEY, topic TEXT DEFAULT '', start_time TEXT DEFAULT '',
    end_time TEXT DEFAULT '', cycle_count INTEGER DEFAULT 0);
CREATE TABLE research_questions (
    id TEXT PRIMARY KEY, question TEXT DEFAULT '', status TEXT DEFAULT 'open');
"""


class MetricsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.path = self.tmp.name
        self.tmp.close()
        conn = sqlite3.connect(self.path)
        conn.executescript(_SCHEMA)
        # Sources: 4 rows, 3 unique URLs (one URL duplicated case-insensitive)
        for url, scored, rel in [
            ("https://a.example/1", 1, 0.4),
            ("https://B.example/2", 1, 0.6),
            ("https://b.example/2", 1, 0.6),   # duplicate by lower(url)
            ("", 0, 0.0),
        ]:
            conn.execute(
                "INSERT INTO sources (id, url, relevance_scored, relevance) VALUES (?, ?, ?, ?)",
                (f"s-{url}-{os.getpid()}", url, scored, rel))
        # Full text: two documents for two distinct sources, page offsets on one
        conn.execute(
            "INSERT INTO source_texts (id, source_id, chars, pages, page_offsets)"
            " VALUES ('t1','x1', 3000, 12, '[[0,3],[3,9]]')")
        conn.execute(
            "INSERT INTO source_texts (id, source_id, chars, pages)"
            " VALUES ('t2','x2', 1200, 3)")
        # Screening: 2 include, 1 exclude with reason
        conn.execute(
            "INSERT INTO screening (id, decision, reason) VALUES ('sc1','include','')")
        conn.execute(
            "INSERT INTO screening (id, decision, reason) VALUES ('sc2','include','')")
        conn.execute(
            "INSERT INTO screening (id, decision, reason) VALUES ('sc3','exclude','wrong design')")
        # Effects: a target-matched poolable pair and a rejected reading
        for eid, ok, se in [("e1", "key", 0.1), ("e2", "key", 0.1)]:
            conn.execute(
                "INSERT INTO study_effects (id, outcome_key, effect, se, disputed,"
                " rejection_reason, quote_start, source_text_id)"
                " VALUES (?, ?, -0.4, ?, 0, '', 5, 't1')", (eid, ok, se))
        conn.execute(
            "INSERT INTO study_effects (id, outcome_key, effect, se, disputed,"
            " rejection_reason, quote_start, source_text_id)"
            " VALUES ('e3', '','', NULL, 0, 'unbekannter Effekttyp', -1, '')")
        conn.execute("INSERT INTO risk_of_bias (source_id, design) VALUES ('x1','rct')")
        conn.execute(
            "INSERT INTO llm_usage (phase, total_tokens, success) VALUES ('a', 100, 1)")
        conn.execute(
            "INSERT INTO llm_usage (phase, total_tokens, success) VALUES ('a', 50, 0)")
        conn.execute(
            "INSERT INTO query_stats (topic, query, provider, attempts, results, kept)"
            " VALUES ('t','q','openalex', 3, 5, 2)")
        conn.execute(
            "INSERT INTO research_sessions (id, topic, start_time, end_time, cycle_count)"
            " VALUES ('r1','t','2026-11-01T10:00:00','2026-11-01T11:00:00', 4)")
        conn.commit()
        conn.close()

    def tearDown(self):
        os.unlink(self.path)

    def test_exact_aggregates(self):
        m = compute_metrics(self.path)
        self.assertEqual(m["sources"]["found"], 4)
        # case-insensitive URL dedup: https://B.example/2 == https://b.example/2
        self.assertEqual(m["sources"]["unique_by_url"], 2)
        # row-count metric (not URL-deduped, stated as such in the metric):
        # a=0.4, B=0.6, b=0.6 -> 3
        self.assertEqual(m["sources"]["relevance_ge_025"], 3)
        self.assertEqual(m["fulltext"]["documents"], 2)
        self.assertEqual(m["fulltext"]["sources_with_text"], 2)
        self.assertEqual(m["fulltext"]["sources_with_page_offsets"], 1)
        self.assertEqual(m["screening"]["by_decision"], {"include": 2, "exclude": 1})
        e = m["effects"]
        self.assertEqual(e["rows_total"], 3)
        self.assertEqual(e["rows_target_matched"], 2)
        self.assertEqual(e["rows_rejected"], 1)
        self.assertEqual(e["rejection_reasons"]["unbekannter Effekttyp"], 1)
        self.assertEqual(e["rows_quote_verified"], 2)
        pools = e["pools"]
        self.assertEqual(len(pools), 1)
        self.assertEqual(pools[0]["distinct_sources"], 1)   # one source, two rows
        self.assertFalse(pools[0]["pooled"])               # k < 2
        self.assertEqual(m["risk_of_bias"]["assessments"], 1)
        self.assertEqual(m["llm"]["calls"], 2)
        self.assertEqual(m["llm"]["calls_failed"], 1)
        self.assertEqual(m["search"]["kept_by_provider"], {"openalex": 2})
        self.assertEqual(m["session"]["cycle_count_total"], 4)
        self.assertEqual(m["session"]["duration_seconds"], 3600.0)
        # Markdown is a deterministic reduction of the same numbers
        md = write_markdown(m)
        self.assertIn("Pools: keiner", md)

    def test_json_roundtrip(self):
        m = compute_metrics(self.path)
        loaded = json.loads(json.dumps(m))
        self.assertEqual(loaded["sources"]["found"], m["sources"]["found"])


if __name__ == "__main__":
    unittest.main()
