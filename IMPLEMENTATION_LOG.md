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
