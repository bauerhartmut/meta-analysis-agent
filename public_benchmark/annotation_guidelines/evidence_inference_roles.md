# Evidence Inference 2.0: Rollen und Annotationen

Quellen: `README.annotation_process.md`, `annotations/README.md`, offizielles
Archiv `v2.0.tar.gz`, Repository-Commit
`a661e8c14f973398380c8865cf2f27a535aaaf6d`.

## Drei Rollen, nicht zwei blinde Rater

1. **Prompt-Generator** liest einen RCT und formuliert ICO-Tripel. Zusätzlich
   wird eine Antwort und eine Textstelle als Begründung erfasst.
2. **Annotator** erhält nur Prompt und Artikel, sucht die Antwort und eine
   direkte Evidenzstelle. Bei unklarem Prompt kann `invalid prompt` gesetzt
   werden.
3. **Verifier** sieht Prompt, Artikel sowie die Antworten/Begründungen von
   Prompt-Generator und Annotator, ohne zu wissen, welche von welcher Rolle
   stammt. Der Verifier prüft `Valid Label` und `Valid Reasoning`.

Die Rollen sind in den CSV-Dateien **nicht als Spalte** ausgewiesen. `UserID`
ist nur eine Personenkennung. Die Verteilung (UserID 0 mit 12.180 der 24.686
Zeilen) ist mit der Rolle des Prompt-Generators vereinbar, aber aus den Daten
allein nicht bewiesen.

## Was veröffentlicht ist

- `prompts_merged.csv`: 12.865 ICO-Prompts aus 3.372 Artikeln.
- `annotations_merged.csv`: 24.686 Zeilen aus 3.346 Artikeln, 8 UserIDs.
- Pro Zeile: Label, Evidenztext, `Evidence Start/End`, `Valid Label`,
  `Valid Reasoning`.
- Mehrere Zeilen pro Prompt/User sind möglich, wenn mehrere Evidenzstellen
  zitiert werden.
- 924 Zeilen haben keine gültige Evidenzspanne (`-1`).

## Was daraus folgt

- Individuelle Antworten sind sichtbar, aber nicht als zwei gleichwertige,
  verblindete Rater-Urteile über dieselbe Aufgabe.
- Es gibt keine einzelne adjudizierte Endannotation pro Prompt. Der Verifier
  akzeptiert oder verwirft die vorliegenden Labels; er ersetzt sie nicht
  durch ein Konsensuslabel.
- Eine naive Paarübereinstimmung von 96,9 % auf Prompts mit mehreren UserIDs
  ist daher **kein** belastbares B-IRR-Maß. Sie vergleicht Rollen und
  wiederholte Evidenzzeilen, nicht zwei unabhängige Zweitannotatoren.
- Für unser B-Experiment ist Evidence Inference nur als komplementäre
  semantische ICO-/Evidenzprüfung brauchbar.

## Numerische Werte

Es gibt keine Spalten für N, Mittelwert, Standardabweichung oder binäre
Ereigniszahlen. Die Antwort ist ausschließlich eine Richtungsentscheidung:

- `significantly increased`
- `significantly decreased`
- `no significant difference`
- `invalid prompt`

Damit ist der Datensatz für die numerische Metaanalyse-Extraktion nicht
ausreichend.
