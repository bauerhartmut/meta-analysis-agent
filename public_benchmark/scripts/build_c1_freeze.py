#!/usr/bin/env python3
"""Freeze the curated C1 reference and prepare the dev pilot inputs.

Reads only public_benchmark/validation/yun_audit_410.jsonl. Writes:
- processed_data/yun_c1_frozen_275.jsonl
- processed_data/yun_c1_dev_26.jsonl
- processed_data/yun_c1_test_249.jsonl
- evaluation/c1_pilot/dev_input.jsonl
- evaluation/c1_pilot/dev_reference.jsonl
- validation/c1_freeze_manifest.json

No model call, no network access and no test-set prompt work.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "validation" / "yun_audit_410.jsonl"
PROCESSED = ROOT / "processed_data"
PILOT = ROOT / "evaluation" / "c1_pilot"
MANIFEST = ROOT / "validation" / "c1_freeze_manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def input_record(row: dict) -> dict:
    """Fields visible to the extraction system; reference values are excluded."""
    return {
        "record_id": row["record_id"],
        "study_id": row["study_id"],
        "pmcid": row["pmcid"],
        "split": row["split"],
        "outcome_type": row["outcome_type"],
        "ico": row["ico"],
        "source_text_path": row["source_text_path"],
    }


def reference_record(row: dict) -> dict:
    """Fields kept back for scoring; never pass this file to the model."""
    return {
        "record_id": row["record_id"],
        "study_id": row["study_id"],
        "pmcid": row["pmcid"],
        "split": row["split"],
        "outcome_type": row["outcome_type"],
        "reference_values": row["reference_values"],
        "curated_values": row["curated_values"],
        "audit_status": row["audit_status"],
        "audit_reason": row["audit_reason"],
        "correction": row.get("correction"),
    }


def counts(rows: list[dict]) -> dict:
    return {
        "records": len(rows),
        "articles": len({row["pmcid"] for row in rows}),
        "by_type": dict(Counter(row["outcome_type"] for row in rows)),
        "by_status": dict(Counter(row["audit_status"] for row in rows)),
    }


def main() -> None:
    audit_rows = [
        json.loads(line)
        for line in AUDIT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    usable = sorted(
        (row for row in audit_rows if row.get("usable_for_c1") is True),
        key=lambda row: row["record_id"],
    )
    if len(usable) != 275:
        raise SystemExit(f"expected 275 usable records, got {len(usable)}")
    dev = [row for row in usable if row["split"] == "dev"]
    test = [row for row in usable if row["split"] == "test"]
    if len(dev) != 26 or len(test) != 249:
        raise SystemExit(f"unexpected split sizes: dev={len(dev)}, test={len(test)}")

    frozen_path = PROCESSED / "yun_c1_frozen_275.jsonl"
    dev_path = PROCESSED / "yun_c1_dev_26.jsonl"
    test_path = PROCESSED / "yun_c1_test_249.jsonl"
    dev_input_path = PILOT / "dev_input.jsonl"
    dev_reference_path = PILOT / "dev_reference.jsonl"

    write_jsonl(frozen_path, usable)
    write_jsonl(dev_path, dev)
    write_jsonl(test_path, test)
    write_jsonl(dev_input_path, [input_record(row) for row in dev])
    write_jsonl(dev_reference_path, [reference_record(row) for row in dev])

    audit_sha = sha256(AUDIT)
    manifest = {
        "freeze_version": 1,
        "created_at": date.today().isoformat(),
        "source": "Yun et al. 2024",
        "source_commit": "1bc768d4d098c727c9866eeff909297c38a3e84c",
        "audit_source": {
            "path": "validation/yun_audit_410.jsonl",
            "sha256": audit_sha,
            "records": len(audit_rows),
        },
        "status": "frozen_pilot_prepared_not_started",
        "counts": counts(usable),
        "splits": {
            "dev": counts(dev),
            "test": counts(test),
        },
        "files": {
            str(path.relative_to(ROOT)): {
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
                "records": len(rows),
            }
            for path, rows in [
                (frozen_path, usable),
                (dev_path, dev),
                (test_path, test),
                (dev_input_path, dev),
                (dev_reference_path, dev),
            ]
        },
        "pilot": {
            "status": "prepared_not_run",
            "input": "evaluation/c1_pilot/dev_input.jsonl",
            "reference": "evaluation/c1_pilot/dev_reference.jsonl",
            "records": len(dev),
            "articles": len({row["pmcid"] for row in dev}),
            "model_run": False,
            "network_run": False,
            "approval_required": True,
        },
        "test_policy": {
            "path": "processed_data/yun_c1_test_249.jsonl",
            "locked": True,
            "used_for_prompt_optimization": False,
            "usage": "Only after a frozen dev protocol and explicit test approval.",
        },
    }
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
