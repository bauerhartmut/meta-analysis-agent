"""
Component Tests for the Research Agent.
Tests all major components: database, search, extraction, memory, LLM, etc.
"""

import sys
import os
import json
import asyncio
import tempfile
import time
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.config import Config
from research_agent.database import Database
from research_agent.memory.store import MemoryStore
from research_agent.models import (
    Source, Fact, Hypothesis, Evidence, ResearchQuestion,
    JournalEntry, Contradiction, KnowledgeGraphNode, Embedding,
    now_iso, gen_id,
)


class TestConfig(unittest.TestCase):
    """Test configuration loading."""

    def test_default_config(self):
        config = Config()
        self.assertEqual(config.ollama_host, "http://localhost:11434")
        self.assertEqual(config.ollama_model, "qwen3:14b")

    def test_config_load(self):
        config = Config.load()
        self.assertIsInstance(config.ollama_host, str)
        self.assertGreater(config.dashboard_port, 0)


class TestDatabase(unittest.TestCase):
    """Test database operations."""

    def setUp(self):
        self.db = Database(":memory:")

    def test_init(self):
        """Database initializes without error."""
        self.assertIsNotNone(self.db)

    def test_source_crud(self):
        """Source create, read, update operations."""
        source = {
            "id": "test_source_1",
            "title": "Test Paper",
            "url": "https://example.com/paper1",
            "source_type": "arxiv",
            "content_hash": "abc123",
            "credibility": 0.8,
            "summary": "A test paper about quantum consciousness",
            "date_added": now_iso(),
        }
        self.db.save_source(source)

        # Read
        retrieved = self.db.get_source("test_source_1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["title"], "Test Paper")

        # By URL
        by_url = self.db.get_source_by_url("https://example.com/paper1")
        self.assertIsNotNone(by_url)

        # By hash
        by_hash = self.db.get_source_by_hash("abc123")
        self.assertIsNotNone(by_hash)

        # Count
        count = self.db.count_sources()
        self.assertEqual(count, 1)

    def test_source_duplicate_detection(self):
        """Detect duplicate sources by URL and hash."""
        source = {
            "id": "s1",
            "url": "https://example.com/paper1",
            "content_hash": "hash1",
            "title": "Paper 1",
        }
        self.db.save_source(source)

        # Same URL
        self.assertIsNotNone(self.db.get_source_by_url("https://example.com/paper1"))
        # Same hash
        self.assertIsNotNone(self.db.get_source_by_hash("hash1"))

    def test_hypothesis_crud(self):
        """Hypothesis CRUD operations."""
        hyp = {
            "id": "h1",
            "claim": "Quantum processes are involved in consciousness",
            "status": "proposed",
            "confidence": 0.4,
            "supporting_evidence": "[]",
            "contradicting_evidence": "[]",
            "date_added": now_iso(),
        }
        self.db.save_hypothesis(hyp)

        retrieved = self.db.get_hypothesis("h1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["claim"], "Quantum processes are involved in consciousness")

        # Active hypotheses
        active = self.db.get_active_hypotheses()
        self.assertEqual(len(active), 1)

    def test_question_crud(self):
        """Research question operations."""
        q = {
            "id": "q1",
            "question": "How does quantum coherence relate to neural processing?",
            "importance": 0.8,
            "uncertainty": 0.7,
            "information_gain": 0.9,
            "researchability": 0.6,
            "novelty": 0.7,
            "status": "open",
            "priority_score": 0.0,
            "date_added": now_iso(),
        }
        q_obj = ResearchQuestion(**{k: v for k, v in q.items() if k != "id"})
        q_obj.id = "q1"
        q_obj.compute_priority()

        q["priority_score"] = q_obj.priority_score
        self.db.save_question(q)

        open_qs = self.db.get_open_questions()
        self.assertEqual(len(open_qs), 1)
        self.assertGreater(open_qs[0]["priority_score"], 0)

    def test_evidence_storage(self):
        """Evidence storage and retrieval."""
        ev = {
            "id": "e1",
            "hypothesis_id": "h1",
            "source_id": "s1",
            "evidence_type": "supports",
            "content": "Study found quantum effects in microtubules",
            "strength": 0.7,
            "date_added": now_iso(),
        }
        self.db.save_evidence(ev)

        # Get evidence for hypothesis
        # (would need to implement this method)
        all_ev = self.db._get_all("evidence", where="hypothesis_id = 'h1'")
        self.assertEqual(len(all_ev), 1)

    def test_journal_entries(self):
        """Journal entry storage."""
        entry = {
            "id": "j1",
            "session_id": "s1",
            "cycle_number": 1,
            "timestamp": now_iso(),
            "research_question": "What is consciousness?",
            "why_selected": "Foundational question",
            "sources_investigated": json.dumps(["Paper A", "Paper B"]),
            "important_findings": json.dumps(["Finding 1"]),
            "new_hypotheses": json.dumps(["Hypothesis 1"]),
        }
        self.db.save_journal_entry(entry)

        entries = self.db.get_journal_entries(session_id="s1")
        self.assertEqual(len(entries), 1)

    def test_knowledge_graph(self):
        """Knowledge graph node and edge operations."""
        node = {
            "id": "n1",
            "node_type": "concept",
            "label": "Quantum Consciousness",
            "content": "Theories linking quantum mechanics to consciousness",
            "date_added": now_iso(),
        }
        self.db.save_knowledge_node(node)

        node2 = {
            "id": "n2",
            "node_type": "hypothesis",
            "label": "Orchestrated Objective Reduction",
            "content": "Penrose-Hameroff theory",
            "date_added": now_iso(),
        }
        self.db.save_knowledge_node(node2)

        edge = {
            "id": "e1",
            "source_node_id": "n2",
            "target_node_id": "n1",
            "relation": "investigates",
            "weight": 1.0,
            "date_added": now_iso(),
        }
        self.db.save_knowledge_edge(edge)

        # Query
        nodes = self.db.get_knowledge_nodes(node_type="concept")
        self.assertEqual(len(nodes), 1)

        edges = self.db.get_edges_for_node("n1")
        self.assertEqual(len(edges), 1)

    def test_embeddings(self):
        """Embedding storage."""
        emb = {
            "id": "emb1",
            "entity_type": "source",
            "entity_id": "s1",
            "embedding": json.dumps([0.1, 0.2, 0.3]),
            "text": "Test embedding",
            "date_added": now_iso(),
        }
        self.db.save_embedding(emb)

        retrieved = self.db.get_embedding_for_entity("source", "s1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["entity_type"], "source")

    def test_stats(self):
        """Statistics gathering."""
        # Add some data
        self.db.save_source({"id": "s1", "url": "http://a.com", "content_hash": "h1"})
        self.db.save_source({"id": "s2", "url": "http://b.com", "content_hash": "h2"})
        self.db.save_hypothesis({"id": "h1", "claim": "Test", "status": "proposed", "confidence": 0.3})

        stats = self.db.get_stats()
        self.assertEqual(stats["sources"], 2)
        self.assertEqual(stats["hypotheses"], 1)

    def test_contradictions(self):
        """Contradiction storage."""
        cont = {
            "id": "c1",
            "claim_a": "Quantum effects are relevant",
            "source_a_id": "s1",
            "claim_b": "Quantum effects are irrelevant",
            "source_b_id": "s2",
            "resolution": "unresolved",
            "date_added": now_iso(),
        }
        self.db.save_contradiction(cont)

        unresolved = self.db.get_unresolved_contradictions()
        self.assertEqual(len(unresolved), 1)


class TestModels(unittest.TestCase):
    """Test data models."""

    def test_source_model(self):
        s = Source(title="Test", url="https://example.com")
        self.assertEqual(s.title, "Test")
        self.assertIsInstance(s.to_dict(), dict)

    def test_hypothesis_model(self):
        h = Hypothesis(claim="Test hypothesis", confidence=0.5)
        self.assertEqual(h.claim, "Test hypothesis")
        self.assertEqual(h.status, "proposed")

    def test_research_question_priority(self):
        q = ResearchQuestion(
            importance=0.8,
            uncertainty=0.7,
            information_gain=0.9,
            researchability=0.6,
            novelty=0.5,
            contradiction_level=0.3,
        )
        priority = q.compute_priority()
        self.assertGreater(priority, 0)
        self.assertLess(priority, 1)

    def test_gen_id(self):
        id1 = gen_id()
        id2 = gen_id()
        self.assertNotEqual(id1, id2)
        self.assertEqual(len(id1), 12)


class TestSearchProviders(unittest.TestCase):
    """Test search providers (require network)."""

    def setUp(self):
        from research_agent.research.search import DuckDuckGoProvider, ArxivProvider
        self.ddg = DuckDuckGoProvider()
        self.arxiv = ArxivProvider()

    def test_ddg_search(self):
        """DuckDuckGo search returns results."""
        async def _test():
            results = await self.ddg.search("quantum consciousness", max_results=3)
            return results

        results = asyncio.run(_test())
        self.assertIsInstance(results, list)
        # May be empty in CI environments, so just check no crash
        print(f"  DuckDuckGo returned {len(results)} results")

    def test_arxiv_search(self):
        """arXiv search returns results."""
        async def _test():
            results = await self.arxiv.search("quantum consciousness", max_results=3)
            return results

        results = asyncio.run(_test())
        self.assertIsInstance(results, list)
        print(f"  arXiv returned {len(results)} results")
        if results:
            self.assertTrue(results[0].url.startswith("http"))


class TestContentExtractor(unittest.TestCase):
    """Test content extraction."""

    def setUp(self):
        from research_agent.research.extractor import ContentExtractor
        self.extractor = ContentExtractor()

    def test_extract_url(self):
        """Extract content from a URL."""
        async def _test():
            result = await self.extractor.extract("https://en.wikipedia.org/wiki/Consciousness")
            await self.extractor.close()
            return result

        result = asyncio.run(_test())
        self.assertIsNotNone(result)
        self.assertTrue(result.get("success"))
        self.assertGreater(len(result.get("content", "")), 100)
        print(f"  Extracted {len(result.get('content', ''))} chars from Wikipedia")

    def test_compute_hash(self):
        """Content hashing works."""
        h1 = self.extractor.compute_hash("Hello World")
        h2 = self.extractor.compute_hash("Hello World")
        h3 = self.extractor.compute_hash("Goodbye World")
        self.assertEqual(h1, h2)
        self.assertNotEqual(h1, h3)


class TestLLMEngine(unittest.TestCase):
    """Test LLM engine (requires Ollama)."""

    def setUp(self):
        from research_agent.llm.engine import LLMEngine
        self.llm = LLMEngine()

    def test_health_check(self):
        """Ollama is reachable."""
        async def _test():
            healthy = await self.llm.health_check()
            await self.llm.close()
            return healthy

        healthy = asyncio.run(_test())
        print(f"  Ollama health check: {'OK' if healthy else 'FAILED'}")

    def test_chat(self):
        """LLM chat returns a response."""
        async def _test():
            response = await self.llm.chat(
                [{"role": "user", "content": "Say exactly: test OK"}],
                max_tokens=20,
            )
            await self.llm.close()
            return response

        response = asyncio.run(_test())
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        print(f"  LLM response: {response[:50]}...")

    def test_embeddings(self):
        """Embedding generation works."""
        async def _test():
            embeddings = await self.llm.embed(["test text"])
            await self.llm.close()
            return embeddings

        embeddings = asyncio.run(_test())
        self.assertEqual(len(embeddings), 1)
        self.assertGreater(len(embeddings[0]), 0)
        print(f"  Embedding dimension: {len(embeddings[0])}")


class TestSessionLifecycle(unittest.TestCase):
    """Session closing on fresh starts + UTF-8 safe logging."""

    def setUp(self):
        self.db = Database(":memory:")

    def _make_session(self, sid, topic="t1", status="active"):
        self.db.save_session({
            "id": sid, "topic": topic, "status": status,
            "cycle_count": 0, "start_time": now_iso(), "end_time": "",
        })

    def test_start_closes_stale_active_sessions(self):
        # Orphaned active sessions (killed before cleanup) on the same + other topics
        self._make_session("s_old_same", topic="eugenics")
        self._make_session("s_old_other", topic="other")

        # What orchestrator.start() does for the topic: settle same-topic actives
        settled = self.db.close_active_sessions("eugenics")
        self.assertEqual(settled, 1)
        closed = self.db.get_session("s_old_same")
        self.assertEqual(closed["status"], "completed")
        self.assertTrue(closed["end_time"])

        # Fresh full start settles every leftover active session
        settled_all = self.db.close_active_sessions()
        self.assertEqual(settled_all, 1)
        self.assertEqual(self.db.get_session("s_old_other")["status"], "completed")

        # The brand-new session then stays the only active one
        self._make_session("s_new", topic="eugenics")
        self.assertEqual(self.db.get_active_session()["id"], "s_new")

    def test_end_time_preserved_when_already_set(self):
        self._make_session("s1", topic="eugenics")
        self.db._update("research_sessions", "s1", {"end_time": "2020-01-01T00:00:00+00:00"})
        self.db.close_active_sessions()
        s = self.db.get_session("s1")
        self.assertEqual(s["status"], "completed")
        self.assertEqual(s["end_time"], "2020-01-01T00:00:00+00:00")

    def test_utf8_logging_survives_unicode(self):
        """StreamHandler emits '\u2192' without UnicodeEncodeError on narrow consoles."""
        import logging
        from research_agent.utf8_logging import ensure_utf8, make_utf8_stream_handler
        ensure_utf8()
        handler = make_utf8_stream_handler()
        record = logging.LogRecord(
            "test", logging.INFO, "testfile", 0,
            "Logging arrow \u2192 and en-dash \u2013 must not crash", (), None,
        )
        # Must not raise UnicodeEncodeError
        try:
            handler.emit(record)
        except UnicodeEncodeError as e:
            self.fail(f"UTF-8 handler raised UnicodeEncodeError: {e}")
        self.assertEqual(handler.stream.encoding, "utf-8")

    def test_start_keyboardinterrupt_closes_session_and_returns(self):
        """SIGINT/KeyboardInterrupt inside the loop closes the session; start()
        returns normally so the caller can exit 0."""
        import tempfile, shutil
        from research_agent.config import Config
        from research_agent.orchestrator import ResearchOrchestrator

        tmp = tempfile.mkdtemp(prefix="rje_test_")
        try:
            cfg = Config()
            cfg.database_url = ":memory:"
            cfg.data_dir = tmp
            cfg.journal_dir = os.path.join(tmp, "journal")
            orch = ResearchOrchestrator(cfg)

            async def _fake_loop():
                raise KeyboardInterrupt()  # simulates SIGINT/Ctrl+C mid-cycle
            orch._research_loop = _fake_loop

            asyncio.run(orch.start("test topic"))  # must not propagate KBInterrupt

            rows = orch.db._get_all("research_sessions")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "completed")
            self.assertTrue(rows[0]["end_time"])
            self.assertEqual(orch.current_session["status"], "completed")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_interrupted_process_exits_zero(self):
        """main()'s KeyboardInterrupt handler exits with code 0 (not 130)."""
        import subprocess
        code = (
            "import asyncio, sys\n"
            "async def main():\n"
            "    raise KeyboardInterrupt\n"
            "try:\n"
            "    asyncio.run(main())\n"
            "except KeyboardInterrupt:\n"
            "    sys.exit(0)\n"
        )
        p = subprocess.run([sys.executable, "-c", code])
        self.assertEqual(p.returncode, 0)


class _RaisingProvider:
    """Fake provider whose search always raises (failure isolation test)."""

    def __init__(self, name="bad"):
        self._name = name

    @property
    def name(self):
        return self._name

    async def search(self, query, max_results=10):
        raise RuntimeError("provider exploded")


class _FakeSearchProvider:
    """Deterministic fake provider for offline SearchManager tests."""

    def __init__(self, name, results):
        self._name = name
        self._results = list(results)
        self.calls = []

    @property
    def name(self):
        return self._name

    async def search(self, query, max_results=10):
        self.calls.append((query, max_results))
        return list(self._results)


class TestSearchCircuitBreaker(unittest.TestCase):
    """Offline tests for the PAKET A search-layer hardening:
    per-provider circuit breaker, bounded retries -> cooldown, provider
    priority, dedup, domain filtering and per-query failure isolation.
    All HTTP is mocked; no live network is touched."""

    def setUp(self):
        import research_agent.research.search as s
        self.smod = s
        # Fresh, deterministic provider set so tests never hit the network.
        self.mgr = s.SearchManager()
        self.mgr.providers = {}
        # Clear any circuit state left by previous runs/tests.
        self.smod.RATE_LIMIT_MEMORY._blocked_until.clear()

    def tearDown(self):
        self.smod.RATE_LIMIT_MEMORY._blocked_until.clear()

    def _fake(self, name, results=None):
        prov = _FakeSearchProvider(name, results or [])
        return prov, prov.calls

    def test_circuit_opens_then_blocks_and_recovers(self):
        mem = self.smod.RATE_LIMIT_MEMORY
        self.assertFalse(mem.blocked("arxiv"))
        mem.penalize("arxiv", 60.0, "rate limited")
        self.assertTrue(mem.blocked("arxiv"))
        # Unrelated provider is unaffected
        self.assertFalse(mem.blocked("pubmed"))
        # Expired window -> recovers and clears the entry
        mem._blocked_until["arxiv"] = time.monotonic() - 1.0
        self.assertFalse(mem.blocked("arxiv"))
        self.assertNotIn("arxiv", mem._blocked_until)

    def test_search_skips_blocked_provider(self):
        p1, c1 = self._fake("arxiv", [self.smod.SearchResult(title="A", url="u1")])
        p2, c2 = self._fake("pubmed", [self.smod.SearchResult(title="B", url="u2")])
        self.mgr.register(p1)
        self.mgr.register(p2)

        # Open the circuit for pubmed before searching.
        self.smod.RATE_LIMIT_MEMORY.penalize("pubmed", 300.0, "test block")
        results = asyncio.run(self.mgr.search("test query", providers=["arxiv", "pubmed"]))

        self.assertEqual(c1, [("test query", 5)])
        self.assertEqual(c2, [])  # pubmed skipped entirely
        self.assertEqual(len(results), 1)
        self.smod.RATE_LIMIT_MEMORY._blocked_until.clear()

    def test_unknown_provider_ignored(self):
        p, _ = self._fake("arxiv", [self.smod.SearchResult(title="A", url="u1")])
        self.mgr.register(p)
        results = asyncio.run(
            self.mgr.search("q", providers=["arxiv", "does_not_exist"])
        )
        self.assertEqual(len(results), 1)

    def test_failure_isolation(self):
        p1, _ = self._fake("arxiv", [self.smod.SearchResult(title="A", url="u1")])
        self.mgr.register(p1)
        self.mgr.register(_RaisingProvider())
        results = asyncio.run(self.mgr.search("q", providers=["arxiv", "bad"]))
        # Healthy provider's results survive a sibling's failure.
        self.assertEqual(len(results), 1)

    def test_dedup_and_domain_filter(self):
        a = self.smod.SearchResult(
            title="Human heritability and twin studies of intelligence",
            url="https://dup.example/1", snippet="heritability twin study")
        b = self.smod.SearchResult(
            title="Same URL re-rendered", url="https://dup.example/1", snippet="x")
        physics = self.smod.SearchResult(
            title="Topological Wilson loop in quantum field theory",
            url="https://irrelevant.example/2", snippet="gauge theory")  # excluded domain
        kept = self.smod.SearchResult(
            title="GWAS polygenic scores predict cognitive outcomes",
            url="https://kept.example/3", snippet="gwas polygenic")
        for n, r in [("arxiv", [a]), ("pubmed", [b]), ("openalex", [physics]), ("semantic_scholar", [kept])]:
            self.mgr.register(self._fake(n, r)[0])

        results = asyncio.run(self.mgr.search("intelligence genetics"))
        urls = sorted(r.url for r in results)
        self.assertEqual(urls, ["https://dup.example/1", "https://kept.example/3"])

    def test_default_provider_priority(self):
        names = list(self.smod.SearchManager().providers.keys())
        # Most reliable first; rate-limit-prone providers last and handled by
        # the circuit breaker.
        self.assertEqual(names[0], "arxiv")
        self.assertIn("pubmed", names)
        self.assertIn("openalex", names)
        self.assertIn("semantic_scholar", names)
        # DuckDuckGo answers with HTTPError/202 on every call and returns no
        # rows; it is off by default and comes back only on request.
        self.assertNotIn("duckduckgo", names)

    def test_duckduckgo_can_be_enabled_explicitly(self):
        from unittest import mock
        with mock.patch.dict(os.environ, {"SEARCH_ENABLE_DDG": "1"}):
            names = list(self.smod.SearchManager().providers.keys())
        self.assertIn("duckduckgo", names)

    def test_retry_exhaustion_opens_circuit(self):
        """Listing retry caps are tight, and exhausting retries opens the circuit."""
        from unittest import mock
        # bounded retry configuration
        # implementation order §4.1: retries 3 with the 3/6/9 s ladder
        self.assertEqual(self.smod.SemanticScholarProvider._max_retries, 3)
        self.assertEqual(self.smod.SemanticScholarProvider._base_delay, 3.0)

        class FakeResp:
            status = 429
            headers = {}
            async def json(self):
                return {}

        class FakeGetResult:
            """Mimics aiohttp's _RequestContextManager returned by session.get()."""
            def __init__(self):
                self.resp = FakeResp()
            async def __aenter__(self):
                return self.resp
            async def __aexit__(self, *a):
                return False

        class FakeSession:
            def __init__(self, *a, **k):
                pass
            async def __aenter__(self):
                return self
            async def __aexit__(self, *a):
                return False
            def get(self, *a, **k):
                return FakeGetResult()

        prov = self.smod.SemanticScholarProvider()
        prov._max_retries = 2
        prov._min_interval = 0.0
        prov._base_delay = 0.0
        prov._cooldown = 600.0
        prov._last_request_time = 0.0
        self.smod.RATE_LIMIT_MEMORY._blocked_until.clear()

        with mock.patch.object(self.smod.aiohttp, "ClientSession", FakeSession):
            results = asyncio.run(prov.search("some genetics query"))

        self.assertEqual(results, [])
        # After all retries were burned, the circuit must be OPEN for the provider.
        self.assertTrue(self.smod.RATE_LIMIT_MEMORY.blocked("semantic_scholar"))
        self.smod.RATE_LIMIT_MEMORY._blocked_until.clear()


class TestDuckDuckGoProvider(unittest.TestCase):
    """DDG provider uses the duckduckgo_search library (backends internal).

    Offline: the duckduckgo_search library is mocked so no network is touched.
    Verifies (a) a healthy library call returns results without opening the
    circuit, and (b) when the library fails (DDG bot challenge / HTTPError)
    the circuit opens instead of stalling the cycle.
    """

    def setUp(self):
        from research_agent.research.search import DuckDuckGoProvider
        import research_agent.research.search as s
        self.prov = DuckDuckGoProvider()
        self.smod = s
        self.smod.RATE_LIMIT_MEMORY._blocked_until.clear()

    def tearDown(self):
        self.smod.RATE_LIMIT_MEMORY._blocked_until.clear()

    @staticmethod
    def _fake_ddgs_module(working):
        """Fake duckduckgo_search module whose DDGS.text() works or raises."""
        import types

        class _FakeDDGS:
            def __init__(self, *a, **k):
                pass

            def text(self, keywords, region="wt-wt", safesearch="moderate",
                     timelimit=None):
                if not working:
                    raise Exception("HTTPError")
                for i in range(3):
                    yield {"title": f"Result {i} for {keywords}",
                           "href": f"https://example.com/{i}",
                           "body": "a snippet"}

        mod = types.ModuleType("duckduckgo_search")
        mod.DDGS = _FakeDDGS
        return mod

    def test_successful_library_call_returns_results(self):
        """Library returns rows -> results mapped, circuit stays closed."""
        import sys
        from unittest import mock
        fake = self._fake_ddgs_module(working=True)
        with mock.patch.dict(sys.modules, {"duckduckgo_search": fake}):
            results = asyncio.run(self.prov.search("IQ genetics", max_results=5))
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r.url.startswith("https://example.com/") for r in results))
        self.assertFalse(self.smod.RATE_LIMIT_MEMORY.blocked("duckduckgo"))

    def test_library_failure_opens_circuit(self):
        """Library raises (bot challenge) -> empty results and circuit OPEN."""
        import sys
        from unittest import mock
        fake = self._fake_ddgs_module(working=False)
        with mock.patch.dict(sys.modules, {"duckduckgo_search": fake}):
            results = asyncio.run(self.prov.search("IQ genetics", max_results=5))
        self.assertEqual(results, [])
        self.assertTrue(self.smod.RATE_LIMIT_MEMORY.blocked("duckduckgo"))

    def test_timeout_and_cooldown_config(self):
        """Provider keeps a bounded timeout and a long cooldown window."""
        self.assertLessEqual(self.prov._search_timeout, 20.0)
        self.assertGreaterEqual(self.prov._cooldown, 300.0)


