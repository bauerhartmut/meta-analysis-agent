"""Tests for citation snowballing (OpenAlex references/citations).

The HTTP layer is faked; everything else is the real code path.
"""

import asyncio
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.config import Config
from research_agent.orchestrator import ResearchOrchestrator
from research_agent.research.search import SearchManager, SearchResult, RATE_LIMIT_MEMORY
from research_agent.models import gen_id, now_iso


class _Resp:
    def __init__(self, status, payload):
        self.status = status
        self._payload = payload

    async def json(self):
        return self._payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _Session:
    def __init__(self, router):
        self.router = router

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def get(self, url, params=None):
        return _Resp(200, self.router(url, params or {}))


def _patch_session(router):
    return mock.patch(
        "research_agent.research.search.aiohttp.ClientSession",
        lambda *a, **k: _Session(router),
    )


class _StatusSession:
    """Like _Session, but the router decides the HTTP status too."""

    def __init__(self, router):
        self.router = router

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def get(self, url, params=None):
        status, payload = self.router(url, params or {})
        return _Resp(status, payload)


def _patch_status_session(router):
    return mock.patch(
        "research_agent.research.search.aiohttp.ClientSession",
        lambda *a, **k: _StatusSession(router),
    )


def _work(title, doi, abstract_words):
    inverted = {w: [i] for i, w in enumerate(abstract_words)}
    return {
        "title": title,
        "doi": doi,
        "publication_year": 2021,
        "abstract_inverted_index": inverted,
        "id": f"https://openalex.org/{title[:4]}",
    }


def _router(url, params):
    if "/works/doi:" in url or url.rstrip("/").endswith("/W100"):
        return {"id": "https://openalex.org/W100", "referenced_works": ["https://openalex.org/W200"],
                "cited_by_count": 40}
    if str(params.get("filter", "")).startswith("openalex_id:"):
        return {"results": [_work("Reference paper", "https://doi.org/10.1234/ref",
                                  ["Heritability", "of", "IQ", "rises"])]}
    if str(params.get("filter", "")).startswith("cites:"):
        return {"results": [_work("Citing paper", "https://doi.org/10.1234/cite",
                                  ["Polygenic", "scores", "predict"])]}
    return {"results": []}


class TestCitationNeighbors(unittest.TestCase):
    def test_doi_extraction(self):
        self.assertEqual(
            SearchManager.doi_from_url("https://doi.org/10.1038/s41586-022-1"),
            "10.1038/s41586-022-1",
        )
        self.assertEqual(SearchManager.doi_from_url("https://example.org/no-doi"), "")

    def test_references_and_citations_are_returned(self):
        with _patch_session(_router):
            results = asyncio.run(
                self.sm.citation_neighbors("https://doi.org/10.1234/seed", limit=6)
            )
        titles = {r.title for r in results}
        self.assertEqual(titles, {"Reference paper", "Citing paper"})
        ref = next(r for r in results if r.title == "Reference paper")
        self.assertEqual(ref.url, "https://doi.org/10.1234/ref")
        self.assertIn("Heritability of IQ rises", ref.snippet)

    def test_pubmed_and_europepmc_urls_map_to_id_space_refs(self):
        self.assertEqual(
            SearchManager.openalex_work_ref("https://pubmed.ncbi.nlm.nih.gov/32943535/"),
            "pmid:32943535",
        )
        self.assertEqual(
            SearchManager.openalex_work_ref("https://europepmc.org/article/MED/42813041"),
            "pmid:42813041",
        )
        self.assertEqual(
            SearchManager.openalex_work_ref("europepmc PMC13637646"),
            "pmcid:PMC13637646",
        )
        self.assertEqual(SearchManager.openalex_work_ref("https://example.org/x"), "")

    def test_openalex_work_url_is_used_directly(self):
        with _patch_session(_router):
            results = asyncio.run(
                self.sm.citation_neighbors("https://openalex.org/W100", limit=4)
            )
        self.assertTrue(results, "the stored OpenAlex work URL must work like a DOI")
        self.assertEqual(SearchManager.openalex_id_from_url("https://openalex.org/W100"), "W100")

    def test_source_without_doi_makes_no_call(self):
        with mock.patch(
            "research_agent.research.search.aiohttp.ClientSession",
            side_effect=AssertionError("must not call the API without a DOI"),
        ):
            self.assertEqual(
                asyncio.run(self.sm.citation_neighbors("https://example.org/plain")), []
            )

    def test_off_domain_neighbour_is_filtered(self):
        def router(url, params):
            if "/works/doi:" in url:
                return {"id": "https://openalex.org/W100",
                        "referenced_works": ["https://openalex.org/W200"]}
            if str(params.get("filter", "")).startswith("openalex_id:"):
                return {"results": [
                    _work("Quantum field theory of Wilson loops", "https://doi.org/10.1234/q",
                          ["gauge", "theory"]),
                ]}
            return {"results": []}

        with _patch_session(router):
            results = asyncio.run(
                self.sm.citation_neighbors("https://doi.org/10.1234/seed", limit=4)
            )
        self.assertEqual(results, [])

    def setUp(self):
        self.sm = SearchManager()
        # The cooldown memory is process-global; a 429 in one test must not
        # silence the provider in the next one.
        RATE_LIMIT_MEMORY._blocked_until.clear()

    def test_openalex_rate_limit_falls_back_to_semantic_scholar(self):
        """One provider's quota must not stop citation work for hours."""
        def router(url, params):
            if "api.openalex.org" in url:
                return 429, {}
            if "/references" in url:
                return 200, {"data": [{"citedPaper": {
                    "title": "Semantic reference", "abstract": "Heritability of IQ rises",
                    "year": 2019, "externalIds": {"DOI": "10.1234/s2ref"},
                    "url": "https://www.semanticscholar.org/paper/x",
                }}]}
            return 200, {"data": []}

        with _patch_status_session(router):
            results = asyncio.run(
                self.sm.citation_neighbors("https://doi.org/10.1234/seed", limit=6)
            )

        self.assertEqual([r.title for r in results], ["Semantic reference"])
        self.assertEqual(results[0].url, "https://doi.org/10.1234/s2ref")
        self.assertEqual(self.sm.last_citation_status, "ok")

    def test_both_indexes_rate_limited_stays_temporary(self):
        def router(url, params):
            return 429, {}

        with _patch_status_session(router):
            results = asyncio.run(
                self.sm.citation_neighbors("https://doi.org/10.1234/seed", limit=6)
            )

        self.assertEqual(results, [])
        self.assertEqual(self.sm.last_citation_status, "rate_limited")

    def test_second_index_answer_closes_the_item(self):
        """If one index answered completely, "no neighbours" is a result."""
        def router(url, params):
            if "api.openalex.org" in url:
                return 200, {"id": "https://openalex.org/W100", "referenced_works": []}
            return 200, {"data": []}

        with _patch_status_session(router):
            results = asyncio.run(
                self.sm.citation_neighbors("https://doi.org/10.1234/seed", limit=6)
            )

        self.assertEqual(results, [])
        self.assertEqual(self.sm.last_citation_status, "ok")

    def test_crossref_references_are_the_third_route(self):
        """Both other indexes over quota: Crossref still lists the references."""
        def router(url, params):
            if "api.openalex.org" in url or "api.semanticscholar.org" in url:
                return 429, {}
            return 200, {"message": {"reference": [
                {"DOI": "10.1234/cr1", "article-title": "Genetic correlation methods",
                 "year": "2020"},
                {"unstructured": "No DOI, so it cannot be resolved"},
                {"DOI": "10.1234/cr2",
                 "unstructured": "Doe, A. (2018). Polygenic scores and health."},
            ]}}

        with _patch_status_session(router):
            results = asyncio.run(
                self.sm.citation_neighbors("https://doi.org/10.1234/seed", limit=6)
            )

        self.assertEqual(self.sm.last_citation_status, "ok")
        self.assertEqual(
            {r.url for r in results},
            {"https://doi.org/10.1234/cr1", "https://doi.org/10.1234/cr2"},
        )
        self.assertIn("Genetic correlation methods", [r.title for r in results])

    def test_api_error_is_not_raised(self):
        def boom(url, params):
            raise RuntimeError("network down")

        with _patch_session(boom):
            self.assertEqual(
                asyncio.run(self.sm.citation_neighbors("https://doi.org/10.1234/x")), []
            )


