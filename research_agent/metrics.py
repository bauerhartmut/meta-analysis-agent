"""Deterministic corpus metrics read out of a completed research database.

Baselines for the implementation roadmap (2026-11-01): each metric is a plain
SQL query against the completed run's SQLite file, so the same numbers can be
recomputed later against the same file, without reading log text or trusting
any model's memory. LLM or provider events are counted only where the run
actually stored them (``llm_usage`` and ``query_stats``); where the schema has
no storage for a number, the metric is reported as unavailable instead of
being estimated.

Older runs wrote their LLM usage into the *global* ``data/research-usage.db``
instead of the topic database; pass it with ``--usage-db`` (the CLI defaults
to it when the topic database carries no calls).

Usage::

    python -m research_agent.metrics data/research-<topic>-<hash>.db \\
        [--out data/baseline/<name>.json] [--label "baseline 18:10"] \\
        [--usage-db data/research-usage.db]
"""

from __future__ import annotations

import argparse
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _connect_readonly(db_path: str) -> sqlite3.Connection:
    """Read-only connection; a running run's database must never be touched."""
    uri = f"file:{db_path}?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def _count(conn: sqlite3.Connection, sql: str, args: tuple = ()) -> int:
    return int(conn.execute(sql, args).fetchone()[0])


def _scalar(conn: sqlite3.Connection, sql: str, args: tuple = ()) -> Any:
    row = conn.execute(sql, args).fetchone()
    return None if row is None else row[0]


def _group(conn: sqlite3.Connection, sql: str, args: tuple = ()) -> Dict[str, int]:
    return {str(r[0]): int(r[1]) for r in conn.execute(sql, args).fetchall()}


def _group_defs(conn: sqlite3.Connection) -> Dict[str, int]:
    """Verworfene Effektzeilen: Grund -> Anzahl (exakt aus rejection_reason).

    The reason column is free text written by the gate, so the metric groups it
    as stored - never normalised mid-air, because a silently merged reason is
    a silently changed rejection.
    """
    return _group(conn,
                  "SELECT rejection_reason, COUNT(*) FROM study_effects "
                  "WHERE TRIM(rejection_reason) != '' GROUP BY rejection_reason "
                  "ORDER BY COUNT(*) DESC")


def _pools(conn: sqlite3.Connection, min_effect_rows: int = 2) -> List[Dict[str, Any]]:
    """k je Outcome-Pool: deterministisch aus study_effects, ohne LLM.

    Mirrors the pool rule in meta/pooling.build_analysis as far as SQL can:
    rows that still have a rejection reason or carry a dispute do not count as
    poolable; the exact per-row scale grouping stays in pooling.py, so these
    numbers are a measurement, not a second implementation of the pooling.
    """
    rows = conn.execute(
        """
        SELECT outcome_key,
               COUNT(*) AS rows_poolable,
               COUNT(DISTINCT source_id) AS distinct_sources
        FROM study_effects
        WHERE TRIM(outcome_key) != '' AND effect IS NOT NULL
          AND disputed = 0 AND TRIM(rejection_reason) = ''
          AND se IS NOT NULL
        GROUP BY outcome_key
        ORDER BY rows_poolable DESC
        """
    ).fetchall()
    pools = []
    for r in rows:
        pools.append({
            "outcome_key": str(r["outcome_key"]),
            "poolable_rows": int(r["rows_poolable"]),
            "distinct_sources": int(r["distinct_sources"]),
            "pooled": int(r["distinct_sources"]) >= min_effect_rows,
        })
    return pools


