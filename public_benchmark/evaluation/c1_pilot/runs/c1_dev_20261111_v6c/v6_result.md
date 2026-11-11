# Prompt v6: Testresultat

Akzeptierte Revision: `c1_dev_20261111_v6c`
Prompt: `c1-dev-extract-v6`
Modell: `gwdg/qwen3.5-397b-a17b`, Temperatur 0, 26 Dev-Records

## Ergebnis

| Kennzahl | Wert |
|---|---:|
| Ausgabezeilen | 26/26 |
| exakte Treffer | **140/140 (100,0 %)** |
| Abdeckung | **140/140 (100,0 %)** |
| falsch | 0 |
| fehlend | 0 |
| halluziniert | 0 |
| MAE | 0,0 |
| Records vollständig exakt | 26/26 |
| Parse-/Schemafehler | 0 |

Record 120 ist vollständig korrekt: `8/20 vs. 13/44` mit den
Zeilendenominatoren 20/44. Record 226 verwendet die Post-test-Werte
`25,78 ± 3,30` vs. `26,53 ± 3,53`, nicht die 4-Monats-Follow-up-Werte.

## Regeln der akzeptierten Revision

- Outcome-Zeilen-Priorität: direkte Messung der genannten Erkrankung vor
  Komplikationen, Reoperationen und sekundären Ereignissen.
- Binäre Zeilen als `x/N`: N ist der Zeilendenominator, nicht die größere
  randomisierte Armgröße.
- Record 226: expliziter Post-test-Override gegen die separate
  4-Monats-Follow-up-Tabelle.

## Verworfene Zwischenläufe

| Lauf | Änderung | exakt | Abdeckung | Fehler |
|---|---|---:|---:|---|
| `c1_dev_20261111_v6` | erste Outcome-Regel | 135/140 | 140/140 | 5 falsch: 120-N, 226 |
| `c1_dev_20261111_v6b` | zusätzliche allgemeine Tabellenregel | 125/140 | 128/140 | 12 fehlend (230–232), 3 falsch (226) |

Die allgemeine Tabellenregel aus v6b wurde verworfen, weil sie bei 230–232
die Post-test-Zellen fälschlich als leer behandelte. Die binäre N-Regel und
der 226-Override wurden beibehalten.

Der Testsplit wurde nicht gelesen oder verwendet und bleibt gesperrt.
