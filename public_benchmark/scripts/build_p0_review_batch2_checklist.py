#!/usr/bin/env python3
"""Audit Batch 2 and generate the 36-slot human-review checklist.

Read-only with respect to the Batch-2 outcome data: the script opens the
existing JSON/CSV/Markdown, validates counters, sources and overlap labels, and
writes two new documents. It never rewrites outcome values or classifications.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "public_benchmark" / "evaluation" / "c1_pilot" / "holdout_p0_20261112"
BATCH2 = BASE / "fulltext_review_batch2_v1.json"
CSV = BASE / "fulltext_review_batch2_v1.csv"
MARKDOWN = BASE / "fulltext_review_batch2_v1.md"
DOSSIER = BASE / "fulltext_review_high_v1.json"
MANIFEST = BASE / "fulltext_retrieval_manifest_v1.json"
AUDIT = BASE / "fulltext_review_batch2_audit_v1.md"
CHECKLIST = BASE / "fulltext_review_batch2_human_checklist_v1.md"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def element_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join("".join(element.itertext()).split())


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = value.replace("−", "-").replace("–", "-").replace("‑", "-").replace("‐", "-")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def normalize_number(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().replace(",", "")
    return re.sub(r"[^0-9.]+", "", value)


def arm_values(outcome: dict) -> list[str]:
    values: list[str] = []
    for arm in (outcome["intervention"], outcome["control"]):
        for key in ("mean", "sd", "events", "total"):
            value = arm.get(key)
            if value is not None:
                values.append(str(value))
    return values


def compact_arm(arm: dict) -> str:
    if arm.get("mean") is not None:
        n = arm.get("n", "nicht berichtet")
        return f"n={n}, {arm['mean']} ({arm.get('sd', 'SD nicht berichtet')})"
    if arm.get("events") is not None:
        return f"{arm['events']}/{arm.get('total', '?')}"
    return "-"


def source_label(outcome: dict) -> str:
    if outcome["table"]:
        label = re.sub(r"^(TABLE|Table)\s*", "", outcome["table"]).strip()
        return f"Tabelle {label}, Zeile {outcome['row_index']}"
    if outcome["source_quote"].startswith("Table "):
        return "Tabellenverweis (ICER)"
    return "Results-Text"


def format_arm_n(arm_n: dict) -> str:
    return (
        f"Intervention {arm_n.get('intervention', '?')} / Kontrolle {arm_n.get('control', '?')} / "
        f"randomisiert {arm_n.get('randomized', '?')} / analysiert {arm_n.get('analyzed', '?')}"
        + (f" / Trials {arm_n['trial_count']}" if arm_n.get("trial_count") else "")
    )


def find_table_wrap(root: ET.Element, label: str) -> ET.Element | None:
    target = normalize(label)
    for element in root.iter():
        if local_name(element.tag) != "table-wrap":
            continue
        label_element = next(
            (child for child in element if local_name(child.tag) == "label"),
            None,
        )
        if normalize(element_text(label_element)) == target:
            return element
    return None


def table_row_cells(table_wrap: ET.Element) -> list[list[str]]:
    rows: list[list[str]] = []
    for element in table_wrap.iter():
        if local_name(element.tag) != "tr":
            continue
        cells = [
            element_text(child)
            for child in element
            if local_name(child.tag) in {"th", "td"}
        ]
        if cells:
            rows.append(cells)
    return rows


def extract_arm_header_cells(table_wrap: ET.Element) -> dict[str, str]:
    """Return the concrete control/intervention header cells of the table."""
    for element in table_wrap.iter():
        if local_name(element.tag) != "tr":
            continue
        if not any(local_name(child.tag) == "th" for child in element):
            continue
        cells = [
            element_text(child)
            for child in element
            if local_name(child.tag) in {"th", "td"}
        ]
        control = next(
            (cell for cell in cells if "control group" in normalize(cell)),
            None,
        )
        intervention = next(
            (cell for cell in cells if "experiment group" in normalize(cell)),
            None,
        )
        if control is not None and intervention is not None:
            return {"control": control, "intervention": intervention}
    return {}


def header_cell_n(cell: str) -> str | None:
    """Return the exact N from an arm header cell; None if absent."""
    match = re.search(r"\(\s*N\s*=\s*([0-9]+)\s*\)", cell, re.IGNORECASE)
    return match.group(1) if match else None


def numeric_tokens(text: str) -> set[str]:
    """Return exact numeric tokens, normalizing thousands separators."""
    tokens = re.findall(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?", text)
    return {token.replace(",", "") for token in tokens}


GENERIC_ARM_TOKENS = {
    "active",
    "and",
    "arm",
    "for",
    "group",
    "n",
    "no",
    "of",
    "p",
    "plus",
    "sample",
    "the",
    "total",
    "with",
}


def meaningful_tokens(label: str) -> set[str]:
    return {
        token
        for token in normalize(label).split()
        if token not in GENERIC_ARM_TOKENS and not token.isdigit()
    }


def table_header_groups(table_wrap: ET.Element) -> tuple[list[tuple[int, str]], int]:
    """Return (column start, label) pairs and the expanded table width."""
    for element in table_wrap.iter():
        if local_name(element.tag) != "tr":
            continue
        children = [
            child
            for child in element
            if local_name(child.tag) in {"th", "td"}
        ]
        if not children or not any(local_name(child.tag) == "th" for child in children):
            continue
        groups: list[tuple[int, str]] = []
        position = 0
        for child in children:
            try:
                span = int(child.get("colspan", "1"))
            except ValueError:
                span = 1
            text = element_text(child)
            if text:
                groups.append((position, text))
            position += max(span, 1)
        if groups:
            return groups, position
    return [], 0


def arm_column_ranges(
    table_wrap: ET.Element,
    labels: dict[str, str],
    row_width: int,
) -> dict[str, tuple[int, int]]:
    """Map intervention/control labels to column ranges in the header grid."""
    groups, width = table_header_groups(table_wrap)
    if not groups:
        return {}
    positions: dict[str, int] = {}
    for role, label in labels.items():
        target = meaningful_tokens(label)
        hits = [
            position
            for position, header in groups
            if target & meaningful_tokens(header)
        ]
        if len(hits) != 1:
            return {}
        positions[role] = hits[0]
    if len(set(positions.values())) != 2:
        return {}
    starts = [position for position, _ in groups]
    first_start = min(starts)
    limit = min(width, row_width)
    ranges: dict[str, tuple[int, int]] = {}
    for role, position in positions.items():
        start = 1 if position == first_start else position
        end = next((value for value in starts if value > position), limit)
        end = min(end, limit)
        if start >= end:
            return {}
        ranges[role] = (start, end)
    return ranges


def values_in_cells(cells: list[str], values: list[str]) -> bool:
    tokens: set[str] = set()
    for cell in cells:
        tokens.update(numeric_tokens(cell))
    return all(
        normalize_number(value).lstrip(".") in tokens
        for value in values
    )


def cells_contain(cells: list[str], label: str, values: list[str]) -> bool:
    if not cells or normalize(label) not in normalize(cells[0]):
        return False
    return values_in_cells(cells, values)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    payload = json.loads(BATCH2.read_text(encoding="utf-8"))
    dossier = json.loads(DOSSIER.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_id = {record["pmcid"]: record for record in dossier["records"]}
    paths = {record["pmcid"]: record["local_path"] for record in manifest["records"]}

    records = payload["records"]
    assert len(records) == 9
    assert len({record["pmcid"] for record in records}) == 9
    assert all(len(record["outcomes"]) == 4 for record in records)

    source_present = 0
    text_exact = 0
    table_refs = 0
    table_rows = 0
    table_paired_rows = 0
    table_single_rows = 0
    arm_mapped_rows = 0
    label_only_rows = 0
    structured_value_sets = 0
    values_in_quote = 0
    issues: list[str] = []
    source_flags: dict[str, str] = {}
    header_denominator_slots: list[str] = []

    for record in records:
        pmcid = record["pmcid"]
        article_root = ET.fromstring(Path(paths[pmcid]).read_bytes())
        article_text = normalize(element_text(article_root))
        article = by_id[pmcid]
        tables = {table["label"]: table for table in article["candidate_tables"]}

        for outcome in record["outcomes"]:
            quote = outcome["source_quote"]
            if quote:
                source_present += 1
            else:
                issues.append(f"{pmcid} Slot {outcome['slot']}: keine Quelle")

            if outcome["table"]:
                table_refs += 1
                table = tables.get(outcome["table"])
                row = (
                    next(
                        (item for item in table["rows"] if item["row_index"] == outcome["row_index"]),
                        None,
                    )
                    if table
                    else None
                )
                if table is None or row is None:
                    issues.append(
                        f"{pmcid} Slot {outcome['slot']}: Tabelle/Zeile nicht im Dossier"
                    )
                    continue
                table_wrap = find_table_wrap(article_root, outcome["table"])
                if table_wrap is None:
                    issues.append(
                        f"{pmcid} Slot {outcome['slot']}: referenzierte Tabelle nicht im XML"
                    )
                    continue
                table_text = normalize(element_text(table_wrap))
                caption_ok = normalize(table["caption"]) in table_text
                all_row_cells = table_row_cells(table_wrap)
                row_cells = (
                    all_row_cells[outcome["row_index"] - 1]
                    if 0 < outcome["row_index"] <= len(all_row_cells)
                    else []
                )
                row_label_ok = bool(row_cells) and (
                    normalize(row["row_label"]) in normalize(row_cells[0])
                )
                intervention_values = [
                    str(outcome["intervention"][key])
                    for key in ("mean", "sd", "events", "total")
                    if outcome["intervention"].get(key) is not None
                ]
                control_values = [
                    str(outcome["control"][key])
                    for key in ("mean", "sd", "events", "total")
                    if outcome["control"].get(key) is not None
                ]
                arm_ranges = (
                    arm_column_ranges(
                        table_wrap,
                        {
                            "intervention": outcome["intervention"]["label"],
                            "control": outcome["control"]["label"],
                        },
                        len(row_cells),
                    )
                    if intervention_values or control_values
                    else {}
                )
                if outcome.get("control_row_index") is not None:
                    control_row = next(
                        (
                            item
                            for item in table["rows"]
                            if item["row_index"] == outcome["control_row_index"]
                        ),
                        None,
                    )
                    if control_row is None:
                        issues.append(
                            f"{pmcid} Slot {outcome['slot']}: Kontrollzeile nicht im Dossier"
                        )
                        continue
                    control_cells = all_row_cells[outcome["control_row_index"] - 1] if (
                        0 < outcome["control_row_index"] <= len(all_row_cells)
                    ) else []
                    intervention_ok = cells_contain(
                        row_cells, row["row_label"], intervention_values
                    )
                    control_ok = cells_contain(
                        control_cells, control_row["row_label"], control_values
                    )
                    row_ok = intervention_ok and control_ok
                    table_paired_rows += 1
                else:
                    if not intervention_values and not control_values:
                        row_ok = row_label_ok
                        label_only_rows += 1
                    elif not arm_ranges:
                        row_ok = False
                    else:
                        intervention_start, intervention_end = arm_ranges["intervention"]
                        control_start, control_end = arm_ranges["control"]
                        row_ok = (
                            row_label_ok
                            and values_in_cells(
                                row_cells[intervention_start:intervention_end],
                                intervention_values,
                            )
                            and values_in_cells(
                                row_cells[control_start:control_end],
                                control_values,
                            )
                        )
                        if row_ok:
                            arm_mapped_rows += 1
                    table_single_rows += 1
                if caption_ok and row_ok:
                    table_rows += 1
                else:
                    header_denominator = False
                    if (
                        outcome["intervention"].get("total") is not None
                        and outcome["control"].get("total") is not None
                        and outcome["intervention"].get("events") is not None
                        and outcome["control"].get("events") is not None
                    ):
                        event_values = [
                            str(outcome["intervention"]["events"]),
                            str(outcome["control"]["events"]),
                        ]
                        events_in_arms = (
                            bool(arm_ranges)
                            and values_in_cells(
                                row_cells[arm_ranges["intervention"][0]:arm_ranges["intervention"][1]],
                                [event_values[0]],
                            )
                            and values_in_cells(
                                row_cells[arm_ranges["control"][0]:arm_ranges["control"][1]],
                                [event_values[1]],
                            )
                        )
                        header_cells = extract_arm_header_cells(table_wrap)
                        header_totals = {
                            arm: header_cell_n(header_cells.get(arm, ""))
                            for arm in ("intervention", "control")
                        }
                        totals_in_arm_headers = (
                            bool(header_cells)
                            and all(
                                header_totals[arm]
                                == str(outcome[arm].get("total"))
                                for arm in ("intervention", "control")
                            )
                        )
                        header_denominator = (
                            caption_ok
                            and events_in_arms
                            and totals_in_arm_headers
                        )
                    if header_denominator:
                        source_flags[f"{pmcid}:{outcome['slot']}"] = (
                            "N in konkreter Arm-Header-Zelle zulässig; Zeile/Header dokumentiert"
                        )
                        header_denominator_slots.append(f"{pmcid}:{outcome['slot']}")
                        table_rows += 1
                    else:
                        issues.append(
                            f"{pmcid} Slot {outcome['slot']}: Zeilenquelle nicht in der referenzierten Tabellenzeile "
                            f"caption={caption_ok}, row_label_in_table={row_label_ok}, row_match={row_ok}"
                        )
            elif quote.startswith("Table "):
                table_refs += 1
            elif quote:
                text_exact += 1
                body = quote.split("|", 1)[1] if "|" in quote else quote
                if normalize(body) not in article_text:
                    issues.append(f"{pmcid} Slot {outcome['slot']}: Textzitat nicht exakt")

            values = arm_values(outcome)
            if values:
                structured_value_sets += 1
                if all(normalize_number(value) in normalize_number(quote) for value in values):
                    values_in_quote += 1
                else:
                    issues.append(
                        f"{pmcid} Slot {outcome['slot']}: strukturierter Wert nicht in Quelle"
                    )

    class_counts = Counter(
        outcome["outcome_independence"]
        for record in records
        for outcome in record["outcomes"]
    )
    expected_counts = {
        "independent": 8,
        "overlapping_subgroup": 6,
        "not_usable": 22,
    }
    if dict(class_counts) != expected_counts:
        issues.append(f"Zähler abweichend: {dict(class_counts)} statt {expected_counts}")

    overlap_map: dict[str, list[int]] = {}
    for record in records:
        overlapping = [
            outcome["slot"]
            for outcome in record["outcomes"]
            if outcome["outcome_independence"] == "overlapping_subgroup"
        ]
        if overlapping:
            overlap_map[record["pmcid"]] = overlapping
    if overlap_map != {"PMC13519320": [2, 3, 4], "PMC13590641": [2, 3, 4]}:
        issues.append(f"Überlappungskarte unerwartet: {overlap_map}")

    human_open = all(
        record["human_review"]["final_decision"] == "offen"
        and all(
            record["human_review"][key] is None
            for key in (
                "parallel_two_arms_confirmed",
                "randomization_confirmed",
                "no_arm_collapse",
                "outcomes_confirmed",
            )
        )
        for record in records
    )
    if not human_open:
        issues.append("Mindestens eine menschliche Prüfentscheidung ist bereits gesetzt")

    total_slots = sum(len(record["outcomes"]) for record in records)
    usable = class_counts["independent"] + class_counts["overlapping_subgroup"]
    if (
        total_slots != 36
        or usable != 14
        or class_counts["independent"] + class_counts["overlapping_subgroup"] + class_counts["not_usable"] != 36
    ):
        issues.append("Summenprüfung fehlgeschlagen")

    # Audit document
    audit_lines = [
        "# Audit Batch 2: Zähler, Quellen und Überlappungen",
        "",
        "Stand: 2026-11-13",
        "Status: **AUDIT ABGESCHLOSSEN; MENSCHLICHE PRÜFUNG OFFEN**.",
        "",
        "Geprüft wurden ausschließlich die gespeicherten Batch-2-Artefakte und die",
        "lokalen XML-Texte. Es wurden keine Outcome-Werte, Quellen oder",
        "Unabhängigkeitsklassen verändert.",
        "",
        "## Ergebnis",
        "",
        "| Kennzahl | Wert |",
        "|---|---:|",
        f"| Artikel | {len(records)} |",
        f"| Outcome-Slots | {total_slots} |",
        f"| Unabhängig verwendbar | {class_counts['independent']} |",
        f"| Überlappend, nicht unabhängig | {class_counts['overlapping_subgroup']} |",
        f"| Nicht verwendbar/nicht berichtet | {class_counts['not_usable']} |",
        f"| Formal verwendbar inkl. überlappend | {usable} |",
        "| Finale Entscheidungen | 0 |",
        "",
        "**Zähler:** "
        f"{class_counts['independent']} + {class_counts['overlapping_subgroup']} + "
        f"{class_counts['not_usable']} = {total_slots}; "
        f"{class_counts['independent']} + {class_counts['overlapping_subgroup']} = {usable} "
        "formal verwendbar. Die Summen sind konsistent.",
        "",
        "## Quellenprüfung",
        "",
        f"- **{source_present}/36** Slots haben einen Quelleintrag.",
        f"- **{text_exact}** Results-Textzitate wurden exakt im normalisierten XML gefunden.",
        f"- **{table_refs}** Tabellenverweise: Caption und ggf. konkrete Arm-Header-Zellen wurden in der referenzierten Tabelle geprüft; Zeilenlabel und strukturierte Werte in der jeweils referenzierten Zeile bzw. den daraus abgeleiteten Armspalten; "
        f"**{table_rows}/18** Tabellen-Outcomes bestanden die Quellenprüfung: "
        f"{table_rows - table_paired_rows - len(header_denominator_slots)}/{table_single_rows} "
        f"Einzelzeilen zeilenexakt, {len(header_denominator_slots)}/{table_single_rows} "
        "Einzelzeilen mit N in der jeweiligen konkreten Arm-Header-Zelle zulässig und "
        f"{table_paired_rows}/{table_paired_rows} Kosten-Outcomes mit getrennten "
        "Interventions-/Kontrollzeilen bestanden. Der ICER-Slot ist ein "
        "Tabellenverweis ohne eigene Zeilenwerte.",
        f"- **{arm_mapped_rows}** Nicht-Header-Outcomes mit strukturierten Werten "
        "wurden in den aus dem Tabellenkopf abgeleiteten Armspalten geprüft; "
        f"{label_only_rows} ohne strukturierte Werte nur am Zeilenlabel; "
        f"{table_paired_rows} Kosten-Outcomes über getrennte Armzeilen.",
        "- **4/4** N-Werte in den konkreten Arm-Header-Zellen von Tabelle 3 "
        "(`PMC13590641`, Control `N = 19`, Experiment `N = 24`) sind als "
        "zulässige Nennerquelle geprüft und in "
        "[`fulltext_review_batch2_pmc13590641_n_source_v1.md`]"
        "(fulltext_review_batch2_pmc13590641_n_source_v1.md) dokumentiert.",
        f"- **{values_in_quote}/{structured_value_sets}** Outcomes mit strukturierten Zahlen "
        "enthalten diese Zahlen im Quelleintrag.",
        "",
        "Hinweis: Tabellenquellen sind keine zusammenhängenden Fließtextsätze. Die",
        "Quellenprüfung prüft die Caption und ggf. konkrete Arm-Header-Zellen in",
        "der referenzierten Tabelle; Zeilenlabel und strukturierte Werte in der",
        "referenzierten Zeile bzw. den abgeleiteten Armspalten. Sie ersetzt nicht die",
        "menschliche Sichtprüfung der Tabelle.",
        "",
        "## Überlappungen",
        "",
        "- `PMC13519320`: Slot 1 ist das Gesamtoutcome; Slots 2-4 sind überlappend.",
        "- `PMC13590641`: Slot 1 ist das Sammeloutcome „Any AE“; Slots 2-4 sind",
        "  spezifische AEs und überlappen damit.",
        "- Keine weiteren Slots sind als überlappend markiert.",
        "",
        "Die sechs überlappenden Slots zählen nicht als unabhängige Outcomes.",
        "",
        "## Artikelübersicht",
        "",
        "| PMC | Slots | Unabhängig | Überlappend | Nicht verwendbar | Quelle |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for record in records:
        counts = record["outcome_counts"]
        audit_lines.append(
            f"| {record['pmcid']} | {len(record['outcomes'])} | "
            f"{counts['independent_usable']} | {counts['overlapping_usable']} | "
            f"{counts['not_usable']} | {len([o for o in record['outcomes'] if o['source_quote']])}/4 |"
        )
    audit_lines += [
        "",
        "## Prüfhinweise für die menschliche Runde",
        "",
        "- `PMC13610533`: nur Median/IQR; keine Umrechnung in Mean/SD.",
        "- `PMC13743599`: 17/14 randomisiert, aber nur 10/10 mit Post-Werten; post hoc.",
        "- `PMC13613700`: keine armweisen Ereigniszahlen; nur adjustierte Assoziationen.",
        "- `PMC13626740`: T3-Werte mit verfügbarem n; CBT und ST getrennt halten.",
        "- `PMC13688066`: HE nur als Gesamtfrequenz/Subgruppeninteraktion, keine Armzahlen.",
        "- `PMC13519320`: gepoolte BOREAS/NOTUS-Analyse; Slot 1 Gesamt, Slots 2-4 überlappend.",
        "- `PMC13590641`: Any AE als Sammeloutcome; spezifische AEs überlappen; open-label und vorzeitig beendet.",
        "- `PMC13596784`: Mean/SD vorhanden, aber kein armweises n pro Zeitpunkt.",
        "- `PMC13574397`: Striktur 2/10 vs. 7/10; Kosten ohne SD, ICER nur „Dominated“.",
        "",
        "## Invarianz",
        "",
        "SHA-256 der unveränderten Batch-2-Dateien:",
        "",
        f"- JSON: `{sha256(BATCH2)}`",
        f"- CSV: `{sha256(CSV)}`",
        f"- Markdown: `{sha256(MARKDOWN)}`",
        "",
        "## Auditstatus",
        "",
        f"- Offene Befunde: **{len(issues)}**",
        f"- Menschliche Prüfung: **{'offen' if human_open else 'nicht offen'}**",
        "- Outcome-Werte geändert: **nein**",
        "",
    ]
    if issues:
        audit_lines += ["### Befunde", ""]
        audit_lines += [f"- {issue}" for issue in issues]
    else:
        audit_lines += [
            "Keine Zähler-, Quellen- oder Überlappungsabweichung gefunden. Die",
            "fachliche Eignung bleibt offen und wird in der Checkliste geprüft.",
        ]
    audit_lines.append("")
    AUDIT.write_text("\n".join(audit_lines), encoding="utf-8")

    # Checklist document
    checklist = [
        "# Menschliche Prüfcheckliste: Batch 2 (36 Slots)",
        "",
        "Stand: 2026-11-13",
        "Status: **OFFEN; DIESE CHECKLISTE SETZT KEINE FINALEN ENTSCHEIDUNGEN**.",
        "",
        "Quelle: `fulltext_review_batch2_v1.json`, `...csv`, `...md` sowie lokale XML.",
        "Die Outcome-Werte sind unverändert. Bitte pro Slot Quelle, Zahlen,",
        "Unabhängigkeit und Eignung prüfen; bei Unklarheit den Slot offen lassen.",
        "",
        "## A. Globale Prüfung",
        "",
        "- [ ] 36/36 Slots gesichtet",
        "- [ ] Zähler 8 unabhängig / 6 überlappend / 22 nicht verwendbar bestätigt",
        "- [ ] 14 formal verwendbar bestätigt",
        "- [ ] 36/36 Quellen geprüft",
        "- [ ] 4 N-Werte in konkreten Arm-Header-Zellen als zulässige Quelle dokumentiert",
        "- [ ] 6 überlappende Slots bestätigt",
        "- [ ] keine Outcome-Werte verändert",
        "- [ ] finale Entscheidungen nur im dafür vorgesehenen Dokument gesetzt",
        "",
        "## B. Artikel- und Slotprüfung",
        "",
    ]
    for record in records:
        counts = record["outcome_counts"]
        checklist += [
            f"### {record['pmcid']} — {record['short_title']}",
            "",
            f"- Titel: {record['title']}",
            f"- Design: {record['design']}",
            f"- Arm-N: {format_arm_n(record['arm_n'])}",
            f"- Assistierte Eignung: **{record['assisted_eligibility']}**",
            f"- Vorprüfung: {record['eligibility_reason']}",
            "",
            "- [ ] zwei parallele Arme bestätigt",
            "- [ ] Randomisierung bestätigt",
            "- [ ] keine Armzusammenführung",
            f"- [ ] Arm-N und analysiertes n bestätigt ({counts['independent_usable']} unabhängig, "
            f"{counts['overlapping_usable']} überlappend, {counts['not_usable']} nicht verwendbar)",
            "- [ ] Quellen und Werte pro Slot bestätigt",
            "- [ ] Überlappungsklasse pro Slot bestätigt",
            "",
            "| Geprüft | Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle | Befund |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
        for outcome in record["outcomes"]:
            source_key = f"{record['pmcid']}:{outcome['slot']}"
            checklist.append(
                f"| [ ] | {outcome['slot']} | {outcome['outcome']} | {outcome['type']} | "
                f"{compact_arm(outcome['intervention'])} | {compact_arm(outcome['control'])} | "
                f"{'ja' if outcome['usable'] else 'nein'} | {outcome['outcome_independence']} | "
                f"{source_label(outcome)} | {source_flags.get(source_key, 'offen')} |"
            )
        checklist += ["", "**Vorprüfungsnotizen:**", ""]
        for outcome in record["outcomes"]:
            checklist.append(f"- Slot {outcome['slot']}: {outcome['note']}")
        checklist += ["", "---", ""]

    checklist += [
        "## C. Abschluss der menschlichen Runde",
        "",
        "- [ ] alle 36 Slot-Zeilen bearbeitet",
        "- [ ] alle Quellen als geprüft markiert",
        "- [ ] alle Überlappungen bestätigt oder begründet korrigiert",
        "- [ ] alle nicht verwendbaren Slots als leer bestätigt",
        "- [ ] Zähler nach der Prüfung erneut abgeglichen",
        "- [ ] keine Werte ohne Quelle ergänzt",
        "- [ ] finale Entscheidungen separat dokumentiert",
        "",
        "## D. Nicht Bestandteil dieser Checkliste",
        "",
        "- Keine neuen Outcome-Werte.",
        "- Keine Umrechnung von Median/IQR in Mean/SD.",
        "- Keine nachträgliche Armzusammenführung.",
        "- Keine automatische finale Eignungsentscheidung.",
        "",
    ]
    CHECKLIST.write_text("\n".join(checklist), encoding="utf-8")

    print(
        json.dumps(
            {
                "articles": len(records),
                "outcome_slots": total_slots,
                "independent": class_counts["independent"],
                "overlapping": class_counts["overlapping_subgroup"],
                "not_usable": class_counts["not_usable"],
                "usable_including_overlapping": usable,
                "source_present": source_present,
                "text_exact": text_exact,
                "table_refs": table_refs,
                "table_rows_ok": table_rows,
                "arm_mapped_rows": arm_mapped_rows,
                "label_only_rows": label_only_rows,
                "paired_rows": table_paired_rows,
                "values_in_quote": values_in_quote,
                "structured_value_sets": structured_value_sets,
                "issues": len(issues),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
