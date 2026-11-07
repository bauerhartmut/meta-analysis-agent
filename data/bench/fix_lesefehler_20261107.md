# Drei Lesefehler geschlossen: Modelltabellen, Skala, gepoolte Werte

Stand: 07.11.2026. Aenderung in `research_agent/meta/effect_columns.py`,
Tabellenfilter im Lauf-Skript `scripts/read_effect_columns_xml6.py`.

## Was jetzt abgelehnt wird

1. **Modelltabellen.** Eine Zeile `(Intercept)` beweist eine Regression;
   damit werden alle Zeilen der Tabelle verworfen (`is_model_table`).
   Einzeln erkannte Intercept-Zeilen tragen den Grund
   "Modelltabelle (Intercept-Zeile), keine Behandlungseffekte".
2. **Skala nicht benannt.** `Effect size (95% CI)` ist kein Effekttyp mehr.
   Gueltig bleibt `Effect size (Hedges g, ...)`, `Cohen's d`, und
   `standardized effect size` -> `smd`.
3. **Gepoolte Schaetzung.** KPI `Pooled effect`, `Leave-one-out`,
   `Random-effects`, `Meta-analysis`, `overall/summary estimate` werden
   als Metaanalyse-Ergebnis abgelehnt, nicht als Studienzeile gespeichert.

## Wirkung, gemessen an beiden Korpora

| Korpus | Effekte vorher | nachher | Modelltabellen (Zeilen) | Gruppen | k >= 2 |
|---|---:|---:|---:|---:|---:|
| SOL, 100 XML | 47 | 15 | 2 (32) | 15 | 0 |
| Melatonin, 43 XML | 31 | 31 | 5 (26) | 19 | 0 |

SOL: 47 -> 15 Zeilen, alle vom Typ g aus
einer sauberen Effekttabelle (`Hedges g (95% CI)`, eigene CIs je Zeile).
Die 16 Minutenwerte aus `Effect size (95% CI)`, die 11 Regressionszeilen und
die 5 gepoolten Werte sind nicht mehr dabei.
Der 43er-Korpus bleibt bei 31 Zeilen: dort war keine der
drei Fehlerquellen enthalten.

Tests: 39 passed (test_effect_columns + test_jats_tables).

## Was offen bleibt

* Kovariaten ohne Intercept-Zeile (nur `Age`, `Sex`) sind von einem
  Behandlungseffekt nicht unterscheidbar; die Tabellenregel braucht die
  Intercept-Zeile als Beweis.
* Outcome-Namen bleiben studienspezifisch: k >= 2 entsteht auch nach der
  Reparatur nicht, weil `Sleep onset latency, min` und `Sleep latency (min)`
  verschiedene Labels sind und die Gruppen exakt matchen.