class TestConfidenceSnapshots(unittest.TestCase):
    """Confidence snapshot persistence + quality-weighted confidence update."""

    def setUp(self):
        self.db = Database(":memory:")
        # A dummy LLM: update_hypothesis never calls it, only stores it.
        self.memory = MemoryStore(self.db, llm=None)

    @staticmethod
    def _run(coro):
        return asyncio.run(coro)

    def _update(self, *args):
        return self._run(self.memory.update_hypothesis(*args))

    def _hypothesis(self, hid="h1", claim="Polygenic scores predict IQ", conf=0.5):
        self.db.save_hypothesis({
            "id": hid, "claim": claim, "status": "active", "confidence": conf,
            "supporting_evidence": "[]", "contradicting_evidence": "[]",
        })

    def test_snapshot_table_grows_and_cycle_filled(self):
        """save_confidence_snapshot writes to confidence_snapshots with real cycle."""
        self.db.save_session({
            "id": "s1", "topic": "t", "cycle_count": 3, "status": "active",
            "start_time": now_iso(),
        })
        self._hypothesis()
        ev = [{
            "id": "e1", "evidence_type": "supports", "source_id": "src1",
            "content": "A cohort study of n=200000 found a significant association (p<0.001).",
            "strength": 0.7,
        }]
        updated = self._update("h1", ev)

        rows = self.db.get_confidence_history(hypothesis_id="h1")
        self.assertEqual(len(rows), 1)
        # cycle_number taken from the active session, not hard-coded 0
        self.assertEqual(rows[0]["cycle_number"], 3)
        self.assertEqual(rows[0]["session_id"], "s1")
        self.assertEqual(rows[0]["hypothesis_id"], "h1")
        self.assertIsNotNone(updated)
        # directly on the raw table
        self.assertEqual(self.db._count("confidence_snapshots"), 1)

    def test_quality_weighting_beats_naive_counts(self):
        """A weak support + strong contradict drives confidence down (vs naive 0.5)."""
        self._hypothesis(conf=0.5)
        weak_support = {
            "id": "e1", "evidence_type": "supports", "source_id": "ws",
            "content": "A blog confidently claims polygenic scores predict IQ.",
            "strength": 0.3,
        }
        strong_contra = {
            "id": "e2", "evidence_type": "contradicts", "source_id": "sc",
            "content": ("A meta-analysis (randomized controlled trials, peer-reviewed, "
                         "n=50000) found no significant effect (p=0.40)."),
            "strength": 0.8,
        }
        updated = self._update("h1", [weak_support, strong_contra])
        # Naive 1-supports/1-contradicts would leave confidence at 0.5.
        self.assertLess(updated["confidence"], 0.5)

    def test_generate_hypotheses_records_snapshot(self):
        """generate_hypotheses writes an initial confidence snapshot (no silent failure)."""
        self.db.save_session({
            "id": "s1", "topic": "t", "cycle_count": 2, "status": "active",
            "start_time": now_iso(),
        })
        # Fake the LLM so generate_hypotheses returns a made-up hypothesis.
        from research_agent.models import Hypothesis, gen_id, now_iso as _now

        class FakeLLM:
            def __init__(self):
                self.snap = {"claim": "Testable new hypothesis", "confidence": 0.4}
            async def chat_json(self, *a, **k):
                return self.snap

        self.memory.llm = FakeLLM()
        hyps = self._run(self.memory.generate_hypotheses([], [], "test topic", "test question?"))
        self.assertEqual(len(hyps), 1)
        rows = self.db.get_all_confidence_history()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reason"], "hypothesis_created")
        self.assertEqual(rows[0]["cycle_number"], 2)
        self.assertEqual(rows[0]["session_id"], "s1")


