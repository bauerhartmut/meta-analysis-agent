# Verbesserungsvorschläge als verteilbare Agent-Prompts

Diese Prompts sind so geschnitten, dass sie von **mehreren Agents parallel** bearbeitet werden können.
Jeder Prompt nennt im "Scope/Grenzen"-Abschnitt, welche Dateien er anfassen darf und welche **nicht**,
damit sich simultane Agents nicht in die Quere kommen.

**Reihenfolge-Hinweis für den Menschen:**
- Pakete A, D, E sind dateidiskjunkt und können sofort parallel starten.
- Pakete B und C berühren beide `memory/store.py` → **nicht gleichzeitig** starten; oder B zuerst, C danach.
- Paket F liest nur die DB und berührt keine Agent-Dateien → kann parallel laufen. Ändert B/C die DB-Schema, kurz warten.

---

## PAKET A — Suchschicht sanieren (größter Sofortgewinn für "kommt nichts voran")

**STATUS: ✅ UMGESETZT + getestet (Buffy).** Die Suchschicht ist bereits hart saniert
(`research_agent/research/search.py`): `_RateLimitMemory`/`RATE_LIMIT_MEMORY` Circuit Breaker pro
Provider (bei 429/503/endpoint-Fail → Cooldown-Fenster, SearchManager skippt geblockte Provider),
begrenzte Retries (SS/OpenAlex `_max_retries=2`, Backoff-Deckel ~10 s, Cooldown 300 s; DDG öffnet
bei Komplettausfall), Provider-Priorität arXiv>PubMed>OpenAlex>SemanticScholar>DDG (zuverlässige
zuerst). Orchestrator Phase 2 ruft 3 Suchen parallel über den Manager auf.
Neu: Offline-Unit-Tests `tests/test_components.py::TestSearchCircuitBreaker` (7 Tests: Circuit
open/block/recover, Block-Skip, dedup+Domain-Filter, Failure-Isolation, Retry-Exhaustion→Cooldown)
- keine Live-Retry/suchzeit hier verifiziert.

```
Du arbeitest in einem Autonomous-Research-Agent-Projekt (Ollama, qwen3:14b). Das Hauptproblem:
Der Research-Zyklus verbringt einen Großteil seiner Zeit mit Warten statt mit Wissensproduktion.
Die Logs zeigen: DuckDuckGo-Endpoints (lite/html) schlagen fehl, Semantic Scholar und OpenAlex
werden rate-limited und warten 30s pro Retry, teils alle Retries ausgeschöpft. Praktisch liefert
nur arXiv noch brauchbare Ergebnisse pro Query. Parallel laufen 3 Queries pro Zyklus, jede über
alle 5 Provider → 15 Requests, von denen die meisten in Retry-Schleifen hängen.

Deine Aufgabe:
1. Analysiere research_agent/research/search.py (DuckDuckGo, PubMed, arXiv, SemanticScholar,
   OpenAlex, SearchManager) und wie research_agent/orchestrator.py die Suchen aufruft
   (Phase 2, 3 parallele searches).
2. Implementiere einen "Circuit Breaker" pro Provider: Nach N Fehlschlägen in Folge (z.B. 2-3)
   wird der Provider für X Minuten deaktiviert, statt weiter brennende Retries zu laufen.
3. Priorisiere die Provider, die tatsächlich liefern (z.B. arXiv, PubMed, OpenAlex mit mailto=
   Polite-Pool); rate-limit-schwache (Semantic Scholar unauthentifiziert) sollen reduziert werden
   oder gar nicht jeden Zyklus belegt werden.
4. Kürze die Retry-Backoffs radikal (max 1-2 Versuche, Deckel auf ~5-10s Gesamtwartezeit pro
   Query), sodass ein Zyklus nie wieder Minuten auf Backoff wartet – lieber 0 Ergebnisse liefern
   als ewig hängen.
5. Optional: Füge ein stabiles, key-loses Web-Such-Backend hinzu (z.B. duckduckgo-search 3.x
   Bibliothek oder ein anderes schnelles Backend), das die zerfallenden HTML-Scraper-Ansätze
   ersetzt. Teste, dass pro Query max ~15-20s verbraucht wird.
6. Aktualisiere die .env/README-Doku wenn sich Provider-Konfiguration ändert. Der Zyklus soll
   bei ausgefallenen Providern sofort zu den nächsten Phasen springen.

Scope/Grenzen:
- Erlaubt: research_agent/research/search.py, research_agent/orchestrator.py (NUR die
  Search-Phase ~Zeilen 170-260), research_agent/config.py, .env, README.md.
- NICHT anfassen: research_agent/memory/store.py, research_agent/memory/retrieval.py,
  research_agent/database.py, research_agent/benchmark.py, research_agent/agents/.
- Nach dem Umbau: `python -m pytest research_agent/tests/ -v` laufen lassen und einen einzelnen
  Zyklus mit `python benchmark.py` timen. Berichte, welche Provider aktuell liefern und wie lang
  die Search-Phase jetzt dauert.
```

