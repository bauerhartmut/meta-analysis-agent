# Briefing: Metaanalyse-Agent — Stand und Umsetzungsauftrag

**Adressat:** ein leistungsfähiges Planungsmodell.
**Zweck:** Dieses Dokument beschreibt den verifizierten Stand des Projekts, die
bereits getroffenen Entscheidungen, die gemessenen Grenzen und die offenen
Arbeitspakete so vollständig, dass daraus ein konkreter Umsetzungsplan
(Phasen, Dateien, Tests, Risiken, Aufwand) erstellt werden kann.

**Was hier NICHT verlangt wird:** Code. Verlangt wird ein Plan, der auf die
unten genannten Dateien, Befehle und Akzeptanzkriterien Bezug nimmt. Jede
Behauptung im Plan muss auf eine prüfbare Quelle (Test, Log, DB-Abfrage,
Skriptlauf) verweisen.

---

## 1. Das Projekt in drei Sätzen

Ein autonomer Metaanalyse-Agent recherchiert zu einer Forschungsfrage selbst im
Web, liest wissenschaftliche Volltexte, extrahiert Effektmaße **wörtlich aus der
Quelle** (Verbatim-Kontrakt), bewertet Bias-Risiken, poolt statistisch
LLM-frei und erzeugt einen zitierfähigen PDF-Bericht. Die Statistik ist
deterministisch und reproduzierbar; kein Sprachmodell rechnet eine Zahl. Die
Mechanik ist gebaut und getestet — der Engpass ist die **Ausbeute an
poolbaren Effekten je Endpunkt**.

## 2. Qualitätsinvarianten (nicht verhandelbar)

Diese Regeln sind der Kern des Projekts. Ein Plan, der sie verletzt, ist
unbrauchbar, auch wenn er schneller wäre.

1. **Verbatim-Kontrakt.** Jede gespeicherte Zahl trägt ein Zitat mit
   Zeichenspan, das gegen den Quelltext geprüft wurde (`quote_start >= 0`).
   Ohne verifizierten Beleg keine Zeile, keine Ausnahme.
2. **Keine erfundenen Werte.** Jede Zahl im Bericht stammt aus DB, Log oder
   einer nachrechenbaren Quelle. Schätzungen werden als Schätzungen markiert.
3. **Doppel-Extraktion wird nie gemittelt.** Zwei abweichende Lesungen ergeben
   `disputed = 1` und fliegen aus dem Pool, nicht in den Mittelwert.
4. **Ein Review ist keine Studie.** Aggregat-Zeilen (Metaanalysen, gepoolte
   Werte) sind keine Primärstudien und dürfen nicht mitgepoolt werden.
5. **k = 1 ergibt keine gepoolte Zahl.** Der Pool verweigert sie und sagt es.
6. **Abhängigkeit zählt einmal.** Gleiche DOI, gleiche Quelle, gleiche
   `study_id` oder gleiche belegte Kohorte kollabieren auf die präziseste
   Zeile; die verdrängten Zeilen werden mit Grund ausgewiesen.
7. **Gates sind deterministisch und dokumentiert.** Design-, Demografie-,
   Median-, SEM/SE- und Tabellenrest-Gates sind Konstanten im Code, keine
   Modellentscheidung.
8. **Geschützte Dateien.** `research_agent/orchestrator.py`,
   `research_agent/meta/extraction.py` und `research_agent/meta/pooling.py`
   sind gitignored: lokal ändern erlaubt, **niemals committen**. Für sie gibt
   es `*_PRIVAT.md`-Beschreibungen im Repo.

## 3. Architektur (Ist-Zustand)

