# SE-Fix in `parse_mean_spread`: Wirkung (2026-11-08)

Behoben wurde der Fehler aus `baseline_gate_befund_20261108.md`: Der Zweig fuer
`Wert +- Wert` gab die Streuungsart unbedingt als `sd` zurueck und verwarf damit
die Rolle aus dem Spaltenkopf. Ein Kopf "mean +- SE" wurde als
Standardabweichung gelesen.

## 1. Die Aenderung

In `research_agent/meta/arm_level.py`, `parse_mean_spread`:

- `has_sd` enthaelt das Zeichen "+-" nicht mehr (vorher war jedes "+-" ein SD).
- Der "+-"-Zweig prueft zuerst `has_se` (Zelle nennt SE), dann `has_sd`, dann
  die Rolle aus dem Kopf (`se` oder `sd`); Rolle `ci` gibt `None` zurueck, weil
  "+-" kein Intervall ist. Ohne Etikett bleibt es bei SD - die Konvention.

Tests: `research_agent/tests/test_se_role.py` (5 Faelle: Rolle `se`, ohne
Etikett, SD im Text schlaegt SE-Rolle, Rolle `ci`, ganzer Arm aus
"mean +- SE"-Kopf mit SD = SE * sqrt(n)). Die bestehenden Arm-Tests
(`test_arm_level.py`, `test_arm_level_pairs.py`) laufen unveraendert mit:
**40 passed**.

## 2. Wirkung auf die SOL-Zeilen: keine

Die 13 SOL-Zeilen des Korpus stammen **alle** aus dem Effektspalten-Leser; der
Arm-Leser steuert keine einzige bei. Der Fix kann dort also nichts veraendern:

| Stand | SOL-Zeilen | aus Arm-Leser |
|---|---:|---:|
| vor dem Fix (`zielmass_schnitt_label2`) | 13 | 0 |
| nach dem Fix (`zielmass_se`) | 13 | 0 |

Der Zielmass-Anteil sinkt nominal von 1,2 % auf 1,1 %, weil der Nenner waechst
(1.099 -> 1.161 Zeilen), nicht weil SOL-Zeilen wegfallen.

## 3. Der eine belegte Fall: Q1-Stichprobe

| | vorher | nachher |
|---|---:|---:|
| Hedges g "Sleep latency (min) by WA" | -2,162 | **-0,358** |
| Standardfehler | 0,2968 | 0,2377 |

Das entspricht der Vorhersage aus dem Baseline-Befund (-0,36) und belegt, dass
die Korrektur an der richtigen Stelle greift. Die Zeile selbst bleibt
unbrauchbar - sie stammt aus einer Baseline-Tabelle und wird vom noch fehlenden
Baseline-Gate nicht erfasst.

## 4. Nebenwirkung im Korpus - nicht sauber isoliert

Der Arm-Leser speicherte im Korpuslauf 97 Zeilen, nach dem Fix 161. Der
Verdacht lag nahe, dass Zellen mit "+-" und SE-Kopf vorher kein Zwei-Arm-Paar
ergaben. **Der Nachbau widerlegt das:** Fuer `PMC4069047` liefert der Leser
unter der alten wie unter der neuen "+-"-Regel je 32 Zeilen.

Damit ist der Zuwachs von 64 Zeilen **nicht** auf diese Aenderung
zurueckzufuehren; der frueher erzeugte Report
(`arm_level_label2_20261108.json`) ist als Vergleichsbasis unbrauchbar, weil er
nicht mit dem Code entstand, der heute im Repository liegt. Was den Unterschied
verursacht, ist offen und nicht Teil dieser Aenderung.

## 5. Was das fuer die Zielmass-Erweiterung heisst

Der Fix war noetig - ein Kopf "mean +- SE" darf nicht als SD gelesen werden,
sonst ist g um ein Vielfaches zu gross. Er aendert aber am SOL-Befund nichts:
Das Problem sind nicht die Streuungen der Arm-Zeilen, sondern die
13 Effektspalten-Zeilen, von denen eine aus einer Praediktortabelle und eine
aus einer Metaanalyse stammt (siehe `baseline_columns_gate_20261108.md`).

Reihenfolge bleibt daher: erst das Baseline-/Spalten-Gate und das Gate gegen
gepoolte Zeilen, dann ueber eine Erweiterung des Zielmasses entscheiden. Ohne
diese Gates wuerde eine Erweiterung auf "sleep latency" vor allem
Ausgangslagentabellen einsammeln.

## 6. Nachweise

| Datei | Inhalt |
|---|---|
| `research_agent/meta/arm_level.py` | korrigierter "+-"-Zweig |
| `research_agent/tests/test_se_role.py` | 5 Tests zur Streuungsart |
| `arm_level_se_20261108.json/.md` | Korpuslauf des Arm-Lesers mit Fix (161 Zeilen) |
| `arm_level_q1_se_20261108.json/.md` | Q1-Stichprobe mit Fix (14 Zeilen, g -0,358) |
| `zielmass_se_20261108.json/.md` | Korpus-Schnitt mit Fix (13 SOL-Zeilen) |
| `zielmass_q1_se_20261108.json/.md` | Q1-Schnitt mit Fix (0 SOL-Zeilen) |
