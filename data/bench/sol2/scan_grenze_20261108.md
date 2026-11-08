# Grenzprüfung: Was ein Scan-PDF durch die Kette verliert

Stand: 2026-11-08. Deterministisch, offline, kein Modell. Belege in
`data/bench/sol2/scanprobe.{json,md}`, Generator `scripts/make_scan_probe.py`.

## Anlass

Die fünf bestellten Artikel von 2001–2026 können als Verlags-PDF mit Textebene
kommen — oder als Scan, wenn eine Bibliothek ältere Jahrgänge eingescannt hat.
Die Frage war: **verliert die PDF-Kette bei einem Scan Inhalt, und sieht man das
im Bericht?**

## Vorbefund: im Bestand liegt kein Scan

Alle 36 PDFs aus `data/origpdf/` wurden auf Textlayer-Qualität vermessen
(Zeichen, Zeichen je Seite, Buchstabenanteil, `(cid:`/Ersatzzeichen als
Kaputt-Indikator):

| Kennzahl | Ergebnis |
|---|---|
| Dateien | 36 |
| Zeichen je Seite | 1.915 bis 6.750 |
| ohne Textlayer (< 100 Zeichen/Seite) | **0** |
| mit kaputten Zeichen (> 20) | **0** |

Es gibt also keinen echten Scan zum Testen. Der Fall wurde deshalb erzeugt:
Seite 1 von `data/origpdf/f6b22caef4606667.pdf` (4 Seiten, Actigraphy-Algorithmus)
mit `pypdfium2` zweifach gerastert und als PDF mit genau einem Bildobjekt und
**ohne jede Textzeichenanweisung** zurückgeschrieben.

```bash
.venv/bin/python.exe scripts/make_scan_probe.py <quelle.pdf> <ziel.pdf> --scale 2
```

Ergebnis: `scan_seite1.pdf`, 1.224 × 1.584 px, 495.588 Byte, 1 Bildobjekt,
Textebene 0 Zeichen. 6,9 % der Pixel sind dunkel — der Text ist im Bild
vorhanden, aber nur als Pixel.

## Messung: dieselbe Seite mit und ohne Textebene

| Weg | Original Seite 1 | Scan |
|---|---:|---:|
| `pypdf` `extract_text()` | 5.497 Zeichen | **0 Zeichen** |
| `pdftotext` (Poppler, unabhängig) | 5.556 Byte | **1 Byte** (nur Seitenvorschub) |

Zwei unabhängige Extraktoren, dasselbe Ergebnis: ohne OCR ist der Text weg.
Nicht „schlecht erkannt", sondern **vollständig verloren**.

## Was die Kette daraus macht

Lauf auf einem Verzeichnis, das nur den Scan enthält:

```
pdfs=1 lesbar=0 zeilen=0 sol=0 k=0
      1  zu wenig Text (Scan oder kaputt)
```

Im Bericht `scanprobe.md` steht die Datei mit `Zeichen 0`, alle folgenden
Spalten `-`, und unter „Ablehnungsgründe" der Grund `zu wenig Text (Scan oder
kaputt)`.

**Das ist der wichtige Punkt:** der Verlust ist *nicht stumm*. Die Datei wird
gezählt, mit 0 Zeichen geführt und begründet abgelehnt. Aber die Kennzahl k
allein unterscheidet einen Scan nicht von einer Studie, die ihre
Einschaflatenz nicht berichtet — beide liefern 0 Zeilen. Wer nur k liest, kann
„PDF kaputt" und „Daten nicht berichtet" nicht auseinanderhalten; dafür muss man
den Ablehnungsabschnitt lesen.

## Wie viel hängt daran?

Ein gescannter A-Artikel kostet **100 % seiner Zeilen** — nicht einen Teil.
Konkret: die 5.497 Zeichen der Originalseite enthalten Abstract und Methoden;
im Scan ist davon nichts lesbar, also auch keine Mittelwerte, kein n, keine
Streuung. Bei k = 1 ist ein einziger Scan dieser Art bereits der Unterschied
zwischen „eine poolbare Studie" und „keine".

## Ist die Grenze behebbar?

OCR-Werkzeuge in dieser Umgebung:

| Werkzeug | Status |
|---|---|
| `tesseract` | nicht vorhanden |
| `ocrmypdf` | nicht vorhanden |
| `pytesseract`, `easyocr`, `paddleocr`, `doctr` | nicht installiert |
| `pdftotext` (Poppler) | vorhanden, macht **kein** OCR |
| `pacman` (MSYS2-Paketverwaltung) | nicht im PATH |

Damit ist die Grenze **strukturell, nicht konfigurierbar**: es fehlt die
Engine, nicht der Aufruf. Drei Wege, insteigendem Aufwand:

1. **Text-PDF statt Scan anfordern** (empfohlen). Verlage liefern bei
   Bibliotheksbestellungen in der Regel das digitale Original; ein Hinweis in
   der Bestellung („bitte als durchsuchbares PDF") kostet nichts.
2. **`tesseract` über MSYS2 nachinstallieren** — das Poppler-Binary liegt unter
   `/ucrt64/bin`, also existiert eine MSYS2-Installation, in deren Repository
   `tesseract` liegt. Aufwand: Installation plus ein OCR-Schritt je Seite;
   Qualität bei zweispaltigen Tabellen ist begrenzt, Zahlen sind der
   fehleranfälligste Teil. **Nicht getestet** — Schätzung.
3. **Manuell abtippen.** Bei einer Handvoll Studien realistisch: SOL-Mittelwert,
   SD und n stehen im Ergebnistext, nicht nur in Tabellen.

## Grenzen dieser Prüfung

- Getestet ist **eine** Seite **eines** PDF. Alte Scans mit 300 dpi-Graustufen
  oder Schräglage verhalten sich gleich (kein Textlayer), aber die Pixelzahlen
  wären andere.
- Der Test belegt den *Verlust*, nicht die *Erkennbarkeit* eines Scans am
  Dateinamen oder an Metadaten. Die Kette erkennt ihn am Ergebnis (0 Zeichen),
  nicht vorab.
- Born-digital-PDFs mit kaputter Zeichenkodierung sind **nicht** abgedeckt: im
  Bestand gab es keinen solchen Fall. Die `fontTools`-Warnungen beim Lesen
  älterer Type1-Schriften sind kosmetisch — der Text kam vollständig heraus
  (5.497 Zeichen).

## Folge für den Ablauf, wenn die Artikel ankommen

1. `read_pdf_corpus.py` über `volltext/` laufen lassen.
2. Steht in der Je-PDF-Tabelle `Zeichen 0` oder `zu wenig Text`, ist das PDF ein
   Scan — **nicht** als „Studie ohne SOL-Daten" verbuchen, sondern zur
   Nachbestellung oder zum Abtippen vormerken.
3. Nur Dateien mit Zeichen > 0 und `SOL 0` sind inhaltlich leere Treffer.
