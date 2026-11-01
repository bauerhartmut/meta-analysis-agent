"""Retrieval over research memory: vector search or a small ranking model.

Two paths, same interface:

* **Embeddings** - vector similarity over stored embeddings. Needs a local
  embedding model (Ollama), which the default deployment does not run.
* **Ranking by a small chat model** - keyword prefilter over the stored texts,
  then a weak model on the chat API orders the candidates. No local model, at
  the price of one cheap call per query.

The fallback is the default because the HRZ API offers chat only. A model that
is weak at reasoning is strong enough for "which of these 25 snippets is about
the query", and a failure of that call degrades to plain keyword order instead
of returning nothing.
"""

import json
import math
import logging
import re
from typing import List, Dict, Optional, Tuple

from ..database import Database
from ..llm.engine import LLMEngine
from ..models import Embedding, now_iso, gen_id

logger = logging.getLogger(__name__)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# Words that carry no retrieval signal in a research corpus.
_STOPWORDS = {
    "der", "die", "das", "und", "oder", "aber", "mit", "von", "für", "fur",
    "auf", "aus", "bei", "nach", "über", "uber", "unter", "zwischen", "ist",
    "sind", "war", "wird", "werden", "dass", "diese", "dieser", "dieses",
    "ein", "eine", "einer", "eines", "dem", "den", "des", "sich", "auch",
    "the", "and", "or", "but", "with", "from", "for", "that", "this",
    "these", "those", "are", "was", "were", "has", "have", "had", "not",
    "can", "may", "into", "than", "then", "which", "when", "how", "why",
}

_TOKEN_RE = re.compile(r"[a-zA-Z\u00c0-\u017f\u00df0-9]{3,}")


def _tokens(text: str) -> set:
    return {
        token for token in _TOKEN_RE.findall((text or "").lower())
        if token not in _STOPWORDS
    }


