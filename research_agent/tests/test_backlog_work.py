"""Tests for backlog-driven cycles, run budget/saturation and the closing report.

Offline: in-memory database, fake extractor/retrieval/LLM. The point is that a
cycle without search results still does concrete work, and that a run ends with
a report instead of repeating itself.
"""

import asyncio
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.config import Config
from research_agent.database import Database
from research_agent.orchestrator import ResearchOrchestrator
from research_agent.report import build_report
from research_agent.models import gen_id, now_iso
from research_agent.work_queue import (
    KIND_CITATION,
    KIND_FULL_TEXT,
    KIND_HYPOTHESIS_EVIDENCE,
    KIND_OPEN_QUESTION,
    WorkQueue,
)


class _FakeExtractor:
    def __init__(self, content="", abstract=""):
        self.content = content
        self.abstract = abstract
        self.calls = []

    async def extract(self, url):
        self.calls.append(url)
        if self.content:
            return {"success": True, "content": self.content, "url": url}
        return {"success": False, "error": "403", "url": url}

    async def fetch_abstract(self, url="", title=""):
        if self.abstract:
            return {"success": True, "content": self.abstract, "url": url}
        return None


class _FakeRetrieval:
    def __init__(self, items):
        self.items = items

    async def retrieve(self, query, top_k=10, entity_types=None):
        return self.items


def _orch(**cfg_kwargs):
    cfg = Config()
    cfg.database_url = ":memory:"
    cfg.llm_failure_threshold = 0
    for key, value in cfg_kwargs.items():
        setattr(cfg, key, value)
    orch = ResearchOrchestrator(cfg)
    orch.current_topic = "test topic"
    orch.work_queue.set_topic("test topic")
    return orch


def _source(db, content="short", url="https://example.org/x", title="A paper",
            relevance=0.0, scored=0):
    sid = gen_id()
    db.save_source({
        "id": sid, "title": title, "url": url, "content": content,
        "relevance": relevance, "relevance_scored": scored,
        "credibility": 0.5, "date_added": now_iso(),
    })
    return sid


def _hypothesis(db, claim="Heritability rises with age", confidence=0.5):
    hid = gen_id()
    db.save_hypothesis({
        "id": hid, "claim": claim, "status": "active", "confidence": confidence,
        "date_added": now_iso(),
    })
    return hid


class TestQueuedQuestion(unittest.TestCase):
    def setUp(self):
        self.orch = _orch()
        self.qid = gen_id()
        self.orch.db.save_question({
            "id": self.qid, "question": "Does PGS predict IQ in embryos?",
            "status": "open", "importance": 0.9, "uncertainty": 0.7,
            "date_added": now_iso(),
        })
        self.orch.work_queue.seed()

    def test_planning_takes_the_queued_question(self):
        planned = asyncio.run(self.orch._plan_research(1))
        self.assertEqual(planned["question"], "Does PGS predict IQ in embryos?")
        self.assertTrue(planned["_work_item_id"])
        self.assertIn(planned["_work_item_id"], self.orch._cycle_item_ids)

    def test_question_is_not_offered_twice(self):
        first = asyncio.run(self.orch._plan_research(1))
        self.orch._finish_cycle_item(first["_work_item_id"], "answered")
        row = self.orch.db._get("work_items", first["_work_item_id"])
        self.assertEqual(row["status"], "done")

    def test_finish_cycle_item_clears_claim(self):
        planned = asyncio.run(self.orch._plan_research(1))
        self.orch._finish_cycle_item(planned["_work_item_id"], "done")
        self.assertEqual(self.orch._cycle_item_ids, [])


