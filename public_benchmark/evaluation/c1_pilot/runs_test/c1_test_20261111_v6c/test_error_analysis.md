# C1-Testlauf v6c: Fehleranalyse

Run: `c1_test_20261111_v6c`
Status: **deskriptiv, eingefrorener Testlauf**

## Kernbefunde

- **32 Records** haben ausschliesslich fehlende Werte, **69 Records** ausschliesslich falsche Werte; **0** haben beides.
- **148/249 Records** sind vollstaendig exakt.
- **0 Halluzinationen**, **0 Schema-/Parsefehler**; Null-Disziplin **684/684**.
- Continuous ist mit **678/936 (72,4 %)** deutlich schwaecher als binary mit **314/372 (84,4 %)**.
- Die Fehler sind ueberwiegend blockweise: ganze Mean/SD-Bloecke oder ganze n-/Event-Bloecke fehlen bzw. weichen ab; einzelne Felder kommen vor, vor allem `comparator_n`.
- Kein durchgaengiger Richtungsbias: Ueber- und Unterschaetzungen wechseln je Feld; einzelne Felder zeigen lokale Asymmetrien.

## Record-Ebene

| Typ | Records | vollstaendig exakt | nur fehlend | nur falsch | beides | 0 exakt |
|---|---:|---:|---:|---:|---:|---:|
| continuous | 156 | 79 | 22 | 55 | 0 | 11 |
| binary | 93 | 69 | 10 | 14 | 0 | 7 |
| gesamt | 249 | 148 | 32 | 69 | 0 | 18 |

## Feldebene

| Typ | Feld | erwartet | exakt | fehlend | falsch | exakt % | MAE |
|---|---|---:|---:|---:|---:|---:|---:|
| continuous | `intervention_n` | 156 | 133 | 11 | 12 | 85.3% | 1.5517 |
| continuous | `comparator_n` | 156 | 120 | 11 | 25 | 76.9% | 3.0138 |
| continuous | `intervention_mean` | 156 | 110 | 21 | 25 | 70.5% | 2.4114 |
| continuous | `comparator_mean` | 156 | 105 | 21 | 30 | 67.3% | 2.5808 |
| continuous | `intervention_sd` | 156 | 106 | 21 | 29 | 68.0% | 0.604 |
| continuous | `comparator_sd` | 156 | 104 | 21 | 31 | 66.7% | 0.3642 |
| binary | `intervention_n` | 93 | 81 | 9 | 3 | 87.1% | 0.25 |
| binary | `comparator_n` | 93 | 81 | 9 | 3 | 87.1% | 0.1667 |
| binary | `intervention_events` | 93 | 76 | 8 | 9 | 81.7% | 1.8 |
| binary | `comparator_events` | 93 | 76 | 8 | 9 | 81.7% | 1.5647 |

## Fehlende Muster

| Typ | Muster | Records | Felder |
|---|---|---:|---:|
| continuous | comparator_mean + comparator_sd + intervention_mean + intervention_sd | 11 | 4 |
| continuous | comparator_mean + comparator_n + comparator_sd + intervention_mean + intervention_n + intervention_sd | 10 | 6 |
| continuous | comparator_n + intervention_n | 1 | 2 |
| binary | comparator_events + comparator_n + intervention_events + intervention_n | 7 | 4 |
| binary | comparator_n + intervention_n | 2 | 2 |
| binary | comparator_events + intervention_events | 1 | 2 |

## Falsche Muster

| Typ | Muster | Records | Felder |
|---|---|---:|---:|
| continuous | comparator_mean + comparator_sd + intervention_mean + intervention_sd | 23 | 4 |
| continuous | comparator_n | 10 | 1 |
| continuous | comparator_n + intervention_n | 10 | 2 |
| continuous | comparator_mean + comparator_n + comparator_sd | 4 | 3 |
| continuous | intervention_sd | 2 | 1 |
| continuous | comparator_mean + comparator_sd + intervention_sd | 1 | 3 |
| continuous | comparator_mean + comparator_sd | 1 | 2 |
| continuous | comparator_mean + comparator_n + comparator_sd + intervention_mean + intervention_n + intervention_sd | 1 | 6 |
| continuous | comparator_sd + intervention_sd | 1 | 2 |
| continuous | intervention_mean + intervention_sd | 1 | 2 |
| continuous | intervention_n | 1 | 1 |
| binary | comparator_events + intervention_events | 7 | 2 |
| binary | comparator_n + intervention_n | 3 | 2 |
| binary | comparator_events | 2 | 1 |
| binary | intervention_events | 2 | 1 |