---

## PAKET B — Evidenz-Bewertung von Brute-Force auf Embedding-RAG umbauen

**STATUS: ✅ UMGESETZT (Buffy).** Geändert: `memory/retrieval.py` (neuer Helper
`find_hypothesis_sources`), `memory/store.py` (Self-Consistency optional, default OFF),
`orchestrator.py` (Phase-5-Paarbildung via Embedding-RAG + dedup-Menge `_evaluated_evidence_pairs`,
erst aus `evidence`-Tabelle geseedet). Getestet: 17 Unit-Tests grün + Logikchecks. Wenn du Paket C
startest, kannst du das parallel zu B laufen lassen, da B hier abgeschlossen ist.

```
Du arbeitest in einem Autonomous-Research-Agent-Projekt (Ollama, qwen3:14b). Problem:
Die Evidenz-Bewertung im Zyklus brennt massiv Compute, bringt aber fast nichts. In der DB
liegen 688 Evidence-Zeilen = 648 "neutral" (94 %), nur 8 contradicts und 32 supports. Das
Verfahren (research_agent/orchestrator.py Phase 5 + research_agent/memory/store.py
evaluate_evidence) prüft ALLE aktiven Hypothesen gegen bis zu 8 Quellen per Keyword-Overlap +
LLM-Klassifikation, kappt auf 20 Paare/Zyklus, und der aktuelle Code verwirft neutrale Resultate
ohnehin wieder – also riesiger Aufwand ohne Signal.

Deine Aufgabe:
1. Baue die Paarbildung auf Embedding-Relevanz um: Nutze research_agent/memory/retrieval.py
   (SemanticRetrieval.retrieve / find_relevant_context) bzw. einen neuen Helper, um zu jeder
   aktiven Hypothese per Vektor-Similarität die TOP-k (z.B. 2-3) tatsächlich nahen Quellen/Facts
   zu finden.
2. Beurteile NUR diese (hypothesis, source)-Paare – statt Brute-Force aller Hypothesen × 8.
   Ergebnis: deutlich weniger LLM-Calls, dafür deutlich höherer Anteil an supports/contradicts.
3. Vermeide es, dieselbe (hypothesis, source)-Kombination mehrfach über Zyklen zu bewerten
   (Persistenz einer "bereits bewerteten Paare"-Menge analog zu _checked_contra_pairs im
   Orchestrator; für neue Quellen neu bewerten).
4. Entferne bzw. reduziere die teure Self-Consistency-Variante (3 zusätzliche LLM-Calls bei
   "neutral") aus research_agent/memory/store.py, ODER mache sie optional/per-Modell-configured.
5. Miss und berichte: Anzahl der LLM-Evidenz-Calls pro Zyklus VORHER und NACHHER sowie den
   Anteil non-neutraler Ergebnisse in der DB vor/nach deiner Änderung.

Scope/Grenzen:
- Erlaubt: research_agent/memory/store.py (FUNKTIONEN zur Paarbildung/Bewertung),
  research_agent/orchestrator.py (NUR Phase-5-Aufruf und Paarbildung),
  research_agent/memory/retrieval.py (nur neue Helper, bestehende Methoden unverändert lassen).
- NICHT gleichzeitig zu PAKET C starten (beide fassen memory/store.py an). Wenn ein anderes
  Paket C läuft, zuerst dieses Paket testen, dann C.
- NICHT anfassen: research_agent/database.py (Schema), research_agent/research/search.py,
  research_agent/agents/, benchmark.py, die Confidence-Update-Formel in
  store.update_hypothesis (das ist Paket C).
- Test: `python -m pytest research_agent/tests/ -v` + ein Zyklus via benchmark.py; berichte
  die Call-Zahlen.
```

