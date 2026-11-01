"""
End-to-End Integration Test for the Research Agent.
Tests the full pipeline: Topic -> Question -> Search -> Source ->
Extraction -> Memory -> Hypothesis -> Critic -> Updated Hypothesis -> Next Question
"""

import sys
import asyncio
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.config import Config
from research_agent.database import Database
from research_agent.llm.engine import LLMEngine
from research_agent.research.search import SearchManager
from research_agent.research.extractor import ContentExtractor
from research_agent.research.sources import SourceManager
from research_agent.memory.store import MemoryStore
from research_agent.memory.retrieval import SemanticRetrieval
from research_agent.agents.roles import (
    ResearcherAgent, AnalystAgent, CriticAgent,
    PlannerAgent, SynthesizerAgent,
)


class TestEndToEnd(unittest.TestCase):
    """Full pipeline integration test."""

    def setUp(self):
        self.db = Database(":memory:")
        self.llm = LLMEngine()
        self.search = SearchManager()
        self.extractor = ContentExtractor()
        self.source_manager = SourceManager(self.db, self.llm)
        self.memory = MemoryStore(self.db, self.llm)
        self.retrieval = SemanticRetrieval(self.db, self.llm)
        self.researcher = ResearcherAgent(self.llm)
        self.analyst = AnalystAgent(self.llm)
        self.critic = CriticAgent(self.llm)
        self.planner = PlannerAgent(self.llm)
        self.synthesizer = SynthesizerAgent(self.llm)

    async def _cleanup(self):
        await self.llm.close()
        await self.extractor.close()

    def test_full_pipeline(self):
        """Test the complete research pipeline."""
        async def _run():
            topic = "quantum consciousness"
            results_summary = {}

            # Step 1: Generate research questions
            print("\n  [1/10] Generating research questions...")
            questions = await self.planner.generate_research_questions(
                topic,
                {"total_sources": 0, "total_cycles": 0, "open_questions": 0},
                {},
            )
            self.assertIsInstance(questions, list)
            self.assertGreater(len(questions), 0)
            results_summary["questions"] = len(questions)
            print(f"    -> Generated {len(questions)} research questions")

            # Step 2: Select best question
            print("  [2/10] Selecting best question...")
            for q in questions:
                q["priority_score"] = 0.5
            selected = await self.planner.select_next_question(questions, {})
            self.assertIsNotNone(selected)
            question = selected.get("question", "") or questions[0].get("question", topic)
            print(f"    -> Selected: {question[:80]}...")

            # Step 3: Plan searches
            print("  [3/10] Planning searches...")
            search_plans = await self.researcher.plan_searches(question, {})
            self.assertIsInstance(search_plans, list)
            self.assertGreater(len(search_plans), 0)
            print(f"    -> Planned {len(search_plans)} searches")

            # Step 4: Execute search
            print("  [4/10] Executing web search...")
            all_results = []
            for plan in search_plans[:2]:
                query = plan.get("query", question)
                results = await self.search.search(query, max_results_per_provider=3)
                all_results.extend(results)
            results_summary["search_results"] = len(all_results)
            print(f"    -> Found {len(all_results)} search results")

            if not all_results:
                print("    -> No search results found, skipping extraction")
                await self._cleanup()
                return results_summary

            # Step 5: Extract content
            print("  [5/10] Extracting content...")
            processed_sources = []
            for result in all_results[:3]:
                extraction = await self.extractor.extract(result.url)
                if extraction and extraction.get("success"):
                    source = await self.source_manager.process_search_result(
                        result.to_dict(), extraction
                    )
                    if source:
                        processed_sources.append(source)
                        await self.retrieval.index_entity("source", source.id, f"{source.title}. {source.summary}")
            results_summary["sources"] = len(processed_sources)
            print(f"    -> Processed {len(processed_sources)} sources")

            # Step 6: Analyze sources
            print("  [6/10] Analyzing sources...")
            findings = []
            for source in processed_sources[:2]:
                analysis = await self.researcher.analyze_source(
                    source.title,
                    source.raw_text or source.content or source.summary,
                    question,
                )
                if analysis:
                    findings.append({"source_id": source.id, "title": source.title, **analysis})
            results_summary["findings"] = len(findings)
            print(f"    -> Analyzed {len(findings)} sources")

            # Step 7: Extract facts
            print("  [7/10] Extracting facts...")
            facts = []
            if processed_sources:
                text = "\n\n".join(
                    s.raw_text or s.content or s.summary for s in processed_sources[:2]
                )
                facts = await self.memory.extract_facts(
                    text, processed_sources[0].id, topic
                )
                await self.retrieval.index_facts([{"id": f.id, "content": f.content} for f in facts])
            results_summary["facts"] = len(facts)
            print(f"    -> Extracted {len(facts)} facts")

            # Step 8: Generate hypotheses
            print("  [8/10] Generating hypotheses...")
            hypotheses = await self.memory.generate_hypotheses(
                [f.to_dict() for f in facts], [], topic, question
            )
            results_summary["hypotheses"] = len(hypotheses)
            print(f"    -> Generated {len(hypotheses)} hypotheses")

            # Step 9: Critic analysis
            print("  [9/10] Running critic analysis...")
            if hypotheses:
                critique = await self.critic.critique_conclusion(
                    hypotheses[0].claim,
                    [{"title": s.title, "summary": s.summary} for s in processed_sources],
                )
                self.assertIsInstance(critique, dict)
                results_summary["critique"] = "completed"
                print(f"    -> Critique completed, weaknesses found: {len(critique.get('weaknesses', []))}")

                # Step 9b: Update hypothesis based on evidence
                if processed_sources:
                    evidence = await self.memory.evaluate_evidence(
                        processed_sources[0].raw_text or processed_sources[0].summary,
                        hypotheses[0].to_dict(),
                        processed_sources[0].id,
                    )
                    if evidence:
                        await self.memory.update_hypothesis(hypotheses[0].id, [evidence.to_dict()])
                        results_summary["evidence"] = "collected"
                        print(f"    -> Evidence collected: {evidence.evidence_type}")

            # Step 10: Synthesize
            print("  [10/10] Synthesizing findings...")
            synthesis = await self.synthesizer.synthesize_research(
                question,
                {"findings": findings[:5], "sources_count": len(processed_sources)},
                [h.to_dict() for h in hypotheses],
                [],
            )
            self.assertIsInstance(synthesis, dict)
            results_summary["synthesis"] = "completed"
            print(f"    -> Synthesis completed: {synthesis.get('confidence_level', 'unknown')} confidence")

            # Verify database state
            print("\n  Database state:")
            stats = self.db.get_stats()
            for k, v in stats.items():
                print(f"    {k}: {v}")

            await self._cleanup()
            return results_summary

        results = asyncio.run(_run())

        print("\n  === E2E Test Results ===")
        for k, v in results.items():
            print(f"    {k}: {v}")

        # Assertions
        self.assertIn("questions", results)
        self.assertIn("search_results", results)
        self.assertGreater(results.get("questions", 0), 0)


class TestDashboardAPI(unittest.TestCase):
    """Test dashboard API endpoints."""

    def test_health_endpoint(self):
        """Health check returns OK."""
        async def _test():
            import aiohttp
            from research_agent.config import get_config
            config = get_config()

            from research_agent.dashboard.server import DashboardServer
            dashboard = DashboardServer(config.dashboard_host, config.dashboard_port + 100)
            dashboard.start()

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"http://localhost:{config.dashboard_port + 100}/api/health") as resp:
                        data = await resp.json()
                        return data
            finally:
                dashboard.stop()

        result = asyncio.run(_test())
        self.assertEqual(result.get("status"), "ok")
        print("  Dashboard health check: OK")


if __name__ == "__main__":
    unittest.main(verbosity=2)
