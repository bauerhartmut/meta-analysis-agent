#!/bin/bash
# Setup script for the Autonomous Research Agent

echo "=== Autonomous Research Agent Setup ==="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "Found: $PYTHON_VERSION"

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "WARNING: Ollama not found."
    echo "Please install Ollama from https://ollama.com"
    echo "Then run: ollama pull qwen3:14b && ollama pull nomic-embed-text"
else
    echo "Found: Ollama $(ollama --version 2>/dev/null)"
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate and install
source .venv/bin/activate 2>/dev/null || .venv\Scripts\activate 2>/dev/null

echo "Installing dependencies..."
pip install --quiet aiohttp beautifulsoup4 pytest

# Create data directories
mkdir -p data data/journal

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env 2>/dev/null || true
fi

echo ""
echo "=== Setup complete! ==="
echo ""
echo "Quick start:"
echo "  source .venv/bin/activate"
echo "  python run.py --topic 'Quantum Consciousness'"
echo ""
echo "Or with dashboard:"
echo "  python run.py"
echo "  Open http://localhost:8080"
