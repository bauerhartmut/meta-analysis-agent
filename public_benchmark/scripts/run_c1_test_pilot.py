"""C1-Test-Pilot: 249 gesperrte Test-Records extrahieren.

Der Runner liest ausschliesslich ``test_locked/test_input.jsonl`` und die
dort referenzierten Artikeltexte. ``test_reference.jsonl`` wird weder
importiert noch geoeffnet. Der Lauf startet nur mit ``--approve-test``.

Aufruf:
    PYTHONIOENCODING=utf-8 .venv/bin/python.exe \
        public_benchmark/scripts/run_c1_test_pilot.py \
        --approve-test --run-id c1_test_20261111_v6c
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
PILOT_ROOT = BENCH_ROOT / "evaluation" / "c1_pilot"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from c1_test_projection import validate_test_input  # noqa: E402
from run_c1_dev_pilot import (  # noqa: E402
    CONCURRENCY,
    DEFAULT_PROMPT_VERSION,
    MAX_TOKENS,
    PROMPT_VERSION_IDS,
    PROMPT_VERSIONS,
    SYSTEM_PROMPTS,
    TEMPERATURE,
    LLMEngine,
    hash_model_config,
    load_jsonl,
    run_one,
    sha256_file,
    sha256_text,
    write_jsonl_atomic,
)

TEST_INPUT_PATH = PILOT_ROOT / "test_locked" / "test_input.jsonl"
TEST_PROJECTION_MANIFEST = PILOT_ROOT / "test_locked" / "test_projection_manifest.json"
TEST_OUTPUT_ROOT = PILOT_ROOT / "runs_test"
EXPECTED_TEST_RECORDS = 249


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="c1_test_20261111_v6c")
    parser.add_argument("--prompt-version", choices=PROMPT_VERSIONS,
                        default=DEFAULT_PROMPT_VERSION)
    parser.add_argument("--approve-test", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    if not args.approve_test:
        print("ABBRUCH: Testlauf nur mit ausdruecklichem --approve-test.")
        print("Der Testsplit wurde nicht geoeffnet.")
        return 2

    if not TEST_INPUT_PATH.exists() or not TEST_PROJECTION_MANIFEST.exists():
        print(f"ABBRUCH: Testprojektion fehlt: {TEST_INPUT_PATH}")
        return 2

    records = load_jsonl(TEST_INPUT_PATH)
    try:
        validate_test_input(records, expected_records=EXPECTED_TEST_RECORDS)
    except ValueError as exc:
        print(f"ABBRUCH: ungueltiger Test-Input: {exc}")
        return 2

    projection = json.loads(TEST_PROJECTION_MANIFEST.read_text(encoding="utf-8"))
    input_sha = sha256_file(TEST_INPUT_PATH)
    if projection.get("input_sha256") != input_sha:
        print("ABBRUCH: Test-Input-Hash weicht vom Projektionsmanifest ab.")
        return 2
    if projection.get("records") != EXPECTED_TEST_RECORDS:
        print("ABBRUCH: Projektionsmanifest meldet nicht 249 Records.")
        return 2

    run_dir = TEST_OUTPUT_ROOT / args.run_id
    output_path = run_dir / "test_output.jsonl"
    raw_path = run_dir / "test_raw.jsonl"
    manifest_path = run_dir / "test_manifest.json"
    runner_sha = sha256_file(Path(__file__))

    if run_dir.exists() and not args.resume:
        print(f"ABBRUCH: {run_dir} existiert bereits; nutze --resume")
        return 2
    if args.resume and not manifest_path.exists():
        print(f"ABBRUCH: Kein Resume-Manifest in {run_dir}")
        return 2

    done_rows: list[dict[str, Any]] = []
    done_raw: list[dict[str, Any]] = []
    previous_manifest: dict[str, Any] = {}
    if args.resume:
        previous_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for key, expected in (
            ("input_sha256", input_sha),
            ("runner_sha256", runner_sha),
            ("prompt_version", PROMPT_VERSION_IDS[args.prompt_version]),
            ("test_split_used", True),
            ("reference_loaded", False),
        ):
            if previous_manifest.get(key) != expected:
                print(f"ABBRUCH: Resume-Konfiguration weicht ab: {key}")
                return 2
        if previous_manifest.get("status") == "completed":
            print("ABBRUCH: Lauf ist bereits vollstaendig.")
            return 2
        if output_path.exists():
            done_rows = load_jsonl(output_path)
        if raw_path.exists():
            done_raw = load_jsonl(raw_path)

    run_dir.mkdir(parents=True, exist_ok=True)
    completed = {int(row["record_id"]) for row in done_rows}
    pending = [record for record in records
               if int(record["record_id"]) not in completed]

    llm = LLMEngine()
    if not await llm.health_check():
        print(f"ABBRUCH: Backend nicht erreichbar: {LLMEngine.last_failure()}")
        await llm.close()
        return 3

    model = getattr(llm, "_tudagpt_model", "")
    model_config = hash_model_config(llm, args.prompt_version)
    if args.resume and previous_manifest.get("model_config_sha256") != model_config:
        print("ABBRUCH: Modellkonfiguration weicht vom Resume-Manifest ab.")
        await llm.close()
        return 2

    manifest = {
        "run_id": args.run_id,
        "prompt_version": PROMPT_VERSION_IDS[args.prompt_version],
        "backend": getattr(llm, "_backend", ""),
        "model": model,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "concurrency": CONCURRENCY,
        "input_path": str(TEST_INPUT_PATH.relative_to(BENCH_ROOT)).replace("\\", "/"),
        "input_sha256": input_sha,
        "input_records": len(records),
        "model_config_sha256": model_config,
        "runner_sha256": runner_sha,
        "projection_manifest": str(
            TEST_PROJECTION_MANIFEST.relative_to(BENCH_ROOT)
        ).replace("\\", "/"),
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "approval": "explicit --approve-test",
        "reference_loaded": False,
        "test_split_used": True,
        "status": "running",
    }
    if previous_manifest:
        manifest["resumed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        manifest["created_at"] = previous_manifest.get("created_at", manifest["created_at"])
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
    complete = len(done_rows) == EXPECTED_TEST_RECORDS
    manifest.update({
        "status": "completed" if complete and not parse_errors else "incomplete",
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
    print(f"Fertig: {len(done_rows)}/{EXPECTED_TEST_RECORDS}, Parse-Fehler {len(parse_errors)}")
    print(f"Ausgabe: {output_path}")
    return 0 if complete and not parse_errors else 4


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
