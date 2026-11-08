# Kopfzeilen-Blocker: abgelehnte Zeilen mit lesbarem Effekt

Stand: 2026-11-08T19:40:32+00:00. Read-only: kein Modell, kein Netz, keine Aenderung an der Pipeline.

## Kennzahlen

| Kennzahl | Wert |
|---|---:|
| untersuchte Dateien | 120 |
| erkannte Tabellenbloecke | 276 |
| von `effects_from_row` abgelehnte Zeilen | 5445 |
| davon mit lesbarem Effekt samt Intervall | **530** (9.73 %) |
| betroffene Bloecke | 71 |
| davon mit Effektwort im Zeilenlabel | 0 |
| davon mit Effektwort in der Caption | 0 |

## Kategorien

| Kategorie | Bedeutung | Zeilen |
|---|---|---:|
| `nur_kopf` | Zelle lesbar, Spaltenzahl passt, aber keine Effektspalte an ihrer Position | 187 |
| `position_daneben` | Effektspalte existiert, aber an anderer Stelle | 0 |
| `kopf_und_spalten` | Zelle lesbar, aber Kopf und Zeile haben verschieden viele Zellen | 343 |

## Beispiele

### `data/bench/sol/fulltext/0006a008e1b297223286ae631de14842.txt`

1 Bloecke, 44 abgelehnte Zeilen, 23 mit lesbarem Effekt.

- Block 1 (nur_kopf): `49.0 (42.0–55.0)` -> [49.0, 42.0, 55.0]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `97.6 (89.1–106.4)` -> [97.6, 89.1, 106.4]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `34.6 (31.6–37.4)` -> [34.6, 31.6, 37.4]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `58.6 (50.5–68.8)` -> [58.6, 50.5, 68.8]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `59.1 (54.4–66.3)` -> [59.1, 54.4, 66.3]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/015c19e709a25c77828bb7d61fd10e0a.txt`

2 Bloecke, 59 abgelehnte Zeilen, 4 mit lesbarem Effekt.

- Block 1 (kopf_und_spalten): `40.6 (30–61)` -> [40.6, 30.0, 61.0]; Spalten 5/3; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (kopf_und_spalten): `31.1 (24–53)` -> [31.1, 24.0, 53.0]; Spalten 5/3; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `8:00–10:00 and 1–2 h pre-bed` -> [8.0, 0.0, 10.0]; Spalten 8/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `Two studies explored the effects of protein to improve sleep. Both studies used the whey protein isolate α-lactalbumin (dose range 20–40 g) [ 24 , 28 ]. In one study with healthy general populations, pre-sleep protein supplementation increased TST by 55 min, alongside a 7% increase in SE [ 28 ]. In the study by MacInnis et al. [ 24 ], α-lactalbumin had no effect on sleep variables in a small sample of cyclists ( n = 6).` -> [24.0, 20.0, 40.0]; Spalten 1/6; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/019117c094a74a98b6c716158908153b.txt`

1 Bloecke, 43 abgelehnte Zeilen, 19 mit lesbarem Effekt.

- Block 1 (nur_kopf): `t = 2.48, p = 0.03*; BCa [1.18, 8.73]` -> [2.48, 1.18, 8.73]; Spalten 8/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `t = 0.11, p = 0.46; BCa [−2.96, 4.14]` -> [0.11, -2.96, 4.14]; Spalten 8/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `t = 0.29, p = 0.78; BCa [−63.92, 53.06]` -> [0.29, -63.92, 53.06]; Spalten 8/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `t = −0.32, p = 0.97; BCa [−5.97, 5.27]` -> [-0.32, -5.97, 5.27]; Spalten 8/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `t = 0.93, p = 0.47; BCa [−2.90, 19.27]` -> [0.93, -2.9, 19.27]; Spalten 8/8; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/019f9ba36dbb084b84a462d277828c4a.txt`

2 Bloecke, 24 abgelehnte Zeilen, 1 mit lesbarem Effekt.

- Block 2 (kopf_und_spalten): `We plan to recruit 60 patients based on power analysis. Power analysis was conducted with G*Power, V.3.1.9.2. 65 Relevant effect sizes (Hegdes g) for power analyses were based on a recent meta-analysis of randomised controlled trials aiming at improving sleep, but that also reported an impact on mental health. The meta-analysis reported (following the removal of outliers) a large, pooled effect size (g=0.97) on sleep quality. The pooled effect size for composite mental health outcomes was g=0.42. 66 The power analysis was based on estimates of changes in DLMO, which is one of the most important primary outcomes. Based on a previous controlled study, 67 we calculated the effect size, using the Comprehensive Meta-Analysis, V.4.0, 68 in favour of the bright light intervention on this parameter to equal a Cohen’s d of 0.64 post-treatment. Based on this, we assumed an effect size (Cohen’s d) for DLMO (primary outcome) of 0.60. Setting the alpha to 0.05, power (1–β) set to 0.80, and the correlation coefficient between repeated measures to r=0.50 showed that 24 patients are needed to detect significant time (pre–post) × group (SSWU-C vs WL) interaction effects. No previous study has investigated secondary (mental health) outcomes of bright light treatment at gradually advanced timing for DSWPD. In terms of secondary outcomes, we therefore set the expected effect size considerably lower (d=0.40), and the power analysis showed that a total of 52 patients are required. Taking into consideration an attrition rate of 10%, we aim to recruit a total of 60 patients.` -> [60.0, 4.0, 68.0]; Spalten 1/3; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/026fff3f427dc358940488292b465995.txt`

5 Bloecke, 46 abgelehnte Zeilen, 6 mit lesbarem Effekt.

- Block 2 (kopf_und_spalten): `ACV 58 [48-82], cPSV 44 [29-30], aPSV 63 [29-80]; ACV 30 [17-41], PSV 28 [17-53], aPSV 23 [21-45]; No statistically significant difference between ventilation modes` -> [58.0, 48.0, 82.0]; Spalten 8/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `PCV 63 [9-100]; PSV 37 [0-96] Not reported; Significantly improved sleep efficiency with PCV` -> [63.0, 9.0, 100.0]; Spalten 8/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `PSV 58% (25); PAV 60 (23); PSV 16 (2-74); PAV 9 (1-41); PSV 53 (59); PAV 24 (15); PAV associated with statistically significantly fewer arousals and episodes of asynchrony` -> [58.0, 2.0, 74.0]; Spalten 8/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `PAV+ 51 [13-66]; PSV 27 [6-22]; PAV+ 11 [4-25]; PSV 12 [3-16]; No statistically significant improvement found with PAV+` -> [51.0, 13.0, 66.0]; Spalten 7/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `NAVA 74 [52-77]; PSV 44 [29-74]; NAVA 18 [8-22]; PSV 34 [25-54]; NAVA statistically significant improvement in the efficiency and reduced fragmentation of sleep` -> [74.0, 52.0, 77.0]; Spalten 7/6; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/02b1b366d919e2891a1e3622f66f93d2.txt`

2 Bloecke, 118 abgelehnte Zeilen, 38 mit lesbarem Effekt.

- Block 1 (nur_kopf): `−5.4 (−7.1 to −3.7)` -> [-5.4, -7.1, -3.7]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `−6.6 (−8.3 to −5.0)` -> [-6.6, -8.3, -5.0]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `−2.4 (−3.7 to −1.1)` -> [-2.4, -3.7, -1.1]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `−3.9 (−5.2 to −2.6)` -> [-3.9, -5.2, -2.6]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `−24.2 (−32.4 to −16.1)` -> [-24.2, -32.4, -16.1]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/02be670d304e34c3e1fd462900a72df5.txt`

