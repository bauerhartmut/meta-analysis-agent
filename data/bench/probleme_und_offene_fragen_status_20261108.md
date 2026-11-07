# Probleme & offene Fragen vom 05.11. — Abgleich mit dem Stand 08.11.2026

Die Datei `data/bench/probleme_und_offene_fragen_20261105.pdf` (3 Seiten,
6.197 Zeichen) ist der PDF-Export der gleichnamigen `.md` (6.216 Zeichen).
Stichproben gegen den Text: „P1", „Vision-Fallback", „Rate-Limits",
„Empfohlene Reihenfolge" stehen in beiden; Abweichung nur durch
PDF-Zeilenumbrüche. **Inhaltlich ist die PDF vollständig erfasst — es fehlt
kein Text.** Ein Verarbeitungsvermerk gab es bisher nicht, und keine Datei
im Repo verwies auf sie.

Damit ist die eigentliche Frage nicht „gelesen?", sondern „abgearbeitet?".
Antwort: **3 von 11 Punkten erledigt, 1 teilweise, 7 offen.**

## 1. Kernprobleme

| Punkt | Stand | Beleg |
|---|---|---|
| **P1** Extraktionstiefe blockiert Pooling | **teilweise** — quantifiziert und eingegrenzt, nicht gelöst | 838 direkte Effektzeilen nach Design-Gates (vorher 987), 11 SOL-Zeilen aus 5 Quellen, davon **k=1 für Melatonin** (`schaetzer_pruefung_20261108.md`) |
| **P2** Vision-Fallback braucht Original-PDFs | **offen** | seit dem Trigger-Fix kein Vision-Lauf: Lauf 1 war text-only, 23 von 33 Dokumenten geladen, 10 × HTTP 500, 0 lesbare SOL-Zeilen |
| **P3** Rate-Limits drosseln die Netzabdeckung | **erledigt** (beantwortet) | Telemetrie Run 2: 1.324 Aufrufe, 636 × HTTP 429; OpenAlex 94, Semantic Scholar 82 Circuit-Breaks, Europe PMC und Crossref 0 → Hypothese auf European PMC umgestellt |
| **P4** Vision-Seitenbudget (12) | **offen** | ohne Vision-Lauf keine Log-Zahlen; Budget bleibt unverändert |
| **P5** Code-Hygiene in `orchestrator.py` | **offen** | Datei ist gitignored und geschützt; die 7 fehlerhaften Zyklen (`An asyncio.Future, a coroutine or an awaitable is required`, Zyklen 3, 6, …, 21) sind dokumentiert, aber nicht behoben |

## 2. Offene Fragen

| Frage | Stand | Beleg / Grund |
|---|---|---|
| **1** Endvergleich Run 1 vs. Run 2 | **erledigt** | Run 2 ausgewertet (Telemetrie, `q1_befund_20261108.md`); kein dritter Netzlauf |
| **2** PDF-Nachschub für OA-XML-Quellen | **offen** | kein Unpaywall-/PMC-Abgleich gelaufen |
| **3** Vision-Zeilen ersetzen oder behalten | **offen** | ohne Vision-Lauf nicht entscheidbar |
| **4** Meta-Reports aus den Referenz-DBs | **erledigt** | `data/bench/regreports/{exercise,kognition,mediterran}_report_meta.json` vorhanden |
| **5** Referenz-Reviews als Goldstandard | **offen** | Einkaufsfrage, kein Budget freigegeben |
| **6** Vision-Seitenbudget erhöhen | **offen** | hängt an P4 |

## 3. Was das für die Reihenfolge heißt

Die empfohlene Reihenfolge der PDF (Run 2 auslaufen lassen → Endvergleich →
bei fehlender Poolbarkeit PDF-Nachschub) ist **abgearbeitet bis zur
Entscheidung**: Der Endvergleich fiel negativ aus, der Abstract-Lauf 1 hat
die Hypothese „Abstracts genügen" belegt (35.707 statt 90.220 Zeichen,
235 Treffer, aber 0 lesbare SOL-Zeilen) und A1–A3 erfüllt, also keinen
zweiten Lauf gerechtfertigt. Der nächste Hebel ist damit Frage 2 (PDF-Nachschub
bzw. Volltext), nicht ein weiterer Blindlauf.

P1 bleibt der Hauptblocker: die Gates sind jetzt eng genug, aber es gibt für
Melatonin nur **eine** SOL-Zeile. Mehr Extraktionsgüte erzeugt keine zweite
Studie — dafür braucht es mehr Quellen mit berichteter SOL in Minuten.

## 4. Empfehlung

1. Frage 2 zuerst: Abgleich der 33 Korpus-Dokumente gegen PMC-PDF/Unpaywall,
   Trefferliste als JSON, kein Netzlauf ohne Freigabe.
2. Danach entscheiden, ob ein Volltext-Lesepass (Text oder Vision) die
   SOL-Ausbeute über k=1 hebt — vorher Telemetrie des letzten Laufs prüfen.
3. P5 nur mitnehmen, wenn `orchestrator.py` ohnehin angefasst wird; der
   asyncio-Fehler kostet Zyklen, ist aber gitignored und nicht Teil des
   Berichts.
