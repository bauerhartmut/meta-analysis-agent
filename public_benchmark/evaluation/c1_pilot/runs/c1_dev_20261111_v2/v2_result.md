# Prompt v2: Testresultat

Run: `c1_dev_20261111_v2`
Prompt: `c1-dev-extract-v2`
Modell: `gwdg/qwen3.5-397b-a17b`, Temperatur 0, 26 Dev-Records

## Ergebnis

| Kennzahl | v1 | v2 |
|---|---:|---:|
| Ausgabezeilen | 26/26 | 26/26 |
| exakte Treffer | 93/140 (66,4 %) | 93/140 (66,4 %) |
| Abdeckung | 136/140 | 136/140 |
| falsch | 43 | 43 |
| fehlend | 4 | 4 |
| halluziniert | 0 | 0 |
| MAE | 4,7066 | 4,6404 |
| Parse-/Schemafehler | 0 | 0 |

Die niedrigere MAE ist kein Qualitätsgewinn: Sie entsteht dadurch, dass Record
120 eine andere falsche Ergebniszeile wählt. Die Zahl der exakten Treffer ist
unverändert.

## Was sich geändert hat

- **224–238:** unverändert. Das Modell wählt weiterhin den 4-Monats-Follow-up
  statt des Post-Tests; die 39 Zeitpunktfelder bleiben falsch.
- **120:** v1 wählte Rezidiv `0/30 vs. 1/52`, v2 wählt Extravasation
  `2/30 vs. 8/52`. Die Referenz bleibt die DTPA-Subgruppe `8/20 vs. 13/44`;
  beide Ausgaben sind falsch.
- **190:** unverändert `null`; die direkt berichteten Counts `52/125` und
  `51/133` werden weiterhin nicht extrahiert.
- **Alle übrigen Records:** unverändert.

## Bewertung

Die Zeitpunktregel ist im Prompt codiert, wird vom Modell aber nicht
umgesetzt. v2 ist damit **keine Verbesserung** und keine Grundlage für eine
Testfreigabe. Der historische v1-Lauf bleibt der belastbare Messpunkt.

Ein v3-Prompt muss die Zeitpunktwahl expliziter machen, zum Beispiel:

- eine vorhandene Spalte mit der wörtlichen Bezeichnung `Post-test` immer
  Vorrang vor `Follow up` geben;
- den gesuchten Spaltenkopf zuerst isoliert identifizieren und erst danach die
  Armwerte lesen;
- `source_note` mit dem wörtlichen Spaltenkopf beginnen lassen.

Das ist eine Hypothese für den nächsten Dev-Test, kein belegter Fix. Der
Testsplit wurde nicht gelesen oder verwendet.
