# Vorbereitungsbericht: Multi-Model Cross-Validation

Stand: 2026-11-13
Status: **Vorbereitung abgeschlossen, kein regulärer Modelllauf**
Belege: [`experiment_plan.md`](experiment_plan.md),
[`entscheidungen_20261113.md`](entscheidungen_20261113.md),
[`schema_v1_documentation.md`](schema_v1_documentation.md),
[`annotation_workflow_v1.md`](annotation_workflow_v1.md),
[`adjudication_protocol_v1.md`](adjudication_protocol_v1.md),
[`dataset_manifest.json`](dataset_manifest.json)

## 0. Grenzen dieses Berichts

- Kein Qwen-, DeepSeek- oder GLM-Lauf auf den 25 Artikeln. Der einzige
  Modellaufruf war die GLM-Diagnose auf zwei vorher schon vorhandenen
  Dev-Records.
- Die 249 Yun-Testrecords wurden nicht verwendet, weder zum Tuning noch zur
  Validierung.
- Die G5-Shortlist ist unverändert; die Auswahl ist nachweislich disjunkt.
- Es existiert **keine** menschliche Annotation. Jede Aussage über
  Referenzgenauigkeit fehlt deshalb zwangsläufig.
- Die Eignungsprüfung ist deterministisch und konservativ. Sie zählt nur, was
  sie auflösen kann; ein `ineligible` heißt nicht zwingend "keine Werte im
  Artikel", sondern "mit den vorhandenen Mitteln nicht armweise belegbar".

## 1. GLM-Diagnose

Datei: [`diagnostics/glm_20261113/glm_diagnostic.json`](diagnostics/glm_20261113/glm_diagnostic.json),
Rohantworten je Fall in `diagnostics/glm_20261113/raw/`.

Acht Aufrufe, Modell `gwdg/glm-5.3`, Daten: Dev-Records 120 und 233.

| Fall | max_tokens | HTTP | content | finish_reason | completion_tokens | reasoning_content | Dauer |
|---|---:|---:|---:|---|---:|---:|---:|
| record120_baseline | 900 | 200 | 0 | length | 900 | 3414 Zeichen | 4,4 s |
| record120_repeat | 900 | 200 | 0 | length | 900 | 3414 Zeichen | 0,1 s |
| record120_no_reasoning_param | 900 | 200 | 0 | length | 900 | 3238 Zeichen | 5,1 s |
| record120_max_tokens_2000 | 2000 | 200 | 0 | length | 2000 | 7551 Zeichen | 9,4 s |
| record120_stream | 900 | 200 | 3282 | length | - | im Stream | 3,8 s |
| record233_baseline | 900 | 200 | 0 | length | 900 | 3345 Zeichen | 4,0 s |
| record120_max_tokens_8000 | 8000 | 200 | 385 | stop | 4035 | - | 20,4 s |
| record120_max_tokens_16000 | 16000 | 200 | 386 | stop | 2544 | - | 14,0 s |

### Ursache der leeren Antworten

GLM 5.3 ist ein Reasoning-Modell. Es schreibt zuerst in `reasoning_content`
und erzeugt `content` erst danach. `reasoning_effort: "none"` wird ignoriert
(mit und ohne Parameter identisches Verhalten). Bei `max_tokens` 900 und 2000
wird das Budget vollständig vom Reasoning verbraucht: `completion_tokens`
entspricht exakt dem Limit, `finish_reason` ist `length`, `content` bleibt
leer. Das ist ein Schnittstellen-/Budgetproblem, kein Extraktionsfehler des
Modells.

### Ursache der abgeschnittenen Antwort

Dieselbe Ursache, andere Schwelle: bei 900 Tokens endet die Antwort mitten im
Reasoning. Der Lauf vom 12.11. hatte einen Fall mit abgeschnittenem JSON; das
ist derselbe Mechanismus, nur mit einem Teil des Contents vor dem Limit.

### Reproduzierbarkeit

