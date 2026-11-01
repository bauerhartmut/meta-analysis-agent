"""
Source Manager - Handles source storage, deduplication, and credibility evaluation.
"""

import json
import logging
from typing import Optional, List, Dict

from ..database import Database
from ..models import Source, now_iso, gen_id
from ..llm.engine import LLMEngine

logger = logging.getLogger(__name__)


# Titles that identify a withdrawn publication. Deliberately narrow: "retraction"
# only as a prefix label, so a paper *about* retractions is not caught.
_RETRACTION_MARKERS = (
    "retracted:", "retraction:", "[retracted]", "retracted article",
    "retract and replace", "this article has been retracted",
)


def is_retracted_work(title: str = "", extra: str = "") -> bool:
    """True for a publication that has been retracted.

    One run's corpus contained "RETRACTED: Causal role of immune cells …" with no
    marker anywhere in the database or the log: it counted as an ordinary source
    and was available as evidence. A withdrawn paper is not evidence for anything,
    and a report that cannot say so is overstating its corpus.
    """
    haystack = f"{title or ''} {extra or ''}".lower()
    return any(marker in haystack for marker in _RETRACTION_MARKERS)


class SourceManager:
    """Manages research sources: storage, dedup, evaluation."""

    def __init__(self, db: Database, llm: LLMEngine):
        self.db = db
        self.llm = llm

    async def process_search_result(self, result: dict, extraction: Optional[dict] = None) -> Optional[Source]:
        """
        Process a search result into a stored source.
        Checks for duplicates by URL and content hash.
        Returns the Source if newly stored, None if duplicate.
        """
        url = result.get("url", "")
        if not url:
            return None

        # Check duplicate by URL
        existing = self.db.get_source_by_url(url)
        if existing:
            logger.debug(f"Duplicate source (URL): {url}")
            return None

        content = extraction.get("content", "") if extraction else ""
        content_hash = extraction.get("content_hash", "") if extraction else ""

        # Check duplicate by content hash
        if content_hash:
            existing_hash = self.db.get_source_by_hash(content_hash)
            if existing_hash:
                logger.debug(f"Duplicate source (hash): {url}")
                return None

        # Build source
        title = result.get("title", "")
        retracted = is_retracted_work(title, result.get("snippet", ""))
        if retracted:
            logger.warning(
                f"Retracted work stored (kept out of evidence): {title[:70]}"
            )

        # DOI from the URL when the provider does not pass one explicitly. Stored
        # once, so the forest table and the same-cohort check do not have to parse
        # URLs at read time (and different providers' URLs differ).
        from .extractor import ContentExtractor
        doi = str(result.get("doi") or "").strip()
        if not doi:
            doi = ContentExtractor.doi_from_url(url)

        source = Source(
            id=gen_id(),
            title=title,
            doi=doi,
            # Whatever the provider could parse. Hard-coding these to "" is why
            # 0 of 83 sources in one run had an author or a year, and why every
            # BibTeX key collapsed to the same anonymous placeholder.
            author=str(result.get("author", "") or "").strip(),
            publication_date=str(result.get("year", "") or "").strip(),
            url=url,
            source_type=result.get("source_type", "web"),
            content_hash=content_hash,
            # A retracted paper keeps a credibility floor of its own: the source
            # row stays (the corpus has to show it was found), but nothing may
            # treat it as support.
            credibility=0.0 if retracted else 0.5,
            relevance=0.0,
            summary=result.get("snippet", ""),
            key_claims="[]",
            counter_claims="[]",
            date_added=now_iso(),
            content=content[:5000],
            raw_text=content,
        )

        self.db.save_source(source.to_dict())
        logger.info(f"New source stored: {source.title[:60]} ({source.id})")
        return source

    async def evaluate_source(self, source: Source, research_question: str) -> dict:
        """
        Use LLM to evaluate source credibility and extract claims.
        """
        if not source.raw_text and not source.summary:
            return {"credibility": 0.3, "claims": [], "summary": source.summary}

        content_preview = (source.raw_text or source.summary)[:3000]

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a critical academic source evaluator. "
                    "Analyze the given source and return JSON with:\n"
                    "- credibility: float 0.0-1.0 (1.0 = peer-reviewed journal, 0.1 = random blog)\n"
                    "- summary: 2-3 sentence summary\n"
                    "- key_claims: list of main factual claims made\n"
                    "- counter_claims: list of claims that contradict common understanding\n"
                    "- source_type: one of academic_journal, preprint, textbook, news, blog, unknown\n"
                    "Return ONLY valid JSON."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Research question: {research_question}\n\n"
                    f"Source title: {source.title}\n"
                    f"Source URL: {source.url}\n\n"
                    f"Content:\n{content_preview}"
                ),
            },
        ]

        result = await self.llm.chat_json(messages, temperature=0.2, max_tokens=1024)

        if result:
            # Update source with evaluation (+ mark as evaluated so it is not
            # re-evaluated on every cycle)
            source.credibility = float(result.get("credibility", 0.5))
            source.summary = result.get("summary", source.summary)
            source.key_claims = json.dumps(result.get("key_claims", []))
            source.counter_claims = json.dumps(result.get("counter_claims", []))
            source.evaluated = 1
            self.db.save_source(source.to_dict())

            return result

        return {"credibility": 0.4, "claims": [], "summary": source.summary}

    def get_recent_sources(self, limit: int = 20) -> List[dict]:
        """Get recently added sources."""
        return self.db.get_all_sources(limit=limit)

    def get_source_count(self) -> int:
        return self.db.count_sources()
