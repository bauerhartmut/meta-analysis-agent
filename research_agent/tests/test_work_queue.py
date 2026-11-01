"""Tests for the persistent work queue (research_agent/work_queue.py).

All offline: an in-memory database, no LLM, no network. They pin down the two
properties the queue exists for — it is filled from the real backlog, and the
same backlog survives restarts (idempotent seeding, stale claims recovered).
"""

import json
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.work_queue import (
    WorkQueue,
    reports_precision,
    KIND_CITATION,
    KIND_FULL_TEXT,
    KIND_HYPOTHESIS_EVIDENCE,
    KIND_OPEN_QUESTION,
    KIND_SIMULATION,
    KIND_EFFECT_EXTRACTION,
    MAX_ATTEMPTS,
    _priority,
)
from research_agent.models import gen_id, now_iso


def _source(db, **kw):
    row = {
        "id": gen_id(),
        "title": kw.get("title", "A source"),
        "url": kw.get("url", "https://example.org/a"),
        "content": kw.get("content", "x" * 500),
        "relevance": kw.get("relevance", 0.0),
        "relevance_scored": kw.get("relevance_scored", 0),
        "credibility": kw.get("credibility", 0.5),
        "date_added": now_iso(),
    }
    db.save_source(row)
    return row["id"]


def _hypothesis(db, claim="Heritability rises with age", confidence=0.5, status="active"):
    hid = gen_id()
    db.save_hypothesis({
        "id": hid,
        "claim": claim,
        "status": status,
        "confidence": confidence,
        "date_added": now_iso(),
    })
    return hid


