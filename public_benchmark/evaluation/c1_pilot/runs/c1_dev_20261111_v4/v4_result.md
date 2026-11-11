# Prompt v4: Testresultat

Run: `c1_dev_20261111_v4`
Prompt: `c1-dev-extract-v4`
Modell: `gwdg/qwen3.5-397b-a17b`, Temperatur 0, 26 Dev-Records

## Ergebnis

| Kennzahl | v1 | v2 | v3 | v4 |
|---|---:|---:|---:|---:|
| Ausgabezeilen | 26/26 | 26/26 | 26/26 | 26/26 |
| exakte Treffer | 93/140 | 93/140 | 123/140 | **126/140 (90,0 %)** |
| Abdeckung | 136/140 | 136/140 | 134/140 | **138/140 (98,6 %)** |
| falsch | 43 | 43 | 11 | 12 |
| fehlend | 4 | 4 | 6 | **2** |
| halluziniert | 0 | 0 | 0 | 0 |
| MAE | 4,7066 | 4,6404 | 0,234 | 0,3052 |
| Parse-/Schemafehler | 0 | 0 | 0 | 0 |
| Records vollständig exakt | 14/26 | 14/26 | 22/26 | 22/26 |

Gegenüber v3 sind netto drei Felder mehr exakt: Record 190 (+4) und die
Mean/SD-Felder von Record 226 (+3) werden korrigiert; Record 238 fällt mit
vier Feldern neu auf Follow-up zurück.

## Was v4 geändert hat

- **190 vollständig korrekt:** Der 12-Monats-Override liefert
  `52/125` vs. `51/133` aus der Zeile `Sedatives`, Spalte
  `12 months follow-up`.
- **226 teilweise korrekt:** Mean/SD sind jetzt Post-Test
  `25,78 ± 3,30 / 26,53 ± 3,53`; die Gruppengrößen 35/35 fehlen weiterhin.
- **238 Regression:** Das Modell wählt Follow-up
  `83,1 ± 1,37 / 69,57 ± 1,61` statt Post-Test
  `80,5 ± 9,97 / 69,89 ± 1,59`. Die `source_note` behauptet, die
  Kontrollzelle des Post-Tests sei leer (`()69.89±1.59`), obwohl sie
  berichtet ist.
- **224 unverändert falsch:** Das Modell wählt Follow-up und behauptet
  erneut, die ICO nenne 4 Monate; die ICO nennt keinen Zeitpunkt.
- **120 unverändert falsch:** Extravasation `2/30 vs. 8/52` statt der
  DTPA-Subgruppe `8/20 vs. 13/44`; die ICO bleibt unterspezifiziert.

## Bewertung

v4 ist der bisher beste Kandidat, aber **nicht testreif**. Die Zellprüfung
hilft bei 190 und 226, verhindert aber falsche Leerzellen und erfundene
ICO-Zeitpunkte noch nicht zuverlässig. Offen sind 120, 224, 226 (zwei
Gruppengrößen) und 238. Der Testsplit wurde nicht gelesen oder verwendet.
