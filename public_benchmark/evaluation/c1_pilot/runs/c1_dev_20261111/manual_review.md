# Manuelle Fehlerprüfung: C1-Dev-Pilot

Run: `c1_dev_20261111`

Grundlage: 26 Modellausgaben, 140 erwartete Felder, 93 exakte Treffer,
43 falsche und 4 fehlende Felder. Alle 47 abweichenden Felder wurden gegen die
Quelltexte geprüft. Es gab keine halluzinierten Werte auf nicht erwarteten
Feldern (68/68 korrekt `null`). Die Abweichungen zerfallen in zwei
Ambiguitätscluster und einen Tabellen-Extraktionsfehler.

## Cluster A: Zeitpunkt (10 Records, 39 Felder)

Betroffen: 224, 225, 226, 227, 229, 234, 235, 236, 237, 238 (alle PMC5498715).

Die Referenz verwendet für diese Records den **Post-Test** (Tabelle 1,
Spalte "Mean±SD of Post-test"). Das Modell verwendet konsistent den
**4-Monats-Follow-up** (Tabelle 1, Spalte "Mean±SD of Follow up after 4
months"; Tabelle 3 wiederholt diese Werte).

Beispiele aus der Quelle:

| Record | Referenz (Post-Test) | Modell (Follow-up) |
|---|---|---|
| 224 External Regulation | 0.30 ± 0.79 / 0.38 ± 0.98 | 0.43 ± 1.04 / 1.19 ± 1.37 |
| 225 Amotivation | 0.33 ± 1.06 / 0.70 ± 1.24 | 0.06 ± 0.36 / 0.58 ± 0.92 |
| 226 BMI | 25.78 ± 3.30 / 26.53 ± 3.53 | 25.32 ± 3.05 / 26.59 ± 3.53 |
| 229 Total PA | 487.33 ± 111.47 / 453.57 ± 60.87 | 854 ± 271.60 / 470 ± 80.46 |
| 234 Intrinsic Motivation | 10.80 ± 2.0 / 4.90 ± 1.88 | 13.50 ± 1.79 / 5.51 ± 2.39 |
| 238 Health care climate | 80.50 ± 9.97 / 69.89 ± 1.59 | 83.10 ± 1.37 / 69.57 ± 1.61 |

Bei 228, 230, 231, 232 und 233 fehlt der Post-Test in der Quelle; dort ist der
Follow-up der einzige postinterventionelle Wert, und Referenz und Modell
stimmen exakt überein. Die Referenzregel ist damit nicht "immer Follow-up",
sondern "frühester berichteter postinterventioneller Wert". Diese Regel steht
nicht in der ICO-Eingabe.

Sensitivität: Würde man den 4-Monats-Follow-up als zulässig akzeptieren, wären
39 der 43 falschen Felder exakt; die strenge Quote stiege von 93/140 (66,4 %)
auf 132/140 (94,3 %). Das ist keine nachträgliche Änderung des Primärergebnisses.

## Cluster B: Record 120 (4 Felder)

Quelle PMC4450164, Tabelle "Comparing Postoperative Course...":

- Referenz: DTPA-Scan, "Partial obstruction" 8/20 vs. 13/44.
- Modell: "Recurrence of stenosis, reoperation" 0/30 vs. 1/52.

Die ICO nennt nur "ureteropelvic junction obstruction" und keinen Zeitpunkt
oder Diagnostikweg. Die Referenz verwendet eine DTPA-Subgruppe mit den
Nennern 20/44, nicht die randomisierten Arme 30/52. Damit ist sowohl die
Outcome-Auswahl als auch die Gruppengröße unterspezifiziert. Das Modell hat
eine andere, ebenfalls berichtete Ergebniszeile gewählt; die vier Felder sind
unter der eingefrorenen Referenz falsch, aber nicht halluziniert.## Cluster C: Record 190 (4 fehlende Felder)

Quelle PMC5244530, Tabelle 2: Die Tabelle berichtet die Sedativa-Werte als
`n (%)` und nennt die Gruppengrößen im selben Block: Intervention `n = 125`,
TAU `n = 133`. Für den 12-Monats-Follow-up stehen dort direkt `52 (42)` und
`51 (38)`. Die Referenzwerte 52/125 und 51/133 sind damit direkt berichtet und
nicht aus Prozenten abgeleitet. Das Modell hat die Zeile dennoch als reine
Prozentangabe gelesen und alle vier Felder auf `null` gesetzt. Das ist ein
Tabellen-Extraktionsfehler, kein Protokollkonflikt.

## Sensitivität ohne die beiden Ambiguitätscluster

Ohne die 10 Zeitpunkt-Records und Record 120 bleiben 15 Records mit 76
erwarteten Feldern. Dort sind **72/76 Felder exakt** (94,7 %); die vier
fehlenden Felder sind Record 190. Diese Zahl ist eine deskriptive
Sensitivitätsanalyse, kein Ersatz für die strenge Auswertung.

## Konsequenz

Der strenge Primärwert bleibt **93/140 exakt (66,4 %)**, Abdeckung 97,1 %,
MAE 4,7066, 0 halluzinierte Felder. Vor einer Testfreigabe müssen zwei
Protokollpunkte entschieden und ein Extraktionsfehler adressiert werden:

1. Welcher Zeitpunkt gilt, wenn Post-Test und Follow-up beide berichtet sind?
2. Wie wird ein unterspezifiziertes ICO wie Record 120 aufgelöst?
3. Record 190 zeigt, dass Counts in `n (%)`-Tabellen trotz direkt berichteter
   Zahl übersehen werden; die Tabellenlesung braucht einen gezielten Dev-Test.

Der Testsplit wurde nicht gelesen oder verwendet.