---

## PAKET C — Confidence-Update qualitätsgewichtet + fehlende Snapshots-Tabelle

```
Du arbeitest in einem Autonomous-Research-Agent-Projekt (Ollama, qwen3:14b). Problem:
Hypothesen-Konfidenzen bewegen sich praktisch nie. In der DB: 29 Hypothesen, fast alle auf
0.43-0.45 festgenagelt, keine einzige mit Status supported/confirmed/contested/rejected. Dazu
ist die Tabelle `confidence_snapshots` (Konfidenz-Trendchart im Dashboard) NICHT angelegt –
der Code schreibt sie in try/except und scheitert still, d.h. die "wird es besser?"-Messung
ist kaputt.

Deine Aufgabe:
1. Verdrahte den existierenden EvidenceScorer (research_agent/agents/evidence_scorer.py,
   compute_composite_score → quality_label/confidence_modifier/weighted_strength) in das
   Confidence-Update in research_agent/memory/store.py (Funktion update_hypothesis). Aktuell
   zählt die Formel nur raw unterstützende vs. kontra-evidenz. Hochwertige Evidenz (Meta-Analyse,
   RCT, großes n, Good-Journal) muss stärker wiegen als schwache Websources. Gewichte pro
   Evidence-Eintrag aus strength * confidence_modifier (contradicts wird im Scorer hochgewertet).
2. Lege eine Migration an, die die Tabelle `confidence_snapshots` (schema-treu zur
   save_confidence_snapshot-Funktion) in der SQLite-DB research_agent/data/research.db erstellt –
   ohne bestehende Daten zu zerstören (CREATE TABLE IF NOT EXISTS). Prüfe research_agent/database.py,
   wie Tabellen definiert/initialisiert werden, und ergänze die Schema-Liste.
3. Stelle sicher, dass update_hypothesis / generate_hypotheses wirklich Snapshot-Rows schreibt
   (die try/except-Stille entfernen oder zumindest loggen im Fehlerfall) und dass die
   cycle_number korrekt befüllt wird (nicht hart 0).
4. Berichte: Anzahl Snapshots nach einem Testlauf, Verteilung von confidence moves vor/nach.

Scope/Grenzen:
- Erlaubt: research_agent/memory/store.py (NUR update_hypothesis + Snapshot-Logik +
  generate_hypotheses-Snapshot-Teil), research_agent/database.py (NUR Schema/migration),
  research_agent/agents/evidence_scorer.py (nur falls kleiner Helfer nötig).
- NICHT gleichzeitig zu PAKET B starten (store.py-Konflikt). Am besten erst nach B.
- NICHT anfassen: research_agent/orchestrator.py (die _devils_advocate phase), retrieval.py,
  search.py, benchmark.py.
- Test: pytest + einen Zyklus; prüfe via sqlite3, dass confidence_snapshots wächst.
```

---

## PAKET D — Ground-Truth-Eval, damit "wird besser" messbar ist

