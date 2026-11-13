# Volltext-Prüfvorlage: 36 vorläufige P0-Einschlüsse

Stand: 2026-11-13
Status: **VOLLTEXT-PRÜFUNG OFFEN**; 30/36 XML lokal verfügbar; sechs Reservefälle nicht abgerufen; kein Gate-Pass, keine endgültige Holdout-Auswahl.

## Regeln

- Genau zwei parallele Arme bestätigen; keine Armzusammenführung.
- Nur berichtete Werte eintragen. Fehlende Werte bleiben leer.
- Keine Schätzung, keine Imputation, keine Umrechnung von SE/CI in SD.
- Kontinuierlich: N, Mean, SD; bei Veränderung zusätzlich Mean change und SD change.
- Binär: Events und Total pro Arm; keine Rekonstruktion aus Prozentwerten.
- Beleg mit Tabelle/Seite und wörtlichem Zitat; keine Paraphrase.
- Reviewer, Datum und finale Entscheidung setzen: `einschluss`, `ausschluss` oder `offen`.

Die maschinenlesbare Langform steht in `fulltext_extraction_template_v1.csv`: pro Artikel
4 Outcome-Slots mit je einer Interventions- und Kontrollzeile.

## 1. PMC13519320 — Dupilumab in chronic obstructive pulmonary disease: a pooled analysis of emergency department visits, hospital admissions, and systemic corticosteroid use.

