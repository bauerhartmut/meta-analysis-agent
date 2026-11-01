"""Offline tests for the federated research engine.

No network: fake providers, a fake LLM and an in-memory database. The point is
the parts that decide *which* sources a cycle gets to see - provider syntax,
duplicate merging, ranking and the query telemetry that retires dead queries.
"""

import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.config import Config
from research_agent.database import Database
from research_agent.models import gen_id, now_iso
from research_agent.orchestrator import ResearchOrchestrator
from research_agent.research.engine import (
    Candidate,
    PlannedQuery,
    QueryPlanner,
    ResearchEngine,
    build_terms,
    merge_candidates,
    rank_candidates,
    render_query,
)
from research_agent.research.search import SearchResult, describe_error
from research_agent.research import search as search_module


class _FakeProvider:
    def __init__(self, name, results=None, raises=False):
        self._name = name
        self.results = list(results or [])
        self.raises = raises
        self.calls = []

    @property
    def name(self):
        return self._name

    async def search(self, query, max_results=10, raw=False):
        self.calls.append({"query": query, "max": max_results, "raw": raw})
        if self.raises:
            raise RuntimeError(f"{self._name} down")
        return list(self.results)


class _FakeSearch:
    def __init__(self, providers):
        self.providers = {p.name: p for p in providers}


class _FakeLLM:
    def __init__(self, payload=None, raises=False):
        self.payload = payload
        self.raises = raises
        self.calls = 0

    async def chat_json(self, *args, **kwargs):
        self.calls += 1
        if self.raises:
            raise RuntimeError("planner backend down")
        return self.payload


def _result(title, url, snippet="", source_type="test"):
    return SearchResult(title=title, url=url, snippet=snippet, source_type=source_type)


class TestErrorReporting(unittest.TestCase):
    def test_exception_without_message_is_still_readable(self):
        """httpx.HTTPError and friends stringify to "": the log read
        "DuckDuckGo search error: " and the circuit opened with no reason."""
        class SilentError(Exception):
            def __str__(self):
                return ""

        text = describe_error(SilentError())
        self.assertIn("SilentError", text)

    def test_message_is_kept_with_its_class(self):
        text = describe_error(TimeoutError("timed out after 20s"))
        self.assertIn("TimeoutError", text)
        self.assertIn("timed out after 20s", text)


class TestCircuitEscalation(unittest.TestCase):
    """A provider that was rate limited a minute ago will be again.

    Measured on the run of 28.10.: 50 rate-limit retries and 24 circuit opens in
    17 minutes, and the search phase spent 84 s per cycle on providers that were
    still limited. The window grows with each repeat instead of retrying the same
    dead endpoint at full price every cycle.
    """

    def setUp(self):
        self.memory = search_module._RateLimitMemory()
        self.addCleanup(self.memory.reset)

    def _window(self, name="openalex"):
        import time

        return self.memory._blocked_until[name] - time.monotonic()

    def test_repeats_escalate_the_window(self):
        self.memory.penalize("openalex", 300, "429")
        first = self._window()
        self.memory.penalize("openalex", 300, "429")
        second = self._window()

        self.assertAlmostEqual(first, 300, delta=2)
        self.assertAlmostEqual(second, 600, delta=2)

    def test_the_window_is_capped(self):
        for _ in range(6):
            self.memory.penalize("openalex", 300, "429")

        self.assertLessEqual(self._window(), search_module.CIRCUIT_MAX_SECONDS + 1)

    def test_a_provider_that_was_quiet_starts_fresh(self):
        self.memory.penalize("openalex", 300, "429")
        # Pretend the last failure was long ago: the next one is not a repeat.
        self.memory._last_penalty["openalex"] = 0.0

        self.memory.penalize("openalex", 300, "429")

        self.assertAlmostEqual(self._window(), 300, delta=2)
        self.assertEqual(self.memory.report()["openalex"]["streak"], 1)

    def test_the_repeat_count_is_reported(self):
        self.memory.penalize("semantic_scholar", 300, "429")
        self.memory.penalize("semantic_scholar", 300, "429")

        self.assertEqual(self.memory.report()["semantic_scholar"]["streak"], 2)


