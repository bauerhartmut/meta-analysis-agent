# Menschliche Prüfcheckliste: Batch 2 (36 Slots)

Stand: 2026-11-13
Status: **OFFEN; DIESE CHECKLISTE SETZT KEINE FINALEN ENTSCHEIDUNGEN**.

Quelle: `fulltext_review_batch2_v1.json`, `...csv`, `...md` sowie lokale XML.
Die Outcome-Werte sind unverändert. Bitte pro Slot Quelle, Zahlen,
Unabhängigkeit und Eignung prüfen; bei Unklarheit den Slot offen lassen.

## A. Globale Prüfung

- [ ] 36/36 Slots gesichtet
- [ ] Zähler 8 unabhängig / 6 überlappend / 22 nicht verwendbar bestätigt
- [ ] 14 formal verwendbar bestätigt
- [ ] 36/36 Quellen geprüft
- [ ] 6 überlappende Slots bestätigt
- [ ] keine Outcome-Werte verändert
- [ ] finale Entscheidungen nur im dafür vorgesehenen Dokument gesetzt

## B. Artikel- und Slotprüfung

### PMC13610533 — Chokeberry juice in women with prediabetes

- Titel: Effects of Chokeberry Juice Added to a Mediterranean-Style Diet on Glycemic Control and Redox Homeostasis in Women with Prediabetes: A Randomized Controlled Trial
- Design: Randomisierte Substudie innerhalb eines einarmigen Elternprojekts; Intervention 27 / Kontrolle 27; 12 Wochen
- Arm-N: Intervention 27 / Kontrolle 27 / randomisiert 54 / analysiert 54
- Assistierte Eignung: **uncertain_nested_substudy_medians**
- Vorprüfung: Zwei randomisierte Arme und Arm-N sind berichtet, aber BMI, Glukose und Redoxwerte liegen als Median (IQR) und Veränderung vor; kein armweises Mean/SD.

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Arm-N und analysiertes n bestätigt (0 unabhängig, 0 überlappend, 4 nicht verwendbar)
- [ ] Quellen und Werte pro Slot bestätigt
- [ ] Überlappungsklasse pro Slot bestätigt

| Geprüft | Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle | Befund |
|---|---|---|---|---|---|---|---|---|---|
| [ ] | 1 | BMI at 3 months | continuous | - | - | nein | not_usable | Tabelle 3, Zeile 3 | offen |
| [ ] | 2 | Fasting glucose at 3 months | continuous | - | - | nein | not_usable | Tabelle 3, Zeile 4 | offen |
| [ ] | 3 | HbA1c at 3 months | continuous | - | - | nein | not_usable | Tabelle 3, Zeile 5 | offen |
| [ ] | 4 | 2-hour postload glucose at 3 months | continuous | - | - | nein | not_usable | Tabelle 3, Zeile 6 | offen |

**Vorprüfungsnotizen:**

- Slot 1: Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung.
- Slot 2: Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung.
- Slot 3: Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung.
- Slot 4: Median (IQR) und Veränderung; kein armweises Mean/SD. Keine Umrechnung.

---

### PMC13743599 — Sublingual apomorphine for parkinsonian tremor

- Titel: Sublingual apomorphine for Parkinsonian tremor: a post-hoc analysis of pivotal trial data
- Design: Post-hoc-Analyse einer pivotalen 12-Wochen-RCT plus offene 12-Monats-Studie; tremor-dominante Subgruppe 17 SL-APO / 14 Placebo; Post-Werte n=10/10
- Arm-N: Intervention 17 / Kontrolle 14 / randomisiert 31 / analysiert 10/10 mit Post-Werten
- Assistierte Eignung: **eligible_single_post_hoc_outcome**
- Vorprüfung: Zwei randomisierte Arme und ein kontinuierliches Outcome mit n/Mean/SD zu Woche 12; weitere Outcomes sind nur als Veränderung, Prozentwerte oder qualitativ berichtet.

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Arm-N und analysiertes n bestätigt (1 unabhängig, 0 überlappend, 3 nicht verwendbar)
- [ ] Quellen und Werte pro Slot bestätigt
- [ ] Überlappungsklasse pro Slot bestätigt

| Geprüft | Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle | Befund |
|---|---|---|---|---|---|---|---|---|---|
| [ ] | 1 | Tremor index at 30 min post-dose, Week 12 | continuous | n=10, 5.7 (3.3) | n=10, 11.3 (5.7) | ja | independent | Results-Text | offen |
| [ ] | 2 | Change in tremor index at 30 min, Week 12 | continuous | - | - | nein | not_usable | Results-Text | offen |
| [ ] | 3 | Responder (>= MIC) at Week 12 | binary | - | - | nein | not_usable | Results-Text | offen |
| [ ] | 4 | Rest and postural tremor subscores | not_available | - | - | nein | not_usable | Results-Text | offen |

