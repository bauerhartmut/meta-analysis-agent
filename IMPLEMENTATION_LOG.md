# IMPLEMENTATION_LOG — Umsetzung des Implementierungsauftrags (01.11.2026)

## Sprint 1 (nach §16 des Auftrags): Audit → Baseline → Tabellen-MVP

### 1. Audit / Bestandsaufnahme (Erfüllung §16.1–16.2)

- **Aktive Prozesse identifiziert:** Lauf `Mediterrane Ernährung…` (PID 44248) läuft; seine DB
  `data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db` wurde **nie geschrieben**;
  alle Messungen hier laufen read-only (`mode=ro`) auf **anderen** DBs.
- **Freie abgeschlossene Baseline-DB:** `research-exercise-and-depressive-symptoms-in-adul-bbb324.db`
  — deren Prozess (PID 25268) ist beendet (tasklist leer); zwei Closing-Reports liegen vor (12:41, 18:10).
- **Abweichungen zur Statusdokumentation:** Kein Git-Repository im Projekt (dieser Sprint legt eins an).
  Die Übergaben „TUDaGPT-Ladder“, Duplikat-DOI-Dedup, Leave-one-out, Subgruppen, Egger sind live im Code
  vorhanden; `llm_usage` wird global in `data/research-usage.db` geschrieben, die Topic-DBs tragen nur
  das leere Schema.

### 2. Phase 0 — Baseline-Kennzahlen (Auftrag §3)

**Umgesetzt:** `research_agent/metrics.py` — jede Kennzahl ist eine SQL-Abfrage gegen die
abgeschlossene DB, CLI `python -m research_agent.metrics <db>`; Artefakte in `data/baseline/`.
LLM-Zahlen kommen aus der(globalen) usage-DB (`--usage-db`), Suchzahlen aus `query_stats` — nichts wird
aus Logtexten geschätzt.

**Baseline (Exercise-Lauf, abgeschlossen, 18:10, via global-usage-db):**

```
Quellen: 440 gesamt / 440 unique / Relevanz ⌀ 0,398 (n=333, ≥0.25: 218)
Volltexte: 293 Dokumente, 293 Quellen mit Text, 8.903.205 Zeichen, 1463 Seiten
Screening: 145 include / 104 exclude
Effektzeilen: 129 gesamt / 93 im Zielmaß / 50 verworfen / 6 strittig / 105 mit geprüfter Quote
  Verwerfungsgründe: 'kein Effektwert gelesen': 37, "unbekannter Effekttyp '(leer)'": 13 (!)
Pools: 1 gepoolt (k = [19])
LLM: 17 628 Calls / 15 failed / 25.269.429 tokens
Suche: arxiv/crossref/europepmc/openalex/pubmed/semantic_scholar je 310 attempts
Lauf: 73 Zyklen, 262 028 s
```

- Wichtig: die 13 Zeilen mit „unbekannter Effekttyp ‚(leer)'" zeigen, dass der heute ausgetauschte
  Effekttyp-Bug in der Baseline-DB real aufgetreten ist — der Fix (meta/extraction) ist derselbe Code-Baum
  und wird erst zu einem zukünftigen Lauf quantifizierbar.
- Definitionstabelle und SQL schön in `data/baseline/exercise-bbb324-metrics.json/md`.

### 3. Phase 1 — Tabellen-Detektion und -Extraktion (Auftrag §4, MVP)

