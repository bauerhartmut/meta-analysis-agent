# Stand in einer Seite

Stand: 2026-11-08. Alle Zahlen stammen aus den genannten Dateien; nichts
geschaetzt. Langfassung: `stand_melatonin_20261108.md`.

## Frage

Kann der Agent aus guten Primaerstudien eine Metaanalyse bauen - messbar an der
Zahl poolbarer Studien (k), nicht an der Zahl gebauter Werkzeuge?

## Antwort heute

**Noch nicht, und der Grund ist Material, nicht Methode.** k = 1: eine Studie
(PMC3489506) mit zwei Zeilen, g = -0,644 (SE 0,193, n = 113) und g = -0,685
(SE 0,294, n = 49). Eine gepoolte Zahl gibt es nicht, weil k < 2 - und es wird
keine berichtet.

## Kennzahlen

| Kennzahl | Wert | Quelle |
|---|---:|---|
| Q2-Treffer (streng) | 114 | `manifest_q2.json` |
| davon als XML gelesen | 31 | `extended.json` |
| ohne Volltext | 83 | `zugangsliste_20261108.csv` |
| davon Prioritaet A / B / C / D | 5 / 20 / 39 / 19 | ebd. |
| offline gelesene PDF-Volltexte | 34 (997.366 Zeichen) | `normalisierung_echte_texte_20261108.md` |
| **poolbare Studien (k)** | **1** | `extended.json` |
| gelieferte A-PDFs | **0** | `lieferung.json` |
| k nach Lieferung | 1 (unveraendert) | `lieferung_pruefung.json` |

## Was gemessen belegt ist

- **Korpus geschnitten**: 114 Treffer, 31 XML, 83 ohne Volltext, 80 mit DOI.
- **PDF-Kette liest**: an 34 echten Volltexten ohne harten Fehler, ohne
  verlorene Tabellenzeile, ohne veraenderte Ziffernfolge.
- **Triage** ordnet Datei, PMID, Prioritaet, Zustand und k in einem Lauf; an
  einer als Simulation gekennzeichneten Lieferung mit 4 Pruef-PDFs geprueft
  (3 poolbar, 1 Scan, k 1 -> 4).
- **Plausibilitaetspruefung** rechnet k nach und vergleicht die Ausbeute mit
  p = 0,20 aus der Schwellenrechnung; bei fehlender Lieferung meldet sie
  "leer" und Exit 2.
- **Crossover getrennt**: 4 von 9 Dokumenten mit SOL-Zeilen sind Crossover und
  werden nicht mit SE(g) fuer unabhaengige Gruppen gepoolt.
- **Keine Skalen geraten**: Wo die Einheit nicht in der Zeile steht, entsteht
  keine Zeile (der Annahme-Durchgang brachte 0 Zeilen und bleibt verworfen).

## Die offene Luecke

83 Dokumente ohne Volltext. Fuenf davon sind als Prioritaet A bestellt; die
Bestellanfrage liegt versandfertig vor (`bestellanfrage_20261108.md` fuer das
Anschreiben, `bestellanfrage_fernleihe_20261108.md` fuer das Formular). Offen
sind dort nur **Name** und **Einrichtung** in der Signatur. Kein PDF ist bisher
eingetroffen (`data/bench/sol2/volltext` enthaelt nur `.gitkeep`).

## Schwellen

| Ziel | Wert | Gilt fuer |
|---|---|---|
| Schritt-Ziel | k >= 2 | die fuenf bestellten Artikel |
| Gesamtziel | k >= 5 | A + B (25 Dokumente), ca. 58 % bei p = 0,20 |

Erwartungswert aus fuenf Artikeln: **eine** poolbare Studie, optimistisch zwei.
k >= 5 aus fuenf Artikeln ist praktisch ausgeschlossen (unter 1 %).

## Naechste Entscheidung

1. **Jetzt:** Signaturfelder fuellen, Fernleih-Formular abschicken. Das ist der
   einzige Schritt, der k bewegen kann.
2. **Nach Eingang:** `triage_lieferung.py`, dann `pruefe_lieferung.py` laufen
   lassen. Zwei Befehle, zwei Berichte.
3. **Bei k >= 2:** poolen (Hartung-Knapp-Sidik-Jonkman), k und I-Quadrat
   ausweisen, bei k = 2 ausdruecklich "I-Quadrat per Definition 0" schreiben.
4. **Bei k = 1:** B-Liste (20 Dokumente) bestellen oder die Untersuchung mit dem
   Befund abschliessen, dass der Berichtsstil der Literatur keine
   Arm-Mittelwerte traegt.

Nicht tun: weitere Leser-Regeln am alten Korpus. Vier gemessene Hebel brachten
dort bei der Einschaflatenz null.

## Reproduktion

```bash
.venv/bin/python.exe scripts/triage_lieferung.py \
  --dir data/bench/sol2/volltext \
  --json data/bench/sol2/lieferung.json \
  --md data/bench/sol2/lieferung.md
.venv/bin/python.exe scripts/pruefe_lieferung.py \
  --bericht data/bench/sol2/lieferung.json \
  --md data/bench/sol2/lieferung_pruefung.md \
  --json data/bench/sol2/lieferung_pruefung.json
```
