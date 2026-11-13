"""Adapter: PICO-Corpus (Mutinda et al., WIESP 2022).

Quelle: https://github.com/sociocom/PICO-Corpus, 1.011 PubMed-Abstracts von
Brustkrebs-RCTs, BRAT-Annotationen.

Uebernommen werden nur die numerischen Annotationen mit Armbezug:
``iv-*`` (Intervention), ``cv-*`` (Kontrolle), jeweils ``bin-abs``,
``bin-percent``, ``cont-mean``, ``cont-sd``, ``cont-median``, ``cont-q1``,
``cont-q3``.

Wichtig: Der Korpus enthaelt **keine Relationen** zwischen Zahl und Outcome.
Deshalb bleibt ``outcome_id`` leer. Zahlen in Worten ("Seven") werden als
``value_text`` gefuehrt und nicht in eine Zahl umgedeutet.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
BENCH = HERE.parents[2]
CROSSVAL = BENCH / "evaluation" / "multi_model_cross_validation"
OUT_DIR = CROSSVAL / "goldstandard_datasets" / "pico_corpus_v1"
ZIP = OUT_DIR / "original" / "pico_corpus_main.zip"
ANN_PREFIX = "PICO-Corpus-main/pico_corpus_brat_annotated_files/"

LABELS = {
    "iv-bin-abs": ("intervention", "events", "count"),
    "cv-bin-abs": ("comparator", "events", "count"),
    "iv-bin-percent": ("intervention", "events", "percent"),
    "cv-bin-percent": ("comparator", "events", "percent"),
    "iv-cont-mean": ("intervention", "mean", "value"),
    "cv-cont-mean": ("comparator", "mean", "value"),
    "iv-cont-sd": ("intervention", "sd", "value"),
    "cv-cont-sd": ("comparator", "sd", "value"),
    "iv-cont-median": ("intervention", "median", "value"),
    "cv-cont-median": ("comparator", "median", "value"),
    "iv-cont-q1": ("intervention", "q1", "value"),
    "cv-cont-q1": ("comparator", "q1", "value"),
    "iv-cont-q3": ("intervention", "q3", "value"),
    "cv-cont-q3": ("comparator", "q3", "value"),
}
NUMBER = re.compile(r"[-+]?\d+(?:[.,]\d+)?")


def parse_value(text: str) -> float | None:
    match = NUMBER.search(text)
    if not match:
        return None
    return float(match.group(0).replace(",", "."))


def main() -> int:
    if not ZIP.exists():
        raise SystemExit(f"PICO-Corpus-Archiv fehlt: {ZIP}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, Any]] = []
    abstracts = 0
    with zipfile.ZipFile(ZIP) as archive:
        annotated = sorted(
            name for name in archive.namelist() if name.startswith(ANN_PREFIX) and name.endswith(".ann")
        )
        texts = {name: archive.read(name).decode("utf-8") for name in annotated}
    for ann_name in annotated:
        abstracts += 1
        pmid = Path(ann_name).stem
        for line in texts[ann_name].splitlines():
            parts = line.split("\t")
            if len(parts) < 3 or not parts[0].startswith("T"):
                continue
            meta = parts[1].split(" ")
            label = meta[0]
            if label not in LABELS:
                continue
            arm, statistic, unit = LABELS[label]
            start, end = meta[1], meta[2]
            text = parts[2]
            records.append(
                {
                    "record_id": hashlib.sha256(f"{pmid}|{start}|{label}".encode()).hexdigest()[:16],
                    "pmid": pmid,
                    "source": "pico_corpus",
                    "arm_id": arm,
                    "statistic": statistic,
                    "unit": unit,
                    "value": parse_value(text),
                    "value_text": text,
                    "numeric_label": label,
                    "outcome_id": None,
                    "timepoint_id": None,
                    "provenance": {
                        "source_document": f"PICO-Corpus/{Path(ann_name).name}",
                        "table_or_section": "abstract",
                        "source_cell_or_location": f"chars {start}-{end}",
                        "page": None,
                        "text_snippet": text,
                    },
                    "verification_status": "verbatim",
                }
            )

    payload = {
        "adapter": "adapter_pico_corpus.py",
        "source": "https://github.com/sociocom/PICO-Corpus",
        "publication": "Mutinda et al., PICO Corpus, WIESP 2022 (ACL Anthology 2022.wiesp-1.4)",
        "license": "keine Lizenzdatei im Repository",
        "abstracts": abstracts,
        "records": len(records),
        "records_by_label": {
            label: sum(1 for row in records if row["numeric_label"] == label)
            for label in sorted(LABELS)
        },
        "records_without_numeric_value": sum(1 for row in records if row["value"] is None),
        "outcome_linked": False,
        "note": "keine Relationen zwischen Zahl und Outcome; outcome_id bleibt leer",
    }
    with (OUT_DIR / "records.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in records:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    (OUT_DIR / "manifest.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: payload[k] for k in ("abstracts", "records", "records_without_numeric_value")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
