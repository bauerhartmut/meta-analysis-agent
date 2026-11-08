# E4c - doppelte Effektzeilen und das Pooling-Gewicht

Stand: 2026-11-08 23:11 · Modellaufrufe: 0 · Tokens: 0

Duplikat = gleiche Quelle, gleiche Quote, gleicher Effekt, gleiches KI,
gleicher Outcome. Read-only auf Kopien; gelesen wurde die Kopie.

| Gruppe | Dateien | Zeilen | Duplikat-Gruppen | ueberzaehlige Zeilen |
|---|---:|---:|---:|---:|
| themen | 9 | 201 | 61 | 64 |
| pipeline | 55 | 7254 | 120 | 122 |
| sonstige | 1 | 13 | 2 | 2 |

## Faengt das Pooling sie?

`build_analysis` hat in den 9 Themen-DBs 39 Zeilen vor dem Pool verworfen (`_collapse_same_study`, je Quelle und Outcome bleibt die praezisere).
Die Zaehlung findet 64 ueberzaehlige Zeilen bei 201 Zeilen mit Effekt - ueber alle Zeilen, auch solche, die nie in einen Pool kommen (k=1, kein Beleg). Die Differenz ist deshalb kein Rest an unentdeckten Dubletten.

## Was ohne den Kollaps passieren wuerde

Gemessen an echten Zeilen (`pool()` direkt, ohne `_collapse_same_study`), Gruppe `incident cardiovascular disease` [log_ratio] aus `data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db`:

| | mit Dublette | ohne Dublette |
|---|---:|---:|
| k | 6 | 5 |
| gepoolt | 0.295155 | 0.240297 |
| 95%-KI | [-0.304763; 0.895073] | [-0.524047; 1.004642] |
| KI-Breite | 1.199836 | 1.528689 |

Die Dublette haette 69.2% des Gewichts getragen (eigene Zeile plus ihr Zwilling). Verschiebung des Punktschaetzers: 0.054858. Genau das verhindert der Kollaps - die Zeile wird nicht zweimal gezaehlt.

## Grenzen

- Der Kollaps greift je Outcome-Gruppe. Zwei identische Zeilen unter
  verschiedenen Outcome-Schreibweisen landen in zwei Gruppen (je k=1)
  und werden nicht gepoolt - dort entsteht kein Gewichtsfehler, aber
  auch keine Analyse.
- `kollabiert` zaehlt auch legitime abhaengige Zeilen (Arme, Kontraste,
  zweite Lesung), nicht nur exakte Dubletten. Die Zahl ist eine
  Obergrenze fuer den Dubletten-Anteil, keine Dublettenzahl.
- Die Demo zeigt den Mechanismus an einer Gruppe; sie ist kein
  Schaetzer fuer den Effekt auf alle gepoolten Ergebnisse.
