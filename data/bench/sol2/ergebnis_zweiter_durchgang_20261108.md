# Zweiter Lesedurchgang: k von 0 auf 1

Stand: 2026-11-08T12:56:33. Kein Netzlauf - gelesen wurden die 31 XML aus
dem Q2-Abzug. Titelscreening, Caption-Etikett, Zeitpunktspalten und
Fallzahl-Fallback sind neu; alles andere ist unveraendert.

## Ergebnis

- Dokumente im Korpus: 31
- nach Titelscreening: 20
- **Studien mit poolbarer Zeile (k): 0** (vorher 0)
- gespeicherte Zeilen: 0

| PMC | Jahr | g | SE | n | Arme (Mittel +- SD) |
|---|---:|---:|---:|---:|---|

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

## Was bewusst draussen bleibt

- **PMC11103136 ist ein Crossover** ("in a crossover design", n = 64 gesamt):
  beide Arme sind dieselben Personen. Die erste Fassung dieses Durchgangs
  zaehlte daraus n = 128 und eine zweite Studie - das wurde beim Pruefen
  gefunden und verworfen. Crossover braucht eine Within-Subject-Korrektur
  und wird hier nicht gepoolt.
- **PMC2933606** (prolonged-release Melatonin, 354 Patienten) stellt je Zeile
  nur einen Arm dar (PRM in einer Zelle, Placebo in einer anderen Zeile).
  Zeilenpaarung ist nicht implementiert; das ist der naechste strukturelle
  Engpass, nicht ein Formatproblem.
- **PMC4365553** hat vier Bedingungen (Laerm, Laerm+Ohrstoepsel, Licht,
  Melatonin) - kein Zwei-Arm-Vergleich.

## Bewertung

D1 bleibt **nicht erfuellt**: k = 1, gefordert waren 5. Der Durchgang belegt
aber, dass die Ursache im Leser lag und nicht in den Dokumenten: dieselben
31 Volltexte liefern 0 bzw. 1 Studie, je nachdem ob Klammer-SD und
Zeitpunktspalten gelesen werden. D2 bleibt nicht pruefbar (k < 2 nach
Ausschluss des Crossover).

Grenze: 83 von 114 Treffern haben keinen PMC-Volltext; k = 1 ist eine
Untergrenze, kein Beleg fuer Studienmangel.
