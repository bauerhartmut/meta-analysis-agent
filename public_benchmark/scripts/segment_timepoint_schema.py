#!/usr/bin/env python3
"""Ergaenzt Goldstandard-Effektzeilen um eine strukturierte Zeitpunktsegmentierung.

Das Skript liest eine Goldstandard-Datei, segmentiert jedes vorhandene
`time_point` in Post-Treatment-, Follow-up- und sonstige Wochen und schreibt
eine Kopie mit dem zusaetzlichen Feld `time_point_segments`. `time_point` und
alle Outcome-Werte bleiben unveraendert.

Aufruf:
    python public_benchmark/scripts/segment_timepoint_schema.py \
        data/golden_effects/goldstandard_A.json \
        /tmp/goldstandard_A_segmentiert.json
"""

from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from match_dcbti_review_studies import parse_timepoints


def segment_effect(effect: dict[str, Any]) -> dict[str, Any]:
    """Gibt eine Kopie der Zeile mit abgeleiteter Segmentierung zurueck."""
    enriched = copy.deepcopy(effect)
    parsed = parse_timepoints(effect.get("time_point"))
    enriched["time_point_segments"] = {
        "status": parsed["status"],
        "post_treatment_weeks": parsed["post_treatment_weeks"],
        "follow_up_weeks": parsed["follow_up_weeks"],
        "other_weeks": parsed["other_weeks"],
        "uncertain_weeks": parsed["uncertain_weeks"],
        "ambiguous_post_treatment": parsed["ambiguous_post_treatment"],
        "raw": parsed["raw"],
    }
    return enriched


def segment_document(document: dict[str, Any]) -> dict[str, Any]:
    enriched = copy.deepcopy(document)
    enriched["effects"] = [
        segment_effect(effect) for effect in document.get("effects", [])
    ]
    return enriched


def segment_file(source: Path, target: Path) -> Counter:
    data = json.loads(source.read_text(encoding="utf-8"))
    enriched = copy.deepcopy(data)
    enriched["documents"] = [
        segment_document(document) for document in data.get("documents", [])
    ]
    target.write_text(
        json.dumps(enriched, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return Counter(
        effect["time_point_segments"]["status"]
        for document in enriched["documents"]
        for effect in document["effects"]
    )


def main(argv: list[str]) -> int:
    if len(argv) not in (1, 2):
        print(__doc__)
        return 1
    source = Path(argv[0])
    target = (
        Path(argv[1])
        if len(argv) == 2
        else source.with_name(f"{source.stem}_segmentiert.json")
    )
    counts = segment_file(source, target)
    total = sum(counts.values())
    details = ", ".join(f"{status}={counts[status]}" for status in sorted(counts))
    print(f"Effektzeilen: {total}; Status: {details or 'keine'}")
    print(f"Quelle: {source}")
    print(f"Ziel:   {target}")
    print("Outcome-Werte und time_point unveraendert.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
