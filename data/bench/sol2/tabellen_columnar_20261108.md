# Tabellen ohne Trennzeichen: Erweiterung und Messung

Stand: 2026-11-08. Anlass: Der Testfall der Lieferungs-Pipeline zeigte, dass
eine SOL-Zeile in einer Tabelle, die nur durch Spaltenabstand getrennt ist,
gar keinen Block ergab (`blocks = 0`) und deshalb als
`endpunkt_nicht_berichtet` gemeldet wurde - obwohl der Endpunkt berichtet war.

## Die Aenderung

`research_agent/research/table_extractor.py`, zwei additive Stellen:

1. `column_cells(line)` trennt eine Zeile an Laeufen von mindestens zwei
   Leerzeichen. `_looks_columnar(line)` akzeptiert sie als Tabellenzeile, wenn
   sie hoechstens 200 Zeichen lang ist, mindestens zwei Zellen hat, keine Zelle
   laenger als 45 Zeichen ist und die Zeile mindestens zwei Ziffern traegt.
2. Im Caption-Pfad von `find_table_blocks`: ein Block entsteht zusaetzlich,
   wenn mindestens zwei Spaltenzeilen und mindestens zwei Zeilen vorliegen.

Die Ziffernpruefung zaehlt Ziffern in der ganzen Zeile, nicht Zellen mit
Ziffern. Grund: Eine gewoehnliche Zwei-Spalten-Tabelle ist "Label | Wert"; nur
eine der beiden Zellen traegt Zahlen. Eine erste Fassung verlangte zwei
Zellen mit Ziffern und erkannte deshalb genau diesen Fall nicht - der Testfall
blieb bei `blocks = 0`.

## Messung 1: Testfall

`scripts/test_pipeline_lieferung.py`, derselbe Aufbau wie zuvor:

| Fall | vorher | nachher |
|---|---|---|
| Tabelle ohne Pipes | `blocks = 0`, `sol_rows = 0` | `blocks = 1`, `sol_rows = 1` |
| Zustand der Datei | `endpunkt_nicht_berichtet` | `sol_nicht_poolbar` |
| Erwartungen erfuellt | 16 von 17 | 17 von 17 |

Der Pipe-Fall, der poolbare Arm-Satz, der Scan, das fehlende PMID und die
Exit-Codes 0/1/2 bleiben unveraendert.

## Messung 2: Regression auf echten PDFs

39 Dateien (36 aus `data/origpdf`, 3 aus `data/bench/sol2/volltext`), gleiche
Kette (`_pdf_to_text` -> `normalize` -> `find_table_blocks`):

| Kennzahl | vorher | nachher |
|---|---:|---:|
| Dateien | 39 | 39 |
| Bloecke | 164 | 164 |
| Effektzellen | 13 | 13 |
| geaenderte Dateien | - | **0** |

Die Erweiterung aendert auf dem vorhandenen Bestand nichts. Das ist erwartbar:
Die pypdf-Extraktion liefert Tabellenzeilen dort bereits ohne
Spaltenabstaende, die Zeilen sind vorher zerfallen. Belege:
`tabellen_baseline.json`, `tabellen_nachher.json`.

## Messung 3: Unit-Tests

```
pytest research_agent/tests/test_table_extractor.py \
       research_agent/tests/test_golden_tables.py \
       research_agent/tests/test_pdf_text_tables.py -q
24 passed
```

## Grenzen

- Nur der Caption-Pfad ist erweitert. Eine Tabelle ohne Caption, die nur ueber
  Spaltenabstand zusammenhaelt, wird weiterhin nicht erkannt; der Pipe-Zweig
  (drei tabulare Zeilen ohne Caption) bleibt unveraendert.
- `_looks_columnar` ist bewusst eng (kurze Zellen, zwei Ziffern). Eine Tabelle
  aus reinen Textspalten ohne Zahlen wird nicht erfasst - dort gibt es aber
  auch keinen poolbaren Effekt zu verlieren.
- Der Layout-Adapter (`pdf_page_blocks`) ist unberuehrt; er arbeitet auf
  `extraction_mode="layout"` und hatte die Zellteilung bereits.
- Die Regression ist eine Stichprobe von 39 Dateien, kein Beweis fuer alle
  kuenftigen Verlags-PDFs.
