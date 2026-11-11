# C1-Dev-Pilot: Ergebnis

Run: `c1_dev_20261111_v6`

## Kopfzahlen

- Records mit Ausgabe: **26/26**
- Erwartete Felder: **140**
- Abdeckung: **140/140** (100.0%)
- Exakte Treffer: **135/140** (96.4%)
- Fehlend: **0**; falsch: **5**; halluziniert: **0**
- MAE über alle gepaarten erwarteten Felder: **0.1341**
- Null-Disziplin auf nicht erwarteten Feldern: **68/68** (100.0%)
- Records mit vollständig exakten Erwartungsfeldern: **24/26**
- Schema-/Parse-Fehler: **0** (keine)

## Feldebene

| Feld | erwartet | vorhanden | exakt | fehlend | falsch | MAE |
|---|---:|---:|---:|---:|---:|---:|
| `intervention_n` | 26 | 26 | 25 | 0 | 1 | 0.3846 |
| `comparator_n` | 26 | 26 | 25 | 0 | 1 | 0.3077 |
| `intervention_mean` | 18 | 18 | 17 | 0 | 1 | 0.0256 |
| `comparator_mean` | 18 | 18 | 17 | 0 | 1 | 0.0033 |
| `intervention_sd` | 18 | 18 | 17 | 0 | 1 | 0.0139 |
| `comparator_sd` | 18 | 18 | 18 | 0 | 0 | 0.0 |
| `intervention_events` | 8 | 8 | 8 | 0 | 0 | 0.0 |
| `comparator_events` | 8 | 8 | 8 | 0 | 0 | 0.0 |

## Fehlerliste

| Record | Feld | Kategorie | Referenz | Modell | absolute Differenz |
|---:|---|---|---:|---:|---:|
| 120 | `intervention_n` | falsch | 20.0 | 30 | 10 |
| 120 | `comparator_n` | falsch | 44.0 | 52 | 8 |
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
