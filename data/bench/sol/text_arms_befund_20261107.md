# Fliesstext-Arm-Leser: eine belegte Zeile, kein k >= 2

Stand: 07.11.2026. Neu: `research_agent/meta/arm_text.py` (Leser),
`research_agent/tests/test_arm_text.py` (22 Tests), `scripts/convert_text_arms_xml6.py`
(Lauf ueber eine Manifest-Liste). Kein LLM, kein Netzzugriff im Leser.

## Was der Leser tut

Er liest Ergebnissaetze der Form

> Following melatonin treatment ( n = 23), DLMO was advanced by 0.73 +- 1.21 h,
> compared to 0.24 +- 1.11 h following placebo ( n = 20)

und rechnet daraus Hedges g mit SE - mit denselben Formeln wie der
Tabellen-Rechner (`arm_level.py`), demselben Store und derselben Zitatpruefung
(`locate_quote` gegen den Dokumenttext). Etikett und Fallzahl werden an
derselben `n = 20`-Stelle verankert; so funktionieren beide Reihenfolgen
("melatonin (n = 20): 18.3 +- 7.2" und "18.3 +- 7.2 min in the melatonin
group (n = 20)").

Abgelehnt wird ausdruecklich:

| Grund | Warum |
|---|---|
| kein Mittelwert mit Streuung | ohne SD keine SMD |
| nicht genau zwei Mittelwerte | vier Werte sind Gruppen oder Zeitpunkte, kein Zwei-Arm-Vergleich |
| Fallzahl je Arm fehlt | eine Gesamt-Fallzahl reicht nicht |
| SEM/SE im Satz | Streuung ist kein SD, wird nicht umgedeutet |
| Median/IQR | andere Schaetzung, nicht die SMD-Formel |
| Baseline-/Veraenderungsmuster | "from 32.1 to 18.3", "change", "delta" berichten keinen Gruppenvergleich |
| Stichproben-/Designbeschreibung | "were randomized to ... age 34.8 +- 9.6" ist Demografie |
| demografische Angabe als Outcome | Alter, BMI, Geschlecht sind kein Endpunkt |
| Tabellen-/Zitationsrest | Zeilen mit "|" und "et al." sind Uebersichtstabellen |
| kein Interventionsarm | aktive vs. inaktive Kinder, Patienten vs. Kontrollen |

## Lauf ueber den vollen SOL-Korpus

1.056 XML-Dokumente (3 fehlen wegen HTTP 500), **315.857 Saetze** geprueft:

| Kennzahl | Wert |
|---|---:|
| Kandidaten | 1 |
| gespeichert | 1 |
| vom Store verworfen | 0 |

Ablehnungsgruende (Saetze):

| Anzahl | Grund |
|---:|---|
| 242.564 | kein Mittelwert mit Streuung im Satz |
| 46.010 | Tabellen-/Zitationsrest statt Ergebnissatz |
| 20.185 | Baseline-/Veraenderungsmuster statt Gruppenvergleich |
| 3.095 | Stichproben- oder Designbeschreibung statt Ergebnis |
| 1.747 | Streuung als SEM/SE im Satz (nicht SD) |
| 1.138 | Median/IQR statt Mittelwert mit SD |
| 711 | nicht genau zwei Mittelwerte mit Streuung |
| 403 | Fallzahl je Arm fehlt |
| 2 | Arm-Etikett fehlt |
| 1 | kein Interventionsarm |

## Der eine belegte Effekt

`10.1371/journal.pmed.1002587` (PMC6005466), Outcome **DLMO**:

| Arm | Mittelwert +- SD | n |
|---|---|---:|
| Melatonin | 0,73 +- 1,21 h | 23 |
| Placebo | 0,24 +- 1,11 h | 20 |

g = **0,413**, SE = 0,309, n = 43. Das Zitat steht woertlich im Dokument
(`locate_quote`, exact = True); der Satz sagt selbst, dass die Differenz
nicht signifikant war (P > 0,05).

## k >= 2: weiterhin null

| Leser | Zeilen | Gruppen | Gruppen mit k >= 2 |
|---|---:|---:|---:|
| Effektspalten | 513 | 154 | 0 |
| Arm-Rechner (Tabellen, Gate) | 8 | 8 | 0 |
| Fliesstext-Arme | 1 | 1 | 0 |

Auch die Vereinigung von Tabellen- und Fliesstext-Armen ergibt keine
Outcome-Gruppe mit zwei unabhaengigen Studien.

## Grenzen

* Der Leser akzeptiert nur Saetze mit ausdruecklichem SD **und** Fallzahl je
  Arm. Change-Scores, SEM, Median/IQR und "mean (range)" bleiben draussen -
  das ist Absicht, kostet aber Reichweite: in diesem Korpus berichten die
  Studien ihre Gruppenwerte ueberwiegend als Veraenderung oder als SEM.
* Zwei fruehere Fassungen des Lesers haben Alter, BMI und Tabellenreste als
  Effekte gespeichert (11 Zeilen). Sie sind durch die Gates oben ersetzt;
  die 11 Zeilen gelten als verworfen und stehen in keiner Auswertung.
* Keine Risk-of-Bias-Bewertung, keine Adjustierung fuer Baseline-Unterschiede.
* 3 von 1.059 Dokumenten fehlen (HTTP 500 bei Europe PMC).
