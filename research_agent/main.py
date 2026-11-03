"""
Main entry point for the Autonomous Research Agent.
Starts the dashboard and optionally begins research.
"""

import sys
import asyncio
import logging
import os
import signal
import argparse
from pathlib import Path

from .config import get_config, Config
from .orchestrator import ResearchOrchestrator
from .dashboard.server import DashboardServer
from .instance_guard import InstanceLock, dashboard_port_in_use
from .utf8_logging import ensure_utf8, make_utf8_stream_handler


def setup_logging(config: Config):
    """Configure logging (UTF-8-safe so '\u2192' etc. never crash the console)."""
    ensure_utf8()
    log_dir = Path(config.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            make_utf8_stream_handler(sys.stdout),
            logging.FileHandler(config.log_file, encoding="utf-8"),
        ],
    )

    # Suppress noisy loggers
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("aiosignal").setLevel(logging.WARNING)


def chat_model(config: Config) -> str:
    """Name of the model used for chat by the configured backend."""
    if config.llm_backend == "tudagpt":
        return config.tudagpt_model
    return config.ollama_model


def backend_error_hint(config: Config) -> str:
    """Actionable message when the configured LLM backend is unreachable."""
    if config.llm_backend == "tudagpt":
        return (
            f"Cannot reach the TUDaGPT API at {config.tudagpt_api_base}. "
            "Check TUDAGPT_API_KEY and TUDAGPT_MODEL in .env, and make sure this "
            "network can reach the HRZ endpoint (campus network/VPN). "
            "Set LLM_BACKEND=ollama in .env to use the local model instead."
        )
    if config.llm_backend in ("kaggle_api", "pc", "auto"):
        return "No remote LLM backend available (PC server offline, Kaggle unreachable)."
    return f"Cannot connect to Ollama at {config.ollama_host}. Please ensure Ollama is running."


