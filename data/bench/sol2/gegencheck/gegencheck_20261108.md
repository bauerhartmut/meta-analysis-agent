# Gegencheck: Spaltenabstands-Erkennung auf den vorhandenen Volltexten

Stand: 2026-11-08T18:51:22. Verzeichnis: `data/bench/sol2/volltext`. Deterministisch, kein Netz, kein Modell.

Verglichen wird dieselbe Lesekette zweimal: **vorher** mit abgeschalteter neuer Erkennung (`_looks_columnar` liefert False), **nachher** mit aktiver Erkennung.

## Gesamt

| Kennzahl | vorher | nachher |
|---|---:|---:|
| blocks | 1 | 1 |
| arm_stored | 0 | 0 |
| direct_stored | 0 | 0 |
| rows | 0 | 0 |
| sol_rows | 0 | 0 |
| sol_poolable | 0 | 0 |
| Abweichungen | - | **0** |

## Je Datei

| Datei | Bloecke | Arme | direkt | SOL-Zeilen | poolbar | Zustand |
|---|---:|---:|---:|---:|---:|---|
| 19030713.pdf | 1 -> 1 | 0 -> 0 | 0 -> 0 | 0 -> 0 | 0 -> 0 | endpunkt_nicht_berichtet -> endpunkt_nicht_berichtet |
| 23098680.pdf | None -> None | None -> None | None -> None | None -> None | None -> None | scan -> scan |
| 35120753.pdf | None -> None | None -> None | None -> None | None -> None | None -> None | scan -> scan |

## Belastbarkeit der Stichprobe

| Datei | Bytes | Kopf | echte PDF | txt daneben | durch Kette lesbar |
|---|---:|---|---|---:|---|
| 19030713.pdf | 464249 | `%PDF-1.3%âã` | ja | 30111 | ja |
| 23098680.pdf | 6001866 | `%PDF-1.6%âã` | ja | 853183 | nein |
| 35120753.pdf | 2737 | `<!DOCTY` | nein | 0 | nein |

- durch die Kette lesbar: 1 von 3
- ohne Aussage (kein Text aus der PDF gewonnen): 2
- mit mindestens einer SOL-Zeile: 0

Damit ist der Vergleich nur fuer die lesbaren Dateien aussagekraeftig. Wo `nein` steht, sagt 'keine Abweichung' nichts ueber die Erweiterung, sondern nur, dass die Kette diese Datei nicht liest.

## Abweichungen

- keine: die Erweiterung aendert an diesen Dateien nichts.

## SOL-Zeilen im Detail (nachher)

- keine

## Grenzen

- Drei Dateien, davon nur ein Teil durch die Kette lesbar; kein Beweis fuer Verlags-PDFs insgesamt.
- Der Vorher-Zustand wird ueber einen Monkeypatch hergestellt (`_looks_columnar` -> False), nicht ueber einen alten Code-Stand; alles andere an der Kette ist identisch.
- `arm_stored` stammt aus dem Fliesstext-Leser und ist von der Tabellenerkennung hoechstens mittelbar beruehrt.
- Eine vorhandene `.txt` neben einer PDF wird von der Kette nicht gelesen; wo nur sie Text enthaelt, bleibt die PDF eine Blindstelle.
