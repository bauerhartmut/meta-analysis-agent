"""Adapter: European-Urology-Goldstandard aus dem OSF-Projekt 8fzps.

Quelle: Yisha et al., BMC Med Res Methodol 2026;26:33, doi
10.1186/s12874-025-02729-5, Daten unter https://osf.io/8fzps/ (vier
Excel-Arbeitsmappen mit den Spalten ``*_rct``).

Die Spalten ``R1_rct``, ``N1_rct``, ``R2_rct``, ``N2_rct`` bzw.
``Mean1_RCT``, ``SD1_RCT``, ``N1_RCT``, ``Mean2_RCT``, ``SD2_RCT``, ``N2_RCT``
sind die vom Autorenteam verifizierten Werte. Die ``*_AI``-Spalten sind
Modellausgaben und werden nicht uebernommen.

Regeln:
- Zeilen ohne Trialname entfallen.
- Gepoolte Zeilen (mehrere Trials in einem Feld, getrennt durch ``;``) sind
  keine Armwerte und entfallen.
- Zeilen mit Regionsuntergruppen bleiben erhalten, werden aber als
  ``subgroup_region`` markiert, weil sie keine Trial-Armwerte sind.
- Fehlende Zellen bleiben ``null``; es wird nichts ergaenzt.
"""

from __future__ import annotations

import hashlib
import json
import unicodedata
from pathlib import Path
from typing import Any

from xlsx_min import header_map, read_sheet

SOURCE = "eururology_osf_8fzps"
HERE = Path(__file__).resolve()
CROSSVAL = HERE.parents[2] / "evaluation" / "multi_model_cross_validation"
OUT_DIR = CROSSVAL / "goldstandard_datasets" / "eururology_v1"
WORKBOOKS = OUT_DIR / "original"

GOLD_BINARY = ("R1_rct", "N1_rct", "R2_rct", "N2_rct")
GOLD_CONTINUOUS = ("Mean1_RCT", "SD1_RCT", "N1_RCT", "Mean2_RCT", "SD2_RCT", "N2_RCT")
META = ("SR name_year", "SR_DOI", "Outcome", "Intervention", "Control", "RCT name_year")


def as_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return None


def clean(text: str) -> str:
    return unicodedata.normalize("NFC", text).strip()