class TestProviderSyntax(unittest.TestCase):
    def setUp(self):
        self.query = PlannedQuery(
            text="polygenic scores embryo selection",
            units=["polygenic score", "embryo selection"],
        )

    def test_field_syntax_per_provider(self):
        self.assertEqual(
            render_query("pubmed", self.query)[0],
            '"polygenic score"[tiab] AND "embryo selection"[tiab]',
        )
        self.assertEqual(
            render_query("arxiv", self.query)[0],
            'all:"polygenic score" AND all:"embryo selection"',
        )
        self.assertEqual(
            render_query("openalex", self.query)[0],
            '"polygenic score" AND "embryo selection"',
        )
        self.assertTrue(render_query("pubmed", self.query)[1], "field syntax must be sent raw")

    def test_plain_text_providers_get_the_readable_query(self):
        text, raw = render_query("crossref", self.query)
        self.assertEqual(text, "polygenic scores embryo selection")
        self.assertTrue(raw)
        text, raw = render_query("duckduckgo", self.query)
        self.assertFalse(raw, "DuckDuckGo must keep using natural language")

    def test_query_without_units_falls_back_to_text(self):
        text, _ = render_query("pubmed", PlannedQuery(text="polygenic embryo selection"))
        self.assertEqual(text, "polygenic embryo selection")


class TestDedupe(unittest.TestCase):
    def test_same_doi_from_three_providers_merges(self):
        merged, duplicates = merge_candidates([
            (_result("Polygenic scores and embryos", "https://pubmed.ncbi.nlm.nih.gov/123"),
             "q1", "pubmed"),
            (_result("Polygenic scores and embryos", "https://doi.org/10.1038/abc123"),
             "q1", "europepmc"),
            (_result("Polygenic scores and embryos (PDF)", "https://doi.org/10.1038/ABC123"),
             "q2", "openalex"),
        ])
        # PubMed carries no DOI, but the identical title identifies the work;
        # the openalex DOI matches case-insensitively.
        self.assertEqual(len(merged), 1)
        self.assertEqual(duplicates, 2)
        self.assertEqual(merged[0].providers, {"pubmed", "europepmc", "openalex"})
        self.assertEqual(len(merged[0].provenance), 3)

    def test_same_title_without_doi_merges(self):
        merged, duplicates = merge_candidates([
            (_result("The Wilson Effect: the increase in heritability of IQ with age",
                     "https://example.org/a"), "q", "crossref"),
            (_result("The Wilson effect - the increase in heritability of IQ with age",
                     "https://example.org/b"), "q", "semantic_scholar"),
        ])
        self.assertEqual(len(merged), 1)
        self.assertEqual(duplicates, 1)
        self.assertEqual(merged[0].providers, {"crossref", "semantic_scholar"})

    def test_different_papers_stay_separate(self):
        merged, duplicates = merge_candidates([
            (_result("Heritability of IQ in twins", "https://example.org/1"), "q", "pubmed"),
            (_result("Educational attainment GWAS in three million individuals",
                     "https://example.org/2"), "q", "pubmed"),
        ])
        self.assertEqual(len(merged), 2)
        self.assertEqual(duplicates, 0)

    def test_metadata_is_extracted_from_url_and_snippet(self):
        merged, _ = merge_candidates([
            (_result("A paper", "https://doi.org/10.1234/xyz",
                     "Smith. 2021. Cited: 42. Abstract..."), "q", "crossref"),
        ])
        candidate = merged[0]
        self.assertEqual(candidate.doi, "10.1234/xyz")
        self.assertEqual(candidate.year, 2021)
        self.assertEqual(candidate.citations, 42)


