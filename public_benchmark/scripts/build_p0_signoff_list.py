#!/usr/bin/env python3
"""Build a compact human sign-off list for the 65 manual P0 cases.

Reads the existing manual decisions and adds a specific open question and
priority per case. Writes Markdown, CSV and JSON. No model or network call.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "evaluation" / "c1_pilot"
OUT = PILOT / "holdout_p0_20261112"
SOURCE = OUT / "manual_review_decisions_v1.jsonl"
MD = OUT / "manual_review_signoff_v1.md"
CSV_PATH = OUT / "manual_review_signoff_v1.csv"
JSON_PATH = OUT / "manual_review_signoff_v1.json"

# pmcid: (priority, open question)
QUESTIONS = {
    "PMC13629817": ("mittel", "Subgruppe <75/>=75; absolute Ereigniszahlen pro Arm und Interaktion pruefen."),
    "PMC13600314": ("mittel", "Drei Bedingungen; pruefen, ob PE+PLB vs. SERT als zwei Arme zulaessig waere (P0: nein)."),
    "PMC13731004": ("niedrig", "Drei Arme; pruefen, ob 7.2 mg vs. Placebo als zwei Arme zulaessig waere (P0: nein)."),
    "PMC13730976": ("niedrig", "Vier Arme; keine Zweiarm-Kontraste."),
    "PMC13714053": ("mittel", "Gepoolt; pruefen, ob Einzelstudien-Armwerte im Volltext stehen."),
    "PMC13635505": ("hoch", "Nur Praediktor-/Modulatoranalyse; SPPB-Armwerte und SD im Volltext pruefen."),
    "PMC13688066": ("hoch", "Post hoc; N/Ereignisse fuer Haematomexpansion pro Arm pruefen."),
    "PMC13745009": ("niedrig", "Assoziation; kein randomisierter Armvergleich."),
    "PMC13743599": ("hoch", "Kleine Tremor-Subgruppe, n=10/Gruppe; SD und Arm-N pruefen."),
    "PMC13720204": ("mittel", "Kleine Stichprobe n=36; PROMIS-29 Armwerte/SD pruefen."),
    "PMC13706700": ("mittel", "Primaer Interaktion; Arm-Mittelwerte/SD und Zeitpunkte pruefen."),
    "PMC13689703": ("niedrig", "2:1-Design; binaere PN-Endpunkte und N pro Arm pruefen."),
    "PMC13628872": ("mittel", "Sekundaeranalyse, n=32; Arm-N/Mean/SD und 3-Monats-Zeitpunkt pruefen."),
    "PMC13626740": ("hoch", "Mechanismusanalyse; unklar, ob Symptomwerte pro Arm als N/Mean/SD berichtet sind."),
    "PMC13621077": ("mittel", "Vergleich nach SSI-Status, nicht randomisierte Arme; klinische Armdaten pruefen."),
    "PMC13621585": ("mittel", "Primaer CEA; klinische PREVSAM-Armwerte im Volltext pruefen."),
    "PMC13610117": ("mittel", "Kleine Stichprobe; Complete-case/ITT-Armwerte pruefen."),
    "PMC13610834": ("mittel", "Kleine Stichprobe; Blutdruck-Armwerte und Zeitpunkt pruefen."),
    "PMC13610533": ("hoch", "Keine Placebo-Kontrolle; Arm-N/Mean/SD und Randomisierung pruefen."),
    "PMC13606361": ("niedrig", "Biomarker-/Diagnostikstudie; kein Interventionseffekt."),
    "PMC13613700": ("hoch", "Sekundaeranalyse; Infektion/PICU-Ereignisse pro Arm und Adjustierung pruefen."),
    "PMC13629967": ("mittel", "EQ-VAS beider Arme gepoolt; kein Treatment-Effekt."),
    "PMC13612665": ("niedrig", "Drei Arme; kein Zweiarm-Vergleich."),
    "PMC13602066": ("mittel", "Langzeit-Follow-up; DFS/OS-Ereignisse pro Arm pruefen."),
    "PMC13630015": ("mittel", "HTA; klinische RCT-Armwerte pruefen, falls berichtet."),
    "PMC13630044": ("mittel", "Selbstberichtete binaere Outcomes; N/Ereignisse pro Arm pruefen."),
    "PMC13591858": ("mittel", "Post hoc; Veraenderungswerte mit SD und zwei Tropicamid-Arme pruefen."),
    "PMC13599935": ("hoch", "Mehrere Regime; pruefen, ob ein Zweiarm-Kontrast zulaessig ist (P0: nein)."),
    "PMC13591290": ("hoch", "Blinding ist primaer; klinischer Schmerzendpunkt und Armwerte unklar."),
    "PMC13590641": ("hoch", "Frueh beendet, n=43; PFS/OS und Zensierung pro Arm pruefen."),
    "PMC13587833": ("hoch", "Emotionsprozessmasse, keine klassischen Armwerte; Eignung pruefen."),
    "PMC13583845": ("mittel", "Post hoc; MINS-Ereignisse pro Arm und CAD-Strata pruefen."),
    "PMC13567134": ("niedrig", "Drei Arme; kein Zweiarm-Vergleich."),
    "PMC13574397": ("hoch", "Sehr klein n=20; Striktur 2/10 vs. 7/10 und oekonomische Zusatzanalyse pruefen."),
    "PMC13693860": ("niedrig", "Vier Bedingungen; kein Zweiarm-Vergleich."),
    "PMC13573578": ("mittel", "Subgruppen nach Verschluss; mRS-Ereignisse pro Arm pruefen."),
    "PMC13562759": ("niedrig", "Paternale Assoziation; kein Interventionseffekt."),
    "PMC13744974": ("niedrig", "Biomarker-Assoziation; kein randomisierter Vergleich."),
    "PMC13599778": ("mittel", "Sekundaeranalyse; CR-Ereignisse pro Arm und CNS-Strata pruefen."),
    "PMC13555364": ("mittel", "Sekundaeranalyse; GOS-E-Ereignisse pro Arm pruefen."),
    "PMC13545155": ("hoch", "Historischer Placebo; kein paralleler Kontrollarm."),
    "PMC13542807": ("mittel", "Sekundaeranalyse; EPDS-Armwerte/SD und ITT-Imputation pruefen."),
    "PMC13595287": ("niedrig", "Beobachtungskohorten; kein randomisierter Armvergleich."),
    "PMC13541226": ("mittel", "Post hoc, per-protocol n=93; VAS-Armwerte/SD pruefen."),
    "PMC13543658": ("niedrig", "Nur Experimentalarm; kein Kontrollarm."),
    "PMC13541895": ("niedrig", "Diagnostische Reanalyse; kein randomisierter Vergleich."),
    "PMC13583526": ("niedrig", "Nur Interventionsarm; keine Kontrollgruppe."),
    "PMC13523073": ("niedrig", "Querschnitt; kein randomisierter Vergleich."),
    "PMC13600430": ("mittel", "Praevalenz; Armvergleich unklar; GAP70+ Volltext pruefen."),
    "PMC13586805": ("mittel", "Interim n=73; ORR-Ereignisse pro Arm pruefen."),
    "PMC13533545": ("mittel", "Post hoc; Gewicht/Lipide als Armwerte/SD pruefen."),
    "PMC13472644": ("niedrig", "Stratifiziert nach Vitamin-D-Status; kein Armvergleich."),
    "PMC13458421": ("mittel", "Post hoc; Leberfett-Armwerte/SD pruefen."),
    "PMC13420175": ("mittel", "Sekundaeranalyse; KCCQ-Armwerte/SD und mITT pruefen."),
    "PMC13352180": ("mittel", "Post hoc; OS-Ereignisse pro Arm und 4-Jahres-Daten pruefen."),
    "PMC13519320": ("hoch", "Gepoolte zwei RCTs; Exazerbations-Ereignisse pro Arm pruefen."),
    "PMC13519342": ("niedrig", "Drei Arme; kein Zweiarm-Vergleich."),
    "PMC13550685": ("niedrig", "Interrater; kein Armvergleich."),
    "PMC13502374": ("mittel", "Produktivitaet/Kosten; klinische VMS-Armwerte pruefen."),
    "PMC13595337": ("niedrig", "Qualitativ; keine quantitativen Armwerte."),
    "PMC13624796": ("hoch", "Post hoc zwei RCTs; UTI-Ereignisse pro Arm pruefen."),
    "PMC13638319": ("mittel", "Sekundaeranalyse; mRS-Ereignisse pro Arm und Verschluss-Subgruppen pruefen."),
    "PMC13690031": ("hoch", "Hierarchischer Score; pruefen, ob einfache binaere Komponenten extrahierbar sind."),
    "PMC13596784": ("hoch", "Feasibility n=57; QoL/Angst-Armwerte/SD pruefen."),
    "PMC13590555": ("hoch", "Sekundaeranalyse; Immunmarker-Armwerte/SD und klinische Relevanz pruefen."),
}


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def short_title(title: str, limit: int = 82) -> str:
    text = " ".join(title.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "..."


def main() -> None:
    decisions = read_jsonl(SOURCE)
    if len(decisions) != 65:
        raise SystemExit(f"expected 65 decisions, got {len(decisions)}")
    ids = {row["pmcid"] for row in decisions}
    if set(QUESTIONS) != ids:
        raise SystemExit(
            f"question mismatch missing={sorted(ids - set(QUESTIONS))} "
            f"extra={sorted(set(QUESTIONS) - ids)}"
        )

    rows = []
    for row in decisions:
        priority, question = QUESTIONS[row["pmcid"]]
        rows.append(
            {
                "pmcid": row["pmcid"],
                "doi": row["doi"],
                "source_url": row["source_url"],
                "title": row["title"],
                "journal": row["journal"],
                "pub_year": row["pub_year"],
                "decision": row["decision"],
                "reason_code": row["reason_code"],
                "has_open_doubt": True,
                "priority": priority,
                "open_question": question,
                "needs_fulltext": row["decision"] == "include_for_fulltext"
                or priority == "hoch",
                "human_signoff": "offen",
                "human_note": "",
            }
        )

    order = {"hoch": 0, "mittel": 1, "niedrig": 2}
    rows.sort(
        key=lambda row: (
            0 if row["decision"] == "include_for_fulltext" else 1,
            order[row["priority"]],
            row["pmcid"],
        )
    )
    for number, row in enumerate(rows, 1):
        row["number"] = number

    JSON_PATH.write_text(
        json.dumps(
            {
                "signoff_id": "p0_manual_signoff_v1",
                "status": "pending_human_signoff",
                "records": len(rows),
                "counts": dict(Counter(row["decision"] for row in rows)),
                "priority_counts": dict(Counter(row["priority"] for row in rows)),
                "rows": rows,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            extrasaction="ignore",
            fieldnames=[
                "number",
                "pmcid",
                "doi",
                "source_url",
                "title",
                "journal",
                "pub_year",
                "decision",
                "reason_code",
                "priority",
                "open_question",
                "needs_fulltext",
                "human_signoff",
                "human_note",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    included = [row for row in rows if row["decision"] == "include_for_fulltext"]
    excluded = [row for row in rows if row["decision"] == "exclude"]

    def table(items: list[dict]) -> list[str]:
        lines = [
            "| Nr | Quelle | Kurztitel | Entscheidung | Offener Zweifel | Prio | Volltext | Freigabe |",
            "|---:|---|---|---|---|---|---|:---:|",
        ]
        for row in items:
            label = "Einschluss" if row["decision"] == "include_for_fulltext" else "Ausschluss"
            fulltext = "ja" if row["needs_fulltext"] else "nein"
            lines.append(
                f"| {row['number']} | [{row['pmcid']}]({row['source_url']})"
                f"<br>`{row['doi']}` | {short_title(row['title'])} | {label} | "
                f"{row['open_question']} | {row['priority']} | {fulltext} | [ ] |"
            )
        return lines

    lines = [
        "# Menschliche Freigabeliste: 65 P0-Einzelfallentscheidungen",
        "",
        "Status: **HUMAN SIGNOFF PENDING**. Diese Liste ist die Prüfvorlage;",
        "sie ist kein Gate-Pass und keine endgültige Holdout-Auswahl.",
        "",
        "Bitte pro Zeile `[ ]` durch `[x]` ersetzen oder in der CSV-Spalte",
        "`human_signoff` auf `ja`, `nein` oder `aendern` setzen. Abweichungen in",
        "`human_note` begründen.",
        "",
        f"- Einschlüsse: **{len(included)}**",
        f"- Ausschlüsse: **{len(excluded)}**",
        f"- hohe Priorität: **{sum(row['priority'] == 'hoch' for row in rows)}**",
        "",
        "## Einschlüsse: vorläufig für Volltext",
        "",
    ]
    lines.extend(table(included))
    lines.extend(
        [
            "",
            "## Ausschlüsse: bestätigen oder korrigieren",
            "",
        ]
    )
    lines.extend(table(excluded))
    lines.extend(
        [
            "",
            "## Legende",
            "",
            "- **Einschluss**: vorläufig für Volltextprüfung; keine endgültige Eignung.",
            "- **Ausschluss**: nach Abstract und fixierten Kriterien; menschliche Gegenprüfung offen.",
            "- **Volltext=ja**: Der offene Zweifel lässt sich nur oder vor allem im Volltext klären.",
            "- **Prio hoch**: Entscheidung könnte sich durch Volltext oder genauere Armprüfung ändern.",
            "",
            "Quellen sind die PMC-Artikelseiten; DOI zusätzlich in der CSV- und JSON-Datei.",
            "Es gab keinen Modelllauf.",
            "",
        ]
    )
    MD.write_text("\n".join(lines), encoding="utf-8")

    print(
        json.dumps(
            {
                "records": len(rows),
                "counts": dict(Counter(row["decision"] for row in rows)),
                "priority_counts": dict(Counter(row["priority"] for row in rows)),
                "human_signoff": "pending",
                "model_used": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