Zweimal 900 Tokens auf demselben Record: identisches Ergebnis (0 Zeichen,
`length`, 900 Tokens). Auch Record 233 zeigt dasselbe Muster. Der Fehler ist
deterministisch an das Budget gekoppelt, nicht sporadisch.

### Technische Korrektur

`max_tokens >= 8000`. Bei 8000 und 16000 liefert das Modell valides JSON,
`finish_reason: stop`, und den korrekten Wert für Record 120 (8/20 vs. 13/44,
DTPA-Subgruppe), also genau die Referenz. Empfehlung: **12000** als
Sicherheitsmarge, weil die Reasoning-Länge zwischen 2544 und 4035 Tokens
schwankte (bei Temperatur 0).

Streaming löst das Problem nicht: der Stream enthält das Reasoning als
`delta.content` und endet ebenfalls mit `length`. Ein Runner müsste die
`think`-Blöcke entfernen und trotzdem genug Budget haben.

### Entscheidung

**GLM 5.3 ist nach Korrektur verwendbar.** Nicht "ungeeignet", nicht
"unverändert verwendbar". Bedingungen für den späteren Lauf:

- `max_tokens` 12000, kein `reasoning_effort`-Verlass,
- `finish_reason` muss `stop` sein; `length` zählt als Infrastrukturfehler und
  wird nicht als leere Extraktion gewertet,
- Latenz und Completion-Tokens werden je Record protokolliert.

Kosten je Record: 2500-4000 Completion-Tokens, 14-20 s. Für 35 Records
(Vollständigkeitslauf) sind das grob 100.000-140.000 Completion-Tokens; das ist
eine Schätzung aus den acht Messungen, keine Messung.

Ein Ersatzmodell ist damit **nicht** nötig. Mistral Large 4 bleibt als
dokumentierte Alternative, falls GLM im späteren Lauf bei 12000 Tokens
truncatet.

## 2. Eignungsprüfung der 25 Hauptartikel

Dateien: [`crossval_eligibility_review_v1.json`](crossval_eligibility_review_v1.json),
[`.md`](crossval_eligibility_review_v1.md); Reserve:
[`crossval_eligibility_reserve_v1.json`](crossval_eligibility_reserve_v1.json).

Methode: JATS-Tabellenleser, Arm-Erkennung der Pipeline, Fallzahl aus dem
Tabellenkopf der Baseline-Tabelle, `mean (SD)` als Streuungshinweis, `n (%)`
als Ereignissignal. Baseline- und Demografietabellen sind ausgeschlossen.

| Klasse | Hauptartikel | Reserve |
|---|---:|---:|
| `eligible_confirmed` | 1 | 1 |
| `eligible_uncertain` | 3 | 3 |
| `manual_review_required` | 10 | 2 |
| `ineligible` | 11 | 4 |

- Bestätigt: `PMC13554527` (15 kontinuierliche Outcome-Zeilen mit Armwerten).
- Unsicher: `PMC13539392`, `PMC13597907`, `PMC13724892` (Ereignispaare ohne
  ableitbaren Zeitpunkt).
- Manuelle Prüfung: u. a. `PMC13587535` (27 Ereigniszeilen, aber 5 Zeitpunkte),
  `PMC13544601` (vertikales Arm-Layout), vier Artikel ganz ohne Tabelle im XML.
- Nicht geeignet: u. a. `PMC13533546` und `PMC13581780` (nur adjustierte
  Differenzen mit KI, keine Armwerte), `PMC13583812` und `PMC13682724`
  (keine armweisen Zahlen auffindbar).

### Bewertung

Das Ergebnis ist unbequem, aber es ist die Antwort auf die Frage: **nur 1 von
25 Artikeln ist automatisch als armwert-tauglich bestätigt.** Für die anderen
24 ist vor der Annotation eine menschliche Volltextprüfung nötig, sonst wird
Annotatorzeit auf Artikel verwendet, die keine Armwerte führen.