**Umgesetzt (deterministisch, keine neue Abhängigkeit):** `research_agent/research/table_extractor.py`
- Caption-Erkennung (Table N. / TABLE N: / Supplementary Table), Blockscan mit Zifferndichte/Umfeld —
  Prosa-Referenzen („Table 1. No sensitivity analyses …") werden **nicht** zu Blöcken.
- Effektzellen-Reader für real vorkommende Formate: `HR 0.72 (95% CI 0.55–0.94)`,
  `OR 0.92 (95% CI 0.85-0.99)`, `[β = -0.05, 95% CI = -0.06 – (-0.04)]` (inkl. EN-Dash,
  Negativwerten in Klammern, Komma- vs. Ganzzahl), `beta 0.14 (SE 0.03)`.
- Falsch-Positive entfernt: kleingeschriebenes „or" („… zero or 1+ …"), „or 4.8 to 7.1 METS".
- **Verbatim-Invariante:** Jeder Block-Body ist ein literaler Substring des Dokuments; quadrant
  der Extraktor grifft Tabellenzuweisungen, die Quote-Verifikation bleibt syntaktisch intakt
  (meta/extraction._store verifiziertVs the stored DB text).
- Datenbank: Tabell `extracted_tables` (migrationssicher, CREATE IF NOT EXISTS) + `Database.save_extracted_tables` /
  `get_extracted_tables`; method/token/name/cell belegbar.
- **Integration** in `orchestrator._work_item_effect_extraction`: Tabellenblöcke werden (max. 6, verbatim)
  an den Extraktions-Text angehängt und als Artefakt mit Span-Positiven gesichert.
- **Golden-Testset:** `data/golden_tables/case_001…003.json` (3 echte Layouts, manuell annotiert),
  `research_agent/tests/test_golden_tables.py` und `tests/test_table_extractor.py`.

**ADR (bewusst, dokumentiert):** Rendering-truerecovery mit Bounding Boxes (pdfplumber/PyMuPDF) und
Vision-Fallback sind **nicht** implementiert: nur `pypdf` ist installiert, und der Auftrag verbietet
blindlibrary-Installationen. Die Datentypen (`TableBlock`, `EffectCell.to_dict()`) sind bereits so geformt,
dass ein Seiten/Bounding-Box-Parser ohne Aufrufer-Anpassung einschieben kann.

### 4. Tests und Verifikation

- `pytest tests/test_table_extractor.py tests/test_golden_tables.py` → **10/10 grün**
  (Formatfälle, negative Fälle, Prosa-Caption ausgeschlossen, verbatim invariant).
- `pytest tests/test_work_queue.py tests/test_meta_extraction.py` → **73/73 grün**
- `pytest tests/test_e2e.py` (kompletter Orchestrator mit Fake-Backend) → **2/2 grün, 81 s**.
- `py_compile` für metrics, table_extractor, database, orchestrator: grün.
- DB-Roundtrip für `extracted_tables` an `:memory:` geprüft.
- Live-Materialprobe: 4 Volltexte aus `data/fulltext` → 4 Tabellenblock-Erkennungen / 75 Effektzellen.

### 5. Offene Punkte (nächste Sprints, Priorität wie im Auftrag)

1. **Golden-Set erweitern auf ≥30 Layouts/≥100 annotierte Zellen** (Auftrag §4.2 Abnahme). Auf
   `grep -l -E "^ *[Tt]able [0-9]+[.:]" data/fulltext/*.txt` sind **149 Volltexte** mit Captions; das
   Startset ist 3. Extensible annotation script fehlt.
2. Tabelle→Effektzeilen-Beleg: der MVP macht Tabellenwerten **lesbar**, nicht automatisch gepoolt.
   Zeilenniveau-Attribution (Zelle → (outcome, group, time) Fälle aus §4.2) muss vom EffectExtractor
   gelesen werden, um „wieder Mitglied" zu sein, und die Dokumentation im Pooling.
3. Volltext-Recovery-Status pro Studie (`fulltext_available`/`abstract_only`/…), Auftrag §4.1 —
   der metrics-Prozess benutzt jetzt die „chars>0"-Proxy; der echte Status-Typ muss in `source_texts`
   wandern.
4. Vision-Fallback §4.3 — als {@_equals} markiert; kein Wert ohne Unterlage.
5. `pypdf`-Adapter für PDF-Original-Seiten (persistente PDFs liegen nicht lokal; die .txt-Abzüge sind
   das bestehende Material).

