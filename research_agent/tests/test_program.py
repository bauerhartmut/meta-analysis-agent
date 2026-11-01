"""Research program: decomposition, allocation, stop rules and verdicts.

Offline: fake planner, in-memory database. The claims under test are the ones
that make a program different from a question loop - work is allocated by
marginal gain, the running sub-question is not abandoned every cycle, stop rules
fire from stored numbers, and a closed sub-question carries a verdict that says
which position the collected evidence favours.
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent import program as P
from research_agent.config import Config
from research_agent.database import Database
from research_agent.models import gen_id, now_iso
from research_agent.orchestrator import ResearchOrchestrator
from research_agent.report import build_report


DECOMPOSITION = [
    {
        "question": "How large is the polygenic score effect on cognitive outcomes?",
        "rationale": "It decides whether selection can matter at all.",
        "kind": "measurement",
        "importance": 0.9,
        "uncertainty": 0.8,
        "rivals": [
            {"position": "The within-family effect is small",
             "discriminating_test": "sibling comparison in the same cohort"},
            {"position": "The effect is large", "discriminating_test": "out-of-sample prediction"},
        ],
    },
    {
        "question": "Which ethical objections are raised against embryo selection for cognition?",
        "rationale": "Determines what may be done at all.",
        "kind": "ethics",
        "importance": 0.6,
        "uncertainty": 0.5,
        "rivals": ["Objections rest on human dignity", "Objections are about distribution"],
    },
    {
        "question": "Which countries regulate polygenic embryo selection?",
        "kind": "context",
        "importance": 0.3,
        "uncertainty": 0.4,
        "rivals": [],
    },
]


def _item(**overrides):
    item = {
        "id": gen_id(), "topic": "t", "question": "A question about heritability?",
        "kind": "empirical", "rivals": "[]", "status": P.STATUS_OPEN,
        "importance": 0.5, "uncertainty": 0.8, "cycles_spent": 0,
        "sources_gained": 0, "facts_gained": 0, "evidence_gained": 0,
        "gain_cycles": 0, "opened_at": now_iso(), "verdict": "{}",
    }
    item.update(overrides)
    return item


class TestDecomposition(unittest.TestCase):
    def test_items_are_parsed_with_defaults(self):
        items = P.parse_decomposition(DECOMPOSITION, "topic", limit=6)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["kind"], "measurement")
        self.assertAlmostEqual(items[0]["importance"], 0.9)
        self.assertEqual(len(items[0]["rivals"]), 2)
        self.assertIn("sibling comparison", items[0]["rivals"][0]["discriminating_test"])
        self.assertEqual(items[2]["kind"], "context")

    def test_string_rivals_become_positions(self):
        items = P.parse_decomposition(DECOMPOSITION, "topic", limit=6)
        positions = [r["position"] for r in items[1]["rivals"]]
        self.assertEqual(positions, ["Objections rest on human dignity",
                                    "Objections are about distribution"])

    def test_non_questions_are_dropped(self):
        payload = [
            {"question": "Too short"},
            {"question": "What is the measured effect size of polygenic scores on cognition?"},
            {"rationale": "no question at all"},
        ]
        items = P.parse_decomposition(payload, "topic")
        self.assertEqual(len(items), 1)
        self.assertIn("effect size", items[0]["question"])

    def test_near_duplicates_are_merged(self):
        payload = [
            {"question": "How large is the polygenic score effect on cognitive outcomes?"},
            {"question": "How large is the polygenic score effect on cognitive outcome?"},
        ]
        self.assertEqual(len(P.parse_decomposition(payload, "topic")), 1)

    def test_limit_caps_the_program(self):
        # Distinct in content, so the cap is what stops them, not the dedupe.
        subjects = [
            "heritability across the lifespan in twin samples",
            "population stratification in score transfer",
            "embryo selection outcomes in clinical cohorts",
            "selection response in breeding programmes",
            "replication rates of behavioural findings",
            "ethical frameworks for reproductive screening",
        ]
        payload = [{"question": f"What is known about {subject}?"} for subject in subjects]
        self.assertEqual(len(P.parse_decomposition(payload, "topic", limit=4)), 4)

    def test_envelope_with_unknown_key_is_unwrapped(self):
        payload = {"plan": [{"question": "What does the within-family design measure exactly?"}]}
        items = P.parse_decomposition(payload, "topic")
        self.assertEqual(len(items), 1)

    def test_importance_and_uncertainty_are_clamped(self):
        payload = [{"question": "What is the replication rate of these polygenic findings?",
                    "importance": 42, "uncertainty": -3}]
        item = P.parse_decomposition(payload, "topic")[0]
        self.assertEqual(item["importance"], 1.0)
        self.assertEqual(item["uncertainty"], 0.1)


class TestAllocation(unittest.TestCase):
    def test_importance_and_uncertainty_drive_the_value(self):
        high = _item(importance=0.9, uncertainty=0.9)
        low = _item(importance=0.2, uncertainty=0.2)
        self.assertGreater(P.marginal_value(high), P.marginal_value(low))

    def test_value_decays_with_what_the_item_already_produced(self):
        fresh = _item()
        fed = _item(facts_gained=6, sources_gained=6)
        self.assertGreater(P.marginal_value(fresh), P.marginal_value(fed))

    def test_value_decays_with_cycles_spent(self):
        self.assertGreater(P.marginal_value(_item()), P.marginal_value(_item(cycles_spent=4)))

    def test_competing_positions_carry_a_premium(self):
        plain = _item()
        contested = _item(rivals=json.dumps([{"position": "Effect is small", "discriminating_test": "x"}]))
        self.assertGreater(P.marginal_value(contested), P.marginal_value(plain))

    def test_rank_ignores_finished_items(self):
        rows = [
            _item(importance=0.9, uncertainty=0.9),
            _item(importance=0.4, uncertainty=0.5),
            _item(importance=1.0, uncertainty=1.0, status=P.STATUS_DONE),
        ]
        ranked = P.rank(rows)
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked[0]["importance"], 0.9)

    def test_running_item_is_kept_unless_clearly_worse(self):
        # The running item is a cycle in (decayed) but still the more valuable
        # one: switching every cycle is how a program becomes round-robin.
        running = _item(importance=0.9, uncertainty=0.9, status=P.STATUS_ACTIVE, cycles_spent=1)
        challenger = _item(importance=0.7, uncertainty=0.7)
        chosen = P.select_next([running, challenger], active_id=running["id"])
        self.assertEqual(chosen["id"], running["id"])
        self.assertGreater(P.marginal_value(running), P.marginal_value(challenger))

    def test_running_item_is_abandoned_when_it_stops_paying(self):
        running = _item(importance=0.2, uncertainty=0.2, status=P.STATUS_ACTIVE,
                        cycles_spent=6, facts_gained=8)
        challenger = _item(importance=0.9, uncertainty=0.9)
        chosen = P.select_next([running, challenger], active_id=running["id"])
        self.assertEqual(chosen["id"], challenger["id"])

    def test_select_next_without_items(self):
        self.assertIsNone(P.select_next([], active_id=""))
        self.assertIsNone(P.select_next([_item(status=P.STATUS_DONE)], active_id=""))


class TestStopRules(unittest.TestCase):
    def test_nothing_closes_before_the_minimum(self):
        closed, reason = P.close_decision(_item(cycles_spent=1), budget_cycles=8,
                                          saturation_cycles=3, min_cycles=2)
        self.assertFalse(closed)
        self.assertEqual(reason, "")

    def test_cycle_budget_closes_an_item(self):
        closed, reason = P.close_decision(_item(cycles_spent=8), budget_cycles=8,
                                          saturation_cycles=3, min_cycles=2)
        self.assertTrue(closed)
        self.assertIn("Zyklenbudget", reason)

    def test_saturation_closes_an_item(self):
        closed, reason = P.close_decision(_item(cycles_spent=4, gain_cycles=3),
                                          budget_cycles=20, saturation_cycles=3, min_cycles=2)
        self.assertTrue(closed)
        self.assertIn("ohne neuen Ertrag", reason)

    def test_a_productive_item_stays_open(self):
        closed, _ = P.close_decision(_item(cycles_spent=3, gain_cycles=0),
                                     budget_cycles=8, saturation_cycles=3, min_cycles=2)
        self.assertFalse(closed)

    def test_finished_items_are_not_closed_twice(self):
        closed, _ = P.close_decision(_item(cycles_spent=9, status=P.STATUS_DONE))
        self.assertFalse(closed)


class TestMaterialSelection(unittest.TestCase):
    FACTS = [
        {"content": "Within-family estimates of polygenic scores are about four percent of variance.",
         "confidence": 0.7},
        {"content": "Embryo selection raises ethical questions about enhancement.",
         "confidence": 0.9},
        {"content": "The within-family design controls for population stratification in polygenic studies.",
         "confidence": 0.5},
    ]

    def test_only_overlapping_facts_are_used(self):
        picked = P.select_facts_for(
            "How large is the polygenic score effect for within-family designs?", self.FACTS
        )
        contents = [f["content"] for f in picked]
        self.assertEqual(len(picked), 2)
        self.assertNotIn("Embryo selection raises ethical questions about enhancement.", contents)

    def test_higher_confidence_breaks_ties(self):
        picked = P.select_facts_for("polygenic within-family", self.FACTS, limit=1)
        self.assertEqual(len(picked), 1)


class TestVerdictStates(unittest.TestCase):
    def test_empty_object_is_not_a_verdict(self):
        self.assertFalse(P.has_verdict({"verdict": "{}"}))
        self.assertFalse(P.has_verdict({"verdict": ""}))

    def test_stored_verdict_is_recognized(self):
        item = {"verdict": json.dumps({"favored": "The small effect", "confidence": 0.6})}
        self.assertTrue(P.has_verdict(item))
        self.assertIn("The small effect", P.verdict_text(json.loads(item["verdict"])))

    def test_verdict_text_of_nothing(self):
        self.assertEqual(P.verdict_text(None), "")
        self.assertEqual(P.verdict_text({}), "")

    def test_progress_counts(self):
        counts = P.progress([
            _item(status=P.STATUS_DONE, cycles_spent=3, facts_gained=4),
            _item(status=P.STATUS_ACTIVE, cycles_spent=2, facts_gained=1),
            _item(status=P.STATUS_OPEN),
        ])
        self.assertEqual(counts["total"], 3)
        self.assertEqual(counts["done"], 1)
        self.assertEqual(counts["active"], 1)
        self.assertEqual(counts["cycles_spent"], 5)
        self.assertEqual(counts["facts_gained"], 5)


class TestProgramStorage(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")

    def test_roundtrip_and_ordering(self):
        for index in range(3):
            self.db.save_program_item(_item(topic="t", question=f"Question {index}?",
                                            opened_at=f"2026-01-0{index + 1}T00:00:00Z"))
        items = self.db.get_program_items("t")
        self.assertEqual([i["question"] for i in items], ["Question 0?", "Question 1?", "Question 2?"])

    def test_status_filter_and_counts(self):
        self.db.save_program_item(_item(topic="t", status=P.STATUS_DONE))
        self.db.save_program_item(_item(topic="t", status=P.STATUS_ACTIVE))
        self.db.save_program_item(_item(topic="other"))
        self.assertEqual(self.db.count_program_items("t"), 2)
        self.assertEqual(self.db.count_program_items("t", status=P.STATUS_ACTIVE), 1)
        self.assertEqual(self.db.get_active_program_item("t")["status"], P.STATUS_ACTIVE)

    def test_update_keeps_the_row(self):
        item = _item(topic="t")
        self.db.save_program_item(item)
        self.db.update_program_item(item["id"], {"cycles_spent": 3, "close_reason": "fertig"})
        stored = self.db.get_program_item(item["id"])
        self.assertEqual(stored["cycles_spent"], 3)
        self.assertEqual(stored["close_reason"], "fertig")


class _FakePlanner:
    def __init__(self, decomposition=None, verdict=None):
        self.decomposition = decomposition if decomposition is not None else DECOMPOSITION
        self.verdict = verdict or {
            "favored": "The within-family effect is small", "confidence": 0.6,
            "reasoning": "within-family estimates are lower",
            "counter_evidence": "between-individual estimates are larger",
            "discriminating_test": "sibling design", "open_questions": ["power"],
            "answered": True,
        }
        self.decompose_calls = 0
        self.verdict_calls = 0

    async def decompose_topic(self, topic, state, context):
        self.decompose_calls += 1
        return self.decomposition

    async def compare_positions(self, question, material, rivals, kind="empirical"):
        self.verdict_calls += 1
        self.last_material = material
        return dict(self.verdict)


def _orch(planner=None, **cfg_kwargs):
    cfg = Config()
    cfg.database_url = ":memory:"
    cfg.llm_failure_threshold = 0
    for key, value in cfg_kwargs.items():
        setattr(cfg, key, value)
    orch = ResearchOrchestrator(cfg)
    orch.current_topic = "Polygenic embryo selection and cognition"
    orch.work_queue.set_topic(orch.current_topic)
    orch.planner = planner or _FakePlanner()
    return orch


def _fact(db, topic: str, content: str, **extra):
    row = {"id": gen_id(), "content": content, "confidence": 0.7, "topic": topic,
           "date_added": now_iso()}
    row.update(extra)
    db.save_fact(row)
    return row


class TestOrchestratorProgram(unittest.TestCase):
    def test_program_is_created_once(self):
        planner = _FakePlanner()
        orch = _orch(planner)

        asyncio.run(orch._ensure_program())
        asyncio.run(orch._ensure_program())

        self.assertEqual(planner.decompose_calls, 1)
        items = orch.db.get_program_items(orch.current_topic)
        self.assertEqual(len(items), 3)
        self.assertEqual(json.loads(items[0]["rivals"])[0]["position"],
                         "The within-family effect is small")
        self.assertEqual(orch._program_status()["counts"]["open"], 3)

    def test_disabled_program_leaves_the_question_loop(self):
        orch = _orch(program_enabled=False)
        asyncio.run(orch._ensure_program())
        self.assertEqual(orch.db.count_program_items(orch.current_topic), 0)

    def test_unusable_decomposition_does_not_break_the_run(self):
        # `None` is what the planner returns when the LLM backend is down.
        for payload in (None, [], {}, [{"rationale": "nothing"}], "not json"):
            planner = _FakePlanner()
            planner.decomposition = payload  # bypass the fake's None -> default rule
            orch = _orch(planner)
            asyncio.run(orch._ensure_program())
            self.assertEqual(orch.db.count_program_items(orch.current_topic), 0)
            self.assertEqual(P.parse_decomposition(payload, "t"), [])

    def test_plan_research_follows_the_program(self):
        orch = _orch()
        asyncio.run(orch._ensure_program())

        planned = asyncio.run(orch._plan_research(1))

        self.assertIn("polygenic score effect", planned["question"])
        self.assertTrue(planned["_program_item_id"])
        self.assertIn("Forschungsprogramm", planned["_selection_reasoning"])
        active = orch.db.get_active_program_item(orch.current_topic)
        self.assertEqual(active["id"], planned["_program_item_id"])

    def test_plan_research_falls_back_without_a_program(self):
        orch = _orch(program_enabled=False)
        planned = asyncio.run(orch._plan_research(1))
        self.assertTrue(planned and planned.get("question"))

    def test_seed_question_bank_is_gated_by_topic(self):
        """The fixed IQ/embryo seed list must not enter an unrelated run.

        _plan_research injects the whole bank whenever the question pool is thin
        and then prefers unanswered seed questions, so a run about cognition and
        mortality would have been flooded with embryo-selection questions.
        """
        own = _orch(program_enabled=False)
        asyncio.run(own._plan_research(1))
        own_questions = [q["question"] for q in own.db.get_all_questions(limit=200)]
        self.assertTrue([q for q in own_questions if "embryo" in q.lower()],
                        "its own topic still gets the seed bank")

        class _QuietPlanner(_FakePlanner):
            async def generate_research_questions(self, topic, state, context):
                return []

        other = _orch(_QuietPlanner(), program_enabled=False)
        other.current_topic = "Cognitive ability and mortality selection"
        other.work_queue.set_topic(other.current_topic)
        asyncio.run(other._plan_research(1))
        foreign = [q["question"] for q in other.db.get_all_questions(limit=200)]
        self.assertEqual([q for q in foreign if "embryo" in q.lower()], [])

    def _run_program_cycle(self, orch, facts=0):
        item = asyncio.run(orch._next_program_item())
        orch.program_item = item
        orch._cycle_start_counts = {"facts": orch.db.count_facts(),
                                   "evidence": orch.db._count("evidence")}
        for index in range(facts):
            _fact(orch.db, orch.current_topic,
                  f"Within-family estimates of polygenic scores for cognition are about "
                  f"{3 + index} percent of variance.")
        orch._cycle_usable_sources = 1 if facts else 0
        asyncio.run(orch._finish_program_cycle())
        return orch.db.get_program_item(item["id"])

    def test_cycle_gains_are_charged_to_the_item(self):
        orch = _orch()
        asyncio.run(orch._ensure_program())

        row = self._run_program_cycle(orch, facts=2)

        self.assertEqual(row["cycles_spent"], 1)
        self.assertEqual(row["facts_gained"], 2)
        self.assertEqual(row["sources_gained"], 1)
        self.assertEqual(row["gain_cycles"], 0)

    def test_empty_cycles_count_as_saturation(self):
        orch = _orch(program_item_budget_cycles=0, program_saturation_cycles=2,
                     program_min_cycles=1)
        asyncio.run(orch._ensure_program())

        row = self._run_program_cycle(orch, facts=0)
        self.assertEqual(row["gain_cycles"], 1)
        row = self._run_program_cycle(orch, facts=0)

        self.assertEqual(row["status"], P.STATUS_DONE)
        self.assertIn("ohne neuen Ertrag", row["close_reason"])

    def test_budget_closes_the_item_with_a_verdict(self):
        orch = _orch(program_item_budget_cycles=2, program_min_cycles=1)
        asyncio.run(orch._ensure_program())

        self._run_program_cycle(orch, facts=2)
        row = self._run_program_cycle(orch, facts=1)

        self.assertEqual(row["status"], P.STATUS_DONE)
        self.assertIn("Zyklenbudget", row["close_reason"])
        verdict = json.loads(row["verdict"])
        self.assertEqual(verdict["favored"], "The within-family effect is small")
        # The verdict was made from collected facts, not from the model's priors.
        self.assertIn("FAKT", orch.planner.last_material)
        self.assertIn("within-family", orch.planner.last_material.lower())

    def test_verdict_records_the_facts_it_was_made_from(self):
        orch = _orch(program_item_budget_cycles=2, program_min_cycles=1)
        asyncio.run(orch._ensure_program())

        self._run_program_cycle(orch, facts=2)
        row = self._run_program_cycle(orch, facts=1)

        ids = json.loads(row["verdict"])["material_fact_ids"]
        self.assertTrue(ids)
        stored = [orch.db._get("facts", fact_id) for fact_id in ids]
        self.assertTrue(all(stored), "every recorded ID must still resolve")
        self.assertTrue(
            any("within-family" in (fact["content"] or "").lower() for fact in stored)
        )
        # The IDs describe exactly the rows the material was built from.
        selected = orch._program_facts(row["question"])
        self.assertEqual(set(ids), {fact["id"] for fact in selected})

    def test_answered_verdict_closes_the_item_early(self):
        orch = _orch(program_item_budget_cycles=20, program_min_cycles=2)
        asyncio.run(orch._ensure_program())

        for _ in range(3):
            row = self._run_program_cycle(orch, facts=1)

        self.assertEqual(row["status"], P.STATUS_DONE)
        self.assertIn("Beantwortet", row["close_reason"])

    def test_item_without_material_gets_no_verdict(self):
        orch = _orch(_FakePlanner(verdict={"favored": "", "reasoning": ""}),
                     program_item_budget_cycles=1, program_min_cycles=1)
        asyncio.run(orch._ensure_program())

        row = self._run_program_cycle(orch, facts=0)

        self.assertEqual(row["status"], P.STATUS_DONE)
        self.assertEqual(json.loads(row["verdict"] or "{}"), {})

    def test_program_exhaustion_is_recorded(self):
        orch = _orch(program_item_budget_cycles=1, program_min_cycles=1)
        asyncio.run(orch._ensure_program())

        for _ in range(3):
            self._run_program_cycle(orch, facts=1)

        self.assertTrue(orch.status.get("program_exhausted"))
        self.assertIsNone(asyncio.run(orch._next_program_item()))

    def test_status_payload_lists_the_program(self):
        orch = _orch()
        asyncio.run(orch._ensure_program())
        self._run_program_cycle(orch, facts=1)

        status = orch.get_status()

        self.assertEqual(status["program"]["counts"]["total"], 3)
        self.assertEqual(status["program"]["counts"]["active"], 1)
        entry = status["program"]["items"][0]
        self.assertIn("marginal_value", entry)
        self.assertIn("question", entry)


class TestProgramReport(unittest.TestCase):
    def test_report_contains_the_program_and_its_verdicts(self):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        db = Database(os.path.join(tmp, "r.db"))
        topic = "Polygenic embryo selection"
        db.save_program_item(_item(
            topic=topic, question="How large is the polygenic score effect?",
            kind="measurement", status=P.STATUS_DONE, cycles_spent=5,
            facts_gained=7, sources_gained=4, close_reason="Zyklenbudget ausgeschöpft",
            verdict=json.dumps({"favored": "The effect is small", "confidence": 0.6,
                                "reasoning": "within-family estimates are lower",
                                "discriminating_test": "sibling design",
                                "answered": True}),
        ))
        db.save_program_item(_item(topic=topic, question="Which countries regulate it?",
                                   kind="context", importance=0.4))

        path = build_report(db, topic, reason="test", out_dir=os.path.join(tmp, "reports"))
        text = Path(path).read_text(encoding="utf-8")

        self.assertIn("## Forschungsprogramm", text)
        self.assertIn("How large is the polygenic score effect?", text)
        self.assertIn("Zyklenbudget ausgeschöpft", text)
        self.assertIn("### Verdikte je Teilfrage", text)
        self.assertIn("Evidenz spricht für: The effect is small", text)
        self.assertIn("Würde es entscheiden: sibling design", text)
        self.assertIn("### Nächste Teilfragen (nach Grenznutzen)", text)


if __name__ == "__main__":
    unittest.main()
