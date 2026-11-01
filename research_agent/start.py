"""
Auto-Start Script for Research Agent
Checks if Ollama is running, starts it if not, then starts the Research Agent.
Works on Windows (primary target) and Linux/Mac.
"""

import subprocess
import sys
import time
import os
import json
import logging
from pathlib import Path
from typing import Optional, List

# Configuration
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_CHECK_URL = f"{OLLAMA_HOST}/api/tags"
MAX_WAIT_SECONDS = 60
RESEARCH_CYCLES = 3
RESEARCH_TOPIC = "heritability of intelligence and embryo selection"

logger = logging.getLogger(__name__)


def _ollama_request(endpoint="", timeout=5):
    """Make a request to Ollama API. Returns parsed JSON or None on failure."""
    import urllib.request
    url = f"{OLLAMA_HOST}{endpoint}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def check_ollama_running():
    """Check if Ollama is running by hitting its API."""
    return _ollama_request("/api/tags") is not None


def get_ollama_models():
    """Get list of available Ollama models."""
    data = _ollama_request("/api/tags")
    if data:
        return [m["name"] for m in data.get("models", [])]
    return []


def ensure_model_available(model):
    """Check if the configured model is available, pull it if not."""
    models = get_ollama_models()
    if model in models:
        return True

    print(f"Model '{model}' not found. Available: {', '.join(models[:5])}")
    print(f"Pulling model '{model}'...")
    try:
        result = subprocess.run(
            ["ollama", "pull", model],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode == 0:
            print(f"Model '{model}' pulled successfully!")
            return True
        else:
            print(f"Failed to pull model: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("Model pull timed out after 10 minutes")
        return False
    except FileNotFoundError:
        print("'ollama' command not found. Is it in your PATH?")
        return False


def start_ollama():
    """Start Ollama server in background."""
    print("Starting Ollama server...")
    try:
        if sys.platform == "win32":
            subprocess.Popen(
                ["ollama", "serve"],
                creationflags=0x00000008,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        return True
    except FileNotFoundError:
        print("Ollama not found. Install: https://ollama.ai/download")
        return False
    except Exception as e:
        print(f"Failed to start Ollama: {e}")
        return False


def wait_for_ollama(timeout=MAX_WAIT_SECONDS):
    """Wait for Ollama to be ready."""
    print(f"Waiting for Ollama (max {timeout}s)...")
    start = time.time()
    while time.time() - start < timeout:
        if check_ollama_running():
            elapsed = time.time() - start
            print(f"Ollama ready! ({elapsed:.1f}s)")
            return True
        time.sleep(2)
    print(f"Ollama not ready after {timeout}s")
    return False


def start_research_agent(cycles=RESEARCH_CYCLES, topic=RESEARCH_TOPIC):
    """Start the Research Agent."""
    print(f"\nStarting Research Agent...")
    print(f"  Topic: {topic}")
    print(f"  Cycles: {cycles}")

    project_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(project_dir))

    log_file = project_dir / "data" / "agent_output.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logging.getLogger().addHandler(file_handler)

    import asyncio
    from research_agent.orchestrator import ResearchOrchestrator
    from research_agent.config import get_config
    from research_agent.utf8_logging import ensure_utf8

    ensure_utf8()

    async def run():
        config = get_config()
        config.max_research_cycles = cycles
        config.research_interval = 0
        orchestrator = ResearchOrchestrator(config)
        await orchestrator.start(topic)

    asyncio.run(run())


def main():
    """Main entry point."""
    # Add project root to path before any research_agent imports
    project_dir = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_dir))

    print("=" * 60)
    print("  Research Agent Auto-Start")
    print("=" * 60)

    if check_ollama_running():
        print("Ollama is running!")
    else:
        print("Ollama is not running")
        if not start_ollama():
            sys.exit(1)
        if not wait_for_ollama():
            sys.exit(1)

    models = get_ollama_models()
    if models:
        print(f"\nModels: {', '.join(models[:5])}")

    from research_agent.config import get_config
    config = get_config()
    model = config.ollama_model
    print(f"\nConfigured model: {model}")
    if not ensure_model_available(model):
        print("Required model not available")
        sys.exit(1)

    start_research_agent()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
