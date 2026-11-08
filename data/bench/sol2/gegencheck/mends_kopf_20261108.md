# Warum der MENDS-Text keine Effektspalte im Kopf findet

Stand: 2026-11-08T19:20:51. Quelle: `data/bench/sol2/volltext/23098680.txt`. Read-only, kein Netz, kein Modell.

Roh: 841300 Zeichen, normalisiert: 831660 Zeichen, erkannte Bloecke: **48**.

## Ablehnungsregel

`header_effect_kind` akzeptiert eine Kopfzelle nur, wenn sie **selbst** ein Effektwort (g, SMD, mean difference, OR, RR, HR, beta) **und** eine CI-Markierung (`CI` oder `confidence interval`) enthaelt. Punktschaetzer und Intervall in zwei getrennten Spalten gelten nur, wenn die Punktspalte links daneben ein Effektwort traegt (`_paired_point`).

## Befund je Block (Kopfzeile)

| Befund | Bloecke |
|---|---:|
| weder Effektwort noch CI | 47 |
| CI ohne Effektwort | 1 |

## Haeufigste Kopfzeilen

- 3x `Reason for missing data | Placebo, n | T+12W | Melatonin, n | T+12W`
- 2x `Laboratory result | Melatonin | Placebo | Total`
- 1x `ISSN 1366-5278 (Print)`
- 1x `Children's Hospital | 2007 | 15 | 30 July 2009`
- 1x `Baseline characteristic | Melatonin (n=70) | Placebo (n=76) | Total (n=146)`
- 1x `T5 | 51 | 59 | 110 | 9 | 17.6 13 | 25.5 10 | 19.6 19 | 37.3 1 | 1.7 5 | 8.5 10 | 16.9 43 | 72.9`
- 1x `T0 | 70 | 76 | 146 | 70 | 100 | 0 | 0 | 0 | 76 | 100 | 0 | 0 | 0`
- 1x `and outcomes | (SD) | 571.26 (71.98) | (SD) | (SD) | 558.03 (68.94) | (SD) | over baseline`
- 1x `CSDI (0-12) (nM=60, | mean (95% CI), p-value`
- 1x `which the parent was | 31.25 (34.25), 0 | to 100 | -100 to 83.33 | 33.74 (35.26), 0 | to 100 | -0.28 (1.37), | p=0.52 | `
- 1x `Sample status | Melatonin | Placebo`
- 1x `0.05`

## Einschaflatenz im Text

125 Fundstellen von 'sleep onset' / 'SOL'.

