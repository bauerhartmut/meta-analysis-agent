# Auftrag: Quantitative Metaanalysen aus der Literatur ermöglichen

**Für:** einen Coding-Agenten, der dieses Repository bearbeitet.
**Verwandt:** [`improvement_prompts.md`](improvement_prompts.md) (Pakete A–O, gleicher Stil). Diese Datei ist eigenständig und setzt nichts davon voraus.

---

## 0. Ziel

Der Agent soll am Ende einen **gepoolten Effektschätzer aus publizierten Studien** liefern können – nicht aus seinen eigenen Simulationen, sondern aus der Literatur: mehrere Studien zu derselben Frage, jede mit Effektstärke und Präzision, kombiniert zu einem Schätzer mit Konfidenzintervall, sichtbarer Heterogenität, Subgruppen- und Publikationsbias-Prüfung, im Abschlussbericht reproduzierbar belegt.

Heute kann er das **nicht**. Er sammelt Quellen, extrahiert Fakten mit wörtlicher Belegstelle und poolt ausschließlich seine eigenen Experimente. Was fehlt, ist nicht die Rechenkunst – die ist zu ~60 % vorhanden – sondern der **strukturierte Weg von einer Zahl in einem Paper in eine Tabelle**.

**Definition von „fertig"** (prüfbar, siehe § 4): Aus einem echten Themenlauf entsteht eine Tabelle mit mindestens 5 Studien-Effekten zum selben Outcome, ein Random-Effects-Pooling mit τ², 95 %-KI und Prediction Interval, eine Publikationsbias-Prüfung und ein Berichtsabschnitt mit Forest-Tabelle – und dieselbe Datenbank ergibt beim erneuten Lauf Zeichen für Zeichen dasselbe Ergebnis.

**Was diese Datei nicht verlangt:** keinen Anspruch auf ein publizierbares *systematic review* (keine PROSPERO-Registrierung, keine menschliche Doppelcodierung, keine Risk-of-Bias-Instrumente). Ein solches Review ist mit einem Agenten nicht erreichbar, siehe § 5.

---

## 1. Ist-Stand (verifiziert am 27.10.2026)

Vor dem Start **nachprüfen** – der Code bewegt sich, Zahlen können veraltet sein:

```bash
python -m pytest research_agent/tests/ -q
sqlite3 data/research.db "SELECT COUNT(*) FROM facts; SELECT COUNT(*) FROM facts WHERE quote_start >= 0;"
sqlite3 data/research.db "SELECT COUNT(*) FROM sources WHERE author <> '';"
sqlite3 data/research.db "SELECT COUNT(*) FROM source_texts WHERE kind <> 'abstract';"
sqlite3 data/research.db "SELECT COUNT(*) FROM evidence;"
```

Themenläufe schreiben wegen `DATABASE_PER_TOPIC=1` in `data/research-<slug>-<hash6>.db`, nicht in `data/research.db`.

### Was schon existiert und wiederverwendet werden muss

| Baustein | Ort | Zustand |
|---|---|---|
| Fakten **mit Belegstelle** | `facts`-Tabelle: `content`, `confidence`, `quote`, `quote_start/end`, `quote_exact`, `source_text_id`, `section`, `page` (`research_agent/database.py:500`) | funktioniert, ist die stärkste Eigenschaft des Systems |
| Dataclass `Fact` | `research_agent/models.py:92` | erweitern, nicht duplizieren |
| Volltext mit Abschnitten und Seiten | `source_texts`: `sections` (JSON), `page_offsets` (JSON), `path` (`research_agent/database.py:346`) | Grundlage für gezielte Ergebnistext-Auswahl |
| Abschnitts- und Zitatlogik | `research_agent/research/fulltext.py`: `split_sections()` (L119), `locate_quote()` (L287), `select_text()` (L356, Ergebnisse vor Einleitung, Referenzen nie) | direkt wiederverwenden |
| **Pooling** (inverse Varianz, I²) | `research_agent/experiments/synthesis.py:81` `pool()`; genutzt nur in `research_agent/report.py:980` | Vorbild und Testmuster, **nicht umbauen** (Simulationsverhalten + Tests hängen daran) |
| Known-Answer-Validierung | `research_agent/experiments/validity.py` (Nullrate, Effektskalierung, Determinismus, analytische Anker) | Muster für die Statistik-Validierung übernehmen |
| Arbeitswarteschlange | `research_agent/work_queue.py`, Tabelle `work_items`, Handler je `kind` (`full_text`, `hypothesis_evidence`, `citation`, `simulation`) | der natürliche Ort für neue Extraktionsarbeit |
| Studien-Metadaten | `SearchResult.author/year` (`research_agent/research/search.py:196`), übernommen in `research_agent/research/sources.py:83` | **inzwischen gefüllt**; nur alte Bestände sind leer |
| Berichtsstruktur | `research_agent/report.py` (LLM-frei, deterministisch), BibTeX-Export daneben | hier kommt der neue Abschnitt hin |

