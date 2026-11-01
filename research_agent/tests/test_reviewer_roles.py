"""Phase 3 tests (order §6): independence, statistical review, resolver."""

import json
import unittest
from typing import Any, Dict, List

from research_agent.database import Database
from research_agent.meta.reviewer_roles import (
    extractor_independence_check, resolve_disputes, statistical_review)


class IndependenceContractTest(unittest.TestCase):
    """Abnahmekriterium: "Extractor B receives no results from A at context"."""

    def test_second_pass_is_built_from_document_only(self):
        captured: List[List[dict]] = []

        class FakeLLM:
            async def chat_json(self, messages, temperature=0.2, max_tokens=4096):
                captured.append(actual := [m.get("content", "") for m in messages])
                if len(captured) == 1:
                    # pass A's honest JSON reading (would poison B if reused)
                    return json.dumps([
                        {"outcome": "depressive symptoms", "comparison":
                         "exercise vs control", "effect_type": "smd",
                         "effect": -0.4290, "se": 0.11,
                         "unit": "SM", "direction": "negative"}])
                return json.dumps([
                    {"outcome": "depressive symptoms", "comparison":
                     "exercise vs control", "effect_type": "smd",
                     "effect": -0.30, "se": 0.2,
                     "unit": "SM", "direction": "negative"}])

        from research_agent.meta.extraction import EffectExtractor
        db = Database(":memory:")
        extractor = EffectExtractor(FakeLLM(), db, double_pass=True)
        text = ("A long paper body with the effect sizes written out clearly. " * 100)
        rows = _run(extractor.extract("src-x", text))

        # both passes saw messages; the second pass's context must NOT include
        # any value string of the first pass output.
        self.assertEqual(len(captured), 2)
        violations = extractor_independence_check(
            [{"content": c} for c in captured[1]],
            first_pass_values=("-0.4290", "exercise vs control", "smd"))
        # a value string from A software must not appear in B's context
        self.assertEqual([v for v in violations if "-0.4290" in v], [])
        # and the contract tool marks real contamination loudly if it appears
        # value string of at least 8 chars: a single short substring like
        # "0.55" occurs in prose too, so the rule guards against those hits.
        poisoned = [{"content": "previous reading: -0.429053 please reconcile"}]
        self.assertTrue(any("-0.429053" in v
                            for v in extractor_independence_check(
                                poisoned, ("-0.429053",))))


def _run(coro):
    import asyncio
    return asyncio.get_event_loop().run_until_complete(coro) \
        if not hasattr(asyncio, "run") else asyncio.run(coro)


class StatisticalReviewTest(unittest.TestCase):
    def test_rule_violations_reported_without_computation(self):
        rows = [
            {"id": "r1", "effect": -0.4, "se": 0.1, "ci_low": -0.7, "ci_high": -0.1},
            {"id": "r2", "effect": 0.3, "se": 0.0, "ci_low": 0.0, "ci_high": 0.6},
            {"id": "r3", "effect_type": "or", "effect": -1.5},
            {"id": "r4", "effect_type": "r", "effect": 1.4},
            {"id": "r5", "effect": 0.2, "se": 0.05, "ci_low": 0.5, "ci_high": 0.9},
        ]
        rep = statistical_review(rows)
        self.assertEqual(rep.role, "statistical_reviewer")
        rules = {f["rule"] for f in rep.detail["findings"]}
        self.assertIn("se_nonpositive", rules)         # r2
        self.assertIn("ratio_nonpositive", rules)      # r3
        self.assertIn("correlation_out_of_range", rules)  # r4
        self.assertIn("effect_outside_ci", rules)      # r5
        self.assertNotIn("ci_inverted", rules)
        # decision and confidence carry a structured version tag
        self.assertEqual(rep.decision, "findings_reported")
        self.assertTrue(rep.version.startswith("reviewer-roles/"))

    def test_clean_rows_report_no_findings(self):
        rep = statistical_review([
            {"id": "ok", "effect": -0.4, "se": 0.1, "ci_low": -0.7, "ci_high": -0.1}])
        self.assertEqual(rep.decision, "no_statistical_findings")
        self.assertEqual(rep.detail["findings"], [])


class DecisionResolverTest(unittest.TestCase):
    def test_one_verified_reading_resolves_from_original_evidence(self):
        db = Database(":memory:")
        rows = [
            {"id": "d1", "outcome": "bp", "comparison": "a vs b", "disputed": 1,
             "quote_start": 10, "source_text_id": "t1", "quote": "HR 0.72 [0.55;0.94]"},
            {"id": "d2", "outcome": "bp", "comparison": "a vs b", "disputed": 1,
             "quote_start": -1, "source_text_id": "", "quote": "HR 0.9"},
        ]
        rep, escalations = resolve_disputes(db, rows)
        self.assertEqual(escalations, 0)
        res = rep.detail["resolutions"]
        self.assertEqual(res[0]["resolution"], "resolved_by_original_evidence")
        self.assertEqual(res[0]["kept_row"], "d1")
        # report stored immutably
        with db._conn() as conn:
            n = conn.execute("SELECT COUNT(*) FROM review_reports").fetchone()[0]
        self.assertEqual(n, 1)

    def test_conflicting_verified_readings_escalate(self):
        db = Database(":memory:")
        rows = [
            {"id": "e1", "outcome": "iq", "comparison": "g vs c", "disputed": 1,
             "quote_start": 3, "source_text_id": "t1", "quote": "SMD -0.30"},
            {"id": "e2", "outcome": "iq", "comparison": "g vs c", "disputed": 1,
             "quote_start": 44, "source_text_id": "t1", "quote": "SMD -0.55"},
        ]
        rep, escalations = resolve_disputes(db, rows)
        self.assertEqual(escalations, 2)
        self.assertEqual(
            rep.detail["resolutions"][0]["resolution"], "escalated")
        self.assertTrue(rep.unresolved_questions)

    def test_undecidable_without_evidence_escalates(self):
        db = Database(":memory:")
        rows = [
            {"id": "f1", "outcome": "x", "comparison": "y", "disputed": 1,
             "quote_start": -1, "source_text_id": ""},
            {"id": "f2", "outcome": "x", "comparison": "y", "disputed": 1,
             "quote_start": -1, "source_text_id": ""},
        ]
        rep, escalations = resolve_disputes(db, rows)
        self.assertEqual(escalations, 2)


if __name__ == "__main__":
    unittest.main()
