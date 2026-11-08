# Stand, Probleme und was heute geschafft wurde

Stand: 2026-11-08. Jede Zahl stammt aus einer der genannten Dateien; nichts
geschaetzt. Kurzfassung fuer Entscheidungen: `stand_kurz_20261108.md`,
Langfassung: `stand_melatonin_20261108.md`.

## Die Frage

Kann der Agent aus guten Primaerstudien eine belastbare Metaanalyse bauen -
gemessen an der Zahl poolbarer Studien (k), nicht an der Zahl gebauter
Werkzeuge?

## Der Stand in drei Saetzen

Der Korpus ist geschnitten: 114 Q2-Treffer, 31 davon mit PMC-Volltext gelesen,
83 ohne Volltext. Die Kette liest XML und PDF deterministisch und ist an 34
echten Volltexten ohne harten Fehler geprueft. **k = 1** - eine Studie
(PMC3489506) mit zwei Zeilen - deshalb gibt es keine gepoolte Schaetzung, kein
CI und kein I-Quadrat.

## Kennzahlen

| Kennzahl | Wert | Quelle |
|---|---:|---|
| Q2-Treffer (streng) | 114 | `manifest_q2.json` |
| davon als XML gelesen | 31 | `extended.json` |
| ohne Volltext | 83 | `zugangsliste_20261108.csv` |
| davon Prioritaet A / B / C / D | 5 / 20 / 39 / 19 | ebd. |
| davon mit DOI | 80 | ebd. |
| offline gelesene PDF-Volltexte | 34 (997.366 Zeichen) | `normalisierung_echte_texte_20261108.md` |
| **poolbare Studien (k)** | **1** | `extended.json` |
| gespeicherte SOL-Zeilen | 2 | `extended.db` |
| gelieferte A-PDFs | **0** | `lieferung.json` |
| Schritt-Ziel / Gesamtziel | k >= 2 / k >= 5 | `schwelle_k5_20261108.md` |

Die eine Studie: g = -0,644 (SE 0,193, n = 113) und g = -0,685 (SE 0,294,
n = 49). Referenz-CI der Literatur fuer D2: -9,75 bis -4,37 min; bei k = 1
nicht pruefbar.

## Die Probleme, nach Schwere

**P1 - Volltextzugang (blockiert alles).** 83 Dokumente ohne Volltext, 80 mit
DOI, alle in der Zugangsliste priorisiert. Fuenf sind bestellt, **kein PDF
eingetroffen** (`data/bench/sol2/volltext` enthaelt nur `.gitkeep`). Ohne
Material kein k > 1 - das ist der einzige harte Blocker.

**P2 - Crossover (Modellgrenze).** Vier von neun Dokumenten mit SOL-Zeilen sind
Crossover (PMC12903794, PMC4425994, PMC4365553, PMC11103136). SE(g) gilt fuer
unabhaengige Gruppen; ohne Within-Subject-Korrektur sind sie nicht poolbar. Das
ist eine Entscheidung, kein Lesefehler - und sie deckelt k im Altkorpus.

**P3 - Berichtsstil (Eigenschaft der Literatur).** Von 30 gescreenten direkten
Effektspalten hatten 8 ein Intervall, 7 einen CI-Kopf und **0 ein genanntes
Effektwort**. Arm-Mittelwerte mit Streuung werden in vielen Arbeiten nicht
berichtet. Der Annahme-Durchgang "Einheit aus dem Kontext" brachte 0 Zeilen und
bleibt verworfen.

**P4 - Gate prueft Form, nicht Plausibilitaet.** Im ersten Durchgang wurden 13
Arm-Zeilen gespeichert, **11 davon Baseline-Merkmale** (Alter, Geschlecht, BMI,
PSQI). Gemessen und dokumentiert; jede neue Regel braucht dafuer einen Testfall.

**P5 - Kein OCR.** Scans ohne Textebene liefern 0 Zeichen (gemessen: 5.497
Zeichen im Original, 0 im Scan). In dieser Umgebung gibt es kein `tesseract`
und kein `pytesseract`. Deshalb bittet die Bestellung um PDFs mit Textebene.

