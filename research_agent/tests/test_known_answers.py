"""Tests for known-answer tests (experiments/validity.py).

The point of these checks is to catch a routine that runs fine and reports
numbers that theory forbids. The tests therefore pair a correct routine with
deliberately broken ones and assert that the broken ones fail - not that the
plumbing calls the right function.
"""

import asyncio
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.experiments.lab import SimulationLab
from research_agent.experiments.protocol import ExperimentProtocol
from research_agent.experiments.runner import ScriptRunner
from research_agent.experiments.validity import (
    KnownAnswerTest,
    analytic_t_power,
    analytic_t_power_options,
    looks_like_t_test,
)
from research_agent.models import now_iso
from research_agent.tests.test_meta_design import META_SCRIPT


def _meta_protocol(**overrides):
    data = dict(
        hypothesis_id="h1",
        claim="Power of a two-group t-test at n=200 is at least 0.6 for d=0.3",
        prediction="power at n=200 is at least 0.6",
        falsification="power at n=200 stays below 0.6",
        design="power simulation over the grid",
        population="two normal groups",
        n=200,
        effect=0.3,
        noise=1.0,
        metric="power",
        test="two-sample t-test",
        alpha=0.05,
        seed=7,
        replications=5,
        design_type="meta",
        metric_kind="power",
        trials=150,
        grid=[200],
        threshold=0.6,
        comparison="at_least",
    )
    data.update(overrides)
    return ExperimentProtocol(**data)


def _one_shot_protocol(**overrides):
    data = dict(
        hypothesis_id="h1",
        claim="Raising a continuous cause raises the outcome by 0.4 per unit",
        prediction="positive slope",
        falsification="no or negative slope",
        design="regression of y on x",
        population="synthetic pairs",
        n=200,
        effect=0.4,
        noise=1.0,
        metric="slope",
        test="ols t-test",
        alpha=0.05,
        seed=7,
        replications=5,
    )
    data.update(overrides)
    return ExperimentProtocol(**data)


ONE_SHOT_SCRIPT = '''import json
import numpy as np
from scipy import stats
import sim_params as P

values, p_values = [], []
for i in range(P.REPLICATIONS):
    rng = np.random.default_rng(P.SEED + i)
    a = rng.normal(0.0, P.NOISE, P.N)
    b = rng.normal(P.EFFECT, P.NOISE, P.N)
    t = stats.ttest_ind(a, b, equal_var=False)
    values.append(float(b.mean() - a.mean()))
    p_values.append(float(t.pvalue))

print(json.dumps({
    "n": P.N, "metric": "mean difference", "test": "t-test", "alpha": P.ALPHA,
    "seed": P.SEED, "replications": P.REPLICATIONS,
    "value": float(np.mean(values)), "ci_low": float(np.min(values)),
    "ci_high": float(np.max(values)), "p_value": float(np.median(p_values)),
    "values": values, "p_values": p_values,
}))
'''


def _broken_meta(*, force_significant=False, double_effect=False,
                  unseeded=False):
    """META_SCRIPT with one deliberate defect."""
    code = META_SCRIPT
    if double_effect:
        code = code.replace("b = rng.normal(P.EFFECT, noise, n)",
                            "b = rng.normal(P.EFFECT * 2.0, noise, n)")
    if force_significant:
        code = code.replace("            hits += int(t.pvalue < P.ALPHA)",
                            "            hits += 1")
    if unseeded:
        code = code.replace("rng = np.random.default_rng(seed)",
                            "rng = np.random.default_rng()")
    return code


class TestAnalyticPower(unittest.TestCase):
    def test_matches_the_textbook_values(self):
        # Standard table: n=100 per group, d=0.5 -> about 0.94;
        # n=200 puts it at the ceiling; no effect -> alpha.
        self.assertAlmostEqual(analytic_t_power(100, 0.5, 1.0), 0.94, places=2)
        self.assertGreater(analytic_t_power(200, 0.5, 1.0), 0.998)
        self.assertAlmostEqual(analytic_t_power(200, 0.0, 1.0), 0.05, places=3)

    def test_power_grows_with_effect_and_sample(self):
        small = analytic_t_power(100, 0.3, 1.0)
        large = analytic_t_power(100, 0.6, 1.0)
        self.assertLess(small, large)
        self.assertLess(small, analytic_t_power(200, 0.3, 1.0))

    def test_noise_works_like_a_smaller_effect(self):
        self.assertAlmostEqual(
            analytic_t_power(100, 0.6, 2.0), analytic_t_power(100, 0.3, 1.0), places=6
        )