| Baustein | Pfad | Aufgabe | Zustand |
|---|---|---|---|
| Orchestrator | `research_agent/orchestrator.py` (geschützt) | Phasen Planning … Updating, Run-Resume | läuft |
| Suche | `research_agent/research/sources.py` | Europe PMC, OpenAlex, Crossref, Semantic Scholar | läuft, rate-limit-anfällig |
| Volltext | `research_agent/research/fulltext.py`, `jats_tables.py` | XML/PDF-Layout, Tabellen | läuft |
| Screening | `research_agent/meta/screening.py` | Include/Exclude mit Begründung | lückenhaft |
| Zielmaße | `research_agent/meta/targets.py` | Frage → Outcome-Vokabular, Kanonisierung | fertig |
| Extraktion | `research_agent/meta/extraction.py` (geschützt) | LLM-Lesung + Verbatim-Prüfung | fertig |
| Leser (deterministisch) | `meta/effect_columns.py`, `arm_level.py`, `arm_text.py`, `arm_change.py` | Tabellen, Arme, Fließtext, Veränderungswerte | fertig, Ausbeute gering |
| Outcome-Namen | `meta/outcome_labels.py` | deterministische Normalisierung für Gruppierung | fertig |
| Pooling | `meta/pooling.py` (geschützt) | HKSJ, REML, RVE, Egger, Leave-one-out, Subgruppen | fertig |
| Bias | `meta/risk_of_bias.py`, `rob2_signalling.py`, `grade.py` | RoB 2, GRADE | läuft |
| Bericht | `report.py`, `report_pdf.py` | Markdown → PDF (Edge headless) | läuft |
| Dashboard | `dashboard/` | localhost-WebUI, keine Auth | läuft |
| Benchmark | `evals/meta_benchmark.py` | Fixtures-Benchmark | nur synthetisch |

## 4. Verifizierter Stand (Messwerte, keine Schätzungen)

### 4.1 Testsuite

```
1146 passed, 2 skipped, 0 failed   (401,72 s, Gesamtsuite)
158 passed                          (Meta-Kern: Leser, Zielmaße, Outcome-Namen)
```

In einer ersten Messung war ein Test rot: das Gruppenlabel
`General cognitive ability [hedges_g]` wurde als
`general cognitive ability [hedges_g]` ausgegeben. Ursache: die
Outcome-Normalisierung überschrieb den Anzeigenamen. Behoben durch eine
Ziel-Label-Zuordnung in `pooling.py` (geschützt, daher lokal, nicht
committet). **Konsequenz für den Plan:** Änderungen an `pooling.py` müssen
lokal getestet und in `*_PRIVAT.md` dokumentiert werden, sie erscheinen nie
im Diff.

### 4.2 Korpus (Frage: Melatonin vs. Placebo, Einschlaflatenz)

| Kennzahl | Wert |
|---|---|
| Europe-PMC-Treffer | 1.067 |
| davon mit PMCID | 1.059 |
| XML erfolgreich geladen | **1.056** (3 × HTTP 500: `PMC7163627`, `PMC8959415`, `PMC9554922`) |
| Dokumente mit mindestens einem „mean ± SD" | 426 von 1.056 |

### 4.3 Ausbeute der vier Leser auf diesem Korpus

| Leser | Eingabe | gespeicherte Zeilen | Dokumente | Gruppen | k ≥ 2 |
|---|---:|---:|---:|---:|---:|
| Effektspalten (Tabellen) | 42.396 Zeilen | 513 | 18 | 154 | 0 |
| Arm-Rechner (Tabellen) | 42.771 Zeilen | 8 | 4 | 8 | 0 |
| Fließtext-Arme | 315.857 Sätze | 1 | 1 | 1 | 0 |
| Veränderungswerte | 315.857 Sätze | 1 | 1 | 1 | 0 |

Vereinigung aller vier Leser: **162 Gruppen**. Der einzige scheinbare
k = 2 (`low`) ist als Artefakt belegt: eine OR-Zeile
(`10.1002/fsn3.1050`) und eine Tertilzeile (`10.1186/s12889-026-26824-4`)
landeten in derselben Gruppe; nach Filter auf Effekttyp g bleibt k = 1.
Von den 513 Effektzeilen sind nur **5 SOL-artig** (197 beta, 160 OR, 112
mean_diff, 15 g, 15 smd, 12 RR, 2 HR).

### 4.4 End-to-End-Läufe (05.11.2026, je ca. 4 h)

