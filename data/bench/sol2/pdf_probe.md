# PDF-Volltexte durch die Kette

Stand: 2026-11-08T13:10:41. Verzeichnis: `data/origpdf`. Deterministisch, kein Netz, kein Modell.

| Kennzahl | Wert |
|---|---:|
| PDFs gefunden | 3 |
| lesbar | 3 |
| gespeicherte Zeilen | 0 |
| davon Einschaflatenz | 0 |
| **k (PDFs mit poolbarer SOL-Zeile)** | **0** |

## Je PDF

| Datei | Zeichen | Arme | Bloecke | direkte Effekte | Zeilen | SOL |
|---|---:|---:|---:|---:|---:|---:|
| 09169ac90aa57bab.pdf | 49343 | 0 | 9 | 0 | 0 | 0 |
| 09d48d210903cc8b.pdf | 31785 | 0 | 3 | 0 | 0 | 0 |
| 21746b00d3a298a6.pdf | 53046 | 0 | 6 | 0 | 0 | 0 |

## Ablehnungsgruende

-   128  keine Effektspalte im Kopf
-     1  Kopfzeile (1 Spalten) passt nicht zur Zeile (11 Zellen) - co
-     1  Kopfzeile (1 Spalten) passt nicht zur Zeile (3 Zellen) - col
-     1  Kopfzeile (1 Spalten) passt nicht zur Zeile (10 Zellen) - co
-     1  Kopfzeile (1 Spalten) passt nicht zur Zeile (6 Zellen) - col
-     1  Kopfzeile (1 Spalten) passt nicht zur Zeile (4 Zellen) - col

## Grenzen

- PDF-Text hat keine Tabellenstruktur; Zwei-Arm-Tabellen werden nur
  gelesen, wenn ihre Zeilen als Textblock erkennbar sind.
- Gescannte PDFs ohne Textebene liefern nichts; das steht als
  'zu wenig Text' im Bericht.
