"""
PC GPU Server
=============
Runs on the PC with GPU (RTX 3060). Wraps local Ollama into an
OpenAI-compatible API so the Raspberry Pi can call it over LAN.

Usage:
    python scripts/pc_gpu_server.py

The Pi connects to http://192.168.178.39:8090 as primary GPU backend.
When the PC is off, the Pi falls back to Kaggle automatically.
"""

import os
import time
import logging
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import aiohttp
import asyncio

# ── Config ──────────────────────────────────────────────────────────────────
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
PORT = int(os.environ.get("PC_SERVER_PORT", "8090"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pc_server")

app = FastAPI(title="PC GPU Server")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ── Pydantic Models ─────────────────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = ""
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 4096
    stream: bool = False
    format: Optional[str] = None
    think: Optional[bool] = None


class EmbedRequest(BaseModel):
    model: str = ""
    input: str | List[str]


# ── Proxy to Ollama ────────────────────────────────────────────────────────
async def ollama_request(endpoint: str, payload: dict) -> dict:
    """Forward a request to Ollama and return the response."""
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{OLLAMA_HOST}{endpoint}", json=payload) as resp:
            if resp.status != 200:
                text = await resp.text()
                raise HTTPException(status_code=resp.status, detail=f"Ollama error: {text[:200]}")
            return await resp.json()


@app.get("/v1/models")
async def list_models():
    data = await ollama_request("/api/tags", {})
    return {
        "object": "list",
        "data": [
            {"id": m["name"], "object": "model", "owned_by": "pc-gpu"}
            for m in data.get("models", [])
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    """OpenAI-compatible chat → forwards to Ollama."""
    model = req.model or "qwen3:14b"

    payload = {
        "model": model,
        "messages": [m.dict() for m in req.messages],
        "stream": False,
        "options": {
            "temperature": req.temperature,
            "num_predict": req.max_tokens,
        },
    }
    if req.format == "json":
        payload["format"] = "json"
    if req.think is not None:
        payload["think"] = req.think

    t0 = time.time()
    data = await ollama_request("/api/chat", payload)
    elapsed = time.time() - t0

    content = data.get("message", {}).get("content", "")
    # qwen3 thinking mode puts response in "thinking" field
    if not content:
        thinking = data.get("message", {}).get("thinking", "")
        if thinking:
            content = thinking
    prompt_tok = data.get("prompt_eval_count", 0) or 0
    compl_tok = data.get("eval_count", 0) or 0

    logger.info(f"Chat [{model}]: {prompt_tok}+{compl_tok} tokens in {elapsed:.1f}s")

    return {
        "id": f"chatcmpl-pc-{int(time.time()*1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {
            "prompt_tokens": prompt_tok,
            "completion_tokens": compl_tok,
            "total_tokens": prompt_tok + compl_tok,
        },
    }


@app.post("/v1/embeddings")
async def embeddings(req: EmbedRequest):
    """Embedding → forwards to Ollama."""
    model = req.model or "nomic-embed-text"
    texts = req.input if isinstance(req.input, list) else [req.input]

    all_embeddings = []
    for text in texts:
        data = await ollama_request("/api/embed", {"model": model, "input": text})
        emb = data.get("embeddings", [[]])[0]
        all_embeddings.append(emb)

    return {
        "object": "list",
        "data": [
            {"object": "embedding", "index": i, "embedding": emb}
            for i, emb in enumerate(all_embeddings)
        ],
        "model": model,
        "usage": {"prompt_tokens": sum(len(t) for t in texts), "total_tokens": sum(len(t) for t in texts)},
    }


@app.get("/health")
async def health():
    """Health check — also verifies Ollama is reachable."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{OLLAMA_HOST}/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m["name"] for m in data.get("models", [])]
                    return {
                        "status": "ok",
                        "backend": "ollama",
                        "host": OLLAMA_HOST,
                        "models": models,
                    }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


if __name__ == "__main__":
    print("=" * 60)
    print("PC GPU SERVER")
    print(f"Ollama: {OLLAMA_HOST}")
    print(f"Listening: 0.0.0.0:{PORT}")
    print(f"Pi connects to: http://<PC-IP>:{PORT}")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
