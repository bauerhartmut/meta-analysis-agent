# Eignungspruefung der 25 Hauptartikel

Stand: 2026-11-13
Deterministisch aus den XML-Volltexten. Kein Modell, kein Netz.

## Verteilung

| Klasse | Artikel |
|---|---:|
| eligible_confirmed | 1 |
| eligible_uncertain | 3 |
| manual_review_required | 2 |
| ineligible | 4 |

## Einzelbefunde

| PMCID | Klasse | Tabellen | Baseline | kont. | bin. | direkte Effekte | Zeitpunkte | Supplement |
|---|---|---:|---:|---:|---:|---:|---|---|
| PMC13560212 | ineligible | 6 | 0 | 0 | 0 | 0 | 3 | ja |
| PMC13624021 | eligible_uncertain | 4 | 1 | 0 | 2 | 9 | 0 | ja |
| PMC13610065 | ineligible | 3 | 1 | 0 | 0 | 0 | 0 | ja |
| PMC13593208 | manual_review_required | 3 | 1 | 10 | 0 | 0 | 5 | ja |
| PMC13577647 | eligible_uncertain | 5 | 1 | 8 | 23 | 0 | 0 | nein |
| PMC13632614 | eligible_confirmed | 2 | 1 | 0 | 7 | 0 | 2 | nein |
| PMC13607715 | ineligible | 3 | 0 | 0 | 0 | 0 | 0 | nein |
| PMC13609332 | manual_review_required | 4 | 2 | 0 | 3 | 0 | 0 | ja |
| PMC13535982 | eligible_uncertain | 3 | 1 | 0 | 8 | 0 | 0 | ja |
| PMC13578717 | ineligible | 2 | 1 | 0 | 0 | 0 | 0 | ja |

## Begruendungen

### PMC13560212 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13624021 - eligible_uncertain

Armwerte vorhanden, aber kein Zeitpunkt in Label oder Spaltenkopf
- binary: Table 2 / ≥ 2: 23 (11.2) | 17 (8.9)
- binary: Table 2 / Intravenous dextrose therapy: 10 (4.9) | 17(8.7)

### PMC13610065 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13593208 - manual_review_required

Mehrarm- oder Mehrzeitpunkt-Struktur: 0 Arme im Kopf, 5 Zeitpunktangaben
- continuous: Table 3 / Baseline: 51.77 ± 13.44 | 48.57–54.98 | 52.68 ± 12.99 | 49.41–55.95
- continuous: Table 3 / 6 months: 54.09 ± 16.24 | 50.13–58.05 | 55.80 ± 13.58 | 52.29–59.31

### PMC13577647 - eligible_uncertain

Armwerte vorhanden, aber kein Zeitpunkt in Label oder Spaltenkopf
- binary: Table 2 / 35–45: 11 (36.6%) | 9 (30.0%)
- binary: Table 2 / 50: 13 (30.0%) | 8 (26.7%)

### PMC13632614 - eligible_confirmed

0 kontinuierliche und 7 binaere Outcome-Zeilen mit Armwerten; Zeitpunkt ableitbar
- binary: Table 2 / mRS 0–2 at 90 days, n (%) c: 40 (18.9) | 2 (3.4)
- binary: Table 2 / mRS 0–3 at 90 days, n (%) c: 52 (25.0) | 3 (5.2)

### PMC13607715 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren

### PMC13609332 - manual_review_required

Mehrarm- oder Mehrzeitpunkt-Struktur: 3 Arme im Kopf, 0 Zeitpunktangaben
- binary: Table 3 / 1: 186 (91.2) | 94 (92.2) | 92 (90.2)
- binary: Table 3 / 2: 15 (7.3) | 6 (5.9) | 9 (8.8)

### PMC13535982 - eligible_uncertain

Armwerte vorhanden, aber kein Zeitpunkt in Label oder Spaltenkopf
- binary: Table 3 / MACE: 8 (12.7) | 5 (8.3)
- binary: Table 3 / All‐cause death: 0 (0.0) | 1 (1.7)

### PMC13578717 - ineligible

keine Outcome-Tabelle mit zwei Armwerten oder zwei Ereignispaaren
