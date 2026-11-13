# Laufbericht: drei Modelle auf GLASS

Stand: 2026-11-13
Datensatz: GLASS TrialReviewBench study results (81 Records, 55 mit Volltext)
Auswertung: [`tier1_scores.json`](tier1_scores.json), `--common`
Rohausgaben: `runs/tier1_20261113/predictions.jsonl`
Skripte: `run_tier1_extraction.py`, `score_tier1.py`

## Ergebnis auf der gemeinsamen Teilmenge

41 Records, die alle drei Modelle beantwortet haben, 22 Cluster (Publikationen),
143 Gold-Zellen. Recall bezieht sich auf diese 41 Records, nicht auf alle 81.

| Modell | Recall | 95 %-Bootstrap | Precision | exakte Records | eigene Zellen |
|---|---:|---|---:|---:|---:|
| GLM 5.3 | **0,650** | 0,531-0,761 | 0,472 | 8 / 41 | 93 |
| Qwen 3.5 397B | **0,615** | 0,500-0,725 | 0,667 | 9 / 41 | 88 |
| DeepSeek V4.1 Flash | **0,615** | 0,494-0,726 | 0,550 | 8 / 41 | 88 |

Die Konfidenzintervalle überlappen vollständig. **Mit 41 Records und 22 Clustern
ist kein Unterschied zwischen den Modellen nachweisbar.** Das ist kein
Gleichstandsnachweis, sondern ein zu kleines Fenster: die kleinste nachweisbare
Differenz liegt bei dieser Größe im Bereich von 10 Prozentpunkten.

## Was die Zahlen sagen

- Alle drei Modelle finden rund 62-65 Prozent der Goldzellen. Etwa jede dritte
  Zahl fehlt oder weicht ab.
- Ganze Records korrekt (alle Goldzellen getroffen, keine Zusatzzellen):
  8 bis 9 von 41, also rund 20 Prozent.
- Precision 0,47-0,67: Die Modelle liefern deutlich mehr Zellen als der
  Goldstandard führt, weil sie alle Subgruppen des Papers extrahieren. Der
  Goldstandard enthält nur die Zeile, die die Metaanalyse verwendet hat.
- GLM hat den höchsten Recall und die niedrigste Precision, Qwen die höchste
  Precision. Beides liegt innerhalb der Unsicherheit.

## Abdeckung und Ausfälle

| Modell | beantwortet | fehlend |
|---|---:|---:|
| DeepSeek | 54 / 55 | 1 |
| Qwen | 50 / 55 | 5 |
| GLM | 42 / 55 | 13 |

GLM-Ausfälle: 6 × HTTP 429, 5 × 503, 2 × Timeout, dazu 6 Antworten mit HTTP 200
und leerem `content` (Reasoning hat das Budget von 12000 Tokens verbraucht,
`finish_reason` dann `length`). Ein Nachlauf für die 16 offenen Aufträge scheiterte
in derselben Sitzung an der Ratengrenze (15 Fehler in 13 Sekunden).

## Laufdaten

- 175 Aufrufe protokolliert, davon 146 mit verwertbaren Zeilen.
- Laufzeit des Hauptlaufs: 24 Minuten für 162 Aufträge bei 4 Threads,
  rund 45 Sekunden je Aufruf.
- Modelle: `gwdg/qwen3.5-397b-a17b` (12000 Tokens), `gwdg/deepseek-v4.1-flash-1017`
  (8000), `gwdg/glm-5.3` (12000), Temperatur 0.
- Prompt: Volltext (max. 45000 Zeichen), Outcome-Name, Feldliste; Antwort als
  JSON-Objekt mit `rows`. Keine Nachbearbeitung, kein Few-Shot.

## Grenzen

- 41 Records, 22 Cluster, 143 Zellen: für Modellvergleiche zu klein.
- Precision ist strukturell benachteiligt (Subgruppenzeilen); der Recall ist die
  belastbarere Zahl.
- Der Goldstandard enthält nur die von der Metaanalyse genutzte Zeile; welches
  die richtige Subgruppe ist, steht in `source_rows`, wurde aber nicht
  ausgewertet.
- Keine Zeitpunkt-, Seiten- oder Tabellenprüfung, weil GLASS diese Felder nicht
  führt.
- Ein Record je Publikation ist nicht dasselbe wie ein Record je Arm; die
  Armzuordnung konnte hier nicht geprüft werden (GLASS-Zellen haben keinen Arm).

## Einordnung

Der Weg funktioniert ohne neue Annotation: öffentlicher Goldstandard, Volltext
aus Europe PMC, drei Modelle, maschinelle Bewertung. Die Ergebnisse sind ein
belastbarer Machbarkeitsnachweis und ein erstes Signal, aber keine
wissenschaftliche Aussage über Modellrangfolge.