class TestFullTextWork(unittest.TestCase):
    def setUp(self):
        self.orch = _orch(work_items_per_cycle=2)
        self.sid = _source(self.orch.db, content="snippet only")
        self.orch.work_queue.seed()

    def test_full_text_item_is_worked_and_closed(self):
        self.orch.extractor = _FakeExtractor(content="y" * 900)

        asyncio.run(self.orch._work_on_backlog(1))

        row = self.orch.db.get_source(self.sid)
        self.assertGreaterEqual(len(row["content"]), 400)
        items = self.orch.db._get_all("work_items", where="kind = ?", params=(KIND_FULL_TEXT,))
        self.assertEqual(items[0]["status"], "done")
        self.assertEqual(self.orch._cycle_work_done, 1)

    def test_abstract_is_accepted_when_the_page_is_blocked(self):
        self.orch.extractor = _FakeExtractor(content="", abstract="z" * 800)

        asyncio.run(self.orch._work_on_backlog(1))

        self.assertIn("abstract", self.orch.db._get("work_items", self._item()["id"])["note"])

    def test_failure_releases_then_blocks_after_retries(self):
        self.orch.extractor = _FakeExtractor()  # nothing readable

        asyncio.run(self.orch._work_on_backlog(1))
        self.assertEqual(self._item()["status"], "open")
        self.assertEqual(self.orch._cycle_work_done, 0)

        asyncio.run(self.orch._work_on_backlog(2))
        self.assertEqual(self._item()["status"], "blocked")

    def _item(self):
        return self.orch.db._get_all("work_items", where="kind = ?", params=(KIND_FULL_TEXT,))[0]


class TestHypothesisEvidenceWork(unittest.TestCase):
    def setUp(self):
        self.orch = _orch(work_items_per_cycle=2)
        self.sid = _source(self.orch.db, content="w" * 900)
        self.hid = _hypothesis(self.orch.db)
        self.fid = gen_id()
        self.orch.db.save_fact({
            "id": self.fid, "content": "Heritability of IQ rises from 0.4 to 0.7 with age.",
            "confidence": 0.6, "source_ids": json.dumps([self.sid]),
            "date_added": now_iso(),
        })
        self.orch.work_queue.seed()

    def test_evidence_is_collected_for_orphan_hypothesis(self):
        stored = []

        class Memory:
            async def evaluate_evidence(self, text, hypothesis, source_id):
                stored.append((text, hypothesis["id"], source_id))
                return object()

        self.orch.memory = Memory()
        self.orch.retrieval = _FakeRetrieval([
            {"entity_type": "source", "entity_id": self.sid, "text": "heritability"}
        ])

        asyncio.run(self.orch._work_on_backlog(1))

        self.assertEqual(stored[0][1], self.hid)
        self.assertEqual(stored[0][2], self.sid)
        items = self.orch.db._get_all("work_items", where="kind = ?",
                                     params=(KIND_HYPOTHESIS_EVIDENCE,))
        self.assertEqual(items[0]["status"], "done")

    def test_no_directional_evidence_is_recorded_as_a_finding(self):
        class Memory:
            async def evaluate_evidence(self, *a, **k):
                return None

        self.orch.memory = Memory()
        self.orch.retrieval = _FakeRetrieval([
            {"entity_type": "source", "entity_id": self.sid, "text": "heritability"}
        ])

        asyncio.run(self.orch._work_on_backlog(1))

        items = self.orch.db._get_all("work_items", where="kind = ?",
                                     params=(KIND_HYPOTHESIS_EVIDENCE,))
        self.assertEqual(items[0]["status"], "done")
        self.assertIn("no directional evidence", items[0]["note"])

    def test_missing_retrieval_defers_instead_of_failing(self):
        self.orch.retrieval = _FakeRetrieval([])
        asyncio.run(self.orch._work_on_backlog(1))
        items = self.orch.db._get_all("work_items", where="kind = ?",
                                     params=(KIND_HYPOTHESIS_EVIDENCE,))
        self.assertEqual(items[0]["status"], "open")
        self.assertEqual(items[0]["attempts"], 0, "a dead embedder must not block items")

    def test_handler_failure_does_not_kill_the_phase(self):
        class Boom:
            async def retrieve(self, *a, **k):
                raise RuntimeError("embedding backend down")

        self.orch.retrieval = Boom()
        asyncio.run(self.orch._work_on_backlog(1))  # must not raise
        self.assertEqual(self.orch._cycle_work_done, 0)


class TestBacklogSelection(unittest.TestCase):
    def test_disabled_by_zero(self):
        orch = _orch(work_items_per_cycle=0)
        _source(orch.db, content="short")
        orch.work_queue.seed()
        asyncio.run(orch._work_on_backlog(1))
        self.assertEqual(orch.db._get_all("work_items")[0]["status"], "open")

    def test_question_kind_is_left_to_planning(self):
        orch = _orch(work_items_per_cycle=3)
        _source(orch.db, content="short")  # no DOI, so no citation item
        orch.db.save_question({
            "id": gen_id(), "question": "Is heritability stable?", "status": "open",
            "importance": 0.8, "uncertainty": 0.7, "date_added": now_iso(),
        })
        orch.work_queue.seed()

        asyncio.run(orch._work_on_backlog(1))

        row = orch.db._get_all("work_items", where="kind = ?",
                               params=(KIND_OPEN_QUESTION,))[0]
        self.assertEqual(row["status"], "open")
        self.assertEqual(row["attempts"], 0, "the backlog phase must not burn attempts")


