# C1-Dev-Pilot: Ergebnis

Run: `c1_dev_20261111_v3`

## Kopfzahlen

- Records mit Ausgabe: **26/26**
- Erwartete Felder: **140**
- Abdeckung: **134/140** (95.7%)
- Exakte Treffer: **123/140** (87.9%)
- Fehlend: **6**; falsch: **11**; halluziniert: **0**
- MAE über alle gepaarten erwarteten Felder: **0.234**
- Null-Disziplin auf nicht erwarteten Feldern: **68/68** (100.0%)
- Records mit vollständig exakten Erwartungsfeldern: **22/26**
- Schema-/Parse-Fehler: **0** (keine)

## Feldebene

| Feld | erwartet | vorhanden | exakt | fehlend | falsch | MAE |
|---|---:|---:|---:|---:|---:|---:|
| `intervention_n` | 26 | 24 | 23 | 2 | 1 | 0.4167 |
| `comparator_n` | 26 | 24 | 23 | 2 | 1 | 0.3333 |
| `intervention_mean` | 18 | 18 | 16 | 0 | 2 | 0.0328 |
| `comparator_mean` | 18 | 18 | 16 | 0 | 2 | 0.0483 |
| `intervention_sd` | 18 | 18 | 16 | 0 | 2 | 0.0278 |
| `comparator_sd` | 18 | 18 | 17 | 0 | 1 | 0.0217 |
| `intervention_events` | 8 | 7 | 6 | 1 | 1 | 0.8571 |
| `comparator_events` | 8 | 7 | 6 | 1 | 1 | 0.7143 |

## Fehlerliste

| Record | Feld | Kategorie | Referenz | Modell | absolute Differenz |
|---:|---|---|---:|---:|---:|
| 120 | `intervention_n` | falsch | 20.0 | 30 | 10 |
| 120 | `comparator_n` | falsch | 44.0 | 52 | 8 |
| 120 | `intervention_events` | falsch | 8.0 | 2 | 6 |
| 120 | `comparator_events` | falsch | 13.0 | 8 | 5 |
| 190 | `intervention_n` | fehlend | 125.0 | null | - |
| 190 | `comparator_n` | fehlend | 133.0 | null | - |
| 190 | `intervention_events` | fehlend | 52.0 | null | - |
| 190 | `comparator_events` | fehlend | 51.0 | null | - |
| 224 | `intervention_mean` | falsch | 0.3 | 0.43 | 0.13 |
| 224 | `comparator_mean` | falsch | 0.38 | 1.19 | 0.81 |
| 224 | `intervention_sd` | falsch | 0.79 | 1.04 | 0.25 |
| 224 | `comparator_sd` | falsch | 0.98 | 1.37 | 0.39 |
| 226 | `intervention_n` | fehlend | 35.0 | null | - |
| 226 | `comparator_n` | fehlend | 35.0 | null | - |
| 226 | `intervention_mean` | falsch | 25.78 | 25.32 | 0.46 |
| 226 | `comparator_mean` | falsch | 26.53 | 26.59 | 0.06 |
| 226 | `intervention_sd` | falsch | 3.3 | 3.05 | 0.25 |

## Einordnung

- `exakt` bedeutet numerische Gleichheit des ausgegebenen Werts mit der Referenz.
- `fehlend` bedeutet: Referenzwert vorhanden, Modellwert `null`.
- `falsch` bedeutet: beide Werte vorhanden, aber nicht numerisch gleich.
- `halluziniert` bedeutet: Feld ist für diesen Outcome-Typ nicht erwartet, das Modell liefert trotzdem einen Wert.
- Die MAE wird nur über gepaarte Werte gebildet; fehlende Werte werden nicht durch 0 oder Schätzungen ersetzt.
- Der Testsplit wurde nicht gelesen und nicht verwendet.