### Was fehlt (die eigentliche Lücke)

1. **Keine Effektstärke als Zahl.** Kein Feld für Effekt, Standardfehler, KI, `n`, Design. Der Extraktions-Prompt (`research_agent/memory/store.py:350`) fordert genau drei Felder: `content`, `quote`, `confidence`. „h² = 0,80 bei N = 11.000" landet als Prosa im `content` und ist damit nicht poolbar.
2. **Keine belastbare Studien-Identität.** Autoren/Jahr sind im Parser gefixt, ein `doi`-Feld gibt es aber nicht – DOI wird nur aus der URL abgeleitet (`research_agent/research/engine.py:137`). Für Forest-Plot-Zeilen, Duplikat-Erkennung (dieselbe Kohorte in mehreren Papers) und stabile Zitationsschlüssel fehlt die Spalte.
3. **Keine Random-Effects-Statistik.** `pool()` ist ein Fixed-Effect-Modell mit I²: kein τ² (DL/REML), kein Prediction Interval, keine HKSJ-Korrektur, keine Subgruppen/Meta-Regression, kein Leave-one-out, kein Egger/Begg, keine Grafik.
4. **Kein Review-Gerüst.** Kein PICO, keine Ein-/Ausschlusskriterien, kein Screening mit Ausschlussgründen, keine PRISMA-Zählungen, kein Risk-of-Bias.
5. **Keine Zahlenverifikation.** Ein wörtlicher Satz beweist, dass die Stelle existiert, nicht dass die Zahl richtig abgelesen wurde (SE vs. SD, 95 % vs. 90 %-KI, Einheiten). Es gibt keine Doppel-Extraktion und keine Plausibilitätsprüfung.

**Nicht anfassen:** dass `neutral`-Verdikte keine `evidence`-Zeile bekommen (`research_agent/memory/store.py:~1006`), ist eine **dokumentierte, absichtliche Entscheidung**. Die Metaanalyse hängt sich nicht an `evidence`, sie bekommt eine eigene Tabelle. Wer die Zeile trotzdem speichern will, macht das als eigenes Vorhaben mit eigener Begründung.

---

## 2. Arbeitspakete

### M1 — Effektstärken strukturiert extrahieren (Kern, ohne das geht nichts)

**Warum.** Ohne maschinenlesbares Tripel (Effekt, Präzision, Study-ID) gibt es kein Pooling, nur Nacherzählen.

**Umsetzung.**
1. Neue Tabelle `study_effects` (Migration im Stil von `database.py:500`, `ALTER`/`CREATE` mit `except sqlite3.OperationalError: pass`):

