"""Tests for the meta design family: power, bias and coverage studies.

A meta hypothesis is about a statistical procedure, not about one dataset, so
the protocol carries a grid of sample sizes, a number of inner trials and a
threshold. These tests pin down that promise: the metric is computed over inner
studies, the verdict compares it with the threshold, and a missing grid or a
shortened trial count is reported as a preregistration deviation.
"""

import asyncio
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.experiments.coder import SimulationWriter
from research_agent.experiments.interpreter import check_compliance, interpret
from research_agent.experiments.lab import SimulationLab
from research_agent.experiments.protocol import ExperimentProtocol
from research_agent.experiments.runner import ScriptRunner, contract_problems
from research_agent.models import now_iso


def _meta_protocol(**overrides):
    data = dict(
        hypothesis_id="h1",
        claim="Power of a two-group t-test at n=200 is at least 0.6 for d=0.5",
        prediction="power at n=200 is at least 0.6",
        falsification="power at n=200 stays below 0.6",
        design="power simulation over a grid of sample sizes",
        population="two normal groups",
        n=200,
        effect=0.5,
        noise=1.0,
        metric="power",
        test="two-sample t-test",
        alpha=0.05,
        seed=7,
        replications=5,
        design_type="meta",
        metric_kind="power",
        trials=200,
        grid=[50, 100, 200],
        threshold=0.6,
        comparison="at_least",
    )
    data.update(overrides)
    return ExperimentProtocol(**data)


