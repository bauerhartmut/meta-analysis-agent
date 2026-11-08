# E1 - MENDS-Extraktion durch den Harness

Stand: 2026-11-08T19:25:06+00:00. Test-ID `E1-extraktion-20261108`.
Eingabe: `data/bench/sol2/volltext/23098680.txt` (831660 Zeichen normalisiert, 48 Tabellenbloecke). Modellaufrufe: keine. Netz: keines.

## Soll gegen Ist

| Effekt | Soll | Toleranz | Gefunden | Ergebnis |
|---|---:|---:|---|---|
| MENDS-Tagebuch | -37.49 min | 0.01 | - | **FAIL** |
| MENDS-Aktigraphie | -45.34 min | 0.01 | - | **FAIL** |

## Was die Leser geliefert haben

- `text_arm_candidates`: 0 Kandidaten
- `change_candidates`: 0 Kandidaten
- Tabellenpfad (`effects_from_row`): 0 direkte Effekte aus 48 Bloecken

Ablehnungsgruende des Tabellenpfads:

| Grund | Anzahl |
|---|---:|
| `keine Effektspalte im Kopf` | 378 |
| `Kopfzeile (2 Spalten) passt nicht zur Zeile (1 Zellen) - col` | 53 |
| `Kopfzeile (8 Spalten) passt nicht zur Zeile (3 Zellen) - col` | 25 |
| `Kopfzeile (4 Spalten) passt nicht zur Zeile (1 Zellen) - col` | 20 |
| `Kopfzeile (1 Spalten) passt nicht zur Zeile (2 Zellen) - col` | 19 |
| `Kopfzeile (8 Spalten) passt nicht zur Zeile (7 Zellen) - col` | 18 |
| `Kopfzeile (8 Spalten) passt nicht zur Zeile (4 Zellen) - col` | 13 |
| `Kopfzeile (2 Spalten) passt nicht zur Zeile (9 Zellen) - col` | 13 |
| `Kopfzeile (8 Spalten) passt nicht zur Zeile (1 Zellen) - col` | 11 |
| `Kopfzeile (8 Spalten) passt nicht zur Zeile (6 Zellen) - col` | 10 |

## Fehlerbeschreibung

- **MENDS-Tagebuch**: Wert -37.49 steht in 4 Textzeile(n) (125, 413, 1729, 1769), in 1 erkannten Tabellenblock/Bloecken. Gefunden: 0.
  - Zelle `-37.49 (-55.27 to -19.71)` in Block 6; `parse_effect_cell` -> (-37.49, -55.27, -19.71); Kopfzelle `(SD)` -> Effektspalte: False.
- **MENDS-Aktigraphie**: Wert -45.34 steht in 4 Textzeile(n) (126, 415, 1730, 1776), in 1 erkannten Tabellenblock/Bloecken. Gefunden: 0.
  - Zelle `-45.34 (-68.75 to -21.93)` in Block 6; `parse_effect_cell` -> (-45.34, -68.75, -21.93); Kopfzelle `571.26 (71.98)` -> Effektspalte: False.

## Korrektur am Bericht

- **Befundtext im Erstlauf**: Der erste Bericht behauptete, der Wert stehe nur im Fliesstext und ein Satz sei kein Tabellenblock. Die Messung widerlegt das: -37.49 und -45.34 stehen in Block 6 als Wert mit Intervall in einer Zelle (`-37.49 (-55.27 to -19.71)`). Korrigiert ist die Ursachenangabe, nicht das Messergebnis (0 Treffer).

## Befund

0 von 2 Effekten wurden von keinem Leser gefunden. 2 von 2 stehen jedoch als Wert mit Intervall in einer Tabellenzelle und sind mit `parse_effect_cell` lesbar; der Tabellenleser erreicht sie nicht, weil die zugehoerige Kopfzelle keine Effektspalte ist (`header_effect_kind` False). Der Blocker sitzt damit in der Kopfzeilenerkennung, nicht im Fehlen der Daten - der Effekt steht zusaetzlich als Satz im Fliesstext, aber er steht auch in der Tabelle.

## Grenzen

- Geprueft ist der deterministische Lesepfad. Der LLM-Extraktor (`EffectExtractor`) wurde nicht aufgerufen (keine Modellaufrufe ohne Freigabe); er ist der naechste Schritt, nicht dieser.
- Eingabe ist die lokale Textebene (`23098680.txt`), nicht das PDF. Die Produktionskette liest das PDF; der Text ist dessen Extrakt.
- Ein FAIL hier heisst: dieser Lesepfad findet die Zahl nicht. Es heisst nicht, dass die Zahl im Dokument fehlt.

## Reproduktion

```bash
export PYTHONIOENCODING=utf-8
.venv/bin/python.exe scripts/validate_extraction_e1.py
```

Laufzeit: 0.981 s. Gesamtergebnis: **FAIL**.