**Vorprüfungsnotizen:**

- Slot 1: Post-hoc; nur n=10/10 mit Post-Werten; 17/14 randomisiert.
- Slot 2: Within-group change: -5.3 [-7.3; -3.3] mit SL-APO und -1.1 [-2.5; 0.3] mit Placebo; Placebo-SD der Veränderung nicht berichtet.
- Slot 3: Nur 80% vs. 30% bei n=10/10; keine Ereigniszahlen berichtet, keine Rekonstruktion.
- Slot 4: Nur qualitative Aussage zu beiden Tremor-Subtypen; keine armweisen Werte.

---

### PMC13613700 — Ureagenesis in the PEPaNIC trial

- Titel: Increased ureagenesis revealing metabolic intolerance to enhanced nutrition in the PICU: a secondary analysis of the PEPaNIC RCT
- Design: Sekundäranalyse der PEPaNIC-RCT; Early-PN 665 / Late-PN 663 ohne RRT; 90 Tage
- Arm-N: Intervention 665 / Kontrolle 663 / randomisiert 1440 / analysiert 1328
- Assistierte Eignung: **uncertain_secondary_no_arm_counts**
- Vorprüfung: Zwei randomisierte Arme sind berichtet, aber die klinischen Outcomes liegen nur als adjustierte OR/HR und p-Werte vor; keine armweisen Ereigniszahlen oder Time-to-Event-Rohdaten.

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Arm-N und analysiertes n bestätigt (0 unabhängig, 0 überlappend, 4 nicht verwendbar)
- [ ] Quellen und Werte pro Slot bestätigt
- [ ] Überlappungsklasse pro Slot bestätigt

| Geprüft | Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle | Befund |
|---|---|---|---|---|---|---|---|---|---|
| [ ] | 1 | New infection during PICU stay | binary | - | - | nein | not_usable | Results-Text | offen |
| [ ] | 2 | PICU dependency (time to live discharge) | time_to_event | - | - | nein | not_usable | Results-Text | offen |
| [ ] | 3 | 90-day mortality | binary | - | - | nein | not_usable | Results-Text | offen |
| [ ] | 4 | Hospital dependency (time to live discharge) | time_to_event | - | - | nein | not_usable | Results-Text | offen |

**Vorprüfungsnotizen:**

- Slot 1: Nur adjustierte Assoziation und p-Wert; keine Ereignisse/Total pro Arm.
- Slot 2: Nur adjustierte HR/Modellresultate; keine armweisen Rohdaten oder Ereigniszahlen.
- Slot 3: Nur adjustierte Assoziation und p-Wert; keine Ereignisse/Total pro Arm.
- Slot 4: Nur adjustierte HR/Modellresultate; keine armweisen Rohdaten oder Ereigniszahlen.

---

### PMC13626740 — Mechanisms of change in depression therapy

- Titel: Mechanisms of Change in the Treatment of Depression: On the Role of Attachment, Reappraisal and Suppression
- Design: Sekundäranalyse der OPTIMA-RCT; CBT 101 / ST 97; T3 nach 7 Wochen
- Arm-N: Intervention 101 / Kontrolle 97 / randomisiert 198 / analysiert 82/66 bei T3
- Assistierte Eignung: **likely_eligible_two_arms**
- Vorprüfung: Zwei randomisierte Arme, Arm-N und vier kontinuierliche Outcomes mit N/Mean/SD zu Post-Treatment T3.

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Arm-N und analysiertes n bestätigt (4 unabhängig, 0 überlappend, 0 nicht verwendbar)
- [ ] Quellen und Werte pro Slot bestätigt
- [ ] Überlappungsklasse pro Slot bestätigt

| Geprüft | Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle | Befund |
|---|---|---|---|---|---|---|---|---|---|
| [ ] | 1 | Depressive symptoms (BDI-II), post-treatment T3 | continuous | n=82, 14.80 (8.99) | n=66, 18.00 (10.97) | ja | independent | Tabelle 1, Zeile 16 | offen |
| [ ] | 2 | Expressive suppression (ERQ), post-treatment T3 | continuous | n=79, 3.53 (1.47) | n=60, 3.73 (1.45) | ja | independent | Tabelle 1, Zeile 17 | offen |
| [ ] | 3 | Cognitive reappraisal (ERQ), post-treatment T3 | continuous | n=79, 4.12 (1.47) | n=60, 3.89 (1.10) | ja | independent | Tabelle 1, Zeile 18 | offen |
| [ ] | 4 | Avoidant attachment (RSQ fear of closeness), post-treatment T3 | continuous | n=79, 2.57 (1.00) | n=59, 2.73 (0.89) | ja | independent | Tabelle 1, Zeile 19 | offen |

