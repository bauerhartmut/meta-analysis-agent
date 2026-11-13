# Ergebnisse: vier Sprachmodelle bei der numerischen Extraktion

Stand: 2026-11-13
Zusammenfassung aller Befunde aus Vorbereitung, Extraktionslauf, Bewertung und
Datensatzprüfung. Alle Zahlen stammen aus den unten genannten Dateien, keine
Werte sind geschätzt; Schätzungen sind als solche markiert.

## 1. Frage und Aufbau

Untersucht wurde, wie zuverlässig vier Sprachmodelle numerische Ergebnisse aus
randomisierten Studien extrahieren und ob sie sich unterscheiden:

| Modell | Kennung | Tokenbudget |
|---|---|---:|
| Qwen 3.5 397B | `gwdg/qwen3.5-397b-a17b` | 16.000 |
| DeepSeek V4.1 Flash | `gwdg/deepseek-v4.1-flash-1017` | 8.000 |
| GLM 5.3 | `gwdg/glm-5.3` | 24.000 |
| Qwen3-30B (A3B Instruct 2507) | `gwdg/qwen3-30b-a3b-instruct-2507` | 8.000 |

Als Goldstandard dient ein öffentlicher Datensatz, keine eigene Annotation.
Temperatur 0, ein Prompt, keine Nachbearbeitung, kein Few-Shot.

## 2. Datenbasis

**GLASS / TrialReviewBench (studying results).** 81 Ergebniszeilen aus 45
Publikationen, 19 Outcomes. Die Zeilen tragen homogene Felder nur teilweise:
`HR`/`sample`/`Name`, `Events`/`Total`/`n`, teils studiobezogene Spalten. Der
Datensatz ist mit 81 Zeilen vollständig ausgeschöpft; per-Arm-Spalten gibt es
nicht.

**Verfügbarkeit der Volltexte** (Europe PMC, 81 Records):

| Status | Records |
|---|---:|
| offener Volltext | 55 |
| nur Abstract | 26 |
| nicht gefunden | 0 |

Ein Record mit Volltextangabe war nicht ladbar (HTTP 500), 54 Records liefen.

**European Urology (OSF, `8fzps`).** 104 Records aus 20 Trials mit echten
Armzellen (`arm_1.n`, `arm_1.events`, `arm_2.*`). Nur 20 dieser Records haben
offenen Volltext, und zwar aus 2 Publikationen (PMID 29624800, 34986007). Der
Datensatz wurde deshalb nicht in den Lauf aufgenommen.

**Überschneidungen.** Keine Überschneidung von GLASS, European Urology und
PICO-Corpus mit Yun, G5 oder der eigenen Auswahl (DOI- und PMID-Vergleich,
`dataset_overlap_report.json`).

## 3. Lauf

- 286 protokollierte Aufrufe insgesamt (inklusive Wiederholungen).
- HTTP-Status: 271 × 200, 6 × 429, 5 × 503, 4 × Timeout/Verbindungsfehler.
- 52 Antworten mit HTTP 200 und leerem Inhalt, alle mit
  `finish_reason: length` — das Reasoning hatte das Tokenbudget verbraucht.
- `finish_reason`: 219 × `stop`, 52 × `length`, 15 × leer (Fehler).
- Median der Laufzeit 10,5 s über alle Aufrufe (die leeren Antworten sind
  schneller, deshalb liegt der Median unter der echten Extraktionszeit von
  etwa 45-90 s).
- Endergebnis: **54 von 54 Records von allen vier Modellen beantwortet**.
- Das Zusatzmodell Qwen3-30B lief in 74 Sekunden durch: 54 Aufrufe, 54 ×
  HTTP 200, kein leerer und kein fehlerhafter Aufruf, Median 0,8 s je Record
  bei drei parallelen Threads (das Modell hat 3B aktive Parameter).

Rohdaten: `runs/tier1_20261113/predictions.jsonl`.

## 4. Hauptergebnis: 54 Records, 182 Gold-Zellen, 28 Cluster

Auswertung über alle Zellen (Multiset), gemeinsame Teilmenge aller Modelle:

| Modell | Recall | 95 %-Bootstrap | Precision | F1 | exakte Records | Trefferzellen |
|---|---:|---|---:|---:|---:|---:|
| GLM 5.3 | 0,604 | 0,485-0,724 | 0,358 | 0,450 | 9 / 54 | 110 |
| DeepSeek V4.1 Flash | 0,577 | 0,469-0,681 | 0,383 | 0,461 | 8 / 54 | 105 |
| Qwen 3.5 397B | 0,571 | 0,471-0,670 | 0,510 | 0,539 | 9 / 54 | 104 |
| Qwen3-30B | 0,566 | 0,477-0,652 | 0,426 | 0,486 | 7 / 54 | 103 |

Bootstrap: 1000 Runden, Seed 20261113, Clusterung nach Publikation.

**Die Konfidenzintervalle überlappen vollständig. Mit 54 Records und 28 Clustern
ist kein Unterschied zwischen den Modellen nachweisbar.** Das ist kein
Gleichstandsnachweis.

