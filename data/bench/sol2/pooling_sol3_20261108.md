# Gepoolte Einschaflatenz: drei Studien, Random Effects, Hartung-Knapp-Sidak

Stand: 2026-11-08. Frage: Senkt Melatonin die Einschaflatenz (SOL, Minuten)
bei Menschen mit Schlafstörung gegenüber Placebo? Vorzeichen: negativ =
Melatonin senkt die SOL.

Auswahlregel vor der Berechnung: `auswahlregel_pooling_20261108.md`.
Einzelwerte und Zitate: `pruefung_kandidaten_20261108.md`.
Rohausgabe: `pooling_sol3_20261108.json`, Skript: `scripts/pool_sol3.py`.
Engine: `research_agent.meta.pooling.pool` (vorhanden, nicht neu gebaut).

## Eingabewerte der Hauptanalyse

| Studie | Effekt (min) | SE | Herkunft |
|---|---:|---:|---|
| PMC3489506 | −37,5 | 9,08 | Schlaftagebuch, adjustiert (CI −55,3 bis −19,7) |
| PMC2933606 | −15,6 | 4,92 | 65–80 Jahre, adjustiert (CI −25,3 bis −6,0) |
| PMC2952772 | −31,0 | 10,00 | 0,05 mg/kg, SE berichtet (CI 9 bis 54) |

Die SE der ersten beiden Zeilen ist aus dem berichteten CI abgeleitet
((obere − untere Grenze) / 3,919928), nicht geschätzt.

## Hauptanalyse

**−26,3 min (95 %-CI −55,6 bis 3,0), k = 3, p = 0,061.**

| Kennzahl | Wert |
|---|---:|
| gepoolter Effekt | −26,29 min |
| 95 %-CI (HKSJ, t mit df = 2) | −55,57 bis 3,00 |
| SE (HKSJ) | 6,81 |
| τ² (DerSimonian–Laird) | 104,50 min² |
| Cochran Q (df = 2) | 5,41 |
| I² | 63,0 % |
| Prediction Interval (df = 1) | −187,0 bis 134,5 |
| Fixed-Effect zum Vergleich | −22,22 (−30,01 bis −14,43) |

Das Intervall schließt die Null ein. Die Fixed-Effect-Schätzung wäre
signifikant (−22,2; CI −30,0 bis −14,4) - der Unterschied ist genau der
Effekt der Heterogenität: Bei τ² = 104,5 min² werden die Gewichte
ausgeglichen, und das HKSJ-Intervall mit nur zwei Freiheitsgraden wird breit.
Das ist die korrekte Unsicherheit, keine Schwäche der Rechnung.

Das Prediction Interval hat df = k − 2 = 1 und ist praktisch unbrauchbar;
es steht nur in der Tabelle, weil es berechenbar ist, nicht weil es etwas
aussagt.

## Unabhängige Nachrechnung

Alle Formeln von Hand, ohne die Engine-Funktionen:

| Schritt | Rechnung | Ergebnis |
|---|---|---|
| Fixed-Effect | Σw·y / Σw mit w = 1/v | −22,220 |
| Q | Σw·(y − FE)² | 5,409 |
| c | Σw − Σw²/Σw | 0,032626 |
| τ² | (Q − 2)/c | 104,496 |
| gepoolt | Σw*·y / Σw* mit w* = 1/(v + τ²) | −26,287 |
| SE (HKSJ) | √(Σw*·(y − μ)² / ((k−1)·Σw*)) | 6,806 |
| 95 %-CI | μ ± t(0,975; 2)·SE, t = 4,303 | −55,57 bis 3,00 |
| p | 2·P(T > 3,862), df = 2 | 0,0610 |

Abweichung zur Engine: 0,000000. Die Engine-Referenztests
(`research_agent/tests/test_pooling_reference.py`) laufen mit 8 von 8 grün.

## Sensitivitätsanalysen (vorab festgelegt)

