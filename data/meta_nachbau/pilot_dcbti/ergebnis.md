# Nachbau: Digitale CBT-I bei jungen Menschen (2026-11-11)

Eine ausführliche Einordnung der Ergebnisse und der Rolle der
B-Zweitannotation steht in
`docs/internal/meta_nachbau_dcbti_erklaerung_20261111.md`.

## Zielwert der Publikation

Subjektive Schlafqualität post-treatment, vier RCTs:

- Hedges g = **-0.58** (95 %-KI **-1.03 bis -0.13**)
- k = 4
- I² = **84 %**
- tau² = **0.17**
- Q = **18.25** (df = 3)

Quelle: Tsai et al. 2022, Journal of Personalized Medicine 12(3):481,
DOI `10.3390/jpm12030481`, PMC `PMC8949345`, Figure 2A.

## Extrahierte Armwerte

| Studie | Instrument | Zeitpunkt | dCBT-I n | dCBT-I M (SD) | Kontrolle n | Kontrolle M (SD) | publiziertes g [95 %-KI] |
|---|---|---|---:|---:|---:|---:|---:|
| Morris 2015 | PSQI | 6 Wochen | 48 | 5.17 (2.50) | 47 | 6.68 (3.37) | -0.51 [-0.91; -0.10] |
| Freeman 2017 | ISI | Woche 10 | 1891 | 9.23 (5.18) | 1864 | 12.95 (5.27) | -0.71 [-0.81; -0.61] |
| Fucito 2017 | PSQI | Woche 5 | 21 | 10.85 (2.02) | 21 | 10.13 (1.97) | +0.35 [-0.26; +0.96] |
| de Bruin 2018 | HSDQi | post-treatment | 39 | 2.86 (0.71) | 39 | 3.74 (0.62) | -1.31 [-1.80; -0.82] |

Die Werte stehen im Einklang mit dem Forest Plot der Review (Figure 2A)
und den Tabellen der Primärtexte:

- Morris: Tabelle 1, PDF S. 36; Post-Werte für Insomnia Relief und Control.
- Freeman: Tabelle 4, PDF S. 8, Week 10; ISI.
- Fucito: Tabelle 4, PDF S. 24, Zeile Subjective Sleep Ratings; Woche 5.
- de Bruin: Tabelle 2, PDF S. 6, Zeile HSDQ - insomnia symptoms; IT vs WL.

## Nachrechnung

Hedges-g aus N, Mittelwert und SD, anschließend
DerSimonian-Laird-Pool:

| Quelle | g | 95 %-KI | Q | tau² | I² |
|---|---:|---:|---:|---:|---:|
| Review (publiziert) | -0.58 | -1.03; -0.13 | 18.25 | 0.17 | 84.00 % |
| aus SMD und KI | -0.5849 | -1.0356; -0.1342 | 18.2133 | 0.1659 | 83.53 % |
| aus N, M und SD | -0.5842 | -1.0295; -0.1389 | 18.3788 | 0.1615 | 83.68 % |

**Befund:** Der publizierte Pool ist aus den vier Studienwerten
reproduzierbar. Die kleinen Abweichungen bei Q, tau² und I² sind auf die
Rundung der berichteten Studien-SMDs bzw. die Varianzberechnung in Review
Manager zurückzuführen; Effekt und 95-%-KI liegen innerhalb der Toleranz.

## Methodische Entscheidungen

1. **Randomisierte N statt Completer-N.** Die Review nutzt die
   randomisierten Arm-N. Bei Morris sind das 48/47, obwohl die Post-Werte
   auf 36/44 Completern beruhen. Mit 36/44 ergäbe sich g = -0.50 statt
   -0.51. Die Inkonsistenz wird dokumentiert, nicht stillschweigend
   korrigiert.
2. **Fucito-PSQI aus modellgeschätzten Mitteln.** Die Arbeit berichtet
   Woche 5 als Mittelwert mit Standardfehler: 10.85 (SE 0.44) vs.
   10.13 (SE 0.43) bei n = 21 je Arm. Die Review verwendet daraus
   SD = SE * sqrt(21) = 2.02 bzw. 1.97.
3. **de Bruin: IT gegen WL.** Der Internet-Arm ist die digitale
   Intervention; GT ist Gruppen-CBT-I und gehört nicht in diesen Pool.
   Die Werte sind 2.86 (0.71) vs. 3.74 (0.62).
4. **Fucito ist kein Nullbefund im Pool, sondern ein Gegenbefund.**
   Der positive SMD (+0.35) bedeutet, dass die Kontrolle in Woche 5
   numerisch etwas besser lag. Die Review berichtet diesen Wert selbst.

## Pipeline-Eingabe

`protokoll.md` enthält keinen Zielwert, keinen gepoolten Effekt und keine
Studien-SMDs. Der Antwortschlüssel liegt getrennt in
`antwortschluessel.json`. Die Pipeline erhält nur das Protokoll und die
Volltexte.

## Status

- Volltexte und extrahierte Texte liegen lokal unter `volltexte/` bzw.
  `volltexte_txt/` und sind wie beim CBT-I-Pilot nicht versioniert.
- Der Nachbau ist abgeschlossen; der Modelllauf wurde nicht gestartet.
- Ein Start bleibt bis zum B-Rücklauf und zur ausdrücklichen Freigabe
  blockiert.
