"""Review frame: a frozen protocol and recorded screening decisions.

Without a protocol written *before* the pooling, "I included 12 studies" is a
choice made after seeing the numbers. Without recorded exclusion reasons a
PRISMA-style count is decoration. Both are cheap: one file and one table.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

from ..models import gen_id, now_iso
from .pooling import aggregate_design, standardize

logger = logging.getLogger(__name__)

PROTOCOL_DIR = "data/reviews"

DECISION_INCLUDE = "include"
DECISION_EXCLUDE = "exclude"


def protocol_path(db, topic: str) -> Path:
    """Where this topic's protocol lives (next to the database)."""
    from ..config import topic_slug

    base = Path(db.db_path).parent if getattr(db, "db_path", "") else Path("data")
    return base.parent / PROTOCOL_DIR / topic_slug(topic) / "protocol.md"


def write_protocol(db, topic: str, text: str) -> Dict:
    """Freeze the protocol. A second call does not overwrite it.

    The whole point of writing it first is that it does not move when the results
    come in, so an existing file is reported as kept, not as written.
    """
    path = protocol_path(db, topic)
    if path.exists() and path.read_text(encoding="utf-8").strip():
        return {"path": str(path), "written": False}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text or "", encoding="utf-8")
    return {"path": str(path), "written": True}


async def build_protocol(llm, topic: str, question: str = "") -> str:
    """An LLM-written protocol, but a file from then on."""
    messages = [
        {
            "role": "system",
            "content": (
                "You write the protocol of a quantitative literature synthesis "
                "BEFORE any number is pooled, so it cannot be tuned to the "
                "results. Be specific and short.\n\n"
                "Return Markdown with exactly these headings:\n"
                "## Frage (PICO)\nPopulation, Intervention/Exposition, Comparison, "
                "Outcome - one line each.\n"
                "## Einschlusskriterien\n bullet list\n"
                "## Ausschlusskriterien\n bullet list\n"
                "## Primäres Outcome\n one line, plus the effect scale that will "
                "be pooled (standardized or raw)\n"
                "## Geplante Zählungen\n what will be reported (found, assessed, "
                "excluded with reasons, included, with usable effect size, pooled)\n"
            ),
        },
        {
            "role": "user",
            "content": (f"Topic: {topic}\n"
                        + (f"Main question: {question}\n" if question else "")
                        + "Write the protocol."),
        },
    ]
    try:
        text = await llm.chat(messages, temperature=0.3, max_tokens=1200)
    except Exception as e:
        logger.warning(f"Could not generate protocol: {e}")
        return ""
    return text or ""


def record_decision(db, topic: str, source_id: str, decision: str,
                    reason: str = "", decided_by: str = "agent") -> Dict:
    """Record one inclusion or exclusion, with its reason."""
    decision = (decision or "").strip().lower()
    if decision not in (DECISION_INCLUDE, DECISION_EXCLUDE):
        decision = DECISION_EXCLUDE
    row = {
        "id": gen_id(),
        "topic": topic or "",
        "source_id": source_id or "",
        "decision": decision,
        "reason": (reason or "")[:500],
        "decided_by": decided_by or "agent",
        "created_at": now_iso(),
    }
    db.save_screening_decision(row)
    return row


