#!/usr/bin/env python3
"""
Standalone Dashboard Server - No external dependencies.
Uses only Python stdlib: http.server, sqlite3, json.
Reads directly from research.db to serve the Knowledge Graph dashboard.
"""

import json
import sqlite3
import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import urlparse

# Resolve paths relative to this script's location
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_DIR = SCRIPT_DIR.parent.parent  # AIResearch root
TEMPLATE_PATH = SCRIPT_DIR / "templates" / "index.html"


def _topic_databases():
    """Per-topic databases in <root>/data, newest first.

    With one database per topic (DATABASE_PER_TOPIC=1) the base research.db is
    not where the latest run wrote, so a read-only viewer that only looked there
    would show a stale corpus.
    """
    data_dir = PROJECT_DIR / "data"
    if not data_dir.exists():
        return []
    files = [
        p for p in data_dir.glob("research-*.db")
        if not p.name.endswith("-usage.db")
    ]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def _resolve_db_path():
    """Resolve the research database path.

    Same convention as research_agent/config.py: relative DATABASE_URL values
    are anchored at the project root; default is <root>/data/research.db.
    With one database per topic the most recently written one is shown, and the
    legacy <root>/research_agent/data/research.db is the last resort.
    """
    env = os.environ.get("DATABASE_URL")
    if env and env != ":memory:":
        p = Path(env)
        return p if p.is_absolute() else PROJECT_DIR / p
    default = PROJECT_DIR / "data" / "research.db"
    flag = (os.environ.get("DATABASE_PER_TOPIC", "") or "1").strip().lower()
    per_topic = flag not in ("0", "false", "no", "off")
    if per_topic:
        candidates = [p for p in ([default] + _topic_databases()) if p.exists()]
        if candidates:
            return max(candidates, key=lambda p: p.stat().st_mtime)
    if default.exists():
        return default
    legacy = PROJECT_DIR / "research_agent" / "data" / "research.db"
    return legacy if legacy.exists() else default


