# Eignungspruefung der 25 Hauptartikel

Stand: 2026-11-13
Deterministisch aus den XML-Volltexten. Kein Modell, kein Netz.

## Verteilung

| Klasse | Artikel |
|---|---:|
| eligible_confirmed | 1 |
| eligible_uncertain | 3 |
| manual_review_required | 10 |
| ineligible | 11 |

## Einzelbefunde

| PMCID | Klasse | Tabellen | Baseline | kont. | bin. | direkte Effekte | Zeitpunkte | Supplement |
|---|---|---:|---:|---:|---:|---:|---|---|
| PMC13533546 | ineligible | 2 | 2 | 0 | 0 | 0 | 0 | ja |
| PMC13587535 | manual_review_required | 3 | 1 | 0 | 27 | 0 | 5 | ja |
| PMC13554527 | eligible_confirmed | 4 | 1 | 15 | 0 | 0 | 2 | ja |
| PMC13581780 | ineligible | 4 | 1 | 0 | 0 | 19 | 0 | ja |
| PMC13544601 | manual_review_required | 2 | 1 | 0 | 0 | 0 | 0 | ja |
| PMC13613989 | ineligible | 3 | 2 | 0 | 0 | 0 | 0 | nein |
| PMC13493211 | manual_review_required | 0 | 0 | 0 | 0 | 0 | 0 | ja |
| PMC13583812 | ineligible | 6 | 5 | 0 | 0 | 0 | 0 | nein |
| PMC13682724 | ineligible | 10 | 4 | 0 | 0 | 0 | 0 | nein |
| PMC13575558 | manual_review_required | 0 | 0 | 0 | 0 | 0 | 0 | ja |
| PMC13568562 | ineligible | 3 | 2 | 0 | 0 | 0 | 1 | ja |
| PMC13539392 | eligible_uncertain | 3 | 2 | 0 | 7 | 0 | 0 | ja |
| PMC13599780 | manual_review_required | 2 | 1 | 0 | 13 | 0 | 0 | ja |
| PMC13683044 | ineligible | 5 | 0 | 0 | 0 | 0 | 1 | ja |
| PMC13597907 | eligible_uncertain | 7 | 1 | 0 | 2 | 2 | 0 | nein |
| PMC13591874 | manual_review_required | 5 | 2 | 4 | 0 | 0 | 3 | ja |
| PMC13553157 | ineligible | 3 | 1 | 0 | 0 | 0 | 0 | nein |
| PMC13587653 | ineligible | 1 | 0 | 0 | 0 | 0 | 0 | ja |
| PMC13724892 | eligible_uncertain | 5 | 2 | 0 | 6 | 0 | 0 | ja |
| PMC13610706 | manual_review_required | 4 | 0 | 0 | 2 | 0 | 3 | nein |
| PMC13645219 | manual_review_required | 0 | 0 | 0 | 0 | 0 | 0 | ja |
| PMC13556510 | manual_review_required | 0 | 0 | 0 | 0 | 0 | 0 | nein |
| PMC13632637 | manual_review_required | 4 | 1 | 0 | 33 | 0 | 4 | ja |
| PMC13729219 | ineligible | 2 | 1 | 0 | 0 | 0 | 0 | nein |
| PMC13601125 | ineligible | 6 | 1 | 0 | 0 | 0 | 0 | ja |

## Begruendungen

### PMC13533546 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13587535 - manual_review_required

Mehrarm- oder Mehrzeitpunkt-Struktur: 2 Arme im Kopf, 5 Zeitpunktangaben
- binary: Table 2. / AUC NRS during coughing within postoperative 48 h, mean (SD): 169 (37) | 175 (47)
- binary: Table 2. / QoR-15, mean (SD): 108 (12) | 116 (10)

### PMC13554527 - eligible_confirmed

15 kontinuierliche und 0 binaere Outcome-Zeilen mit Armwerten; Zeitpunkt ableitbar
- continuous: Table 3. / MCC (mL): Pre | 210.68 ± 34.90 | 206.76 ± 32.60 | 3.92
- continuous: Table 3. / Post: 316.81 ± 56.59 | 290.68 ± 45.54 | 26.13 | [5.42, 46.84]

