"""Tests for the embedding-free retrieval path (memory/retrieval.py).

The default deployment runs no local model, so retrieval must work through the
chat API alone. These tests pin down what that path promises:

* the query is never embedded when embeddings are disabled,
* the ranking model's order is used, with scores clamped to 0..1,
* a failing or nonsensical ranking degrades to keyword order instead of
  returning nothing, because an empty result silently stops the evidence work,
* entity-type filters are honoured.
"""

import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.memory.retrieval import SemanticRetrieval
from research_agent.models import gen_id, now_iso


class _Config:
    def __init__(self, embeddings_enabled=False, retrieval_model="gwdg/tiny"):
        self.embeddings_enabled = embeddings_enabled
        self.retrieval_model = retrieval_model
        self.retrieval_candidates = 25


class _FakeLLM:
    def __init__(self, reply=None, raise_on_rank=False, config=None):
        self.config = config or _Config()
        self.reply = reply
        self.raise_on_rank = raise_on_rank
        self.rank_calls = 0
        self.embed_calls = 0

    async def chat_json(self, messages, model=None, temperature=0.0, max_tokens=700):
        self.rank_calls += 1
        if self.raise_on_rank:
            raise RuntimeError("backend down")
        return self.reply

    async def embed_single(self, text, model=None):
        self.embed_calls += 1
        return []


def _db():
    db = Database(":memory:")
    rows = [
        ("Politische Selektion und Intelligenz", "Erörtert, warum Intelligenz sinkt."),
        ("Schlafentzug und Fehlerrate", "Müdigkeit erhöht Fehler bei Aufmerksamkeitstests."),
        ("Preisgestaltung im Einzelhandel", "Rabatte und Margen im Handel."),
    ]
    for title, summary in rows:
        db.save_source({
            "id": gen_id(),
            "title": title,
            "url": f"https://example.org/{gen_id()}",
            "summary": summary,
            "content": summary,
            "date_added": now_iso(),
        })
    db.save_fact({
        "id": gen_id(),
        "content": "Schlafentzug von 24 Stunden senkt die Reaktionszeit um 30 Prozent.",
        "confidence": 0.7,
        "source_ids": "[]",
        "date_added": now_iso(),
    })
    return db


class TestModelBasedRetrieval(unittest.TestCase):
    def test_ranking_model_order_is_used_and_scores_are_clamped(self):
        llm = _FakeLLM(reply={"scores": [{"index": 3, "score": 1.4}, {"index": 1, "score": 0.2}]})
        query = "Schlafentzug Fehlerrate"
        retrieval = SemanticRetrieval(_db(), llm)
        # Candidate order after the keyword prefilter, which the model then reorders.
        pool = [
            row["text"]
            for _, row in retrieval.keyword_scores(query, retrieval._live_rows(["source"]))
        ]
        out = asyncio.run(retrieval.retrieve(query, top_k=3, entity_types=["source"]))
        self.assertEqual(llm.embed_calls, 0, "no local embedding model may run")
        self.assertEqual(llm.rank_calls, 1)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["score"], 1.0)
        self.assertEqual(out[1]["score"], 0.2)
        self.assertEqual(out[0]["text"][:40], pool[2][:40], "model's order wins")
        self.assertEqual(out[1]["text"][:40], pool[0][:40])

    def test_failing_ranking_model_falls_back_to_keywords(self):
        llm = _FakeLLM(raise_on_rank=True)
        out = asyncio.run(SemanticRetrieval(_db(), llm).retrieve(
            "Schlafentzug Fehlerrate", top_k=3, entity_types=["source"]
        ))
        self.assertTrue(out, "keyword fallback must still return candidates")
        self.assertIn("Schlafentzug", out[0]["text"])

    def test_unusable_ranking_answer_falls_back_to_keywords(self):
        llm = _FakeLLM(reply={"scores": [{"index": 99, "score": 0.9}, "nonsense"]})
        out = asyncio.run(SemanticRetrieval(_db(), llm).retrieve(
            "Intelligenz Selektion", top_k=2, entity_types=["source"]
        ))
        self.assertTrue(out)
        self.assertIn("Selektion", out[0]["text"])

    def test_entity_type_filter_is_respected(self):
        llm = _FakeLLM(reply=None)
        out = asyncio.run(SemanticRetrieval(_db(), llm).retrieve(
            "Schlafentzug", top_k=10, entity_types=["fact"]
        ))
        self.assertEqual([r["entity_type"] for r in out], ["fact"])

    def test_indexing_is_skipped_without_embeddings(self):
        db = _db()
        llm = _FakeLLM()
        retrieval = SemanticRetrieval(db, llm)
        asyncio.run(retrieval.index_entity("source", "abc", "a long enough text to index"))
        self.assertEqual(llm.embed_calls, 0)
        self.assertEqual(db.get_all_embeddings(), [])

    def test_keyword_scores_rank_the_matching_row_first(self):
        db = _db()
        rows = SemanticRetrieval(db, _FakeLLM())._live_rows(["source"])
        ranked = SemanticRetrieval.keyword_scores("Schlafentzug Fehlerrate", rows)
        self.assertIn("Schlafentzug", ranked[0][1]["text"])


if __name__ == "__main__":
    unittest.main()
