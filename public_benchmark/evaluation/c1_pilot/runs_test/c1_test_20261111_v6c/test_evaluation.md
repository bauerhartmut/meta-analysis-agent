# C1-Test-Pilot: Ergebnis

Run: `c1_test_20261111_v6c`

## Kopfzahlen

- Records mit Ausgabe: **249/249**
- Erwartete Felder: **1308**
- Abdeckung: **1168/1308** (89.3%)
- Exakte Treffer: **992/1308** (75.8%)
- Fehlend: **140**; falsch: **176**; halluziniert: **0**
- MAE über alle gepaarten erwarteten Felder: **1.5305**
- Null-Disziplin auf nicht erwarteten Feldern: **684/684** (100.0%)
- Records mit vollständig exakten Erwartungsfeldern: **148/249**
- Schema-/Parse-Fehler: **0** (keine)

## Feldebene

| Feld | erwartet | vorhanden | exakt | fehlend | falsch | MAE |
|---|---:|---:|---:|---:|---:|---:|
| `intervention_n` | 249 | 229 | 214 | 20 | 15 | 1.0742 |
| `comparator_n` | 249 | 229 | 201 | 20 | 28 | 1.9694 |
| `intervention_mean` | 156 | 135 | 110 | 21 | 25 | 2.4114 |
| `comparator_mean` | 156 | 135 | 105 | 21 | 30 | 2.5808 |
| `intervention_sd` | 156 | 135 | 106 | 21 | 29 | 0.604 |
| `comparator_sd` | 156 | 135 | 104 | 21 | 31 | 0.3642 |
| `intervention_events` | 93 | 85 | 76 | 8 | 9 | 1.8 |
| `comparator_events` | 93 | 85 | 76 | 8 | 9 | 1.5647 |

## Fehlerliste