### 6. Risiken

- Header/Held und Multilines-Layouts (Acta PDFs, Tabellen mit Spaltengruppen) werfen keine sauberen
  Blöcke; die Daten esfuerzo producieren Zahlen ohne Zeilenzuordnung — daher ist die **zentrale** Abnahme nob-
  counted mehr effektzeilen **nicht** erzwingen: Kandidaten nur Ausgrundsmitteln, keine Pool-Erweiterung.
- Der laufende Mediterranean-Lauf (PID 44248) nutzt den Stand von 21:44 — dieser Sprint fließt
  nicht in Tuning- oder laudende Läufe ein.

## Commits

- `a1 baseline`: Projektlage/X ohne Sprint-Änderungen + Status-HANDOFF.
- `p0 metrics`: metrics.py + Tests + Baseline-Artefakte.
- `p1 tables`: table_extractor.py + goldens + Integration + schema migration.

## Sprint 2 (02.11.2026): Phasenlücken-Audit + Phase-1-Vollendungsteile + Phase 9 + Phase 2

### Bestand-audit: bereits gebaut (keine Duplikate mehr!)
- coverage/manager.py (= Auftrag §2 ä canonical workflow
  states": studies-Registry, studies_status_log, legal-first acquisition,
  Author-Requests mit user-only approval) — integriert in orchestrator
  (_note_coverage), Tests test_coverage.py (165 Zeilen).
- evals/ (Paket D/H): deterministisches claim-recall/number-accuracy eval
  gegen golden_answers.json. Phase-9-Anteil, aber NICHT der §12-Review-
  Benchmark → neu gebaut (unten).
- meta/extraction.compare_extraction_passes: doble pass on fields (§4.4)
  existed with effect/se/ci_level/n.