**Vorprüfungsnotizen:**

- Slot 1: Post-treatment T3 (Woche 7); verfügbares n.
- Slot 2: Post-treatment T3 (Woche 7); verfügbares n.
- Slot 3: Post-treatment T3 (Woche 7); verfügbares n.
- Slot 4: Post-treatment T3 (Woche 7); verfügbares n.

---

### PMC13688066 — NCCT markers and andexanet response

- Titel: Non‐contrast CT Markers of Hematoma Expansion and Andexanet Response in Factor Xa Inhibitor‐Associated Intracerebral Hemorrhage: An Analysis from ANNEXa‐I Trial
- Design: Post-hoc-Sekundäranalyse der ANNEXa-I-RCT; 434 von 530 ITT mit Bildgebung; Andexanet vs. Usual Care
- Arm-N: Intervention nicht berichtet / Kontrolle nicht berichtet / randomisiert 530 / analysiert 434
- Assistierte Eignung: **uncertain_post_hoc_no_arm_counts**
- Vorprüfung: Randomisierte Arme sind im Design berichtet, aber die HE-Outcomes liegen nur als Gesamtfrequenz, Subgruppeninteraktionen oder adjustierte Assoziationen vor; keine armweisen Ereignisse/Total.

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Arm-N und analysiertes n bestätigt (0 unabhängig, 0 überlappend, 4 nicht verwendbar)
- [ ] Quellen und Werte pro Slot bestätigt
- [ ] Überlappungsklasse pro Slot bestätigt

| Geprüft | Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle | Befund |
|---|---|---|---|---|---|---|---|---|---|
| [ ] | 1 | Significant hematoma expansion (>=12.5 ml or >=35%) | binary | - | - | nein | not_usable | Results-Text | offen |
| [ ] | 2 | Severe hematoma expansion (>=12.5 ml or >=66%) | binary | - | - | nein | not_usable | Results-Text | offen |
| [ ] | 3 | HE in hypodensity subgroup | binary | - | - | nein | not_usable | Results-Text | offen |
| [ ] | 4 | HE in blend-sign subgroup | binary | - | - | nein | not_usable | Results-Text | offen |

**Vorprüfungsnotizen:**

- Slot 1: Gesamtpopulation 138/434 (31.8%); keine armweisen Ereigniszahlen im Text.
- Slot 2: Nur definiertes Outcome; keine armweisen Ereigniszahlen im Text.
- Slot 3: Nur absolute Reduktion 19.5% vs. 8.0% berichtet; keine Ereigniszahlen.
- Slot 4: Nur Interaktions-OR 0.03 (0.00-0.29) vs. 0.60 (0.38-0.96), p=0.01; keine Ereigniszahlen.

---

### PMC13519320 — Dupilumab and COPD exacerbation resource use

- Titel: Dupilumab in chronic obstructive pulmonary disease: a pooled analysis of emergency department visits, hospital admissions, and systemic corticosteroid use
- Design: Post-hoc-gepoolte Analyse von BOREAS und NOTUS; Dupilumab 938 / Placebo 936; 52 Wochen
- Arm-N: Intervention 938 / Kontrolle 936 / randomisiert 1874 / analysiert 1874 / Trials 2
- Assistierte Eignung: **uncertain_pooled_two_trials**
- Vorprüfung: Zwei RCTs mit zwei Armen und Ereigniszahlen, aber die Analyse poolt BOREAS und NOTUS; die vier Outcomes überlappen sich und sind nicht als vier unabhängige Outcomes zu zählen.

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Arm-N und analysiertes n bestätigt (1 unabhängig, 3 überlappend, 0 nicht verwendbar)
- [ ] Quellen und Werte pro Slot bestätigt
- [ ] Überlappungsklasse pro Slot bestätigt

