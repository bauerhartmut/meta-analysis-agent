# Adjudikationsprotokoll v1

Stand: 2026-11-13
Bezug: Entscheidung F5, [`schema_v1.json`](schema_v1.json)
Umsetzung: `public_benchmark/scripts/build_adjudication_batch.py`,
`public_benchmark/scripts/evaluate_adjudication.py`
Tests: `public_benchmark/tests/test_crossval_adjudication.py`

## 1. Rollen

| Rolle | Modell | Aufgabe |
|---|---|---|
| Arm A | Qwen 3.5 397B | unabhängige Extraktion, später primärer Adjudikator |
| Arm B | DeepSeek V4.1 Flash | unabhängige Extraktion |
| Arm C | GLM 5.3 | unabhängige Extraktion |
| Kontrolle | viertes Modell, sofern verfügbar | zweite, unabhängige Adjudikation derselben Konflikte |

Die Kontrolle ist optional, aber nicht stillschweigend: fehlt sie, steht das im
Bericht.

## 2. Verblindung

Der Batch enthält nur `candidate_1`, `candidate_2`, `candidate_3`. Die
Zuordnung zu den Modellen steht ausschließlich in
`adjudication_blinding_v1.json` und wird erst nach der Adjudikation
ausgewertet.

Die Reihenfolge wird je Konflikt aus `sha256(salt|record_id|field)` abgeleitet.
Damit hängt sie weder von Modellnamen noch von Eingabereihenfolge ab. Ein Test
prüft, dass im Batch keine Modellnamen vorkommen und die Zuordnung eine
Bijektion ist.

## 3. Ablauf

1. Feldweise Annotationen der drei Modelle liegen vor (JSONL, je Record und
   Feld ein Wert mit Beleg).
2. `build_adjudication_batch.py` kategorisiert jedes Feld (C1–C6) und schreibt
   nur die Konflikte C2–C6 in den Batch.
3. Qwen erhält je Konflikt: Originalstudie, die drei Kandidaten mit Belegen,
   die Feldbezeichnung. Es soll die Quelle erneut prüfen, nicht abstimmen.
4. Qwen liefert je Konflikt: Wert, Begründung, Seite, Tabelle, Beleg,
   vermutlich richtiges und falsche Modelle, Konfidenz, Status
   (`resolved`, `unresolved`, `insufficient_evidence`).
5. Das Kontrollmodell erhält denselben Batch und dieselben Quellen.
6. `evaluate_adjudication.py` vergleicht beide Adjudikationen mit der
   eingefrorenen Referenz.

## 4. Auswertung

Je Adjudikator:

- Genauigkeit auf den Konfliktfeldern (gegen Referenz),
- Anteil `resolved`, `unresolved`, `insufficient_evidence`,
- Selbstwahlquote: wie oft wird der eigene Kandidat gewählt,
- Korrektheit der Selbstwahl,
- Verbesserungen gegenüber dem Adjudikator-Modell allein,
- Verschlechterungen: ursprünglich korrekter Wert wird durch die Adjudikation
  falsch.

Die Selbstwahlquote ist der wichtigste Indikator für den Bias, den ein Modell
als Richter über die eigene Antwort hat.

## 5. Grenzen

- Die Adjudikation ist kein Goldstandard. Sie ist ein weiterer Vorschlag.
- `unresolved` ist ein zulässiges Ergebnis und wird nicht durch Mehrheit
  ersetzt.
- Unaufgelöste Konflikte gehen nicht in ein Pooling.
- Die Referenz bleibt unverändert; eine Adjudikation schreibt nie in
  `reference_v1.jsonl`.
- Ein nicht signifikanter Unterschied zwischen Adjudikation und Einzelmodell
  ist kein Nachweis gleicher Leistung.
