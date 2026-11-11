# C1-Dev-Pilot: Ergebnis

Run: `c1_dev_20261111_v4`

## Kopfzahlen

- Records mit Ausgabe: **26/26**
- Erwartete Felder: **140**
- Abdeckung: **138/140** (98.6%)
- Exakte Treffer: **126/140** (90.0%)
- Fehlend: **2**; falsch: **12**; halluziniert: **0**
- MAE über alle gepaarten erwarteten Felder: **0.3052**
- Null-Disziplin auf nicht erwarteten Feldern: **68/68** (100.0%)
- Records mit vollständig exakten Erwartungsfeldern: **22/26**
- Schema-/Parse-Fehler: **0** (keine)

## Feldebene

| Feld | erwartet | vorhanden | exakt | fehlend | falsch | MAE |
|---|---:|---:|---:|---:|---:|---:|
| `intervention_n` | 26 | 25 | 24 | 1 | 1 | 0.4 |
| `comparator_n` | 26 | 25 | 24 | 1 | 1 | 0.32 |
| `intervention_mean` | 18 | 18 | 16 | 0 | 2 | 0.1517 |
| `comparator_mean` | 18 | 18 | 16 | 0 | 2 | 0.0628 |
| `intervention_sd` | 18 | 18 | 16 | 0 | 2 | 0.4917 |
| `comparator_sd` | 18 | 18 | 16 | 0 | 2 | 0.0228 |
| `intervention_events` | 8 | 8 | 7 | 0 | 1 | 0.75 |
| `comparator_events` | 8 | 8 | 7 | 0 | 1 | 0.625 |

## Fehlerliste

| Record | Feld | Kategorie | Referenz | Modell | absolute Differenz |
|---:|---|---|---:|---:|---:|
| 120 | `intervention_n` | falsch | 20.0 | 30 | 10 |
| 120 | `comparator_n` | falsch | 44.0 | 52 | 8 |
| 120 | `intervention_events` | falsch | 8.0 | 2 | 6 |
| 120 | `comparator_events` | falsch | 13.0 | 8 | 5 |
| 224 | `intervention_mean` | falsch | 0.3 | 0.43 | 0.13 |
| 224 | `comparator_mean` | falsch | 0.38 | 1.19 | 0.81 |
| 224 | `intervention_sd` | falsch | 0.79 | 1.04 | 0.25 |
| 224 | `comparator_sd` | falsch | 0.98 | 1.37 | 0.39 |
| 226 | `intervention_n` | fehlend | 35.0 | null | - |
| 226 | `comparator_n` | fehlend | 35.0 | null | - |
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
