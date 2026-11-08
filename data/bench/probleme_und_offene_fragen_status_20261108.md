# Probleme & offene Fragen vom 05.11. — Stand 08.11.2026 (abgeschlossen)

Die Datei `data/bench/probleme_und_offene_fragen_20261105.pdf` (3 Seiten,
6.197 Zeichen) ist der PDF-Export der gleichnamigen `.md` (6.216 Zeichen);
inhaltlich vollständig erfasst, Abweichung nur durch PDF-Zeilenumbrüche.

**Endstand der 11 Punkte: 6 erledigt oder beantwortet, 4 durch Messung
entschieden, 1 durch Budget blockiert.** Kein Punkt wartet mehr auf Arbeit.

## 1. Kernprobleme

| Punkt | Stand | Beleg |
|---|---|---|
| **P1** Extraktionstiefe blockiert Pooling | **beantwortet (negativ)** | 33 von 33 Dokumenten gelesen, 0 lesbare SOL-Zeilen (`xml_nachladen_20261108.md`); Gesamtkorpus 11 SOL-Zeilen aus 5 Quellen, **k=1** (`schaetzer_pruefung_20261108.md`) |
| **P2** Vision-Fallback braucht Original-PDFs | **entschieden: nicht durchführen** | 0 von 26 colspan-verworfenen Zeilen tragen eine Effektspalte; 5 Regex-Treffer sind falsch positiv (`colspan_befund_20261108.md`) |
| **P3** Rate-Limits drosseln die Netzabdeckung | **erledigt** | Telemetrie Run 2: 1.324 Aufrufe, 636 × HTTP 429; Europe PMC und Crossref 0 Fehler → Hypothese umgestellt |
| **P4** Vision-Seitenbudget (12) | **entfällt** mit P2 | ohne Ziel kein Budget nötig; Wert unverändert |
| **P5** Code-Hygiene in `orchestrator.py` | **erledigt (verifiziert)** | alle acht `asyncio.gather`-Stellen entpacken ihre Coroutines, Wächter-Test grün; Datei gitignored, kein Commit |

## 2. Offene Fragen

| Frage | Stand | Beleg / Grund |
|---|---|---|
| **1** Endvergleich Run 1 vs. Run 2 | **erledigt** | Run 2 ausgewertet (`q1_befund_20261108.md`, Telemetrie) |
| **2** PDF-Nachschub für OA-XML-Quellen | **erledigt** | offline 0 PDF / 23 XML / 10 nur PMC; Beschaffung 10 × HTTP 500 (Europe PMC, 20 von 20 Versuchen) und 10 × HTTP 200 (NCBI) → 33/33 lesbar. PDFs sind für die Text-Leser nicht nötig |
| **3** Vision-Zeilen ersetzen oder behalten | **entfällt** | es existieren keine Vision-Zeilen; ohne Ziel (P2) auch keine geplant |
| **4** Meta-Reports aus den Referenz-DBs | **erledigt** | `data/bench/regreports/{exercise,kognition,mediterran}_report_meta.json`, jetzt versioniert |
| **5** Referenz-Reviews als Goldstandard | **blockiert** — Einkaufsfrage, kein Budget freigegeben | nicht durch Arbeit lösbar |
| **6** Vision-Seitenbudget erhöhen | **entfällt** mit P2 | — |

## 3. Die drei Schritte vom 08.11.2026

| Schritt | Ergebnis | Artefakt |
|---|---|---|
| PDF-Verfügbarkeit der 33 Dokumente (offline) | 0 PDF, 23 XML, 10 nur PMC, 33 abgeleitete PMC-URLs | `pdf_verfuegbarkeit_20261108.md` |
| 10 fehlende Dokumente beschaffen und lesen | NCBI statt Europe PMC: 10/10 geladen, 62 Tabellenzeilen, **0 Effekte**, 0 SOL | `xml_nachladen_20261108.md` |
| Lohnt Spaltenauflöser/Vision? | 342 Mismatch-Zeilen, **0 mit Effektspalte** | `colspan_befund_20261108.md` |

Der wichtigste Nebenbefund: Europe PMC lieferte für zehn PMCIDs in **20 von 20**
Versuchen HTTP 500, NCBI efetch alle zehn. Ein Anbieterausfall ist kein
„Dokument nicht verfügbar".

## 4. Was jetzt noch zu tun wäre — und warum nicht hier

**Frage 5 (Goldstandard-Reviews)** ist der einzige offene Punkt. Er braucht
Geld (Referenz-Reviews kaufen) und danach einen Abgleich der eigenen
Extraktion gegen deren Effekttabellen. Ohne Budget keine Aussage über
Sensitivität oder Spezifität — jede Zahl dazu wäre erfunden.

**P1 ist beantwortet, nicht repariert.** Drei Leser-Fixes mit messbarer
Wirkung auf die Gesamtausbeute (+576 Zeilen) hatten bei SOL null Wirkung, und
der vierte Kandidat (colspan) hat nachweislich kein Ziel. Ein fünfter hätte
keine Grundlage. Wer mehr SOL-Zeilen will, braucht **anderen Korpus**, nicht
besseren Leser.

## 5. Empfehlung

1. **Diesen Korpus abschließen.** Die Aussage steht: 1,2 % der Zeilen
   betreffen SOL, k=1, kein Pooling.
2. **Neues Material nur mit breiterem Kriterium** („sleep latency" statt der
   engen Synonymliste, andere Population) — und vorher die Erwartung
   quantifizieren, sonst wiederholt sich der Abstract-Lauf.
3. **Frage 5 nur mit Budget.** Sie ist die einzige, die die Extraktionsgüte
   wirklich messen würde.