def _resolve_usage_db_path():
    """The shared token ledger, not the topic database.

    Accounting is deliberately one file across topics ("tokens today" is a
    question about time), so the topic database holds zero usage rows while the
    run records every call - the panel read 0 tokens for a running agent. Falls
    back to the newest *-usage.db, then to the research database.
    """
    try:
        from research_agent.config import get_config
        configured = (getattr(get_config(), "usage_database_url", "") or "").strip()
    except Exception:
        configured = ""
    if configured and configured != ":memory:":
        path = Path(configured)
        if not path.is_absolute():
            path = PROJECT_DIR / path
        if path.exists():
            return path
    data_dir = PROJECT_DIR / "data"
    if data_dir.exists():
        ledgers = sorted(
            (p for p in data_dir.glob("*-usage.db")), key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if ledgers:
            return ledgers[0]
    return DB_PATH


DB_PATH = _resolve_db_path()
USAGE_DB_PATH = _resolve_usage_db_path()

HOST = os.environ.get("DASHBOARD_HOST", "0.0.0.0")
PORT = int(os.environ.get("DASHBOARD_PORT", "8080"))


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def get_db():
    """Get a new database connection (thread-safe)."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def query_all(sql, params=()):
    """Execute query and return list of dicts."""
    conn = get_db()
    try:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    except Exception as e:
        print(f"DB error: {e}")
        return []
    finally:
        conn.close()


def query_one(sql, params=()):
    """Execute query and return single dict or None."""
    conn = get_db()
    try:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"DB error: {e}")
        return None
    finally:
        conn.close()


# === API HANDLERS ===

def api_status():
    """Get current research status."""
    session = query_one(
        "SELECT * FROM research_sessions ORDER BY id DESC LIMIT 1"
    )
    stats = api_stats()
    open_qs = query_all(
        "SELECT * FROM research_questions WHERE status='open' ORDER BY priority_score DESC LIMIT 5"
    )
    active_hyps = api_hypotheses()
    contradictions = api_contradictions()

    phase = "idle"
    topic = ""
    current_question = ""
    if session:
        phase = session.get("status", "idle") or "idle"
        topic = session.get("topic", "") or ""

    if open_qs:
        current_question = open_qs[0].get("question", "")

    return {
        "phase": phase,
        "topic": topic,
        "cycle_count": stats.get("total_cycles", 0),
        "current_question": current_question,
        "current_task": "--",
        "last_finding": "",
        "stats": stats,
        "active_hypotheses": active_hyps,
        "open_questions": open_qs,
        "recent_sources": query_all(
            "SELECT * FROM sources ORDER BY id DESC LIMIT 20"
        ),
        "contradictions": contradictions,
    }


def api_stats():
    """Get database statistics."""
    sources = query_one("SELECT COUNT(*) as c FROM sources")
    facts = query_one("SELECT COUNT(*) as c FROM facts")
    hyps = query_one("SELECT COUNT(*) as c FROM hypotheses WHERE status != 'rejected'")
    open_q = query_one(
        "SELECT COUNT(*) as c FROM research_questions WHERE status='open'"
    )
    contras = query_one(
        "SELECT COUNT(*) as c FROM contradictions WHERE resolved=0"
    )
    sessions = query_one(
        "SELECT SUM(cycle_count) as c FROM research_sessions"
    )
    nodes = query_one("SELECT COUNT(*) as c FROM knowledge_nodes")
    full_texts = query_one(
        "SELECT COUNT(*) as c FROM source_texts WHERE kind <> 'abstract' AND chars >= 3000"
    )
    quotes = query_one(
        "SELECT COUNT(*) as c FROM facts WHERE quote_start >= 0 AND quote <> ''"
    )

    return {
        "sources": sources["c"] if sources else 0,
        "facts": facts["c"] if facts else 0,
        "hypotheses": hyps["c"] if hyps else 0,
        "open_questions": open_q["c"] if open_q else 0,
        "contradictions": contras["c"] if contras else 0,
        "total_cycles": sessions["c"] if sessions and sessions["c"] else 0,
        "knowledge_nodes": nodes["c"] if nodes else 0,
        "fulltext": {
            "sources_with_fulltext": full_texts["c"] if full_texts else 0,
            "facts_with_quote": quotes["c"] if quotes else 0,
        },
    }


def api_hypotheses():
    """Get active hypotheses."""
    return query_all(
        "SELECT * FROM hypotheses WHERE status != 'rejected' ORDER BY confidence DESC LIMIT 50"
    )


def api_questions():
    """Get open research questions."""
    return query_all(
        "SELECT * FROM research_questions WHERE status='open' ORDER BY priority_score DESC LIMIT 50"
    )


def api_sources():
    """Get all sources."""
    return query_all("SELECT * FROM sources ORDER BY id DESC LIMIT 50")


def api_journal():
    """Get journal entries."""
    return query_all(
        "SELECT * FROM journal_entries ORDER BY id DESC LIMIT 30"
    )


def api_contradictions():
    """Get unresolved contradictions."""
    return query_all(
        "SELECT * FROM contradictions WHERE resolved=0 ORDER BY id DESC LIMIT 30"
    )


def api_rejected():
    """Get rejected hypotheses."""
    return query_all(
        "SELECT * FROM hypotheses WHERE status='rejected' ORDER BY id DESC LIMIT 30"
    )


def api_hypothesis_detail(hyp_id):
    """Get full hypothesis detail with evidence and linked sources."""
    hyp = query_one("SELECT * FROM hypotheses WHERE id=?", (hyp_id,))
    if not hyp:
        return {"error": "Hypothesis not found"}

    # Parse JSON fields
    for field in ('supporting_evidence', 'contradicting_evidence', 'alternative_explanations', 'predictions', 'falsification_conditions'):
        try:
            hyp[field] = json.loads(hyp.get(field) or '[]')
        except (json.JSONDecodeError, TypeError):
            hyp[field] = []

    # Get linked evidence records from evidence table
    evidence_records = query_all(
        "SELECT e.*, s.title as source_title, s.url as source_url, s.source_type, s.credibility "
        "FROM evidence e LEFT JOIN sources s ON e.source_id = s.id "
        "WHERE e.hypothesis_id=? ORDER BY e.strength DESC",
        (hyp_id,)
    )

    # Get related contradictions
    contradictions = query_all(
        "SELECT * FROM contradictions WHERE claim_a LIKE ? OR claim_b LIKE ?",
        (f'%{hyp["claim"][:50]}%', f'%{hyp["claim"][:50]}%')
    )

    # Get linked source details from knowledge_edges
    linked_sources = []
    try:
        raw_edges = query_all(
            "SELECT ke.*, s.title, s.url, s.source_type, s.credibility, s.summary "
            "FROM knowledge_edges ke "
            "LEFT JOIN sources s ON ke.target_node_id = s.id "
            "WHERE ke.source_node_id=? AND s.id IS NOT NULL",
            (hyp_id,)
        )
        linked_sources = raw_edges
    except Exception:
        pass

    # Get related hypotheses (same topic or sharing evidence sources)
    related_hyps = []
    try:
        # Find hypotheses that share sources via evidence table
        related_hyps = query_all(
            "SELECT DISTINCT h2.id, h2.claim, h2.confidence, h2.status "
            "FROM evidence e1 "
            "JOIN evidence e2 ON e1.source_id = e2.source_id AND e2.hypothesis_id != e1.hypothesis_id "
            "JOIN hypotheses h2 ON e2.hypothesis_id = h2.id "
            "WHERE e1.hypothesis_id=? AND h2.status != 'rejected' LIMIT 10",
            (hyp_id,)
        )
    except Exception:
        pass

    hyp['evidence_records'] = evidence_records
    hyp['contradictions'] = contradictions
    hyp['linked_sources'] = linked_sources
    hyp['related_hypotheses'] = related_hyps
    return hyp


def api_sessions():
    """Get all research sessions."""
    return query_all("SELECT * FROM research_sessions ORDER BY start_time DESC LIMIT 50")


def api_source_analytics():
    """Get source type distribution and credibility stats."""
    # Source type counts
    type_counts = query_all(
        "SELECT source_type, COUNT(*) as count, AVG(credibility) as avg_credibility "
        "FROM sources GROUP BY source_type ORDER BY count DESC"
    )
    # Total sources and average credibility
    totals = query_one("SELECT COUNT(*) as total, AVG(credibility) as avg_cred FROM sources")
    # Credibility distribution (buckets)
    cred_dist = query_all(
        "SELECT CASE "
        "WHEN credibility >= 0.8 THEN 'High (0.8+)' "
        "WHEN credibility >= 0.6 THEN 'Medium (0.6-0.8)' "
        "WHEN credibility >= 0.4 THEN 'Low (0.4-0.6)' "
        "ELSE 'Very Low (<0.4)' END as bucket, "
        "COUNT(*) as count FROM sources GROUP BY bucket ORDER BY bucket DESC"
    )
    # Sources added per day (last 30 days)
    daily_sources = query_all(
        "SELECT DATE(date_added) as day, COUNT(*) as count "
        "FROM sources WHERE date_added >= DATE('now', '-30 days') "
        "GROUP BY day ORDER BY day"
    )
    return {
        "type_counts": type_counts,
        "total_sources": totals["total"] if totals else 0,
        "avg_credibility": round(totals["avg_cred"] or 0, 3) if totals else 0,
        "credibility_distribution": cred_dist,
        "daily_sources": daily_sources,
    }


def api_system_health():
    """Get system health: DB size, model info, uptime."""
    import os
    db_path_str = str(DB_PATH)
    db_size = 0
    if os.path.exists(db_path_str):
        db_size = os.path.getsize(db_path_str)

    # Table row counts
    tables = {}
    for t in ['sources', 'facts', 'hypotheses', 'evidence', 'research_questions',
              'journal_entries', 'contradictions', 'knowledge_nodes', 'knowledge_edges',
              'embeddings', 'research_sessions']:
        try:
            r = query_one(f"SELECT COUNT(*) as c FROM {t}")
            tables[t] = r["c"] if r else 0
        except Exception:
            tables[t] = 0

    return {
        "db_path": db_path_str,
        "db_size_bytes": db_size,
        "db_size_mb": round(db_size / (1024 * 1024), 2),
        "table_counts": tables,
        "server_status": "running",
    }


def api_errors():
    """Get recent errors from the server log."""
    return {"errors": _recent_errors[-50:]}  # Last 50 errors


def api_confidence_history():
    """Get confidence history for trend charts."""
    history = query_all(
        "SELECT hypothesis_id, hypothesis_claim, confidence, cycle_number, reason, timestamp "
        "FROM confidence_snapshots ORDER BY timestamp ASC LIMIT 2000"
    )
    # Group by hypothesis
    by_hypothesis = {}
    for h in history:
        hid = h["hypothesis_id"]
        if hid not in by_hypothesis:
            by_hypothesis[hid] = {
                "id": hid,
                "claim": h["hypothesis_claim"],
                "data": [],
            }
        by_hypothesis[hid]["data"].append({
            "confidence": h["confidence"],
            "cycle": h["cycle_number"],
            "reason": h["reason"],
            "timestamp": h["timestamp"],
        })
    return {"hypotheses": list(by_hypothesis.values())}


def api_llm_stats():
    """Live counters plus the stored per-day totals (which outlive a restart)."""
    try:
        from research_agent.llm.engine import LLMEngine
        stats = LLMEngine.get_stats()
    except Exception:
        stats = {"total_calls": 0, "recent_calls": []}
    try:
        from research_agent.database import Database
        stats["persisted"] = Database(str(USAGE_DB_PATH)).get_llm_usage_summary()
        stats["usage_database"] = str(USAGE_DB_PATH)
    except Exception:
        stats["persisted"] = None
    return stats


# Error log buffer
_recent_errors = []


def _log_error(category: str, message: str, details: str = ""):
    """Log an error to the buffer."""
    import datetime as _dt
    entry = {
        "timestamp": _dt.datetime.utcnow().isoformat() + "Z",
        "category": category,
        "message": message,
        "details": details[:500],
    }
    _recent_errors.append(entry)
    if len(_recent_errors) > 200:
        _recent_errors.pop(0)


def api_knowledge_graph():
    """Build knowledge graph data for D3.js visualization.
    
    Edge types generated:
    - supports: evidence supports hypothesis -> source
    - contradicts: evidence contradicts hypothesis -> source
    - related_to: two hypotheses share common evidence sources
    - derived_from: fact -> source
    - neutral: neutral evidence -> source
    """
    # Get knowledge nodes
    nodes_raw = query_all("SELECT * FROM knowledge_nodes LIMIT 200")
    nodes = []
    node_ids = set()
    for n in nodes_raw:
        node_ids.add(n["id"])
        nodes.append({
            "id": n["id"],
            "type": n["node_type"],
            "label": (n.get("label", "") or "")[:80],
            "content": (n.get("content", "") or "")[:200],
        })

    # Add active hypotheses as nodes
    hyps = query_all(
        "SELECT * FROM hypotheses WHERE status != 'rejected' LIMIT 50"
    )
    for h in hyps:
        if h["id"] not in node_ids:
            nodes.append({
                "id": h["id"],
                "type": "hypothesis",
                "label": (h.get("claim", "") or "")[:80],
                "content": h.get("claim", ""),
                "confidence": h.get("confidence", 0),
                "status": h.get("status", "proposed"),
            })
            node_ids.add(h["id"])

    # Add sources as nodes (top 50 by credibility)
    sources = query_all("SELECT * FROM sources ORDER BY credibility DESC LIMIT 50")
    for s in sources:
        if s["id"] not in node_ids:
            nodes.append({
                "id": s["id"],
                "type": "source",
                "label": (s.get("title", "") or "")[:80],
                "content": (s.get("summary", "") or "")[:200],
                "credibility": s.get("credibility", 0.5),
            })
            node_ids.add(s["id"])

    all_edges = []
    seen_edges = set()

    # === EDGES FROM knowledge_edges table ===
    try:
        raw_edges = query_all("SELECT * FROM knowledge_edges LIMIT 500")
        for e in raw_edges:
            src = e.get("source_node_id")
            tgt = e.get("target_node_id")
            key = (src, tgt)
            if (
                key not in seen_edges
                and src in node_ids
                and tgt in node_ids
            ):
                seen_edges.add(key)
                all_edges.append({
                    "source": src,
                    "target": tgt,
                    "relation": e.get("relation", "related"),
                    "weight": e.get("weight", 1),
                })
    except Exception:
        pass

    # === EDGES: Hypothesis <-> Source (supports/contradicts/neutral) ===
    # Get all evidence for active hypotheses
    hyp_evidence = {}
    try:
        all_ev = query_all(
            "SELECT hypothesis_id, source_id, evidence_type, strength "
            "FROM evidence WHERE source_id != '' AND source_id IS NOT NULL LIMIT 500"
        )
        for ev in all_ev:
            hyp_id = ev["hypothesis_id"]
            src_id = ev["source_id"]
            if hyp_id not in hyp_evidence:
                hyp_evidence[hyp_id] = []
            hyp_evidence[hyp_id].append(ev)
    except Exception:
        pass

    for h in hyps:
        h_id = h["id"]
        if h_id not in hyp_evidence:
            continue
        for ev in hyp_evidence[h_id]:
            src_id = ev["source_id"]
            ev_type = ev["evidence_type"]
            strength = ev.get("strength", 0.5)
            key = (h_id, src_id)
            if (
                src_id in node_ids
                and h_id in node_ids
                and key not in seen_edges
            ):
                seen_edges.add(key)
                all_edges.append({
                    "source": h_id,
                    "target": src_id,
                    "relation": ev_type,  # supports, contradicts, neutral
                    "weight": round(strength * 5) if strength else 1,
                })

    # === EDGES: Hypothesis <-> Hypothesis (related_to via shared sources) ===
    # Build source sets per hypothesis
    hyp_sources = {}
    for h in hyps:
        h_id = h["id"]
        if h_id in hyp_evidence:
            hyp_sources[h_id] = set(ev["source_id"] for ev in hyp_evidence[h_id])
        else:
            hyp_sources[h_id] = set()

    # Find hypotheses that share sources
    hyp_ids = list(hyp_sources.keys())
    for i in range(len(hyp_ids)):
        for j in range(i + 1, len(hyp_ids)):
            h1 = hyp_ids[i]
            h2 = hyp_ids[j]
            shared = hyp_sources[h1] & hyp_sources[h2]
            if len(shared) >= 2:  # Require at least 2 shared sources
                key_fwd = (h1, h2)
                key_bwd = (h2, h1)
                if key_fwd not in seen_edges and key_bwd not in seen_edges:
                    seen_edges.add(key_fwd)
                    # Check if one contradicts and the other supports
                    h1_types = set(ev["evidence_type"] for ev in hyp_evidence.get(h1, []))
                    h2_types = set(ev["evidence_type"] for ev in hyp_evidence.get(h2, []))
                    if "contradicts" in h1_types and "contradicts" in h2_types:
                        relation = "both_contested"
                    elif "supports" in h1_types and "supports" in h2_types:
                        relation = "related_to"
                    else:
                        relation = "related_to"
                    all_edges.append({
                        "source": h1,
                        "target": h2,
                        "relation": relation,
                        "weight": min(len(shared), 10),
                    })

    # === EDGES: Fact -> Source ===
    try:
        facts = query_all("SELECT * FROM facts WHERE source_id IS NOT NULL LIMIT 100")
        for f in facts:
            if f.get("id") in node_ids and f.get("source_id") in node_ids:
                key = (f["id"], f["source_id"])
                if key not in seen_edges:
                    seen_edges.add(key)
                    all_edges.append({
                        "source": f["id"],
                        "target": f["source_id"],
                        "relation": "derived_from",
                        "weight": 1,
                    })
    except Exception:
        pass

    return {"nodes": nodes, "edges": all_edges}


# === HTTP HANDLER ===

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        routes = {
            "/": self._serve_html,
            "/index.html": self._serve_html,
            "/api/status": lambda: self._json(api_status()),
            "/api/stats": lambda: self._json(api_stats()),
            "/api/hypotheses": lambda: self._json(api_hypotheses()),
            "/api/questions": lambda: self._json(api_questions()),
            "/api/sources": lambda: self._json(api_sources()),
            "/api/journal": lambda: self._json(api_journal()),
            "/api/contradictions": lambda: self._json(api_contradictions()),
            "/api/rejected": lambda: self._json(api_rejected()),
            "/api/graph": lambda: self._json(api_knowledge_graph()),
            "/api/sessions": lambda: self._json(api_sessions()),
            "/api/source-analytics": lambda: self._json(api_source_analytics()),
            "/api/system-health": lambda: self._json(api_system_health()),
            "/api/errors": lambda: self._json(api_errors()),
            "/api/confidence-history": lambda: self._json(api_confidence_history()),
            "/api/llm-stats": lambda: self._json(api_llm_stats()),
            "/api/health": lambda: self._json({"status": "ok"}),
        }

        handler = routes.get(path)
        if handler:
            handler()
        elif path.startswith("/api/hypothesis/"):
            hyp_id = path.split("/api/hypothesis/", 1)[1]
            self._json(api_hypothesis_detail(hyp_id))
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b""

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            data = {}

        if path == "/api/start":
            self._json({"status": "idle", "message": "Dashboard is read-only (standalone mode). Use the full agent to start research."})
        elif path == "/api/pause":
            self._json({"status": "idle", "message": "Dashboard is read-only (standalone mode)."})
        elif path == "/api/resume":
            self._json({"status": "idle", "message": "Dashboard is read-only (standalone mode)."})
        elif path == "/api/stop":
            self._json({"status": "idle", "message": "Dashboard is read-only (standalone mode)."})
        elif path == "/api/dataset":
            self._json({"status": "ok", "message": "Export available via full agent mode."})
        elif path == "/api/finetune":
            self._json({"status": "ok", "message": "Fine-tune export available via full agent mode."})
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _serve_html(self):
        if TEMPLATE_PATH.exists():
            content = TEMPLATE_PATH.read_text(encoding="utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            self.send_error(404, "Dashboard HTML not found")

    def _json(self, data):
        body = json.dumps(data, default=str, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[Dashboard] {args[0]}" if args else "")


def main():
    print(f"=" * 60)
    print(f"  Research Agent Dashboard (Standalone)")
    print(f"  Database: {DB_PATH}")
    print(f"  Template: {TEMPLATE_PATH}")
    print(f"  Server:   http://localhost:{PORT}")
    print(f"=" * 60)

    if not DB_PATH.exists():
        print(f"ERROR: Database not found at {DB_PATH}")
        sys.exit(1)
    if not TEMPLATE_PATH.exists():
        print(f"ERROR: Template not found at {TEMPLATE_PATH}")
        sys.exit(1)

    server = ThreadingHTTPServer((HOST, PORT), DashboardHandler)
    print(f"\nDashboard running at http://localhost:{PORT}")
    print(f"   Press Ctrl+C to stop.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