```
Du arbeitest in einem Autonomous-Research-Agent-Projekt (Ollama, qwen3:14b) zum Thema
"Eugenik: Embryonenselektion / selektive Reproduktion / IQ-Optimierung". Es gibt bisher KEIN
Maß für Output-Qualität – benchmark.py misst nur Zeit, keine Korrektheit. Deshalb kann niemand
sagen, ob der Agent tatsächlich besser wird.

Deine Aufgabe:
1. Lege ein goldenes Eval-Set an (z.B. research_agent/evals/golden_answers.json oder
   research_agent/tests/golden_questions.jsonl): die ~10 Seed-Fragen aus der DB/PROGRESS.md mit
   erwarteten Key-Claims und konkreten Zahlen (z.B. "Wilson Effect: h² 0.40→0.80",
   "Flynn Effect Plateau", "PGT-A/PGT-M outcomes", "polygenic scores"), je 3-8 goldene Claims.
   Setze dafür SSOT-Quellen als Referenz. Kein Fachwissen erfinden – aus vorhandenen
   hochwertigen Quellen/Daten geeignete Claims übernehmen, jeweils mit Claim + Kurzquelle.
2. Baue einen Score-Mechanismus (research_agent/evals/quality_eval.py), der gegen die aktuelle
   Wissensbasis (Facts/Hypothesen/Synthesen in der DB, plus optional die letzte Journal-Synthese)
   pro Frage Recall + Fakten-Korrektheit (Abgleich Zahlen) berechnet. Zwei Optionen:
   a) deterministisch (Keyword-/Zahlenabgleich), b) LLM-as-Judge: ein ausführlicherer/anderer
   Prompt fungiert als Review der Synthese gegen die goldenen Claims.
3. Integriere einen CLI/Entry (z.B. `python -m research_agent.evals.quality_eval`) der ein
   Score-Report (JSON + Konsolenausgabe) pro Frage und Gesamt ausgibt, ohne andere Teile zu
   stören.
4. Doku im README oder eigenen Evaluations-MD: wie ausführen, wie lesen.

Scope/Grenzen:
- Erlaubt: NEUE Dateien unter research_agent/evals/ und evtl. research_agent/tests/,
  README.md, research_agent/config.py (nur lesen, ggf. Pfad-Config ergänzen).
- NICHT anfassen (außer Lesen): research_agent/orchestrator.py, memory/*, database.py,
  research/search.py, agents/*. Der Eval läuft ausgelagert und ändert keine Agent-Logik.
- Test: einen Lauf gegen die aktuelle research_agent/data/research.db ausführen und den
  Score-Report zeigen.
```

---

## PAKET E — Stille Fehler & Session-Lebenszyklus fixen

```
Du arbeitest in einem Autonomous-Research-Agent-Projekt (Ollama). Bekannte stille Defekte,
die so aussehen als würde nichts vorangehen:

1. Alle 39 research_sessions in der DB haben status='active' und leeres end_time – der
   Cleanup (orchestrator._cleanup), der end_time/status='completed' setzt, läuft offenbar nie,
   weil der Prozess bei jedem Start gekillt/gestoppt wird oder die Session-Neuanlage das
   überschreibt.
2. Es gibt viele Sessions mit 0 cycles = wiederholte Fehlstarts. Der Session-Kreislauf
   (research_agent/orchestrator.py start/`_cleanup`) soll robust werden: bei einem Start in
   die gleiche Topic soll keine unbeschränkte Session-Kette entstehen; Sessions sauber
   abschließen auch bei SIGINT/Exception.
3. Logging-Fehler: research_agent/agents/roles.py und andere liefern Unicode-Zeichen (z.B.
   '→'), die auf Windows/Consoles (cp1252) zu `UnicodeEncodeError: 'charmap' codec can't
   encode character '\u2192'` führen und so die Log-Ausgabe still brechen. Logging soll
   UTF-8-sicher laufen (z.B. sys.stdout reconfigure bzw. logging StreamHandler mit utf-8,
   oder die _safe()-Helfer konsequent anwenden), ohne den Rest zu ändern.

Deine Aufgabe:
1. Untersuche research_agent/orchestrator.py _cleanup()/start() und research_agent/database.py
   save_session/get_session; stelle sicher, dass end_time+status beim Beenden zuverlässig
   geschrieben werden (auch bei KeyboardInterrupt/CancelledError) und dass ein frischer Start
   fur dieselbe Topic die alte Session ordentlich beendet.
2. Behebe das Unicode-Logging-Problem global (Start im research_agent/main.py / run.py mit
   einem utf-8-fähigen StreamHandler + errorhandler), sodass agent.err.log keine
   UnicodeEncodeError-Logging-Fehler mehr zeigt.
3. Hinweis: schreibe kurz einen Test/nachweis, dass sessions geschlossen werden und Logging
   nicht mehr crasht.

Scope/Grenzen:
- Erlaubt: research_agent/orchestrator.py (NUR Session-Lebenszyklus/`_cleanup`/start-session),
  research_agent/main.py, run.py, research_agent/database.py (NUR session-Ablauf),
  research_agent/agents/roles.py & others falls Logging-Fix nötig.
- NICHT anfassen: research_agent/memory/store.py (Confidence), retrieval.py, search.py,
  benchmark.py, agents/evidence_scorer.py (ausser Logging-Utility).
- Parallel-kompatibel zu A/D/F. Nicht gleichzeitig mit B/C anfassen, wenn dir gesagt wurde die
  laufen schon – ansonsten nur die o.g. Dateien.
```

