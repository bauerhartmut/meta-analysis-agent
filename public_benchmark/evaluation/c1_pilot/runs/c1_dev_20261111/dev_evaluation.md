# C1-Dev-Pilot: Ergebnis

Run: `c1_dev_20261111`

## Kopfzahlen

- Records mit Ausgabe: **26/26**
- Erwartete Felder: **140**
- Abdeckung: **136/140** (97.1%)
- Exakte Treffer: **93/140** (66.4%)
- Fehlend: **4**; falsch: **43**; halluziniert: **0**
- MAE über alle gepaarten erwarteten Felder: **4.7066**
- Null-Disziplin auf nicht erwarteten Feldern: **68/68** (100.0%)
- Records mit vollständig exakten Erwartungsfeldern: **14/26**
- Schema-/Parse-Fehler: **0** (keine)

## Feldebene

| Feld | erwartet | vorhanden | exakt | fehlend | falsch | MAE |
|---|---:|---:|---:|---:|---:|---:|
| `intervention_n` | 26 | 25 | 24 | 1 | 1 | 0.4 |
| `comparator_n` | 26 | 25 | 24 | 1 | 1 | 0.32 |
| `intervention_mean` | 18 | 18 | 8 | 0 | 10 | 21.3306 |
| `comparator_mean` | 18 | 18 | 8 | 0 | 10 | 1.1261 |
| `intervention_sd` | 18 | 18 | 8 | 0 | 10 | 9.7594 |
| `comparator_sd` | 18 | 18 | 9 | 0 | 9 | 1.2339 |
| `intervention_events` | 8 | 7 | 6 | 1 | 1 | 1.1429 |
| `comparator_events` | 8 | 7 | 6 | 1 | 1 | 1.7143 |

## Fehlerliste

| Record | Feld | Kategorie | Referenz | Modell | absolute Differenz |
|---:|---|---|---:|---:|---:|
| 120 | `intervention_n` | falsch | 20.0 | 30 | 10 |
| 120 | `comparator_n` | falsch | 44.0 | 52 | 8 |
| 120 | `intervention_events` | falsch | 8.0 | 0 | 8 |
| 120 | `comparator_events` | falsch | 13.0 | 1 | 12 |
| 190 | `intervention_n` | fehlend | 125.0 | null | - |
| 190 | `comparator_n` | fehlend | 133.0 | null | - |
| 190 | `intervention_events` | fehlend | 52.0 | null | - |
| 190 | `comparator_events` | fehlend | 51.0 | null | - |
| 224 | `intervention_mean` | falsch | 0.3 | 0.43 | 0.13 |
| 224 | `comparator_mean` | falsch | 0.38 | 1.19 | 0.81 |
| 224 | `intervention_sd` | falsch | 0.79 | 1.04 | 0.25 |
| 224 | `comparator_sd` | falsch | 0.98 | 1.37 | 0.39 |
| 225 | `intervention_mean` | falsch | 0.33 | 0.06 | 0.27 |
| 225 | `comparator_mean` | falsch | 0.7 | 0.58 | 0.12 |
| 225 | `intervention_sd` | falsch | 1.06 | 0.36 | 0.7 |
| 225 | `comparator_sd` | falsch | 1.24 | 0.92 | 0.32 |
| 226 | `intervention_mean` | falsch | 25.78 | 25.32 | 0.46 |
| 226 | `comparator_mean` | falsch | 26.53 | 26.59 | 0.06 |
| 226 | `intervention_sd` | falsch | 3.3 | 3.05 | 0.25 |
| 227 | `intervention_mean` | falsch | 5.28 | 4.26 | 1.02 |
| 227 | `comparator_mean` | falsch | 5.75 | 5.91 | 0.16 |
| 227 | `intervention_sd` | falsch | 2.34 | 1.76 | 0.58 |
| 227 | `comparator_sd` | falsch | 2.34 | 2.21 | 0.13 |
| 229 | `intervention_mean` | falsch | 487.33 | 854 | 366.67 |
| 229 | `comparator_mean` | falsch | 453.57 | 470 | 16.43 |
| 229 | `intervention_sd` | falsch | 111.47 | 271.6 | 160.13 |
| 229 | `comparator_sd` | falsch | 60.87 | 80.46 | 19.59 |
| 234 | `intervention_mean` | falsch | 10.8 | 13.5 | 2.7 |
| 234 | `comparator_mean` | falsch | 4.9 | 5.51 | 0.61 |
| 234 | `intervention_sd` | falsch | 2.0 | 1.79 | 0.21 |
| 234 | `comparator_sd` | falsch | 1.88 | 2.39 | 0.51 |
| 235 | `intervention_mean` | falsch | 13.6 | 17.2 | 3.6 |
| 235 | `comparator_mean` | falsch | 14.71 | 14.1 | 0.61 |
| 235 | `intervention_sd` | falsch | 3.05 | 3.46 | 0.41 |
| 235 | `comparator_sd` | falsch | 3.87 | 3.82 | 0.05 |
| 236 | `intervention_mean` | falsch | 26.6 | 30.4 | 3.8 |
| 236 | `comparator_mean` | falsch | 19.89 | 19.85 | 0.04 |
| 236 | `intervention_sd` | falsch | 4.43 | 2.83 | 1.6 |
| 236 | `comparator_sd` | falsch | 4.56 | 5.24 | 0.68 |
| 237 | `intervention_mean` | falsch | 27.3 | 30 | 2.7 |
| 237 | `comparator_mean` | falsch | 26.0 | 24.89 | 1.11 |
| 237 | `intervention_sd` | falsch | 6.77 | 3.83 | 2.94 |
| 237 | `comparator_sd` | falsch | 4.68 | 5.2 | 0.52 |
| 238 | `intervention_mean` | falsch | 80.5 | 83.1 | 2.6 |
| 238 | `comparator_mean` | falsch | 69.89 | 69.57 | 0.32 |
| 238 | `intervention_sd` | falsch | 9.97 | 1.37 | 8.6 |
| 238 | `comparator_sd` | falsch | 1.59 | 1.61 | 0.02 |

## Einordnung

- `exakt` bedeutet numerische Gleichheit des ausgegebenen Werts mit der Referenz.
- `fehlend` bedeutet: Referenzwert vorhanden, Modellwert `null`.
- `falsch` bedeutet: beide Werte vorhanden, aber nicht numerisch gleich.
- `halluziniert` bedeutet: Feld ist für diesen Outcome-Typ nicht erwartet, das Modell liefert trotzdem einen Wert.
- Die MAE wird nur über gepaarte Werte gebildet; fehlende Werte werden nicht durch 0 oder Schätzungen ersetzt.
- Der Testsplit wurde nicht gelesen und nicht verwendet.
