"""A research program instead of a question loop.

The agent used to pick its next question from one flat pool: open questions,
seed questions, whatever the planner invented last cycle. Over hours that
produces a long list of loosely related lookups - and no answer, because nothing
ever gets finished. A scientist works differently: the topic is broken into
sub-questions, each is worked until it is decided or stops paying, and the effort
goes to whichever part currently promises the largest gain.

This module holds that program:

* ``parse_decomposition`` turns the planner's answer into program items, each
  with a rationale, competing positions to separate, and an initial weight.
* ``marginal_value`` is the allocation rule: importance x openness, discounted by
  what the item has already produced, divided by what it has cost in cycles.
* ``close_decision`` owns the stop rules (cycle budget, saturation). Deciding
  that a sub-question is *answered* stays with the LLM verdict - a rule cannot
  read a literature, but it can notice that reading further pays nothing.
* ``select_facts_for`` picks the material a verdict is derived from, so the
  comparison between competing positions is made against collected evidence
  rather than against the model's priors.

Deliberately free of LLM calls and side effects: everything here is a function of
stored numbers, so it is testable and reproducible.
"""

import json
import logging
import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

STATUS_OPEN = "open"
STATUS_ACTIVE = "active"
STATUS_DONE = "done"
STATUSES = (STATUS_OPEN, STATUS_ACTIVE, STATUS_DONE)

# What kind of sub-question this is. The kind decides how a result has to look
# before the question may be closed: an empirical question wants evidence, a
# conceptual one wants a distinction that survives the objections.
KINDS = ("empirical", "mechanism", "measurement", "theory", "ethics", "context")

_ITEM_KEYS = ("subquestions", "sub_questions", "items", "program", "questions", "parts")
_STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "what", "which",
    "does", "how", "are", "was", "were", "have", "has", "been", "being", "than",
    "when", "where", "whether", "there", "their", "them", "they", "its", "it",
    "about", "between", "under", "over", "more", "most", "less", "least", "any",
    "all", "some", "such", "can", "could", "would", "should", "may", "might",
    "not", "but", "ist", "und", "der", "die", "das", "wie", "was", "welche",
    "welcher", "welches", "für", "mit", "von", "auf", "eine", "einer", "eines",
    "sich", "dass", "auch", "aus", "bei", "nach",
}


def _clamp(value, low: float, high: float, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def normalize_kind(value) -> str:
    text = str(value or "").strip().lower()
    if text in KINDS:
        return text
    for kind in KINDS:
        if kind in text:
            return kind
    return "empirical"


def parse_rivals(value) -> List[dict]:
    """Competing positions for a sub-question, each with the test that separates it.

    Accepts the shapes a chat model actually returns: a list of dicts, a list of
    strings, or one dict with a "positions" key.
    """
    raw = value
    if isinstance(raw, dict):
        for key in ("positions", "rivals", "theories", "alternatives"):
            if key in raw:
                raw = raw[key]
                break
        else:
            raw = [raw]
    if isinstance(raw, str):
        raw = [part.strip() for part in re.split(r"\n+|;", raw) if part.strip()]
    if not isinstance(raw, (list, tuple)):
        return []

    out: List[dict] = []
    seen = set()
    for entry in raw:
        if isinstance(entry, str):
            position, test = entry.strip(), ""
        elif isinstance(entry, dict):
            position = str(
                entry.get("position") or entry.get("claim") or entry.get("theory") or ""
            ).strip()
            test = str(
                entry.get("discriminating_test") or entry.get("test")
                or entry.get("would_distinguish") or ""
            ).strip()
        else:
            continue
        if len(position) < 8:
            continue
        key = position.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append({"position": position, "discriminating_test": test})
    return out[:4]


def _words(text: str) -> set:
    return {
        word for word in re.findall(r"[a-zäöüß0-9]{4,}", (text or "").lower())
        if word not in _STOPWORDS
    }


def _similar(left: str, right: str) -> float:
    a, b = _words(left), _words(right)
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def _items_from_payload(payload) -> List[dict]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, (dict, str))]
    if isinstance(payload, dict):
        for key in _ITEM_KEYS:
            if isinstance(payload.get(key), list):
                return payload[key]
        if payload.get("question"):
            return [payload]
        # A model that wraps the array under a key we did not anticipate: take
        # the only list in the object rather than giving up on the whole program.
        lists = [value for value in payload.values() if isinstance(value, list)]
        if len(lists) == 1:
            return lists[0]
    return []