4 Bloecke, 80 abgelehnte Zeilen, 3 mit lesbarem Effekt.

- Block 2 (kopf_und_spalten): `5 mg or 0.5 mg melatonin capsules vs. placebo taken daily at bedtime on travel day and post-travel days 1-5` -> [5.0, 1.0, 5.0]; Spalten 7/1; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `2 mg prolonged-release Circadin pill vs. placebo taken daily 1-2 h before bedtime (bedtime between 2100-2200 h)` -> [2.0, 1.0, 2.0]; Spalten 7/1; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `2 mg melatonin drink (100 ml of 1% ethanol in water) vs. placebo drink administered every 2-3 h, starting at 1600–1700 h e` -> [2.0, 2.0, 3.0]; Spalten 7/1; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/03c5e3811b5f555bd893096579bab8c5.txt`

3 Bloecke, 76 abgelehnte Zeilen, 7 mit lesbarem Effekt.

- Block 2 (nur_kopf): `51.5 (23, 80)` -> [51.5, 23.0, 80.0]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `The proportion of patients transitioning from pre-treatment to LEM during the titration phase was 95.6% (95% CI 89.0–98.8%) overall and 92.0% (74.0–99.0%), 96.0% (79.6–99.9%), 95.2% (76.2–99.9%), and 100.0% (82.4–100.0%) in the Z-drug monotherapy, SUV monotherapy, SUV combination, and RMT combination cohorts, respectively (Table  2 ).` -> [95.6, 89.0, 98.8]; Spalten 1/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `95.6 (89.0–98.8)` -> [95.6, 89.0, 98.8]; Spalten 8/9; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `97.8 (92.2–99.7)` -> [97.8, 92.2, 99.7]; Spalten 8/9; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `82.2 (72.7–89.5)` -> [82.2, 72.7, 89.5]; Spalten 8/9; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/040c42e3f8bdbc015578ca5f0883f280.txt`

3 Bloecke, 47 abgelehnte Zeilen, 1 mit lesbarem Effekt.

- Block 1 (nur_kopf): `Except for carvedilol and nebivolol [ 70 , 71 ], beta-blockers have been shown to reduce nocturnal melatonin levels [ 70 , 72 , 73 ]` -> [70.0, 70.0, 71.0]; Spalten 2/2; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/05036150800b359e10ff34ef5d689c5e.txt`

2 Bloecke, 73 abgelehnte Zeilen, 5 mit lesbarem Effekt.

- Block 1 (kopf_und_spalten): `Months post-injury: Overall: 46 (13–102) ** Intervention to control group: 61 (28–115) ** Control to intervention group: 25 (10–72) **` -> [46.0, 13.0, 102.0]; Spalten 12/2; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (kopf_und_spalten): `Community-dwelling adults with persistent cognitive difficulties following mTBI. Age (years): 21–64 Intervention group: 45 (27) ** Control Group: 44 (28) **` -> [45.0, 21.0, 64.0]; Spalten 12/2; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (kopf_und_spalten): `Community-dwelling adults with PCS symptoms. Age (years): 18–65 Overall: 45 (12.2) *` -> [45.0, 18.0, 65.0]; Spalten 12/2; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (kopf_und_spalten): `There was a significant reduction in self-reported cognitive shortcomings as measured using CFQ scores in the intervention group. Mean difference in CFQ for Enzogenol ® versus the placebo was −6.9 points (95% CI; −10.8 to −4.1). Those in the intervention group had a 28% change versus a 22% change in the placebo group. p values were not documented. Enzogenol ® was associated with self-reported cognitive failures until the results stabilised at week 11. The observed benefits were stable during the 4-week period following cessation of the treatment. There were no significant treatment effects on working or episodic memory at 6 weeks based on WAIS and CVLT scores. Mean levels of anxiety and depression reduced by a similar amount in both groups at 6 weeks. Among those with moderate and severe levels of anxiety at baseline, 31% in the placebo group and 54% in the intervention group improved to normal levels at 6 weeks. Among those with moderate and severe depression at baseline, 71% in the placebo group and 83% in the intervention group improved to normal levels at 6 weeks There was a trend towards improved frequency of post-concussion symptoms as measured using the RPQ. Although, p -values were not listed, these improvements were referred to as “not statistically significant”.` -> [-6.9, -10.8, -4.1]; Spalten 6/2; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (kopf_und_spalten): `The visual memory domain of the ImPACT values reported significant improvements following the KD intervention. Scores increased from 56.0 (51.5–66.0) ** at baseline to 70.0 (64.5–79.5) ** post-intervention, where p = 0.02. This was a mean improvement of 12.2 points. Though not-significant, the PCSS scores reported a decrease from 33.0 (19.5–65.5) ** to 28.0 (13.5–50.0) ** from baseline to month 2, where p = 0.34, which may suggest improved symptomology. No significant changes were found in the PHQ-9, GAD-7 or M-BESS following the intervention.` -> [56.0, 51.5, 66.0]; Spalten 6/2; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/0641f9655f7e7cc63e875948d25fd4a7.txt`

6 Bloecke, 59 abgelehnte Zeilen, 3 mit lesbarem Effekt.