class SemanticRetrieval:
    """Retrieval over research memory (vector search or a ranking model)."""

    MAX_CANDIDATE_ROWS = 400
    MAX_TEXT_IN_PROMPT = 240

    def __init__(self, db: Database, llm: LLMEngine):
        self.db = db
        self.llm = llm
        config = getattr(llm, "config", None)
        self.embeddings_enabled = bool(
            getattr(config, "embeddings_enabled", False)
        )
        self.retrieval_model = getattr(config, "retrieval_model", "") or None
        try:
            self.candidates = max(5, int(getattr(config, "retrieval_candidates", 25)))
        except (TypeError, ValueError):
            self.candidates = 25

    async def index_entity(self, entity_type: str, entity_id: str, text: str):
        """Create/update an embedding for an entity."""
        if not self.embeddings_enabled:
            # Without embeddings the ranking model reads the live rows, so an
            # index would only cost a local model call and storage nobody reads.
            return
        if not text or len(text.strip()) < 10:
            return

        # Check if embedding already exists
        existing = self.db.get_embedding_for_entity(entity_type, entity_id)
        if existing:
            return  # Already indexed

        embedding = await self.llm.embed_single(text)
        if not embedding:
            return

        emb = Embedding(
            id=gen_id(),
            entity_type=entity_type,
            entity_id=entity_id,
            embedding=json.dumps(embedding),
            text=text[:500],
            date_added=now_iso(),
        )
        self.db.save_embedding(emb.to_dict())
        logger.debug(f"Indexed {entity_type}:{entity_id}")

    async def index_sources(self, sources: List[dict]):
        """Index source summaries + distilled claims for retrieval."""
        for source in sources:
            text = self._source_index_text(source)
            await self.index_entity("source", source["id"], text)

    @staticmethod
    def _source_index_text(source: dict) -> str:
        """Build the embedding text for a source. Includes the distilled
        key_claims/counter_claims (the directional surface of a source) in
        addition to title+summary, so embedding retrieval can find sources that
        take a position even when their summary is generic."""
        parts = [source.get("title", ""), source.get("summary", "")]
        for field in ("key_claims", "counter_claims"):
            raw = source.get(field, "")
            try:
                claims = json.loads(raw) if isinstance(raw, str) else (raw or [])
                if isinstance(claims, list):
                    parts.append(" ".join(str(c) for c in claims if str(c).strip()))
            except (json.JSONDecodeError, TypeError):
                pass
        return ". ".join(p for p in parts if p)

    async def index_facts(self, facts: List[dict]):
        """Index facts for retrieval."""
        for fact in facts:
            await self.index_entity("fact", fact["id"], fact.get("content", ""))

    async def index_hypotheses(self, hypotheses: List[dict]):
        """Index hypotheses for retrieval."""
        for hyp in hypotheses:
            await self.index_entity("hypothesis", hyp["id"], hyp.get("claim", ""))

    async def index_questions(self, questions: List[dict]):
        """Index research questions for retrieval."""
        for q in questions:
            await self.index_entity("question", q["id"], q.get("question", ""))

    async def retrieve(self, query: str, top_k: int = 10, entity_types: Optional[List[str]] = None) -> List[Dict]:
        """
        Retrieve most relevant memories for a query.
        
        Args:
            query: The search query
            top_k: Number of results to return
            entity_types: Filter by entity types (None = all)
            
        Returns:
            List of {entity_type, entity_id, text, score} dicts, sorted by relevance.
        """
        if self.embeddings_enabled:
            results = await self._retrieve_vectors(query, top_k, entity_types)
            if results:
                return results
        return await self._retrieve_via_llm(query, top_k, entity_types)

    async def _retrieve_vectors(
        self, query: str, top_k: int = 10, entity_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """Vector path: embed the query, rank the stored embeddings by cosine."""
        query_embedding = await self.llm.embed_single(query)
        if not query_embedding:
            logger.warning("Failed to generate query embedding")
            return []

        # Get all embeddings (or filtered)
        all_embeddings = self.db.get_all_embeddings()

        # Filter by entity type if specified
        if entity_types:
            all_embeddings = [e for e in all_embeddings if e.get("entity_type") in entity_types]

        # Compute similarities
        scored = []
        for emb_record in all_embeddings:
            try:
                emb_vector = json.loads(emb_record.get("embedding", "[]"))
                if not emb_vector:
                    continue
                score = cosine_similarity(query_embedding, emb_vector)
                scored.append({
                    "entity_type": emb_record["entity_type"],
                    "entity_id": emb_record["entity_id"],
                    "text": emb_record.get("text", ""),
                    "score": score,
                })
            except (json.JSONDecodeError, Exception):
                continue

        # Sort by score descending
        scored.sort(key=lambda x: x["score"], reverse=True)

        return scored[:top_k]

    # === Model-based ranking (no local embeddings) ===

    def _live_rows(self, entity_types: Optional[List[str]]) -> List[Dict]:
        """Candidate rows from the database with their retrievable text."""
        types = entity_types or ["source", "fact", "hypothesis", "question"]
        rows: List[Dict] = []
        for entity_type in types:
            if entity_type == "source":
                for row in self.db._get_all(
                    "sources", order="date_added DESC", limit=self.MAX_CANDIDATE_ROWS
                ):
                    text = self._source_index_text(row) or (row.get("title") or "")
                    rows.append({"entity_type": "source", "entity_id": row["id"],
                                 "text": text})
            elif entity_type == "fact":
                for row in self.db._get_all(
                    "facts", order="date_added DESC", limit=self.MAX_CANDIDATE_ROWS
                ):
                    rows.append({"entity_type": "fact", "entity_id": row["id"],
                                 "text": row.get("content") or ""})
            elif entity_type == "hypothesis":
                for row in self.db._get_all(
                    "hypotheses", order="date_added DESC", limit=self.MAX_CANDIDATE_ROWS
                ):
                    rows.append({"entity_type": "hypothesis", "entity_id": row["id"],
                                 "text": row.get("claim") or ""})
            elif entity_type == "question":
                for row in self.db._get_all(
                    "research_questions", order="date_added DESC",
                    limit=self.MAX_CANDIDATE_ROWS,
                ):
                    rows.append({"entity_type": "question", "entity_id": row["id"],
                                 "text": row.get("question") or ""})
        return [row for row in rows if (row["text"] or "").strip()]

    @staticmethod
    def keyword_scores(query: str, rows: List[Dict]) -> List[Tuple[float, dict]]:
        """Cheap lexical prefilter: shared distinctive tokens over query length."""
        query_tokens = _tokens(query)
        if not query_tokens:
            return [(0.0, row) for row in rows]
        scored = []
        for row in rows:
            overlap = len(query_tokens & _tokens(row["text"]))
            scored.append((overlap / len(query_tokens), row))
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored

    async def _retrieve_via_llm(
        self, query: str, top_k: int = 10, entity_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """Keyword prefilter, then a weak chat model orders the candidates."""
        rows = self._live_rows(entity_types)
        if not rows:
            return []
        ranked = self.keyword_scores(query, rows)
        candidates = [row for _, row in ranked[: self.candidates]]
        keyword_order = [
            {"entity_type": row["entity_type"], "entity_id": row["entity_id"],
             "text": row["text"][:500], "score": round(score, 3)}
            for score, row in ranked[:top_k]
        ]

        listing = "\n".join(
            f"{i}. [{row['entity_type']}] "
            f"{(row['text'] or '')[: self.MAX_TEXT_IN_PROMPT].replace(chr(10), ' ')}"
            for i, row in enumerate(candidates, start=1)
        )
        messages = [
            {
                "role": "system",
                "content": (
                    "You rank research memory by relevance to a query.\n"
                    "Return JSON: {\"scores\": [{\"index\": 1, \"score\": 0.8}]} "
                    "for the candidates that genuinely help answer the query, "
                    "best first. Omit the rest. Score 0..1. No prose."
                ),
            },
            {"role": "user", "content": f"QUERY: {query}\n\nCANDIDATES:\n{listing}"},
        ]
        try:
            reply = await self.llm.chat_json(
                messages, model=self.retrieval_model, temperature=0.0, max_tokens=700
            )
        except Exception as exc:  # noqa: BLE001 - ranking must never break a cycle
            logger.warning(f"Retrieval ranking unavailable: {exc}")
            reply = None

        votes = reply.get("scores") if isinstance(reply, dict) else reply
        results = []
        for vote in votes or []:
            if not isinstance(vote, dict):
                continue
            try:
                index = int(vote.get("index"))
                score = float(vote.get("score", 0.5))
            except (TypeError, ValueError):
                continue
            if not (1 <= index <= len(candidates)):
                continue
            row = candidates[index - 1]
            results.append({
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "text": row["text"][:500],
                "score": round(min(1.0, max(0.0, score)), 3),
            })
        results.sort(key=lambda item: item["score"], reverse=True)
        if not results:
            if votes:
                logger.debug("Retrieval ranking returned no usable index; using keywords")
            return keyword_order
        return results[:top_k]

    async def find_similar(self, text: str, entity_type: str = "", top_k: int = 5) -> List[Dict]:
        """Find similar entities to given text."""
        entity_types = [entity_type] if entity_type else None
        return await self.retrieve(text, top_k=top_k, entity_types=entity_types)

    async def find_hypothesis_sources(
        self, claim: str, top_k: int = 8, min_score: float = 0.3,
        extra_query: str = "",
    ) -> List[Dict]:
        """
        Return the source candidates that are semantically closest to a hypothesis
        claim (Embedding-RAG pre-selection).

        Replaces brute-force (hypothesis x all sources) pairing: only genuinely
        nearby sources are returned, so the LLM-classification budget is spent on
        pairs that are actually likely to yield supports/contradicts.

        Args:
            claim: The hypothesis claim text.
            top_k: Max candidate sources to retrieve.
            min_score: Minimum cosine similarity to keep a candidate.
            extra_query: Optional additional text folded into the query embedding
                (e.g. the hypothesis's predictions/falsification conditions) so
                the retrieval is anchored on the specific testable claims rather
                than only the generic claim wording.

        Returns:
            List of {source_id, title, score} sorted by descending score.
        """
        query = (claim + " " + extra_query).strip() if extra_query else claim
        results = await self.retrieve(query, top_k=top_k, entity_types=["source"])
        candidates = []
        for r in results:
            if r["score"] < min_score:
                continue
            sid = r["entity_id"]
            source = self.db.get_source(sid)
            if not source or not sid:
                continue
            candidates.append({
                "source_id": sid,
                "title": source.get("title", ""),
                "score": r["score"],
            })
        return candidates

    async def find_relevant_context(self, question: str, topic: str = "") -> Dict:
        """
        Build a comprehensive context from memory for a research question.
        Returns structured context with sources, facts, hypotheses, etc.
        """
        # Retrieve across all entity types
        results = await self.retrieve(question, top_k=20)

        context = {
            "relevant_sources": [],
            "relevant_facts": [],
            "relevant_hypotheses": [],
            "relevant_questions": [],
        }

        for r in results:
            etype = r["entity_type"]
            eid = r["entity_id"]
            text = r["text"]
            score = r["score"]

            if score < 0.3:  # Minimum relevance threshold
                continue

            if etype == "source":
                source = self.db.get_source(eid)
                if source:
                    context["relevant_sources"].append({
                        "id": eid,
                        "title": source.get("title", ""),
                        "summary": source.get("summary", ""),
                        "relevance_score": score,
                    })
            elif etype == "fact":
                fact = self.db._get("facts", eid)
                if fact:
                    context["relevant_facts"].append({
                        "id": eid,
                        "content": fact.get("content", ""),
                        "confidence": fact.get("confidence", 0.5),
                        "relevance_score": score,
                    })
            elif etype == "hypothesis":
                hyp = self.db.get_hypothesis(eid)
                if hyp:
                    context["relevant_hypotheses"].append({
                        "id": eid,
                        "claim": hyp.get("claim", ""),
                        "status": hyp.get("status", ""),
                        "confidence": hyp.get("confidence", 0.0),
                        "relevance_score": score,
                    })
            elif etype == "question":
                q = self.db.get_question(eid)
                if q:
                    context["relevant_questions"].append({
                        "id": eid,
                        "question": q.get("question", ""),
                        "status": q.get("status", ""),
                        "relevance_score": score,
                    })

        return context

    async def check_already_researched(self, question: str) -> bool:
        """Check if a similar question has already been researched."""
        results = await self.retrieve(question, top_k=3, entity_types=["question"])
        for r in results:
            if r["score"] > 0.85:  # Very high similarity threshold
                return True
        return False

    def get_index_stats(self) -> dict:
        """Get embedding index statistics."""
        all_embs = self.db.get_all_embeddings()
        types = {}
        for e in all_embs:
            t = e.get("entity_type", "unknown")
            types[t] = types.get(t, 0) + 1
        return {
            "total_embeddings": len(all_embs),
            "by_type": types,
        }
