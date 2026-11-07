# Arm-Deskriptiva umrechnen: Modul, Tests, Messung

Stand: 07.11.2026. Rechner: `research_agent/meta/arm_level.py`
(`ARM_LEVEL_VERSION = "arm-level/1"`), Tests:
`research_agent/tests/test_arm_level.py`, Messung:
`scripts/convert_arm_level_xml6.py`.

## Was der Rechner tut

Aus zwei Armen mit Mittelwert, Streuung und Fallzahl berechnet er
deterministisch die standardisierte Mittelwertdifferenz:

    s_pooled^2 = ((n1-1) s1^2 + (n2-1) s2^2) / (n1 + n2 - 2)
    d          = (m1 - m2) / s_pooled
    J          = 1 - 3 / (4 (n1 + n2) - 9)
    g          = J * d
    SE(g)      = sqrt((n1 + n2)/(n1 n2) + g^2 / (2 (n1 + n2)))

Streuungen werden nur aus eindeutigen Angaben gebildet:
`391.8 ± 12.4` (SD), `7.21 (SE 1.13)` (SD = SE * sqrt(n)),
`16.7 (11.6 to 22.0)` mit n (SE aus dem 95 %-CI, SD = SE * sqrt(n)).
Ein nackter Wert in Klammern (`16.7 (11.6)`) bleibt uneindeutig und wird
verworfen, ebenso alles ohne Fallzahl je Arm.

Gespeichert wird nur, wenn (a) beide Arme vollstaendig sind, (b) das
Zitat woertlich im gespeicherten Dokument steht (`locate_quote`) und
(c) die Plausibilitaetspruefung des Effekt-Stores besteht. Es wird nichts
interpoliert, ergaenzt oder aus einer Gesamt-Fallzahl aufgeteilt.

## Tests

24 Tests gruen, Erwartungswerte von Hand nach den Formeln gerechnet
(u. a. d = -1.0, J = 0.980132, g = -0.980132, SE = 0.334676 bei
m = 10/12, SD = 2/2, n = 20/20). Abgedeckt sind ausserdem:
Dezimalkomma und Unicode-Minus, `<.001` als p-Wert, SD aus SE und aus
95 %-CI, Ablehnung von n < 2, Median/IQR, OR/RR/HR-Spalten, mehr als zwei
Armspalten, fehlende Fallzahl und ein nicht verifizierbares Zitat.

## Messung auf den sechs XML-Dokumenten

354 Tabellenzeilen, **0 umrechenbar, 0 gespeichert**.

| Grund | Zeilen |
|---|---:|
| kein Mittelwert mit eindeutiger Streuung in zwei Spalten | 289 |
| direkter Effekt mit OR/RR/HR (nicht Aufgabe des Arm-Rechners) | 23 |
| nicht genau zwei Spalten mit Mittelwert und Streuung | 20 |
| Median/IQR statt Mittelwert mit SD/SE/CI | 12 |
| zu wenige Spalten | 10 |

Die Verteilung ist der Befund: In diesen sechs Dokumenten gibt es keine
Tabelle mit zwei Studienarmen als Mittelwert plus SD/SE/CI und Fallzahl je
Arm. Die Tabellen liefern statt dessen

* **Mediane mit IQR** plus eine fertige Effektspalte (`jamanetworkopen`:
  `Hedges g (95% CI)` je Outcome, z. B. `-0.22 (-0.32 to -0.17)`),
* **adjustierte Odds Ratios** je Outcome (`pcd20.230198`:
  `OR (95% CI)` und `Adjusted OR (95% CI)`),
* **Arm-Mittelwerte ohne Fallzahl je Arm**, oft mit einer Gesamt-N-Spalte
  (`jamanetworkopen`: "No. of pairs" = 342 fuer beide Arme),
* **mehr als zwei Wertspalten** (Gruppen, Zeitpunkte, Analyte), die kein
  Zwei-Arm-Vergleich sind (`ijms27146320`: acht Gruppenmittel je Zeile).

## Konsequenz

Der Rechner ist fertig und geprueft, aber fuer diesen Korpus greift er
nicht: Wo die Tabellen Effekte enthalten, stehen sie schon als g oder OR
da (der LLM-Extraktor liest sie, Ergebnis: 1 poolbare Zeile). Wo nur
Mittelwerte stehen, fehlt die Fallzahl je Arm. Der naechste Hebel ist
deshalb nicht die SMD-Formel, sondern die **Fallzahl** - und, fuer den
jamanetworkopen-Fall, die direkte Uebernahme der berichteten Effektspalte
statt eines Umwegs ueber Arm-Deskriptiva.

Grenzen: sechs Dokumente, ein Korpus, eine Messung; 0 heisst "in dieser
Auswahl nicht anwendbar", nicht "der Rechner funktioniert nicht" - die
Tests rechnen echte Zwei-Arm-Tabellen korrekt. Nicht implementiert:
Median-zu-SMD-Konversion (braucht eine Verteilungsannahme und ist damit
nicht mehr deterministisch) und die Rueckrechnung von OR in SMD.
