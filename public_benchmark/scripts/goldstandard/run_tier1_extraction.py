#!/usr/bin/env python3
"""Extraktionslauf auf dem externen Validierungssatz (Stufe 1).

Jedes Modell bekommt den Volltext eines Trials und die Liste der gesuchten
Felder und soll eine JSON-Zeile je Studienarm zurueckgeben. Es wird nichts
nachbearbeitet: was das Modell liefert, wird so bewertet, wie es kommt.

Aufruf (nach ausdruecklicher Freigabe):

    python public_benchmark/scripts/goldstandard/run_tier1_extraction.py \
        --models qwen deepseek glm --workers 3

Die Ausgabe ist eine JSONL mit einer Zeile je (Record, Modell); ein
abgebrochener Lauf kann mit demselben Befehl fortgesetzt werden.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
BENCH = HERE.parents[2]
REPO = BENCH.parent
CROSSVAL = BENCH / "evaluation" / "multi_model_cross_validation"
SET = CROSSVAL / "tier1_validation_set_v1.jsonl"
DOCS = CROSSVAL / "tier1_documents_v1.json"
TEXT_DIR = REPO / "data" / "fulltext_inbox" / "tier1_xml"
RUN_DIR = CROSSVAL / "runs" / "tier1_20261113"

sys.path.insert(0, str(REPO))
from research_agent.config import get_config  # noqa: E402

MODELS = {
    "qwen": {"id": "gwdg/qwen3.5-397b-a17b", "max_tokens": 12000},
    "deepseek": {"id": "gwdg/deepseek-v4.1-flash-1017", "max_tokens": 8000},
    "glm": {"id": "gwdg/glm-5.3", "max_tokens": 12000},
}

SYSTEM = (
    "You extract numerical results from randomised controlled trial publications. "
    "You answer with a single JSON object and nothing else. You never invent values: "
    "if a value is not reported, you use null."
)

LOCK = threading.Lock()


def strip_xml(raw: str) -> str:
    text = re.sub(r"<(xref|ext-link)[^>]*>.*?</\1>", " ", raw, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def build_prompt(record: dict[str, Any], text: str, limit: int = 45000) -> str:
    fields = record["requested_fields"]
    field_list = ", ".join(f'"{name}"' for name in fields)
    body = text[:limit]
    return (
        f"Publication:\n{body}\n\n"
        f"Outcome of interest: {record['outcome_label']}\n\n"
        "Extract the numerical results reported for this outcome. Return exactly one JSON object:\n"
        '{"rows": [{"<field>": <value>, ...}, ...]}\n'
        f"Use exactly these fields in every row: {field_list}. "
        "One row per study arm or study comparison reported in the paper. "
        "Numbers must be copied as reported; do not convert, do not compute, do not guess. "
        "Use null for a field the paper does not report. "
        "Do not add commentary, markdown or code fences."
    )


def call(
    model: dict[str, Any], prompt: str, key: str, base: str, attempts: int = 4
) -> dict[str, Any]:
    last: dict[str, Any] | None = None
    for attempt in range(1, attempts + 1):
        last = _call_once(model, prompt, key, base)
        status = last.get("http_status")
        if status == 200 and last.get("content"):
            return last
        if status in (429, 500, 502, 503, 504) and attempt < attempts:
            wait = 5 * attempt + random.uniform(0, 3)
            print(f"  {model['id']} {status}, warte {wait:.1f}s (Versuch {attempt})", flush=True)
            time.sleep(wait)
            continue
        return last
    return last or {"http_status": 0, "error": "kein Versuch", "content": ""}


def _call_once(model: dict[str, Any], prompt: str, key: str, base: str) -> dict[str, Any]:
    payload = {
        "model": model["id"],
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.0,
        "max_tokens": model["max_tokens"],
    }
    request = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            body = response.read().decode("utf-8", errors="replace")
            status = response.status
    except urllib.error.HTTPError as exc:
        return {
            "http_status": exc.code,
            "elapsed_s": round(time.monotonic() - started, 2),
            "error": f"HTTPError {exc.code}: {exc.read().decode('utf-8', 'replace')[:300]}",
            "content": "",
            "finish_reason": "",
            "completion_tokens": None,
        }
    except Exception as exc:  # noqa: BLE001 - Lauf soll weiterlaufen
        return {
            "http_status": 0,
            "elapsed_s": round(time.monotonic() - started, 2),
            "error": f"{type(exc).__name__}: {exc}",
            "content": "",
            "finish_reason": "",
            "completion_tokens": None,
        }

    parsed = json.loads(body)
    choice = (parsed.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    usage = parsed.get("usage") or {}
    return {
        "http_status": status,
        "elapsed_s": round(time.monotonic() - started, 2),
        "error": "",
        "content": message.get("content") or "",
        "finish_reason": choice.get("finish_reason") or "",
        "completion_tokens": usage.get("completion_tokens"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "model_in_response": parsed.get("model", ""),
    }


def parse_rows(content: str) -> tuple[list[dict[str, Any]], str]:
    text = content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as error:
        match = re.search(r"\{.*\}", text, re.S)
        if not match:
            return [], f"json_error: {error}"
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError as second:
            return [], f"json_error: {second}"
    rows = payload.get("rows") if isinstance(payload, dict) else None
    if rows is None and isinstance(payload, list):
        rows = payload
    if not isinstance(rows, list):
        return [], "no_rows"
    return [row for row in rows if isinstance(row, dict)], ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["qwen", "deepseek", "glm"])
    parser.add_argument("--dataset", default="glass_trialreviewbench")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--records", type=int, default=0, help="nur die ersten N Records")
    parser.add_argument("--sleep", type=float, default=0.0, help="Pause zwischen Auftraegen")
    args = parser.parse_args()

    config = get_config()
    key = getattr(config, "tudagpt_api_key", "")
    base = (getattr(config, "tudagpt_api_base", "") or "").rstrip("/")
    if not key or not base:
        print("ABBRUCH: TUDaGPT-Zugang nicht konfiguriert.")
        return 2

    records = [
        json.loads(line) for line in SET.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    docs = {
        item["record_id"]: item
        for item in json.loads(DOCS.read_text(encoding="utf-8"))["details"]
    }
    jobs = []
    seen: list[str] = []
    for record in records:
        if record["dataset"] != args.dataset:
            continue
        if args.records:
            if record["record_id"] not in seen:
                if len(seen) >= args.records:
                    continue
                seen.append(record["record_id"])
        doc = docs.get(record["record_id"], {})
        pmcid = doc.get("pmcid", "")
        path = TEXT_DIR / f"{pmcid}.xml"
        if not pmcid or not path.exists():
            continue
        for name in args.models:
            jobs.append((record, name, path))
    if args.limit:
        jobs = jobs[: args.limit]

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    out = RUN_DIR / "predictions.jsonl"
    done = set()
    if out.exists():
        for line in out.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("rows"):
                    done.add((row["record_id"], row["model"]))

    print(f"{len(jobs)} Auftraege, {len(done)} bereits erledigt, {args.workers} Threads")
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def work(job: tuple[dict[str, Any], str, Path]) -> dict[str, Any]:
        record, name, path = job
        text = strip_xml(path.read_text(encoding="utf-8", errors="replace"))
        prompt = build_prompt(record, text)
        if args.sleep:
            time.sleep(args.sleep)
        result = call(MODELS[name], prompt, key, base)
        rows, parse_error = parse_rows(result["content"]) if result["content"] else ([], "leer")
        with LOCK, out.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(
                json.dumps(
                    {
                        "record_id": record["record_id"],
                        "model": name,
                        "model_id": MODELS[name]["id"],
                        "dataset": record["dataset"],
                        "http_status": result["http_status"],
                        "error": result["error"],
                        "finish_reason": result["finish_reason"],
                        "completion_tokens": result.get("completion_tokens"),
                        "prompt_tokens": result.get("prompt_tokens"),
                        "elapsed_s": result["elapsed_s"],
                        "content_len": len(result["content"]),
                        "parse_error": parse_error,
                        "rows": rows,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
        return {"model": name, "ok": bool(rows), "parse_error": parse_error, "status": result["http_status"]}

    tally = {"ok": 0, "leer": 0, "fehler": 0}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(work, job) for job in jobs if (job[0]["record_id"], job[1]) not in done]
        for future in as_completed(futures):
            outcome = future.result()
            if outcome["ok"]:
                tally["ok"] += 1
            elif outcome["parse_error"] == "leer" or outcome["status"] != 200:
                tally["fehler"] += 1
            else:
                tally["leer"] += 1
            print(
                f"{outcome['model']}: status {outcome['status']}, "
                f"rows {'ja' if outcome['ok'] else 'nein'} {outcome['parse_error']}",
                flush=True,
            )

    manifest = {
        "run_id": "tier1_20261113",
        "started": started,
        "finished": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dataset": args.dataset,
        "models": {name: MODELS[name] for name in args.models},
        "jobs": len(jobs),
        "tally": tally,
        "predictions": "predictions.jsonl",
    }
    (RUN_DIR / "run_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
