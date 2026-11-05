# Autonomous Research Agent

An autonomous research agent that conducts long-term, self-directed research on any topic, with its chat phases running on the HRZ TUDaGPT API (no local model). It searches the internet, reads scientific sources, builds hypotheses, critiques its own conclusions, and continuously deepens its understanding.

## Quick Start

### Prerequisites

1. **TUDaGPT API key** from the HRZ (see [TUDaGPT](#tudagpt-hochschulrechenzentrum-tu-darmstadt)); reachable from the campus network/VPN
2. **Python 3.10+**
3. No local model is required: chat and retrieval both run on the HRZ API
   (retrieval through a small ranking model). Embeddings via Ollama are opt-in
   (`EMBEDDINGS_ENABLED=1`, then `ollama pull nomic-embed-text`).

### Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install aiohttp beautifulsoup4 pytest

# Run the agent
python run.py --topic "Quantum Consciousness"
```

### Run with Dashboard

```bash
# Start dashboard only (then use web UI to start research)
python run.py

# Dashboard opens at http://localhost:8080
```

### Headless Mode

```bash
python run.py --no-dashboard --topic "The Origin of Consciousness"
```

### Keep It Running (Supervisor)

`run.py` runs in the foreground: when the process dies, the research stops. `supervisor.py`
keeps it alive.

```bash
# Dashboard + research, restarted automatically if the agent dies or hangs
python supervisor.py -- --topic "Polygenic embryo selection and intelligence"

# Dashboard only, then start research from the web UI
python supervisor.py --
```

What it does:

- restarts the agent when it exits with an error (exit code 0 means "finished" and is not restarted),
- restarts it when `http://127.0.0.1:8080/api/health` stays silent for `--stall-timeout`
  seconds - the dashboard answers from its own thread during long cycles, so silence
  means the process is wedged, not busy,
- waits 10s, 20s, 40s ... up to 5 minutes between restarts and gives up after
  `--max-restarts-per-hour` (default 6), so a broken setup cannot hammer the API for hours,
- refuses to start a second time (`data/supervisor.pid`) and logs to `data/supervisor.log`
  (`data/supervisor_child.out.log` / `.err.log` hold the agent's own output).

Useful flags: `--max-runtime 28800` (stop after 8 hours), `--port`, `--model`,
`--restart-on-clean-exit`. Full list: `python supervisor.py --help`.

On Windows use `scripts\start_supervised.bat "topic"` for a launcher, and
`scripts\install_supervisor_task.bat` to have the supervisor start automatically at
logon (runs as the current user, no admin rights required; remove it again with
`schtasks /Delete /TN "AIResearch Supervisor" /F`).

### Eine Datenbank pro Thema

Ein neues Thema erbte bisher den gesamten Altbestand: 311 Quellen, 266 Fakten,
261 Hypothesen und einen Knowledge Graph aus 391 Knoten des *vorigen* Themas.
Aus dem gesamten Korpus lassen sich schlecht Schlüsse über eine neue Frage
ziehen, und der Graph zeigte über 99 % fremdes Material. Deshalb gilt
`DATABASE_PER_TOPIC=1` (Standard): ein Lauf mit `--topic` schreibt in

```
data/research-<slug>-<hash6>.db      # z. B. data/research-kognition-und-gesundheit-1a2b3c.db
```

Der Slug kommt aus dem Thema (Umlaute transliteriert, Sonderzeichen zu `-`,
auf 40 Zeichen gekürzt), der Hash aus dem vollen Text - damit kollidieren
`IQ Genetics` und `IQ Genetics (PGT-A)` nicht in einer Datei. Betroffen sind
Korpus, Programm, Fakten, Hypothesen, Evidenz, Journal, Experimente und der
Knowledge Graph: alles, was an `self.db` hängt, wird beim Binden mitgezogen.

Drei Dinge, die dazugehören:

* **Token-Abrechnung bleibt global.** `llm_usage` liegt in
  `data/research-usage.db`; „wie viel hat heute gekostet?“ ist eine Frage nach
  Zeit, nicht nach Thema, und darf nicht in eine Antwort pro Thema zerfallen.
  Das Dashboard liest dafür dieselbe Datei.
* **Ein Prozess, ein Thema.** Startet das Dashboard einen Lauf, wird die
  Datenbank vor dem ersten Zyklus gebunden (`use_topic_database`). Ist der
  Prozess schon Zyklen gelaufen, wird der Wechsel abgelehnt und gewarnt, statt
  das laufende Korpus still zu verlassen - ein anderes Thema heißt: Prozess neu
  starten.
* **Der Basisbestand bleibt.** `DATABASE_URL=data/research.db` wird weiterhin
  benutzt, wenn ohne Thema gestartet wird (nur Dashboard), und der read-only
  Standalone-Server zeigt den zuletzt geschriebenen Thema-Bestand.

`DATABASE_PER_TOPIC=0` schaltet die Trennung ab: dann teilen alle Themen
`DATABASE_URL` - und der Graph mischt wieder alles.

## Architecture

```
+------------------------------------------+
|           Dashboard (Web UI)             |
|       Python http.server + HTML/JS       |
+------------------------------------------+
|          Agent Orchestrator              |
|  Research Loop . State Machine . Router  |
+--------+--------+--------+------+-------+
|Research|Analyst |Critic  |Planner|Synth. |
|  Agent | Agent  | Agent  | Agent | Agent |
+--------+--------+--------+------+-------+
|         Memory & Retrieval Layer         |
| Semantic Search . Knowledge Graph       |
+------------------------------------------+
|        LLM Engine (TUDaGPT / HRZ)        |
|    Chat . Embeddings . Structured Output |
+------------------------------------------+
|           Web Research Layer             |
|  DuckDuckGo . arXiv . PubMed . Web Fetch|
+------------------------------------------+
|            SQLite Database               |
| Sources . Hypotheses . Evidence . Journal|
+------------------------------------------+
```

## Configuration

All settings are in `.env`:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:14b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

> **LLM throughput notes:** qwen3:14b (Q4_K_M, ~9.6GB) on a 12GB GPU is
> memory-bandwidth-bound at roughly 10–15 tokens/s, which dominates the
> analysis/evidence phases. The agent already fires LLM calls concurrently, and
> Ollama pipelines them; raising `OLLAMA_NUM_PARALLEL` beyond 1 does **not** add
> throughput (the GPU is saturated) and can increase per-call latency. If the
> phases are too slow, the effective levers are a faster model
> (`OLLAMA_MODEL=qwen3:8b` is ~2× faster) or a shorter context.
>
> **Operational warning:** never leave multiple Ollama servers/runners running.
> Every `ollama serve` spawns a `llama-server.exe` that holds VRAM until its
> parent dies; accumulated zombie runners exhaust the 12GB GPU, the model gets
> CPU-offloaded, and LLM calls slow down 4–5×. After a restart, verify
> `ollama ps` shows the model fully in VRAM (`size_vram` ≈ model size) and
> that only one `llama-server.exe` exists.

SEARCH_PROVIDER=duckduckgo
DATABASE_URL=data/research.db
DATABASE_PER_TOPIC=1            # eine Datenbank pro Thema (siehe unten)

MAX_RESEARCH_CYCLES=0           # 0 = unlimited
MAX_SOURCES_PER_CYCLE=10
RESEARCH_INTERVAL=30            # seconds between cycles
SOURCE_RELEVANCE_THRESHOLD=0.25 # topic-relevance score (0-1) a source needs to be analyzed again / yield facts

DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8080

# Optional: Semantic Scholar personal API key (free; removes shared-pool 429s)
# SEMANTIC_SCHOLAR_API_KEY=
```

### Search Providers

Providers run in priority order (most reliable first):

1. **arXiv** — Atom API, no key, stable
2. **PubMed** — NCBI E-utilities, no key, stable
3. **Europe PMC** — EBI REST API, no key, generous limits (biomedical focus)
4. **Crossref** — polite pool via `mailto=`, generous
5. **OpenAlex** — polite pool via `mailto=`, generous
6. **Semantic Scholar** — unauthenticated shared pool hits 429 often; set `SEMANTIC_SCHOLAR_API_KEY` in `.env` (free) for a personal quota
7. **DuckDuckGo** — HTML scraping, fragile (202 bot challenges)

Rate-limited providers are handled by a **circuit breaker**: after retries exhaust, the provider is skipped for 5–10 minutes instead of stalling the cycle with retry loops. Search phase never waits more than ~10s per provider per query.

### Research Engine (federated search)

The search phase is a small engine of its own ([research/engine.py](research_agent/research/engine.py)) instead of one keyword string sent to all providers:

1. **Plan** - one LLM call turns the cycle's question into 3 queries with 2–3 concept phrases each (`"polygenic score"`, `"embryo selection"`), plus a broad sweep query over topic keywords so precision does not cost recall. Planner failure falls back to the existing query pool.
2. **Translate** - each provider gets the query in its own syntax: `"phrase"[tiab] AND ...` for PubMed, `all:"phrase"` for arXiv, `"phrase" AND "phrase"` for OpenAlex/Europe PMC, plain phrases for Crossref/Semantic Scholar/DuckDuckGo. Queries are sent with `raw=True`, so `extract_keywords` no longer mangles the field syntax.
3. **Merge** - duplicates are merged by DOI, then by normalized title: the same paper from PubMed, Europe PMC and Crossref is one candidate with three providers, not three sources.
4. **Rank** - deterministic score `0.45·relevance + 0.20·recency + 0.20·impact + 0.15·provider consensus` (relevance = share of concept phrases in title/abstract, impact = log citations). The cycle analyses the best candidates, not whichever provider answered first.
5. **Remember** - every (query, provider) attempt, its hit count and how many hits survived the relevance gate is stored in `query_stats`. Queries tried twice without a single kept candidate are dropped from later pools - including after a restart, which the in-memory stats could not do.

Requests to one provider are serialized (its own rate spacing works, providers still run in parallel to each other). Settings: `RESEARCH_ENGINE_ENABLED` (1/0), `QUERIES_PER_CYCLE` (3, plus the sweep), `SEARCH_RESULTS_PER_QUERY` (10 per provider and query; the cycle still analyses at most `MAX_SOURCES_PER_CYCLE`).

Measured with [scripts/measure_search_quality.py](scripts/measure_search_quality.py) on the topic *IQ Genetics* (same question, same providers, read-only):

| | legacy keyword search | research engine |
|---|---|---|
| raw hits | 45 | 86 |
| cross-provider copies merged | 4 (URL dedupe missed them) | 29 |
| unique works | 41 | 57 |
| passing the topic gate | 38 | 55 |

OpenAlex (429: daily budget for this IP) and Semantic Scholar (429: shared pool, no key) returned nothing during the measurement, so these numbers are Crossref + Europe PMC + PubMed + arXiv only. With a free `SEMANTIC_SCHOLAR_API_KEY` and a fresh OpenAlex budget the pool grows further.

### Swap Models

```env
OLLAMA_MODEL=qwen3:8b          # Faster, less capable
OLLAMA_MODEL=qwen3:14b         # Balanced
OLLAMA_MODEL=gemma3:4b         # Lightweight
```

### TUDaGPT (Hochschulrechenzentrum TU Darmstadt)

Chat phases run against the TUDaGPT API of the HRZ; this is the default backend,
and nothing falls back to a local model:

```env
LLM_BACKEND=tudagpt
TUDAGPT_API_BASE=https://tudagpt2.hrz.tu-darmstadt.de/api
TUDAGPT_MODEL=gwdg/qwen3.5-397b-a17b
TUDAGPT_API_KEY=<your key from the HRZ>
```

The endpoint is OpenAI-compatible (`POST {TUDAGPT_API_BASE}/chat/completions`
with a Bearer token) and normally only reachable from the campus network/VPN.
It offers **chat completions only** - there is no embeddings route. Retrieval
works anyway, without any local model: the query filters the stored texts by
keyword, then a small chat model on the same API ranks the candidates
(`RETRIEVAL_MODEL`, default `gwdg/meta-llama-3.1-8b-instruct`,
`RETRIEVAL_CANDIDATES` = 25). That costs one cheap call per query (measured:
~2 s over 300 stored sources) and degrades to plain keyword order if the call
fails, so a backend hiccup returns a worse ranking instead of nothing.

Vector search is opt-in: `EMBEDDINGS_ENABLED=1` uses a local Ollama embedding
model (`OLLAMA_HOST`, `OLLAMA_EMBEDDING_MODEL`) and skips the ranking call.
`LLM_BACKEND` can be set to `ollama`/`kaggle_api` explicitly, but that is a
choice, not a fallback - with `tudagpt` no local model is started.

The key is read from `.env` or the process environment and is never sent to the
browser or written to logs. `--model "<name>"` overrides the model of whichever
backend is active.

## Research Loop

Each cycle follows a structured process:

1. **Planning** - Work the sub-question of the research program with the largest
   marginal gain (see below); without a program: pick from the question pool
2. **Searching** - Query DuckDuckGo, arXiv, and PubMed
3. **Extracting** - Fetch and parse web pages
4. **Analyzing** - LLM analyzes sources for relevance and claims; relevance is
   scored against the research topic (the current sub-question is context only),
   the score is stored on the source, and sources below
   `SOURCE_RELEVANCE_THRESHOLD` are skipped before analysis (next cycle) and
   before fact extraction (now)
5. **Hypothesizing** - Generate/update hypotheses from evidence
6. **Critiquing** - Red-team analysis of conclusions
7. **Contradiction Detection** - Find conflicting sources
8. **Synthesizing** - Combine findings into coherent conclusions
9. **Journaling** - Document the cycle
10. **Strategy Review** - Adapt approach every 10 cycles

### Forschungsprogramm (Teilfragen statt Fragenschleife)

Ein flacher Fragenvorrat erzeugt über Stunden viele Varianten derselben Frage und
keine Antwort: jede Zyklus-Frage kommt aus einem Pool, nichts wird je
abgeschlossen. Deshalb steht am Anfang eines Laufs ein **Programm**
(`research_agent/program.py`): das Thema wird **einmal** in 4–6 Teilfragen zerlegt
(`PROGRAM_ITEMS`), jede mit Begründung, Art (`empirical`, `mechanism`,
`measurement`, `theory`, `ethics`, `context`), Wichtigkeit, Offenheit - und mit den
**konkurrierenden Positionen** der Literatur samt der Beobachtung, die sie
trennen würde.

**Aufwand nach Grenznutzen.** Jede Teilfrage hat einen Wert:

```
Wichtigkeit × Offenheit / (1 + 0,10·Fakten + 0,05·Quellen) / (1 + 0,35·Zyklen)
```

mal 1,15, wenn konkurrierende Positionen im Spiel sind - eine Entscheidung
zwischen zwei lebenden Erklärungen ist mehr wert als ein weiteres bestätigendes
Paper. Gearbeitet wird immer die Teilfrage mit dem höchsten Wert, aber **nicht
jeden Zyklus neu gewählt**: die laufende Teilfrage bleibt aktiv, solange sie 70 %
des Werts der besten anderen erreicht. Ohne diese Bindung sieht die Regel nach
optimaler Allokation aus und verhält sich wie Round-Robin - jede Teilfrage
bekommt einen Zyklus, keine wird entschieden.

**Abschlussregeln** (pro Teilfrage, aus gespeicherten Zahlen, kein Modell):

| Regel | Bedingung |
|---|---|
| Mindestlaufzeit | vor `PROGRAM_MIN_CYCLES` (Standard 2) wird nichts geschlossen |
| Zyklenbudget | `PROGRAM_ITEM_BUDGET_CYCLES` (Standard 8) Zyklen verbraucht |
| Sättigung | `PROGRAM_SATURATION_CYCLES` (Standard 3) Zyklen in Folge ohne neue Quelle, keinen neuen Fakt und keine neue Evidenzzeile |

Ob eine Teilfrage **beantwortet** ist, entscheidet keine Regel, sondern das
**Verdikt**: eine LLM-Bewertung, die gegen das gesammelte Material läuft - die
gespeicherten Fakten mit ihren Zitatstellen, Abschnitt und Seite, plus die
Hypothesen mit ihrer Evidenzlage. Es nennt die gestützte Position mit Konfidenz,
die Begründung, Gegenbelege im Material, den Test, der es entscheiden würde, was
offen bleibt - und ob die Frage damit beantwortet ist. Ein Verdikt entsteht
während des Laufs (alle drei Zyklen ab drei Fakten) und spätestens beim
Abschluss; ein beantwortetes Verdikt schließt die Teilfrage vorzeitig. Das
Material wird nur aus Fakten gebaut, deren Text die Teilfrage berührt
(`select_facts_for`), damit die Bewertung gegen Belege läuft und nicht gegen die
Vorannahmen des Modells. Die IDs dieser Fakten werden mit dem Verdikt gespeichert
(`verdict.material_fact_ids`), damit der Bericht die Kette nachweisen kann: unter
jedem Verdikt stehen die Belege des Materials mit Zitat, Abschnitt und Seite.
Verdikte aus der Zeit davor sagen stattdessen, dass ihre Belege fehlen.

Sichtbar ist das an vier Stellen: `/api/status` liefert unter `program` die
Zählung, die aktive Teilfrage und alle Einträge mit Wert, Zyklen, Zuwächsen,
Abschlussgrund und Verdikt; das Dashboard zeigt das Panel
**Forschungsprogramm** mit der laufenden Teilfrage; der Abschlussbericht hat einen
Abschnitt `## Forschungsprogramm` mit Tabelle, Verdikten und den nächsten
Teilfragen nach Grenznutzen; und jede Zykluszeile im Log nennt die Teilfrage, die
sie bedient hat.

Einstellungen: `PROGRAM_ENABLED` (Standard 1), `PROGRAM_ITEMS` (6),
`PROGRAM_ITEM_BUDGET_CYCLES` (8), `PROGRAM_SATURATION_CYCLES` (3),
`PROGRAM_MIN_CYCLES` (2).

Ein Hinweis, der dazugehört: der Planer-Prompt war bis hierher eine
Befürworter-Anweisung ("baue den stärksten Fall", "überwältige den Widerstand"),
mit einer festen Themenliste. Ein Programm, das aus einer solchen Anweisung
entsteht, plant Bestätigung - die Zerlegung, die Prioritäten und der Vergleich
konkurrierender Positionen sind jetzt neutral formuliert. Grenze der Zerlegung:
Wichtigkeit und Offenheit sind Schätzungen des Modells, keine Messungen; belastbar
sind die Teile, an denen das Verdikt gemessen wird - Art der Frage, Positionen,
Belege mit Zitatstelle.

### When Searching Stops Paying Off

Cycles can run perfectly while finding nothing: the same six topic queries rotate,
the providers are rate-limited, and every cycle ends with "no new sources" and a
re-analysis of the known ones. After `SEARCH_STALL_CYCLES` (default 3) cycles in a
row without a single new source, the query strategy escalates:

1. **level 0** - topic-adapted queries (the normal rotation),
2. **level 1** - method-anchored queries built from the topic keywords
   (`... meta-analysis`, `... longitudinal cohort study`, `... replication study`),
3. **level 2** - queries derived from the claims the agent is actually chasing
   (keywords of active hypotheses), not from the topic phrase.

Queries are built from two anchors - the topic plus the concept the agent is
currently working on - and words that carry no topic signal ("correlation",
"study", "results") are dropped, because "intelligence genetic correlation
longitudinal cohort study" returns papers about acne severity. A query used within
the last `2 * SEARCH_STALL_CYCLES` cycles is skipped while there are alternatives,
and a query that returned nothing twice is dropped from the pool.

What counts as success is a **new source the relevance gate accepts**, not a new
database row. Otherwise a fallback round full of off-topic hits would look like
progress and switch the strategy straight back off. `/api/status` reports both:
`search_strategy` (level, stall counter, queries) and `relevance_yield` (new
sources scored vs. above `SOURCE_RELEVANCE_THRESHOLD`, split by strategy level),
and every cycle logs a `Relevance yield: n/m` line.

### LLM Watchdog

A dead or rate-limited LLM backend used to keep the loop running: every call
returned `[ERROR: ...]`, the phases swallowed it, and the cycle ended "complete"
with nothing in it. The engine now counts consecutive failed calls (`chat()`
wrapper), and every phase checks that counter before it starts the next step.
Once `LLM_FAILURE_THRESHOLD` (default 5) is reached, the run sets the phase to
`waiting_for_llm`, marks `llm_unavailable` in `/api/status`, and polls the backend
every `LLM_RECOVERY_INTERVAL` seconds (default 60) instead of writing empty
cycles. When the backend answers again the counter is reset and the same cycle
continues; hitting Ctrl+C or Stop while paused aborts the run immediately.
Only backend errors count - a successful call that merely returns unparseable
JSON does not trip the watchdog.

### Work Queue (lange Läufe)

Suche ist keine Arbeit: sobald die Literatur eines Themas abgegrast ist, liefert
jeder Zyklus nur noch Quellen, die schon in der Datenbank liegen - 350 Zyklen
brachten in diesem Projekt ~0,8 neue Quellen pro Zyklus, und 107 Hypothesen
hatten nie eine Evidenzzeile gesehen. Statt weiter zu suchen, arbeitet der Zyklus
deshalb einen **persistenten Rückstand** ab (`research_agent/work_queue.py`,
Tabelle `work_items`):

| Art | Arbeit | Quelle des Rückstands |
|---|---|---|
| `full_text` | Volltext/Abstract erneut holen, Quelle wird bewertbar | Quellen mit < 400 Zeichen Text |
| `hypothesis_evidence` | die drei ähnlichsten Quellen gegen eine ungeprüfte Hypothese bewerten; auch "keine richtungsweisende Evidenz" wird als Befund festgehalten | aktive Hypothesen ohne Evidenz |
| `open_question` | offene Frage wird zur Frage des Zyklus und nach der Synthese geschlossen | `research_questions` mit Status `open` |
| `citation` | Referenzen und Zitierungen einer relevanten Arbeit folgen (OpenAlex) | Quellen mit DOI über der Relevanzschwelle |
| `simulation` | eigene Prüfung: Hypothese → Protokoll → Python-Experiment → Verdikt | testbare Hypothesen ohne Evidenz, unklare nachtesten |
| `effect_extraction` | Effektgröße aus einem Paper lesen (Zahl, Präzision, wörtlicher Belegsatz); zwei Pässe, abweichende Lesungen werden *strittig* statt gemittelt | Quellen mit echtem Dokumenttext über der Relevanzschwelle, die noch keine `study_effects`-Zeile haben |

Priorität ist `Wert × Unsicherheit / Kosten`: eine Hypothese bei Konfidenz 0,5
ist die interessantere als eine bei 0,95, und die Evidenzprüfung steht vor dem
Nachladen fehlenden Volltexts. Nach `MAX_ATTEMPTS` (2) Fehlschlägen wird ein
Punkt blockiert statt endlos wiederholt; beim Start eines Laufs gehen
abgebrochene Ansprüche zurück in die Warteschlange. Ist der Blocker vorübergehend
und extern (OpenAlex-Budget erschöpft, Embedding-Backend weg), wird der Punkt
zurückgelegt, ohne einen Versuch zu verbrauchen - sonst würde ein
Provider-Ausfall den ganzen Rückstand blockieren. Quellen, die beim
Zitations-Schneeball entstehen, laufen noch im selben Zyklus durch die Analyse,
sonst blieben sie unbewertet liegen.

Damit die Warteschlange tatsächlich abnimmt, gibt es eine Hypothesen-Bremse:
Sobald `HYPOTHESIS_BACKLOG_LIMIT` (Standard 25) aktive Hypothesen ohne eine
einzige Evidenzzeile dastehen, überspringt ein Zyklus die Hypothesenphase und
steckt seine Zeit in die bestehenden Punkte. Ein neuer Gedanke kostet einen
Aufruf, seine Prüfung mehrere Zyklen - ungebremst wächst der Rückstand schneller
als `WORK_ITEMS_PER_CYCLE` ihn abarbeitet. Neu erzeugte Hypothesen landen sofort
in der Warteschlange, damit die Evidenzarbeit sie ohne Neustart erreicht.

Sichtbar ist der Stand an zwei Stellen: `/api/status` liefert unter
`work_queue.hypothesis_brake` die offenen Evidenz-Punkte, die Schwelle und ob die
Bremse greift (dazu die Entscheidung des letzten Zyklus unter
`hypotheses_paused`), das Monitoring-Tab des Dashboards zeigt beides als Karte
und Statuszeile, und der Abschlussbericht schreibt es unter
`## Arbeitsrückstand`.

Einstellungen: `WORK_ITEMS_PER_CYCLE` (Standard 2, 0 = aus),
`HYPOTHESIS_BACKLOG_LIMIT` (Standard 25, 0 = Bremse aus),
`RUN_BUDGET_MINUTES` (Standard 0 = kein Limit) und `SATURATION_CYCLES`
(Standard 6). Ein Zyklus gilt als leer, wenn er weder eine brauchbare neue
Quelle noch einen erledigten Rückstandspunkt produziert hat. Sind so viele
Zyklen in Folge leer **und** ist die Warteschlange leer, endet der Lauf - mit
einem Bericht unter `data/reports/`. Derselbe Bericht entsteht am Laufzeitbudget
und beim Stoppen. `/api/status` zeigt den Rückstand unter `work_queue` und die
Arbeit des letzten Zyklus unter `cycle_work`.

#### Aufbau des Abschlussberichts

Der Bericht (`research_agent/report.py`) ist kein Zählerstand, sondern die Form,
die jemand prüfen kann - in der Reihenfolge, in der ein Gutachter liest:

| Abschnitt | Inhalt |
|---|---|
| Kurzfassung | Ergebnis in vier Sätzen, aus denselben Zeilen wie der Rest |
| Fragestellung | Thema und die Teilfragen, die der Lauf tatsächlich gestellt hat |
| Methode | Suchlauf, Relevanzfilter, Volltext, Extraktion, Programm, Simulation - jeweils mit den Zahlen, mit denen gearbeitet wurde |
| Ergebnis | Fakten und Hypothesen mit Konfidenz, Programm samt Verdikten, simulierte Experimente, gepoolte Schätzung, was nicht bestätigt wurde |
| Limitationen | aus der Datenbank gezählt: Belegdichte, Volltextabdeckung, nicht replizierte Simulationen, aus Aufwandsgründen geschlossene Teilfragen; dazu Review und Ein-Lauf-Korpus |
| Was würde mich umstimmen | die gespeicherten Falsifikationsbedingungen der Hypothesen, der entscheidende Test je Verdikt, die Falsifikationsbedingung je Simulation |
| Evidenzkette | pro Behauptung: Zitationsschlüssel, wörtliches Zitat, Abschnitt und Seite - oder ausdrücklich der Hinweis, dass keine Textstelle gespeichert ist; auch je Programm-Verdikt stehen die Fakten, gegen die es lief |
| Literatur (BibTeX) | alle zitierten Quellen als `@misc`-Einträge, zusätzlich als Datei `<bericht>.bib` daneben |

Die Zitationsschlüssel sind deterministisch: Nachname des ersten Autors plus
Jahr, bei Kollision ein Buchstabe in Zitierreihenfolge (`doe2024`, `doe2024a`).
Zeitschrift, Band, Seiten und DOI stehen nicht in der Datenbank und werden
deshalb **nicht** erfunden; fehlt eine Quelle im Bestand, bleibt der Schlüssel
`fehlt…` sichtbar statt den Beleg zu verschweigen. Der ganze Bericht ist
LLM-frei: dieselbe Datenbank ergibt denselben Text.

### Volltext und Belegstellen

Ein Abstract ist keine Quelle, aus der man Behauptungen belegen kann: im
Durchschnitt lagen die gespeicherten Quellentexte bei **1.922 Zeichen** - also
bei dem, was Suchmaschinen und Verlage als Zusammenfassung herausgeben. Daraus
lassen sich Themen einschätzen, aber kein Methodenteil, keine Stichprobengröße
und keine Ergebnistabelle prüfen. Jede Quelle bekommt deshalb einen **belegbaren
Dokumenttext** (`research_agent/research/fulltext.py`):

1. **Holen** - zuerst die Seite selbst (PDF-Links werden gelesen, nicht mehr als
   "[PDF document]" abgelegt), dann eine Open-Access-Kopie (Unpaywall-PDF,
   arXiv-PDF zur `abs`-URL, Europe PMC Volltext-XML), zuletzt das Abstract.
   Pro Zyklus werden bis zu `FULLTEXT_PER_CYCLE` ältere Quellen von Abstract auf
   Volltext aufgerüstet, damit der Bestand mit der Zeit heilt.
2. **Gliedern** - der Text wird in Abschnitte zerlegt (Abstract, Introduction,
   Methods, Results, Discussion, References …) und bei PDFs seitenweise
   gespeichert. Beides bleibt als Offset erhalten, nicht als Überschrift ohne
   Textbezug.
3. **Belegen** - die Fakten-Extraktion verlangt zu jeder Aussage den *wörtlichen*
   Satz. Dieser Satz wird **im Quellentext gesucht**, nicht im Modelloutput:
   gefunden → Zeichenbereich, Abschnitt und Seite werden gespeichert; nicht
   gefunden → der Fakt bleibt als Aussage, ist aber als unbelegt markiert
   (`quote_start = -1`) und verliert 15 % Konfidenz. Erfundene Zitate werden so
   nicht zu Belegen.

Damit ein langer Text nicht wieder auf die ersten 5.000 Zeichen zusammenschnitten
wird, wählt `select_text` die aussagekräftigsten Absätze (Ergebnisse vor
Einleitung, Referenzen nie) für den Prompt. Zitiert wird trotzdem gegen das
**ganze** Dokument - der Zeichenbereich zeigt in den vollen Text, nicht in den
gekürzten Prompt.

Gespeichert wird der Text in `data/fulltext/<hash>.txt` (eine Datei pro
Inhalt, nicht pro Quelle) plus eine Zeile in `source_texts` mit Abschnitten,
Seitenranges und Herkunft. Die Fakten tragen `quote`, `quote_start`,
`quote_end`, `quote_exact`, `section`, `page` und `source_text_id`. Im Dashboard
zeigen zwei Karten den Stand: **Full Texts** (Quellen mit echtem Dokumenttext)
und **Cited Facts** (Fakten mit gefundener Textstelle); `/api/stats` liefert
beides unter `fulltext`.

Einstellungen: `FULLTEXT_MAX_CHARS` (Standard 300.000), `FULLTEXT_MAX_PAGES`
(Standard 40) und `FULLTEXT_PER_CYCLE` (Standard 3, 0 = kein Aufrüsten).

Grenzen, ungeschönt: zweispaltige PDFs kommen aus der Textextraktion
verschachtelt, dadurch werden weniger Abschnitte erkannt (Offsets und Zitate
bleiben korrekt); PDFs ohne Textebene (Scans) liefern nichts; und für viele
Verlagsartikel existiert keine Open-Access-Kopie - dann bleibt es beim Abstract,
und der Fakt nennt als Belegstelle eben das Abstract.

### Metaanalyse aus Literatur

Eine gepoolte Zahl aus **publizierten** Studien ist etwas anderes als die
Simulationen des Agenten: sie kommt aus der Welt. Der Weg dorthin läuft über eine
eigene Tabelle, nicht über `evidence` - `evidence` bewertet, wie eine Quelle zu
einer Hypothese steht (ein Urteil), `study_effects` hält fest, was gemessen wurde
(eine Ablesung, die man nachprüfen kann):

| Feldgruppe | Inhalt |
|---|---|
| Zahl | `effect`, `effect_type` (`smd`, `r`, `or`, `rr`, `hr`, `beta`, `mean_diff`, `heritability`, …), `unit`, `direction` |
| Präzision | `se` **oder** `ci_low`/`ci_high` mit `ci_level` (90 % bleibt 90 % - ein blind als 95 % gelesenes KI ist ein Faktor 1,22 im Standardfehler) |
| Studie | `source_id`, `outcome` (gelesen), `outcome_key` (Ziel-Outcome), `comparison`, `n`, `events`, `design`, `population`, `moderators` |
| Beleg | `quote`, `quote_start/end`, `section`, `page` - derselbe Prüflauf wie bei Fakten: ein Satz, den der Quellentext nicht enthält, macht die Zeile **unbelegt** |
| Herkunft | `extractor` (Prompt-Version), `extraction_pass` (1 oder 2) |

Der Extraktionsprompt darf **nur** Zahlen verwenden, die im Text stehen: kein
Schätzen, kein Ableiten, und fehlt der Standardfehler ebenso wie das KI, bleibt
`se` leer - die Zeile ist dann nicht poolbar, und das ist das ehrliche Ergebnis.
Der Text wird vorher über `select_text()` geschnitten, damit Ergebnisabschnitte
statt Front Matter im Kontextfenster landen.

**Zielmaß statt eigener Formulierungen.** Ein Lauf liest zu jedem Paper, *welche*
Zahlen es berichtet - aber nicht, welche davon die Frage beantworten. Genau daran
scheiterte das Pooling: das eine Paper schreibt "fluid intelligence", das nächste
"IQ", jede Zeile bekommt ihre eigene Gruppe, und jede Gruppe bleibt bei k = 1.
Deshalb wird vor der ersten Zahl das **Ziel** aus der Forschungsfrage abgeleitet
(`research_agent/meta/targets.py`): ein LLM-Aufruf pro Thema liefert 2–3 Outcomes
mit Label, den üblichen Synonymen, der Richtung ("higher = better cognition")
und der Skala, die dort üblich ist. Das Ziel wird **einmal** geschrieben und
nicht überschrieben - ein Ziel, das sich nach den Ergebnissen ändert, entscheidet,
was gepoolt wird.

Drei Wirkungen: der Extraktionsprompt bekommt die Labels als festes Vokabular
("use the label EXACTLY as written"); jede gelesene Zeile wird danach
**deterministisch** darauf abgebildet - exakt, über ein Synonym oder über
Enthaltensein ab vier Zeichen (`cognitive ability` in `general cognitive ability`;
kurze Synonyme wie `IQ` matchen nur exakt) - und landet als `outcome_key` in der
Tabelle, während die Formulierung des Modells in `outcome` unangetastet bleibt;
und das Pooling gruppiert nach dem Ziel, nicht nach dem Wortlaut. Zeilen ohne
Treffer werden **nicht** stillschweigend verworfen, sondern als "gelesen, aber
nicht im Zielmaß" gezählt und im Bericht aufgelistet - der Unterschied zwischen
"wir haben 3 Studien gepoolt" und "wir haben 40 Papers gelesen und 3 waren über
diese Frage".

Zeilen, die vor dem Ziel gespeichert wurden, werden **beim Lesen** zugeordnet,
nicht migriert: die Ablesung und ihr Zitat bleiben, nur die Gruppe ändert sich.
Ohne Ziel (Ableitung fehlgeschlagen, oder `META_TARGETS_ENABLED=0`) bleibt alles
wie zuvor, und der Bericht sagt, dass kein Zielmaß abgeleitet wurde.

**Studien-Identität.** Die DOI steht an der Quelle (`sources.doi`, beim Speichern
aus der URL abgeleitet; für Altbestände füllt `scripts/backfill_dois.py` sie
nach). Beim Pooling zählt dieselbe DOI innerhalb eines Outcomes **einmal**: zwei
Papers über dieselbe Kohorte würden dieselben Personen doppelt zählen und das
Intervall verengen, ohne Information hinzuzufügen. Behalten wird die präzisere
Lesung, die verdrängte Zeile steht im Bericht. Zeilen ohne DOI bleiben einzeln -
deshalb nennt der Bericht die Identität als eigene Frage.

Dieselbe Regel gilt **innerhalb** einer Quelle: mehrere Arme, mehrere Kontraste
oder die zweite Lesung derselben Tabelle sind abhängige Schätzungen, keine
zusätzlichen Studien. Sie zählen je Outcome **einmal** (die präzisere Lesung
bleibt). Ohne diese Regel verdoppelt die Doppel-Extraktion bei Papers ohne DOI
jedes k - und genau die sind im OA-Korpus die Mehrheit.

**Nur Primärstudien.** Eine Übersichtsarbeit ist keine Studie: ihr Schätzer ist
schon eine Kombination der Primärstudien, also würde ein Pool sie doppelt zählen
und das Gewicht ihres eigenen Modells übernehmen. Zeilen, deren `design` eine
Metaanalyse, ein systematisches/Scoping-/Umbrella-Review, eine gepoolte Analyse
oder eine quantitative Synthese nennt, werden deshalb **nicht** gepoolt - sie
bleiben mit Zitat in der Tabelle und stehen mit Grund unter „Warum Zeilen nicht
gepoolt wurden“. Die Regel ist deterministisch (`research_agent/meta/designs.py`)
und gilt für Pooling, PRISMA-Zählung und Coverage gemeinsam; ein leeres oder
unbekanntes Design bleibt eine Studie, weil ein fehlendes Feld ein Extraktions-
loch ist und kein Befund. Im ersten echten Lauf zu diesem Thema waren sechs von
acht Zeilen aus Übersichten — der gepoolte Wert lag dadurch bei −1,15 mit einem
Intervall von −11,6 bis 9,3, getrieben von einer Netzwerk-Metaanalyse mit
SMD −2,02. Ohne diese Regel wäre das als Ergebnis im Bericht gelandet.

**Doppel-Extraktion.** Jedes Dokument wird zweimal gelesen (unterschiedliche
Feldreihenfolge und Temperatur). Weichen die Lesungen ab, wird die Zeile als
`disputed` markiert und ist **nicht** poolbar - zwei Zahlen zu mitteln würde den
Widerspruch verstecken. Die Konfliktquote steht im Bericht; sie ist eine
Qualitätsaussage, keine Nebensache. Vor dem Speichern greift ein
Plausibilitätsgate (`|r| <= 1`, Quoten positiv, KI enthält den Punktschätzer,
`n > 0`, `ci_level` in (0,5; 1,0), `se > 0`); abgelehnte Zeilen bleiben mit Grund
erhalten.

**Pooling** (`research_agent/meta/pooling.py`, LLM-frei und aus der Datenbank
reproduzierbar): Effekte werden auf eine Skala gebracht (`r` → Fisher-z, `smd` →
Hedges-g mit kleiner Stichprobenkorrektur, `or`/`rr`/`hr` → Log-Skala, Betas und
Mittelwertdifferenzen roh je Typ) und **innerhalb einer Skala** kombiniert, nie
darüber hinweg. Random Effects mit τ² nach DerSimonian-Laird **und** REML,
Gewichte `1/(v + τ²)`, als Standardintervall **Hartung-Knapp-Sidak** (t mit k-1
Freiheitsgraden), weil das Normalintervall bei kleinem k zu schmal ist; die
Fixed-Effect-Spalte steht zum Vergleich daneben. Dazu `Q`, `df`, `p(Q)`, `I²`,
`H²`, τ, das Prediction Interval (was eine *künftige* vergleichbare Studie
zeigen würde) und die Publikationsbias-Prüfung nach Egger (Achsenabschnitt),
subgruppenweise mit `Q_between`, Leave-one-out über alle Studien und die
Funnel-Daten als Tabelle. Das Protokoll liegt eingefroren unter
`data/reviews/<slug>/protocol.md`, die Ein-/Ausschlussentscheidungen mit Grund in
der Tabelle `screening` - ohne Ausschlussgrund gäbe es keine nachvollziehbaren
Zählungen.

**Grenzen des Verfahrens** (sie stehen auch im Bericht, nicht im Kleingedruckten):

- Ohne institutionellen Volltextzugang ist der Korpus OA-lastig, und im Abstract
  stehen selten Standardfehler. Eine Synthese über diesen Korpus ist systematisch
  nicht repräsentativ - und das ist selbst eine Bias-Quelle, die der Egger-Test
  nicht sieht.
- `k` bleibt klein: für eine enge Frage finden sich selten 10 vergleichbare
  Studien mit nutzbarer Effektgröße. Unter `k = 10` sind Funnel und Egger schwach.
- Kein Risk-of-Bias-Instrument (RoB 2, ROBINS-I), keine GRADE-Bewertung, keine
  Registrierung, kein Peer Review: das Ergebnis ist eine quantitative Synthese,
  **keine** systematische Übersichtsarbeit.
- Gepoolte Beobachtungsdaten bleiben Beobachtungsdaten - der gepoolte Schätzer
  ist keine Kausalaussage.

Einstellungen: `META_EFFECTS_PER_CYCLE` (Standard 1; wie viele Dokumente ein
Zyklus auf Effektgrößen liest - jedes kostet zwei LLM-Pässe, Werte < 1 gelten
als 1), `META_MIN_STUDIES` (Standard 2; darunter wird **nicht** gepoolt,
sondern tabellarisch berichtet) und `META_TARGETS_ENABLED` (Standard 1; leitet
das Zielmaß einmal pro Thema ab). Der Abschnitt `## Metaanalyse` des
Abschlussberichts nennt zuerst die Zählungen (Quellen, bewertet, ausgeschlossen
mit Gründen, eingeschlossen, mit Effektzeile, poolbar, strittig, verworfen), dann
je Outcome und Skala die Forest-Tabelle mit Heterogenität, Prediction Interval,
Subgruppen, Leave-one-out und Egger - und ausdrücklich die Zeilen, die **nicht**
gepoolt wurden, samt Grund. Ohne Effektzeile schweigt der Abschnitt nicht: er
nennt die Zahl der Quellen und sagt, dass die Daten fehlen.

### Labor: eigene Experimente statt nur Zitate

Der Agent prüft seine Vorhersagen selbst. Eine Hypothese mit Falsifikations-
bedingung wird zu einem Experiment, und zwar in der Reihenfolge, in der ein
Wissenschaftler arbeitet:

1. **Preregistrierung** — Population, Stichprobe `n`, erwartete Effektgröße,
   Rauschen, Metrik, Test, `alpha`, Startseed und die Zahl der Wiederholungen
   werden festgeschrieben, *bevor* ein Ergebnis existiert. Das Protokoll liegt in
   `experiments.protocol`.
2. **Skript** — das Modell schreibt `sim.py`, geprüft gegen eine Import-Allowlist
   (`math`, `random`, `statistics`, `json`, `numpy`, `scipy`, …; kein `os`, kein
   Netz, kein `subprocess`, kein `eval`). Die Zahlen kommen aus dem generierten
   Modul `sim_params` (`N`, `EFFECT`, `NOISE`, `ALPHA`, `SEED`,
   `REPLICATIONS`) — hartkodierte Werte werden abgelehnt, sonst wäre weder ein
   Testlauf mit kleinem n noch die Preregistrierung durchsetzbar.
3. **Review vor der Ausführung** — ein unabhängiger Kritiker liest das Skript,
   bevor es läuft: misst es die Variable der Vorhersage, erzeugt es die Daten
   ohne die Schlussfolgerung vorwegzunehmen, gibt es einen echten Test?
   Beanstandungen gehen als Feedback an den Schreiber.
4. **Mini-Testlauf** — dasselbe Skript einmal mit `SIM_SMOKE_N` (Standard 30) und
   einer Wiederholung. Geprüft wird nur, ob es läuft und die vereinbarte
   JSON-Zeile vollständig druckt: `n`, `metric`, `test`, `value`, `p_value`,
   `values`, `p_values`. Ein kaputter Vertrag kostet Sekunden statt einer Studie.
5. **Known-Answer-Tests** — bevor die Studie läuft, wird dieselbe Routine mit
   Parametern ausgeführt, deren Antwort die Theorie festlegt: ohne Effekt muss ein
   gültiger Test zu etwa `alpha` anschlagen (ein 95 %-KI in etwa 95 % überdecken),
   ein verdreifachter Effekt darf die Power nicht senken, ein fester Seed muss
   dieselben Zahlen liefern, und bei überwältigendem Effekt (`d=5`) muss die Power
   1 sein — das gilt für jeden konsistenten Test, auch ohne geschlossene Formel.
   Bei Ein-Schuss-Designs kommt die **Unverzerrtheit** dazu: ohne Effekt muss der
   Schätzer um 0 zentriert sein (4 Standardfehler Toleranz). Ist die Routine ein
   t-Test, kommt der **analytische Anker** dazu: die Power aus der nichtzentralen
   t-Verteilung (`nct`, `df=2n-2`, `nc=d·sqrt(n/2)`) wird per Binomialtest mit der
   gemessenen verglichen — für die ein- *und* die zweiseitige Antwort; gewertet
   wird gegen die, die die Messung trifft, damit eine korrekte einseitige Routine
   nicht an der zweiseitigen Zahl scheitert. Die Prüfläufe nutzen
   `SIM_KAT_TRIALS` (Standard 400), nicht die Trial-Zahl der Studie: mit 150
   inneren Trials sind Power 0,91 und 1,0 nicht unterscheidbar. Widerspricht die
   Routine der Theorie, erzeugt sie keine Evidenz — der Schreiber bekommt Zahlen
   und Traceback und muss sie reparieren.
6. **Reparatur** — scheitert Review, Testlauf oder Lauf, bekommt der Schreiber
   genau diese Fehlermeldung (Traceback, fehlende Schlüssel, Beanstandungen) und
   liefert eine neue Fassung; nach `SIM_SCRIPT_ATTEMPTS` (Standard 3) ist Schluss
   und das Experiment wird als `failed` mit dem Grund gespeichert. Lehnt der
   Reviewer bis zum Ende ab, läuft die letzte testlauf-fähige Fassung trotzdem —
   seine Beanstandungen senken dann über den Audit die Evidenzstärke.
7. **Ausführung** — eigenes Verzeichnis unter `data/simulations/<id>/`, `python -I`,
   geleerte Umgebung (keine API-Keys), blockierte Sockets im Wrapper, harter
   Timeout, Skript-Hash. Das ist eine Absicherung gegen Unfälle, **kein**
   OS-Sandbox — dafür bräuchte es einen Container.
8. **Replikation** — jedes Experiment wiederholt die Studie `SIM_REPLICATIONS`-mal
   mit frischem Rauschen. Ein einzelner signifikanter Lauf ist genau das, was man
   bei zwanzig Läufen ohne Effekt erwartet; das Verdikt hängt an der Quote.
9. **Sensitivitätsprüfung** — dasselbe Experiment bei halbiertem und doppeltem
   Rauschen. Kippt die Schlussfolgerung dabei, wird sie herabgestuft statt
   berichtet.
10. **Audit nach dem Lauf** — derselbe Kritiker prüft am Ergebnis, ob das Skript
   die Vorhersage getestet hat. Pre-Review und Audit werden zusammengeführt:
   beide müssen zustimmen, die Beanstandungen werden gesammelt (eine Halbierung,
   nicht zwei für denselben Mangel).
11. **Verdikt** — deterministisch aus Replikationsquote, Richtung, Sensitivität und
   `alpha`: `supports` nur, wenn ≥ 80 % der Wiederholungen signifikant **und** in
   der vorhergesagten Richtung sind; instabile Signifikanz gilt als „unterpowert“
   (schwach, kein Befund), ein Nullresultat als `neutral` und wird berichtet.
12. **Protokoll-Abweichungen** — weicht das Skript von `n`, `alpha`, Seed oder der
   Zahl der Wiederholungen ab, steht das im Datensatz und senkt die Stärke. Eine
   Studie, die heimlich anders gerechnet hat, ist nicht die preregistrierte.

Evidenz aus einer Simulation ist bei `SIM_EVIDENCE_CAP` (Standard 0,6) gedeckelt
und trägt `evidence.experiment_id` — sie zählt nie wie eine echte Studie. Ist die
Vorhersage nicht messbar (ethisch, normativ, definitorisch), wird die Hypothese
als `not_testable` geschlossen; das ist ein Befund, kein Fehler.

Mehrere Experimente zu einer Hypothese werden **gepoolt** (inverse Varianz,
95 %-KI, I² als Heterogenität) statt gezählt: `report.py` schreibt eine Tabelle
`## Gepoolte Schätzung` plus `## Nicht bestätigt` mit allen widerlegten und
unklaren Befunden. Ein unklares Ergebnis ist ein Grund, die Studie zu wiederholen
(bis `SIM_MAX_PER_HYPOTHESIS`, Standard 2), kein Grund, die Hypothese zu
schließen.

### Zwei Design-Familien

**`one_shot`** (Standard) — die Hypothese handelt von der Welt. Jede Wiederholung
zieht einen Datensatz und schätzt den Effekt; das Verdikt fragt, ob der Effekt
frisches Rauschen überlebt.

**`meta`** — die Hypothese handelt von einem *statistischen Verfahren*: wie viel
Power ein Design hat, ob ein Schätzer verzerrt ist, ob sein 95 %-KI den wahren
Wert überdeckt. Ein Datensatz sagt dazu nichts. Jede Wiederholung führt deshalb
`trials` innere Studien über ein Raster von Stichprobengrößen `grid` aus und
fasst sie zusammen; die Vorhersage ist eine **Schwelle** auf dieser Kennzahl:

| Feld | Bedeutung |
|---|---|
| `metric_kind` | `power` (Anteil p < alpha) · `bias` (mittlere absolute Abweichung) · `coverage` (Anteil überdeckender 95 %-KI) |
| `trials` | innere Studien pro Rasterzelle, 50–200 000 |
| `grid` | ansteigende Stichprobengrößen, 1–6 Werte, je ≥ 10 |
| `n` | die Rasterzelle, von der die Vorhersage spricht; muss im Raster liegen |
| `threshold` | vorhergesagter Wert der Kennzahl (Anteil für power/coverage, Toleranz für bias) |
| `comparison` | `at_least` oder `at_most` |

Beispiel: „Power bei n=200 ist mindestens 0,6 für d=0,5“ → `n=200`,
`grid=[100,200,400]`, `threshold=0.6`, `comparison=at_least`, `trials=2000`. Der
p-Wert jeder Wiederholung kommt aus einem einseitigen Test der Kennzahl gegen
die Schwelle (`binomtest` für power/coverage, `ttest_1samp` für bias), und die
Replikationslogik bleibt dieselbe: `supports` nur, wenn die Schwelle in ≥ 80 %
der Wiederholungen **und** signifikant gehalten wird. Zusätzlich berichtet das
Ergebnis die `cells` über das ganze Raster und einen `trend` (Anteil der
Rasterschritte, die sich wie vorhergesagt bewegen); der Bericht kennzeichnet
diese Experimente als `meta/power` usw.

Einstellungen: `SIMULATIONS_ENABLED`, `SIM_REPLICATIONS` (Standard 5, Minimum 3),
`SIM_MAX_PER_HYPOTHESIS` (Standard 2), `SIM_SCRIPT_ATTEMPTS` (Standard 3),
`SIM_SMOKE_N` (Standard 30), `SIM_SMOKE_TIMEOUT` (Standard 45),
`SIM_KAT_ENABLED` (Standard 1), `SIM_KAT_TRIALS` (Standard 400, innere Trials je
Prüflauf), `SIM_TIMEOUT_SECONDS`, `SIM_EVIDENCE_CAP`, `SIM_DIR`. Das Monitoring-Tab zeigt unter `Labor` die letzten Experimente mit
Verdikt, Replikationsquote und dem Known-Answer-Ergebnis (`KAT 3/4`, Kachel
`Known-Answer` als Summe über die letzten Läufe); `/api/status` liefert sie unter
`experiments` (`kat_passed`, `kat_total`). Der Abschlussbericht schreibt die
Prüfungen als Spalte `KAT` neben jedes Experiment.

Extracted facts get a confidence derived from their evidence rather than from
the model's self-report: source credibility and study quality, how much of the
source was actually read (full text vs. abstract vs. snippet), and whether the
sentence states a measured number or hedges ("may", "suggests"). The model's
own rating only nudges it by +/-0.05, and the value is capped at 0.90.
`MemoryStore.recalibrate_stored_facts()` recomputes it for existing rows.

Every cycle must produce concrete state changes:
- New source, new evidence, new hypothesis
- Updated hypothesis confidence
- Resolved contradiction
- New research question
- Backlog item finished (full text recovered, hypothesis tested, question closed)

A run ends for a reason and says which: `RUN_BUDGET_MINUTES` reached, backlog
exhausted (`SATURATION_CYCLES` empty cycles with an empty queue), or the user
stopped it. In every case the closing report is written first.

## Agent Roles

| Role | Purpose |
|------|---------|
| **Researcher** | Finds and gathers information |
| **Analyst** | Identifies patterns and synthesizes |
| **Critic** | Challenges conclusions, finds biases |
| **Planner** | Prioritizes questions, adapts strategy |
| **Synthesizer** | Creates coherent research narratives |

All roles use the same chat model with different system prompts.

## Dashboard

The web dashboard shows:
- Current research topic and phase
- Active research question
- Statistics (sources, cycles, hypotheses, facts)
- Active hypotheses with confidence levels
- Open research questions ranked by priority
- Recent sources with credibility scores
- Contradictions found
- Research journal entries
- Tokenverbrauch: heute, pro Tag und pro Phase (siehe unten)
- Start/Pause/Resume/Stop controls

### Tokenverbrauch

Jeder LLM-Aufruf schreibt eine Zeile in `llm_usage` (Phase, Backend, Modell,
Prompt-/Completion-Tokens, Dauer, Erfolg) und wird über den Sink in
`LLMEngine.set_usage_sink()` vom Orchestrator gespeichert. Die Zähler im Engine
selbst liegen nur im Prozessgedächtnis und beginnen nach einem Neustart wieder
bei null — für „wie viel hat heute gekostet?“ ist deshalb die Tabelle die
Antwort, nicht das Dashboard-Live-Feld.

Das Panel `LLM Performance` zeigt beides: die Live-Zähler dieses Prozesses und
darunter `Tokens heute`, `Aufrufe heute`, `Tokens/Aufruf`, `Fehler heute`,
`Gesamt (DB)` sowie den Verbrauch der letzten sieben Tage. Die Phasenbalken
kommen aus der Datenbank, sobald dort Zeilen für heute liegen — sie überleben
also einen Neustart. Abfragbar ist das auch direkt:

```bash
curl -s http://localhost:8080/api/llm-stats | python -m json.tool
# ... "persisted": {"today": {...}, "by_phase": [...], "by_model": [...], "by_day": [...]}
```

Der `day` einer Zeile ist das lokale Datum des Aufrufs; `timestamp` bleibt die
vollständige Zeit mit Zeitzone. Ein Speicherfehler wird geschluckt (und auf
Debug geloggt): die Abrechnung darf niemals einen Forschungszyklus abbrechen.

## Database Schema

| Table | Purpose |
|-------|---------|
| `sources` | All researched sources with dedup |
| `facts` | Verified factual claims, mit Belegstelle: `quote`, `quote_start/end`, `section`, `page`, `source_text_id` |
| `source_texts` | Volltext einer Quelle: Abschnitte mit Offsets, Seitenranges, Pfad in `data/fulltext/` |
| `claims` | Claims extracted from sources |
| `hypotheses` | Active and historical hypotheses |
| `evidence` | Evidence supporting/contradicting hypotheses |
| `research_questions` | Open and answered questions |
| `research_sessions` | Session metadata |
| `journal_entries` | Cycle-by-cycle journal |
| `contradictions` | Detected contradictions |
| `knowledge_nodes` | Knowledge graph nodes |
| `knowledge_edges` | Knowledge graph edges |
| `embeddings` | Vector embeddings for semantic search |
| `experiments` | Simulierte Experimente: Protokoll, Skript, Ergebnis, Replikationsquote, Protokoll-Abweichungen |
| `study_effects` | Effektgrößen aus publizierten Studien: Zahl, `se`/KI mit `ci_level`, `n`, Design, Belegsatz mit Abschnitt und Seite, `outcome_key` (Ziel-Outcome), `disputed` und `rejection_reason` |
| `review_targets` | Das Zielmaß der Synthese je Thema: Frage, Population, Outcomes mit Synonymen und Richtung; einmal geschrieben und eingefroren |
| `screening` | Ein-/Ausschlussentscheidung je Quelle mit Grund und Urheber (Grundlage der PRISMA-Zählungen) |
| `llm_usage` | Ein Eintrag pro LLM-Aufruf: Tokens, Phase, Modell, Dauer — die Grundlage der Tages- und Phasensummen |

## Testing

```bash
# Run all tests
python -m pytest research_agent/tests/ -v

# Component tests only
python -m pytest research_agent/tests/test_components.py -v

# Volltext-Pipeline: Abschnitte, Zitate, Seiten, PDF-Parsing (offline)
python -m pytest research_agent/tests/test_fulltext.py -v

# End-to-end test
python -m pytest research_agent/tests/test_e2e.py -v -s
```

## Project Structure

```
research_agent/
  config.py           - Configuration loader
  models.py           - Data models (dataclasses)
  database.py         - SQLite database layer
  orchestrator.py     - Main research loop
  main.py             - Entry point
  llm/
    engine.py         - Ollama API wrapper
  research/
    search.py         - Search providers (DDG, arXiv, PubMed)
    extractor.py      - Web content extraction
    sources.py        - Source management & dedup
  memory/
    store.py          - Facts, hypotheses, knowledge graph
    retrieval.py      - Semantic search via embeddings
  agents/
    base.py           - Base agent class
    roles.py          - Researcher, Analyst, Critic, Planner, Synthesizer
  dashboard/
    server.py         - HTTP server for dashboard
    templates/
      index.html      - Dashboard UI
  tests/
    test_components.py - Unit/integration tests
    test_e2e.py       - End-to-end pipeline test
```

## Troubleshooting

**Ollama not reachable:**
```bash
ollama serve  # Start Ollama server
```

**Slow first cycle:**
The first LLM call may be slow as the model loads into memory.

**No search results:**
Check internet connectivity. DuckDuckGo may rate-limit. arXiv and PubMed work without API keys.

**Empty LLM responses:**
qwen3 models use "thinking" mode. The agent handles this automatically.
