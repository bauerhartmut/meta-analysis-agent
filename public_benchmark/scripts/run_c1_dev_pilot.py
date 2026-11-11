"""C1-Dev-Pilot: 26 eingefrorene Yun-Records extrahieren.

Der Lauf liest ausschliesslich ``dev_input.jsonl`` und die dort referenzierten
öffentlichen Artikeltexte. ``dev_reference.jsonl`` wird in diesem Skript nicht
geladen. Jede Modellantwort wird roh gesichert, bevor sie geparst wird.

Aufruf:
    PYTHONIOENCODING=utf-8 .venv/bin/python.exe \
        public_benchmark/scripts/run_c1_dev_pilot.py --run-id c1_dev_20261111

Prompt-Versionen:
    v1  historischer Prompt ohne Zeitpunktregel (reproduziert den ersten Lauf)
    v2  verbindliche C1-Zeitpunktregel (Standard)

Ein vorhandener Run wird nur mit ``--resume`` fortgesetzt.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BENCH_ROOT.parent
sys.path.insert(0, str(REPO_ROOT))

from research_agent.llm.engine import LLMEngine  # noqa: E402

INPUT_PATH = BENCH_ROOT / "evaluation" / "c1_pilot" / "dev_input.jsonl"
OUTPUT_ROOT = BENCH_ROOT / "evaluation" / "c1_pilot" / "runs"
PROMPT_VERSIONS = ("v1", "v2")
PROMPT_VERSION_IDS = {
    "v1": "c1-dev-extract-v1",
    "v2": "c1-dev-extract-v2",
}
DEFAULT_PROMPT_VERSION = "v2"
TEMPERATURE = 0.0
MAX_TOKENS = 900
CONCURRENCY = 3

SYSTEM_PROMPT_V1 = """You are a precise data extractor for a meta-analysis benchmark.

Extract only the aggregate arm-level values that the supplied article reports
for exactly the requested intervention, comparator and outcome.

Hard rules:
- Use only the supplied text. Do not use outside knowledge and do not infer,
  recalculate, pool, or complete missing values.
- If a value is not explicitly reported for that arm and outcome, return null.
- Never substitute a baseline value, a change score, a median, a percentage, or
  another outcome for a missing mean, SD, count, or group size.
- intervention_n and comparator_n are the analysed group sizes for this outcome.
- For a continuous outcome, report the two means and two standard deviations and
  return null for both event counts.
- For a binary outcome, report the two event counts and the two analysed group
  sizes, and return null for all means and standard deviations.
- source_note is a short quote or a precise table/location reference (at most 30
  words). It must not contain reasoning.
- Return exactly one JSON object with every key below, using JSON null where a
  value is not reported. No markdown, no code fence, no additional prose."""

SYSTEM_PROMPT_V2 = SYSTEM_PROMPT_V1 + """

TIMEPOINT RULE (mandatory):
- If the ICO names a timepoint, use that timepoint.
- Otherwise use the immediate post-test: the first measurement after the
  intervention that is not labelled as follow-up.
- If the post-test is not reported for both arms, use the earliest follow-up
  for which both arms are fully reported.
- Never use baseline, change, peak, or mixed timepoints. Both arms must come
  from the same timepoint and the same outcome definition.
- Name the chosen timepoint and the table/row in source_note."""

SYSTEM_PROMPTS = {
    "v1": SYSTEM_PROMPT_V1,
    "v2": SYSTEM_PROMPT_V2,
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def resolve_source(path_text: str) -> Path:
    """Quellenpfade sind ab Repo-Wurzel gespeichert, nicht ab public_benchmark."""
    candidate = REPO_ROOT / path_text
    if candidate.exists():
        return candidate
    candidate = BENCH_ROOT / path_text
    if candidate.exists():
        return candidate
    raise FileNotFoundError(path_text)


def render_prompt(record: dict[str, Any], source_text: str,
                  prompt_version: str = DEFAULT_PROMPT_VERSION) -> str:
    if prompt_version not in PROMPT_VERSIONS:
        raise ValueError(f"Unbekannte Prompt-Version: {prompt_version}")
    ico = record["ico"]
    outcome_type = record["outcome_type"]
    if outcome_type == "continuous":
        schema = {
            "record_id": record["record_id"],
            "outcome_type": "continuous",
            "intervention_n": None,
            "comparator_n": None,
            "intervention_mean": None,
            "intervention_sd": None,
            "comparator_mean": None,
            "comparator_sd": None,
            "intervention_events": None,
            "comparator_events": None,
            "source_note": "",
        }
    elif outcome_type == "binary":
        schema = {
            "record_id": record["record_id"],
            "outcome_type": "binary",
            "intervention_n": None,
            "comparator_n": None,
            "intervention_mean": None,
            "intervention_sd": None,
            "comparator_mean": None,
            "comparator_sd": None,
            "intervention_events": None,
            "comparator_events": None,
            "source_note": "",
        }
    else:
        raise ValueError(f"Unbekannter outcome_type: {outcome_type}")

    timepoint_section = ""
    if prompt_version == "v2":
        timepoint_section = """
