#!/usr/bin/env python3
"""Finalize the 65 manual P0 abstract-review cases.

Writes one decision per case with PMC source URL, DOI, title evidence and a
German rationale. Also creates a consolidated v2 decision view and summary.
No model call, no network access, no full-text access.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "evaluation" / "c1_pilot"
OUT = PILOT / "holdout_p0_20261112"
QUEUE = OUT / "manual_review_queue_v1.jsonl"
V1 = OUT / "screening_decisions_v1.jsonl"
DECISIONS = OUT / "manual_review_decisions_v1.jsonl"
V2 = OUT / "screening_decisions_v2.jsonl"
SUMMARY_JSON = OUT / "screening_summary_v2.json"
SUMMARY_MD = OUT / "screening_summary_v2.md"

# pmcid: (decision, reason_code, German rationale)
MAPPING = {
    "PMC13629817": ("include_for_fulltext", "I02", "Zweiarmige randomisierte Deeskalation vs. Fortfuehrung; Alters-Subgruppenanalyse mit Ereignisraten; Armwerte im Volltext pruefen."),
    "PMC13600314": ("exclude", "X01", "Drei randomisierte Behandlungsbedingungen; kein Zweiarm-Vergleich."),
    "PMC13731004": ("exclude", "X01", "Drei Arme (7.2 mg, 2.4 mg, Placebo); kein Zweiarm-Vergleich."),
    "PMC13730976": ("exclude", "X01", "Vier Arme (drei Dosen plus Placebo); kein Zweiarm-Vergleich."),
    "PMC13714053": ("exclude", "X02", "Gepoolte Analyse dreier RCTs; keine eigenstaendigen Zweiarm-Armwerte."),
    "PMC13635505": ("include_for_fulltext", "I02", "Sekundaeranalyse eines RCT; Trainings- vs. Usual-Care-Arm; funktioneller Endpunkt; Armwerte im Volltext pruefen."),
    "PMC13688066": ("include_for_fulltext", "I02", "Post-hoc-Analyse eines RCT; Andexanet vs. Kontrolle; Haematomexpansion als binaerer Endpunkt; Volltext pruefen."),
    "PMC13745009": ("exclude", "X03", "Beobachtende Assoziationsanalyse der Anastomosenlage; kein randomisierter Vergleich."),
    "PMC13743599": ("include_for_fulltext", "I02", "Post-hoc-Analyse eines placebo-kontrollierten RCT; zwei Arme; Tremor-Scores; kleine Subgruppe, Volltext pruefen."),
    "PMC13720204": ("include_for_fulltext", "I01", "Randomisierter 2:1-Placebo-Vergleich; zwei Arme; PROMIS-29; Volltext pruefen."),
    "PMC13706700": ("include_for_fulltext", "I01", "Randomisierter Zweiarm-Vergleich; POCUS-Endpunkte; Armwerte im Volltext."),
    "PMC13689703": ("include_for_fulltext", "I01", "Randomisierter 2:1-Vergleich; zwei Arme; binaerer PN-Endpunkt; Volltext."),
    "PMC13628872": ("include_for_fulltext", "I02", "Sekundaeranalyse eines RCT; zwei Expansionsverfahren; Kiefer-/Atemwegsendpunkte; Volltext."),
    "PMC13626740": ("include_for_fulltext", "I02", "Sekundaeranalyse eines RCT; Schema- vs. CBT-Arm; Symptom-/Mechanismuswerte; Volltext."),
    "PMC13621077": ("exclude", "X05", "Kosten-/QoL-Analyse nach SSI-Status; keine randomisierte Armgegenueberstellung."),
    "PMC13621585": ("exclude", "X04", "Kosteneffektivitaetsanalyse; keine extrahierbaren klinischen Armwerte als primaeres Ziel."),
    "PMC13610117": ("include_for_fulltext", "I02", "Sekundaeranalyse eines placebo-kontrollierten RCT; zwei Arme; metabolische Endpunkte; Volltext."),
    "PMC13610834": ("include_for_fulltext", "I02", "Sekundaeranalyse eines randomisierten Parallelgruppen-RCT; zwei Ballaststoffarme; Blutdruckwerte; Volltext."),
    "PMC13610533": ("include_for_fulltext", "I01", "Randomisierte Zweiarm-Substudie; Intervention vs. Kontrolle; glykaemische/Redox-Endpunkte; Volltext."),
    "PMC13606361": ("exclude", "X07", "Ancillary Biomarker-/Diagnostikstudie; kein randomisierter Interventionsvergleich."),
    "PMC13613700": ("include_for_fulltext", "I02", "Sekundaeranalyse der PEPaNIC-RCT; early vs. late PN; Infektion/PICU; Volltext."),
    "PMC13629967": ("exclude", "X05", "Gepoolte EQ-VAS-Daten beider Arme zur MID-Schaetzung; kein Behandlungseffekt."),
    "PMC13612665": ("exclude", "X01", "Drei Arme (904 nm, 650 nm, Sham); kein Zweiarm-Vergleich."),
    "PMC13602066": ("include_for_fulltext", "I02", "Langzeit-Follow-up eines RCT; zwei Arme; DFS/OS; Volltext."),
    "PMC13630015": ("exclude", "X04", "HTA-/Kosteneffektivitaetsanalyse; keine geeigneten Armwerte."),
    "PMC13630044": ("include_for_fulltext", "I02", "Sekundaeranalyse eines RCT; Exercise vs. Kontrolle; Gedaechtnis/ADL; Volltext."),
    "PMC13591858": ("include_for_fulltext", "I02", "Post-hoc-Analyse eines RCT; 0.5% vs. 1% Tropicamid; Keratometrie mit SD; Volltext."),
    "PMC13599935": ("exclude", "X01", "Mehrere Antithrombotika-Regime (Aspirin, Heparin, beides, keines); kein Zweiarm-Vergleich."),
    "PMC13591290": ("include_for_fulltext", "I02", "Sekundaeranalyse eines placebo-kontrollierten RCT; aktive vs. Sham-SMT; Schmerz-/Blinding-Daten; Volltext."),
    "PMC13590641": ("include_for_fulltext", "I03", "Randomisierter 1:1-Interimsvergleich; zwei Arme; PFS/OS; Volltext."),
    "PMC13587833": ("include_for_fulltext", "I02", "Sekundaeranalyse eines RCT; GPM vs. TAU; Emotionsprozesswerte; Volltext."),
    "PMC13583845": ("include_for_fulltext", "I02", "Post-hoc-Sekundaeranalyse eines RCT; Colchicin vs. Placebo; MINS binaer; Volltext."),
    "PMC13567134": ("exclude", "X01", "Drei Arme (EXE, MOT, CON); kein Zweiarm-Vergleich."),
    "PMC13574397": ("include_for_fulltext", "I04", "Trial-basierte oekonomische Analyse, aber randomisierter Zweiarm-Vergleich mit Strikturereignissen; Volltext pruefen."),
    "PMC13693860": ("exclude", "X01", "Vier Bedingungen (drei Meditationen, Internetkontrolle); kein Zweiarm-Vergleich."),
    "PMC13573578": ("include_for_fulltext", "I02", "Sekundaeranalyse eines RCT; Tenecteplase vs. Standard; mRS binaer; Volltext."),
    "PMC13562759": ("exclude", "X03", "Assoziationsanalyse paternaler Faktoren; kein Interventionseffekt."),
    "PMC13744974": ("exclude", "X03", "Ancillary Biomarker-Assoziationsstudie; kein randomisierter Vergleich."),
    "PMC13599778": ("include_for_fulltext", "I02", "Sekundaeranalyse eines RCT; Olanzapin vs. Placebo; CR binaer; Volltext."),
    "PMC13555364": ("include_for_fulltext", "I02", "Praeplanmaessige Sekundaeranalyse eines RCT; liberal vs. restriktiv; GOS-E binaer; Volltext."),
    "PMC13545155": ("exclude", "X08", "Vergleich gegen historischen Placebo, kein paralleler randomisierter Kontrollarm."),
    "PMC13542807": ("include_for_fulltext", "I02", "Praeplanmaessige Sekundaeranalyse eines RCT; eMBI vs. TAU; EPDS kontinuierlich; Volltext."),
    "PMC13595287": ("exclude", "X03", "Post-hoc-Beobachtung von Screening-Kohorten; kein randomisierter Armvergleich."),
    "PMC13541226": ("include_for_fulltext", "I02", "Post-hoc-Sekundaeranalyse eines Sham-RCT; DTx vs. Sham; VAS-Schmerz; Volltext."),
    "PMC13543658": ("exclude", "X06", "Nur Experimentalarm der EMI-Studie; kein Kontrollarm."),
    "PMC13541895": ("exclude", "X07", "Diagnostische Reanalyse des Beobachtungsarms; kein randomisierter Vergleich."),
    "PMC13583526": ("exclude", "X06", "Nur Interventionsarm; Engagementanalyse ohne Kontrollgruppe."),
    "PMC13523073": ("exclude", "X05", "Querschnittliche Post-hoc-Charakterisierung; kein randomisierter Vergleich."),
    "PMC13600430": ("exclude", "X05", "Praevalenzanalyse ohne Armgegenueberstellung; kein Behandlungseffekt."),
    "PMC13586805": ("include_for_fulltext", "I03", "Randomisierter 1:1-Interimsvergleich; zwei Arme; ORR binaer; Volltext."),
    "PMC13533545": ("include_for_fulltext", "I02", "Post-hoc-Analyse eines randomisierten 12-Monats-Vergleichs; PP6M vs. PP3M; Gewicht/Lipide; Volltext."),
    "PMC13472644": ("exclude", "X03", "Sekundaeranalyse stratifiziert nach Vitamin-D-Status; kein randomisierter Armvergleich."),
    "PMC13458421": ("include_for_fulltext", "I02", "Post-hoc-Analyse eines RCT; Tirzepatid vs. Insulin degludec; Leberfett; Volltext."),
    "PMC13420175": ("include_for_fulltext", "I02", "Sekundaeranalyse eines placebo-kontrollierten RCT; Acoramidis vs. Placebo; KCCQ; Volltext."),
    "PMC13352180": ("include_for_fulltext", "I02", "Post-hoc-Analyse eines RCT; Durvalumab vs. Placebo; OS; Volltext."),
    "PMC13519320": ("include_for_fulltext", "I02", "Gepoolte Analyse zweier placebo-kontrollierter RCT; zwei Arme; Exazerbationen; Volltext."),
    "PMC13519342": ("exclude", "X01", "Drei Arme (Q2W, Q4W, Placebo); kein Zweiarm-Vergleich."),
    "PMC13550685": ("exclude", "X05", "Interrater-Analyse ohne Armvergleich; kein Behandlungseffekt."),
    "PMC13502374": ("exclude", "X04", "Post-hoc-Arbeitsproduktivitaets-/Kostenanalyse; kein klinischer Armendpunkt."),
    "PMC13595337": ("exclude", "X10", "Qualitative Substichprobe; keine quantitativen Armwerte."),
    "PMC13624796": ("include_for_fulltext", "I02", "Post-hoc-Analyse zweier placebo-kontrollierter RCT; Canagliflozin vs. Placebo; UTI binaer; Volltext."),
    "PMC13638319": ("include_for_fulltext", "I02", "Praeplanmaessige Sekundaeranalyse eines RCT; IA-Tenecteplase vs. Standard; mRS binaer; Volltext."),
    "PMC13690031": ("exclude", "X09", "Nur hierarchische Win-Ratio/DOOR; keine N/Mean/SD/Event-Armwerte."),
    "PMC13596784": ("include_for_fulltext", "I01", "Randomisierte Zweiarm-Feasibility-Studie; MATILDA vs. aktive Kontrolle; QoL/Angst; Volltext."),
    "PMC13590555": ("include_for_fulltext", "I02", "Sekundaeranalyse eines RCT; HIIT vs. Usual Care; Immunmarker kontinuierlich; Volltext."),
}


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    queue = {row["pmcid"]: row for row in read_jsonl(QUEUE)}
    if set(MAPPING) != set(queue):
        raise SystemExit(
            f"mapping mismatch missing={sorted(set(queue) - set(MAPPING))} "
            f"extra={sorted(set(MAPPING) - set(queue))}"
        )
    if len(MAPPING) != 65:
        raise SystemExit(f"expected 65 mappings, got {len(MAPPING)}")

    reviewed = []
    for pmcid, (decision, code, rationale) in MAPPING.items():
        q = queue[pmcid]
        reviewed.append(
            {
                "pmcid": pmcid,
                "pmid": q["pmid"],
                "doi": q["doi"],
                "title": q["title"],
                "journal": q["journal"],
                "pub_year": q["pub_year"],
                "source_url": q["source_url"],
                "source_type": "PMC Abstract",
                "source_quote": q["title"],
                "source_locator": "Titel",
                "original_manual_reasons": q["original_manual_reasons"],
                "decision": decision,
                "reason_code": code,
                "rationale_de": rationale,
                "review_stage": "manual_abstract_review",
                "reviewer": "Codebuff assistierte Einzelpruefung",
                "human_review": False,
                "human_signoff": "pending",
                "model_used": False,
                "reviewed_at": "2026-11-12",
            }
        )

    with DECISIONS.open("w", encoding="utf-8", newline="\n") as handle:
        for row in reviewed:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    manual_map = {row["pmcid"]: row for row in reviewed}
    v1 = read_jsonl(V1)
    v2 = []
    for row in v1:
        if row["decision"] == "manual_review":
            decision = manual_map[row["pmcid"]]
            row = dict(row)
            row["decision"] = decision["decision"]
            row["reason_codes"] = [decision["reason_code"]]
            row["reason_labels"] = [decision["rationale_de"]]
            row["evidence"] = [
                {
                    "rule_id": decision["reason_code"],
                    "decision": decision["decision"],
                    "label": decision["rationale_de"],
                    "field": "title",
                    "match": decision["source_quote"],
                    "evidence": decision["source_quote"],
                }
            ]
            row["screening_method"] = "manual_assisted_review_v1"
            row["human_review"] = False
            row["human_signoff"] = "pending"
        v2.append(row)
    if len(v2) != 596:
        raise SystemExit(f"expected 596 v2 decisions, got {len(v2)}")
    with V2.open("w", encoding="utf-8", newline="\n") as handle:
        for row in v2:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    counts = Counter(row["decision"] for row in v2)
    manual_counts = Counter(row["reason_code"] for row in reviewed)
    summary = {
        "screening_id": "p0_abstract_screening_v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "records": len(v2),
        "counts": {
            "exclude": counts["exclude"],
            "manual_review": counts.get("manual_review", 0),
            "include_for_fulltext": counts["include_for_fulltext"],
        },
        "manual_cases": len(reviewed),
        "manual_include": sum(
            row["decision"] == "include_for_fulltext" for row in reviewed
        ),
        "manual_exclude": sum(row["decision"] == "exclude" for row in reviewed),
        "manual_reason_counts": dict(sorted(manual_counts.items())),
        "human_review": False,
        "human_signoff": "pending",
        "model_used": False,
        "fulltext_screening": False,
    }
    SUMMARY_JSON.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# P0-Abstract-Screening v2",
        "",
        "Die 65 manuellen Fälle wurden einzelfallgeprüft; die Entscheidungen sind",
        "assistiert und noch nicht menschlich freigegeben.",
        "",
        "| Entscheidung | Anzahl |",
        "|---|---:|",
        f"| Ausschluss | {counts['exclude']} |",
        f"| Manuelle Prüfung | {counts.get('manual_review', 0)} |",
        f"| Vorläufig für Volltext | {counts['include_for_fulltext']} |",
        f"| **Gesamt** | **{len(v2)}** |",
        "",
        f"Von den 65 manuellen Fällen: **{summary['manual_include']}** vorläufig",
        f"eingeschlossen und **{summary['manual_exclude']}** ausgeschlossen.",
        "",
        "Jede Einzelfallentscheidung enthält Quelle, DOI, Titelbeleg und Begründung in",
        "[`manual_review_decisions_v1.jsonl`](manual_review_decisions_v1.jsonl).",
        "Die konsolidierte Entscheidung steht in",
        "[`screening_decisions_v2.jsonl`](screening_decisions_v2.jsonl).",
        "",
        "**Kein Modelllauf, keine Volltextprüfung.** Die menschliche Freigabe",
        "(`human_signoff`) steht aus.",
        "",
    ]
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
