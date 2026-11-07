# Probleme & offene Fragen — Stand Metaanalyse-Agent

**Stand:** 05.11.2026, ~21:45 · Thema: „Does melatonin improve sleep onset latency and sleep quality in adults"
**Grundlage:** Run 1 (Netzlauf 15:12–19:14), Run (b) Harness-Lauf, Fixtures-Benchmark,
Repeat-Lauf Run 2 (seit 19:30, DB `data/research2-…382747.db`, laufend), TODO-Liste
`data/bench/todo_gelernte_fehler.md`, Logs unter `data/runs/`.

---

## 1. Kurzbilanz: erledigt seit dem letzten Stand

| Item | Ergebnis | Fundort |
|---|---|---|
| 1a/1b Poolbarkeits-Gate | Prüft korrekt — Ursache ist die Extraktionstiefe, nicht der Filter | Diagnose im TODO |
| 1c Pooling-Engine | Existiert bereits (`meta/pooling.py`: HKSJ + RVE, `build_analysis`, in `report.py` verdrahtet, Referenztests) | Git-Tree |
| 2a Relevanz-Gate arXiv | 4 Fixes (case-insensitive Kategorien, Legacy-Präfixe, ≥2 Treffer für moderne IDs, `sleep_medicine`-Domänengruppe) | lokal, gitignored |
| 2a Tests | `test_topic_gate_arxiv.py`, 5/5 bestanden, Commit `fc5bcdd`, gepusht | Repo |
| 3a-i Vision-Fallback-Trigger | Trigger feuert jetzt auch bei „Zeilen da, aber 0 poolbar" (SE/CI fehlt komplett); 6 neue Tests, Suite **1024 passed / 2 skipped** | Commit `de4cd5c` |
| 4a Biz-Scanner-Selbstwarnung | 31 Hypothesen : 2 Befunde als korrektes Früh-Signal dokumentiert, nicht stummgestellt | Vergleichsbericht |
| Fixtures-Benchmark | recall 1.0 · precision 0.667 · extraction 1.0 · critical_errors 0 | `data/bench/fixt/` |

---

## 2. Aktuelle Kernprobleme (nach Schwere)

### P1 — Extraktionstiefe blockiert das Pooling (Hauptblocker)

Das Pooling braucht ≥2 Zeilen mit SE oder CI in derselben Outcome-Gruppe. Realität:

| DB | Effektzeilen | mit SE | mit CI | poolbar |
|---|---|---|---|---|
| Run 1 (Melatonin, Netzlauf) | 19 | 1 | 0 | 1 |
| Run 2 (Repeat, Stand 21:45) | 6 (3 einzig.) | 2 | 1 | 1 (β 0.198, se 0.021, ci 0.156–0.239, sleep quality) |
| Run 1 Caffeine ×2 | 8 / 12 | 0 | 0 | 0 |
| Referenz: Exercise-DB | 129 | 55 | 55 | 55 |
| Referenz: Mediterrane-DB | 91 | 38 | 36 | 38 |
| Referenz: Kognition-DB | 127 | 27 | 21 | 27 |