def record_automatic_decisions(db, topic: str, min_relevance: float = 0.25,
                              limit: int = 400) -> Dict[str, int]:
    """Write the decisions the data already implies, once per source.

    Included: scored at or above the relevance gate *and* with a real document
    text (an abstract-only source cannot contribute a poolable number).
    Excluded: scored below the gate. Unscored sources are left undecided on
    purpose - a decision before the relevance judgement would be a guess.
    """
    decided = decided_source_ids(db, topic)
    written = {DECISION_INCLUDE: 0, DECISION_EXCLUDE: 0}
    with_text = set()
    for row in db._get_all("source_texts"):
        if row.get("source_id") and row.get("kind") != "abstract" and \
                int(row.get("chars") or 0) >= 3000:
            with_text.add(row["source_id"])
    for source in db._get_all("sources", limit=limit):
        source_id = source.get("id") or ""
        if not source_id or source_id in decided:
            continue
        if int(source.get("relevance_scored") or 0) != 1:
            continue
        relevance = float(source.get("relevance") or 0.0)
        if relevance < float(min_relevance or 0.0):
            record_decision(db, topic, source_id, DECISION_EXCLUDE,
                            f"Relevanz {relevance:.2f} unter der Schwelle "
                            f"{float(min_relevance):.2f}", decided_by="relevance-gate")
            written[DECISION_EXCLUDE] += 1
            continue
        if source_id in with_text:
            record_decision(db, topic, source_id, DECISION_INCLUDE,
                            f"Relevanz {relevance:.2f}, voller Text vorhanden",
                            decided_by="relevance-gate")
            written[DECISION_INCLUDE] += 1
    return written


def decided_source_ids(db, topic: str) -> Dict[str, dict]:
    """Latest decision per source (a later decision wins)."""
    latest: Dict[str, dict] = {}
    for row in db.get_screening_decisions(topic=topic):
        latest[row.get("source_id") or ""] = row
    return latest


def prisma_counts(db, topic: str, min_relevance: float = 0.25,
                  min_studies: int = 2) -> Dict:
    """Counts the database can prove - nothing inferred, nothing rounded up."""
    sources = db._get_all("sources")
    decisions = decided_source_ids(db, topic)
    assessed = [s for s in sources if int(s.get("relevance_scored") or 0) == 1]
    excluded_reasons: Dict[str, int] = {}
    included: List[dict] = []
    for source in sources:
        decision = decisions.get(source.get("id") or "")
        if decision and decision.get("decision") == DECISION_EXCLUDE:
            reason = (decision.get("reason") or "ohne Grund").strip() or "ohne Grund"
            excluded_reasons[reason] = excluded_reasons.get(reason, 0) + 1
            continue
        if decision and decision.get("decision") == DECISION_INCLUDE:
            included.append(source)
            continue
        if int(source.get("relevance_scored") or 0) == 1 and \
                float(source.get("relevance") or 0.0) >= float(min_relevance or 0.0):
            included.append(source)

    with_effects = {
        row.get("source_id") for row in db._get_all("study_effects")
        if row.get("source_id")
    }
    effects = db._get_all("study_effects")
    disputed = [row for row in effects if int(row.get("disputed") or 0) == 1]
    # Rows that report a review's aggregate rather than a primary sample. They are
    # counted here because "poolbar" without this number reads as "these studies
    # go into the pooled estimate", and they do not.
    aggregate = [
        row for row in effects
        if aggregate_design(str(row.get("design") or ""))
    ]
    # The number a reader actually wants: rows that survive every gate the pool
    # applies (not disputed, not rejected, a primary design, usable precision).
    # Computed with the same function the pool uses, so the count cannot drift
    # away from the table.
    poolable_primary = sum(1 for row in effects if not standardize(row)[3])
    rejected = [row for row in effects if not int(row.get("disputed") or 0) == 1
                and (row.get("rejection_reason") or "")]
    return {
        "sources": len(sources),
        "assessed": len(assessed),
        "included": len(included),
        "excluded": sum(excluded_reasons.values()),
        "excluded_reasons": excluded_reasons,
        "effects": len(effects),
        "effects_with_source": len(with_effects),
        "effects_poolable": db.count_poolable_effects(),
        "effects_aggregate": len(aggregate),
        "effects_poolable_primary": poolable_primary,
        "effects_disputed": len(disputed),
        "effects_rejected": len(rejected),
        "sources_without_effects": len(included) - len(with_effects),
        "min_relevance": float(min_relevance or 0.0),
        "min_studies": int(min_studies or 2),
    }