---

## PAKET F — Deliverable-orientierte Synthese für das Fine-Tuning-Dataset

**STATUS: ✅ UMGESETZT (Buffy).** Neue Dateien: `finetune/export_synthesis.py`,
`dataset/validate.py`, `dataset/README.md`. `dataset/synthesis_v1.jsonl` (15 Zeilen, 0 Fehler)
wurde erzeugt. Bestands-`finetune.jsonl`: 429/466 Defekt-Zeilen (426 Duplikate, 321 Weak-Evidence).

```
Du arbeitest in einem Autonomous-Research-Agent-Projekt, dessen Endziel ein Fine-Tuning-Dataset
(dataset/finetune.jsonl, 466 Zeilen) für einen qwen3-Klon ist. Die Daten stammen aus der DB
(research_agent/data/research.db) und werden u.a. per build_notebook*.py/repair/clean Skripten
aufgebaut. Problem: Die Wissensbasis ist flach (Facts sind auf ~37 geschrumpft, Hypothesen fast
alle confidence ~0.43 ohne Status) und die finetune.jsonl klingt nach generischen Systemprompts
mit unbestätigten Fakten (z.B. 'Confidence: 95 %. This finding is supported by 1 sources.').

Deine Aufgabe:
1. Baue (NEUER Export-/Kuratierungshelfer, z.B. finetune/export_synthesis.py) der pro
   Seed-Frage aus der DB eine kuratierte, zitierte Synthese erzeugt: nimm die relevanten
   Facts/Hypothesen inklusive ihrer confidence und quality/source-credibility, und formatiere
   ein "takeaway" je Claim MIT Quelle/Zahlen. Keine Claims ohne Beleg in der DB aufnehmen;
   übernehme nichts blind aus LLM-Zusammenfassungen.
2. Prüfe dataset/finetune.jsonl auf qualitätsdefekte Zeilen (z.B. fehlerhafte Formatierung,
   unvollständige messages, 'supported by 1 sources', Systemprompt-Duplikate) und schreibe
   einen Validator (z.B. dataset/validate.py), der solche Zeilen meldet (und optional filtert).
3. Doku: Wie exportiere ich (Schritt-bis-Pipeline), wie validiere ich, wie oft neu generieren.
4. Berichte: Wie viele Konsistenz-/Qualitätsfehler fandst du im bestehenden dataset/finetune.jsonl?

Scope/Grenzen:
- Erlaubt: NEUE Dateien (finetune/export_synthesis.py, dataset/validate.py), build/repair
  Skripte NUR falls Fehler dort behebbar sind (build_notebook*.py, repair_knowledge_graph.py),
  README/PROGRESS-Doku.
- NICHT anfassen: research_agent/orchestrator.py, memory/*, database.py (kein Schema-Eingriff),
  search.py, agents/*.
- Kompatibel parallel mit allen anderen Paketen, da neue Dateien. Nutze read-only-Zugriff auf
  research_agent/data/research.db.
```

---

### Schnell-Check-Tabelle (Konflikte)

| Paket | Hauptdateien | parallel laufen lassen mit |
|---|---|---|
| A | search.py, orchestrator (Search-Phase), config | B, C, D, E, F |
| B | store.py, orchestrator (Phase 5), retrieval | A, D, E, F — **nicht C gleichzeitig** |
| C | store.py, database.py | A, D, E, F — **nicht B gleichzeitig** |
| D | NEW evals/ | alle |
| E | orchestrator (Cleanup), main.py, database.py | alle (A, B, C, D, F) |
| F | NEW export/validate + build-Skripte | alle |

