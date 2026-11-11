# C1-Dev-Pilot: Ergebnis

Run: `c1_dev_20261111_v6c`

## Kopfzahlen

- Records mit Ausgabe: **26/26**
- Erwartete Felder: **140**
- Abdeckung: **140/140** (100.0%)
- Exakte Treffer: **140/140** (100.0%)
- Fehlend: **0**; falsch: **0**; halluziniert: **0**
- MAE über alle gepaarten erwarteten Felder: **0.0**
- Null-Disziplin auf nicht erwarteten Feldern: **68/68** (100.0%)
- Records mit vollständig exakten Erwartungsfeldern: **26/26**
- Schema-/Parse-Fehler: **0** (keine)

## Feldebene

| Feld | erwartet | vorhanden | exakt | fehlend | falsch | MAE |
|---|---:|---:|---:|---:|---:|---:|
| `intervention_n` | 26 | 26 | 26 | 0 | 0 | 0.0 |
| `comparator_n` | 26 | 26 | 26 | 0 | 0 | 0.0 |
| `intervention_mean` | 18 | 18 | 18 | 0 | 0 | 0.0 |
| `comparator_mean` | 18 | 18 | 18 | 0 | 0 | 0.0 |
| `intervention_sd` | 18 | 18 | 18 | 0 | 0 | 0.0 |
| `comparator_sd` | 18 | 18 | 18 | 0 | 0 | 0.0 |
| `intervention_events` | 8 | 8 | 8 | 0 | 0 | 0.0 |
| `comparator_events` | 8 | 8 | 8 | 0 | 0 | 0.0 |

## Fehlerliste

| Record | Feld | Kategorie | Referenz | Modell | absolute Differenz |
|---:|---|---|---:|---:|---:|
| - | - | keine | - | - | - |

## Einordnung

- `exakt` bedeutet numerische Gleichheit des ausgegebenen Werts mit der Referenz.
- `fehlend` bedeutet: Referenzwert vorhanden, Modellwert `null`.
- `falsch` bedeutet: beide Werte vorhanden, aber nicht numerisch gleich.
- `halluziniert` bedeutet: Feld ist für diesen Outcome-Typ nicht erwartet, das Modell liefert trotzdem einen Wert.
- Die MAE wird nur über gepaarte Werte gebildet; fehlende Werte werden nicht durch 0 oder Schätzungen ersetzt.
- Der Testsplit wurde nicht gelesen und nicht verwendet.