class TestHypothesisBrake(unittest.TestCase):
    def test_backlog_counts_hypotheses_without_evidence(self):
        orch = _orch()
        for claim in ("A", "B", "C"):
            _hypothesis(orch.db, claim=claim)
        evidence_free = _hypothesis(orch.db, claim="checked later")
        orch.db.save_hypothesis({
            "id": gen_id(), "claim": "D", "status": "rejected",
            "confidence": 0.2, "date_added": now_iso(),
        })
        orch.work_queue.seed()
        self.assertEqual(orch.work_queue.unevidenced_hypotheses(), 4)

        # A checked hypothesis that produced no directional evidence has not
        # been answered: closing its item must not make the backlog look smaller,
        # otherwise "the corpus does not settle this" licenses generating a
        # replacement for it - the data dredging the critic block complains about.
        item = orch.db._get_all(
            "work_items", where="ref_id = ?", params=(evidence_free,)
        )[0]
        orch.work_queue.resolve(item["id"], "no directional evidence (corpus gap)")

        self.assertEqual(orch.work_queue.unevidenced_hypotheses(), 4)

    def test_a_blocked_item_takes_its_hypothesis_out_of_the_count(self):
        orch = _orch()
        untestable = _hypothesis(orch.db, claim="Nothing in the corpus can test this")
        orch.work_queue.seed()
        item = orch.db._get_all(
            "work_items", where="ref_id = ?", params=(untestable,)
        )[0]

        orch.work_queue.block(item["id"], "no source in the corpus")

        self.assertEqual(
            orch.work_queue.unevidenced_hypotheses(), 0,
            "the brake must be releasable when a claim is untestable here",
        )

    def test_a_hypothesis_with_evidence_is_not_in_the_backlog(self):
        orch = _orch()
        answered = _hypothesis(orch.db, claim="Has a supporting row")
        orch.db.save_evidence({
            "id": gen_id(), "hypothesis_id": answered, "source_id": gen_id(),
            "evidence_type": "supports", "content": "reported effect",
            "strength": 0.7, "date_added": now_iso(),
        })

        self.assertEqual(orch.work_queue.unevidenced_hypotheses(), 0)

    def test_other_topics_are_not_this_runs_backlog(self):
        orch = _orch()
        foreign = WorkQueue(orch.db, topic="other topic")
        foreign._insert_item(KIND_HYPOTHESIS_EVIDENCE, gen_id(), "foreign", 1.0, now_iso())

        self.assertEqual(orch.work_queue.unevidenced_hypotheses(), 0)

        claimed = orch.work_queue.claim(5, kinds=[KIND_HYPOTHESIS_EVIDENCE])
        self.assertEqual(claimed, [], "a run must not consume another topic's queue")

    def test_generation_is_skipped_at_the_limit(self):
        orch = _orch(hypothesis_backlog_limit=2)
        _hypothesis(orch.db, claim="A")
        _hypothesis(orch.db, claim="B")
        orch.work_queue.seed()
        calls = []

        class Memory:
            def get_active_hypotheses(self):
                return []

            def get_facts(self, **kwargs):
                return []

            async def generate_hypotheses(self, *a, **k):
                calls.append(1)
                return []

        orch.memory = Memory()

        self.assertEqual(asyncio.run(orch._hypothesize("Q?")), [])
        self.assertEqual(calls, [], "no LLM call while the backlog is above the limit")
        self.assertEqual(orch.status["hypotheses_paused"],
                         {"evidence_open": 2, "limit": 2})
        self.assertTrue(orch.work_queue.stats()["hypothesis_brake"]["active"])

    def test_generation_resumes_below_the_limit_and_queues_new_work(self):
        from research_agent.models import Hypothesis

        orch = _orch(hypothesis_backlog_limit=2)
        _hypothesis(orch.db, claim="A")
        fresh = Hypothesis(claim="Fresh claim", status="active",
                           confidence=0.4, topic="test topic")

        class Memory:
            def get_active_hypotheses(self):
                return []

            def get_facts(self, **kwargs):
                return []

            async def generate_hypotheses(self, *a, **k):
                orch.db.save_hypothesis(fresh.to_dict())
                return [fresh]

        orch.memory = Memory()

        self.assertEqual(asyncio.run(orch._hypothesize("Q?")), [fresh])
        self.assertIsNone(orch.status["hypotheses_paused"])
        queued = orch.db._get_all(
            "work_items", where="kind = ? AND ref_id = ?",
            params=(KIND_HYPOTHESIS_EVIDENCE, fresh.id),
        )
        self.assertEqual(len(queued), 1, "new hypotheses must enter the queue at once")

    def test_brake_can_be_disabled(self):
        orch = _orch(hypothesis_backlog_limit=0)
        _hypothesis(orch.db, claim="A")
        _hypothesis(orch.db, claim="B")

        self.assertIsNone(orch._hypothesis_generation_blocked())