| Nr. | Änderung | k | gepoolt (min) | 95 %-CI | τ² | I² |
|---|---|---:|---:|---|---:|---:|
| S1 | PMC3489506 Aktigraphie statt Tagebuch | 3 | −28,13 | −65,10 bis 8,85 | 162,12 | 68,2 |
| S2 | PMC2933606 Low excretors statt 65–80 | 3 | −22,34 | −72,05 bis 27,38 | 395,23 | 84,4 |
| S3 | PMC2952772 0,15 mg/kg statt 0,05 | 3 | −30,44 | −66,61 bis 5,73 | 201,19 | 78,0 |
| S3b | PMC2952772 0,1 mg/kg statt 0,05 | 3 | −28,02 | −59,80 bis 3,76 | 137,86 | 69,2 |
| S4 | S1 + S2 + S3 gleichzeitig | 3 | −28,42 | −91,04 bis 34,19 | 672,19 | 89,2 |
| S5a | ohne PMC3489506 | 2 | −20,84 | −113,55 bis 71,87 | 56,46 | 47,6 |
| S5b | ohne PMC2933606 | 2 | −34,56 | −75,67 bis 6,54 | 0,00 | 0,0 |
| S5c | ohne PMC2952772 | 2 | −25,22 | −163,32 bis 112,88 | 186,45 | 77,7 |

Keine Sensitivität dreht das Vorzeichen, keine macht das Intervall deutlich
schmaler. S5b (ohne die Studie mit dem kleinsten Effekt) hat τ² = 0 - das ist
kein Beleg für Homogenität, sondern ein Artefakt von k = 2: Mit zwei
Beobachtungen und ähnlichen Effekten schätzt DL die Zwischenstudienvarianz
auf null. Bei k = 2 ist I² = 0 nicht als Homogenität zu lesen.

## Was die Zahl sagt - und was nicht

**Sagt sie:** Über drei Studien mit zusammen rund 500 Teilnehmern liegt der
Punktschätzer bei −26 min, also einer Reduktion der Einschaflatenz um gut
eine halbe Stunde. Die Richtung ist in allen drei Studien und in allen
Sensitivitäten gleich.

**Sagt sie nicht:** Dass der Effekt statistisch gesichert ist. Das
HKSJ-Intervall schließt die Null ein (p = 0,061), und die
Zwischenstudienvarianz ist mit τ² = 104,5 min² groß: Die Studien schätzen
nicht denselben Effekt. Die drei Populationen sind verschieden - Kinder mit
Entwicklungsstörung über 12 Wochen, Erwachsene 65–80 über 3 Wochen, Kinder
6–12 mit chronischer Einschaflatenz-Insomnie über 1 Woche. Bei k = 3 lässt
sich nicht prüfen, ob die Heterogenität an Population, Dauer oder Dosis
liegt; jede Subgruppenanalyse wäre hier eine Aussage über eine einzelne
Studie.

**Sagt sie nicht:** Etwas über Publikationsbias. Bei k = 3 ist weder ein
Funnel-Plot noch ein Egger-Test sinnvoll; beides wird nicht gerechnet.

## Grenzen

- k = 3, davon zwei Effekte aus Adjustierungen der Originalstudien und einer
  aus einer berichteten Differenz mit SE. Die Adjustierung ist
  studienintern unterschiedlich (Kovariaten nicht vereinheitlicht).
- PMC2933606 und PMC2952772 haben je zwei bzw. drei mögliche Zeilen; die
  Auswahl ist nach der Regel „größere Population / empfohlene Dosis"
  getroffen, nicht präregistriert. Sensitivitäten S2/S3 zeigen die Spanne.
- Die Effekte sind adjustierte Differenzen aus verschiedenen Modellen; eine
  gemeinsame Adjustierung für Baseline-SOL gibt es nicht.
- I² bei k = 3 ist eine Zahl, kein Befund.

## Nächster Schritt

Die gepoolte Zahl ist mit k = 3 nicht entscheidbar. Der Hebel liegt nicht in
weiteren Modellvarianten an denselben drei Studien, sondern in mehr
unabhängigen Studien: die 83 Volltexte aus der Zugangsliste
(`zugangsliste_20261108.csv`) enthalten die Kandidaten, mit denen k auf 5–8
steigen kann. Erst ab k ≥ 5 sind Subgruppen (Kinder vs. Erwachsene, Dauer)
und eine belastbare Heterogenitätsaussage möglich.