- Block 2 (nur_kopf): `2 mg/day, 1–2 hr before going to bed and after food` -> [2.0, 1.0, 2.0]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (nur_kopf): `15% (range 10–56%) a` -> [15.0, 10.0, 56.0]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 6 (kopf_und_spalten): `Four articles described the use of approved melatonin receptor agonists for non‐24: two were randomized, double‐blind, placebo‐controlled studies conducted in blind patients with non‐24, 64 , 66 one was a case report detailing use in two sighted patients with non‐24, 67 and another was a case report regarding use in a single patient with traumatic brain injury. 65 Diagnostic criteria for non‐24 were not consistent across studies, thus complicating interpretation.` -> [24.0, 24.0, 64.0]; Spalten 1/7; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/065c3e8085ced9b54f69747f38dbd28f.txt`

3 Bloecke, 41 abgelehnte Zeilen, 1 mit lesbarem Effekt.

- Block 2 (kopf_und_spalten): `As data from the UNICEF report indicate, physical activity levels among children and young people remain consistently low, whilst the amount of time spent sitting—often in front of screens—is on the rise [ 167 ]. This is also confirmed by the study conducted by Zawadzka et al. in all voivodeships in Poland on behalf of the Minister of Sport and Tourism [ 168 ]. Since the start of the coronavirus pandemic lockdown, the results of numerous observational studies have indicated longer screen time among children, significantly exceeding the recommendations of the American and Canadian Pediatric Societies, which call for a maximum of two hours of screen time [ 167 , 169 , 170 ].` -> [167.0, 167.0, 169.0]; Spalten 1/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/0746b9b47452c12115b4629c23d2bf0b.txt`

4 Bloecke, 50 abgelehnte Zeilen, 14 mit lesbarem Effekt.

- Block 2 (nur_kopf): `1 (1, 1.5)` -> [1.0, 1.0, 1.5]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `1 (1, 2)` -> [1.0, 1.0, 2.0]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `1 (0, 2)` -> [1.0, 0.0, 2.0]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `0 (0, 1)` -> [0.0, 0.0, 1.0]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `2 (1.5, 2)` -> [2.0, 1.5, 2.0]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/088725125a4fa9ef0cbf61ea9df9213c.txt`

4 Bloecke, 82 abgelehnte Zeilen, 2 mit lesbarem Effekt.

- Block 3 (nur_kopf): `5,792 ± 776.17` -> [776.17, 5.0, 792.0]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `5,992 ± 707` -> [707.0, 5.0, 992.0]; Spalten 3/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/08f4381fa3e95989a010dedf4ebe0b6b.txt`

2 Bloecke, 39 abgelehnte Zeilen, 8 mit lesbarem Effekt.

- Block 2 (kopf_und_spalten): `−2.22 [−3.47, −0.97]` -> [-2.22, -3.47, -0.97]; Spalten 7/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `−2.17 [−3.21, −1.12]` -> [-2.17, -3.21, -1.12]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `−2.95 [−4.08, −1.81]` -> [-2.95, -4.08, -1.81]; Spalten 7/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `−1.42 [−2.37, −0.47]` -> [-1.42, -2.37, -0.47]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `−2.43 [−3.76, −1.10]` -> [-2.43, -3.76, -1.1]; Spalten 7/6; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/08f8af50f7cffd0df7ef36111916afbc.txt`

3 Bloecke, 46 abgelehnte Zeilen, 2 mit lesbarem Effekt.

- Block 1 (kopf_und_spalten): `Most of the 52 intervention participants ( n  = 41, 85%) completed the full i-Sleep intervention. Four participants dropped out of the intervention (see flowchart, Fig. 1 ). The remaining participants completed 1 ( n  = 3), 2 ( n  = 1), or four sessions ( n  = 3).` -> [52.0, 41.0, 85.0]; Spalten 1/3; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (kopf_und_spalten): `On average patients were satisfied with the website (M = 7.67 on a scale 1–10, s.d.  = 0.98), with the feedback (M = 7.91, s.d.  = 0.87), and the online module (M = 7.91, s.d.  = 0.82, see online Supplementary Table S1). No adverse events related to the intervention or trial were reported.` -> [7.67, 1.0, 10.0]; Spalten 1/3; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/094b5a8ccd92d18f4af5176c8d2ea7f7.txt`

3 Bloecke, 44 abgelehnte Zeilen, 6 mit lesbarem Effekt.

- Block 2 (nur_kopf): `9 cases of children with Autistic Disorder (AD) aged from 2–11 years. Chronic sleep problems` -> [9.0, 2.0, 11.0]; Spalten 11/11; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `15 children with AS (DSM-IV) aged from 6–17 years with severe sleep problems for at least 3 months` -> [15.0, 6.0, 17.0]; Spalten 11/11; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `9 children and adolescents with Rett syndrome aged from 4 to 17 years. Mean age :10 years old` -> [9.0, 4.0, 17.0]; Spalten 11/11; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `11 children and adolescents with ASD aged from 5–15 years with chronic sleep disorders resistant to behavioral treatment` -> [11.0, 5.0, 15.0]; Spalten 11/11; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `12 children and adolescents with unspecified sleep problems, aged from 2–15 years: 5 patients with AD (ADOS and ADI-R), 3 patients with fragile X syndrome with AD, 3 patients with AD and fragile X syndrome, and 1 patient with fragile X premutation` -> [12.0, 2.0, 15.0]; Spalten 11/11; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/09e205fe7963bd9db926957e004d5b78.txt`

2 Bloecke, 16 abgelehnte Zeilen, 1 mit lesbarem Effekt.

- Block 2 (kopf_und_spalten): `The appropriate duration and frequency of exercise (where frequency refers to the number of days per week the exercise plan is executed) are crucial factors affecting sleep quality. The World Health Organization recommends, for the promotion and maintenance of health, a minimum of 5 days per week of medium-intensity aerobic physical activity for 30 min each time, or a minimum of 20 min of high-intensity aerobic exercise 3 days a week ( 74 ). Gong Mingjun et al. ( 76 ) used meta-analysis research methods, incorporating a sample of 1,270 subjects. They employed a random-effects model for overall effect size and heterogeneity tests to examine the effects of exercise interventions on sleep disorders. Intervention durations ranged from 4 to 48 weeks, divided into groups of 4–9 weeks, 12 weeks, 16–18 weeks, 24–25 weeks, and 48 weeks. Single exercise durations varied from 30 to 90 min, categorized into groups of 30–50 min, 55–60 min, and 70–90 min. Exercise frequency ranged from 2–7 times per week, divided into groups of 2 times/week, 3 times/week, and 4–7 times/week. Data analysis revealed that a regimen of exercising about 60 min each session, 3 times a week, for approximately 16 weeks had the most significant effect in improving sleep disorders. However, other research suggests that shorter exercise training durations (like 16 weeks of medium-intensity exercise) only influence the subjective sleep quality assessed by the PSQI and overall sleep score evaluations, with no impact on objective sleep measures ( 73 ).` -> [5.0, 1.0, 270.0]; Spalten 1/6; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/09ef041bc5277ed4a022ba661398ef70.txt`

3 Bloecke, 12 abgelehnte Zeilen, 1 mit lesbarem Effekt.

