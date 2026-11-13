# Experiment: Multi-Model Cross-Validation mit Qwen-Adjudikation

Stand: 2026-11-13
Status: **PLANUNG - keine Modellausgabe, kein Netzlauf, kein eingefrorener Datensatz**
Art des Dokuments: Infrastrukturprüfung, Blockeranalyse, Implementierungsplan

Dieses Dokument beantwortet zwei Fragen: Was ist an Infrastruktur vorhanden, und
was fehlt, bevor Phase A gestartet werden darf. Es enthält keine Ergebnisse und
keine geschätzten Genauigkeiten.

## 1. Kurzfazit

Das Experiment ist in dieser Form **noch nicht startbar**. Drei Befunde sind
vorgelagert und unabhängig voneinander:

1. **GLM 5.3 ist derzeit nicht messbar.** Im vorhandenen Dev-Lauf
   `c1_dev_20261112_glm_5_3` sind **19 von 26** `raw_response` leer und eine
   Antwort abgeschnitten; das ergibt 20 Parse-Fehler und 34/140 exakte Felder.
   Ein leerer Content-Fall ist keine Modellaussage, sondern ein
   Endpoint-/Payload-Problem. Solange das offen ist, vergleicht das Experiment
   zwei Modelle und ein Nichts.
2. **Es gibt keinen geeigneten Referenzdatensatz mit Armwerten.** Yun-Dev ist zu
   klein und am Ceiling (Qwen 140/140), Yun-Test ist verbraucht und ausdrücklich
   verboten, P0 ist der geplante G5-Holdout und damit ebenfalls verboten, und
   Goldstandard A enthält **keine** Armfelder (siehe 3.5). Ohne neue,
   menschliche Arm-Annotation gibt es keine Phase D.
3. **Es gibt keinen Multi-Modell-Runner und keinen Konfliktvergleicher.** Der
   vorhandene Runner ist auf 26 Dev-Records fest verdrahtet; der vorhandene
   Evaluator bewertet genau ein Modell gegen eine Referenz. Phase B, C und E
   sind vollständig neu zu bauen.

Der Plan darunter ist so gebaut, dass jede Phase ein eigenes, prüfbares
Artefakt hinterlässt und kein Schritt Modellausgaben erzeugt, bevor Datensatz,
Referenz, Prompt und Hashes eingefroren sind.

## 2. Geltungsbereich und Abgrenzung

- Kein Modelllauf in dieser Planungsphase. Ein Lauf braucht eine eigene,
  ausdrückliche Freigabe (AGENTS.md, Abschnitt "Läufe und Kosten").
- Keine Änderung an geschützten Dateien: `research_agent/orchestrator.py`,
  `research_agent/config.py`, `research_agent/llm/engine.py`,
  `research_agent/meta/pooling.py`, `research_agent/meta/extraction.py`,
  `research_agent/report.py` stehen in der `.gitignore`-Sektion
  "Kernbausteine".
- Der verbrauchte Yun-Test (249 Records, 1308 Felder) wird nicht verwendet,
  weder zur Prompt-Optimierung noch als Evaluationsgrundlage.
- Der P0-Holdout bleibt G5-reserviert. Kein Artikel der 30er-Shortlist darf in
  dieses Experiment.
- Die Qwen-Adjudikation ist ein Modellvorschlag, keine Ground Truth. Die
  Bewertung erfolgt ausschließlich gegen die menschliche Referenz.

## 3. Infrastrukturprüfung

### 3.1 LLM-Zugang

| Gegenstand | Befund | Ort |
|---|---|---|
| Backend | TUDaGPT (OpenAI-kompatibel), Modellwahl über `TUDAGPT_MODEL`, Überschreibung per `--model` in `main.py` | `research_agent/main.py`, `research_agent/llm/engine.py` |
| Modellnamen | `gwdg/qwen3.5-397b-a17b`, `gwdg/deepseek-v4.1-flash-1017`, `gwdg/glm-5.3` sind belegt und gelaufen | `model_screen_20261112.md`, `run_manifest.json` der Läufe |
| Parameter | `temperature=0.0`, `max_tokens=900`, `concurrency=3`, `reasoning_effort="none"`, optional `response_format=json_object` | `run_c1_dev_pilot.py`, `llm/engine.py` |
| Antwortauswertung | Nur `choices[0].message.content` wird gelesen; leere Antworten werden als Warnung geloggt und als `""` zurückgegeben | `llm/engine.py`, Block `if resp.status == 200` |
| Kosten/Telemetrie | Token- und Latenztelemetrie pro Aufruf vorhanden | `llm/engine.py`, `_record_call` |

