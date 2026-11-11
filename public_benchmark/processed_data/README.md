# Verarbeitete Daten

## `yun_ico_records.jsonl`

699 Zeilen, eine Zeile pro Yun-ICO-Record. Die Datei ist eine
**Projektion** der unveränderten Referenzannotation, keine neue Annotation
und keine Modellausgabe.

### Regeln

- `study_id` = `PMC` + `pmcid`.
- Leere numerische Felder werden zu `null`; sie werden **nicht** als 0 oder
  als geschätzt behandelt.
- `intervention_n` usw. sind normalisierte Zahlen. Die ursprünglichen
  Zellwerte stehen zusätzlich in `raw_numeric_values`, damit
  Tausender-Kommas und ähnliche Schreibweisen nachvollziehbar bleiben.
- `timepoint` ist immer `null`, weil Yun kein separates Zeitpunktfeld hat.
- `source_quote` ist immer `null`, weil Yun keine Evidenzstellen auszeichnet.
- `annotator_notes` enthält den Freitext aus `notes`. Das ist keine
  strukturierte Begründung und keine Adjudikationsakte.
- `strict_complete` bedeutet: bei kontinuierlichen Outcomes sind N, Mean und
  SD beider Arme vorhanden; bei binären Outcomes sind Ereignisse und N beider
  Arme vorhanden.
- `is_data_complete_flag` ist das unveränderte Yun-Flag. Es kann von
  `strict_complete` abweichen.

### Bekannte Abweichungen

- 412 Records tragen `is_data_complete=TRUE`, aber nur 410 erfüllen die
  strenge Feldregel. Die IDs 635 und 636 haben keine Gruppengrößen.
- Record 12 (PMC2667135) enthält `intervention_sd = 23.34`; die Tabelle im
  Artikel zeigt `12.34`. Der Rohwert wurde nicht korrigiert.
- Der Datensatz zählt 517 kontinuierliche und 182 binäre Records; das Paper
  nennt 516/183.

## Evidence Inference und DTA

Für Evidence Inference wird keine numerische Projektion erzeugt, weil N,
Mean und SD fehlen. Die Roh-CSV bleibt maßgeblich. Für DTA wird keine
Projektion erzeugt, weil es diagnostische 2x2-Daten und keine
Intervention-/Kontroll-Mittelwerte enthält.
