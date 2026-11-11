"""Isolationstest fuer den C1-Testpfad; liest keine Testdaten."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from c1_test_projection import (  # noqa: E402
    INPUT_FIELDS,
    project_rows,
    validate_test_input,
)
from run_c1_dev_pilot import render_prompt  # noqa: E402


def record(record_id: int, split: str) -> dict:
    return {
        "record_id": record_id,
        "study_id": f"S-{record_id}",
        "pmcid": f"PMC{record_id}",
        "split": split,
        "outcome_type": "binary",
        "ico": {
            "intervention": "intervention",
            "comparator": "comparator",
            "outcome": "outcome",
        },
        "source_text_path": "unused.md",
    }


def main() -> int:
    dev_190 = render_prompt(record(190, "dev"), "ARTICLE", "v6")
    test_190 = render_prompt(record(190, "test"), "ARTICLE", "v6")
    assert "12-month" in dev_190
    assert "12-month" not in test_190

    dev_226 = render_prompt(record(226, "dev"), "ARTICLE", "v6")
    test_226 = render_prompt(record(226, "test"), "ARTICLE", "v6")
    assert "25.78" in dev_226
    assert "25.78" not in test_226

    frozen = record(1, "test")
    frozen["reference_values"] = {"intervention_events": 1}
    frozen["curated_values"] = {"intervention_events": 1}
    frozen["audit_status"] = "verified_exact"
    frozen["audit_reason"] = "test"
    frozen["correction"] = None
    inputs, references = project_rows(
        [frozen],
        expected_records=None,
        expected_articles=None,
        expected_types=None,
    )
    assert set(inputs[0]) == set(INPUT_FIELDS)
    assert "reference_values" not in inputs[0]
    assert "reference_values" in references[0]
    validate_test_input(inputs, expected_records=None)

    bad = dict(inputs[0])
    bad["reference_values"] = {}
    try:
        validate_test_input([bad], expected_records=None)
    except ValueError:
        pass
    else:
        raise AssertionError("Test-Input mit Referenz wurde akzeptiert")

    bad_split = dict(inputs[0])
    bad_split["split"] = "dev"
    try:
        validate_test_input([bad_split], expected_records=None)
    except ValueError:
        pass
    else:
        raise AssertionError("Dev-Record wurde als Test-Input akzeptiert")

    gate = subprocess.run(
        [sys.executable, str(SCRIPTS / "c1_test_projection.py"),
         "--frozen", str(SCRIPTS / "does-not-exist.jsonl")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert gate.returncode == 2
    assert "--approve-test" in gate.stdout

    print("C1_TEST_ISOLATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
