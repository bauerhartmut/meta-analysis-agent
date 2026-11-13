# Numerische Extraktion aus RCT-Publikationen: Vergleich von vier Sprachmodellen

**Stand:** 13. November 2026
**Status:** Ergebnisbericht, nicht begutachtet
**Datenbasis:** GLASS / TrialReviewBench (öffentlich), 54 Publikationen, 182 Gold-Zellen
**Modelle:** GLM 5.3, DeepSeek V4.1 Flash, Qwen 3.5 397B, Qwen3-30B

---

## Zusammenfassung

Vier Sprachmodelle extrahierten numerische Ergebnisse aus 54 onkologischen
RCT-Publikationen mit offenem Volltext. Bewertet wurde gegen einen öffentlichen
Goldstandard ohne eigene Annotation.

- Alle Modelle erreichen einen **Recall von 0,57 bis 0,60** auf 182 Gold-Zellen.
- **7 bis 9 von 54 Records** sind vollständig korrekt.
- Wenn die richtige Ergebniszeile gefunden wird, stimmen **74 bis 90 Prozent**
  ihrer Zellen.
- **Kein Unterschied zwischen den Modellen ist statistisch belegbar**; die
  95-Prozent-Intervalle überlappen vollständig. Die kleinste mit dieser
  Stichprobe nachweisbare Differenz liegt bei **7,0 Prozentpunkten**.
- Das kleinste Modell (Qwen3-30B) hält beim Recall mit, füllt gefundene Zeilen
  aber seltener korrekt und ist rund **20-mal schneller** als die großen
  Modelle.

Der wichtigste technische Befund betrifft nicht die Modellwahl: Ein zu kleines
Tokenbudget erzeugte 52 leere Antworten, weil das Reasoning das Budget vor der
JSON-Ausgabe aufbrauchte. Mit 24.000 Tokens lief das betroffene Modell
fehlerfrei.

---

## 1. Fragestellung

Wie zuverlässig extrahieren aktuelle Sprachmodelle numerische Ergebnisse
(Ereigniszahlen, Gruppengrößen, Hazard Ratios, Mittelwerte) aus
RCT-Publikationen, und unterscheiden sich die Modelle darin messbar?

Die Untersuchung ist bewusst als externe Validierung angelegt: kein eigener
Annotationsaufwand, sondern ein öffentlich verfügbarer Goldstandard.

## 2. Datenbasis

**Goldstandard.** GLASS / TrialReviewBench, Teilmenge „study results": 81
Ergebniszeilen aus 45 Publikationen, 19 Outcomes. Die Zeilen sind heterogen —
`HR` / `sample` / `Name`, `Events` / `Total` / `n`, teils studiobezogene Spalten.

**Volltexte.** Über Europe PMC waren 55 der 81 Records als offener Volltext
verfügbar, 26 nur als Abstract. Ein Record mit Volltextangabe war nicht ladbar
(HTTP 500). In den Lauf gingen **54 Records** aus 28 Studien.

**Nicht aufgenommen.** Der European-Urology-Datensatz (OSF-Projekt `8fzps`,
104 Records mit Armwerten aus 20 Trials) enthält zwar echte Armzellen, aber nur
für 2 Publikationen einen offenen Volltext. Er wurde deshalb nicht bewertet;
Einzelheiten in `second_goldstandard_feasibility.md`.

**Überschneidungen.** Keine Überschneidung mit den lokal vorhandenen
Yun-Daten, der G5-Shortlist oder der eigenen Auswahl (DOI- und PMID-Vergleich).

## 3. Methode

**Aufgabe.** Je Record ein Volltext (maximal 45.000 Zeichen), Outcome-Name und
Feldliste. Antwort als JSON mit `rows`; jede Zeile enthält die extrahierten
Felder. Temperatur 0, ein Prompt, kein Few-Shot, keine Nachbearbeitung der
Modellantwort.

| Modell | Kennung | Tokenbudget |
|---|---|---:|
| GLM 5.3 | `gwdg/glm-5.3` | 24.000 |
| DeepSeek V4.1 Flash | `gwdg/deepseek-v4.1-flash-1017` | 8.000 |
| Qwen 3.5 397B | `gwdg/qwen3.5-397b-a17b` | 16.000 |
| Qwen3-30B | `gwdg/qwen3-30b-a3b-instruct-2507` | 8.000 |

**Bewertung, Stufe 1 (Multiset).** Alle numerischen Zellen eines Records werden
als Multiset verglichen. Recall = korrekt gelieferte Gold-Zellen / alle
Gold-Zellen; Precision = korrekt gelieferte Zellen / alle gelieferten Zellen.

