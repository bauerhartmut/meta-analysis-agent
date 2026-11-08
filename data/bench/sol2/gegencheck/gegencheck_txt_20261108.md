# Gegencheck auf den vorhandenen .txt-Texten

Stand: 2026-11-08T19:13:33. Verzeichnis: `data/bench/sol2/volltext`. Deterministisch, kein Netz, kein Modell.

Textquelle ist die bereits vorhandene `.txt`; ersetzt wird nur `read_pdf_corpus._pdf_to_text`, der Rest der Kette ist identisch. **vorher** = neue Erkennung aus, **nachher** = an.

## Gesamt

| Kennzahl | vorher | nachher |
|---|---:|---:|
| chars | 860834 | 860908 |
| blocks | 47 | 50 |
| arm_stored | 0 | 0 |
| direct_stored | 0 | 0 |
| rows | 0 | 0 |
| sol_rows | 0 | 0 |
| sol_poolable | 0 | 0 |
| Abweichungen | - | **2** |

## Je Datei

| Datei | Bytes | Zeichen | Bloecke | Arme | direkt | SOL | poolbar | Zustand |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 19030713.pdf | 0 | 29322 | 2 -> 2 | 0 -> 0 | 0 -> 0 | 0 -> 0 | 0 -> 0 | endpunkt_nicht_berichtet -> endpunkt_nicht_berichtet |
| 23098680.pdf | 0 | 831512 | 45 -> 48 | 0 -> 0 | 0 -> 0 | 0 -> 0 | 0 -> 0 | endpunkt_nicht_berichtet -> endpunkt_nicht_berichtet |

## Gegenueberstellung mit dem PDF-Lauf

| Datei | PDF: Bloecke | PDF: SOL | txt: Bloecke | txt: SOL |
|---|---:|---:|---:|---:|
| 19030713.pdf | 1 | 0 | 2 | 0 |
| 23098680.pdf | Fehler | - | 48 | 0 |

Der PDF-Lauf konnte `23098680.pdf` nicht lesen; die `.txt` daneben enthaelt 853 KB Text, der bislang ungenutzt war.

## Abweichungen

- `23098680.pdf`: chars 831512 -> 831586
- `23098680.pdf`: blocks 45 -> 48

## SOL-Zeilen im Detail (nachher)

- keine

## Warum `chars` und `blocks` steigen

`normalize()` in `meta/pdf_text.py` schuetzt erkannte Tabellenbereiche vor der Fliesstext-Verklebung (`_table_spans` -> `find_table_blocks`). Erkennt die neue Fassung mehr Bereiche, bleiben diese Zeilen roh stehen: Zeilenumbrueche und Bindestriche werden nicht aufgeloest, der Text wird laenger.

Der Effekt ist also nicht 'drei Tabellen mehr gefunden', sondern 'drei Bereiche ueberleben die Normalisierung und werden danach erkannt'. Kausal haengt beides aneinander: die Erkennung wirkt zweimal, einmal als Schutz in `normalize`, einmal als Leser in `find_table_blocks`.

Folge: `arm_stored`, `direct_stored` und `sol_rows` bleiben bei 0, aber der Fliesstext-Leser sieht bei `23098680.txt` anderen Text als vorher - das ist eine echte Verhaltensaenderung, keine Nullnummer.

## Grenzen

- Zwei `.txt`-Dateien; keine Aussage ueber Verlags-PDFs insgesamt.
- Die `.txt` stammt nicht aus pypdf, sondern aus einem frueheren, anderen Leseweg. Ihre Zeilenumbrueche sind daher nicht identisch mit dem, was die PDF-Kette produzieren wuerde.
- Der Vorher-Zustand kommt aus einem Monkeypatch (`_looks_columnar` -> False), nicht aus einem alten Code-Stand.
- Treffer hier sagen, was die Erweiterung auf diesem Text findet, nicht, dass sie in der Produktionskette ankommt - die liest weiterhin die PDF.