Konsequenz: Die Modellwahl ist ohne Codeänderung möglich (Umgebungsvariable
bzw. `--model`), der Payload dagegen nicht. Genau dort liegt der GLM-Blocker.

### 3.2 Runner und Evaluator

| Gegenstand | Befund |
|---|---|
| `public_benchmark/scripts/run_c1_dev_pilot.py` | Prompt-Versionen v2-v6, Resume, Manifest mit Input-/Prompt-/Modell-Hash, Rohantworten in `dev_raw.jsonl`. **Hart verdrahtet:** `INPUT_PATH = evaluation/c1_pilot/dev_input.jsonl`, Abbruch bei `len(records) != 26`, Abbruch bei `split != "dev"`. |
| `public_benchmark/scripts/evaluate_c1_dev_pilot.py` | Genau ein Ausgabesatz gegen genau eine Referenz; Feldgenauigkeit, Abdeckung, fehlend/falsch/halluziniert, MAE, Null-Disziplin. Keine Modell-zu-Modell-Logik. |
| `check_c1_gates.py`, `check_c1_test_isolation.py`, `c1_test_projection.py` | Gate- und Isolationsprüfungen, wiederverwendbar als Vorbild für die Freeze-Prüfungen dieses Experiments. |
| Vorhandene Modelläufe | Qwen v6c 140/140, DeepSeek 134/140, GLM 34/140 - alle auf den 26 Dev-Records. |

Wiederverwendbar sind Prompt-Bau, Manifest- und Hash-Logik, Resume-Mechanik und
die Auswertungssemantik. Nicht wiederverwendbar sind der feste Eingabepfad, die
26-Record-Sperre und die Ein-Modell-Annahme des Evaluators.

### 3.3 Vorhandene Korpora

| Korpus | Umfang | Armwerte | Status für dieses Experiment |
|---|---|---|---|
| Yun gesamt | 699 ICO-Records, 120 Artikel | ja | Referenz stammt aus konsolidierter Doppelannotation, keine Quellenbelege, kein Zeitpunktfeld |
| Yun-Dev | 26 Records, 6 Artikel, 140 Felder | ja | zu klein, Qwen am Ceiling, widerspricht "neuer unabhängiger Datensatz" |
| Yun-Test | 249 Records, 64 Artikel, 1308 Felder | ja | **verbraucht und gesperrt** |
| P0 / G5 | 30 Artikel (XML abgerufen), 36 Outcome-Slots in 14 geprüften Artikeln | nein, noch nicht annotiert | **G5-reserviert, verboten** |
| Goldstandard A | 30 Dokumente, 69 Effektzeilen | **nein** | siehe 3.5 |
| Goldstandard B | 0 Zeilen, 30 offene Dokumente | nein | Zweitannotation steht aus |

### 3.4 P0-Stand (nur zur Abgrenzung)

30 Shortlist-Artikel sind als XML abgerufen (`fulltext_retrieval_manifest_v1.json`,
30/30 gespeichert, `model_used=false`). Die Volltextprüfung liefert 36
Outcome-Slots in 14 Artikeln, davon 16 unabhängig verwendbar. Das ist der
G5-Kandidat und gleichzeitig **nicht** ausreichend für die geforderten 50-100
Records. Für dieses Experiment ist P0 aus zwei Gründen unzulässig: G5-Reservierung
und unvollständige Annotation.

### 3.5 Goldstandard A ist kein Armwert-Datensatz

Geprüft am eingefrorenen Stand (`goldstandard_A.json`, Hash
`d9bb867c303dc19ddaf90cce3414ada0f4484b5a03881d65261950db0762a810`):

- 30 Dokumente, 17 davon mit Effektzeilen, zusammen 69 Zeilen.
- Effekttypen: 28 OR, 17 beta, 7 HR, 6 r, 5 g, 4 SMD, 1 MD, 1 RR.
- Felder je Zeile: `effect`, `se`, `ci_low`, `ci_high`, `n`, `quote`,
  `quote_start`, `quote_end`, `source_table`, `certainty`, `time_point`.
- **Treffer für `intervention_mean`, `comparator_mean`, `intervention_n` in der
  Datei: 0.** Es gibt keine getrennten Armwerte.
