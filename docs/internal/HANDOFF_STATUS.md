# Handoff: Status des Autonomous Research Agents

**Stand:** 01.11.2026, Abend (Research-Agent) · Goldstandard B: 10.11.2026 · **Projekt:** `D:\daswu\AIResearch`, Paket `research_agent/`
**Auftrag an die empfangende KI:** verbesserungsvorschläge machen. Siehe Abschnitt 6 (bekannte Schwächen) und 7 (offene To-dos). Für den Goldstandard-Workstream siehe Abschnitt 0.

## 0. Goldstandard B: Stand 10.11.2026

Dieser Workstream ist getrennt vom Agenten-Betrieb. A und B bleiben
getrennt; es gab keinen Vergleich zwischen A und B.

### Stand

| Gegenstand | Stand |
|---|---|
| `goldstandard_A.json` | 69 Zeilen, 13 Begründungen, 0 offen, 30 Dokumente |
| A-Hash | `d9bb867c303dc19ddaf90cce3414ada0f4484b5a03881d65261950db0762a810` |
| `goldstandard_B.json` | 0 Zeilen, 0 Begründungen, 30 offen, 30 Dokumente |
| B-Hash (Gerüst) | `93802e1798ae5e54ef3896e162e2fdeb2d783486a40239df590ddfa0dfe46d20` |
| B-Rücklauf | liegt nicht vor |
| B-Abgabe-Hash | nicht eingefroren |
| Kappa/Konflikte | nicht gestartet |

### Vorhandene Artefakte

- `blind_b_20261110.zip` — portables Blind-Paket mit 30 Volltexten,
  SHA-256 `2f9db202c218abaf34bbabbb332c7e31d64693b0faed467dda3854e5a3b9b173`.
- `data/golden_effects/blind_b_20261110/` — Vorlage mit B-Gerüst,
  Anleitung v1.2, Schema, 30 Arbeitsblättern, Manifest und Prüfsummen.
- `scripts/pruefe_b_ruecklauf.py` — prüft IDs, Vollständigkeit,
  Designmetadaten und Hash; schreibt die Abgabenotiz nur bei 0 Fehlern
  und 0 offenen Dokumenten.
- `docs/internal/goldstandard_B_uebergabe_20261110.md` — versandfertige
  Anweisung für die externe Annotation.
- `docs/internal/status_20261110_b_ruecklauf.md` — ausführlicher
  Statusbericht.
- `docs/internal/vollannotation_abgabe_checkliste_20261110.md` —
  Checkliste mit offenen Abgabe-Hashes.
- Paketprüfung: 36 Prüfsummen OK, ZIP mit 67 Dateien und 30 Volltexten,
  B im ZIP mit 0 Fehlern und 30 offen; keine echte A-Datei.

### Nächste Schritte

1. Externen B-Rücklauf unter
   `data/golden_effects/goldstandard_B_ruecklauf.json` ablegen.
2. Zuerst nur prüfen:

       .venv/bin/python.exe scripts/pruefe_b_ruecklauf.py data/golden_effects/goldstandard_B_ruecklauf.json --keine-notiz

3. Bei Fehlern den Rücklauf an die annotierende Person zurückgeben;
   keine inhaltlichen Korrekturen selbst vornehmen.
4. Bei 0 Fehlern und 0 offenen Dokumenten ohne `--keine-notiz` laufen
   lassen; die Abgabenotiz mit SHA-256 erzeugen.
5. B-Hash in die Abgabe-Checkliste eintragen und B nicht mehr ändern.
6. Erst danach A öffnen und Kappa/Konflikte mit dem Rücklauf berechnen:

       B=data/golden_effects/goldstandard_B_ruecklauf.json

       .venv/bin/python.exe scripts/werte_kappa_probe.py --b "$B"
       .venv/bin/python.exe scripts/berichte_kappa_konflikte.py --b "$B" --md docs/internal/kappa_konflikte_vollannotation_20261110.md --out data/golden_effects/kappa_konflikte_vollannotation.json
       .venv/bin/python.exe scripts/priorisiere_kappa_konflikte.py --quelle data/golden_effects/kappa_konflikte_vollannotation.json --md docs/internal/kappa_konflikte_priorisiert_vollannotation_20261110.md --out data/golden_effects/kappa_konflikte_priorisiert_vollannotation.json