- Block 2 (nur_kopf): `IRR: 1.07; 95%CI: 1.01-1.14` -> [1.07, 1.01, 1.14]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/0b93c6155c05696625ffc7f400bb53a8.txt`

2 Bloecke, 27 abgelehnte Zeilen, 2 mit lesbarem Effekt.

- Block 2 (nur_kopf): `Terminal half-life: approximately 15 hours (range, 10–22 hours)` -> [15.0, 10.0, 22.0]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `In an analysis of nine clinical studies conducted during the clinical development program of lemborexant, which included assessments of next-morning or across-the-day residual medication effects, lemborexant did not negatively impact next-day functioning in healthy individuals or patients with insomnia. 137 Lemborexant treatment was associated with significantly greater alertness for up to 6 months versus placebo as determined by next-morning sleep diary ratings. 137 In addition, whereas zolpidem differed from placebo on multiple measures of the Cognitive Performance Assessment Battery, power of attention was the only measure that found significantly decreased performance with lemborexant compared with placebo, and only in one of two studies. 137 Similarly, lemborexant treatment was also not associated with statistically significant or clinically meaningful next-day impairment in a randomized, double-blind, double-dummy, placebo- and active-controlled, four-period, incomplete crossover study conducted in healthy volunteers to determine effects on driving performance during a standardized highway driving test in normal traffic. 138 However, while there were no stopped drives during the lemborexant conditions, driving ability was impaired in 2 of the 32 participants receiving lemborexant 10 mg, and the product label recommends that patients who take the 10-mg dose should be advised about the possibility of next-morning driving impairment due to individual variation in lemborexant sensitivity; of note, the recommended starting dose of lemborexant is 5 mg. 139 The effects of lemborexant, zolpidem, and placebo on auditory awakening threshold and postural stability in the middle of the night and upon morning awakening were assessed in healthy females (≥55 years of age) and males (≥65 years of age). 140 Neither lemborexant nor zolpidem impaired the ability of participants to awaken to auditory signals in the middle of the night (4 hours post-dose). 140 While both lemborexant and zolpidem induced significantly more postural instability than placebo in the middle of the night (4 hours post-dose), lemborexant was associated with significantly less postural instability than zolpidem. 140 In the morning (8 hours post-dose), postural instability was observed with zolpidem compared with placebo, but not for lemborexant compared with placebo. 140 An open-label pilot study ( NCT04009577 , E2006-A001-312) has been carried out to evaluate prespecified dosing approaches for direct transition from zolpidem to lemborexant. 141 , 142 The primary endpoint of the study, which was recently completed, is the proportion of patients with insomnia who successfully transition from intermittent or frequent zolpidem use to lemborexant 5 mg or 10 mg after 2 weeks of treatment. 142 Following the 2-week titration period, 43 out of 53 subjects (81.1%) transitioned to lemborexant.` -> [137.0, 1.0, 312.0]; Spalten 1/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/0de4f7e3db93ce2dd7f5f32ec9b36f7b.txt`

3 Bloecke, 52 abgelehnte Zeilen, 8 mit lesbarem Effekt.

- Block 2 (nur_kopf): `9 cases of children with autistic disorder (AD) aged from 2 to 11 years. Chronic sleep problems` -> [9.0, 2.0, 11.0]; Spalten 11/11; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `15 children with AS (DSM-IV) aged from 6 to 17 years with severe sleep problems for at least 3 months` -> [15.0, 6.0, 17.0]; Spalten 11/11; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `9 children and adolescents with Rett syndrome aged from 4 to 17 years. Mean age:10 years old` -> [9.0, 4.0, 17.0]; Spalten 11/11; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `11 children and adolescents with ASD aged from 5 to 15 years with chronic sleep disorders resistant to behavioral treatment` -> [11.0, 5.0, 15.0]; Spalten 11/11; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `12 children and adolescents with unspecified sleep problems, aged from 2 to 15 years: 5 patients with AD (ADOS and ADI-R), 3 patients with fragile X syndrome with AD, 3 patients with AD and fragile X syndrome, and 1 patient with fragile X premutation` -> [12.0, 2.0, 15.0]; Spalten 11/11; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/0f590a0ef8352cbd19896c2ea745690f.txt`

4 Bloecke, 82 abgelehnte Zeilen, 2 mit lesbarem Effekt.

- Block 2 (kopf_und_spalten): `The SS scale is divided into two components ( Figure 2 ). The first (SSa) measures the severity of fatigue, unrefreshing sleep, and cognitive symptoms using a 4-point Likert scale, with a total score ranging from 0 to 9. The second (SSb) consists of a checklist of 41 somatic symptoms, scored from 0 to 3 based on the number of symptoms reported by the patient: 0 symptoms (score of 0), 1 to 10 symptoms (score of 1), 11 to 24 symptoms (score of 2), and 25 or more symptoms (score of 3). The final SS score is calculated by summing the SSa and SSb scores, resulting in a total score between 0 and 12.` -> [2.0, 0.0, 9.0]; Spalten 1/3; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (nur_kopf): `12-week flexible-dose (10–60 mg/day)` -> [12.0, 10.0, 60.0]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/0ff7a6072dab56bd3af591bee509588c.txt`

1 Bloecke, 28 abgelehnte Zeilen, 1 mit lesbarem Effekt.

- Block 1 (nur_kopf): `1-2 g/d of combined DHA and EPA (preferably in a 2:1 ratio)` -> [2.0, 1.0, 2.0]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/10115ba260c143ec6a665c0317c63090.txt`

2 Bloecke, 22 abgelehnte Zeilen, 1 mit lesbarem Effekt.

- Block 1 (nur_kopf): `Delayed CBT minimum (≈06:00–07:00); ↑ nocturnal CBT; ↓ amplitude [ 85 , 86 ]` -> [6.0, 0.0, 7.0]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/10ba126fd391323480bf897847762feb.txt`

2 Bloecke, 126 abgelehnte Zeilen, 74 mit lesbarem Effekt.

- Block 1 (nur_kopf): `51.78 (49.23, 54.32)` -> [51.78, 49.23, 54.32]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `160.51 (158.09, 162.93)` -> [160.51, 158.09, 162.93]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `59.88 (56.98, 62.78)` -> [59.88, 56.98, 62.78]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `23.12 (22.42, 23.81)` -> [23.12, 22.42, 23.81]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `6.86 (6.43, 7.28)` -> [6.86, 6.43, 7.28]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/114009829f1ee266e64cf29eb422831a.txt`

3 Bloecke, 68 abgelehnte Zeilen, 2 mit lesbarem Effekt.

- Block 2 (nur_kopf): `28-h plasma cortisol at 20-60 minute intervals: Diurnal variation, phase, amplitude, mesor, phase angles` -> [28.0, 20.0, 60.0]; Spalten 12/12; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `Finally, among cohorts of advanced cancer patients, significant associations have been detected between disrupted circadian activity rhythms and fatigue ( 202 , 205 ), depressed mood ( 205 ), and poorer subjective sleep/sleep quality ( 203 , 206 ).` -> [205.0, 202.0, 205.0]; Spalten 1/12; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/11deac694e569988666e44dc4492feea.txt`

