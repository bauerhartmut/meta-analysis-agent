# Design- und Zeitpunkt-Gate im Arm-Rechner

Stand: 07.11.2026. Aenderung in `research_agent/meta/arm_level.py`;
gemessen offline ueber die 100 SOL-XML.

## Was jetzt abgelehnt bzw. mitgefuehrt wird

1. **Baseline-Zeilen.** Eine Spalte `Day`/`Week`/`Visit`/`Time point` mit
   Wert `0` oder `baseline` sowie eine Zeilenbeschriftung `Baseline`,
   `Day 0` oder `pre-...` ergibt den Grund "Baseline-Zeile (Tag 0 / vor
   Intervention) - kein Behandlungseffekt". `0.5 mg` ist kein Tag 0: das
   Muster verlangt den ganzen Zellwert.
2. **Querschnittsgruppen.** Benennen die Arme Gruppen ("Active children"
   vs. "Inactive children", "Patients" vs. "Healthy Controls") und
   keiner davon eine Intervention, wird die Zeile abgelehnt. Generische
   Etiketten wie `Mean (SD)` benennen nichts und werden nicht
   klassifiziert.
3. **Zeitpunkt.** `Day 30`, `Week 4` oder `post-BLT1` landen als
   `time_point` in der Zeile, statt in der Tabellen-Caption zu
   verschwinden; das Outcome kommt aus der Zeile, nicht aus der Caption.

## Wirkung auf den SOL-Korpus

| Kennzahl | vorher | nachher |
|---|---:|---:|
| gespeicherte Zeilen | 23 | 3 |
| Pooling-Gruppen | 16 | 3 |
| Gruppen mit k >= 2 | 1 | 0 |

Neu abgelehnt: 47 Zeilen als
Baseline, 10 als Querschnittsvergleich.
Der einzige k = 2-Pool (`total sleep time min`, g = -0,224, CI -5,76 bis
5,31) verschwindet damit - zu Recht: eine Querschnittstabelle und ein
Baseline-Kontrast waren kein Pool.

## Die drei uebrig gebliebenen Zeilen

| DOI | Outcome | g | SE | n | Zeitpunkt |
|---|---|---:|---:|---:|---|
| 10.1093/gerona/glag105 | Table 3 Comparison of temporal chang | -2.345 | 0.335 | 60 | time point Day 30 |
| 10.1093/gerona/glag105 | Table 4 Comparison of Pittsburgh Sle | -3.790 | 0.432 | 60 | time point Day 30 |
| 10.1093/gerona/glag105 | Table 5 Comparison of Blessed Orient | -1.581 | 0.296 | 60 | time point Day 30 |

Zeilen mit Zeitpunkt: 3 von 3.

## Grenzen

* Die Zaehlung der Gruende erfolgt je Tabellenzeile, nicht je zuvor
  gespeicherter Zeile; ein Teil der Baseline-Ablehnungen waere ohnehin an
  fehlender Streuung gescheitert.
* Die Interventionsvokabeln sind bewusst eng (intervention, treatment,
  placebo, sham, dose, mg, supplement, therapy, training, exercise, diet,
  usual care, drug, capsule, tablet, infusion, melatonin, caffeine). Arme
  mit reinen Substanzkuerzeln wie `MEL + CAF` gegen `MEL + PLA` werden
  deshalb abgelehnt - konservativ, nicht falsch.
* Das Gate ersetzt keine Risiko-of-Bias-Bewertung; es verhindert nur die
  offensichtlich falschen Zeilen.