```sql
CREATE TABLE IF NOT EXISTS study_effects (
    id             TEXT PRIMARY KEY,
    source_id      TEXT DEFAULT '',     -- sources.id
    hypothesis_id  TEXT DEFAULT '',     -- optionale Bindung
    outcome        TEXT DEFAULT '',     -- z. B. 'Kognition'
    comparison     TEXT DEFAULT '',      -- Gruppe/Kontrast, z. B. 'PGT vs. IVF'
    effect_type    TEXT DEFAULT '',      -- smd|r|or|rr|hr|beta|mean_diff|heritability|other
    effect         REAL,                 -- Punktschätzer auf der Skala von effect_type
    se             REAL,                 -- Standardfehler (bevorzugt); NULL = nicht poolbar
    ci_low         REAL, ci_high REAL,
    ci_level       REAL DEFAULT 0.95,    -- berichtetes Niveau, NICHT annehmen
    n              INTEGER,              -- Stichprobe
    events         INTEGER,              -- optional, für or/rr
    design         TEXT DEFAULT '',      -- cohort|rct|twin|gwas|cross_sectional|...
    population     TEXT DEFAULT '',
    moderators     TEXT DEFAULT '{}',    -- JSON: Alter, Geschlecht, Herkunft ...
    direction      TEXT DEFAULT '',      -- was "größer" bedeutet (Vorzeichen!)
    unit           TEXT DEFAULT '',
    quote          TEXT DEFAULT '',      -- wörtliche Stelle, wie bei facts
    quote_start    INTEGER DEFAULT -1, quote_end INTEGER DEFAULT -1,
    source_text_id TEXT DEFAULT '', section TEXT DEFAULT '', page INTEGER DEFAULT -1,
    extractor      TEXT DEFAULT '',      -- Prompt-/Modellversion
    extraction_pass INTEGER DEFAULT 1,   -- 1 oder 2 (M6)
    created_at     TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_study_effects_source ON study_effects(source_id);
```

2. Neue Dataclass `StudyEffect` in `research_agent/models.py`, analog zu `Fact`.
3. Neue Funktion `extract_effect_sizes(...)` in `research_agent/memory/store.py` (oder neuem Modul `research_agent/meta/extraction.py`), Signatur analog `extract_facts`:

```python
async def extract_effect_sizes(self, text, source_id, topic="",
                               sections=None, page_offsets=None,
                               source_text_id="") -> List[StudyEffect]:
```

4. Prompt-Regeln, hart formuliert:
   - **Nur Zahlen, die im Text stehen.** Kein Schätzen, kein Ableiten, kein „etwa". Fehlt der Standardfehler **und** das KI, wird `se` auf `NULL` gesetzt und der Effekt ist nicht poolbar – lieber eine Zeile weniger als eine erfundene Präzision.
   - **`ci_level` immer mitlesen.** Aus einem KI darf `se` nur bei bekanntem Niveau berechnet werden: `se = (ci_high - ci_low) / (2 * 1.96)` **nur** bei `ci_level = 0.95` (allgemein `2 * z(1 - (1-ci_level)/2)`). Ein 90 %-KI blind als 95 % zu lesen ist ein Faktor 1,22 im Standardfehler.
   - **Jeder Effekt braucht einen wörtlichen Satz.** Der Satz wird mit `locate_quote()` im Quellentext gesucht; nicht gefunden → Zeile bleibt, `quote_start = -1`, und die Zeile wird im Bericht als unbelegt gezählt (dieselbe Regel wie bei `facts`).
   - **Vollständigkeit vorliegend:** pro Studie so viele Outcomes/Kontraste wie berichtet, nicht nur den auffälligsten.
   - `direction` ist Pflicht: „höher ist besser" vs. „höher ist schlechter". Ohne Vorzeichenkonvention ist ein gepoolter Effekt nicht interpretierbar.
5. Prompt-Text über `select_text(body, topic.split(), budget, sections)` schneiden, damit Ergebnisteile ins Kontextfenster kommen statt des Front Matters.

**Scope/Grenzen.**
- Erlaubt: `research_agent/database.py`, `research_agent/models.py`, `research_agent/memory/store.py`, neu `research_agent/meta/` (`__init__.py`, `extraction.py`), `research_agent/tests/test_meta_extraction.py`, `requirements.txt` **nur** wenn eine Abhängigkeit wirklich nötig ist (siehe § 6).
- Nicht anfassen: `research_agent/experiments/*` (Simulationssemantik), `research_agent/report.py` (erst in M5), `research_agent/agents/*`.