TIMEPOINT
Apply the mandatory timepoint rule from the system message. State the chosen
timepoint in source_note.
"""

    return f"""TASK
Extract the arm-level result for this record.

record_id: {record["record_id"]}
outcome_type: {outcome_type}
Intervention: {ico["intervention"]}
Comparator: {ico["comparator"]}
Outcome: {ico["outcome"]}
{timepoint_section}
Required JSON object (same keys, values filled or null):
{json.dumps(schema, ensure_ascii=False, indent=2)}

ARTICLE TEXT
--- BEGIN ARTICLE ---
{source_text}
--- END ARTICLE ---
"""


def hash_model_config(llm: LLMEngine, prompt_version: str) -> str:
    config = {
        "backend": getattr(llm, "_backend", ""),
        "model": getattr(llm, "_tudagpt_model", ""),
        "prompt_version": PROMPT_VERSION_IDS[prompt_version],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }
    return sha256_text(json.dumps(config, sort_keys=True, ensure_ascii=False))


def parse_model_json(raw: str) -> tuple[dict[str, Any] | None, str]:
    """Parst die Modellantwort ohne inhaltliche Reparatur."""
    if raw.startswith("[ERROR:"):
        return None, raw.strip()
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            return None, "kein JSON-Objekt in der Antwort"
        try:
            parsed = json.loads(text[start:end + 1])
        except json.JSONDecodeError as exc:
            return None, f"{type(exc).__name__}: {exc}"
    if not isinstance(parsed, dict):
        return None, f"JSON-Toptyp ist {type(parsed).__name__}, nicht object"
    return parsed, ""


NUMBER_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")


def clean_number(value: Any) -> int | float | None:
    """Akzeptiert nur echte Zahlen; keine Prozente, Bereiche oder Textzahlen."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        if number != number or number in (float("inf"), float("-inf")):
            return None
        return int(number) if number.is_integer() else number
    if isinstance(value, str):
        text = value.strip().replace(" ", "")
        if not NUMBER_RE.fullmatch(text):
            return None
        number = float(text)
        return int(number) if number.is_integer() else number
    return None


def normalize_row(record: dict[str, Any], parsed: dict[str, Any],
                  parse_error: str) -> dict[str, Any]:
    if parse_error:
        return {
            "record_id": record["record_id"],
            "outcome_type": record["outcome_type"],
            "intervention_n": None,
            "comparator_n": None,
            "intervention_mean": None,
            "intervention_sd": None,
            "comparator_mean": None,
            "comparator_sd": None,
            "intervention_events": None,
            "comparator_events": None,
            "source_note": "MODEL_OUTPUT_UNPARSEABLE",
            "_parse_error": parse_error,
        }

    note = parsed.get("source_note")
    if not isinstance(note, str):
        note = "" if note is None else str(note)
    row = {
        "record_id": record["record_id"],
        "outcome_type": record["outcome_type"],
        "intervention_n": clean_number(parsed.get("intervention_n")),
        "comparator_n": clean_number(parsed.get("comparator_n")),
        "intervention_mean": clean_number(parsed.get("intervention_mean")),
        "intervention_sd": clean_number(parsed.get("intervention_sd")),
        "comparator_mean": clean_number(parsed.get("comparator_mean")),
        "comparator_sd": clean_number(parsed.get("comparator_sd")),
        "intervention_events": clean_number(parsed.get("intervention_events")),
        "comparator_events": clean_number(parsed.get("comparator_events")),
        "source_note": note.strip()[:500],
    }
    if parsed.get("outcome_type") != record["outcome_type"]:
        row["_parse_error"] = (
            "outcome_type im Modell-JSON weicht ab: "
            f"{parsed.get('outcome_type')!r}"
        )
    return row


async def run_one(record: dict[str, Any], llm: LLMEngine,
                  semaphore: asyncio.Semaphore,
                  prompt_version: str) -> dict[str, Any]:
    source_path = resolve_source(record["source_text_path"])
    source_text = source_path.read_text(encoding="utf-8", errors="replace")
    prompt = render_prompt(record, source_text, prompt_version)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPTS[prompt_version]},
        {"role": "user", "content": prompt},
    ]

    started = time.monotonic()
    async with semaphore:
        raw = await llm.chat(
            messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            format_json=True,
        )
    elapsed = round(time.monotonic() - started, 2)

    parsed, parse_error = parse_model_json(raw)
    if parsed is None:
        row = normalize_row(record, {}, parse_error)
    else:
        row = normalize_row(record, parsed, "")
    return {
        "record_id": record["record_id"],
        "prompt_sha256": sha256_text(prompt),
        "source_chars": len(source_text),
        "latency_s": elapsed,
        "raw_response": raw,
        "parse_error": row.pop("_parse_error", ""),
        "row": row,
    }


