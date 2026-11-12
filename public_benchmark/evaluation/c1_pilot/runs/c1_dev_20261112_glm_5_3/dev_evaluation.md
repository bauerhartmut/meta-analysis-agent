# C1-Dev-Pilot: Ergebnis

Run: `c1_dev_20261112_glm_5_3`

## Kopfzahlen

- Records mit Ausgabe: **26/26**
- Erwartete Felder: **140**
- Abdeckung: **34/140** (24.3%)
- Exakte Treffer: **34/140** (24.3%)
- Fehlend: **106**; falsch: **0**; halluziniert: **0**
- MAE über alle gepaarten erwarteten Felder: **0.0**
- Null-Disziplin auf nicht erwarteten Feldern: **68/68** (100.0%)
- Records mit vollständig exakten Erwartungsfeldern: **6/26**
- Schema-/Parse-Fehler: **20** (4, 5, 88, 120, 190, 191, 192, 224, 227, 228, 229, 230, 231, 232, 233, 235, 238, 260, 262, 263)

## Feldebene

| Feld | erwartet | vorhanden | exakt | fehlend | falsch | MAE |
|---|---:|---:|---:|---:|---:|---:|
| `intervention_n` | 26 | 6 | 6 | 20 | 0 | 0.0 |
| `comparator_n` | 26 | 6 | 6 | 20 | 0 | 0.0 |
| `intervention_mean` | 18 | 5 | 5 | 13 | 0 | 0.0 |
| `comparator_mean` | 18 | 5 | 5 | 13 | 0 | 0.0 |
| `intervention_sd` | 18 | 5 | 5 | 13 | 0 | 0.0 |
| `comparator_sd` | 18 | 5 | 5 | 13 | 0 | 0.0 |
| `intervention_events` | 8 | 1 | 1 | 7 | 0 | 0.0 |
| `comparator_events` | 8 | 1 | 1 | 7 | 0 | 0.0 |

## Fehlerliste