**P6 - Die Schwelle war falsch formuliert (behoben).** k >= 5 aus fuenf
Artikeln ist bei p = 0,20 praktisch ausgeschlossen (unter 1 Prozent). Jetzt
zweistufig: k >= 2 fuer die fuenf Artikel, k >= 5 nur mit A + B (25 Dokumente,
rund 58 Prozent).

**P7 - Keine Zahl bei k < 2.** Kein gepoolter Wert, kein CI, kein "Trend". Bei
k = 2 waere I-Quadrat per Definition 0 - das muss dann dastehen, nicht als
Heterogenitaetsbefund verkauft werden.

## Was heute geschafft wurde

49 Commits, davon die letzten neun ausschliesslich Werkzeuge, Tests und
Dokumente. Die produktiven Ergebnisse:

| Bereich | Ergebnis | Beleg |
|---|---|---|
| PDF-Normalisierung | 18 verlorene Tabellenbloecke / 152 Zeilen gefunden, Tabellenschutz eingebaut; an 34 echten Texten danach **0 harte Fehler, 0 verlorene Tabellenzeilen, 0 veraenderte Ziffernfolgen** | `normalisierung_echte_texte_20261108.md`, Commits `6d9812c`, `990b42d` |
| Schwellenrechnung | k >= 5 aus fuenf Artikeln widerlegt (unter 1 Prozent), zweistufiges Ziel eingefuehrt | `schwelle_k5_20261108.md`, `5b3a0c3` |
| Triage-Ablauf | `scripts/triage_lieferung.py`: ein Befehl liest PDFs, ordnet je Datei einen Zustand zu und schreibt k fort; leerer Ordner liefert Exit 2 mit Bericht | `e43c050`, `0ed922c`, `54e3e47` |
| Plausibilitaetspruefung | `scripts/pruefe_lieferung.py`: rechnet k nach, vergleicht Ausbeute mit p = 0,20, meldet Abweichungen und Luecken | `34e6472` |
| Lieferung simuliert | 4 Pruef-PDFs unter A-PMIDs: 3 poolbar, 1 Scan, k 1 -> 4 (SIMULATION, kein Studienbefund) | `46d5ab0`, `f66be18` |
| Bestellanfrage | von sechs Platzhaltern auf zwei reduziert (Name, Einrichtung); Betrag, Kostenstelle, Telefon, E-Mail entfallen durch Formulierung | `309002e` |
| Fernleih-Kurzfassung | Feldliste und Ein-Satz-Variante fuer Formulare ohne Anschreiben | `b866f75` |
| Stand-Dokumente | Ein-Seiten-Fassung und dieses Dokument | `8beb196` |

Tests: 35 gruen fuer PDF-Kette und Triage, 23 fuer Triage und Pruefung. Lint
nicht gelaufen - `ruff` ist im Venv nicht installiert.

## Was heute nicht passiert ist

- Kein neues Dokument gelesen, **k unveraendert 1**.
- Kein Netzlauf (Korpus offline ausgeschoepft, Netzlaeufe brauchen Freigabe).
- Keine gepoolte Zahl, kein Bericht mit Ergebnis - dafuer fehlt Material.

## Naechste Entscheidung

1. **A + B bestellen (25 Dokumente), nicht nur die fuenf.** Mit fuenf ist die
   erwartete Ausbeute eine poolbare Studie (k = 2); fuer k >= 5 braucht es 25,
   Chance rund 58 Prozent.
2. **Bis zur Lieferung keine Software mehr.** Ein Schritt zaehlt nur, wenn er
   ein neues Dokument liest, eine gemessene Fehlerquelle schliesst oder k
   aendert. Alles andere ist Politur.
3. **Nach Eingang:** `triage_lieferung.py`, dann `pruefe_lieferung.py`.
4. **Wenn die Lieferung ausbleibt:** als "der Korpus gibt es nicht her"
   abschliessen, nicht durch weitere Vorbereitung offen halten.

## Grenzen dieser Darstellung

- k = 4 aus dem Simulationslauf ist kein Studienbefund, sondern ein Nachweis
  der Mechanik.
- p = 0,20 ist eine Annahme aus neun bzw. fuenf Dokumenten, keine Messung.
- Die 83 ungesehenen Dokumente koennten die Quote heben oder senken; k = 1 ist
  eine Untergrenze, kein Beweis fuer Evidenzmangel.