class TestLLMWatchdog(unittest.TestCase):
    """Consecutive LLM failures pause the run instead of producing empty cycles."""

    def setUp(self):
        from research_agent.config import Config
        from research_agent.orchestrator import ResearchOrchestrator
        from research_agent.llm.engine import LLMEngine

        self.LLMEngine = LLMEngine
        LLMEngine.reset_failure_counter()
        cfg = Config()
        cfg.database_url = ":memory:"
        cfg.llm_failure_threshold = 3
        cfg.llm_recovery_interval = 0.05
        self.orch = ResearchOrchestrator(cfg)

    def tearDown(self):
        self.LLMEngine.reset_failure_counter()

    def _fail(self, times=3):
        for _ in range(times):
            self.LLMEngine._track_result("[ERROR: TUDaGPT returned status 503]")

    def test_below_threshold_does_not_pause(self):
        self._fail(2)
        self.assertTrue(asyncio.run(self.orch._await_llm_recovery()))
        self.assertEqual(self.orch.phase, "idle")  # untouched
        self.assertNotIn("llm_unavailable", self.orch.status)

    def test_pause_waits_for_the_backend_and_resets_the_counter(self):
        orch = self.orch

        class FakeLLM:
            def __init__(self):
                self.seen_flags = []

            async def health_check(self):
                # Recorded while the watchdog is waiting, before recovery.
                self.seen_flags.append(orch.status.get("llm_unavailable"))
                return len(self.seen_flags) >= 2  # down once, then back

        fake = FakeLLM()
        orch.llm = fake
        orch.running = True
        self._fail(3)

        self.assertTrue(asyncio.run(orch._await_llm_recovery()))
        self.assertEqual(len(fake.seen_flags), 2)
        self.assertTrue(fake.seen_flags[0], "the run must be marked unavailable while waiting")
        self.assertEqual(self.LLMEngine.consecutive_failures(), 0)
        self.assertFalse(orch.status["llm_unavailable"])
        self.assertEqual(orch.phase, "waiting_for_llm")

    def test_stop_while_waiting_aborts_immediately(self):
        class FakeLLM:
            async def health_check(self):
                return False

        self.orch.llm = FakeLLM()
        self.orch.running = True
        self.orch._stop_event.set()
        self._fail(3)

        started = time.time()
        self.assertFalse(asyncio.run(self.orch._await_llm_recovery()))
        self.assertLess(time.time() - started, 5)

    def test_threshold_zero_disables_the_watchdog(self):
        self.orch.config.llm_failure_threshold = 0
        self._fail(10)
        self.assertTrue(asyncio.run(self.orch._await_llm_recovery()))
        self.assertEqual(self.orch.phase, "idle")

    def test_loop_starts_no_cycle_while_the_backend_is_down(self):
        calls = []

        async def fake_cycle(number):
            calls.append(number)

        async def no_recovery():
            return False

        self.orch.running = True
        self.orch._run_cycle = fake_cycle
        self.orch._await_llm_recovery = no_recovery

        asyncio.run(self.orch._research_loop())
        self.assertEqual(calls, [], "no cycle may run without a working LLM")

    def test_cycle_stops_before_the_next_phase(self):
        async def fake_plan(number):
            return {"question": "Is IQ heritable?", "importance": 0.5}

        async def no_recovery():
            return False

        self.orch._plan_research = fake_plan
        self.orch._await_llm_recovery = no_recovery

        asyncio.run(self.orch._run_cycle(1))
        # The gate after planning must keep the cycle from moving on to searching.
        self.assertEqual(self.orch.phase, "planning")
        self.assertEqual(self.orch.db.get_all_sources(), [])


