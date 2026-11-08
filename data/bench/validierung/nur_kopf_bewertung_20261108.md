# Bewertung der 20 gezogenen `nur_kopf`-Zeilen

Stand: 2026-11-08. Rohdaten: `nur_kopf_stichprobe_20261108.md` (Seed 20261108,
20 von 187 Zeilen aus 120 Dokumenten). Bewertet von Hand nach Label, Zelle,
Kopfzelle und Caption - die Signale im Skript haben nur 0 Treffer gemeldet,
weil sie auf Label und Caption schauen, nicht auf die Zellform.

## Urteilskategorien

| Kategorie | Bedeutung |
|---|---|
| `kein_effekt` | Baseline-Charakteristikum, Deskriptivwert (Median/IQR, Mittelwert mit Spanne), Textzelle oder Teststatistik |
| `change_arm_intern` | Veränderung innerhalb einer Gruppe, kein Vergleich zwischen Gruppen |
| `effekt_sekundaer` | Effektschätzer aus einer Übersichtsarbeit oder Metaanalyse |
| `between_group_primaer` | der gesuchte Fall: Vergleichseffekt aus einer Primärstudie |

## Die 20 Zeilen

| # | Datei / Block | Label | Lesbare Zelle | Urteil | Begründung |
|---|---|---|---|---|---|
| 1 | `0006a008…` 1 | Fat-free mass (kg) | `58.6 (50.5–68.8)` | kein_effekt | Mittelwert mit Spanne einer Baseline-Charakteristik (`All`) |
| 2 | `0006a008…` 1 | Number of awakenings (n) | `1.0 (0.0–3.0)` | kein_effekt | Deskriptivwert, keine Vergleichsgruppe |
| 3 | `0006a008…` 1 | Age (years) | `49.0 (42.0–55.0)` | kein_effekt | Alter als Stichprobenbeschreibung |
| 4 | `0006a008…` 1 | Sleep efficiency (%) | `87.5 (81.8–92.5)` | kein_effekt | Baseline-Wert, kein Effekt |
| 5 | `019117c0…` 1 | WASO | `t = 0.93, p = 0.47; BCa [−2.90, 19.27]` | kein_effekt | Teststatistik plus Bootstrap-Intervall, kein Effektschätzer; `t = 0.93` wird als Punktwert gelesen (falsch positiv) |
| 6 | `02b1b366…` 1 | Week-3 | `−1.6 (−2.6 to −0.6)` | change_arm_intern | Veränderung in der Akupunkturgruppe, kein Between-Group-Vergleich |
| 7 | `02b1b366…` 2 | Week-14 | `−2.4 (−3.5 to −1.4) #` | change_arm_intern | dito, Woche 14 |
| 8 | `02b1b366…` 2 | Week-10 | `−5.0 (−6.6 to −3.6) #` | change_arm_intern | dito, Woche 10 |
| 9 | `0641f965…` 2 | Prolonged-release melatonin … 39 | `2 mg/day, 1–2 hr before going to bed and after food` | kein_effekt | Dosistext; `2 / 1 / 2` wird als Effekt gelesen (falsch positiv) |
| 10 | `08f4381f…` 2 | Women only | `−1.80 [−2.86, −0.73]` | effekt_sekundaer | Subgruppen-Pooling-Schätzer einer Übersichtsarbeit |
| 11 | `094b5a8c…` 2 | Paavonen et al., 2003 [89] | `15 children with AS (DSM-IV) aged from 6–17 years …` | kein_effekt | Populationstext; Zahlen darin sind n und Altersgrenzen |
| 12 | `09ef041b…` 2 | [26] | `IRR: 1.07; 95%CI: 1.01-1.14` | effekt_sekundaer | echter Effektschätzer (Inzidenzrate) aus einer Übersicht |
| 13 | `0de4f7e3…` 2 | Garstang and Wallis (102) | `11 children and adolescents with ASD aged from 5 to 15 years` | kein_effekt | Populationstext (falsch positiv) |
| 14 | `10ba126f…` 1 | Weight (kg) c | `59.88 (56.98, 62.78)` | kein_effekt | Baseline-Gewicht je Arm |
| 15 | `11400982…` 2 | Zeitzer et al. (115) | `28-h plasma cortisol at 20-60 minute intervals: …` | kein_effekt | Methodentext (falsch positiv) |
| 16 | `134ced88…` 2 | Type 2 diabetes | `OR 2.29 (95% CI 1.48–3.55)` | effekt_sekundaer | Odds Ratio aus einer Übersicht |
| 17 | `134ced88…` 2 | Inflammation | `g = −0.16 (95% CI −0.30 to −0.03)` | effekt_sekundaer | Hedges g aus einer Übersicht |
| 18 | `1bddfad8…` 1 | PSQI total score, median (IQR) | `16.50 (14.75, 18.00)` | kein_effekt | Median mit IQR, kein Effekt |
| 19 | `1bf4688b…` 2 | Malow et al, 35 2012 (US) | `5.9 (NA) [3-10]` | kein_effekt | Alter der Teilnehmer, Baseline |
| 20 | `1c5c16c7…` 2 | Median (IQR) duration of follow-up … | `24 (14-50.5)` | kein_effekt | Deskriptivwert der Übersicht |

