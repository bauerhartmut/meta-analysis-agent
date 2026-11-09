# Übergabe: Stand der Technik und offene inhaltliche Punkte

Stand: 2026-11-09, abends. Kurzfassung für den nächsten Einstieg. Alles
Technische ist committet und gepusht; die inhaltliche Arbeit hängt an einer
Lieferung, die noch nicht da ist.

## 1. Wo die Technik steht

| Bereich | Stand | Beleg |
|---|---|---|
| Metaanalyse-Endpunkt | 14 Gruppen, RVE und RVE-RE über echtes HTTP geprüft | `scripts/pruefe_metaanalysis_api.py`, `stand_20261109.md` |
| Meta-Karte im Browser | rendert Zeilenbasis, RVE, RVE-RE; visuell bestätigt | `browser_meta_20261109.md` |
| Fehler im Endpunkt | defekte Zieldefinition → HTTP 500, im Browser sichtbar | `9687021`, `a0f1802`, `browser_meta_fehler_20261109.md` |
| Netzwerkfehler in der Karte | sichtbar, per `fetch`-Mock im Browser geprüft | `210fb34`, `465c09f` |
| Betrieb: zwei Themen | 14 → 2 → 0 Gruppen, Filterung über `review_targets` | `betriebstest_20261109.md` |
| Betrieb: Lesen und Schreiben | 200 Schreibungen neben 200 GETs, 0 Fehler, kein Lock | dito |
| Fernleihliste | 25 Positionen, 20 bestellfähig, druckfertig | `fernleihliste_20261109.md`/`.txt` |
| Extraktionsformular | Register, Crossover-Pfad, Dedup gegen S1–S3, Prüfskript | `extraktionsformular_20261109.md` |
| IP-Frage | Vorlage mit vier Alternativen, Entscheidung offen | `ip_entscheidungsvorlage_20261109.md` |

Commits der Reihe: `ac9f107`, `18d7ea5`, `8e607d9`, `ab527f4`, `9687021`,
`a0f1802`, `210fb34`, `465c09f`.

Wichtig für den nächsten, der die Karte anfasst: Die Seite lädt `app.js?v=3`.
Ein Cache-Buster auf der HTML-URL genügt nicht, um eine geänderte `app.js` im
Browser zu sehen — nötig ist `fetch(src,{cache:'reload'})` und ein Reload.

## 2. Wo die Wissenschaft steht

Unverändert seit dem 8.11., **0 Modellaufrufe** in der gesamten Reihe.

| Größe | Wert |
|---|---|
| eingeschlossene Studien | k = 3 (S1 MENDS, S2 Wade, S3 van Geijlswijk) |
| gepoolter Effekt (SOL) | −26,29 min (95 %-CI −55,57 bis 3,00), p = 0,061 |
| Heterogenität | τ² = 104,5, I² = 63 % |
| Fixed-Effect (nur Vergleich) | −22,22 min |
| Leave-one-out | −20,84 / −34,56 / −25,22; keins signifikant (p 0,214 / 0,059 / 0,259) |

Die 83 Dokumente ohne PMC-Volltext sind geprüft: keines liegt lokal, Europe PMC
hat für 77 kein OA-PDF, OpenAlex liefert einen Treffer (Nunes 2008), der nur
eine PSQI-Komponente berichtet und nicht poolbar ist. Zwei Doppelpublikationen
sind aufgelöst: 23098680 ist der HTA-Bericht von S1, 21091391 eine
Sekundärpublikation von S2.

## 3. Offene inhaltliche Punkte

1. **Fernleihe bestellen.** 5 A-Titel plus 15 B-Titel (fünf der zwanzig B sind
   nach der Triage Klasse D und gestrichen). Die Liste liegt als Markdown und
   als reiner Text vor, mit Autor, Quelle, DOI und PMID je Titel.
2. **Nach der Lieferung zuerst deduplizieren.** Register-ID, n, Zentren,
   Rekrutierungszeitraum gegen S1–S3 prüfen, bevor eine Zahl eingetragen wird.
   Erst danach extrahieren, dann poolen.
3. **IP-Entscheidung.** `pooling.py`, `report.py` und der Orchestrator bleiben
   gitignored. Die Vorlage nennt vier Alternativen; die Entscheidung ist nicht
   technisch und steht beim Eigentümer.
4. **Voll-Suite-Lauf.** Der letzte Vollauf (1331 passed, 2 skipped) stammt von
   vor den heutigen Änderungen an `server.py`, `app.js` und den zwei neuen
   Tests. Die betroffenen Tests sind einzeln grün (14 passed), ein Vollauf ist
   offen und billig.
5. **Phase 3 des Auftrags** (neue Untersuchungsfrage) ist ohne neue Daten nicht
   startbar. Ein Lauf würde dieselben drei Studien erneut lesen.

## 4. Reproduktion

```text
export PYTHONIOENCODING=utf-8

# Endpunkt und Karte
.venv/bin/python.exe scripts/serve_dashboard_stub.py            # Port 8099
.venv/bin/python.exe scripts/serve_dashboard_stub.py --kaputtes-ziel
.venv/bin/python.exe scripts/pruefe_metaanalysis_api.py

# Betrieb
.venv/bin/python.exe scripts/pruefe_betrieb_20261109.py --beide --n 200

# Fernleihe und Extraktion
.venv/bin/python.exe scripts/erstelle_fernleihliste.py
.venv/bin/python.exe scripts/pruefe_extraktion_20261109.py --check

# Tests
.venv/bin/python.exe -m pytest research_agent/tests/test_dashboard_contract.py \
    research_agent/tests/test_dashboard_metaanalysis_error.py -q
```

Alle Skripte laufen auf Kopien oder lesend. Kein Netz, kein Modell, keine
Schreibzugriffe auf die Original-DB.

## 5. Empfehlung

**Die 20 Bestellungen abschicken und bis zur Lieferung nichts am Analysesystem
ändern.** Grund: Der Punktschätzer bei k = 3 liegt mit p = 0,061 knapp über der
Schwelle; jede weitere Modell- oder UI-Variante verschiebt nur Nachkommastellen.
Die einzige Größe, die sich bewegen kann, ist k, und die hängt an Volltexten,
die ohne Bibliothek nicht erreichbar sind. Der billigste sinnvolle Schritt
daneben ist der Voll-Suite-Lauf, weil er die heutigen Änderungen in einem
Durchgang abdeckt.
