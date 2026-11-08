# PDF-Volltexte durch die Kette

Stand: 2026-11-08T13:53:12. Verzeichnis: `data/bench/sol2/probelauf`. Deterministisch, kein Netz, kein Modell.

| Kennzahl | Wert |
|---|---:|
| PDFs gefunden | 4 |
| lesbar | 3 |
| gespeicherte Zeilen | 3 |
| davon Einschaflatenz | 3 |
| **k (PDFs mit poolbarer SOL-Zeile)** | **3** |

## Je PDF

| Datei | Zeichen | Arme | Bloecke | direkte Effekte | Zeilen | SOL |
|---|---:|---:|---:|---:|---:|---:|
| probe_artikel_1.pdf | 1883 (kurz) | 1 | 0 | 0 | 1 | 1 |
| probe_artikel_2.pdf | 1741 (kurz) | 1 | 0 | 0 | 1 | 1 |
| probe_artikel_3_kurz.pdf | 618 (kurz) | 1 | 0 | 0 | 1 | 1 |
| probe_scan.pdf | 0 | - | - | - | - | - |

## Ablehnungsgruende

-     3  kurzer Text (unter min-chars, trotzdem gelesen)
-     1  kein Textlayer (Scan oder kaputt)

## Grenzen

- PDF-Text hat keine Tabellenstruktur; Zwei-Arm-Tabellen werden nur
  gelesen, wenn ihre Zeilen als Textblock erkennbar sind.
- Gescannte PDFs ohne Textebene liefern nichts; das steht als
  'kein Textlayer' im Bericht.
- Texte unter --min-chars werden gelesen und als 'kurzer Text'
  gezaehlt, nicht als Scan abgetan.
