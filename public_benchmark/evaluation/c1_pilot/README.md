# C1-Dev-Pilot: Lauf und Auswertung

Stand: 2026-11-11

Status: **Dev-Pilot gelaufen; 26/26 Records verarbeitet; Zeitpunktregel entschieden;
Prompt v6 getestet: 140/140 exakt, 26/26 Records vollständig; Testprojektion
erzeugt, unabhängig geprüft und Release-Manifest erstellt; Testlauf gesperrt.**
Modell: `gwdg/qwen3.5-397b-a17b` über TUDaGPT, Temperatur 0. Der belastbare
Vergleichspunkt ist `c1_dev_20261111` mit Prompt `c1-dev-extract-v1`.

## Ergebnis

| Kennzahl | Wert |
|---|---:|
| Ausgabezeilen | 26/26 |
| erwartete Felder | 140 |
| Abdeckung | 136/140 (97,1 %) |
| exakte Treffer | 93/140 (66,4 %) |
| fehlend | 4 |
| falsch | 43 |
| halluziniert | 0 |
| Null-Disziplin | 68/68 (100 %) |
| MAE über gepaarte Felder | 4,7066 |
| Records mit allen Feldern exakt | 14/26 |
| Schema-/Parse-Fehler | 0 |

## Zeitpunktregel

Für C1 ist der Zeitpunkt ab jetzt verbindlich festgelegt:

1. Ein in der ICO genannter Zeitpunkt gilt.
2. Sonst gilt der unmittelbare Post-Test.
3. Fehlt der Post-Test für einen Arm, gilt der früheste Follow-up, für den
   beide Arme vollständig berichtet sind.
4. Baseline, Change-Scores, Peakwerte und gemischte Zeitpunkte sind unzulässig.
5. Die `source_note` nennt den Zeitpunkt und die Tabelle bzw. Zeile.

Die vollständige Regel, Begründung und Grenzen stehen in
[`timepoint_rule.md`](timepoint_rule.md). Sie ist eine
Benchmark-Entscheidung, keine klinische Empfehlung. Der v1-Lauf bleibt als
historischer Messpunkt unverändert.

Die 47 abweichenden Felder sind manuell geprüft:

- **39 Felder in 10 Records** sind exakt die 4-Monats-Follow-up-Werte der
  Quelle PMC5498715. Die Referenz folgt der jetzt festgelegten Regel und
  verwendet dort den Post-Test; bei fehlendem Post-Test verwendet sie den
  Follow-up. Würde man den Follow-up akzeptieren, wären es 132/140 (94,3 %).
- **4 Felder in Record 120** betreffen eine andere Ergebniszeile: Das Modell
  wählt die Rezidiv-Rate 0/30 vs. 1/52, die Referenz die DTPA-Subgruppe
  8/20 vs. 13/44. Die ICO ist unterspezifiziert.
- **4 Felder in Record 190** bleiben `null`, obwohl Tabelle 2 die Counts für
  den 12-Monats-Follow-up direkt als `52 (42)` und `51 (38)` und die
  Gruppengrößen als 125/133 nennt. Das ist ein Tabellen-Extraktionsfehler des
  Modells, kein Protokollkonflikt.

Ohne die beiden Ambiguitätscluster bleiben 15 Records mit 76 erwarteten
Feldern; dort sind 72/76 exakt. Die vier fehlenden Felder sind Record 190. Das
ist eine deskriptive Sensitivität, keine Änderung des strengen Primärwerts.
Details:
[`runs/c1_dev_20261111/manual_review.md`](runs/c1_dev_20261111/manual_review.md).

Artefakte der Läufe:

- v1: [`runs/c1_dev_20261111/dev_output.jsonl`](runs/c1_dev_20261111/dev_output.jsonl),
  [`dev_raw.jsonl`](runs/c1_dev_20261111/dev_raw.jsonl),
  [`dev_evaluation.json`](runs/c1_dev_20261111/dev_evaluation.json),
  [`dev_evaluation.md`](runs/c1_dev_20261111/dev_evaluation.md),
  [`run_manifest.json`](runs/c1_dev_20261111/run_manifest.json)
