# Paket C, Schritt 1: mehrzeilige Kopfzeilen (2026-11-08)

Frage: Wie viel Ausbeute geht verloren, weil der Tabellenleser nur die erste
Kopfzeile liest und `colspan`/`rowspan` im Kopf nicht aufloest?

## Aenderung

`research_agent/research/jats_tables.py`:

- Der Kopf wird aus **allen** Zeilen des `thead` gebaut (ohne `thead`: aus den
  fuehrenden reinen `th`-Zeilen), nicht mehr nur aus der ersten Zeile.
- `colspan` breitet eine Kopfzelle auf ihre Spaltenbreite aus, `rowspan` traegt
  ihre Beschriftung in die naechste Kopfzeile.
- Je Datenspalte wird der Pfad gebildet ("Treatment Mean", "Placebo SD").
- Eine Kopfzeile mit genau einer Zelle ueber eine Spalte, der weitere
  Kopfzeilen folgen, gilt als Tabellentitel und wird verworfen.
- **Datenzellen bleiben woertlich und unexpandiert.** Eine zusammengefasste
  Datenzelle wird nicht verdoppelt (sonst wuerden Werte erfunden), und die
  Zeile bleibt als Zitat ein Teilstring des Dokumenttexts. Solche Zeilen
  fallen weiter im Abgleich Kopfbreite/Zellenzahl auf.

## Messung mit dem Funnel (1.056 XML, offline)

| Stufe | vorher | nachher | Delta |
|---|---:|---:|---:|
| Dokumente | 1.056 | 1.056 | 0 |
| SOL-Kandidaten | 946 | 946 | 0 |
| Tabellen | 2.735 | 2.735 | 0 |
| Tabellenzeilen | 42.771 | 41.821 | -950 |
| Kandidaten (Effekte) | 539 | 1.115 | **+576** |
| gespeichert (DBs) | 523 | 523 | 0 |
| poolbar (Zeilen) | 152 | 152 | 0 |

Leser im Einzelnen:

| Leser | Effekte vorher | nachher |
|---|---:|---:|
| Effektspalten | 529 | 1.016 |
| Arm-Tabelle | 8 | 97 |
| Fliesstext | 1 | 1 |
| Veraenderung | 1 | 1 |

Die 950 Zeilen weniger sind keine verlorenen Daten: das sind Kopfzeilen, die
vorher als Datenzeilen gezaehlt und dort scheiterten.

Verteilung: 33 Dokumente gewinnen Kandidaten, 1 verliert einen
(`PMC13104238`). Groesste Zunahmen: `PMC12013145` (0 -> 104),
`PMC13155930` (0 -> 72), `PMC9570822` (8 -> 54).

## Stichprobe (Qualitaetsgate)

`PMC12013145` hat jetzt einen 11-spaltigen Kopf
(`Crude model OR (95% CI)`, `Model 1 OR`, `Model 2 OR`, `Model 3 OR`) und
Datenzeilen mit 11 Zellen; je Zeile werden vier OR gelesen, jeder Punktwert
liegt im eigenen Intervall. Die Zahlen stammen aus den Zellen, nichts ist
ergaenzt.

Grenze der Stichprobe: das Outcome-Label dieser Tabelle ist "T2"/"T3", weil die
erste Zelle (rowspan der Krankheitsgruppe) leer ist. Die Spaltenzuordnung ist
korrekt, die Beschriftung des Outcomes aber unbrauchbar - offener Punkt.

## Was diese Zahl nicht ist

Die 1.115 Kandidaten sind **Lesepotenzial**, nicht gespeicherte Effekte. Die
Datenbanken sind unveraendert (523 Zeilen), weil der Funnel nur liest; ein
Konverterlauf, der die neuen Zeilen speichert, ist ein eigener Schritt mit
eigenen Pruefungen (Zitat-Gate, Plausibilitaet, Abhaengigkeiten).

## Tests

- `research_agent/tests/test_jats_tables.py`: fuenf neue Tests
  (zwei Kopfzeilen zusammengesetzt, Titelzeile verworfen, Datenzeilen nicht im
  Kopf, Zellenzahl gleich Kopfbreite, zusammengefasste Datenzelle bleibt eine
  Zelle).
- `pytest test_jats_tables.py test_effect_columns.py test_xml_first_fulltext.py`
  -> 51 passed.

Gesamtsuite (ohne `test_funnel_sol.py`): 1154 passed, 2 skipped in 695 s -
keine Regression durch den neuen Kopfaufbau.
