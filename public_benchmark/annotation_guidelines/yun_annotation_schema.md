# Yun et al. 2024: Extraktionsschema

Quellen: Paper (Abschnitt 4, Annotation), `evaluation/data/DATASET.md`,
`evaluation/data/annotated_rct_dataset.json`, Repository-Commit
`1bc768d4d098c727c9866eeff909297c38a3e84c`.

## Einheit

Ein Record ist ein ICO-Tripel:

- **I**ntervention
- **C**omparator
- **O**utcome

Mehrere Outcomes pro Artikel sind zulässig. Zusammengesetzte Outcomes und
Interventionen wurden teilweise in separate Records aufgeteilt; dadurch
entstehen mehr ICO-Records als ursprüngliche Evidence-Inference-Prompts.

## Pflichtfelder je Record

1. `outcome_type`: `binary` oder `continuous`.
2. Bei binär: `intervention_events`, `intervention_group_size`,
   `comparator_events`, `comparator_group_size`.
3. Bei kontinuierlich: `intervention_mean`,
   `intervention_standard_deviation`, `intervention_group_size`,
   `comparator_mean`, `comparator_standard_deviation`,
   `comparator_group_size`.

Fehlt ein Wert im Abstract/Results-Abschnitt, bleibt das Feld leer. Es wird
nicht geschätzt und nicht als Null interpretiert.

## Zeitpunkt

Es gibt **kein separates Zeitpunktfeld**. Die Regeln im Paper lauten:

- Nennt das Outcome mehrere Zeitpunkte, wird der primäre Zeitpunkt des RCT
  verwendet.
- Ist kein primärer Zeitpunkt angegeben, wird der letzte Zeitpunkt verwendet.
- Der gewählte Zeitpunkt steht teilweise nur im Freitext `notes`, teilweise
  nur im Outcome-Text.

Für einen Benchmark muss der Zeitpunkt daher entweder aus dem Outcome-Text
abgeleitet oder als nicht verfügbar markiert werden. Eine automatische
Zeitpunktbewertung ist mit diesem Datensatz nicht direkt möglich.

## Umgang mit fehlenden oder abgeleiteten Werten

- Mediane werden nicht als Mittelwerte extrahiert; solche Records bleiben
  leer.
- Standardabweichungen werden nur übernommen, wenn sie explizit berichtet
  oder aus einem 95%-KI nach der im Paper genannten Formel zurückgerechnet
  wurden.
- `notes` dokumentiert gelegentlich, warum ein Wert fehlt oder aus welcher
  Tabelle/Figur er stammt. Das ist **keine** strukturierte Begründung und
  keine Adjudikationsakte.
- `is_data_in_figure_graphics`, `is_relevant_data_in_table` und
  `is_table_in_graphic_format` sind Metadaten, keine Evidenzstellen.

## Annotatoren

Zwei Co-Autorinnen/Co-Autoren mit Informatik-Hintergrund annotierten jeden
Record zunächst unabhängig und einigten sich anschließend in regelmäßigen
Treffen auf die endgültige Annotation. Eine klinische Forscherin beriet bei
Grenzfällen. Veröffentlicht wurden nur die konsolidierten Records; es gibt
keine Annotator-IDs und keine unabhängigen Einzelannotationen.

## Konsequenz für unser B-Experiment

Yun ist als **numerischer Referenzbenchmark** geeignet, aber nicht als
unabhängige menschliche Zweitannotation im Sinne unseres B-Designs. Aus Yun
lässt sich keine Inter-Rater-Reliabilität berechnen. Die konsolidierte
Referenz kann für Experiment C verwendet werden; die fehlenden Felder
Zeitpunkt, Quellenstelle und individuelle Annotation müssen als
Nichtverfügbarkeit ausgewiesen werden.