async def run_with_dashboard(args):
    """Run the agent with the web dashboard."""
    config = get_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)

    # One writer per database. Two run.py processes on one corpus look like one
    # busy client to every provider, which is why every query came back 429
    # while two runs shared the quota. The lock is keyed on the database, so
    # parallel work on *different* topics keeps working.
    guard = InstanceLock.for_database(config.database_for_topic(args.topic or ""))
    if not guard.acquire():
        logger.error(
            "Another agent is already running on this database (pid %s, lock %s). "
            "Two runs share the LLM rate limit, the search quota and the token "
            "budget - stop the other one first, or use a different --topic.",
            guard.held_by, guard.path,
        )
        sys.exit(1)
    if dashboard_port_in_use(config.dashboard_host, config.dashboard_port):
        logger.error(
            "Dashboard port %s is already serving something else - the page you "
            "would open belongs to another process. Stop that run, or start this "
            "one with --port <n>.",
            config.dashboard_port,
        )
        guard.release()
        sys.exit(1)

    # One database per topic: the topic given on the command line decides which
    # corpus this process reads and writes (see Config.database_for_topic).
    orchestrator = ResearchOrchestrator(config, topic=args.topic or "")
    dashboard = DashboardServer(config.dashboard_host, config.dashboard_port)
    logger.info(f"Database: {orchestrator.database_path}")

    # Check LLM backend connectivity
    logger.info(f"Checking {config.llm_backend} connection...")
    if not await orchestrator.llm.health_check():
        logger.error(backend_error_hint(config))
        sys.exit(1)

    models = await orchestrator.llm.list_models()
    logger.info(f"Available models: {', '.join(models)}")
    logger.info(f"Using model: {chat_model(config)}")
    logger.info(f"Using embeddings: {config.ollama_embedding_model} (Ollama)")

    # Start dashboard
    dashboard.start(orchestrator)
    logger.info(f"Dashboard: http://localhost:{config.dashboard_port}")

    # Handle graceful shutdown
    loop = asyncio.get_event_loop()
    stop_event = asyncio.Event()

    def shutdown_handler():
        logger.info("Shutdown signal received...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown_handler)
        except NotImplementedError:
            pass  # Windows doesn't support add_signal_handler

    # If topic provided as argument, start research automatically
    if args.topic:
        logger.info(f"Auto-starting research on: {args.topic}")
        research_task = asyncio.create_task(orchestrator.start(args.topic))

        # Wait for stop signal or research completion
        await asyncio.gather(
            research_task,
            stop_event.wait(),
            return_exceptions=True,
        )

        await orchestrator.stop()
        # Ensure the research task's cleanup (writes end_time plus the honest
        # close status - completed only when the queue really drained)
        # finishes before we tear down resources and exit the process.
        await asyncio.gather(research_task, return_exceptions=True)
    else:
        logger.info("Dashboard is running. Use it to start research, or restart with --topic.")
        logger.info("Press Ctrl+C to stop.")
        await stop_event.wait()

    # Best-effort teardown, also reached when interrupted (orchestrator.start()
    # already closed the session via _cleanup in its finally block).
    try:
        dashboard.stop()
    finally:
        await orchestrator.llm.close()
        await orchestrator.extractor.close()
    logger.info("Research agent stopped.")


async def run_headless(args):
    """Run the agent headless (no dashboard, topic required)."""
    config = get_config()
    setup_logging(config)
    logger = logging.getLogger(__name__)

    if not args.topic:
        logger.error("Topic is required for headless mode. Use --topic 'your topic'")
        sys.exit(1)

    guard = InstanceLock.for_database(config.database_for_topic(args.topic or ""))
    if not guard.acquire():
        logger.error(
            "Another agent is already running on this database (pid %s, lock %s) - "
            "stop it first.",
            guard.held_by, guard.path,
        )
        sys.exit(1)

    orchestrator = ResearchOrchestrator(config, topic=args.topic or "")
    logger.info(f"Database: {orchestrator.database_path}")

    if not await orchestrator.llm.health_check():
        logger.error(backend_error_hint(config))
        sys.exit(1)

    logger.info(f"Starting headless research on: {args.topic}")
    exit_code = 0
    try:
        await orchestrator.start(args.topic)  # start() closes the session in its finally
    except BaseException:
        logger.exception("Headless run ended with an error")
        exit_code = 1
    finally:
        await orchestrator.llm.close()
        await orchestrator.extractor.close()
        # Release the database lock explicitly before the hard exit below:
        # os._exit skips the atexit machinery that would normally remove it.
        guard.release()
        logging.shutdown()  # flush file handler after lightly-stopped log
        # Open aiohttp transports kept a finished headless run alive as a
        # zombie holding the database lock (seen live 01.11.: a run whose
        # session had closed hung for hours with the lock in place). asyncio
        # cancelling every task is not guaranteed to unwind them all, so the
        # headless mode terminates the process hard once everything above is
        # flushed. The dashboard mode stays interactive and exits normally.
        os._exit(exit_code)


def main():
    parser = argparse.ArgumentParser(description="Autonomous Research Agent")
    parser.add_argument("--topic", "-t", type=str, help="Research topic to investigate")
    parser.add_argument("--no-dashboard", action="store_true", help="Run without web dashboard")
    parser.add_argument("--port", "-p", type=int, help="Dashboard port (default: 8080)")
    parser.add_argument("--model", "-m", type=str, help="Override the chat model (Ollama or TUDaGPT, whichever backend is active)")

    args = parser.parse_args()

    # Override config if needed
    if args.port:
        import os
        os.environ["DASHBOARD_PORT"] = str(args.port)
    if args.model:
        import os
        # The override applies to the active chat backend.
        os.environ["OLLAMA_MODEL"] = args.model
        os.environ["TUDAGPT_MODEL"] = args.model

    # Reset config to pick up overrides
    import research_agent.config as cfg
    cfg._config = None

    try:
        if args.no_dashboard:
            asyncio.run(run_headless(args))
        else:
            asyncio.run(run_with_dashboard(args))
    except KeyboardInterrupt:
        # SIGINT/Ctrl+C: the orchestrator's start() already closed the session
        # cleanly (end_time/status via _cleanup). Exit 0 rather than the default
        # non-zero status for an interrupted process.
        logging.getLogger(__name__).info("Interrupted by user; exiting cleanly.")
        sys.exit(0)


if __name__ == "__main__":
    main()
