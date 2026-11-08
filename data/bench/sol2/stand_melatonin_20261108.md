# Melatonin und Einschaflatenz: Stand der Untersuchung

Stand: 2026-11-08. Jede Zahl steht in einer der unten genannten Dateien; es gibt
keine Schaetzung ohne Kennzeichnung. Ein Netzlauf fand statt (Q2-Abzug), alle
weiteren Schritte liefen offline.

## Frage

Kann der Agent aus guten Primaerstudien eine belastbare Metaanalyse bauen -
messbar an der Zahl poolbarer Studien (k) und nicht an der Zahl gebauter
Werkzeuge?

## Antwort in einem Absatz

Der Korpus ist jetzt richtig geschnitten und die Kette liest XML und PDF, aber
**k = 1**: eine Studie (PMC3489506) mit zwei Zeilen, g = -0,644 (SE 0,193,
n = 113) und g = -0,685 (SE 0,294, n = 49). Eine gepoolte Aussage gibt es
**nicht**, weil k < 2. Die fehlenden Studien liegen hinter fehlendem
Volltextzugang und in Studienlayouts, die Arm-Mittelwerte nicht berichten -
nicht in fehlender Extraktion.

## Kennzahlen

| Kennzahl | Wert | Quelle |
|---|---:|---|
| Suchtreffer Q2 (streng) | 114 | `manifest_q2.json` |
| davon mit PMC-Volltext | 31 | `manifest_q2.json` |
| ohne Volltext | 83 | `manifest_q2.json` |
| ohne Volltext, Prioritaet A / B / C / D | 5 / 20 / 39 / 19 | `zugangsliste_20261108.json` |
| davon mit DOI | 80 | ebd. |
| nach Titelscreening gelesen | 20 | `extended.json` |
| Dokumente mit Einschaflatenz-Zeilen | 9 | `schwelle_analyse.json` |
| SOL-Zeilen in diesen Dokumenten | 83 | ebd. |
| **poolbare Studien (k)** | **1** | `extended.json` |
| gespeicherte Zeilen | 2 | `extended.db` (`study_effects`) |
| erster Durchgang, ohne Screening: Dokumente / SOL-Zeilen | 12 / 93 | `bewertung_q2_20261108.md` |
| erste Extraktion: Arm-Zeilen gespeichert / davon SOL | 13 / 0 | ebd. |
| davon Baseline-Merkmale statt Effekte | 11 | ebd. |

## Warum k = 1 und nicht 5

**Vier von neun** Dokumenten mit SOL-Zeilen sind Crossover (PMC12903794,
PMC4425994, PMC4365553, PMC11103136). SE(g) gilt fuer unabhaengige Gruppen; ohne
Within-Subject-Korrektur sind sie nicht poolbar. Das ist eine Modellentscheidung,
kein Lesefehler.

Von den **fuenf parallelen** Studien konvertiert eine. Die vier offenen:

| PMC | Hindernis |
|---|---|
| PMC2952772 | Dosisfindung, mehrere Arme |
| PMC2933606 | zwei Arme, je eine Zeile pro Arm (Zeilenpaarung) |
| PMC5774131 | Spaltenformat (Effekt als Verhaeltnis) |
| PMC10131443 | ein Wert je Arm |

Weitere gemessene Befunde:

- Im ersten Durchgang wurden 13 Arm-Zeilen gespeichert, **11 davon
  Baseline-Merkmale** (Alter, Geschlecht, BMI, PSQI). Das Gate prueft Form,
  nicht Plausibilitaet.
- Direkte Effektspalten: 30 SOL-Zeilen gescreent, 8 mit Intervall, 7 mit
  CI-Kopf, **0 mit genanntem Effektwort** (`ergebnis_direkte_effekte_20261108.md`).
  Ein Durchgang mit der Annahme "Einheit aus dem Kontext" lieferte ebenfalls 0 -
  er ist dokumentiert und verworfen, weil die Skala nirgends genannt wird.
- Eine fremde gepoolte Schaetzung (PMC3489506, Tabelle 9: WMD -13,2
  [-27,3; 0,9]) wurde bewusst **nicht** als Studienzeile uebernommen.

## Erfolgsschwelle (zweistufig)