**Bewertung, Stufe 2 (Zeilenzuordnung).** Der Goldstandard führt je Record genau
eine Zeile — die gepoolte der Metaanalyse. Die Modelle liefern Subgruppenzeilen
mit eigenen Bezeichnungen (statt „Keller, 2016" etwa „EBRT before vs
during/after nivolumab"). Eine Zuordnung über den Studiennnamen gelingt deshalb
nicht. Der Auswerter ordnet über die übereinstimmende Zahl zu (Anker:
Effektgröße, dann weitere numerische Zellen) und berichtet danach getrennt:

- **Zuordnungsrate:** Anteil Goldzeilen mit einer zugeordneten Vorhersagezeile,
- **Genauigkeit in gefundener Zeile:** korrekte Zellen / (korrekte + falsche
  Zellen) innerhalb zugeordneter Zeilen,
- **Zusatzzellen:** gelieferte Zellen, die zu keiner Goldzeile gehören.

**Unsicherheit.** Bootstrap über Studien-Cluster, 1000 Runden, Seed 20261113,
28 Cluster. Power-Abschätzung mit gepaartem McNemar-Test, Alpha 0,05
zweiseitig, Power 0,80.

## 4. Ergebnisse

### 4.1 Gesamtleistung (54 Records, 182 Gold-Zellen)

| Modell | Recall | 95 %-KI | Precision | F1 | exakte Records |
|---|---:|---|---:|---:|---:|
| GLM 5.3 | 0,604 | 0,485-0,724 | 0,358 | 0,450 | 9 / 54 |
| DeepSeek V4.1 Flash | 0,577 | 0,469-0,681 | 0,383 | 0,461 | 8 / 54 |
| Qwen 3.5 397B | 0,571 | 0,471-0,670 | 0,510 | 0,539 | 9 / 54 |
| Qwen3-30B | 0,566 | 0,477-0,652 | 0,426 | 0,486 | 7 / 54 |

Die Intervalle überlappen vollständig. Die Rangfolge nach Recall ist mit dieser
Stichprobe nicht belegbar; die Unterschiede liegen innerhalb der Unsicherheit.

### 4.2 Zeilenweise Auswertung

| Modell | Zuordnungsrate | Recall | Precision | Genauigkeit in gefundener Zeile | Zusatzzellen |
|---|---:|---:|---:|---:|---:|
| GLM 5.3 | 0,852 | 0,593 | 0,352 | 0,844 | 179 |
| DeepSeek V4.1 Flash | 0,852 | 0,566 | 0,376 | 0,851 | 153 |
| Qwen 3.5 397B | 0,815 | 0,571 | 0,510 | 0,897 | 88 |
| Qwen3-30B | 0,778 | 0,528 | 0,397 | 0,744 | 113 |

Drei Beobachtungen:

1. **Das Finden der Zeile ist der Engpass, nicht die Zahl.** 78 bis 85 Prozent
   der Goldzeilen werden zugeordnet; ist die Zeile gefunden, stimmen 74 bis 90
   Prozent ihrer Zellen.
2. **Die Precision unterschätzt die Genauigkeit systematisch**, weil die Modelle
   alle Subgruppen eines Papers liefern, der Goldstandard aber nur eine Zeile
   führt. 88 bis 179 Zellen pro Modell gehören zu keiner Goldzeile — das ist
   echte Überextraktion gegenüber der Goldgranularität, kein Bewertungsfehler.
3. **Das kleine Modell füllt gefundene Zeilen schlechter.** Qwen3-30B ordnet
   ähnlich viele Zeilen zu wie Qwen 3.5 397B (0,778 gegen 0,815), erreicht in
   diesen Zeilen aber nur 0,744 statt 0,897. Der Unterschied ist nicht
   signifikant, aber über alle Kennzahlen gleichgerichtet.

### 4.3 Stabilität und Aufwand

| Modell | Aufrufe | leer (HTTP 200, kein Inhalt) | Fehler (429/503/Timeout) | Median je Record |
|---|---:|---:|---:|---:|
| GLM 5.3 | 111 | 41 | 13 | 24,3 s |
| Qwen 3.5 397B | 67 | 11 | 2 | 49,6 s |
| DeepSeek V4.1 Flash | 54 | 0 | 0 | 4,2 s |
| Qwen3-30B | 54 | 0 | 0 | 0,8 s |

Alle leeren Antworten hatten `finish_reason: length` und exakt das jeweilige
Tokenbudget verbraucht: Das Reasoning endete vor der JSON-Ausgabe. Nach Anhebung
auf 24.000 Tokens liefen alle 10 offenen GLM-Aufträge ohne einen einzigen Fehler
durch. Die erfolgreichen Läufe mit kleinerem Budget bleiben gültig, weil das
Budget dort nicht bindend war (`finish_reason: stop`).

## 5. Interpretation

Das absolute Niveau ist für den praktischen Einsatz mäßig: Rund 40 Prozent der
Gold-Zellen fehlen oder weichen ab, und nur jeder sechste Record ist vollständig
korrekt. Für eine Metaanalyse, die auf diesen Werten aufbaut, bedeutet das eine
erhebliche manuelle Nachkontrolle — der Nutzen liegt in der Vorarbeit, nicht in
der Endkontrolle.

Gleichzeitig zeigt die zeilenweise Auswertung, dass die Modelle die relevanten
Stellen überwiegend finden. Der Fehler entsteht beim Befüllen und beim
Granularitätsunterschied zwischen Paper (viele Subgruppen) und Metaanalyse (eine
gepoolte Zeile).

Ein Modellrang ist mit 54 Records und 28 Clustern nicht zu vergeben. Wer
trotzdem wählen muss, wählt nach Nebenkriterien: Qwen 3.5 397B liefert die
saubersten Zeilen (höchste Precision, wenigste Überextraktion), GLM die meisten
Treffer, Qwen3-30B das mit Abstand beste Verhältnis aus Laufzeit und Recall.

## 6. Grenzen

1. **Stichprobengröße.** 54 Records, 28 Cluster, 182 Zellen. Die kleinste
   nachweisbare Differenz liegt bei 7,0 Prozentpunkten (ICC 0,1, Diskordanz
   0,25); bei Diskordanz 0,15 sind es 5,4 Prozentpunkte. Ein nicht signifikantes
   Ergebnis ist kein Gleichstandsnachweis.
2. **Precision strukturell benachteiligt.** Der Goldstandard führt eine Zeile je
   Record, die Modelle liefern Subgruppen. Die Genauigkeit in gefundener Zeile
   ist die fairere Kennzahl, ankert aber auf der Goldzahl und ist damit leicht
   zugunsten des Modells verzerrt.
3. **Keine Arm-, Zeitpunkt- oder Herkunftsprüfung.** GLASS führt keine
   per-Arm-Werte, keine Zeitpunkte und keine Seiten- oder Tabellenangaben.
   Armverwechslung — der Fehler mit der größten Wirkung auf eine Metaanalyse —
   ist damit strukturell unsichtbar.
4. **Domäne.** Ausschließlich Onkologie, überwiegend neuere Publikationen mit
   offenem Volltext. Die Übertragbarkeit auf andere Felder ist nicht geprüft.
5. **Dienstgrenzen.** Die Ratengrenze des Anbieters (10 Anfragen pro 10 s)
   erzeugte 6 × HTTP 429 und 5 × HTTP 503; sequenzielle Nachläufe liefen
   fehlerfrei. Die Fehlerzahlen in Tabelle 4.3 sind deshalb zum Teil
   Infrastruktur, nicht Modellverhalten.
6. **Goldstandardqualität.** Die Gold-Zeilen wurden nicht unabhängig
   nachgeprüft. Einzelne Zeilen enthalten gemischte Angaben (etwa mehrere Trials
   in einem Feld bei European Urology); für GLASS wurde die Zeilenstruktur
   übernommen, wie sie veröffentlicht ist.

## 7. Reproduzierbarkeit

| Datei | Inhalt |
|---|---|
| `tier1_validation_set_v1.jsonl/.json` | 185 Records (104 EU + 81 GLASS) mit Goldzeilen |
| `tier1_documents_v1.json` | Volltextlage je Record |
| `runs/tier1_20261113/predictions.jsonl` | 286 Rohaufrufe |
| `tier1_scores_aligned.json` | Auswertung: Multiset und Zeilenzuordnung |
| `tier1_validation_protocol.md` | Protokoll vor dem Lauf |
| `power_estimation_v1.md` | Power-Abschätzung |
| `public_goldstandard_dataset_review.md` | Prüfung der öffentlichen Datensätze |
| `second_goldstandard_feasibility.md` | Prüfung zweiter Goldstandard mit Armwerten |

Skripte: `public_benchmark/scripts/goldstandard/` —
`build_tier1_validation_set.py`, `prepare_tier1_documents.py`,
`run_tier1_extraction.py`, `score_tier1.py`, Adapter und `xlsx_min.py`.
Tests: `public_benchmark/tests/test_tier1_validation.py` und
`test_goldstandard_adapters.py` (8 Tests, grün).

Aufruf der Auswertung:

```
python public_benchmark/scripts/goldstandard/score_tier1.py \
  --common --aligned --bootstrap 1000 \
  --out public_benchmark/evaluation/multi_model_cross_validation/tier1_scores_aligned.json
```

## 8. Empfehlung

Für eine belastbare Rangfolge fehlen Records und Cluster, nicht Rechenzeit. Zwei
Wege sind realistisch:

1. **Autorenanfrage European Urology** nach den im Artikel genannten 105 Trials
   statt der veröffentlichten 20, mit Armwerten und Belegstelle. Erwartung: 158
   Records aus 42 Clustern, kleinste nachweisbare Differenz 4,5 Prozentpunkte,
   dazu erstmals Armprüfung und Vertauschungsrate.
2. **Cochrane-Genehmigung** für die nicht-kommerzielle Nutzung der
   CDSR-Ergebnisdaten (760.486 Ergebniszeilen mit Armwerten). Die Bedingungen
   verlangen für KI-Nutzung eine ausdrückliche Genehmigung; ohne sie ist der
   Datensatz nicht verwendbar. Bei Zusage: 200 Zeilen aus 80 Reviews,
   3,8 Prozentpunkte.

Bis dahin gilt: Die vorhandenen 54 Records tragen eine belastbare
Absoluteinschätzung und eine schwache Rangfolge — beides ist getrennt zu
berichten.
