# Change-Score-Leser: rho offengelegt, eine Zeile, kein k >= 2

Stand: 07.11.2026. Neu: `research_agent/meta/arm_change.py`, 14 Tests in
`research_agent/tests/test_arm_change.py`, `scripts/convert_change_arms_xml6.py`.
Kein LLM, kein Netzzugriff im Leser.

## Zwei Modelle, klar getrennt

**A - gemeldete Veraenderung (Modell `reported`).** Der Satz nennt die
Differenz selbst: "DLMO was advanced by 0.73 +- 1.21 h ... compared to
0.24 +- 1.11 h following placebo (n = 20)". Die Streuung der Veraenderung ist
gegeben, die Korrelation zwischen den Messzeitpunkten spielt keine Rolle -
g wird exakt gerechnet, `rho` ist im Datensatz `null`.

**B - prae/post (Modell `prepost`).** Der Satz nennt beide Zeitpunkte:
"decreased from 32.1 +- 9.4 to 18.3 +- 7.2 min". Die Veraenderung ist
`post - pre`, ihre Streuung aber

    SD_change = sqrt(SD_pre^2 + SD_post^2 - 2 * rho * SD_pre * SD_post)

und `rho` steht in fast keinem Paper. Es wird nicht still gesetzt: der
gespeicherte Wert ist der Primaerwert bei **rho = 0.5**, ausgewiesen in
`moderators` (`rho`, `rho_assumed = true`), und jede Zeile traegt ein
Sensitivitaetsgrid ueber rho = 0.0, 0.3, 0.5, 0.7, 0.9. Ein groesseres rho
bedeutet kleinere Change-SD und damit groesseres |g|; das Grid zeigt, wie
stark der Befund an der Annahme haengt, statt sie zu verstecken.

Abgelehnt wird wie bei den anderen Lesern: SEM/SE, Median/IQR, Tabellen- und
Zitationsreste, Designsaetze, demografische Outcomes, Vergleiche ohne
Interventionsarm und Saetze ohne Fallzahl je Arm. Gespeichert wird nur mit
woertlichem Zitatbeleg (`locate_quote`) und Plausibilitaetspruefung.

## Lauf ueber den vollen SOL-Korpus

1.056 XML (3 fehlen, HTTP 500), **315.857 Saetze**:

| Kennzahl | Wert |
|---|---:|
| Kandidaten | 1 |
| gespeichert | 1 |
| davon `reported` | 1 |
| davon `prepost` | 0 |

Ablehnungsgruende:

| Anzahl | Grund |
|---:|---|
| 220.850 | kein Veraenderungswert im Satz |
| 50.336 | Tabellen-/Zitationsrest statt Ergebnissatz |
| 38.393 | nicht genau zwei Arme mit Veraenderung im Satz |
| 3.340 | Stichproben- oder Designbeschreibung statt Ergebnis |
| 1.763 | Streuung als SEM/SE im Satz (nicht SD) |
| 939 | Median/IQR statt Mittelwert mit SD |
| 235 | Fallzahl je Arm fehlt |

Die 38.393 Ablehnungen sind kein Musterfehler: in den ersten 120 Dokumenten
gibt es genau **einen** Satz mit zwei prae/post-Paaren, und der ist eine
Tabellenunterschrift. Die Studien berichten ihre Veraenderung fast immer je
Arm einzeln ("SOL sank in der Melatoningruppe von ... auf ..."), nicht beide
Arme in einem Satz.

## Der gespeicherte Effekt

`10.1371/journal.pmed.1002587`, Outcome **DLMO**, Modell `reported`:
Melatonin +0,73 +- 1,21 h (n = 23) gegen Placebo +0,24 +- 1,11 h (n = 20),
g = **0,413** (SE 0,309, n = 43), Zitat woertlich belegt (exact = True).

**Wichtig:** Das ist derselbe Satz, den auch der Post-Wert-Leser liest - dort
als Mittelwert nach Behandlung, hier als Zuwachs. Beide Wege ergeben
denselben Effekt; die Zeile ist also eine Dublette und kein zweiter Befund.
Fuer die Vereinigung zaehlt sie einmal.

## k >= 2: null, auch nach der Vereinigung

| Leser | Zeilen | Gruppen | k >= 2 |
|---|---:|---:|---:|
| Effektspalten | 513 | 154 | 0 |
| Arm-Rechner (Tabellen) | 8 | 8 | 0 |
| Fliesstext (Post-Werte) | 1 | 1 | 0 |
| Veraenderungswerte (dieser Lauf) | 1 | 1 | 0 |

Die Vereinigung ueber alle vier Leser ergibt 162 Outcome-Gruppen. Genau eine
traegt zwei Studien - der Schluessel `low` -, und die ist **falsch**: dort
steht ein OR-Wert ("Low", 10.1002/fsn3.1050) neben einer Tertilzeile
("Low (< 9.49)", 10.1186/s12889-026-26824-4). Zwei verschiedene Bedeutungen
von "low" und zwei nicht vergleichbare Effektmasse. Filtert man auf
Effekttyp g, bleibt k = 1. Ein echter Zwei-Studien-Pool entsteht nicht.

## Grenzen

* Das prae/post-Modell greift nur, wenn beide Arme im selben Satz mit
  Streuung stehen - im Korpus fast nie. Der Weg ueber Einzelarm-Saetze
  braeuchte Satzuebergriff und ist bewusst nicht gebaut.
* rho = 0.5 ist eine Annahme, keine Messung. Bei `prepost`-Zeilen muss jede
  Auswertung das Grid mitberichten (oder rho = 0 als konservativen Rand).
* Change-SMD und Post-Wert-SMD sind unterschiedlich standardisiert und
  duerfen nicht ungeprueft in denselben Pool.
* Keine Risk-of-Bias-Bewertung, keine Adjustierung fuer Baseline-Unterschiede.
* 3 von 1.059 Dokumenten fehlen (HTTP 500).