**Wie prüfen.**
- Offline-Tests mit gefälschtem LLM, analog `tests/test_fulltext.py`: ein Paper mit bekanntem Ergebnisabschnitt → erwartete Zeilen mit korrektem `effect`, `se`, `n`, `ci_level`; Paper ohne SE/KI → `se IS NULL` und „nicht poolbar"-Flag; erfundenes Zitat → `quote_start = -1`; 90 %-KI → `se` korrekt umgerechnet.
- Nebenbefund dokumentieren: Wie viele Quellen des echten Bestands haben überhaupt einen Abschnitt, in dem Effektgrößen stehen? (Erwartung: deutlich weniger als die Zahl der Quellen – das ist selbst ein Befund und gehört in den Bericht.)

### M2 — Studien-Identität und Ergebnisse statt Titelseite

**Warum.** Ohne `doi`, Autor, Jahr und Design ist jede Forest-Plot-Zeile anonym; die Duplikat-Erkennung derselben Kohorte ist unmöglich.

**Umsetzung.**
1. Spalte `doi TEXT DEFAULT ''` auf `sources`, gefüllt über die vorhandene Extraktion `doi_from_url` (`research_agent/research/engine.py:137`, `research_agent/research/extractor.py:90`); Backfill-Skript für Bestands-Datenbanken (DOI aus `url`, sonst `''`).
2. Beim Pooling Studien ohne `doi`/`author`/`year` zulassen, aber im Bericht als „nicht identifizierbar" kennzeichnen und **nicht** stillschweigend zusammenfassen.
3. Prüfen, ob `sources.publication_date` aus Bestandsdaten nachfüllbar ist (OpenAlex/Crossref-Nachschlag per DOI) – nur wenn ohne API-Schlüssel und mit Circuit Breaker aus `search.py` möglich.

**Scope/Grenzen.** Erlaubt: `database.py`, `research/sources.py`, `research/engine.py`, `scripts/` (Backfill), Tests. Nicht anfassen: `search.py`-Providerlogik (in PAKET A/J gerade erst saniert).

**Wie prüfen.** `SELECT COUNT(*) FROM sources WHERE doi <> ''` vor/nach dem Backfill in einer Kopie einer Themedatenbank; Test: DOI aus `https://doi.org/10.1038/ng.3285` und aus `10.1038/ng.3285` identisch; zwei Papers derselben Kohorte (gleiche DOI, verschiedene URLs) ergeben **eine** Studienzeile im Pooling.

### M3 — Random-Effects-Engine mit Validierung

**Warum.** `pool()` ist Fixed-Effect. Zwischen Feldstudien ist das die falsche Annahme, und ohne τ² ist die Aussage „gepoolt" nicht belastbar.

**Umsetzung.** Neues Modul `research_agent/meta/pooling.py`, LLM-frei und aus gespeicherten Zahlen reproduzierbar (wie `experiments/synthesis.py`):

- **Effektkonversionen** in eine gemeinsame Skala, jede Konversion als eigene, getestete Funktion: `r → Fisher-z`, `d → Hedges' g` (kleine Stichprobenkorrektur), `or/rr → ln`, `beta → (beta, se)` falls `se` berichtet. Konversion nur mit bekanntem `n`; sonst Zeile überspringen und zählen.
- **Random Effects**: τ² nach DerSimonian–Laird und REML (iterativ, Konvergenz dokumentieren), Gewichte `w = 1/(v + τ²)`, gepoolter Effekt, 95 %-KI; zusätzlich **Hartung–Knapp–Sidak**-Variante mit `t`-Verteilung (`k-1` Freiheitsgrade) als Standard, weil sie bei kleinen `k` korrekt überdeckt.
- **Heterogenität**: `Q`, `df`, `p(Q)`, `I²`, `H²`, **τ** (nicht nur τ²: τ ist auf der Effektskala lesbar).
- **Prediction Interval** (`t` mit `k-2` df): was ein *künftiges* vergleichbares Ergebnis wäre. Bei erheblicher Heterogenität ist das die ehrlichere Zahl als das KI des Mittelwerts.
- **Fixed-Effect-Spalte zum Vergleich** daneben, nicht statt.
- **Sperren, die greifen müssen**: Pooling erst ab `k >= 2`; verschiedene `effect_type` ohne definierte Konversion → ablehnen statt mischen; `k < 10` ⇒ Publikationsbias-Tests nur mit ausdrücklichem Unsicherheitshinweis; Effekt ohne `se`/KI → ausgeschlossen und mit Anzahl genannt.

