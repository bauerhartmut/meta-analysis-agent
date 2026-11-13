#!/usr/bin/env python3
"""Eignungspruefung der 25 Hauptartikel an den XML-Volltexten.

Deterministisch, kein Modell, kein Netz. Grundlage ist der vorhandene
JATS-Tabellenleser (``research_agent.research.jats_tables``) und die
Arm-Erkennung der Pipeline (``research_agent.meta.arm_level.arms_from_row``).

Damit wird nicht ein Signal geprueft, sondern ob eine Tabellenzeile
tatsaechlich zwei Armwerte ergibt. Baseline- und Demografietabellen sind
ausgeschlossen: sie liefern Armwerte, aber keinen Behandlungseffekt.

Klassifikation je Artikel:
- ``eligible_confirmed``: mindestens eine Outcome-Zeile mit zwei Armen
  (Mittelwert plus Streuung) oder zwei Ereignispaaren, Zeitpunkt ableitbar.
- ``eligible_uncertain``: Armwerte vorhanden, Zeitpunkt nicht belegt.
- ``manual_review_required``: Mehrarm-Design, viele Zeitpunkte oder
  Supplementtabellen erfordern Zuordnungslogik.
- ``ineligible``: keine armweisen Outcome-Zahlen gefunden.

Ausgabe:
- ``crossval_eligibility_review_v1.json``
- ``crossval_eligibility_review_v1.md``
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
ROOT = BENCH_ROOT.parent
OUT_DIR = BENCH_ROOT / "evaluation" / "multi_model_cross_validation"
SELECTION = OUT_DIR / "candidate_shortlist_v2.json"
AVAILABILITY = OUT_DIR / "fulltext_availability_v1.json"
REVIEW_JSON = OUT_DIR / "crossval_eligibility_review_v1.json"
REVIEW_MD = OUT_DIR / "crossval_eligibility_review_v1.md"

sys.path.insert(0, str(ROOT))

from research_agent.meta.arm_level import arms_from_row  # noqa: E402
from research_agent.meta.arm_text import text_arm_candidates  # noqa: E402
from research_agent.research.jats_tables import parse_jats  # noqa: E402

EVENTS_PAIR = re.compile(r"^(\d{1,5})\s*/\s*(\d{1,5})$")
PERCENT_PAIR = re.compile(r"^(\d{1,5})\s*\(\s*(\d{1,3}(?:[.,]\d+)?)\s*%?\s*\)$")
ARM_SIZE = re.compile(r"\bn\s*=\s*(\d{1,6})", re.IGNORECASE)
TIMEPOINT = re.compile(
    r"\b(baseline|day\s*\d+|week\s*\d+|\d+\s*weeks?|month\s*\d+|\d+\s*months?|"
    r"\d+\s*(?:h|hours?)|follow[- ]?up|post[- ]?(?:test|treatment|intervention)|"
    r"end\s*of\s*treatment)\b",
    re.IGNORECASE,
)
BASELINE_TABLE = re.compile(
    r"baseline|characteristic|demographic|participant|clinical\s+and", re.IGNORECASE
)
BASELINE_ROW = re.compile(
    r"^(sex|gender|age|male|female|height|weight|bmi|body mass|education|smoking|"
    r"married|employment|ethnicity|income|handedness|duration of)",
    re.IGNORECASE,
)
SUPP_REFERENCE = re.compile(r"supplementary\s+(?:table|figure|material)", re.IGNORECASE)
DIRECT_EFFECT = re.compile(
    r"[-−]?\d+(?:\.\d+)?\s*\(\s*[-−]?\d+(?:\.\d+)?\s*[,;]\s*[-−]?\d+(?:\.\d+)?\s*\)"
)
VERTICAL_ARM = re.compile(r"^(AG|CG|EG|IG|TG|PG|VG|group\s*[A-Z0-9])\s*$", re.IGNORECASE)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(elem: Any) -> str:
    return " ".join("".join(elem.itertext()).split())


def timepoints_in(text: str) -> list[str]:
    return sorted({m.group(1).lower() for m in TIMEPOINT.finditer(text)})


def review_article(pmcid: str, path: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "pmcid": pmcid,
        "available": True,
        "tables": 0,
        "outcome_tables": 0,
        "baseline_tables_skipped": 0,
        "continuous_rows": 0,
        "binary_rows": 0,
        "direct_effect_rows": 0,
        "vertical_arm_rows": 0,
        "evidence": [],
        "timepoints": [],
        "supplement_needed": False,
        "arms_in_header": 0,
        "classification": "",
        "reason": "",
    }
    tables = parse_jats(path)
    entry["tables"] = len(tables)
    raw = path.read_bytes()
    entry["supplement_needed"] = bool(
        b"supplementary-material" in raw or SUPP_REFERENCE.search(raw.decode("utf-8", "replace")[:60000])
    )

    timepoints: set[str] = set()
    # Die Fallzahl je Arm steht oft nur in der Baseline-Tabelle, waehrend die
    # Outcome-Tabelle nur Mittelwert und Streuung fuehrt. Genau diese
    # Zuordnung soll die Pruefung leisten, nicht erraten.
    n_per_arm: list[int] | None = None
    for table in tables:
        sizes = [int(m.group(1)) for cell in (table.header or []) for m in ARM_SIZE.finditer(cell)]
        if len(sizes) == 2:
            n_per_arm = sizes
            break
    entry["n_per_arm"] = n_per_arm
    for table in tables:
        context = " ".join([table.label, table.caption])
        if BASELINE_TABLE.search(context):
            entry["baseline_tables_skipped"] += 1
            continue
        entry["outcome_tables"] += 1
        header = table.header or []
        arms_named = len([cell for cell in header if re.search(r"\bn\s*=", cell, re.IGNORECASE)])
        entry["arms_in_header"] = max(entry["arms_in_header"], arms_named)
        timepoints.update(timepoints_in(context))
        for row in table.rows:
            cells = row.cells
            if len(cells) < 3:
                continue
            label = cells[0]
            if BASELINE_ROW.match(label):
                continue
            timepoints.update(timepoints_in(label))
            if VERTICAL_ARM.match(label.strip()) and len(cells) > 1 and re.search(
                r"\d\s*±\s*\d", cells[1]
            ):
                entry["vertical_arm_rows"] += 1
            if any(DIRECT_EFFECT.search(cell) for cell in cells[1:]):
                entry["direct_effect_rows"] += 1
            parsed, reason = arms_from_row(
                header, cells, n_per_arm=n_per_arm, spread_hint=label
            )
            if len(parsed) == 2:
                entry["continuous_rows"] += 1
                if len(entry["evidence"]) < 4:
                    entry["evidence"].append(
                        {
                            "kind": "continuous",
                            "table": table.label or table.caption[:60],
                            "row": label,
                            "cells": cells[1:5],
                            "arms": [
                                {"label": a.label, "n": a.n, "mean": a.mean, "sd": a.sd}
                                for a in parsed
                            ],
                        }
                    )
                continue
            pairs = [cell for cell in cells if EVENTS_PAIR.match(cell.strip())]
            percent = [cell for cell in cells if PERCENT_PAIR.match(cell.strip())]
            header_percent = any(re.search(r"n\s*\(\s*%\s*\)", cell, re.I) for cell in header)
            if header_percent:
                percent = [cell for cell in cells if re.match(r"^\d{1,5}\s*\(\s*[\d.,]+\s*\)$", cell.strip())]
            if len(pairs) >= 2 or len(percent) >= 2:
                entry["binary_rows"] += 1
                if len(entry["evidence"]) < 4:
                    entry["evidence"].append(
                        {
                            "kind": "binary",
                            "table": table.label or table.caption[:60],
                            "row": label,
                            "cells": (pairs or percent)[:4],
                            "reason_if_no_arm": reason,
                        }
                    )

    entry["timepoints"] = sorted(timepoints)
    has_numbers = entry["continuous_rows"] > 0 or entry["binary_rows"] > 0
    text_hits: list[dict] = []
    if not has_numbers:
        # Zahlen koennen auch nur im Fliesstext stehen. Sie werden als
        # Kandidaten gefuehrt, nicht als bestaetigte Armwerte.
        plain = " ".join(" ".join(ET.fromstring(raw).itertext()).split())
        text_hits = text_arm_candidates(plain[:60000])[:5]
    entry["text_candidates"] = len(text_hits)
    if not has_numbers:
        if entry["tables"] == 0:
            entry["classification"] = "manual_review_required"
            entry["reason"] = (
                "XML enthaelt keine Tabelle; Werte koennen nur im PDF oder Supplement stehen "
                "und sind aus dem XML nicht pruefbar"
            )
        elif text_hits:
            entry["classification"] = "eligible_uncertain"
            entry["reason"] = (
                f"keine Armwerte in Tabellen, aber {len(text_hits)} Satzkandidaten im Text; "
                "Zuordnung muss geprueft werden"
            )
            entry["evidence"] = [
                {"kind": "text", "table": "", "row": str(hit.get("outcome", ""))[:60],
                 "cells": [str(hit.get("quote", ""))[:180]]}
                for hit in text_hits[:2]
            ]
        elif entry["vertical_arm_rows"] > 0:
            entry["classification"] = "manual_review_required"
            entry["reason"] = (
                f"vertikales Arm-Layout ({entry['vertical_arm_rows']} Zeilen mit Armname und "
                "Mittelwert in der Nachbarzelle); Zuordnung braucht eigene Logik"
            )
        elif entry["direct_effect_rows"] > 0:
            entry["classification"] = "ineligible"
            entry["reason"] = (
                f"nur direkter Effekt mit Konfidenzintervall ({entry['direct_effect_rows']} Zeilen); "
                "keine Armwerte fuer N/Mean/SD"
            )
        else:
            entry["classification"] = "ineligible"
            entry["reason"] = "keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren"
    elif entry["arms_in_header"] >= 3 or len(timepoints) >= 3:
        entry["classification"] = "manual_review_required"
        entry["reason"] = (
            f"Mehrarm- oder Mehrzeitpunkt-Struktur: {entry['arms_in_header']} Arme im Kopf, "
            f"{len(timepoints)} Zeitpunktangaben"
        )
    elif timepoints:
        entry["classification"] = "eligible_confirmed"
        entry["reason"] = (
            f"{entry['continuous_rows']} kontinuierliche und {entry['binary_rows']} binaere "
            f"Outcome-Zeilen mit Armwerten; Zeitpunkt ableitbar"
        )
    else:
        entry["classification"] = "eligible_uncertain"
        entry["reason"] = "Armwerte vorhanden, aber kein Zeitpunkt in Label oder Spaltenkopf"
    return entry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=("primary", "reserve"), default="primary")
    args = parser.parse_args()

    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    primary = [row for row in selection["articles"] if row["role"] == args.role]
    review_json = REVIEW_JSON if args.role == "primary" else OUT_DIR / "crossval_eligibility_reserve_v1.json"
    review_md = REVIEW_MD if args.role == "primary" else OUT_DIR / "crossval_eligibility_reserve_v1.md"
    availability = {
        row["pmcid"]: row
        for row in json.loads(AVAILABILITY.read_text(encoding="utf-8"))["records"]
    }

    reviews = []
    for row in primary:
        record = availability[row["pmcid"]]
        path = ROOT / record["local_path"]
        if not record.get("saved") or not path.exists():
            reviews.append(
                {
                    "pmcid": row["pmcid"],
                    "available": False,
                    "tables": 0,
                    "classification": "manual_review_required",
                    "reason": "Volltext fehlt lokal",
                    "evidence": [],
                }
            )
            continue
        reviews.append(review_article(row["pmcid"], path))

    counts = Counter(review["classification"] for review in reviews)
    payload = {
        "review_id": "crossval_eligibility_v1",
        "created": date.today().isoformat(),
        "scope": (
            "25 Hauptartikel der Auswahl v2"
            if args.role == "primary"
            else "10 Reserveartikel der Auswahl v2"
        ),
        "model_used": False,
        "network_used": False,
        "method": {
            "tables": "research_agent.research.jats_tables.parse_jats",
            "continuous": "arms_from_row auf JATS-Kopf und -Zeile: zwei Arme mit Mittelwert, Streuung und n",
            "binary": "zwei Zellen der Form x/N oder x (y %) in einer Outcome-Zeile",
            "baseline_exclusion": "Tabellen mit baseline/characteristic/demographic im Label oder Caption und Demografiezeilen werden nicht als Outcome gewertet",
            "timepoint": "Label, Caption oder Spaltenkopf mit Tag/Woche/Monat/Follow-up",
            "manual_review_required": "drei oder mehr Arme im Kopf oder drei oder mehr Zeitpunktangaben",
        },
        "counts": dict(counts),
        "articles": reviews,
    }
    review_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Eignungspruefung der 25 Hauptartikel",
        "",
        f"Stand: {payload['created']}",
        "Deterministisch aus den XML-Volltexten. Kein Modell, kein Netz.",
        "",
        "## Verteilung",
        "",
        "| Klasse | Artikel |",
        "|---|---:|",
    ]
    for key in ("eligible_confirmed", "eligible_uncertain", "manual_review_required", "ineligible"):
        lines.append(f"| {key} | {counts.get(key, 0)} |")
    lines += [
        "",
        "## Einzelbefunde",
        "",
        "| PMCID | Klasse | Tabellen | Baseline | kont. | bin. | direkte Effekte | Zeitpunkte | Supplement |",
        "|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for review in reviews:
        lines.append(
            f"| {review['pmcid']} | {review['classification']} | {review.get('tables', 0)} | "
            f"{review.get('baseline_tables_skipped', 0)} | {review.get('continuous_rows', 0)} | "
            f"{review.get('binary_rows', 0)} | {review.get('direct_effect_rows', 0)} | "
            f"{len(review.get('timepoints') or [])} | "
            f"{'ja' if review.get('supplement_needed') else 'nein'} |"
        )
    lines += ["", "## Begruendungen", ""]
    for review in reviews:
        lines.append(f"### {review['pmcid']} - {review['classification']}")
        lines.append("")
        lines.append(review["reason"])
        for item in (review.get("evidence") or [])[:2]:
            cells = " | ".join(str(cell) for cell in item.get("cells", []))
            lines.append(f"- {item['kind']}: {item.get('table', '')} / {item.get('row', '')}: {cells}")
        lines.append("")
    review_md.write_text("\n".join(lines), encoding="utf-8")

    print(dict(counts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