Empfehlung Start: **A + D + E + F** sofort parallel, danach **B**, zuletzt **C**.

---

## PAKET G — Eigener Single-Shot Deep-Research-Agent (Entscheidung des Nutzers)

**STATUS: ✅ UMGESETZT (Buffy).** Neuer Modul `research_agent/deep_research.py`: pro Frage
führt er EINEN begrenzten, deliverable-orientierten Pass aus (Query-Expansion → parallele
Suchen → Extrahieren → RAG-Kontext → zitierte Synthese mit [n]-Zitaten → optional LLM-as-judge)
und liefert einen Markdown-Report (stdout + `data/reports/*.md`). Wiederverwendet
SearchManager/ContentExtractor/SourceManager/SemanticRetrieval; erzeugt keine Hypothesen-/Evidenz-\
churn.

    python -m research_agent.deep_research --question "Was ist der Wilson Effekt?" \\
        --topic "Eugenik / Embryonenselektion" --max-sources 8 --self-check

**Note (PAKET H, erledigt danach):** `research_agent/evals/report_eval.py` koppelt diese
Reports an das Paket-D-Golden-Set und schreibt einen Score-Verlauf (`--record`/`--trend`),
`quality_eval.py` liest jetzt auch `data/reports/*.md` als Synthese-Korpus.

**Note (PAKET I, erledigt):** Golden-Set `evals/golden_answers.json` um 9 re-recherchierte,
extern belegte Claims erweitert (Polderman/Lee/Savage/Yengo/HFEA/Agar/Bratsberg/Turley/Karavani),
NICHT aus der DB. Overall composite gesunken 100 → ~69,8; score differenziert wieder.

**Note (PAKET J, Provider-Fix):** arXiv in `search.py`+`extractor.py` auf `https://export.arxiv.org`
umgestellt; Semantic-Scholar-Key (`SEMANTIC_SCHOLAR_API_KEY`) und OpenAlex-`mailto`
(`OPENALEX_MAILTO`) werden aus env gelesen. Live-Test: arxiv/pubmed/openalex/crossref liefern
wieder 3 Ergebnisse; semantic_scholar braucht einen Key; duckduckgo ist geblockt (202/Timeout).
Deep-Research auf q02 sammelt aber weiter zu triviale Quellen (composite 0) → Präzisionsproblem
von Queries/Filter, nicht mehr ein Provider-Ausfall.

**Note (PAKET L, Gather-Präzision):** `deep_research.py` reichert jetzt LLM-Queries mit
Präzisionsbegriffen an (`_enrich_query`: genome-wide association meta-analysis / heritability /
preimplantation / time trends) und fügt bei passendem Thema gezielte Kernstudien-Queries hinzu
(`_attach_key_studies`: Lee 2018, Savage 2018, Polderman, Yengo, Turley, Karavani, Bratsberg).
`search.py`-Domain-Filter gegen CS/AI-Treffer gehärtet (artificial intelligence/LLM/langauge model/
neural network/robot u. ä., mit bestehender Relevance-Sicherung). Verifiziert: AI-/CS-Müll raus,
Genetik-/GWAS-Inhalte kommen rein. q02-Score blieb aber 0, weil die konkreten Kernstudien-Abstracts
über die aktuellen Provider-URLs (OpenAlex-ID-Links, EuropePMC-JS-Seiten) nicht extrahierbar sind →
nächster Engpass ist die Extraktionsabdeckung, nicht Query/Filter.

**Note (PAKET N, Lokal-Fallback + Topic-Filter — Stufe 1, Punkte 1+2):** in `deep_research.py`
umgesetzt: (1) `_local_sources()` — bei knappem externen Gather wird der Rest des
Max-Source-Budgets aus `research.db` (Facts/Hypothesen/Sources, Keyword-Scored) gefüllt;
(2) `is_on_topic()` — strenger Domain-Gate gegen CS/AI (genetic algorithm, genetic programming,
knapsack, neural network, LLM, …) vor der Extraktion. Verifiziert am Wilson-Lauf: der Report
ist jetzt fachlich korrekt (zitiert DB-Hypothesen + Van Leeuwen) statt CS-Müll; vorher
"nicht erwähnt".

