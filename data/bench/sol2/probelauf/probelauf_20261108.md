# Probelauf der Warteliste mit synthetischen PDFs

Stand: 2026-11-08. Zweck: den Ablauf aus `warteliste_nach_lieferung_20261108.md`
einmal durchlaufen, bevor echte Verlags-PDFs eintreffen. Alle PDFs sind
**Simulationen**; ihre Zahlen sind erfunden und tragen keinen Evidenzwert.

## Was gebaut wurde

| Datei | Art | Zeichen | Ergebnis |
|---|---|---:|---|
| `probe_artikel_1.pdf` | Textlayer, 2 Arme | 1883 | gelesen, 1 Zeile |
| `probe_artikel_2.pdf` | Textlayer, 2 Arme | 1741 | gelesen, 1 Zeile |
| `probe_artikel_3_kurz.pdf` | Textlayer, kurz | 618 | gelesen, 1 Zeile |
| `probe_scan.pdf` | Bild ohne Textlayer | 0 | abgelehnt: kein Textlayer |

Quelle: `src/*.txt`, erzeugt mit `scripts/make_text_pdf.py` (Textlayer) bzw.
`scripts/make_scan_probe.py` (Bild-PDF). Lauf:
`pdfs=4 lesbar=3 zeilen=3 sol=3 k=3`.

## Zwei Fehler, die der Probelauf gefunden hat

**1. Kurzer Text wurde als Scan verkauft.** Die Kette lehnte PDFs mit 1.787
Zeichen als "zu wenig Text (Scan oder kaputt)" ab, weil die Schwelle
`--min-chars` (2000) beides zusammenwarf. Genau die Fehldiagnose, vor der die
Warteliste warnt: ein kurzer Artikel waere zur Nachbestellung gegangen, obwohl
der Text vollstaendig lesbar war. Jetzt trennt `classify_text()`:
`< 50` Zeichen = kein Textlayer, `50..min-chars` = kurzer Text (wird gelesen
und gezaehlt), darueber = normal.

**2. PDF-Zeilenumbrueche zerlegten die Saetze.** Der Fliesstext-Leser arbeitet
zeilenweise, PDF-Text bricht Saetze aber an der Satzbreite um. Ergebnis: 3
lesbare PDFs, 0 Arm-Zeilen, k = 0 - obwohl der Satz wortgleich im Dokument
stand. Geflacht (`flatten_prose()`, Tabellenzeilen bleiben stehen) findet der
Leser den Satz sofort. Ohne diesen Probelauf waere der erste echte Lauf mit
k = 0 geendet und haette wie ein Literaturabefund ausgesehen.

## Pooling mit k = 3

| Kennzahl | Wert |
|---|---:|
| k | 3 |
| gepoolt (Hedges g) | -0.961 |
| 95-Prozent-CI | -1.493 bis -0.430 |
| I-Quadrat | 0.0 Prozent |
| tau-Quadrat | 0.000 |

Leave-one-out: gepoolt zwischen -1.096 und
-0.853. Hinweis, wie er im Bericht stehen muss: Kleine Studienanzahl (k=3): Heterogenitaets- und Intervallangaben sind mit Vorsicht zu interpretieren.

I-Quadrat = 0 bei k = 3 ist **kein** Heterogenitaetsbefund, sondern die Folge
der kleinen Zahl. Die drei Zeilen tragen alle ein woertliches Zitat.

## Was der Probelauf nicht abdeckt

- Ein echter Verlags-PDF-Text ist zweispaltig, enthaelt Fussnoten, Kopf- und
  Fusszeilen und Tabellen mit Spaltenlayout. Der Fliesstext-Leser wird dort
  mehr Rauschen sehen als hier.
- Silbentrennung ueber Zeilen (la- / tency) loest `dehyphenate()` auf;
  geprueft an `probelauf_bindestrich/` (k = 1, Zitat ohne Bindestrich).
- Zweispaltige Zeilen trennt `split_columns()` an der breitesten Luecke,
  wenn beide Seiten Text sind; am Fixture geprueft. Tabellenzeilen bleiben.
  nur fuer den einfachen Bindestrich-Fall.
- Die Zeile "kurzer Text" ist hier kuenstlich erzeugt; ob echte Kurzberichte
  darunter fallen, zeigt sich erst am Material.

## Folge fuer die Warteliste

Die Triage-Regel lautet jetzt: **`kein Textlayer` (oder unter 50 Zeichen) =
Scan**, `kurzer Text` = gelesen und normal auswerten. Beides steht im Bericht,
beides ist unterscheidbar.