class TestMetaKnownAnswers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runner = ScriptRunner(base_dir=self.tmp.name, timeout=120)
        # 400 inner trials: below that, a power of 0.92 and a power of 1.0 are
        # not far enough apart to be told apart at the tolerance used here.
        self.kat = KnownAnswerTest(self.runner, trials=400)

    def tearDown(self):
        self.tmp.cleanup()

    def _check(self, code, protocol=None):
        return asyncio.run(self.kat.run(
            "kat", protocol or _meta_protocol(), code
        ))

    def test_correct_routine_passes(self):
        report = self._check(META_SCRIPT)
        self.assertTrue(report.passed, report.failures)
        names = " | ".join(check.name for check in report.checks)
        self.assertIn("null rate is alpha", names)
        self.assertIn("effect scaling", names)
        self.assertIn("deterministic", names)
        self.assertIn("analytic t-test power", names)

    def test_inflated_effect_is_caught_by_the_analytic_anchor(self):
        report = self._check(_broken_meta(double_effect=True))
        self.assertFalse(report.passed)
        self.assertIn("analytic t-test power", " | ".join(report.failures))

    def test_always_significant_is_caught_by_the_null_rate(self):
        report = self._check(_broken_meta(force_significant=True))
        self.assertFalse(report.passed)
        self.assertIn("null rate", " | ".join(report.failures))

    def test_unseeded_randomness_is_caught(self):
        report = self._check(_broken_meta(unseeded=True))
        self.assertFalse(report.passed)
        self.assertIn("deterministic", " | ".join(report.failures))

    def test_parametrised_routine_is_not_special_casing(self):
        # The correct script reads sim_params, so changing EFFECT changes the
        # answer; a script with hardcoded d would fail the scaling check.
        report = self._check(META_SCRIPT, _meta_protocol(effect=0.5, n=100))
        self.assertTrue(report.passed, report.failures)

    def test_power_that_never_reaches_one_is_caught(self):
        # Capped at 0.5: the null rate and the scaling still look fine, but no
        # consistent test fails to reject an effect of d=5.
        code = META_SCRIPT.replace(
            "    return hits / P.TRIALS, None",
            "    return min(0.5, hits / P.TRIALS), None",
        )
        report = self._check(code)
        self.assertFalse(report.passed)
        self.assertIn("overwhelming effect", " | ".join(report.failures))

    def test_one_sided_routine_is_judged_against_one_sided_power(self):
        # A one-sided test has more power than a two-sided one. Judging it
        # against the two-sided number would reject a correct routine.
        # The effect sits in group b, so the correct one-sided alternative is
        # "less" (mean(a) < mean(b)); the other one would give power 0.
        code = META_SCRIPT.replace(
            "t = stats.ttest_ind(a, b, equal_var=False)",
            't = stats.ttest_ind(a, b, equal_var=False, alternative="less")',
        )
        report = self._check(code, _meta_protocol(effect=0.3, n=200))
        self.assertTrue(report.passed, report.failures)
        detail = " | ".join(c.detail for c in report.checks
                            if "analytic t-test power" in c.name)
        self.assertIn("(one-sided;", detail)

    def test_both_analytic_answers_are_offered(self):
        options = dict(analytic_t_power_options(200, 0.3, 1.0))
        self.assertAlmostEqual(options["two-sided"], 0.848, places=2)
        self.assertGreater(options["one-sided"], options["two-sided"])

    def test_t_test_written_by_hand_still_gets_the_anchor(self):
        # No `ttest_ind` anywhere: the effect is inflated by hand, and only the
        # analytic anchor can see it.
        code = META_SCRIPT.replace(
            "        t = stats.ttest_ind(a, b, equal_var=False)\n",
            "        diff = b.mean() - a.mean()\n"
            "        se = np.sqrt(a.var(ddof=1) / n + b.var(ddof=1) / n)\n"
            "        tval = diff / se\n"
            "        pval = 2.0 * stats.t.sf(abs(tval), 2 * n - 2)\n"
            "        t = type('R', (), {'pvalue': pval,\n"
            "                          'confidence_interval': lambda s, c:\n"
            "                          type('CI', (), {'low': diff - 1.96 * se,\n"
            "                                          'high': diff + 1.96 * se})()})()\n",
        ).replace(
            "b = rng.normal(P.EFFECT, noise, n)",
            "b = rng.normal(P.EFFECT * 2.0, noise, n)",
        )
        self.assertNotIn("ttest_ind", code)
        self.assertTrue(looks_like_t_test(code, ""))
        report = self._check(code, _meta_protocol(effect=0.3, n=200))
        self.assertFalse(report.passed)
        self.assertIn("analytic t-test power", " | ".join(report.failures))