def parse_decomposition(payload, topic: str, limit: int = 6) -> List[dict]:
    """Program items from the planner's decomposition ([] when unusable).

    Drops items that are not questions, merges duplicates that differ only in
    wording, and caps the program: a program of thirty sub-questions is the
    question loop with extra steps.
    """
    items: List[dict] = []
    for entry in _items_from_payload(payload):
        if isinstance(entry, str):
            entry = {"question": entry}
        question = str(
            entry.get("question") or entry.get("sub_question") or entry.get("title") or ""
        ).strip()
        if len(question) < 15:
            continue
        rivals = parse_rivals(
            entry.get("rivals") or entry.get("competing_positions")
            or entry.get("theories") or entry.get("positions")
        )
        if any(_similar(question, existing["question"]) > 0.7 for existing in items):
            logger.debug(f"Decomposition: merged duplicate sub-question {question[:60]}")
            continue
        items.append({
            "question": question,
            "rationale": str(
                entry.get("rationale") or entry.get("why") or entry.get("relevance") or ""
            ).strip()[:600],
            "kind": normalize_kind(entry.get("kind") or entry.get("type")),
            "importance": _clamp(entry.get("importance"), 0.05, 1.0, 0.5),
            "uncertainty": _clamp(
                entry.get("uncertainty") or entry.get("openness"), 0.1, 1.0, 0.8
            ),
            "rivals": rivals,
        })
        if len(items) >= max(1, limit):
            break
    return items


def marginal_value(item: dict) -> float:
    """Expected gain per cycle for working this sub-question next.

    Three factors, all from stored numbers: how much the answer matters
    (importance), how open the question still is (uncertainty, discounted by what
    the item has already produced), and what it has cost so far (cycles). Items
    that have to separate competing positions carry a small premium - deciding
    between two live explanations is worth more than adding another confirming
    paper to an uncontested one.
    """
    importance = _clamp(item.get("importance"), 0.05, 1.0, 0.5)
    uncertainty = _clamp(item.get("uncertainty"), 0.1, 1.0, 0.8)
    cycles = int(item.get("cycles_spent") or 0)
    facts = int(item.get("facts_gained") or 0)
    sources = int(item.get("sources_gained") or 0)

    value = importance * uncertainty
    value /= 1.0 + 0.10 * facts + 0.05 * sources
    value /= 1.0 + 0.35 * cycles
    if parse_rivals(item.get("rivals")):
        value *= 1.15
    return round(value, 4)


def rank(items: Sequence[dict]) -> List[dict]:
    """Items by marginal value, highest first (deterministic tie-break)."""
    return sorted(
        [item for item in (items or ()) if item.get("status") != STATUS_DONE],
        key=lambda item: (
            -marginal_value(item),
            str(item.get("opened_at") or ""),
            str(item.get("id") or ""),
        ),
    )


def select_next(
    items: Sequence[dict], active_id: str = "", switch_threshold: float = 0.7
) -> Optional[dict]:
    """Which sub-question to work next, with commitment to the running one.

    Always taking the global maximum looks like optimal allocation and behaves
    like round-robin: as soon as the current item has cost a cycle, a fresh item
    outranks it, so every item gets one cycle and none gets decided. The running
    item is therefore kept until another one is clearly better - `switch_threshold`
    as the share of the best value it must still reach. That is what lets an item
    reach its cycle budget and produce a verdict.
    """
    rows = [item for item in (items or ()) if item.get("status") != STATUS_DONE]
    ranked = rank(rows)
    if not ranked:
        return None
    best = ranked[0]
    if active_id:
        active = next(
            (item for item in rows if str(item.get("id")) == str(active_id)), None
        )
        if active is not None:
            best_value = marginal_value(best)
            if best_value <= 0 or marginal_value(active) >= switch_threshold * best_value:
                return active
    return best