Die Engine **kann** SE/CI sauber ziehen (Referenz-DBs beweisen es). Die
Caffeine/Melatonin-Läufe bleiben da stehen, wo die Zahlen nur in Diagrammen oder
langen Tabellen des PDFs stecken. Run 1 + Run 2 kombinieren hilft nicht: die
Zeilen gehören zu verschiedenen Outcome-Maßen (β vs. HR vs. „other" ohne Wert).

### P2 — Vision-Fallback braucht Original-PDFs, die oft fehlen

Der Fallback rasterisiert **nur Original-PDFs**. Die 62 OA-Volltexte im
Seeder-Puffer sind XML — für diese Quellen kann die Bildlesung nichts lesen.
Da der Trigger erst mit dem Fix von heute Abend überhaupt anspringt, ist der
tatsächliche Effekt von P2 noch **unbeobachtet**: Nach dem Run-2-Ende muss der
Endvergleich zeigen, für wie viele Quellen der Fix überhaupt angenommen hat.

### P3 — Rate-Limits drosseln die Netzabdeckung

OpenAlex/Semantic Scholar sitzen abends dauerhaft im 429/503-Backoff
(20–30 min offen), TUDaGPT teilen sich beide Läufe. Der Repeat-Lauf überlebt
das mit Backoff (LOW Speed), aber Suchbreite und Tempo verlieren spürbar.
Konsequenz: Messergebnisse aus Abend-Läufen unterschätzen die Tages-Performance.

### P4 — Vision-Seitenbudget kann knapp werden

`vision_max_pages_per_run = 12`. Sobald der Trigger-Fix greift und viele Quellen
Fallback-Lesungen beanspruchen, hat das Budget Nachjustierpotenzial —
**nach** geprüften Log-Zahlen entscheiden, nicht blind erhöhen (Kosten).

### P5 — Code-Hygienefund am Rande

In `orchestrator.py` existieren korruptierte Kommentare (Zeilen in
`_vision_fallback_effects`) und die Datei enthielt bis heute Abend fast nur
`CR CR LF`-Zeilenenden (4872/4890), was Tokenizer-Unterschiede zwischen Tools
erzeugte. Seit heute auf LF normalisiert (lokal, gitignored). Konsequenz:
Reiner Kommentar-Textstaub berührt die Logik nicht, sollte aber beim nächsten
Arbeitszug gestutzt werden.

---

## 3. Offene Fragen (Entscheidungsbedarf)

1. **Endvergleich Run 1 vs. Run 2 (3a-ii):** Steigt die Effekt-/CI-Rate so weit,
   dass ≥2 poolbare Zeilen zusammenkommen? Wenn **nein** → nächster Hebel ist
   PDF-Nachschub (P2), nicht ein weiterer Blindlauf.
2. **PDF-Nachschub:** Für welchen Teil der 62 OA-XML-Quellen existiert parallel
   ein Publisher-PDF über Unpaywall/PMC? Ein Skript kann das prüfen und direkt
   laden; danach gezielter Extraktionspass — oder sind die Quellen auch dort
   tabellen-/diagrammlastig?
3. **Merge oder Ersetzen beim Vision-Fallback:** Heute ersetzen Vision-Zeilen
   die nutzlosen Text-Zeilen (Semantik wie der `not rows`-Pfad). Sollen wir die
   Text-Zeilen zusätzlich behalten (Dokumentation, nicht poolbar) — oder bleibt
   es beim Ersetzen (aktuell)?
4. **Meta-Ende der Benchmark-DBs:** Exercise/Mediterrane/Kognition tragen 21–55
   poolbare Zeilen. Sollen wir dort **sofort** vollständige Reports inkl. Pooling
   erzeugen, um die Engine end-to-end zu prüfen — ohne Melatonin?
5. **Referenz-Reviews für den Benchmark:** 20–30 echte publizierte Metaanalysen
   als Goldstandard bleiben Einkaufsaufgabe. Wann und mit welchem Budget?
6. **Budget P4:** Vision-Seitenbudget erhöhen — nur wenn Log-Daten zeigen, dass
   12 Seiten ein echtes Limit für laufende Lesungen sind.

---

## 4. Empfohlene Reihenfolge

1. **Jetzt das laufende Run 2 auslaufen lassen** — kein Abbruch, kein zweiter
   Netzlauf gleichzeitig (Rate-Limits).
2. **Nach dem Ende:** Endvergleich (Effekt-/CI-Rate, `eval_run_results.py` auf
   `research2-…db`) + prüfen, ob der Report einen gepoolten Effekt hat.
3. **Danach entscheiden:** poolbar? → fertig. Nicht poolbar? → PDF-Nachschub
   (Frage 2), gezielter Extraktionspass, dann neuer Lauf — nicht vor dem Fix
   blind einen dritten Melatonin-Lauf.
4. **Parallel ohne Risiko:** Meta-Reports aus den befüllten DBs erzeugen (Frage 4).

---

## 5. Artefakte in diesem Bericht

- TODO mit allen Items: `data/bench/todo_gelernte_fehler.md`
- Vergleichsbericht Run 1: `data/bench/lauf_vergleich_20261105.md`
- Zwischenstand Run 2: `data/bench/net_run2_zwischenstand.md`
- Logs: `data/runs/melatonin_net_run{1,2}.log`, `melatonin_harness_run1.log`
- Reports als PDF: `data/reports/20261105-18{13,14}-*.pdf`
- Fixtures-Benchmark: `data/bench/fixt/benchmark_smoke.json`