7. Konflikte für die dritte Stimme klären; Schwelle Zeilen-Kappa 0,80.

### Guardrails

- B nicht selbst annotieren: Der Assistent hat A geschrieben; die
  Zweitannotation muss unabhängig bleiben.
- A erst nach eingefrorenem B-Hash öffnen oder vergleichen.
- Keine Netzläufe und keine Modellaufrufe für diesen Schritt.
- Das portable ZIP bleibt untracked; es enthält Volltexte und gehört
  nicht ins Repository.

## 1. Zweck und Arbeitsweise

Ein autonomer Recherche-/Metaanalysen-Agent (Python, ~30 Module). Für ein Thema durchläuft er selbstständig:

1. **Suche** über wissenschaftliche Provider (arXiv, PubMed, Europe PMC, Crossref, OpenAlex, Semantic Scholar; DuckDuckGo deaktiviert wegen Bot-Challenge).
2. **Relevanz-Gate** (LLM-Score 0–1, Schwelle 0.25) → Volltext-Recovery (arXiv-PDF, PubMed-Abstract-API, Crossref-Fallback) → Relevanz-Urteil am Dokumenttext, nicht am Abstract.
3. **Quellen-Analyse + Fakten-Extraktion** mit Pflicht-Quote-Verification: jede Fakten-Aussage muss per String-Suche im gespeicherten Dokumenttext lokalisiert sein; sonst wird sie als „nicht am Text nachprüfbar" markiert, nie still gelöscht.
4. **Forschungsprogramm:** Thema wird in Teilfragen zerlegt (je 8 Zyklen Budget, Sättigungsregel), Verdicts je Teilfrage.
5. **Hypothesen-Agentur:** mikro-spezifische mechanistische Hypothesen, gerichtete Evidenz-Klassifikation (supports/contradicts/neutral), Kontradiktionen-Scan, Devil's Advocate mit Gegen-Recherche.
6. **Meta-Schicht:** Effektgrößen-Extraktion nach `study_effects` (mit Zitatposition, Section, Page), Zielmaß-Ableitung (einmalig, eingefroren), Screening-Zählliste PRISMA-artig, Risk-of-Bias (6 Domänen, quote-belegt, Doppel-Durchlauf), GRADE, Pooling (Random Effects Hartung-Knapp-Sidak + REML, Subgruppen nach Design, Leave-one-out, Egger-Regression).
7. **Abschlussbericht:** deterministisch aus der SQLite-DB erzeugt (keine LLM-Aufrufe im Bericht). Enthält PRISMA-Durchfluss mit Ausschlussgründen, Summary of Findings (nur bei k ≥ Mindestzahl), Structured Abstract, Registrierung/Reproduzierbarkeit, Limitationen inkl. Suchprovider-Ausfallstatistik, „Was würde mich umstimmen"-Bedingungen, BibTeX; PDF folgt.

Grundprinzip: Zahlen/Evidenz sind deterministisch und nachprüfbar (DB); nur Lesen/Klassifizieren macht das LLM. Jede maschinelle Bewertung ist als solche gekennzeichnet (RoB/GRADE sind nicht menschlich verifiziert, das steht im Bericht).

## 2. Architektur-Übersicht

