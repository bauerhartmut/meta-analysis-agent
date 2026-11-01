"""What the synthesis is aiming at - the outcome targets of the research goal.

Grouping by the free-text outcome label was the weak link in the chain: the
extractor was told to "report every outcome and contrast the text quantifies",
so one paper reported "fluid intelligence" and the next "IQ", both landed in
their own group, and every group stayed at k = 1. The pooling engine was ready
and correctly refused to average a single study - the run simply never gave it
two rows about the same thing.

This module closes that gap on the side of the question, not the side of the
data:

1. **Derive** - one LLM call turns the research question into a small set of
   outcome labels with their usual aliases, a direction ("higher = better
   cognition") and a population. It is written once per topic and stored, so a
   later cycle cannot quietly re-aim the synthesis at whatever the papers
   happened to report.
2. **Aim** - the extraction prompt gets these labels as a fixed vocabulary: when
   the text quantifies one of them, the model must use exactly that label.
3. **Canonicalise** - deterministically, after the reading: a label that matches
   a target (exactly, by alias, or by containment) is stored under the target's
   label in ``study_effects.outcome_key``. The label the model actually wrote
   stays in ``outcome``, so nothing is rewritten and every row is still
   checkable against its quote.
4. **Count the coverage** - how many stored rows lie on the target and how many
   beside it. A synthesis that reads 40 papers and pools 3 of them has to say
   so, not present the 3 as the state of the literature.

Without targets (the derivation failed, or ``META_TARGETS_ENABLED=0``) nothing
is filtered: rows keep their own labels and behave as before. A missing aim is
reported as missing, never silently replaced by a guess.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Dict, Iterable, List, Optional

from ..models import now_iso
from .designs import is_primary_study

logger = logging.getLogger(__name__)

# Bumped when the derivation prompt changes; stored with the targets so a report
# can tell which aim it is reading. v2 (01.11.): the Mediterranean run pooled
# k = 2 while 21 poolable rows sat beside the aim - related cardiovascular
# endpoints are now their own aim entries, and exposure metadata (adherence
# scores, test-retest reliability) is excluded up front.
TARGETS_VERSION = "meta-targets/2"

MAX_OUTCOMES = 6
MAX_ALIASES = 6

# Properties of a *study*, not of the world. A synthesis pools what was measured
# in people; "statistical power" or "causal effect estimate" are answers the run
# computes itself, and a paper never reports them as an outcome to be pooled.
# Measured on the real model: asked about a power question, it offered exactly
# these two - so the guard is needed, not hypothetical.
DESIGN_PROPERTIES = (
    "statistical power", "power to", "sample size", "effect estimate",
    "causal effect", "p value", "p-value", "confidence interval",
    "statistical significance", "detection probability", "variance explained",
)
# Only rejected as the whole label: "attentional bias" and "grip strength" are
# measurements, "bias" and "power" alone are not.
DESIGN_PROPERTY_EXACT = ("power", "estimate", "precision", "bias", "significance")


def _is_design_property(label: str) -> bool:
    text = _norm(label)
    if text in DESIGN_PROPERTY_EXACT:
        return True
    return any(term in text for term in DESIGN_PROPERTIES)


def _norm(value: str) -> str:
    """Lowercase, punctuation to spaces, collapsed - the same for both sides."""
    text = re.sub(r"[^\w\s]+", " ", str(value or "").lower())
    return " ".join(text.split())


def target_labels(targets: Optional[Dict]) -> List[str]:
    """The canonical labels, in the order the derivation returned them."""
    return [str(entry.get("label") or "").strip()
            for entry in (targets or {}).get("outcomes") or []
            if str(entry.get("label") or "").strip()]


def canonical_outcome(label: str, targets: Optional[Dict]) -> str:
    """The target label this reading belongs to, or '' when it belongs to none.

    Exact match first, then an alias, then containment ("cognitive ability"
    inside "general cognitive ability"). Containment is only accepted from four
    characters up, so a two-letter alias like "iq" has to match exactly and
    cannot swallow unrelated labels.
    """
    norm = _norm(label)
    if not norm or not targets:
        return ""
    contained = ""
    for entry in targets.get("outcomes") or []:
        name = str(entry.get("label") or "").strip()
        if not name:
            continue
        for candidate in [name] + list(entry.get("aliases") or []):
            alias = _norm(candidate)
            if not alias:
                continue
            if alias == norm:
                return name
            if len(alias) >= 4 and (alias in norm or norm in alias):
                contained = contained or name
    return contained


def normalize_targets(payload, question: str = "") -> Dict:
    """Accept what the model returned and keep only what a table can use.

    Tolerates a bare list, a wrapped object and string entries, because a
    derivation that fails on shape would leave the run without an aim for a
    reason that has nothing to do with the science.
    """
    data = payload
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except (TypeError, ValueError):
            return {}
    if isinstance(data, list):
        data = {"outcomes": data}
    if not isinstance(data, dict):
        return {}

    outcomes: List[Dict] = []
    seen = set()
    for item in data.get("outcomes") or []:
        if isinstance(item, str):
            item = {"label": item}
        if not isinstance(item, dict):
            continue
        label = " ".join(str(item.get("label") or item.get("outcome") or "").split())
        if not label or len(label) > 120:
            continue
        if _is_design_property(label):
            logger.info(f"Outcome target rejected as a study property: '{label}'")
            continue
        key = _norm(label)
        if key in seen:
            continue
        seen.add(key)
        aliases: List[str] = []
        for alias in item.get("aliases") or []:
            text = " ".join(str(alias).split())
            if text and _norm(text) not in {_norm(a) for a in aliases} and \
                    _norm(text) != key:
                aliases.append(text)
        outcomes.append({
            "label": label,
            "aliases": aliases[:MAX_ALIASES],
            "direction": str(item.get("direction") or "").strip()[:200],
            "scale": str(item.get("scale") or item.get("effect_type") or "").strip()[:40],
        })
        if len(outcomes) >= MAX_OUTCOMES:
            break

    if not outcomes:
        return {}

    # The question we asked about wins over the one the model wrote back. Measured
    # on the real model: asked about a broad topic it returned a narrow
    # falsification test as its own "question", and a synthesis aimed at that
    # sub-question excludes most of its own corpus.
    return {
        "version": TARGETS_VERSION,
        "question": str(question or data.get("question") or "").strip()[:1000],
        "population": str(data.get("population") or "").strip()[:400],
        "comparison": str(data.get("comparison") or "").strip()[:400],
        "outcomes": outcomes,
        "exclusion": [str(x).strip()[:200] for x in (data.get("exclusion") or [])
                      if str(x).strip()][:8],
        "created_at": str(data.get("created_at") or now_iso()),
    }


async def build_targets(llm, topic: str, question: str = "") -> Dict:
    """Ask once which outcomes the question is about.

    The prompt is deliberately narrow: a synthesis needs two or three outcomes
    that many papers report, not a complete ontology. Too many targets split the
    pool again - which is the failure this module exists to fix.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "You define the outcome measures of a quantitative literature "
                "synthesis, before any number is read. You do not search and you "
                "do not answer the question.\n\n"
                "An outcome is a variable measured IN PEOPLE: a test score, a "
                "diagnosis, a biomarker, a mortality endpoint. It is never a "
                "property of the study or the analysis - not statistical power, "
                "not a sample size, not a causal estimate, not a p-value. If the "
                "question asks about a design parameter, name the variables that "
                "design is about: those are what the papers measure.\n\n"
                "Give at most five outcomes: two or three the question is "
                "directly about, plus one or two CLOSELY RELATED physiological "
                "endpoints the literature commonly reports alongside them (e.g. "
                "for a cardiovascular question: blood pressure, lipid profile, "
                "atherosclerosis, hypertensive disorders in pregnancy). Each "
                "related endpoint is its own outcome with its own aliases - "
                "folding it into the main outcome via an alias would pool "
                "different constructs into one number. Do not list how the "
                "exposure is MEASURED: adherence scores (MEDAS, aMED), rating "
                "scales and test-retest reliability describe the exposure, not "
                "an endpoint the body shows, and rows on them can never enter a "
                "pool of health outcomes.\n"
                "Use the label a paper would use in a results table, in "
                "English, short. Add the aliases under which the same construct "
                "appears in that literature (e.g. 'IQ', 'cognitive test score', "
                "'general cognitive ability'), because two labels for one "
                "construct split a pool and make it unpoolable.\n"
                "`direction` says what a HIGHER number means ('higher = better "
                "cognition'). `scale` is the effect measure papers usually "
                "report for it (smd, r, or, hr, beta, mean_diff, ...).\n"
                "If the question names no measurable outcome, return an empty "
                "outcomes list - an invented outcome would aim the whole "
                "synthesis at nothing.\n\n"
                "Return JSON: {\"question\": str, \"population\": str, "
                "\"comparison\": str, \"outcomes\": [{\"label\": str, "
                "\"aliases\": [str], \"direction\": str, \"scale\": str}], "
                "\"exclusion\": [str]}"
            ),
        },
        {
            "role": "user",
            "content": (f"Topic: {topic}\n"
                        + (f"Research question: {question}\n" if question else "")
                        + "Which outcomes measure this question?"),
        },
    ]
    try:
        result = await llm.chat_json(messages, temperature=0.2, max_tokens=900)
    except Exception as e:
        logger.warning(f"Could not derive outcome targets: {e}")
        return {}
    return normalize_targets(result, question=question or topic)


def save_targets(db, topic: str, targets: Dict) -> Dict:
    """Store the aim. Written once - a second derivation is reported, not applied."""
    if not targets or not target_labels(targets):
        return {"written": False, "reason": "no usable targets"}
    try:
        existing = load_targets(db, topic)
    except Exception:
        existing = {}
    if existing and target_labels(existing):
        return {"written": False, "reason": "targets already frozen"}
    payload = dict(targets)
    payload.setdefault("created_at", now_iso())
    db.save_review_targets(topic or "", payload)
    return {"written": True, "targets": payload}


def load_targets(db, topic: str) -> Dict:
    """The stored aim for this topic, or {} when none was derived."""
    try:
        row = db.get_review_targets(topic or "")
    except Exception as e:
        logger.debug(f"Could not load review targets: {e}")
        return {}
    if not row:
        return {}
    payload = row.get("payload")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except (TypeError, ValueError):
            return {}
    return payload if isinstance(payload, dict) else {}


def _poolable(row: Dict) -> bool:
    if int(row.get("disputed") or 0) == 1:
        return False
    # A review's aggregate never enters the pool, so it must not be counted as
    # a poolable row here either - otherwise the report claims studies it does
    # not pool.
    if not is_primary_study(row):
        return False
    if str(row.get("rejection_reason") or "").strip():
        return False
    return row.get("se") is not None or (
        row.get("ci_low") is not None and row.get("ci_high") is not None
    )