| Geprüft | Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle | Befund |
|---|---|---|---|---|---|---|---|---|---|
| [ ] | 1 | Patients with >=1 ED visit/hospital admission, 52 weeks | binary | 50/938 | 80/936 | ja | independent | Results-Text | offen |
| [ ] | 2 | Patients with >=1 severe exacerbation, 52 weeks | binary | 41/938 | 60/936 | ja | overlapping_subgroup | Results-Text | offen |
| [ ] | 3 | Patients with systemic corticosteroid use, 52 weeks | binary | 315/938 | 366/936 | ja | overlapping_subgroup | Results-Text | offen |
| [ ] | 4 | Patients with ICU admission, 52 weeks | binary | 3/938 | 7/936 | ja | overlapping_subgroup | Results-Text | offen |

**Vorprüfungsnotizen:**

- Slot 1: Gepoolte ITT-Population; Ereignisse/Total aus Text.
- Slot 2: Subgruppe mit Überlappung zu Slot 1; exakte Patientenzahlen aus Baseline-Charakteristik.
- Slot 3: Überlappt mit Exazerbations-Outcomes; Ereignisse/Total aus Text.
- Slot 4: Subgruppe der Hospitalisierten; überlappt mit Slot 1 und Slot 2.

---

### PMC13590641 — Aumolertinib plus radiotherapy in stage III NSCLC

- Titel: Induction and concurrent aumolertinib with radiotherapy for EGFR-mutated stage III NSCLC: results of phase III ADVANCE trial and real-world validation
- Design: Phase-III-ADVANCE-RCT, open-label, vorzeitig beendet; Experiment 24 / Kontrolle 19; plus Real-World-Kohorte
- Arm-N: Intervention 24 / Kontrolle 19 / randomisiert 43 / analysiert 43
- Assistierte Eignung: **uncertain_safety_only_early_stopped**
- Vorprüfung: Zwei randomisierte Arme und Arm-N sind berichtet; vier Sicherheitsoutcomes mit Events/Total sind extrahierbar, armweise Wirksamkeitsdaten liegen jedoch nicht in vergleichbarer Form vor. Open-label und vorzeitig beendet.

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Arm-N und analysiertes n bestätigt (1 unabhängig, 3 überlappend, 0 nicht verwendbar)
- [ ] Quellen und Werte pro Slot bestätigt
- [ ] Überlappungsklasse pro Slot bestätigt

| Geprüft | Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle | Befund |
|---|---|---|---|---|---|---|---|---|---|
| [ ] | 1 | Any adverse event, any grade | binary | 23/24 | 15/19 | ja | independent | Tabelle 3, Zeile 3 | offen |
| [ ] | 2 | Neutropenia, any grade | binary | 4/24 | 10/19 | ja | overlapping_subgroup | Tabelle 3, Zeile 10 | offen |
| [ ] | 3 | Nausea, any grade | binary | 0/24 | 5/19 | ja | overlapping_subgroup | Tabelle 3, Zeile 6 | offen |
| [ ] | 4 | Rash, any grade | binary | 6/24 | 1/19 | ja | overlapping_subgroup | Tabelle 3, Zeile 5 | offen |

**Vorprüfungsnotizen:**

- Slot 1: Any grade; Sammeloutcome. Tabelle führt zusätzlich Grade 1-4.
- Slot 2: Any grade; spezifische AE, überlappt mit dem Sammeloutcome in Slot 1.
- Slot 3: Any grade; spezifische AE, überlappt mit dem Sammeloutcome in Slot 1.
- Slot 4: Any grade; spezifische AE, überlappt mit dem Sammeloutcome in Slot 1.

---

### PMC13596784 — MATILDA feasibility trial

- Titel: Implementing the MATILDA intervention to enhance community participation for older adults with intellectual disability: A feasibility randomised controlled trial and RE-AIM guided process evaluation
- Design: Zweiarmige randomisierte Machbarkeitsstudie; MATILDA 28 / aktive Kontrolle 29; 6 und 12 Monate
- Arm-N: Intervention 28 / Kontrolle 29 / randomisiert 57 / analysiert 52 mit 6-Monats-Daten; 25 MATILDA nach Tod/Withdrawal
- Assistierte Eignung: **uncertain_feasibility_no_timepoint_n**
- Vorprüfung: Zwei randomisierte Arme und Mean/SD zu 6 Monaten sind berichtet, aber das armweise analysierte n pro Zeitpunkt fehlt; die Studie ist eine nicht gepowerte Machbarkeitsstudie.

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Arm-N und analysiertes n bestätigt (0 unabhängig, 0 überlappend, 4 nicht verwendbar)
- [ ] Quellen und Werte pro Slot bestätigt
- [ ] Überlappungsklasse pro Slot bestätigt