## 5. Zeilenweise Auswertung (Alignment)

Der Goldstandard führt je Record genau eine Zeile — die, die die Metaanalyse
gepoolt hat. Die Modelle liefern Subgruppenzeilen mit eigenen Namen (statt
„Keller, 2016" etwa „EBRT before vs during/after nivolumab"). Eine Zuordnung
über den Studiennnamen scheitert bei 0 von 41 geprüften Records.

Der Auswerter ordnet deshalb über die übereinstimmende Zahl zu (Anker:
Effektgröße, dann weitere numerische Zellen) und trennt danach:

| Modell | Zeilen zugeordnet | Recall | Precision | Genauigkeit in gefundener Zeile | Zusatzzellen |
|---|---:|---:|---:|---:|---:|
| GLM 5.3 | 0,852 | 0,593 | 0,352 | 0,844 | 179 |
| DeepSeek V4.1 Flash | 0,852 | 0,566 | 0,376 | 0,851 | 153 |
| Qwen 3.5 397B | 0,815 | 0,571 | 0,510 | 0,897 | 88 |
| Qwen3-30B | 0,778 | 0,528 | 0,397 | 0,744 | 113 |

Lesart:

- Rund 82-85 Prozent der Goldzeilen werden überhaupt gefunden.
- Wenn die Zeile gefunden ist, stimmen 84-90 Prozent ihrer Zellen. Der Fehler
  liegt überwiegend im Finden der richtigen Zeile, nicht in falschen Zahlen.
- Die Precision bleibt darunter, weil 88-179 Zellen zu keiner Goldzeile
  gehören. Das ist echte Überextraktion gegenüber der Goldgranularität, kein
  Bewertungsartefakt.
- Qwen überextrahiert am wenigsten und hat die höchste Genauigkeit in
  gefundenen Zeilen; GLM hat den höchsten Recall. Beides liegt innerhalb der
  Unsicherheit.

Einschränkung: Der Anker ist die Goldzahl selbst, deshalb sind Recall und
Precision leicht zugunsten des Modells verzerrt. Belastbar ist vor allem die
Genauigkeit der übrigen Zellen einer gefundenen Zeile.

**Das kleinere Modell im Vergleich.** Qwen3-30B erreicht beim Recall Anschluss
(0,566 gegen 0,571 bis 0,604), liegt bei Precision und F1 im Mittelfeld, aber
in der Genauigkeit gefundener Zeilen deutlich niedriger (0,744 gegen 0,844 bis
0,897). Es findet die Zeile also ähnlich oft, füllt sie aber häufiger falsch.
Auch die Zuordnungsrate ist mit 0,778 die niedrigste. Der Abstand zu Qwen 3.5
397B ist bei 54 Records nicht signifikant, die Richtung ist aber über alle
drei Kennzahlen gleich.

## 6. Zwischenstand auf 41 Records (überholt)

Der erste vollständige Durchlauf umfasste nur die 41 Records, die alle drei
Modelle beantwortet hatten: Recall 0,650 (GLM), 0,615 (Qwen), 0,615
(DeepSeek), Precision 0,472 / 0,667 / 0,550. Diese Zahlen sind durch Abschnitt 4
ersetzt; sie stehen in `tier1_scores.json` und sind nur noch als Verlaufsstand
relevant.

## 7. Die eigentliche Fehlerquelle: Tokenbudget

Beim ersten Durchlauf mit `max_tokens` 12000 blieben 48 Antworten leer:
`finish_reason: length`, `completion_tokens` exakt 12000, `content` leer. Das
Reasoning hatte das Budget verbraucht, bevor die JSON-Antwort begann.

Mit 24000 Tokens liefen alle 10 offenen GLM-Aufträge **ohne einen einzigen
Fehler** durch (0 leer, 0 Fehler). Qwen brauchte 16000 für seinen letzten
Record. Die erfolgreichen 12000er-Läufe bleiben gültig, weil das Budget dort
nicht bindend war (`finish_reason: stop`).

Nebenbefund: Die Ratengrenze des Dienstes (10 Anfragen pro 10 s) erzeugte
6 × HTTP 429 und 5 × 503. Sequenzielle Nachläufe mit 10 s Pause liefen
fehlerfrei.

## 8. Was das statistisch trägt

Gerechnet mit `estimate_crossval_power.py` (gepaarter McNemar-Test,
Alpha 0,05 zweiseitig, Power 0,80, 8 Felder je Record):

| Szenario | Records | Cluster | Felder | kleinste nachweisbare Differenz |
|---|---:|---:|---:|---|
| heutiger Stand | 54 | 28 | 432 | 7,02 pp (ICC 0,1); 5,44 pp bei Diskordanz 0,15 |
| + EU-Volltext | 74 | 24 | 592 | 6,31 pp |
| + EU komplett (Autorentabellen) | 158 | 42 | 1.264 | 4,45 pp |
| Cochrane, 200 Zeilen / 80 Reviews | 200 | 80 | 1.600 | 3,75 pp |
| AACT, 120 Trials | 120 | 120 | 960 | 4,52 pp |

