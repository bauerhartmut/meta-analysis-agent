# C1-Testlauf v6c: Ergebnis

Run: `c1_test_20261111_v6c`
Status: **COMPLETED**

## Kopfzahlen

- Records mit Ausgabe: **249/249**
- Erwartete Felder: **1308**
- Abdeckung: **1168/1308** (89.3%)
- Exakte Treffer: **992/1308** (75.8%)
- Fehlend: **140**; falsch: **176**; halluziniert: **0**
- MAE: **1.5305**
- Records vollständig exakt: **148/249**
- Parse-/Schemafehler: **0**

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

## Nach Outcome-Typ

| Typ | Records | erwartet | exakt | fehlend | falsch | vollständig exakt |
|---|---:|---:|---:|---:|---:|---:|
| `continuous` | 156 | 936 | 678 | 106 | 152 | 79/156 |
| `binary` | 93 | 372 | 314 | 34 | 24 | 69/93 |

## Einordnung

- Ein einzelner freigegebener Testlauf über alle 249 Records.
- Der Runner hat die Testreferenz nicht geladen (`reference_loaded=false`).
- Nach Testbeginn wurde der Prompt nicht geändert.
- Das Testergebnis wurde nicht zur Prompt-Optimierung verwendet.
- 0 Halluzinationen und 0 Parse-/Schemafehler; die Abweichungen sind fehlende oder falsche Werte.