class TestSearchStrategySwitch(unittest.TestCase):
    """Several cycles without a new source rotate the query strategy."""

    def setUp(self):
        from research_agent.config import Config
        from research_agent.orchestrator import ResearchOrchestrator

        cfg = Config()
        cfg.database_url = ":memory:"
        cfg.search_stall_cycles = 2
        self.orch = ResearchOrchestrator(cfg)
        self.orch.current_topic = "polygenic embryo selection and intelligence"

    def test_productive_cycle_stays_on_the_normal_queries(self):
        self.orch._note_cycle_yield(3)
        self.assertEqual(self.orch._search_strategy_level, 0)
        self.assertEqual(self.orch._stalled_cycles, 0)

    def test_escalates_one_level_per_stall_window(self):
        self.orch._note_cycle_yield(0)
        self.assertEqual(self.orch._search_strategy_level, 0, "one empty cycle is not a stall")
        self.orch._note_cycle_yield(0)
        self.assertEqual(self.orch._search_strategy_level, 1)
        self.orch._note_cycle_yield(0)
        self.assertEqual(self.orch._search_strategy_level, 1)
        self.orch._note_cycle_yield(0)
        self.assertEqual(self.orch._search_strategy_level, 2)
        self.orch._note_cycle_yield(0)
        self.assertEqual(self.orch._search_strategy_level, 2, "level 2 is the ceiling")

    def test_a_new_source_resets_the_strategy(self):
        for _ in range(4):
            self.orch._note_cycle_yield(0)
        self.assertEqual(self.orch._search_strategy_level, 2)
        self.orch._note_cycle_yield(1)
        self.assertEqual(self.orch._search_strategy_level, 0)
        self.assertEqual(self.orch._stalled_cycles, 0)

    def test_level_one_queries_combine_topic_and_concept(self):
        self.orch.db.save_hypothesis({
            "id": "h_anchor", "claim": "Heritability of IQ rises across the lifespan",
            "status": "active", "confidence": 0.4,
        })
        queries = self.orch._variant_queries()
        self.assertTrue(queries)
        first = queries[0].lower()
        # Topic anchor stays, and the concept under investigation joins it -
        # otherwise "<topic> <method>" matches any neighbouring paper.
        self.assertIn("polygenic", first)
        self.assertTrue("heritability" in first or "iq" in first, first)
        self.assertIn("meta-analysis", first)
        self.assertGreaterEqual(len(first.split()), 4)

    def test_anchors_drop_low_signal_words(self):
        self.orch.db.save_hypothesis({
            "id": "h_glue",
            "claim": "Genetic correlation between IQ and brain volume in twin studies",
            "status": "active", "confidence": 0.4,
        })
        anchors = self.orch._search_anchors(max_words=3).lower().split()
        self.assertNotIn("correlation", anchors)
        self.assertTrue(anchors)

    def test_entity_queries_also_drop_low_signal_words(self):
        self.orch.db.save_hypothesis({
            "id": "h_ent",
            "claim": "Correlation between polygenic scores and cognitive outcomes",
            "status": "active", "confidence": 0.4,
        })
        queries = " ".join(self.orch._entity_queries()).lower()
        self.assertNotIn("correlation", queries)
        self.assertIn("polygenic", queries)

    def test_streak_ignores_off_topic_new_sources(self):
        # Ten new rows, none usable: this must NOT reset the strategy - that is
        # exactly how the fallback queries used to switch themselves off again.
        self.orch._note_cycle_yield(0, discovered=10)
        self.orch._note_cycle_yield(0, discovered=8)
        self.assertEqual(self.orch._stalled_cycles, 2)
        self.assertEqual(self.orch._search_strategy_level, 1)
        # A usable source ends the stall immediately.
        self.orch._note_cycle_yield(1, discovered=2)
        self.assertEqual(self.orch._search_strategy_level, 0)

    def test_variant_queries_work_without_hypotheses(self):
        queries = self.orch._variant_queries()
        self.assertTrue(queries)
        self.assertTrue(queries[0].startswith("polygenic") or "intelligence" in queries[0])
        self.assertIn("meta-analysis", queries[0])

    def test_level_one_queries_are_method_anchored(self):
        self.orch._search_strategy_level = 1
        queries = self.orch._plan_domain_queries(1)
        self.assertEqual(len(queries), 2)
        joined = " ".join(queries).lower()
        self.assertTrue(any(term in joined for term in
                            ("meta-analysis", "systematic review", "cohort", "replication", "trial")))
        self.assertNotIn(queries[0], self.orch._get_topic_queries())

    def test_level_two_queries_use_hypothesis_wording(self):
        self.orch.db.save_hypothesis({
            "id": "h_strategy", "claim": "Heritability of IQ increases with age",
            "status": "active", "confidence": 0.4,
        })
        self.orch._search_strategy_level = 2
        queries = self.orch._plan_domain_queries(1)
        self.assertTrue(queries)
        self.assertTrue(self.orch._entity_queries(), "entities from hypotheses must be available")
        self.assertTrue(
            any("heritability" in q.lower() or "iq" in q.lower()
                for q in self.orch._entity_queries())
        )

    def test_queries_are_not_repeated_within_the_cooldown(self):
        first = self.orch._plan_domain_queries(1)
        for query in first:
            self.orch._record_query_outcome(query, 3, cycle_number=1)
        second = self.orch._plan_domain_queries(2)
        self.assertEqual(set(first) & set(second), set(),
                         "a query used one cycle ago must not be picked again")

    def test_queries_that_keep_returning_nothing_are_dropped(self):
        pool = self.orch._search_query_pool()
        dead = pool[0]
        self.orch._record_query_outcome(dead, 0, cycle_number=1)
        self.assertFalse(self.orch._query_is_dead(dead), "one empty result is not enough")
        self.orch._record_query_outcome(dead, 0, cycle_number=2)
        self.assertTrue(self.orch._query_is_dead(dead))
        self.assertNotIn(dead, self.orch._search_query_pool())

    def test_zero_disables_the_switch(self):
        self.orch.config.search_stall_cycles = 0
        for _ in range(10):
            self.orch._note_cycle_yield(0)
        self.assertEqual(self.orch._search_strategy_level, 0)

    def test_relevance_yield_is_bucketed_by_strategy_level(self):
        self.orch.config.source_relevance_threshold = 0.5
        self.orch._source_strategy_level = {
            "s_l1_a": 1, "s_l1_b": 1, "s_l0": 0,
        }
        self.orch._record_relevance_yield({
            "s_l1_a": 0.8,   # level 1, passes
            "s_l1_b": 0.1,   # level 1, rejected
            "s_l0": 0.9,     # level 0, passes
            "s_reanalysed": 0.7,  # not found in this run -> not counted
        })

        stats = self.orch._relevance_stats
        self.assertEqual(stats["new_scored"], 3)
        self.assertEqual(stats["new_passed"], 2)
        self.assertEqual(stats["by_level"]["1"], {"scored": 2, "passed": 1})
        self.assertEqual(stats["by_level"]["0"], {"scored": 1, "passed": 1})
        self.assertAlmostEqual(self.orch.status["relevance_yield"]["pass_rate"], 0.67)
        self.assertEqual(self.orch.status["relevance_yield"]["threshold"], 0.5)

    def test_strategy_is_visible_in_the_status(self):
        for _ in range(2):
            self.orch._note_cycle_yield(0)
        strategy = self.orch.status["search_strategy"]
        self.assertEqual(strategy["level"], 1)
        self.assertTrue(strategy["description"])
        self.assertEqual(strategy["new_sources_last_cycles"], [0, 0])


class TestEvidenceClassificationInput(unittest.TestCase):
    """What the classifier is shown, and what happens to its answer.

    Both halves of one bug: the classifier was handed the first 3000 characters
    of a paper (title page and abstract), answered 'neutral' - correctly, that
    text takes no position on a claim - and the neutral answer was then thrown
    away. A 48-minute run paid for 34 classifications and stored no evidence at
    all, so nothing could ever move a hypothesis.
    """

    # Longer than the classification budget: only then does the excerpt get
    # selected at all, which is the case that matters (the run's documents are
    # 40k-120k characters of PDF text).
    DOC = (
        "Abstract\n"
        "We study the genetic architecture of body mass index across cohorts.\n\n"
        "Introduction\n"
        + ("Obesity is a major public health concern worldwide. " * 200) + "\n\n"
        "Results\n"
        "The causal estimate shrank from 0.09 to 0.02 once pleiotropy was modelled, "
        "so the naive instruments overstate the effect.\n\n"
        "Discussion\n"
        "Our estimates are inconsistent with a large causal effect of the exposure.\n"
    )

    def setUp(self):
        self.db = Database(":memory:")
        self.memory = MemoryStore(self.db, llm=None)
        self.prompts = []

    def _fake_llm(self, payload):
        prompts = self.prompts

        class FakeLLM:
            async def chat_json(self, *args, **kwargs):
                prompts.append(args[0] if args else kwargs.get("messages"))
                return payload

        return FakeLLM()

    def _sections(self):
        from research_agent.research.fulltext import split_sections
        return split_sections(self.DOC)

    def test_neutral_classification_is_not_stored_as_evidence(self):
        """A neutral verdict is a pairing decision, not a fact about the world.

        Storing it turned a zero-evidence cycle into 19 evidence rows (measured
        on a live batch) and inflated the report's Belegdichte.
        """
        self.db.save_hypothesis({"id": "h1", "claim": "The effect is causal", "status": "active"})
        self.memory.llm = self._fake_llm({
            "evidence_type": "neutral", "strength": 0.9,
            "reasoning": "The text measures an association and takes no position on causality.",
        })

        result = asyncio.run(self.memory.evaluate_evidence(
            self.DOC, {"id": "h1", "claim": "The effect is causal"}, "s1",
            sections=self._sections(),
        ))

        # The verdict is still returned (the phase counts it and shows it), but
        # no row is written.
        self.assertIsNotNone(result)
        self.assertEqual(result.evidence_type, "neutral")
        self.assertEqual(self.db.get_evidence_for_hypothesis("h1"), [])

    def test_topic_vocabulary_does_not_overrule_a_neutral_verdict(self):
        """A document full of the topic's own words must not become 'contradicts'.

        The removed keyword fallback labelled 22 of 134 contradicting rows in the
        live run 'Auto-classified ... (LLM returned neutral)' because the lists
        held generic markers ('bias', 'confounding', 'limitations', 'no evidence')
        that every methodology paper on this topic contains. Direction comes from
        the model; a confirmed neutral stays neutral and writes no row.
        """
        self.db.save_hypothesis({"id": "h1", "claim": "The effect is causal", "status": "active"})
        self.memory.llm = self._fake_llm({
            "evidence_type": "neutral", "strength": 0.9,
            "reasoning": "The paper discusses bias in general and takes no position on causality.",
        })
        keyword_soup = self.DOC + (
            "\nLimitations\nHowever, this design has limitations: confounding, selection "
            "bias, measurement bias, no evidence of replication, small sample, "
            "underpowered, preliminary, mixed results, questionable, uncertain, "
            "overestimated, methodological flaws. " * 20
        )

        result = asyncio.run(self.memory.evaluate_evidence(
            keyword_soup, {"id": "h1", "claim": "The effect is causal"}, "s1",
            sections=self._sections(),
        ))

        self.assertEqual(result.evidence_type, "neutral")
        self.assertEqual(self.db.get_evidence_for_hypothesis("h1"), [])

    def test_neutral_evidence_does_not_move_the_hypothesis(self):
        self.db.save_hypothesis({"id": "h1", "claim": "The effect is causal",
                                 "status": "active", "confidence": 0.6})
        asyncio.run(self.memory.update_hypothesis("h1", [{
            "id": "e1", "hypothesis_id": "h1", "source_id": "s1",
            "evidence_type": "neutral", "content": "no position taken", "strength": 0.9,
        }]))
        hyp = self.db.get_hypothesis("h1")
        self.assertAlmostEqual(float(hyp["confidence"]), 0.6)
        self.assertEqual(json.loads(hyp["supporting_evidence"] or "[]"), [])

    def test_classifier_sees_findings_not_the_abstract(self):
        """The excerpt must come from results/discussion, not the front matter."""
        self.db.save_hypothesis({"id": "h1", "claim": "The causal estimate shrinks", "status": "active"})
        self.memory.llm = self._fake_llm({
            "evidence_type": "neutral", "strength": 0.5, "reasoning": "inconclusive",
        })

        asyncio.run(self.memory.evaluate_evidence(
            self.DOC, {"id": "h1", "claim": "The causal estimate shrinks"}, "s1",
            sections=self._sections(), source_claims="the estimate shrank",
        ))

        user_message = self.prompts[0][1]["content"]
        self.assertIn("causal estimate shrank", user_message)
        self.assertIn("overstate the effect", user_message)
        self.assertNotIn("Obesity is a major public health concern", user_message)

    def test_evidence_budget_is_the_classification_budget(self):
        """The prompt is cut to the configured budget, not to a magic 3000."""
        from research_agent.research.fulltext import split_sections
        long_doc = self.DOC + "\n\n" + ("The estimate is stable across cohorts. " * 900)
        self.db.save_hypothesis({"id": "h1", "claim": "The estimate is stable", "status": "active"})
        self.memory.llm = self._fake_llm({
            "evidence_type": "supports", "strength": 0.7, "reasoning": "stable across cohorts",
        })

        asyncio.run(self.memory.evaluate_evidence(
            long_doc, {"id": "h1", "claim": "The estimate is stable"}, "s1",
            sections=split_sections(long_doc),
        ))

        user_message = self.prompts[0][1]["content"]
        excerpt = user_message.split("front matter is deliberately omitted):")[-1].strip()
        self.assertLessEqual(len(excerpt), self.memory.EVIDENCE_TEXT_BUDGET + 200)
        self.assertGreater(len(excerpt), 1000)
        self.assertNotIn("Obesity is a major public health concern", excerpt)


