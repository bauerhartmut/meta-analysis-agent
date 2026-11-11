"""C1-Test-Pilot gegen die getrennte Test-Referenz auswerten.

Der Evaluator prueft zuerst das eingefrorene Test-Manifest und den
Output-Hash. Erst danach laedt er ``test_reference.jsonl``. Der Runner hat
diese Datei nie gesehen.

Aufruf:
    PYTHONIOENCODING=utf-8 .venv/bin/python.exe \
        public_benchmark/scripts/evaluate_c1_test_pilot.py \
        --run-id c1_test_20261111_v6c
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

BENCH_ROOT = Path(__file__).resolve().parents[1]
PILOT_ROOT = BENCH_ROOT / "evaluation" / "c1_pilot"
sys_path = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(sys_path))

from evaluate_c1_dev_pilot import evaluate, render_markdown  # noqa: E402
from run_c1_dev_pilot import load_jsonl, sha256_file  # noqa: E402

TEST_INPUT_PATH = PILOT_ROOT / "test_locked" / "test_input.jsonl"
TEST_REFERENCE_PATH = PILOT_ROOT / "test_locked" / "test_reference.jsonl"
TEST_PROJECTION_MANIFEST = PILOT_ROOT / "test_locked" / "test_projection_manifest.json"
TEST_OUTPUT_ROOT = PILOT_ROOT / "runs_test"
EXPECTED_TEST_RECORDS = 249
EXPECTED_TEST_FIELDS = 1308


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default="c1_test_20261111_v6c")
    args = parser.parse_args()

    run_dir = TEST_OUTPUT_ROOT / args.run_id
    output_path = run_dir / "test_output.jsonl"
    manifest_path = run_dir / "test_manifest.json"
    if not output_path.exists() or not manifest_path.exists():
        print(f"ABBRUCH: Testlauf unvollstaendig: {run_dir}")
        return 2

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks = {
        "test_split_used": True,
        "reference_loaded": False,
        "completed_records": EXPECTED_TEST_RECORDS,
        "input_sha256": sha256_file(TEST_INPUT_PATH),
        "output_sha256": sha256_file(output_path),
    }
    for key, expected in checks.items():
        if manifest.get(key) != expected:
            print(f"ABBRUCH: Test-Manifest weicht ab: {key}")
            return 2

    if not TEST_REFERENCE_PATH.exists() or not TEST_PROJECTION_MANIFEST.exists():
        print(f"ABBRUCH: Test-Referenz oder Projektionsmanifest fehlt")
        return 2

    projection = json.loads(TEST_PROJECTION_MANIFEST.read_text(encoding="utf-8"))
    if projection.get("input_sha256") != checks["input_sha256"]:
        print("ABBRUCH: Test-Input-Hash weicht vom Projektionsmanifest ab.")
        return 2
    if projection.get("reference_sha256") != sha256_file(TEST_REFERENCE_PATH):
        print("ABBRUCH: Test-Referenz-Hash weicht vom Projektionsmanifest ab.")
        return 2

    # Ab hier ist der Output eingefroren; erst jetzt wird die Referenz geladen.
    summary = evaluate(
        args.run_id,
        input_path=TEST_INPUT_PATH,
        reference_path=TEST_REFERENCE_PATH,
        output_path=output_path,
        test_mode=True,
    )
    summary["test_split_used"] = True
    if summary["expected_fields_total"] != EXPECTED_TEST_FIELDS:
        print("ABBRUCH: Erwartete Testfelder weichen von 1.308 ab.")
        return 2

    summary_path = run_dir / "test_evaluation.json"
    report_path = run_dir / "test_evaluation.md"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    report_path.write_text(
        render_markdown(
            summary,
            title="C1-Test-Pilot: Ergebnis",
            note="Testlauf nach Output-Freeze; Referenz erst danach geladen.",
        ),
        encoding="utf-8",
    )

    print(f"Records: {summary['records_with_output']}/{summary['records']}")
    print(
        f"Exakt: {summary['exact_fields']}/{summary['expected_fields_total']} "
        f"({summary['exact_rate']:.1%}), Abdeckung {summary['coverage']:.1%}, "
        f"MAE {summary['mae_paired_all']}"
    )
    print(
        f"Fehlend {summary['missing_fields']}, falsch {summary['wrong_fields']}, "
        f"halluziniert {summary['hallucinated_fields']}"
    )
    print(f"JSON: {summary_path}")
    print(f"Bericht: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
