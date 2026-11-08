# Warteliste: was nach Eintreffen der PDFs zu tun ist

Stand: 2026-11-08. Reihenfolge, Abbruchpunkte und Messgroessen fuer den Fall,
dass die fuenf bestellten Artikel als PDF eintreffen. Jeder Schritt nennt den
Befehl und das Artefakt, das er hinterlaesst.

## 0. Ablage (vor dem ersten Lauf)

- PDFs nach `data/bench/sol2/volltext/` legen.
- Dateiname = PMID, z. B. `41122831.pdf`, `33157425.pdf`, `28364493.pdf`,
  `14566165.pdf`, `11292231.pdf`. Dann ist die Zuordnung zur Bestellliste
  eindeutig und der Bericht lesbar.
- `data/bench/sol2/fulltext/` ist etwas anderes: dort liegen 34 bereits
  geloeste Volltexte als `.txt`. Nicht hineinmischen.

## 1. Lesen (ein Befehl, offline)

```bash
.venv/bin/python.exe scripts/read_pdf_corpus.py \
  --dir data/bench/sol2/volltext \
  --db data/bench/sol2/pdf.db \
  --json data/bench/sol2/pdf.json \
  --md data/bench/sol2/pdf.md
```

Artefakte: `pdf.md` (Menschen), `pdf.json` (Maschine), `pdf.db` (Zeilen mit
Zitat). Kennzahlen im Bericht: `pdfs`, `readable`, `rows`, `sol_rows`,
`k_sol_poolable`, `problems`, je Datei `chars`, `arm_candidates`, `arm_stored`.

## 2. Triage je Datei (in dieser Reihenfolge)

| Befund im Bericht | Bedeutung | Was tun |
|---|---|---|
| "kein Textlayer" oder `chars` < 50 | Scan ohne Textebene | nicht als leere Studie verbuchen. Nachbestellen (mit Bitte um Textebene) oder abtippen. Kein OCR-Setup bauen |
| `kurzer Text` (unter 2000 Zeichen) | gelesen, nur wenig Text | normal auswerten; im Bericht steht der Hinweis |
| `chars` ok, `sol_rows` = 0 | Endpunkt nicht berichtet | als "nicht berichtet" zaehlen. Das ist ein Befund ueber die Studie, kein Fehler der Kette |
| `sol_rows` > 0, `arm_stored` = 0 | Leser-Luecke | Zitat im Text suchen (Strg+F nach "onset latency"); erst wenn ein Muster fehlt, eine Regel ergaenzen - mit Testfall |
| `arm_stored` > 0 | Zeile gespeichert | weiter zu Schritt 3 |

Ein Scan im Bericht ist **nicht** dasselbe wie "keine Daten": beide ergeben
0 Zeilen, nur der Ablehnungsgrund unterscheidet sie
(`scan_grenze_20261108.md`).

## 3. k bestimmen und gegen das Schritt-Ziel pruefen

- `k_sol_poolable` aus `pdf.json` ablesen, nicht schaetzen.
- **Schritt-Ziel: k >= 2** (Gesamtziel k >= 5 erst mit A + B).
- Bisheriger Stand vor Lieferung: k = 1 (PMC3489506, zwei Zeilen).
- Erwartung aus fuenf Artikeln: eine poolbare Studie, optimistisch zwei
  (`schwelle_k5_20261108.md`). Wird es mehr, ist die Quote besser als gemessen -
  dann die Annahme im Schwellendokument fortschreiben, nicht stillschweigend.

## 4. Wenn k >= 2: poolen

```python
# research_agent/meta/pooling.py (lokal, gitignored - nicht committen)
from research_agent.meta.pooling import pool, leave_one_out, forest_table
analysis = pool(rows, method="hksj")
```

- Zeilen aus `pdf.db` (`study_effects`) laden, **eine Zeile je Studie und
  Subgruppe**, nicht je Tabelle.
- Berichten: k, gepoolte MD, 95-Prozent-CI, tau-Quadrat, I-Quadrat, Modell
  (Hartung-Knapp-Sidik-Jonkman), plus Leave-one-out.
- Bei k = 2 ist I-Quadrat per Definition 0 - das hinschreiben, nicht als
  Heterogenitaetsbefund verkaufen.
- Abgleich mit der Referenz (gepoolte MD im CI -9,75 bis -4,37 min) nur, wenn
  die Trialmenge ueberlappt; sonst als nicht vergleichbar kennzeichnen.

## 5. Wenn k < 2: keine gepoolte Zahl

- Kein Wert, kein CI, kein "Trend". Nur Einzelstudien tabellarisch.
- Entscheidung dokumentieren: B-Liste (20 weitere, `zugangsliste_20261108.csv`)
  bestellen oder Untersuchung mit dem Befund "Berichtsstil traegt keine
  Arm-Mittelwerte" abschliessen.

## 6. Erfolg messen (die eigentliche Frage)

| Kriterium | Messgroesse | Wo |
|---|---|---|
| Ausbeute | `k_sol_poolable` | `pdf.json` |
| Nachvollziehbarkeit | jede Zeile mit woertlichem Zitat | `pdf.db`, Spalte `quote` |
| Ehrlichkeit | k, Einheit, Modell im Bericht genannt; kein Wert bei k < 2 | Bericht |
| Kein Skalenraten | Zeilen ohne genannte Einheit bleiben draussen | `problems` im Bericht |
| Crossover getrennt | Crossover-Studien nicht mit SE(g) gepoolt | Bericht |

## 7. Nach dem Lauf (Pflicht, sonst veraltet der Stand)

1. `stand_melatonin_20261108.md` fortschreiben: neues k, neue Zahl der
   auswertbaren Zeilen, Restluecke.
2. Dieses Dokument als erledigt markieren (Datum, k).
3. Commit mit den neuen Artefakten - Zahlen ohne Commit sind nicht zitierfaehig.

## 8. Was hier ausdruecklich nicht passiert

- Kein OCR-Nachbau (kein `tesseract` vorhanden, `scan_grenze_20261108.md`).
- Keine Einheit aus dem Kontext raten - der Annahme-Durchgang hat 0 Zeilen
  gebracht und bleibt verworfen.
- Crossover-Studien nicht mit SE(g) fuer unabhaengige Gruppen poolen.
- Keine zusammenfassenden Schaetzungen aus Uebersichtsarbeiten als Studienzeile.
- Kein Netzlauf fuer einzelne PDFs; Nachbestellung laeuft ueber die Bibliothek.

## 9. Aufwand (Schaetzung, nicht gemessen)

Lesen und Triage: wenige Minuten je PDF. Nacharbeit nur bei Leser-Luecken, dann
ein Testfall plus eine Regel - nicht mehr. Pooling und Bericht: ein Durchgang,
weil die Rechnung bereits getestet ist (`test_pooling_reference.py`).
