#!/usr/bin/env python3
"""Erzeugt ``dataset_manifest.json`` fuer das Cross-Validation-Experiment.

Das Manifest ist ein Entwurf, solange die Referenzannotation fehlt. Es haelt
Artikel, Hashes, Reservierung und die geprueften Disjunktheiten fest, damit
vor dem Freeze nichts stillschweigend veraendert werden kann.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parents[1]
ROOT = BENCH_ROOT.parent
OUT_DIR = BENCH_ROOT / "evaluation" / "multi_model_cross_validation"
P0_DIR = BENCH_ROOT / "evaluation" / "c1_pilot" / "holdout_p0_20261112"
MANIFEST = OUT_DIR / "dataset_manifest.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pmcids(path: Path) -> set[str]:
    return {
        json.loads(line)["pmcid"]
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def main() -> int:
    selection = json.loads((OUT_DIR / "candidate_shortlist_v2.json").read_text(encoding="utf-8"))
    availability = {
        row["pmcid"]: row
        for row in json.loads((OUT_DIR / "fulltext_availability_v1.json").read_text(encoding="utf-8"))[
            "records"
        ]
    }
    g5 = json.loads((P0_DIR / "fulltext_retrieval_manifest_v1.json").read_text(encoding="utf-8"))
    g5_ids = {row["pmcid"] for row in g5["records"]}
    review_path = OUT_DIR / "crossval_eligibility_review_v1.json"
    eligibility = {}
    if review_path.exists():
        review = json.loads(review_path.read_text(encoding="utf-8"))
        eligibility = {row["pmcid"]: row["classification"] for row in review["articles"]}
    yun = set()
    for name in ("yun_c1_frozen_275.jsonl", "yun_c1_dev_26.jsonl", "yun_c1_test_249.jsonl"):
        yun |= pmcids(BENCH_ROOT / "processed_data" / name)

    articles = []
    for row in selection["articles"]:
        record = availability[row["pmcid"]]
        local = ROOT / record["local_path"]
        articles.append(
            {
                "position": row["position"],
                "role": row["role"],
                "pmcid": row["pmcid"],
                "doi": record.get("doi") or "",
                "reserved_for": row.get("reserved_for", "crossval_exploration"),
                "source_document": record["local_path"],
                "input_sha256": record["sha256"],
                "file_sha256_now": sha256_file(local) if local.exists() else "",
                "eligibility": eligibility.get(row["pmcid"], "not_reviewed"),
            }
        )

    selected = {row["pmcid"] for row in articles}
    schema_hash = sha256_file(OUT_DIR / "schema_v1.json")
    payload = {
        "dataset_id": "crossval_exploration_v1",
        "created": date.today().isoformat(),
        "status": "draft_pending_annotation",
        "model_used": False,
        "purpose": "unabhaengiger Explorationsdatensatz fuer die Multi-Model-Cross-Validation",
        "article_counts": {
            "primary": sum(1 for row in articles if row["role"] == "primary"),
            "reserve": sum(1 for row in articles if row["role"] == "reserve"),
        },
        "target_records": [60, 80],
        "records": None,
        "record_count_note": "wird nach der Referenzannotation gesetzt, nicht geschaetzt",
        "reference": {
            "path": None,
            "sha256": None,
            "status": "pending",
            "annotators": [],
            "independent_second_annotator": None,
        },
        "schema": {"path": "schema_v1.json", "sha256": schema_hash},
        "prompt": {
            "path": None,
            "sha256": None,
            "status": "not_created",
            "note": "Prompt fuer Arm-Extraktion nach schema_v1 ist noch nicht eingefroren",
        },
        "models": {
            "qwen": {"id": "gwdg/qwen3.5-397b-a17b", "role": "arm_a_and_adjudicator"},
            "deepseek": {"id": "gwdg/deepseek-v4.1-flash-1017", "role": "arm_b"},
            "glm": {
                "id": "gwdg/glm-5.3",
                "role": "arm_c",
                "status": "usable_with_larger_max_tokens",
                "required_max_tokens": 8000,
            },
        },
        "disjointness": {
            "g5_shortlist": sorted(g5_ids),
            "g5_overlap": sorted(selected & g5_ids),
            "yun_articles": len(yun),
            "yun_overlap": sorted(selected & yun),
            "verified": not (selected & g5_ids) and not (selected & yun),
        },
        "freeze": {
            "frozen": False,
            "reason": "Referenzannotation und Prompt fehlen; kein Freeze vor deren Abschluss",
        },
        "articles": articles,
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Artikel {payload['article_counts']}, Disjunktheit {payload['disjointness']['verified']}, "
        f"Schema-Hash {schema_hash[:16]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