class TestRanking(unittest.TestCase):
    def _candidate(self, title, year=0, citations=0, providers=("pubmed",), snippet=""):
        return Candidate(
            title=title, url=f"https://example.org/{title[:10]}", snippet=snippet,
            year=year, citations=citations, providers=set(providers),
        )

    def test_on_topic_recent_cited_and_corroborated_wins(self):
        good = self._candidate(
            "Polygenic scores and embryo selection: measured outcomes",
            year=2024, citations=120, providers=("pubmed", "openalex", "europepmc"),
        )
        weak = self._candidate(
            "A history of beekeeping in Lower Saxony", year=1994, citations=0,
        )
        ranked = rank_candidates([weak, good], ["polygenic score", "embryo selection"],
                                 now_year=2026)
        self.assertEqual(ranked[0].title, good.title)
        self.assertGreater(ranked[0].score, ranked[1].score)

    def test_ranking_is_deterministic(self):
        a = self._candidate("Polygenic score prediction", year=2020, citations=10)
        b = self._candidate("Embryo selection ethics", year=2021, citations=5)
        first = [c.title for c in rank_candidates([a, b], ["polygenic score"], now_year=2026)]
        second = [c.title for c in rank_candidates([a, b], ["polygenic score"], now_year=2026)]
        self.assertEqual(first, second)

    def test_terms_come_from_units_and_topic(self):
        terms = build_terms(
            [PlannedQuery(text="x", units=["embryo selection"])], topic="polygenic IQ"
        )
        self.assertIn("embryo selection", terms)
        self.assertTrue(any("polygenic" in t for t in terms))

    def test_short_acronyms_survive_the_keyword_filter(self):
        # extract_keywords drops words under three letters, so "IQ Genetics"
        # would rank papers on "genetics" alone.
        terms = build_terms([], topic="IQ Genetics")
        self.assertIn("iq", terms)

    def test_iq_paper_outranks_generic_genetics_paper(self):
        iq_paper = Candidate(title="Does IQ predict school achievement?",
                             url="https://e.org/1", providers={"pubmed"})
        generic = Candidate(title="Genetics of barley yield",
                            url="https://e.org/2", providers={"pubmed"})
        ranked = rank_candidates([generic, iq_paper], build_terms([], topic="IQ Genetics"),
                                 now_year=2026)
        self.assertEqual(ranked[0].title, iq_paper.title)


class TestQueryPlanner(unittest.TestCase):
    def test_parses_envelope_and_caps(self):
        planned = QueryPlanner._parse({"queries": [
            {"text": "polygenic scores embryo selection", "phrases": ["polygenic score", "embryo selection"], "goal": "mechanism"},
            {"text": "polygenic scores embryo selection", "phrases": [], "goal": "duplicate"},
            {"text": "too short", "phrases": []},
            {"text": "cognitive outcomes of children conceived by IVF", "phrases": ["cognitive outcome", "IVF"]},
            {"text": "a fourth distinct query about heritability", "phrases": ["heritability"]},
        ]}, max_queries=3)
        self.assertEqual(len(planned), 3)
        self.assertEqual(planned[0].units, ["polygenic score", "embryo selection"])
        self.assertEqual(planned[0].goal, "mechanism")

    def test_planner_uses_llm_result(self):
        llm = _FakeLLM(payload={"queries": [
            {"text": "polygenic score embryo selection outcomes",
             "phrases": ["polygenic score", "embryo selection"]},
        ]})
        planned = asyncio.run(QueryPlanner(llm).plan(
            "Do polygenic scores predict outcomes?", "IQ genetics",
            fallbacks=["heritability IQ twin"], max_queries=3,
        ))
        self.assertEqual(len(planned), 1)
        self.assertEqual(llm.calls, 1)
        self.assertEqual(planned[0].origin, "planner")

    def test_planner_falls_back_when_the_llm_fails(self):
        llm = _FakeLLM(raises=True)
        planned = asyncio.run(QueryPlanner(llm).plan(
            "Do polygenic scores predict cognitive outcomes?",
            "polygenic embryo selection",
            fallbacks=["heritability IQ twin study", "GWAS cognitive ability"],
            max_queries=3,
        ))
        self.assertGreaterEqual(len(planned), 2)
        self.assertTrue(all(q.origin != "planner" for q in planned))
        self.assertEqual(planned[0].text, "heritability IQ twin study")

    def test_junk_llm_output_falls_back(self):
        planned = asyncio.run(QueryPlanner(_FakeLLM(payload={"nonsense": True})).plan(
            "question", "topic", fallbacks=["fallback query text"], max_queries=2,
        ))
        self.assertTrue(planned)
        self.assertEqual(planned[0].text, "fallback query text")


