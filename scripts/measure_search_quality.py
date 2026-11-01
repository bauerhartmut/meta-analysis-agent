#!/usr/bin/env python3
"""Measure search quality: legacy keyword search vs. the federated engine.

Runs both paths against the live providers for the same question, then reports
what a cycle would actually have seen: raw hits, duplicate copies, unique works,
how many pass the topic relevance gate, and how many of the first ten are
relevant (i.e. whether ranking helps or only the pile is bigger).

    python scripts/measure_search_quality.py --topic "IQ Genetics" \\
        --question "Do polygenic scores predict cognitive outcomes?"

Read-only: it queries the providers and the existing topic filter and writes no
search telemetry to the database (that would mark the compared queries as dead).
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from research_agent.config import get_config
from research_agent.orchestrator import ResearchOrchestrator
from research_agent.research.engine import merge_candidates
from research_agent.research.search import extract_keywords


def _unique_by_url(results):
    seen, unique = set(), []
    for r in results:
        if r.url not in seen:
            seen.add(r.url)
            unique.append(r)
    return unique


def _relevant(orch, results):
    return [r for r in results if orch._is_topic_relevant(r)]


async def run_legacy(orch, queries, per_provider):
    gathered = await asyncio.gather(
        *[orch.search.search(q, max_results_per_provider=per_provider) for q in queries],
        return_exceptions=True,
    )
    raw = []
    for item in gathered:
        if isinstance(item, list):
            raw.extend(item)
        else:
            print(f"  legacy query failed: {item}")
    return raw


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="IQ Genetics")
    parser.add_argument("--question", required=True)
    parser.add_argument("--per-provider", type=int, default=5)
    args = parser.parse_args()

    config = get_config()
    orch = ResearchOrchestrator(config)
    orch.current_topic = args.topic
    # A measurement must not teach the production telemetry: the queries below
    # are deliberately compared without recording them as tried-and-failed, or
    # the next real cycle would treat them as dead.
    orch.engine.db = None

    fallbacks = [
        extract_keywords(args.question, max_words=6),
        extract_keywords(args.topic, max_words=4) + " study evidence",
        "polygenic score prediction cognitive outcome",
    ]
    print(f"Topic:    {args.topic}")
    print(f"Question: {args.question}")
    print(f"Fallback queries (legacy path): {fallbacks}\n")

    print("=== legacy: 3 keyword queries, URL dedupe, provider order ===")
    legacy_raw = await run_legacy(orch, fallbacks, args.per_provider)
    legacy_unique = _unique_by_url(legacy_raw)
    legacy_merged, legacy_dupes = merge_candidates(
        [(r, "", r.source_type) for r in legacy_raw]
    )
    legacy_keep = _relevant(orch, legacy_unique)
    legacy_keep_merged = _relevant(orch, legacy_merged)
    print(f"raw hits:            {len(legacy_raw)}")
    print(f"unique by URL:       {len(legacy_unique)}")
    print(f"same work, ignored:  {legacy_dupes} cross-provider copies")
    print(f"unique works:        {len(legacy_merged)}")
    print(f"pass topic gate:     {len(legacy_keep_merged)}/{len(legacy_merged)}")
    print(f"gate on first 10:    {len(_relevant(orch, legacy_unique[:10]))}/10")
    legacy_by_provider = {}
    for result in legacy_raw:
        name = getattr(result, "source_type", "?") or "?"
        legacy_by_provider[name] = legacy_by_provider.get(name, 0) + 1
    print("per provider:", ", ".join(
        f"{name}={count}" for name, count in sorted(
            legacy_by_provider.items(), key=lambda kv: -kv[1]
        )
    ), "\n")

    print("=== engine: planned queries, provider syntax, DOI/title dedupe, ranking ===")
    batch = await orch.engine.search_cycle(
        args.question, args.topic, fallbacks=fallbacks, cycle=0
    )
    print("planned queries:")
    for q in batch.queries:
        units = f" | phrases: {q.units}" if q.units else ""
        print(f"  - {q.text}{units}")
    engine_keep = _relevant(orch, batch.candidates)
    by_provider = {}
    for row in batch.provider_rows:
        entry = by_provider.setdefault(row["provider"], {"requests": 0, "hits": 0})
        entry["requests"] += 1
        entry["hits"] += int(row.get("results") or 0)
    print("per provider:")
    for name, entry in sorted(by_provider.items(), key=lambda kv: -kv[1]["hits"]):
        print(f"  {name:<18} {entry['hits']:>3} hit(s) / {entry['requests']} request(s)")
    if batch.failures:
        print("failures:", "; ".join(batch.failures[:6]))
    print(f"raw hits:            {sum(row['results'] for row in batch.provider_rows)}")
    print(f"same work, merged:   {batch.duplicates} duplicates")
    print(f"unique works:        {len(batch.candidates)}")
    print(f"pass topic gate:     {len(engine_keep)}/{len(batch.candidates)}")
    print(f"gate on first 10:    {len(_relevant(orch, batch.candidates[:10]))}/10")
    top = batch.candidates[:8]
    print("\ntop ranked candidates:")
    for candidate in top:
        mark = "keep" if orch._is_topic_relevant(candidate) else "drop"
        print(f"  [{mark}] {candidate.score:.3f}  {candidate.title[:88]}")
        print(f"          {', '.join(sorted(candidate.providers))} | {candidate.year or '?'} | cit {candidate.citations}")

    print("\n=== delta ===")
    print(f"unique works:  {len(legacy_merged)} -> {len(batch.candidates)}")
    print(f"relevant:      {len(legacy_keep_merged)} -> {len(engine_keep)}")
    print(f"relevant in first 10: {len(_relevant(orch, legacy_unique[:10]))} -> "
          f"{len(_relevant(orch, batch.candidates[:10]))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
