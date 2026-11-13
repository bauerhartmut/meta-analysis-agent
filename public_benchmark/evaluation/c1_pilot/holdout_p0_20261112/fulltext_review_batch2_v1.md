# Assistierte Volltextprüfung: Batch 2 (neun hohe Prioritäten)

Stand: 2026-11-13
Status: **ASSISTIERTE PRÜFUNG; MENSCHLICHE BESTÄTIGUNG OFFEN**.

Keine finale Eignungsentscheidung, keine Übernahme in die Extraktionsvorlage,
kein Modelllauf, kein Netzabruf. Werte sind nur aus berichteten Tabellenzeilen
oder Results-Texten mit armweisen N/Mean/SD bzw. Events/Total transkribiert;
Median/IQR, adjustierte Assoziationen und fehlende Arm-N bleiben leer.

## Übersicht

| PMC | Design | Arm-N | Assistierte Eignung | Verwendbar | Unabhängig | Überlappend |
|---|---|---|---|---:|---:|---:|
| [PMC13610533](https://pmc.ncbi.nlm.nih.gov/articles/PMC13610533/) | Randomisierte Substudie innerhalb eines einarmigen Elternprojekts; Intervention 27 / Kontrolle 27; 12 Wochen | Intervention 27 / Kontrolle 27 / randomisiert 54 / analysiert 54 | uncertain_nested_substudy_medians | 0/4 | 0/4 | 0/4 |
| [PMC13743599](https://pmc.ncbi.nlm.nih.gov/articles/PMC13743599/) | Post-hoc-Analyse einer pivotalen 12-Wochen-RCT plus offene 12-Monats-Studie; tremor-dominante Subgruppe 17 SL-APO / 14 Placebo; Post-Werte n=10/10 | Intervention 17 / Kontrolle 14 / randomisiert 31 / analysiert 10/10 mit Post-Werten | eligible_single_post_hoc_outcome | 1/4 | 1/4 | 0/4 |
| [PMC13613700](https://pmc.ncbi.nlm.nih.gov/articles/PMC13613700/) | Sekundäranalyse der PEPaNIC-RCT; Early-PN 665 / Late-PN 663 ohne RRT; 90 Tage | Intervention 665 / Kontrolle 663 / randomisiert 1440 / analysiert 1328 | uncertain_secondary_no_arm_counts | 0/4 | 0/4 | 0/4 |
| [PMC13626740](https://pmc.ncbi.nlm.nih.gov/articles/PMC13626740/) | Sekundäranalyse der OPTIMA-RCT; CBT 101 / ST 97; T3 nach 7 Wochen | Intervention 101 / Kontrolle 97 / randomisiert 198 / analysiert 82/66 bei T3 | likely_eligible_two_arms | 4/4 | 4/4 | 0/4 |
| [PMC13688066](https://pmc.ncbi.nlm.nih.gov/articles/PMC13688066/) | Post-hoc-Sekundäranalyse der ANNEXa-I-RCT; 434 von 530 ITT mit Bildgebung; Andexanet vs. Usual Care | Intervention nicht berichtet / Kontrolle nicht berichtet / randomisiert 530 / analysiert 434 | uncertain_post_hoc_no_arm_counts | 0/4 | 0/4 | 0/4 |
| [PMC13519320](https://pmc.ncbi.nlm.nih.gov/articles/PMC13519320/) | Post-hoc-gepoolte Analyse von BOREAS und NOTUS; Dupilumab 938 / Placebo 936; 52 Wochen | Intervention 938 / Kontrolle 936 / randomisiert 1874 / analysiert 1874 / Trials 2 | uncertain_pooled_two_trials | 4/4 | 1/4 | 3/4 |
| [PMC13590641](https://pmc.ncbi.nlm.nih.gov/articles/PMC13590641/) | Phase-III-ADVANCE-RCT, open-label, vorzeitig beendet; Experiment 24 / Kontrolle 19; plus Real-World-Kohorte | Intervention 24 / Kontrolle 19 / randomisiert 43 / analysiert 43 | uncertain_safety_only_early_stopped | 4/4 | 1/4 | 3/4 |
| [PMC13596784](https://pmc.ncbi.nlm.nih.gov/articles/PMC13596784/) | Zweiarmige randomisierte Machbarkeitsstudie; MATILDA 28 / aktive Kontrolle 29; 6 und 12 Monate | Intervention 28 / Kontrolle 29 / randomisiert 57 / analysiert 52 mit 6-Monats-Daten; 25 MATILDA nach Tod/Withdrawal | uncertain_feasibility_no_timepoint_n | 0/4 | 0/4 | 0/4 |
| [PMC13574397](https://pmc.ncbi.nlm.nih.gov/articles/PMC13574397/) | Kosteneffektivitätsanalyse der vorausgegangenen RCT; Omeprazol 10 / Standard 10; 4 Wochen | Intervention 10 / Kontrolle 10 / randomisiert 20 / analysiert 20 | eligible_single_binary_outcome | 1/4 | 1/4 | 0/4 |

Unabhängig verwendbar: **8/36**; überlappend, nicht unabhängig: **6/36**; nicht verwendbar oder nicht berichtet: **22/36**.
Formal verwendbar einschließlich überlappender Outcomes: **14/36**.

## PMC13610533 — Chokeberry juice in women with prediabetes

- Titel: Effects of Chokeberry Juice Added to a Mediterranean-Style Diet on Glycemic Control and Redox Homeostasis in Women with Prediabetes: A Randomized Controlled Trial
- Design: Randomisierte Substudie innerhalb eines einarmigen Elternprojekts; Intervention 27 / Kontrolle 27; 12 Wochen
- Arm-N: Intervention 27 / Kontrolle 27 / randomisiert 54 / analysiert 54
- Assistierte Eignung: **uncertain_nested_substudy_medians**
- Begründung: Zwei randomisierte Arme und Arm-N sind berichtet, aber BMI, Glukose und Redoxwerte liegen als Median (IQR) und Veränderung vor; kein armweises Mean/SD.
- Risiken/Hinweise: nested substudy, single-group parent project, median/IQR statt Mean/SD, kleine Stichprobe

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle |
|---:|---|---|---|---|---|---|---|
| 1 | BMI at 3 months | continuous | - | - | nein | not_usable | Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung. |
| 2 | Fasting glucose at 3 months | continuous | - | - | nein | not_usable | Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung. |
| 3 | HbA1c at 3 months | continuous | - | - | nein | not_usable | Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung. |
| 4 | 2-hour postload glucose at 3 months | continuous | - | - | nein | not_usable | Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung. |

### Quellen

- Slot 1: `Table 3 | Baseline values and changes in BMI, glycemic, and redox-related parameters after the 3-month intervention in the intervention and control groups. | Arms: Intervention Group / ΔIG / Control Group / ΔCG / p for ΔIG vs. CG / FDR-Adjusted p / H–L est. for ΔIG − ΔCG (95% CI) / Cliff’s δ | BMI(kg/m2) | 25.8(24.6–26.7) | 25.9(23.8–26.9) | −0.4(−1 to 1) | 25.4(24.1–26.3) | 25.8(24.4–26.4) | 0.6(−0.6 to 0.7) | 0.310 | - |  | −0.168 | Context: 3-Monats-Werte; Reihenfolge: Baseline IG, 3 Monate IG, Delta IG, Baseline CG, 3 Monate CG, Delta CG, p, FDR-p, H-L-Effekt, Cliff's delta; Werte sind Median (IQR).`
- Slot 2: `Table 3 | Baseline values and changes in BMI, glycemic, and redox-related parameters after the 3-month intervention in the intervention and control groups. | Arms: Intervention Group / ΔIG / Control Group / ΔCG / p for ΔIG vs. CG / FDR-Adjusted p / H–L est. for ΔIG − ΔCG (95% CI) / Cliff’s δ | FG(mg/dL) | 112(107, 120) | 109(103, 117) | −3(−4 to −2) | 113(108, 118) | 112(108, 118) | −1(−2 to −1) | <0.001 | <0.001 | −2(−3 to −1) | −0.715 | Context: 3-Monats-Werte; Reihenfolge: Baseline IG, 3 Monate IG, Delta IG, Baseline CG, 3 Monate CG, Delta CG, p, FDR-p, H-L-Effekt, Cliff's delta; Werte sind Median (IQR).`
- Slot 3: `Table 3 | Baseline values and changes in BMI, glycemic, and redox-related parameters after the 3-month intervention in the intervention and control groups. | Arms: Intervention Group / ΔIG / Control Group / ΔCG / p for ΔIG vs. CG / FDR-Adjusted p / H–L est. for ΔIG − ΔCG (95% CI) / Cliff’s δ | HbA1c(mmol/mol) | 44(42, 45) | 41(39, 43) | −3(−3 to −2) | 44(42, 45) | 43(42, 45) | 1(−2 to 1) | <0.001 | <0.001 | −3(−4 to −1) | −0.734 | Context: 3-Monats-Werte; Reihenfolge: Baseline IG, 3 Monate IG, Delta IG, Baseline CG, 3 Monate CG, Delta CG, p, FDR-p, H-L-Effekt, Cliff's delta; Werte sind Median (IQR).`
- Slot 4: `Table 3 | Baseline values and changes in BMI, glycemic, and redox-related parameters after the 3-month intervention in the intervention and control groups. | Arms: Intervention Group / ΔIG / Control Group / ΔCG / p for ΔIG vs. CG / FDR-Adjusted p / H–L est. for ΔIG − ΔCG (95% CI) / Cliff’s δ | 2h-PG(mg/dL) | 164(151, 183) | 159(148, 179) | −4(−5 to −2) | 163(157, 180) | 162(157, 178) | −1(−2 to 1) | <0.001 | <0.001 | −3(−5 to −2) | −0.803 | Context: 3-Monats-Werte; Reihenfolge: Baseline IG, 3 Monate IG, Delta IG, Baseline CG, 3 Monate CG, Delta CG, p, FDR-p, H-L-Effekt, Cliff's delta; Werte sind Median (IQR).`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13743599 — Sublingual apomorphine for parkinsonian tremor

- Titel: Sublingual apomorphine for Parkinsonian tremor: a post-hoc analysis of pivotal trial data
- Design: Post-hoc-Analyse einer pivotalen 12-Wochen-RCT plus offene 12-Monats-Studie; tremor-dominante Subgruppe 17 SL-APO / 14 Placebo; Post-Werte n=10/10
- Arm-N: Intervention 17 / Kontrolle 14 / randomisiert 31 / analysiert 10/10 mit Post-Werten
- Assistierte Eignung: **eligible_single_post_hoc_outcome**
- Begründung: Zwei randomisierte Arme und ein kontinuierliches Outcome mit n/Mean/SD zu Woche 12; weitere Outcomes sind nur als Veränderung, Prozentwerte oder qualitativ berichtet.
- Risiken/Hinweise: post hoc, kleine tremor-dominante Subgruppe, available-case n=10/10, offene Verlängerung nicht kontrolliert

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle |
|---:|---|---|---|---|---|---|---|
| 1 | Tremor index at 30 min post-dose, Week 12 | continuous | n=10, 5.7 (3.3) | n=10, 11.3 (5.7) | ja | independent | Post-hoc; nur n=10/10 mit Post-Werten; 17/14 randomisiert. |
| 2 | Change in tremor index at 30 min, Week 12 | continuous | - | - | nein | not_usable | Within-group change: -5.3 [-7.3; -3.3] mit SL-APO und -1.1 [-2.5; 0.3] mit Placebo; Placebo-SD der Veränderung nicht berichtet. |
| 3 | Responder (>= MIC) at Week 12 | binary | - | - | nein | not_usable | Nur 80% vs. 30% bei n=10/10; keine Ereigniszahlen berichtet, keine Rekonstruktion. |
| 4 | Rest and postural tremor subscores | not_available | - | - | nein | not_usable | Nur qualitative Aussage zu beiden Tremor-Subtypen; keine armweisen Werte. |

### Quellen

- Slot 1: `Results | Mean ± SD tremor index scores decreased from 11.0 ± 4.8 pre-dose to 5.7 ± 3.3 at 30 min post-intake with SL-APO (n = 10), versus 12.4 ± 4.8 to 11.3 ± 5.7 with placebo (n = 10).`
- Slot 2: `Results | The within-group change was − 5.3 [− 7.3; −3.3] with SL‑APO and − 1.1 [− 2.5; 0.3] with placebo, yielding a between-group treatment effect of − 4.4 [− 6.5; −2.3] (p < 0.001; Fig. 1a).`
- Slot 3: `Results | Based on a calculated MIC of 2.3, responder rates were 80% with SL‑APO and 30% with placebo, supported by cumulative distribution function plots showing a consistent shift toward greater improvement with SL‑APO (Fig. 1c).`
- Slot 4: `Results | Improvements reflected reductions in both rest and postural tremor.`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13613700 — Ureagenesis in the PEPaNIC trial

- Titel: Increased ureagenesis revealing metabolic intolerance to enhanced nutrition in the PICU: a secondary analysis of the PEPaNIC RCT
- Design: Sekundäranalyse der PEPaNIC-RCT; Early-PN 665 / Late-PN 663 ohne RRT; 90 Tage
- Arm-N: Intervention 665 / Kontrolle 663 / randomisiert 1440 / analysiert 1328
- Assistierte Eignung: **uncertain_secondary_no_arm_counts**
- Begründung: Zwei randomisierte Arme sind berichtet, aber die klinischen Outcomes liegen nur als adjustierte OR/HR und p-Werte vor; keine armweisen Ereigniszahlen oder Time-to-Event-Rohdaten.
- Risiken/Hinweise: secondary analysis, keine armweisen Ereigniszahlen, RRT-Patienten ausgeschlossen, kompetierendes Risiko Tod, 6% fehlende Daten

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle |
|---:|---|---|---|---|---|---|---|
| 1 | New infection during PICU stay | binary | - | - | nein | not_usable | Nur adjustierte Assoziation und p-Wert; keine Ereignisse/Total pro Arm. |
| 2 | PICU dependency (time to live discharge) | time_to_event | - | - | nein | not_usable | Nur adjustierte HR/Modellresultate; keine armweisen Rohdaten oder Ereigniszahlen. |
| 3 | 90-day mortality | binary | - | - | nein | not_usable | Nur adjustierte Assoziation und p-Wert; keine Ereignisse/Total pro Arm. |
| 4 | Hospital dependency (time to live discharge) | time_to_event | - | - | nein | not_usable | Nur adjustierte HR/Modellresultate; keine armweisen Rohdaten oder Ereigniszahlen. |

### Quellen

- Slot 1: `Results | Adjusting for baseline risk factors, randomization to early-PN as compared with late-PN was independently associated with a higher risk of acquiring a new infection in the PICU (p = 0.0063) and a lower likelihood of earlier live discharge from the PICU (p = 0.0068) and the hospital (p = 0.023), but not with 90-day mortality (p = 0.22) (Fig. 3, Additional File 1 Table S2).`
- Slot 2: `Results | Adjusting for baseline risk factors, randomization to early-PN as compared with late-PN was independently associated with a higher risk of acquiring a new infection in the PICU (p = 0.0063) and a lower likelihood of earlier live discharge from the PICU (p = 0.0068) and the hospital (p = 0.023), but not with 90-day mortality (p = 0.22) (Fig. 3, Additional File 1 Table S2).`
- Slot 3: `Results | Adjusting for baseline risk factors, randomization to early-PN as compared with late-PN was independently associated with a higher risk of acquiring a new infection in the PICU (p = 0.0063) and a lower likelihood of earlier live discharge from the PICU (p = 0.0068) and the hospital (p = 0.023), but not with 90-day mortality (p = 0.22) (Fig. 3, Additional File 1 Table S2).`
- Slot 4: `Results | Adjusting for baseline risk factors, randomization to early-PN as compared with late-PN was independently associated with a higher risk of acquiring a new infection in the PICU (p = 0.0063) and a lower likelihood of earlier live discharge from the PICU (p = 0.0068) and the hospital (p = 0.023), but not with 90-day mortality (p = 0.22) (Fig. 3, Additional File 1 Table S2).`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13626740 — Mechanisms of change in depression therapy

- Titel: Mechanisms of Change in the Treatment of Depression: On the Role of Attachment, Reappraisal and Suppression
- Design: Sekundäranalyse der OPTIMA-RCT; CBT 101 / ST 97; T3 nach 7 Wochen
- Arm-N: Intervention 101 / Kontrolle 97 / randomisiert 198 / analysiert 82/66 bei T3
- Assistierte Eignung: **likely_eligible_two_arms**
- Begründung: Zwei randomisierte Arme, Arm-N und vier kontinuierliche Outcomes mit N/Mean/SD zu Post-Treatment T3.
- Risiken/Hinweise: secondary analysis, available-case n zu T3, Parent-RCT OPTIMA, nur CBT vs. ST ausgewählt

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle |
|---:|---|---|---|---|---|---|---|
| 1 | Depressive symptoms (BDI-II), post-treatment T3 | continuous | n=82, 14.80 (8.99) | n=66, 18.00 (10.97) | ja | independent | Post-treatment T3 (Woche 7); verfügbares n. |
| 2 | Expressive suppression (ERQ), post-treatment T3 | continuous | n=79, 3.53 (1.47) | n=60, 3.73 (1.45) | ja | independent | Post-treatment T3 (Woche 7); verfügbares n. |
| 3 | Cognitive reappraisal (ERQ), post-treatment T3 | continuous | n=79, 4.12 (1.47) | n=60, 3.89 (1.10) | ja | independent | Post-treatment T3 (Woche 7); verfügbares n. |
| 4 | Avoidant attachment (RSQ fear of closeness), post-treatment T3 | continuous | n=79, 2.57 (1.00) | n=59, 2.73 (0.89) | ja | independent | Post-treatment T3 (Woche 7); verfügbares n. |

### Quellen

- Slot 1: `TABLE 1 | Means and standard deviations of the mechanisms and depressive symptoms. | Arms: Total sample (n = 198) / CBT (n = 101) / ST (n = 97) | DS | 148 | 16.23 | 10.02 | 82 | 14.80 | 8.99 | 66 | 18.00 | 10.97 | Context: Post-treatment T3 (Woche 7); Spalten: Total n/M/SD, CBT n/M/SD, ST n/M/SD.`
- Slot 2: `TABLE 1 | Means and standard deviations of the mechanisms and depressive symptoms. | Arms: Total sample (n = 198) / CBT (n = 101) / ST (n = 97) | ES | 139 | 3.62 | 1.46 | 79 | 3.53 | 1.47 | 60 | 3.73 | 1.45 | Context: Post-treatment T3 (Woche 7); Spalten: Total n/M/SD, CBT n/M/SD, ST n/M/SD.`
- Slot 3: `TABLE 1 | Means and standard deviations of the mechanisms and depressive symptoms. | Arms: Total sample (n = 198) / CBT (n = 101) / ST (n = 97) | CR | 139 | 4.02 | 1.32 | 79 | 4.12 | 1.47 | 60 | 3.89 | 1.10 | Context: Post-treatment T3 (Woche 7); Spalten: Total n/M/SD, CBT n/M/SD, ST n/M/SD.`
- Slot 4: `TABLE 1 | Means and standard deviations of the mechanisms and depressive symptoms. | Arms: Total sample (n = 198) / CBT (n = 101) / ST (n = 97) | AV | 138 | 2.64 | 0.95 | 79 | 2.57 | 1.00 | 59 | 2.73 | 0.89 | Context: Post-treatment T3 (Woche 7); Spalten: Total n/M/SD, CBT n/M/SD, ST n/M/SD.`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13688066 — NCCT markers and andexanet response

- Titel: Non‐contrast CT Markers of Hematoma Expansion and Andexanet Response in Factor Xa Inhibitor‐Associated Intracerebral Hemorrhage: An Analysis from ANNEXa‐I Trial
- Design: Post-hoc-Sekundäranalyse der ANNEXa-I-RCT; 434 von 530 ITT mit Bildgebung; Andexanet vs. Usual Care
- Arm-N: Intervention nicht berichtet / Kontrolle nicht berichtet / randomisiert 530 / analysiert 434
- Assistierte Eignung: **uncertain_post_hoc_no_arm_counts**
- Begründung: Randomisierte Arme sind im Design berichtet, aber die HE-Outcomes liegen nur als Gesamtfrequenz, Subgruppeninteraktionen oder adjustierte Assoziationen vor; keine armweisen Ereignisse/Total.
- Risiken/Hinweise: post hoc, keine armweisen Ereigniszahlen, 434/530 mit Bildgebung, explorative Interaktionstests, Bildgebungsselektion

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle |
|---:|---|---|---|---|---|---|---|
| 1 | Significant hematoma expansion (>=12.5 ml or >=35%) | binary | - | - | nein | not_usable | Gesamtpopulation 138/434 (31.8%); keine armweisen Ereigniszahlen im Text. |
| 2 | Severe hematoma expansion (>=12.5 ml or >=66%) | binary | - | - | nein | not_usable | Nur definiertes Outcome; keine armweisen Ereigniszahlen im Text. |
| 3 | HE in hypodensity subgroup | binary | - | - | nein | not_usable | Nur absolute Reduktion 19.5% vs. 8.0% berichtet; keine Ereigniszahlen. |
| 4 | HE in blend-sign subgroup | binary | - | - | nein | not_usable | Nur Interaktions-OR 0.03 (0.00-0.29) vs. 0.60 (0.38-0.96), p=0.01; keine Ereigniszahlen. |

### Quellen

- Slot 1: `Patients' Characteristics | Among 530 patients in the intention‐to‐treat population, 434 (197 female, mean age 79.3 ± 8.1 years) had qualifying ICH, baseline NCCT, and follow‐up imaging available for assessment of HE and were included in this study (Figure S2). HE was observed in 138 patients (31.8%).`
- Slot 2: `Outcomes | The secondary outcome was severe HE, defined as ≥12.5 ml or ≥ 66% increase.`
- Slot 3: `Treatment Interaction of Andexanet | The absolute reduction in HE with andexanet appeared greater in patients with hypodensity (19.5% vs. 8.0%) than those without.`
- Slot 4: `Treatment Interaction of Andexanet | A treatment interaction was observed for the blend sign (OR 0.03, 95% CI 0.00–0.29 for those with blend sign; and OR 0.60, 95% CI 0.38–0.96 for those without, p for interaction = 0.01).`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13519320 — Dupilumab and COPD exacerbation resource use

- Titel: Dupilumab in chronic obstructive pulmonary disease: a pooled analysis of emergency department visits, hospital admissions, and systemic corticosteroid use
- Design: Post-hoc-gepoolte Analyse von BOREAS und NOTUS; Dupilumab 938 / Placebo 936; 52 Wochen
- Arm-N: Intervention 938 / Kontrolle 936 / randomisiert 1874 / analysiert 1874 / Trials 2
- Assistierte Eignung: **uncertain_pooled_two_trials**
- Begründung: Zwei RCTs mit zwei Armen und Ereigniszahlen, aber die Analyse poolt BOREAS und NOTUS; die vier Outcomes überlappen sich und sind nicht als vier unabhängige Outcomes zu zählen.
- Risiken/Hinweise: post hoc, pooled analysis of two RCTs, overlapping outcomes, NOTUS vorzeitig beendet, keine Adjustierung für multiples Testen

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle |
|---:|---|---|---|---|---|---|---|
| 1 | Patients with >=1 ED visit/hospital admission, 52 weeks | binary | 50/938 | 80/936 | ja | independent | Gepoolte ITT-Population; Ereignisse/Total aus Text. |
| 2 | Patients with >=1 severe exacerbation, 52 weeks | binary | 41/938 | 60/936 | ja | overlapping_subgroup | Subgruppe mit Überlappung zu Slot 1; exakte Patientenzahlen aus Baseline-Charakteristik. |
| 3 | Patients with systemic corticosteroid use, 52 weeks | binary | 315/938 | 366/936 | ja | overlapping_subgroup | Überlappt mit Exazerbations-Outcomes; Ereignisse/Total aus Text. |
| 4 | Patients with ICU admission, 52 weeks | binary | 3/938 | 7/936 | ja | overlapping_subgroup | Subgruppe der Hospitalisierten; überlappt mit Slot 1 und Slot 2. |

### Quellen

- Slot 1: `Emergency department visits/hospitalizations | In the pooled ITT population, 5.3% (50 of 938) of patients receiving dupilumab and 8.5% (80 of 936) of patients receiving placebo had 65 and 96 ED visits/hospital admissions, respectively, during the 52-week treatment period.`
- Slot 2: `Baseline demographics and disease characteristics | Baseline demographics and disease characteristics for the pooled ITT population (dupilumab: N = 938; placebo: N = 936), patients without an exacerbation event during the study (dupilumab: n = 600; placebo: n = 542), and patients with ≥ 1 severe exacerbation (dupilumab: n = 41; placebo: n = 60) or moderate exacerbation(s) only (dupilumab: n = 297; placebo: n = 334) during the study were similar across treatment arms and subgroups (Table 1 and Table S1).`
- Slot 3: `Systemic corticosteroid use | Overall, 33.6% (315 of 938) of patients receiving dupilumab and 39.1% (366 of 936) receiving placebo reported systemic corticosteroid use during the treatment period.`
- Slot 4: `Severe exacerbations | Of patients receiving dupilumab, 0.3% (3 of 938) had 3 COPD-related admissions to an intensive care unit; of patients receiving placebo, 0.7% (7 of 936) reported 7 admissions to an intensive care unit.`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13590641 — Aumolertinib plus radiotherapy in stage III NSCLC

- Titel: Induction and concurrent aumolertinib with radiotherapy for EGFR-mutated stage III NSCLC: results of phase III ADVANCE trial and real-world validation
- Design: Phase-III-ADVANCE-RCT, open-label, vorzeitig beendet; Experiment 24 / Kontrolle 19; plus Real-World-Kohorte
- Arm-N: Intervention 24 / Kontrolle 19 / randomisiert 43 / analysiert 43
- Assistierte Eignung: **uncertain_safety_only_early_stopped**
- Begründung: Zwei randomisierte Arme und Arm-N sind berichtet; vier Sicherheitsoutcomes mit Events/Total sind extrahierbar, armweise Wirksamkeitsdaten liegen jedoch nicht in vergleichbarer Form vor. Open-label und vorzeitig beendet.
- Risiken/Hinweise: open-label, vorzeitig beendet, Safety-Population, kleine Stichprobe, Real-World-Kohorte nicht randomisiert

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle |
|---:|---|---|---|---|---|---|---|
| 1 | Any adverse event, any grade | binary | 23/24 | 15/19 | ja | independent | Any grade; Sammeloutcome. Tabelle führt zusätzlich Grade 1-4. |
| 2 | Neutropenia, any grade | binary | 4/24 | 10/19 | ja | overlapping_subgroup | Any grade; spezifische AE, überlappt mit dem Sammeloutcome in Slot 1. |
| 3 | Nausea, any grade | binary | 0/24 | 5/19 | ja | overlapping_subgroup | Any grade; spezifische AE, überlappt mit dem Sammeloutcome in Slot 1. |
| 4 | Rash, any grade | binary | 6/24 | 1/19 | ja | overlapping_subgroup | Any grade; spezifische AE, überlappt mit dem Sammeloutcome in Slot 1. |

### Quellen

- Slot 1: `Table 3 | Most common adverse events of any cause in > 5% | Arms: Control groupNo. (%) (N = 19) / Experiment groupNo. (%) (N = 24) / P | Any events | 15 (78.9) | 5 (26.3) | 6 (31.6) | 4 (21.1) | 0 (0.0) | 23 (95.8) | 10 (41.7) | 9 (37.5) | 4 (16.7) | 0 (0.0) | 0.32 | Context: Any grade (erste Spalte je Arm); weitere Spalten Grade 1-4.`
- Slot 2: `Table 3 | Most common adverse events of any cause in > 5% | Arms: Control groupNo. (%) (N = 19) / Experiment groupNo. (%) (N = 24) / P | Neutropenia | 10 (52.6) | 1 (5.3) | 6 (31.6) | 3 (15.8) | 0 (0.0) | 4 (16.7) | 3 (12.5) | 1 (4.2) | 0 (0.0) | 0 (0.0) | 0.01 | Context: Any grade (erste Spalte je Arm); weitere Spalten Grade 1-4.`
- Slot 3: `Table 3 | Most common adverse events of any cause in > 5% | Arms: Control groupNo. (%) (N = 19) / Experiment groupNo. (%) (N = 24) / P | Nausea | 5 (26.3) | 1 (5.3) | 4 (21.1) | 0 (0.0) | 0 (0.0) | 0 (0.0) | 0 (0.0) | 0 (0.0) | 0 (0.0) | 0 (0.0) | 0.028 | Context: Any grade (erste Spalte je Arm); weitere Spalten Grade 1-4.`
- Slot 4: `Table 3 | Most common adverse events of any cause in > 5% | Arms: Control groupNo. (%) (N = 19) / Experiment groupNo. (%) (N = 24) / P | Rash | 1 (5.3) | 0 (0.0) | 1 (5.3) | 0 (0.0) | 0 (0.0) | 6 (25.0) | 4 (16.7) | 2 (8.3) | 0 (0.0) | 0 (0.0) | 0.15 | Context: Any grade (erste Spalte je Arm); weitere Spalten Grade 1-4.`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13596784 — MATILDA feasibility trial

- Titel: Implementing the MATILDA intervention to enhance community participation for older adults with intellectual disability: A feasibility randomised controlled trial and RE-AIM guided process evaluation
- Design: Zweiarmige randomisierte Machbarkeitsstudie; MATILDA 28 / aktive Kontrolle 29; 6 und 12 Monate
- Arm-N: Intervention 28 / Kontrolle 29 / randomisiert 57 / analysiert 52 mit 6-Monats-Daten; 25 MATILDA nach Tod/Withdrawal
- Assistierte Eignung: **uncertain_feasibility_no_timepoint_n**
- Begründung: Zwei randomisierte Arme und Mean/SD zu 6 Monaten sind berichtet, aber das armweise analysierte n pro Zeitpunkt fehlt; die Studie ist eine nicht gepowerte Machbarkeitsstudie.
- Risiken/Hinweise: feasibility trial, nicht gepowert, kein armweises n pro Zeitpunkt, unblinded, missing data ohne Imputation

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle |
|---:|---|---|---|---|---|---|---|
| 1 | Glasgow Anxiety Inventory at 6 months | continuous | n=nicht berichtet, 18.1 (8.3) | n=nicht berichtet, 17.1 (9.1) | nein | not_usable | Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation. |
| 2 | WHO (Five) Well-Being Index at 6 months | continuous | n=nicht berichtet, 16.4 (6.2) | n=nicht berichtet, 15.3 (6.2) | nein | not_usable | Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation. |
| 3 | WHOQOL-DIS physical health at 6 months | continuous | n=nicht berichtet, 3.8 (0.5) | n=nicht berichtet, 3.7 (0.5) | nein | not_usable | Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation. |
| 4 | WHOQOL-DIS psychological health at 6 months | continuous | n=nicht berichtet, 3.4 (0.5) | n=nicht berichtet, 3.2 (0.5) | nein | not_usable | Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation. |

### Quellen

- Slot 1: `Table 4 | Mean and standard deviations of the secondary outcome measures for the participants in the MATILDA and Control Arms. | Arms:  / Control Arm /  / MATILDA Arm | Glasgow Anxiety Inventory | 19.6 (9.6) | 17.1 (9.1) | 18.2 (11.2) | 20.7 (10.5) | 18.1 (8.3) | 16 (9.1) | | Context: 6-Monats-Follow-up; Spalten: Control Baseline/6m/12m, MATILDA Baseline/6m/12m.`
- Slot 2: `Table 4 | Mean and standard deviations of the secondary outcome measures for the participants in the MATILDA and Control Arms. | Arms:  / Control Arm /  / MATILDA Arm | WHO (Five) Well-Being Index | 17.5 (5.3) | 15.3 (6.2) | 18.5 (5.2) | 18.9 (4.7) | 16.4 (6.2) | 18.2 (5.1) | | Context: 6-Monats-Follow-up; Spalten: Control Baseline/6m/12m, MATILDA Baseline/6m/12m.`
- Slot 3: `Table 4 | Mean and standard deviations of the secondary outcome measures for the participants in the MATILDA and Control Arms. | Arms:  / Control Arm /  / MATILDA Arm | Physical Health | 3.5 (0.3) | 3.7 (0.5) | 3 (0.5) | 3.5(0.5) | 3.8 (0.5) | 3 (0.5) | | Context: 6-Monats-Follow-up; Spalten: Control Baseline/6m/12m, MATILDA Baseline/6m/12m.`
- Slot 4: `Table 4 | Mean and standard deviations of the secondary outcome measures for the participants in the MATILDA and Control Arms. | Arms:  / Control Arm /  / MATILDA Arm | Psychological Health | 3.3 (0.5) | 3.2 (0.5) | 3.3 (0.5) | 3.4 (0.5) | 3.4 (0.5) | 3.2 (0.5) | | Context: 6-Monats-Follow-up; Spalten: Control Baseline/6m/12m, MATILDA Baseline/6m/12m.`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13574397 — Cost-effectiveness of omeprazole for esophageal stricture

- Titel: Cost-effectiveness analysis of omeprazole for preventing esophageal stricture in patients with Zargar grade 2b and 3a corrosive esophageal injuries
- Design: Kosteneffektivitätsanalyse der vorausgegangenen RCT; Omeprazol 10 / Standard 10; 4 Wochen
- Arm-N: Intervention 10 / Kontrolle 10 / randomisiert 20 / analysiert 20
- Assistierte Eignung: **eligible_single_binary_outcome**
- Begründung: Zwei randomisierte Arme und ein binäres klinisches Outcome mit Ereignissen/Total; die ökonomischen Outcomes sind ohne SD oder numerischen ICER nicht als Mean/SD extrahierbar.
- Risiken/Hinweise: cost-effectiveness analysis, post hoc, kleine Stichprobe, single center, kurze Nachbeobachtung, kein SD für Kosten

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle |
|---:|---|---|---|---|---|---|---|
| 1 | Esophageal stricture at 4 weeks | binary | 2/10 | 7/10 | ja | independent | Ereignisse/Total aus Text; 20% und 70% nicht rekonstruiert. |
| 2 | Total cost per case, provider perspective (THB) | continuous | n=10, 12103.32 (SD nicht berichtet) | n=10, 16745.62 (SD nicht berichtet) | nein | not_usable | Kosten pro Fall; kein SD berichtet. |
| 3 | Total cost per case, patient perspective (THB) | continuous | n=10, 7652.60 (SD nicht berichtet) | n=10, 13129.20 (SD nicht berichtet) | nein | not_usable | Kosten pro Fall; kein SD berichtet. |
| 4 | Incremental cost-effectiveness ratio (ICER) | not_available | - | - | nein | not_usable | Standard care ist dominiert; kein numerischer ICER mit Unsicherheit berichtet. |

### Quellen

- Slot 1: `Results | The incidence of corrosive esophageal stricture was 20% (2/10) in the omeprazole group and 70% (7/10) in the standard treatment group (relative risk, 0.29; 95% confidence interval, 0.08–1.05; Fisher’s exact test, P = .070).`
- Slot 2: `Table 2 | Base case results of health impact. | Arms: Total cost (THB per case) / Total health outcome endpoint (corrosive esophageal stricture rate) / ICER* | Omeprazole plus standard care | 12,103.32 | 0.20 | | Control row: Standard care | 16,745.62 | 0.70 | Dominated** | Context: Provider perspective; Kostenspalte pro Fall, danach Strikturrate und ICER.`
- Slot 3: `Table 2 | Base case results of health impact. | Arms: Total cost (THB per case) / Total health outcome endpoint (corrosive esophageal stricture rate) / ICER* | Omeprazole plus standard care | 7652.60 | 0.20 | | Control row: Standard care | 13,129.20 | 0.70 | Dominated** | Context: Patient perspective; Kostenspalte pro Fall, danach Strikturrate und ICER.`
- Slot 4: `Table 2 | Base case results of health impact | Arms: Total cost (THB per case) / Total health outcome endpoint (corrosive esophageal stricture rate) / ICER* | Standard care | 16,745.62 | 0.70 | Dominated** | Context: Provider perspective; Standard care ist dominiert.`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## Konsequenz

8 Outcomes sind unabhängig verwendbar: vier aus `PMC13626740`,
eines aus `PMC13590641` (Sammeloutcome Any AE), eines aus `PMC13743599`, eines
aus `PMC13574397` und eines aus `PMC13519320`. `PMC13519320` liefert
drei weitere überlappende Outcomes aus einer gepoolten Analyse zweier RCTs;
`PMC13590641` liefert drei spezifische AEs, die mit dem Sammeloutcome
überlappen. Sie zählen nicht als unabhängig. Vier Artikel
bleiben ohne strukturierte Werte: `PMC13610533` (Median/IQR),
`PMC13613700` (nur adjustierte Assoziationen), `PMC13688066` (keine
Armzahlen) und `PMC13596784` (kein armweises n pro Zeitpunkt); bei
`PMC13574397` bleiben die ökonomischen Slots ohne SD bzw. numerischen ICER.

Kein Modelllauf, kein Netzabruf, keine finale Auswahl.
