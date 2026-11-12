# P0-Abstract-Screening v1

Kriterien: [`screening_criteria_v1.json`](screening_criteria_v1.json)
Kandidaten: **596**
Methode: deterministische Regeln, kein Modellaufruf.

| Entscheidung | Anzahl |
|---|---:|
| Ausschluss | 152 |
| Manuelle Prüfung | 65 |
| Vorläufig für Volltext | 379 |
| **Gesamt** | **596** |

## Ausschlussgründe

| Regel | Anzahl Records |
|---|---:|
| E01 | 19 |
| E03 | 90 |
| E04 | 53 |
| E05 | 33 |
| E06 | 2 |
| E07 | 13 |
| E08 | 1 |
| E09 | 1 |
| E10 | 13 |
| E11 | 5 |

Mehrfachgründe sind möglich; die Regeltabelle zählt Records mit der jeweiligen
Regel, nicht disjunkte Entscheidungen.

## Manuelle Prüfung

| Regel | Anzahl Records |
|---|---:|
| M01 | 87 |
| M02 | 3 |
| M03 | 6 |

Jeder Ausschluss ist mit PMCID, Regel-ID, Begründung und Textbeleg in
[`screening_exclusions_v1.jsonl`](screening_exclusions_v1.jsonl) dokumentiert. Alle 596
Entscheidungen stehen in
[`screening_decisions_v1.jsonl`](screening_decisions_v1.jsonl).

**Keine endgültige Eignung:** Parallelgruppen, zwei Arme und
extrahierbare N/Mean/SD/Events werden erst im Volltext geprüft.
Kein Modelllauf.