| Kennzahl | Netzlauf | Harness-Lauf |
|---|---:|---:|
| Quellen | 127 | 112 |
| registrierte Studien | 26 | 34 |
| Volltext vorhanden | 9 (35 %) | 20 (59 %) |
| Effekte extrahiert | 14 | 21 |
| davon `mean_diff` | 3 | 16 |
| davon mit Konfidenzintervall | 0 | 2 |

Beide Läufe erzeugten PDF-Berichte. Der Netzlauf zeigt den Kern des Problems:
ohne Volltexte bleiben fast nur verbale, nicht poolbare Befunde.

### 4.5 Der Saat-Korpus-Versuch (gescheitert, und zwar an der Paywall)

Die einzige publizierte Metaanalyse zur Frage — *Sleep Medicine* 2020,
DOI `10.1016/j.sleep.2019.02.017`, PMID 31982807 — ist **nicht offen**
(kein PMCID, `isOpenAccess = N`). Sie nennt im Abstract: 7 Trials, 387
Teilnehmer, SOL MD −0,36 h (95 %-CI −0,49 bis −0,24), SOT −0,62 h
(−0,80 bis −0,45), DLMO −0,82 h (−1,23 bis −0,41), TST +0,38 h.

Aus ihrer Referenzliste (46 Einträge, ohne DOIs) wurden 8 Trial-Kandidaten
extrahiert, 8 von 8 DOIs aufgelöst, dann PMC-Zuordnung:

- **7 von 8 ohne PMC-Volltext** (Europe-PMC-Titelsuche und NCBI-ID-Konverter
  stimmen überein),
- 1 PMCID (`PMC5872230`) — eine Langzeit-Follow-up-Studie, die die
  Metaanalyse vermutlich ausgeschlossen hat,
- Lauf aller Leser auf diesem Dokument: **0 Zeilen** (23 + 1 + 2
  Ablehnungen).

**Ergebnis: der Saat-Weg liefert k = 0, und die Schranke ist der Zugang,
nicht die Extraktion.** Der offene Korpus enthält die Studien nicht, weil sie
nicht offen sind — ein Negativbefund aus ihm ist ein Befund über die offene
Teilmenge, nicht über die Literatur.

## 5. Die vier Blocker (in dieser Reihenfolge)

**B1 — Ausbeute je Endpunkt.** 42.396 Tabellenzeilen ergeben 513 Effektzeilen,
aber nur 5 SOL-artige und nach Effekttyp-Filter k = 0. Es ist unbekannt, an
welcher Filterstufe die Masse verloren geht (Tabellenerkennung? Spaltenpaar?
Gate? Outcome-Zuordnung?). Ohne dieses Wissen ist jede weitere Optimierung
Raten.

**B2 — Keine Referenzvalidierung.** Pooling, g↔MD-Umrechnung und
Heterogenitätsschätzer sind gegen synthetische Fixtures und Unit-Tests
geprüft, aber nie gegen ein veröffentlichtes gepooltes Ergebnis. Es gibt
keinen Beleg, dass der Agent bei bekannter Wahrheit dasselbe herausbekommt.

**B3 — Screening/Relevanz-Gate.** Im Harness-Lauf (05.11.) nahm der Agent
themenfremde arXiv-Quellen auf (Gesichtsmimik-Erkennung, Gruppentheorie,
N-Körper-Code). Das Gate filterte sie erst später; eine Quelle blieb bis zum
Ausschluss unter Schwelle sichtbar.

**B4 — Zugang zu geschlossener Literatur.** Sieben RCTs hinter Paywall. Ohne
Bibliothekszugang oder manuelle Erfassung ist diese Evidenzbasis für den Agenten
nicht erreichbar; die Frage muss entweder anders zugeschnitten oder die
Tabelle von Hand erfasst werden.

## 6. Bereits entschieden (nicht neu verhandeln)

1. **Zwei Change-Modelle:** `reported` (Veränderung ± SD im Satz → g exakt,
   ρ irrelevant, `rho = null`) und `prepost`
   (`SD_change = sqrt(SD_pre² + SD_post² − 2ρ·SD_pre·SD_post)`), primär
   ρ = 0,5 offengelegt (`rho_assumed: true`) plus Sensitivitätsgrid
   0,0/0,3/0,5/0,7/0,9.
