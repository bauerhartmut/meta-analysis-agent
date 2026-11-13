# Externer Benchmark v1: Numerische Outcome-Extraktion

Erstellt: 2026-11-13T12:08:20Z

## Zweck und Abgrenzung

Dieser Benchmark vergleicht die vorhandene, eingefrorene C1-Ausgabe mit der kuratierten numerischen Referenz aus Yun et al. 2024. Er startet kein Modell, veraendert keine produktiven Studiendaten und trifft keine klinische Eignungsentscheidung. Er ist **keine A/B-Messung**.

## Datengrundlage

- Referenz: `processed_data/yun_c1_frozen_275.jsonl` (275 Records, 70 Artikel)
- Quelle: Yun et al. 2024, Commit `1bc768d4d098c727c9866eeff909297c38a3e84c`
- Lizenz: Apache-2.0 (repository); article excerpts retain PMC article terms
- Ausgabe `c1_pipeline`: `evaluation/c1_pilot/runs_test/c1_test_20261111_v6c/test_output.jsonl` (249 Records)

## Kopfzahlen

- Vergleichbare Records: **249/275**
- Erwartete numerische Felder: **1308**
- Exakt: **993/1308** (75.9%)
- Mit Rundung/Skalierung akzeptabel: **1005/1308** (76.8%)
- Fehlend: **140**; abweichend: **163**; Referenz unvollstaendig: **0**
- Abdeckung: **89.3%**; MAE gepaart: **1.5211**
- Records vollstaendig exakt: **149**; vollstaendig akzeptabel: **151**
- Vermutete Armvertauschungen: **0**

## Kategorien

| Kategorie | Records | Bedeutung |
|---|---:|---|
| 1 automatisch bestaetigt | 151 | numerisch exakt oder gerundet, kein Schemafehler |
| 2 automatisch widerspruechlich | 98 | abweichend, fehlend, schemawidrig oder Armvertauschung |
| 3 nicht extern validierbar | 26 | keine Ausgabe, unvollstaendige Referenz oder nicht vergleichbar |

Kategorie 1 bestaetigt **nur die numerischen Felder**. Zeitpunkt, Population, Outcome-Text und Quellenstelle bleiben ungeprueft; eine klinisch-wissenschaftliche Freigabe ist das nicht.

## Feldebene

| Feld | erwartet | vorhanden | exakt | Rundung/Skalierung | abweichend | fehlend | exakt % | MAE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `intervention_n` | 249 | 229 | 214 | 0 | 15 | 20 | 85.9% | 1.0742 |
| `comparator_n` | 249 | 229 | 201 | 0 | 28 | 20 | 80.7% | 1.9694 |
| `intervention_mean` | 156 | 135 | 110 | 3 | 22 | 21 | 70.5% | 2.4114 |
| `comparator_mean` | 156 | 135 | 105 | 2 | 28 | 21 | 67.3% | 2.5808 |
| `intervention_sd` | 156 | 135 | 107 | 4 | 24 | 21 | 68.6% | 0.5225 |
| `comparator_sd` | 156 | 135 | 104 | 3 | 28 | 21 | 66.7% | 0.3642 |
| `intervention_events` | 93 | 85 | 76 | 0 | 9 | 8 | 81.7% | 1.8 |
| `comparator_events` | 93 | 85 | 76 | 0 | 9 | 8 | 81.7% | 1.5647 |

## Vergleichskriterien

| Kriterium | Status | Begruendung |
|---|---|---|
| study_identification | nicht_pruefbar | Der Lauf erhielt die Studie als Input; es gab keine freie Studienidentifikation. |
| population | nicht_pruefbar | Die Referenz annotiert keine Population; der Input enthaelt nur ICO. |
| intervention | nicht_pruefbar | Interventionsname ist im Input vorgegeben und wird nicht extrahiert. |
| comparator | nicht_pruefbar | Comparatorsname ist im Input vorgegeben und wird nicht extrahiert. |
| outcome | nicht_pruefbar | Outcome-Text ist im Input vorgegeben; Precision/Recall/F1 der Outcome-Erkennung sind mit diesem Lauf nicht messbar. |
| timepoint | nicht_pruefbar | Yun hat kein Zeitpunktfeld; die Ausgabe hat kein strukturiertes Zeitpunktfeld. |
| n | gemessen | Feldmetriken siehe oben |
| events | gemessen | Feldmetriken siehe oben |
| mean | gemessen | Feldmetriken siehe oben |
| sd | gemessen | Feldmetriken siehe oben |
| source | nicht_pruefbar | Die Referenz hat keine Evidenzspannen; source_note ist Freitext ohne Referenzabgleich. |

## Fehlerklassen

| Klasse | Anzahl |
|---|---:|
| abweichender Wert | 163 |
| fehlender Wert | 140 |
| zulaessige Skalierung (Prozent/Anteil) | 8 |
| zulaessige Rundung | 4 |

Die vollstaendige Einzelliste liegt in `external_benchmark_errors_v1.csv`.

## A/B-Vergleich

Kein A/B-Vergleich: Es liegt keine separate B-Ausgabe vor. Die vorhandene C1-Ausgabe ist ein Pipeline-Lauf, keine unabhaengige menschliche Zweitannotation.

## Grenzen

- Die Referenz ist eine konsolidierte Annotation, kein unabhaengiger blinder Zweitbewerter.
- Yun enthaelt keinen Zeitpunkt, keine Evidenzspanne und keine Populationsannotation.
- Der Lauf prueft keine freie Studien-, Arm- oder Outcome-Erkennung, weil die ICO-Vorgabe im Input lag.
- Die C1-Ausgabe ist ein einzelner eingefrorener Testlauf, keine A/B-Messung.
- Die Referenz selbst kann Fehler enthalten; 1 Record wurde quellenbasiert korrigiert.

## Empfehlung

- Kategorie 1 kann die numerische Sichtpruefung unterstuetzen, aber nicht die Zeitpunkt-, Quellen- und Populationspruefung ersetzen.
- Kategorie 2 ist die Arbeitsliste fuer die manuelle Pruefung.
- Kategorie 3 braucht eine andere Referenz oder eine menschliche Erstpruefung; sie ist kein Pipeline-Fehler.
- Vor einer klinisch-wissenschaftlichen Freigabe bleibt eine fachliche Pruefung von Zeitpunkt, Armzuordnung und Quellenstelle noetig.
