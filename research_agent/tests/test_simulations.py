"""Tests for the simulation lab.

Offline except for the runner tests, which start a real Python subprocess (that
is the thing under test: sandbox, timeout, JSON parsing, network block).
"""

import asyncio
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.config import Config
from research_agent.database import Database
from research_agent.experiments.coder import (
    SimulationWriter,
    check_imports,
    check_uses_params,
)
from research_agent.experiments.interpreter import (
    audit_script,
    check_compliance,
    interpret,
)
from research_agent.experiments.lab import SimulationLab
from research_agent.experiments.protocol import ExperimentProtocol
from research_agent.experiments.runner import ScriptRunner, parse_result
from research_agent.models import gen_id, now_iso
from research_agent.orchestrator import ResearchOrchestrator
from research_agent.work_queue import KIND_SIMULATION, WorkQueue


def _protocol(**overrides):
    data = dict(
        hypothesis_id="h1",
        claim="Polygenic scores for educational attainment predict school grades",
        prediction="Higher PGS means higher grades (positive effect)",
        falsification="No association in a simulated sibling comparison",
        design="Simulated sibling pairs with shared family effect",
        population="synthetic sibling pairs",
        n=400,
        effect=0.4,
        noise=1.0,
        metric="grade difference per PGS SD",
        test="two-sided t-test",
        alpha=0.05,
        seed=7,
    )
    data.update(overrides)
    return ExperimentProtocol(**data)


def _replicated_result(**overrides):
    """A study that ran the preregistered replications, all significant."""
    values = [0.40, 0.42, 0.39, 0.41, 0.38]
    data = dict(
        n=400,
        metric="grade difference per PGS SD",
        test="two-sided t-test",
        alpha=0.05,
        seed=7,
        replications=5,
        value=sum(values) / len(values),
        ci_low=0.34,
        ci_high=0.46,
        p_value=1e-6,
        values=values,
        p_values=[1e-6, 2e-7, 3e-6, 1e-7, 2e-5],
        significant_share=1.0,
        direction_share=1.0,
        sensitivity=[
            {"noise_multiplier": 0.5, "value": 0.41, "p_value": 1e-6},
            {"noise_multiplier": 2.0, "value": 0.33, "p_value": 1e-3},
        ],
    )
    data.update(overrides)
    return data


class _FakeLLM:
    """Returns a scripted reply per call; chat() for code, chat_json() for JSON."""

    def __init__(self, chat_replies=None, json_replies=None, raises=False):
        self.chat_replies = list(chat_replies or [])
        self.json_replies = list(json_replies or [])
        self.raises = raises
        self.calls = 0
        self.prompts = []

    async def chat(self, *args, **kwargs):
        self.calls += 1
        if args:
            self.prompts.append(args[0])
        if self.raises:
            raise RuntimeError("llm down")
        return self.chat_replies.pop(0) if self.chat_replies else ""

    async def chat_json(self, *args, **kwargs):
        self.calls += 1
        if self.raises:
            raise RuntimeError("llm down")
        return self.json_replies.pop(0) if self.json_replies else {}


class TestProtocol(unittest.TestCase):
    def test_valid_protocol(self):
        ok, reason = _protocol().validate()
        self.assertTrue(ok, reason)

    def test_rejects_impossible_parameters(self):
        self.assertFalse(_protocol(n=5).validate()[0])
        self.assertFalse(_protocol(effect=0).validate()[0])
        self.assertFalse(_protocol(noise=0).validate()[0])
        self.assertFalse(_protocol(alpha=0.9).validate()[0])
        self.assertFalse(_protocol(seed=-1).validate()[0])

    def test_rejects_vague_text(self):
        self.assertFalse(_protocol(prediction="yes").validate()[0])

    def test_roundtrip(self):
        protocol = _protocol()
        restored = ExperimentProtocol.from_dict(json.loads(protocol.to_json()))
        self.assertEqual(restored.n, protocol.n)
        self.assertEqual(restored.effect, protocol.effect)
        self.assertEqual(restored.hypothesis_id, "h1")