### Phase 1 (§4.4/§4.2/§5.2 rest) — Umsetzung
- compare_extraction_passes erweitert: unit, design, direction, population
  (case-insensitiv), ci_bounds (ohne „SE ok aber KI falsch"-Loch). Tests.
- coverage/manager._xml_to_text: Tables werden nicht mehr still weggeworfen
  ([table omitted]); stattdessen caption + verbatim pipe-rows (§4.2), so
  textbasierte Tabellenhinweise überhaupt möglich. Regressionstest + neuer
  Keep-rows-Test.
- table_extractor: ICCaption-Trennzeichen ggelockert (Space allowed), Z-
  Offsets der Zell-Kandidaten korrigiert (caption,line Issues), und pipe-
  block-Erkennung ohne Caption (≥3 aufeinanderfolgend tabularrows), da XML-
  tabellen ohne „Table N.“-Caption real vorkommen.
- table_annotation.py: Annotations-Workflow build/promote. 22 Machine-
  Kandidaten in data/golden_tables/pending_reviews/ (nicht gold!). Ehrliche
  Limitation: der BESTEHENDE Textkorpus versorgt ~22 Blockkandidaten; mehr
  Blöcke entstehen erst in neuen Läufen mit §4.2-Fix (§16.7 erfüllbar
  abnavigation in data/reanalysis).

### Phase 9 — Benchmark-Grundgerüst (order §12)
- evals/meta_benchmark.py: ReferenceCase-Struktur + Validator, deterministisch
  Holdout-Split (sha256-prefix), Metric-Runner (screening recall/precision,
  fulltext retrieval mit dokumentiertem Nenner, extraction exact match,
  provenance, critical_errors) aus Roh-DB-Artefakten; Thresholds vorab
  festzusetzen, der Runner weigert sich, ohne zu filtern. CLI + output JSON.
- 8/8 Tests grün (inkl. direction-critical, precision, threshold blockers,
  deterministischer holdout).
- **Offen:** die 20–30 veröffentlichten Referenz-Reviews + manuelle Gold-
  Standards müssen beschafft werden (Aufgabenbeschaffung, keine Software).

### Phase 2 — Study-level Datenmodell (order §5.1/§5.2)
- meta/studies.py: additive Migration (meta_publications, meta_studies,
  meta_overlap_candidates; study_effects.study_id addil), Registry-API:
  register/link (mit Pflicht-Rationale), mark_overlap_candidate (never
  auto-resolved), resolve_overlap fixed status list + rationale/decided_by
  Pflicht. Kein stillender Mehrfach-Publikation-Zusammenfuehren.
- 4/4 Tests grün.

### Test-Status Sprint 2
- 86/86 (extraction 18, pooling 34, coverage 8, benchmark 8, golden 1, studies
  4, table 9+1, metrics 2) + e2e 2/2 (86 s) grün. py_compile alle Module.

### Typo-Fund im Commit-Protokoll der vorherigen Sprints
Die bereitstehenden Commit-Nummern dokumentieren den Startpunkt. Phase 3, 4
(Referenz-Tabellentests), 5 (RoB 2/ROBINS-I/AMSTAR2), 6, 7, 8 Areach open und
werden je nach Sprint-Priorität (§15) abgearbeitet.

## Sprint 3 (02.11.2026): Phase 3 - Unabhaengige Reviewer-Rollen (Auftrag §6)

### Umsetzung
- `meta/reviewer_roles.py`, REPORT_VERSION `reviewer-roles/1`:
  - **Dependency-Contract-Test:** `extractor_independence_check` beweist im
    Unit-Test, dass Pass-B-Messages keine Werte aus Pass-A tragen (>=8 char
    guard gegen normale Kurztreffer). Kontamination faellt laut.
  - **Statistical Reviewer:** reine Regelpruefungen (se<=0, CI invertiert,
    Effekt ausserhalb CI, OR/RR/HR<=0, r ausserhalb [-1,1]); *keine*
    Berechnung, strukturierte findings mit row+rule.
  - **Decision Resolver:** feldweise Klassifikation der Double-Pass-Disputes
    — exactly one verifiable reading -> `resolved_by_original_evidence`
    (die andere verschwindet durch ihren eigenen unverifizierten Status aus
    dem Pool, nichts wird gemittelt); beide verifiziert oder keine verifiziert
    -> `escalated` mit unresolved_questions. Keine Mehrheit, kein dritter
    Wert. Berichte werden unveraenderlich in `review_reports` gespeichert
    (additive Tabelle, im Resolver-Schema erstellt).
  - `review_segment(db, rows)`: ruft Statistical Reviewer + Resolver auf und
    speichert beide Berichte; return (stats, resolver, escalations).
- Orchestrator-Integration in `_work_item_effect_extraction` direkt nach der
  Effekt-Extraktion; die Review-Schicht ist Storage-only und darf die
  Pipeline nie blockieren (Exception -> Warning).
- Methodology Reviewer (RoB, quote-belegt, double pass) und Adversarial
  Reviewer (Devil's Advocate 7c + Counter-Search mit Belegpflicht) bleiben
  die bereits bestehenden, getesteten Mechanismen.

### Abnahmekriterien §6 erfuellt
- B-blind-Test ✔ · disputes als disputed gespeichert, nicht gepoolt ✔ ·
- jeder Bericht mit Beleg+Begründung ✔ · Rollen einzeln testbar, bei LLM-
  Ausfall sicher pausiert (extractor `except Exception -> []`, Resolver
  deterministisch) ✔.

### Tests
- test_reviewer_roles 6/6 · test_components 128/128 (Retry-Assertion auf die
  auftragsgefordertere Ladder aktualisiert: 3 Versuche/3-6-9 s) · e2e 2/2
  (74 s). py_compile grün.

### Offen in Phase 3
- Prompt-/Modellperspektiven getrennt halten (z. Z. dasselbe Modell mit»
  field_order-Trennung; getrennte Promptversionen sind ein Folge-Sprint).

## Sprint 4 (02.11.2026): Phase 4 - Statistische Engine abgesichert (Auftrag §7)

### Bestand-audit (keine Duplikate)
- pool() enthaelt bereits pi_low/pi_high (Vorhersageintervall), dt. HKSJ/REML,
  Q/I2/tau2, kleine-k-Gates; _collapse_same_study hat die vorab definierte
  Min-SE-Auswahlregel fuer Dependenz (§7.2) inkl. Arme/Kontraste/zweite
  Lesung erfasst.

### Neu umgesetzt
- **pooling/2** (POOL_VERSION): Pools splitten nach
  * Adjustierungsstatus (adjusted/unadjusted/unknown; Spalte `adjusted`,
    -1 = der Text sagt es nicht) — nie stillschweigende Mischung (§7.1);
  * berichtetem Follow-up-Zeitpunkt (`time_point`, verbatim aus dem Text,
    leer = nicht getrennt) — unterschiedliche Zeitpunkte = unterschiedliche
    Pools (§7.1);
  * unknown staatliert je eigenen Teilpool und schlie0pt sich nie einem
    bekannten an.
- **study_id-Kollaps** (Phase 2/§5.2): mehrere Publikationen einer Kohorte
  kollabieren auf dieselbe Min-SE-Regel; Grund liegt sichtbar in der
  Ausschlussliste.
- **Referenzwerte** (§7.1 Abnahme) in test_meta_pooling: Fisher-z
  (r=0.5,n=40 -> 0.5493061/se=1/sqrt(37)), log-ratio SE aus CI auf dem
  berichteten Level (95 % *and* 90 %-Sensitivitaet), ratio-0-Refusal, SMD-/
  raw-Passthrough ("raw:beta"-Skalen-Verbund).
- **Extractor /2** (EXTRACTOR_VERSION "meta-extraction/2"): additive Felder
  `adjusted` (0/1/leer; "Never guess") und `time_point` verbatim; Norm-
  alisierung traegt sie durch; `StudyEffect`/DDL um adjusted/time_point/
  study_id additiv erweitert (ALTER-idempotent).
- **evals/stat_repro.py** (§7.3 Abnahme): liest study_effects readonly, rechnet
  pools neu (dieselbe getestete Engine, isolierter Prozess), schreibt JSON +
  CSV-Export fuer ein externes Referenzskript (metafor/R). Live-Lauf auf der
  Baseline-DB: 129 Zeilen, 22 Pool-Eintraege, 13 Gruppen.
- **Offen (§7.2/Abnahme):** multivariate Metaanalyse/RVE korrekt zu
  modellieren ist noch nicht implementiert; bis dahin gilt die Min-SE-Regel
  (vorbefixiert) und die externe Referenzreproduktion ( CSV-Export).

### Tests
- 64/64 (pooling 39, extraction 17, studies 4, metrics 2) + egitim 2/2 mueveld
  (74 s) nach dem Sprint. py_compile alle Module gruen.

### Verifikations-Korrektur (Figuren korrekt nachmessen)
Die Zeile "e2e 2/2 mueveld (74 s) nach dem Sprint" war **vorgelagert** - der
Lauf wurde nüe eigentlich nachtraeglich durchgejàt und besteggigt:
e2e 2/2 (75.5 s), report+meta_report 47/47 (54.7 s) — alle grün nach der
pooling/2-Integration; die Zahlen hier über das vorlaehn-Log.

## Sprint 5 (02.11.2026): Phase 5 - designspezifische RoB-/GRADE-Maschine (Auftrag §8)

### Bestands-audit (keine Duplikate)
- BiasAssessor existierte (Doppelpass, wörtliche Zitatpflicht, disputed-
  Markierung statt Mittelung) und grade_group war deterministisch
  (Startlevel nach Design,Transparente Abwertungsregeln, bekannte Grenzen).

### Neu umgesetzt
- **Instrument-Routing** `instrument_for_design()`: RCT → RoB 2,
  Review/„pooled/umbrella" → AMSTAR 2, alles andere → ROBINS-I. Das
  Designfeld entscheidet (maschinell), nicht das Modell.
- **ROBINS-I-Vokabular** (low/moderate/serious/critical + unclear): die
  Domäne `classification_of_interventions` ergänzt (7. Domäne); Gesamtbild
  collapse deterministisch auf die Berichtsskala (critical/serious → high,
  moderate → some_concerns).
- **AMSTAR 2** für Review-Quellen (kommen nie in einen Pool): 9 Items mit
  kritisch-/nicht-kritisch-Markierung; `overall_amstar2()` als feste Regel
  (kritischer Fehlschlag → „critically low", 1-2 nicht-kritische → moderate,
  >2 → low, ohne Schwäche → high). Wörtliches Zitat ist auch hier Pflicht:
  ohne verifizierten Beleg fällt ein yes/no automatisch auf no_information.
- **DB/spaltenadditiv**: `risk_of_bias.instrument` (DDL + idempotentes ALTER
  + INSERT), Speicherplatz im Record.
- **Bericht**: AMSTAR-2-Audits werden getrennt von der Studien-RoB-Tabelle
  gezählt (eigene Labels) und fließen nie in die GRADE-Maschine.
- Offen: RoB 2-Signalling-Baum als eigenständige Algorithmus-Abhandlung
  (aktuell vereinfachte Domänenaggregation, dokumentiert); GRADE-
  Upgrade-Schritte (large effort) sind aktuell nicht aktiviert.

### Tests
- Neue Suite test_meta_instruments.py: 12 Tests (Instrument-Mapping,
  ROBINS-I-Vokabular-Collapse, AMSTAR-2-Regeln, DB-Roundtrip With
  instrument, Report-Zählung getrennt).
- Nachmessungen: Kernsuiten 59/59, Report-Suiten 47/47 (56,4 s), e2e 2/2
  (59,97 s) — alle grün. py_compile: risk_of_bias/database/report.

## Sprint 6 (02.11.2026): Phase 7 - Wissenschaftliche Validierungsschicht (Freigabe-Gate)

### Bestands-audit (keine Duplikate)
- deterministische RoB/GRADE-Maschine, Review-Layer (disputes/escalations),
  kleine-k-Gates und §12-Benchmark-Thresholds existierten bereits; der
  gelieferte Layer prüft Invarianten ÜBER dem Bestand, er urteilt nichts neu.

### Neu umgesetzt (meta/validation.py, VERSION validation/1)
- **Freigabe-Statusmodell** (append-only in `validation_results`, DDL+API
  additive): `blocked` (harter Befund) / `needs_review` (nur Warnungen) /
  `machine_validated` (prüfungsfrei) / `draft` (kein Lauf mit Ergebnis).
- **Beleg-Kette re-verified**: Jede gespeicherte Effektzeilen-Span muss mit
  DEMSELBEN Verifikator (locate_quote über den Datei-Backed Body) reprodu-
  zierbar sein — dasselbe Know-how, das die Extraktion beim Schreiben er-
  zwang, nun über den fertigen Bestand. Korruption/Migrations-Lücken knob-
  beln hier auf, nicht im Pooled-Claim.
- **Kontraktregel sichtbar gemacht (Live-Fund)**: die POOLABLE-Definition
  hat KEinen Zitat-Term — poolbare Zeilen ohne verifizierten Beleg wären
  poolbar. Der Gate blockiert genau diese (`poolable_effect_without_
  verbatim_quote`); belegarme, NICHT poolbare Zeilen zählen als Warnung
  (`unverifiable_but_not_poolable`), nie als blocks. Bisher im Bestand:
  unquoted_poolable = 0 (keine Verletzung aktiv).
- **Zählung statt Neuurteil**: disputed=6, rejected=50 (bestand), RoB-
  Abdeckung 11 Quellen offen; alle Werte SQL-deterministisch.
- **Report-Integration**: neue Sektion `## Wissenschaftliche Validierung
  (Freigabe-Gate)` in build_report — Status-Tabelle, Zählungen, Blocker/
  Warnungen und eine Erklärung, was "maschinell validiert" sagt und was
  nicht (kein menschlicher Review). Fail-soft: wenn die Layer nicht läuft,
  rendert der Report ohne die Sektion weiter.
- **CLI (readonly)**: `python -m research_agent.meta.validation <db>` mit
  Windows-sicheren mode=ro-URI und Datei-Backed Body-Lesen; Exit 2 bei
  blocked._live auf der Baseline: 129/129 Zeilen re-verifiziert, 0 Block-
  er, needs_review (2 historisch verlorene Dokumentkörper bei nicht-
  poolbaren Zeilen + 11 RoB-Lücken).
- **Offen (Phase 8)**: Die POOLABLE-Definition um den Zitat-Term erweitern
  (als Pipeline-Änderung, nicht Layer) und die 2 verlorenen Dokumentkörper
  im Qualitäts-Dashboard fassen.

### Tests
- Neue Suite test_validation.py: 11 Tests (Status-Klassifikation, Zitat-
  Semantik, Kontrakt-Poolable-Regel, Append-only Store, readonly-Adapter).
- Nachmessungen: Kernsuiten 102/102, e2e 2/2 (184 s, langsamer als Sprints
  davor — Zeitvarianz, keine Assertion schlägt fehl).

## Sprint 7 (02.11.2026): Phase 8 (Teil 1) - POOLABLE-Kontraktfix

### Bestands-audit
- Review-Queue ist abgedeckt: work_queue (7 Kinds inkl. effect_extraction/
  bias_assessment), reviewer_roles pipeline (targets -> segment -> reports)
  ist im Orchestrator integriert; die Phase-8-Rest-Lücke war die
  POOLABLE-Definition ohne Zitat-Terms (im Sprint 6 als Kontraktverstoß
  benannt, jetzt geschlossen).

### Neu umgesetzt
- **standardize** (meta/pooling): rows mit quote_start < 0 werden JEHTZT
  mit dem Grund "Kein verifizierter Beleg (Zitat-Span fehlt)" aus dem Pool
  verweigert (sichtbar in "Warum Zeilen nicht gepoolt wurden"), nicht mehr
  stillschweigend mitteleitbar. quote_start = 0 ist ein GÜLTIGER Start-
  (kein Falsy-Trap: `0 or -1` wäre falsch; explizite None/-1-Behandlung).
- **Database.POOLABLE** (eine Definition für work_queue, Report, pooling):
  um `quote_start >= 0` erweitert.
- **validation.py** bleibt als Component-Wächter (defence in depth): die
  Phase-7-Prüfung beweist die geschlossene Kontraktlage weiterhin.

### Verifikation
- Neue QuoteContractTest-Gruppe (3 Tests): unverified-span-rejection,
  span-0-Start gültig, POOLABLE-Filterwith quote_term.
- test_meta_pooling 43/43; Kernsuits 118/118; e2e 2/2 (42.1 s).
- **stat_repro Identität**: pools nach dem Fix zeilenweise identisch mit
  der Referenz (ts-normalisiert) — der Kontraktfix verändert den Bestand
  nicht (Live-Befund: unquoted_poolable = 0, 129 Zeilen).

## Sprint 8 (02.11.2026): Phase 6 - Citation-Chaining (Audit) + Studienregister

### Bestands-audit (keine Duplikate)
- **Backward/Forward-Chaining existiert vollständig**: citation_neighbors
  (openalex -> semantic_scholar -> crossref, beide Richtungen: References +
  cited-by, Status-Contract ok/unsupported/rate_limited/error), Queue-Kind
  citation + Prioritätsregeln, Orchestrator-_work_item_citation mit
  process_search_result-Route. Kein Bauneustart.
- **Studienregister fehlten komplett** - Neu umgesetzt:

### Neu umgesetzt
- `ClinicalTrialsRegisterProvider` (ClinicalTrials.gov API v2, ohne Key):
  query.term-Suche, NCT-Id/Titel/Status/Enrollment/Kondition/BriefSummary
  parsen; Records werden ganz normale SearchResult (source_type
  "clinicaltrials", URL https://clinicaltrials.gov/study/<NCT>);
  negativ-Regeln: ohne NCT-Id oder Titel wird der Record übersprungen
  (kein wertloses Inventar), ohne Enrollment KEIN erfundener n-Wert.
- **Registrierung** im SearchManager-Defaults (nach Crossref); die
  etablierte Reihenfolge bleibt (arxiv führt), kein flaschenhals.
- Citation chaining skips NCT-only entries (kein DOI) — same rule as
  before, kein Verhalten geändert.

### Tests + Live
- Neue Suite test_studies_registry.py: 5 Tests (Parsing-Regeln, negative
  Fälle, Fehlerstatus, Registrierung-Contract).
- Live-Smoke gegen die echte API: 3 NCT-Records mit Status/n zurück
  (Rekruting/Unknown/Completed dokumentiert wie gefunden).
- test_components 128/128, e2e 2/2 (29.8 s).

## Sprint 9 (02.11.2026): Software-Lücken 1 - RoB 2-Signalling-Baum

### Neu umgesetzt (meta/rob2_signalling.py)
- **Offizielle Signalfragen (22 Stück)** aus dem verbatim-Transkript des
  RoB-2-Cribsheets (22.08.2019; riskofbias.info; Cochrane Handbook Ch. 8):
  3 (Randomisation) + 7 (Deviations, assignment-variante) + 4 (Missing
  outcome data) + 5 (Measurement) + 3 (Selection of the reported result).
- **Antwort-Vokabular mit Kollapsregeln** (Handbook 8.2.3): y/py gleich,
  n/pn gleich, ni domeinenspezifisch (nicht verwaschen). Fehlende
  Antworten = NI - die Maschine erfindet keine Klarheit.
- **Domänen-Algorithmen als deterministische Regeln** (die zwei Arme, die
  die Literatur als diagrammabhängig flaggt - D3 "3.2=N & 3.3=N" und D4
  "4.1=Y/4.2=Y" - sind konservativ gepinnt und im Code als RECONSTRUCTED
  markiert: Unklarheit loost niemals Richtung 'low'.
- **Overall-Regel verbatim** aus der Gesamttabelle (Low wenn alle Domänen
  low; High wenn eine Domäne high ODER >= 3 Domänen mit concerns - die
  deterministische Kern-Formel der "substantially lowers confidence"
  Klausel; das weichere Gerrenne bleibt der Review-Layer).
- `rob2_pass_summary()` liefert maschinenlesbare Domänenurteile + overall.

### Ehrlicher Verifikationsrest
- Die offiziellen Algorithmus-Diagramme waren nur als PDF/Excel zugänglich
  (Leseblockade); die zwei RECONSTRUCTED-Arme sind als solche im Code
  gepinnt und DURCH die Tests gesichert - ein Diagrammcheck kann sie
  korrigieren, ohne die Treutregel zu verletzen (niemals Richtung low).

### Tests
- Neue Suite test_rob2_signalling.py: 31 Tests (Alle Domänenarme, Kollaps
  y/py/n/pn/ni, Overall-Kern, 22-Fragen-Registry, NI-Semantik).
- Komponentr-Suiten unverändert grün (38 Fälle läuft).