| Ziel | Schwelle | Gilt fuer |
|---|---|---|
| Schritt-Ziel | k >= 2 | die fuenf bestellten A-Artikel |
| Gesamtziel | k >= 5 | A + B (25 Dokumente) |

Grundlage: `schwelle_k5_20261108.md`. Bei der beobachteten Quote (eine poolbare
Studie aus fuenf parallelen) erwartet man aus fuenf Artikeln **eine** Studie;
k >= 5 erreicht erst A + B, mit rund 58 Prozent Wahrscheinlichkeit. Die
Referenz fuer die Rechnung bleibt die gepoolte MD im CI -9,75 bis -4,37 min
(`abzug_plan_melatonin_20261108.md`, D2); sie ist bei k = 1 nicht pruefbar.

## Was jetzt laeuft (getestet)

| Weg | Skript | Stand |
|---|---|---|
| PMC-XML | `scripts/read_q2_extended.py` | Titelscreening, Klammer-SD nur mit Etikett, Zeitpunktspalten, Crossover nur im Textkopf; liefert k = 1 |
| PDF | `scripts/read_pdf_corpus.py` | Ende-zu-Ende getestet: typischer Satz wird zu einer Zeile in der DB, mit Zitat |
| Scan-Erkennung | `scripts/make_scan_probe.py` | 5.497 Zeichen im Original, 0 im Scan, unabhaengig mit `pdftotext` bestaetigt |

Im Bestand gibt es **keinen** Scan: alle 36 PDFs in `data/origpdf` haben eine
Textebene (1.915 bis 6.750 Zeichen je Seite). OCR ist in dieser Umgebung nicht
verfuegbar (kein `tesseract`, kein `pytesseract`); die Bestellmail bittet
deshalb um PDFs mit Textebene.

## Die offene Luecke

**83 Dokumente ohne Volltext**, 80 davon mit DOI. Fuenf sind als Prioritaet A
ausgewaehlt und bestellt (Mail in `bestellanfrage_20261108.txt`). Bei der
beobachteten Quote ist daraus **eine** poolbare Studie zu erwarten, optimistisch
zwei - nicht fuenf. k >= 5 verlangt die B-Liste (20 weitere).

## Was ausdruecklich nicht gilt

- **Keine gepoolte Mittelwertdifferenz, kein CI, kein I-Quadrat.** D2 ist nicht
  pruefbar (k < 2), und es wird kein Wert berichtet.
- **Kein belegter Evidenzmangel.** 83 Dokumente sind ungelesen; k = 1 ist eine
  Untergrenze, kein Beweis, dass es die Daten nicht gibt.
- **Kein Ersatz durch Sekundaerliteratur.** Zusammenfassende Schaetzungen aus
  Uebersichtsarbeiten werden nicht als Studienzeilen gezaehlt.
- **Keine Minuten aus unbenannten Skalen.** Wo die Einheit nicht in der Zeile
  steht, entsteht keine Zeile.

## Reproduktion

```bash
# XML-Korpus (offline, 31 Dokumente)
.venv/bin/python.exe scripts/read_q2_extended.py

# PDF-Kette, sobald Volltexte in data/bench/sol2/volltext/ liegen
.venv/bin/python.exe scripts/read_pdf_corpus.py --dir data/bench/sol2/volltext

# Schwellenrechnung
.venv/bin/python.exe -m pytest research_agent/tests -q
```

## Einordnung

Die Untersuchung beantwortet die Ausgangsfrage derzeit mit **"noch nicht, aber
aus benennbarem Grund"**. Zwei Engpaesse sind gemessen und behoben (Korpus,
Tabellenformen), einer ist gemessen und offen (Volltextzugang), einer ist eine
Modellgrenze (Crossover). Was fehlt, ist Material - nicht ein weiterer Leser:
vier gemessene Hebel am alten Korpus brachten bei der Einschaflatenz null
(`data/bench/sol/ergebnisstand_20261108.md`).

Der naechste belastbare Schritt ist deshalb die Lieferung der fuenf Artikel. Ist
k danach >= 2, ist die Frage mit einer ehrlich als duenn ausgewiesenen
Schaetzung beantwortbar; bleibt k = 1, ist auch das ein Befund ueber den
Berichtsstil der Literatur, nicht ueber den Agenten.
