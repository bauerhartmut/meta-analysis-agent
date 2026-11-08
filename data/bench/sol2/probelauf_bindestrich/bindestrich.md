# PDF-Volltexte durch die Kette

Stand: 2026-11-08T13:53:13. Verzeichnis: `data/bench/sol2/probelauf_bindestrich`. Deterministisch, kein Netz, kein Modell.

| Kennzahl | Wert |
|---|---:|
| PDFs gefunden | 1 |
| lesbar | 1 |
| gespeicherte Zeilen | 1 |
| davon Einschaflatenz | 1 |
| **k (PDFs mit poolbarer SOL-Zeile)** | **1** |

## Je PDF

| Datei | Zeichen | Arme | Bloecke | direkte Effekte | Zeilen | SOL |
|---|---:|---:|---:|---:|---:|---:|
| probe_bindestrich.pdf | 1195 (kurz) | 1 | 0 | 0 | 1 | 1 |

## Ablehnungsgruende

-     1  kurzer Text (unter min-chars, trotzdem gelesen)

## Grenzen

- PDF-Text hat keine Tabellenstruktur; Zwei-Arm-Tabellen werden nur
  gelesen, wenn ihre Zeilen als Textblock erkennbar sind.
- Gescannte PDFs ohne Textebene liefern nichts; das steht als
  'kein Textlayer' im Bericht.
- Texte unter --min-chars werden gelesen und als 'kurzer Text'
  gezaehlt, nicht als Scan abgetan.