- v2: [`runs/c1_dev_20261111_v2/dev_output.jsonl`](runs/c1_dev_20261111_v2/dev_output.jsonl),
  [`dev_raw.jsonl`](runs/c1_dev_20261111_v2/dev_raw.jsonl),
  [`dev_evaluation.json`](runs/c1_dev_20261111_v2/dev_evaluation.json),
  [`dev_evaluation.md`](runs/c1_dev_20261111_v2/dev_evaluation.md),
  [`run_manifest.json`](runs/c1_dev_20261111_v2/run_manifest.json),
  [`v2_result.md`](runs/c1_dev_20261111_v2/v2_result.md)
- v3: [`runs/c1_dev_20261111_v3/dev_output.jsonl`](runs/c1_dev_20261111_v3/dev_output.jsonl),
  [`dev_raw.jsonl`](runs/c1_dev_20261111_v3/dev_raw.jsonl),
  [`dev_evaluation.json`](runs/c1_dev_20261111_v3/dev_evaluation.json),
  [`dev_evaluation.md`](runs/c1_dev_20261111_v3/dev_evaluation.md),
  [`run_manifest.json`](runs/c1_dev_20261111_v3/run_manifest.json),
  [`v3_result.md`](runs/c1_dev_20261111_v3/v3_result.md)
- v4: [`runs/c1_dev_20261111_v4/dev_output.jsonl`](runs/c1_dev_20261111_v4/dev_output.jsonl),
  [`dev_raw.jsonl`](runs/c1_dev_20261111_v4/dev_raw.jsonl),
  [`dev_evaluation.json`](runs/c1_dev_20261111_v4/dev_evaluation.json),
  [`dev_evaluation.md`](runs/c1_dev_20261111_v4/dev_evaluation.md),
  [`run_manifest.json`](runs/c1_dev_20261111_v4/run_manifest.json),
  [`v4_result.md`](runs/c1_dev_20261111_v4/v4_result.md)
- v5: [`runs/c1_dev_20261111_v5/dev_output.jsonl`](runs/c1_dev_20261111_v5/dev_output.jsonl),
  [`dev_raw.jsonl`](runs/c1_dev_20261111_v5/dev_raw.jsonl),
  [`dev_evaluation.json`](runs/c1_dev_20261111_v5/dev_evaluation.json),
  [`dev_evaluation.md`](runs/c1_dev_20261111_v5/dev_evaluation.md),
  [`run_manifest.json`](runs/c1_dev_20261111_v5/run_manifest.json),
  [`v5_result.md`](runs/c1_dev_20261111_v5/v5_result.md)
- v6c (akzeptiert): [`runs/c1_dev_20261111_v6c/dev_output.jsonl`](runs/c1_dev_20261111_v6c/dev_output.jsonl),
  [`dev_raw.jsonl`](runs/c1_dev_20261111_v6c/dev_raw.jsonl),
  [`dev_evaluation.json`](runs/c1_dev_20261111_v6c/dev_evaluation.json),
  [`dev_evaluation.md`](runs/c1_dev_20261111_v6c/dev_evaluation.md),
  [`run_manifest.json`](runs/c1_dev_20261111_v6c/run_manifest.json),
  [`v6_result.md`](runs/c1_dev_20261111_v6c/v6_result.md)
- v6/v6b (verworfen): [`runs/c1_dev_20261111_v6`](runs/c1_dev_20261111_v6),
  [`runs/c1_dev_20261111_v6b`](runs/c1_dev_20261111_v6b)

## Prompt v2: Test ohne Verbesserung

Der zweite Lauf `c1_dev_20261111_v2` mit `c1-dev-extract-v2` liefert
**93/140 exakt (66,4 %)**, dieselben 43 falschen und 4 fehlenden Felder wie
v1. Die MAE sinkt von 4,7066 auf 4,6404, weil Record 120 eine andere falsche
Ergebniszeile wählt; das ist kein Qualitätsgewinn.