- `main.py` — CLI (`--topic`, `--no-dashboard`, `--port`, `--model`); Instance-Lock **pro Datenbank** (verschiedene Topics parallel erlaubt); LLM-Gesundheitscheck vor Start. **Heute gefixt:** Headless terminiert nach Session-Ende hart (`os._exit` nach `guard.release()` + `logging.shutdown()`), weil offene aiohttp-Transports `asyncio.run` sonst nie zurückkehren ließen (beobachtet: fertiger Lauf hing 4 h als Zombie mit DB-Sperre).
- `orchestrator.py` (~4540 Zeilen) — Zyklus-Pipeline; Arbeit über `work_queue`-Backlog (Arten: full_text, hypothesis_evidence, open_question, citation, simulation, effect_extraction, bias_assessment; Prioritäten mit Outbid-Logik). Phase 7b (Gegenargumente je Hypothese) läuft jetzt via `asyncio.gather`; Phase 7c ist der Devil's Advocate. Budget-Ende → Closing-Report.
- `llm/engine.py` — Backends: **TUDaGPT** (remote, OpenAI-/litellm-kompatibel, Modell `qwen3.5-397b-a17b`, kostenlos, campus-netz-abhängig) und lokal Ollama. Retry mit Backoff; Watchdog: nach 5 konsekutiven LLM-Fehlern pausiert der Run statt leere Zyklen zu schreiben. **Neu heute:** globales `asyncio.Semaphore` liest Breite aus `config.llm_concurrency` (vorher hardcodiert 3), loop-safe (Neubau bei Loop-/Width-Wechsel). Usage-DB `data/research-usage.db` pro Call (phase/backend/model/tokens/dauer).
- `research/search.py` — Provider-Adapter + Circuit-Breaker (`RateLimitMemory`): **neu:** 3 statt 2 Retries, Ladder 3/6/9 s, Retry-After-Cap 20 s, Cooldown 600 s und Eskalation je wiederholtem Ausfall (live beobachtet 600→1200→1800 s).
- `research/extractor.py`, `research/fulltext.py` — Volltext-/Abstract-Recovery; `select_text` wählt das informativste Textbudget priorisiert nach Abschnitten (Referenzen fallen raus).
- `memory/store.py` — Fakten (mit Quote-Verifikation), Hypothesen, Evidenzzeilen, Wissensgraph.
- `meta/extraction.py` — `EffectExtractor` (Doppel-Durchlauf; Differenzen werden als `disputed` markiert, nie gemittelt). `EFFECT_TYPES = (smd, g, r, z, or, rr, hr, beta, mean_diff, heritability, other)`. Hartschinen-Gate `check_plausibility`: unbekannter Effekttyp, fehlender Effektwert, Simulations-Annahme (Regex auf „we set … to −0.05"), r∉[−1,1], or/rr/hr ≤ 0, SE ≤ 0, verdrehtes/unvollständiges Konfidenzintervall, KI enthält Punktschätzer nicht, KI-Level∉(0.5,1.0), absurd n, fehlende Richtung. **Neu heute:** Prompt macht `effect_type` zur Pflicht; neue `infer_effect_type()`-Heuristik rekonstruiert **nur einen leeren** Typ aus dem eigenen Zeilentext (hazard/odds/risk ratio, correlation, standardized mean difference, …; Ratio-Familie zuerst). Erfundene Typen (z. B. „galaxy") bleiben abgelehnt.
- `meta/targets.py` — Zielmaß-Ableitung durch einen LLM-Aufruf, einmal pro Thema, **eingefroren**. `canonical_outcome` matcht exakt → Alias → Containment (Alias ≥ 4 Zeichen, damit „iq" nicht wahllos schluckt). Design-Properties (statistical power, sample size, causal effect, p-value …) werden abgelehnt. **Neu heute, `meta-targets/2`:** Prompt erlaubtABB max. 5 Outcomes: 2–3 Kernmaße plus 1–2 eng verwandte physiologische Endpunkte als *eigene* Einträge mit *eigenen* Aliassen (Alias-Merge explizit verboten — das würde verschiedene Konstrukte zu einer Zahl poolen). Exposure-Metadaten (MEDAS/aMED-Scores, Rating-Skalen, Test-retest-Reliabilität) sind ausdrücklich ausgeschlossen, da nie poolbare Gesundheitsmaße.
- `meta/pooling.py` — Skalen-Standardisierung (smd/g/d → Hedges-g; r → Fisher-z; or/rr/hr → log_ratio mit aus KI abgeleitetem SE auf berichtetem Level; beta/mean_diff/other → raw mit SE-Pflicht). RoB-/Übersicht-Gate (design-Feld nennt „meta-analysis/systematic review/…" → „keine Primärstudie"). **DOI-Dedup bereits gebaut und getestet** (case-insensitive; bei Duplikat bleibt die präzisere Lesung). Gruppiert nach (outcome_key, Skala); liefert pools mit Q/I²/τ² (DL + REML), Vorhersage-Intervall, `subgroups_design`, `leave_one_out`, `egger`, `scope_flags` (POPULationsverletzung wird gezeigt, nicht versteckt).
- `meta/risk_of_bias.py` — 6 Domänen, gegenläufige Doppel-Läufe, Zitat-Pflicht, Abweichung → `disputed` (nicht gemittelt).
- `meta/grade.py` — automatisierte Abwertungen (RoB, Inkonsistenz I², Imprecision-KI-Breite) vom designabhängigen Startniveau.
- `meta/designs.py` — `aggregate_design`/`is_primary_study`: **nur positive Beweise schließen aus**; leere/unbekannte designs bleiben Primärstudien. **Neu heute:** dieselbe Regel wird als Titel-Gate im Orchestrator verwendet — heißt der Titel „systematic review of …", überspringt die Quelle die Effekt-Extraktion (spart 2 LLM-Pässe je benanntem Review; der Pool-Gate bleibt zweite Instanz für unbenannte Reviews).
- `meta/screening.py` — schreibt die Screening-Entscheidungen je Quelle (included = Relevanz ≥ Schwelle **und** echtes Dokument) und deckt sie mit derselben Pool-Regel ab, damit Zähler und Tabelle nicht differieren.
- `report.py` — deterministischer Bericht; druckt Subgruppen, Leave-one-out, Egger, scope-flags; Limitations-Sektion zählt die Suchausfälle je Provider.
- `work_queue.py`, `program.py`, `experiments/` — Backlog und Teilfragen/Simulations-Lab.
- `dashboard/server.py` — HTTP-Panel; Metaanalyse-Endpoint spiegelt dieselbe `build_analysis`-Pipeline (kein Zahlen-Divergenzrisiko zwischen Dashboard und Bericht).
- `config.py` — alles via `.env`: unter anderem `RUN_BUDGET_MINUTES=240` (Wanduhr-Sicherheit: ein früherer Bug ließ Backlogs sich endlos selbst nachfüllen, der Prozess lief stundenlang weiter), `PROGRAM_ITEM_BUDGET_CYCLES=8`, `milestone LLM_CONCURRENCY` (neu, default 3, aktuell 6), `FULLTEXT_PER_CYCLE` (neu gesetzt: 6 statt 3), `SOURCE_RELEVANCE_THRESHOLD=0.25`, `meta_min_studies=2`, `llm_failure_threshold=5`. Env liest nur beim Start — Knopfänderungen brauchen einen Neustart des Prozesses.
- `instance_guard.py` — Sperre als `data/research-<hash>.pid`.

## 3. Live-Stand im Moment

- **Aktiver Lauf:** PID 44248, topic „Mediterrane Ernaehrung und kardiovaskulaeres Risiko bei Erwachsenen", DB `data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db`, Log `data/agent_run_mediterranean2.log`, gestartet 21:44, Run-Budget 240 min (~Ende 01:44). Zyklus 1–2 stabil, 203 Quellen im Bestand (Stand 22:01), Relevanz-Ø 0.59 (Vormittag: 0.36); TUDaGPT-429s werden vom Backoff regulär abgefangen.
- **Wichtig für die nächste KI:** der aktive Lauf startete mit dem Code-Kontext von 21:44 und enthält daher die Parallelisierungs-Umbauten, aber **nicht** die späteren Patches (Titel-Gate, `meta-targets/2`, `FULLTEXT_PER_CYCLE=6`, Zombie-Exit). Diese wirksam erst beim nächsten Start.
- **Baseline des Vortags (Closing-Report `data/reports/20261101-1953-…md`, 68 KB):** 44 Zyklen, 186 Quellen, 128 bewertet, 87 eingeschlossen, 130 Volltexte (53 % Abdeckung),Effektzeilen 67 → **nur 19 im Zielmaß** → 30 poolbar (29 verworfen wegen „unbekannter Effekttyp ‚(leer)'" — der heute gefixte Bug) → **ein Pool mit k = 2** (I² 97 %, KI [−8.07, 8.66] — rechnerisch korrekt, inhaltlich leer). 62 Hypothesen ↔ 66 gerichtete Evidenzzeilen; 35 Fakten (97 % belegt); 5 Teilfragen als „done", aber kein Verdikt „beantwortet".
- Historisch: 16 327 LLM-Calls (Stand vor dziś), Ø-Zeiten analytisch 10.6 s, kritisch 5.0 s, synthetisch 21.6 s.

## 4. Heutige Patches (chronologisch)

1. **`LLM_CONCURRENCY`-Knopf** (`config.py`, `llm/engine.py`) — Semaphore-Widt aus config; loop-safe; Default bleibt 3; `.env` jetzt 6.
2. **Phase 7b parallelisiert** (`orchestrator.py`) — `asyncio.gather` statt serialer Doppel-LLM-Aufrufe.
3. **Extrakt-Koaleszenz** (`orchestrator.py`) — `self._facts_in_flight` keyed `"{source.id}|{topic}"`; parallele Duplikate einer Fakten-Extraktion teilen einen LLM-Call (behebt das beobachtete Doppel-„Extracted 0 facts" innerhalb ~100 ms).
4. **Effekttyp-(leer)-Fix** (`meta/extraction.py`) — Prompt-Pflicht + `infer_effect_type`; 3 neue Tests.
5. **Provider-Retries** (`research/search.py`) — 3 Versuche, Ladder 3/6/9 s, Retry-After-Cap 20 s, Cooldown 600 s.
6. **Titel-Gate für Reviews** (`orchestrator.py`) — benannte Reviews überspringen die Effekt-Extraktion; dieselbe `aggregate_design`-Regel wie der Pool.
7. **Zombie-Exit** (`main.py`) — saubere Sperre-Release + Log-Flush + starrer Exit mit korrektem Exit-Code.
8. **`.env`-Knöpfe** — `FULLTEXT_PER_CYCLE=6`.
9. **`meta-targets/2`** (`meta/targets.py`) — verwandte Endpunkte als eigene Pools, Exposure-Metadaten ausgeschlossen.

**Tests heute:** 47/47 (`test_meta_extraction` + `test_research_engine`), 34/34 (`test_meta_targets`), 58/58 (`test_work_queue` + `test_e2e`, e2e baut den kompletten Orchestrator mit Fake-Backend), 56/56 am Vormittag (`test_report` + `test_meta_report` + `test_meta_quality_gates`). `py_compile` für alle geänderten Dateien grün.

**Konventionen:** `PYTHONIOENCODING=utf-8` (Windows-Konsole CP850); pytest-Timeout ≤ 300 s; gezielte Nachbarsuitens statt der ganzen Suite (>290 s wird zu groß).

## 5. Was bereits existiert und nicht doppelt gebaut werden sollte

- DOI-Dedup vor dem Poolen (getestet). 
- Leave-one-out, Subgruppen nach Design, Egger — berechnet und gedruckt, sobald k ≥ 3; bei k<2 sagt der Report „zu wenige Studien" statt einen Unsinn zu poolen.
- Effektmaß-Skala-Trennung: SMD und Fisher-z teilen niemals einen Pool; or/rr/hr werden auf log_ratio normiert, raw-Maße behalten ihre Einheiten.
- Doppel-Extraktion → `disputed` statt Mittelung.
- Quote-Verifikation für Fakten **und** Effektzeilen (nicht am Text fundierte Lesungen behalten Ursprüngliche, werden aber nicht als belegt gezählt).

## 6. Bekannte Schwächen (aktuell gültig)

1. Der aktive Lauf läuft noch mit dem 21:44-Kontext; Titelfeld-Gate `meta-targets/2` und `FULLTEXT_PER_CYCLE=6` wirken erst beim Neustart.
2. Die Effekttyp-Rettung hat im laufenden Log bis jetzt **kein einziges Mal** getriggert (0 Treffer) — ob die 29 Verwurf-Zeilen tatsächlich gerettet werden, zeigt erst der Abschlusslauf.
3. Provider-Suchausfälle (OpenAlex/Semantic Scholar) werden abgefangen, aber man sieht nicht quantifiziert im Live-Verlauf, wie viel **geliefert** wurde pro Provider im Run (nur im Closing-Report).
4. Das „Neutral"-Recycling der Evidenz-Klassifikation: 43 Klassifikationen → 0 gerichtete Zeilen in 3 Zyklen (Basislinie) — Ursache offen; die Budget-Sperrdatei füllt die Lücke, nicht die Diagnose.
5. Volltextabdeckung 53 %; Tabellen in PDFs (die weitaus meisten Effektgrößen) werden **nicht** gelesen, weil der Extraktor laufend Fließtext konsumiert — größter verbleibender Yield-Hebel.
6. Sättigungs- und bias-Bericht können unkoordiniert laufen (die Bias-Warnungen, die XFerro-zahlen aus die Zyklen ablesen, ignorieren den Zyklus-Kontext).
7. Erwartung mit User-Entscheidungen: `LLM_CONCURRENCY`=6 ist unma 롤北斗prüfung; die 429-Rate des Backends kann steigen (Backoff korrigiert es, aber Durchsatzzugewinn ist unbelegbar bis der Lauf durch ist).

## 7. Offene To-dos

| # | Was | Warum | Wie verifizieren |
|---|---|---|---|
| 1 | Nach Lauf-Ende zählen: `(leer)`-Verwürfe vor/nach (29 Basislinie) | Beweis für Fix | Log-Grep „Effect type missing - inferred" + DB-Abruf `rejection_reason` |
| 2 | Zombie-Exit verifizieren: nach Session-Ende Prozess weg, Sperren-Datei frei | Beweis für Fix | `tasklist`, PID-Datei |
| 3 | A/B-Kennzahlen: Effektzeilen, Verwurfquote, poolbar, k im Pool | Baseline 20:53-Report | DB + Closing-Report |
| 4 | Tabellen-PDF-Parsing (Tabellen-Zellsucher in `fulltext.py`) | größter Yield-Hebel | vgl. Abschnitt 6.5 |
| 5 | Human-in-the-Loop-Review-UI (Screening bestätigen + RoB verifizieren, mit kappa) | PRISMA-/GRADE-Anforderungen | Dashboard-Erweiterung |
| 6 | Unabhängiger Reproduktionslauf (zweites Korpus, Vergleich der Schlüsse) | Report-Limitation „Reproduzierbarkeit liegt in der DB, nicht in Wiederholung" | zweiter Umfang + Diff |
| 7 | `LLM_CONCURRENCY=6`-Effekt: Calls/s vor/nach aus der usage-DB | Beweis für Parallelisierung | SQL auf `data/research-usage.db` |
| 8 | Evidenz-Klassifikation: warum gleichrichtige Neutral-Recycling? | Yield-Schwäche | DB-Aufschlüsselung der Klassifikationsgründe |

## 8. Grundsätze (nicht ohne Verstand „verbessern")

Diese Entscheidungen sind bewusst gesetzt und durch Tests bedacht:

- **Keine Berechnung im Bericht:** das LLM darf Zahlen nicht erfinden oder umrechnen. Eine OR→RR- oder g→d-Konvertierung ist deshalb bewusst **nicht** gebaut — sie braucht Baseline-Daten, welche die Studien nicht liefern; das würde den „never compute"-Verstoß genau wieder einführen.
- **Nur positive Beweise schließen aus:** leere/unbekannte Designs schließen nie aus; verworfene Zeilen behalten einen schriftlichen Grund und werden im Bericht gezählt, nie still gelöscht.
- **Frozen-Protokoll:** Zielmaß und Protokoll werden vor der ersten Lesung fixiert; nachträgliches Re-Aiming wäre ein Protokollverstoß. Änderungen wie `meta-targets/2` greifen für **den nächsten** Lauf.
- **Doppel-Lesung weicht ab → disputed**, nie gemittelt; unentschiedene Zeilen poolen nicht.
- **Maschinen-Ratings** (RoB/GRADE) sind im Bericht als nicht-verifiziert deklariert (Nutzerfreigabe 31.10.2026) — jedes Rating ist mit einem wörtlichen Zitat belegt und über die DB nachprüfbar.
- **Semaphor-Default bleibt 3** (Nutzerentscheidung); 6 ist nur ein '.env'-Wert, nicht Code-Änderung.

## 9. Schnell-Befehle

```bash
# Tests (Konventionen beachten)
PYTHONIOENCODING=utf-8 python -m pytest research_agent/tests/test_meta_extraction.py -q
PYTHONIOENCODING=utf-8 python -m pytest research_agent/tests/test_work_queue.py research_agent/tests/test_e2e.py -q   # ~3 min

# Compile nach dem Editen
python -m py_compile research_agent/main.py research_agent/orchestrator.py research_agent/meta/extraction.py research_agent/meta/targets.py research_agent/research/search.py research_agent/llm/engine.py

# Lauf starten (PID notieren, Log umleiten)
PYTHONIOENCODING=utf-8 python -m research_agent.main --no-dashboard --topic "..." > data/agent_run_<name>.log 2>&1 &
# Zombie aufräumen: taskkill //PID <n> //F; Sperre data/research-<hash>.pid löschen

# Live-Log prüfen
tail -n 40 data/agent_run_mediterranean2.log

# Bericht aus DB neu bauen (PDF folgt automatisch)
PYTHONIOENCODING=utf-8 python -c "from research_agent.database import Database; from research_agent.report import build_report; print(build_report(Database('data/research-<db>.db'), '<topic>', reason='...'))"
```