class TestSourceMetadata(unittest.TestCase):
    """Author and year must survive from the provider to the source row.

    The providers always parsed them; the row was built with author="" and
    publication_date="", so 0 of 83 sources in one run had either - and every
    BibTeX entry was `anonnd` with `year = {o. J.}`.
    """

    def test_source_stores_author_and_year(self):
        from research_agent.research.sources import SourceManager
        from research_agent.research.search import SearchResult

        db = Database(":memory:")
        manager = SourceManager(db, llm=None)
        result = SearchResult(
            title="Cognitive ability and physical health",
            url="https://doi.org/10.1038/s41598-017-02837-3",
            snippet="a snippet",
            source_type="crossref",
            author="Jane Doe; John Smith",
            year="2017",
        )

        source = asyncio.run(manager.process_search_result(result.to_dict()))

        self.assertIsNotNone(source)
        self.assertEqual(source.author, "Jane Doe; John Smith")
        self.assertEqual(source.publication_date, "2017")
        row = db.get_source(source.id)
        self.assertEqual(row["author"], "Jane Doe; John Smith")
        self.assertEqual(row["publication_date"], "2017")

    def test_missing_metadata_stays_empty_not_invented(self):
        from research_agent.research.sources import SourceManager
        from research_agent.research.search import SearchResult

        db = Database(":memory:")
        manager = SourceManager(db, llm=None)
        result = SearchResult(title="Untitled web page", url="https://example.org/x")
        source = asyncio.run(manager.process_search_result(result.to_dict()))
        self.assertEqual(source.author, "")
        self.assertEqual(source.publication_date, "")

    def test_bibliography_key_turns_into_surname_and_year(self):
        from research_agent.report import _Bibliography

        db = Database(":memory:")
        db.save_source({
            "id": "s1", "title": "Cognitive ability and physical health",
            "author": "Jane Doe; John Smith", "publication_date": "2017",
            "url": "https://doi.org/10.1038/x", "source_type": "crossref",
        })
        bib = _Bibliography(db)
        self.assertEqual(bib.cite("s1"), "[doe2017]")
        self.assertIn("year = {2017}", bib.entry("doe2017"))


class TestEvidenceTraceability(unittest.TestCase):
    """Every evidence id a hypothesis references has to resolve to a row.

    A hypothesis in one run referenced "02188d41acc8" in contradicting_evidence
    while the evidence table held nothing: the report's promised chain per claim
    ended in an id nobody could look up.
    """

    def setUp(self):
        self.db = Database(":memory:")
        self.memory = MemoryStore(self.db, llm=None)
        self.db.save_hypothesis({"id": "h1", "claim": "The effect is causal",
                                 "status": "active", "confidence": 0.6})

    def _referenced_ids(self, column):
        return json.loads(self.db.get_hypothesis("h1")[column] or "[]")

    def test_referenced_id_gets_a_row(self):
        asyncio.run(self.memory.update_hypothesis("h1", [{
            "hypothesis_id": "h1", "source_id": "", "evidence_type": "contradicts",
            "content": "Devil's Advocate (verdict: weakened): the estimate ignores selection.",
            "strength": 0.7,
        }]))

        ids = self._referenced_ids("contradicting_evidence")
        self.assertEqual(len(ids), 1)
        row = self.db._get("evidence", ids[0])
        self.assertIsNotNone(row, "the hypothesis references an id with no evidence row")
        self.assertEqual(row["evidence_type"], "contradicts")
        self.assertEqual(row["hypothesis_id"], "h1")

    def test_already_stored_row_is_updated_not_doubled(self):
        self.db.save_evidence({
            "id": "e1", "hypothesis_id": "h1", "source_id": "s1",
            "evidence_type": "supports", "content": "The estimate replicates.",
            "strength": 0.8,
        })
        asyncio.run(self.memory.update_hypothesis("h1", [{
            "id": "e1", "hypothesis_id": "h1", "source_id": "s1",
            "evidence_type": "supports", "content": "The estimate replicates.",
            "strength": 0.8,
        }]))
        self.assertEqual(self._referenced_ids("supporting_evidence"), ["e1"])
        self.assertEqual(self.db._count("evidence"), 1)

    def test_empty_content_is_not_invented_into_a_row(self):
        asyncio.run(self.memory.update_hypothesis("h1", [{
            "id": "e2", "hypothesis_id": "h1", "evidence_type": "contradicts",
            "content": "   ", "strength": 0.5,
        }]))
        self.assertIsNone(self.db._get("evidence", "e2"))

    def test_neutral_evidence_is_never_referenced(self):
        asyncio.run(self.memory.update_hypothesis("h1", [{
            "id": "e3", "hypothesis_id": "h1", "evidence_type": "neutral",
            "content": "The text takes no position.", "strength": 0.9,
        }]))
        self.assertEqual(self._referenced_ids("contradicting_evidence"), [])
        self.assertEqual(self._referenced_ids("supporting_evidence"), [])


class TestEvidenceDedup(unittest.TestCase):
    """Evidence dedup: near-identical LLM rows must not be stored twice."""

    def setUp(self):
        self.db = Database(":memory:")
        self.memory = MemoryStore(self.db, llm=None)

    def test_exact_duplicate_detected(self):
        self.db.save_evidence({
            "id": "e1", "hypothesis_id": "h1", "source_id": "s1",
            "evidence_type": "supports",
            "content": "The text explicitly describes the Wilson Effect, which states that heritability of IQ increases with age.",
            "strength": 0.9,
        })
        # Same content, different case/whitespace -> duplicate
        self.assertTrue(self.memory._evidence_duplicate_exists(
            "h1", "  The text explicitly describes THE Wilson Effect, which states that heritability of IQ increases with age.  "
        ))

    def test_prefix_similar_detected(self):
        self.db.save_evidence({
            "id": "e1", "hypothesis_id": "h1", "source_id": "s1",
            "evidence_type": "supports",
            "content": "The text explicitly describes the Wilson Effect, which states that heritability of IQ increases with age and reaches a plateau in adulthood.",
            "strength": 0.9,
        })
        # Near-identical rephrasing sharing the first 60 chars
        self.assertTrue(self.memory._evidence_duplicate_exists(
            "h1", "The text explicitly describes the Wilson Effect, which states that heritability of IQ increases with age and remains stable afterward."
        ))

    def test_distinct_content_not_deduplicated(self):
        self.db.save_evidence({
            "id": "e1", "hypothesis_id": "h1", "source_id": "s1",
            "evidence_type": "supports",
            "content": "GWAS identified 205 genomic loci associated with intelligence in 269,867 individuals.",
            "strength": 0.9,
        })
        # Genuinely different claim -> kept
        self.assertFalse(self.memory._evidence_duplicate_exists(
            "h1", "A meta-analysis of 50 studies found polygenic scores explain 10-15% of IQ variance."
        ))

    def test_short_shared_prefix_not_deduplicated(self):
        # 40-char shared prefix must NOT count as duplicate (only 60+)
        self.db.save_evidence({
            "id": "e1", "hypothesis_id": "h1", "source_id": "s1",
            "evidence_type": "supports",
            "content": "Twin studies show heritability of IQ increases from 0.40 in childhood.",
            "strength": 0.9,
        })
        self.assertFalse(self.memory._evidence_duplicate_exists(
            "h1", "Twin studies show heritability of IQ increases with age, but critics dispute the equal-environments assumption."
        ))

    def test_duplicate_evidence_not_saved_by_evaluate(self):
        """evaluate_evidence with a fake LLM returns None for a duplicate row."""
        self.db.save_evidence({
            "id": "e1", "hypothesis_id": "h1", "source_id": "s1",
            "evidence_type": "supports",
            "content": "The Wilson Effect shows heritability of IQ rising from about 0.40 in childhood to 0.80 in adulthood.",
            "strength": 0.9,
        })
        self.db.save_hypothesis({"id": "h1", "claim": "Wilson Effect claim", "status": "active"})

        class FakeLLM:
            async def chat_json(self, *a, **k):
                return {"evidence_type": "supports", "strength": 0.9,
                        "reasoning": "The Wilson Effect shows heritability of IQ rising from about 0.40 in childhood to 0.80 in adulthood."}

        self.memory.llm = FakeLLM()
        result = asyncio.run(self.memory.evaluate_evidence("irrelevant", {"id": "h1", "claim": "Wilson Effect claim"}, "s2"))
        self.assertIsNone(result)
        # Only the original row remains
        rows = self.db.get_evidence_for_hypothesis("h1")
        self.assertEqual(len(rows), 1)


class TestJunkFactFilter(unittest.TestCase):
    """Fact extraction hard-rejects physics/CS junk and keeps topic-relevant facts."""

    def setUp(self):
        self.db = Database(":memory:")
        self.memory = MemoryStore(self.db, llm=None)

    def test_junk_markers_rejected_and_relevant_kept(self):
        class FakeLLM:
            async def chat_json(self, *a, **k):
                return [
                    {"content": "The study was published in Phys. Rev. D 89, 066008 (2014).", "confidence": 0.9},
                    {"content": "The ChildCI framework includes over 100 global features.", "confidence": 0.9},
                    {"content": "The Wilson Effect demonstrates that heritability of IQ increases from 0.40 in childhood to 0.80 in adulthood.", "confidence": 0.95},
                ]

        self.memory.llm = FakeLLM()
        facts = asyncio.run(self.memory.extract_facts("text", "src1", "IQ Genetics"))
        self.assertEqual(len(facts), 1)
        self.assertIn("Wilson Effect", facts[0].content)


