# Gates gegen Praediktortabellen und gepoolte Zeilen (2026-11-08)

Nach dem Baseline-Gate blieben zwei der 13 SOL-Zeilen offen: eine
Praediktortabelle (OR 2,56) und eine gepoolte Metaanalyse-Zeile (MD 2,12).
Beide sind keine Behandlungseffekte einer Primaerstudie - aus
unterschiedlichen Gruenden.

## 1. Regeln

**Gepoolte Zeile** (`research_agent/meta/design_gates.py`):

- Caption nennt `meta-analysis`, `pooled estimate`, `random-effects model`
  oder `fixed-effects model`, **oder**
- der Kopf enthaelt ein Heterogenitaetsmass: `I 2`, `I-Quadrat`, `Tau 2`,
  `heterogeneity`, `Q statistic`.

Die zweite Regel ist die wichtigere: Metaanalyse-Tabellen heissen oft
"Subgroup analysis" oder "Safety outcomes analysis" und verraten sich nur
durch die I-Quadrat-Spalte.

Eine Zeile "Overall" in einer Studientabelle wird **nicht** verworfen - dort
fehlt der zweite Beleg.

**Praediktortabelle:**

- Der Kopf nennt Gruppen nach dem **Ergebnis**: `Better outcome`,
  `Worse outcome`, `Responder`, `Non-responder`, `Improved`, `Remitter`, **oder**
- die Caption nennt `predictor`, `determinant`, `risk factor`,
  `associated with`, `correlat` **und** der Kopf enthaelt
  `univariate`/`multivariate`/`crude OR`/`adjusted OR`.

Beide Gates laufen im Effektspalten-Leser vor der Suche nach Effektspalten;
der Arm-Leser braucht sie nicht, weil dort `_INTERVENTION_ARM` schon greift.

## 2. Tests

`research_agent/tests/test_design_gates.py` (5 Faelle): Metaanalyse-Zeile ueber
Caption und ueber I-Quadrat, Praediktortabelle, und zwei Gegenproben
(adjustierte Differenz in einer gemischten Tabelle, Veraenderungswerte mit SE).
Zusammen mit Baseline-, Arm-, Effektspalten-, JATS- und SE-Tests:
**105 passed in 1,88 s**.

## 3. Wirkung auf die SOL-Zeilen

| Stand | SOL-Zeilen | offene Zeilen |
|---|---:|---|
| vor den Gates | 13 | 2 |
| nach Baseline-Gate | 13 | 2 |
| nach Praediktor-/Pooling-Gate | **11** | **0** |

Entfernt wurden genau die beiden:

- `10.2147/nss.s460882`, OR 2,56 - "A Better Outcome (n = 24) Multivariate
  Effect Size OR (95% CI)": Gruppen nach Ergebnis, kein Behandlungseffekt.
- `10.3389/fnins.2026.1816963`, MD 2,12 - `MD [95%CI]` neben `I 2 (%)` in
  "Table 3 Meta-analysis of PSG of rTMS vs. Sham rTMS".

Keine der elf verbleibenden Zeilen wurde angetastet, insbesondere nicht die
vier adjustierten Differenzen aus `10.1111/jsr.70311`.

## 4. Wirkung im Korpus

| Kennzahl | vorher | nachher |
|---|---:|---:|
| gespeicherte Effektspalten-Zeilen | 987 | **838** |
| Kandidaten | 993 | 844 |
| OR | 391 | 319 |
| mean_diff | 278 | 228 |
| SMD | 19 | 4 |
| RR | 12 | 0 |
| beta / g / HR | 270 / 15 / 2 | unveraendert |

Abgelehnte Zeilen nach Grund (Zaehler ueber alle Tabellenzeilen, nicht nur
gespeicherte): **620 gepoolt**, **91 Praediktor**. Die Zahl ist groesser als
der Verlust von 149 Zeilen, weil das Gate vor der Effektpruefung greift: viele
dieser Zeilen waeren ohnehin an fehlender Effektspalte gescheitert, tragen jetzt
aber den zutreffenden Grund.

Haeufigste Captions der verlorenen Zeilen:

| Zeilen | Caption |
|---:|---|
| 48 | "Table 2 Multivariable logistic models examining evening eating associated with short sleep" |
| 19 | "Table 2 Predictors of hypomagnesemia" |
| 15 | "TABLE 2 Effect sizes of the subgroup analysis" (Metaanalyse, I-Quadrat im Kopf) |
| 13 | "Table 3 Sensitivity analysis ... of PSG" (Metaanalyse) |
| 12 | "Table 3 Safety outcomes analysis" (gepoolt) |
| 10 | "Table 4 Subgroup analysis for PSQI total scores ..." (Metaanalyse) |

Alle geprueften Faelle sind Modell-, Praediktor- oder Metaanalyse-Tabellen.

## 5. Was jetzt gilt

- **11 von 11 verbleibenden SOL-Zeilen sind Behandlungseffekte** aus
  Primaerstudien; keine ist mehr eine Baseline-, Praediktor- oder
  Metaanalyse-Zeile.
- Die Zahl der unabhaengigen Quellen sinkt von 7 auf **5**: die zwei
  entfernten Zeilen waren die einzigen ihrer Studien. k = 1 bleibt: Es gibt
  weiterhin keine Gruppe mit zwei unabhaengigen Studien auf derselben Skala.
- Offen bleibt allein die **Skalenfrage**: `10.2188/jea.je20140201` berichtet
  "log min", die uebrigen "min". Ein gemeinsamer Mittelwert ueber beide waere
  falsch; das ist eine Pooling-Entscheidung, kein Gate.

## 6. Grenzen

- Das Gate greift vor der Effektpruefung; der Grund "gepoolt" kann eine Zeile
  treffen, die ohnehin nicht speicherbar gewesen waere. Fuer die Frage "ist das
  ein Behandlungseffekt?" ist das unerheblich, fuer die Ausbeutezahl nicht.
- **Risiko Falsch-Positiv:** Eine Responder-Analyse in einer RCT ("Responder
  (n)", "OR (95% CI)") ist ein legitimer Behandlungseffekt, wird vom
  Ergebnis-Gruppen-Muster aber erfasst. Wie oft das im Korpus vorkommt, ist
  nicht gemessen; in den gesichteten Captions kam der Fall nicht vor.
- Die Muster sind englisch; anderssprachige Captions werden nicht erfasst.
- 149 verlorene Zeilen wurden nicht vollstaendig gesichtet, nur die haeufigsten
  Captions und fuenf Einzelfaelle.

## 7. Nachweise

| Datei | Inhalt |
|---|---|
| `research_agent/meta/design_gates.py` | Regeln und Gruende |
| `research_agent/tests/test_design_gates.py` | 5 Tests |
| `effect_columns_design_20261108.json/.md` | Effektspalten-Leser mit allen Gates (838 Zeilen) |
| `arm_level_gate2_20261108.json/.md` | Arm-Leser mit Baseline-Gate (159 Zeilen) |
| `zielmass_design_20261108.json/.md` | Schnitt mit allen Gates (11 SOL-Zeilen) |