class TestImportGuard(unittest.TestCase):
    def test_allows_scientific_stack(self):
        ok, _ = check_imports("import numpy as np\nfrom scipy import stats\nimport json")
        self.assertTrue(ok)

    def test_blocks_system_access(self):
        for snippet in ("import os", "import socket", "import subprocess",
                        "from pathlib import Path", "import requests"):
            ok, reason = check_imports(snippet)
            self.assertFalse(ok, snippet)
            self.assertTrue(reason)

    def test_blocks_dynamic_execution(self):
        self.assertFalse(check_imports("eval('1+1')")[0])
        self.assertFalse(check_imports("open('x','w')")[0])

    def test_reports_syntax_errors(self):
        ok, reason = check_imports("def broken(:\n  pass")
        self.assertFalse(ok)
        self.assertIn("syntax", reason.lower())


class TestParamRequirement(unittest.TestCase):
    """The script must take its numbers from the generated module."""

    def test_accepts_import(self):
        ok, reason = check_uses_params("import sim_params as P\nn = P.N\n")
        self.assertTrue(ok, reason)

    def test_accepts_from_import(self):
        ok, reason = check_uses_params("from sim_params import N\nn = N\n")
        self.assertTrue(ok, reason)

    def test_rejects_hardcoded_numbers(self):
        ok, reason = check_uses_params("N = 400\nprint(N)\n")
        self.assertFalse(ok)
        self.assertIn("sim_params", reason)

    def test_rejects_import_without_use(self):
        ok, reason = check_uses_params("import sim_params\nN = 400\n")
        self.assertFalse(ok)
        self.assertIn("never reads", reason)

    def test_importing_sim_params_is_allowed(self):
        self.assertTrue(check_imports("import sim_params as P\n")[0])


