#!/usr/bin/env python3
"""Baut den externen Validierungssatz (Stufe 1) aus vorhandenen Goldstandards.

Vereinheitlicht European Urology (104 Records, Arme bekannt) und GLASS
TrialReviewBench study results (81 Records, Felder heterogen) zu einem
Record-Format mit Zellen:

    {"record_id", "dataset", "study_id", "outcome_label", "cells": [...]}

Jede Zelle hat ``cell_id``, ``label``, ``arm`` (oder ``null``), ``statistic``
und ``value``. Es wird nichts ergaenzt; fehlende Zellen existieren einfach
nicht.

Ausgabe: ``tier1_validation_set_v1.jsonl`` und ``tier1_validation_set_v1.json``.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
CROSSVAL = HERE.parents[2] / "evaluation" / "multi_model_cross_validation"
GOLD = CROSSVAL / "goldstandard_datasets"
EU = GOLD / "eururology_v1" / "records.jsonl"
GLASS = GOLD / "glass_v1" / "original" / "trialreviewbench-study-results-v1.0.0.jsonl.gz"
OUT_JSONL = CROSSVAL / "tier1_validation_set_v1.jsonl"
OUT_MANIFEST = CROSSVAL / "tier1_validation_set_v1.json"

EU_STATISTIC = {"events": "events", "n": "group_size", "mean": "mean", "sd": "sd"}


def eu_records() -> list[dict[str, Any]]:
    records = []
    for line in EU.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        cells = []
        for arm in row["arms"]:
            for key, value in arm.items():
                if key in ("arm_id", "label") or value is None:
                    continue
                cells.append(
                    {
                        "cell_id": f"{arm['arm_id']}.{key}",
                        "label": f"{arm['label']} {key}",
                        "arm": arm["arm_id"],
                        "statistic": EU_STATISTIC.get(key, key),
                        "value": value,
                    }
                )
        records.append(
            {
                "record_id": f"eu::{row['record_id']}",
                "source_record_id": row["record_id"],
                "dataset": "eururology",
                "study_id": row["study_id"],
                "study_ref": row["trial_doi"],
                "outcome_label": row["outcome_label"],
                "outcome_type": row["outcome_type"],
                "cells": cells,
                "provenance": row["provenance"],
            }
        )
    return records


def glass_records() -> list[dict[str, Any]]:
    records = []
    with gzip.open(GLASS, "rt", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            cells = []
            for index, target in enumerate(row["target"].get("rows", [])):
                for key, value in target.items():
                    if not isinstance(value, (int, float)) or isinstance(value, bool):
                        continue
                    cells.append(
                        {
                            "cell_id": f"row{index}.{key}",
                            "label": key,
                            "arm": None,
                            "statistic": key,
                            "value": float(value),
                        }
                    )
            records.append(
                {
                    "record_id": f"glass::{row['id']}",
                    "source_record_id": row["id"],
                    "dataset": "glass_trialreviewbench",
                    "study_id": ",".join(row["input"].get("study_pmids", [])),
                    "study_ref": ",".join(row["input"].get("study_pmids", [])),
                    "outcome_label": row["review_context"].get("outcome", ""),
                    "outcome_type": "mixed",
                    "cells": cells,
                    "provenance": {
                        "source_document": "GLASS v1.0.0 trialreviewbench-study-results",
                        "table_or_section": row["target"].get("worksheet"),
                        "source_cell_or_location": f"{row['target'].get('source_file')} rows {row['target'].get('source_rows')}",
                        "page": None,
                        "text_snippet": None,
                    },
                }
            )
    return records


def main() -> int:
    eu = eu_records()
    glass = glass_records()
    records = eu + glass

    with OUT_JSONL.open("w", encoding="utf-8", newline="\n") as handle:
        for row in records:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    manifest = {
        "set_id": "tier1_validation_set_v1",
        "created": "2026-11-13",
        "purpose": "externe Validierung der numerischen Extraktion ohne neue Annotation",
        "records": len(records),
        "records_by_dataset": {"eururology": len(eu), "glass_trialreviewbench": len(glass)},
        "cells": sum(len(row["cells"]) for row in records),
        "cells_by_dataset": {
            "eururology": sum(len(row["cells"]) for row in eu),
            "glass_trialreviewbench": sum(len(row["cells"]) for row in glass),
        },
        "clusters": {
            "eururology_trials": len({row["study_id"] for row in eu}),
            "glass_publications": len({row["study_id"] for row in glass}),
        },
        "records_without_cells": sum(1 for row in records if not row["cells"]),
        "records_without_arm": sum(
            1 for row in records if any(cell["arm"] is None for cell in row["cells"])
        ),
        "set_sha256": hashlib.sha256(OUT_JSONL.read_bytes()).hexdigest(),
        "sources": {
            "eururology": "goldstandard_datasets/eururology_v1/records.jsonl",
            "glass_trialreviewbench": "goldstandard_datasets/glass_v1/original/trialreviewbench-study-results-v1.0.0.jsonl.gz",
        },
        "note": "GLASS-Zellen haben keinen Armbezug; dort wird nur Label und Wert bewertet.",
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:1200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