### Ersetzungsvorschlag (nicht ausgeführt)

Für die 11 nicht geeigneten Hauptartikel stehen nur **4** brauchbare
Reserveartikel bereit (`PMC13632614` bestätigt, `PMC13624021`, `PMC13577647`,
`PMC13535982` unsicher). Eine vollständige Ersetzung ist mit der definierten
Reserve **nicht möglich**. Die Auswahl wurde daher nicht verändert; jede
Ersetzung braucht eine dokumentierte Freigabe, und für mehr als vier
Ersetzungen wäre ein neues Artikelkontingent nötig.

## 3. Schema v1

Dateien: [`schema_v1.json`](schema_v1.json),
[`schema_v1_documentation.md`](schema_v1_documentation.md), Validator
`public_benchmark/scripts/validate_crossval_annotation.py`, Tests
`public_benchmark/tests/test_crossval_schema.py`.

- 13 Pflichtfelder je Zahl, exakt wie beauftragt.
- Beziehungen `study -> arms / outcomes / timepoints -> values` mit
  auflösbaren IDs; eine Zahl ohne Arm-, Outcome- und Zeitpunktbezug ist
  ungültig.
- Alle sechs Konfliktkategorien C1-C6 explizit definiert; C5 und C6 sind erst
  durch `table_or_section`, `source_cell_or_location`, `arm_id`, `outcome_id`,
  `timepoint_id` bestimmbar.
- `verification_status` trennt `verbatim`, `parsed_from_cell`,
  `derived_from_ci`, `disputed`, `insufficient_evidence`, `adjudicated`.
- Validator ohne neue Abhängigkeit (`jsonschema` ist nicht installiert und
  wird nicht nachgezogen).
- v6 unverändert: Test prüft den eingefrorenen Prompt-Hash
  `d0300215...` aus `release_v6c.json`.

10 Tests, alle grün. Das Schema ist Entwurf, solange die Referenzannotation
nicht dagegen validiert wurde.

## 4. Referenzannotations-Workflow

Datei: [`annotation_workflow_v1.md`](annotation_workflow_v1.md).

- Rollen A, B und Schlichter/in mit Qualifikationsanforderungen.
- Sieben Schritte von getrennter Annotation über deterministischen Vergleich
  und Konfliktauflösung bis zum eingefrorenen `reference_v1.jsonl` mit
  Manifest.
- Verblindung: keine Person sieht vor Schritt 3 die Datei der anderen, niemand
  sieht vor Schritt 6 Modellausgaben.
- Eine-Person-Fallback heißt `reference_preliminary_v1.jsonl` mit
  `independent_second_annotator: false`; die Einschränkung ist im
  Ergebnisteil auszuweisen.
- Metriken: exakte Übereinstimmung, absolute Differenz, ICC(2,1), Kappa nur
  kategorial. Kein Kappa-Gate.
- Umfang: geschätzt 600-900 Einzelwerte plus Belegstellen.

**Es existiert keine Annotation.** Der Workflow ist vorbereitet, nicht
gestartet.

## 5. Power-Abschätzung

Dateien: [`power_estimation_v1.json`](power_estimation_v1.json),
[`.md`](power_estimation_v1.md).

Gepaarter McNemar-Test auf Feldebene, Design-Effekt aus Artikel-Clustering
(ICC 0,1-0,3), Alpha 0,05 zweiseitig, Power 0,80, Diskordanz 0,25.

| Records | Felder/Record | ICC 0,1 | ICC 0,2 | ICC 0,3 |
|---:|---:|---:|---:|---:|
| 60 | 6 | 7,85 pp | 8,32 pp | 8,76 pp |
| 80 | 6 | 7,04 pp | 7,65 pp | 8,20 pp |
| 100 | 6 | 6,50 pp | 7,21 pp | 7,85 pp |

