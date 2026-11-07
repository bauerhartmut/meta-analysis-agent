# Gate auf Spalten- und Zeitpunktebene gegen Baseline-Werte (2026-11-08)

Das Caption-Gate aus `baseline_gate_befund_20261108.md` war zu grob: Es haette
bei `10.1111/jsr.70311` vier brauchbare SOL-Zeilen mit verworfen, weil dort
Baseline- und 6-Monats-Spalten in derselben Tabelle stehen. Dieses Gate prueft
deshalb die **Spalten**, aus denen der Effekt gebildet wurde.

## 1. Regeln

Eine Spalte gilt als Ausgangswert, wenn ihr Kopf nennt:

- `Baseline`, `Baseline Mean (SD)`, `At baseline`
- `Pre-treatment`, `Pre-dose`, `Vor der Intervention`
- `Day 0`, `Week 0`, `T0`

Nennt der Kopf keinen Zeitpunkt, zaehlt die Zwischenueberschrift der Zeile
(`row_group`), etwa eine Sektionszeile "Baseline" ueber Spalten "Mean (SD)".
Ein Kopf mit eigenem Zeitpunkt (`6 months`, `Change`, `Follow-up`) schlaegt die
Zwischenueberschrift.

Daraus folgen zwei Ablehnungsgruende:

| Fall | Grund |
|---|---|
| alle verwendeten Spalten sind Ausgangswerte | "Baseline-Spalte (vor Intervention) - kein Behandlungseffekt" |
| nur ein Teil ist Ausgangswert | "gemischte Zeitpunkte (Baseline und Follow-up) - kein Behandlungseffekt" |

Eine Zeile ohne Baseline-Spalte wird **nie** allein wegen ihrer Caption
verworfen.

## 2. Einbau

- Neues Modul `research_agent/meta/baseline_columns.py` mit `baseline_columns`
  und `baseline_violation`.
- `arm_level.arms_from_row` prueft die Spalten der gewaehlten Arme; dafuer
  bekommt die Funktion und `convert_row` einen Parameter `row_group`.
- `effect_columns.effects_from_row` sammelt die Spalten, aus denen die Effekte
  gelesen wurden, und prueft dieselben Regeln.

## 3. Tests

`research_agent/tests/test_baseline_columns.py` (5 Faelle): Baseline-Spalten
werden erkannt, die adjustierte Differenz derselben Tabelle nicht, gemischte
Zeitpunkte werden abgelehnt, `Day 0` zaehlt als Ausgangswert, die
Zwischenueberschrift wirkt nur bei einem Kopf ohne Zeitpunkt.

Zusammen mit den Arm-, Effektspalten-, JATS- und SE-Tests: **100 passed in
1,88 s**.

## 4. Wirkung im Korpus

| Leser | Zeilen vorher | Zeilen nachher | SOL vorher | SOL nachher |
|---|---:|---:|---:|---:|
| Effektspalten | 1.000 | **987** | 13 | **13** |
| Arm-Deskriptiva | 161 | **159** | 0 | **0** |
| Summe | 1.161 | 1.146 | 13 | 13 |

Ablehnungen mit neuem Grund:

- Effektspalten: 12 Zeilen "Baseline-Spalte".
- Arm-Deskriptiva: 24 Zeilen "Baseline-Spalte", 347 Zeilen "gemischte
  Zeitpunkte"; die gespeicherte Zahl sinkt trotzdem nur um 2, weil die meisten
  dieser Zeilen schon vorher an anderen Gates scheiterten (Fallzahl,
  Spaltenpaarung).

Wichtig: **keine SOL-Zeile geht verloren.** Das Gate ist eng genug, um die
adjustierte Differenz in einer gemischten Tabelle zu behalten, und breit genug,
um 36 Zeilen zu verwerfen, die reine Ausgangswerte vergleichen.

## 5. Die 13 SOL-Zeilen nach dem Gate

| Quelle | Zeile | comparison | Urteil |
|---|---|---|---|
| `10.1001/jamanetworkopen.2026.26983` | g 0,07 | Hedges g (95% CI) | brauchbar |
| `10.1093/sleep/zsaa194` | -5,1 | Difference 95% CI | brauchbar |
| `10.1093/sleep/zsae250` | -4,2 / -2,3 / 1,3 | Main effect of trial, Mean difference (95% CI) | brauchbar |
| `10.1111/jsr.70311` | 3,8 / 3,4 / 5,7 / 4,6 | **Adjusted mean difference between groups** | brauchbar, Gate greift korrekt nicht |
| `10.2188/jea.je20140201` | -0,1 / -0,002 | Difference (CS - No CS, 95% CI) | brauchbar, Skala "log min" |
| `10.2147/nss.s460882` | OR 2,56 | A Better Outcome (n = 24), Multivariate OR | **Praediktortabelle, kein Behandlungseffekt** |
| `10.3389/fnins.2026.1816963` | MD 2,12 | MD [95%CI] in Metaanalyse-Tabelle | **gepoolte Zeile, keine Studie** |

Ergebnis: **11 von 13 brauchbar**, 2 offen - beide ausserhalb der
Baseline-Frage.

## 6. Was noch fehlt

1. **Praediktortabellen:** Spalten wie "A Better Outcome (n = 24)" benennen
   Gruppen nach dem Ergebnis, nicht nach der Intervention. Das Arm-Gate
   (`_INTERVENTION_ARM`) kennt den Fall, der Effektspalten-Leser nicht.
2. **Gepoolte Zeilen:** `MD [95%CI]` neben `I2` und `p` ist eine
   Metaanalyse-Schaetzung. Das Pooling-Gate erkennt diese Schreibweise nicht.
3. **Skalen:** `log min` und `min` stehen weiterhin nebeneinander; ein Pooling
   ueber beide waere falsch.

## 7. Grenzen

- Das Gate prueft Koepfe und Zwischenueberschriften, keine Zellwerte. Eine
  Spalte "Follow-up" mit einem Ausgangswert darin bleibt unentdeckt.
- Die Muster sind englisch/deutsch; anderssprachige Tabellen werden nicht
  erfasst.
- Die 36 abgelehnten Zeilen wurden nicht einzeln gesichtet; die Zahl stammt aus
  den Zaehlern der Konverter.
- Ein Baseline-Gate ersetzt keine Risiko-fuer-Verzerrung-Bewertung: es sagt
  nur, dass die Zeile einen Zustand nach der Intervention beschreibt.

## 8. Nachweise

| Datei | Inhalt |
|---|---|
| `research_agent/meta/baseline_columns.py` | Regeln und Ablehnungsgruende |
| `research_agent/tests/test_baseline_columns.py` | 5 Tests |
| `effect_columns_gate_20261108.json/.md` | Effektspalten-Leser mit Gate (987 Zeilen, 12 Baseline-Ablehnungen) |
| `arm_level_gate2_20261108.json/.md` | Arm-Leser mit Gate (159 Zeilen, 24 + 347 Ablehnungen) |
| `zielmass_gate_20261108.json/.md` | Schnitt mit Gate (13 SOL-Zeilen) |