4 Bloecke, 42 abgelehnte Zeilen, 3 mit lesbarem Effekt.

- Block 1 (nur_kopf): `16 children (2–16 years)` -> [16.0, 2.0, 16.0]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (kopf_und_spalten): `Peirano et al. [ 10 ] investigated the possible effects of iron deficient anemia (IDA) in infancy and subsequent alterations in sleep organization. They enrolled 55 healthy 4-year-old children; 27 with IDA and 28 nonanemic controls, born full term, and with IDA assessed at 6, 12 and 18 months of age. Both control and experimental groups underwent iron therapy; children diagnosed with IDA at 6 months were administered oral ferrous sulphate 15 mg/day for one year, whereas those diagnosed at 12 or 18 months were supplemented with oral iron 30 mg/day for at least 6 months. A higher percentage of REM sleep was noted in the IDA group, due to both an increase in the number of the single REM stages and of their duration. Furthermore, in the experimental group, within the first sleep cycle, there was a tendency for a shorter first REM latency and for a briefer NREM sleep stage 2 and slow-wave sleep (SWS) duration. The study showed that the occurrence of IDA in early infancy is associated with long-term changes in the temporal organization of sleep stages.` -> [10.0, 6.0, 12.0]; Spalten 1/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (nur_kopf): `18 infants (12–20 weeks)` -> [18.0, 12.0, 20.0]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/12012c1b977b52f3499a02537b47166a.txt`

2 Bloecke, 46 abgelehnte Zeilen, 9 mit lesbarem Effekt.

- Block 2 (nur_kopf): `−2.092 (4.011; −10.130 to 5.946)` -> [-2.092, -10.13, 5.946]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `0.025 (0.037; −0.048 to 0.098)` -> [0.025, -0.048, 0.098]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `3.606 (4.085; −4.581 to 11.794)` -> [3.606, -4.581, 11.794]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `−0.033 (0.035; −0.104 to 0.038)` -> [-0.033, -0.104, 0.038]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `0.043 (0.072; −0.101 to 0.188)` -> [0.043, -0.101, 0.188]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/12b4ad401bd1d6181a503a14622e56b1.txt`

4 Bloecke, 90 abgelehnte Zeilen, 6 mit lesbarem Effekt.

- Block 2 (nur_kopf): `47 (20–87)` -> [47.0, 20.0, 87.0]; Spalten 2/2; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `3 (0.4–10 years)` -> [3.0, 0.4, 10.0]; Spalten 2/2; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `2.9 (0.4–10)` -> [2.9, 0.4, 10.0]; Spalten 2/2; Kopf-Effektspalten -; Label-Effektwort -
- Block 4 (kopf_und_spalten): `1.6 *** [0.8–2.3]` -> [1.6, 0.8, 2.3]; Spalten 8/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 4 (kopf_und_spalten): `0.9 ** [0.3–1.5]` -> [0.9, 0.3, 1.5]; Spalten 8/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/131dc3c03726768db8c2eec063db0386.txt`

2 Bloecke, 31 abgelehnte Zeilen, 4 mit lesbarem Effekt.

- Block 1 (nur_kopf): `Here, we conducted a study to document the bioavailability of melatonin after administration of an oral prolonged-release tablet and an immediate-release sublingual spray. Both preparations are of major interest. The prolonged-release tablet was developed to mimic the plateau observed with endogenous melatonin secretion, whereas the sublingual spray was designed to provide an early melatonin peak, and to limit first-pass hepatic metabolism, since vascularization is highly developed under the tongue. We also measured the metabolite 6-SMT, which has not been measured in previously published studies with such melatonin formulations [ 1 , 18 , 19 ]. Its determination is important as an index of the hepatic transformation of melatonin.` -> [6.0, 1.0, 18.0]; Spalten 1/1; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `AUC 0–540, AUC 0–420` -> [0.0, 0.0, 540.0]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `AUC 0–540, AUC 0–420` -> [0.0, 0.0, 540.0]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `The plasma melatonin AUC 0–540/420 /plasma 6-SMT AUC 0–540/420 ratio was 0.09 for the PR form and 0.16 for the IR form, in agreement with a lower hepatic transformation with the IR form.` -> [420.0, 0.0, 540.0]; Spalten 1/4; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/134ced883600564bab4f6164883762de.txt`

2 Bloecke, 34 abgelehnte Zeilen, 6 mit lesbarem Effekt.

- Block 2 (nur_kopf): `OR 1.20 (95% CI 1.05–1.37)` -> [1.2, 1.05, 1.37]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `OR 1.55 (95% CI 1.32–1.81)` -> [1.55, 1.32, 1.81]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `g = 0.71 (95% CI 0.12–1.31)` -> [0.71, 0.12, 1.31]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `g = −0.16 (95% CI −0.30 to −0.03)` -> [-0.16, -0.3, -0.03]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `OR 2.29 (95% CI 1.48–3.55)` -> [2.29, 1.48, 3.55]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/155f51f17ff6f11fabfd3ee98c52977e.txt`

6 Bloecke, 112 abgelehnte Zeilen, 57 mit lesbarem Effekt.

- Block 3 (kopf_und_spalten): `9.42 (1, 19.00)` -> [9.42, 1.0, 19.0]; Spalten 15/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `3.97 (1, 21.80)` -> [3.97, 1.0, 21.8]; Spalten 15/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `8.18 (1, 19.00)` -> [8.18, 1.0, 19.0]; Spalten 15/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `7.53 (4, 452.00)` -> [7.53, 4.0, 452.0]; Spalten 15/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `7.29 (1, 19.00)` -> [7.29, 1.0, 19.0]; Spalten 15/8; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/15ec49a74ee0d27a5d32270dfb907597.txt`

2 Bloecke, 35 abgelehnte Zeilen, 13 mit lesbarem Effekt.