def _meta_result(values, p_values, **overrides):
    data = {
        "n": 200,
        "metric": "power at n=200",
        "test": "binomial test against 0.6",
        "alpha": 0.05,
        "seed": 7,
        "replications": len(values),
        "value": sum(values) / len(values),
        "ci_low": min(values),
        "ci_high": max(values),
        "p_value": sorted(p_values)[len(p_values) // 2],
        "values": values,
        "p_values": p_values,
        "cells": [
            {"n": 50, "metric": 0.30, "trials": 200},
            {"n": 100, "metric": 0.55, "trials": 200},
            {"n": 200, "metric": 0.90, "trials": 200},
        ],
        "grid": [50, 100, 200],
        "trend": 1.0,
    }
    data.update(overrides)
    return data


META_SCRIPT = '''import json
import numpy as np
from scipy import stats
import sim_params as P

ALT = "greater" if P.COMPARISON == "at_least" else "less"


def cell(seed, n, noise):
    rng = np.random.default_rng(seed)
    hits, devs = 0, []
    for _ in range(P.TRIALS):
        a = rng.normal(0.0, noise, n)
        b = rng.normal(P.EFFECT, noise, n)
        t = stats.ttest_ind(a, b, equal_var=False)
        est = float(b.mean() - a.mean())
        devs.append(abs(est - P.EFFECT))
        ci = t.confidence_interval(0.95)
        if P.METRIC_KIND == "power":
            hits += int(t.pvalue < P.ALPHA)
        elif P.METRIC_KIND == "coverage":
            hits += int(ci.low <= P.EFFECT <= ci.high)
    if P.METRIC_KIND == "bias":
        return float(np.mean(devs)), devs
    return hits / P.TRIALS, None


def threshold_p(hits, devs):
    if P.METRIC_KIND == "bias":
        return float(stats.ttest_1samp(devs, P.THRESHOLD, alternative=ALT).pvalue)
    return float(stats.binomtest(int(round(hits * P.TRIALS)), P.TRIALS,
                                 P.THRESHOLD, alternative=ALT).pvalue)


values, p_values, acc = [], [], {}
for r in range(P.REPLICATIONS):
    ref = (None, None)
    for n in P.GRID:
        metric, devs = cell(P.SEED + r, n, P.NOISE)
        acc.setdefault(n, []).append(metric)
        if n == P.REFERENCE_N:
            ref = (metric, devs)
            values.append(metric)
    p_values.append(threshold_p(ref[0], ref[1]))

cells = [{"n": n, "metric": float(np.mean(v)), "trials": P.TRIALS}
         for n, v in sorted(acc.items())]
deltas = [b["metric"] - a["metric"] for a, b in zip(cells, cells[1:])]
stepping = sum(1 for d in deltas if (d <= 0 if P.METRIC_KIND == "bias" else d >= 0))
trend = stepping / len(deltas) if deltas else 0.0

sensitivity = []
for mult in (0.5, 2.0):
    metric, devs = cell(P.SEED, P.REFERENCE_N, P.NOISE * mult)
    sensitivity.append({"noise_multiplier": mult, "value": metric,
                        "p_value": threshold_p(metric, devs)})

print(json.dumps({
    "n": P.REFERENCE_N, "metric": P.METRIC_KIND, "test": "binomial vs threshold",
    "alpha": P.ALPHA, "seed": P.SEED, "replications": P.REPLICATIONS,
    "value": float(np.mean(values)), "ci_low": float(np.min(values)),
    "ci_high": float(np.max(values)), "p_value": float(np.median(p_values)),
    "values": values, "p_values": p_values, "sensitivity": sensitivity,
    "cells": cells, "grid": P.GRID, "trend": trend,
}))
'''


class _FakeLLM:
    def __init__(self, chat_replies=None, json_replies=None):
        self.chat_replies = list(chat_replies or [])
        self.json_replies = list(json_replies or [])
        self.prompts = []

    async def chat(self, *args, **kwargs):
        if args:
            self.prompts.append(args[0])
        return self.chat_replies.pop(0) if self.chat_replies else ""

    async def chat_json(self, *args, **kwargs):
        if args:
            self.prompts.append(args[0])
        return self.json_replies.pop(0) if self.json_replies else {}


class TestMetaProtocol(unittest.TestCase):
    def test_valid_meta_protocol(self):
        ok, reason = _meta_protocol().validate()
        self.assertTrue(ok, reason)
        self.assertTrue(_meta_protocol().is_meta)

    def test_roundtrip_keeps_meta_fields(self):
        back = ExperimentProtocol.from_dict(_meta_protocol().to_dict())
        self.assertEqual(back.design_type, "meta")
        self.assertEqual(back.metric_kind, "power")
        self.assertEqual(back.grid, [50, 100, 200])
        self.assertEqual(back.trials, 200)
        self.assertAlmostEqual(back.threshold, 0.6)

    def test_rejects_too_few_trials(self):
        ok, reason = _meta_protocol(trials=10).validate()
        self.assertFalse(ok)
        self.assertIn("trials", reason)

    def test_rejects_unknown_metric_kind(self):
        ok, reason = _meta_protocol(metric_kind="vibes").validate()
        self.assertFalse(ok)
        self.assertIn("metric_kind", reason)

    def test_rejects_a_grid_that_does_not_contain_n(self):
        ok, reason = _meta_protocol(grid=[50, 100, 150]).validate()
        self.assertFalse(ok)
        self.assertIn("not one of the grid", reason)

    def test_rejects_a_non_increasing_grid(self):
        ok, reason = _meta_protocol(grid=[200, 100], n=200).validate()
        self.assertFalse(ok)
        self.assertIn("strictly increasing", reason)

    def test_rejects_a_proportion_outside_zero_one(self):
        ok, reason = _meta_protocol(threshold=1.4).validate()
        self.assertFalse(ok)
        self.assertIn("proportion", reason)

    def test_bias_accepts_a_tolerance_above_one(self):
        ok, reason = _meta_protocol(
            metric_kind="bias", threshold=0.05, comparison="at_most"
        ).validate()
        self.assertTrue(ok, reason)

    def test_rejects_unknown_comparison(self):
        ok, reason = _meta_protocol(comparison="roughly").validate()
        self.assertFalse(ok)
        self.assertIn("comparison", reason)


class TestMetaParams(unittest.TestCase):
    def test_full_run_gets_the_preregistered_numbers(self):
        params = ScriptRunner.protocol_params(_meta_protocol())
        self.assertEqual(params["GRID"], [50, 100, 200])
        self.assertEqual(params["TRIALS"], 200)
        self.assertEqual(params["REFERENCE_N"], 200)
        self.assertAlmostEqual(params["THRESHOLD"], 0.6)
        self.assertEqual(params["COMPARISON"], "at_least")
        self.assertEqual(params["METRIC_KIND"], "power")

    def test_smoke_test_gets_one_small_cell(self):
        params = ScriptRunner.protocol_params(_meta_protocol(), n=30, replications=1,
                                              smoke=True)
        self.assertEqual(params["GRID"], [30])
        self.assertLessEqual(params["TRIALS"], 20)
        self.assertEqual(params["REPLICATIONS"], 1)
        self.assertEqual(params["REFERENCE_N"], 30)

    def test_meta_result_needs_cells(self):
        problems = contract_problems(_meta_result([0.9] * 5, [1e-6] * 5), require_cells=True)
        self.assertEqual(problems, [])
        without = _meta_result([0.9] * 5, [1e-6] * 5)
        without.pop("cells")
        self.assertIn("cells", " ".join(contract_problems(without, require_cells=True)))


class TestMetaVerdict(unittest.TestCase):
    def test_metric_above_threshold_supports(self):
        verdict = interpret(_meta_protocol(),
                            _meta_result([0.90, 0.92, 0.88, 0.91, 0.89], [1e-6] * 5))
        self.assertEqual(verdict.evidence_type, "supports")
        self.assertEqual(verdict.replication_rate, 1.0)
        self.assertIn("vs 0.6 (at_least)", verdict.reasoning)
        self.assertEqual(verdict.deviations, [])

    def test_metric_below_threshold_contradicts(self):
        verdict = interpret(_meta_protocol(),
                            _meta_result([0.30, 0.32, 0.28, 0.31, 0.29], [1e-6] * 5))
        self.assertEqual(verdict.evidence_type, "contradicts")
        self.assertIn("wrong side of the threshold", verdict.reasoning)

    def test_threshold_with_at_most_judges_the_other_side(self):
        protocol = _meta_protocol(
            metric_kind="bias", threshold=0.05, comparison="at_most",
            claim="Absolute bias of the estimator at n=200 stays at or below 0.05",
            prediction="bias at n=200 is at most 0.05",
            falsification="bias above 0.05",
            metric="bias",
        )
        ok, reason = protocol.validate()
        self.assertTrue(ok, reason)
        verdict = interpret(protocol, _meta_result(
            [0.02, 0.03, 0.02, 0.04, 0.01], [0.01] * 5
        ))
        self.assertEqual(verdict.evidence_type, "supports")

    def test_grid_trend_is_reported(self):
        verdict = interpret(_meta_protocol(),
                            _meta_result([0.90] * 5, [1e-6] * 5, trend=0.5))
        self.assertIn("grid trend", verdict.reasoning)

    def test_single_cell_grid_makes_no_trend_claim(self):
        # A one-cell grid has no adjacent steps; "100% as predicted" would be a
        # claim about nothing.
        result = _meta_result(
            [0.90] * 5, [1e-6] * 5, trend=1.0,
            cells=[{"n": 200, "metric": 0.9, "trials": 200}], grid=[200],
        )
        verdict = interpret(_meta_protocol(), result)
        self.assertNotIn("grid trend", verdict.reasoning)

    def test_shortened_trials_are_a_deviation(self):
        result = _meta_result([0.9] * 5, [1e-6] * 5)
        for cell in result["cells"]:
            cell["trials"] = 50
        deviations = " | ".join(check_compliance(_meta_protocol(), result))
        self.assertIn("inner trials", deviations)

    def test_missing_grid_is_a_deviation(self):
        result = _meta_result([0.9] * 5, [1e-6] * 5)
        result.pop("grid")
        deviations = " | ".join(check_compliance(_meta_protocol(), result))
        self.assertIn("grid of sample sizes", deviations)


class TestMetaLabRun(unittest.TestCase):
    """A real subprocess meta study through the whole pipeline."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(":memory:")
        self.hypothesis = {
            "id": "h1",
            "claim": "Power of a two-group t-test at n=200 is at least 0.6 for d=0.5",
            "predictions": '["power at n=200 is at least 0.6"]',
            "falsification_conditions": '["power at n=200 stays below 0.6"]',
            "confidence": 0.5,
            "status": "active",
        }
        self.db.save_hypothesis({**self.hypothesis, "date_added": now_iso()})
        self.protocol_json = {"designable": True, "protocol": _meta_protocol().to_dict()}

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, llm):
        lab = SimulationLab(
            self.db, llm, base_dir=self.tmp.name, timeout=120,
            smoke_n=30, smoke_timeout=60, max_attempts=3,
            runner=ScriptRunner(base_dir=self.tmp.name, timeout=120),
        )
        return asyncio.run(lab.run(self.hypothesis, topic="power"))

    def test_meta_study_runs_and_verdict_follows_the_threshold(self):
        llm = _FakeLLM(
            chat_replies=[META_SCRIPT],
            json_replies=[
                self.protocol_json,
                {"approved": True, "problems": []},
                {"tests_the_prediction": True, "concerns": []},
            ],
        )
        outcome = self._run(llm)
        self.assertTrue(outcome["ok"], outcome["note"])
        evidence = outcome["evidence"]
        self.assertEqual(evidence["evidence_type"], "supports")
        self.assertAlmostEqual(evidence["strength"], 0.6)

        experiment = self.db.get_experiment(evidence["experiment_id"])
        self.assertEqual(experiment["design_type"], "meta")
        self.assertEqual(experiment["status"], "completed")
        result = json.loads(experiment["result"])
        self.assertEqual(result["grid"], [50, 100, 200])
        self.assertEqual(len(result["cells"]), 3)
        self.assertGreaterEqual(result["cells"][-1]["metric"], 0.6)
        self.assertEqual(json.loads(experiment["deviations"]), [])
        self.assertEqual(experiment["attempts"], 1)


class TestReviewerContext(unittest.TestCase):
    def test_reviewer_sees_the_generated_parameters(self):
        from research_agent.experiments.review import ScriptReviewer

        llm = _FakeLLM(json_replies=[{"approved": True, "problems": []}])
        params = ScriptRunner.protocol_params(_meta_protocol())
        asyncio.run(ScriptReviewer(llm).review(
            _meta_protocol(), META_SCRIPT,
            smoke={"params": {"N": 30}, "stdout": "{}"}, params=params,
        ))
        prompt = " ".join(
            str(message.get("content", ""))
            for messages in llm.prompts for message in messages
        )
        self.assertIn("sim_params contains exactly", prompt)
        self.assertIn("REFERENCE_N=200", prompt)


class TestMetaWriter(unittest.TestCase):
    def test_writer_uses_the_meta_contract(self):
        llm = _FakeLLM(chat_replies=[META_SCRIPT])
        code, error = asyncio.run(SimulationWriter(llm).write(_meta_protocol()))
        self.assertTrue(code, error)
        prompt = " ".join(
            str(message.get("content", ""))
            for messages in llm.prompts for message in messages
        )
        self.assertIn("GRID", prompt)
        self.assertIn("TRIALS", prompt)
        self.assertIn("REFERENCE_N", prompt)


if __name__ == "__main__":
    unittest.main()