class TestOneShotKnownAnswers(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runner = ScriptRunner(base_dir=self.tmp.name, timeout=120)
        self.kat = KnownAnswerTest(self.runner, trials=100)

    def tearDown(self):
        self.tmp.cleanup()

    def _check(self, code, protocol=None):
        return asyncio.run(self.kat.run(
            "kat", protocol or _one_shot_protocol(), code
        ))

    def test_correct_estimator_passes(self):
        report = self._check(ONE_SHOT_SCRIPT)
        self.assertTrue(report.passed, report.failures)
        names = " | ".join(check.name for check in report.checks)
        self.assertIn("no effect means no finding", names)
        self.assertIn("estimate scales with the effect", names)

    def test_ignoring_the_effect_is_caught(self):
        code = ONE_SHOT_SCRIPT.replace(
            "b = rng.normal(P.EFFECT, P.NOISE, P.N)",
            "b = rng.normal(0.0, P.NOISE, P.N)",
        )
        report = self._check(code)
        self.assertFalse(report.passed)
        self.assertIn("estimate scales with the effect", " | ".join(report.failures))

    def test_always_significant_is_caught(self):
        code = ONE_SHOT_SCRIPT.replace(
            "p_values.append(float(t.pvalue))", "p_values.append(1e-9)"
        )
        report = self._check(code)
        self.assertFalse(report.passed)
        self.assertIn("no effect means no finding", " | ".join(report.failures))

    def test_estimator_with_an_offset_is_caught(self):
        # Unbiasedness is analytic: with no effect the estimate must sit at 0.
        # The p-values here stay honest, so only the offset check can fire.
        code = ONE_SHOT_SCRIPT.replace(
            "values.append(float(b.mean() - a.mean()))",
            "values.append(float(b.mean() - a.mean() + 0.5))",
        )
        report = self._check(code)
        self.assertFalse(report.passed)
        self.assertIn("centred on zero", " | ".join(report.failures))
        self.assertNotIn("no effect means no finding", " | ".join(report.failures))


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


class TestLabBlocksOnFailingRoutine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(":memory:")
        self.hypothesis = {
            "id": "h1",
            "claim": "Power of a two-group t-test at n=200 is at least 0.6 for d=0.3",
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
            kat_trials=400, runner=ScriptRunner(base_dir=self.tmp.name, timeout=120),
        )
        return asyncio.run(lab.run(self.hypothesis, topic="power"))

    def test_known_answer_failure_triggers_a_rewrite_and_is_recorded(self):
        llm = _FakeLLM(
            chat_replies=[_broken_meta(double_effect=True), META_SCRIPT],
            json_replies=[
                self.protocol_json,
                {"approved": True, "problems": []},
                {"tests_the_prediction": True, "concerns": []},
            ],
        )
        outcome = self._run(llm)
        self.assertTrue(outcome["ok"], outcome["note"])
        experiment = self.db.get_experiment(outcome["experiment_id"])
        self.assertEqual(experiment["attempts"], 2)
        checks = json.loads(experiment["validity"])
        self.assertTrue(checks)
        self.assertTrue(all(check["passed"] for check in checks), checks)
        self.assertIn("known-answer test failed", " ".join(
            str(message.get("content", ""))
            for messages in llm.prompts for message in messages
        ))

    def test_routine_that_never_convinces_produces_no_evidence(self):
        llm = _FakeLLM(
            chat_replies=[_broken_meta(force_significant=True)] * 3,
            json_replies=[self.protocol_json],
        )
        outcome = self._run(llm)
        self.assertFalse(outcome["ok"])
        self.assertIsNone(outcome["evidence"])
        experiment = self.db.get_experiment(outcome["experiment_id"])
        self.assertEqual(experiment["status"], "failed")
        self.assertIn("known-answer test failed", experiment["error"])
        checks = json.loads(experiment["validity"])
        self.assertTrue(any(not check["passed"] for check in checks))


if __name__ == "__main__":
    unittest.main()
