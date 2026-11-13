# Pilotlauf auf dem öffentlichen Datensatz

Stand: 2026-11-13
Datensatz: [`tier1_validation_set_v1.jsonl`](tier1_validation_set_v1.jsonl) (GLASS TrialReviewBench, 81 Records, 55 mit Volltext)
Rohausgaben: `runs/tier1_20261113/predictions.jsonl`
Bewertung: [`tier1_scores.json`](tier1_scores.json)
Skripte: `run_tier1_extraction.py`, `score_tier1.py`

## Was gelaufen ist

Erster echter Extraktionslauf auf einem öffentlichen Goldstandard, ohne neue
Annotation: jedes Modell bekommt den Volltext, den Outcome-Namen und die Liste
der gesuchten Felder (z. B. `Name`, `sample`, `HR`) und liefert JSON-Zeilen.

| Modell | Läufe | beantwortet | Gold-Zellen (beantwortete Records) | Treffer | Recall | Precision | eigene Zellen |
|---|---:|---:|---:|---:|---:|---:|---:|
| DeepSeek V4.1 Flash | 8 | 8 | 16 | 11 | 0,688 | 0,097 | 114 |
| Qwen 3.5 397B | 6 | 6 | 12 | 8 | 0,667 | 0,195 | 41 |
| GLM 5.3 | 13 | 0 | 0 | 0 | - | - | 0 |

Recall bezieht sich nur auf die tatsächlich beantworteten Records. Über alle 81
Records gerechnet liegt er bei 0,043 (DeepSeek) und 0,031 (Qwen), weil 73 bzw.
75 Records nicht gelaufen sind.

## Die zwei wichtigen Befunde

**1. GLM 5.3 ist derzeit nicht lauffähig.** 13 Versuche, alle ohne Antwort:
6 × HTTP 429 (`Rate limit exceeded: user 10s request limit reached`),
5 × HTTP 503, 2 × Zeitüberschreitung. Das ist kein Modellfehler, sondern eine
Dienstgrenze; derselbe Aufruf lief am 13.11. mit `max_tokens` 8000 auf den
Dev-Daten erfolgreich. Ein Lauf mit 12000 Tokens braucht entsprechend mehr
Zeitfenster, nicht mehr Budget.

**2. Die Precision ist aus einem strukturellen Grund niedrig.** Der Goldstandard
führt je Record **eine** Ergebniszeile (die, die die Metaanalyse verwendet hat).
Die Modelle extrahieren alle Subgruppenzeilen der Publikation — bei einem Record
19 Zeilen statt einer. Der Recall ist deshalb die aussagekräftige Zahl, die
Precision bestraft hier korrektes Verhalten. Für einen fairen Precision-Wert
müsste man die Zeilen vorher auf die relevante Subgruppe eingrenzen; das ist
im Datensatz nicht markiert und wurde nicht nachträglich hineininterpretiert.

## Warum nur 8 von 81 Records

Der Zugang ist auf 10 Anfragen pro 10 Sekunden begrenzt und der Dienst antwortet
zeitweise mit 503. Bei rund 45 Sekunden je Aufruf (Reasoning-Modelle mit
mehreren Tausend Completion-Tokens) dauert der volle Lauf 55 Records × 3 Modelle
etwa 1,5 Stunden. Der Lauf wurde nach 21 Aufrufen gestoppt, damit keine
halben, nicht vergleichbaren Zahlen berichtet werden.

## Was das für die Entscheidung bedeutet

- Der Weg funktioniert: öffentlicher Goldstandard → Volltext → Modell → JSON →
  Bewertung, ohne eine einzige menschliche Annotation.
- Die ersten Zahlen sind ein Signal, keine Messung: 8 bzw. 6 Records, ein
  Goldwert je Record, keine Konfidenzintervalle, die belastbar wären.
- Der Nutzen liegt vor allem darin, dass die Pipeline steht und die
  Fehlerquellen sichtbar sind (Reasoning-Budget, Rate-Limit, Subgruppenzeilen).

## Nächster Lauf

1. GLM außerhalb der Drosselung, sequenziell mit Pausen, 55 Records.
2. Qwen und DeepSeek für dieselben 55 Records nachziehen.
3. Precision zusätzlich auf die von der Metaanalyse genutzte Subgruppe
   beschränken — dafür müsste das Feld ``source_rows`` aus GLASS ausgewertet
   werden; das ist noch nicht umgesetzt.
4. Erst danach Aussagen über Modellunterschiede.

## Grenzen

- 8 bzw. 6 beantwortete Records, 16 bzw. 12 Gold-Zellen: keine Aussage über
  Modellqualität, nur über Machbarkeit.
- GLM hat null beantwortete Records; jeder Vergleich ohne GLM ist unvollständig.
- Der Lauf nutzt nur GLASS. Die European-Urology-Teilmenge hat nur zwei Trials
  mit offenem Volltext und wurde deshalb nicht einbezogen.