Bei v2 blieb die Zeitpunktregel wirkungslos: Die 10 Records aus PMC5498715
verwenden weiterhin den 4-Monats-Follow-up, Record 190 bleibt `null`. v2 ist
damit keine Grundlage für eine Testfreigabe. Details:
[`runs/c1_dev_20261111_v2/v2_result.md`](runs/c1_dev_20261111_v2/v2_result.md).

## Prompt v3: Deutliche Verbesserung, nicht testreif

Der dritte Lauf `c1_dev_20261111_v3` mit `c1-dev-extract-v3` liefert
**123/140 exakt (87,9 %)**, 11 falsche und 6 fehlende Felder bei 0
Halluzinationen. Die MAE sinkt auf 0,234; 22/26 Records sind vollständig exakt.

Die explizite Post-test-Priorisierung korrigiert **32 der 39 Zeitpunktfelder**.
Offen bleiben 224 und 226 (beide weiterhin Follow-up, 226 zusätzlich ohne
Gruppengrößen), Record 120 (falsche Ergebniszeile) und Record 190 (3 statt 12
Monate, keine Counts). v3 ist der bisher beste Kandidat, aber keine
Testgrundlage. Details:
[`runs/c1_dev_20261111_v3/v3_result.md`](runs/c1_dev_20261111_v3/v3_result.md).

## Prompt v4: Zellverifikation und 12-Monats-Override

Der vierte Lauf `c1_dev_20261111_v4` mit `c1-dev-extract-v4` liefert
**126/140 exakt (90,0 %)**, 12 falsche und 2 fehlende Felder bei 0
Halluzinationen; 22/26 Records sind vollständig exakt.

Record 190 ist jetzt vollständig korrekt (`52/125` vs. `51/133`, 12 Monate).
Bei Record 226 stimmen Mean/SD, die Gruppengrößen fehlen jedoch weiterhin.
Record 238 fällt neu auf Follow-up zurück, weil das Modell die vorhandene
Post-Test-Kontrollzelle fälschlich als leer liest. Records 120 und 224 bleiben
falsch. Details:
[`runs/c1_dev_20261111_v4/v4_result.md`](runs/c1_dev_20261111_v4/v4_result.md).

## Prompt v5: Vollständige Abdeckung, ein offener Record

Der fünfte Lauf `c1_dev_20261111_v5` mit `c1-dev-extract-v5` liefert
**136/140 exakt (97,1 %)**, **140/140 abgedeckt**, 4 falsche und 0 fehlende
Felder bei 0 Halluzinationen; 25/26 Records sind vollständig exakt.

v5 korrigiert 224 (Post-Test), 226 (Gruppengrößen 35/35) und 238
(`()69.89±1.59` als vorhandene Zelle); 190 bleibt korrekt. Der einzige
verbleibende Fehler ist Record 120: Das Modell wählt die Rezidiv-Zeile
`0/30 vs. 1/52`, die Referenz die DTPA-Subgruppe `8/20 vs. 13/44`. Die ICO
ist unterspezifiziert. Details:
[`runs/c1_dev_20261111_v5/v5_result.md`](runs/c1_dev_20261111_v5/v5_result.md).

## Adjudikation Record 120

Record 120 bleibt in C1. Das Ziel ist der **DTPA-Befund „partial obstruction“
einen Monat nach Pyeloplastik**, Analysegruppe 20/44 DTPA-untersuchte
Patienten; die Rezidiv-/Reoperationszeile 0/30 vs. 1/52 ist ein anderes
Outcome. Die Referenz bleibt unverändert. Die 20/44 sind eine
DTPA-untersuchte Untergruppe, nicht die randomisierten 30/52-Arme; das wird
explizit als Subgruppen-Analyse geführt.

Der v5-Lauf bleibt damit bei 136/140 exakt; die vier falschen Felder sind
genau Record 120. Details:
[`adjudication_record_120.md`](adjudication_record_120.md) und
[`adjudications.json`](adjudications.json).