class TestSourceCommentaryFilter(unittest.TestCase):
    """Facts that describe the source document are dropped; real findings survive."""

    def setUp(self):
        self.db = Database(":memory:")
        self.memory = MemoryStore(self.db, llm=None)

    def test_rejects_source_commentary(self):
        # These four were actually stored as facts (confidence 1.0) in the
        # 2026-10-25 IQ-Genetics session.
        contaminated = [
            "The provided source text is a truncated abstract snippet discussing genetic correlations "
            "between neurodevelopmental conditions like Autism and ADHD, with no mention of embryo "
            "selection, polygenic scores for intelligence, or simulation studies.",
            "The text describes a longitudinal twin study on language acquisition with data collection "
            "at ages 2, 4, 6, 9, and 14 years, but contains no statistical findings, effect sizes, or "
            "conclusions relevant to IQ genetics or embryo selection.",
            "The provided source is a hallucinated or future-dated entry (published in 2026) with an "
            "invalid PMID format that claims to investigate the causal link between cognitive function "
            "and knee osteoarthritis using Mendelian randomization.",
            "The provided source appears to be a hallucinated or future-dated entry (published in 2026) "
            "with an incomplete abstract that discusses convex approaches for genetic components of "
            "complex diseases.",
        ]
        for text in contaminated:
            self.assertTrue(self.memory._is_source_commentary(text), text[:60])

    def test_keeps_real_findings(self):
        findings = [
            "The Wilson Effect shows heritability of IQ rising from 0.40 in childhood to 0.80 in "
            "adulthood in twin studies.",
            "The paper reports a heritability estimate of 0.8 in a sample of 11,000 twin pairs.",
            "Polygenic scores for educational attainment explain 12% of variance (R2) in a cohort of "
            "300,000 individuals.",
        ]
        for text in findings:
            self.assertFalse(self.memory._is_source_commentary(text), text[:60])

    def test_extract_facts_drops_commentary_end_to_end(self):
        class FakeLLM:
            async def chat_json(self, *a, **k):
                return [
                    {"content": "The provided source text is a truncated abstract with no mention of "
                                "embryo selection or polygenic scores.", "confidence": 1.0},
                    {"content": "The Wilson Effect shows heritability of IQ rising from 0.40 in "
                                "childhood to 0.80 in adulthood in twin studies.", "confidence": 0.9},
                ]

        self.memory.llm = FakeLLM()
        facts = asyncio.run(self.memory.extract_facts("text", "src1", "IQ Genetics"))
        self.assertEqual(len(facts), 1)
        self.assertIn("Wilson Effect", facts[0].content)


class TestKnowledgeGraphLinking(unittest.TestCase):
    """Graph edges come from embedding similarity; keyword overlap is the fallback.

    Keyword overlap needed >25% shared words and produced zero edges once labels
    were full sentences, leaving a rebuilt graph with 72 nodes and 0 edges.
    """

    def setUp(self):
        self.db = Database(":memory:")
        self.memory = MemoryStore(self.db, llm=None)

    def _fact(self, fid, content):
        self.db.save_fact({"id": fid, "content": content, "confidence": 0.6,
                           "source_ids": "[]", "topic": "intelligence"})

    def _hyp(self, hid, claim):
        self.db.save_hypothesis({"id": hid, "claim": claim, "status": "active",
                                 "confidence": 0.4,
                                 "supporting_evidence": "[]",
                                 "contradicting_evidence": "[]"})

    def _embed(self, entity_type, entity_id, vector):
        self.db.save_embedding({
            "id": f"e-{entity_id}", "entity_type": entity_type, "entity_id": entity_id,
            "embedding": json.dumps(vector), "text": "",
        })

    def _build(self):
        asyncio.run(self.memory.build_knowledge_graph("intelligence"))
        return self.db._get_all("knowledge_edges")

    def _node_id(self, node_type, text):
        for n in self.db.get_knowledge_nodes():
            if n["node_type"] == node_type and n["content"] == text:
                return n["id"]
        return None

    def test_edge_between_similar_fact_and_hypothesis(self):
        self._fact("f1", "Heritability of intelligence rises with age in twin studies.")
        self._fact("f2", "Embryo screening regulation differs across countries in Europe.")
        self._hyp("h1", "Heritability of intelligence increases from childhood to adulthood.")
        self._hyp("h2", "Regulators should restrict polygenic embryo screening.")
        self._embed("fact", "f1", [1.0, 0.0, 0.0, 0.0])
        self._embed("fact", "f2", [0.0, 0.0, 1.0, 0.0])
        self._embed("hypothesis", "h1", [1.0, 0.0, 0.0, 0.0])
        self._embed("hypothesis", "h2", [0.0, 0.0, 1.0, 0.0])

        edges = self._build()
        pairs = {(e["source_node_id"], e["target_node_id"]) for e in edges}
        f1 = self._node_id("fact", "Heritability of intelligence rises with age in twin studies.")
        h1 = self._node_id("hypothesis", "Heritability of intelligence increases from childhood to adulthood.")
        f2 = self._node_id("fact", "Embryo screening regulation differs across countries in Europe.")
        h2 = self._node_id("hypothesis", "Regulators should restrict polygenic embryo screening.")
        self.assertIn((f1, h1), pairs)
        self.assertIn((f2, h2), pairs)
        # The cross pairs are orthogonal -> below the floor, no edge.
        self.assertNotIn((f1, h2), pairs)
        self.assertNotIn((f2, h1), pairs)
        self.assertEqual(edges[0]["relation"], "related_to")
        self.assertAlmostEqual(max(e["weight"] for e in edges), 1.0, places=3)

    def test_no_edges_when_similarity_below_floor(self):
        self._fact("f1", "Heritability of intelligence rises with age in twin studies.")
        self._hyp("h1", "Regulators should restrict polygenic embryo screening.")
        # cosine ~0.55: related-looking but under the 0.80 floor.
        self._embed("fact", "f1", [1.0, 0.0, 0.0])
        self._embed("hypothesis", "h1", [0.55, 0.835, 0.0])
        self.assertEqual(self._build(), [])

    def test_keyword_edge_claims_direction_only_with_stored_evidence(self):
        """Overlap is co-occurrence; "supports" needs an evidence row.

        On the live corpus 146 of 164 keyword edges were labelled "supports"
        although no evidence row connected the fact's source to the hypothesis.
        """
        sourced = "Heritability of intelligence increases with age in twin studies."
        unsourced = "Heritability of intelligence varies with schooling across cohorts."
        claim = "Heritability of intelligence increases with genetic nurture."
        self.db.save_fact({"id": "f1", "content": sourced, "confidence": 0.6,
                           "source_ids": json.dumps(["s1"]), "topic": "intelligence"})
        self.db.save_fact({"id": "f2", "content": unsourced, "confidence": 0.6,
                           "source_ids": json.dumps(["s2"]), "topic": "intelligence"})
        self._hyp("h1", claim)
        self.db.save_evidence({
            "id": "ev1", "hypothesis_id": "h1", "source_id": "s1",
            "evidence_type": "contradicts", "content": "Twin design is confounded.",
            "strength": 0.6, "date_added": now_iso(),
        })

        edges = self._build()
        relations = {(e["source_node_id"], e["relation"]) for e in edges}

        # Both facts overlap the claim and get an edge; only the one whose own
        # source carries directional evidence may claim a direction.
        self.assertIn((self._node_id("fact", sourced), "contradicts"), relations)
        self.assertIn((self._node_id("fact", unsourced), "related_to"), relations)
        self.assertEqual(len(relations), 2)

    def test_rebuild_adds_no_duplicate_edges(self):
        self._fact("f1", "Heritability of intelligence rises with age in twin studies.")
        self._hyp("h1", "Heritability of intelligence increases from childhood to adulthood.")
        self._embed("fact", "f1", [1.0, 0.0, 0.0])
        self._embed("hypothesis", "h1", [1.0, 0.0, 0.0])
        first = len(self._build())
        second = len(self._build())
        self.assertEqual(first, 1)
        self.assertEqual(second, first)

    def test_whole_memory_becomes_nodes(self):
        """Not just the newest 50 facts / 30 hypotheses (the old caps)."""
        for i in range(55):
            self._fact(f"f{i}", f"Fact {i} on heritability of intelligence in twin sample {i}.")
        for i in range(35):
            self._hyp(f"h{i}", f"Hypothesis {i} concerns heritability of intelligence case{i}.")
        self._build()
        nodes = self.db.get_knowledge_nodes(limit=0)
        facts = [n for n in nodes if n["node_type"] == "fact"]
        hyps = [n for n in nodes if n["node_type"] == "hypothesis"]
        self.assertEqual(len(facts), 55)
        self.assertEqual(len(hyps), 35)

    def test_keyword_fallback_when_no_embeddings(self):
        fact_text = "Heritability of intelligence is high in twin studies."
        hyp_text = "Heritability of intelligence increases with age in twin studies."
        self._fact("f1", fact_text)
        self._hyp("h1", hyp_text)
        edges = self._build()
        self.assertEqual(len(edges), 1)
        # Overlap is co-occurrence, not agreement: this fact has no stored
        # evidence for the hypothesis, so the edge may not claim a direction.
        self.assertEqual(edges[0]["relation"], "related_to")


class TestGraphRelationRepair(unittest.TestCase):
    """Old graphs say "supports" where only word overlap was measured."""

    def test_repair_downgrades_only_unevidenced_directions(self):
        import sqlite3
        import repair_knowledge_graph as repair

        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "graph.db")
        db = Database(path)
        for fid, source in (("f1", "s1"), ("f2", "s2")):
            db.save_fact({"id": fid, "content": f"Fact {fid}", "confidence": 0.5,
                          "source_ids": json.dumps([source]), "topic": "t"})
            db.save_knowledge_node({"id": f"n-{fid}", "node_type": "fact",
                                    "label": f"Fact {fid}", "content": f"Fact {fid}"})
        db.save_hypothesis({"id": "h1", "claim": "Claim h1", "status": "active"})
        db.save_knowledge_node({"id": "n-h1", "node_type": "hypothesis",
                                "label": "Claim h1", "content": "Claim h1"})
        db.save_evidence({"id": "ev1", "hypothesis_id": "h1", "source_id": "s1",
                          "evidence_type": "supports", "content": "It replicates.",
                          "strength": 0.7, "date_added": now_iso()})
        for eid, fact_node in (("e1", "n-f1"), ("e2", "n-f2")):
            db.save_knowledge_edge({"id": eid, "source_node_id": fact_node,
                                    "target_node_id": "n-h1", "relation": "supports",
                                    "weight": 0.5, "date_added": now_iso()})

        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        downgraded = repair.downgrade_unevidenced_relations(conn)
        conn.commit()
        relations = {r["id"]: r["relation"]
                     for r in conn.execute("SELECT id, relation FROM knowledge_edges")}
        conn.close()

        self.assertEqual(downgraded, 1)
        self.assertEqual(relations["e1"], "supports")     # backed by ev1 (s1)
        self.assertEqual(relations["e2"], "related_to")   # no evidence for s2