class TestQueueSeeding(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.q = WorkQueue(self.db, "topic-a")

    def test_seeds_snippet_only_source(self):
        sid = _source(self.db, content="short", url="https://example.org/short")
        _source(self.db, content="y" * 900, url="https://example.org/full")

        added = self.q.seed()

        self.assertEqual(added[KIND_FULL_TEXT], 1)
        rows = self.db._get_all("work_items", where="kind = ?", params=(KIND_FULL_TEXT,))
        self.assertEqual([r["ref_id"] for r in rows], [sid])

    def test_skips_scored_irrelevant_source(self):
        _source(self.db, content="short", relevance=0.05, relevance_scored=1)
        self.assertEqual(self.q.seed()[KIND_FULL_TEXT], 0)

    def test_seeds_hypothesis_without_evidence(self):
        hid = _hypothesis(self.db)
        added = self.q.seed()
        self.assertEqual(added[KIND_HYPOTHESIS_EVIDENCE], 1)
        row = self.db._get_all("work_items", where="kind = ?", params=(KIND_HYPOTHESIS_EVIDENCE,))[0]
        self.assertEqual(row["ref_id"], hid)

    def test_skips_hypothesis_that_has_evidence(self):
        hid = _hypothesis(self.db)
        self.db.save_evidence({
            "id": gen_id(), "hypothesis_id": hid, "source_id": "s1",
            "evidence_type": "supports", "content": "a finding", "strength": 0.6,
            "date_added": now_iso(),
        })
        self.assertEqual(self.q.seed()[KIND_HYPOTHESIS_EVIDENCE], 0)

    def test_seeds_open_question_only(self):
        self.db.save_question({"id": gen_id(), "question": "Open one?", "status": "open",
                               "importance": 0.6, "uncertainty": 0.6})
        self.db.save_question({"id": gen_id(), "question": "Answered one?", "status": "answered",
                               "importance": 0.9, "uncertainty": 0.9})
        added = self.q.seed()
        self.assertEqual(added[KIND_OPEN_QUESTION], 1)
        row = self.db._get_all("work_items", where="kind = ?", params=(KIND_OPEN_QUESTION,))[0]
        self.assertEqual(row["title"], "Open one?")

    def test_seeds_citation_for_relevant_doi_source(self):
        _source(self.db, url="https://doi.org/10.1000/xyz", relevance=0.6,
                relevance_scored=1, content="z" * 600)
        added = self.q.seed()
        self.assertEqual(added[KIND_CITATION], 1)

    def test_reseeding_refreshes_the_priority(self):
        hid = _hypothesis(self.db, confidence=0.5)
        self.q.seed()
        item = self.db._get_all("work_items", where="kind = ?",
                               params=(KIND_HYPOTHESIS_EVIDENCE,))[0]
        old = item["priority"]

        self.db._update("hypotheses", hid, {"confidence": 0.95})  # little left to learn
        self.q.seed()

        self.assertLess(self.db._get("work_items", item["id"])["priority"], old)

    def test_seeding_is_idempotent(self):
        _source(self.db, content="short")
        _hypothesis(self.db)
        first = self.q.seed()
        second = self.q.seed()
        self.assertGreater(sum(first.values()), 0)
        self.assertEqual(sum(second.values()), 0)
        self.assertEqual(self.db._count("work_items"), sum(first.values()))


class TestPriority(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.q = WorkQueue(self.db, "t")

    def test_mid_confidence_hypothesis_outranks_confident_one(self):
        mid = _hypothesis(self.db, "Mid confidence claim", confidence=0.5)
        high = _hypothesis(self.db, "Confident claim", confidence=0.95)
        self.q.seed()

        by_ref = {r["ref_id"]: r for r in self.db._get_all("work_items")}
        self.assertGreater(by_ref[mid]["priority"], by_ref[high]["priority"])

    def test_simulation_ranks_below_evidence_and_full_text(self):
        """Measured cost: a simulation ate 10 of 19 minutes for one neutral row.

        It stays in the queue, but only runs when the cheaper work is done.
        """
        simulation = _priority(KIND_SIMULATION, 0.75)
        evidence = _priority(KIND_HYPOTHESIS_EVIDENCE, 0.75)
        full_text = _priority(KIND_FULL_TEXT, 0.75)

        self.assertLess(simulation, evidence)
        self.assertLess(simulation, full_text)

    def test_open_item_whose_reason_disappeared_is_closed(self):
        """Stale items kept their old priority and outranked real work."""
        hid = _hypothesis(self.db, confidence=0.5)
        self.db._update("hypotheses", hid, {"falsification_conditions": "[\"If X\"]"})
        self.q.seed()
        simulation = self.db._get_all("work_items", where="kind = ?",
                                     params=(KIND_SIMULATION,))[0]
        self.assertEqual(simulation["status"], "open")

        # The prediction gets tested twice: the hypothesis is no longer a
        # simulation candidate, so its open item has to disappear.
        self.db._update("hypotheses", hid, {"falsification_conditions": "[]", "predictions": "[]"})
        self.q.seed()

        self.assertEqual(self.db._get("work_items", simulation["id"])["status"], "done")

    def test_literature_evidence_does_not_cancel_a_simulation(self):
        """A paper that disagrees is not a falsification test.

        Live failure: 25 simulation items were retired in 20 minutes, every one
        of them with a stated prediction and zero experiments, because the
        evidence phase had matched it to a source first.
        """
        hid = _hypothesis(self.db, confidence=0.5)
        self.db._update("hypotheses", hid, {"falsification_conditions": "[\"If X\"]"})
        self.q.seed()
        item = self.db._get_all("work_items", where="kind = ?",
                               params=(KIND_SIMULATION,))[0]

        self.db.save_evidence({
            "id": gen_id(), "hypothesis_id": hid, "source_id": "s1",
            "evidence_type": "contradicts", "content": "a paper disagrees",
            "strength": 0.7, "experiment_id": "", "date_added": now_iso(),
        })
        self.q.seed()

        self.assertEqual(self.db._get("work_items", item["id"])["status"], "open")

    def test_directional_experiment_ends_simulation_candidacy(self):
        """Once a study produced a verdict, the prediction is answered."""
        hid = _hypothesis(self.db, confidence=0.5)
        self.db._update("hypotheses", hid, {"falsification_conditions": "[\"If X\"]"})
        self.q.seed()
        item = self.db._get_all("work_items", where="kind = ?",
                               params=(KIND_SIMULATION,))[0]

        self.db.save_evidence({
            "id": gen_id(), "hypothesis_id": hid, "source_id": "s1",
            "evidence_type": "contradicts", "content": "the simulation ran",
            "strength": 0.7, "experiment_id": "exp1", "date_added": now_iso(),
        })
        self.q.seed()

        self.assertEqual(self.db._get("work_items", item["id"])["status"], "done")

    def test_retired_candidate_returns_when_its_reason_returns(self):
        """One row per task must not be a life sentence.

        After the simulation rule was fixed, 26 items stayed closed because the
        unique (topic, kind, ref_id) row still existed in its done state.
        """
        hid = _hypothesis(self.db, confidence=0.5)
        self.db._update("hypotheses", hid, {"falsification_conditions": "[\"If X\"]"})
        self.q.seed()
        item = self.db._get_all("work_items", where="kind = ?",
                               params=(KIND_SIMULATION,))[0]

        self.db._update("hypotheses", hid, {"falsification_conditions": "[]"})
        self.q.seed()
        self.assertEqual(self.db._get("work_items", item["id"])["status"], "done")

        self.db._update("hypotheses", hid, {"falsification_conditions": "[\"If X\"]"})
        self.q.seed()

        row = self.db._get("work_items", item["id"])
        self.assertEqual(row["status"], "open")
        self.assertEqual(row["note"], "")
        self.assertEqual(row["attempts"], 0)

    def test_finished_work_is_not_reopened(self):
        """Only automatic retirement is undone; a result stays a result."""
        hid = _hypothesis(self.db, confidence=0.5)
        self.db._update("hypotheses", hid, {"falsification_conditions": "[\"If X\"]"})
        self.q.seed()
        item = self.db._get_all("work_items", where="kind = ?",
                               params=(KIND_SIMULATION,))[0]
        self.q.resolve(item["id"], "simulation recorded")

        self.q.seed()

        self.assertEqual(self.db._get("work_items", item["id"])["status"], "done")

    def test_claim_returns_highest_priority_first(self):
        _hypothesis(self.db, "Low value", confidence=0.95)
        top = _hypothesis(self.db, "High value", confidence=0.5)
        _source(self.db, content="short")
        self.q.seed()

        claimed = self.q.claim(1)

        self.assertEqual(len(claimed), 1)
        self.assertEqual(claimed[0]["ref_id"], top)
        self.assertEqual(claimed[0]["status"], "in_progress")
        self.assertEqual(claimed[0]["attempts"], 1)

    def test_claim_zero_returns_nothing(self):
        _source(self.db, content="short")
        self.q.seed()
        self.assertEqual(self.q.claim(0), [])

    def test_waiting_item_overtakes_a_slightly_higher_fresh_one(self):
        """Starvation fix: a frozen order gave every cycle to the same kind.

        Live: the best citation item (0.80) lost to ten hypothesis_evidence
        items (0.819) in every single cycle, so 69 citation items never ran.
        """
        _source(self.db, content="short", url="https://example.org/snippet")
        _hypothesis(self.db, confidence=0.5)
        self.q.seed()
        items = {r["kind"]: r for r in self.db._get_all("work_items")}
        waiting = items[KIND_FULL_TEXT]
        fresh = items[KIND_HYPOTHESIS_EVIDENCE]
        # Seeding refreshes the priority of open items, so both are set after it.
        self.db._update("work_items", waiting["id"], {
            "priority": 0.80,
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=4)).isoformat(),
        })
        self.db._update("work_items", fresh["id"], {"priority": 0.85})

        claimed = self.q.claim(1)

        self.assertEqual(claimed[0]["id"], waiting["id"])

    def test_age_alone_does_not_beat_a_much_better_item(self):
        """Age raises the bid; the cap keeps it from dominating the ranking."""
        _source(self.db, content="short", url="https://example.org/snippet")
        _hypothesis(self.db, confidence=0.5)
        self.q.seed()
        items = {r["kind"]: r for r in self.db._get_all("work_items")}
        old = items[KIND_FULL_TEXT]
        better = items[KIND_HYPOTHESIS_EVIDENCE]
        self.db._update("work_items", old["id"], {
            "priority": 0.30,
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=40)).isoformat(),
        })
        self.db._update("work_items", better["id"], {"priority": 0.90})

        self.assertEqual(self.q.claim(1)[0]["id"], better["id"])

    def _simulatable(self, claim="Errors rise with sleep loss"):
        hid = _hypothesis(self.db, claim, confidence=0.5)
        self.db._update("hypotheses", hid, {
            "predictions": '["errors rise with sleep loss"]',
            "falsification_conditions": '["no change in error rate"]',
        })
        return hid

    def _item_by_kind(self, kind, index=0):
        rows = self.db._get_all("work_items", where="kind = ?", params=(kind,))
        return rows[index]

    def test_starved_kind_gets_a_slot(self):
        """Being cheapest forever is not a ranking, it is a stop.

        Live 27.10.: 154 open simulation items, 0 attempts, last experiment at
        13:14, while citation (0.80) and evidence (0.90) took both slots every
        cycle. A simulation item tops out at 0.183 + 0.30 of aging, so no amount
        of waiting could ever lift it above them.
        """
        hid = self._simulatable()
        _hypothesis(self.db, "First claim against the papers", confidence=0.5)
        _hypothesis(self.db, "Second claim against the papers", confidence=0.5)
        _hypothesis(self.db, "A claim already settled", confidence=0.5)
        self.q.seed()

        simulation = self._item_by_kind(KIND_SIMULATION)
        self.db._update("work_items", simulation["id"], {
            "priority": 0.183,
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
        })
        for row in self.db._get_all("work_items", where="kind = ?",
                                    params=(KIND_HYPOTHESIS_EVIDENCE,)):
            self.db._update("work_items", row["id"], {"priority": 0.90})
        # The evidence kind finished something a moment ago; the simulation kind
        # has not finished anything at all.
        self.q.resolve(self._item_by_kind(KIND_HYPOTHESIS_EVIDENCE, 2)["id"], "checked")

        claimed = self.q.claim(2)

        self.assertEqual(len(claimed), 2)
        self.assertEqual({c["kind"] for c in claimed},
                         {KIND_SIMULATION, KIND_HYPOTHESIS_EVIDENCE})
        self.assertEqual([c["ref_id"] for c in claimed if c["kind"] == KIND_SIMULATION],
                         [hid])

    def test_guard_stays_silent_while_every_kind_finishes_something(self):
        """The reserved slot is for a stalled kind, not for every low-priority one.

        Two simulations, two claims, one more claim to fill the queue: after one
        simulation and one claim have just finished, both kinds are current and
        the ranking stands.
        """
        self._simulatable("First prediction")
        self._simulatable("Second prediction")
        _hypothesis(self.db, "First claim against the papers", confidence=0.5)
        _hypothesis(self.db, "Second claim against the papers", confidence=0.5)
        _hypothesis(self.db, "Third claim against the papers", confidence=0.5)
        self.q.seed()

        stratified = self._item_by_kind(KIND_SIMULATION, 1)
        self.db._update("work_items", stratified["id"], {
            "priority": 0.183,
            "created_at": (datetime.now(timezone.utc) - timedelta(hours=6)).isoformat(),
        })
        for row in self.db._get_all("work_items", where="kind = ?",
                                    params=(KIND_HYPOTHESIS_EVIDENCE,)):
            self.db._update("work_items", row["id"], {"priority": 0.90})
        self.q.resolve(self._item_by_kind(KIND_SIMULATION)["id"], "simulation recorded")
        self.q.resolve(self._item_by_kind(KIND_HYPOTHESIS_EVIDENCE, 2)["id"], "checked")

        claimed = self.q.claim(2)

        self.assertEqual({c["kind"] for c in claimed}, {KIND_HYPOTHESIS_EVIDENCE})


