#!/usr/bin/env python3
"""Prueft eine Annotation gegen ``schema_v1.json``.

Bewusst ohne externe Abhaengigkeit (``jsonschema`` ist im Projekt nicht
installiert). Geprueft werden Pflichtfelder, Datentypen, Enums, aufloesbare
Referenzen und die Belegpflicht.

Nutzung:
    python public_benchmark/scripts/validate_crossval_annotation.py DATEI.jsonl
    python -c "from validate_crossval_annotation import validate_record"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = (
    BENCH_ROOT / "evaluation" / "multi_model_cross_validation" / "schema_v1.json"
)


def load_schema(path: Path = SCHEMA_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _require(obj: dict[str, Any], fields: list[str], where: str, errors: list[str]) -> None:
    for field in fields:
        if field not in obj:
            errors.append(f"{where}: Pflichtfeld fehlt: {field}")


def validate_record(record: dict[str, Any], schema: dict[str, Any] | None = None) -> list[str]:
    """Gibt eine Liste von Fehlern zurueck; leer bedeutet gueltig."""
    schema = schema or load_schema()
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["Dokument ist kein Objekt"]

    _require(record, schema["document_required"], "dokument", errors)
    if errors:
        return errors

    study = record.get("study") or {}
    _require(study, schema["study_required"], "study", errors)

    arm_ids: set[str] = set()
    for index, arm in enumerate(record.get("arms") or []):
        _require(arm, schema["arm_required"], f"arms[{index}]", errors)
        if arm.get("role") not in schema["enums"]["arm_role"]:
            errors.append(f"arms[{index}]: role ungueltig: {arm.get('role')}")
        if arm.get("arm_id"):
            arm_ids.add(arm["arm_id"])

    outcome_ids: set[str] = set()
    for index, outcome in enumerate(record.get("outcomes") or []):
        _require(outcome, schema["outcome_required"], f"outcomes[{index}]", errors)
        if outcome.get("type") not in schema["enums"]["outcome_type"]:
            errors.append(f"outcomes[{index}]: type ungueltig: {outcome.get('type')}")
        if outcome.get("outcome_id"):
            outcome_ids.add(outcome["outcome_id"])

    timepoint_ids: set[str] = set()
    for index, timepoint in enumerate(record.get("timepoints") or []):
        _require(timepoint, schema["timepoint_required"], f"timepoints[{index}]", errors)
        if timepoint.get("relative_to") not in schema["enums"]["relative_to"]:
            errors.append(
                f"timepoints[{index}]: relative_to ungueltig: {timepoint.get('relative_to')}"
            )
        if timepoint.get("timepoint_id"):
            timepoint_ids.add(timepoint["timepoint_id"])

    for index, value in enumerate(record.get("values") or []):
        where = f"values[{index}]"
        _require(value, schema["value_required"], where, errors)
        if errors and any(error.startswith(where) for error in errors):
            continue
        number = value.get("value")
        if number is not None and not isinstance(number, (int, float)):
            errors.append(f"{where}: value ist keine Zahl: {number!r}")
        if isinstance(number, bool):
            errors.append(f"{where}: value darf kein Wahrheitswert sein")
        for field, kind in schema["value_types"].items():
            field_value = value.get(field)
            if field == "value" or field_value is None:
                continue
            if kind == "string" and not isinstance(field_value, str):
                errors.append(f"{where}: {field} muss Text sein")
            if kind == "string" and isinstance(field_value, str) and not field_value.strip():
                errors.append(f"{where}: {field} ist leer")
        if value.get("assignment_confidence") not in schema["enums"]["assignment_confidence"]:
            errors.append(
                f"{where}: assignment_confidence ungueltig: {value.get('assignment_confidence')}"
            )
        if value.get("verification_status") not in schema["enums"]["verification_status"]:
            errors.append(
                f"{where}: verification_status ungueltig: {value.get('verification_status')}"
            )
        if value.get("arm_id") and value["arm_id"] not in arm_ids:
            errors.append(f"{where}: arm_id nicht aufloesbar: {value['arm_id']}")
        if value.get("outcome_id") and value["outcome_id"] not in outcome_ids:
            errors.append(f"{where}: outcome_id nicht aufloesbar: {value['outcome_id']}")
        if value.get("timepoint_id") and value["timepoint_id"] not in timepoint_ids:
            errors.append(f"{where}: timepoint_id nicht aufloesbar: {value['timepoint_id']}")
        needs_note = (
            value.get("assignment_confidence") == "low"
            or value.get("verification_status") not in ("verbatim", "parsed_from_cell")
        )
        if needs_note and not (value.get("uncertainty_note") or "").strip():
            errors.append(f"{where}: uncertainty_note fehlt bei unsicherer Zuordnung")
        if value.get("page") == "unbekannt" and value.get("verification_status") != "insufficient_evidence":
            errors.append(
                f"{where}: Seite unbekannt, aber Status nicht insufficient_evidence"
            )
    return errors


def validate_file(path: Path) -> list[str]:
    schema = load_schema()
    errors: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"Zeile {line_number}: kein JSON: {exc}")
                continue
            for error in validate_record(record, schema):
                errors.append(f"Zeile {line_number}: {error}")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Nutzung: validate_crossval_annotation.py DATEI.jsonl")
        return 2
    errors = validate_file(Path(sys.argv[1]))
    if errors:
        for error in errors:
            print(error)
        return 1
    print("gueltig")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