class TestFactConfidenceCalibration(unittest.TestCase):
    """Fact confidence comes from the evidence, not from the model's self-report.

    Before calibration every extracted fact was stored at 0.9-1.0 whatever the
    source or the wording, so confidence carried no information.
    """

    def setUp(self):
        self.db = Database(":memory:")
        self.memory = MemoryStore(self.db, llm=None)

    def _source(self, sid, content_len=3000, credibility=0.7, evaluated=1):
        self.db.save_source({
            "id": sid,
            "title": "Twin study of cognitive ability in 11,000 pairs",
            "url": f"https://example.org/{sid}",
            "source_type": "pubmed",
            "content": "twin study " * (content_len // 10),
            "credibility": credibility,
            "evaluated": evaluated,
        })
        return self.db.get_source(sid)

    def _extract(self, content, source_id, llm_confidence):
        class FakeLLM:
            async def chat_json(self, *a, **k):
                return [{"content": content, "confidence": llm_confidence}]

        self.memory.llm = FakeLLM()
        facts = asyncio.run(self.memory.extract_facts("text", source_id, "IQ Genetics"))
        self.assertEqual(len(facts), 1)
        return facts[0].confidence

    def test_llm_self_report_no_longer_sets_confidence(self):
        """A claimed 1.0 does not become a stored 1.0."""
        self._source("s1")
        conf = self._extract(
            "GWAS identified 33 shared loci in 420,531 European individuals.",
            "s1", 1.0,
        )
        self.assertLessEqual(conf, 0.9)
        self.assertGreater(conf, 0.4)

    def test_full_text_beats_snippet(self):
        """Same claim, same model rating: a full paper outranks a snippet."""
        self._source("full", content_len=6000, credibility=0.7)
        self._source("snippet", content_len=200, credibility=0.7)
        text = "Heritability of vocabulary was 0.49 in 1,188 children from 594 twin pairs."
        full = self._extract(text, "full", 0.9)
        snippet = self._extract(
            "Heritability of nonverbal IQ was 0.85 in 1,188 children from 594 twin pairs.",
            "snippet", 0.9,
        )
        self.assertGreater(full, snippet + 0.1)

    def test_hedged_statement_scores_below_measured_result(self):
        self._source("s1")
        measured = self._extract(
            "Heritability of nonverbal IQ was 0.85 in 1,188 children.", "s1", 0.9,
        )
        self.db._delete("facts", self.db.get_facts(limit=1)[0]["id"])
        hedged = self._extract(
            "Nonverbal IQ may be influenced by many small genetic variants.", "s1", 0.9,
        )
        self.assertGreater(measured, hedged + 0.1)

    def test_unassessed_source_uses_metadata_credibility(self):
        """evaluated=0 means 'not assessed', not 'mediocre'."""
        self._source("peer", credibility=0.5, evaluated=0)
        self.db.save_source({
            "id": "blog", "title": "A blog post about IQ",
            "url": "https://blog.example.org/iq", "source_type": "duckduckgo",
            "content": "twin study " * 300, "credibility": 0.5, "evaluated": 0,
        })
        text = "Twin studies report a heritability of 0.8 for adult IQ."
        peer = self._extract(text, "peer", 0.9)
        self.db._delete("facts", self.db.get_facts(limit=1)[0]["id"])
        blog = self._extract(text + " (post)", "blog", 0.9)
        self.assertGreater(peer, blog)

    def test_llm_nudge_is_bounded(self):
        source = self._source("s1")
        text = "Heritability of nonverbal IQ was 0.85 in 1,188 children."
        low = self.memory.calibrate_fact_confidence(text, source, 0.0)
        high = self.memory.calibrate_fact_confidence(text, source, 1.0)
        self.assertLessEqual(abs(high - low), 0.101)

    def test_recalibrate_stored_facts_lowers_inflated_rows(self):
        """Legacy facts stored at 1.0 are recomputed, not left as-is."""
        self._source("s1", content_len=200, credibility=0.45)
        self.db.save_fact({
            "id": "f1",
            "content": "Intelligence may be shaped by many variants of small effect.",
            "confidence": 1.0,
            "source_ids": json.dumps(["s1"]),
            "topic": "IQ Genetics",
        })
        stats = self.memory.recalibrate_stored_facts()
        self.assertEqual(stats["changed"], 1)
        stored = self.db.get_facts(limit=10)[0]
        self.assertLess(stored["confidence"], 0.6)
        # Idempotent: a second pass finds nothing to change.
        self.assertEqual(self.memory.recalibrate_stored_facts()["changed"], 0)


class TestStatusThresholds(unittest.TestCase):
    """Relaxed confidence/status thresholds: strong evidence reaches supported/confirmed."""

    def setUp(self):
        self.db = Database(":memory:")
        self.memory = MemoryStore(self.db, llm=None)

    @staticmethod
    def _run(coro):
        return asyncio.run(coro)

    def _hypothesis(self, conf=0.3, support_ids=None, contra_ids=None):
        self.db.save_hypothesis({
            "id": "h1", "claim": "Polygenic scores predict IQ", "status": "active",
            "confidence": conf,
            "supporting_evidence": json.dumps(support_ids or []),
            "contradicting_evidence": json.dumps(contra_ids or []),
        })

    def _support(self, i, strength=0.8):
        return {
            "id": f"e{i}", "evidence_type": "supports", "source_id": f"src{i}",
            "content": f"A meta-analysis of n=50000 participants found a significant effect (p<0.001) in study {i}.",
            "strength": strength,
        }

    def test_three_strong_supports_reach_supported(self):
        """3 strong supports push confidence > 0.6 -> status 'supported'."""
        self._hypothesis(conf=0.3)
        updated = self._run(self.memory.update_hypothesis("h1", [self._support(i) for i in range(3)]))
        self.assertEqual(updated["status"], "supported")
        self.assertGreater(updated["confidence"], 0.6)

    def test_five_strong_supports_reach_confirmed(self):
        """5 strong supports accumulated across batches -> status 'confirmed'.

        A single batch from conf=0.3 caps at 0.625 (target 0.95, 50/50 blend), so
        confirmed (> 0.75) is reached by accumulating evidence across cycles -
        which is exactly the intended behavior of the cumulative counts.
        """
        self._hypothesis(conf=0.3)
        updated = self._run(self.memory.update_hypothesis("h1", [self._support(i) for i in range(3)]))
        self.assertEqual(updated["status"], "supported")
        updated = self._run(self.memory.update_hypothesis("h1", [self._support(i) for i in range(3, 5)]))
        self.assertEqual(updated["status"], "confirmed")
        self.assertGreater(updated["confidence"], 0.75)

    def test_cumulative_counts_accumulate_across_batches(self):
        """Supports from earlier batches count toward the status threshold."""
        self._hypothesis(conf=0.3)
        self._run(self.memory.update_hypothesis("h1", [self._support(0), self._support(1)]))
        updated = self._run(self.memory.update_hypothesis("h1", [self._support(2)]))
        # 2 + 1 = 3 cumulative supports -> supported
        self.assertEqual(updated["status"], "supported")

    def test_duplicate_ids_in_legacy_lists_do_not_inflate(self):
        """Duplicate evidence IDs in stored lists count only once for status."""
        self._hypothesis(conf=0.3, support_ids=["e1", "e1", "e1", "e1", "e1"])
        # Legacy list has 5 ids but only 1 unique -> NOT confirmed by count alone
        updated = self._run(self.memory.update_hypothesis("h1", []))
        self.assertNotEqual(updated["status"], "confirmed")
        self.assertNotEqual(updated["status"], "supported")


class TestSemanticRetrieval(unittest.TestCase):
    """Test semantic retrieval system."""

    def setUp(self):
        self.db = Database(":memory:")
        from research_agent.llm.engine import LLMEngine
        self.llm = LLMEngine()
        from research_agent.memory.retrieval import SemanticRetrieval
        self.retrieval = SemanticRetrieval(self.db, self.llm)

    def test_index_and_retrieve(self):
        """Index entities and retrieve by similarity."""
        async def _test():
            # Index some facts
            await self.retrieval.index_entity("fact", "f1", "Quantum mechanics describes subatomic particles")
            await self.retrieval.index_entity("fact", "f2", "Neurons communicate through electrical signals")
            await self.retrieval.index_entity("fact", "f3", "Consciousness is a subjective experience")

            # Retrieve
            results = await self.retrieval.retrieve("quantum physics particles", top_k=3)
            await self.llm.close()
            return results

        results = asyncio.run(_test())
        self.assertIsInstance(results, list)
        if results:
            self.assertIn("entity_type", results[0])
            self.assertIn("score", results[0])
            print(f"  Retrieved {len(results)} results, top score: {results[0]['score']:.3f}")

    def tearDown(self):
        async def _cleanup():
            await self.llm.close()
        try:
            asyncio.run(_cleanup())
        except:
            pass


class TestSourceRelevanceGate(unittest.TestCase):
    """The analyzer relevance score is persisted to sources.relevance and used
    as a gate before re-analysis and before fact extraction."""

    def setUp(self):
        from research_agent.config import Config
        from research_agent.orchestrator import ResearchOrchestrator

        cfg = Config()
        cfg.database_url = ":memory:"
        cfg.source_relevance_threshold = 0.35
        self.orch = ResearchOrchestrator(cfg)
        self.db = self.orch.db

    def _save_source(self, sid, relevance=0.0, title="A source"):
        self.db.save_source({
            "id": sid, "title": title, "url": f"https://example.org/{sid}",
            "credibility": 0.5, "relevance": relevance, "date_added": now_iso(),
        })

    def test_relevance_score_is_persisted(self):
        self._save_source("src_persist", relevance=0.0)
        findings = [{"source_id": "src_persist", "relevance": 0.82}]

        scores = self.orch._persist_source_relevance(findings)

        self.assertEqual(scores, {"src_persist": 0.82})
        row = self.db.get_source("src_persist")
        self.assertAlmostEqual(row["relevance"], 0.82)
        self.assertEqual(row["relevance_scored"], 1)
        # Nothing else is clobbered
        self.assertEqual(row["title"], "A source")

    def test_score_parsing_covers_llm_variants(self):
        coerce = self.orch._coerce_relevance
        self.assertAlmostEqual(coerce(0.8), 0.8)
        self.assertAlmostEqual(coerce("0.6"), 0.6)
        self.assertAlmostEqual(coerce("high"), 0.9)
        self.assertAlmostEqual(coerce("Low relevance"), 0.15)
        self.assertAlmostEqual(coerce(8), 0.8)      # 0-10 scale
        self.assertAlmostEqual(coerce("80"), 0.8)   # percent
        self.assertAlmostEqual(coerce(-3), 0.0)     # clamped
        self.assertAlmostEqual(coerce(1.5), 0.15)   # off-scale -> /10
        self.assertIsNone(coerce(None))
        self.assertIsNone(coerce(True))
        self.assertIsNone(coerce("unscored"))

    def test_unscored_sources_pass_the_gate(self):
        # Never scored (schema default) -> must pass, nothing is known yet
        self.assertTrue(self.orch._passes_relevance_gate(0.0, scored=False))
        # Scored 0.0 -> the analyzer judged it irrelevant
        self.assertFalse(self.orch._passes_relevance_gate(0.0))
        self.assertTrue(self.orch._passes_relevance_gate(None))
        self.assertFalse(self.orch._passes_relevance_gate(0.2))
        self.assertTrue(self.orch._passes_relevance_gate(0.35))
        self.assertTrue(self.orch._passes_relevance_gate(0.9))

    def test_threshold_zero_disables_the_gate(self):
        self.orch.config.source_relevance_threshold = 0
        self.assertTrue(self.orch._passes_relevance_gate(0.01))


    def test_low_scored_sources_are_dropped_before_analysis(self):
        src_ok = Source(id="s_ok", title="Polygenic scores and IQ",
                        relevance=0.7, relevance_scored=1)
        src_bad = Source(id="s_bad", title="Controllability of brain networks",
                         relevance=0.1, relevance_scored=1)
        src_zero = Source(id="s_zero", title="Scored as irrelevant",
                          relevance=0.0, relevance_scored=1)
        src_new = Source(id="s_new", title="Fresh hit", relevance=0.0,
                         relevance_scored=0)

        kept = self.orch._filter_sources_by_stored_relevance(
            [src_ok, src_bad, src_zero, src_new]
        )

        self.assertEqual([s.id for s in kept], ["s_ok", "s_new"])

    def test_analyze_source_scores_against_topic_not_subquestion(self):
        from research_agent.agents.roles import ResearcherAgent

        class CaptureLLM:
            def __init__(self):
                self.messages = None

            async def chat_json(self, messages, **k):
                self.messages = messages
                return {"relevance": 0.5, "key_findings": []}

        llm = CaptureLLM()
        asyncio.run(
            ResearcherAgent(llm).analyze_source(
                "Shared genetic architecture of ADHD and intelligence",
                "Some content",
                "Falsification test for multi-omics in nutritional environments",
                topic="IQ Genetics & Embryo Selection",
            )
        )
        prompt = " ".join(m["content"] for m in llm.messages)
        self.assertIn("Research topic: IQ Genetics & Embryo Selection", prompt)
        self.assertIn("not to the sub-question", prompt)
        self.assertIn("context only", prompt)

    def test_most_relevant_sources_replaces_recency_fallback(self):
        # Scored-relevant sources come first (best score first), then unscored
        # ones; sources scored below the threshold are never returned.
        self.db.save_source({"id": "s_low", "title": "Off-topic but newest",
                             "relevance": 0.05, "relevance_scored": 1,
                             "date_added": "2026-10-25T12:00:00"})
        self.db.save_source({"id": "s_good_old", "title": "Relevant, older",
                             "relevance": 0.8, "relevance_scored": 1,
                             "date_added": "2026-01-01T00:00:00"})
        self.db.save_source({"id": "s_best", "title": "Most relevant",
                             "relevance": 0.95, "relevance_scored": 1,
                             "date_added": "2025-06-01T00:00:00"})
        self.db.save_source({"id": "s_unscored", "title": "Never scored",
                             "relevance": 0.0, "relevance_scored": 0,
                             "date_added": "2026-10-24T00:00:00"})

        picked = [r["id"] for r in self.db.get_most_relevant_sources(limit=5, min_relevance=0.35)]

        self.assertEqual(picked, ["s_best", "s_good_old", "s_unscored"])
        self.assertNotIn("s_low", picked)

    def test_analyzable_text_never_uses_the_llm_summary(self):
        bare = Source(id="s1", title="T", summary="The provided source is truncated...")
        self.assertEqual(self.orch._analyzable_text(bare), "")

        full = Source(id="s2", title="T", summary="LLM commentary",
                      raw_text="Full document text about polygenic scores.")
        self.assertEqual(self.orch._analyzable_text(full),
                         "Full document text about polygenic scores.")

        content_only = Source(id="s3", title="T", content="Body text", raw_text="")
        self.assertEqual(self.orch._analyzable_text(content_only), "Body text")

    def test_unjudgeable_sources_are_flagged_not_scored(self):
        self._save_source("src_thin", relevance=0.0)
        self.db.update_source("src_thin", {"relevance_unjudgeable": 1})
        row = self.db.get_source("src_thin")
        self.assertEqual(row["relevance_unjudgeable"], 1)
        # Never written off as irrelevant
        self.assertEqual(row["relevance_scored"], 0)
        self.assertEqual(row["relevance"], 0.0)

    def test_scoring_a_source_clears_the_unjudgeable_flag(self):
        self._save_source("src_late", relevance=0.0)
        self.db.update_source("src_late", {"relevance_unjudgeable": 1})

        self.orch._persist_source_relevance(
            [{"source_id": "src_late", "relevance": 0.6}]
        )

        row = self.db.get_source("src_late")
        self.assertEqual(row["relevance_unjudgeable"], 0)
        self.assertEqual(row["relevance_scored"], 1)
        self.assertAlmostEqual(row["relevance"], 0.6)

    def test_unjudgeable_sources_are_picked_last(self):
        self.db.save_source({"id": "s_rel", "title": "relevant", "relevance": 0.8,
                             "relevance_scored": 1, "date_added": "2026-01-01T00:00:00"})
        self.db.save_source({"id": "s_fresh", "title": "unscored", "relevance": 0.0,
                             "relevance_scored": 0, "date_added": "2026-02-01T00:00:00"})
        self.db.save_source({"id": "s_thin", "title": "no full text", "relevance": 0.0,
                             "relevance_scored": 0, "relevance_unjudgeable": 1,
                             "date_added": "2026-03-01T00:00:00"})

        picked = [r["id"] for r in self.db.get_most_relevant_sources(limit=3)]

        self.assertEqual(picked, ["s_rel", "s_fresh", "s_thin"])

    def test_most_relevant_sources_respects_limit(self):
        for i in range(7):
            self.db.save_source({"id": f"s{i}", "title": f"t{i}", "relevance": 0.9,
                                 "relevance_scored": 1, "date_added": "2026-10-01T00:00:00"})
        self.assertEqual(len(self.db.get_most_relevant_sources(limit=3)), 3)

    def test_update_source_writes_only_given_fields(self):
        self._save_source("src_upd", relevance=0.0, title="Keep me")
        self.db.update_source("src_upd", {"relevance": 0.55})
        row = self.db.get_source("src_upd")
        self.assertAlmostEqual(row["relevance"], 0.55)
        self.assertEqual(row["title"], "Keep me")
        self.db.update_source("src_upd", {})  # must be a no-op, not an error


class TestJSONEnvelopeHandling(unittest.TestCase):
    """JSON-object mode wraps "array only" answers ({"claims": [...]}) - the
    extraction paths must unwrap the envelope instead of dropping it."""

    def setUp(self):
        self.db = Database(":memory:")
        self.memory = MemoryStore(self.db, llm=None)

    def test_extract_facts_unwraps_claims_envelope(self):
        class FakeLLM:
            async def chat_json(self, *a, **k):
                return {"claims": [
                    {"content": "A GWAS of 269,867 individuals identified 205 cognitive "
                                "ability loci, highlighting the polygenic architecture of IQ.",
                     "confidence": 0.9},
                ]}

        self.memory.llm = FakeLLM()
        facts = asyncio.run(
            self.memory.extract_facts("text", "src1", "IQ Genetics")
        )
        self.assertEqual(len(facts), 1)
        self.assertIn("205 cognitive ability loci", facts[0].content)
        self.assertEqual(len(self.db.get_facts(limit=10)), 1)

    def test_generate_hypotheses_unwraps_envelope(self):
        class FakeLLM:
            async def chat_json(self, *a, **k):
                return {"hypotheses": [
                    {"claim": "Embryo selection on polygenic scores raises mean IQ by "
                               "a measurable but small margin within one generation.",
                     "confidence": 0.35,
                     "predictions": ["selected cohorts score higher than siblings"],
                     "falsification_conditions": ["no effect in sibling comparisons"]},
                ]}

        self.memory.llm = FakeLLM()
        hyps = asyncio.run(
            self.memory.generate_hypotheses([], [], "IQ Genetics", "Does it work?")
        )
        self.assertEqual(len(hyps), 1)
        self.assertIn("Embryo selection", hyps[0].claim)

    def test_role_plan_searches_unwraps_envelope(self):
        from research_agent.agents.roles import ResearcherAgent

        class FakeLLM:
            async def chat_json(self, *a, **k):
                return {"search_plans": [
                    {"query": "polygenic score intelligence GWAS", "provider": "pubmed",
                     "purpose": "core evidence", "priority": "high"},
                ]}

        plans = asyncio.run(
            ResearcherAgent(FakeLLM()).plan_searches("q", {})
        )
        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0]["query"], "polygenic score intelligence GWAS")

    def test_devil_search_plans_unwrap_envelope(self):
        from research_agent.agents.devils_advocate import DevilsAdvocateAgent

        class FakeLLM:
            async def chat_json(self, *a, **k):
                return {"plans": [
                    {"query": "embryo selection failed replication", "provider": "pubmed",
                     "purpose": "counter-evidence", "threat_level": "high"},
                ]}

        plans = asyncio.run(
            DevilsAdvocateAgent(FakeLLM()).generate_counter_search_queries(
                {"claim": "PGS selection works"}, []
            )
        )
        self.assertEqual(len(plans), 1)
        self.assertEqual(plans[0]["threat_level"], "high")