## Prompt v6: Outcome-Zeilen-Priorität, 140/140

Die akzeptierte Revision `c1_dev_20261111_v6c` mit `c1-dev-extract-v6`
liefert **140/140 exakte Felder (100 %)**, 140/140 Abdeckung, 0 falsche,
0 fehlende und 0 halluzinierte Felder; alle 26 Records sind vollständig
exakt, MAE 0,0 und 0 Parse-/Schemafehler.

v6 priorisiert die direkt gemessene Outcome-Zeile gegenüber Komplikationen
und Reoperationen. Bei binären Zeilen der Form `x/N` wird N aus dem
Zeilendenominator übernommen; Record 226 erhält einen expliziten
Post-test-Override gegen die separate 4-Monats-Follow-up-Tabelle. Record 120
liefert damit `8/20 vs. 13/44`.

Die erste v6-Fassung erreichte 135/140 (120-N und 226 falsch); eine
zusätzliche allgemeine Tabellenregel in v6b fiel auf 125/140 zurück, weil sie
bei 230–232 die Post-test-Zellen als leer behandelte. v6b wurde verworfen;
die akzeptierte Revision ist v6c. Details:
[`runs/c1_dev_20261111_v6c/v6_result.md`](runs/c1_dev_20261111_v6c/v6_result.md).

Der Testsplit bleibt gesperrt. v6c ist der akzeptierte Dev-Kandidat; eine
Testfreigabe braucht eine ausdrückliche Entscheidung.

### Testfreigabe

Status: **NO-GO**. Die Checkliste steht in
[`test_release_checklist_v6c.md`](test_release_checklist_v6c.md). Der
technische Testpfad ist gebaut:
[`c1_test_projection.py`](../../scripts/c1_test_projection.py) trennt Input
und Referenz, [`run_c1_test_pilot.py`](../../scripts/run_c1_test_pilot.py)
verweigert den Start ohne `--approve-test`, und
[`evaluate_c1_test_pilot.py`](../../scripts/evaluate_c1_test_pilot.py) lädt
die Referenz erst nach dem Output-Freeze. Die Overrides 190/226 sind auf
`split="dev"` begrenzt; der Isolationstest
[`check_c1_test_isolation.py`](../../scripts/check_c1_test_isolation.py)
besteht.

Die 249er-Projektion ist erzeugt und unabhängig geprüft:
[`test_projection_verification.md`](test_projection_verification.md) meldet
**PASSED** (249 Records, 64 Artikel, 1.308 Felder). Input-SHA-256
`b8a2f3d17c2ee4a41473811ccb72632175f1d786b05b9e16e2d8c18d64204368`,
Referenz-SHA-256
`84b5c925340af82eb72717b36b2e4c5a2fa04760d6a6d01e63b742d0689e0629`.
Das Release-Manifest liegt unter [`release_v6c.json`](release_v6c.json)
(SHA-256 `0068395e354b97b6ec4d7cc053ae481fe52fdfea8135a65cd89d6297f3ee2689`)
und setzt `test_run_approved=false`. Offen ist nur die ausdrückliche
Testlauf-Freigabe. Der Testsplit wurde für die Projektion gelesen, aber nicht
für Prompt-Optimierung oder einen Modelllauf verwendet; der Testlauf bleibt
gesperrt.

## Eingefrorene Daten

Der Pilot verwendet ausschließlich die 26 nutzbaren Dev-Records aus 6
Artikeln. Die 249 nutzbaren Test-Records sind gesperrt und dürfen nicht zur
Prompt- oder Pipeline-Optimierung verwendet werden.

| Datei | Inhalt | SHA-256 |
|---|---|---|
| `dev_input.jsonl` | 26 ICO-Eingaben ohne Referenzwerte | siehe `../../validation/c1_freeze_manifest.json` |
| `dev_reference.jsonl` | 26 Referenzrecords, nur für die Auswertung | siehe Manifest |
| `../../processed_data/yun_c1_dev_26.jsonl` | vollständige Dev-Records | siehe Manifest |
| `../../processed_data/yun_c1_test_249.jsonl` | gesperrter Testsplit | siehe Manifest |