- Block 1 (kopf_und_spalten): `0.7 (0.1, 3.2)` -> [0.7, 0.1, 3.2]; Spalten 6/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `85.9 (84.7, 87.1)` -> [85.9, 84.7, 87.1]; Spalten 5/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `44.2 (39.8, 48.6)` -> [44.2, 39.8, 48.6]; Spalten 5/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `2.9 (2.8, 3.0)` -> [2.9, 2.8, 3.0]; Spalten 5/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `434.5 (423.0, 446.0)` -> [434.5, 423.0, 446.0]; Spalten 5/4; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/166f633ccfd1d82c8c7df37a504ee9a7.txt`

3 Bloecke, 45 abgelehnte Zeilen, 9 mit lesbarem Effekt.

- Block 2 (kopf_und_spalten): `3.151 (2.728–3.640)` -> [3.151, 2.728, 3.64]; Spalten 7/3; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `0.317 (0.275–0.367)` -> [0.317, 0.275, 0.367]; Spalten 7/3; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `1.078 (1.010–1.150)` -> [1.078, 1.01, 1.15]; Spalten 7/3; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `0.645 (0.606–0.686)` -> [0.645, 0.606, 0.686]; Spalten 7/3; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `0.773 (0.718–0.831)` -> [0.773, 0.718, 0.831]; Spalten 7/3; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/16a1cfd5d279e4d1fd3a90d3c6768ec2.txt`

4 Bloecke, 70 abgelehnte Zeilen, 1 mit lesbarem Effekt.

- Block 2 (nur_kopf): `10 × 90‐min in‐person group sessions with 6 to 10 participants per group at a specialist outpatient ADHD clinic` -> [10.0, 6.0, 10.0]; Spalten 10/10; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/16d2c384b057665a2dd14c06bb2352e3.txt`

1 Bloecke, 29 abgelehnte Zeilen, 3 mit lesbarem Effekt.

- Block 1 (nur_kopf): `45 AD pts. Group P ( n = 11): plb Vitamin E and D; Group D ( n = 12): 1600 IU Vitamin D and Vitamin E plb; Group E ( n = 11): 600 IU synthetic Vitamin E plus Vitamin D plb; Group DE ( n = 11), 1,600 IU Vitamin D plus 600 IU synthetic Vitamin E for 60 ds` -> [45.0, 1.0, 600.0]; Spalten 3/3; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (kopf_und_spalten): `The AD inflammatory response involves both adaptive and non-adaptive immunity and occurs in two-steps ( 1 , 48 ). In the acute phase, the allergens cross the immune barrier and stimulate a T helper (Th) 2 response with the production of IL-4, IL-13, IL-22 and IL-31. Mast cells (MCs) are stimulated and degranulate, releasing histamine, IL-6, IL-8, prostaglandin D2 and tumor necrosis factor-alpha (TNF)- α together with IL-23 and IL-31 and other cytokines ( 48 , 49 ). Additionally, keratinocytes and Langerhans cells (LCs), release cytokines such as IL-10, IL-12, IL-18, IL-23, IL-17 and IL-22 and thymic stromal lymphopoietin (TSLP), leading to an enhanced Th2-type inflammatory response ( 48 , 50 , 51 ).` -> [2.0, 1.0, 48.0]; Spalten 1/3; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (kopf_und_spalten): `Angiogenesis, the process of forming new blood vessels, contributes to the pathophysiology of AD and other diseases such as psoriasis and melanoma ( 53–55 ). Keratinocytes and mast cells have been shown to be a major source of vascular endothelial growth factor (VEGF) expression in AD; in fact, VEGF levels are elevated in the serum and skin of patients with AD compared with healthy controls ( 53–57 ).` -> [53.0, 53.0, 55.0]; Spalten 1/3; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/172cd64290a1733bf8e40b99e1fa696a.txt`

1 Bloecke, 35 abgelehnte Zeilen, 5 mit lesbarem Effekt.

- Block 1 (nur_kopf): `Adults 18–84 yrs, 61+ 15–20%; subgroup analyses performed` -> [61.0, 18.0, 84.0]; Spalten 9/9; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `≥50 yrs, 34% 50–64, 39% 65–74, 28% ≥75` -> [50.0, 50.0, 64.0]; Spalten 9/9; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `50 (10,903 person-nights)` -> [50.0, 10.0, 903.0]; Spalten 9/9; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `Healthy high-altitude adults (≥40 years included within 26–64 age group); no chronic disease; non-smokers; long-term residents` -> [40.0, 26.0, 64.0]; Spalten 9/9; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `Adults aged 45–75 at baseline, follow-up screening at 50–80 years (includes older/elderly subgroup ~60+)` -> [50.0, 45.0, 75.0]; Spalten 9/9; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/17316b89f3a3a12489f69344d04faa9b.txt`

3 Bloecke, 53 abgelehnte Zeilen, 2 mit lesbarem Effekt.

- Block 1 (kopf_und_spalten): `A full range of genotoxicity tests, including in vitro non-mammalian [ 113 , [116] , [117] , [118] ] and in vitro mammalian cell systems [ 113 , 117 , 119 ], and in vivo mammalian system [ 120 , 121 ] tests consistently found no evidence that melatonin is genotoxic (neither mutagenic or clastogenic). Furthermore, several studies in various in vitro/in vivo systems have reported the anti-genotoxic action of melatonin [ [122] , [123] , [124] , [125] , [126] ], usually ascribed to its antioxidant activity.` -> [113.0, 113.0, 117.0]; Spalten 1/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (nur_kopf): `n = 13/2–50 yrs` -> [13.0, 2.0, 50.0]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/17dfec0d5550510082b4563aab14ba40.txt`

3 Bloecke, 65 abgelehnte Zeilen, 8 mit lesbarem Effekt.

- Block 2 (kopf_und_spalten): `3.40 (0.86–13.36)` -> [3.4, 0.86, 13.36]; Spalten 6/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `1.36 (0.43–4.33)` -> [1.36, 0.43, 4.33]; Spalten 6/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `0.49 (0.14–1.69)` -> [0.49, 0.14, 1.69]; Spalten 6/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `1.03 (0.99–1.07)` -> [1.03, 0.99, 1.07]; Spalten 6/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `1.08 (0.94–1.24)` -> [1.08, 0.94, 1.24]; Spalten 6/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/185faa5e36d0776c76ef400759a88be6.txt`

4 Bloecke, 54 abgelehnte Zeilen, 1 mit lesbarem Effekt.

- Block 3 (nur_kopf): `ISI, 43 ESS 44 , GAD-7, 45 VES-13, 46 SF-12v2, 47 BMQ 48` -> [43.0, -7.0, 45.0]; Spalten 2/2; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/188245dbfd21ce50b288159127e7492b.txt`

5 Bloecke, 96 abgelehnte Zeilen, 21 mit lesbarem Effekt.

