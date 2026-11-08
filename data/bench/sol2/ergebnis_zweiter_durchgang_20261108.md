# Zweiter Lesedurchgang: k von 0 auf 1

Stand: 2026-11-08T12:57:18. Kein Netzlauf - gelesen wurden die 31 XML aus
dem Q2-Abzug. Titelscreening, Caption-Etikett, Zeitpunktspalten und
Fallzahl-Fallback sind neu; alles andere ist unveraendert.

## Ergebnis

- Dokumente im Korpus: 31
- nach Titelscreening: 20
- **Studien mit poolbarer Zeile (k): 1** (vorher 0)
- gespeicherte Zeilen: 2

| PMC | Jahr | g | SE | n | Arme (Mittel +- SD) |
|---|---:|---:|---:|---:|---|
| PMC3489506 | 2012 | -0.644 | 0.193 | 113 | Melatonin 54.8 +- 51.9 (n=54); Placebo 92.4 +- 63.0 (n=59) |
| PMC3489506 | 2012 | -0.685 | 0.294 | 49 | Melatonin 68.4 +- 41.0 (n=24); Placebo 104.1 +- 59.5 (n=25) |

Beide Zeilen stammen aus PMC3489506 (Melatonin gegen Placebo bei Kindern
mit Entwicklungsstoerungen, zwei Subgruppen). Die Einschaflatenz sinkt unter
Melatonin um 37,6 bzw. 35,7 Minuten; g = -0,644 und -0,685.

## Was jetzt gelesen wird

- **Klammer-SD mit Etikett**: steht in der Caption "means (SD)", gilt
  `54.8 (51.9)` als Mittelwert mit Streuung. Ohne Etikett bleibt es
  mehrdeutig und wird weiter verworfen.
- **Zeitpunktspalten**: bei "Baseline | Week 12" wird die Nach-Baseline-
  Spalte je Arm gewaehlt statt die Zeile zu verwerfen.
- **Fallzahl**: aus einer N-Zeile derselben Tabelle (`N | 86 | 86`) oder aus
  einer Spalte "Melatonin No of children".
- **Crossover-Erkennung**: nur im Textkopf (Abstract) und nur ohne
  "parallel". Die erste Fassung suchte im ganzen Dokument, traf damit die
  Diskussion von PMC3489506 und verwarf eine gueltige Parallelstudie - nach
  der Verschaerfung bleibt genau der echte Crossover-Fall uebrig.

## Was bewusst draussen bleibt

- **PMC11103136 ist ein Crossover** ("in a crossover design", n = 64 gesamt):
  beide Arme sind dieselben Personen. Eine Zwischenfassung zaehlte daraus
  n = 128 und eine zweite Studie; das wurde beim Pruefen gefunden und
  verworfen. Crossover braucht eine Within-Subject-Korrektur.
- **PMC2933606** (prolonged-release Melatonin, 354 Patienten) stellt je Zeile
  nur einen Arm dar (PRM in einer Zelle, Placebo in einer anderen Zeile).
  Zeilenpaarung ist nicht implementiert; das ist der naechste strukturelle
  Engpass, nicht ein Formatproblem.
- **PMC4365553** hat vier Bedingungen (Laerm, Ohrstoepsel, Licht, Melatonin)
  und ist zudem Crossover - kein Zwei-Arm-Vergleich.

## Bewertung

D1 bleibt **nicht erfuellt**: k = 1, das Schritt-Ziel verlangt k >= 2
(Gesamtziel k >= 5 erst mit A + B; Staffelung in `schwelle_k5_20261108.md`). Der Durchgang
belegt aber, dass die Ursache im Leser lag und nicht in den Dokumenten:
dieselben 31 Volltexte liefern 0 bzw. 1 Studie, je nachdem ob Klammer-SD
und Zeitpunktspalten gelesen werden. D2 bleibt nicht pruefbar (k < 2).

Grenze: 83 von 114 Treffern haben keinen PMC-Volltext; k = 1 ist eine
Untergrenze, kein Beleg fuer Studienmangel.