class TestCitationWorkItem(unittest.TestCase):
    def setUp(self):
        cfg = Config()
        cfg.database_url = ":memory:"
        cfg.llm_failure_threshold = 0
        cfg.work_items_per_cycle = 2
        self.orch = ResearchOrchestrator(cfg)
        self.orch.current_topic = "test topic"
        self.orch.work_queue.set_topic("test topic")
        self.sid = gen_id()
        self.orch.db.save_source({
            "id": self.sid, "title": "Seed paper",
            "url": "https://doi.org/10.1234/seed", "content": "x" * 800,
            "relevance": 0.8, "relevance_scored": 1, "credibility": 0.7,
            "date_added": now_iso(),
        })
        self.orch.work_queue.seed()

    def test_handler_stores_candidates(self):
        class FakeSearch:
            async def citation_neighbors(self, url, limit=10):
                return [SearchResult(title="Neighbour", url="https://doi.org/10.1234/n",
                                     snippet="Heritability of IQ rises with age.", source_type="openalex")]

        self.orch.search = FakeSearch()
        sources = asyncio.run(self.orch._work_on_backlog(1))

        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].title, "Neighbour")
        self.assertIsNotNone(self.orch.db.get_source_by_url("https://doi.org/10.1234/n"))
        item = self.orch.db._get_all("work_items", where="kind = ?", params=("citation",))[0]
        self.assertEqual(item["status"], "done")

    def test_rate_limit_defers_instead_of_failing(self):
        class FakeSearch:
            last_citation_status = "rate_limited"

            async def citation_neighbors(self, url, limit=10):
                return []

        self.orch.search = FakeSearch()
        before = self.orch.db._get_all("work_items", where="kind = ?", params=("citation",))[0]
        asyncio.run(self.orch._work_on_backlog(1))

        item = self.orch.db._get("work_items", before["id"])
        self.assertEqual(item["status"], "open")
        self.assertEqual(item["attempts"], 0, "a rate limit must not burn a retry")
        self.assertIn("rate_limited", item["note"])

    def test_second_run_finds_nothing_new_and_releases(self):
        class FakeSearch:
            async def citation_neighbors(self, url, limit=10):
                return [SearchResult(title="Neighbour", url="https://doi.org/10.1234/n",
                                     snippet="Text", source_type="openalex")]

        self.orch.search = FakeSearch()
        asyncio.run(self.orch._work_on_backlog(1))
        # Re-seed the item as if it were new work, then run again.
        self.orch.db._update("work_items",
                             self.orch.db._get_all("work_items")[0]["id"],
                             {"status": "open", "attempts": 0})
        self.assertEqual(asyncio.run(self.orch._work_on_backlog(2)), [])
        item = self.orch.db._get_all("work_items")[0]
        self.assertEqual(item["status"], "open")


if __name__ == "__main__":
    unittest.main()