- Designs: 11 observational, 7 aggregate, 4 parallel RCT, 3 crossover RCT,
  5 unknown. Für eine Extraktion von Interventions- und Kontrollarm sind
  aggregat- und observational-Zeilen strukturell ungeeignet.

Damit ist A als Referenz für N/Mean/SD/Events **nicht** verwendbar, obwohl es
menschenannotiert, verblindet, gehasht und Yun-disjunkt ist. Es ist ein
Effektzeilen-Datensatz, kein Armwert-Datensatz. Diese Unterscheidung ist der
wichtigste Befund der Infrastrukturprüfung.

### 3.6 Testinfrastruktur

`public_benchmark/tests/` enthält drei Testmodule (dCBTI-Überlappung,
externer Benchmark, Zeitpunkt-Schema). Die geforderten Tests für
Record-Zuordnung, Feldvergleich, Rundungstoleranz, Quellenbelege,
Unveränderlichkeit und G5-Ausschluss existieren noch nicht.

## 4. Blocker

| ID | Blocker | Wirkung | Behebung |
|---|---|---|---|
| B0 | GLM 5.3 liefert 19/26 leeren Content, 1 abgeschnittene Antwort | drittes Modell nicht messbar; Aussage "drei Modelle" nicht belegbar | Payload/Response-Diagnose: `finish_reason`, `usage`, `reasoning_content`, `max_tokens`; ein Testaufruf nur mit Freigabe |
| B1 | Kein Referenzdatensatz mit Armwerten, der nicht verbraucht oder G5-reserviert ist | Phase D unmöglich, kein Goldstandard | neue menschliche Annotation, siehe Abschnitt 5 |
| B2 | Kein Multi-Modell-Runner, kein Vergleichs-/Adjudikationswerkzeug | Phasen A-C nicht ausführbar | neue Skripte, siehe Abschnitt 6 |
| B3 | Qwen 3.5 ist Arm A **und** Adjudikator | Selbstpräferenz-Bias bei Phase C | verblindete Vorschlagsreihenfolge, Zuordnungstabelle getrennt gespeichert, Selbstwahl explizit berichten |
| B4 | Extraktionsschema liefert nur `source_note`, nicht Seite/Tabelle/Beleg je Feld | Phase-B-Kategorien 5 und 6 nicht bestimmbar | Schema v1 mit strukturierten Belegfeldern je Zahl |
| B5 | Kein G5-disjunkter Explorationsdatensatz vorhanden | Auftragsbedingung "unabhängiger Datensatz" nicht erfüllt | Partitionierung, siehe Abschnitt 5 |

## 5. Datensatzentscheidung

### 5.1 Optionen

**Option A - neues PMC-Set, artikeldisjunkt zu G5 (empfohlen).**
Aus dem bereits vorhandenen September-2026-Frame (596 artikeldisjunkte
Kandidaten, 415 nach Abstract-Screening für Volltext vorgemerkt) wird eine
eigene Teilmenge gezogen, die **keinen** der 30 G5-Shortlist-Artikel enthält.
Ziel: 25 Artikel, 60-80 Armwert-Records, gemischt kontinuierlich/binär, mit
Tabellen- und Fließtextwerten, Mehrarm- und Follow-up-Fällen. Annotation
menschlich, vor Phase A eingefroren.

- Vorteile: erfüllt alle Bedingungen des Auftrags; Kandidatenpool existiert
  bereits; Volltextzugriff über Europe PMC ist belegt (30/30).
- Kosten: die Annotation ist der dominante Aufwand (Abschnitt 9).
- Risiko: Ausbeute je Artikel unbekannt; 25 Artikel liefern nicht garantiert
  60-80 vollständige Records. Deshalb Reserveartikel einplanen und die
  tatsächliche Recordzahl vor dem Einfrieren feststellen.

**Option B - Goldstandard A armweise nachannotieren.**
30 Dokumente sind vorhanden und gehasht, aber 18 von 30 sind aggregat oder
observational, und es fehlen alle Armwerte. Nachannotation wäre eine neue
Vollerhebung auf ungeeigneten Designs. **Verworfen.**

**Option C - Yun-Dev verwenden.**
26 Records, 140 Felder, Qwen bei 140/140. Kein Spielraum für "besser als Qwen",
und es ist kein neuer Datensatz. **Verworfen.**

**Option D - P0 verwenden.**
G5-reserviert und unvollständig annotiert. **Verworfen.**