def record_id(payload: dict[str, Any]) -> str:
    key = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def read_workbook(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    binary_rows = read_sheet(path, 1)
    continuous_rows = read_sheet(path, 2)
    return (
        parse_sheet(binary_rows, "binary", path.name),
        parse_sheet(continuous_rows, "continuous", path.name),
    )


def parse_sheet(rows: list[dict[str, str]], outcome_type: str, workbook: str) -> list[dict[str, Any]]:
    if not rows:
        return []
    header = header_map(rows[0])
    required = [name for name in META if name in header]
    if len(required) < len(META):
        missing = sorted(set(META) - set(required))
        raise ValueError(f"{workbook}: Spalten fehlen: {missing}")

    parsed: list[dict[str, Any]] = []
    for row in rows[1:]:
        trial_raw = clean(row.get(header["RCT name_year"], ""))
        if not trial_raw:
            continue
        pooled = ";" in trial_raw or "\uff1b" in trial_raw
        outcome = clean(row.get(header["Outcome"], ""))
        if pooled:
            parsed.append(
                {
                    "skipped": "pooled_row",
                    "reason": "mehrere Trials in einem Feld, kein Armwert",
                    "trial_name_raw": trial_raw,
                    "outcome_label": outcome,
                    "workbook": workbook,
                }
            )
            continue
        if outcome_type == "binary":
            values = {name: as_float(row.get(header[name], "")) for name in GOLD_BINARY}
            arms = [
                {"arm_id": "arm_1", "n": values["N1_rct"], "events": values["R1_rct"]},
                {"arm_id": "arm_2", "n": values["N2_rct"], "events": values["R2_rct"]},
            ]
        else:
            values = {name: as_float(row.get(header[name], "")) for name in GOLD_CONTINUOUS}
            arms = [
                {
                    "arm_id": "arm_1",
                    "n": values["N1_RCT"],
                    "mean": values["Mean1_RCT"],
                    "sd": values["SD1_RCT"],
                },
                {
                    "arm_id": "arm_2",
                    "n": values["N2_RCT"],
                    "mean": values["Mean2_RCT"],
                    "sd": values["SD2_RCT"],
                },
            ]
        missing = [name for name, value in values.items() if value is None]
        if len(missing) == len(values):
            parsed.append(
                {
                    "skipped": "no_gold_values",
                    "reason": "Zeile ohne jeden Goldwert",
                    "trial_name_raw": trial_raw,
                    "outcome_label": outcome,
                    "workbook": workbook,
                }
            )
            continue
        subgroup = "subgroup" in outcome.lower()
        payload = {
            "source": SOURCE,
            "outcome_type": outcome_type,
            "sr_name": clean(row.get(header["SR name_year"], "")),
            "sr_doi": clean(row.get(header["SR_DOI"], "")).lower(),
            "outcome_label": outcome,
            "trial_name_raw": trial_raw,
            "trial_doi": clean(row.get(header.get("RCT_DOI or Link", "I"), "")).lower(),
            "arm_labels": [
                clean(row.get(header["Intervention"], "")),
                clean(row.get(header["Control"], "")),
            ],
            "values": values,
        }
        parsed.append(
            {
                "record_id": record_id(payload),
                "source": SOURCE,
                "outcome_type": outcome_type,
                "study_id": f"{payload['sr_name']}::{trial_raw}",
                "trial_name_raw": trial_raw,
                "trial_doi": payload["trial_doi"],
                "sr_name": payload["sr_name"],
                "sr_doi": payload["sr_doi"],
                "outcome_id": f"{payload['sr_name']}::{outcome}",
                "outcome_label": outcome,
                "timepoint_id": None,
                "arms": [
                    {"arm_id": arm["arm_id"], "label": label, **{k: v for k, v in arm.items() if k != "arm_id"}}
                    for arm, label in zip(arms, payload["arm_labels"])
                ],
                "unit_of_analysis": "subgroup_region" if subgroup else "trial",
                "missing_gold_fields": missing,
                "provenance": {
                    "source_document": f"OSF 8fzps / {workbook}",
                    "table_or_section": "sheet",
                    "source_cell_or_location": None,
                    "page": None,
                    "text_snippet": None,
                },
                "schema_version": "schema_v1",
                "verification_status": "verbatim",
            }
        )
    return parsed


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(WORKBOOKS.glob("*.xlsx"))
    if not files:
        raise SystemExit(f"keine Arbeitsmappen in {WORKBOOKS}")

    per_file: dict[str, list[dict[str, Any]]] = {}
    skipped: list[dict[str, Any]] = []
    for path in files:
        binary, continuous = read_workbook(path)
        rows = binary + continuous
        per_file[path.name] = [row for row in rows if "record_id" in row]
        skipped.extend(row for row in rows if "skipped" in row)

    def gold_key(row: dict[str, Any]) -> tuple:
        return (
            row["trial_doi"] or " ".join(row["trial_name_raw"].lower().split()),
            row["outcome_type"],
            json.dumps(row["arms"], sort_keys=True),
        )

    reference = {gold_key(row) for row in per_file[files[0].name]}
    consistent = all({gold_key(row) for row in rows} == reference for rows in per_file.values())
    def label_key(row: dict[str, Any]) -> tuple[str, str]:
        return (
            " ".join(row["trial_name_raw"].lower().split()),
            " ".join(row["outcome_label"].lower().split()),
        )

    label_sets = [{label_key(row) for row in rows} for rows in per_file.values()]
    union = set().union(*label_sets)
    label_variant_count = len(union) - len(set.intersection(*label_sets))
    records = per_file[files[0].name]

    compared = sorted(
        {(row["trial_name_raw"].lower(), row["outcome_label"].lower()) for row in records}
    )
    payload = {
        "adapter": "adapter_eururology.py",
        "source": SOURCE,
        "source_document": "https://osf.io/8fzps/",
        "publication": "Yisha et al., BMC Med Res Methodol 2026;26:33, doi 10.1186/s12874-025-02729-5",
        "license": "keine Lizenz im OSF-Projekt angegeben",
        "workbooks": [
            {
                "name": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "records": len(per_file[path.name]),
            }
            for path in files
        ],
        "records": len(records),
        "records_binary": sum(1 for row in records if row["outcome_type"] == "binary"),
        "records_continuous": sum(1 for row in records if row["outcome_type"] == "continuous"),
        "distinct_trials": len({row["trial_name_raw"] for row in records}),
        "distinct_trial_dois": len({row["trial_doi"] for row in records if row["trial_doi"]}),
        "distinct_outcomes": len(compared),
        "skipped_rows": len(skipped),
        "skipped_reasons": sorted({row["reason"] for row in skipped}),
        "skipped_by_reason": {
            reason: sum(1 for row in skipped if row["reason"] == reason)
            for reason in sorted({row["reason"] for row in skipped})
        },
        "records_with_missing_gold_cells": sum(1 for row in records if row["missing_gold_fields"]),
        "gold_columns_consistent_across_workbooks": consistent,
        "label_spelling_variants_across_workbooks": label_variant_count,
        "duplicate_record_ids": len(records) - len({row["record_id"] for row in records}),
    }

    with (OUT_DIR / "records.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in records:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