class TestEngineExecution(unittest.TestCase):
    def test_fan_out_merges_and_records_telemetry(self):
        db = Database(":memory:")
        paper = _result("Polygenic scores and embryo selection", "https://doi.org/10.9/x1",
                        "Smith. 2023. Cited: 7. Abstract")
        pubmed = _FakeProvider("pubmed", [paper])
        openalex = _FakeProvider("openalex", [paper])
        engine = ResearchEngine(_FakeSearch([pubmed, openalex]), db=db, planner=QueryPlanner(None))

        batch = asyncio.run(engine.execute(
            [PlannedQuery(text="polygenic score embryo selection",
                          units=["polygenic score", "embryo selection"])],
            topic="IQ genetics", cycle=1,
        ))

        self.assertEqual(len(batch.candidates), 1)
        self.assertEqual(batch.candidates[0].providers, {"pubmed", "openalex"})
        self.assertEqual(batch.duplicates, 1)
        # Each provider got the query in its own syntax, unshortened.
        self.assertEqual(pubmed.calls[0]["query"],
                         '"polygenic score"[tiab] AND "embryo selection"[tiab]')
        self.assertTrue(pubmed.calls[0]["raw"])
        rows = db.get_query_stats("IQ genetics")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["attempts"], 1)
        self.assertEqual(rows[0]["results"], 1)

    def test_one_failing_provider_does_not_kill_the_search(self):
        db = Database(":memory:")
        broken = _FakeProvider("pubmed", raises=True)
        working = _FakeProvider("openalex", [_result("A paper", "https://example.org/a")])
        engine = ResearchEngine(_FakeSearch([broken, working]), db=db, planner=QueryPlanner(None))

        batch = asyncio.run(engine.execute([PlannedQuery(text="a query text")], topic="t"))

        self.assertEqual(len(batch.candidates), 1)
        self.assertEqual(len(batch.failures), 1)
        self.assertIn("pubmed", batch.failures[0])

    def test_provider_that_swallows_its_error_is_still_a_failure(self):
        """A provider catching its own error must not read as "found nothing".

        Live log before the fix: "0 provider failure(s) for 4 queries" in a batch
        where DuckDuckGo had failed four times and opened its circuit.
        """
        class _SilentProvider:
            name = "duckduckgo"

            async def search(self, query, max_results=10, raw=False):
                self.last_error = "HTTPError: "
                return []

        db = Database(":memory:")
        engine = ResearchEngine(_FakeSearch([_SilentProvider()]), db=db,
                                planner=QueryPlanner(None))

        batch = asyncio.run(engine.execute([PlannedQuery(text="a query text")], topic="t"))

        self.assertEqual(len(batch.failures), 1)
        self.assertIn("duckduckgo", batch.failures[0])
        self.assertIn("HTTPError", batch.failures[0])

    def test_kept_recording_and_dead_query_retirement(self):
        db = Database(":memory:")
        provider = _FakeProvider("pubmed", [_result("Polygenic paper", "https://example.org/p")])
        engine = ResearchEngine(_FakeSearch([provider]), db=db, planner=QueryPlanner(None))
        query = PlannedQuery(text="polygenic score embryo selection")

        for cycle in (1, 2):
            batch = asyncio.run(engine.execute([query], topic="t", cycle=cycle))
        self.assertIn("polygenic score embryo selection", db.get_dead_queries("t"))

        # One kept candidate is enough to keep the query alive.
        engine.record_kept(batch, batch.candidates, cycle=3)
        self.assertEqual(db.get_dead_queries("t"), [])
        self.assertEqual(db.get_query_stats("t")[0]["kept"], 1)

    def test_disabled_without_database(self):
        provider = _FakeProvider("pubmed", [_result("A", "https://example.org/a")])
        engine = ResearchEngine(_FakeSearch([provider]), db=None, planner=QueryPlanner(None))
        batch = asyncio.run(engine.execute([PlannedQuery(text="a query")], topic="t"))
        self.assertEqual(len(batch.candidates), 1)
        engine.record_kept(batch, batch.candidates)  # must not raise


class TestOrchestratorWiring(unittest.TestCase):
    def setUp(self):
        cfg = Config()
        cfg.database_url = ":memory:"
        self.orch = ResearchOrchestrator(cfg)
        self.orch.current_topic = "test topic"
        self.orch.current_cycle = 3

    def test_engine_is_wired_with_the_configured_limits(self):
        self.assertEqual(self.orch.engine.max_queries, self.orch.config.queries_per_cycle)
        self.assertEqual(self.orch.engine.per_provider, self.orch.config.search_results_per_query)

    def test_dead_queries_from_telemetry_are_not_planned_again(self):
        for _ in range(2):
            self.orch.db.record_query_stat("test topic", "dead query text", "pubmed", results=0)
        self.assertTrue(self.orch._query_is_dead("dead query text"))
        self.assertFalse(self.orch._query_is_dead("a fresh query"))

    def test_dead_queries_with_kept_hits_stay_alive(self):
        for _ in range(2):
            self.orch.db.record_query_stat("test topic", "good query text", "pubmed", results=3)
        self.orch.db.record_query_kept("test topic", "good query text", "pubmed", 2)
        self.assertFalse(self.orch._query_is_dead("good query text"))


if __name__ == "__main__":
    unittest.main()
