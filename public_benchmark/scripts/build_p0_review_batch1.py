#!/usr/bin/env python3
"""Assisted fulltext review of the first five high-priority P0 articles.

The review is deliberately conservative: extracted values are transcribed from
reported table rows, unusable/absent outcomes remain explicit empty slots, and
no eligibility decision is finalized. Human confirmation is required.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public_benchmark" / "evaluation" / "c1_pilot" / "holdout_p0_20261112"
DOSSIER = OUT / "fulltext_review_high_v1.json"
JSON_PATH = OUT / "fulltext_review_batch1_v1.json"
CSV_PATH = OUT / "fulltext_review_batch1_v1.csv"
MD_PATH = OUT / "fulltext_review_batch1_v1.md"

TARGETS = [
    "PMC13591290",
    "PMC13590555",
    "PMC13587833",
    "PMC13635505",
    "PMC13624796",
]

RECORDS = {
    "PMC13591290": {
        "short_title": "Blinding in a placebo-controlled manual-therapy RCT",
        "design": "Sekundäranalyse eines zweiarmigen, placebokontrollierten RCT; 102 randomisiert, 98 analysiert",
        "arm_n": {"intervention": 49, "control": 49, "randomized": 102, "analyzed": 98},
        "assisted_eligibility": "uncertain_no_overall_outcome_table",
        "eligibility_reason": "Zwei parallele Arme und Arm-N sind berichtet, aber die klinischen Outcomes liegen nur stratifiziert nach Blinding-Status vor; kein Gesamtkontrast der randomisierten Arme in der Tabelle.",
        "risk_notes": ["secondary analysis", "klinische Outcomes nur nach Blinding-Status stratifiziert"],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "Pain intensity at 4 weeks, blinded participants",
                "type": "continuous",
                "table": "TABLE 3",
                "row_index": 3,
                "context_row_index": 2,
                "intervention": {"label": "Active SMT, blinded", "n": 11, "mean": "19.5", "sd": "11.3"},
                "control": {"label": "Placebo SMT, blinded", "n": 35, "mean": "22.5", "sd": "21.1"},
                "usable": False,
                "note": "Stratifizierte Blinding-Untergruppe, kein randomisierter Gesamtarm-Vergleich.",
            },
            {
                "slot": 2,
                "outcome": "Pain intensity at 4 weeks, unblinded participants",
                "type": "continuous",
                "table": "TABLE 3",
                "row_index": 8,
                "context_row_index": 7,
                "intervention": {"label": "Active SMT, unblinded", "n": 38, "mean": "15.5", "sd": "14.7"},
                "control": {"label": "Placebo SMT, unblinded", "n": 14, "mean": "42.4", "sd": "23.8"},
                "usable": False,
                "note": "Stratifizierte Blinding-Untergruppe, kein randomisierter Gesamtarm-Vergleich.",
            },
            {
                "slot": 3,
                "outcome": "Unique participants with adverse events, blinded participants",
                "type": "binary",
                "table": "TABLE 3",
                "row_index": 6,
                "context_row_index": 2,
                "intervention": {"label": "Active SMT, blinded", "events": 9, "total": 11},
                "control": {"label": "Placebo SMT, blinded", "events": 32, "total": 35},
                "usable": False,
                "note": "Stratifizierte Blinding-Untergruppe; keine armübergreifende Ereignisrate.",
            },
            {
                "slot": 4,
                "outcome": "Unique participants with adverse events, unblinded participants",
                "type": "binary",
                "table": "TABLE 3",
                "row_index": 11,
                "context_row_index": 7,
                "intervention": {"label": "Active SMT, unblinded", "events": 28, "total": 38},
                "control": {"label": "Placebo SMT, unblinded", "events": 10, "total": 14},
                "usable": False,
                "note": "Stratifizierte Blinding-Untergruppe; keine armübergreifende Ereignisrate.",
            },
        ],
    },
    "PMC13590555": {
        "short_title": "Immune-cell changes after HIIT in prostate cancer",
        "design": "Sekundäranalyse des ERASE-RCT; zwei Arme, 1:1 randomisiert; 26 HIIT und 26 Usual Care randomisiert",
        "arm_n": {"intervention": 26, "control": 26, "randomized": 52, "analyzed": "24/25 für die ausgewählten Blutbild-Outcomes"},
        "assisted_eligibility": "likely_eligible",
        "eligibility_reason": "Zwei parallele Arme, Randomisierung 1:1, berichtete Arm-N und vier kontinuierliche Outcomes mit N/Mean/SD zu Baseline und Postintervention.",
        "risk_notes": ["secondary analysis"],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "White blood cell count (10^9/L), postintervention",
                "type": "continuous",
                "table": "Table 2",
                "row_index": 4,
                "control_row_index": 5,
                "intervention": {"label": "HIIT", "n": 24, "mean": "6.33", "sd": "1.32"},
                "control": {"label": "Usual care", "n": 25, "mean": "5.78", "sd": "1.17"},
                "usable": True,
                "note": "Postintervention; Baselinewerte in derselben Tabelle.",
            },
            {
                "slot": 2,
                "outcome": "Neutrophils (10^9/L), postintervention",
                "type": "continuous",
                "table": "Table 2",
                "row_index": 7,
                "control_row_index": 8,
                "intervention": {"label": "HIIT", "n": 24, "mean": "3.75", "sd": "1.01"},
                "control": {"label": "Usual care", "n": 25, "mean": "3.23", "sd": "0.82"},
                "usable": True,
                "note": "Postintervention; Baselinewerte in derselben Tabelle.",
            },
            {
                "slot": 3,
                "outcome": "Lymphocytes (10^9/L), postintervention",
                "type": "continuous",
                "table": "Table 2",
                "row_index": 10,
                "control_row_index": 11,
                "intervention": {"label": "HIIT", "n": 24, "mean": "1.61", "sd": "0.57"},
                "control": {"label": "Usual care", "n": 25, "mean": "1.67", "sd": "0.64"},
                "usable": True,
                "note": "Postintervention; Baselinewerte in derselben Tabelle.",
            },
            {
                "slot": 4,
                "outcome": "Monocytes (10^9/L), postintervention",
                "type": "continuous",
                "table": "Table 2",
                "row_index": 13,
                "control_row_index": 14,
                "intervention": {"label": "HIIT", "n": 24, "mean": "0.67", "sd": "0.29"},
                "control": {"label": "Usual care", "n": 25, "mean": "0.58", "sd": "0.29"},
                "usable": True,
                "note": "Postintervention; Baselinewerte in derselben Tabelle.",
            },
        ],
    },
    "PMC13587833": {
        "short_title": "Self-contempt and emotion processing in BPD psychotherapy",
        "design": "Sekundäranalyse eines RCT; GPM vs. TAU; 50 Klienten, 27 GPM und 23 TAU; 29 gesunde Kontrollen nicht Teil des randomisierten Vergleichs",
        "arm_n": {"intervention": 27, "control": 23, "randomized": 50, "analyzed": 50},
        "assisted_eligibility": "likely_eligible_three_outcomes",
        "eligibility_reason": "Zwei randomisierte Klientenarme, Arm-N und drei auswertbare Outcomes zu Time 2; ein viertes unabhängiges Outcome ist in den Tabellen nicht berichtet.",
        "risk_notes": ["secondary analysis", "kleine Stichprobe", "nur drei unabhängige Outcomes"],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "Self-contempt intensity at Time 2",
                "type": "continuous",
                "table": "TABLE 1B",
                "row_index": 3,
                "intervention": {"label": "GPM", "n": 27, "mean": "3.81", "sd": "0.92"},
                "control": {"label": "TAU", "n": 23, "mean": "4.22", "sd": "0.67"},
                "usable": True,
                "note": "Time 2; Time 1 ist Baseline und nicht als unabhängiges Outcome ausgewählt.",
            },
            {
                "slot": 2,
                "outcome": "Presence of self-compassion at Time 2",
                "type": "binary",
                "table": "TABLE 2B",
                "row_index": 3,
                "intervention": {"label": "GPM", "events": 14, "total": 27},
                "control": {"label": "TAU", "events": 0, "total": 23},
                "usable": True,
                "note": "Tabellenwerte sind Anzahlen; keine Prozentrekonstruktion.",
            },
            {
                "slot": 3,
                "outcome": "Presence of assertive anger at Time 2",
                "type": "binary",
                "table": "TABLE 3B",
                "row_index": 3,
                "intervention": {"label": "GPM", "events": 19, "total": 27},
                "control": {"label": "TAU", "events": 2, "total": 23},
                "usable": True,
                "note": "Tabellenwerte sind Anzahlen; keine Prozentrekonstruktion.",
            },
            {
                "slot": 4,
                "outcome": "Fourth independent outcome",
                "type": "not_available",
                "table": "",
                "row_index": None,
                "intervention": {},
                "control": {},
                "usable": False,
                "note": "Kein viertes unabhängiges Outcome in den Tabellen; State Self-Esteem wird nur im Text erwähnt, ohne armweise Werte.",
            },
        ],
    },
    "PMC13635505": {
        "short_title": "Functional response to in-hospital exercise",
        "design": "Sekundäranalyse eines zweiarmigen RCT; Intervention 150, Kontrolle 153; funktionale Response als binäres Outcome",
        "arm_n": {"intervention": 150, "control": 153, "randomized": 303, "analyzed": 303},
        "assisted_eligibility": "eligible_with_single_binary_outcome",
        "eligibility_reason": "Zwei parallele Arme und ein berichtetes binäres Outcome mit Events/Total; die weiteren funktionalen Werte liegen nur als Median/IQR oder Regressionsmodelle vor.",
        "risk_notes": ["secondary analysis", "nur ein auswertbares binäres Outcome", "kontinuierliche SPPB-Werte nicht als Mean/SD berichtet"],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "Functional response (SPPB increase >= 1 point), discharge",
                "type": "binary",
                "table": "Table 1",
                "row_index": 13,
                "intervention": {"label": "Intervention", "events": 128, "total": 150},
                "control": {"label": "Control", "events": 57, "total": 153},
                "usable": True,
                "note": "Events/Total aus Tabelle; 85.3% und 37.3% nicht als Ereigniszahlen rekonstruiert.",
            },
            {
                "slot": 2,
                "outcome": "SPPB change, continuous",
                "type": "not_available",
                "table": "",
                "row_index": None,
                "intervention": {},
                "control": {},
                "usable": False,
                "note": "Kein armweiser Mean/SD für SPPB zu Entlassung berichtet; Baseline nur Median/IQR.",
            },
            {
                "slot": 3,
                "outcome": "Total cholesterol, continuous",
                "type": "not_available",
                "table": "",
                "row_index": None,
                "intervention": {},
                "control": {},
                "usable": False,
                "note": "Baseline-Prädiktor, kein Behandlungsoutcome; nur Median/IQR und Regressions-OR.",
            },
            {
                "slot": 4,
                "outcome": "Additional functional outcome",
                "type": "not_available",
                "table": "",
                "row_index": None,
                "intervention": {},
                "control": {},
                "usable": False,
                "note": "Kein weiteres armweises Outcome mit N/Mean/SD oder Events/Total in den Tabellen.",
            },
        ],
    },
    "PMC13624796": {
        "short_title": "Dipstick findings and UTI risk with canagliflozin",
        "design": "Post-hoc-Analyse gepoolter Individualdaten aus CANVAS und CREDENCE; zwei RCTs, Canagliflozin vs. Placebo; 3602 Placebo und 5012 Canagliflozin",
        "arm_n": {"intervention": 5012, "control": 3602, "randomized": 8614, "analyzed": 8614, "trial_count": 2},
        "assisted_eligibility": "uncertain_pooled_two_trials",
        "eligibility_reason": "Zwei parallele Arme mit Ereigniszahlen, aber die Analyse poolt zwei separate RCTs und mehrere Subgruppen; kein einzelner RCT und keine unabhängigen vier Outcomes.",
        "risk_notes": ["post hoc", "pooled analysis of two RCTs", "subgroup overlap", "UTI data truncated in CANVAS"],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "First UTI, whole population",
                "type": "binary",
                "table": "Table 3:",
                "row_index": 4,
                "intervention": {"label": "Canagliflozin", "events": 550, "total": 5012},
                "control": {"label": "Placebo", "events": 353, "total": 3602},
                "usable": True,
                "note": "Gepoolte RCT-Population; Ereignisse/Total, keine Unabhängigkeit zwischen den Subgruppen.",
            },
            {
                "slot": 2,
                "outcome": "First UTI, LE normal",
                "type": "binary",
                "table": "Table 3:",
                "row_index": 7,
                "intervention": {"label": "Canagliflozin", "events": 420, "total": 4522},
                "control": {"label": "Placebo", "events": 237, "total": 3171},
                "usable": True,
                "note": "LE-Subgruppe; überlappt mit Slot 1 und ist kein unabhängiges Outcome.",
            },
            {
                "slot": 3,
                "outcome": "First UTI, LE abnormal",
                "type": "binary",
                "table": "Table 3:",
                "row_index": 12,
                "intervention": {"label": "Canagliflozin", "events": 130, "total": 490},
                "control": {"label": "Placebo", "events": 116, "total": 431},
                "usable": True,
                "note": "LE-Subgruppe; überlappt mit Slot 1 und ist kein unabhängiges Outcome.",
            },
            {
                "slot": 4,
                "outcome": "First UTI, NIT abnormal",
                "type": "binary",
                "table": "Table 3:",
                "row_index": 15,
                "intervention": {"label": "Canagliflozin", "events": 45, "total": 173},
                "control": {"label": "Placebo", "events": 34, "total": 129},
                "usable": True,
                "note": "NIT-Subgruppe; überlappt mit Slot 1 und ist kein unabhängiges Outcome.",
            },
        ],
    },
}


def load_tables(pmcid: str) -> dict:
    dossier = json.loads(DOSSIER.read_text(encoding="utf-8"))
    article = next(a for a in dossier["records"] if a["pmcid"] == pmcid)
    return {table["label"]: table for table in article["candidate_tables"]}


def main() -> None:
    dossier = json.loads(DOSSIER.read_text(encoding="utf-8"))
    by_id = {a["pmcid"]: a for a in dossier["records"]}
    payload = {
        "review_id": "p0_fulltext_review_batch1_v1",
        "created_at": "2026-11-13",
        "status": "assisted_batch_ready_for_human_confirmation",
        "scope": "Fünf hohe Prioritäten: PMC13591290, PMC13590555, PMC13587833, PMC13635505, PMC13624796",
        "articles": len(TARGETS),
        "outcome_slots": 20,
        "usable_outcomes": 0,
        "not_usable_or_absent": 0,
        "final_decisions_made": False,
        "human_confirmation_required": True,
        "model_used": False,
        "network_used": False,
        "source_dossier": str(DOSSIER.relative_to(ROOT)).replace("\\", "/"),
        "records": [],
    }
    csv_rows = []

    for pmcid in TARGETS:
        meta = RECORDS[pmcid]
        article = by_id[pmcid]
        tables = load_tables(pmcid)
        outcomes = []
        for outcome in meta["outcomes"]:
            if outcome["table"]:
                table = tables.get(outcome["table"])
                if table is None:
                    raise SystemExit(f"{pmcid}: table not found: {outcome['table']}")
                row = next((r for r in table["rows"] if r["row_index"] == outcome["row_index"]), None)
                if row is None:
                    raise SystemExit(f"{pmcid}: row {outcome['row_index']} not found in {outcome['table']}")
                context_row = None
                if outcome.get("context_row_index") is not None:
                    context_row = next(
                        (r for r in table["rows"] if r["row_index"] == outcome["context_row_index"]),
                        None,
                    )
                    if context_row is None:
                        raise SystemExit(
                            f"{pmcid}: context row {outcome['context_row_index']} not found in {outcome['table']}"
                        )
                if outcome.get("control_row_index") is not None:
                    control_row = next(
                        (r for r in table["rows"] if r["row_index"] == outcome["control_row_index"]),
                        None,
                    )
                    if control_row is None:
                        raise SystemExit(
                            f"{pmcid}: control row {outcome['control_row_index']} not found in {outcome['table']}"
                        )
                    source_quote = (
                        f"{table['label']} | {table['caption']} | Arms: {' / '.join(table['arm_headers'])} | "
                        f"{outcome['outcome']} | Intervention: {row['row_text']} | Control: {control_row['row_text']}"
                    )
                else:
                    source_quote = (
                        f"{table['label']} | {table['caption']} | Arms: {' / '.join(table['arm_headers'])} | "
                        f"{row['row_text']}"
                    )
                if context_row is not None:
                    source_quote += f" | Context: {context_row['row_text']}"
            else:
                source_quote = ""
            item = dict(outcome)
            item["source_quote"] = source_quote
            outcomes.append(item)
            usable = bool(outcome["usable"])
            payload["usable_outcomes" if usable else "not_usable_or_absent"] += 1
            csv_rows.append(
                {
                    "pmcid": pmcid,
                    "slot": outcome["slot"],
                    "outcome": outcome["outcome"],
                    "type": outcome["type"],
                    "table": outcome["table"],
                    "row_index": outcome["row_index"] if outcome["row_index"] is not None else "",
                    "intervention_label": outcome["intervention"].get("label", ""),
                    "intervention_n": outcome["intervention"].get("n", ""),
                    "intervention_mean": outcome["intervention"].get("mean", ""),
                    "intervention_sd": outcome["intervention"].get("sd", ""),
                    "intervention_events": outcome["intervention"].get("events", ""),
                    "intervention_total": outcome["intervention"].get("total", ""),
                    "control_label": outcome["control"].get("label", ""),
                    "control_n": outcome["control"].get("n", ""),
                    "control_mean": outcome["control"].get("mean", ""),
                    "control_sd": outcome["control"].get("sd", ""),
                    "control_events": outcome["control"].get("events", ""),
                    "control_total": outcome["control"].get("total", ""),
                    "usable": usable,
                    "note": outcome["note"],
                    "source_quote": source_quote,
                }
            )
        payload["records"].append(
            {
                "pmcid": pmcid,
                "short_title": meta["short_title"],
                "title": article["title"],
                "design": meta["design"],
                "arm_n": meta["arm_n"],
                "assisted_eligibility": meta["assisted_eligibility"],
                "eligibility_reason": meta["eligibility_reason"],
                "risk_notes": meta["risk_notes"],
                "human_review": {
                    "reviewer": "offen",
                    "review_date": "offen",
                    "parallel_two_arms_confirmed": None,
                    "randomization_confirmed": None,
                    "no_arm_collapse": None,
                    "outcomes_confirmed": None,
                    "final_decision": "offen",
                },
                "outcomes": outcomes,
            }
        )

    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fieldnames = list(csv_rows[0].keys())
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    def format_arm_n(arm_n: dict) -> str:
        return (
            f"Intervention {arm_n.get('intervention', '?')} / Kontrolle {arm_n.get('control', '?')} / "
            f"randomisiert {arm_n.get('randomized', '?')} / analysiert {arm_n.get('analyzed', '?')}"
            + (f" / Trials {arm_n['trial_count']}" if arm_n.get("trial_count") else "")
        )

    lines = [
        "# Assistierte Volltextprüfung: Batch 1 (fünf hohe Prioritäten)",
        "",
        "Stand: 2026-11-13",
        "Status: **ASSISTIERTE PRÜFUNG; MENSCHLICHE BESTÄTIGUNG OFFEN**.",
        "",
        "Keine finale Eignungsentscheidung, keine Übernahme in die Extraktionsvorlage,",
        "kein Modelllauf, kein Netzabruf. Werte sind aus berichteten Tabellenzeilen",
        "transkribiert; nicht verwendbare oder fehlende Outcomes bleiben leer.",
        "",
        "## Übersicht",
        "",
        "| PMC | Design | Arm-N | Assistierte Eignung | Verwendbar |",
        "|---|---|---|---|---:|",
    ]
    for record in payload["records"]:
        usable = sum(1 for outcome in record["outcomes"] if outcome["usable"])
        lines.append(
            f"| [{record['pmcid']}](https://pmc.ncbi.nlm.nih.gov/articles/{record['pmcid']}/) | "
            f"{record['design']} | {format_arm_n(record['arm_n'])} | {record['assisted_eligibility']} | {usable}/4 |"
        )
    lines += [
        "",
        f"Verwendbare Outcomes: **{payload['usable_outcomes']}/20**; "
        f"nicht verwendbar oder nicht berichtet: **{payload['not_usable_or_absent']}/20**.",
        "",
    ]
    for record in payload["records"]:
        lines += [
            f"## {record['pmcid']} — {record['short_title']}",
            "",
            f"- Titel: {record['title']}",
            f"- Design: {record['design']}",
            f"- Arm-N: {format_arm_n(record['arm_n'])}",
            f"- Assistierte Eignung: **{record['assisted_eligibility']}**",
            f"- Begründung: {record['eligibility_reason']}",
            f"- Risiken/Hinweise: {', '.join(record['risk_notes'])}",
            "",
            "| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Quelle |",
            "|---:|---|---|---|---|---|---|",
        ]
        for outcome in record["outcomes"]:
            inter = outcome["intervention"]
            control = outcome["control"]
            if outcome["type"] == "continuous":
                ival = f"n={inter.get('n')}, {inter.get('mean')} ({inter.get('sd')})"
                cval = f"n={control.get('n')}, {control.get('mean')} ({control.get('sd')})"
            elif outcome["type"] == "binary":
                ival = f"{inter.get('events')}/{inter.get('total')}"
                cval = f"{control.get('events')}/{control.get('total')}"
            else:
                ival = "-"
                cval = "-"
            lines.append(
                f"| {outcome['slot']} | {outcome['outcome']} | {outcome['type']} | {ival} | {cval} | "
                f"{'ja' if outcome['usable'] else 'nein'} | {outcome['note']} |"
            )
        lines += ["", "### Quellen", ""]
        for outcome in record["outcomes"]:
            if outcome["source_quote"]:
                lines.append(f"- Slot {outcome['slot']}: `{outcome['source_quote']}`")
            else:
                lines.append(f"- Slot {outcome['slot']}: keine armweise Quelle berichtet")
        lines += ["", "### Menschliche Prüfung", "", "- [ ] zwei parallele Arme bestätigt", "- [ ] Randomisierung bestätigt", "- [ ] keine Armzusammenführung", "- [ ] Outcomes und Quellen bestätigt", "- [ ] finale Entscheidung gesetzt", "", "---", ""]

    lines += [
        "## Konsequenz",
        "",
        "Nur `PMC13590555` liefert vier direkt verwendbare kontinuierliche Outcomes.",
        "`PMC13587833` liefert drei verwendbare Outcomes, `PMC13635505` nur ein",
        "binäres Outcome. `PMC13591290` enthält klinische Werte nur stratifiziert",
        "nach Blinding-Status; `PMC13624796` ist eine gepoolte Analyse zweier RCTs",
        "mit überlappenden Subgruppen. Diese beiden Fälle sind ohne menschliche",
        "Entscheidung nicht als unabhängige RCT-Datensätze zu übernehmen.",
        "",
        "Kein Modelllauf, kein Netzabruf, keine finale Auswahl.",
        "",
    ]
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "articles": len(TARGETS),
                "usable_outcomes": payload["usable_outcomes"],
                "not_usable_or_absent": payload["not_usable_or_absent"],
                "final_decisions_made": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