| Record | Feld | Kategorie | Referenz | Modell | absolute Differenz |
|---:|---|---|---:|---:|---:|
| 4 | `intervention_n` | fehlend | 30.0 | null | - |
| 4 | `comparator_n` | fehlend | 30.0 | null | - |
| 4 | `intervention_mean` | fehlend | 47.5 | null | - |
| 4 | `comparator_mean` | fehlend | 26.5 | null | - |
| 4 | `intervention_sd` | fehlend | 38.9 | null | - |
| 4 | `comparator_sd` | fehlend | 27.4 | null | - |
| 5 | `intervention_n` | fehlend | 30.0 | null | - |
| 5 | `comparator_n` | fehlend | 30.0 | null | - |
| 5 | `intervention_mean` | fehlend | 3.59 | null | - |
| 5 | `comparator_mean` | fehlend | 2.19 | null | - |
| 5 | `intervention_sd` | fehlend | 2.35 | null | - |
| 5 | `comparator_sd` | fehlend | 1.63 | null | - |
| 88 | `intervention_n` | fehlend | 19.0 | null | - |
| 88 | `comparator_n` | fehlend | 23.0 | null | - |
| 88 | `intervention_mean` | fehlend | 117.63 | null | - |
| 88 | `comparator_mean` | fehlend | 158.52 | null | - |
| 88 | `intervention_sd` | fehlend | 19.01 | null | - |
| 88 | `comparator_sd` | fehlend | 23.19 | null | - |
| 120 | `intervention_n` | fehlend | 20.0 | null | - |
| 120 | `comparator_n` | fehlend | 44.0 | null | - |
| 120 | `intervention_events` | fehlend | 8.0 | null | - |
| 120 | `comparator_events` | fehlend | 13.0 | null | - |
| 190 | `intervention_n` | fehlend | 125.0 | null | - |
| 190 | `comparator_n` | fehlend | 133.0 | null | - |
| 190 | `intervention_events` | fehlend | 52.0 | null | - |
| 190 | `comparator_events` | fehlend | 51.0 | null | - |
| 191 | `intervention_n` | fehlend | 125.0 | null | - |
| 191 | `comparator_n` | fehlend | 133.0 | null | - |
| 191 | `intervention_events` | fehlend | 49.0 | null | - |
| 191 | `comparator_events` | fehlend | 64.0 | null | - |
| 192 | `intervention_n` | fehlend | 125.0 | null | - |
| 192 | `comparator_n` | fehlend | 133.0 | null | - |
| 192 | `intervention_events` | fehlend | 86.0 | null | - |
| 192 | `comparator_events` | fehlend | 78.0 | null | - |
| 224 | `intervention_n` | fehlend | 35.0 | null | - |
| 224 | `comparator_n` | fehlend | 35.0 | null | - |
| 224 | `intervention_mean` | fehlend | 0.3 | null | - |
| 224 | `comparator_mean` | fehlend | 0.38 | null | - |
| 224 | `intervention_sd` | fehlend | 0.79 | null | - |
| 224 | `comparator_sd` | fehlend | 0.98 | null | - |
| 227 | `intervention_n` | fehlend | 35.0 | null | - |
| 227 | `comparator_n` | fehlend | 35.0 | null | - |
| 227 | `intervention_mean` | fehlend | 5.28 | null | - |
| 227 | `comparator_mean` | fehlend | 5.75 | null | - |
| 227 | `intervention_sd` | fehlend | 2.34 | null | - |
| 227 | `comparator_sd` | fehlend | 2.34 | null | - |
| 228 | `intervention_n` | fehlend | 35.0 | null | - |
| 228 | `comparator_n` | fehlend | 35.0 | null | - |
| 228 | `intervention_mean` | fehlend | 13.21 | null | - |
| 228 | `comparator_mean` | fehlend | 13.8 | null | - |
| 228 | `intervention_sd` | fehlend | 1.44 | null | - |
| 228 | `comparator_sd` | fehlend | 1.14 | null | - |
| 229 | `intervention_n` | fehlend | 35.0 | null | - |
| 229 | `comparator_n` | fehlend | 35.0 | null | - |
| 229 | `intervention_mean` | fehlend | 487.33 | null | - |
| 229 | `comparator_mean` | fehlend | 453.57 | null | - |
| 229 | `intervention_sd` | fehlend | 111.47 | null | - |
| 229 | `comparator_sd` | fehlend | 60.87 | null | - |
| 230 | `intervention_n` | fehlend | 35.0 | null | - |
| 230 | `comparator_n` | fehlend | 35.0 | null | - |
| 230 | `intervention_mean` | fehlend | 35.53 | null | - |
| 230 | `comparator_mean` | fehlend | 26.83 | null | - |
| 230 | `intervention_sd` | fehlend | 5.87 | null | - |
| 230 | `comparator_sd` | fehlend | 5.47 | null | - |
| 231 | `intervention_n` | fehlend | 35.0 | null | - |
| 231 | `comparator_n` | fehlend | 35.0 | null | - |
| 231 | `intervention_mean` | fehlend | 17.83 | null | - |
| 231 | `comparator_mean` | fehlend | 12.48 | null | - |
| 231 | `intervention_sd` | fehlend | 2.7 | null | - |
| 231 | `comparator_sd` | fehlend | 2.9 | null | - |
| 232 | `intervention_n` | fehlend | 35.0 | null | - |
| 232 | `comparator_n` | fehlend | 35.0 | null | - |
| 232 | `intervention_mean` | fehlend | 13.21 | null | - |
| 232 | `comparator_mean` | fehlend | 13.8 | null | - |
| 232 | `intervention_sd` | fehlend | 1.44 | null | - |
| 232 | `comparator_sd` | fehlend | 1.14 | null | - |
| 233 | `intervention_n` | fehlend | 35.0 | null | - |
| 233 | `comparator_n` | fehlend | 35.0 | null | - |
| 233 | `intervention_mean` | fehlend | 39.1 | null | - |
| 233 | `comparator_mean` | fehlend | 37.99 | null | - |
| 233 | `intervention_sd` | fehlend | 2.76 | null | - |
| 233 | `comparator_sd` | fehlend | 2.14 | null | - |
| 235 | `intervention_n` | fehlend | 35.0 | null | - |
| 235 | `comparator_n` | fehlend | 35.0 | null | - |
| 235 | `intervention_mean` | fehlend | 13.6 | null | - |
| 235 | `comparator_mean` | fehlend | 14.71 | null | - |
| 235 | `intervention_sd` | fehlend | 3.05 | null | - |
| 235 | `comparator_sd` | fehlend | 3.87 | null | - |
| 238 | `intervention_n` | fehlend | 35.0 | null | - |
| 238 | `comparator_n` | fehlend | 35.0 | null | - |
| 238 | `intervention_mean` | fehlend | 80.5 | null | - |
| 238 | `comparator_mean` | fehlend | 69.89 | null | - |
| 238 | `intervention_sd` | fehlend | 9.97 | null | - |
| 238 | `comparator_sd` | fehlend | 1.59 | null | - |
| 260 | `intervention_n` | fehlend | 101.0 | null | - |
| 260 | `comparator_n` | fehlend | 99.0 | null | - |
| 260 | `intervention_events` | fehlend | 79.0 | null | - |
| 260 | `comparator_events` | fehlend | 62.0 | null | - |
| 262 | `intervention_n` | fehlend | 115.0 | null | - |
| 262 | `comparator_n` | fehlend | 112.0 | null | - |
| 262 | `intervention_events` | fehlend | 69.0 | null | - |
| 262 | `comparator_events` | fehlend | 79.0 | null | - |
| 263 | `intervention_n` | fehlend | 112.0 | null | - |
| 263 | `comparator_n` | fehlend | 112.0 | null | - |
| 263 | `intervention_events` | fehlend | 72.0 | null | - |
| 263 | `comparator_events` | fehlend | 79.0 | null | - |

## Einordnung

- `exakt` bedeutet numerische Gleichheit des ausgegebenen Werts mit der Referenz.
- `fehlend` bedeutet: Referenzwert vorhanden, Modellwert `null`.
- `falsch` bedeutet: beide Werte vorhanden, aber nicht numerisch gleich.
- `halluziniert` bedeutet: Feld ist für diesen Outcome-Typ nicht erwartet, das Modell liefert trotzdem einen Wert.
- Die MAE wird nur über gepaarte Werte gebildet; fehlende Werte werden nicht durch 0 oder Schätzungen ersetzt.
- Der Testsplit wurde nicht gelesen und nicht verwendet.
