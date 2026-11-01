"""
PC GPU Server + ngrok Tunnel
=============================
Starts the PC GPU server and creates an ngrok tunnel so the Pi
can access it even when the firewall blocks direct connections.

Usage:
    python scripts/pc_gpu_server_with_ngrok.py
"""

import os
import sys
import threading
import time
import logging

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyngrok import ngrok
import uvicorn

# Import the FastAPI app from pc_gpu_server
from scripts.pc_gpu_server import app, OLLAMA_HOST, PORT

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pc_server_ngrok")

NGROK_AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN", "")


def start_ngrok():
    """Create ngrok tunnel to the PC server port."""
    try:
        if NGROK_AUTH_TOKEN:
            ngrok.set_auth_token(NGROK_AUTH_TOKEN)

        public_url = ngrok.connect(PORT).public_url
        logger.info(f"")
        logger.info(f"{'=' * 60}")
        logger.info(f"NGROK TUNNEL ACTIVE")
        logger.info(f"Public URL: {public_url}")
        logger.info(f"")
        logger.info(f"Copy this URL into the Pi's .env:")
        logger.info(f"  PC_SERVER_URL={public_url}")
        logger.info(f"{'=' * 60}")

        # Save URL to file
        with open("pc_server_url.txt", "w") as f:
            f.write(public_url)
        logger.info(f"URL saved to pc_server_url.txt")

        return public_url
    except Exception as e:
        logger.error(f"ngrok failed: {e}")
        logger.info("Server will run on localhost only.")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("PC GPU SERVER + NGROK TUNNEL")
    print(f"Ollama: {OLLAMA_HOST}")
    print(f"Server port: {PORT}")
    print("=" * 60)

    # Start ngrok in background thread
    ngrok_thread = threading.Thread(target=start_ngrok, daemon=True)
    ngrok_thread.start()
    time.sleep(2)  # Give ngrok time to connect

    # Start the FastAPI server (blocks)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
