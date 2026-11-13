#!/usr/bin/env python3
"""Isolierte Diagnose fuer GLM 5.3 auf vorhandenen Dev-Daten.

Kein Cross-Validation-Artikel, kein Referenzwert, kein regulaerer Lauf. Der
Test wiederholt die Bedingungen des gescheiterten Dev-Laufs und variiert
gezielt Payload-Parameter, um leere und abgeschnittene Antworten zu erklaeren.

Rohantworten und Metadaten werden unveraendert gespeichert. Der API-Schluessel
wird nie geschrieben oder ausgegeben.

Ausgabe:
- ``diagnostics/glm_20261113/raw/<case>.json`` (vollstaendiger Response-Body)
- ``diagnostics/glm_20261113/glm_diagnostic.json``
- ``diagnostics/glm_20261113/glm_diagnostic.md``
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BENCH_ROOT.parent
OUT = BENCH_ROOT / "evaluation" / "multi_model_cross_validation" / "diagnostics" / "glm_20261113"
RAW = OUT / "raw"
DEV_INPUT = BENCH_ROOT / "evaluation" / "c1_pilot" / "dev_input.jsonl"
MODEL = "gwdg/glm-5.3"

sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(BENCH_ROOT / "scripts"))

from research_agent.config import get_config  # noqa: E402

import run_c1_dev_pilot as dev  # noqa: E402


def load_record(record_id: int) -> dict:
    for line in DEV_INPUT.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if int(row["record_id"]) == record_id:
            return row
    raise SystemExit(f"Dev-Record {record_id} nicht gefunden")


def source_text(record: dict) -> str:
    path = record["source_text_path"]
    candidate = REPO_ROOT / path
    if not candidate.exists():
        candidate = BENCH_ROOT / path
    return candidate.read_text(encoding="utf-8", errors="replace")


def build_payload(messages: list[dict], case: dict) -> dict:
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": case.get("max_tokens", 900),
        "stream": case.get("stream", False),
    }
    if case.get("reasoning_effort") is not None:
        payload["reasoning_effort"] = case["reasoning_effort"]
    if case.get("response_format_json"):
        payload["response_format"] = {"type": "json_object"}
    return payload


def call(payload: dict, key: str, base: str) -> dict:
    request = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            status = response.status
            headers = dict(response.headers)
            if payload.get("stream"):
                chunks = []
                finish = ""
                for raw in response:
                    line = raw.decode("utf-8", errors="replace").strip()
                    if not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        event = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    for choice in event.get("choices") or []:
                        delta = choice.get("delta") or {}
                        if delta.get("content"):
                            chunks.append(delta["content"])
                        if choice.get("finish_reason"):
                            finish = choice["finish_reason"]
                body = "".join(chunks)
                return {
                    "http_status": status,
                    "content_type": headers.get("Content-Type", ""),
                    "elapsed_s": round(time.monotonic() - started, 2),
                    "streamed_text": body,
                    "stream_finish_reason": finish,
                    "body": None,
                    "error": "",
                }
            body = response.read().decode("utf-8", errors="replace")
            return {
                "http_status": status,
                "content_type": headers.get("Content-Type", ""),
                "elapsed_s": round(time.monotonic() - started, 2),
                "body": body,
                "error": "",
            }
    except urllib.error.HTTPError as exc:
        return {
            "http_status": exc.code,
            "content_type": "",
            "elapsed_s": round(time.monotonic() - started, 2),
            "body": exc.read().decode("utf-8", errors="replace"),
            "error": f"HTTPError {exc.code}",
        }
    except Exception as exc:  # noqa: BLE001 - Diagnose soll weiterlaufen
        return {
            "http_status": 0,
            "content_type": "",
            "elapsed_s": round(time.monotonic() - started, 2),
            "body": "",
            "error": f"{type(exc).__name__}: {exc}",
        }


def analyse(result: dict, payload: dict) -> dict:
    body = result.get("body")
    parsed = {}
    if body:
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {}
    choices = parsed.get("choices") or []
    message = (choices[0] or {}).get("message", {}) if choices else {}
    content = message.get("content") or ""
    reasoning = message.get("reasoning_content") or ""
    if result.get("streamed_text") is not None:
        content = result["streamed_text"]
    usage = parsed.get("usage") or {}
    return {
        "http_status": result.get("http_status"),
        "content_type": result.get("content_type", ""),
        "elapsed_s": result.get("elapsed_s"),
        "error": result.get("error", ""),
        "max_tokens": payload.get("max_tokens"),
        "stream": payload.get("stream"),
        "reasoning_effort": payload.get("reasoning_effort", "<nicht gesendet>"),
        "finish_reason": (choices[0] or {}).get("finish_reason")
        if choices
        else result.get("stream_finish_reason", ""),
        "content_len": len(content),
        "content_head": content[:400],
        "content_is_json": _is_json(content),
        "reasoning_len": len(reasoning),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "model_in_response": parsed.get("model", ""),
        "message_keys": sorted(message.keys()),
    }


def _is_json(text: str) -> bool:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[-1] if "\n" in text else text
    try:
        json.loads(text)
        return True
    except Exception:  # noqa: BLE001 - nur eine Ja/Nein-Pruefung
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="GLM-5.3-Diagnose")
    parser.add_argument(
        "--budget",
        type=int,
        nargs="+",
        default=None,
        help="max_tokens-Stufen, die zusaetzlich auf Record 120 geprueft werden",
    )
    args = parser.parse_args()

    config = get_config()
    key = getattr(config, "tudagpt_api_key", "")
    base = (getattr(config, "tudagpt_api_base", "") or "").rstrip("/")
    if not key:
        print("ABBRUCH: kein TUDAGPT_API_KEY konfiguriert (nicht ausgeben, nur setzen).")
        return 2
    if not base:
        print("ABBRUCH: TUDAGPT_API_BASE fehlt.")
        return 2

    RAW.mkdir(parents=True, exist_ok=True)
    records = {rid: load_record(rid) for rid in (120, 233)}
    if args.budget:
        cases = [
            (
                f"record120_max_tokens_{n}",
                120,
                {"reasoning_effort": "none", "max_tokens": n},
            )
            for n in args.budget
        ]
    else:
        cases = [
            ("record120_baseline", 120, {"reasoning_effort": "none", "max_tokens": 900}),
            ("record120_repeat", 120, {"reasoning_effort": "none", "max_tokens": 900}),
            ("record120_no_reasoning_param", 120, {"max_tokens": 900}),
            ("record120_max_tokens_2000", 120, {"reasoning_effort": "none", "max_tokens": 2000}),
            ("record120_stream", 120, {"reasoning_effort": "none", "max_tokens": 900, "stream": True}),
            ("record233_baseline", 233, {"reasoning_effort": "none", "max_tokens": 900}),
        ]

    results = []
    for name, record_id, case in cases:
        record = records[record_id]
        text = source_text(record)
        prompt = dev.render_prompt(record, text, "v6")
        messages = [
            {"role": "system", "content": dev.SYSTEM_PROMPTS["v6"]},
            {"role": "user", "content": prompt},
        ]
        payload = build_payload(messages, case)
        result = call(payload, key, base)
        raw_path = RAW / f"{name}.json"
        raw_path.write_text(
            json.dumps(
                {
                    "case": name,
                    "record_id": record_id,
                    "request": {k: v for k, v in payload.items() if k != "messages"},
                    "prompt_chars": len(prompt),
                    "response": result,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        summary = analyse(result, payload)
        summary["case"] = name
        summary["record_id"] = record_id
        summary["prompt_chars"] = len(prompt)
        results.append(summary)
        print(
            f"{name}: HTTP {summary['http_status']}, content {summary['content_len']} Zeichen, "
            f"finish {summary['finish_reason'] or '-'}, completion_tokens "
            f"{summary['completion_tokens']}"
        )
        time.sleep(1.0)

    out_path = OUT / "glm_diagnostic.json"
    existing: list[dict] = []
    if args.budget and out_path.exists():
        existing = json.loads(out_path.read_text(encoding="utf-8")).get("cases", [])
    results = existing + results

    payload_out = {
        "diagnostic_id": "glm_diagnostic_20261113",
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "model_requested": MODEL,
        "backend": "tudagpt",
        "api_base": base,
        "data": "dev_input.jsonl records 120 und 233; kein Cross-Validation-Artikel",
        "model_used": True,
        "network_used": True,
        "cases": results,
    }
    out_path.write_text(
        json.dumps(payload_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# GLM-5.3-Diagnose",
        "",
        f"Stand: {payload_out['created'][:10]}",
        f"Modell angefragt: `{MODEL}`, Backend TUDaGPT, Daten: Dev-Records 120 und 233.",
        "",
        "| Fall | HTTP | content | finish_reason | completion_tokens | reasoning |",
        "|---|---:|---:|---|---:|---:|",
    ]
    for row in results:
        lines.append(
            f"| {row['case']} | {row['http_status']} | {row['content_len']} | "
            f"{row['finish_reason'] or '-'} | {row['completion_tokens']} | "
            f"{row['reasoning_len']} |"
        )
    lines.append("")
    (OUT / "glm_diagnostic.md").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