## Richtung und Groesse der falschen Werte

`near` zaehlt bei n/events die exakte Differenz 1, 2 oder >= 3; bei Mean/SD die Differenz <= 0,5, <= 1 oder <= 2.

| Typ | Feld | falsch | ueber | unter | Median | p90 | max | near 1 | near 2 | near 3 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| continuous | `intervention_n` | 12 | 3 | 9 | 1.5 | 49.0 | 128.0 | 6 | 1 | 5 |
| continuous | `comparator_n` | 25 | 10 | 15 | 2.0 | 17.0 | 308.0 | 7 | 11 | 7 |
| continuous | `intervention_mean` | 25 | 13 | 12 | 3.4 | 68.23 | 81.18 | 4 | 6 | 7 |
| continuous | `comparator_mean` | 30 | 14 | 16 | 2.85 | 29.5 | 91.08 | 8 | 11 | 13 |
| continuous | `intervention_sd` | 29 | 15 | 14 | 0.9 | 8.8 | 19.3 | 10 | 16 | 20 |
| continuous | `comparator_sd` | 31 | 16 | 15 | 0.59 | 4.95 | 7.43 | 14 | 20 | 23 |
| binary | `intervention_n` | 3 | 1 | 2 | 5.0 | 15.0 | 15.0 | 1 | 0 | 2 |
| binary | `comparator_n` | 3 | 1 | 2 | 4.0 | 9.0 | 9.0 | 1 | 0 | 2 |
| binary | `intervention_events` | 9 | 7 | 2 | 6.0 | 56.0 | 56.0 | 0 | 0 | 9 |
| binary | `comparator_events` | 9 | 5 | 4 | 4.0 | 54.0 | 54.0 | 1 | 1 | 7 |

## Auditstatus

| Status | Records | vollstaendig exakt | nur fehlend | nur falsch |
|---|---:|---:|---:|---:|
| `corrected_with_source` | 1 | 0 | 0 | 1 |
| `verified_exact` | 215 | 125 | 30 | 60 |
| `verified_table` | 33 | 23 | 2 | 8 |

## Deutung

- Die saubere Trennung von fehlend und falsch spricht fuer blockweise Extraktion: Das Modell liefert entweder einen vollstaendigen Block (moeglicherweise mit falschen Werten) oder laesst einen Block als `null` weg.
- Der groesste falsche Block sind **23 kontinuierliche Records mit allen vier Mean/SD-Feldern falsch**, waehrend beide n-Felder exakt sind. Der groesste fehlende Block sind **11 Records mit beiden Mean/SD-Armen fehlend**.
- Beim binären Typ sind **7 Records mit allen vier Feldern fehlend** und **7 Records mit beiden Event-Feldern falsch** die groessten Gruppen.
- Die exakte Metrik bestraft auch kleine Rundungs- oder Skalierungsabweichungen. Die Near-Miss-Spalten zeigen, wie viele falsche Werte nahe an der Referenz liegen; die Bewertung sollte deshalb nicht nur als eine einzelne Exact-Match-Zahl gelesen werden.
- Der Vergleichsarm ist bei n und Mean/SD etwas schwaecher als der Interventionsarm; die Event-Felder sind arm-symmetrisch.

## Grenzen und Protokoll

- Ein einzelner eingefrorener Testlauf; keine neue Modellausfuehrung.
- Keine Prompt-Aenderung und keine Verwendung des Testsplit zur Optimierung.
- Die Analyse ist deskriptiv; sie belegt keine Kausalitaet fuer die beobachteten Blockmuster.
- Keine Testwerte oder Record-IDs in diesem Bericht.