- Quelle: [PMC13519320](https://pmc.ncbi.nlm.nih.gov/articles/PMC13519320/) · DOI `10.1093/ajrccm/aamag227`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13519320.xml` · SHA-256 `9d5dc0a092efd8e311848050bb6654d58d27a1ec290bd34b8a173456748f2958` · 119110 Bytes
- Journal/Jahr: American journal of respiratory and critical care medicine (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **hoch**
- Offener Zweifel: Gepoolte zwei RCTs; Exazerbations-Ereignisse pro Arm pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 2. PMC13574397 — Cost-effectiveness analysis of omeprazole for preventing esophageal stricture in patients with Zargar grade 2b and 3a corrosive esophageal injuries: A trial-based economic evaluation.

- Quelle: [PMC13574397](https://pmc.ncbi.nlm.nih.gov/articles/PMC13574397/) · DOI `10.1097/md.0000000000050701`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13574397.xml` · SHA-256 `8852c3c8f0ca3d81e98e9e0334d0a7b98ec066fcb0ebc304abed7b7d1db5a9dc` · 53002 Bytes
- Journal/Jahr: Medicine (2026)
- Screening: vorläufiger Einschluss (I04); Priorität **hoch**
- Offener Zweifel: Sehr klein n=20; Striktur 2/10 vs. 7/10 und oekonomische Zusatzanalyse pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 3. PMC13587833 — Undoing Self-Contempt in Borderline Personality Disorder: A Controlled Test of Change in Emotion Processing in Psychotherapy.

- Quelle: [PMC13587833](https://pmc.ncbi.nlm.nih.gov/articles/PMC13587833/) · DOI `10.1002/cpp.70335`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13587833.xml` · SHA-256 `9be06f3c6b439783305c97acb22f22bcef3a470e7cce1ac06fbee0e89580377d` · 141078 Bytes
- Journal/Jahr: Clinical psychology & psychotherapy (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **hoch**
- Offener Zweifel: Emotionsprozessmasse, keine klassischen Armwerte; Eignung pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 4. PMC13590555 — Changes in circulating immune cells and cytokines after high-intensity aerobic exercise in patients with prostate cancer undergoing active surveillance from the ERASE randomized controlled trial.

- Quelle: [PMC13590555](https://pmc.ncbi.nlm.nih.gov/articles/PMC13590555/) · DOI `10.3389/fimmu.2026.1923463`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13590555.xml` · SHA-256 `915625142187c49278705f40036360c85b6f2b391250964872d69f7e53e09b7c` · 157251 Bytes
- Journal/Jahr: Frontiers in immunology (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **hoch**
- Offener Zweifel: Sekundaeranalyse; Immunmarker-Armwerte/SD und klinische Relevanz pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 5. PMC13590641 — Induction and concurrent aumolertinib with radiotherapy for EGFR-mutated stage III NSCLC: results of phase III ADVANCE trial and real-world validation.

- Quelle: [PMC13590641](https://pmc.ncbi.nlm.nih.gov/articles/PMC13590641/) · DOI `10.1038/s41392-026-02891-2`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13590641.xml` · SHA-256 `cbf7dd52c2b90d4d7c7db1479b88c8ba237d32c35826420e6546ca8c2b95a75e` · 136084 Bytes
- Journal/Jahr: Signal transduction and targeted therapy (2026)
- Screening: vorläufiger Einschluss (I03); Priorität **hoch**
- Offener Zweifel: Frueh beendet, n=43; PFS/OS und Zensierung pro Arm pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 6. PMC13591290 — Successful Blinding or Wishful Thinking? A Secondary Analysis of a Randomised Controlled Trial of Manual Therapy.

- Quelle: [PMC13591290](https://pmc.ncbi.nlm.nih.gov/articles/PMC13591290/) · DOI `10.1002/ejp.70370`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13591290.xml` · SHA-256 `4e25807231375ab3724274426345a2dd90814e91e5a7323349c119074c51ae23` · 103180 Bytes
- Journal/Jahr: European journal of pain (London, England) (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **hoch**
- Offener Zweifel: Blinding ist primaer; klinischer Schmerzendpunkt und Armwerte unklar.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 7. PMC13596784 — Implementing the MATILDA intervention to enhance community participation for older adults with intellectual disability: A feasibility randomised controlled trial and RE-AIM guided process evaluation.

- Quelle: [PMC13596784](https://pmc.ncbi.nlm.nih.gov/articles/PMC13596784/) · DOI `10.1371/journal.pone.0341940`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13596784.xml` · SHA-256 `694b49f81d303ee8db3d4db530f047fab9983a0e5c8099185a6d3eb714c9ec4a` · 180538 Bytes
- Journal/Jahr: PloS one (2026)
- Screening: vorläufiger Einschluss (I01); Priorität **hoch**
- Offener Zweifel: Feasibility n=57; QoL/Angst-Armwerte/SD pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 8. PMC13610533 — Effects of Chokeberry Juice Added to a Mediterranean-Style Diet on Glycemic Control and Redox Homeostasis in Women with Prediabetes: A Randomized Controlled Trial.

- Quelle: [PMC13610533](https://pmc.ncbi.nlm.nih.gov/articles/PMC13610533/) · DOI `10.3390/nu18182948`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13610533.xml` · SHA-256 `a9e4c5555615bbded09267d3ed938b224ca7764ab518e46cf4f40d43d19765f6` · 118660 Bytes
- Journal/Jahr: Nutrients (2026)
- Screening: vorläufiger Einschluss (I01); Priorität **hoch**
- Offener Zweifel: Keine Placebo-Kontrolle; Arm-N/Mean/SD und Randomisierung pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 9. PMC13613700 — Increased ureagenesis revealing metabolic intolerance to enhanced nutrition in the PICU: a secondary analysis of the PEPaNIC RCT.

- Quelle: [PMC13613700](https://pmc.ncbi.nlm.nih.gov/articles/PMC13613700/) · DOI `10.1186/s13054-026-06345-7`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13613700.xml` · SHA-256 `c937491a4a2a6e414f61ec965bab758d6025cdeb60ef80a14401821b45f900ae` · 90504 Bytes
- Journal/Jahr: Critical care (London, England) (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **hoch**
- Offener Zweifel: Sekundaeranalyse; Infektion/PICU-Ereignisse pro Arm und Adjustierung pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 10. PMC13624796 — Urinary dipstick findings and UTI risk with SGLT2 inhibitors: a post-hoc analysis of the CANVAS and CREDENCE trials.

- Quelle: [PMC13624796](https://pmc.ncbi.nlm.nih.gov/articles/PMC13624796/) · DOI `10.1093/ndt/gfag062`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13624796.xml` · SHA-256 `4db72ee954ba3fb07fc84cadff943f8d78f59dbeb9acd30c1f50e1c98c3964f6` · 107034 Bytes
- Journal/Jahr: Nephrology, dialysis, transplantation : official publication of the European Dialysis and Transplant Association - European Renal Association (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **hoch**
- Offener Zweifel: Post hoc zwei RCTs; UTI-Ereignisse pro Arm pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 11. PMC13626740 — Mechanisms of Change in the Treatment of Depression: On the Role of Attachment, Reappraisal and Suppression.

- Quelle: [PMC13626740](https://pmc.ncbi.nlm.nih.gov/articles/PMC13626740/) · DOI `10.1002/cpp.70345`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13626740.xml` · SHA-256 `b466ff623fcf08b77d0baba0ec1f89cd9f7954339f045dd71924ec851ce2f1e5` · 170463 Bytes
- Journal/Jahr: Clinical psychology & psychotherapy (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **hoch**
- Offener Zweifel: Mechanismusanalyse; unklar, ob Symptomwerte pro Arm als N/Mean/SD berichtet sind.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 12. PMC13635505 — Metabolic reserve: baseline cholesterol as a predictor and modulator of response to in-hospital exercise in older adults.

- Quelle: [PMC13635505](https://pmc.ncbi.nlm.nih.gov/articles/PMC13635505/) · DOI `10.1016/j.jnha.2026.100989`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13635505.xml` · SHA-256 `b221ecb1df8f2c8de76c0cf4eb0e926728fd86f1a0130cfad407559c06a2f8de` · 91732 Bytes
- Journal/Jahr: The journal of nutrition, health & aging (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **hoch**
- Offener Zweifel: Nur Praediktor-/Modulatoranalyse; SPPB-Armwerte und SD im Volltext pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 13. PMC13688066 — Non-contrast CT Markers of Hematoma Expansion and Andexanet Response in Factor Xa Inhibitor-Associated Intracerebral Hemorrhage: An Analysis from ANNEXa-I Trial.

- Quelle: [PMC13688066](https://pmc.ncbi.nlm.nih.gov/articles/PMC13688066/) · DOI `10.1002/ana.78347`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13688066.xml` · SHA-256 `fc2b84036059546d985727351e33a68dff5447366534e07855ed48944e372ca5` · 68926 Bytes
- Journal/Jahr: Annals of neurology (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **hoch**
- Offener Zweifel: Post hoc; N/Ereignisse fuer Haematomexpansion pro Arm pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 14. PMC13743599 — Sublingual apomorphine for Parkinsonian tremor: a post-hoc analysis of pivotal trial data.

- Quelle: [PMC13743599](https://pmc.ncbi.nlm.nih.gov/articles/PMC13743599/) · DOI `10.1007/s00702-026-03225-w`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13743599.xml` · SHA-256 `ac88c4486f17841a14c33d8ed2df55b63942e097501f1dd17b7856bd44afa8d9` · 52092 Bytes
- Journal/Jahr: Journal of neural transmission (Vienna, Austria : 1996) (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **hoch**
- Offener Zweifel: Kleine Tremor-Subgruppe, n=10/Gruppe; SD und Arm-N pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 15. PMC13352180 — Durvalumab Plus Chemotherapy for Advanced Biliary Tract Cancer: A Post Hoc Analysis of the TOPAZ-1 Randomized Clinical Trial.

- Quelle: [PMC13352180](https://pmc.ncbi.nlm.nih.gov/articles/PMC13352180/) · DOI `10.1001/jamaoncol.2026.2204`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13352180.xml` · SHA-256 `55c393c555f60c8e4abcc6e52f9df62d20e6779756d98e4823d6c9e8957b4495` · 51200 Bytes
- Journal/Jahr: JAMA oncology (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Post hoc; OS-Ereignisse pro Arm und 4-Jahres-Daten pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 16. PMC13420175 — Effect of Acoramidis on Heart Failure-Related Health Status: A Secondary Analysis of the ATTRibute-CM Randomized Clinical Trial.

- Quelle: [PMC13420175](https://pmc.ncbi.nlm.nih.gov/articles/PMC13420175/) · DOI `10.1001/jamacardio.2026.2413`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13420175.xml` · SHA-256 `3af1b16a5db65db0e72cda74d23390f4413142a45f60b861997add099c04e31d` · 110346 Bytes
- Journal/Jahr: JAMA cardiology (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Sekundaeranalyse; KCCQ-Armwerte/SD und mITT pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 17. PMC13458421 — Liver Fat Changes in Patients With Type 2 Diabetes by Presence of Genetic Hepatic Steatosis: A Post Hoc Analysis of SURPASS-3 MRI.

- Quelle: [PMC13458421](https://pmc.ncbi.nlm.nih.gov/articles/PMC13458421/) · DOI `10.1111/liv.70837`
- Lokal: nicht abgerufen (Reservefall)
- Journal/Jahr: Liver international : official journal of the International Association for the Study of the Liver (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Post hoc; Leberfett-Armwerte/SD pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 18. PMC13533545 — Weight and metabolic changes in patients with schizophrenia treated with paliperidone palmitate 6-month formulation versus paliperidone palmitate 3-month formulation: a post-hoc analysis.

- Quelle: [PMC13533545](https://pmc.ncbi.nlm.nih.gov/articles/PMC13533545/) · DOI `10.1093/ijnp/pyag042`
- Lokal: nicht abgerufen (Reservefall)
- Journal/Jahr: The international journal of neuropsychopharmacology (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Post hoc; Gewicht/Lipide als Armwerte/SD pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 19. PMC13541226 — Behavioral Modification as a Putative Mediator of Digital Therapeutic Response in Temporomandibular Disorders: Secondary Analysis of a Multicenter Sham-Controlled Randomized Trial.

- Quelle: [PMC13541226](https://pmc.ncbi.nlm.nih.gov/articles/PMC13541226/) · DOI `10.2196/104264`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13541226.xml` · SHA-256 `7118dd185e6faf68d79692c9d37db099368d4b32dc3167403f95c0c93cf573c9` · 148227 Bytes
- Journal/Jahr: JMIR mHealth and uHealth (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Post hoc, per-protocol n=93; VAS-Armwerte/SD pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 20. PMC13542807 — Digital Mindfulness Intervention for Pregnant Women With Affective Disorders and Acute Stress Reactions: Prespecified Secondary Analysis of a Randomized Controlled Trial.

- Quelle: [PMC13542807](https://pmc.ncbi.nlm.nih.gov/articles/PMC13542807/) · DOI `10.2196/93811`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13542807.xml` · SHA-256 `c2e2ec6f44a6214abdd5cea2c1bced289c8fd081fb684f991148a6621b015254` · 116598 Bytes
- Journal/Jahr: Journal of medical Internet research (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Sekundaeranalyse; EPDS-Armwerte/SD und ITT-Imputation pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 21. PMC13555364 — Restrictive vs Liberal Transfusion Strategy in Traumatic Brain Injury: A Secondary Analysis of the TRAIN Trial.

- Quelle: [PMC13555364](https://pmc.ncbi.nlm.nih.gov/articles/PMC13555364/) · DOI `10.1001/jamanetworkopen.2026.32555`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13555364.xml` · SHA-256 `766b29261c92d03e38e476ce130f8981df0ae2760f690af0f763612f363127ae` · 152161 Bytes
- Journal/Jahr: JAMA network open (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Sekundaeranalyse; GOS-E-Ereignisse pro Arm pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 22. PMC13573578 — Tenecteplase versus standard care for minor ischaemic stroke according to the baseline occlusion status in TEMPO-2 trial.

- Quelle: [PMC13573578](https://pmc.ncbi.nlm.nih.gov/articles/PMC13573578/) · DOI `10.1093/esj/aakag111`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13573578.xml` · SHA-256 `313e87bbd5dafa2cf80448b0f979a69f6d07587d36b5a28d3a21dc25e94e1ce1` · 105010 Bytes
- Journal/Jahr: European stroke journal (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Subgruppen nach Verschluss; mRS-Ereignisse pro Arm pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 23. PMC13583845 — Colchicine to prevent cardiovascular events in thoracic surgery patients with or without coronary artery disease: a secondary analysis.

- Quelle: [PMC13583845](https://pmc.ncbi.nlm.nih.gov/articles/PMC13583845/) · DOI `10.1136/openhrt-2026-004172`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13583845.xml` · SHA-256 `7be3eda9b5b41c15d5cdf9ccaca49d2d838d3610b6d06a7b262fbbea8ba176e1` · 106562 Bytes
- Journal/Jahr: Open heart (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Post hoc; MINS-Ereignisse pro Arm und CAD-Strata pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 24. PMC13586805 — A Phase II Study of Berzosertib in Combination with Carboplatin Compared with Docetaxel with Carboplatin in Metastatic Castration-Resistant Prostate Cancer.

- Quelle: [PMC13586805](https://pmc.ncbi.nlm.nih.gov/articles/PMC13586805/) · DOI `10.1158/2767-9764.crc-26-0488`
- Lokal: nicht abgerufen (Reservefall)
- Journal/Jahr: Cancer research communications (2026)
- Screening: vorläufiger Einschluss (I03); Priorität **mittel**
- Offener Zweifel: Interim n=73; ORR-Ereignisse pro Arm pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 25. PMC13591858 — The effect of cycloplegia on corneal power and diameter measured by an auto-kerato-refractometer in presbyopic patients with type 2 diabetes mellitus: a post-hoc analysis of a randomized clinical trial.

- Quelle: [PMC13591858](https://pmc.ncbi.nlm.nih.gov/articles/PMC13591858/) · DOI `10.1186/s12886-026-05351-1`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13591858.xml` · SHA-256 `7f390267519db7f41b16b12edbfd206002486ee88d599cd36ce7d7b0407968b4` · 67424 Bytes
- Journal/Jahr: BMC ophthalmology (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Post hoc; Veraenderungswerte mit SD und zwei Tropicamid-Arme pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 26. PMC13599778 — Central nervous system symptom burden and clinical implications for antiemetic management with olanzapine in AC chemotherapy.

- Quelle: [PMC13599778](https://pmc.ncbi.nlm.nih.gov/articles/PMC13599778/) · DOI `10.1093/oncolo/oyag351`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13599778.xml` · SHA-256 `c9edf870db02f18b47dc92e6575b2bbe48a2ae9dd2b9c47ab8d0aa089326ef67` · 89414 Bytes
- Journal/Jahr: The oncologist (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Sekundaeranalyse; CR-Ereignisse pro Arm und CNS-Strata pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 27. PMC13602066 — Effect of immunonutrition on postoperative infectious complications and survival after colon cancer surgery: long-term follow up of randomized clinical trial.

- Quelle: [PMC13602066](https://pmc.ncbi.nlm.nih.gov/articles/PMC13602066/) · DOI `10.1093/bjsopen/zrag043`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13602066.xml` · SHA-256 `fdb10a5fc12d09144e9448fb18d1b9ccb2d3e7846afa3dd551bced4b23e3cf2d` · 119337 Bytes
- Journal/Jahr: BJS open (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Langzeit-Follow-up; DFS/OS-Ereignisse pro Arm pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 28. PMC13610117 — More than Hormones? Metabolic Effects of Twelve-Week Probiotic Supplementation in Women with Polycystic Ovary Syndrome: A Secondary Analysis of a Randomized Double-Blind Placebo-Controlled Study.

- Quelle: [PMC13610117](https://pmc.ncbi.nlm.nih.gov/articles/PMC13610117/) · DOI `10.3390/nu18183090`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13610117.xml` · SHA-256 `95eb94e31d76ee10388aabf03ac22c4f251d541e06ffa148574afbd926f2ae9c` · 101078 Bytes
- Journal/Jahr: Nutrients (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Kleine Stichprobe; Complete-case/ITT-Armwerte pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 29. PMC13610834 — Dietary Fiber Supplementation Reduces Systolic Blood Pressure in High-Risk Patients with Type 2 Diabetes and Hypertension: A Secondary Analysis of a Randomized Trial.

- Quelle: [PMC13610834](https://pmc.ncbi.nlm.nih.gov/articles/PMC13610834/) · DOI `10.3390/nu18182945`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13610834.xml` · SHA-256 `f2d7f2012d59c8f6395a3dda0e9983314d2e6d28bebc920292d03c6ad17d1389` · 148092 Bytes
- Journal/Jahr: Nutrients (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Kleine Stichprobe; Blutdruck-Armwerte und Zeitpunkt pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 30. PMC13628872 — Skeletal displacements and upper airway changes following tooth-borne and tooth-bone-borne rapid palatal expansion in adolescents: secondary analysis of a randomized clinical trial.

- Quelle: [PMC13628872](https://pmc.ncbi.nlm.nih.gov/articles/PMC13628872/) · DOI `10.1186/s12903-026-09784-4`
- Lokal: nicht abgerufen (Reservefall)
- Journal/Jahr: BMC oral health (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Sekundaeranalyse, n=32; Arm-N/Mean/SD und 3-Monats-Zeitpunkt pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 31. PMC13629817 — Age and antiplatelet de-escalation after myocardial infarction in the TALOS-AMI trial.

- Quelle: [PMC13629817](https://pmc.ncbi.nlm.nih.gov/articles/PMC13629817/) · DOI `10.1080/07853890.2026.2726716`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13629817.xml` · SHA-256 `c2b8d662da246b1ace432f3850a6ede81e4e45488964e96f55832da31f943090` · 112957 Bytes
- Journal/Jahr: Annals of medicine (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Subgruppe <75/>=75; absolute Ereigniszahlen pro Arm und Interaktion pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 32. PMC13630044 — Effect of exercise on memory function and daily activities after colorectal cancer surgery: an exploratory secondary analysis from the randomised trial PHYSSURG-C.

- Quelle: [PMC13630044](https://pmc.ncbi.nlm.nih.gov/articles/PMC13630044/) · DOI `10.1136/bmjopen-2026-120096`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13630044.xml` · SHA-256 `6b8e90e63ac675ceae541a93a495979f2ad2ef21039154ddcb75571b7141564c` · 82851 Bytes
- Journal/Jahr: BMJ open (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Selbstberichtete binaere Outcomes; N/Ereignisse pro Arm pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 33. PMC13638319 — Occlusion site and outcomes in intra-arterial tenecteplase after successful endovascular therapy: a secondary analysis of the ANGEL-TNK trial.

- Quelle: [PMC13638319](https://pmc.ncbi.nlm.nih.gov/articles/PMC13638319/) · DOI `10.1136/jnis-2025-024129`
- Lokal: nicht abgerufen (Reservefall)
- Journal/Jahr: Journal of neurointerventional surgery (2026)
- Screening: vorläufiger Einschluss (I02); Priorität **mittel**
- Offener Zweifel: Sekundaeranalyse; mRS-Ereignisse pro Arm und Verschluss-Subgruppen pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 34. PMC13706700 — Point-of-Care Ultrasound of Upper Airway Changes During Cardiopulmonary Bypass in Coronary Artery Bypass Grafting: A Randomized Controlled Trial.

- Quelle: [PMC13706700](https://pmc.ncbi.nlm.nih.gov/articles/PMC13706700/) · DOI `10.3390/medicina62101829`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13706700.xml` · SHA-256 `29b2578a48ba15a565c90b14d433f976a2f0baa19c1383adba1296e8b5f7a60a` · 142663 Bytes
- Journal/Jahr: Medicina (Kaunas, Lithuania) (2026)
- Screening: vorläufiger Einschluss (I01); Priorität **mittel**
- Offener Zweifel: Primaer Interaktion; Arm-Mittelwerte/SD und Zeitpunkte pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 35. PMC13720204 — SARS-CoV-2-specific monoclonal antibody AER002 in Long COVID: an exploratory randomized phase 2a mechanistic trial.

- Quelle: [PMC13720204](https://pmc.ncbi.nlm.nih.gov/articles/PMC13720204/) · DOI `10.1038/s41467-026-77925-y`
- Lokal: `data/fulltext_inbox/p0_20261113_xml/PMC13720204.xml` · SHA-256 `fe77762995abf22397e9c7de07de23ea2fe206397b55b592286d97a7baaf8663` · 238134 Bytes
- Journal/Jahr: Nature communications (2026)
- Screening: vorläufiger Einschluss (I01); Priorität **mittel**
- Offener Zweifel: Kleine Stichprobe n=36; PROMIS-29 Armwerte/SD pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## 36. PMC13689703 — Chyme reinfusion using The Insides® System to reduce parenteral nutrition dependence in type 2 intestinal failure: multicentre randomized clinical trial (REINFUSE).

- Quelle: [PMC13689703](https://pmc.ncbi.nlm.nih.gov/articles/PMC13689703/) · DOI `10.1093/bjsopen/zrag158`
- Lokal: nicht abgerufen (Reservefall)
- Journal/Jahr: BJS open (2026)
- Screening: vorläufiger Einschluss (I01); Priorität **niedrig**
- Offener Zweifel: 2:1-Design; binaere PN-Endpunkte und N pro Arm pruefen.
- Reviewer: **offen** · Datum: **offen** · Finale Entscheidung: **offen**

### Eignung am Volltext

- [ ] randomisierter Parallelvergleich
- [ ] genau zwei Arme; keine Zusammenführung getrennter Arme
- [ ] Arm-N bzw. analysierte N pro Arm berichtet
- [ ] mindestens ein Outcome mit N/Mean/SD oder Events/Total
- [ ] Outcome, Einheit und Zeitpunkt eindeutig

### Studien- und Armdefinition

| Feld | Eintrag |
|---|---|
| Design (wörtlich) | |
| Design-Kategorie | |
| Trial-/Studienname | |
| Randomisierungsverhältnis | |
| Interventionsarm (Label) | |
| Kontrollarm (Label) | |
| N randomisiert (Intervention / Kontrolle) | / |
| N analysiert (Intervention / Kontrolle) | / |
| Analysepopulation | |
| Follow-up / Zeitpunkte | |
| Beleg (Tabelle/Seite) | |
| Zitat | |

### Outcome-Definitionen

| Slot | Outcome (wörtlich) | Typ | Einheit | Zeitpunkt | geplanter Effekttyp |
|---:|---|---|---|---|---|
| 1 | | cont/bin | | | md/smd/or/rr |
| 2 | | cont/bin | | | md/smd/or/rr |
| 3 | | cont/bin | | | md/smd/or/rr |
| 4 | | cont/bin | | | md/smd/or/rr |

### Armwerte

| Slot | Arm | N | Mean | SD | Mean change | SD change | SE | 95%-CI | Events | Total | Beleg |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|
| 1 | Intervention | | | | | | | | | | |
| 1 | Kontrolle | | | | | | | | | | |
| 2 | Intervention | | | | | | | | | | |
| 2 | Kontrolle | | | | | | | | | | |
| 3 | Intervention | | | | | | | | | | |
| 3 | Kontrolle | | | | | | | | | | |
| 4 | Intervention | | | | | | | | | | |
| 4 | Kontrolle | | | | | | | | | | |

Belege/Zitate pro Slot (Tabelle, Seite, wörtlicher Ausschnitt):

- Slot 1:
- Slot 2:
- Slot 3:
- Slot 4:

### Abschluss

- [ ] alle berichteten Armwerte eingetragen
- [ ] keine Schätzung/Umrechnung/Armzusammenführung
- [ ] finale Entscheidung gesetzt und begründet

---

## Legende

- **cont**: kontinuierliches Outcome; **bin**: binäres Outcome.
- **md**: Mittelwertsdifferenz; **smd**: standardisierte Differenz; **or/rr**: Odds-/Risk Ratio.
- **Mean change/SD change**: nur wenn als Veränderung berichtet; nicht aus Baseline und Follow-up schätzen.
- **SE/95%-CI**: nur wörtlich übernehmen; keine Umrechnung in SD.
- **Beleg**: Tabelle/Abbildung/Seite plus wörtliches Zitat; keine Paraphrase.

Kein Modelllauf; 30 Shortlist-XML abgerufen, keine PDFs, keine Testwiederverwendung.