def _session_window(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Run duration from the stored session rows, parsed deterministically.

    Mixed ISO formats happen; unknown timestamps parse to None and the total
    is then reported as unavailable, not guessed.
    """
    rows = conn.execute(
        "SELECT start_time, end_time, cycle_count FROM research_sessions"
    ).fetchall()
    starts, ends = [], []
    cycles = 0
    parsed_bad = 0
    for r in rows:
        cycles += int(r["cycle_count"] or 0)
        for key, bucket in (("start_time", starts), ("end_time", ends)):
            raw = str(r[key] or "")
            try:
                bucket.append(datetime.fromisoformat(raw.replace("Z", "+00:00")))
            except ValueError:
                parsed_bad += 1
    duration_s = None
    if starts and ends:
        duration_s = (max(ends) - min(starts)).total_seconds()
    return {
        "sessions": len(rows),
        "cycle_count_total": cycles,
        "duration_seconds": duration_s,
        "timestamps_unparsed": parsed_bad,
    }


def _llm_metrics(conn: sqlite3.Connection,
                 usage_db_path: Optional[str]) -> Dict[str, Any]:
    """LLM call/failure/token counts - read, never estimated.

    Reads the topic database's ``llm_usage`` table; when that carries no calls
    (older runs stored usage globally) and ``usage_db_path`` exists, the
    numbers come from there and the source is reported honestly.
    """
    try:
        if _count(conn, "SELECT COUNT(*) FROM llm_usage") > 0 or not usage_db_path:
            src, usage = "topic-db", conn
        else:
            usage = _connect_readonly(usage_db_path)
            src = "global-usage-db"
    except sqlite3.OperationalError:
        return {"unavailable": "no llm_usage table in this database"}
    try:
        return {
            "source": src,
            "calls": _count(usage, "SELECT COUNT(*) FROM llm_usage"),
            "calls_failed": _count(
                usage, "SELECT COUNT(*) FROM llm_usage WHERE success = 0"),
            "calls_success": _count(
                usage, "SELECT COUNT(*) FROM llm_usage WHERE success = 1"),
            "total_tokens": int(_scalar(
                usage, "SELECT SUM(total_tokens) FROM llm_usage") or 0),
            "time_ms_mean": _scalar(usage, "SELECT AVG(time_ms) FROM llm_usage"),
            "by_phase": _group(
                usage, "SELECT phase, COUNT(*) FROM llm_usage GROUP BY phase"),
        }
    except sqlite3.OperationalError:
        return {"unavailable": "no llm_usage table in this database"}
    finally:
        if usage is not conn:
            usage.close()


def compute_metrics(db_path: str,
                    usage_db_path: Optional[str] = None,
                    **_ignored: Any) -> Dict[str, Any]:
    """All baseline metrics of one completed run. Read-only by definition."""
    conn = _connect_readonly(db_path)
    try:
        metrics: Dict[str, Any] = {}
        metrics["db_path"] = str(db_path)

        # === Quellen ===
        metrics["sources"] = {
            "found": _count(conn, "SELECT COUNT(*) FROM sources"),
            "unique_by_url": _count(
                conn, "SELECT COUNT(DISTINCT LOWER(url)) FROM sources WHERE url != ''"),
            "content_hashes": _count(
                conn, "SELECT COUNT(DISTINCT content_hash) FROM sources WHERE content_hash != ''"),
            "relevance_scored": _count(
                conn, "SELECT COUNT(*) FROM sources WHERE relevance_scored = 1"),
            "relevance_unjudgeable": _count(
                conn, "SELECT COUNT(*) FROM sources WHERE relevance_unjudgeable = 1"),
            "relevance_mean_scored": _scalar(
                conn, "SELECT AVG(relevance) FROM sources WHERE relevance_scored = 1"),
            "relevance_ge_025": _count(
                conn, "SELECT COUNT(*) FROM sources WHERE relevance >= 0.25 AND relevance_scored = 1"),
        }

        # === Volltexte (Textkoerper liegen in data/fulltext/*.txt) ===
        metrics["fulltext"] = {
            "documents": _count(conn, "SELECT COUNT(*) FROM source_texts"),
            "sources_with_text": _count(
                conn,
                "SELECT COUNT(DISTINCT source_id) FROM source_texts WHERE chars > 0"),
            "sources_with_page_offsets": _count(
                conn,
                "SELECT COUNT(*) FROM source_texts "
                "WHERE page_offsets IS NOT NULL AND page_offsets != '[]' "
                "AND TRIM(page_offsets) != ''"),
            "chars_total": int(_scalar(conn, "SELECT SUM(chars) FROM source_texts") or 0),
            "chars_mean": _scalar(
                conn, "SELECT AVG(chars) FROM source_texts"),
            "pages_total": int(_scalar(conn, "SELECT SUM(pages) FROM source_texts") or 0),
        }

        # === Screening ===
        metrics["screening"] = {
            "decisions": _count(conn, "SELECT COUNT(*) FROM screening"),
            "by_decision": _group(
                conn, "SELECT decision, COUNT(*) FROM screening GROUP BY decision"),
            "reasons": _group(
                conn,
                "SELECT reason, COUNT(*) FROM screening WHERE TRIM(reason) != '' "
                "GROUP BY reason ORDER BY COUNT(*) DESC"),
        }

        # === Fakten, Hypothesen, Evidenz ===
        metrics["facts"] = {"total": _count(conn, "SELECT COUNT(*) FROM facts")}
        metrics["hypotheses"] = {
            "total": _count(conn, "SELECT COUNT(*) FROM hypotheses"),
            "by_status": _group(
                conn, "SELECT status, COUNT(*) FROM hypotheses GROUP BY status"),
        }
        metrics["evidence"] = {
            "rows": _count(conn, "SELECT COUNT(*) FROM evidence"),
            "by_type": _group(
                conn, "SELECT evidence_type, COUNT(*) FROM evidence GROUP BY evidence_type"),
            "pairs": _count(conn, "SELECT COUNT(*) FROM evidence_pairs"),
            "pairs_by_verdict": _group(
                conn, "SELECT verdict, COUNT(*) FROM evidence_pairs GROUP BY verdict"),
        }

        # === Effektzeilen (die quantitative Engstelle der Baseline) ===
        metrics["effects"] = {
            "rows_total": _count(conn, "SELECT COUNT(*) FROM study_effects"),
            "rows_target_matched": _count(
                conn, "SELECT COUNT(*) FROM study_effects WHERE TRIM(outcome_key) != ''"),
            "rows_rejected": _count(
                conn, "SELECT COUNT(*) FROM study_effects WHERE TRIM(rejection_reason) != ''"),
            "rejection_reasons": _group_defs(conn),
            "rows_disputed": _count(
                conn, "SELECT COUNT(*) FROM study_effects WHERE disputed = 1"),
            "rows_quote_verified": _count(
                conn,
                "SELECT COUNT(*) FROM study_effects "
                "WHERE quote_start >= 0 AND TRIM(source_text_id) != ''"),
            "rows_effect_missing": _count(
                conn, "SELECT COUNT(*) FROM study_effects WHERE effect IS NULL"),
            "pools": _pools(conn),
        }

        # === RoB (zaehlend, keine Bewertungen!) ===
        metrics["risk_of_bias"] = {"assessments": _count(
            conn, "SELECT COUNT(*) FROM risk_of_bias")}

        # === LLM-Verbrauch (aus der DB, nicht geschaetzt) ===
        metrics["llm"] = _llm_metrics(conn, usage_db_path)

        # === Suchschicht: Versuche/Treffer je Provider (aus query_stats) ===
        try:
            metrics["search"] = {
                "provider_rows": _count(conn, "SELECT COUNT(*) FROM query_stats"),
                "attempts_by_provider": _group(
                    conn, "SELECT provider, SUM(attempts) FROM query_stats GROUP BY provider"),
                "results_by_provider": _group(
                    conn, "SELECT provider, SUM(results) FROM query_stats GROUP BY provider"),
                "kept_by_provider": _group(
                    conn, "SELECT provider, SUM(kept) FROM query_stats GROUP BY provider"),
                "duplicates_by_provider": _group(
                    conn, "SELECT provider, SUM(duplicates) FROM query_stats GROUP BY provider"),
            }
        except sqlite3.OperationalError:
            metrics["search"] = {"unavailable": "no query_stats table in this database"}

        # === Session/Umfang ===
        metrics["session"] = _session_window(conn)

        # === Forschungsprogramm ===
        metrics["program"] = {
            "questions": _count(conn, "SELECT COUNT(*) FROM research_questions"),
            "by_status": _group(
                conn, "SELECT status, COUNT(*) FROM research_questions GROUP BY status"),
        }
        return metrics
    finally:
        conn.close()


def to_json(metrics: Dict[str, Any]) -> str:
    return json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=False)


def write_markdown(metrics: Dict[str, Any]) -> str:
    """A short deterministic table of the headline metrics for the log."""
    lines: List[str] = []
    add = lines.append
    add("# Baseline-Metriken")
    add("")
    add(f"- Datenbank: `{metrics.get('db_path')}`")
    s = metrics.get("sources", {})
    _rel = s.get("relevance_mean_scored")
    _rel = "k. A." if _rel is None else f"{round(_rel, 3)}"
    add(f"- Quellen: {s.get('found')} gesamt, {s.get('unique_by_url')} "
        f"eindeutig je URL, Relevanz-Durchschnitt {_rel} "
        f"(n={s.get('relevance_scored')}, >=0.25: {s.get('relevance_ge_025')})")
    f = metrics.get("fulltext", {})
    add(f"- Volltexte: {f.get('documents')} Dokumente, {f.get('sources_with_text')} "
        f"Quellen mit Text, {f.get('chars_total')} Zeichen gesamt "
        f"({f.get('pages_total')} Seiten)")
    sc = metrics.get("screening", {})
    add(f"- Screening: {sc.get('by_decision')}")
    e = metrics.get("effects", {})
    add(f"- Effektzeilen: {e.get('rows_total')} gesamt, {e.get('rows_target_matched')} "
        f"im Zielmaß, {e.get('rows_rejected')} verworfen, {e.get('rows_disputed')} strittig, "
        f"{e.get('rows_quote_verified')} mit geprüfter Quote")
    add(f"- Verwerfungsgründe: "
        f"{dict(list((e.get('rejection_reasons') or {}).items())[:6])}")
    pools = e.get("pools") or []
    pooled = [p for p in pools if p.get("pooled")]
    add(f"- Pools: {len(pooled)} gepoolt "
        f"(k = {sorted(p['distinct_sources'] for p in pooled)})"
        if pooled else "- Pools: keiner")
    l = metrics.get("llm", {})
    if "calls" in l:
        add(f"- LLM: {l.get('calls')} Calls, {l.get('calls_failed')} failed, "
            f"{l.get('total_tokens')} tokens (Quelle: {l.get('source')})")
    elif "unavailable" in l:
        add(f"- LLM: {l.get('unavailable')}")
    q = metrics.get("search", {})
    if "attempts_by_provider" in q:
        add(f"- Suche (attempts je Provider): {q.get('attempts_by_provider')}")
    if "duplicates_by_provider" in q:
        add(f"- Suche (duplicates je Provider): {q.get('duplicates_by_provider')}")
    sess = metrics.get("session", {})
    add(f"- Lauf: {sess.get('cycle_count_total')} Zyklen, "
        f"{sess.get('duration_seconds')} s Dauer")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministische Kennzahlen einer abgeschlossenen Forschungs-DB")
    parser.add_argument("db", type=str)
    parser.add_argument("--out", type=str, default=None,
                        help="Pfad für das JSON-Artefakt; default: data/baseline/…")
    parser.add_argument("--label", type=str, default="")
    parser.add_argument("--usage-db", type=str, default=None,
                        help="Globale LLM-Usage-DB, wenn die Topic-DB leer ist")
    args = parser.parse_args()

    usage_db = args.usage_db
    if not usage_db:
        default_usage = Path("data/research-usage.db")
        if default_usage.exists():
            usage_db = str(default_usage)

    metrics = compute_metrics(args.db, usage_db_path=usage_db)
    if args.label:
        metrics["label"] = args.label

    out_path = args.out
    if not out_path:
        stem = Path(args.db).stem
        Path("data/baseline").mkdir(parents=True, exist_ok=True)
        out_path = str(Path("data/baseline") / f"{stem}-metrics.json")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(to_json(metrics), encoding="utf-8")

    md_path = Path(out_path).with_suffix(".md")
    md_path.write_text(write_markdown(metrics), encoding="utf-8")

    print(write_markdown(metrics))
    print(f"[metrics] JSON: {out_path} / Markdown: {md_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
