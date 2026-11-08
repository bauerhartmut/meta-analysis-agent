# Gepoolte Einschaflatenz: drei Studien, Random Effects, Hartung-Knapp-Sidak

Stand: 2026-11-08. Frage: Senkt Melatonin die Einschaflatenz (SOL, Minuten)
bei Menschen mit Schlafstoerung gegenueber Placebo? Vorzeichen: negativ =
Melatonin senkt die SOL.

Auswahlregel vor der Berechnung: `auswahlregel_pooling_20261108.md`.
Einzelwerte und Zitate: `pruefung_kandidaten_20261108.md`.
Zusatzdaten aus dem HTA-Bericht: `mends_hta_zusatz_20261108.md`.
Validierung und Gesamtbewertung: `validierung_sol3_20261108.md`.
Rohausgabe: `pooling_sol3_20261108.json`, Skript: `scripts/pool_sol3.py`.
Engine: `research_agent.meta.pooling.pool` (vorhanden, nicht neu gebaut).

## Eingabewerte der Hauptanalyse

| Studie | Effekt (min) | SE | Herkunft |
|---|---:|---:|---|
| PMC3489506 | -37,5 | 9,08 | Schlaftagebuch, adjustiert (CI -55,3 bis -19,7) |
| PMC2933606 | -15,6 | 4,92 | Subgruppe 65-80 Jahre, adjustiert (CI -25,3 bis -6,0) |
| PMC2952772 | -31,0 | 10,00 | 0,05 mg/kg, SE berichtet (CI 9 bis 54) |

Die SE der ersten beiden Zeilen ist aus dem berichteten CI abgeleitet
((obere - untere Grenze) / 3,919928), nicht geschaetzt.

## Hauptanalyse

**-26,3 min (95%-CI -55,6 bis 3,0), k = 3, p = 0,061.**

| Kennzahl | Wert |
|---|---:|
| gepoolter Effekt | -26,29 min |
| 95%-CI (HKSJ, t mit df = 2) | -55,57 bis 3,00 |
| SE (HKSJ) | 6,81 |
| tau^2 (DerSimonian-Laird) | 104,50 min^2 |
| Cochran Q (df = 2) | 5,41 |
| I^2 | 63,0 % |
| Prediction Interval (df = 1) | -187,0 bis 134,5 |
| Fixed-Effect zum Vergleich | -22,22 (-30,01 bis -14,43) |

Das Intervall schliesst die Null ein. Die Fixed-Effect-Schaetzung waere
signifikant (-22,2; CI -30,0 bis -14,4) - der Unterschied ist genau der
Effekt der Heterogenitaet: Bei tau^2 = 104,5 min^2 werden die Gewichte
ausgeglichen, und das HKSJ-Intervall mit nur zwei Freiheitsgraden wird breit.
Das ist die korrekte Unsicherheit, keine Schwaee der Rechnung.

Das Prediction Interval hat df = k - 2 = 1 und ist praktisch unbrauchbar;
es steht nur in der Tabelle, weil es berechenbar ist, nicht weil es etwas
aussagt.

## Unabhaengige Nachrechnung

Alle Formeln von Hand, ohne die Engine-Funktionen:

| Schritt | Rechnung | Ergebnis |
|---|---|---|
| Fixed-Effect | Summe w*y / Summe w mit w = 1/v | -22,220 |
| Q | Summe w*(y - FE)^2 | 5,409 |
| c | Summe w - Summe w^2/Summe w | 0,032626 |
| tau^2 | (Q - 2)/c | 104,496 |
| gepoolt | Summe w**y / Summe w* mit w* = 1/(v + tau^2) | -26,287 |
| SE (HKSJ) | Wurzel(Summe w**(y - mu)^2 / ((k-1)*Summe w*)) | 6,806 |
| 95%-CI | mu +/- t(0,975; 2)*SE, t = 4,303 | -55,57 bis 3,00 |
| p | 2*P(T > 3,862), df = 2 | 0,0610 |

Abweichung zur Engine: 0,000000. Die Engine-Referenztests
(`research_agent/tests/test_pooling_reference.py`) laufen mit 8 von 8 gruen.

## Sensitivitaetsanalysen

| Nr. | Aenderung | k | gepoolt (min) | 95%-CI | tau^2 | I^2 |
|---|---|---:|---:|---|---:|---:|
| S1 | PMC3489506 Aktigraphie statt Tagebuch | 3 | -28,13 | -65,10 bis 8,85 | 162,12 | 68,2 |
| S2 | PMC2933606 Low excretors statt 65-80 | 3 | -22,34 | -72,05 bis 27,38 | 395,23 | 84,4 |
| S3 | PMC2952772 0,15 mg/kg statt 0,05 | 3 | -30,44 | -66,61 bis 5,73 | 201,19 | 78,0 |
| S3b | PMC2952772 0,1 mg/kg statt 0,05 | 3 | -28,02 | -59,80 bis 3,76 | 137,86 | 69,2 |
| S4 | S1 + S2 + S3 gleichzeitig | 3 | -28,42 | -91,04 bis 34,19 | 672,19 | 89,2 |
| S5a | ohne PMC3489506 | 2 | -20,84 | -113,55 bis 71,87 | 56,46 | 47,6 |
| S5b | ohne PMC2933606 | 2 | -34,56 | -75,67 bis 6,54 | 0,00 | 0,0 |
| S5c | ohne PMC2952772 | 2 | -25,22 | -163,32 bis 112,88 | 186,45 | 77,7 |
| S8 | S1 Tagebuch unadjustiert (HTA) | 3 | -25,43 | -54,37 bis 3,50 | 87,60 | 55,4 |
| S9 | S1 Aktigraphie unadjustiert (HTA) | 3 | -30,12 | -76,83 bis 16,59 | 230,17 | 72,7 |
| S10 | PMC2952772 SE 11,0 statt 10,0 | 3 | -26,20 | -55,75 bis 3,36 | 107,13 | 62,1 |