**Validierung (Known-Answer, in `research_agent/tests/test_meta_pooling.py`).**
- **Analytische Anker, geschlossen lösbar**: `k = 2` mit gleichen Varianzen ⇒ FE = RE = arithmetisches Mittel; `τ² = 0` ⇒ RE identisch zu FE; Vorzeichenumkehr aller Effekte ⇒ gepoolter Effekt mit umgekehrtem Vorzeichen, gleiches KI.
- **Recovery per Simulation**: Effekte aus bekanntem Modell mit bekanntem τ² erzeugen, über viele Zufallsziehungen schätzen ⇒ `τ²`-Schätzer um den wahren Wert zentriert, **Überdeckung des 95 %-KI ≈ 95 %** (Toleranz wie in `experiments/validity.py`; mit `k` klein und HKSJ muss die Überdeckung besser sein als mit `z`).
- **Determinismus**: fester Seed ⇒ identische Zahlen; dieselbe DB zweimal ⇒ byte-identischer Berichtstext.
- **Veröffentlichtes Beispiel als Anker** (wenn beschaffbar): Datensatz mit belegtem veröffentlichtem Ergebnis; die erwarteten Werte **aus der Quelle zitieren und die Quelle im Test als Kommentar nennen** – nicht aus dem Gedächtnis einsetzen. Passt kein Beispiel, bei den Simulationsankern bleiben und das als Limitation notieren.

**Scope/Grenzen.** Erlaubt: neu `research_agent/meta/pooling.py`, Tests, `research_agent/meta/__init__.py`. **Nicht** `research_agent/experiments/synthesis.py` ändern – dessen Semantik (Experimente, Verdikte, Replikationsquote) bleibt unverändert.

**Abhängigkeiten.** `numpy`/`scipy` sind deklariert (`requirements.txt`). Wenn `scipy.optimize` für REML reicht: gut. Eine neue Statistikbibliothek nur nach Freigabe (§ 6).

### M4 — Heterogenität sichtbar machen: Subgruppen, Leave-one-out, Publikationsbias, Forest-Tabelle

**Warum.** Ein gepoolter Wert bei I² > 70 % ist irreführend, wenn niemand die Streuung sieht.