Für 5 Prozentpunkte wären bei 60 Records **893 bis 1112 Felder** nötig - mehr,
als 60-80 Records mit 6 bis 8 Feldern liefern. Auch 100 Records reichen bei
ICC 0,2 dafür nicht (1253 Felder nötig).

**Folgerung:** Mit 60-80 Records sind nur Differenzen ab etwa 7-9
Prozentpunkten entscheidbar. Kleinere Unterschiede sind mit dieser Stichprobe
nicht nachweisbar. Das Experiment ist in dieser Größe **explorativ**; ein
nicht signifikantes Ergebnis ist kein Gleichstandsbeweis. Für 5 pp bräuchte es
etwa 1200 Felder, also rund 150 Records bei 8 Feldern - das wäre eine andere
Annotation.

## 6. Adjudikationsverfahren

Dateien: [`adjudication_protocol_v1.md`](adjudication_protocol_v1.md),
`public_benchmark/scripts/build_adjudication_batch.py`,
`public_benchmark/scripts/evaluate_adjudication.py`,
`public_benchmark/tests/test_crossval_adjudication.py`.

- Kandidaten als `candidate_1..3`, Reihenfolge aus `sha256(salt|record|field)`,
  damit unabhängig von Modellnamen und Eingabereihenfolge.
- Zuordnung nur in `adjudication_blinding_v1.json`; ein Test prüft, dass im
  Batch keine Modellnamen vorkommen.
- Kategorien C1-C6 inklusive C5 (Quellenkonflikt) und C6 (Strukturkonflikt).
- Auswertung liefert Selbstwahlquote, Korrektheit der Selbstwahl, Verbesserung
  und Verschlechterung gegenüber Qwen allein, Anteil `unresolved`.
- Qwen primär; viertes Modell als Kontrolle ist im Protokoll vorgesehen, aber
  noch nicht ausgewählt.

3 Tests, alle grün. Der Batch-Bauer ist ohne echte Modellannotationen nur mit
Synthetik getestet.

## 7. Offene Blocker

| Blocker | Wirkung | Nötig |
|---|---|---|
| Keine Referenzannotation | keine Genauigkeitsaussage möglich | zwei Personen, 25 Artikel, vor dem ersten Lauf |
| 24 von 25 Artikeln nicht automatisch bestätigt | Annotationszeit könnte ins Leere laufen | menschliche Volltextprüfung vor der Annotation |
| Nur 4 brauchbare Reserveartikel | Ersetzung der 11 ungeeigneten nicht möglich | Entscheidung: Auswahl schrumpfen, Kontingent erweitern oder manuell prüfen |
| Prompt für `schema_v1` fehlt | kein Modelllauf möglich | Prompt bauen und einfrieren |
| Viertes Adjudikationsmodell unbestimmt | nur eine Adjudikation | Modell auswählen oder Einschränkung dokumentieren |
| Stichprobe zu klein für 5 pp | nur große Effekte nachweisbar | Erweiterung auf ~150 Records oder explorativ erklären |

## 8. Empfehlung

**Nächster Schritt: menschliche Volltextprüfung der 25 Artikel, bevor eine
einzige Annotation beginnt.** Begründung: 24 von 25 Artikeln sind automatisch
nicht bestätigt, und die Reserve reicht nicht, um die 11 ungeeigneten zu
ersetzen. Jede Stunde Annotation auf einem Artikel ohne Armwerte ist verloren -
und die Annotation ist der teuerste Posten des ganzen Experiments.

Reihenfolge danach: Prompt für `schema_v1` bauen und einfrieren, dann
Referenz annotieren, dann Power-Entscheidung (60-80 explorativ oder ~150
Records), dann `freeze.json`. Der GLM-Blocker ist beseitigt; er kostet nur
`max_tokens` 12000 im späteren Runner.

Risiko der Empfehlung: Die Volltextprüfung von 25 Artikeln ist selbst
Arbeitszeit, aber sie ist billiger als eine Annotation, die auf untauglichen
Artikeln aufsetzt. Kein Modellaufruf ist dafür nötig.
