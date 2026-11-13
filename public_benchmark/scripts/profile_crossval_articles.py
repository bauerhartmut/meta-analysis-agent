#!/usr/bin/env python3
"""Profiliert die Cross-Validation-Artikel und waehlt v2 aus.

Deterministisch, ohne Modell, ohne Netz. Grundlage sind die abgerufenen
Europe-PMC-XML-Volltexte und das Abrufmanifest.

Geprueft wird je Artikel:

- Tabellenstruktur: Anzahl Tabellen, Tabellen mit Armverdacht, Zahlenzellen.
- Kontinuierliches Signal: Mittelwert plus Streuung (``+/-``, ``SD``, ``SE``,
  ``standard deviation``) in einer Tabelle.
- Binaeres Signal: Ereignis-/Prozentzellen (``n (%)``, ``x/y``, ``events``).
- Design: sekundaere Analyse, Pilot, Crossover, Cluster, Mehrarm-Hinweis.
- Supplement: ``supplementary-material`` vorhanden.
- Dublette: gleiche Register-ID oder gleiches Trial-Akronym in einem
  hoeher gerankten Artikel. Der hoeher gerankte Artikel bleibt.

Ausgabe:
- ``fallmix_profile_v1.json``
- ``fallmix_profile_v1.md``
- ``candidate_shortlist_v2.json``
- ``candidate_shortlist_v2.md``
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

BENCH_ROOT = Path(__file__).resolve().parents[1]
ROOT = BENCH_ROOT.parent
OUT_DIR = BENCH_ROOT / "evaluation" / "multi_model_cross_validation"
AVAILABILITY = OUT_DIR / "fulltext_availability_v1.json"
PROFILE_JSON = OUT_DIR / "fallmix_profile_v1.json"
PROFILE_MD = OUT_DIR / "fallmix_profile_v1.md"
SELECTION_V2 = OUT_DIR / "candidate_shortlist_v2.json"
SELECTION_V2_MD = OUT_DIR / "candidate_shortlist_v2.md"

PRIMARY_COUNT = 25
RESERVE_COUNT = 10

REGISTRY = re.compile(
    r"\b(NCT\d{8}|ISRCTN\d+|ChiCTR[\w-]*\d+|DRKS\d+|CTRI/\d{4}/[\d/]+|UMIN\d+|"
    r"ACTRN\d+|EudraCT[\d-]+|IRCT\d+|jRCT\w+|TCTR\d+)\b",
    re.IGNORECASE,
)
ACRONYM = re.compile(r"\b([A-Z][A-Z0-9]{2,}(?:-[A-Z0-9]+)+)\b")
CONTINUOUS = re.compile(r"±|\+/-|\bSD\b|\bSE\b|standard deviation|std\.? dev", re.IGNORECASE)
BINARY = re.compile(
    r"\bn\s*\(\s*%\s*\)|no\.?\s*\(\s*%\s*\)|\bevents?\b|\b\d+\s*/\s*\d+\b", re.IGNORECASE
)
SECONDARY = re.compile(
    r"secondary analysis|post[- ]hoc|subgroup analysis|ancillary study", re.IGNORECASE
)
PILOT = re.compile(r"\bpilot\b|feasibility", re.IGNORECASE)
CROSSOVER = re.compile(r"crossover|cross-over|within[- ]participant", re.IGNORECASE)
CLUSTER = re.compile(r"cluster[- ]randomi[sz]ed", re.IGNORECASE)
MULTIARM = re.compile(
    r"\b(three|four|five)[ -](arm|arms|groups?)\b|\bthree[- ]group\b|\bfour[- ]group\b",
    re.IGNORECASE,
)
REVIEW = re.compile(r"systematic review|meta-analysis|narrative review", re.IGNORECASE)
NUMERIC_CELL = re.compile(r"\d")
# Fliesstext-Signale: RCTs fuehren Armwerte oft im Text statt in einer Tabelle.
TEXT_CONTINUOUS = re.compile(r"±|\+/-|\bmean\s*\(\s*SD\s*\)|\bSD\b", re.IGNORECASE)
TEXT_BINARY = re.compile(r"\b\d+\s*/\s*\d+\b|\b\d+\s*\(\s*\d+(?:\.\d+)?\s*%\s*\)")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def element_text(elem: ET.Element) -> str:
    return " ".join("".join(elem.itertext()).split())


def tables_of(root: ET.Element) -> list[dict[str, Any]]:
    tables = []
    for elem in root.iter():
        if local_name(elem.tag) != "table-wrap":
            continue
        label = ""
        caption = ""
        cells: list[str] = []
        for child in elem.iter():
            name = local_name(child.tag)
            if name == "label" and not label:
                label = element_text(child)
            elif name == "caption" and not caption:
                caption = element_text(child)
            elif name in ("td", "th"):
                text = element_text(child)
                if text:
                    cells.append(text)
        tables.append({"label": label, "caption": caption, "cells": cells})
    return tables


def profile_one(record: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / record["local_path"]
    result: dict[str, Any] = {
        "pmcid": record["pmcid"],
        "rank_sha256": record.get("rank_sha256", ""),
        "batch": record.get("batch", "initial"),
        "position": record["position"],
        "role": record["role"],
        "available": False,
        "sha256": record.get("sha256", ""),
        "table_count": 0,
        "tables_with_arms": 0,
        "numeric_cells": 0,
        "continuous_tables": 0,
        "binary_tables": 0,
        "supplement": False,
        "registry_ids": [],
        "acronyms": [],
        "design_flags": [],
        "reasons": [],
    }
    if not record.get("saved") or not path.exists():
        result["reasons"].append("no_fulltext")
        return result

    try:
        root = ET.fromstring(path.read_bytes())
    except ET.ParseError:
        result["reasons"].append("no_fulltext")
        return result

    result["available"] = True
    full_text = element_text(root)
    tables = tables_of(root)
    result["table_count"] = len(tables)
    for table in tables:
        blob = " ".join([table["caption"]] + table["cells"])
        numeric = sum(1 for cell in table["cells"] if NUMERIC_CELL.search(cell))
        result["numeric_cells"] += numeric
        continuous = bool(CONTINUOUS.search(blob))
        binary = bool(BINARY.search(blob))
        if continuous:
            result["continuous_tables"] += 1
        if binary:
            result["binary_tables"] += 1
        if continuous or binary:
            if numeric >= 6:
                result["tables_with_arms"] += 1

    result["text_continuous_hits"] = len(TEXT_CONTINUOUS.findall(full_text))
    result["text_binary_hits"] = len(TEXT_BINARY.findall(full_text))

    result["supplement"] = any(
        local_name(elem.tag) in ("supplementary-material", "supplementary-material-wrap")
        for elem in root.iter()
    )
    result["registry_ids"] = sorted({m.group(1).upper() for m in REGISTRY.finditer(full_text)})

    title = ""
    for elem in root.iter():
        if local_name(elem.tag) == "article-title":
            title = element_text(elem)
            break
    result["acronyms"] = sorted(set(ACRONYM.findall(title)))

    flags = []
    if SECONDARY.search(title) or SECONDARY.search(full_text[:20000]):
        flags.append("secondary")
    if PILOT.search(title) or PILOT.search(full_text[:20000]):
        flags.append("pilot")
    if CROSSOVER.search(full_text[:20000]):
        flags.append("crossover")
    if CLUSTER.search(full_text[:20000]):
        flags.append("cluster")
    if MULTIARM.search(full_text[:20000]):
        flags.append("multiarm")
    if REVIEW.search(title):
        flags.append("review_title")
    result["design_flags"] = flags

    if "review_title" in flags:
        result["reasons"].append("review_or_summary")
    if result["tables_with_arms"] == 0:
        # Ohne Tabelle ist ein Artikel nur dann ungeeignet, wenn auch der Text
        # keine Armwerte andeutet. Sonst bleibt er als text-only annotierbar.
        if result["text_continuous_hits"] >= 2 or result["text_binary_hits"] >= 2:
            flags.append("text_only_arm_data")
        else:
            result["reasons"].append("no_arm_data")
    return result


def mark_duplicates(profiles: list[dict[str, Any]]) -> None:
    """Markiert Dubletten desselben Trials, der hoeher gerankte Artikel bleibt."""
    seen_registry: dict[str, str] = {}
    seen_acronym: dict[str, str] = {}
    for profile in sorted(profiles, key=lambda row: row["position"]):
        duplicate_of = ""
        for registry in profile["registry_ids"]:
            if registry in seen_registry:
                duplicate_of = seen_registry[registry]
                break
        if not duplicate_of:
            for acronym in profile["acronyms"]:
                if len(acronym) >= 5 and acronym in seen_acronym:
                    duplicate_of = seen_acronym[acronym]
                    break
        if duplicate_of:
            profile["duplicate_of"] = duplicate_of
            profile["reasons"].append("duplicate_trial")
            continue
        for registry in profile["registry_ids"]:
            seen_registry.setdefault(registry, profile["pmcid"])
        for acronym in profile["acronyms"]:
            if len(acronym) >= 5:
                seen_acronym.setdefault(acronym, profile["pmcid"])


def build() -> dict[str, Any]:
    availability = json.loads(AVAILABILITY.read_text(encoding="utf-8"))
    profiles = [profile_one(record) for record in availability["records"]]
    # Kanonische Rangfolge aus dem Pool-Hash, unabhaengig von der Reihenfolge
    # im Abrufmanifest. Ersatzartikel stehen damit an derselben Stelle wie im
    # gerankten Pool.
    profiles.sort(key=lambda row: row["rank_sha256"])
    for index, row in enumerate(profiles, start=1):
        row["position"] = index
    mark_duplicates(profiles)

    suitable = [row for row in profiles if not row["reasons"]]
    primary = suitable[:PRIMARY_COUNT]
    reserve = suitable[PRIMARY_COUNT: PRIMARY_COUNT + RESERVE_COUNT]

    for row in profiles:
        row["selected"] = ""
    for row in primary:
        row["selected"] = "primary"
    for row in reserve:
        row["selected"] = "reserve"

    counts = Counter()
    for row in profiles:
        for reason in row["reasons"]:
            counts[reason] += 1

    def mix(rows: list[dict[str, Any]]) -> dict[str, int]:
        return {
            "articles": len(rows),
            "continuous_signal": sum(1 for row in rows if row["continuous_tables"] > 0),
            "binary_signal": sum(1 for row in rows if row["binary_tables"] > 0),
            "both_signals": sum(
                1 for row in rows if row["continuous_tables"] > 0 and row["binary_tables"] > 0
            ),
            "multiarm": sum(1 for row in rows if "multiarm" in row["design_flags"]),
            "crossover": sum(1 for row in rows if "crossover" in row["design_flags"]),
            "pilot": sum(1 for row in rows if "pilot" in row["design_flags"]),
            "secondary": sum(1 for row in rows if "secondary" in row["design_flags"]),
            "cluster": sum(1 for row in rows if "cluster" in row["design_flags"]),
            "with_supplement": sum(1 for row in rows if row["supplement"]),
            "tables_total": sum(row["table_count"] for row in rows),
        }

    checks = {
        "primary_count_ok": len(primary) == PRIMARY_COUNT,
        "reserve_count_ok": len(reserve) == RESERVE_COUNT,
        "no_duplicates_in_selection": not any(
            row["reasons"] for row in primary + reserve
        ),
        "all_selected_available": all(row["available"] for row in primary + reserve),
        "unsuitable_reasons": dict(counts),
        "shortfall_primary": max(0, PRIMARY_COUNT - len(primary)),
        "shortfall_reserve": max(0, RESERVE_COUNT - len(reserve)),
    }
    checks["ok"] = all(
        checks[key]
        for key in (
            "primary_count_ok",
            "reserve_count_ok",
            "no_duplicates_in_selection",
            "all_selected_available",
        )
    )

    return {
        "profile_id": "crossval_fallmix_v1",
        "created": date.today().isoformat(),
        "status": "ready" if checks["ok"] else "shortfall",
        "model_used": False,
        "method": {
            "continuous": "Tabelle enthaelt Mittelwert mit Streuung (+/-, SD, SE, standard deviation) und mindestens 6 Zahlenzellen",
            "binary": "Tabelle enthaelt Ereignis- oder Prozentzellen (n (%), x/y, events)",
            "duplicate": "gleiche Register-ID oder gleiches Trial-Akronym (>= 5 Zeichen) im Titel; der hoeher gerankte Artikel bleibt",
            "no_arm_data": "keine Tabelle mit Armverdacht und weniger als 2 Zahlensignale im Text; Artikel bleibt dokumentiert, wird aber nicht annotiert",
            "text_only_arm_data": "keine Arm-Tabelle erkannt, aber Zahlensignale im Fliesstext; bleibt annotierbar und wird als text-only gefuehrt",
        },
        "case_mix_primary": mix(primary),
        "case_mix_reserve": mix(reserve),
        "checks": checks,
        "profiles": profiles,
        "selection": {"primary": [row["pmcid"] for row in primary],
                      "reserve": [row["pmcid"] for row in reserve]},
    }


def render_md(payload: dict[str, Any]) -> str:
    checks = payload["checks"]
    mix = payload["case_mix_primary"]
    lines = [
        "# Cross-Validation: Fallmix und Eignung v1",
        "",
        f"Stand: {payload['created']}",
        f"Status: **{payload['status']}**",
        "Deterministisch aus den abgerufenen XML-Volltexten. Kein Modell.",
        "",
        "## Fallmix der Auswahl v2 (primaer)",
        "",
        "| Merkmal | Artikel |",
        "|---|---:|",
        f"| Artikel | {mix['articles']} |",
        f"| kontinuierliches Tabellensignal | {mix['continuous_signal']} |",
        f"| binaeres Tabellensignal | {mix['binary_signal']} |",
        f"| beide Signale | {mix['both_signals']} |",
        f"| Mehrarm-Hinweis | {mix['multiarm']} |",
        f"| Crossover | {mix['crossover']} |",
        f"| Cluster-randomisiert | {mix['cluster']} |",
        f"| Pilot/Feasibility | {mix['pilot']} |",
        f"| sekundaere Analyse | {mix['secondary']} |",
        f"| mit Supplement | {mix['with_supplement']} |",
        f"| Tabellen gesamt | {mix['tables_total']} |",
        "",
        "## Ausschluesse",
        "",
        "| Grund | Artikel |",
        "|---|---:|",
    ]
    for reason, count in sorted(checks["unsuitable_reasons"].items()):
        lines.append(f"| {reason} | {count} |")
    lines += [
        "",
        "## Einzelprofile",
        "",
        "| # | PMCID | Tabellen | Arm-Tabellen | kont. | bin. | Text-Signale (k/b) | Design | Ausschluss |",
        "|---:|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["profiles"]:
        flags = ",".join(row["design_flags"]) or "-"
        reasons = ",".join(row["reasons"]) or "-"
        lines.append(
            f"| {row['position']} | {row['pmcid']} | {row['table_count']} | "
            f"{row['tables_with_arms']} | {row['continuous_tables']} | "
            f"{row['binary_tables']} | {row['text_continuous_hits']}/{row['text_binary_hits']} | "
            f"{flags} | {reasons} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_selection(payload: dict[str, Any], availability: dict[str, Any]) -> str:
    by_pmcid = {row["pmcid"]: row for row in availability["records"]}
    prof = {row["pmcid"]: row for row in payload["profiles"]}
    lines = [
        "# Cross-Validation: Artikelauswahl v2",
        "",
        f"Stand: {payload['created']}",
        "Auswahl nach Fallmix- und Dublettenpruefung. Kein Modellaufruf.",
        "",
        "| # | Rolle | PMCID | kont. | bin. | Design | Supplement |",
        "|---:|---|---|---:|---:|---|---|",
    ]
    position = 0
    for role in ("primary", "reserve"):
        for pmcid in payload["selection"][role]:
            position += 1
            row = prof[pmcid]
            lines.append(
                f"| {position} | {role} | {pmcid} | {row['continuous_tables']} | "
                f"{row['binary_tables']} | {','.join(row['design_flags']) or '-'} | "
                f"{'ja' if row['supplement'] else 'nein'} |"
            )
    lines += [
        "",
        "## Regeln",
        "",
        "1. Nur Artikel mit Volltext, ohne Review-Titel und mit mindestens einer",
        "   Tabelle, die Armwerte erwarten laesst.",
        "2. Kein Artikel eines Trials, der bereits durch einen hoeher gerankten",
        "   Artikel vertreten ist (Register-ID oder Trial-Akronym).",
        "3. Reihenfolge und Rang bleiben aus v1 erhalten.",
        "",
        "Die Eignung ist ein Tabellensignal, keine Extraktionsbestaetigung. Die",
        "Volltextpruefung vor der Annotation entscheidet endgueltig.",
        "",
        f"Verfuegbarkeit: {availability['saved']}/{availability['requested']} XML abgerufen.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    payload = build()
    PROFILE_JSON.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    PROFILE_MD.write_text(render_md(payload), encoding="utf-8")

    availability = json.loads(AVAILABILITY.read_text(encoding="utf-8"))
    SELECTION_V2.write_text(
        json.dumps(
            {
                "dataset": "crossval_exploration",
                "version": "2.0",
                "created": payload["created"],
                "status": "selected_pending_annotation"
                if payload["checks"]["ok"]
                else "shortfall",
                "model_used": False,
                "network_used": False,
                "source_profile": "fallmix_profile_v1.json",
                "primary_count": len(payload["selection"]["primary"]),
                "reserve_count": len(payload["selection"]["reserve"]),
                "checks": payload["checks"],
                "articles": [
                    {
                        "position": index,
                        "role": "primary" if index <= PRIMARY_COUNT else "reserve",
                        "pmcid": pmcid,
                        "sha256": next(
                            row["sha256"]
                            for row in availability["records"]
                            if row["pmcid"] == pmcid
                        ),
                        "profile": next(
                            {
                                key: row[key]
                                for key in (
                                    "continuous_tables",
                                    "binary_tables",
                                    "table_count",
                                    "tables_with_arms",
                                    "supplement",
                                    "design_flags",
                                )
                            }
                            for row in payload["profiles"]
                            if row["pmcid"] == pmcid
                        ),
                        "reserved_for": "crossval_exploration",
                    }
                    for index, pmcid in enumerate(
                        payload["selection"]["primary"] + payload["selection"]["reserve"],
                        start=1,
                    )
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    SELECTION_V2_MD.write_text(render_selection(payload, availability), encoding="utf-8")

    mix = payload["case_mix_primary"]
    print(f"primaer {mix['articles']}, reserve {len(payload['selection']['reserve'])}")
    print(f"kontinuierlich {mix['continuous_signal']}, binaer {mix['binary_signal']}, "
          f"beide {mix['both_signals']}, multiarm {mix['multiarm']}")
    print(f"Ausschluesse: {payload['checks']['unsuitable_reasons']}")
    print(f"Status: {payload['status']}")
    return 0 if payload["checks"]["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
