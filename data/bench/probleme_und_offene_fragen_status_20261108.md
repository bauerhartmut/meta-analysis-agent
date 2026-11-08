# Probleme & offene Fragen vom 05.11. — Abgleich mit dem Stand 08.11.2026

Die Datei `data/bench/probleme_und_offene_fragen_20261105.pdf` (3 Seiten,
6.197 Zeichen) ist der PDF-Export der gleichnamigen `.md` (6.216 Zeichen).
Stichproben gegen den Text: „P1", „Vision-Fallback", „Rate-Limits",
„Empfohlene Reihenfolge" stehen in beiden; Abweichung nur durch
PDF-Zeilenumbrüche. **Inhaltlich ist die PDF vollständig erfasst.**

Stand nach dem Nachladen der zehn fehlenden Dokumente (2026-11-08, abends):
**5 von 11 Punkten erledigt, 1 beantwortet-negativ, 5 blockiert** (alle fünf
warten auf eine Entscheidung, die Geld oder Modellkontingent kostet, nicht auf
Arbeit).

## 1. Kernprobleme

| Punkt | Stand | Beleg |
|---|---|---|
| **P1** Extraktionstiefe blockiert Pooling | **beantwortet (negativ)**, nicht gelöst | 33 von 33 Dokumenten der Stichprobe gelesen, 0 lesbare SOL-Zeilen (`xml_nachladen_20261108.md`); Gesamtkorpus 11 SOL-Zeilen aus 5 Quellen, **k=1** (`schaetzer_pruefung_20261108.md`) |
| **P2** Vision-Fallback braucht Original-PDFs | **blockiert** — 0 von 33 Original-PDFs lokal; ein Vision-Lauf kostet Modellkontingent und ist nicht freigegeben | `pdf_verfuegbarkeit_20261108.json`; neue Teilantwort: der Text-Layer ist jetzt vollständig, die 10 fehlenden XML kamen über NCBI efetch |
| **P3** Rate-Limits drosseln die Netzabdeckung | **erledigt** | Telemetrie Run 2: 1.324 Aufrufe, 636 × HTTP 429; Europe PMC und Crossref 0 Fehler → Hypothese auf Europe PMC umgestellt |
| **P4** Vision-Seitenbudget (12) | **blockiert** an P2 — ohne Vision-Lauf keine Log-Zahlen | Budget unverändert |
| **P5** Code-Hygiene in `orchestrator.py` | **erledigt (verifiziert)** | alle acht `asyncio.gather`-Stellen entpacken ihre Coroutines (`*[...]`), Wächter `test_async_gather_guards.py` grün; Datei ist gitignored, daher kein Commit |

## 2. Offene Fragen

| Frage | Stand | Beleg / Grund |
|---|---|---|
| **1** Endvergleich Run 1 vs. Run 2 | **erledigt** | Run 2 ausgewertet (Telemetrie, `q1_befund_20261108.md`) |
| **2** PDF-Nachschub für OA-XML-Quellen | **erledigt** | offline: 0 lokale PDF, 23 lokale XML, 10 nur PMC (`pdf_verfuegbarkeit_20261108.md`); Beschaffung: 10 × HTTP 500 bei Europe PMC, 10 × HTTP 200 bei NCBI → 33/33 lesbar. **PDFs sind für die Text-Leser nicht nötig.** Publisher-PDF bleibt unbekannt (keine Unpaywall-Daten lokal) |
| **3** Vision-Zeilen ersetzen oder behalten | **entschieden für diesen Datenstand** | es gibt keine Vision-Zeilen: Lauf 1 war text-only, Lauf 2 hatte wegen des damaligen Triggers 0 Vision-Aufrufe. Die Frage stellt sich erst nach einem Vision-Lauf |
| **4** Meta-Reports aus den Referenz-DBs | **erledigt** | `data/bench/regreports/{exercise,kognition,mediterran}_report_meta.json` — jetzt versioniert |
| **5** Referenz-Reviews als Goldstandard | **blockiert** — Einkaufsfrage, kein Budget freigegeben | nicht durch Arbeit lösbar |
| **6** Vision-Seitenbudget erhöhen | **blockiert** an P4 | hängt am selben Vision-Lauf |

## 3. Was der Nachladeschritt geändert hat

Der Abschlussbericht notierte als Grenze: „Die 10 ungeprüften Dokumente
könnten die Null des Abstract-Laufs verändern." Diese Grenze ist weg:

| | vorher | nachher |
|---|---:|---:|
| Dokumente der Stichprobe | 33 | 33 |
| gelesen | 23 | **33** |
| lesbare SOL-Zeilen | 0 | **0** |

Der Beschaffungsweg ist der eigentliche Fund: Europe PMC liefert für diese
zehn PMCIDs reproduzierbar HTTP 500 (20 von 20 Versuchen), NCBI efetch
liefert alle zehn (8,6–100,6 KB). Ein Anbieterausfall darf künftig nicht als
„Dokument nicht verfügbar" verbucht werden.

## 4. Warum die restlichen fünf Punkte stehen

Sie brauchen keine weitere Analyse, sondern eine Entscheidung:

1. **P2/P4/F3/F6 — ein Vision-Lauf.** Voraussetzung: Original-PDFs (lokal 0)
   und Modellkontingent. Nutzen fraglich: 26 der 62 Tabellenzeilen der neuen
   Dokumente scheiterten an `colspan`, nicht an fehlenden Bildern. Der
   Vision-Fallback liest Bilder, er löst keine Spaltenstruktur im Text.
2. **F5 — Goldstandard-Reviews.** Einkauf; ohne Budget keine Aussage über
   Sensitivität/Spezifität der Extraktion.

## 5. Empfehlung

1. **P1 abschließen, nicht weiter reparieren:** der Korpus trägt keine zweite
   unabhängige SOL-Studie. Ein weiterer Leser-Fix an diesem Korpus hat in drei
   messbaren Versuchen null Wirkung auf SOL gehabt.
2. **Wenn überhaupt neues Material, dann ein anderer Korpus** (breitere
   Synonymliste „sleep latency", andere Population), nicht ein vierter Leser.
3. **Vision nur mit klarer Frage:** vorher prüfen, wie viele der 26
   `colspan`-Zeilen überhaupt eine Effektspalte tragen — sonst bezahlt man
   Modellkontingent für Demografietabellen.