2. **Outcome-Gruppierung** über normalisierte Namen plus geprüfte
   Synonymtabelle; keine Ähnlichkeitsheuristik. Zielmaß-Wortlaut bleibt
   Anzeigename.
3. **Pooling/2:** adjustiert vs. unadjustiert und verschiedene
   Follow-up-Zeitpunkte werden nie in einen Pool gemischt; unbekannte
   Zustände bilden einen eigenen, markierten Pool.
4. **Hartung-Knapp-Sidak als Standard**, Fixed-Effect nur als
   Vergleichsspalte, Prediction Interval erst ab k ≥ 3.
5. **k-Gate für Moderatoren:** Subgruppen unter k = 3 tragen keine
   Q-between-Aussage.
6. **Netz-Budget:** höchstens 2–3 Läufe je Untersuchungsfrage, kein Lauf ohne
   ausdrückliche Freigabe, vorher Telemetrie des letzten Laufs auswerten.

## 7. Auftrag: Arbeitspakete mit Akzeptanzkriterien

Der Plan soll diese fünf Pakete in eine Reihenfolge bringen, Aufwand und
Risiko schätzen und für jedes Paket Dateien, Tests und Abbruchkriterien
benennen.

### A — Ausbeute-Funnel messen (Voraussetzung für alles Weitere)

Ziel: für den SOL-Korpus eine Tabelle „1.056 Dokumente → n Tabellen → n
Zeilen → n Kandidaten → n gespeicherte Zeilen → n poolbare Zeilen", jeweils
mit Ablehnungsgrund und Anzahl. Heute existieren nur die Endpunkte dieser
Kette.

Akzeptanz: ein Skript, das den Funnel reproduzierbar ausgibt; jede Stufe mit
Zahl und Grund; das Ergebnis zeigt, welche **eine** Stufe den größten Verlust
verursacht. Kein Netzzugriff nötig (XML liegt lokal).

Verifikation: Skriptlauf auf `data/bench/sol/manifest_all.json`, Ausgabe als
JSON + Markdown, Zahlen gegen die bestehenden Befunde (513 Zeilen) konsistent.

### B — Referenzdatensatz mit bekannter Wahrheit

Ziel: sieben Zeilen (SOT/SOL je Arm, n, SD) der Kinder-Metaanalyse als
Referenz erfassen, k = 7 per Konstruktion, dann Pooling und g↔MD-Umrechnung
gegen SOL −0,36 h (−0,49 bis −0,24) prüfen.

Akzeptanz: Referenzdatei mit Quelle je Zahl (Tabelle/Seite), als **manuell
erfasst** markiert; ein Vergleichslauf, der die Abweichung des Agenten zur
publizierten Schätzung beziffert; Abweichung erklärt oder als offen benannt.

Risiko: ohne Zugang zur Tabelle nicht durchführbar — dann muss der Plan eine
Alternativquelle (offenes Referenz-Review) benennen.

### C — Tabellenlese-Pfad härten

