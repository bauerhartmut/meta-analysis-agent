#!/usr/bin/env python3
"""Assisted fulltext review of the remaining nine high-priority P0 articles.

Values are transcribed only when the article reports an arm-level outcome with
an explicit N/Mean/SD or Events/Total. Median/IQR values, adjusted associations
and outcomes without arm-specific counts remain explicit empty slots. No
eligibility decision is finalized and human confirmation is required.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public_benchmark" / "evaluation" / "c1_pilot" / "holdout_p0_20261112"
DOSSIER = OUT / "fulltext_review_high_v1.json"
JSON_PATH = OUT / "fulltext_review_batch2_v1.json"
CSV_PATH = OUT / "fulltext_review_batch2_v1.csv"
MD_PATH = OUT / "fulltext_review_batch2_v1.md"

TARGETS = [
    "PMC13610533",
    "PMC13743599",
    "PMC13613700",
    "PMC13626740",
    "PMC13688066",
    "PMC13519320",
    "PMC13590641",
    "PMC13596784",
    "PMC13574397",
]

CONTEXTS = {
    ("PMC13610533", 3): "3-Monats-Werte; Reihenfolge: Baseline IG, 3 Monate IG, Delta IG, Baseline CG, 3 Monate CG, Delta CG, p, FDR-p, H-L-Effekt, Cliff's delta; Werte sind Median (IQR).",
    ("PMC13610533", 4): "3-Monats-Werte; Reihenfolge: Baseline IG, 3 Monate IG, Delta IG, Baseline CG, 3 Monate CG, Delta CG, p, FDR-p, H-L-Effekt, Cliff's delta; Werte sind Median (IQR).",
    ("PMC13610533", 5): "3-Monats-Werte; Reihenfolge: Baseline IG, 3 Monate IG, Delta IG, Baseline CG, 3 Monate CG, Delta CG, p, FDR-p, H-L-Effekt, Cliff's delta; Werte sind Median (IQR).",
    ("PMC13610533", 6): "3-Monats-Werte; Reihenfolge: Baseline IG, 3 Monate IG, Delta IG, Baseline CG, 3 Monate CG, Delta CG, p, FDR-p, H-L-Effekt, Cliff's delta; Werte sind Median (IQR).",
    ("PMC13626740", 16): "Post-treatment T3 (Woche 7); Spalten: Total n/M/SD, CBT n/M/SD, ST n/M/SD.",
    ("PMC13626740", 17): "Post-treatment T3 (Woche 7); Spalten: Total n/M/SD, CBT n/M/SD, ST n/M/SD.",
    ("PMC13626740", 18): "Post-treatment T3 (Woche 7); Spalten: Total n/M/SD, CBT n/M/SD, ST n/M/SD.",
    ("PMC13626740", 19): "Post-treatment T3 (Woche 7); Spalten: Total n/M/SD, CBT n/M/SD, ST n/M/SD.",
    ("PMC13590641", 3): "Any grade (erste Spalte je Arm); weitere Spalten Grade 1-4.",
    ("PMC13590641", 5): "Any grade (erste Spalte je Arm); weitere Spalten Grade 1-4.",
    ("PMC13590641", 6): "Any grade (erste Spalte je Arm); weitere Spalten Grade 1-4.",
    ("PMC13590641", 10): "Any grade (erste Spalte je Arm); weitere Spalten Grade 1-4.",
    ("PMC13596784", 5): "6-Monats-Follow-up; Spalten: Control Baseline/6m/12m, MATILDA Baseline/6m/12m.",
    ("PMC13596784", 6): "6-Monats-Follow-up; Spalten: Control Baseline/6m/12m, MATILDA Baseline/6m/12m.",
    ("PMC13596784", 10): "6-Monats-Follow-up; Spalten: Control Baseline/6m/12m, MATILDA Baseline/6m/12m.",
    ("PMC13596784", 16): "6-Monats-Follow-up; Spalten: Control Baseline/6m/12m, MATILDA Baseline/6m/12m.",
    ("PMC13574397", 3): "Provider perspective; Kostenspalte pro Fall, danach Strikturrate und ICER.",
    ("PMC13574397", 7): "Patient perspective; Kostenspalte pro Fall, danach Strikturrate und ICER.",
}

RECORDS = {
    "PMC13610533": {
        "short_title": "Chokeberry juice in women with prediabetes",
        "design": "Randomisierte Substudie innerhalb eines einarmigen Elternprojekts; Intervention 27 / Kontrolle 27; 12 Wochen",
        "arm_n": {"intervention": 27, "control": 27, "randomized": 54, "analyzed": 54},
        "assisted_eligibility": "uncertain_nested_substudy_medians",
        "eligibility_reason": "Zwei randomisierte Arme und Arm-N sind berichtet, aber BMI, Glukose und Redoxwerte liegen als Median (IQR) und Veränderung vor; kein armweises Mean/SD.",
        "risk_notes": [
            "nested substudy",
            "single-group parent project",
            "median/IQR statt Mean/SD",
            "kleine Stichprobe",
        ],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "BMI at 3 months",
                "type": "continuous",
                "table": "Table 3",
                "row_index": 3,
                "intervention": {"label": "Chokeberry juice + Mediterranean diet"},
                "control": {"label": "Mediterranean diet"},
                "usable": False,
                "note": "Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung.",
            },
            {
                "slot": 2,
                "outcome": "Fasting glucose at 3 months",
                "type": "continuous",
                "table": "Table 3",
                "row_index": 4,
                "intervention": {"label": "Chokeberry juice + Mediterranean diet"},
                "control": {"label": "Mediterranean diet"},
                "usable": False,
                "note": "Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung.",
            },
            {
                "slot": 3,
                "outcome": "HbA1c at 3 months",
                "type": "continuous",
                "table": "Table 3",
                "row_index": 5,
                "intervention": {"label": "Chokeberry juice + Mediterranean diet"},
                "control": {"label": "Mediterranean diet"},
                "usable": False,
                "note": "Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung.",
            },
            {
                "slot": 4,
                "outcome": "2-hour postload glucose at 3 months",
                "type": "continuous",
                "table": "Table 3",
                "row_index": 6,
                "intervention": {"label": "Chokeberry juice + Mediterranean diet"},
                "control": {"label": "Mediterranean diet"},
                "usable": False,
                "note": "Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung.",
            },
        ],
    },
    "PMC13743599": {
        "short_title": "Sublingual apomorphine for parkinsonian tremor",
        "design": "Post-hoc-Analyse einer pivotalen 12-Wochen-RCT plus offene 12-Monats-Studie; tremor-dominante Subgruppe 17 SL-APO / 14 Placebo; Post-Werte n=10/10",
        "arm_n": {"intervention": 17, "control": 14, "randomized": 31, "analyzed": "10/10 mit Post-Werten"},
        "assisted_eligibility": "eligible_single_post_hoc_outcome",
        "eligibility_reason": "Zwei randomisierte Arme und ein kontinuierliches Outcome mit n/Mean/SD zu Woche 12; weitere Outcomes sind nur als Veränderung, Prozentwerte oder qualitativ berichtet.",
        "risk_notes": [
            "post hoc",
            "kleine tremor-dominante Subgruppe",
            "available-case n=10/10",
            "offene Verlängerung nicht kontrolliert",
        ],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "Tremor index at 30 min post-dose, Week 12",
                "type": "continuous",
                "table": "",
                "row_index": None,
                "intervention": {"label": "SL-APO", "n": 10, "mean": "5.7", "sd": "3.3"},
                "control": {"label": "Placebo", "n": 10, "mean": "11.3", "sd": "5.7"},
                "usable": True,
                "note": "Post-hoc; nur n=10/10 mit Post-Werten; 17/14 randomisiert.",
                "source_quote": "Results | Mean ± SD tremor index scores decreased from 11.0 ± 4.8 pre-dose to 5.7 ± 3.3 at 30 min post-intake with SL-APO (n = 10), versus 12.4 ± 4.8 to 11.3 ± 5.7 with placebo (n = 10).",
            },
            {
                "slot": 2,
                "outcome": "Change in tremor index at 30 min, Week 12",
                "type": "continuous",
                "table": "",
                "row_index": None,
                "intervention": {"label": "SL-APO"},
                "control": {"label": "Placebo"},
                "usable": False,
                "note": "Within-group change: -5.3 [-7.3; -3.3] mit SL-APO und -1.1 [-2.5; 0.3] mit Placebo; Placebo-SD der Veränderung nicht berichtet.",
                "source_quote": "Results | The within-group change was − 5.3 [− 7.3; −3.3] with SL‑APO and − 1.1 [− 2.5; 0.3] with placebo, yielding a between-group treatment effect of − 4.4 [− 6.5; −2.3] (p < 0.001; Fig. 1a).",
            },
            {
                "slot": 3,
                "outcome": "Responder (>= MIC) at Week 12",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "SL-APO"},
                "control": {"label": "Placebo"},
                "usable": False,
                "note": "Nur 80% vs. 30% bei n=10/10; keine Ereigniszahlen berichtet, keine Rekonstruktion.",
                "source_quote": "Results | Based on a calculated MIC of 2.3, responder rates were 80% with SL‑APO and 30% with placebo, supported by cumulative distribution function plots showing a consistent shift toward greater improvement with SL‑APO (Fig. 1c).",
            },
            {
                "slot": 4,
                "outcome": "Rest and postural tremor subscores",
                "type": "not_available",
                "table": "",
                "row_index": None,
                "intervention": {},
                "control": {},
                "usable": False,
                "note": "Nur qualitative Aussage zu beiden Tremor-Subtypen; keine armweisen Werte.",
                "source_quote": "Results | Improvements reflected reductions in both rest and postural tremor.",
            },
        ],
    },
    "PMC13613700": {
        "short_title": "Ureagenesis in the PEPaNIC trial",
        "design": "Sekundäranalyse der PEPaNIC-RCT; Early-PN 665 / Late-PN 663 ohne RRT; 90 Tage",
        "arm_n": {"intervention": 665, "control": 663, "randomized": 1440, "analyzed": 1328},
        "assisted_eligibility": "uncertain_secondary_no_arm_counts",
        "eligibility_reason": "Zwei randomisierte Arme sind berichtet, aber die klinischen Outcomes liegen nur als adjustierte OR/HR und p-Werte vor; keine armweisen Ereigniszahlen oder Time-to-Event-Rohdaten.",
        "risk_notes": [
            "secondary analysis",
            "keine armweisen Ereigniszahlen",
            "RRT-Patienten ausgeschlossen",
            "kompetierendes Risiko Tod",
            "6% fehlende Daten",
        ],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "New infection during PICU stay",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Early-PN"},
                "control": {"label": "Late-PN"},
                "usable": False,
                "note": "Nur adjustierte Assoziation und p-Wert; keine Ereignisse/Total pro Arm.",
                "source_quote": "Results | Adjusting for baseline risk factors, randomization to early-PN as compared with late-PN was independently associated with a higher risk of acquiring a new infection in the PICU (p = 0.0063) and a lower likelihood of earlier live discharge from the PICU (p = 0.0068) and the hospital (p = 0.023), but not with 90-day mortality (p = 0.22) (Fig. 3, Additional File 1 Table S2).",
            },
            {
                "slot": 2,
                "outcome": "PICU dependency (time to live discharge)",
                "type": "time_to_event",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Early-PN"},
                "control": {"label": "Late-PN"},
                "usable": False,
                "note": "Nur adjustierte HR/Modellresultate; keine armweisen Rohdaten oder Ereigniszahlen.",
                "source_quote": "Results | Adjusting for baseline risk factors, randomization to early-PN as compared with late-PN was independently associated with a higher risk of acquiring a new infection in the PICU (p = 0.0063) and a lower likelihood of earlier live discharge from the PICU (p = 0.0068) and the hospital (p = 0.023), but not with 90-day mortality (p = 0.22) (Fig. 3, Additional File 1 Table S2).",
            },
            {
                "slot": 3,
                "outcome": "90-day mortality",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Early-PN"},
                "control": {"label": "Late-PN"},
                "usable": False,
                "note": "Nur adjustierte Assoziation und p-Wert; keine Ereignisse/Total pro Arm.",
                "source_quote": "Results | Adjusting for baseline risk factors, randomization to early-PN as compared with late-PN was independently associated with a higher risk of acquiring a new infection in the PICU (p = 0.0063) and a lower likelihood of earlier live discharge from the PICU (p = 0.0068) and the hospital (p = 0.023), but not with 90-day mortality (p = 0.22) (Fig. 3, Additional File 1 Table S2).",
            },
            {
                "slot": 4,
                "outcome": "Hospital dependency (time to live discharge)",
                "type": "time_to_event",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Early-PN"},
                "control": {"label": "Late-PN"},
                "usable": False,
                "note": "Nur adjustierte HR/Modellresultate; keine armweisen Rohdaten oder Ereigniszahlen.",
                "source_quote": "Results | Adjusting for baseline risk factors, randomization to early-PN as compared with late-PN was independently associated with a higher risk of acquiring a new infection in the PICU (p = 0.0063) and a lower likelihood of earlier live discharge from the PICU (p = 0.0068) and the hospital (p = 0.023), but not with 90-day mortality (p = 0.22) (Fig. 3, Additional File 1 Table S2).",
            },
        ],
    },
    "PMC13626740": {
        "short_title": "Mechanisms of change in depression therapy",
        "design": "Sekundäranalyse der OPTIMA-RCT; CBT 101 / ST 97; T3 nach 7 Wochen",
        "arm_n": {"intervention": 101, "control": 97, "randomized": 198, "analyzed": "82/66 bei T3"},
        "assisted_eligibility": "likely_eligible_two_arms",
        "eligibility_reason": "Zwei randomisierte Arme, Arm-N und vier kontinuierliche Outcomes mit N/Mean/SD zu Post-Treatment T3.",
        "risk_notes": [
            "secondary analysis",
            "available-case n zu T3",
            "Parent-RCT OPTIMA",
            "nur CBT vs. ST ausgewählt",
        ],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "Depressive symptoms (BDI-II), post-treatment T3",
                "type": "continuous",
                "table": "TABLE 1",
                "row_index": 16,
                "intervention": {"label": "CBT", "n": 82, "mean": "14.80", "sd": "8.99"},
                "control": {"label": "ST", "n": 66, "mean": "18.00", "sd": "10.97"},
                "usable": True,
                "note": "Post-treatment T3 (Woche 7); verfügbares n.",
            },
            {
                "slot": 2,
                "outcome": "Expressive suppression (ERQ), post-treatment T3",
                "type": "continuous",
                "table": "TABLE 1",
                "row_index": 17,
                "intervention": {"label": "CBT", "n": 79, "mean": "3.53", "sd": "1.47"},
                "control": {"label": "ST", "n": 60, "mean": "3.73", "sd": "1.45"},
                "usable": True,
                "note": "Post-treatment T3 (Woche 7); verfügbares n.",
            },
            {
                "slot": 3,
                "outcome": "Cognitive reappraisal (ERQ), post-treatment T3",
                "type": "continuous",
                "table": "TABLE 1",
                "row_index": 18,
                "intervention": {"label": "CBT", "n": 79, "mean": "4.12", "sd": "1.47"},
                "control": {"label": "ST", "n": 60, "mean": "3.89", "sd": "1.10"},
                "usable": True,
                "note": "Post-treatment T3 (Woche 7); verfügbares n.",
            },
            {
                "slot": 4,
                "outcome": "Avoidant attachment (RSQ fear of closeness), post-treatment T3",
                "type": "continuous",
                "table": "TABLE 1",
                "row_index": 19,
                "intervention": {"label": "CBT", "n": 79, "mean": "2.57", "sd": "1.00"},
                "control": {"label": "ST", "n": 59, "mean": "2.73", "sd": "0.89"},
                "usable": True,
                "note": "Post-treatment T3 (Woche 7); verfügbares n.",
            },
        ],
    },
    "PMC13688066": {
        "short_title": "NCCT markers and andexanet response",
        "design": "Post-hoc-Sekundäranalyse der ANNEXa-I-RCT; 434 von 530 ITT mit Bildgebung; Andexanet vs. Usual Care",
        "arm_n": {
            "intervention": "nicht berichtet",
            "control": "nicht berichtet",
            "randomized": 530,
            "analyzed": 434,
        },
        "assisted_eligibility": "uncertain_post_hoc_no_arm_counts",
        "eligibility_reason": "Randomisierte Arme sind im Design berichtet, aber die HE-Outcomes liegen nur als Gesamtfrequenz, Subgruppeninteraktionen oder adjustierte Assoziationen vor; keine armweisen Ereignisse/Total.",
        "risk_notes": [
            "post hoc",
            "keine armweisen Ereigniszahlen",
            "434/530 mit Bildgebung",
            "explorative Interaktionstests",
            "Bildgebungsselektion",
        ],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "Significant hematoma expansion (>=12.5 ml or >=35%)",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Andexanet"},
                "control": {"label": "Usual care"},
                "usable": False,
                "note": "Gesamtpopulation 138/434 (31.8%); keine armweisen Ereigniszahlen im Text.",
                "source_quote": "Patients' Characteristics | Among 530 patients in the intention‐to‐treat population, 434 (197 female, mean age 79.3 ± 8.1 years) had qualifying ICH, baseline NCCT, and follow‐up imaging available for assessment of HE and were included in this study (Figure S2). HE was observed in 138 patients (31.8%).",
            },
            {
                "slot": 2,
                "outcome": "Severe hematoma expansion (>=12.5 ml or >=66%)",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Andexanet"},
                "control": {"label": "Usual care"},
                "usable": False,
                "note": "Nur definiertes Outcome; keine armweisen Ereigniszahlen im Text.",
                "source_quote": "Outcomes | The secondary outcome was severe HE, defined as ≥12.5 ml or ≥ 66% increase.",
            },
            {
                "slot": 3,
                "outcome": "HE in hypodensity subgroup",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Andexanet"},
                "control": {"label": "Usual care"},
                "usable": False,
                "note": "Nur absolute Reduktion 19.5% vs. 8.0% berichtet; keine Ereigniszahlen.",
                "source_quote": "Treatment Interaction of Andexanet | The absolute reduction in HE with andexanet appeared greater in patients with hypodensity (19.5% vs. 8.0%) than those without.",
            },
            {
                "slot": 4,
                "outcome": "HE in blend-sign subgroup",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Andexanet"},
                "control": {"label": "Usual care"},
                "usable": False,
                "note": "Nur Interaktions-OR 0.03 (0.00-0.29) vs. 0.60 (0.38-0.96), p=0.01; keine Ereigniszahlen.",
                "source_quote": "Treatment Interaction of Andexanet | A treatment interaction was observed for the blend sign (OR 0.03, 95% CI 0.00–0.29 for those with blend sign; and OR 0.60, 95% CI 0.38–0.96 for those without, p for interaction = 0.01).",
            },
        ],
    },
    "PMC13519320": {
        "short_title": "Dupilumab and COPD exacerbation resource use",
        "design": "Post-hoc-gepoolte Analyse von BOREAS und NOTUS; Dupilumab 938 / Placebo 936; 52 Wochen",
        "arm_n": {
            "intervention": 938,
            "control": 936,
            "randomized": 1874,
            "analyzed": 1874,
            "trial_count": 2,
        },
        "assisted_eligibility": "uncertain_pooled_two_trials",
        "eligibility_reason": "Zwei RCTs mit zwei Armen und Ereigniszahlen, aber die Analyse poolt BOREAS und NOTUS; die vier Outcomes überlappen sich und sind nicht als vier unabhängige Outcomes zu zählen.",
        "risk_notes": [
            "post hoc",
            "pooled analysis of two RCTs",
            "overlapping outcomes",
            "NOTUS vorzeitig beendet",
            "keine Adjustierung für multiples Testen",
        ],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "Patients with >=1 ED visit/hospital admission, 52 weeks",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Dupilumab", "events": 50, "total": 938},
                "control": {"label": "Placebo", "events": 80, "total": 936},
                "usable": True,
                "independence": "independent",
                "note": "Gepoolte ITT-Population; Ereignisse/Total aus Text.",
                "source_quote": "Emergency department visits/hospitalizations | In the pooled ITT population, 5.3% (50 of 938) of patients receiving dupilumab and 8.5% (80 of 936) of patients receiving placebo had 65 and 96 ED visits/hospital admissions, respectively, during the 52-week treatment period.",
            },
            {
                "slot": 2,
                "outcome": "Patients with >=1 severe exacerbation, 52 weeks",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Dupilumab", "events": 41, "total": 938},
                "control": {"label": "Placebo", "events": 60, "total": 936},
                "usable": True,
                "independence": "overlapping_subgroup",
                "note": "Subgruppe mit Überlappung zu Slot 1; exakte Patientenzahlen aus Baseline-Charakteristik.",
                "source_quote": "Baseline demographics and disease characteristics | Baseline demographics and disease characteristics for the pooled ITT population (dupilumab: N = 938; placebo: N = 936), patients without an exacerbation event during the study (dupilumab: n = 600; placebo: n = 542), and patients with ≥ 1 severe exacerbation (dupilumab: n = 41; placebo: n = 60) or moderate exacerbation(s) only (dupilumab: n = 297; placebo: n = 334) during the study were similar across treatment arms and subgroups (Table 1 and Table S1).",
            },
            {
                "slot": 3,
                "outcome": "Patients with systemic corticosteroid use, 52 weeks",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Dupilumab", "events": 315, "total": 938},
                "control": {"label": "Placebo", "events": 366, "total": 936},
                "usable": True,
                "independence": "overlapping_subgroup",
                "note": "Überlappt mit Exazerbations-Outcomes; Ereignisse/Total aus Text.",
                "source_quote": "Systemic corticosteroid use | Overall, 33.6% (315 of 938) of patients receiving dupilumab and 39.1% (366 of 936) receiving placebo reported systemic corticosteroid use during the treatment period.",
            },
            {
                "slot": 4,
                "outcome": "Patients with ICU admission, 52 weeks",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Dupilumab", "events": 3, "total": 938},
                "control": {"label": "Placebo", "events": 7, "total": 936},
                "usable": True,
                "independence": "overlapping_subgroup",
                "note": "Subgruppe der Hospitalisierten; überlappt mit Slot 1 und Slot 2.",
                "source_quote": "Severe exacerbations | Of patients receiving dupilumab, 0.3% (3 of 938) had 3 COPD-related admissions to an intensive care unit; of patients receiving placebo, 0.7% (7 of 936) reported 7 admissions to an intensive care unit.",
            },
        ],
    },
    "PMC13590641": {
        "short_title": "Aumolertinib plus radiotherapy in stage III NSCLC",
        "design": "Phase-III-ADVANCE-RCT, open-label, vorzeitig beendet; Experiment 24 / Kontrolle 19; plus Real-World-Kohorte",
        "arm_n": {"intervention": 24, "control": 19, "randomized": 43, "analyzed": 43},
        "assisted_eligibility": "uncertain_safety_only_early_stopped",
        "eligibility_reason": "Zwei randomisierte Arme und Arm-N sind berichtet; vier Sicherheitsoutcomes mit Events/Total sind extrahierbar, armweise Wirksamkeitsdaten liegen jedoch nicht in vergleichbarer Form vor. Open-label und vorzeitig beendet.",
        "risk_notes": [
            "open-label",
            "vorzeitig beendet",
            "Safety-Population",
            "kleine Stichprobe",
            "Real-World-Kohorte nicht randomisiert",
        ],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "Any adverse event, any grade",
                "type": "binary",
                "table": "Table 3",
                "row_index": 3,
                "intervention": {"label": "Experiment (aumolertinib + RT)", "events": 23, "total": 24},
                "control": {"label": "Control (cCRT)", "events": 15, "total": 19},
                "usable": True,
                "note": "Any grade; Sammeloutcome. Tabelle führt zusätzlich Grade 1-4.",
            },
            {
                "slot": 2,
                "outcome": "Neutropenia, any grade",
                "type": "binary",
                "table": "Table 3",
                "row_index": 10,
                "intervention": {"label": "Experiment (aumolertinib + RT)", "events": 4, "total": 24},
                "control": {"label": "Control (cCRT)", "events": 10, "total": 19},
                "usable": True,
                "independence": "overlapping_subgroup",
                "note": "Any grade; spezifische AE, überlappt mit dem Sammeloutcome in Slot 1.",
            },
            {
                "slot": 3,
                "outcome": "Nausea, any grade",
                "type": "binary",
                "table": "Table 3",
                "row_index": 6,
                "intervention": {"label": "Experiment (aumolertinib + RT)", "events": 0, "total": 24},
                "control": {"label": "Control (cCRT)", "events": 5, "total": 19},
                "usable": True,
                "independence": "overlapping_subgroup",
                "note": "Any grade; spezifische AE, überlappt mit dem Sammeloutcome in Slot 1.",
            },
            {
                "slot": 4,
                "outcome": "Rash, any grade",
                "type": "binary",
                "table": "Table 3",
                "row_index": 5,
                "intervention": {"label": "Experiment (aumolertinib + RT)", "events": 6, "total": 24},
                "control": {"label": "Control (cCRT)", "events": 1, "total": 19},
                "usable": True,
                "independence": "overlapping_subgroup",
                "note": "Any grade; spezifische AE, überlappt mit dem Sammeloutcome in Slot 1.",
            },
        ],
    },
    "PMC13596784": {
        "short_title": "MATILDA feasibility trial",
        "design": "Zweiarmige randomisierte Machbarkeitsstudie; MATILDA 28 / aktive Kontrolle 29; 6 und 12 Monate",
        "arm_n": {
            "intervention": 28,
            "control": 29,
            "randomized": 57,
            "analyzed": "52 mit 6-Monats-Daten; 25 MATILDA nach Tod/Withdrawal",
        },
        "assisted_eligibility": "uncertain_feasibility_no_timepoint_n",
        "eligibility_reason": "Zwei randomisierte Arme und Mean/SD zu 6 Monaten sind berichtet, aber das armweise analysierte n pro Zeitpunkt fehlt; die Studie ist eine nicht gepowerte Machbarkeitsstudie.",
        "risk_notes": [
            "feasibility trial",
            "nicht gepowert",
            "kein armweises n pro Zeitpunkt",
            "unblinded",
            "missing data ohne Imputation",
        ],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "Glasgow Anxiety Inventory at 6 months",
                "type": "continuous",
                "table": "Table 4",
                "row_index": 10,
                "intervention": {"label": "MATILDA", "n": "nicht berichtet", "mean": "18.1", "sd": "8.3"},
                "control": {"label": "Active control", "n": "nicht berichtet", "mean": "17.1", "sd": "9.1"},
                "usable": False,
                "note": "Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation.",
            },
            {
                "slot": 2,
                "outcome": "WHO (Five) Well-Being Index at 6 months",
                "type": "continuous",
                "table": "Table 4",
                "row_index": 16,
                "intervention": {"label": "MATILDA", "n": "nicht berichtet", "mean": "16.4", "sd": "6.2"},
                "control": {"label": "Active control", "n": "nicht berichtet", "mean": "15.3", "sd": "6.2"},
                "usable": False,
                "note": "Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation.",
            },
            {
                "slot": 3,
                "outcome": "WHOQOL-DIS physical health at 6 months",
                "type": "continuous",
                "table": "Table 4",
                "row_index": 5,
                "intervention": {"label": "MATILDA", "n": "nicht berichtet", "mean": "3.8", "sd": "0.5"},
                "control": {"label": "Active control", "n": "nicht berichtet", "mean": "3.7", "sd": "0.5"},
                "usable": False,
                "note": "Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation.",
            },
            {
                "slot": 4,
                "outcome": "WHOQOL-DIS psychological health at 6 months",
                "type": "continuous",
                "table": "Table 4",
                "row_index": 6,
                "intervention": {"label": "MATILDA", "n": "nicht berichtet", "mean": "3.4", "sd": "0.5"},
                "control": {"label": "Active control", "n": "nicht berichtet", "mean": "3.2", "sd": "0.5"},
                "usable": False,
                "note": "Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation.",
            },
        ],
    },
    "PMC13574397": {
        "short_title": "Cost-effectiveness of omeprazole for esophageal stricture",
        "design": "Kosteneffektivitätsanalyse der vorausgegangenen RCT; Omeprazol 10 / Standard 10; 4 Wochen",
        "arm_n": {"intervention": 10, "control": 10, "randomized": 20, "analyzed": 20},
        "assisted_eligibility": "eligible_single_binary_outcome",
        "eligibility_reason": "Zwei randomisierte Arme und ein binäres klinisches Outcome mit Ereignissen/Total; die ökonomischen Outcomes sind ohne SD oder numerischen ICER nicht als Mean/SD extrahierbar.",
        "risk_notes": [
            "cost-effectiveness analysis",
            "post hoc",
            "kleine Stichprobe",
            "single center",
            "kurze Nachbeobachtung",
            "kein SD für Kosten",
        ],
        "outcomes": [
            {
                "slot": 1,
                "outcome": "Esophageal stricture at 4 weeks",
                "type": "binary",
                "table": "",
                "row_index": None,
                "intervention": {"label": "Omeprazole + standard care", "events": 2, "total": 10},
                "control": {"label": "Standard care", "events": 7, "total": 10},
                "usable": True,
                "note": "Ereignisse/Total aus Text; 20% und 70% nicht rekonstruiert.",
                "source_quote": "Results | The incidence of corrosive esophageal stricture was 20% (2/10) in the omeprazole group and 70% (7/10) in the standard treatment group (relative risk, 0.29; 95% confidence interval, 0.08–1.05; Fisher’s exact test, P = .070).",
            },
            {
                "slot": 2,
                "outcome": "Total cost per case, provider perspective (THB)",
                "type": "continuous",
                "table": "Table 2",
                "row_index": 3,
                "control_row_index": 4,
                "intervention": {"label": "Omeprazole + standard care", "n": 10, "mean": "12103.32"},
                "control": {"label": "Standard care", "n": 10, "mean": "16745.62"},
                "usable": False,
                "note": "Kosten pro Fall; kein SD berichtet.",
            },
            {
                "slot": 3,
                "outcome": "Total cost per case, patient perspective (THB)",
                "type": "continuous",
                "table": "Table 2",
                "row_index": 7,
                "control_row_index": 8,
                "intervention": {"label": "Omeprazole + standard care", "n": 10, "mean": "7652.60"},
                "control": {"label": "Standard care", "n": 10, "mean": "13129.20"},
                "usable": False,
                "note": "Kosten pro Fall; kein SD berichtet.",
            },
            {
                "slot": 4,
                "outcome": "Incremental cost-effectiveness ratio (ICER)",
                "type": "not_available",
                "table": "",
                "row_index": None,
                "intervention": {},
                "control": {},
                "usable": False,
                "note": "Standard care ist dominiert; kein numerischer ICER mit Unsicherheit berichtet.",
                "source_quote": "Table 2 | Base case results of health impact | Arms: Total cost (THB per case) / Total health outcome endpoint (corrosive esophageal stricture rate) / ICER* | Standard care | 16,745.62 | 0.70 | Dominated** | Context: Provider perspective; Standard care ist dominiert.",
            },
        ],
    },
}


def tables_by_label(article: dict) -> dict:
    return {table["label"]: table for table in article["candidate_tables"]}


def classify_independence(outcome: dict, pmcid: str) -> str:
    if not outcome["usable"]:
        return "not_usable"
    if outcome.get("independence"):
        return outcome["independence"]
    return "independent"


def main() -> None:
    dossier = json.loads(DOSSIER.read_text(encoding="utf-8"))
    by_id = {a["pmcid"]: a for a in dossier["records"]}
    payload = {
        "review_id": "p0_fulltext_review_batch2_v1",
        "created_at": "2026-11-13",
        "status": "assisted_batch_ready_for_human_confirmation",
        "scope": "Neun verbleibende hohe Prioritäten: " + ", ".join(TARGETS),
        "articles": len(TARGETS),
        "outcome_slots": 4 * len(TARGETS),
        "independent_usable_outcomes": 0,
        "overlapping_usable_outcomes": 0,
        "not_usable_or_absent": 0,
        "usable_outcomes_including_overlapping": 0,
        "final_decisions_made": False,
        "human_confirmation_required": True,
        "model_used": False,
        "network_used": False,
        "source_dossier": str(DOSSIER.relative_to(ROOT)).replace("\\", "/"),
        "records": [],
    }
    csv_rows = []
    class_counts = Counter()

    for pmcid in TARGETS:
        meta = RECORDS[pmcid]
        article = by_id[pmcid]
        tables = tables_by_label(article)
        outcomes = []
        for outcome in meta["outcomes"]:
            item = dict(outcome)
            manual_quote = item.pop("source_quote", "")
            if item["table"]:
                table = tables.get(item["table"])
                if table is None:
                    raise SystemExit(f"{pmcid}: table not found: {item['table']}")
                row = next((r for r in table["rows"] if r["row_index"] == item["row_index"]), None)
                if row is None:
                    raise SystemExit(f"{pmcid}: row {item['row_index']} not found in {item['table']}")
                if item.get("control_row_index") is not None:
                    control_row = next(
                        (r for r in table["rows"] if r["row_index"] == item["control_row_index"]),
                        None,
                    )
                    if control_row is None:
                        raise SystemExit(
                            f"{pmcid}: control row {item['control_row_index']} not found in {item['table']}"
                        )
                    source_quote = (
                        f"{table['label']} | {table['caption']} | Arms: {' / '.join(table['arm_headers'])} | "
                        f"{row['row_text']} | Control row: {control_row['row_text']}"
                    )
                else:
                    source_quote = (
                        f"{table['label']} | {table['caption']} | Arms: {' / '.join(table['arm_headers'])} | "
                        f"{row['row_text']}"
                    )
            else:
                source_quote = manual_quote

            context = CONTEXTS.get((pmcid, item["row_index"]))
            if context:
                source_quote += f" | Context: {context}"
            item["source_quote"] = source_quote
            independence = classify_independence(item, pmcid)
            item.pop("independence", None)
            item["outcome_independence"] = independence
            class_counts[independence] += 1
            outcomes.append(item)
            csv_rows.append(
                {
                    "pmcid": pmcid,
                    "slot": item["slot"],
                    "outcome": item["outcome"],
                    "type": item["type"],
                    "table": item["table"],
                    "row_index": item["row_index"] if item["row_index"] is not None else "",
                    "intervention_label": item["intervention"].get("label", ""),
                    "intervention_n": item["intervention"].get("n", ""),
                    "intervention_mean": item["intervention"].get("mean", ""),
                    "intervention_sd": item["intervention"].get("sd", ""),
                    "intervention_events": item["intervention"].get("events", ""),
                    "intervention_total": item["intervention"].get("total", ""),
                    "control_label": item["control"].get("label", ""),
                    "control_n": item["control"].get("n", ""),
                    "control_mean": item["control"].get("mean", ""),
                    "control_sd": item["control"].get("sd", ""),
                    "control_events": item["control"].get("events", ""),
                    "control_total": item["control"].get("total", ""),
                    "usable": item["usable"],
                    "outcome_independence": independence,
                    "note": item["note"],
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
                "outcome_counts": {
                    "independent_usable": sum(
                        1 for o in outcomes if o["outcome_independence"] == "independent"
                    ),
                    "overlapping_usable": sum(
                        1 for o in outcomes if o["outcome_independence"] == "overlapping_subgroup"
                    ),
                    "not_usable": sum(
                        1 for o in outcomes if o["outcome_independence"] == "not_usable"
                    ),
                },
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

    payload["independent_usable_outcomes"] = class_counts["independent"]
    payload["overlapping_usable_outcomes"] = class_counts["overlapping_subgroup"]
    payload["not_usable_or_absent"] = class_counts["not_usable"]
    payload["usable_outcomes_including_overlapping"] = (
        class_counts["independent"] + class_counts["overlapping_subgroup"]
    )
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    def format_arm_n(arm_n: dict) -> str:
        return (
            f"Intervention {arm_n.get('intervention', '?')} / Kontrolle {arm_n.get('control', '?')} / "
            f"randomisiert {arm_n.get('randomized', '?')} / analysiert {arm_n.get('analyzed', '?')}"
            + (f" / Trials {arm_n['trial_count']}" if arm_n.get("trial_count") else "")
        )

    def format_continuous(arm: dict) -> str:
        if arm.get("mean") is None:
            return "-"
        n = arm.get("n", "nicht berichtet")
        return f"n={n}, {arm['mean']} ({arm.get('sd', 'SD nicht berichtet')})"

    def format_binary(arm: dict) -> str:
        if arm.get("events") is None:
            return "-"
        return f"{arm['events']}/{arm.get('total', '?')}"

    lines = [
        "# Assistierte Volltextprüfung: Batch 2 (neun hohe Prioritäten)",
        "",
        "Stand: 2026-11-13",
        "Status: **ASSISTIERTE PRÜFUNG; MENSCHLICHE BESTÄTIGUNG OFFEN**.",
        "",
        "Keine finale Eignungsentscheidung, keine Übernahme in die Extraktionsvorlage,",
        "kein Modelllauf, kein Netzabruf. Werte sind nur aus berichteten Tabellenzeilen",
        "oder Results-Texten mit armweisen N/Mean/SD bzw. Events/Total transkribiert;",
        "Median/IQR, adjustierte Assoziationen und fehlende Arm-N bleiben leer.",
        "",
        "## Übersicht",
        "",
        "| PMC | Design | Arm-N | Assistierte Eignung | Verwendbar | Unabhängig | Überlappend |",
        "|---|---|---|---|---:|---:|---:|",
    ]
    for record in payload["records"]:
        counts = record["outcome_counts"]
        usable = counts["independent_usable"] + counts["overlapping_usable"]
        lines.append(
            f"| [{record['pmcid']}](https://pmc.ncbi.nlm.nih.gov/articles/{record['pmcid']}/) | "
            f"{record['design']} | {format_arm_n(record['arm_n'])} | {record['assisted_eligibility']} | "
            f"{usable}/4 | {counts['independent_usable']}/4 | {counts['overlapping_usable']}/4 |"
        )
    lines += [
        "",
        f"Unabhängig verwendbar: **{payload['independent_usable_outcomes']}/36**; "
        f"überlappend, nicht unabhängig: **{payload['overlapping_usable_outcomes']}/36**; "
        f"nicht verwendbar oder nicht berichtet: **{payload['not_usable_or_absent']}/36**.",
        f"Formal verwendbar einschließlich überlappender Outcomes: "
        f"**{payload['usable_outcomes_including_overlapping']}/36**.",
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
            "| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle |",
            "|---:|---|---|---|---|---|---|---|",
        ]
        for outcome in record["outcomes"]:
            inter = outcome["intervention"]
            control = outcome["control"]
            if outcome["type"] == "continuous":
                ival = format_continuous(inter)
                cval = format_continuous(control)
            elif outcome["type"] == "binary":
                ival = format_binary(inter)
                cval = format_binary(control)
            else:
                ival = "-"
                cval = "-"
            lines.append(
                f"| {outcome['slot']} | {outcome['outcome']} | {outcome['type']} | {ival} | {cval} | "
                f"{'ja' if outcome['usable'] else 'nein'} | {outcome['outcome_independence']} | {outcome['note']} |"
            )
        lines += ["", "### Quellen", ""]
        for outcome in record["outcomes"]:
            if outcome["source_quote"]:
                lines.append(f"- Slot {outcome['slot']}: `{outcome['source_quote']}`")
            else:
                lines.append(f"- Slot {outcome['slot']}: keine armweise Quelle berichtet")
        lines += [
            "",
            "### Menschliche Prüfung",
            "",
            "- [ ] zwei parallele Arme bestätigt",
            "- [ ] Randomisierung bestätigt",
            "- [ ] keine Armzusammenführung",
            "- [ ] Outcomes und Quellen bestätigt",
            "- [ ] finale Entscheidung gesetzt",
            "",
            "---",
            "",
        ]

    lines += [
        "## Konsequenz",
        "",
        f"{payload['independent_usable_outcomes']} Outcomes sind unabhängig verwendbar: vier aus `PMC13626740`,",
        f"eines aus `PMC13590641` (Sammeloutcome Any AE), eines aus `PMC13743599`, eines",
        f"aus `PMC13574397` und eines aus `PMC13519320`. `PMC13519320` liefert",
        f"drei weitere überlappende Outcomes aus einer gepoolten Analyse zweier RCTs;",
        f"`PMC13590641` liefert drei spezifische AEs, die mit dem Sammeloutcome",
        f"überlappen. Sie zählen nicht als unabhängig. Vier Artikel",
        f"bleiben ohne strukturierte Werte: `PMC13610533` (Median/IQR),",
        f"`PMC13613700` (nur adjustierte Assoziationen), `PMC13688066` (keine",
        f"Armzahlen) und `PMC13596784` (kein armweises n pro Zeitpunkt); bei",
        f"`PMC13574397` bleiben die ökonomischen Slots ohne SD bzw. numerischen ICER.",
        "",
        "Kein Modelllauf, kein Netzabruf, keine finale Auswahl.",
        "",
    ]
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "articles": len(TARGETS),
                "outcome_slots": payload["outcome_slots"],
                "independent_usable_outcomes": payload["independent_usable_outcomes"],
                "overlapping_usable_outcomes": payload["overlapping_usable_outcomes"],
                "not_usable_or_absent": payload["not_usable_or_absent"],
                "usable_outcomes_including_overlapping": payload[
                    "usable_outcomes_including_overlapping"
                ],
                "final_decisions_made": False,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