**Umsetzung.**
- **Subgruppen-Analyse** entlang `moderators` (z. B. Design, Population) mit Between-Group-`Q` (`Q_between`, `df = g-1`, p-Wert). Meta-Regression (gewichtet) optional, nur mit `k >= 10`.
- **Leave-one-out**: gepoolter Effekt ohne jede einzelne Studie; berichtet wird die Spanne, nicht nur ein Wert („fällt der Effekt, wenn man eine Studie entfernt?").
- **Publikationsbias**: Egger-Regression (gewichtete Regression des standardisierten Effekts auf die Präzision), optional Begg-Rangkorrelation; Trim-and-Fill nur als ausdrücklich gekennzeichneter Zusatz, weil es stark modellabhängig ist.
- **Forest-Tabelle** als Markdown (Studie, Jahr, Effekt [KI], Gewicht %, plus gepoolte Zeile, I², τ, PI). **Funnel-Plot-Daten** als Tabelle mitliefern.
- **Grafik**: `matplotlib` ist **nicht** in `requirements.txt`. Entweder den Forest Plot als **SVG von Hand** erzeugen (keine neue Abhängigkeit, passt zum Markdown-Bericht) oder vorher fragen. Kein stilles Hinzufügen einer Abhängigkeit.

**Wie prüfen.** Test mit synthetischen Subgruppen (zwei Gruppen, bekannter Unterschied) ⇒ `Q_between` schlägt an; Leave-one-out lässt den Effekt in der erwarteten Studie kippen; Egger bei künstlich asymmetrischem Funnel signifikant, bei symmetrischem nicht; Forest-Tabelle enthält für jede gepoolte Zeile `k` sichtbar.

### M5 — Review-Gerüst und Berichtsabschnitt

**Warum.** Ohne Ein-/Ausschlusskriterien und Zählungen ist „ich habe 12 Studien gepoolt" keine prüfbare Aussage. Und ohne Einbindung in Lauf und Bericht bleibt die Tabelle unsichtbar.

**Umsetzung.**
1. **Neuer `work_items`-Kind `effect_extraction`** in `research_agent/work_queue.py`, geseedet wie `citation`: Quellen über der Relevanzschwelle **mit echtem Dokumenttext** (nicht `kind = 'abstract'`) und ohne `study_effects`-Zeile. Damit füllt der bestehende Rückstandsmechanismus die neue Tabelle über die Laufzeit, statt einen zweiten Extraktionspfad zu bauen. Priorität nach dem bestehenden Schema (Wert × Unsicherheit / Kosten). Fehlschläge wie gehabt nach `MAX_ATTEMPTS` blockieren.
2. **Protokoll** als versioniertes Artefakt (`data/reviews/<slug>/protocol.md`, LLM-erzeugt, aber als Datei eingefroren): PICO-Frage, Ein-/Ausschlusskriterien, primäres Outcome, geplante Effektskala, Datum. Vor dem Pooling geschrieben, danach nicht mehr geändert.
3. **Screening** (klein halten, aber vorhanden): Tabelle `screening(source_id, decision, reason, decided_by, created_at)` mit `include`/`exclude`. Ohne Screening gibt es keinen Ausschlussgrund – und damit keine PRISMA-Zahlen.
4. **Berichtsabschnitt `## Metaanalyse`** in `research_agent/report.py`, LLM-frei und deterministisch:
   - Zählungen im PRISMA-Stil, aber **nur, was die Datenbank beweisen kann**: gefunden / bewertet / ausgeschlossen (mit Gründen) / eingeschlossen / mit nutzbarer Effektgröße / gepoolt.
   - Forest-Tabelle, gepoolter Effekt mit KI, PI, I², τ, Subgruppen, Leave-one-out, Egger.
   - Ausdrücklich: Zahl der Studien, die **keinen** poolbaren Effekt lieferten, und warum (kein `se`, kein KI, Effekt nicht im Ergebnistext gefunden).
   - Nur bei `k >= 2` „gepoolt" schreiben; sonst tabellarisch und das Wort „gepoolt" vermeiden.
5. `.env`/Config-Schalter `META_MIN_STUDIES` (Standard 2) und `META_EFFECTS_PER_CYCLE` (Standard 1) im Stil der bestehenden Schalter; README-Abschnitt ergänzen.

**Scope/Grenzen.** Erlaubt: `report.py`, `work_queue.py`, `orchestrator.py` (nur die Stelle, die Work-Items abarbeitet), `config.py`, `.env`, `README.md`, Tests. Nicht anfassen: `experiments/*`, `agents/*`, `dashboard/*` (eine Kachel kommt erst, wenn Zahlen da sind).

**Wie prüfen.** Test: leere `study_effects` ⇒ Abschnitt sagt klar „keine Metaanalyse möglich (k = 0)" statt zu schweigen; eine einzelne Studie ⇒ tabellarisch, **kein** gepoolter Wert; zwei Studien mit KI ⇒ gepoolte Zeile mit korrekter Arithmetik; Ausschlussgründe erscheinen in den Zählungen. Echter Lauf: `work_items` sinkt, `study_effects` wächst, Bericht enthält den Abschnitt mit denselben Zahlen wie die DB.

### M6 — Zahlenverifikation (Doppel-Extraktion)

**Warum.** Ein Zitat beweist die Stelle, nicht das Ablesen. Metaanalysen scheitern praktisch an falsch extrahierten Zahlen, nicht an der Formel.

**Umsetzung.**
- **Zwei Pässe** pro Quelle mit unterschiedlicher Temperatur oder Reihenfolge der Felder, gespeichert mit `extraction_pass = 1|2`.
- **Vergleich** in einer Funktion `compare_extraction_passes(source_id)` über die Schlüsselfelder (`effect`, `se`, `ci_level`, `n`, `effect_type`), mit relativer Toleranz (z. B. 1 % auf `effect`, 5 % auf `se`).
- **Konflikte sind nicht auflösbar durch Mitteln.** Die Zeile wird als `disputed` markiert und ist **nicht poolbar**, bis ein dritter Pass oder ein Mensch entscheidet. Der Bericht nennt die Konfliktquote – das ist eine Qualitätsaussage, keine Nebensache.
- **Plausibilitätsgates** vor dem Speichern, jede Ablehnung mit Grund protokolliert: `|r| <= 1`; `or/rr/hr > 0`; KI muss den Punktschätzer enthalten (`ci_low <= effect <= ci_high`); `n > 0` wenn gesetzt; `ci_level` in `(0.5, 1.0)`; `se > 0`.

**Wie prüfen.** Test: zwei Pässe mit absichtlich abweichendem `effect` ⇒ `disputed`, nicht gepoolt; identische Pässe ⇒ poolbar; unbemerkte KI, die den Schätzer nicht enthält ⇒ abgelehnt mit Grund; Konfliktquote erscheint im Bericht.

---

## 3. Reihenfolge, Abhängigkeiten, Parallelität

| Paket | Hängt ab von | Parallel möglich mit |
|---|---|---|
| M1 Effektstärken-Schema + Extraktion | – | M2, M4 (nur Logik ohne Bericht) |
| M2 Studien-Identität (`doi`, Backfill) | – | M1, M4 |
| M3 Pooling-Engine + Validierung | M1 (Datenmodell) | M2, M4 |
| M4 Subgruppen/Bias/Forest | M3 | – |
| M5 Work-Item + Bericht | M1, M3, M6 (Konfliktquote) | – |
| M6 Doppel-Extraktion | M1 | M2 parallel |

**Empfehlung:** M1 + M2 sofort parallel (dateidiskunkt bis auf `database.py` – Migrationen **hintereinander** committen, nicht gleichzeitig im selben File arbeiten). Danach M3, dann M6, dann M4, zuletzt M5, weil M5 alles zusammenführt. M3/M4 sind reine Rechenkerne und können ohne laufenden Agenten entwickelt und vollständig getestet werden – das ist die risikoärmste Arbeit und sollte zuerst grün sein.

---

## 4. Definition of Done

1. `python -m pytest research_agent/tests/ -v` ist grün, **einschließlich** der neuen Tests `test_meta_extraction.py`, `test_meta_pooling.py`, `test_meta_screening.py`, `test_meta_report.py`. Kein Test wird abgeschwächt, keine Assertion auskommentiert.
2. Ein echter Lauf auf einem Thema erzeugt ≥ 5 `study_effects` zum selben Outcome, davon ≥ 2 mit `se` oder KI, und der Bericht enthält `## Metaanalyse` mit Forest-Tabelle, gepooltem Effekt, KI, PI, I², τ und Publikationsbias-Prüfung.
3. **Reproduzierbarkeit:** dieselbe Datenbank zweimal gepoolt ⇒ identischer Berichtstext (LLM-freier Pfad). Ein Neustart mitten im Lauf verliert keine `work_items` und keine `study_effects`.
4. **Überdeckungstest grün:** simuliertes 95 %-KI überdeckt den wahren gepoolten Effekt in ≈ 95 % der Wiederholungen.
5. **Ehrlichkeitstest:** hat ein Thema keine poolbaren Effekte, schreibt der Bericht das ausdrücklich (Zahl der Quellen, Grund der Ausschlüsse) – statt eine Zahl zu erfinden oder den Abschnitt wegzulassen.
6. `requirements.txt` ist unverändert, außer eine Abhängigkeit wurde vorher ausdrücklich freigegeben (§ 6).
7. README-Abschnitt „Metaanalyse aus Literatur" mit den Schaltern und den **ungeschönten Grenzen** (Abschnitt 5).

---

## 5. Grenzen, die auch nach der Umsetzung gelten

Diese Punkte gehören in den Berichtstext, nicht ins Kleingedruckte:

- **Open-Access-Verzerrung.** Ohne institutionellen Volltextzugang ist der Korpus OA-lastig; Verlagsartikel bleiben Abstract, und im Abstract stehen selten Standardfehler. Eine Metaanalyse über diesen Korpus ist **systematisch nicht repräsentativ** – und das ist selbst eine Publikationsbias-Quelle, die die Egger-Prüfung nicht sieht.
- **`k` bleibt klein.** Ein autonomer Lauf findet für eine enge Frage selten 10 vergleichbare Studien mit nutzbarer Effektgröße. Unter `k = 10` sind Funnel-Plot und Egger schwach; das muss im Bericht stehen.
- **Gerätefehler werden nicht korrigiert.** Kein Risk-of-Bias-Instrument (RoB 2, ROBINS-I), keine GRADE-Bewertung. „Alle Studien eingeschlossen" heißt hier nicht „alle Studien geprüft".
- **Keine Registrierung, kein Peer Review.** Das Ergebnis ist eine quantitative Synthese, kein *systematic review*. Die Bezeichnung „Metaanalyse" ist nur mit den ausgewiesenen Einschränkungen zulässig.
- **Zahlen bleiben Modellablesung.** Die Doppel-Extraktion senkt, sie beseitigt den Fehler nicht. Für eine Publikation bleibt menschliche Doppelcodierung Pflicht.
- **Keine Kausalaussage.** Gepoolte Beobachtungsdaten bleiben Beobachtungsdaten; die Konfidenzheuristik des Systems darf den gepoolten Schätzer nicht überschreiben.

---

## 6. Entscheidungen, die der Mensch treffen muss

1. **Effektskala.** Standardisiert (SMD/Fisher-z, vergleichbar über Studien) oder roh (IQ-Punkte, %-Punkte, interpretierbarer)? Standardisiert ist vergleichbarer, roh ist lesbarer. Empfehlung: beides speichern (roh im `unit`-Feld dokumentiert), poolen auf der standardisierten Skala.
2. **Neue Abhängigkeit.** Braucht es `matplotlib` (Forest/Funnel-Grafik) oder `statsmodels` (Meta-Regression)? Ohne Freigabe: SVG/ASCII von Hand + `numpy`/`scipy`. `R`/`metafor` ist hier **nicht installiert** und sollte nicht vorausgesetzt werden.
3. **Screening-Tiefe.** Reicht eine Einschlussentscheidung pro Quelle, oder braucht es Volltext-Screening mit zwei unabhängigen Entscheidungen? Mehr Tiefe heißt mehr LLM-Kosten pro Quelle.
4. **Bestands-Datenbanken.** Werden alte Themen-Datenbanken per Backfill nachgezogen (DOIs, Metadaten) oder nur neue Läufe ab jetzt? Backfill kostet API-Zeit und kann fehlschlagen.
5. **`neutral`-Rückkopplung.** Bleibt sie wie dokumentiert (keine Zeile)? Wenn nicht, ist das ein eigenes Paket mit eigener Messung – nicht als Nebeneffekt dieses Auftrags.

---

## 7. Nachtrag (31.10.2026): Maschinelle RoB- und GRADE-Bewertung freigegeben

Der Nutzer hat die ergänzenden Entscheidungen getroffen:

1. **Risk-of-Bias und GRADE werden maschinell bewertet.** Die Grenze aus § 5
   („kein Risk-of-Bias-Instrument") ist als Nutzer-Entscheidung aufgehoben: Der
   Agent bewertet die Domänen selbst (Module `meta/risk_of_bias.py`,`meta/grade.py`).
   Bind der Freigabe bleibt: Jedes Rating braucht eine wörtliche, im
   Volltext verifizierte Belegstelle; ohne Beleg gilt `unclear`, niemals eine
   Schätzung. Ausgänge sind überall mit `maschinell` gekennzeichnet. Disputed
   Rating-Doppel-Pässe werden markiert statt gemittelt.
2. **OA-Korpus akzeptiert.** Die Open-Access-Verzerrung aus § 5 bleibt als
   dokumentierter Bias im Berichtstext stehen; auf Verlags-Volltexte wird
   verzichtet, mit dem bestehenden Korpus gearbeitet.
3. Berichtsabschnitt erweitert: `### Risk-of-Bias (maschinell,
   quote-belegt)` und `### Evidenzqualität (GRADE, maschinell)` - jede
   Abwertung nennt ihre ausführlich begründete Regel; regelnarmenmentiert
   (deterministisch) berechnet. Dashboard-Tab
   „Metaanalyse" zeigt dieselben Zahlen aus der Datenbank.