### PMC13581780 - ineligible

nur direkter Effekt mit Konfidenzintervall (19 Zeilen); keine Armwerte fuer N/Mean/SD

### PMC13544601 - manual_review_required

vertikales Arm-Layout (6 Zeilen mit Armname und Mittelwert in der Nachbarzelle); Zuordnung braucht eigene Logik

### PMC13613989 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13493211 - manual_review_required

XML enthaelt keine Tabelle; Werte koennen nur im PDF oder Supplement stehen und sind aus dem XML nicht pruefbar

### PMC13583812 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13682724 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13575558 - manual_review_required

XML enthaelt keine Tabelle; Werte koennen nur im PDF oder Supplement stehen und sind aus dem XML nicht pruefbar

### PMC13568562 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13539392 - eligible_uncertain

Armwerte vorhanden, aber kein Zeitpunkt in Label oder Spaltenkopf
- binary: Table 3. / Denver Health EHR: 8 (8.6) | 12 (12.5)
- binary: Table 3. / Any treatment b: 24 (25.0) | 24 (25.0)

### PMC13599780 - manual_review_required

Mehrarm- oder Mehrzeitpunkt-Struktur: 3 Arme im Kopf, 0 Zeitpunktangaben
- binary: Table 2 / Infections and infestations: 14 (44) | 6 (33) | 8 (57)
- binary: Table 2 / General disorders and administration site conditions: 7 (22) | 7 (39) | 0 (0)

### PMC13683044 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13597907 - eligible_uncertain

Armwerte vorhanden, aber kein Zeitpunkt in Label oder Spaltenkopf
- binary: Table 7 / Pregnancy Rate: 4(12.1) | 29(87.9)
- binary: Table 7 / Control: 2(6.9) | 27(93.1)

### PMC13591874 - manual_review_required

Mehrarm- oder Mehrzeitpunkt-Struktur: 2 Arme im Kopf, 3 Zeitpunktangaben
- continuous: Table 2 / Baseline: 55.00 ± 14.58 | 50.88 ± 10.86 | −4.1 (− 17.9, 9.7) | 0.53
- continuous: Table 2 / 3 months: 63.13 ± 9.63 | 61.00 ± 7.25 | −2.1 (− 11.3, 7.0) | 0.63

### PMC13553157 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13587653 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13724892 - eligible_uncertain

Armwerte vorhanden, aber kein Zeitpunkt in Label oder Spaltenkopf
- binary: Table 3. / SBP (mmHg): 138 (12) | 130 (14) | 130 (14) | 124 (21.5)
- binary: Table 3. / DBP (mmHg): 86 (11.5) | 80 (6) | 79 (12) | 80 (5)

### PMC13610706 - manual_review_required

Mehrarm- oder Mehrzeitpunkt-Struktur: 4 Arme im Kopf, 3 Zeitpunktangaben
- binary: Table 1 / ASD diagnosis confirmed, n (%): 1 (10.0%) | 5 (62.5%) | 1 (11.1%) | 5 (71.4%)
- binary: Table 1 / Learning disorder, n (%): 1 (10.0%) | 4 (50.0%) | 1 (11.1%) | 5 (71.4%)

### PMC13645219 - manual_review_required

XML enthaelt keine Tabelle; Werte koennen nur im PDF oder Supplement stehen und sind aus dem XML nicht pruefbar

### PMC13556510 - manual_review_required

XML enthaelt keine Tabelle; Werte koennen nur im PDF oder Supplement stehen und sind aus dem XML nicht pruefbar

### PMC13632637 - manual_review_required

Mehrarm- oder Mehrzeitpunkt-Struktur: 2 Arme im Kopf, 4 Zeitpunktangaben
- binary: Table 2 / Overall PONV within 24 h: 23 (31.5%) | 43 (58.9%)
- binary: Table 2 / Overall nausea within 24 h: 20 (27.4%) | 36 (49.3%)

### PMC13729219 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13601125 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren
