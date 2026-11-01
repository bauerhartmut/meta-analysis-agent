#!/usr/bin/env python3
"""Read effect sizes out of the papers the queue would read next - now.

The run works its backlog in priority order, and evidence work outranks effect
reading. That is right for a long run and wrong when someone wants to see whether
the extraction works: waiting for the queue means waiting for hours before the
first number exists.

This script is the same code path the run uses - same targets, same extractor,
same quote verification, same plausibility gate, same work items - only claimed
immediately and bounded to N documents. Items it finishes are marked done, so the
run does not read the same paper again.

Usage:
    python scripts/extract_effects_on_demand.py --topic "<topic>" [--count 6]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from research_agent.config import get_config
from research_agent.database import Database
from research_agent.llm.engine import LLMEngine
from research_agent.meta import (
    EffectExtractor, build_targets, load_targets, save_targets, target_labels,
)
from research_agent.meta.screening import record_automatic_decisions
from research_agent.work_queue import KIND_EFFECT_EXTRACTION, WorkQueue


def _usage_sink(usage_db, backend: str):
    """Store each call's tokens where the run stores them.

    Without a sink this script's calls are invisible in the dashboard: the panel
    reads the shared usage database, and a call nobody recorded did not cost
    anything only as long as nobody looks. The run wires the same sink in
    ``ResearchOrchestrator._persist_llm_usage``.
    """
    import time
    from datetime import datetime

    def sink(entry: dict) -> None:
        try:
            stamp = datetime.fromtimestamp(
                float(entry.get("timestamp") or time.time())
            ).astimezone().isoformat()
        except (TypeError, ValueError):
            stamp = datetime.now().astimezone().isoformat()
        usage_db.record_llm_usage(
            phase=str(entry.get("phase") or "effect_extraction"),
            prompt_tokens=int(entry.get("prompt_tokens") or 0),
            completion_tokens=int(entry.get("completion_tokens") or 0),
            time_ms=float(entry.get("time_ms") or 0.0),
            success=bool(entry.get("success", True)),
            model=str(entry.get("model") or ""),
            backend=backend,
            timestamp=stamp,
        )

    return sink


def _json_list(value) -> list:
    if isinstance(value, list):
        return value
    try:
        loaded = json.loads(value or "[]")
        return loaded if isinstance(loaded, list) else []
    except (TypeError, ValueError):
        return []


async def run(topic: str, count: int) -> int:
    config = get_config()
    path = config.database_for_topic(topic) if config.database_per_topic \
        else config.database_url
    db = Database(path)
    # Accounting goes to the shared file, exactly like the run's own calls.
    usage_db = Database(config.usage_database_url or path)
    LLMEngine.set_usage_sink(_usage_sink(usage_db, config.llm_backend))
    llm = LLMEngine()
    if not await llm.health_check():
        print("LLM backend not reachable", file=sys.stderr)
        return 2

    targets = load_targets(db, topic)
    if not target_labels(targets):
        targets = await build_targets(llm, topic, question=topic)
        if target_labels(targets):
            print("targets:", ", ".join(target_labels(targets)))
            save_targets(db, topic, targets)
        else:
            print("no outcome targets derived - effects keep their own labels")

    queue = WorkQueue(db, topic, config.source_relevance_threshold)
    extractor = EffectExtractor(llm, db, double_pass=True)
    read = 0
    for _ in range(max(1, count)):
        claimed = queue.claim(1, kinds=[KIND_EFFECT_EXTRACTION])
        if not claimed:
            print("no open effect_extraction item left")
            break
        item = claimed[0]
        source = db.get_source(item["ref_id"]) or {}
        payload = db.get_source_text_for_source(item["ref_id"]) or {}
        text_id = payload.get("id") or ""
        text = db.read_source_text(text_id) if text_id else ""
        title = (source.get("title") or item.get("title") or "")[:60]
        if len(text) < 2000:
            queue.resolve(item["id"], "no document text to read")
            print(f"- skipped (no text): {title}")
            continue

        rows = await extractor.extract(
            item["ref_id"], text, topic=topic,
            sections=_json_list(payload.get("sections")),
            page_offsets=_json_list(payload.get("page_offsets")),
            source_text_id=text_id, targets=targets,
        )
        read += 1
        poolable = sum(
            1 for row in rows
            if not row.disputed and not row.rejection_reason
            and (row.se is not None or (row.ci_low is not None and row.ci_high is not None))
        )
        disputed = sum(1 for row in rows if row.disputed)
        keys = sorted({row.outcome_key for row in rows if row.outcome_key})
        queue.resolve(
            item["id"],
            f"{len(rows)} Effektzeile(n), {poolable} poolbar, {disputed} strittig",
        )
        print(
            f"- {title}: {len(rows)} rows, {poolable} poolable, {disputed} disputed"
            + (f", targets: {', '.join(keys)}" if keys else ", no target hit")
        )

    record_automatic_decisions(db, topic, config.source_relevance_threshold)
    print(
        f"done: {read} document(s) read, "
        f"{db.count_study_effects()} effect row(s) stored, "
        f"{db.count_poolable_effects()} poolable"
    )
    await llm.close()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", "-t", required=True)
    parser.add_argument("--count", "-c", type=int, default=6)
    args = parser.parse_args()
    return asyncio.run(run(args.topic, args.count))


if __name__ == "__main__":
    raise SystemExit(main())