### 5.2 Empfehlung und Partitionsregel

Option A. Damit G5 sauber bleibt, wird die Zuweisung **vor** der Annotation
deterministisch und dauerhaft festgeschrieben:

- `reserved_for: "g5_holdout"` für die 30 PMCIDs aus
  `fulltext_candidate_priority_v1.json` (Shortlist) und alle 36 Slots.
- `reserved_for: "crossval_exploration"` für die in diesem Experiment
  gezogenen Artikel.
- Ein Artikel erhält genau ein Label. Ein späterer Tausch ist ausgeschlossen;
  bei Bedarf wird ein neuer Artikel gezogen, nie ein reservierter umgewidmet.
- Prüfskript: Schnittmenge der beiden PMCID-Mengen muss leer sein, und die
  Schnittmenge mit Yun-Freeze (275 Records) sowie Yun-Dev/-Test muss leer sein.

## 6. Implementierungsplan

Alle Pfade relativ zu `public_benchmark/evaluation/multi_model_cross_validation/`.

### Phase 0 - Einfrieren (Gate vor jedem Modellaufruf)

| Artefakt | Inhalt |
|---|---|
| `dataset_manifest.json` | Artikel, PMCIDs, Record-IDs, `reserved_for`, SHA-256 je Input (XML/PDF/Supplement), Referenz-Hash, Artikeldisjunktheit gegen Yun-Freeze und G5 |
| `reference.jsonl` | menschliche Armwerte je Record und Feld, mit Belegstelle; vor Phase A erzeugt und gehasht |
| `prompt_v1.md` + `prompt_manifest.json` | identischer Prompt für alle drei Modelle, SHA-256, Schema-Version |
| `schema_v1.json` | Felder: DOI, Study ID, Outcome, Instrument, Zeitpunkt, je Arm N/Mean/SD/Events, je Zahl Seite, Tabelle/Abschnitt, Originalkontext, Einheit, Zuordnungssicherheit |
| `freeze.json` | Prompt-Hash, Schema-Hash, Modellliste mit exakten Modellnamen, Temperatur, `max_tokens`, Datum, Freigabevermerk |

Regel: `freeze.json` existiert, bevor ein Modell aufgerufen wird. Ohne diesen
Hash darf kein Runner starten; der Runner prüft ihn selbst.

### Phase A - unabhängige Extraktion

Drei Läufe, je ein eigener Ordner, keine gemeinsame Sicht:

```
runs/<run_id>/annotation_qwen.jsonl
runs/<run_id>/annotation_deepseek.jsonl
runs/<run_id>/annotation_glm.jsonl
```

- Ein Prozess pro Modell, gleicher Input, gleicher Prompt, gleiche Supplemente.
- Jede Zeile trägt `model`, `model_version`, `prompt_sha256`, `input_sha256`,
  `timestamp`, `raw_response_sha256`.
- Schreibweise: einmalig schreiben, danach nur lesen. Ein `--resume` darf
  fehlende Records ergänzen, niemals vorhandene überschreiben; das wird im
  Manifest festgehalten.
- Kein Modell erhält Referenzwerte, andere Modellausgaben oder Hinweise auf
  erwartete Werte.

### Phase B - deterministischer Vergleich

Neues Skript `compare_annotations.py`, ohne Modellaufruf:

- Schlüssel: `record_id` + Feldname. Record-Zuordnung ausschließlich über
  `record_id`, nie über Textähnlichkeit.
- Numerischer Vergleich nach Normalisierung (Dezimalkomma, Tausendertrenner,
  Einheiten). Zwei Stufen: `equal` (nach Normalisierung exakt) und
  `near` (relative Abweichung <= 1 %, nur berichtet, nicht als Einstimmigkeit
  gezählt).
- Kategorien 1-6 wie im Auftrag; Kategorie 5 und 6 nur, wenn die
  Belegfelder aus `schema_v1.json` gefüllt sind.
- Ausgaben: `model_agreement.json`, `model_disagreements.jsonl`,
  `model_comparison_report.md`, `model_error_matrix.csv`.
- Determinismus: keine Zufallselemente, keine Zeitabhängigkeit, sortierte
  Ausgabe; ein zweiter Lauf muss byte-identisch sein (Test).

### Phase C - Qwen-Adjudikation

Neues Skript `adjudicate_conflicts.py`:

- Eingabe: Originalstudie, drei Vorschläge, deren Belege, Konfliktliste.
- **Verblindet:** Die drei Vorschläge werden als `candidate_1..3` übergeben,
  die Zuordnung Modell zu Buchstabe steht nur in `adjudication_blinding.json`
  und wird erst nach dem Lauf ausgewertet. Sonst bevorzugt Qwen systematisch
  seine eigene Antwort.
- Ausgabe je Konflikt: Record-ID, Feld, Wert, Begründung, Seite,
  Tabellenreferenz, Beleg, "vermutlich richtig/falsch" je Modell, Konfidenz,
  Status `resolved` / `unresolved` / `insufficient_evidence`.
- `unresolved` ist ein zulässiges und erwartetes Ergebnis.
- Die Adjudikation schreibt ausschließlich in `qwen_adjudication.jsonl`, nie in
  die drei Originalannotationen.

### Phase D - Bewertung gegen die menschliche Referenz

Neues Skript `evaluate_variants.py`, fünf Varianten:

| Variante | Definition |
|---|---|
| Qwen allein | Ausgabe Arm A |
| DeepSeek allein | Ausgabe Arm B |
| GLM allein | Ausgabe Arm C |
| Mehrheitsentscheidung | nur bei exakt gleichem Wert von >= 2 Modellen, sonst fehlend |
| Qwen-Adjudikation | Adjudikationswert, wo vorhanden, sonst Mehrheit, sonst fehlend |

Kennzahlen je Variante: Feldgenauigkeit, Record-Genauigkeit, Abdeckung,
fehlend/falsch, getrennt kontinuierlich/binär und je Feldtyp. Zusätzlich:
Anteil korrekt aufgelöster, falsch aufgelöster und ungelöster Konflikte; Anteil
Fälle, in denen alle drei falsch liegen; Anteil erkannter vs. tatsächlich
korrigierter Fehler; Anteil ursprünglich korrekter Werte, die die Adjudikation
verschlechtert.

Statistik: gepaarte Vergleiche (exakter McNemar-Test) Qwen allein vs.
Adjudikation und Qwen allein vs. Mehrheit, alpha 0.05, mit Bootstrap-CI. Vor
dem Einfrieren ist eine Power-Abschätzung zu dokumentieren; bei 60-80 Records
und 6-8 Feldern je Record sind nur größere Differenzen nachweisbar. Kleine
Unterschiede werden als "nicht entscheidbar" berichtet, nicht als Gleichstand.

### Phase E - Fehlerkorrelation

Neues Skript `error_correlation.py`:

- Paarweise Ko-Fehler-Matrix je Feldtyp (N, Mean, SD, Events) mit Phi-Koeffizient
  und rohen Quoten.
- Auswertung nach Tabellenstruktur (Mehrarm, Follow-up, Supplement,
  Fließtext-only), nach Design und nach kontinuierlich/binär.
- Getrennte Zählung: genau ein Modell falsch und die anderen richtig; zwei
  gleichzeitig falsch; alle drei falsch.
- Genauigkeit der Mehrheitsentscheidung getrennt nach Feldtyp.

### Abschluss

`final_evaluation.md` beantwortet die Forschungsfrage ausschließlich anhand der
menschlichen Referenz, mit expliziter Nennung der Grenzen (Stichprobengröße,
Designmix, ein Adjudikator, keine Zweitannotation der Referenz).
`reproducibility_manifest.json` pinnt alle Hashes, Skriptversionen und die
Reihenfolge der Schritte.

## 7. Automatisierte Tests

Neue Module in `public_benchmark/tests/`, Stil wie die vorhandenen Tests:

| Test | Prüft |
|---|---|
| `test_crossval_record_mapping.py` | Record-Zuordnung nur über `record_id`; fehlende/überzählige Records werden erkannt |
| `test_crossval_field_compare.py` | Numerische Normalisierung, Kategorien 1-4, `near` zählt nicht als Einstimmigkeit |
| `test_crossval_missing.py` | `null` vs. fehlendes Feld vs. 0; keine Imputation |
| `test_crossval_tolerance.py` | Rundungsband 1 % relativ, Grenzfälle |
| `test_crossval_evidence.py` | Belegfelder Pflicht bei `resolved`; Kategorien 5/6 nur mit Beleg |
| `test_crossval_immutability.py` | Vorhandene Annotation wird bei `--resume` nicht überschrieben; Hash bleibt |
| `test_crossval_g5_exclusion.py` | Schnittmenge mit G5-Shortlist und Yun-Freeze ist leer |
| `test_crossval_blinding.py` | Adjudikationsdatei enthält keine Modellnamen, nur `candidate_*` |