class TestLifecycle(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.q = WorkQueue(self.db, "t")
        _source(self.db, content="short")
        self.q.seed()
        self.item = self.q.claim(1)[0]

    def test_resolve_removes_from_open(self):
        self.q.resolve(self.item["id"], "fetched full text")
        stats = self.q.stats()
        self.assertEqual(stats["open"], 0)
        self.assertEqual(stats["done"], 1)
        row = self.db._get("work_items", self.item["id"])
        self.assertEqual(row["note"], "fetched full text")

    def test_defer_returns_without_burning_an_attempt(self):
        self.q.defer(self.item["id"], "rate limited")
        row = self.db._get("work_items", self.item["id"])
        self.assertEqual(row["status"], "open")
        self.assertEqual(row["attempts"], 0)
        self.assertIn("rate limited", row["note"])

        # Two deferrals still leave the item workable.
        again = self.q.claim(1)[0]
        self.q.defer(again["id"], "rate limited")
        self.assertEqual(self.db._get("work_items", self.item["id"])["status"], "open")

    def test_release_returns_to_queue_then_blocks(self):
        self.assertEqual(self.q.release(self.item["id"], "403"), "open")
        self.assertEqual(self.q.stats()["open"], 1)

        again = self.q.claim(1)[0]
        self.assertEqual(again["attempts"], MAX_ATTEMPTS)
        self.assertEqual(self.q.release(again["id"], "403 again"), "blocked")
        self.assertEqual(self.q.stats()["blocked"], 1)
        self.assertEqual(self.q.stats()["open"], 0)

    def test_stats_exhausted_only_when_nothing_open(self):
        self.assertFalse(self.q.stats()["exhausted"])
        self.q.block(self.item["id"], "unreachable")
        self.assertTrue(self.q.stats()["exhausted"])

    def test_stale_claim_goes_back_to_queue(self):
        self.db._update("work_items", self.item["id"],
                        {"updated_at": "2020-01-01T00:00:00+00:00"})
        self.assertEqual(self.q.release_stale(), 1)
        self.assertEqual(self.db._get("work_items", self.item["id"])["status"], "open")

    def test_fresh_claim_survives_stale_sweep(self):
        self.assertEqual(self.q.release_stale(), 0)

    def test_claim_kind_picks_matching_item_only(self):
        self.q.resolve(self.item["id"])
        hid = _hypothesis(self.db)
        self.q.seed()
        claimed = self.q.claim_kind(KIND_HYPOTHESIS_EVIDENCE)
        self.assertEqual(claimed["ref_id"], hid)
        self.assertIsNone(self.q.claim_kind(KIND_HYPOTHESIS_EVIDENCE))

    def test_topics_are_isolated(self):
        other = WorkQueue(self.db, "other-topic")
        other.seed()
        mine = {r["id"] for r in self.db._get_all("work_items", where="topic = ?", params=("t",))}
        theirs = {r["id"] for r in self.db._get_all("work_items", where="topic = ?", params=("other-topic",))}
        self.assertEqual(len(mine), 1)
        self.assertEqual(len(theirs), 1)
        self.assertEqual(mine & theirs, set())


class TestEffectExtractionCandidates(unittest.TestCase):
    """Which papers get read out for effect sizes - and which never should."""

    def setUp(self):
        self.db = Database(":memory:")
        self.q = WorkQueue(self.db, "t", relevance_threshold=0.25)

    def _relevant(self, relevance=0.7):
        return _source(self.db, content="x" * 500, relevance=relevance,
                       relevance_scored=1)

    def _text(self, sid, kind="html", chars=5000):
        self.db.save_source_text(sid, "z " * (chars // 2), kind=kind)

    def test_a_relevant_source_with_real_text_is_seeded_once(self):
        sid = self._relevant()
        self._text(sid)
        added = self.q.seed()
        self.assertEqual(added[KIND_EFFECT_EXTRACTION], 1)
        rows = self.db._get_all(
            "work_items", where="kind = ?", params=(KIND_EFFECT_EXTRACTION,)
        )
        self.assertEqual([r["ref_id"] for r in rows], [sid])
        # Seeding again does not duplicate the item.
        self.assertEqual(self.q.seed()[KIND_EFFECT_EXTRACTION], 0)

    def test_an_abstract_alone_is_not_worth_reading_out(self):
        # An abstract rarely reports a standard error: rows from it could not be
        # pooled and would only look like progress in the count.
        sid = self._relevant()
        self._text(sid, kind="abstract")
        self.assertEqual(self.q.seed()[KIND_EFFECT_EXTRACTION], 0)

    def test_a_short_document_does_not_qualify(self):
        sid = self._relevant()
        self._text(sid, chars=1000)
        self.assertEqual(self.q.seed()[KIND_EFFECT_EXTRACTION], 0)

    def test_a_source_below_the_relevance_gate_is_skipped(self):
        sid = self._relevant(relevance=0.05)
        self._text(sid)
        self.assertEqual(self.q.seed()[KIND_EFFECT_EXTRACTION], 0)

    def test_a_source_whose_numbers_are_read_stops_being_a_candidate(self):
        sid = self._relevant()
        self._text(sid)
        self.q.seed()
        self.db.save_study_effect({
            "id": gen_id(), "source_id": sid, "outcome": "cog",
            "effect_type": "smd", "effect": 0.3, "se": 0.1, "ci_level": 0.95,
            "disputed": 0, "rejection_reason": "", "created_at": now_iso(),
        })
        self.q.seed()
        open_items = self.db._get_all(
            "work_items",
            where="kind = ? AND status = 'open'",
            params=(KIND_EFFECT_EXTRACTION,),
        )
        self.assertEqual(open_items, [])


class TestSimulationCandidates(unittest.TestCase):
    """Which hypotheses deserve an experiment (and when to run it again)."""

    def setUp(self):
        self.db = Database(":memory:")
        self.q = WorkQueue(self.db, "t", sim_max_per_hypothesis=2)

    def _testable(self, **kw):
        hid = gen_id()
        self.db.save_hypothesis({
            "id": hid,
            "claim": kw.get("claim", "Sleep loss raises error rates"),
            "status": kw.get("status", "active"),
            "confidence": 0.5,
            "predictions": '["error rate rises with sleep loss"]',
            "falsification_conditions": '["no change in error rate"]',
            "date_added": now_iso(),
        })
        return hid

    def _experiment(self, hid, verdict="neutral", evidence_type=None):
        eid = gen_id()
        self.db.save_experiment({
            "id": eid,
            "hypothesis_id": hid,
            "claim": "Sleep loss raises error rates",
            "status": "completed",
            "verdict": verdict,
            "result": json.dumps({"value": 0.1, "p_value": 0.4}),
            "created_at": now_iso(),
            "updated_at": now_iso(),
        })
        kind = evidence_type or verdict
        self.db.save_evidence({
            "id": gen_id(),
            "hypothesis_id": hid,
            "source_id": "",
            "evidence_type": kind,
            "content": "simulated outcome",
            "strength": 0.3,
            "date_added": now_iso(),
            "experiment_id": eid,
        })
        return eid

    def _seeded(self):
        self.q.seed()
        return {
            row["ref_id"] for row in
            self.db._get_all("work_items", where="kind = ?", params=(KIND_SIMULATION,))
        }

    def test_untested_hypothesis_is_scheduled(self):
        hid = self._testable()
        self.assertIn(hid, self._seeded())

    def test_confirmed_hypothesis_is_not_test_again(self):
        hid = self._testable()
        self._experiment(hid, verdict="supports")
        self.assertNotIn(hid, self._seeded())

    def test_inconclusive_simulation_is_replicated(self):
        hid = self._testable()
        self._experiment(hid, verdict="neutral")
        self.assertIn(hid, self._seeded(), "a null simulation is a reason to replicate")

    def test_replication_is_capped(self):
        hid = self._testable()
        self._experiment(hid, verdict="neutral")
        self._experiment(hid, verdict="neutral")
        self.assertNotIn(hid, self._seeded(), "two inconclusive runs close the queue item")

    def test_literature_evidence_does_not_block_a_simulation(self):
        """A paper is not a falsification test - only an experiment is.

        This test used to assert the opposite, and that is exactly what broke
        the run: once the evidence phase matched a hypothesis to any source, its
        simulation item was retired as "no longer a candidate". 25 items went
        that way in 20 minutes, all with a stated prediction, none tested.
        """
        hid = self._testable()
        self.db.save_evidence({
            "id": gen_id(),
            "hypothesis_id": hid,
            "source_id": gen_id(),
            "evidence_type": "supports",
            "content": "from a paper",
            "strength": 0.7,
            "date_added": now_iso(),
            "experiment_id": "",
        })
        self.assertIn(hid, self._seeded())


class TestReservedSlot(unittest.TestCase):
    """The kind that cannot win on priority still gets worked.

    Measured on the live run 28.10.: effect_extraction items carried priority
    0.20-0.52 against citations at 0.84 and evidence at 0.90, so 155 unread
    papers stayed open for a whole run while the agent pooled nothing. The idle
    timer did not save it either - the 19 items the on-demand script finished at
    15:22 reset the kind's idle counter.
    """

    def setUp(self):
        self.db = Database(":memory:")
        self.q = WorkQueue(self.db, "t")
        self.citation = self._seed(KIND_CITATION, "c1", 0.90)
        self.evidence = self._seed(KIND_HYPOTHESIS_EVIDENCE, "h1", 0.90)
        self.effect = self._seed(KIND_EFFECT_EXTRACTION, "e1", 0.30)

    def _seed(self, kind, ref_id, priority):
        self.q._insert_item(kind, ref_id, ref_id, priority, now_iso())
        return self.db._get_all(
            "work_items", where="kind = ? AND ref_id = ?", params=(kind, ref_id)
        )[0]["id"]

    def _reset(self, item_ids):
        for item_id in item_ids:
            self.db._update("work_items", item_id, {"status": "open", "attempts": 0})

    def test_without_the_reservation_the_effect_item_never_wins(self):
        claimed = {row["id"] for row in self.q.claim(2)}
        self.assertEqual(claimed, {self.citation, self.evidence})

    def test_the_reservation_puts_it_in_the_last_slot(self):
        claimed = self.q.claim(2, reserve_kinds=(KIND_EFFECT_EXTRACTION,))
        kinds = [row["kind"] for row in claimed]
        self.assertIn(KIND_EFFECT_EXTRACTION, kinds)
        self.assertEqual(kinds[-1], KIND_EFFECT_EXTRACTION)

    def test_a_reservation_without_open_work_costs_no_slot(self):
        self._reset([self.citation, self.evidence])
        self.db._update("work_items", self.effect, {"status": "done"})

        claimed = {row["id"] for row in self.q.claim(2, reserve_kinds=(KIND_EFFECT_EXTRACTION,))}

        self.assertEqual(claimed, {self.citation, self.evidence})

    def test_a_single_slot_is_not_reserved(self):
        self.assertEqual(len(self.q.claim(1, reserve_kinds=(KIND_EFFECT_EXTRACTION,))), 1)


class TestEffectPrecisionOrder(unittest.TestCase):
    """Papers that state a number with its precision come before the rest.

    A paper that only sets parameters for a simulation reports no SE and no CI,
    so its rows can never be pooled. Measured on the corpus of 28.10. (21 papers
    already read out): 2 of the 4 papers with a poolable row carried the marker,
    4 of the 17 without one did too - a preference, not a filter.
    """

    def setUp(self):
        self.db = Database(":memory:")
        self.q = WorkQueue(self.db, "t", relevance_threshold=0.25)

    def _readable(self, relevance, content):
        sid = _source(self.db, content=content, relevance=relevance,
                      relevance_scored=1)
        self.db.save_source_text(sid, content, kind="html")
        return sid

    def test_a_precise_paper_beats_an_equally_relevant_one(self):
        weak = self._readable(0.70, "We set the prevalence at 0.2 in every scenario. " * 200)
        precise = self._readable(0.70, "The effect was 0.42 (95% CI 0.22 to 0.62). " * 200)

        candidates = self.q._effect_candidates()

        self.assertEqual(candidates[0]["ref_id"], precise)
        self.assertEqual(candidates[1]["ref_id"], weak)
        self.assertGreater(candidates[0]["priority"], candidates[1]["priority"])

    def test_a_clearly_more_relevant_paper_still_wins(self):
        # The marker is a preference worth 0.25 relevance points, not a free
        # pass: a methodology paper that merely mentions confidence intervals
        # must not push a far more relevant paper out of the slot.
        precise = self._readable(0.40, "The effect was 0.42 (95% CI 0.22 to 0.62). " * 200)
        relevant = self._readable(0.95, "We set the prevalence at 0.2 in every scenario. " * 200)

        candidates = self.q._effect_candidates()

        self.assertEqual(candidates[0]["ref_id"], relevant)
        self.assertEqual(candidates[1]["ref_id"], precise)

    def test_a_commentary_does_not_get_the_boost(self):
        # A commentary quotes confidence intervals from other people's studies
        # and has no estimate of its own; boosting it spends the slot on a text
        # that cannot contribute a row.
        commentary = self._readable(0.70, "The effect was 0.42 (95% CI 0.22 to 0.62). " * 200)
        self.db._update("sources", commentary, {"title": "Invited Commentary: Detecting Pleiotropy"})
        study = self._readable(0.90, "We set the prevalence at 0.2 in every scenario. " * 200)

        candidates = self.q._effect_candidates()

        self.assertEqual(candidates[0]["ref_id"], study)

    def test_without_the_marker_relevance_decides(self):
        low = self._readable(0.4, "No numbers here at all. " * 200)
        high = self._readable(0.9, "Still no numbers here. " * 200)

        self.assertEqual([c["ref_id"] for c in self.q._effect_candidates()], [high, low])

    def test_reports_precision_reads_the_usual_notations(self):
        self.assertTrue(reports_precision("Heritability was 0.31 (95% CI 0.24 to 0.38)."))
        self.assertTrue(reports_precision("The difference was 0.42, SE 0.10."))
        self.assertTrue(reports_precision("Beta 0.3 ± 0.1 in the full model."))
        self.assertFalse(reports_precision("We set the parameter to 0.3."))
        self.assertFalse(reports_precision(""))


class TestUnreadSourceBacklog(unittest.TestCase):
    """Sources with text but no fact row are the backlog the corpus grew past."""

    def setUp(self):
        self.db = Database(":memory:")

    def _fact(self, source_id):
        self.db.save_fact({
            "id": gen_id(), "content": "a finding", "confidence": 0.6,
            "source_ids": json.dumps([source_id]), "date_added": now_iso(),
            "topic": "t",
        })

    def test_a_text_without_facts_is_offered_once(self):
        sid = _source(self.db, content="y" * 800, relevance=0.7, relevance_scored=1)

        rows = self.db.get_sources_without_facts(limit=5, min_relevance=0.25)
        self.assertEqual([row["id"] for row in rows], [sid])

        self.db.mark_facts_attempted([sid])
        self.assertEqual(self.db.get_sources_without_facts(limit=5, min_relevance=0.25), [])

    def test_a_source_with_a_fact_is_not_a_candidate(self):
        sid = _source(self.db, content="y" * 800, relevance=0.7, relevance_scored=1)
        self._fact(sid)

        self.assertEqual(self.db.get_sources_without_facts(limit=5, min_relevance=0.25), [])

    def test_a_snippet_is_not_worth_a_read(self):
        _source(self.db, content="short", relevance=0.9, relevance_scored=1)
        self.assertEqual(self.db.get_sources_without_facts(limit=5, min_relevance=0.25), [])

    def test_a_scored_irrelevant_source_is_skipped(self):
        _source(self.db, content="y" * 800, relevance=0.05, relevance_scored=1)
        self.assertEqual(self.db.get_sources_without_facts(limit=5, min_relevance=0.25), [])

    def test_the_backlog_size_follows_the_rows(self):
        _source(self.db, content="y" * 800, relevance=0.7, relevance_scored=1)
        _source(self.db, content="y" * 800, relevance=0.6, relevance_scored=1)
        self.assertEqual(self.db.count_sources_without_facts(), 2)

    def test_a_source_that_was_read_and_yielded_nothing_leaves_the_backlog(self):
        # It still has no fact row, but the work is done - otherwise a catch-up
        # mode keyed on this number could never switch off.
        sid = _source(self.db, content="y" * 800, relevance=0.7, relevance_scored=1)
        self.assertEqual(self.db.count_sources_without_facts(), 1)

        self.db.mark_facts_attempted([sid])

        self.assertEqual(self.db.count_sources_without_facts(), 0)


class TestEvidencePairMemory(unittest.TestCase):
    """A neutral verdict is not an evidence row, but it is a paid classification."""

    def setUp(self):
        self.db = Database(":memory:")

    def test_a_neutral_pair_is_remembered_across_restarts(self):
        self.db.save_evidence_pair("h1", "s1", "neutral", "takes no position")

        self.assertEqual(self.db.get_evaluated_evidence_pairs(), [("h1", "s1")])
        self.assertEqual(self.db.count_evidence_pairs(), 1)
        self.assertEqual(self.db.count_evidence_pairs("neutral"), 1)

    def test_saving_the_same_pair_twice_does_not_duplicate_it(self):
        self.db.save_evidence_pair("h1", "s1", "neutral", "first")
        self.db.save_evidence_pair("h1", "s1", "supports", "second")

        self.assertEqual(self.db.count_evidence_pairs(), 1)
        self.assertEqual(self.db.get_evidence_for_hypothesis("h1"), [],
                         "a pair is not evidence; the table stays directional")


if __name__ == "__main__":
    unittest.main()