def write_jsonl_atomic(path: Path, rows: list[dict[str, Any]]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    tmp.replace(path)


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="c1_dev_20261111_v2")
    parser.add_argument("--prompt-version", choices=PROMPT_VERSIONS,
                        default=DEFAULT_PROMPT_VERSION)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    records = load_jsonl(INPUT_PATH)
    if len(records) != 26:
        print(f"ABBRUCH: {len(records)} statt 26 Dev-Records")
        return 2
    if any(record.get("split") != "dev" for record in records):
        print("ABBRUCH: Nicht-Dev-Record in dev_input.jsonl")
        return 2

    run_dir = OUTPUT_ROOT / args.run_id
    output_path = run_dir / "dev_output.jsonl"
    raw_path = run_dir / "dev_raw.jsonl"
    manifest_path = run_dir / "run_manifest.json"

    if run_dir.exists() and not args.resume:
        print(f"ABBRUCH: {run_dir} existiert bereits; nutze --resume")
        return 2
    run_dir.mkdir(parents=True, exist_ok=True)

    done_rows: list[dict[str, Any]] = []
    done_raw: list[dict[str, Any]] = []
    if args.resume and output_path.exists():
        done_rows = load_jsonl(output_path)
        done_raw = load_jsonl(raw_path)
    completed = {int(row["record_id"]) for row in done_rows}
    pending = [record for record in records if int(record["record_id"]) not in completed]

    llm = LLMEngine()
    if not await llm.health_check():
        print(f"ABBRUCH: Backend nicht erreichbar: {LLMEngine.last_failure()}")
        await llm.close()
        return 3

    model = getattr(llm, "_tudagpt_model", "")
    manifest = {
        "run_id": args.run_id,
        "prompt_version": PROMPT_VERSION_IDS[args.prompt_version],
        "backend": getattr(llm, "_backend", ""),
        "model": model,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "concurrency": CONCURRENCY,
        "input_path": str(INPUT_PATH.relative_to(BENCH_ROOT)).replace("\\", "/"),
        "input_sha256": sha256_file(INPUT_PATH),
        "model_config_sha256": hash_model_config(llm, args.prompt_version),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "reference_loaded": False,
        "test_split_used": False,
        "status": "running",
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    semaphore = asyncio.Semaphore(CONCURRENCY)
    print(
        f"Start: {len(pending)} offen, {len(completed)} erledigt, "
        f"Prompt {PROMPT_VERSION_IDS[args.prompt_version]}, Modell {model}"
    )
    try:
        for offset in range(0, len(pending), CONCURRENCY):
            batch = pending[offset:offset + CONCURRENCY]
            results = await asyncio.gather(
                *(run_one(record, llm, semaphore, args.prompt_version)
                  for record in batch)
            )
            for result in results:
                done_raw.append(result)
                done_rows.append(result["row"])
                print(
                    f"  {result['record_id']}: {result['latency_s']}s, "
                    f"{len(result['raw_response'])} Zeichen, "
                    f"parse={'ok' if not result['parse_error'] else 'FEHLER'}"
                )
            order = {int(record["record_id"]): index for index, record in enumerate(records)}
            done_rows.sort(key=lambda row: order[int(row["record_id"])])
            done_raw.sort(key=lambda row: order[int(row["record_id"])])
            write_jsonl_atomic(output_path, done_rows)
            write_jsonl_atomic(raw_path, done_raw)
    finally:
        await llm.close()

    parse_errors = [row for row in done_raw if row.get("parse_error")]
    manifest.update({
        "status": "completed" if len(done_rows) == 26 else "incomplete",
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "completed_records": len(done_rows),
        "parse_errors": len(parse_errors),
        "parse_error_record_ids": [row["record_id"] for row in parse_errors],
        "output_sha256": sha256_file(output_path),
        "raw_sha256": sha256_file(raw_path),
        "prompt_sha256_all": sha256_text(
            "\n".join(row["prompt_sha256"] for row in done_raw)
        ),
    })
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Fertig: {len(done_rows)}/26, Parse-Fehler {len(parse_errors)}")
    print(f"Ausgabe: {output_path}")
    return 0 if len(done_rows) == 26 else 4


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