- Block 1 (nur_kopf): `1.00 (0.75, 4.00)` -> [1.0, 0.75, 4.0]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `2.00 (0.00, 3.25)` -> [2.0, 0.0, 3.25]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `1.50 (0.00, 3.00)` -> [1.5, 0.0, 3.0]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `1.9 (0.675, 3.65)` -> [1.9, 0.675, 3.65]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `1.15 (0.0, 1.525)` -> [1.15, 0.0, 1.525]; Spalten 6/6; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/19602681fd8902b18ec788e6aefdc423.txt`

3 Bloecke, 66 abgelehnte Zeilen, 3 mit lesbarem Effekt.

- Block 1 (nur_kopf): `Observational studies in children have found high Pittsburgh Sleep Quality Index (PSQI) scores that are at or above the clinical cutoff for poor sleep quality ( 6 , 7 ). Children who report poor sleep also report high diabetes-specific stress, poor diabetes self-management, and high state anxiety ( 7 ). A case–control study of 154 subjects, which investigated three pediatric populations (children, adolescents, and young adults), showed that young adults had higher PSQI scores than controls, while children and adolescents were no different than controls. No significant correlations were found between the self-reported sleep quality assessed using PSQI score and diabetes duration, HbA1c, the mode of therapy, the mode of glucose monitoring, or the rate of nocturnal hypo- or hyperglycemic episodes ( 11 ) (` -> [7.0, 6.0, 7.0]; Spalten 1/1; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (nur_kopf): `Adults, age 19–61 years, 58.8% male, HbA1c 7.3%` -> [58.8, 19.0, 61.0]; Spalten 9/9; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `When analyzing sleep quality with glycemia, poor sleep quality was significantly associated with greater glycemic variability after accounting for age, sex, and body mass index (BMI). Those participants with poor sleep quality had greater nocturnal glycemic variability than those with good sleep ( 19 – 21 ). Higher glucose levels and lower time in range were associated with poorer sleep quality ( 21 , 22 ).` -> [21.0, 19.0, 21.0]; Spalten 1/9; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/198c7b6dfdfea7d6960dd5262c851f6a.txt`

2 Bloecke, 110 abgelehnte Zeilen, 1 mit lesbarem Effekt.

- Block 2 (nur_kopf): `1,885 [581; 3,654]` -> [581.0, 1.0, 885.0]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/19cd2520d212256fc718fda99cdcf7f5.txt`

3 Bloecke, 33 abgelehnte Zeilen, 5 mit lesbarem Effekt.

- Block 2 (kopf_und_spalten): `In the delayed phase, plasma melatonin concentration 4–6 h post-administration exhibited a significant increase with Oniria ® compared with IRT (three times higher; Fig. 4 ). In addition, Oniria ® showed concentrations still surpassing the described endogenous melatonin peak of 80 pg/mL 6–8.5 h post-administration (2.5 h longer than the reference formulation) (Fig. 4 ). Fig. 4 Linear plot of melatonin plasma concentration in the 2–11 h timeframe post-administration (delayed phase). Mean plasma concentrations of exogenous melatonin formulations administered in fasting conditions, compared with endogenous melatonin profile. x3 indicates three times higher Oniria melatonin concentration vs Melatoplus` -> [4.0, 4.0, 6.0]; Spalten 1/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `0.50 (0.25–1.50)` -> [0.5, 0.25, 1.5]; Spalten 9/1; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `0.75 (0.25–1.50)` -> [0.75, 0.25, 1.5]; Spalten 9/1; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (kopf_und_spalten): `5.50 (2.50–10.00)` -> [5.5, 2.5, 10.0]; Spalten 9/1; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (nur_kopf): `In the case of t max , the median value for melatonin was 0.50 h for Oniria ® and 0.75 h for IRT (15 min), with a range of 0.25–1.50 h for both formulations.` -> [0.5, 0.25, 1.5]; Spalten 1/1; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/1b0ad5a4211bf81b849a25b746dadaf0.txt`

1 Bloecke, 49 abgelehnte Zeilen, 2 mit lesbarem Effekt.

- Block 1 (kopf_und_spalten): `IVA-CPT scores improved from baseline to 3 months follow-up, as well as from 3 to 6 months follow-up. Severity of OSAHS was associated with worse Full Attention Quotient scores, but not Hyperactivity or Full Scale Response Control Quotient.` -> [3.0, 3.0, 6.0]; Spalten 10/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (kopf_und_spalten): `29 children with narcolepsy type 1, 39 controls. Sex: 36 males, 32 females Age (M±SD), years: narcolepsy type 1: 11.52± 2.89; control: 11.21±3.44` -> [29.0, 1.0, 39.0]; Spalten 10/8; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/1b14023562a7ff34d8c27d9a8f72ee08.txt`

4 Bloecke, 66 abgelehnte Zeilen, 4 mit lesbarem Effekt.

- Block 1 (nur_kopf): `Sleep efficiency improved by 1.88 percentage points (95% CI 1.00–2.77 percentage points); no statistically significant effect on sleep latency or duration.` -> [1.88, 1.0, 2.77]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `Latest versus earliest tertile adjusted PSQI differences: first meal +0.545 (95% CI 0.226–0.864), midpoint +0.586 (0.277–0.896), and last meal +0.385 (0.090–0.680).` -> [0.545, 0.226, 0.864]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `General drinking: OR 1.37 (95% CI 1.22–1.54); heavy drinking subgroup: OR 1.22 (95% CI 0.94–1.60).` -> [1.37, 1.22, 1.54]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `Daily consumption was associated with short sleep, with RR 2.07 (95% CI 1.77–2.42) in men and 1.87 (1.64–2.14) in women.` -> [2.07, 1.77, 2.42]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/1bb6cc56874f97fb4f253f194a574f1d.txt`

2 Bloecke, 10 abgelehnte Zeilen, 4 mit lesbarem Effekt.

- Block 1 (nur_kopf): `−0.12 (95% CI: −0.20, −0.04)` -> [-0.12, -0.2, -0.04]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `1.45 (1.22–1.72)` -> [1.45, 1.22, 1.72]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `1.89 (1.65–2.17)` -> [1.89, 1.65, 2.17]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `2.54 (2.20–2.93)` -> [2.54, 2.2, 2.93]; Spalten 4/4; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/1bddfad854558113b1d43c1974160067.txt`

4 Bloecke, 72 abgelehnte Zeilen, 12 mit lesbarem Effekt.

- Block 1 (nur_kopf): `44.7 ± 11.9 (21–67)` -> [44.7, 21.0, 67.0]; Spalten 2/2; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `3.5 ± 2.2 (0.5–11)` -> [3.5, 0.5, 11.0]; Spalten 2/2; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `16.50 (14.75, 18.00)` -> [16.5, 14.75, 18.0]; Spalten 2/2; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `3.00 (2.00, 3.00)` -> [3.0, 2.0, 3.0]; Spalten 8/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `2.00 (1.00, 3.00)ᵃ` -> [2.0, 1.0, 3.0]; Spalten 8/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/1bf4688b968c4d000bd8a31ab224585f.txt`

4 Bloecke, 74 abgelehnte Zeilen, 8 mit lesbarem Effekt.

- Block 2 (nur_kopf): `4.6 (2.2) [2.6-9.6]` -> [4.6, 2.6, 9.6]; Spalten 10/10; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `8.7 (4.15) [2-17]` -> [8.7, 2.0, 17.0]; Spalten 10/10; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `4-12 mo (Mean, 7.5 mo)` -> [7.5, 4.0, 12.0]; Spalten 10/10; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `5.9 (NA) [3-10]` -> [5.9, 3.0, 10.0]; Spalten 10/10; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `0-2, 2-5` -> [2.0, 0.0, 2.0]; Spalten 9/10; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/1c5bb40083cf7c15e1f8867b76a386d2.txt`

5 Bloecke, 107 abgelehnte Zeilen, 2 mit lesbarem Effekt.

- Block 1 (nur_kopf): `37.07 (20-67)` -> [37.07, 20.0, 67.0]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `Years of Schooling 7–14 14–20` -> [14.0, 7.0, 14.0]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/1c5c16c7488cc3cb6301319faf0fd28d.txt`

8 Bloecke, 191 abgelehnte Zeilen, 2 mit lesbarem Effekt.

- Block 2 (nur_kopf): `24 (14-50.5)` -> [24.0, 14.0, 50.5]; Spalten 2/2; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (nur_kopf): `188 (70-528)` -> [188.0, 70.0, 528.0]; Spalten 2/2; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/1cbb4c256297be13f057132c2674289a.txt`

4 Bloecke, 81 abgelehnte Zeilen, 34 mit lesbarem Effekt.

- Block 1 (nur_kopf): `40 (31.5–53.0)` -> [40.0, 31.5, 53.0]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (nur_kopf): `36 (17.75–79.5)` -> [36.0, 17.75, 79.5]; Spalten 5/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 1 (kopf_und_spalten): `For the primary outcome, at post-treatment, the linear mixed model for insomnia severity showed a significant time*group interaction effect, F (2, 178.96) = 6.03, p = 0.001, indicating that the change in ISI over time was significantly different between the two groups at post-treatment. Specifically, the estimated effect toward ISI decreased by 3.8-fold [standard error (SE) = 1.1] in the iCBT-I group compared to the CAU group. At follow-up, there were no significant between-group differences ( p = 0.16).` -> [6.03, 2.0, 178.96]; Spalten 1/5; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `0.21 (−0.63, 3.94)` -> [0.21, -0.63, 3.94]; Spalten 8/6; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `0.27 (−0.15, 4,05)` -> [0.27, -0.15, 4.05]; Spalten 8/6; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/1cf23279ef71541391a6d432a37e6586.txt`

4 Bloecke, 66 abgelehnte Zeilen, 5 mit lesbarem Effekt.

- Block 3 (nur_kopf): `Twins N = 11,604 BE = 427/92% NE = 419/54%` -> [427.0, 11.0, 604.0]; Spalten 8/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 3 (nur_kopf): `Total = 1,636/59.5%` -> [59.5, 1.0, 636.0]; Spalten 8/8; Kopf-Effektspalten -; Label-Effektwort -
- Block 4 (nur_kopf): `Laboratory sessions: Fluorescent “BLT” (2,500 lux) or “Dim light” (500 lux) at 3 ft. from source at 17:00 h. 2 h/session, 6 days` -> [500.0, 2.0, 500.0]; Spalten 9/9; Kopf-Effektspalten -; Label-Effektwort -
- Block 4 (nur_kopf): `Early morning (7:00 to 8:00 am) BLT (10,000 lux) or Dim red light (500 lux) for 30 min` -> [7.0, 0.0, 8.0]; Spalten 9/9; Kopf-Effektspalten -; Label-Effektwort -
- Block 4 (kopf_und_spalten): `In the only study that administered BLT in the evening, 18 patients were randomized to receive 2 weeks of bright (2,500 lux, n = 9) or moderate (500 lux, n = 9) light, each given at 17:00 h for 2 h and at three feet from the light source ( 74 ). There were no significant differences between the active or sham groups regarding frequencies of BE or compensatory behaviors, or in perceived control of food intake.` -> [18.0, 2.0, 500.0]; Spalten 1/9; Kopf-Effektspalten -; Label-Effektwort -

### `data/bench/sol/fulltext/1d53ef275903943af47cfd720fc37344.txt`

6 Bloecke, 137 abgelehnte Zeilen, 65 mit lesbarem Effekt.

- Block 2 (kopf_und_spalten): `09:00 (08:05 – 10:30)` -> [9.0, 5.0, 10.0]; Spalten 6/1; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `8.18 (7.31 – 8.50)` -> [8.18, 7.31, 8.5]; Spalten 6/1; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `7.19 (6.44 –7.48)` -> [7.19, 6.44, 7.48]; Spalten 6/1; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `08:45 (08:04 – 10:10)` -> [8.0, 4.0, 10.0]; Spalten 6/1; Kopf-Effektspalten -; Label-Effektwort -
- Block 2 (kopf_und_spalten): `7.15 (6.42 – 7.51)` -> [7.15, 6.42, 7.51]; Spalten 6/1; Kopf-Effektspalten -; Label-Effektwort -

## Was die Zahl bedeutet

530 von 5445 abgelehnten Zeilen tragen einen lesbaren Effekt samt Intervall (9.73 %). Davon haetten 187 bei stimmiger Spaltenzuordnung nur am Kopf gescheitert; die uebrigen scheitern zusaetzlich an der Spaltenzuordnung oder an der Position der Effektspalte. Ein Kopfzeilen-Fix allein rettet also hoechstens 187 Zeile(n).

## Grenzen

- Gemessen wird nur, was `parse_effect_cell` lesen kann; andere Schreibweisen zaehlen als nicht lesbar.
- Eine lesbare Zelle belegt nicht die richtige Zuordnung zu Endpunkt, Arm und Zeitpunkt. Die Messung sagt nur, ob die Zahl maschinenlesbar vorliegt.
- Die Stichprobe ist der lokale Textbestand, keine Aussage ueber den gesamten Korpus.
- `parse_effect_cell` liest auch Baseline-Zeilen wie `106 (34.8), 44 to 181` als Effekt mit Intervall. Die Kategorie `nur_kopf` ist deshalb eine OBERGRENZE, keine Trefferzahl: bei MENDS sind ihre drei Zeilen Baseline-Mittelwerte, keine Effekte.

## Reproduktion

```bash
export PYTHONIOENCODING=utf-8
.venv/bin/python.exe scripts/messe_kopf_blocker.py \
  --file data/bench/sol2/volltext/23098680.txt
```

Laufzeit: 3.339 s.
