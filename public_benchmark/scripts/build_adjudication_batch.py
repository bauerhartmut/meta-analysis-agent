#!/usr/bin/env python3
"""Baut den verblindeten Adjudikations-Batch aus drei Modellannotationen.

Eingabe sind feldweise Annotationen (JSONL) mit mindestens
``record_id``, ``field`` und ``value``; optional ``table_or_section``,
``source_cell_or_location``, ``arm_id``, ``outcome_id``, ``timepoint_id``.

Vergleich und Kategorien:
- C1 unanimity: alle drei Werte gleich (kein Adjudikationsfall).
- C2 two_vs_one: zwei gleich, eines abweichend.
- C3 three_way: drei verschiedene Werte.
- C4 missing_value: mindestens ein Modell ohne Wert.
- C5 source_conflict: gleicher Wert, verschiedene Quelle.
- C6 structural_conflict: gleicher Wert, verschiedene Arm-/Outcome-/Zeitpunkt-ID.

Verblindung: Die Zuordnung Modell -> ``candidate_1..3`` wird je Konflikt aus
``sha256(salt|record_id|field)`` abgeleitet. Damit ist die Reihenfolge
unabhaengig von Modellnamen, Eingabereihenfolge und Datenlage im Batch.

Ausgabe:
- ``adjudication_batch_v1.jsonl`` (ohne Modellnamen)
- ``adjudication_blinding_v1.json`` (Zuordnung, getrennt)
- ``model_agreement_v1.json`` (Zaehlung je Kategorie)
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = BENCH_ROOT / "evaluation" / "multi_model_cross_validation"
SALT = "crossval-adjudication-20261113-v1"
STRUCTURAL_FIELDS = ("arm_id", "outcome_id", "timepoint_id")
SOURCE_FIELDS = ("table_or_section", "source_cell_or_location")


def load_rows(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    rows: dict[tuple[str, str], dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            rows[(str(row["record_id"]), row["field"])] = row
    return rows


def label_order(record_id: str, field: str, models: list[str]) -> list[str]:
    """Deterministische, modellunabhaengige Reihenfolge der Kandidaten."""
    digest = hashlib.sha256(f"{SALT}|{record_id}|{field}".encode("utf-8")).hexdigest()
    order = sorted(models, key=lambda model: (digest, model))
    return order


def normalise(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qwen", type=Path, required=True)
    parser.add_argument("--deepseek", type=Path, required=True)
    parser.add_argument("--glm", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    models = {"qwen": args.qwen, "deepseek": args.deepseek, "glm": args.glm}
    data = {name: load_rows(path) for name, path in models.items()}
    keys = sorted(set().union(*(rows.keys() for rows in data.values())))

    batch: list[dict[str, Any]] = []
    blinding: dict[str, dict[str, str]] = {}
    counts: Counter[str] = Counter()

    for record_id, field in keys:
        present = {name: rows[(record_id, field)] for name, rows in data.items() if (record_id, field) in rows}
        values = {name: normalise(row.get("value")) for name, row in present.items()}
        distinct = {repr(value) for value in values.values() if value is not None}
        missing = len(present) < 3 or any(value is None for value in values.values())

        sources = {
            name: tuple(row.get(field_name) for field_name in SOURCE_FIELDS)
            for name, row in present.items()
        }
        structures = {
            name: tuple(row.get(field_name) for field_name in STRUCTURAL_FIELDS)
            for name, row in present.items()
        }
        same_value = len(distinct) <= 1

        if same_value and not missing and len(set(sources.values())) > 1:
            category = "C5"
        elif same_value and not missing and len(set(structures.values())) > 1:
            category = "C6"
        elif missing:
            category = "C4"
        elif len(distinct) == 3:
            category = "C3"
        elif len(distinct) == 2:
            category = "C2"
        else:
            category = "C1"

        counts[category] += 1
        if category == "C1":
            continue

        order = label_order(record_id, field, sorted(present))
        mapping = {f"candidate_{index}": name for index, name in enumerate(order, start=1)}
        blinding[f"{record_id}|{field}"] = mapping
        batch.append(
            {
                "record_id": record_id,
                "field": field,
                "category": category,
                "candidates": [
                    {
                        "label": f"candidate_{index}",
                        "value": values[name],
                        "table_or_section": present[name].get("table_or_section"),
                        "source_cell_or_location": present[name].get("source_cell_or_location"),
                        "arm_id": present[name].get("arm_id"),
                        "outcome_id": present[name].get("outcome_id"),
                        "timepoint_id": present[name].get("timepoint_id"),
                        "source_context": present[name].get("source_context"),
                    }
                    for index, name in enumerate(order, start=1)
                ],
            }
        )

    out_dir = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "adjudication_batch_v1.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in batch:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    (out_dir / "adjudication_blinding_v1.json").write_text(
        json.dumps(
            {
                "salt": SALT,
                "note": "Zuordnung erst nach der Adjudikation auswerten.",
                "conflicts": blinding,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "model_agreement_v1.json").write_text(
        json.dumps(
            {
                "fields_compared": len(keys),
                "categories": dict(sorted(counts.items())),
                "conflicts": len(batch),
                "models": sorted(models),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"{len(keys)} Felder verglichen, {len(batch)} Konflikte, {dict(sorted(counts.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
