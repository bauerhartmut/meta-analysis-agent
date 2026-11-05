# Verbesserungsbriefing für Claude — Metaanalyse-Agent

> **Zweck dieses Dokuments:** Du (Claude) erhältst hier eine vollständige, selbsttragende
> Beschreibung des Projekts, seiner Architektur, seiner unantastbaren Verträge und seines
> aktuellen Stands. Deine Aufgabe ist es danach, **konkrete, priorisierte
> Verbesserungsvorschläge** zu erarbeiten — nicht Änderungen direkt umzusetzen, sondern
> einen begründeten Vorschlagskatalog zu liefern, den der Nutzer auswählen kann.
>
> **Sprachregel:** Antworte ausschließlich auf Deutsch. Schreibe keinen Code- oder
> Datei-Text, der chinesische Zeichen enthält.
> **Geheimnisregel:** Nie API-Keys im Chat, Code oder Dateien. Die `.env` wird niemals
> gelesen (höchstens per `grep -c` auf Existenz geprüft).Wenn du Beispieldaten brauchst,
> erfinde Platzhalter.

---

## 1. Projekt in einem Satz

Ein **autonom laufender Metaanalyse-Agent** (Python, lokal, Windows + Git Bash), der zu
einem Forschungsthema selbstständig recherchiert (Web + PDF-Volltexte), Evidenz extrahiert,
Hypothesen bildet, sie adversarial prüft (Devil's Advocate), statistisch poolt
(Metaregression) und daraus einen belastbaren, zitierfähigen Bericht erzeugt — gesteuert
über eine Weboberfläche („Evidenz-Labor"-Dashboard).

- **Entwicklungsgrundlage:** „Entwicklungsauftrag v2" (Projektname: Auftragsv2), Gearbeitet
  wird in **Sprints**; jeder Sprint wird in `IMPLEMENTATION_LOG.md` dokumentiert.
- **Aktueller Stand:** Sprint 29 abgeschlossen (Stand 05.11.2026), Sprint 30 ist der
  nächste Schritt.

## 2. Verzeichniskarte (wichtigste Pfade)

```
research_agent/
├── main.py                  # CLI-Einstieg
├── orchestrator.py          # Herzstück: Autonome Läufe, Phasen-Pipeline (Planning … Updating)
├── program.py               # Forschungsprogramm / Zielverwaltung
├── work_queue.py            # Arbeitswarteschlange über Neustarts hinweg (Run-Resume)
├── instance_guard.py        # Verhindert Doppel-Instanzen
├── deep_research.py         # Web-Recherche orchestrieren
├── benchmark.py             # Benchmark-Runner gegen Goldstandard (Auftragsv2 §9.2)
├── dataset.py / report.py / report_pdf.py / metrics.py
├── config.py / database.py  # Konfiguration + SQLite-Lauf-DB (readonly-Zugriff vom UI)
├── models.py                # Datenmodelle (Facts, Hypothesen, Zitate …)
├── utf8_logging.py          # Windows-UTF8-Logging-Fix
├── agents/                  # debate.py, devils_advocate.py, roles.py, evidence_scorer.py, base.py
├── memory/                  # Laufzustand / Store
├── llm/                     # LLM-Engine (Multi-LLM), Zulltufe, Timeout-Absicherung
├── meta/                    # Statistik: pooling.py, Gruppen-Metaregression, k-Gate (Sprint 26)
├── research/                # table_extractor.py, vision_table.py (Sprint 29), pypdf-Adapter
├── coverage/ evals/ experiments/
├── tests/                   # 42 Testdateien (pytest)
├── dashboard/               # WebUI: server.py (Live), standalone_server.py (Port 8080),
│                            # templates/ (index.html ~530 Z., style.css, app.js)
data/                        # Lauf-DBs, PDFs, reviews/ (Benchmarks) — nichts davon im Git-Bestand
IMPLEMENTATION_LOG.md        # 26 Sprint-Einträge, 908 Zeilen — Chronik
VERBESSERUNGSBRIEFING.md     # dieses Dokument
```

## 3. Die unantastbaren Verträge (bitte nicht „verbessern", sondern respektieren)

Diese Prinzipien sind bewusste Design-Entscheidungen und dürfen von Vorschlägen NICHT
abgeschwächt werden. Vorschläge, die sie umgehen, sind abzulehnen oder müssen erklären,
warum sie den Vertrag *stärken*.

1. **Verbatim-Kontrakt:** Jede zitierte Tatsache ist Wort für Wort aus der Quelle
   übernommen (mit Seiten-/Abschnittsverweis). Keine Paraphrase in Zitaten. Der Kontrakt
   selbst ist ein Konsfokus: Er darf **erweitert** werden (z. B. um die Bild-Evidenzart,
   siehe Sprint 30), aber seine strenge Wortform bleibt.
2. **Doppel-Lesung bei Vision:** Bei Bild-basierter Tabellenlesung wird parallel in zwei
   unabhängigen Leitungen gelesen (Modell n. Modell, Bitte n. Bitte). Bei Abweichung →
   Status `disputed`. **Nie mitteln.** Das ist die bewusste Antwort auf
   Halluzinationsrisiken von Vision-Modellen.
3. **Adversarial-Prüfung:** Hypothesen werden von einem Devil's-Advocate-Agent angegriffen,
   bevor sie aufgenommen werden (Sprint 25: Aufnahmeprüfung, Konfidenz-Akzente).
4. **Keys/Geheimnisse:** Nie im Chat, nie in Code oder Dateien, nie in Logs. Umgebung:
   Windows, Git Bash, Python-Lokalbetrieb.
5. **Lauf-DBs sind readonly** für das Dashboard/UI; Schemafehler degradiert UI-Teile
   sauber (z. B. Poll-404-Schleife), statt aufzuhängen oder zu crashen.

## 4. Was der Agent derzeit kann (Sprint-Rückbasis)

Chronik komplett in `IMPLEMENTATION_LOG.md`. Kernmeilensteine der letzten Sprints:

| Sprint | Inhalt | Auftrag | Status |
|--------|--------|--------|--------|
| 22 | pypdf-Layout-Adapter: Layout-treue PDF-Tabellen-Extraktion | §2.1 | erledigt |
| 23 | Original-PDF im Effekt-Lauf verdrahtet (Persistenz + Blick-Ontologie) | §2.1 | erledigt |
| 24 | Header-Spaltenkontext im Layout-Scanner (Spaltennamen aus Kontext) | §2.1 | erledigt |
| 25 | Aufnahmeprüfung für Hypothesen (Gates, Konfidenz-Akzente) | §6.3 | erledigt |
| 26 | k-Gate in der Gruppen-Metaregression (Mindestgrößen vor Pooling) | §5.2 | erledigt |
| 27 | Run-Resume: Fortsetzung nach Neustart über die Workspace-DB | §10a | erledigt |
| 28 | Benchmark-Runner + §9.2-Report gegen Goldstandard, Goldstandard-Fundus | §9.2/§9.3 | erledigt |
| 29 | Vision-Tabellenlesung via TUDaGPT (Qwen3-VL) mit Doppel-Lesung, kein Vertrauen auf OCR | §2.1 | erledigt |

**Fixtur-Beweis Sprint 29:** Eine Goldstandard-Tabelle (2) wurde exakt ±SE/CI gelesen
(13/13 Tests grün). Vision-Modell: `qwen3-vl-30b-a3b-instruct-awq`, Endpunkt **TUDaGPT**
(Mehrpositionen-Werkbank), Keys liegen nur in `.env`.

## 5. Was gerade offen ist (= Rohmaterial für Vorschläge)

Diese Punkte sind AUSSCHNITT aus dem Blick des Projekts, aber am wachsen — biete hier
Priorisierung und Methodenvorschläge an:

1. **Sprint 30 (geplant, der nächste große Schritt):** Den Sprint-29-Vision-Reader in den
   Orchestrator **einbinden**: Currently läuft er nur als eigenes Modul + Fixture-Tests;
   er muss an der Pipeline (Extracting-Phase) hängen und der Verbatim-Vertrag muss um
   die Evidenzart „aus Bild gelesen (Vision)" erweitert werden — woabra alle Grenzen des
   Kontrakts respektiert werden (siehe Abschnitt 3).
2. **Goldstandard-Testlauf in Aktion:** Den Benchmark-Runner (Sprint 28) einmal ECHT
   anlaufen lassen, gegen den Fundus, und die Schulleistung statistisch bereihen.
   Deren Ergebnis ist der beste Anhaltspunkt für weiter Priorisierung.
3. **Öffentliche README:** Das GitHub-Repo ist öffentlich, aber eine Darstellung für
   Fremde fehlt (was tut es, was ist öffentlich, was ist geschützt, wie setzt man es auf).
4. **`data/reviews/` (untracked):** Zwei Caffeine-Laufadapterungen — bewusst draußen.
   Entscheide mit, ob/wohin sie legal pousses werden könnten (nach Prüfung auf
   Risiko-Einstufung (Personenbezug) in Texten).
5. **Dashboard-Umfang:** Leitschrank-Layout frisch (05.11.2026); Feinjustierung möglich
   aber NICHT nötig, wenn höhere Achsen bessere Vorschläge liefern.

## 6. Architektur-Fakten, die du beim Beurteilen kennen solltest

- **Orchestrator-Phasen (Pipeline):** `planning → searching → extracting → analyzing →
  hypothesizing → critiquing → synthesizing → updating` (plus `idle`). Die UI zeigt sie
  als nummerierte Messroute (01–08), real werden sie vom `orchestrator.py` gesteuert.
- **Parallelität:** LLM-Engine arbeitet mit Parallelläufen/Timeout (UI zeigt „Parallel
  Task Monitor"). Achtung: Im Standalone-Server (Port 8080) fehlen TEILE der
  API-Endpunkte, die der Liveserver (`server.py`) bietet (z. B. phase timings, active
  tasks) — die UI degradiert sie mit Hinweistext. schnittstellen-Fix wäre ein legitimer
  Verbesserungsvorschlag.
- **Statistik:** `meta/pooling.py` mit k-Gate (Sprint 26), Gruppen-Metaregression,
  Konfidenzbänder; Berichte via `report.py`/`report_pdf.py`; Benchmark via
  `benchmark.py` gegen §9.2-Datengrundfähigkeit.
- **Robustheits-Fix bereits drin:** Windows/PDF-UTF8-Fix (`utf8_logging.py`),
  Lauf-Fragmente (db-wal) nicht im Git-Bestand, UI-Poll degradiert bei 404.
- **Testland:** 42 Testdateien in `research_agent/tests/` (pytest), UTF-8-Fix per
  `export PYTHONIOENCODING=utf-8`.

## 7. Deine Aufgabe: Verbesserungsvorschläge erarbeiten

### 7.1 Vorgehen

1. **Lese zuerst** (in dieser Reihenfolge):
   - `IMPLEMENTATION_LOG.md` (systematisch, alle 26 Sprints)
   - `orchestrator.py`, `llm/engine.py`, `agents/debate.py`, `meta/pooling.py`,
     `research/vision_table.py` (Skim-Stufe für Architekturverständnis)
   - `benchmark.py` + `research/vision_table.py`-Tests
   - `dashboard/` (server.py, standalone_server.py, templates/)
2. **Analysiere** entlang der untenstehenden Achsen.
3. **Liefere einen Vorschlagskatalog** im Format aus 7.3.

### 7.2 Analyse-Achsen (je nach Gewichtigung von dir als Vorschlag)

| Achse | Leitfragen |
|---|---|
| **Architektur** | Orchestrator-Kopplung, Zuschnitt von `llm/engine` auf einzelne Zwei-Leitungen (Doppel-Lesung), Modularisierung, Zyklen, Codewiederholung |
| **Robustheit** | Fehlerbehandlung der LLM-API (Timeout, Retry, Rate-Limits), DB-Schema-Migrationen, Partial-Fehler während des Laufs, Run-Resume-Rundherum |
| **Fachrichtigkeit (Statistik)** | k-Gate-Kriterien, Heterogenitätsdiagnostik (I², Q), Forestplots, Sensitivitätsanalysen |
| **Evidenz-Qualität** | Vision-Doppel-Lesung (Grenzen, Strategien), Verbatim-Erweiterung für Bild-Evidenz, Zitat-Bindung |
| **Performance** | LLM-Kosten (Promptgröße, Caching), Parallelitätsgrad, DB-Zugriffe, Latenz im UI-Poll |
| **Sicherheit** | Secrets, Injections (z. B. HTML in UI-Feldern), Fenster der API, LLM-Ausgabe als Daten |
| **WebUI** | Accessibility, Mobile, Tastatur, Zustandsreflexion (Polling), Sichtbarkeit-Limit der Panels, Endpunkt-Duplikat (standalone vs live server) |
| **Tests** | Abdeckungslücken, Seniority der Fixture-Tests, Benchmark-Runner gegen echte Daten |
| **Prozess** | Commit-Grade, Sprint-Doku, README, Onboarding für Fremde |

### 7.3 Ausgabe-Format (bitte exactly so)

Für jeden Vorschlag ein Block:

```markdown
### Vorschlag N: <Knapper Titel>
- **Achse:** (Architektur / Robustheit / Statistik / Evidenz-Qualität /
  Performance / Sicherheit / WebUI / Tests / Prozess)
- **Priorität:** hoch / mittel / niedrig
- **Aufwand:** klein (≤1 Sprint-Stück) / mittel / groß (meher-Sprint)
- **Betroffene Dateien:** <Pfadliste>
- **Problem:** Was heute schief oder schwach läuft, mit konkretem Verweis auf
  Code-/Logstelle (Zeile/Datei/Commit), sofern möglich.
- **Lösungsidee:** Konkreter Ansatz, wie er umsetzbar wäre — pseudo-umsetzbar,
  ohne den Bestand zu verbiegen.
- **Risiko / Nebenaspekt:** Was bei Änderung noch beachtet werden MUSS (betr.
  Verträge aus Abschnitt 3).
```

Mach aus 20 raw Ideen **8–12 getestete Vorschläge** — lieber wenige gute mit klarem
Workplan als viele Slogans.

### 7.4Besondere Feuerpunkte, die du tief beurteilen solltest

- **Sprint 30-Vorbereitung:** Wie wird der Verbatim-Vertrag um die Bild-Evidenzart
  ERWEITERT? Denke einen Entwurf aus: Datenmodell, Zitatverweise (Bild-PDF,
  Seite, Region), Ausschlusslexikon (was gilt nicht als Verbatim), Blick auf neue Tests.
- **Doppel-Lesung als Architekturprinzip:** Lohnt sie sich generisch — z. B. auch für
  Text-Tabellenlesung (Sprint 22–24-Pfad) oder Web-Auszüge? Koste-Nutzen-Abwägung.
- **Benchmarks ohne „Selbsttauscher":** Sprint 28 misst den Agenten — aber wie verhindern
  wir Overfitting auf den eigenen Goldstandard (das ist die eigentliche Benchmark-Frage)?
- **LLM-Kosten-Governance:** TUDaGPT-Endpunkt, Vision-Aufrufe sind teuer — Budget-
  Regler?teborg­stop per Session? Nachweisbarer Spar-Effekt (Report-artig)?
- **Server-Dualität:** `server.py` vs `standalone_server.py` teilen UI, aber NICHT alle
  Endpunkte — Kandidat für Zusammenführung oder klarer Contract-Test.

### 7.5 Was NICHT als Vorschlag zählt

- Alles, was die Verträge aus Abschnitt 3 abschwächt (z. B. „merai­l­ Mittelung bei
  Zwei-Lesung für(Task-Confidence)").
- Alles, was das Ziel des Projekts verzögert (der Agent soll METANALYSEN produzieren,
  kein generisches Chatprodukt).
- Kosmetische Vorschläge am Dashboard als TOP-Prioritäten (die UI ist frisch, Feintuning
  ist erlaubt, aber nicht die Boss-Sache).
- Vorschläge, die Netz/Cloud-Infrastruktur voraussetzen, die nicht auf dem PC liegt.

## 8. Arbeits-/Commit-Konventionen (falls du am Ende einen Plan schreibst)

- Commits: klein, aussagekräftig, Commit-Fußzeile `Generated with Codebuff` +
  `Co-Authored-By: Codebuff <noreply@codebuff.com>`; Deutsch im Committext.
- Push nach GitHub nur nach Nutzer-Freigabe; Repo: `bauerhartmut/meta-analysis-agent`,
  Branch `master`. Backup-Log der alten Historie: `backups/pre_history_clean.bundle`.
- Tests mit UTF-8-Ausgabe: `export PYTHONIOENCODING=utf-8; python -m pytest
  research_agent/tests/<file>.py -q`.
- Standalone-Server: `python research_agent/dashboard/standalone_server.py` (Port 8080,
  BACKGROUND-Start); Cache-Buster `?v=N` manuell in `index.html` nach CSS/JS-Änderungen
  (Server hält `max-age=300` für Static).

---

**Letzter Stand dieses Briefing-Textes:** 5. November 2026 (nach Sprint 29,
Leitschrank-Dashboard, GitHub-S Cleaning). Wenn sich bis dahin etwas geändert hat,
priorisiere die aktuellen `IMPLEMENTATION_LOG.md`-Einträge über dieser Beschreibung.
