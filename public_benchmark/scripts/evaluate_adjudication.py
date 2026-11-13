#!/usr/bin/env python3
"""Wertet eine Adjudikation gegen die Referenz aus.

Gemessen wird ausschliesslich gegen die menschliche Referenz, nie gegen
Modellkonsens. Ausgegeben werden Modellgenauigkeit auf den Konfliktfeldern,
Genauigkeit der gewaehlten Kandidaten, Selbstwahlquote der Adjudikation,
Anteil ungeloester Faelle sowie Verbesserungen und Verschlechterungen
gegenueber dem Adjudikator-Modell allein.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def field_rows(path: Path) -> dict[tuple[str, str], Any]:
    return {(str(row["record_id"]), row["field"]): row.get("value") for row in load_jsonl(path)}


def same(a: Any, b: Any) -> bool:
    if a is None or b is None:
        return a is b
    try:
        return abs(float(a) - float(b)) < 1e-9
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--blinding", type=Path, required=True)
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--qwen", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    blinding = json.loads(args.blinding.read_text(encoding="utf-8"))["conflicts"]
    reference = field_rows(args.reference)
    qwen = field_rows(args.qwen)
    adjudications = {
        (str(row["record_id"]), row["field"]): row for row in load_jsonl(args.adjudication)
    }

    counts: Counter[str] = Counter()
    chosen_correct = 0
    self_choice = 0
    self_choice_correct = 0
    improved = 0
    worsened = 0

    for row in load_jsonl(args.batch):
        key = (str(row["record_id"]), row["field"])
        truth = reference.get(key)
        if truth is None:
            counts["ohne_referenz"] += 1
            continue
        verdict = adjudications.get(key)
        if not verdict:
            counts["nicht_adjudiziert"] += 1
            continue
        status = verdict.get("status", "unresolved")
        counts[f"status_{status}"] += 1
        if status != "resolved":
            continue
        chosen = verdict.get("chosen_candidate")
        mapping = blinding.get(f"{key[0]}|{key[1]}", {})
        chosen_model = mapping.get(chosen, "")
        if chosen_model == "qwen":
            self_choice += 1
            if same(verdict.get("value"), truth):
                self_choice_correct += 1
        if same(verdict.get("value"), truth):
            chosen_correct += 1
        before_ok = same(qwen.get(key), truth)
        after_ok = same(verdict.get("value"), truth)
        if not before_ok and after_ok:
            improved += 1
        if before_ok and not after_ok:
            worsened += 1

    resolved = sum(value for name, value in counts.items() if name == "status_resolved")
    payload = {
        "batch_fields": sum(1 for _ in load_jsonl(args.batch)),
        "counts": dict(sorted(counts.items())),
        "resolved": resolved,
        "chosen_correct": chosen_correct,
        "chosen_accuracy_on_resolved": round(chosen_correct / resolved, 4) if resolved else None,
        "self_choice": self_choice,
        "self_choice_correct": self_choice_correct,
        "self_choice_rate": round(self_choice / resolved, 4) if resolved else None,
        "improved_vs_qwen": improved,
        "worsened_vs_qwen": worsened,
        "note": "Die Adjudikation ist kein Goldstandard; Grundlage ist ausschliesslich die Referenz.",
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
