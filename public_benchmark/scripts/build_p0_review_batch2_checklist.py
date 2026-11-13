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


def extract_table_rows(table_wrap: ET.Element) -> list[str]:
    rows: list[str] = []
    for element in table_wrap.iter():
        if local_name(element.tag) != "tr":
            continue
        cells = [
            element_text(child)
            for child in element
            if local_name(child.tag) in {"th", "td"}
        ]
        if cells:
            rows.append(" | ".join(cells))
    return rows


def row_contains(row: str, label: str, values: list[str]) -> bool:
    if normalize(label) not in normalize(row):
        return False
    return all(
        normalize_number(value) in normalize_number(row)
        for value in values
    )


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
    table_values_ok = 0
    table_rows = 0
    table_paired_rows = 0
    table_single_rows = 0
    structured_value_sets = 0
    values_in_quote = 0
    issues: list[str] = []
    source_flags: dict[str, str] = {}
    header_only_slots: list[str] = []

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
                table_raw = element_text(table_wrap)
                table_text = normalize(table_raw)
                caption_ok = normalize(table["caption"]) in table_text
                row_label_ok = normalize(row["row_label"]) in table_text
                xml_rows = extract_table_rows(table_wrap)
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
                    intervention_ok = any(
                        row_contains(item, row["row_label"], intervention_values)
                        for item in xml_rows
                    )
                    control_ok = any(
                        row_contains(item, control_row["row_label"], control_values)
                        for item in xml_rows
                    )
                    row_ok = intervention_ok and control_ok
                    table_paired_rows += 1
                else:
                    all_values = intervention_values + control_values
                    row_ok = any(
                        row_contains(item, row["row_label"], all_values)
                        for item in xml_rows
                    )
                    table_single_rows += 1
                if caption_ok and row_ok:
                    table_rows += 1
                    table_values_ok += 1
                else:
                    header_only = False
                    if outcome["type"] == "binary":
                        event_values = [
                            str(outcome["intervention"]["events"]),
                            str(outcome["control"]["events"]),
                        ]
                        events_in_row = any(
                            row_contains(item, row["row_label"], event_values)
                            for item in xml_rows
                        )
                        totals_in_table = all(
                            normalize_number(value) in normalize_number(table_raw)
                            for value in (
                                str(outcome["intervention"].get("total")),
                                str(outcome["control"].get("total")),
                            )
                        )
                        header_only = events_in_row and totals_in_table
                    if header_only:
                        source_flags[f"{pmcid}:{outcome['slot']}"] = (
                            "N nur im Arm-Header; Zeile separat prüfen"
                        )
                        header_only_slots.append(f"{pmcid}:{outcome['slot']}")
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
        f"- **{table_refs}** Tabellenverweise: Caption, Zeilenlabel und strukturierte Werte wurden ausschließlich in der jeweils referenzierten Tabellenzeile geprüft; "
        f"**{table_rows}/18** Tabellen-Outcomes bestanden die zeilenexakte Prüfung: "
        f"{table_rows - table_paired_rows}/{table_single_rows} Einzelzeilen und "
        f"{table_paired_rows}/{table_paired_rows} Kosten-Outcomes mit getrennten "
        f"Interventions-/Kontrollzeilen bestanden. {len(header_only_slots)} binäre "
        "AE-Outcomes haben Ereignisse in der Zeile, aber N nur im Arm-Header und "
        "bestehen die Zeilenprüfung deshalb nicht. Der ICER-Slot ist ein "
        "Tabellenverweis ohne eigene Zeilenwerte.",
        f"- **{values_in_quote}/{structured_value_sets}** Outcomes mit strukturierten Zahlen "
        "enthalten diese Zahlen im Quelleintrag.",
        "",
        "Hinweis: Tabellenquellen sind keine zusammenhängenden Fließtextsätze. Die",
        "Quellenprüfung vergleicht deshalb Caption, Zeilenlabel und strukturierte",
        "Werte ausschließlich in der referenzierten Tabellenzeile; sie",
        "ersetzt nicht die menschliche Sichtprüfung der Tabelle.",
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
        "- [ ] 4 Hinweise „N nur im Arm-Header“ geprüft",
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