- Zeile 108: `measures included TST calculated using actigraphy data, sleep-onset latency (SOL) (time`
- Zeile 108: `measures included TST calculated using actigraphy data, sleep-onset latency (SOL) (time`
- Zeile 124: `measured using sleep diaries. A reduction in SOL, adjusted for baseline, was seen for`
- Zeile 133: `Melatonin is effective in reducing SOL in children with neurodevelopmental delay by a`
- Zeile 243: `SOL                    sleep-onset latency`
- Zeile 243: `SOL                    sleep-onset latency`
- Zeile 290: `included TST calculated using actigraphy data, sleep-onset latency (SOL) (time taken to fall`
- Zeile 290: `included TST calculated using actigraphy data, sleep-onset latency (SOL) (time taken to fall`
- Zeile 411: `The outcome of SOL measured the time taken for a child to go to sleep from `snuggle-down`
- Zeile 413: `between the treatment groups, adjusting for mean baseline SOL, was -37.49 minutes (95% CI`
- Zeile 433: `worthwhile difference specified at the outset of the trial. Melatonin is effective in reducing SOL in`
- Zeile 568: `time it takes children to fall asleep (time to sleep onset or sleep latency) and increasing the`
- Zeile 580: `disorders and idiopathic chronic sleep-onset insomnia20,21 as well as in some children with`
- Zeile 761: `target sleep onset time earlier than 20:30 for children at age 6 years and 15 minutes later`
- Zeile 879: `Sleep diaries were used to calculate TST, SOL (the time taken to fall asleep) and daily global sleep`
- Zeile 906: `10-minute period as the time of sleep onset.`
- Zeile 1004: `Total night-time sleep was calculated as the sum of all epochs scored as sleep from sleep onset to`
- Zeile 1209: `SOL (the time taken to fall asleep) calculated using actigraphy.`
- Zeile 1210: `SOL (the time taken to fall asleep) calculated using sleep diaries (the number of minutes`
- Zeile 1239: `TST calculated using the data recorded in sleep diaries and SOL calculated using actigraphy.`
- Zeile 1243: `by the Trial Management Group to amend the protocol to move the end point SOL measured`
- Zeile 1268: `For the outcome SOL, the null hypothesis is that there is no difference in the time to sleep`
- Zeile 1270: `is a difference in the time to sleep onset. A sample size of 78 in each group (86 per group with`
- Zeile 1277: `night-time sleep and actigraphy for time to sleep onset. Both outcomes will be analysed using`
- Zeile 1282: `of the sample size calculations for the outcomes SOL (n=172) and TST (n=126). The original`
- ... 100 weitere

## Bloecke, die die Einschaflatenz enthalten

4 von 48 Bloecken.

### Block 6: `(pipe table at char 156219)`

- Kopf: `and outcomes | (SD) | 571.26 (71.98) | (SD) | (SD) | 558.03 (68.94) | (SD) | over baseline`
- Spalten: 8, Zeilen: 16
- Kopfzellen mit CI: 0, mit Effektwort: 0, mit beidem: 0
- gelesene Effekte: 0
- Ablehnungsgruende: {'Kopfzeile (8 Spalten) passt nicht zur Zeile (3 Zellen) - col': 4, 'Kopfzeile (8 Spalten) passt nicht zur Zeile (1 Zellen) - col': 3, 'Kopfzeile (8 Spalten) passt nicht zur Zeile (2 Zellen) - col': 2, 'Kopfzeile (8 Spalten) passt nicht zur Zeile (7 Zellen) - col': 2}

  - `['SOL (minutes)', '-3.71 (47.37)', '(p=0.007)', '(p<0.0001)']`
  - `['SOL (minutes)', '(p=0.0004)', '(p=0.0003)']`

### Block 13: `(pipe table at char 188436)`

- Kopf: `700`
- Spalten: 1, Zeilen: 24
- Kopfzellen mit CI: 0, mit Effektwort: 0, mit beidem: 0
- gelesene Effekte: 0
- Ablehnungsgruende: {'keine Effektspalte im Kopf': 19, 'Kopfzeile (1 Spalten) passt nicht zur Zeile (2 Zellen) - col': 3, 'Kopfzeile (1 Spalten) passt nicht zur Zeile (9 Zellen) - col': 1, 'Kopfzeile (1 Spalten) passt nicht zur Zeile (4 Zellen) - col': 1}

  - `['SOL T0 (minutes)']`
  - `['FIGURE 9 Relationship between melatonin levels and sleep disorders. (a) DLMO quartiles against SOL displayed as box plots and histograms at baseline`

### Block 20: `TABLE 25. Reasons for missing data completed for SOL using sleep diaries`

- Kopf: `Reason for missing data | Placebo, n | T+12W | Melatonin, n | T+12W`
- Spalten: 5, Zeilen: 14
- Kopfzellen mit CI: 0, mit Effektwort: 0, mit beidem: 0
- gelesene Effekte: 0
- Ablehnungsgruende: {'keine Effektspalte im Kopf': 9, 'Kopfzeile (5 Spalten) passt nicht zur Zeile (2 Zellen) - col': 2, 'Kopfzeile (5 Spalten) passt nicht zur Zeile (1 Zellen) - col': 2, 'Kopfzeile (5 Spalten) passt nicht zur Zeile (3 Zellen) - col': 1}

  - `['Child only had 1/7 nights completed SOL', 'T0W', '0', 'T0W', '1']`
  - `['Child only had 2/7 nights completed SOL', '1', '0']`
  - `['Child only had 3/7 nights completed SOL', '0', '1', '0', '2']`
  - `['Child only had 4/7 nights completed SOL', '1', '6', '3', '1']`

### Block 21: `TABLE 26. Reasons for missing data completed for SOL using actigraphy`

- Kopf: `Reason for missing data | Placebo, n | T+12W | Melatonin, n | T+12W`
- Spalten: 5, Zeilen: 6
- Kopfzellen mit CI: 0, mit Effektwort: 0, mit beidem: 0
- gelesene Effekte: 0
- Ablehnungsgruende: {'keine Effektspalte im Kopf': 5, 'Kopfzeile (5 Spalten) passt nicht zur Zeile (3 Zellen) - col': 1}

  - `['Child only had 1/7 nights data completed for SOL', 'T0W', '1', 'T0W', '3']`
  - `['Child only had 2/7 nights data completed for SOL', '2', '2']`
  - `['Child only had 3/7 nights data completed for SOL', '1', '2', '4', '3']`
  - `['Child only had 4/7 nights data completed for SOL', '3', '5', '4', '6']`


## Effektgroesse im Fliesstext

2 SOL-Saetze mit Intervall. Kein Tabellenleser sieht sie: `effects_from_row` arbeitet nur auf Zeilen erkannter Bloecke, und ein Satz ist kein Block.

- Zeile 413: The outcome of SOL measured the time taken for a child to go to sleep from `snuggle-down time'. This was calculated using both the actigraphy data and the sleep diary. The mean difference between the treatment groups, adjusting for mean baseline SOL, was -37.49 minutes (95% CI -55.27 to -19.71 minutes; p<0.0001) in favour of the melatonin group using the sleep diary and -45.34 minutes (95% CI -68.75 to -21.93 minutes; p=0.0003) using actigraphy. Both measures showed that the time taken to fall asleep by children in the melatonin group was statistically � Queen's Printer and Controller of HMSO 2012. This work was produced by Appleton et al. under the terms of a commissioning contract issued b
- Zeile 1729: The outcome of SOL measured the time taken for a child to go to sleep from `snuggle-down' time. This was calculated using both actigraphy and sleep diary data. The mean difference between treatment groups, adjusting for the mean baseline SOL, was -37.49 minutes (95% CI -55.27 to -19.71 minutes) using the sleep diary and -45.34 minutes (95% CI -68.75 to -21.93 minutes) using actigraphy in favour of the melatonin group. Both measures showed that the time taken to fall asleep by children in the melatonin group was statistically and clinically significantly less than that in the placebo group. The adjusted difference in sleep efficiency between the two treatment groups was not statistically sign
## Grenzen

- Nur eine Datei (MENDS-Doppelpublikation).
- Blockbildung und Kopfzeile haengen davon ab, wie die `.txt` umgebrochen ist; die Produktionskette liest die PDF.
- Die Diagnose aendert keinen Code und keine Daten.