Ziel: erklären, warum aus 42.396 Tabellenzeilen nur 513 Effektzeilen werden,
und die größten deterministischen Verluste beheben (Spaltenerkennung,
Einheiten, „mean (SD)"-Varianten, Mehrzeilen-Köpfe).

Akzeptanz: Vorher/Nachher-Zahlen auf demselben Korpus; kein Rückgang der
bestehenden Tests; jede Lockerung eines Gates mit Begründung und einem
Fall, den sie rettet — nie pauschal.

### D — Screening gegen Thementrift

Ziel: das Relevanz-Gate so schärfen, dass themenfremde Quellen vor der
Aufnahme abgelehnt werden, mit Begründung und ohne die Trefferquote echter
Studien zu senken.

Akzeptanz: gemessene Precision/Recall auf einem annotierten Satz (die
bestehenden Läufe liefern die Positiv- und Negativfälle), Vorher/Nachher
ausgewiesen.

### E — Bericht: Ehrlichkeit über k

Ziel: der Bericht muss bei k = 1 oder k = 0 explizit sagen, dass keine
gepoolte Zahl existiert, und die Coverage-Zeile („40 gelesen, 4 zum Zielmaß")
prominent zeigen.

Akzeptanz: ein Bericht aus einem Lauf mit k = 1 enthält keinen Satz, der wie
ein gepooltes Ergebnis klingt; PRISMA-Zahlen stimmen mit der DB überein.

## 8. Randbedingungen für den Plan

- **Keine Netzkäufe ohne Freigabe.** Tests und Funnel-Analysen laufen offline
  auf `data/bench/sol/xml/`.
- **Geschützte Dateien** (Abschnitt 2, Punkt 8) dürfen lokal geändert, aber
  nicht committet werden; der Plan muss sagen, wie deren Änderungen
  dokumentiert und getestet werden.
- **Secrets** niemals in Code, Chat oder Commit; `.env` wird nicht gelesen.
- **Commits** klein und thematisch, Footer:
  `🤖 Generated with Codebuff` / `Co-Authored-By: Codebuff <noreply@codebuff.com>`.
- **Jeder Schritt hinterlässt ein Artefakt** (Skript, JSON, Markdown) plus
  Commit.
- **Keine Zahlen ohne Quelle.** Im Plan jede Aufwandsschätzung als Schätzung
  markieren.

## 9. Was der Plan enthalten soll

1. **Reihenfolge und Abhängigkeiten** der Pakete A–E, mit Begründung, warum
   diese Reihenfolge und nicht eine andere.
2. **Je Paket:** betroffene Dateien, neue Tests (Name + was sie prüfen),
   Verifikationsbefehl, Akzeptanzkriterium, geschätzter Aufwand in Sitzungen,
   Risiko und Abbruchkriterium.
3. **Messgrößen**, an denen Fortschritt erkennbar ist (z. B. poolbare Zeilen je
   Endpunkt, k je Endpunkt, Abweichung zum Referenzdatensatz).
4. **Was bewusst nicht getan wird** und warum.
5. **Offene Fragen an den Menschen**, maximal fünf, jede mit der Information,
   die ohne Antwort fehlt.

## 10. Datenlage (Pfade)

| Inhalt | Pfad |
|---|---|
| Korpus-Manifest (1.059) | `data/bench/sol/manifest_all.json` |
| XML-Volltexte (1.056) | `data/bench/sol/xml/` (gitignored) |
| Effektzeilen DB | `data/bench/sol/direct_all.db` |
| Arm-/Text-/Change-DBs | `data/bench/sol/arm_all.db`, `text_arms.db`, `change_arms.db` |
| Befunde | `data/bench/sol/abschlussbericht_20261107.md`, `seed_meta_befund_20261107.md` |
| Seed-Versuch | `data/bench/sol/seed_*.json`, `seed_xml/` |
| Stand/Reifegrad | `data/bench/stand_20261107.md` |
| Lauf-Auswertungen | `data/bench/net_run_final.md`, `harness_run_final.md` |
| Testlog | `data/runs/pytest_full_20261107b.log` |

## 11. Reproduktion (Befehle)

```bash
export PYTHONIOENCODING=utf-8
.venv/bin/python.exe -m pytest research_agent/tests -q
.venv/bin/python.exe scripts/convert_text_arms_xml6.py \
  --manifest data/bench/sol/manifest_all.json \
  --xml-dir data/bench/sol/xml --db data/bench/sol/text_arms.db
.venv/bin/python.exe scripts/convert_change_arms_xml6.py \
  --manifest data/bench/sol/manifest_all.json \
  --xml-dir data/bench/sol/xml --db data/bench/sol/change_arms.db
.venv/bin/python.exe scripts/pool_direct_effects_xml6.py
```

## 12. Ein Satz, der den Auftrag zusammenfasst

Der Agent kann alles außer dem einen, worauf es ankommt: aus einem großen
offenen Korpus genug belegte Effekte je Endpunkt herausziehen, dass k ≥ 2
entsteht — plane zuerst die Messung dieses Verlusts, dann die Behebung, dann
die Validierung gegen eine bekannte Wahrheit.