| Geprüft | Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle | Befund |
|---|---|---|---|---|---|---|---|---|---|
| [ ] | 1 | Glasgow Anxiety Inventory at 6 months | continuous | n=nicht berichtet, 18.1 (8.3) | n=nicht berichtet, 17.1 (9.1) | nein | not_usable | Tabelle 4, Zeile 10 | offen |
| [ ] | 2 | WHO (Five) Well-Being Index at 6 months | continuous | n=nicht berichtet, 16.4 (6.2) | n=nicht berichtet, 15.3 (6.2) | nein | not_usable | Tabelle 4, Zeile 16 | offen |
| [ ] | 3 | WHOQOL-DIS physical health at 6 months | continuous | n=nicht berichtet, 3.8 (0.5) | n=nicht berichtet, 3.7 (0.5) | nein | not_usable | Tabelle 4, Zeile 5 | offen |
| [ ] | 4 | WHOQOL-DIS psychological health at 6 months | continuous | n=nicht berichtet, 3.4 (0.5) | n=nicht berichtet, 3.2 (0.5) | nein | not_usable | Tabelle 4, Zeile 6 | offen |

**Vorprüfungsnotizen:**

- Slot 1: Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation.
- Slot 2: Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation.
- Slot 3: Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation.
- Slot 4: Mean/SD aus Tabelle; armweises analysiertes n pro Zeitpunkt nicht berichtet. N randomisiert 28/29; keine Imputation.

---

### PMC13574397 — Cost-effectiveness of omeprazole for esophageal stricture

- Titel: Cost-effectiveness analysis of omeprazole for preventing esophageal stricture in patients with Zargar grade 2b and 3a corrosive esophageal injuries
- Design: Kosteneffektivitätsanalyse der vorausgegangenen RCT; Omeprazol 10 / Standard 10; 4 Wochen
- Arm-N: Intervention 10 / Kontrolle 10 / randomisiert 20 / analysiert 20
- Assistierte Eignung: **eligible_single_binary_outcome**
- Vorprüfung: Zwei randomisierte Arme und ein binäres klinisches Outcome mit Ereignissen/Total; die ökonomischen Outcomes sind ohne SD oder numerischen ICER nicht als Mean/SD extrahierbar.

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Arm-N und analysiertes n bestätigt (1 unabhängig, 0 überlappend, 3 nicht verwendbar)
- [ ] Quellen und Werte pro Slot bestätigt
- [ ] Überlappungsklasse pro Slot bestätigt

| Geprüft | Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Unabhängigkeit | Quelle | Befund |
|---|---|---|---|---|---|---|---|---|---|
| [ ] | 1 | Esophageal stricture at 4 weeks | binary | 2/10 | 7/10 | ja | independent | Results-Text | offen |
| [ ] | 2 | Total cost per case, provider perspective (THB) | continuous | n=10, 12103.32 (SD nicht berichtet) | n=10, 16745.62 (SD nicht berichtet) | nein | not_usable | Tabelle 2, Zeile 3 | offen |
| [ ] | 3 | Total cost per case, patient perspective (THB) | continuous | n=10, 7652.60 (SD nicht berichtet) | n=10, 13129.20 (SD nicht berichtet) | nein | not_usable | Tabelle 2, Zeile 7 | offen |
| [ ] | 4 | Incremental cost-effectiveness ratio (ICER) | not_available | - | - | nein | not_usable | Tabellenverweis (ICER) | offen |

**Vorprüfungsnotizen:**

- Slot 1: Ereignisse/Total aus Text; 20% und 70% nicht rekonstruiert.
- Slot 2: Kosten pro Fall; kein SD berichtet.
- Slot 3: Kosten pro Fall; kein SD berichtet.
- Slot 4: Standard care ist dominiert; kein numerischer ICER mit Unsicherheit berichtet.

---

## C. Abschluss der menschlichen Runde

- [ ] alle 36 Slot-Zeilen bearbeitet
- [ ] alle Quellen als geprüft markiert
- [ ] alle Überlappungen bestätigt oder begründet korrigiert
- [ ] alle nicht verwendbaren Slots als leer bestätigt
- [ ] Zähler nach der Prüfung erneut abgeglichen
- [ ] keine Werte ohne Quelle ergänzt
- [ ] finale Entscheidungen separat dokumentiert

## D. Nicht Bestandteil dieser Checkliste

- Keine neuen Outcome-Werte.
- Keine Umrechnung von Median/IQR in Mean/SD.
- Keine nachträgliche Armzusammenführung.
- Keine automatische finale Eignungsentscheidung.
