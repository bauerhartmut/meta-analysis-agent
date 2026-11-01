"""
Kaggle GPU LLM Server
=====================
Run this in a Kaggle notebook (GPU enabled). Exposes an OpenAI-compatible
API via ngrok so the Raspberry Pi can call it remotely.

Usage in a Kaggle notebook cell:
    !pip install -q fastapi uvicorn pyngrok transformers accelerate bitsandbytes
    !python kaggle_gpu_server.py
"""

import os
import sys
import json
import time
import logging
import asyncio
from typing import Optional, List, Dict, Any

import torch
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig,
)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# ── Config ──────────────────────────────────────────────────────────────────
MODEL_NAME = os.environ.get("KAGGLE_MODEL", "Qwen/Qwen3-14B")
MAX_NEW_TOKENS = int(os.environ.get("KAGGLE_MAX_TOKENS", "2048"))
NGROK_AUTH_TOKEN = os.environ.get("NGROK_AUTH_TOKEN", "")  # optional, for stable URLs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kaggle_server")

# ── Model Loading ───────────────────────────────────────────────────────────
logger.info(f"Loading model: {MODEL_NAME}")
logger.info(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
    logger.info(f"VRAM: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB")

# int4 quantization so Qwen3-14B fits in 16GB VRAM (T4)
use_quant = "14b" in MODEL_NAME.lower() or "70b" in MODEL_NAME.lower()
if use_quant:
    logger.info("Using int4 quantization (BitsAndBytes)")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
else:
    bnb_config = None
    logger.info("Loading in float16 (no quantization)")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    torch_dtype=torch.float16 if not use_quant else None,
    device_map="auto",
    trust_remote_code=True,
)

logger.info(f"Model loaded. Parameters: {model.num_parameters() / 1e9:.1f}B")

# ── FastAPI App ─────────────────────────────────────────────────────────────
app = FastAPI(title="Kaggle GPU LLM Server")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = MODEL_NAME
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = MAX_NEW_TOKENS
    stream: bool = False
    format: Optional[str] = None  # "json" or None
    think: Optional[bool] = None  # qwen3 thinking mode


class EmbedRequest(BaseModel):
    model: str = "embed"
    input: str | List[str]


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [{"id": MODEL_NAME, "object": "model", "owned_by": "kaggle"}],
    }


@app.post("/v1/chat/completions")
def chat_completions(req: ChatRequest):
    """OpenAI-compatible chat completion endpoint."""
    try:
        # Build prompt from messages
        prompt = tokenizer.apply_chat_template(
            [m.model_dump() for m in req.messages],
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=req.think if req.think is not None else False,
        )

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        gen_kwargs = {
            "max_new_tokens": min(req.max_tokens, MAX_NEW_TOKENS),
            "temperature": max(req.temperature, 0.01),
            "do_sample": req.temperature > 0,
            "top_p": 0.95,
        }

        if req.format == "json":
            # Force JSON output with guided generation hint
            gen_kwargs["return_dict_in_generate"] = False

        t0 = time.time()
        with torch.no_grad():
            outputs = model.generate(**inputs, **gen_kwargs)
        elapsed = time.time() - t0

        # Decode only new tokens
        new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
        content = tokenizer.decode(new_tokens, skip_special_tokens=True)

        # Strip thinking tags if present
        if "<think>" in content and "</think>" in content:
            think_end = content.index("</think>") + len("</think>")
            content = content[think_end:].strip()

        prompt_tokens = inputs["input_ids"].shape[1]
        completion_tokens = len(new_tokens)

        logger.info(f"Chat: {prompt_tokens}+{completion_tokens} tokens in {elapsed:.1f}s")

        return {
            "id": f"chatcmpl-{int(time.time()*1000)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": req.model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        }

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/embeddings")
def embeddings(req: EmbedRequest):
    """Embedding endpoint using model's hidden states (mean pooling)."""
    try:
        texts = req.input if isinstance(req.input, list) else [req.input]

        # Use tokenizer + model forward pass for embeddings
        encoded = tokenizer(texts, padding=True, truncation=True,
                          max_length=512, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model(**encoded, output_hidden_states=True)
            # Use last hidden state, mean pooling
            hidden = outputs.hidden_states[-1]
            attention_mask = encoded["attention_mask"].unsqueeze(-1)
            embeddings = (hidden * attention_mask).sum(1) / attention_mask.sum(1)

        # Normalize
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

        data = []
        for i, emb in enumerate(embeddings):
            data.append({
                "object": "embedding",
                "index": i,
                "embedding": emb.cpu().float().tolist(),
            })

        return {
            "object": "list",
            "data": data,
            "model": req.model,
            "usage": {"prompt_tokens": sum(encoded["input_ids"].shape[1]), "total_tokens": sum(encoded["input_ids"].shape[1])},
        }

    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    gpu_info = {}
    if torch.cuda.is_available():
        gpu_info = {
            "gpu": torch.cuda.get_device_name(0),
            "vram_used_gb": round(torch.cuda.memory_allocated(0) / 1e9, 2),
            "vram_total_gb": round(torch.cuda.get_device_properties(0).total_mem / 1e9, 1),
        }
    return {"status": "ok", "model": MODEL_NAME, **gpu_info}


# ── Main: start server + ngrok ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("KAGGLE GPU LLM SERVER")
    print(f"Model: {MODEL_NAME}")
    print(f"Max tokens: {MAX_NEW_TOKENS}")
    print("=" * 60)

    # Try to use ngrok for public URL
    public_url = None
    try:
        from pyngrok import ngrok
        if NGROK_AUTH_TOKEN:
            ngrok.set_auth_token(NGROK_AUTH_TOKEN)
        public_url = ngrok.connect(8888).public_url
        print(f"\n{'=' * 60}")
        print(f"PUBLIC URL: {public_url}")
        print(f"Use this URL in your Pi's .env: KAGGLE_API_URL={public_url}")
        print(f"{'=' * 60}\n")
    except ImportError:
        print("pyngrok not installed. Install with: pip install pyngrok")
        print("Server will run on localhost:8888 only.")
    except Exception as e:
        print(f"ngrok failed: {e}")
        print("Server will run on localhost:8888 only.")

    if public_url:
        # Write URL to file for easy retrieval
        with open("/kaggle/working/api_url.txt", "w") as f:
            f.write(public_url)
        print(f"URL also saved to /kaggle/working/api_url.txt")

    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