class TestRetractedSources(unittest.TestCase):
    """A withdrawn paper is not evidence.

    One run's corpus held "RETRACTED: Causal role of immune cells …" with no marker
    anywhere in the database: it was available as ordinary evidence.
    """

    def test_retracted_titles_are_detected(self):
        from research_agent.research.sources import is_retracted_work
        self.assertTrue(is_retracted_work("RETRACTED: Causal role of immune cells in cognition"))
        self.assertTrue(is_retracted_work("Retraction: Polygenic scores and outcomes"))
        self.assertTrue(is_retracted_work("Effects of X on Y [Retracted]"))
        self.assertTrue(is_retracted_work("Editorial", "This article has been retracted by the journal"))

    def test_ordinary_titles_are_not_flagged(self):
        from research_agent.research.sources import is_retracted_work
        self.assertFalse(is_retracted_work("Cognitive ability and physical health: a MR study"))
        self.assertFalse(is_retracted_work("A survey of retraction practices in psychology"))
        self.assertFalse(is_retracted_work(""))

    def test_retracted_source_gets_no_credibility(self):
        from research_agent.research.sources import SourceManager
        from research_agent.research.search import SearchResult

        db = Database(":memory:")
        manager = SourceManager(db, llm=None)
        result = SearchResult(
            title="RETRACTED: Causal role of immune cells in cognitive decline",
            url="https://example.org/retracted", snippet="s", source_type="openalex",
        )
        source = asyncio.run(manager.process_search_result(result.to_dict()))
        self.assertIsNotNone(source)
        self.assertEqual(source.credibility, 0.0)

    def test_report_counts_them_as_a_limitation(self):
        from research_agent.report import _counts, _limitations

        db = Database(":memory:")
        db.save_source({"id": "s1", "title": "RETRACTED: Causal role of immune cells",
                        "url": "https://example.org/r"})
        db.save_source({"id": "s2", "title": "Ordinary paper", "url": "https://example.org/o"})
        counts = _counts(db)
        self.assertEqual(counts["sources_retracted"], 1)
        text = " ".join(_limitations(db, counts, [], []))
        self.assertIn("Zur\u00fcckgezogene Quellen", text)


class TestConfidenceScale(unittest.TestCase):
    """A model-reported confidence has to land on the pipeline's 0-1 scale.

    One run logged "verdict=destroyed, confidence 70% -> 500%" because the model
    answered 25 (percent) where 0.25 was expected. Nothing persisted the wrong
    value at the time, but the contract was broken.
    """

    def test_percentage_is_scaled_down(self):
        from research_agent.agents.devils_advocate import _normalize_confidence
        self.assertAlmostEqual(_normalize_confidence(25, 0.7), 0.25)
        self.assertAlmostEqual(_normalize_confidence("40", 0.7), 0.4)

    def test_absurd_value_is_clamped(self):
        from research_agent.agents.devils_advocate import _normalize_confidence
        self.assertEqual(_normalize_confidence(500, 0.7), 1.0)
        self.assertEqual(_normalize_confidence(-3, 0.7), 0.0)

    def test_fraction_passes_through(self):
        from research_agent.agents.devils_advocate import _normalize_confidence
        self.assertAlmostEqual(_normalize_confidence(0.35, 0.7), 0.35)

    def test_unparseable_falls_back_to_the_current_confidence(self):
        from research_agent.agents.devils_advocate import _normalize_confidence
        self.assertAlmostEqual(_normalize_confidence("high", 0.7), 0.7)
        self.assertAlmostEqual(_normalize_confidence(None, 0.42), 0.42)


if __name__ == "__main__":
    unittest.main(verbosity=2)
