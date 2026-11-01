#!/usr/bin/env python3
"""
Kaggle GPU Server - Quick Start Guide
=====================================

HOW IT WORKS:
  Raspberry Pi (8GB)           Kaggle Free GPU (T4, 16GB)
  ┌──────────────────┐         ┌──────────────────────────┐
  │ Agent + DB       │──API──▶│ Qwen3-8B via FastAPI     │
  │ Dashboard :8080  │◀───────│ + ngrok tunnel           │
  │ SQLite           │         │ ~10-15 tok/s             │
  └──────────────────┘         └──────────────────────────┘

STEP 1: Start Kaggle GPU Server
  1. Go to kaggle.com → Code → New Notebook
  2. Enable GPU: Settings → Accelerator → GPU T4 x2
  3. In the first cell, run:
     !pip install -q fastapi uvicorn pyngrok transformers accelerate
  4. Upload scripts/kaggle_gpu_server.py or paste its contents
  5. Run it: !python kaggle_gpu_server.py
  6. Copy the PUBLIC URL that appears (https://xxxx.ngrok-free.app)

STEP 2: Configure the Pi
  ssh into the Pi and edit .env:
     cd ~/AIResearch
     nano .env

  Set these values:
     LLM_BACKEND=kaggle_api
     KAGGLE_API_URL=https://xxxx.ngrok-free.app
     KAGGLE_API_KEY=     (leave empty unless you set ngrok auth)

STEP 3: Start the Agent on the Pi
     cd ~/AIResearch
     source .venv/bin/activate
     python run.py

  Or with the dashboard:
     python -m research_agent.main

STEP 4: Access Dashboard
  Open http://192.168.178.109:8080 in your browser

TROUBLESHOOTING:
  - If ngrok shows "session expired", restart the Kaggle notebook
  - Kaggle notebooks auto-disconnect after 60min of inactivity
  - If connection fails, check KAGGLE_API_URL in .env matches the ngrok URL
  - The agent will fall back gracefully if the GPU server is unreachable

MODEL OPTIONS:
  Change KAGGLE_MODEL env var in the notebook:
  - Qwen/Qwen3-8B   (8B params, ~6GB VRAM, fast)
  - Qwen/Qwen3-14B  (14B params, ~10GB VRAM, best quality)
  - meta-llama/Llama-3.1-8B-Instruct (8B, good for English)
"""
