# Assistierte Volltextprüfung: Batch 1 (fünf hohe Prioritäten)

Stand: 2026-11-13
Status: **ASSISTIERTE PRÜFUNG; MENSCHLICHE BESTÄTIGUNG OFFEN**.

Keine finale Eignungsentscheidung, keine Übernahme in die Extraktionsvorlage,
kein Modelllauf, kein Netzabruf. Werte sind aus berichteten Tabellenzeilen
transkribiert; nicht verwendbare oder fehlende Outcomes bleiben leer.

## Übersicht

| PMC | Design | Arm-N | Assistierte Eignung | Verwendbar |
|---|---|---|---|---:|
| [PMC13591290](https://pmc.ncbi.nlm.nih.gov/articles/PMC13591290/) | Sekundäranalyse eines zweiarmigen, placebokontrollierten RCT; 102 randomisiert, 98 analysiert | Intervention 49 / Kontrolle 49 / randomisiert 102 / analysiert 98 | uncertain_no_overall_outcome_table | 0/4 |
| [PMC13590555](https://pmc.ncbi.nlm.nih.gov/articles/PMC13590555/) | Sekundäranalyse des ERASE-RCT; zwei Arme, 1:1 randomisiert; 26 HIIT und 26 Usual Care randomisiert | Intervention 26 / Kontrolle 26 / randomisiert 52 / analysiert 24/25 für die ausgewählten Blutbild-Outcomes | likely_eligible | 4/4 |
| [PMC13587833](https://pmc.ncbi.nlm.nih.gov/articles/PMC13587833/) | Sekundäranalyse eines RCT; GPM vs. TAU; 50 Klienten, 27 GPM und 23 TAU; 29 gesunde Kontrollen nicht Teil des randomisierten Vergleichs | Intervention 27 / Kontrolle 23 / randomisiert 50 / analysiert 50 | likely_eligible_three_outcomes | 3/4 |
| [PMC13635505](https://pmc.ncbi.nlm.nih.gov/articles/PMC13635505/) | Sekundäranalyse eines zweiarmigen RCT; Intervention 150, Kontrolle 153; funktionale Response als binäres Outcome | Intervention 150 / Kontrolle 153 / randomisiert 303 / analysiert 303 | eligible_with_single_binary_outcome | 1/4 |
| [PMC13624796](https://pmc.ncbi.nlm.nih.gov/articles/PMC13624796/) | Post-hoc-Analyse gepoolter Individualdaten aus CANVAS und CREDENCE; zwei RCTs, Canagliflozin vs. Placebo; 3602 Placebo und 5012 Canagliflozin | Intervention 5012 / Kontrolle 3602 / randomisiert 8614 / analysiert 8614 / Trials 2 | uncertain_pooled_two_trials | 4/4 |

Verwendbare Outcomes: **12/20**; nicht verwendbar oder nicht berichtet: **8/20**.

## PMC13591290 — Blinding in a placebo-controlled manual-therapy RCT

- Titel: Successful Blinding or Wishful Thinking? A Secondary Analysis of a Randomised Controlled Trial of Manual Therapy
- Design: Sekundäranalyse eines zweiarmigen, placebokontrollierten RCT; 102 randomisiert, 98 analysiert
- Arm-N: Intervention 49 / Kontrolle 49 / randomisiert 102 / analysiert 98
- Assistierte Eignung: **uncertain_no_overall_outcome_table**
- Begründung: Zwei parallele Arme und Arm-N sind berichtet, aber die klinischen Outcomes liegen nur stratifiziert nach Blinding-Status vor; kein Gesamtkontrast der randomisierten Arme in der Tabelle.
- Risiken/Hinweise: secondary analysis, klinische Outcomes nur nach Blinding-Status stratifiziert

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Quelle |
|---:|---|---|---|---|---|---|
| 1 | Pain intensity at 4 weeks, blinded participants | continuous | n=11, 19.5 (11.3) | n=35, 22.5 (21.1) | nein | Stratifizierte Blinding-Untergruppe, kein randomisierter Gesamtarm-Vergleich. |
| 2 | Pain intensity at 4 weeks, unblinded participants | continuous | n=38, 15.5 (14.7) | n=14, 42.4 (23.8) | nein | Stratifizierte Blinding-Untergruppe, kein randomisierter Gesamtarm-Vergleich. |
| 3 | Unique participants with adverse events, blinded participants | binary | 9/11 | 32/35 | nein | Stratifizierte Blinding-Untergruppe; keine armübergreifende Ereignisrate. |
| 4 | Unique participants with adverse events, unblinded participants | binary | 28/38 | 10/14 | nein | Stratifizierte Blinding-Untergruppe; keine armübergreifende Ereignisrate. |

### Quellen

- Slot 1: `TABLE 3 | Treatment effects and adverse events. | Arms: Active SMT / Placebo SMT / Effect (95% CI) | Pain intensity at 4 weeks, mean (SD), NRS | 19.5 (11.3) | 22.5 (21.1) | −3 (−12.7 to 6.7) | Context: Blinded participants a | (n = 11) | (n = 35) |`
- Slot 2: `TABLE 3 | Treatment effects and adverse events. | Arms: Active SMT / Placebo SMT / Effect (95% CI) | Pain intensity at 4 weeks, mean (SD), NRS | 15.5 (14.7) | 42.4 (23.8) | −26.9 (−40.2 to −13.6) | Context: Unblinded participants c | (n = 38) | (n = 14) |`
- Slot 3: `TABLE 3 | Treatment effects and adverse events. | Arms: Active SMT / Placebo SMT / Effect (95% CI) | Unique participants with AEs, No. (%) | 9 (81.8) | 32 (91.4) | −9 (−34 to 15) b | Context: Blinded participants a | (n = 11) | (n = 35) |`
- Slot 4: `TABLE 3 | Treatment effects and adverse events. | Arms: Active SMT / Placebo SMT / Effect (95% CI) | Unique participants with AEs, No. (%) | 28 (73.7) | 10 (71.4) | 3 (−25 to 30) b | Context: Unblinded participants c | (n = 38) | (n = 14) |`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13590555 — Immune-cell changes after HIIT in prostate cancer

- Titel: Changes in circulating immune cells and cytokines after high-intensity aerobic exercise in patients with prostate cancer undergoing active surveillance from the ERASE randomized controlled trial
- Design: Sekundäranalyse des ERASE-RCT; zwei Arme, 1:1 randomisiert; 26 HIIT und 26 Usual Care randomisiert
- Arm-N: Intervention 26 / Kontrolle 26 / randomisiert 52 / analysiert 24/25 für die ausgewählten Blutbild-Outcomes
- Assistierte Eignung: **likely_eligible**
- Begründung: Zwei parallele Arme, Randomisierung 1:1, berichtete Arm-N und vier kontinuierliche Outcomes mit N/Mean/SD zu Baseline und Postintervention.
- Risiken/Hinweise: secondary analysis

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Quelle |
|---:|---|---|---|---|---|---|
| 1 | White blood cell count (10^9/L), postintervention | continuous | n=24, 6.33 (1.32) | n=25, 5.78 (1.17) | ja | Postintervention; Baselinewerte in derselben Tabelle. |
| 2 | Neutrophils (10^9/L), postintervention | continuous | n=24, 3.75 (1.01) | n=25, 3.23 (0.82) | ja | Postintervention; Baselinewerte in derselben Tabelle. |
| 3 | Lymphocytes (10^9/L), postintervention | continuous | n=24, 1.61 (0.57) | n=25, 1.67 (0.64) | ja | Postintervention; Baselinewerte in derselben Tabelle. |
| 4 | Monocytes (10^9/L), postintervention | continuous | n=24, 0.67 (0.29) | n=25, 0.58 (0.29) | ja | Postintervention; Baselinewerte in derselben Tabelle. |

### Quellen

- Slot 1: `Table 2 | Effects of high-intensity interval training on complete blood count with differential in men with prostate cancer under active surveillance. | Arms: Baseline / Postintervention / Within-group mean change / Adjusted between-group difference | White blood cell count (10^9/L), postintervention | Intervention: HIIT (n=24) | 6.73 (1.60) | 6.33 (1.32) | -0.40 (-0.76, -0.04) | 0.029 | -0.08 (-0.52, 0.37) | 0.73 | Control: UC (n=25) | 5.95 (1.13) | 5.78 (1.17) | -0.17 (-0.49, 0.14) | 0.27 |  |`
- Slot 2: `Table 2 | Effects of high-intensity interval training on complete blood count with differential in men with prostate cancer under active surveillance. | Arms: Baseline / Postintervention / Within-group mean change / Adjusted between-group difference | Neutrophils (10^9/L), postintervention | Intervention: HIIT (n=24) | 4.03 (0.99) | 3.75 (1.01) | -0.28 (-0.58, 0.03) | 0.073 | 0.07 (-0.33, 0.47) | 0.73 | Control: UC (n=25) | 3.43 (0.84) | 3.23 (0.82) | -0.20 (-0.48, 0.07) | 0.14 |  |`
- Slot 3: `Table 2 | Effects of high-intensity interval training on complete blood count with differential in men with prostate cancer under active surveillance. | Arms: Baseline / Postintervention / Within-group mean change / Adjusted between-group difference | Lymphocytes (10^9/L), postintervention | Intervention: HIIT (n=24) | 1.78 (0.66) | 1.61 (0.57) | -0.17 (-0.40, 0.06) | 0.14 | -0.11 (-0.38, 0.17) | 0.44 | Control: UC (n=25) | 1.67 (0.58) | 1.67 (0.64) | -0.02 (-0.21, 0.17) | 0.83 |  |`
- Slot 4: `Table 2 | Effects of high-intensity interval training on complete blood count with differential in men with prostate cancer under active surveillance. | Arms: Baseline / Postintervention / Within-group mean change / Adjusted between-group difference | Monocytes (10^9/L), postintervention | Intervention: HIIT (n=24) | 0.67 (0.19) | 0.67 (0.29) | 0.00 (-0.09, 0.10) | 0.93 | -0.05 (-0.20, 0.11) | 0.55 | Control: UC (n=25) | 0.55 (0.16) | 0.58 (0.29) | 0.04 (-0.07, 0.14) | 0.50 |  |`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13587833 — Self-contempt and emotion processing in BPD psychotherapy

- Titel: Undoing Self‐Contempt in Borderline Personality Disorder: A Controlled Test of Change in Emotion Processing in Psychotherapy
- Design: Sekundäranalyse eines RCT; GPM vs. TAU; 50 Klienten, 27 GPM und 23 TAU; 29 gesunde Kontrollen nicht Teil des randomisierten Vergleichs
- Arm-N: Intervention 27 / Kontrolle 23 / randomisiert 50 / analysiert 50
- Assistierte Eignung: **likely_eligible_three_outcomes**
- Begründung: Zwei randomisierte Klientenarme, Arm-N und drei auswertbare Outcomes zu Time 2; ein viertes unabhängiges Outcome ist in den Tabellen nicht berichtet.
- Risiken/Hinweise: secondary analysis, kleine Stichprobe, nur drei unabhängige Outcomes

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Quelle |
|---:|---|---|---|---|---|---|
| 1 | Self-contempt intensity at Time 2 | continuous | n=27, 3.81 (0.92) | n=23, 4.22 (0.67) | ja | Time 2; Time 1 ist Baseline und nicht als unabhängiges Outcome ausgewählt. |
| 2 | Presence of self-compassion at Time 2 | binary | 14/27 | 0/23 | ja | Tabellenwerte sind Anzahlen; keine Prozentrekonstruktion. |
| 3 | Presence of assertive anger at Time 2 | binary | 19/27 | 2/23 | ja | Tabellenwerte sind Anzahlen; keine Prozentrekonstruktion. |
| 4 | Fourth independent outcome | not_available | - | - | nein | Kein viertes unabhängiges Outcome in den Tabellen; State Self-Esteem wird nur im Text erwähnt, ohne armweise Werte. |

### Quellen

- Slot 1: `TABLE 1B | Self‐contempt for clients undergoing GPM and TAU (N = 50). | Arms: GPM (n = 27) Mean (SD) / TAU (n = 23) Mean (SD) / t‐test / p | Time 2 | 3.81 (0.92) | 4.22 (0.67) | 1.74 | 0.04`
- Slot 2: `TABLE 2B | Presence of self‐compassion for clients undergoing GPM and TAU (N = 50). | Arms: GPM (n = 27) Proportion / TAU (n = 23) Proportion / Chi‐square / p | Time 2 | 14 | 0 | 16.56 | 0.00+`
- Slot 3: `TABLE 3B | Presence of assertive anger for clients undergoing GPM and TAU (N = 50). | Arms: GPM (n = 27) Proportion / TAU (n = 23) Proportion / Chi‐square / p | Time 2 | 19 | 2 | 19.39 | 0.00+`
- Slot 4: keine armweise Quelle berichtet

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13635505 — Functional response to in-hospital exercise

- Titel: Metabolic reserve: baseline cholesterol as a predictor and modulator of response to in-hospital exercise in older adults
- Design: Sekundäranalyse eines zweiarmigen RCT; Intervention 150, Kontrolle 153; funktionale Response als binäres Outcome
- Arm-N: Intervention 150 / Kontrolle 153 / randomisiert 303 / analysiert 303
- Assistierte Eignung: **eligible_with_single_binary_outcome**
- Begründung: Zwei parallele Arme und ein berichtetes binäres Outcome mit Events/Total; die weiteren funktionalen Werte liegen nur als Median/IQR oder Regressionsmodelle vor.
- Risiken/Hinweise: secondary analysis, nur ein auswertbares binäres Outcome, kontinuierliche SPPB-Werte nicht als Mean/SD berichtet

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Quelle |
|---:|---|---|---|---|---|---|
| 1 | Functional response (SPPB increase >= 1 point), discharge | binary | 128/150 | 57/153 | ja | Events/Total aus Tabelle; 85.3% und 37.3% nicht als Ereigniszahlen rekonstruiert. |
| 2 | SPPB change, continuous | not_available | - | - | nein | Kein armweiser Mean/SD für SPPB zu Entlassung berichtet; Baseline nur Median/IQR. |
| 3 | Total cholesterol, continuous | not_available | - | - | nein | Baseline-Prädiktor, kein Behandlungsoutcome; nur Median/IQR und Regressions-OR. |
| 4 | Additional functional outcome | not_available | - | - | nein | Kein weiteres armweises Outcome mit N/Mean/SD oder Events/Total in den Tabellen. |

### Quellen

- Slot 1: `Table 1 | Baseline clinical and nutritional characteristics of the study population. Categorical variables were compared using the chi-square test. Continuous variables are presented as median [interquartile range] and were compared, excluding age, using the Mann–Whitney U test. Age was compared using Student’s T-test. IQR, interquartile range; MNA, Mini Nutritional Assessment; CIRS-G, Cumulative Illness Rating Scale for Geriatrics; SPPB, Short Physical Performance Battery; CRP, C-Reactive Protein. | Arms: Intervention (n = 150) Median (IQR) / Control (n = 153) Median (IQR) / p | Functional response, n (%) | 128 (85.3%) | 57 (37.3%) | <0.001`
- Slot 2: keine armweise Quelle berichtet
- Slot 3: keine armweise Quelle berichtet
- Slot 4: keine armweise Quelle berichtet

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## PMC13624796 — Dipstick findings and UTI risk with canagliflozin

- Titel: Urinary dipstick findings and UTI risk with SGLT2 inhibitors: a post-hoc analysis of the CANVAS and CREDENCE trials
- Design: Post-hoc-Analyse gepoolter Individualdaten aus CANVAS und CREDENCE; zwei RCTs, Canagliflozin vs. Placebo; 3602 Placebo und 5012 Canagliflozin
- Arm-N: Intervention 5012 / Kontrolle 3602 / randomisiert 8614 / analysiert 8614 / Trials 2
- Assistierte Eignung: **uncertain_pooled_two_trials**
- Begründung: Zwei parallele Arme mit Ereigniszahlen, aber die Analyse poolt zwei separate RCTs und mehrere Subgruppen; kein einzelner RCT und keine unabhängigen vier Outcomes.
- Risiken/Hinweise: post hoc, pooled analysis of two RCTs, subgroup overlap, UTI data truncated in CANVAS

| Slot | Outcome | Typ | Intervention | Kontrolle | Verwendbar | Quelle |
|---:|---|---|---|---|---|---|
| 1 | First UTI, whole population | binary | 550/5012 | 353/3602 | ja | Gepoolte RCT-Population; Ereignisse/Total, keine Unabhängigkeit zwischen den Subgruppen. |
| 2 | First UTI, LE normal | binary | 420/4522 | 237/3171 | ja | LE-Subgruppe; überlappt mit Slot 1 und ist kein unabhängiges Outcome. |
| 3 | First UTI, LE abnormal | binary | 130/490 | 116/431 | ja | LE-Subgruppe; überlappt mit Slot 1 und ist kein unabhängiges Outcome. |
| 4 | First UTI, NIT abnormal | binary | 45/173 | 34/129 | ja | NIT-Subgruppe; überlappt mit Slot 1 und ist kein unabhängiges Outcome. |

### Quellen

- Slot 1: `Table 3: | Effects of canagliflozin versus placebo on UTI outcomes stratified by baseline dipstick results. | Arms: Placebo / Canagliflozin /  / P interaction | Whole | 353/3602 (9.8) | 41.4 | 550/5012 (11.0) | 41.9 | 1.07 (0.93–1.22) |`
- Slot 2: `Table 3: | Effects of canagliflozin versus placebo on UTI outcomes stratified by baseline dipstick results. | Arms: Placebo / Canagliflozin /  / P interaction | Normal | 237/3171 (7.5) | 30.9 | 420/4522 (9.2) | 34.8 | 1.17 (1.00–1.38) | .20`
- Slot 3: `Table 3: | Effects of canagliflozin versus placebo on UTI outcomes stratified by baseline dipstick results. | Arms: Placebo / Canagliflozin /  / P interaction | Abnormal | 116/431 (26.9) | 132.8 | 130/490 (26.5) | 122.3 | 0.94 (0.73–1.21) |`
- Slot 4: `Table 3: | Effects of canagliflozin versus placebo on UTI outcomes stratified by baseline dipstick results. | Arms: Placebo / Canagliflozin /  / P interaction | Abnormal | 34/129 (26.4) | 132.2 | 45/173 (26.0) | 118.0 | 0.92 (0.59–1.43) |`

### Menschliche Prüfung

- [ ] zwei parallele Arme bestätigt
- [ ] Randomisierung bestätigt
- [ ] keine Armzusammenführung
- [ ] Outcomes und Quellen bestätigt
- [ ] finale Entscheidung gesetzt

---

## Konsequenz

Nur `PMC13590555` liefert vier direkt verwendbare kontinuierliche Outcomes.
`PMC13587833` liefert drei verwendbare Outcomes, `PMC13635505` nur ein
binäres Outcome. `PMC13591290` enthält klinische Werte nur stratifiziert
nach Blinding-Status; `PMC13624796` ist eine gepoolte Analyse zweier RCTs
mit überlappenden Subgruppen. Diese beiden Fälle sind ohne menschliche
Entscheidung nicht als unabhängige RCT-Datensätze zu übernehmen.

Kein Modelllauf, kein Netzabruf, keine finale Auswahl.