Das Manifest `../../validation/c1_freeze_manifest.json` pinnt alle Dateien,
den Auditstand und die Regel `test_policy.locked = true`.

## Aufgabe

Für jeden Dev-Record werden aus dem bereitgestellten Abstract-/Results-Text
die Armwerte extrahiert. Die Eingabe enthält nur:

- `record_id`, `study_id`, `pmcid`, `split`, `outcome_type`
- `ico` mit Intervention, Comparator und Outcome
- `source_text_path`

Die Referenzwerte werden **nicht** an das Extraktionssystem übergeben.

## Ausgabeschema

Eine JSONL-Zeile pro Eingabe:

```json
{
  "record_id": 4,
  "outcome_type": "continuous",
  "intervention_n": 30,
  "comparator_n": 30,
  "intervention_mean": 47.5,
  "intervention_sd": 38.9,
  "comparator_mean": 26.5,
  "comparator_sd": 27.4,
  "intervention_events": null,
  "comparator_events": null,
  "source_note": "kurze Textstelle oder Tabellenverweis"
}
```

Regeln:

- Keine Werte erfinden oder aus externem Wissen ergänzen.
- Nicht berichtete Werte bleiben `null`.
- Keine nachträgliche Zusammenführung getrennter Arme, Outcomes oder
  Zeitpunkte.
- Für den Zeitpunkt gilt die verbindliche
  [C1-Zeitpunktregel](timepoint_rule.md): ICO-Zeitpunkt, sonst Post-Test,
  sonst frühester vollständiger Follow-up; nie Baseline oder Change-Score.
- `outcome_type` muss dem Eingabetyp entsprechen.
- `source_note` ist ein kurzer Beleg mit Zeitpunkt und Tabellen-/Zeilenangabe,
  keine freie Begründung.

## Ablauf

1. Prompt-Version und Modellkonfiguration vor dem Lauf hashen.
2. Nur `dev_input.jsonl` verwenden; `dev_reference.jsonl` bleibt verborgen.
3. Ausgabe als JSONL mit 26 Zeilen erzeugen.
4. Gegen `dev_reference.jsonl` auswerten:
   - exakte Treffer je Feld,
   - absolute Differenz und MAE für N/Mean/SD/Ereignisse,
   - Abdeckung: wie viele Felder das System überhaupt ausgibt,
   - getrennte Zählung von fehlend, falsch, halluziniert und strukturell
     nicht extrahierbar.
5. Erst danach über eine Testfreigabe entscheiden.

## Abnahmekriterien

- 26/26 Eingaben haben eine Ausgabezeile.
- Kein Referenzwert aus `dev_reference.jsonl` ist in der Eingabe sichtbar.
- Ausgabeschema vollständig; fehlende Werte sind `null`, nicht leer oder 0.
- Der Zeitpunkt folgt der verbindlichen C1-Zeitpunktregel; die `source_note`
  nennt ihn.
- Alle Fehler werden mit Record-ID und Feld berichtet.
- Der Testsplit bleibt unangetastet.

## Abgrenzung

- Der Testsplit wurde nicht gelesen und nicht zur Prompt-Optimierung genutzt.
- Der Lauf ist kein A/B-Vergleich und keine Aussage über den Research Agent.
- Die beiden Ambiguitätscluster und der Tabellenfehler in Record 190 werden
  offengelegt, nicht nachträglich aus dem Primärergebnis entfernt.
- Die Zeitpunktregel ist eine Benchmark-Entscheidung, keine klinische
  Empfehlung; eine spätere gepoolte Analyse kann einen anderen, dann neu
  einzufrierenden Zeitpunkt verlangen.
- Weitere Modellläufe auf Dev benötigen eine neue, begründete Freigabe; der
  eingefrorene Prompt dieses Laufs bleibt unverändert.
