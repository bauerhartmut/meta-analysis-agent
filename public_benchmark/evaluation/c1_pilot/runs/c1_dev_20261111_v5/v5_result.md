# Prompt v5: Testresultat

Run: `c1_dev_20261111_v5`
Prompt: `c1-dev-extract-v5`
Modell: `gwdg/qwen3.5-397b-a17b`, Temperatur 0, 26 Dev-Records

## Ergebnis

| Kennzahl | v1 | v2 | v3 | v4 | v5 |
|---|---:|---:|---:|---:|---:|
| Ausgabezeilen | 26/26 | 26/26 | 26/26 | 26/26 | 26/26 |
| exakte Treffer | 93/140 | 93/140 | 123/140 | 126/140 | **136/140 (97,1 %)** |
| Abdeckung | 136/140 | 136/140 | 134/140 | 138/140 | **140/140 (100 %)** |
| falsch | 43 | 43 | 11 | 12 | **4** |
| fehlend | 4 | 4 | 6 | 2 | **0** |
| halluziniert | 0 | 0 | 0 | 0 | 0 |
| MAE | 4,7066 | 4,6404 | 0,234 | 0,3052 | 0,2714 |
| Records vollständig exakt | 14/26 | 14/26 | 22/26 | 22/26 | **25/26** |
| Parse-/Schemafehler | 0 | 0 | 0 | 0 | 0 |

Gegenüber v4 sind zehn Felder mehr exakt:

- 224: Post-Test statt Follow-up (+4)
- 226: Gruppengrößen 35/35 (+2)
- 238: `()69.89±1.59` wird als vorhandene Zelle gelesen (+4)

Record 190 bleibt mit dem 12-Monats-Override korrekt.

## Verbleibender Fehler

**Record 120, 4 falsch:** Das Modell wählt erneut die Rezidiv-Zeile
`0/30 vs. 1/52`; die Referenz ist die DTPA-Subgruppe `8/20 vs. 13/44`.
Die ICO „ureteropelvic junction obstruction“ legt weder Diagnostikweg noch
Ergebniszeile fest. Der Record wurde am 2026-11-11 adjudiziert: Ziel ist der
DTPA-Befund „partial obstruction“ (20/44 DTPA-untersuchte Patienten); die
Rezidivzeile ist ein anderes Outcome. Die Referenz bleibt unverändert, v5
bleibt bei 136/140. Details:
[`../adjudication_record_120.md`](../adjudication_record_120.md).

## Bewertung

v5 ist der erste Lauf mit vollständiger Abdeckung und ohne fehlende Felder.
Alle 22 zuvor offenen Zeitpunkt-/Zellfelder sind korrekt. Der einzige
verbleibende Fehler liegt in einem Record mit unterspezifizierter ICO.

Der Testsplit wurde nicht gelesen oder verwendet und bleibt gesperrt. Vor
einer Testfreigabe muss Record 120 entweder präzisiert, ausgeschlossen oder
vorab adjudiziert werden.
