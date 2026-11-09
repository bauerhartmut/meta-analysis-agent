"""
Dashboard Server - Lightweight HTTP server for monitoring and controlling the research agent.
Uses Python's built-in http.server with async API endpoints.
"""

import json
import asyncio
import logging
import threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from typing import Optional


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
from urllib.parse import urlparse, parse_qs

from .api_manifest import capabilities as _api_capabilities

logger = logging.getLogger(__name__)


class _AsyncRunner:
    """Runs coroutines on ONE dedicated event loop in a daemon thread.

    aiohttp sessions, asyncio Events/Locks and the LLM engine's resources are
    all bound to the event loop they were created/used on. Spawning a fresh
    ``asyncio.new_event_loop()`` per HTTP request (as the old handler did for
    start/pause/resume/stop) means orchestrator control coroutines ran on
    DIFFERENT loops from the long-running research loop, which crashes with
    ``RuntimeError: Task got Future attached to a different loop``. Routing all
    control calls through this single worker loop fixes that without touching
    the orchestrator itself.
    """

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._thread_main, daemon=True, name="dashboard-async-loop"
        )
        self._thread.start()

    def _thread_main(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def submit(self, coro):
        """Schedule a coroutine on the shared loop; return a concurrent Future."""
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def stop(self):
        if self._loop.is_running():
            self._loop.call_soon_threadsafe(self._loop.stop)


class DashboardHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for the dashboard."""

    orchestrator = None  # Set by DashboardServer
    _runner: Optional["_AsyncRunner"] = None  # Set by DashboardServer

    def _get_runner(self):
        return DashboardHandler._runner

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._serve_html()
        elif path == "/style.css":
            self._serve_static("style.css", "text/css; charset=utf-8")
        elif path == "/app.js":
            self._serve_static("app.js", "application/javascript; charset=utf-8")
        elif path == "/api/status":
            self._json_response(self._get_status())
        elif path == "/api/stats":
            self._json_response(self._get_stats())
        elif path == "/api/coverage":
            self._json_response(self._get_coverage())
        elif path == "/api/metaanalysis":
            payload = self._get_metaanalysis()
            # A broken target definition must not look like an empty
            # analysis: 200 with groups={} is indistinguishable from "no
            # studies", so the failure goes out as 500 and stays visible in
            # monitoring and in the panel.
            self._json_response(
                payload, status=500 if payload.get("error") else 200)
        elif path == "/api/capabilities":
            # Eine Quelle der Uhr (Claude-Vorschlag 9): das UI fragt die
            # Endpunkt-Sichtbarkeit einmal, statt 404 als Rätsel zu raten.
            self._json_response(_api_capabilities("live"))
        elif path == "/api/hypotheses":
            self._json_response(self._get_hypotheses())
        elif path.startswith("/api/hypothesis/"):
            # Contract (Vorschlag 9): dieselbe Detail-Route wie im Standalone
            # — der Contract-Test hindert das Wiederauftauchen des Loches.
            hyp_id = path.split("/api/hypothesis/", 1)[1]
            self._json_response(self._get_hypothesis_detail(hyp_id))
        elif path == "/api/questions":
            self._json_response(self._get_questions())
        elif path == "/api/sources":
            self._json_response(self._get_sources())
        elif path == "/api/journal":
            self._json_response(self._get_journal())
        elif path == "/api/contradictions":
            self._json_response(self._get_contradictions())
        elif path == "/api/rejected":
            self._json_response(self._get_rejected_hypotheses())
        elif path == "/api/graph":
            self._json_response(self._get_knowledge_graph())
        elif path == "/api/dataset":
            self._json_response(self._export_dataset())
        elif path == "/api/finetune":
            self._json_response(self._export_finetune())
        elif path == "/api/parallel-stats":
            self._json_response(self._get_parallel_stats())
        elif path == "/api/sessions":
            self._json_response(self._get_sessions())
        elif path == "/api/source-analytics":
            self._json_response(self._get_source_analytics())
        elif path == "/api/system-health":
            self._json_response(self._get_system_health())
        elif path == "/api/errors":
            self._json_response(self._get_errors())
        elif path == "/api/confidence-history":
            self._json_response(self._get_confidence_history())
        elif path == "/api/llm-stats":
            self._json_response(self._get_llm_stats())
        elif path == "/api/health":
            self._json_response({"status": "ok"})
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
            self._handle_start(data)
        elif path == "/api/pause":
            self._handle_pause()
        elif path == "/api/resume":
            self._handle_resume()
        elif path == "/api/stop":
            self._handle_stop()
        else:
            self.send_error(404)

    def _serve_html(self):
        html_path = Path(__file__).parent / "templates" / "index.html"
        if html_path.exists():
            content = html_path.read_text(encoding="utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            # Ohne cachen: die Seite reflektiert den aktiven Agent-Zustand.
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            self.send_error(404, "Dashboard HTML not found")

    def _serve_static(self, name, content_type):
        """Statische Frontend-Dateien mit moderatem Cache (HTML/CSS/JS
        getrennt)."""
        p = Path(__file__).parent / "templates" / name
        if not p.exists():
            self.send_error(404, f"{name} not found")
            return
        content = p.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "max-age=300")
        self.end_headers()
        self.wfile.write(content)

    def _json_response(self, data, status: int = 200):
        body = json.dumps(data, default=str, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _get_status(self):
        if self.orchestrator:
            return self.orchestrator.get_status()
        return {"phase": "idle", "topic": "", "error": "Orchestrator not initialized"}

    def _get_stats(self):
        if self.orchestrator:
            return self.orchestrator.db.get_stats()
        return {}

    def _get_coverage(self):
        """Fulltext-coverage numbers from the coverage manager (read-only)."""
        if not self.orchestrator:
            return {}
        try:
            from ..coverage.manager import CoverageManager

            manager = CoverageManager(self.orchestrator.db.db_path)
            return manager.coverage_stats()
        except Exception as e:
            return {"error": str(e), "identified": 0}

    def _get_metaanalysis(self):
        """Gepoolte Metaanalyse aus den gespeicherten Effektzeilen (read-only).

        Reuses the same deterministic pipeline as the report's
        ``## Metaanalyse`` section: build_analysis() over study_effects,
        PRISMA counts over screening decisions. One built, never fetched -
        the JSON mirrors the report numbers, so dashboard and report cannot
        drift apart.
        """
        empty = {"groups": {}, "excluded": [], "off_target": [],
                 "prisma": {}, "effect_rows": 0, "usable": 0}
        if not self.orchestrator:
            return empty
        db = self.orchestrator.db
        topic = getattr(self.orchestrator, "current_topic", "") or ""
        try:
            from ..meta import pooling as meta_pooling
            from ..meta import screening as meta_screening
            from ..meta import grade as meta_grade
            from ..meta import targets as meta_targets
            from ..report import _meta_rows

            rows = _meta_rows(db)
            targets = None
            labels = None
            try:
                targets = meta_targets.load_targets(db, topic)
                if targets:
                    labels = meta_targets.target_labels(targets)
            except Exception as e:
                # A broken aim changes which rows are grouped, so it is not a
                # side note like a missing PRISMA count: swallowing it here
                # would render "no studies" for a defect. The caller turns
                # this into 500.
                logger.warning(f"Could not load review targets: {e}")
                raise
            analysis = meta_pooling.build_analysis(
                rows, outcomes=labels, targets=targets
            )
            try:
                prisma = meta_screening.prisma_counts(db, topic)
            except Exception as e:
                logger.debug(f"Could not build PRISMA counts: {e}")
                prisma = {}
            rob_assessments: Dict[str, str] = {}
            rob_records = []
            try:
                rob_records = db.get_all_bias_assessments() or []
                for row in rob_records:
                    if (row.get("source_id") and row.get("overall")
                            and not int(row.get("disputed") or 0)):
                        rob_assessments[row["source_id"]] = str(row["overall"])
            except Exception as e:
                logger.debug(f"Could not load bias assessments: {e}")
            grade = {}
            try:
                for key, g in (analysis.get("groups") or {}).items():
                    if g.get("pooled") is None:
                        continue
                    try:
                        grade[key] = meta_grade.grade_group(g, rob_assessments)
                    except Exception as e:
                        logger.debug(f"GRADE failed for {key}: {e}")
            except Exception as e:
                logger.debug(f"Could not grade groups: {e}")
            return {
                "topic": topic,
                "effect_rows": len(rows),
                "usable": analysis.get("usable", 0),
                "groups": analysis.get("groups", {}),
                "excluded": analysis.get("excluded", []),
                "off_target": analysis.get("off_target", []),
                "prisma": prisma,
                "grade": grade,
                "risk_of_bias": rob_records,
            }
        except Exception as e:
            return dict(empty, error=str(e))

    def _get_parallel_stats(self):
        if self.orchestrator:
            return self.orchestrator.parallel_stats
        return {"active_tasks": 0, "total_tasks_run": 0, "phase_timings": {}, "current_phase_tasks": []}

    def _get_sessions(self):
        if self.orchestrator:
            return self.orchestrator.db.get_all_sessions(limit=50)
        return []

    def _get_source_analytics(self):
        if not self.orchestrator:
            return {}
        db = self.orchestrator.db
        # Source type counts
        type_counts = db._get_all(
            "sources",
            where="",
            order="",
        )
        # Aggregate by source_type in Python
        from collections import Counter
        type_counter = Counter(s.get("source_type", "unknown") for s in type_counts)
        type_counts_agg = [
            {"source_type": t, "count": c} for t, c in type_counter.most_common()
        ]
        # Average credibility
        creds = [s.get("credibility", 0.5) for s in type_counts if s.get("credibility") is not None]
        avg_cred = sum(creds) / len(creds) if creds else 0
        # Credibility buckets
        cred_buckets = {"High (0.8+)": 0, "Medium (0.6-0.8)": 0, "Low (0.4-0.6)": 0, "Very Low (<0.4)": 0}
        for c in creds:
            if c >= 0.8: cred_buckets["High (0.8+)"] += 1
            elif c >= 0.6: cred_buckets["Medium (0.6-0.8)"] += 1
            elif c >= 0.4: cred_buckets["Low (0.4-0.6)"] += 1
            else: cred_buckets["Very Low (<0.4)"] += 1
        cred_dist = [{"bucket": k, "count": v} for k, v in cred_buckets.items() if v > 0]
        return {
            "type_counts": type_counts_agg,
            "total_sources": len(type_counts),
            "avg_credibility": round(avg_cred, 3),
            "credibility_distribution": cred_dist,
        }

    def _get_system_health(self):
        import os
        if not self.orchestrator:
            return {}
        db = self.orchestrator.db
        db_path_str = db.db_path
        db_size = 0
        if os.path.exists(db_path_str):
            db_size = os.path.getsize(db_path_str)
        tables = {}
        for t in ['sources', 'facts', 'hypotheses', 'evidence', 'research_questions',
                  'journal_entries', 'contradictions', 'knowledge_nodes', 'knowledge_edges',
                  'embeddings', 'research_sessions']:
            try:
                tables[t] = db._count(t)
            except Exception:
                tables[t] = 0
        return {
            "db_path": db_path_str,
            "db_size_bytes": db_size,
            "db_size_mb": round(db_size / (1024 * 1024), 2),
            "table_counts": tables,
            "server_status": "running",
            "running": self.orchestrator.running,
            "paused": self.orchestrator.paused,
        }

    def _get_errors(self):
        # For the main server, return empty for now (errors are in orchestrator logs)
        return {"errors": []}

    def _get_llm_stats(self):
        """Live counters from this process plus the stored per-day totals.

        The in-memory counters reset when the agent restarts; the database rows
        are what make today's spend answerable afterwards.
        """
        try:
            from ..llm.engine import LLMEngine
            stats = LLMEngine.get_stats()
        except Exception:
            stats = {"total_calls": 0, "recent_calls": []}
        stats["persisted"] = None
        try:
            if self.orchestrator is not None:
                # Accounting lives in the shared usage database when each topic
                # has its own corpus (one file per topic must not split "tokens
                # today" into one answer per topic).
                usage_db = getattr(self.orchestrator, "usage_db", None) \
                    or self.orchestrator.db
                stats["persisted"] = usage_db.get_llm_usage_summary()
        except Exception as exc:  # noqa: BLE001 - the panel must still render
            logger.debug(f"Could not load stored token usage: {exc}")
            stats["persisted"] = None
        return stats

    def _get_confidence_history(self):
        if not self.orchestrator:
            return {"hypotheses": []}
        db = self.orchestrator.db
        history = db.get_all_confidence_history(limit=2000)
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

    def _get_hypotheses(self):
        if self.orchestrator:
            return self.orchestrator.db.get_hypotheses(limit=50)
        return []

    def _get_hypothesis_detail(self, hyp_id: str):
        """Detail einer Hypothese inkl. Evidence (Contract: in BEIDEN Servern).

        Der Standonly bietet dieselbe Route (api_hypothesis_detail); der
        Live-Server liest ueber die Orchestrator-DB statt direkt.
        """
        if not self.orchestrator:
            return {"error": "Hypothesis detail needs the live orchestrator"}
        db = self.orchestrator.db
        try:
            hyp = db.get_hypothesis(hyp_id)
        except Exception as e:
            return {"error": f"Hypothesis read failed: {e}"}
        if not hyp:
            return {"error": "Hypothesis not found"}
        for field in ("supporting_evidence", "contradicting_evidence",
                      "alternative_explanations", "predictions",
                      "falsification_conditions"):
            try:
                hyp[field] = json.loads(hyp.get(field) or "[]")
            except (json.JSONDecodeError, TypeError):
                hyp[field] = []
        try:
            hyp["evidence_records"] = db.get_evidence_for_hypothesis(hyp_id)
        except Exception:
            hyp["evidence_records"] = []
        return hyp

    def _get_questions(self):
        if self.orchestrator:
            return self.orchestrator.db.get_open_questions(limit=50)
        return []

    def _get_sources(self):
        if self.orchestrator:
            return self.orchestrator.db.get_all_sources(limit=50)
        return []

    def _get_journal(self):
        if self.orchestrator:
            return self.orchestrator.db.get_journal_entries(limit=30)
        return []

    def _get_contradictions(self):
        if self.orchestrator:
            return self.orchestrator.db.get_unresolved_contradictions()
        return []

    def _get_rejected_hypotheses(self):
        if self.orchestrator:
            return self.orchestrator.db.get_hypotheses(status="rejected", limit=30)
        return []

    # The graph is the whole memory (348 nodes), and the force layout gets slow
    # with hundreds of unconnected circles. Only nodes that carry a relation are
    # drawn, and sources are context: the ones supporting the most hypotheses,
    # capped so the canvas does not turn into a source cloud.
    _GRAPH_MAX_SOURCES = 40

    def _get_knowledge_graph(self):
        if not self.orchestrator:
            return {"nodes": [], "edges": []}
        db = self.orchestrator.db

        nodes_by_id = {}
        nodes_raw = db.get_knowledge_nodes(limit=2000)
        for n in nodes_raw:
            nodes_by_id[n["id"]] = {
                "id": n["id"],
                "type": n["node_type"],
                "label": (n["label"] or "")[:80],
                "content": (n.get("content", "") or "")[:200],
            }

        # Active hypotheses that are not already a graph node. Graph nodes carry
        # their own ids, so the claim text decides - otherwise every hypothesis
        # would appear twice (once as its graph node, once by its own id).
        graph_claims = {(n.get("content") or "").strip() for n in nodes_raw}
        node_by_claim = {(n.get("content") or "").strip(): n["id"]
                         for n in nodes_raw if n["node_type"] == "hypothesis"}
        hyps = db.get_active_hypotheses()
        for h in hyps:
            claim = (h.get("claim") or "").strip()
            if claim in graph_claims or h["id"] in nodes_by_id:
                continue
            nodes_by_id[h["id"]] = {
                "id": h["id"],
                "type": "hypothesis",
                "label": claim[:80],
                "content": claim,
                "confidence": h.get("confidence", 0),
                "status": h.get("status", "proposed"),
            }

        # All graph edges in one query (this used to be one query per node).
        edges, seen_edges = [], set()
        for e in db._get_all("knowledge_edges"):
            src_id, dst_id = e["source_node_id"], e["target_node_id"]
            if src_id in nodes_by_id and dst_id in nodes_by_id and (src_id, dst_id) not in seen_edges:
                seen_edges.add((src_id, dst_id))
                edges.append({
                    "source": src_id,
                    "target": dst_id,
                    "relation": e.get("relation", "related_to"),
                    "weight": e.get("weight", 1),
                })

        # Sources: only those with evidence for a drawn hypothesis, best linked first.
        hypothesis_node = {}
        for h in hyps:
            claim = (h.get("claim") or "").strip()
            hypothesis_node[h["id"]] = h["id"] if h["id"] in nodes_by_id else node_by_claim.get(claim)
        links_by_source = {}
        for ev in db._get_all("evidence"):
            if not ev.get("content"):
                continue
            node_id = hypothesis_node.get(ev.get("hypothesis_id", ""))
            source_id = ev.get("source_id", "")
            if node_id and source_id:
                links_by_source.setdefault(source_id, []).append(
                    (node_id, ev.get("evidence_type") or "evidence")
                )
        selected = sorted(links_by_source.items(), key=lambda kv: -len(kv[1]))
        for source_id, links in selected[:self._GRAPH_MAX_SOURCES]:
            if source_id in nodes_by_id:
                continue
            source = db.get_source(source_id)
            if not source:
                continue
            nodes_by_id[source_id] = {
                "id": source_id,
                "type": "source",
                "label": (source.get("title") or "")[:80],
                "content": (source.get("summary") or "")[:200],
            }
            for node_id, relation in links:
                key = (node_id, source_id)
                if key in seen_edges:
                    continue
                seen_edges.add(key)
                edges.append({"source": node_id, "target": source_id,
                              "relation": relation, "weight": 1})

        connected = {e["source"] for e in edges} | {e["target"] for e in edges}
        nodes = [n for node_id, n in nodes_by_id.items() if node_id in connected]
        return {"nodes": nodes, "edges": edges}

    def _export_dataset(self):
        if self.orchestrator:
            from ..dataset import DatasetExporter
            exporter = DatasetExporter(self.orchestrator.db)
            files = exporter.export_full_dataset()
            return {"status": "ok", "files": files}
        return {"error": "Orchestrator not available"}

    def _export_finetune(self):
        if self.orchestrator:
            from ..dataset import DatasetExporter
            exporter = DatasetExporter(self.orchestrator.db)
            path = exporter.export_for_finetuning()
            return {"status": "ok", "file": path}
        return {"error": "Orchestrator not available"}

    def _handle_start(self, data):
        topic = data.get("topic", "")
        if not topic:
            self._json_response({"error": "No topic provided"})
            return

        runner = self._get_runner()
        if self.orchestrator and not self.orchestrator.running and runner:
            # Fire-and-forget on the shared loop; orchestrator.start() runs its
            # own long-lived cycle loop there.
            runner.submit(self.orchestrator.start(topic))
            self._json_response({"status": "started", "topic": topic})
        else:
            self._json_response({"error": "Already running or orchestrator not available"})

    def _run_on_shared_loop(self, coro):
        """Run an orchestrator control coroutine on the shared loop and wait."""
        runner = self._get_runner()
        if not runner:
            return False
        future = runner.submit(coro)
        try:
            future.result(timeout=30)
        except Exception as e:
            logger.error(f"Dashboard async control failed: {e}")
            return False
        return True

    def _handle_pause(self):
        if self.orchestrator and self.orchestrator.running:
            ok = self._run_on_shared_loop(self.orchestrator.pause())
            self._json_response({"status": "paused" if ok else "error"})
        else:
            self._json_response({"error": "Not running"})

    def _handle_resume(self):
        if self.orchestrator and self.orchestrator.paused:
            ok = self._run_on_shared_loop(self.orchestrator.resume())
            self._json_response({"status": "resumed" if ok else "error"})
        else:
            self._json_response({"error": "Not paused"})

    def _handle_stop(self):
        if self.orchestrator and self.orchestrator.running:
            ok = self._run_on_shared_loop(self.orchestrator.stop())
            self._json_response({"status": "stopped" if ok else "error"})
        else:
            self._json_response({"error": "Not running"})

    def log_message(self, format, *args):
        logger.debug(f"Dashboard: {format % args}")


class DashboardServer:
    """Manages the dashboard HTTP server."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None

    def start(self, orchestrator=None):
        """Start the dashboard server in a background thread."""
        DashboardHandler.orchestrator = orchestrator
        DashboardHandler._runner = _AsyncRunner()
        self.server = ThreadingHTTPServer((self.host, self.port), DashboardHandler)
        if self.host not in ("127.0.0.1", "localhost"):
            logger.warning(
                "Dashboard lauscht auf %s:%s ohne Authentifizierung (Start/Stop "
                "steuerbar von jedem Geraet im Netz). Nur bewusst starten.",
                self.host, self.port,
            )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        logger.info(f"Dashboard running at http://{self.host}:{self.port}")

    def stop(self):
        """Stop the dashboard server."""
        if self.server:
            self.server.shutdown()
            logger.info("Dashboard server stopped")
        runner = DashboardHandler._runner
        if runner:
            runner.stop()
            DashboardHandler._runner = None
