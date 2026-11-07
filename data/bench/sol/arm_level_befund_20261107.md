# Arm-Rechner über die 100 SOL-XML: 23 Zeilen, 16 Gruppen, ein k = 2

Stand: 07.11.2026. `research_agent/meta/arm_level.py` über alle 100
geladenen Europe-PMC-XML. Deterministisch, kein LLM, kein Netz (XML lag
bereits lokal).

## Kennzahlen

| Kennzahl | Wert |
|---|---:|
| Tabellenzeilen geprueft | 4035 |
| umrechenbar (beide Arme mit n und Streuung) | 23 |
| gespeichert (Zitat belegt, plausibel) | 23 |
| verworfen nach Zitat-/Plausibilitaetspruefung | 0 |
| Dokumente mit Zeilen | 3 von 100 |
| Pooling-Gruppen | 16 |
| **Gruppen mit k >= 2** | **1** |

Haeufigste Ablehnungsgruende:

*  3138  kein Mittelwert mit eindeutiger Streuung in zwei Spalten
*   271  nicht genau zwei Spalten mit Mittelwert und Streuung
*   193  zu wenige Spalten
*   182  Fallzahl je Arm fehlt
*   162  direkter Effekt mit OR/RR/HR - nicht Aufgabe des Arm-Rechners
*    66  Median/IQR statt Mittelwert mit SD/SE/CI (kein SMD)

## Der einzige k = 2-Pool

`total sleep time min [hedges_g]`: k = 2, g = -0.224, 95 %-CI -5.76 bis 5.31, I² = 88.3 %, tau² = 0.337

Die beiden Zeilen und ihre Arme:

* `10.1111/sms.70277` - Total sleep time (mins): g = +0.183, SE = 0.136
  Arme: Active children ( n = 174, 68.8%) M ± SD (n=174, 404.17 ± 33.91, sd); Inactive children ( n = 79, 31.2%) M ± S (n=79, 397.32 ± 44.2, sd)
* `10.1093/gerona/glag105` - Total sleep time (min): g = -0.691, SE = 0.266
  Arme: Intervention ( n = 30) Mean ± SD (n=30, 322.07 ± 15.28, sd); Control ( n = 30) Mean ± SD (n=30, 334.57 ± 20.12, sd)

## Warum das kein verwertbarer Pool ist

Die Arm-Etiketten widerlegen die Annahme, dass hier zwei Studien dieselbe
Intervention vergleichen:

* `10.1111/sms.70277` vergleicht **aktive gegen inaktive Kinder** in einer
  Querschnittstabelle - keine Intervention, keine Randomisierung.
* `10.1093/gerona/glag105` traegt die Zeile der Tabelle mit der Spalte
  `Day` und dem Wert `0`: das ist der **Baseline-Vergleich** der beiden
  Arme vor der Intervention, kein Behandlungseffekt. Zusaetzlich sind
  `322.07 ± 15.28` bei n = 30 als SD unplausibel klein fuer
  Gesamtschlafzeit; als SE waere die SD etwa 84 min. Der Leser nimmt die
  Beschriftung `Mean ± SD` beim Wort.

Das gepoolte CI von -5,76 bis 5,31 bei SE 0,27 und 0,14 ist genau das,
was bei k = 2 mit HKSJ und I² = 88 % herauskommt: eine Zahl ohne
Aussagekraft. **k >= 2 ist damit formal erreicht, aber nicht belegt.**

## Was der Lauf sonst zeigt

Der Arm-Rechner ist der produktivste Leser im Korpus: 23 Zeilen
aus Deskriptivtabellen, gegen 15 Zeilen aus fertigen Effektspalten. Die
Ablehnungsgruende sind sauber: 3138 Zeilen haben keinen Mittelwert mit
eindeutiger Streuung in zwei Spalten, 182 keine Fallzahl je Arm, 66 nur
Median/IQR.

Defekte, die jetzt sichtbar werden:

* **Baseline-Zeilen** (`Day 0`, `pre-BLT`) werden als Behandlungseffekt
  gespeichert; `time_point` bleibt leer, das Pooling kann sie nicht
  trennen.
* **Querschnittsvergleiche** (aktive vs. inaktive Kinder, Patienten vs.
  Kontrollen) sind keine Interventionseffekte, werden aber wie zwei Arme
  einer Studie gelesen.
* **Outcome-Label faellt auf die Tabellen-Caption zurueck**, wenn die
  erste Zelle eine Zahl enthaelt (`Day 0`): dann heissen Zeilen wie ihre
  Tabelle, und `Day 0`/`Day 30` sind nicht unterscheidbar.

## Grenzen

* Nur die ersten 100 von 1068 Europe-PMC-Treffern; Auswahl 'neueste
  zuerst', nicht nach Eignung.
* Der Arm-Rechner prueft das Design nicht; `design` und `time_point`
  bleiben in allen 23 Zeilen leer.

