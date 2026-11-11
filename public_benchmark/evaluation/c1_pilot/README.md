# C1-Dev-Pilot: vorbereitet, nicht gestartet

Stand: 2026-11-11

Status: **Pilot vorbereitet; kein Modelllauf; keine Netzwerkanfrage; keine
Testdaten verwendet.**

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
- Keine nachträgliche Zusammenführung getrennter Arme oder Outcomes.
- `outcome_type` muss dem Eingabetyp entsprechen.
- `source_note` ist ein kurzer Beleg, keine freie Begründung.

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
- Alle Fehler werden mit Record-ID und Feld berichtet.
- Der Testsplit bleibt unangetastet.

## Nicht enthalten

- Kein Modellaufruf.
- Kein Prompt wurde gegen Testdaten optimiert.
- Keine Aussage über die Leistungsfähigkeit des Research Agents.
- Ein Lauf benötigt eine ausdrückliche Freigabe.
