# PDF-Volltexte durch die Kette

Stand: 2026-11-08T13:16:31. Verzeichnis: `data/bench/sol2/scanprobe`. Deterministisch, kein Netz, kein Modell.

| Kennzahl | Wert |
|---|---:|
| PDFs gefunden | 1 |
| lesbar | 0 |
| gespeicherte Zeilen | 0 |
| davon Einschaflatenz | 0 |
| **k (PDFs mit poolbarer SOL-Zeile)** | **0** |

## Je PDF

| Datei | Zeichen | Arme | Bloecke | direkte Effekte | Zeilen | SOL |
|---|---:|---:|---:|---:|---:|---:|
| scan_seite1.pdf | 0 | - | - | - | - | - |

## Ablehnungsgruende

-     1  zu wenig Text (Scan oder kaputt)

## Grenzen

- PDF-Text hat keine Tabellenstruktur; Zwei-Arm-Tabellen werden nur
  gelesen, wenn ihre Zeilen als Textblock erkennbar sind.
- Gescannte PDFs ohne Textebene liefern nichts; das steht als
  'zu wenig Text' im Bericht.
