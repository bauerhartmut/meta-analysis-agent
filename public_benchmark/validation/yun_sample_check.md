# Yun-Stichprobe: fünf Records gegen den Volltext

Geprüft am 2026-11-11 gegen
`raw_data/yun_llm_meta_analysis/evaluation/data/no_attributes_markdown_files/`.
Die Referenzwerte stammen aus `annotated_rct_dataset.json`. Die Texte wurden
nicht verändert.

| ID | PMC | Outcome | Referenz | Textbefund | Bewertung |
|---:|---|---|---|---|---|
| 4 | PMC1216327 | Dauer der Erkrankung | WGJ: N=30, 47,5 ± 38,9; Wasser: N=30, 26,5 ± 27,4 | Abstrakt und Tabelle 5 nennen exakt `47.5 ± 38.9` und `26.5 ± 27.4`; N=30 je Arm | **stimmt** |
| 12 | PMC2667135 | Antibiotikadauer | CoPAT: N=103, 25,4 ± **23,34**; IPAT: N=97, 13,5 ± 9,49 | Tabelle: `25.4 (12.34)` und `13.5 (9.49)`; `23.34` kommt im Text nicht vor | **SD-Diskrepanz** |
| 21 | PMC2972614 | Schmerzintensität | Laser: N=30, 3,76 ± 1,45; Placebo: N=22, 4,63 ± 2,1 | Tabelle: `3.76±1.45` und `4.63±2.10`; N=30/22 | **stimmt** (2,1 = 2,10) |
| 30 | PMC3003523 | SF-36-Verbesserung | CZP 200 mg: N=393, 38,1 ± 9,5; Kontrolle: N=199, 31,5 ± 7,4 | Tabelle: `38.1 (9.5)` und `31.5 (7.4)`; N=393/199; Freitext nennt 52 Wochen | **stimmt** |
| 73 | PMC3546023 | Urin-Cotinin | Palmvitee-Raucher: N=30, 1,179 ± 0,738; Nichtraucher: N=19, 0,047 ± 0,017 | Tabelle Woche 24: `1.179 ± 0.738` und `0.047 ± 0.017`; N=30/19 | **stimmt** |

## Ergebnis

- **4 von 5** geprüften Records sind numerisch exakt nachvollziehbar.
- **1 von 5** enthält eine klare Diskrepanz: Record 12 führt eine
  Interventions-SD von 23,34, während die Tabelle 12,34 zeigt. Es handelt
  sich wahrscheinlich um einen Zahlendreher in der Referenzannotation. Der
  Wert wurde **nicht korrigiert**, weil die Rohdaten unverändert bleiben.
- Die Stichprobe ist klein und kein Vollaudit. Sie zeigt aber, dass die
  Yun-Referenz nicht blind als fehlerfrei behandelt werden darf.

## Zusätzliche Auffälligkeiten

- IDs 635/636 (PMC5777645) tragen `is_data_complete=TRUE`, obwohl
  `intervention_group_size` und `comparator_group_size` leer sind. Damit
  fehlen die N für eine belastbare Effektberechnung.
- Der Datensatz enthält 517 kontinuierliche und 182 binäre Records; das Paper
  berichtet 516/183.
- Das Paper nennt 413 Records mit ausreichenden Daten; im Release sind 412
  per Flag und 410 per strenger Feldregel vollständig.

## Konsequenz

Vor Experiment C ist ein breiteres Audit der vollständigen Records nötig.
Mindestens sollten alle 261 streng vollständigen kontinuierlichen Records
oder eine vorab festgelegte Zufallsstichprobe geprüft werden. Die
Testannotationen dürfen dabei nicht zur Prompt-Optimierung verwendet werden.
