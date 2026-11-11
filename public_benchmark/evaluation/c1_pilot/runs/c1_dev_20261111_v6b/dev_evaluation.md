# C1-Dev-Pilot: Ergebnis

Run: `c1_dev_20261111_v6b`

## Kopfzahlen

- Records mit Ausgabe: **26/26**
- Erwartete Felder: **140**
- Abdeckung: **128/140** (91.4%)
- Exakte Treffer: **125/140** (89.3%)
- Fehlend: **12**; falsch: **3**; halluziniert: **0**
- MAE über alle gepaarten erwarteten Felder: **0.006**
- Null-Disziplin auf nicht erwarteten Feldern: **68/68** (100.0%)
- Records mit vollständig exakten Erwartungsfeldern: **22/26**
- Schema-/Parse-Fehler: **0** (keine)

## Feldebene

| Feld | erwartet | vorhanden | exakt | fehlend | falsch | MAE |
|---|---:|---:|---:|---:|---:|---:|
| `intervention_n` | 26 | 26 | 26 | 0 | 0 | 0.0 |
| `comparator_n` | 26 | 26 | 26 | 0 | 0 | 0.0 |
| `intervention_mean` | 18 | 15 | 14 | 3 | 1 | 0.0307 |
| `comparator_mean` | 18 | 15 | 14 | 3 | 1 | 0.004 |
| `intervention_sd` | 18 | 15 | 14 | 3 | 1 | 0.0167 |
| `comparator_sd` | 18 | 15 | 15 | 3 | 0 | 0.0 |
| `intervention_events` | 8 | 8 | 8 | 0 | 0 | 0.0 |
| `comparator_events` | 8 | 8 | 8 | 0 | 0 | 0.0 |

## Fehlerliste

| Record | Feld | Kategorie | Referenz | Modell | absolute Differenz |
|---:|---|---|---:|---:|---:|
| 226 | `intervention_mean` | falsch | 25.78 | 25.32 | 0.46 |
| 226 | `comparator_mean` | falsch | 26.53 | 26.59 | 0.06 |
| 226 | `intervention_sd` | falsch | 3.3 | 3.05 | 0.25 |
| 230 | `intervention_mean` | fehlend | 35.53 | null | - |
| 230 | `comparator_mean` | fehlend | 26.83 | null | - |
| 230 | `intervention_sd` | fehlend | 5.87 | null | - |
| 230 | `comparator_sd` | fehlend | 5.47 | null | - |
| 231 | `intervention_mean` | fehlend | 17.83 | null | - |
| 231 | `comparator_mean` | fehlend | 12.48 | null | - |
| 231 | `intervention_sd` | fehlend | 2.7 | null | - |
| 231 | `comparator_sd` | fehlend | 2.9 | null | - |
| 232 | `intervention_mean` | fehlend | 13.21 | null | - |
| 232 | `comparator_mean` | fehlend | 13.8 | null | - |
| 232 | `intervention_sd` | fehlend | 1.44 | null | - |
| 232 | `comparator_sd` | fehlend | 1.14 | null | - |

## Einordnung

- `exakt` bedeutet numerische Gleichheit des ausgegebenen Werts mit der Referenz.
- `fehlend` bedeutet: Referenzwert vorhanden, Modellwert `null`.
- `falsch` bedeutet: beide Werte vorhanden, aber nicht numerisch gleich.
- `halluziniert` bedeutet: Feld ist für diesen Outcome-Typ nicht erwartet, das Modell liefert trotzdem einen Wert.
- Die MAE wird nur über gepaarte Werte gebildet; fehlende Werte werden nicht durch 0 oder Schätzungen ersetzt.
- Der Testsplit wurde nicht gelesen und nicht verwendet.
