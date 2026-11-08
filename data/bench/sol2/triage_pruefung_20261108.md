# Pruefung: Triage-Bericht an einer simulierten Lieferung

**SIMULATION - KEINE ECHTEN STUDIENDATEN.** Die vier PDFs sind die
synthetischen Pruef-PDFs aus `data/bench/sol2/probelauf/`, nur mit den
PMIDs der A-Liste als Dateinamen. Geprueft wird die Mechanik des
Berichts (Zuordnung, Zustaende, k-Fortschreibung), nicht die Extraktion
und nicht eine echte Studie.

Stand: 2026-11-08T14:09:20. Bestanden: ja.

## Aufbau

- Vier der fuenf A-Artikel liegen als Datei vor, `11292231` fehlt
  absichtlich, damit die Fehlliste geprueft werden kann.
- Eine Datei (`14566165`) ist bewusst der Scan ohne Textebene.
- Zuordnung ueber den Dateinamen, wie es die Warteliste verlangt.

| Datei | Inhalt der Pruefdatei |
|---|---|
| `41122831.pdf` | `probe_artikel_1.pdf` |
| `33157425.pdf` | `probe_artikel_2.pdf` |
| `28364493.pdf` | `probe_artikel_3_kurz.pdf` |
| `14566165.pdf` | `probe_scan.pdf` |

## Kriterien

| Kriterium | erwartet | gemessen | bestanden |
|---|---|---|---|
| PMID aus Dateiname, Prio A, als angefordert erkannt | 4 von 4 | 4 Dateien, PMID = Dateiname, alle Prio A | ja |
| Zustaende wie erwartet | 3 poolbar, 1 Scan | 3 poolbar, 1 scan | ja |
| k = Basis + poolbare Dateien | 1 + 3 = 4 | Basis 1, Zuwachs 3, k 4, erreicht ja | ja |
| nicht geliefert | nur 11292231 | 11292231 | ja |
| keine fremde Datei | leer | leer | ja |

## Was der Bericht je Datei sagt

| Datei | PMID | Prio | Zustand | Zeichen | SOL-Zeilen | poolbar |
|---|---|---|---|---:|---:|---:|
| 14566165.pdf | 14566165 | A | scan | - | - | - |
| 28364493.pdf | 28364493 | A | poolbar | 618 | 1 | 1 |
| 33157425.pdf | 33157425 | A | poolbar | 1741 | 1 | 1 |
| 41122831.pdf | 41122831 | A | poolbar | 1883 | 1 | 1 |

## k-Fortschreibung

- k vorher: 1 (PMC3489506, XML-Korpus)
- poolbare Dateien: 3
- k nachher: 4 von Ziel 2, erreicht: ja
- Satz des Berichts: k >= Ziel: poolen (Warteliste Schritt 4). Bei k = 2 ist I-Quadrat per Definition 0 - das hinschreiben, nicht als Heterogenitaetsbefund verkaufen.

## Was damit belegt ist und was nicht

Belegt: Dateiname mit PMID wird zur Prio-A-Zeile, fehlende Artikel
erscheinen namentlich, ein Scan wird nicht als poolbare Zeile gezaehlt,
und k ist die Summe aus Basis und poolbaren Dateien.

Nicht belegt: dass eine echte Lieferung dieselbe Ausbeute hat. k = 4
stammt hier aus drei synthetischen PDFs mit je einem konstruierten
Fließtext-Satz und ist kein Studienbefund. Die echte Auswertung ersetzt
diese Zahl, sobald die PDFs eintreffen.

## Reproduktion

```bash
# vier Pruef-PDFs unter PMID-Namen ablegen, dann
.venv/bin/python.exe scripts/triage_lieferung.py \
  --dir <ordner> --work-dir <ordner>/work \
  --json <ordner>/lieferung.json --md <ordner>/lieferung.md
```
