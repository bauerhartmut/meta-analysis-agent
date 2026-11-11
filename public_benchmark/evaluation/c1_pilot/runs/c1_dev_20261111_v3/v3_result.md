# Prompt v3: Testresultat

Run: `c1_dev_20261111_v3`
Prompt: `c1-dev-extract-v3`
Modell: `gwdg/qwen3.5-397b-a17b`, Temperatur 0, 26 Dev-Records

## Ergebnis

| Kennzahl | v1 | v2 | v3 |
|---|---:|---:|---:|
| Ausgabezeilen | 26/26 | 26/26 | 26/26 |
| exakte Treffer | 93/140 (66,4 %) | 93/140 (66,4 %) | **123/140 (87,9 %)** |
| Abdeckung | 136/140 | 136/140 | 134/140 (95,7 %) |
| falsch | 43 | 43 | **11** |
| fehlend | 4 | 4 | 6 |
| halluziniert | 0 | 0 | 0 |
| MAE | 4,7066 | 4,6404 | **0,234** |
| Parse-/Schemafehler | 0 | 0 | 0 |
| Records mit allen Feldern exakt | 14/26 | 14/26 | **22/26** |

v3 verbessert **32 der 39 Zeitpunktfelder**. Zugleich fehlen bei Record 226
zwei vorher korrekte Gruppengrößen, sodass die Zahl der exakten Felder netto
um 30 steigt. Das ist ein echter Fortschritt, aber noch keine Testfreigabe.

## Verbleibende Fehler

- **120 (4 falsch):** Das Modell wählt erneut die Extravasation-Zeile
  `2/30 vs. 8/52`; die Referenz ist die DTPA-Subgruppe `8/20 vs. 13/44`.
  Die ICO ist weiterhin unterspezifiziert.
- **224 (4 falsch):** Das Modell wählt den Follow-up `0,43 ± 1,04 / 1,19 ± 1,37`
  statt des Post-Tests `0,30 ± 0,79 / 0,38 ± 0,98`. Die `source_note` behauptet,
  die ICO nenne 4 Monate; das ist falsch.
- **226 (3 falsch, 2 fehlend):** Das Modell wählt den Follow-up für BMI und
  behauptet, der Post-Test sei leer. Die Quelle berichtet jedoch
  `25,78 ± 3,30 / 26,53 ± 3,53`; zusätzlich fehlen die Gruppengrößen 35/35.
- **190 (4 fehlend):** Das Modell wählt 3 Monate und liest dort nur
  Prozentwerte. Die Referenz verwendet 12 Monate mit den direkt berichteten
  Counts `52 (42)` und `51 (38)` sowie 125/133. Der Record braucht eine
  explizite Zeitpunktangabe; die bisherige „frühester Follow-up“-Regel greift
  hier zu kurz.

## Bewertung

Die explizite Spaltenpriorisierung und die Endprüfung wirken: Die Mehrheit der
Follow-up-Fehler ist beseitigt. v3 ist der bisher beste Kandidat, aber wegen
der vier offenen Records **nicht testreif**. Der Testsplit wurde nicht gelesen
oder verwendet.
