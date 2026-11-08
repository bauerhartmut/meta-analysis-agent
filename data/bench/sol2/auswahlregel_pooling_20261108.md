# Auswahlregel für das Pooling der SOL-Effekte

Festgelegt: 2026-11-08, **vor** der ersten gepoolten Berechnung.
Zeitpunkt der Ehrlichkeit halber: Die drei Einzeleffekte waren zu diesem
Zeitpunkt bereits bekannt (siehe `pruefung_kandidaten_20261108.md`), die
gepoolte Zahl und ihre Heterogenität nicht. Die Regel ist damit nicht
präregistriert im strengen Sinn, aber sie ist vor der Zielgröße fixiert und
wird nicht nachträglich an das Ergebnis angepasst.

## Forschungsfrage

Senkt Melatonin die Einschaflatenz (SOL, Minuten) bei Menschen mit
Schlafstörung im Vergleich zu Placebo?

## Regel 1 - Unabhängige Einheit

Eine Zeile je **Studie**. Mehrere Populationen, Dosen, Messmethoden oder
Zeitpunkte einer Studie sind keine zusätzliche Evidenz. PMC3489506 hat zwei
Messmethoden (Tagebuch, Aktigraphie) - das bleibt k = 1.

## Regel 2 - Endpunkt und Einheit

SOL in **Minuten**, Differenz Melatonin minus Placebo, negativ = Melatonin
senkt die SOL. Ausgeschlossen: log-Einheiten, Kategorien, SMD ohne
Minutenbezug.

## Regel 3 - Effektschätzer und Streuung

Mittlere Differenz (MD) mit Standardfehler. SE aus dem berichteten 95 %-CI
als (obere − untere Grenze) / 3,919928; wo die Studie den SE direkt angibt,
wird dieser genommen. Nichts wird geschätzt, was nicht berichtet ist.

## Regel 4 - Auswahl bei mehreren Populationen

Die **größere randomisierte Population**, weil sie präziser ist - nicht die
Population mit dem größeren Effekt.

- PMC2933606: 65–80 Jahre (N 281) vor Low excretors (N 172).

## Regel 5 - Auswahl bei mehreren Dosen

Die von den **Autoren empfohlene Dosis**, nicht die mit dem größten Effekt.

- PMC2952772: 0,05 mg/kg (31 min, SE 10). Die Autoren schreiben: „This study
  demonstrates that melatonin for treatment of chronic sleep onset insomnia in
  children is effective in a dosage of 0.05 mg/kg".

## Regel 6 - Auswahl bei mehreren Messmethoden

Die **vollständigere** Erhebung, die dem primären Endpunkt der Studie
entspricht.

- PMC3489506: Schlaftagebuch (n = 113) vor Aktigraphie (n = 49). Die
  Aktigraphie hatte 66 % fehlende Daten und wurde per Amendment sekundär.

## Regel 7 - Modell

Random Effects mit τ² nach DerSimonian–Laird, Gewichte 1/(v + τ²),
**Hartung–Knapp–Sidak**-Intervall mit t-Verteilung und df = k − 1 als
Hauptschätzung. Fixed-Effect nur als Vergleichsspalte. Prediction Interval
wird berichtet, aber mit dem ausdrücklichen Hinweis, dass df = k − 2 = 1 ist
und die Zahl damit praktisch unbrauchbar breit.

## Regel 8 - Was bei k = 3 nicht gemacht wird

Keine Subgruppenanalyse, keine Meta-Regression, keine Interpretation von I²
als Heterogenitätsmaß, kein Egger-Test (unter 10 Studien nicht sinnvoll),
keine Adjustierung für Publikationsbias. I² und Q werden als Zahlen berichtet,
nicht als Aussage.

## Regel 9 - Sensitivitätsanalysen (vorab festgelegt)

| Nr. | Änderung gegenüber der Hauptanalyse |
|---|---|
| S1 | PMC3489506 mit Aktigraphie statt Tagebuch (−45,3; SE 11,96) |
| S2 | PMC2933606 mit Low excretors statt 65–80 (−0,6; SE 6,81) |
| S3 | PMC2952772 mit 0,15 mg/kg statt 0,05 (−42; SE 9) |
| S4 | S1 + S2 + S3 gleichzeitig (ungünstigste Kombination) |
| S5 | Leave-one-out: je eine Studie entfernt |
| S6 | τ² nach Paule–Mandel statt DerSimonian–Laird, falls die Engine das kann |
| S7 | Fixed-Effect als Vergleich |

Alle Sensitivitäten werden getrennt ausgewiesen. Keine wird zur Hauptzahl
erklärt, auch wenn sie besser aussieht.

## Regel 10 - Berichtsform

Jede Zahl mit Studien-IDs, Effekt, 95 %-CI, k, τ², Q, I² und der Angabe, ob
sie adjustiert (Studienangabe) oder unadjustiert (eigene Rechnung) ist.