class TestRunner(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runner = ScriptRunner(base_dir=self.tmp.name, timeout=20)

    def tearDown(self):
        self.tmp.cleanup()

    def test_runs_a_real_script_and_parses_the_result(self):
        code = (
            "import json\n"
            "import numpy as np\n"
            "rng = np.random.default_rng(7)\n"
            "data = rng.normal(0.3, 1.0, size=200)\n"
            "value = float(data.mean())\n"
            "print(json.dumps({'n': 200, 'metric': 'mean', 'value': value,\n"
            "                  'p_value': 0.01, 'seed': 7, 'test': 't'}))\n"
        )
        outcome = self.runner.run("exp1", code)
        self.assertTrue(outcome["ok"], outcome["error"])
        self.assertEqual(outcome["result"]["n"], 200)
        self.assertAlmostEqual(outcome["result"]["value"], outcome["result"]["value"])
        self.assertTrue(Path(outcome["script_path"]).exists())
        self.assertTrue((Path(self.tmp.name) / "exp1" / "result.json").exists())

    def test_relative_base_dir_runs_from_its_own_directory(self):
        # Regression: cwd is the experiment directory, so a relative base_dir was
        # resolved twice and the sandbox wrapper path did not exist.
        cwd = os.getcwd()
        os.chdir(self.tmp.name)
        try:
            runner = ScriptRunner(base_dir="sims", timeout=20)
            outcome = runner.run(
                "rel1",
                "import json\nprint(json.dumps({'value': 1.0, 'metric': 'm', "
                "'p_value': 0.01}))\n",
            )
        finally:
            os.chdir(cwd)
        self.assertTrue(outcome["ok"], outcome["error"])
        self.assertTrue((Path(self.tmp.name) / "sims" / "rel1" / "sim.py").exists())

    def test_protocol_numbers_are_written_and_read(self):
        code = (
            "import json, sim_params as P\n"
            "print(json.dumps({'n': P.N, 'metric': 'm', 'test': 't',\n"
            "                  'value': P.EFFECT, 'p_value': 0.1,\n"
            "                  'values': [P.EFFECT], 'p_values': [0.1]}))\n"
        )
        params = self.runner.protocol_params(_protocol())
        outcome = self.runner.run("exp_params", code, params)
        self.assertTrue(outcome["ok"], outcome["error"])
        self.assertEqual(outcome["result"]["n"], 400)
        self.assertTrue((Path(self.tmp.name) / "exp_params" / "sim_params.py").exists())

    def test_smoke_test_runs_the_same_script_at_small_n(self):
        code = (
            "import json, sim_params as P\n"
            "print(json.dumps({'n': P.N, 'metric': 'm', 'test': 't',\n"
            "                  'value': 1.0, 'p_value': 0.1,\n"
            "                  'values': [1.0], 'p_values': [0.1]}))\n"
        )
        outcome = asyncio.run(self.runner.smoke_test(
            "exp_smoke", _protocol(), code, n=30
        ))
        self.assertTrue(outcome["ok"], outcome["error"])
        self.assertEqual(outcome["result"]["n"], 30)
        self.assertEqual(outcome["params"]["REPLICATIONS"], 1)

    def test_smoke_test_reports_a_missing_result_line_as_a_problem(self):
        outcome = asyncio.run(self.runner.smoke_test(
            "exp_smoke_bad", _protocol(),
            "import sim_params as P\nprint('only noise', P.N)\n", n=30,
        ))
        self.assertFalse(outcome["ok"])
        self.assertIn("no JSON result line", outcome["error"])

    def test_smoke_test_rejects_an_incomplete_result(self):
        code = (
            "import json, sim_params as P\n"
            "print(json.dumps({'value': 1.0, 'p_value': 0.02}))\n"
        )
        outcome = asyncio.run(self.runner.smoke_test(
            "exp_smoke_partial", _protocol(), code, n=30
        ))
        self.assertFalse(outcome["ok"])
        self.assertIn("'n' is missing", outcome["error"])

    def test_timeout_kills_a_hanging_script(self):
        runner = ScriptRunner(base_dir=self.tmp.name, timeout=2)
        outcome = runner.run("exp_slow", "import time\ntime.sleep(30)\n")
        self.assertFalse(outcome["ok"])
        self.assertTrue(outcome["timed_out"])
        self.assertIn("timeout", outcome["error"].lower())

    def test_network_is_blocked(self):
        code = (
            "import json, socket\n"
            "try:\n"
            "    socket.create_connection(('example.org', 80), timeout=1)\n"
            "    blocked = False\n"
            "except Exception:\n"
            "    blocked = True\n"
            "print(json.dumps({'n': 1, 'metric': 'blocked', 'value': float(blocked),\n"
            "                  'p_value': 1.0, 'seed': 0, 'test': 'none'}))\n"
        )
        outcome = self.runner.run("exp_net", code)
        self.assertTrue(outcome["ok"], outcome["error"])
        self.assertEqual(outcome["result"]["value"], 1.0, "socket must not be reachable")

    def test_missing_result_line_is_an_error(self):
        outcome = self.runner.run("exp_none", "print('hello')\n")
        self.assertFalse(outcome["ok"])
        self.assertIn("JSON", outcome["error"])

    def test_parse_result_takes_the_last_json_object(self):
        stdout = 'noise\n{"value": 1}\nmore\n{"metric": "x", "value": 2, "p_value": 0.1}\n'
        self.assertEqual(parse_result(stdout)["value"], 2)


class TestInterpretation(unittest.TestCase):
    def test_significant_effect_in_predicted_direction_supports(self):
        verdict = interpret(_protocol(), {"p_value": 0.001, "value": 0.4, "n": 400})
        self.assertEqual(verdict.evidence_type, "supports")
        self.assertLessEqual(verdict.strength, 0.6)

    def test_opposite_direction_contradicts(self):
        verdict = interpret(_protocol(), {"p_value": 0.001, "value": -0.4, "n": 400})
        self.assertEqual(verdict.evidence_type, "contradicts")

    def test_null_result_is_neutral(self):
        verdict = interpret(_protocol(), {"p_value": 0.4, "value": 0.01, "n": 400})
        self.assertEqual(verdict.evidence_type, "neutral")

    def test_failed_audit_halves_the_strength(self):
        strong = interpret(_protocol(), _replicated_result())
        flagged = interpret(_protocol(), _replicated_result(),
                            audit={"tests_the_prediction": False,
                                   "concerns": ["outcome not measured"]})
        self.assertEqual(flagged.strength, 0.3, "audit failure caps at half the simulation cap")
        self.assertLess(flagged.strength, strong.strength)
        self.assertIn("audit concern", flagged.reasoning)

    # === Replication ===

    def test_replicated_effect_uses_the_full_cap(self):
        verdict = interpret(_protocol(), _replicated_result())
        self.assertEqual(verdict.evidence_type, "supports")
        self.assertEqual(verdict.strength, 0.6)
        self.assertEqual(verdict.replication_rate, 1.0)
        self.assertEqual(verdict.deviations, [])
        self.assertIn("5/5 replications significant", verdict.reasoning)

    def test_single_run_is_not_a_finding(self):
        single = interpret(_protocol(), {"p_value": 1e-6, "value": 0.4,
                                         "n": 400, "test": "t", "seed": 7})
        replicated = interpret(_protocol(), _replicated_result())
        self.assertEqual(single.evidence_type, "supports")
        self.assertLess(single.strength, replicated.strength)
        self.assertIn("not replicated", single.reasoning)
        self.assertTrue(any("replication" in d for d in single.deviations))

    def test_unstable_significance_is_reported_as_underpowered(self):
        result = _replicated_result(
            p_values=[0.01, 0.30, 0.20, 0.02, 0.40], significant_share=0.4
        )
        verdict = interpret(_protocol(), result)
        self.assertEqual(verdict.evidence_type, "supports")
        self.assertLess(verdict.strength, 0.45)
        self.assertIn("underpowered", verdict.reasoning)

    def test_effect_that_does_not_reproduce_is_neutral(self):
        result = _replicated_result(
            p_values=[0.30, 0.40, 0.20, 0.50, 0.60], significant_share=0.0
        )
        verdict = interpret(_protocol(), result)
        self.assertEqual(verdict.evidence_type, "neutral")
        self.assertIn("did not reproduce", verdict.reasoning)

    def test_mixed_replications_are_inconclusive(self):
        result = _replicated_result(
            values=[0.4, -0.3, 0.2, -0.1, 0.05],
            p_values=[0.01, 0.02, 0.30, 0.20, 0.60],
            significant_share=0.4,
            direction_share=0.6,
        )
        verdict = interpret(_protocol(), result)
        self.assertEqual(verdict.evidence_type, "neutral")
        self.assertIn("inconclusive", verdict.reasoning)

    def test_effect_reproducing_against_the_prediction_contradicts(self):
        result = _replicated_result(
            values=[-0.40, -0.38, -0.42, -0.39, -0.41],
            value=-0.40,
            p_values=[1e-5, 1e-5, 1e-6, 1e-4, 1e-5],
            significant_share=1.0,
            direction_share=0.0,
        )
        verdict = interpret(_protocol(), result)
        self.assertEqual(verdict.evidence_type, "contradicts")

    # === Sensitivity and preregistration compliance ===

    def test_conclusion_that_flips_under_noise_is_downgraded(self):
        broken = _replicated_result(
            sensitivity=[
                {"noise_multiplier": 0.5, "value": 0.41, "p_value": 1e-6},
                {"noise_multiplier": 2.0, "value": -0.02, "p_value": 0.70},
            ]
        )
        stable = interpret(_protocol(), _replicated_result())
        fragile = interpret(_protocol(), broken)
        self.assertEqual(fragile.evidence_type, "supports")
        self.assertLess(fragile.strength, stable.strength)
        self.assertIn("changed noise assumptions", fragile.reasoning)

    def test_missing_sensitivity_is_noted(self):
        verdict = interpret(_protocol(), _replicated_result(sensitivity=[]))
        self.assertIn("no sensitivity analysis", verdict.reasoning)

    def test_preregistration_deviation_weakens_the_evidence(self):
        verdict = interpret(_protocol(), _replicated_result(n=4000))
        self.assertTrue(verdict.deviations)
        self.assertIn("deviates from the preregistered n", verdict.deviations[0])
        self.assertLess(verdict.strength, 0.6)

    def test_wrong_alpha_and_seed_are_deviations(self):
        verdict = interpret(_protocol(), _replicated_result(alpha=0.2, seed=99))
        joined = " | ".join(verdict.deviations)
        self.assertIn("alpha", joined)
        self.assertIn("seed", joined)

    def test_compliance_accepts_the_preregistered_numbers(self):
        self.assertEqual(check_compliance(_protocol(), _replicated_result()), [])

    def test_compliance_reports_missing_n_and_test(self):
        result = _replicated_result()
        result.pop("n")
        result.pop("test")
        deviations = " | ".join(check_compliance(_protocol(), result))
        self.assertIn("n not reported", deviations)
        self.assertIn("no statistical test", deviations)

    def test_failed_audit_cannot_support_or_refute(self):
        for value in (0.4, -0.4):
            verdict = interpret(
                _protocol(),
                _replicated_result(value=value),
                audit={"tests_the_prediction": False, "concerns": ["wrong outcome"]},
            )
            self.assertEqual(verdict.evidence_type, "neutral")
            self.assertIn("does not test the prediction", verdict.reasoning)

    def test_unusable_result_is_neutral_and_weak(self):
        verdict = interpret(_protocol(), {"metric": "x"})
        self.assertEqual(verdict.evidence_type, "neutral")
        self.assertLess(verdict.strength, 0.35)


class TestLab(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(":memory:")
        self.hypothesis = {
            "id": "h1",
            "claim": "Polygenic scores predict school grades",
            "predictions": '["PGS correlates positively with grades"]',
            "falsification_conditions": '["no association in sibling comparison"]',
            "confidence": 0.5,
            "status": "active",
        }
        self.db.save_hypothesis({
            **self.hypothesis, "date_added": now_iso(),
        })

    def tearDown(self):
        self.tmp.cleanup()

    def _lab(self, llm):
        return SimulationLab(
            self.db, llm, base_dir=self.tmp.name, timeout=20,
            designer=None, writer=None,
            runner=ScriptRunner(base_dir=self.tmp.name, timeout=20),
        )

    def test_full_flow_stores_experiment_and_evidence(self):
        protocol_json = {"designable": True, "protocol": _protocol().to_dict()}
        code = _valid_script()
        llm = _FakeLLM(
            chat_replies=[code],
            json_replies=[
                protocol_json,
                {"approved": True, "problems": []},          # pre-run reviewer
                {"tests_the_prediction": True, "concerns": []},  # post-run audit
            ],
        )
        outcome = asyncio.run(self._lab(llm).run(self.hypothesis, topic="t"))

        self.assertTrue(outcome["ok"], outcome["note"])
        evidence = outcome["evidence"]
        self.assertEqual(evidence["evidence_type"], "supports")
        self.assertEqual(evidence["strength"], 0.6)  # capped
        self.assertTrue(evidence["experiment_id"])

        experiment = self.db.get_experiment(evidence["experiment_id"])
        self.assertEqual(experiment["status"], "completed")
        self.assertEqual(experiment["verdict"], "supports")
        self.assertTrue(experiment["script_sha256"])
        self.assertIn("p_value", experiment["result"])
        self.assertAlmostEqual(experiment["replication_rate"], 1.0)
        self.assertEqual(json.loads(experiment["deviations"]), [])
        self.assertEqual(json.loads(experiment["sensitivity"]), [])

    def test_untestable_hypothesis_is_closed_without_a_script(self):
        llm = _FakeLLM(json_replies=[{"designable": False, "reason": "ethical claim"}])
        outcome = asyncio.run(self._lab(llm).run(self.hypothesis, topic="t"))
        self.assertTrue(outcome["ok"])
        self.assertIsNone(outcome["evidence"])
        experiments = self.db.get_experiments()
        self.assertEqual(experiments[0]["status"], "not_testable")

    def test_failed_script_is_reported_not_recorded_as_evidence(self):
        llm = _FakeLLM(
            chat_replies=["import os\nprint('nope')"] * 2,
            json_replies=[{"designable": True, "protocol": _protocol().to_dict()}],
        )
        outcome = asyncio.run(self._lab(llm).run(self.hypothesis, topic="t"))
        self.assertFalse(outcome["ok"])
        self.assertIsNone(outcome["evidence"])
        self.assertEqual(self.db.get_experiments()[0]["status"], "failed")

    def test_script_that_prints_nothing_is_a_failure(self):
        llm = _FakeLLM(
            chat_replies=["import sim_params as P\nprint('hello', P.N)\n"],
            json_replies=[{"designable": True, "protocol": _protocol().to_dict()}],
        )
        outcome = asyncio.run(self._lab(llm).run(self.hypothesis, topic="t"))
        self.assertFalse(outcome["ok"])
        self.assertIn("JSON", outcome["note"])


def _valid_script() -> str:
    """A script that satisfies the contract and survives the known-answer checks.

    The p-values are computed from the data, not written down: a script that
    always prints ``p < alpha`` still runs fine and passes a smoke test, but it
    is exactly what the null-rate check exists to catch.
    """
    return (
        "import json, numpy as np\n"
        "from scipy import stats\n"
        "import sim_params as P\n"
        "values, p_values = [], []\n"
        "for i in range(P.REPLICATIONS):\n"
        "    rng = np.random.default_rng(P.SEED + i)\n"
        "    x = rng.normal(0, 1, P.N)\n"
        "    y = P.EFFECT * x + rng.normal(0, 0.6, P.N)\n"
        "    fit = stats.linregress(x, y)\n"
        "    values.append(float(fit.slope))\n"
        "    p_values.append(float(fit.pvalue))\n"
        "print(json.dumps({'n': P.N, 'metric': 'slope', 'test': 'ols',\n"
        "                  'alpha': P.ALPHA, 'seed': P.SEED,\n"
        "                  'replications': P.REPLICATIONS,\n"
        "                  'value': sum(values) / len(values),\n"
        "                  'ci_low': min(values), 'ci_high': max(values),\n"
        "                  'p_value': float(np.median(p_values)), 'values': values,\n"
        "                  'p_values': p_values, 'significant_share': 1.0,\n"
        "                  'direction_share': 1.0, 'sensitivity': []}))\n"
    )


def _flaky_script() -> str:
    """Passes the smoke test at n=30 and dies at the real sample size."""
    return _valid_script().replace(
        "values, p_values = [], []",
        "if P.N > 100:\n    raise RuntimeError('explodes at full size')\n"
        "values, p_values = [], []",
    )


class TestRepairLoop(unittest.TestCase):
    """A script is reviewed, smoke-tested and repaired before it counts."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(":memory:")
        self.hypothesis = {
            "id": "h1",
            "claim": "Polygenic scores predict school grades",
            "predictions": '["PGS correlates positively with grades"]',
            "falsification_conditions": '["no association in sibling comparison"]',
            "confidence": 0.5,
            "status": "active",
        }
        self.db.save_hypothesis({**self.hypothesis, "date_added": now_iso()})
        self.protocol_json = {"designable": True, "protocol": _protocol().to_dict()}

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, llm):
        lab = SimulationLab(
            self.db, llm, base_dir=self.tmp.name, timeout=20,
            smoke_n=30, smoke_timeout=20, max_attempts=3,
            runner=ScriptRunner(base_dir=self.tmp.name, timeout=20),
        )
        return asyncio.run(lab.run(self.hypothesis, topic="t"))

    def _prompts(self, llm):
        return " ".join(
            str(message.get("content", ""))
            for messages in llm.prompts for message in messages
        )

    def test_smoke_failure_is_repaired_with_the_error(self):
        broken = "import sim_params as P\nprint('only noise', P.N)\n"
        llm = _FakeLLM(
            chat_replies=[broken, _valid_script()],
            json_replies=[
                self.protocol_json,
                {"approved": True, "problems": []},
                {"tests_the_prediction": True, "concerns": []},
            ],
        )
        outcome = self._run(llm)
        self.assertTrue(outcome["ok"], outcome["note"])
        self.assertEqual(outcome["evidence"]["evidence_type"], "supports")
        experiment = self.db.get_experiment(outcome["experiment_id"])
        self.assertEqual(experiment["attempts"], 2)
        self.assertIn("no JSON result line", self._prompts(llm)), (
            "the smoke-test error must reach the writer"
        )

    def test_runtime_failure_is_repaired_with_the_traceback(self):
        llm = _FakeLLM(
            chat_replies=[_flaky_script(), _valid_script()],
            json_replies=[
                self.protocol_json,
                {"approved": True, "problems": []},
                {"approved": True, "problems": []},
                {"tests_the_prediction": True, "concerns": []},
            ],
        )
        outcome = self._run(llm)
        self.assertTrue(outcome["ok"], outcome["note"])
        self.assertEqual(self.db.get_experiment(outcome["experiment_id"])["attempts"], 2)
        self.assertIn("explodes at full size", self._prompts(llm))

    def test_reviewer_rejection_triggers_a_rewrite(self):
        llm = _FakeLLM(
            chat_replies=[_valid_script(), _valid_script()],
            json_replies=[
                self.protocol_json,
                {"approved": False, "problems": ["measures grades, not the score"]},
                {"approved": True, "problems": []},
                {"tests_the_prediction": True, "concerns": []},
            ],
        )
        outcome = self._run(llm)
        self.assertTrue(outcome["ok"], outcome["note"])
        self.assertEqual(self.db.get_experiment(outcome["experiment_id"])["attempts"], 2)
        self.assertEqual(outcome["evidence"]["strength"], 0.6)
        self.assertIn("measures grades, not the score", self._prompts(llm))

    def test_unapproved_reviewer_still_runs_but_halves_the_evidence(self):
        llm = _FakeLLM(
            chat_replies=[_valid_script()] * 3,
            json_replies=[
                self.protocol_json,
                {"approved": False, "problems": ["data generation presupposes the effect"]},
                {"approved": False, "problems": ["data generation presupposes the effect"]},
                {"approved": False, "problems": ["data generation presupposes the effect"]},
                {"tests_the_prediction": True, "concerns": []},
            ],
        )
        outcome = self._run(llm)
        self.assertTrue(outcome["ok"], outcome["note"])
        self.assertEqual(outcome["evidence"]["strength"], 0.3)
        self.assertEqual(
            outcome["evidence"]["evidence_type"], "neutral",
            "a script that does not test the prediction cannot support it",
        )
        self.assertIn("audit concern", outcome["evidence"]["content"])
        self.assertIn("inconclusive", outcome["evidence"]["content"])

    def test_exhausted_attempts_record_the_reason(self):
        broken = "import sim_params as P\nprint('only noise', P.N)\n"
        llm = _FakeLLM(
            chat_replies=[broken] * 3,
            json_replies=[self.protocol_json],
        )
        outcome = self._run(llm)
        self.assertFalse(outcome["ok"])
        self.assertIsNone(outcome["evidence"])
        experiment = self.db.get_experiment(outcome["experiment_id"])
        self.assertEqual(experiment["status"], "failed")
        self.assertIn("smoke test failed", experiment["error"])


class TestQueueAndHandler(unittest.TestCase):
    def _orch(self):
        cfg = Config()
        cfg.database_url = ":memory:"
        cfg.llm_failure_threshold = 0
        cfg.sim_timeout_seconds = 20
        orch = ResearchOrchestrator(cfg)
        orch.current_topic = "test topic"
        orch.work_queue.set_topic("test topic")
        return orch

    def test_only_testable_hypotheses_are_seeded(self):
        orch = self._orch()
        orch.db.save_hypothesis({
            "id": "sim1", "claim": "A testable claim", "status": "active",
            "confidence": 0.5, "predictions": '["X raises Y"]',
            "falsification_conditions": '["no effect of X on Y"]',
            "date_added": now_iso(),
        })
        orch.db.save_hypothesis({
            "id": "eth1", "claim": "An ethical claim", "status": "active",
            "confidence": 0.5, "predictions": "[]",
            "falsification_conditions": "[]", "date_added": now_iso(),
        })
        orch.work_queue.seed()
        items = orch.db._get_all("work_items", where="kind = ?", params=(KIND_SIMULATION,))
        self.assertEqual([item["ref_id"] for item in items], ["sim1"])

    def test_handler_stores_evidence_and_updates_confidence(self):
        orch = self._orch()
        orch.db.save_hypothesis({
            "id": "sim1", "claim": "A testable claim", "status": "active",
            "confidence": 0.5, "predictions": '["X raises Y"]',
            "falsification_conditions": '["no effect of X on Y"]',
            "date_added": now_iso(),
        })
        orch.work_queue.seed()
        item = orch.db._get_all("work_items", where="kind = ?", params=(KIND_SIMULATION,))[0]

        class FakeLab:
            async def run(self, hypothesis, topic=""):
                return {"ok": True, "note": "simulation supports (p=0.001, strength 0.6)",
                        "experiment_id": "exp1",
                        "evidence": {"id": gen_id(), "hypothesis_id": hypothesis["id"],
                                     "source_id": "", "evidence_type": "supports",
                                     "content": "Simulation: effect in predicted direction",
                                     "strength": 0.6, "date_added": now_iso(),
                                     "experiment_id": "exp1"}}

        orch.simulation_lab = FakeLab()
        outcome = asyncio.run(orch._work_item_simulation(item))
        self.assertTrue(outcome[0])
        rows = orch.db.get_evidence_for_hypothesis("sim1")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["experiment_id"], "exp1")

    def test_disabled_simulations_defer_without_burning_attempts(self):
        orch = self._orch()
        orch.config.simulations_enabled = False
        orch.db.save_hypothesis({
            "id": "sim1", "claim": "A testable claim", "status": "active",
            "confidence": 0.5, "predictions": '["X raises Y"]',
            "falsification_conditions": '["no effect"]', "date_added": now_iso(),
        })
        orch.work_queue.seed()
        item = orch.db._get_all("work_items", where="kind = ?", params=(KIND_SIMULATION,))[0]
        ok, note = asyncio.run(orch._work_item_simulation(item))
        self.assertIsNone(ok)
        self.assertIn("disabled", note)


if __name__ == "__main__":
    unittest.main()