Für eine Rangfolge mit 5 Prozentpunkten Auflösung braucht es mindestens 158
Records aus 42 Clustern.

## 9. Zweiter Goldstandard mit Armwerten: geprüft und verworfen

| Quelle | Armwerte | Umfang | Volltext | Lizenz | Urteil |
|---|---|---|---|---|---|
| GLASS | nein | 81 Zeilen, 45 Publikationen | 54 von 81 | Labels MIT, Artikel eigene Rechte | erschöpft |
| European Urology | ja | 104 Records, 20 Trials | 20 Records aus 2 Publikationen | keine Lizenz angegeben | zu klein nutzbar |
| Cochrane CDSR (über BEAR) | ja | 760.486 Zeilen, 90.042 Paare, 6.619 Reviews | über PMID/DOI beschaffbar | nicht-kommerziell, KI-Nutzung nur mit Genehmigung | passend, aber gesperrt |
| AACT / ClinicalTrials.gov | ja | 907.566 Ergebniszeilen | Registertabelle, kein PDF | Public Domain | anderer Extraktionsgegenstand |
| PICO-Corpus | teils | 5.024 Zahlen, 1.011 Abstracts | nur Abstracts | keine Lizenzdatei | keine Outcome-Zuordnung |

Die Cochrane-Bedingungen sind eindeutig: „AI developers must obtain
authorization before using data from Cochrane reviews for AI development,
training, or implementation" und „no implied permission exists without a
licence". Ohne schriftliche Genehmigung ist der Datensatz nicht verwendbar.

## 10. Grenzen

- 54 Records, 28 Cluster, 182 Zellen: zu klein für Unterschiede unter
  7 Prozentpunkten.
- Precision strukturell benachteiligt (Subgruppenzeilen); Recall ist die
  belastbarere Zahl.
- Keine Arm-, Zeitpunkt-, Seiten- oder Tabellenprüfung, weil GLASS diese Felder
  nicht führt. Armverwechslung — der Fehler mit der größten Wirkung auf eine
  Metaanalyse — ist damit strukturell unsichtbar.
- Der Zeilenabgleich ankert auf der Goldzahl.
- Ein 55. Record war nicht ladbar (Europe PMC HTTP 500).
- Die Cochrane-Zahlen stammen aus der BEAR-Aufbereitung, nicht aus einem
  eigenen CDSR-Download.

## 11. Artefakte

| Datei | Inhalt |
|---|---|
| `tier1_validation_set_v1.jsonl/.json` | 185 Records (104 EU + 81 GLASS) mit Goldzeilen |
| `tier1_documents_v1.json` | Volltextlage je Record |
| `runs/tier1_20261113/predictions.jsonl` | alle 232 Rohaufrufe |
| `tier1_scores_aligned.json` | Auswertung 54 Records, Multiset und Alignment |
| `tier1_scores.json` | Zwischenstand 41 Records |
| `tier1_run_report.md` | Laufbericht |
| `tier1_validation_protocol.md` | Protokoll vor dem Lauf |
| `public_goldstandard_dataset_review.md` | Prüfung der öffentlichen Datensätze |
| `second_goldstandard_feasibility.md` | Prüfung zweiter Goldstandard mit Armwerten |
| `power_estimation_v1.md` | Power-Abschätzung |
| `dataset_overlap_report.json` | Überschneidungsprüfung |

Skripte: `public_benchmark/scripts/goldstandard/` (`build_tier1_validation_set.py`,
`prepare_tier1_documents.py`, `run_tier1_extraction.py`, `score_tier1.py`,
Adapter, `xlsx_min.py`).
Tests: `public_benchmark/tests/test_tier1_validation.py`,
`test_goldstandard_adapters.py` (8 Tests, grün).

## 12. Fazit

1. Der Weg funktioniert ohne neue Annotation: öffentlicher Goldstandard,
   Volltext aus Europe PMC, drei Modelle, maschinelle Bewertung.
2. Das absolute Niveau ist mäßig: rund 57-60 Prozent der Goldzellen, 8-9 von 54
   Records vollständig korrekt. Wenn die richtige Zeile gefunden wird, stimmen
   84-90 Prozent der Zellen.
3. Ein Modellunterschied ist mit dieser Stichprobe nicht belegbar. Qwen liefert
   die saubersten Zeilen, GLM die meisten Treffer, DeepSeek liegt dazwischen —
   alle Differenzen innerhalb der Unsicherheit. Das kleinere Qwen3-30B hält
   beim Recall mit, füllt gefundene Zeilen aber seltener korrekt.
4. Der größte Einzelfehler war technisch, nicht methodisch: zu kleines
   Tokenbudget. Mit 24000 Tokens lief GLM fehlerfrei.
5. Für eine belastbare Rangfolge fehlen Records und Cluster, nicht Rechenzeit.
