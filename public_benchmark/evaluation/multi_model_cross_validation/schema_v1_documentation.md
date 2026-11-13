# Schema v1: Dokumentation

Stand: 2026-11-13
Datei: [`schema_v1.json`](schema_v1.json)
Validator: `public_benchmark/scripts/validate_crossval_annotation.py`
Tests: `public_benchmark/tests/test_crossval_schema.py`

## 1. Warum ein neues Schema

Das v6-Schema liefert je Record nur eine `source_note`. Damit ist nicht
entscheidbar, ob ein Modell eine falsche Zahl gelesen hat oder eine richtige
Zahl dem falschen Arm, Outcome oder Zeitpunkt zugeordnet hat. Genau diese
Unterscheidung braucht das Experiment für die Konfliktkategorien C5 und C6.

Das v6-Schema bleibt unverändert. Es ist über den Prompt-Hash in
`evaluation/c1_pilot/release_v6c.json` eingefroren; ein Test prüft, dass dieser
Hash unverändert bleibt.

## 2. Aufbau

Ein Dokument ist ein Studienrecord mit vier Beziehungen:

```
study
 ├── arms[]        (arm_id, label, role, n)
 ├── outcomes[]    (outcome_id, label, type)
 ├── timepoints[]  (timepoint_id, label, relative_to)
 └── values[]      (je Zahl ein Objekt, das auf arm_id, outcome_id, timepoint_id verweist)
```

Jede Zahl trägt ihre eigene Provenienz. Das ist der Kern: eine Zahl ohne
Fundstelle ist im Schema nicht darstellbar.

## 3. Pflichtfelder je Zahl

| Feld | Bedeutung |
|---|---|
| `value` | Zahl oder `null`; `null` heißt nicht berichtet, nicht geschätzt |
| `unit` | Einheit, z. B. `score points`, `events`, `kg` |
| `source_document` | Dateipfad des Volltexts |
| `page` | Seite; `unbekannt` nur mit Status `insufficient_evidence` |
| `table_or_section` | Tabelle oder Abschnitt, z. B. `Table 2` |
| `source_context` | wörtlicher Kontext oder Zeilenlabel |
| `source_cell_or_location` | Zelle, Zeile/Spalte oder Satzposition |
| `arm_id` | muss in `arms[]` auflösbar sein |
| `outcome_id` | muss in `outcomes[]` auflösbar sein |
| `timepoint_id` | muss in `timepoints[]` auflösbar sein |
| `assignment_confidence` | `high`, `medium`, `low` |
| `verification_status` | `verbatim`, `parsed_from_cell`, `derived_from_ci`, `disputed`, `insufficient_evidence`, `adjudicated` |
| `uncertainty_note` | Pflicht bei `low` oder bei Status außerhalb `verbatim`/`parsed_from_cell` |

## 4. Enums

- `arm_role`: `intervention`, `control`, `third_arm`, `unclear`
- `outcome_type`: `continuous`, `binary`
- `relative_to`: `baseline`, `post_test`, `follow_up`, `mid_treatment`, `unclear`

## 5. Konfliktkategorien

| ID | Name | Definition |
|---|---|---|
| C1 | `unanimity` | alle Modelle liefern denselben Wert |
| C2 | `two_vs_one` | zwei gleich, eines weicht ab |
| C3 | `three_way` | drei verschiedene Werte |
| C4 | `missing_value` | mindestens ein Modell liefert keinen Wert |
| C5 | `source_conflict` | gleicher Wert, verschiedene Quelle oder Tabelle |
| C6 | `structural_conflict` | gleiche Zahl, andere Zuordnung zu Arm, Outcome oder Zeitpunkt |

C5 und C6 sind nur bestimmbar, weil `table_or_section`, `source_cell_or_location`,
`arm_id`, `outcome_id` und `timepoint_id` je Zahl erhoben werden.

## 6. Regeln

1. Fehlende Werte werden nicht geschätzt, nicht als 0 geschrieben und nicht
   durch Mehrheitsentscheidung ersetzt.
2. Eine Zahl ohne auflösbare Arm-, Outcome- und Zeitpunkt-Referenz ist
   ungültig; sie gehört als Befund in die Prüfung, nicht in den Datensatz.
3. Adjudizierte Werte werden getrennt geführt und überschreiben keine
   Modellausgabe.
4. `page = unbekannt` ist nur mit `insufficient_evidence` zulässig. Das ist
   eine bewusste Unschärfe: XML-Positionen sind keine Seitenzahlen.

## 7. Validierung

```
.venv/bin/python public_benchmark/scripts/validate_crossval_annotation.py DATEI.jsonl
```

Der Validator prüft Pflichtfelder, Typen, Enums, Referenzauflösung und die
Belegpflicht. Er nutzt keine externen Pakete; `jsonschema` ist im Projekt nicht
installiert und wird bewusst nicht nachgezogen.