## Auszählung

| Urteil | Zeilen | Anteil |
|---|---:|---:|
| `kein_effekt` | 13 | 65 % |
| `change_arm_intern` | 3 | 15 % |
| `effekt_sekundaer` | 4 | 20 % |
| `between_group_primaer` | **0** | **0 %** |

Falsch positive Zelllesungen (Text oder Teststatistik als Effekt):
5 von 20 (Nummern 5, 9, 11, 13, 15 - vier Textzellen und eine
Teststatistik).

## Hochrechnung auf die 187

- Erwartete gesuchte Effekte (Between-Group, Primärstudie): **0 von 187**.
- Exakte obere 95 %-Grenze bei 0 von 20: `1 − 0.05^(1/20) = 13,9 %`, also
  höchstens etwa **26 Zeilen** - und das ist eine Obergrenze, keine Erwartung.
- Echte Effektschätzer anderer Art (überwiegend aus Übersichtsarbeiten):
  hochgerechnet etwa 37 Zeilen; arm-interne Veränderungen etwa 28.

## Was das heißt

Die Kategorie `nur_kopf` ist keine Reserve poolbarer Effekte. Sie besteht
überwiegend aus Deskriptivzeilen, die `parse_effect_cell` kontextblind als
„Wert mit Intervall" liest - `mean (range)`, `median (IQR)`, Altersangaben,
Dosistexte. Wer sie über einen Kopfzeilen-Fix freischaltet, gewinnt keine
Between-Group-Effekte aus Primärstudien, sondern überwiegend Baseline-Zahlen
und fremde Pooling-Schätzer. Der zweite Fall wäre sogar schädlich: Ein
Sekundär-Pooling-Schätzer im eigenen Pool zählt dieselben Teilnehmer doppelt -
genau das, was das Design-Gate verhindert.

## Grenzen

- Stichprobe n = 20 von 187 (10,7 %); das Urteil ist eine Einzelbewertung
  ohne Zweitleser, also nicht reliabilitätsgeprüft.
- Die Zuordnung stützt sich auf Label, Zelle, Kopfzelle und Caption des
  jeweiligen Blocks, nicht auf den umgebenden Fließtext.
- `change_arm_intern` ist ein echter Effekt, aber keiner, der ohne
  Kontrollgruppe poolbar wäre; die Kategorie ist deshalb nicht mit
  `between_group_primaer` gleichzusetzen.
- Die Hochrechnung unterstellt, dass die Stichprobe repräsentativ ist. Bei
  n = 20 ist die Unsicherheit groß; die Aussage „0 von 20" trägt aber
  unabhängig davon, dass ein Kopfzeilen-Fix hier nichts Ertragreiches öffnet.