| Record | Feld | Kategorie | Referenz | Modell | absolute Differenz |
|---:|---|---|---:|---:|---:|
| 12 | `intervention_sd` | falsch | 23.34 | 12.34 | 11 |
| 14 | `comparator_events` | falsch | 54.0 | 53 | 1 |
| 22 | `intervention_mean` | falsch | 48.13 | 44.33 | 3.8 |
| 22 | `comparator_mean` | falsch | 40.99 | 36.39 | 4.6 |
| 22 | `intervention_sd` | falsch | 22.1 | 2.8 | 19.3 |
| 22 | `comparator_sd` | falsch | 20.98 | 20.53 | 0.45 |
| 30 | `intervention_mean` | falsch | 38.1 | 5.6 | 32.5 |
| 30 | `comparator_mean` | falsch | 31.5 | 2 | 29.5 |
| 30 | `intervention_sd` | falsch | 9.5 | 0.7 | 8.8 |
| 30 | `comparator_sd` | falsch | 7.4 | 0.8 | 6.6 |
| 31 | `intervention_mean` | falsch | 38.9 | 45.7 | 6.8 |
| 31 | `comparator_mean` | falsch | 31.5 | 41.4 | 9.9 |
| 31 | `intervention_sd` | falsch | 8.9 | 11.6 | 2.7 |
| 31 | `comparator_sd` | falsch | 7.4 | 10.8 | 3.4 |
| 32 | `intervention_n` | fehlend | 390.0 | null | - |
| 32 | `comparator_n` | fehlend | 199.0 | null | - |
| 32 | `intervention_mean` | fehlend | 53.9 | null | - |
| 32 | `comparator_mean` | fehlend | 34.0 | null | - |
| 32 | `intervention_sd` | fehlend | 22.2 | null | - |
| 32 | `comparator_sd` | fehlend | 20.1 | null | - |
| 33 | `intervention_mean` | falsch | 38.1 | 45.5 | 7.4 |
| 33 | `comparator_mean` | falsch | 31.5 | 41.4 | 9.9 |
| 33 | `intervention_sd` | falsch | 9.5 | 11.5 | 2 |
| 33 | `comparator_sd` | falsch | 7.4 | 10.8 | 3.4 |
| 37 | `intervention_n` | fehlend | 6.0 | null | - |
| 37 | `comparator_n` | fehlend | 14.0 | null | - |
| 38 | `intervention_n` | fehlend | 6.0 | null | - |
| 38 | `comparator_n` | fehlend | 14.0 | null | - |
| 38 | `intervention_events` | fehlend | 0.0 | null | - |
| 38 | `comparator_events` | fehlend | 0.0 | null | - |
| 39 | `intervention_n` | fehlend | 6.0 | null | - |
| 39 | `comparator_n` | fehlend | 14.0 | null | - |
| 39 | `intervention_events` | fehlend | 0.0 | null | - |
| 39 | `comparator_events` | fehlend | 0.0 | null | - |
| 40 | `intervention_n` | fehlend | 6.0 | null | - |
| 40 | `comparator_n` | fehlend | 14.0 | null | - |
| 40 | `intervention_events` | fehlend | 0.0 | null | - |
| 40 | `comparator_events` | fehlend | 0.0 | null | - |
| 41 | `intervention_n` | fehlend | 6.0 | null | - |
| 41 | `comparator_n` | fehlend | 14.0 | null | - |
| 41 | `intervention_events` | fehlend | 0.0 | null | - |
| 41 | `comparator_events` | fehlend | 0.0 | null | - |
| 42 | `intervention_n` | fehlend | 6.0 | null | - |
| 42 | `comparator_n` | fehlend | 14.0 | null | - |
| 42 | `intervention_events` | fehlend | 0.0 | null | - |
| 42 | `comparator_events` | fehlend | 0.0 | null | - |
| 43 | `intervention_n` | fehlend | 6.0 | null | - |
| 43 | `comparator_n` | fehlend | 14.0 | null | - |
| 43 | `intervention_events` | fehlend | 0.0 | null | - |
| 43 | `comparator_events` | fehlend | 0.0 | null | - |
| 73 | `comparator_n` | falsch | 19.0 | 28 | 9 |
| 73 | `comparator_mean` | falsch | 0.047 | 0.866 | 0.819 |
| 73 | `comparator_sd` | falsch | 0.017 | 0.754 | 0.737 |
| 74 | `comparator_n` | falsch | 19.0 | 28 | 9 |
| 74 | `comparator_mean` | falsch | 1.45 | 1.69 | 0.24 |
| 74 | `comparator_sd` | falsch | 0.24 | 0.37 | 0.13 |
| 77 | `comparator_n` | falsch | 29.0 | 28 | 1 |
| 77 | `comparator_mean` | falsch | 24.72 | 19.18 | 5.54 |
| 77 | `comparator_sd` | falsch | 8.78 | 10.93 | 2.15 |
| 82 | `comparator_n` | falsch | 29.0 | 28 | 1 |
| 82 | `comparator_mean` | falsch | 1.03 | 1.25 | 0.22 |
| 82 | `comparator_sd` | falsch | 0.53 | 0.36 | 0.17 |
| 127 | `intervention_events` | falsch | 11.0 | 5 | 6 |
| 127 | `comparator_events` | falsch | 21.0 | 17 | 4 |
| 128 | `comparator_events` | falsch | 21.0 | 17 | 4 |
| 130 | `intervention_events` | falsch | 11.0 | 5 | 6 |
| 132 | `intervention_n` | falsch | 326.0 | 311 | 15 |
| 132 | `comparator_n` | falsch | 326.0 | 317 | 9 |
| 133 | `intervention_events` | falsch | 45.0 | 51 | 6 |
| 133 | `comparator_events` | falsch | 58.0 | 52 | 6 |
| 152 | `intervention_events` | falsch | 14.0 | 21 | 7 |
| 176 | `intervention_n` | fehlend | 26.0 | null | - |
| 176 | `comparator_n` | fehlend | 26.0 | null | - |
| 176 | `intervention_mean` | fehlend | 18.23 | null | - |
| 176 | `comparator_mean` | fehlend | 22.46 | null | - |
| 176 | `intervention_sd` | fehlend | 8.14 | null | - |
| 176 | `comparator_sd` | fehlend | 8.67 | null | - |
| 177 | `intervention_n` | fehlend | 26.0 | null | - |
| 177 | `comparator_n` | fehlend | 26.0 | null | - |
| 177 | `intervention_mean` | fehlend | 50.24 | null | - |
| 177 | `comparator_mean` | fehlend | 45.63 | null | - |
| 177 | `intervention_sd` | fehlend | 7.41 | null | - |
| 177 | `comparator_sd` | fehlend | 6.31 | null | - |
| 179 | `intervention_n` | fehlend | 26.0 | null | - |
| 179 | `comparator_n` | fehlend | 26.0 | null | - |
| 179 | `intervention_mean` | fehlend | 32.81 | null | - |
| 179 | `comparator_mean` | fehlend | 32.93 | null | - |
| 179 | `intervention_sd` | fehlend | 5.31 | null | - |
| 179 | `comparator_sd` | fehlend | 4.85 | null | - |
| 180 | `intervention_n` | fehlend | 26.0 | null | - |
| 180 | `comparator_n` | fehlend | 26.0 | null | - |
| 180 | `intervention_mean` | fehlend | 50.87 | null | - |
| 180 | `comparator_mean` | fehlend | 50.46 | null | - |
| 180 | `intervention_sd` | fehlend | 11.02 | null | - |
| 180 | `comparator_sd` | fehlend | 7.83 | null | - |
| 182 | `intervention_events` | falsch | 0.0 | 4 | 4 |
| 182 | `comparator_events` | falsch | 0.0 | 2 | 2 |
| 194 | `intervention_events` | fehlend | 39.0 | null | - |
| 194 | `comparator_events` | fehlend | 35.0 | null | - |
| 209 | `intervention_mean` | falsch | 4.0 | 6.6 | 2.6 |
| 209 | `comparator_mean` | falsch | 4.0 | 6.7 | 2.7 |
| 209 | `intervention_sd` | falsch | 0.3 | 0.9 | 0.6 |
| 209 | `comparator_sd` | falsch | 0.6 | 1.1 | 0.5 |
| 213 | `intervention_mean` | falsch | 5.8 | 9.8 | 4 |
| 213 | `comparator_mean` | falsch | 5.9 | 10.1 | 4.2 |
| 213 | `intervention_sd` | falsch | 0.5 | 1.2 | 0.7 |
| 213 | `comparator_sd` | falsch | 0.7 | 1.2 | 0.5 |
| 217 | `intervention_n` | fehlend | 8.0 | null | - |
| 217 | `comparator_n` | fehlend | 8.0 | null | - |
| 221 | `intervention_mean` | falsch | 0.34 | 0.33 | 0.01 |
| 221 | `comparator_mean` | falsch | 7.47 | 7.2 | 0.27 |
| 221 | `intervention_sd` | falsch | 0.12 | 0.11 | 0.01 |
| 221 | `comparator_sd` | falsch | 1.45 | 1.33 | 0.12 |
| 222 | `comparator_mean` | falsch | 2.67 | 2.53 | 0.14 |
| 222 | `intervention_sd` | falsch | 0.02 | 0.01 | 0.01 |
| 222 | `comparator_sd` | falsch | 0.68 | 0.67 | 0.01 |
| 223 | `comparator_mean` | falsch | 1.62 | 1.53 | 0.09 |
| 223 | `comparator_sd` | falsch | 0.47 | 0.42 | 0.05 |
| 240 | `intervention_mean` | falsch | 6.0 | 0.11 | 5.89 |
| 240 | `comparator_mean` | falsch | 4.8 | -0.25 | 5.05 |
| 240 | `intervention_sd` | falsch | 0.9 | 0.81 | 0.09 |
| 240 | `comparator_sd` | falsch | 0.9 | 0.71 | 0.19 |
| 241 | `intervention_mean` | falsch | 6.0 | 0.11 | 5.89 |
| 241 | `comparator_mean` | falsch | 6.2 | 0.13 | 6.07 |
| 241 | `intervention_sd` | falsch | 0.9 | 0.81 | 0.09 |
| 241 | `comparator_sd` | falsch | 1.8 | 0.82 | 0.98 |
| 242 | `intervention_mean` | falsch | 6.2 | 0.13 | 6.07 |
| 242 | `comparator_mean` | falsch | 4.8 | -0.25 | 5.05 |
| 242 | `intervention_sd` | falsch | 1.8 | 0.82 | 0.98 |
| 242 | `comparator_sd` | falsch | 0.9 | 0.71 | 0.19 |
| 244 | `intervention_mean` | falsch | 0.82 | 82 | 81.18 |
| 244 | `comparator_mean` | falsch | 0.92 | 92 | 91.08 |
| 244 | `intervention_sd` | falsch | 0.05 | 5 | 4.95 |
| 244 | `comparator_sd` | falsch | 0.07 | 7 | 6.93 |
| 246 | `intervention_mean` | falsch | 0.74 | 74 | 73.26 |
| 246 | `comparator_mean` | falsch | 0.83 | 83 | 82.17 |
| 246 | `intervention_sd` | falsch | 0.05 | 5 | 4.95 |
| 246 | `comparator_sd` | falsch | 0.05 | 5 | 4.95 |
| 251 | `intervention_events` | falsch | 8.0 | 64 | 56 |
| 251 | `comparator_events` | falsch | 7.0 | 61 | 54 |
| 306 | `comparator_n` | falsch | 30.0 | 29 | 1 |
| 307 | `comparator_n` | falsch | 30.0 | 29 | 1 |
| 308 | `comparator_n` | falsch | 30.0 | 29 | 1 |
| 309 | `comparator_n` | falsch | 30.0 | 29 | 1 |
| 310 | `comparator_n` | falsch | 30.0 | 29 | 1 |
| 316 | `intervention_mean` | falsch | 4.3 | 6.4 | 2.1 |
| 316 | `comparator_mean` | falsch | 3.6 | 5.1 | 1.5 |
| 316 | `intervention_sd` | falsch | 1.0 | 1.3 | 0.3 |
| 316 | `comparator_sd` | falsch | 1.2 | 1.6 | 0.4 |
| 346 | `intervention_n` | falsch | 22.0 | 5 | 17 |
| 346 | `comparator_n` | falsch | 22.0 | 5 | 17 |
| 347 | `intervention_n` | falsch | 22.0 | 5 | 17 |
| 347 | `comparator_n` | falsch | 22.0 | 5 | 17 |
| 355 | `intervention_mean` | falsch | 5.71 | 6.29 | 0.58 |
| 355 | `comparator_mean` | falsch | 5.7 | 6.35 | 0.65 |
| 355 | `intervention_sd` | falsch | 0.71 | 0.31 | 0.4 |
| 355 | `comparator_sd` | falsch | 0.45 | 0.34 | 0.11 |
| 359 | `intervention_n` | fehlend | 720.0 | null | - |
| 359 | `comparator_n` | fehlend | 682.0 | null | - |
| 359 | `intervention_mean` | fehlend | 4.1 | null | - |
| 359 | `comparator_mean` | fehlend | 2.9 | null | - |
| 359 | `intervention_sd` | fehlend | 12.4 | null | - |
| 359 | `comparator_sd` | fehlend | 12.7 | null | - |
| 400 | `intervention_n` | fehlend | 53.0 | null | - |
| 400 | `comparator_n` | fehlend | 53.0 | null | - |
| 400 | `intervention_events` | fehlend | 4.0 | null | - |
| 400 | `comparator_events` | fehlend | 2.0 | null | - |
| 417 | `intervention_sd` | falsch | 1.4 | 1.5 | 0.1 |
| 420 | `intervention_mean` | falsch | 0.95 | 0.8 | 0.15 |
| 420 | `comparator_mean` | falsch | 1.43 | 1.1 | 0.33 |
| 420 | `intervention_sd` | falsch | 0.24 | 0.1 | 0.14 |
| 420 | `comparator_sd` | falsch | 0.48 | 0.2 | 0.28 |
| 421 | `intervention_mean` | falsch | 0.83 | 0.8 | 0.03 |
| 421 | `comparator_mean` | falsch | 1.32 | 1.2 | 0.12 |
| 421 | `intervention_sd` | falsch | 0.22 | 0.1 | 0.12 |
| 421 | `comparator_sd` | falsch | 0.51 | 0.4 | 0.11 |
| 426 | `intervention_n` | falsch | 49.0 | 55 | 6 |
| 426 | `comparator_n` | falsch | 44.0 | 48 | 4 |
| 426 | `intervention_mean` | falsch | 32.0 | 31.7 | 0.3 |
| 426 | `comparator_mean` | falsch | 20.0 | 19.8 | 0.2 |
| 426 | `intervention_sd` | falsch | 22.0 | 21.6 | 0.4 |
| 426 | `comparator_sd` | falsch | 9.0 | 8.5 | 0.5 |
| 427 | `intervention_n` | falsch | 44.0 | 93 | 49 |
| 427 | `comparator_n` | falsch | 49.0 | 93 | 44 |
| 441 | `intervention_mean` | falsch | 68.6 | 0.37 | 68.23 |
| 441 | `comparator_mean` | falsch | 68.8 | 0.41 | 68.39 |
| 441 | `intervention_sd` | falsch | 7.7 | 0.22 | 7.48 |
| 441 | `comparator_sd` | falsch | 7.5 | 0.07 | 7.43 |
| 449 | `intervention_mean` | fehlend | 0.07 | null | - |
| 449 | `comparator_mean` | fehlend | 0.01 | null | - |
| 449 | `intervention_sd` | fehlend | 0.26 | null | - |
| 449 | `comparator_sd` | fehlend | 0.33 | null | - |
| 500 | `intervention_events` | falsch | 12.0 | 48 | 36 |
| 500 | `comparator_events` | falsch | 10.0 | 45 | 35 |
| 501 | `intervention_events` | falsch | 10.0 | 37 | 27 |
| 501 | `comparator_events` | falsch | 15.0 | 38 | 23 |
| 502 | `intervention_events` | falsch | 2.0 | 7 | 5 |
| 502 | `comparator_events` | falsch | 4.0 | 8 | 4 |
| 512 | `intervention_n` | falsch | 123.0 | 122 | 1 |
| 512 | `comparator_n` | falsch | 122.0 | 121 | 1 |
| 518 | `comparator_n` | falsch | 30.0 | 32 | 2 |
| 519 | `comparator_n` | falsch | 30.0 | 32 | 2 |
| 520 | `comparator_n` | falsch | 30.0 | 32 | 2 |
| 521 | `comparator_n` | falsch | 30.0 | 32 | 2 |
| 522 | `comparator_n` | falsch | 30.0 | 32 | 2 |
| 524 | `intervention_sd` | falsch | 0.46 | 1.09 | 0.63 |
| 524 | `comparator_sd` | falsch | 0.47 | 2.29 | 1.82 |
| 525 | `intervention_mean` | falsch | 18.53 | 17.73 | 0.8 |
| 525 | `comparator_mean` | falsch | 18.99 | 12.13 | 6.86 |
| 525 | `intervention_sd` | falsch | 0.22 | 1.09 | 0.87 |
| 525 | `comparator_sd` | falsch | 0.22 | 2.29 | 2.07 |
| 526 | `intervention_mean` | fehlend | -0.28 | null | - |
| 526 | `comparator_mean` | fehlend | -0.14 | null | - |
| 526 | `intervention_sd` | fehlend | 0.11 | null | - |
| 526 | `comparator_sd` | fehlend | 0.05 | null | - |
| 529 | `intervention_mean` | fehlend | -7.7 | null | - |
| 529 | `comparator_mean` | fehlend | -5.02 | null | - |
| 529 | `intervention_sd` | fehlend | 2.3 | null | - |
| 529 | `comparator_sd` | fehlend | 1.07 | null | - |
| 534 | `intervention_mean` | falsch | 1.13 | 3.18 | 2.05 |
| 534 | `comparator_mean` | falsch | 2.23 | 4.45 | 2.22 |
| 534 | `intervention_sd` | falsch | 1.15 | 2.27 | 1.12 |
| 534 | `comparator_sd` | falsch | 1.57 | 2.16 | 0.59 |
| 547 | `intervention_n` | falsch | 69.0 | 74 | 5 |
| 547 | `comparator_n` | falsch | 68.0 | 72 | 4 |
| 548 | `intervention_n` | fehlend | 69.0 | null | - |
| 548 | `comparator_n` | fehlend | 68.0 | null | - |
| 550 | `intervention_n` | falsch | 18.0 | 17 | 1 |
| 550 | `comparator_n` | falsch | 19.0 | 17 | 2 |
| 551 | `intervention_n` | falsch | 18.0 | 17 | 1 |
| 551 | `comparator_n` | falsch | 19.0 | 17 | 2 |
| 552 | `intervention_n` | falsch | 18.0 | 17 | 1 |
| 552 | `comparator_n` | falsch | 19.0 | 17 | 2 |
| 553 | `intervention_n` | falsch | 18.0 | 17 | 1 |
| 553 | `comparator_n` | falsch | 19.0 | 17 | 2 |
| 554 | `intervention_n` | falsch | 18.0 | 17 | 1 |
| 554 | `comparator_n` | falsch | 19.0 | 17 | 2 |
| 555 | `intervention_n` | falsch | 18.0 | 17 | 1 |
| 555 | `comparator_n` | falsch | 19.0 | 17 | 2 |
| 567 | `intervention_mean` | falsch | -0.7 | 0.5 | 1.2 |
| 567 | `comparator_mean` | falsch | 1.0 | 4 | 3 |
| 567 | `intervention_sd` | falsch | 1.5 | 2.4 | 0.9 |
| 567 | `comparator_sd` | falsch | 1.1 | 2.3 | 1.2 |
| 572 | `intervention_mean` | falsch | -1.4 | 0.7 | 2.1 |
| 572 | `comparator_mean` | falsch | -3.3 | -4 | 0.7 |
| 572 | `intervention_sd` | falsch | 4.2 | 5.9 | 1.7 |
| 572 | `comparator_sd` | falsch | 5.3 | 3.9 | 1.4 |
| 573 | `intervention_mean` | falsch | -3.7 | -1.4 | 2.3 |
| 573 | `comparator_mean` | falsch | -0.8 | -2.7 | 1.9 |
| 573 | `intervention_sd` | falsch | 3.4 | 5.3 | 1.9 |
| 573 | `comparator_sd` | falsch | 3.5 | 4.4 | 0.9 |
| 634 | `intervention_n` | fehlend | 70.0 | null | - |
| 634 | `comparator_n` | fehlend | 70.0 | null | - |
| 634 | `intervention_mean` | fehlend | 1.05 | null | - |
| 634 | `comparator_mean` | fehlend | 0.15 | null | - |
| 634 | `intervention_sd` | fehlend | 2.0 | null | - |
| 634 | `comparator_sd` | fehlend | 1.7 | null | - |
| 664 | `intervention_mean` | fehlend | 101.9 | null | - |
| 664 | `comparator_mean` | fehlend | 97.6 | null | - |
| 664 | `intervention_sd` | fehlend | 35.1 | null | - |
| 664 | `comparator_sd` | fehlend | 20.8 | null | - |
| 665 | `intervention_mean` | fehlend | 103.4 | null | - |
| 665 | `comparator_mean` | fehlend | 97.6 | null | - |
| 665 | `intervention_sd` | fehlend | 28.9 | null | - |
| 665 | `comparator_sd` | fehlend | 20.8 | null | - |
| 666 | `intervention_mean` | fehlend | 206.9 | null | - |
| 666 | `comparator_mean` | fehlend | 184.4 | null | - |
| 666 | `intervention_sd` | fehlend | 36.2 | null | - |
| 666 | `comparator_sd` | fehlend | 37.5 | null | - |
| 667 | `intervention_mean` | fehlend | 207.2 | null | - |
| 667 | `comparator_mean` | fehlend | 184.4 | null | - |
| 667 | `intervention_sd` | fehlend | 42.3 | null | - |
| 667 | `comparator_sd` | fehlend | 37.5 | null | - |
| 668 | `intervention_mean` | fehlend | 194.3 | null | - |
| 668 | `comparator_mean` | fehlend | 181.8 | null | - |
| 668 | `intervention_sd` | fehlend | 63.1 | null | - |
| 668 | `comparator_sd` | fehlend | 61.3 | null | - |
| 669 | `intervention_mean` | fehlend | 200.1 | null | - |
| 669 | `comparator_mean` | fehlend | 181.8 | null | - |
| 669 | `intervention_sd` | fehlend | 55.9 | null | - |
| 669 | `comparator_sd` | fehlend | 61.3 | null | - |
| 674 | `intervention_mean` | falsch | 23.5 | 36.4 | 12.9 |
| 674 | `intervention_sd` | falsch | 26.0 | 32 | 6 |
| 675 | `intervention_n` | falsch | 14.0 | 142 | 128 |
| 675 | `comparator_n` | falsch | 12.0 | 320 | 308 |
| 676 | `intervention_n` | falsch | 14.0 | 12 | 2 |
| 679 | `intervention_n` | fehlend | 16.0 | null | - |
| 679 | `comparator_n` | fehlend | 15.0 | null | - |
| 679 | `intervention_mean` | fehlend | 3.4 | null | - |
| 679 | `comparator_mean` | fehlend | 4.3 | null | - |
| 679 | `intervention_sd` | fehlend | 0.6 | null | - |
| 679 | `comparator_sd` | fehlend | 1.4 | null | - |
| 680 | `intervention_n` | fehlend | 16.0 | null | - |
| 680 | `comparator_n` | fehlend | 15.0 | null | - |
| 680 | `intervention_mean` | fehlend | 2.2 | null | - |
| 680 | `comparator_mean` | fehlend | 2.5 | null | - |
| 680 | `intervention_sd` | fehlend | 0.3 | null | - |
| 680 | `comparator_sd` | fehlend | 0.6 | null | - |
| 681 | `intervention_mean` | falsch | 28.1 | 24.7 | 3.4 |
| 681 | `comparator_mean` | falsch | 27.4 | 32.4 | 5 |
| 681 | `intervention_sd` | falsch | 14.6 | 11.3 | 3.3 |
| 681 | `comparator_sd` | falsch | 13.0 | 13.9 | 0.9 |
| 682 | `intervention_mean` | fehlend | 4.1 | null | - |
| 682 | `comparator_mean` | fehlend | 4.3 | null | - |
| 682 | `intervention_sd` | fehlend | 1.0 | null | - |
| 682 | `comparator_sd` | fehlend | 1.4 | null | - |
| 683 | `intervention_n` | fehlend | 16.0 | null | - |
| 683 | `comparator_n` | fehlend | 15.0 | null | - |
| 683 | `intervention_mean` | fehlend | 2.3 | null | - |
| 683 | `comparator_mean` | fehlend | 2.5 | null | - |
| 683 | `intervention_sd` | fehlend | 0.3 | null | - |
| 683 | `comparator_sd` | fehlend | 0.6 | null | - |
| 684 | `intervention_mean` | fehlend | 31.8 | null | - |
| 684 | `comparator_mean` | fehlend | 27.4 | null | - |
| 684 | `intervention_sd` | fehlend | 14.8 | null | - |
| 684 | `comparator_sd` | fehlend | 13.0 | null | - |

## Einordnung

- `exakt` bedeutet numerische Gleichheit des ausgegebenen Werts mit der Referenz.
- `fehlend` bedeutet: Referenzwert vorhanden, Modellwert `null`.
- `falsch` bedeutet: beide Werte vorhanden, aber nicht numerisch gleich.
- `halluziniert` bedeutet: Feld ist für diesen Outcome-Typ nicht erwartet, das Modell liefert trotzdem einen Wert.
- Die MAE wird nur über gepaarte Werte gebildet; fehlende Werte werden nicht durch 0 oder Schätzungen ersetzt.
- Testlauf nach Output-Freeze; Referenz erst danach geladen.