S8 und S9 nutzen die im HTA-Bericht zusaetzlich berichtete **unadjustierte**
Differenz der Change-Werte (Tagebuch -37,44; Aktigraphie -54,61) mit
SE 10,88 bzw. 14,82 statt der adjustierten Differenz (SE 9,08 bzw. 11,96).
Die gepoolte Zahl aendert sich um 0,9 bzw. 3,8 min; die Unsicherheit wird
etwas groesser, weil die unadjustierte Schaetzung die Baseline-Kovariate nicht
nutzt. Die adjustierte Variante bleibt Hauptanalyse - nicht weil sie besser
aussieht, sondern weil sie praeziser ist und die Studienanalyse sie als
primaere Schaetzung ausweist.

S10 nutzt SE 11,0 fuer PMC2952772, abgeleitet aus dem berichteten CI
9 bis 54 min; die Differenz zur Hauptanalyse betraegt 0,09 min. Der
berichtete SE 10 bleibt massgeblich, weil er die Autorenangabe ist.
Begruendung in `validierung_sol3_20261108.md`, Aufgabe 3.

Keine Sensitivitaet dreht das Vorzeichen, keine macht das Intervall deutlich
schmaler. S5b (ohne die Studie mit dem kleinsten Effekt) hat tau^2 = 0 - das
ist kein Beleg fuer Homogenitaet, sondern ein Artefakt von k = 2: Mit zwei
Beobachtungen und aehnlichen Effekten schaetzt DL die Zwischenstudienvarianz
auf null. Bei k = 2 ist I^2 = 0 nicht als Homogenitaet zu lesen.

## Was die Zahl sagt - und was nicht

**Sagt sie:** Ueber drei Studien mit zusammen rund 500 Teilnehmern liegt der
Punktschaetzer bei -26 min, also einer Reduktion der Einschaflatenz um gut
eine halbe Stunde. Die Richtung ist in allen drei Studien und in allen
Sensitivitaeten gleich.

**Sagt sie nicht:** Dass der Effekt statistisch gesichert ist. Das
HKSJ-Intervall schliesst die Null ein (p = 0,061), und die
Zwischenstudienvarianz ist mit tau^2 = 104,5 min^2 gross: Die Studien
schaetzen nicht denselben Effekt. Die drei Populationen sind verschieden -
Kinder 3-15,8 Jahre mit Entwicklungsstoerung ueber 12 Wochen, Erwachsene
65-80 ohne Melatonin-Schwelle ueber 3 Wochen, Kinder 6-12 mit chronischer
Einschlafinsomnia ueber 1 Woche. Bei k = 3 laesst sich nicht pruefen, ob die
Heterogenitaet an Population, Dauer oder Dosis liegt; jede
Subgruppenanalyse waere hier eine Aussage ueber eine einzelne Studie.

**Sagt sie nicht:** Etwas ueber Publikationsbias. Bei k = 3 ist weder ein
Funnel-Plot noch ein Egger-Test sinnvoll; beides wird nicht gerechnet.

## Grenzen

- k = 3, davon zwei Effekte aus Adjustierungen der Originalstudien und einer
  aus einer berichteten Differenz mit SE. Die Adjustierung ist
  studienintern unterschiedlich (Kovariaten nicht vereinheitlicht).
- PMC2933606 und PMC2952772 haben je zwei bzw. drei moegliche Zeilen; die
  Auswahl ist nach der Regel "groessere Population / empfohlene Dosis"
  getroffen. Sensitivitaeten S2/S3 zeigen die Spanne.
- Die Effekte sind adjustierte Differenzen aus verschiedenen Modellen; eine
  gemeinsame Adjustierung fuer Baseline-SOL gibt es nicht.
- I^2 bei k = 3 ist eine Zahl, kein Befund.
- 83 Dokumente der Suche waren nicht beschaffbar; die Verzerrung durch
  diese Luecke ist nicht quantifizierbar.

## Naechster Schritt

Die gepoolte Zahl ist mit k = 3 nicht entscheidbar. Der Hebel liegt nicht in
weiteren Modellvarianten an denselben drei Studien, sondern in mehr
unabhaengigen Studien: die 83 Volltexte aus der Zugangsliste
(`zugangsliste_20261108.csv`) enthalten die Kandidaten, mit denen k auf 5-8
steigen kann. Erst ab k >= 5 sind Subgruppen (Kinder vs. Erwachsene, Dauer)
und eine belastbare Heterogenitaetsaussage moeglich.