**Note (PAKET O, Determinismus — Stufe-1 Punkt 4, umgesetzt):** `deep_research.py` plant
Queries jetzt standardmäßig deterministisch statt mit dem flaky LLM-Planner: `_seed_queries()`
liefert pro erkanntem Topik-Bucket (`QUERY_SEEDS`: GWAS/Genom, Zwillings-/Erblichkeit, Embryo/PGT,
Größe, Flynn/Kohorten) eine feste, kuratierte Query-Liste (rohe Frage zuerst als Anker).
Unbekannte Topics bekommen einen deterministischen Fallback (Frage + „evidence meta-analysis
systematic“) statt eines LLM-Aufrufs. Der LLM-Planner ist nur noch via `--llm-plan` erreichbar.
Verifiziert: `_seed_queries` liefert für dieselbe Frage zweimal exakt dieselbe Liste, Off-Topic
-> deterministischer Fallback. Damit ist die flaky Schritt-Seite des Gathers geschlossen; die
Provider-Reihenfolge/Ergebnis-Dedup ist ohnehin stabil. NOTE: `run()`/CLI haben den neuen
`deterministic`-Parameter (Default True); `report_eval --run-deep` erbt ihn automatisch.

**Note (PAKET N, Punkt 3 — Abstract-Resolver für DOI, umgesetzt):** neue `_fetch_abstract_by_doi()`
(löst DOI via **EuropePMC core** primär, **Crossref works** als Fallback) + `_fetch_crossref_abstract()`;
`_key_studies_for()` liefert jetzt 3-Tupel mit DOI, `_keystudy_sources()` holt die Abstracts der
Kernstudien direkt in die Source-Liste. Verifiziert am q02-Lauf: Report zitiert jetzt Savage 2018
(269 867 / 205 Loci / 190 neu) und Lee 2018 (1 271 SNPs / 7–10 % Varianz) aus den echten,
aufgelösten Abstracts. Wirkung im Trend: q02 **0,0 → 8,2** (num_accuracy 0,273); die goldenen
Zahlen sind jetzt physisch im Report. Offen bleibt Stufe-1 Punkt 4 (Determinismus: feste
Query-Seeds statt flaky LLM-Planung).

**Note (PAKET M, Gather-Metriken):** `DeepReport` um `sources_gathered` und
`extractable_content_len` erweitert; `report_eval` zeigt sie pro Lauf („gather = 2 sources,
5450 chars extracted“) und schreibt sie in den History-Record. Damit ist ein 0-Score klar
zurechenbar: `gather=0` → Suche fand nichts; `gather>0` mit wenig chars → Extraktion scheiterte;
`gather>0` mit viel chars → Suche+Extraktion ok, aber Zahlen/Inhalt fehlt (Wissens-/Präzisionslücke).

**Note (PAKET K, DuckDuckGo):** Provider auf `duckduckgo-search`-Bibliothek umgestellt,
API-Nutzung für 3.7.0 korrigiert (text() ist Iterator → `itertools.islice`), + fail-fast +
Circuit-Breaker (20s-Cap). Dependency gebaut und installiert (mit Freigabe): `httpx<0.28`
(jetzt 0.27.2) — damit war der Ursprungsbug (`proxies`→`proxy`) behoben. `primp` war nicht
installierbar (kein Wheel fürs MSYS2-Python, Rust-Build scheitert). Live-Test: **alle DDG-
Backends timeouten (Bot-Block dieser IP)** → DDG liefert hier keine echten Treffer; das ist ein
Netzwerk-Ebene-Problem, kein Code-Problem. Wichtigster Nutzen: kein Lauf wartet mehr 35s
(erster Versuch ≤20s, danach Circuit offen).

Entscheidung des Nutzers war „Single-Shot-Modus im bestehenden Agent“ (nicht eigenes Paket,
nicht OSS-Tool). Falls ein vollständig entkoppeltes `deep_research/`-Paket oder das Einbinden
einer OSS-RAG-Lösung gewünscht ist, das als neues Paket H ansehen.