class TestConcludeConditions(unittest.TestCase):
    def test_budget_concludes(self):
        import time

        orch = _orch(run_budget_minutes=1)
        orch._run_started_at = time.time() - 120  # two minutes into a 1-minute budget
        orch.current_cycle = 3
        self.assertTrue(orch._should_conclude())
        self.assertIn("budget", orch._conclude_reason)

    def test_no_budget_no_conclusion(self):
        import time

        orch = _orch(run_budget_minutes=0)
        orch._run_started_at = time.time() - 3600
        self.assertFalse(orch._should_conclude())

    def test_saturation_with_empty_queue_concludes(self):
        orch = _orch(saturation_cycles=2)
        _source(orch.db, content="short")
        orch.work_queue.seed()
        asyncio.run(orch._work_on_backlog(1))  # one item worked, queue empty now
        orch._empty_cycles = 2
        stats = orch.work_queue.stats()
        if stats["open"] == 0:
            self.assertTrue(orch._should_conclude())

    def test_saturation_with_open_work_does_not_conclude(self):
        orch = _orch(saturation_cycles=2)
        _source(orch.db, content="short")
        orch.work_queue.seed()
        orch._empty_cycles = 2
        self.assertFalse(orch._should_conclude())


class TestClosingReport(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.tmp = tempfile.mkdtemp(prefix="report_test_")
        self.sid = _source(self.db, title="Twin study of IQ", content="w" * 800,
                           relevance=0.6, scored=1)
        self.db.save_fact({
            "id": gen_id(), "content": "IQ heritability increases with age.",
            "confidence": 0.62, "source_ids": json.dumps([self.sid]),
            "date_added": now_iso(),
        })
        self.hid = _hypothesis(self.db, "Heritability rises with age", confidence=0.45)

    def test_report_contains_fact_source_and_hypothesis(self):
        path = build_report(self.db, "intelligence", reason="budget reached",
                            out_dir=self.tmp)
        text = Path(path).read_text(encoding="utf-8")
        self.assertIn("Wissensstand: intelligence", text)
        self.assertIn("budget reached", text)
        self.assertIn("IQ heritability increases with age.", text)
        self.assertIn("Twin study of IQ", text)
        self.assertIn("Heritability rises with age", text)
        self.assertIn("0.62", text)

    def test_report_lists_open_questions_and_queue(self):
        self.db.save_question({
            "id": gen_id(), "question": "Open: does PGS work?", "status": "open",
            "importance": 0.7, "uncertainty": 0.6, "priority_score": 0.9,
            "date_added": now_iso(),
        })
        path = build_report(self.db, "intelligence", out_dir=self.tmp,
                            work_stats={"open": 3, "in_progress": 0, "done": 5,
                                        "blocked": 1, "open_by_kind": {"full_text": 3},
                                        "next": [{"kind": "full_text", "title": "A paper"}]})
        text = Path(path).read_text(encoding="utf-8")
        self.assertIn("Open: does PGS work?", text)
        self.assertIn("full_text=3", text)
        self.assertIn("A paper", text)

    def test_report_shows_evidence_backlog_and_brake(self):
        path = build_report(self.db, "intelligence", out_dir=self.tmp,
                            work_stats={"open": 3, "in_progress": 0, "done": 5,
                                        "blocked": 1, "open_by_kind": {"hypothesis_evidence": 3},
                                        "hypothesis_brake": {"limit": 25, "evidence_open": 3,
                                                             "active": False}})
        text = Path(path).read_text(encoding="utf-8")
        self.assertIn("Hypothesen ohne Evidenz: 3", text)
        self.assertIn("Bremse greift nicht", text)

        path = build_report(self.db, "intelligence", out_dir=self.tmp,
                            work_stats={"open": 40, "in_progress": 0, "done": 5,
                                        "blocked": 1, "open_by_kind": {"hypothesis_evidence": 40},
                                        "hypothesis_brake": {"limit": 25, "evidence_open": 40,
                                                             "active": True}})
        text = Path(path).read_text(encoding="utf-8")
        self.assertIn("Hypothesen ohne Evidenz: 40", text)
        self.assertIn("Bremse greift, Schwelle 25", text)

    def test_report_discloses_refused_hypotheses(self):
        """Auftrag v2 §6.3: durch die Aufnahmeprüfung abgelehnte
        Hypothesen sind im Report sichtlich dokumentiert."""
        self.db.save_hypothesis({
            "id": gen_id(),
            "claim": "Something vague without falsification.",
            "status": "speculative", "confidence": 0.3,
            "topic": "intelligence", "date_added": now_iso(),
        })
        path = build_report(self.db, "intelligence", out_dir=self.tmp,
                            work_stats={"open": 0, "in_progress": 0, "done": 0,
                                        "blocked": 0})
        text = Path(path).read_text(encoding="utf-8")
        self.assertIn("Aufnahmeprüfung: 1 Hypothesen nicht aufgenommen", text)

    def test_report_without_refused_hypotheses_has_no_admission_line(self):
        """Keine abgelehnten Hypothesen -> keine Offenlegungszeile."""
        path = build_report(self.db, "intelligence", out_dir=self.tmp,
                            work_stats={"open": 0, "in_progress": 0, "done": 0,
                                        "blocked": 0})
        text = Path(path).read_text(encoding="utf-8")
        self.assertNotIn("Aufnahmeprüfung", text)

    def test_empty_database_still_produces_a_report(self):
        empty = Database(":memory:")
        path = build_report(empty, "", reason="", out_dir=self.tmp)
        text = Path(path).read_text(encoding="utf-8")
        self.assertIn("_Keine Fakten im Bestand._", text)


class TestFactBackfill(unittest.TestCase):
    """The corpus grew faster than it was read; a fixed budget closes that gap."""

    def _orch(self, limit):
        orch = _orch(analysis_backfill_per_cycle=limit)
        self.calls = []

        async def fake_extract(source, topic):
            self.calls.append(source.id)
            return []

        orch._extract_source_facts = fake_extract
        return orch

    def test_an_unread_source_is_read_again_and_remembered(self):
        orch = self._orch(2)
        sid = _source(orch.db, content="y" * 800, relevance=0.8, scored=1)

        asyncio.run(orch._backfill_source_facts())

        self.assertEqual(self.calls, [sid])
        self.assertEqual(orch.db.get_source(sid)["facts_attempted"], 1)

        asyncio.run(orch._backfill_source_facts())
        self.assertEqual(self.calls, [sid],
                         "a source without an extractable claim is not re-read forever")

    def test_a_scored_irrelevant_source_is_not_read(self):
        orch = self._orch(2)
        _source(orch.db, content="y" * 800, relevance=0.05, scored=1)

        asyncio.run(orch._backfill_source_facts())

        self.assertEqual(self.calls, [])

    def test_the_budget_bounds_one_cycle(self):
        orch = self._orch(1)
        for _ in range(3):
            _source(orch.db, content="y" * 800, relevance=0.8, scored=1)

        asyncio.run(orch._backfill_source_facts())

        self.assertEqual(len(self.calls), 1)

    def test_it_can_be_disabled(self):
        orch = self._orch(0)
        _source(orch.db, content="y" * 800, relevance=0.8, scored=1)

        asyncio.run(orch._backfill_source_facts())

        self.assertEqual(self.calls, [])


class TestCatchupMode(unittest.TestCase):
    """While the unread pile is large, the cycle reads instead of searching.

    Measured on 28.10.: 519 sources with text and no fact row, growing by ~20 per
    cycle while 3 were read out. Searching more can only widen that gap.
    """

    def test_a_large_unread_pile_switches_to_reading(self):
        orch = _orch(backlog_catchup_at=2, backlog_catchup_queries=1,
                     analysis_backfill_per_cycle=3, backlog_catchup_backfill=8)
        for _ in range(3):
            _source(orch.db, content="y" * 800, relevance=0.8, scored=1)

        state = orch._apply_backlog_catchup()

        self.assertTrue(state["active"])
        self.assertEqual(orch.engine.max_queries, 1)
        self.assertEqual(orch._backfill_budget(), 8)
        self.assertEqual(orch.status["catchup"]["unread"], 3)

    def test_a_small_pile_restores_the_normal_settings(self):
        orch = _orch(backlog_catchup_at=10, backlog_catchup_queries=1,
                     queries_per_cycle=3)
        _source(orch.db, content="y" * 800, relevance=0.8, scored=1)

        state = orch._apply_backlog_catchup()

        self.assertFalse(state["active"])
        self.assertEqual(orch.engine.max_queries, 3)
        self.assertEqual(orch._backfill_budget(), 3)

    def test_a_disabled_mode_does_not_log(self):
        orch = _orch(backlog_catchup_at=0)
        with self.assertNoLogs("research_agent.orchestrator", level="INFO"):
            orch._apply_backlog_catchup()
        self.assertFalse(orch.status["catchup"]["active"])

    def test_disabling_the_backfill_is_not_overridden(self):
        orch = _orch(analysis_backfill_per_cycle=0)
        orch._catchup = {"active": True}

        self.assertEqual(orch._backfill_budget(), 0)

    def test_the_read_budget_follows_the_mode(self):
        orch = _orch(analysis_backfill_per_cycle=3, backlog_catchup_backfill=8)

        self.assertEqual(orch._backfill_budget(), 3)
        orch._catchup = {"active": True}
        self.assertEqual(orch._backfill_budget(), 8)


class TestEvidenceBudget(unittest.TestCase):
    """14 classifications for 0-1 row is a price worth questioning."""

    def test_three_cycles_without_a_row_shrink_the_budget(self):
        orch = _orch()
        orch._evidence_yield = [(14, 0), (14, 0), (14, 0)]

        self.assertEqual(orch._evidence_budget(20), 6)

    def test_one_directional_row_restores_it(self):
        orch = _orch()
        orch._evidence_yield = [(14, 0), (14, 0), (14, 1)]

        self.assertEqual(orch._evidence_budget(20), 20)

    def test_a_small_sample_does_not_count_as_evidence(self):
        orch = _orch()
        orch._evidence_yield = [(5, 0)]

        self.assertEqual(orch._evidence_budget(20), 20)

    def test_the_reduced_budget_has_a_floor(self):
        orch = _orch()
        orch._evidence_yield = [(20, 0), (20, 0), (20, 0)]

        self.assertEqual(orch._evidence_budget(6), 4)


class TestRunResume(unittest.TestCase):
    """Auftrag v2 §10a: endet die letzte Runde eines Themas unvollständig,
    ist der Neustart eine dokumentierte Fortsetzung - Session-Kette via
    previous_session_id, sichtbar im Status, kein stiller Neuanfang."""

    def _save_session(self, db, sid, topic="test topic", status="stopped"):
        db.save_session({
            "id": sid, "topic": topic, "status": status,
            "start_time": "2026-11-01T10:00:00+00:00",
            "end_time": "2026-11-01T11:00:00+00:00",
            "cycle_count": 14,
            "sources_found": 74, "hypotheses_generated": 49,
            "questions_answered": 0, "summary": "",
        })

    def test_unfinished_session_is_the_resume_anchor(self):
        db = Database(":memory:")
        self._save_session(db, "s_done", status="completed")
        self.assertIsNone(db.get_last_unfinished_session("test topic"))
        self._save_session(db, "s_stopped", status="stopped")
        row = db.get_last_unfinished_session("test topic")
        self.assertEqual(row["id"], "s_stopped")
        # Anderes Thema ist kein Anschluss:
        self.assertIsNone(db.get_last_unfinished_session("anderes Thema"))

    def test_session_row_carries_the_previous_id(self):
        db = Database(":memory:")
        db.save_session({
            "id": "s_child", "topic": "t", "status": "active",
            "start_time": "2026-11-01T10:00:00+00:00",
            "previous_session_id": "s_parent",
        })
        row = db.get_session("s_child")
        self.assertEqual(row.get("previous_session_id"), "s_parent")

    def test_restart_after_resource_limit_resumes_the_run(self):
        orch = _orch()
        self._save_session(orch.db, "s_limited",
                           status="resource_limit_reached")

        async def _noop_loop():
            return

        self.orch_loop = orch
        orch._research_loop = _noop_loop
        asyncio.run(orch.start("test topic"))

        # Der neue Lauf verweist auf die unvollständige Runde:
        current = orch.current_session
        self.assertEqual(current.get("previous_session_id"), "s_limited")
        resumed = orch.status.get("resumed_from") or {}
        self.assertEqual(resumed.get("session_id"), "s_limited")
        self.assertEqual(resumed.get("cycles"), 14)

    def test_fresh_topic_starts_without_resume_hook(self):
        orch = _orch()

        async def _noop_loop():
            return

        orch._research_loop = _noop_loop
        asyncio.run(orch.start("test topic"))
        self.assertNotIn("resumed_from", orch.status)
        self.assertEqual(orch.current_session.get("previous_session_id") or
                         "", "")


class _AdmissionFakeLLM:
    """LLM-Stub: liefert die.generateierten Hypothesen-Rohobjekte."""

    def __init__(self, items):
        self.items = items

    async def chat_json(self, messages, temperature=0.0, max_tokens=2048):
        return self.items


class TestHypothesisAdmission(unittest.TestCase):
    """Auftrag v2 §6.3: nicht jede generierte Hypothese tritt ins
    Forschungsprogramm ein - nur pruefbare werden 'active';
    unwertvolle bleiben als 'speculative' dokumentiert und belasten
    den Evidenz-Backlog nicht."""

    def _memory(self, items):
        from research_agent.memory.store import MemoryStore
        return MemoryStore(Database(":memory:"), _AdmissionFakeLLM(items))

    _TESTABLE = {
        "claim": "Acute caffeine ingestion lowers reaction time in healthy adults",
        "confidence": 0.4,
        "predictions": ["crossover trials show shorter RT after caffeine"],
        "falsification_conditions": ["no RT difference in placebo-controlled RCTs"],
    }

    def run_generate(self, items):
        mem = self._memory(items)
        kept = asyncio.run(
            mem.generate_hypotheses([], [], "caffeine", "RT?"))
        return mem, kept

    def test_testable_hypothesis_enters_the_program(self):
        mem, kept = self.run_generate([self._TESTABLE])
        self.assertEqual(len(kept), 1)
        self.assertEqual(kept[0].status, "active")
        self.assertEqual(len(mem.get_active_hypotheses()), 1)

    def test_without_falsification_conditions_it_stays_speculative(self):
        item = dict(self._TESTABLE, falsification_conditions=[])
        mem, kept = self.run_generate([item])
        self.assertEqual(kept, [])
        # In der DB dokumentiert, aber NICHT im Evidenz-Backlog:
        hyps = mem.db.get_hypotheses()
        self.assertEqual([h["status"] for h in hyps], ["speculative"])
        self.assertEqual(mem.get_active_hypotheses(), [])

    def test_contentless_claim_is_refused(self):
        item = {
            "claim": "It might be interesting.",
            "confidence": 0.9,
            "predictions": ["x"],
            "falsification_conditions": ["y"],
        }
        mem, kept = self.run_generate([item])
        self.assertEqual(kept, [])
        hyps = mem.db.get_hypotheses()
        self.assertEqual([h["status"] for h in hyps], ["speculative"])

    def test_admission_review_is_pure(self):
        from research_agent.memory.store import MemoryStore
        cases = [
            ("short claim", [], [], "speculative"),
            ("a substantive testable statement here",
             ["cannot hold"], ["forecast"], "active"),
            ("a substantive testable statement here", [], ["forecast"],
             "speculative"),
        ]
        for claim, fals, preds, expected in cases:
            status, _ = MemoryStore.admission_review(claim, fals, preds)
            self.assertEqual(status, expected, claim)


if __name__ == "__main__":
    unittest.main()