## 8. Freeze-Checkliste (Gate)

Kein Modellaufruf, solange nicht alle Punkte belegt sind:

1. `dataset_manifest.json` mit Input-Hashes und `reserved_for` vorhanden.
2. Artikeldisjunktheit gegen Yun-Freeze (275), Yun-Dev (26), Yun-Test (249)
   und G5-Shortlist (30) nachgewiesen.
3. `reference.jsonl` vollständig, gehasht, vom Annotator freigegeben, für die
   Modelle unzugänglich.
4. `prompt_v1.md` und `schema_v1.json` eingefroren und gehasht.
5. Modellnamen exakt festgeschrieben; GLM-Frage entschieden (B0).
6. `freeze.json` mit Datum und Freigabevermerk.
7. Power-Abschätzung dokumentiert.
8. Genau eine Freigabe für Phase A dokumentiert.

## 9. Aufwand, Kosten, Risiken

| Posten | Größe | Anmerkung |
|---|---|---|
| Menschliche Annotation | 60-80 Records x 6-8 Felder, 25 Artikel | dominanter Aufwand, nur manuell, nicht automatisierbar; Vorlage kann aus `fulltext_extraction_template_v1.md` abgeleitet werden |
| Modellaufrufe Phase A | 3 x 60-80 Aufrufe | mit vorhandener Infrastruktur machbar, Kosten gering gegenüber der Annotation |
| Adjudikation | nur Konfliktfelder, eher 20-40 % der Felder | zweite Runde, gleiche Größenordnung |
| Neue Skripte | 5 Skripte + 8 Tests | Phase B-E vollständig neu |
| GLM-Klärung | ein diagnostischer Aufruf | ohne Freigabe nicht durchführbar |

Risiken:

| Risiko | Wirkung | Gegenmaßnahme |
|---|---|---|
| GLM bleibt leer | Dreimodell-Aussage unmöglich | B0 vor Phase A lösen, sonst Experiment als Zweimodell-Vergleich deklarieren |
| Zu wenige vollständige Records | kleine Stichprobe, keine belastbare Aussage | Reserveartikel, Recordzahl vor Einfrieren feststellen |
| Qwen bewertet sich selbst | überschätzte Adjudikationsgüte | verblindete Kandidaten, Selbstwahlquote berichten |
| Referenzfehler | falsche Genauigkeiten | Belegpflicht je Zahl, Stichprobenprüfung der Referenz, Referenzfehler getrennt zählen |
| G5-Kontamination | G5 verliert seinen Wert | Partitionsregel, Prüfskript, Hashes |
| Annotation sieht Modellausgaben | Bewertung wertlos | Referenz vor Phase A, Zugriff getrennt |

## 10. Offene Entscheidungen (vor Phase 0)

1. **Datensatz:** Option A bestätigen, oder eine andere Quelle vorgeben.
2. **Annotation:** wer annotiert die 60-80 Armwert-Records, und in welchem
   Zeitfenster?
3. **GLM:** Payload-Diagnose freigeben (ein Aufruf) oder GLM durch ein anderes
   verfügbares Modell ersetzen?
4. **Schema:** Erweiterung um Seite/Tabelle/Beleg je Zahl bestätigen; das
   vorhandene v6-Schema liefert nur eine `source_note`.
5. **Adjudikator:** Qwen 3.5 wie gefordert, mit verblindeten Kandidaten - oder
   ein viertes, nicht beteiligtes Modell?
6. **Zweitannotation:** Reicht eine menschliche Erstannotation als Referenz,
   oder ist der B-Rücklauf (Kappa >= 0,80) Voraussetzung?

## 11. Nächster Schritt

**Vor jedem Modellaufruf:** die sechs offenen Entscheidungen aus Abschnitt 10
klären, dann Phase 0 aufsetzen (Manifest, Schema, Prompt, Referenz, Hashes).
Der größte Hebel ist die Referenzannotation, nicht die Modellseite: Ohne sie
gibt es keine Phase D, und ohne Phase D beantwortet das Experiment die
Forschungsfrage nicht. Der GLM-Blocker ist dagegen billig zu klären und
entscheidet, ob überhaupt drei Modelle verglichen werden.

**Kein Modelllauf. Keine Prompt-Änderung. Keine Testwiederverwendung.**
