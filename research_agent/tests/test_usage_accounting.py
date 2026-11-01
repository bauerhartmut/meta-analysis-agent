"""Tests for persisted LLM token accounting.

The engine counts tokens in memory, and those counters start at zero again after
a restart — which is why "how many tokens did today cost?" was unanswerable. The
tests here pin down the fix: every call is stored, and today's spend is
aggregated per phase and per model from those rows.
"""

import asyncio
import datetime
import json
import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.llm.engine import LLMEngine


class TestUsageStorage(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")

    def tearDown(self):
        LLMEngine.set_usage_sink(None)

    def test_a_call_is_stored_and_counted_for_today(self):
        self.db.record_llm_usage(
            phase="analyzing", prompt_tokens=1000, completion_tokens=250,
            time_ms=1200.0, model="gpt-test", backend="tudagpt",
        )
        summary = self.db.get_llm_usage_summary()
        self.assertEqual(summary["today"]["calls"], 1)
        self.assertEqual(summary["today"]["prompt_tokens"], 1000)
        self.assertEqual(summary["today"]["completion_tokens"], 250)
        self.assertEqual(summary["today"]["total_tokens"], 1250)
        self.assertEqual(summary["today"]["tokens_per_call"], 1250.0)
        self.assertEqual(summary["today"]["errors"], 0)

    def test_today_is_grouped_by_phase_and_model(self):
        for phase, prompt, completion in (
            ("analyzing", 1000, 200),
            ("analyzing", 500, 100),
            ("hypothesizing", 3000, 900),
        ):
            self.db.record_llm_usage(phase=phase, prompt_tokens=prompt,
                                     completion_tokens=completion, model="m1")
        summary = self.db.get_llm_usage_summary()
        by_phase = {row["phase"]: row for row in summary["by_phase"]}
        self.assertEqual(by_phase["analyzing"]["calls"], 2)
        self.assertEqual(by_phase["analyzing"]["total_tokens"], 1800)
        self.assertEqual(by_phase["hypothesizing"]["total_tokens"], 3900)
        # Ordered by spend: the expensive phase is the interesting one.
        self.assertEqual(summary["by_phase"][0]["phase"], "hypothesizing")
        self.assertEqual(summary["by_model"][0]["model"], "m1")
        self.assertEqual(summary["by_day"][0]["total_tokens"], 5700)

    def test_failed_calls_are_counted_as_errors_not_tokens(self):
        self.db.record_llm_usage(phase="analyzing", success=False)
        summary = self.db.get_llm_usage_summary()
        self.assertEqual(summary["today"]["calls"], 1)
        self.assertEqual(summary["today"]["errors"], 1)
        self.assertEqual(summary["today"]["total_tokens"], 0)

    def test_an_old_call_stays_out_of_today(self):
        yesterday = (
            datetime.datetime.now() - datetime.timedelta(days=1)
        ).astimezone().isoformat()
        self.db.record_llm_usage(prompt_tokens=5000, timestamp=yesterday)
        self.db.record_llm_usage(prompt_tokens=100)
        summary = self.db.get_llm_usage_summary()
        self.assertEqual(summary["today"]["calls"], 1)
        self.assertEqual(summary["today"]["total_tokens"], 100)
        self.assertEqual(summary["all_time"]["total_tokens"], 5100)
        days = {row["day"]: row["total_tokens"] for row in summary["by_day"]}
        self.assertEqual(len(days), 2)


class TestEngineSink(unittest.TestCase):
    def setUp(self):
        self.seen = []
        LLMEngine.set_usage_sink(self.seen.append)

    def tearDown(self):
        LLMEngine.set_usage_sink(None)

    def test_every_call_reaches_the_sink(self):
        LLMEngine._record_call(120, 30, 42.5, "analyzing", success=True,
                               model="gpt-test")
        LLMEngine._record_call(0, 0, 0, "analyzing", success=False)
        self.assertEqual(len(self.seen), 2)
        self.assertEqual(self.seen[0]["total_tokens"], 150)
        self.assertEqual(self.seen[0]["model"], "gpt-test")
        self.assertEqual(self.seen[0]["phase"], "analyzing")
        self.assertFalse(self.seen[1]["success"])
        self.assertEqual(self.seen[1]["total_tokens"], 0)

    def test_a_broken_sink_cannot_break_a_cycle(self):
        def explode(_entry):
            raise RuntimeError("database gone")

        LLMEngine.set_usage_sink(explode)
        # Must not raise: accounting is never allowed to take the run down.
        LLMEngine._record_call(10, 5, 1.0, "idle")

    def test_without_a_sink_the_engine_still_counts(self):
        LLMEngine.set_usage_sink(None)
        before = LLMEngine.get_stats()["total_calls"]
        LLMEngine._record_call(10, 5, 1.0, "idle")
        self.assertEqual(LLMEngine.get_stats()["total_calls"], before + 1)


class TestOrchestratorWiring(unittest.TestCase):
    def setUp(self):
        from research_agent.config import Config
        from research_agent.orchestrator import ResearchOrchestrator

        self.LLMEngine = LLMEngine
        cfg = Config()
        cfg.database_url = ":memory:"
        self.orch = ResearchOrchestrator(cfg)

    def tearDown(self):
        LLMEngine.set_usage_sink(None)

    def test_engine_usage_lands_in_the_database(self):
        self.LLMEngine._record_call(200, 50, 10.0, "hypothesizing",
                                    success=True, model="gpt-test")
        summary = self.orch.db.get_llm_usage_summary()
        self.assertEqual(summary["today"]["calls"], 1)
        self.assertEqual(summary["today"]["total_tokens"], 250)
        self.assertEqual(summary["by_phase"][0]["phase"], "hypothesizing")
        self.assertEqual(summary["by_model"][0]["model"], "gpt-test")

    def test_the_stored_row_carries_the_backend_and_a_timestamp(self):
        self.LLMEngine._record_call(1, 1, 1.0, "idle")
        rows = self.orch.db._get_all("llm_usage")
        self.assertEqual(rows[0]["backend"], self.orch.config.llm_backend)
        stamp = rows[0]["timestamp"]
        self.assertTrue(stamp)
        # Parses back as a real time, so day boundaries stay meaningful.
        self.assertIsNotNone(datetime.datetime.fromisoformat(stamp))


class TestDashboardPayload(unittest.TestCase):
    def setUp(self):
        from research_agent.dashboard.server import DashboardHandler

        self.handler = DashboardHandler.__new__(DashboardHandler)
        self.db = Database(":memory:")
        self.handler.orchestrator = type("Orch", (), {"db": self.db})()

    def tearDown(self):
        LLMEngine.set_usage_sink(None)

    def test_stats_include_todays_stored_usage(self):
        self.db.record_llm_usage(phase="analyzing", prompt_tokens=400,
                                 completion_tokens=100, model="m")
        payload = self.handler._get_llm_stats()
        persisted = payload["persisted"]
        self.assertIsNotNone(persisted)
        self.assertEqual(persisted["today"]["total_tokens"], 500)
        self.assertEqual(persisted["by_phase"][0]["phase"], "analyzing")
        # The dashboard serialises this straight to JSON.
        json.dumps(payload)

    def test_a_database_error_does_not_break_the_panel(self):
        class Broken:
            def get_llm_usage_summary(self, *_a, **_k):
                raise RuntimeError("locked")

        self.handler.orchestrator = type("Orch", (), {"db": Broken()})()
        payload = self.handler._get_llm_stats()
        self.assertIsNone(payload["persisted"])
        self.assertIn("total_calls", payload)


if __name__ == "__main__":
    unittest.main()