def coverage(rows: Iterable[Dict], targets: Optional[Dict]) -> Dict:
    """How much of the read literature actually serves the question.

    ``off_target`` is not a defect - a paper can quantify something real that
    the question is not about. It is a number the report needs, because it is
    the difference between "we pooled 4 studies" and "we read 40 papers and 4
    were about this".
    """
    labels = target_labels(targets)
    result: Dict = {
        "has_targets": bool(labels),
        "targets": labels,
        "rows": 0,
        "on_target": 0,
        "off_target": 0,
        "on_target_poolable": 0,
        "by_outcome": {},
    }
    for row in rows:
        result["rows"] += 1
        key = str(row.get("outcome_key") or "").strip()
        if labels and (not key or key not in labels):
            # Rows read before an aim existed - or under one that was later
            # re-derived - are matched on read, not migrated.
            key = canonical_outcome(row.get("outcome"), targets) or key
        if not labels:
            result["off_target"] += 1
            continue
        if key and key in labels:
            result["on_target"] += 1
            bucket = result["by_outcome"].setdefault(
                key, {"rows": 0, "poolable": 0}
            )
            bucket["rows"] += 1
            if _poolable(row):
                result["on_target_poolable"] += 1
                bucket["poolable"] += 1
        else:
            result["off_target"] += 1
    return result
