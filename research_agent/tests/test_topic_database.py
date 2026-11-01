"""One database per topic: path derivation and binding.

The claim under test is isolation: a run started on a new topic must not read or
write the previous topic's corpus, and switching must be refused once a process
has worked in a database (so a run never silently abandons its own data). Token
accounting is the deliberate exception - it stays in one shared file, because
"tokens today" is a question about time, not about a topic.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.config import (
    Config,
    topic_database_path,
    topic_slug,
    usage_database_path,
)
from research_agent.models import gen_id, now_iso
from research_agent.orchestrator import ResearchOrchestrator


class TestTopicPaths(unittest.TestCase):
    def test_slug_is_readable_and_stable(self):
        self.assertEqual(topic_slug("Kognition und Gesundheit"), "kognition-und-gesundheit")
        self.assertEqual(topic_slug("Heritabilität & IQ"), "heritabilitaet-iq")
        self.assertEqual(topic_slug("Kognition und Gesundheit"),
                         topic_slug("  Kognition und Gesundheit  "))

    def test_slug_survives_hostile_input(self):
        self.assertEqual(topic_slug("../../etc/passwd"), "etc-passwd")
        self.assertEqual(topic_slug(""), "topic")
        self.assertEqual(topic_slug("///"), "topic")
        self.assertLessEqual(len(topic_slug("x" * 300)), 40)

    def test_paths_sit_next_to_the_base_file(self):
        base = str(Path("C:/tmp") / "data" / "research.db") if os.name == "nt" \
            else "/tmp/data/research.db"
        topic_path = topic_database_path(base, "Kognition und Gesundheit")

        self.assertEqual(Path(topic_path).parent, Path(base).parent)
        self.assertTrue(Path(topic_path).name.startswith("research-kognition-und-gesundheit-"))
        self.assertTrue(Path(topic_path).name.endswith(".db"))
        self.assertNotEqual(topic_path, base)

    def test_similar_topics_get_distinct_files(self):
        base = "/tmp/data/research.db"
        first = topic_database_path(base, "IQ Genetics")
        second = topic_database_path(base, "IQ Genetics (PGT-A)")
        self.assertNotEqual(first, second)
        # ... and the same topic maps to the same file every time.
        self.assertEqual(first, topic_database_path(base, "IQ Genetics"))

    def test_memory_databases_are_left_alone(self):
        self.assertEqual(topic_database_path(":memory:", "anything"), ":memory:")
        self.assertEqual(usage_database_path(":memory:"), ":memory:")

    def test_usage_file_is_a_sibling(self):
        base = "/tmp/data/research.db"
        self.assertEqual(usage_database_path(base), "/tmp/data/research-usage.db")

    def test_config_derives_and_respects_the_flag(self):
        cfg = Config()
        cfg.database_url = "/tmp/data/research.db"
        cfg.database_per_topic = True
        self.assertEqual(cfg.database_for_topic("A topic"),
                         topic_database_path("/tmp/data/research.db", "A topic"))
        self.assertEqual(cfg.database_for_topic(""), "/tmp/data/research.db")

        cfg.database_per_topic = False
        self.assertEqual(cfg.database_for_topic("A topic"), "/tmp/data/research.db")

    def test_load_reads_the_flag_from_the_environment(self):
        tmp = tempfile.mkdtemp(prefix="topicdb_cfg_")
        base = str(Path(tmp) / "research.db")
        with patch.dict(os.environ, {"DATABASE_URL": base, "DATABASE_PER_TOPIC": "0"}):
            cfg = Config.load(env_file=str(Path(tmp) / "missing.env"))
            self.assertFalse(cfg.database_per_topic)
            self.assertEqual(cfg.database_for_topic("X"), base)
            self.assertEqual(cfg.usage_database_url, usage_database_path(base))


def _config(tmp: str, per_topic: bool = True) -> Config:
    cfg = Config()
    cfg.database_url = str(Path(tmp) / "research.db")
    cfg.usage_database_url = usage_database_path(cfg.database_url)
    cfg.database_per_topic = per_topic
    cfg.llm_failure_threshold = 0
    return cfg


class TestOrchestratorBinding(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.mkdtemp(prefix="topicdb_")
        self.tmp = tmp
        self.addCleanup(lambda: __import__("shutil").rmtree(tmp, ignore_errors=True))

    def test_topic_at_construction_selects_the_database(self):
        topic = "Kognition und Gesundheit"
        orch = ResearchOrchestrator(_config(self.tmp), topic=topic)

        self.assertEqual(orch.database_path,
                         topic_database_path(str(Path(self.tmp) / "research.db"), topic))
        self.assertTrue(Path(orch.database_path).exists())
        # Everything knowledge-bound reads the same handle.
        for component in (orch.memory, orch.retrieval, orch.source_manager,
                          orch.work_queue, orch.simulation_lab):
            self.assertIs(component.db, orch.db)

    def test_accounting_stays_in_one_shared_file(self):
        orch = ResearchOrchestrator(_config(self.tmp), topic="A topic")

        self.assertNotEqual(orch.usage_db.db_path, orch.db.db_path)
        self.assertEqual(orch.usage_db.db_path,
                         usage_database_path(str(Path(self.tmp) / "research.db")))
        # The usage sink routes every call to the shared file, so a topic
        # database stays free of accounting rows.
        orch._persist_llm_usage({"phase": "planning", "prompt_tokens": 10,
                                 "completion_tokens": 5, "model": "m",
                                 "success": True})
        self.assertEqual(orch.usage_db.get_llm_usage_summary()["all_time"]["total_tokens"], 15)
        self.assertEqual(orch.db.get_llm_usage_summary()["all_time"]["total_tokens"], 0)

    def test_dashboard_start_switches_before_the_first_cycle(self):
        orch = ResearchOrchestrator(_config(self.tmp))          # dashboard-only mode
        self.assertEqual(orch.database_path, str(Path(self.tmp) / "research.db"))

        switched = orch.use_topic_database("Kognition und Gesundheit")

        self.assertTrue(switched)
        self.assertEqual(orch.db.db_path,
                         topic_database_path(str(Path(self.tmp) / "research.db"),
                                             "Kognition und Gesundheit"))
        # Idempotent: the same topic again is not a switch.
        self.assertFalse(orch.use_topic_database("Kognition und Gesundheit"))

    def test_switch_is_refused_once_the_process_worked(self):
        orch = ResearchOrchestrator(_config(self.tmp))
        before = orch.database_path
        orch.current_cycle = 1

        self.assertFalse(orch.use_topic_database("Some other topic"))
        self.assertEqual(orch.database_path, before)
        self.assertFalse(Path(topic_database_path(before, "Some other topic")).exists())

    def test_disabled_flag_keeps_one_shared_database(self):
        orch = ResearchOrchestrator(_config(self.tmp, per_topic=False), topic="A topic")

        self.assertEqual(orch.database_path, str(Path(self.tmp) / "research.db"))
        self.assertIs(orch.usage_db, orch.db)
        self.assertFalse(orch.use_topic_database("Another topic"))

    def test_two_topics_do_not_see_each_others_facts(self):
        first = ResearchOrchestrator(_config(self.tmp), topic="First topic")
        first.db.save_fact({
            "id": gen_id(), "content": "Only the first topic knows this.",
            "confidence": 0.7, "source_ids": "[]", "topic": "First topic",
            "date_added": now_iso(),
        })
        second = ResearchOrchestrator(_config(self.tmp), topic="Second topic")

        self.assertNotEqual(first.db.db_path, second.db.db_path)
        self.assertEqual(second.db.count_facts(), 0)
        self.assertEqual(first.db.count_facts(), 1)


if __name__ == "__main__":
    unittest.main()
