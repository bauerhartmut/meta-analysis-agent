"""C1-Release-Manifest fuer den eingefrorenen v6c-Kandidaten bauen.

Das Manifest pinnt Kandidat, Freeze, Testprojektion, Runner-/Prompt-Hashes und
den Verifikationsbericht. Es autorisiert keinen Testlauf: Der Testlauf bleibt
bis zu einer separaten ausdruecklichen Freigabe gesperrt.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BENCH_ROOT.parent
PILOT_ROOT = BENCH_ROOT / "evaluation" / "c1_pilot"
RELEASE_PATH = PILOT_ROOT / "release_v6c.json"
HASH_PATH = PILOT_ROOT / "release_v6c.sha256"

FROZEN_PATH = BENCH_ROOT / "processed_data" / "yun_c1_frozen_275.jsonl"
TEST_PATH = BENCH_ROOT / "processed_data" / "yun_c1_test_249.jsonl"
FREEZE_MANIFEST = BENCH_ROOT / "validation" / "c1_freeze_manifest.json"

DEV_RUN = PILOT_ROOT / "runs" / "c1_dev_20261111_v6c"
TEST_PROJECTION_DIR = PILOT_ROOT / "test_locked"
TEST_PROJECTION_MANIFEST = TEST_PROJECTION_DIR / "test_projection_manifest.json"
TEST_INPUT = TEST_PROJECTION_DIR / "test_input.jsonl"
TEST_REFERENCE = TEST_PROJECTION_DIR / "test_reference.jsonl"
VERIFICATION = PILOT_ROOT / "test_projection_verification.json"
TEST_RUNS = PILOT_ROOT / "runs_test"

CODE_FILES = {
    "prompt_and_dev_runner": BENCH_ROOT / "scripts" / "run_c1_dev_pilot.py",
    "dev_evaluator": BENCH_ROOT / "scripts" / "evaluate_c1_dev_pilot.py",
    "test_projection": BENCH_ROOT / "scripts" / "c1_test_projection.py",
    "test_runner": BENCH_ROOT / "scripts" / "run_c1_test_pilot.py",
    "test_evaluator": BENCH_ROOT / "scripts" / "evaluate_c1_test_pilot.py",
    "test_projection_verifier": BENCH_ROOT / "scripts" / "verify_c1_test_projection.py",
    "test_isolation_check": BENCH_ROOT / "scripts" / "check_c1_test_isolation.py",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    return str(path.relative_to(BENCH_ROOT)).replace("\\", "/")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def main() -> int:
    for path in (
        FROZEN_PATH, TEST_PATH, FREEZE_MANIFEST, TEST_PROJECTION_MANIFEST,
        TEST_INPUT, TEST_REFERENCE, VERIFICATION,
        DEV_RUN / "run_manifest.json", DEV_RUN / "dev_evaluation.json",
        *CODE_FILES.values(),
    ):
        require(path.exists(), f"fehlt: {path}")

    freeze = load_json(FREEZE_MANIFEST)
    dev_run = load_json(DEV_RUN / "run_manifest.json")
    dev_eval = load_json(DEV_RUN / "dev_evaluation.json")
    projection = load_json(TEST_PROJECTION_MANIFEST)
    verification = load_json(VERIFICATION)

    require(freeze["test_policy"]["locked"] is True, "Test-Policy ist nicht locked")
    require(freeze["files"]["processed_data/yun_c1_test_249.jsonl"]["sha256"]
            == sha256_file(TEST_PATH), "Test-249-Hash weicht vom Freeze ab")
    require(freeze["files"]["processed_data/yun_c1_frozen_275.jsonl"]["sha256"]
            == sha256_file(FROZEN_PATH), "275er-Hash weicht vom Freeze ab")

    require(dev_run["run_id"] == "c1_dev_20261111_v6c", "falscher Dev-Run")
    require(dev_run["test_split_used"] is False, "Dev-Run hat Testsplit verwendet")
    require(dev_run["reference_loaded"] is False, "Dev-Run hat Referenz geladen")
    require((dev_eval["exact_fields"], dev_eval["expected_fields_present"],
             dev_eval["wrong_fields"], dev_eval["missing_fields"]) == (140, 140, 0, 0),
            "v6c ist nicht 140/140")
    require(not dev_eval["errors"], "v6c hat Evaluationsfehler")

    require(verification["status"] == "passed", "Projektionsprüfung nicht bestanden")
    require(all(check["passed"] for check in verification["checks"]),
            "mindestens ein Projektionscheck fehlgeschlagen")
    require(projection["input_sha256"] == sha256_file(TEST_INPUT),
            "Test-Input-Hash weicht vom Projektionsmanifest ab")
    require(projection["reference_sha256"] == sha256_file(TEST_REFERENCE),
            "Test-Referenz-Hash weicht vom Projektionsmanifest ab")
    require(projection["records"] == 249 and projection["articles"] == 64,
            "Projektionszahlen weichen ab")

    test_run_present = any(TEST_RUNS.glob("*/test_manifest.json")) if TEST_RUNS.exists() else False
    require(not test_run_present, "Es existiert bereits ein Testlauf-Manifest")

    manifest = {
        "release_version": 1,
        "release_id": "c1-v6c-20261111",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "status": "candidate_locked_pending_test_approval",
        "test_run_approved": False,
        "test_run_started": False,
        "code_commit": git_commit(),
        "candidate": {
            "run_id": dev_run["run_id"],
            "prompt_version": dev_run["prompt_version"],
            "model": dev_run["model"],
            "temperature": dev_run["temperature"],
            "max_tokens": dev_run["max_tokens"],
            "concurrency": dev_run["concurrency"],
            "prompt_sha256_all": dev_run["prompt_sha256_all"],
            "model_config_sha256": dev_run["model_config_sha256"],
            "input_sha256": dev_run["input_sha256"],
            "output_sha256": dev_run["output_sha256"],
            "raw_sha256": dev_run["raw_sha256"],
            "dev_evaluation_sha256": sha256_file(DEV_RUN / "dev_evaluation.json"),
            "dev_metrics": {
                "records": dev_eval["records"],
                "exact_fields": dev_eval["exact_fields"],
                "expected_fields": dev_eval["expected_fields_total"],
                "coverage": dev_eval["coverage"],
                "wrong_fields": dev_eval["wrong_fields"],
                "missing_fields": dev_eval["missing_fields"],
                "hallucinated_fields": dev_eval["hallucinated_fields"],
                "mae": dev_eval["mae_paired_all"],
            },
        },
        "data": {
            "freeze_275": {
                "path": rel(FROZEN_PATH),
                "sha256": sha256_file(FROZEN_PATH),
                "records": freeze["counts"]["records"],
            },
            "test_249": {
                "path": rel(TEST_PATH),
                "sha256": sha256_file(TEST_PATH),
                "records": freeze["splits"]["test"]["records"],
                "articles": freeze["splits"]["test"]["articles"],
                "by_type": freeze["splits"]["test"]["by_type"],
            },
            "dev_input": {
                "path": rel(PILOT_ROOT / "dev_input.jsonl"),
                "sha256": sha256_file(PILOT_ROOT / "dev_input.jsonl"),
            },
            "dev_reference": {
                "path": rel(PILOT_ROOT / "dev_reference.jsonl"),
                "sha256": sha256_file(PILOT_ROOT / "dev_reference.jsonl"),
            },
        },
        "test_projection": {
            "input_path": rel(TEST_INPUT),
            "input_sha256": sha256_file(TEST_INPUT),
            "reference_path": rel(TEST_REFERENCE),
            "reference_sha256": sha256_file(TEST_REFERENCE),
            "records": projection["records"],
            "articles": projection["articles"],
            "by_type": projection["by_type"],
            "expected_fields": 1308,
            "verification_path": rel(VERIFICATION),
            "verification_sha256": sha256_file(VERIFICATION),
            "verification_status": verification["status"],
            "verification_checks": len(verification["checks"]),
        },
        "code": {
            name: {"path": rel(path), "sha256": sha256_file(path)}
            for name, path in CODE_FILES.items()
        },
        "gates": {
            "B1_test_runner": True,
            "B2_test_input_separate_reference": True,
            "B3_dev_only_overrides": True,
            "B4_release_manifest": True,
            "B5_projection_independently_verified": True,
            "explicit_test_approval": False,
        },
        "test_plan": {
            "records": 249,
            "expected_fields": 1308,
            "primary_metric": "exact_fields / 1308",
            "status": "not_started",
            "approval_reference": None,
        },
        "note": (
            "Dieses Manifest autorisiert keinen Testlauf. Der Testlauf braucht "
            "eine separate ausdrueckliche Freigabe; die Testprojektion bleibt "
            "lokal und ist nicht versioniert."
        ),
    }

    RELEASE_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with HASH_PATH.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"{sha256_file(RELEASE_PATH)}  {rel(RELEASE_PATH)}\n")
    print(
        f"Release: {manifest['release_id']} status={manifest['status']} "
        f"test_approved={manifest['test_run_approved']}"
    )
    print(f"Test-Input: {manifest['test_projection']['input_sha256']}")
    print(f"Test-Referenz: {manifest['test_projection']['reference_sha256']}")
    print(f"Manifest: {RELEASE_PATH}")
    print(f"Hash: {HASH_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
