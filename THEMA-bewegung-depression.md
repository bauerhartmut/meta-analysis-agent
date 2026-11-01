# Neues Thema: Bewegung und depressive Symptome bei Erwachsenen

Angelegt am 2026-10-29. **Kein Lauf gestartet** — es gibt Datenbank, Protokoll
und Zielmaß, aber noch keine Quelle. Der Start ist ein Befehl (unten).

Dieses Thema ist das erste, das nicht auf eine breite Frage zielt, sondern auf
eine **poolbare Effektgröße**: eine Zahl, die aus publizierten randomisierten
Studien zusammengefasst werden kann, mit Heterogenität, Prediction Interval und
Publikationsbias-Prüfung. Die Pipeline dafür steht bereits im Projekt
(`research_agent/meta/`, Berichtsabschnitt `## Metaanalyse`, siehe
[README.md](README.md#L511)).

## Der Themen-String

```
Exercise and depressive symptoms in adults
```

Dieser String ist der Schlüssel: Datenbankname (Hash des vollen Textes) und
Protokollordner (Slug) hängen daran. Abweichungen — anderer Fall, Zusatz in
Klammern, deutsches „Bewegung" — landen in einer **anderen** Datenbank. Bitte
zeichengenau verwenden.

## Die Frage

Wie groß ist der Effekt von strukturiertem körperlichem Training auf die Schwere
depressiver Symptome bei Erwachsenen, verglichen mit keiner Behandlung oder einer
inaktiven Kontrolle?

| PICO | Inhalt |
|---|---|
| Population | Erwachsene ≥ 18 mit depressiven Symptomen oder diagnostizierter Depression, ohne postpartale Depression |
| Intervention | strukturiertes, angeleitetes Training (aerob, Kraft, kombiniert), definierte Dauer und Häufigkeit |
| Comparison | keine Behandlung, Warteliste, übliche Versorgung, Aufmerksamkeitskontrolle |
| Outcome | Schwere depressiver Symptome am Interventionsende, validierte Skala, gepoolt als SMD (Hedges' g) |

## Warum dieses Thema für eine Metaanalyse taugt

- **Ein Outcome, eine Skala.** Alle Studien berichten Depressivität auf einer
  validierten Skala; nach der Standardisierung auf Hedges' g liegen sie auf einer
  gemeinsamen Achse. Genau daran scheitern Themen, deren Studien Bits, Sekunden
  oder Prozentpunkte auf nicht vergleichbaren Instrumenten berichten.
- **Zahlen mit Präzision im Abstract.** RCTs dieses Feldes berichten meist
  Mittelwertdifferenz oder SMD **mit 95 %-KI** — daraus leitet `derive_se()` den
  Standardfehler ab, ohne den eine Zeile nicht poolbar ist.
- **k ist realistisch groß.** Cochrane zählt 57 bis 73 RCTs; selbst ein Bruchteil
  davon im OA-Korpus reicht für Random Effects, Subgruppen und Egger. Bei k < 10
  sind Funnel und Egger schwach — hier ist das kein Problem, bei engeren Themen
  wäre es eines.
- **Heterogenität ist inhaltlich interessant, nicht nur ein Störfaktor.**
  Intensität, Interventionsdauer und Art der Kontrolle sind dokumentierte
  Moderatoren, also sinnvolle Subgruppen statt beliebiger Schnitte.
- **Es gibt einen externen Referenzwert** (siehe unten) — dieselbe
  Known-Answer-Idee wie im Simulationslabor, nur gegen die Literatur statt gegen
  eine Formel.

## Externer Referenzwert

Cochrane-Übersicht „Exercise for depression" (Update 2026, CD004366,
[PubMed 41500513](https://pubmed.ncbi.nlm.nih.gov/41500513/)): 57 RCTs gegen
inaktive Kontrolle, **SMD −0,67 (95 %-KI −0,82 bis −0,52)**; in der Teilmenge mit
adäquater Verdeckung, Intention-to-treat und verblindeter Messung **−0,46
(−0,88 bis −0,04)**. Für Bias-korrigierte Schätzer berichten Schuch et al. 2016
deutlich kleinere Effekte als die unkorrigierten Metaanalysen.

Ein gepoolter Schätzer in der Größenordnung −0,4 bis −0,7 ist plausibel. Deutlich
größere Werte (etwa < −1,0) wären in diesem Korpus kein Befund, sondern ein
Hinweis auf selektive OA-Abdeckung kleiner positiver Studien — und genau das soll
der Bericht dann auch sagen.

## Was angelegt wurde

| Artefakt | Pfad | Inhalt |
|---|---|---|
| Datenbank | `data/research-exercise-and-depressive-symptoms-in-adul-bbb324.db` | leeres Schema, 0 Quellen; `review_targets` gesetzt |
| Protokoll (eingefroren) | `data/reviews/exercise-and-depressive-symptoms-in-adul/protocol.md` | PICO, Ein-/Ausschluss, primäres Outcome, geplante Zählungen, Referenzwert, Grenzen |
| Zielmaß | Tabelle `review_targets`, Topic = obiger String | ein Outcome: `depressive symptoms` |

Das Zielmaß im Detail:

- **Label** `depressive symptoms`, **Skala** `smd`, **Richtung** „higher = more
  depressive symptoms (worse)".
- **Aliase** `depression severity`, `depression score`, `depressive symptom`,
  `bdi ii`, `phq 9`, `ces d` — damit „BDI-II score", „PHQ-9" oder „CES-D score"
  deterministisch auf dasselbe Outcome abgebildet werden, statt je Studie eine
  eigene Gruppe mit k = 1 zu bilden.
- **Ein** Outcome, nicht drei. Jedes weitere Zielmaß teilt den Pool; hier ist
  Tiefe mehr wert als Breite.

Das Zielmaß wurde **von Hand** gesetzt, nicht vom LLM abgeleitet. Das ist Absicht:
`save_targets()` überschreibt ein vorhandenes Ziel nicht, also bleibt das
Vokabular fest, bevor die erste Zahl gelesen wird. Ein Zielmaß, das nach den
Ergebnissen noch entsteht, entscheidet mit, was gepoolt wird.

## Start

```bash
python run.py --topic "Exercise and depressive symptoms in adults"
```

Mit Neustart-Aufsicht (empfohlen für einen Lauf über Stunden):

```bash
python supervisor.py -- --topic "Exercise and depressive symptoms in adults"
```

Schnellerer erster Beleg, dass die Extraktion greift — liest sofort einige
Dokumente aus der Warteschlange, statt auf sie zu warten:

```bash
python scripts/extract_effects_on_demand.py --topic "Exercise and depressive symptoms in adults" --count 6
```

Relevante Einstellungen (Standard in Klammern): `META_EFFECTS_PER_CYCLE` (1, jedes
Dokument kostet zwei LLM-Pässe), `META_MIN_STUDIES` (2, darunter wird nicht
gepoolt), `META_TARGETS_ENABLED` (1, hier ohne Wirkung, weil das Ziel schon
eingefroren ist).

Zum Interpreter: `python` (3.12.9) startet den Agenten auf diesem Rechner
vollständig. Der Projekt-venv `.venv` ist derzeit **unvollständig** — `numpy`,
`scipy` und `pandas` fehlen, deshalb bricht `.venv/bin/python.exe run.py` beim
Import von `scipy` ab. Entweder bei `python` bleiben oder im venv einmalig
`pip install -r requirements.txt` nachziehen.

## Woran man erkennt, dass die Metaanalyse wirklich gelaufen ist

1. `study_effects` enthält Zeilen mit `se` **oder** `ci_low`/`ci_high`, jede mit
   `quote` und gefundener Textstelle. Zeilen ohne Beleg sind wertlos.
2. `canonical_outcome` ordnet die meisten Zeilen dem Label zu; der Rest erscheint
   als „gelesen, aber nicht im Zielmaß" im Bericht. Ein hoher Off-Target-Anteil
   ist ein Befund über den Korpus, kein Fehler.
3. Der Bericht nennt unter `## Metaanalyse` die PRISMA-Zählungen (gefunden,
   bewertet, ausgeschlossen mit Grund, eingeschlossen, mit Effektzeile, poolbar,
   strittig, verworfen), dann je Outcome die Forest-Tabelle mit τ², I²,
   Prediction Interval, Subgruppen, Leave-one-out und Egger.
4. Zeilen aus Übersichtsarbeiten (Metaanalyse, NMA, systematisches Review) werden
   **nicht** gepoolt: sie stehen mit Zitat in der Tabelle und mit Grund unter
   „Warum Zeilen nicht gepoolt wurden“. Die Zählung dazu nennt der Bericht als
   eigene Zeile („davon aus Übersichtsarbeiten“).
5. `k ≥ 2` wird gepoolt; unterhalb von `META_MIN_STUDIES` bleibt es bei der
   Tabelle. Ein Lauf, der nur zwei Studien mit Effektzeile findet, ist kein
   gescheiterter Lauf — er ist ein ehrliches Ergebnis, das so im Bericht steht.

## Was das Ergebnis nicht sein wird

Keine systematische Übersichtsarbeit: keine Registrierung, kein RoB 2/ROBINS-I,
keine GRADE-Bewertung, keine menschliche Doppelcodierung, kein Peer Review. Der
Korpus ist OA-lastig, und im Abstract fehlt häufig der Standardfehler — was fehlt,
wird als fehlend berichtet statt geschätzt. Gepoolte Beobachtungs- und
Interventionsdaten bleiben, was sie sind: eine quantitative Synthese.

## Offene Entscheidungen (vor dem ersten Lauf, danach eingefroren)

- **Sekundäres Outcome** (z. B. Remissionsraten als `rr`): würde einen zweiten
  Pool eröffnen und die Extraktion breiter machen — jetzt ist nur ein Outcome
  gesetzt.
- **Mindestdauer vier Wochen** ist im Protokoll als Einschlussgrenze gesetzt;
  kürzere Studien laufen nur in der Sensitivitätsanalyse mit.
- **Aktive Vergleiche** (Sport gegen Psychotherapie) sind bewusst nicht Teil des
  primären Pools, sondern werden getrennt berichtet.