def close_decision(
    item: dict,
    budget_cycles: int = 8,
    saturation_cycles: int = 3,
    min_cycles: int = 2,
) -> Tuple[bool, str]:
    """Stop rules for one sub-question: (close?, reason).

    Two rules, both about effort rather than about truth: the item has used its
    cycle budget, or the last cycles brought no new fact, no new source and no
    new evidence. Whether a sub-question is *answered* is not decided here - that
    is what the verdict is for.
    """
    if item.get("status") == STATUS_DONE:
        return False, ""
    cycles = int(item.get("cycles_spent") or 0)
    if cycles < max(0, min_cycles):
        return False, ""
    if budget_cycles > 0 and cycles >= budget_cycles:
        return True, f"Zyklenbudget ausgeschöpft ({cycles}/{budget_cycles})"
    gain_cycles = int(item.get("gain_cycles") or 0)
    if saturation_cycles > 0 and gain_cycles >= saturation_cycles:
        return True, f"{gain_cycles} Zyklen in Folge ohne neuen Ertrag"
    return False, ""


def select_facts_for(question: str, facts: Iterable[dict], limit: int = 12) -> List[dict]:
    """Facts that actually bear on a sub-question, best first.

    Keyword overlap against the question, then confidence. Used to build the
    material for a verdict, so the comparison between competing positions is made
    against what was collected instead of against the model's priors.
    """
    wanted = _words(question)
    scored: List[Tuple[float, float, dict]] = []
    for fact in facts or ():
        content = str(fact.get("content") or "")
        overlap = len(wanted & _words(content))
        if overlap <= 0:
            continue
        try:
            confidence = float(fact.get("confidence") or 0.0)
        except (TypeError, ValueError):
            confidence = 0.0
        scored.append((overlap, confidence, fact))
    scored.sort(key=lambda entry: (-entry[0], -entry[1]))
    return [entry[2] for entry in scored[:limit]]


def progress(items: Sequence[dict]) -> Dict[str, int]:
    """Counts for the dashboard and the report."""
    rows = list(items or ())
    return {
        "total": len(rows),
        "open": sum(1 for item in rows if item.get("status") == STATUS_OPEN),
        "active": sum(1 for item in rows if item.get("status") == STATUS_ACTIVE),
        "done": sum(1 for item in rows if item.get("status") == STATUS_DONE),
        "cycles_spent": sum(int(item.get("cycles_spent") or 0) for item in rows),
        "facts_gained": sum(int(item.get("facts_gained") or 0) for item in rows),
    }


def summarize(items: Sequence[dict], limit: int = 12) -> str:
    """Compact program state for a prompt or a report."""
    rows = list(items or ())[:limit]
    if not rows:
        return "(noch kein Forschungsprogramm aufgestellt)"
    lines = []
    for item in rows:
        lines.append(
            f"- [{item.get('status', '?')}] {item.get('question', '').strip()} "
            f"(Zyklen {int(item.get('cycles_spent') or 0)}, "
            f"Fakten +{int(item.get('facts_gained') or 0)}, "
            f"Quellen +{int(item.get('sources_gained') or 0)})"
            + (f" - Abschluss: {item.get('close_reason')}" if item.get("close_reason") else "")
        )
    return "\n".join(lines)


def has_verdict(item: dict) -> bool:
    """True when a usable verdict is stored.

    An empty JSON object is the column default, not a verdict: treating it as one
    silently skips every comparison.
    """
    raw = item.get("verdict")
    if isinstance(raw, dict):
        return bool(raw.get("favored") or raw.get("reasoning"))
    if not raw:
        return False
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return False
    return isinstance(parsed, dict) and bool(parsed.get("favored") or parsed.get("reasoning"))


def verdict_text(verdict: Optional[dict]) -> str:
    """One-line summary of a theory verdict ('' when there is none)."""
    if not isinstance(verdict, dict) or not verdict:
        return ""
    favored = str(verdict.get("favored") or "").strip()
    if not favored:
        return ""
    try:
        confidence = float(verdict.get("confidence") or 0.0)
    except (TypeError, ValueError):
        confidence = 0.0
    answer = "beantwortet" if verdict.get("answered") else "offen"
    return f"{favored} ({confidence:.0%}, {answer})"
