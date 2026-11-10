# Goldstandard: Duplikate in den Pipeline-Zeilen (2026-11-10)

Read-only, kein Modellaufruf. Dedupe-Regel wie im Pooling: Zwilling ist
gleiche Quelle plus gleicher Effekt (9 Stellen, SE) oder gleicher
normalisierter Zitattext (erste 200 Zeichen). Die erste Zeile bleibt.

**37 Zeilen, 24 unique, 13 Duplikate** (12 Wert-Zwillinge, 1 Zitat-Zwillinge) in 12 von 30 Dokumenten.

Prueffrage je Zeile: Ist die Doppelung eine echte zweite Lesung oder
eine andere Aussage mit gleichem Wert/Beleg? Nur im zweiten Fall darf
die Zeile fachlich stehen bleiben; der Abgleich zaehlt sie dennoch
einmal, weil das Pooling sie ebenfalls einmal zaehlt.

| Dokument | Stratum | Dup-ID | Original-ID | Grund | Outcome | Typ | Effekt | KI | poolbar | Zitat |
|---|---|---|---|---|---|---|---|---|---|---|
| 3134fdc8c3 | cohort | 558364b463 | 309a2d3433 | Wert | depressive symptoms | rr | 1.1 | 1.04-1.18 | ja | High UPF consumption at time zero was associated with an increased risk of depressive symptoms at follow-ups (RR: 1.10; CI: 1.04–1.18). |
| d0bec407a2 | cohort | 4c8774f123 | 28f5c2501d | Wert | colorectal cancer risk | hr | 0.95 | 0.87-1.05 | ja | The HRs for colorectal cancer risk for high (75th percentile; 411 min/week) versus low (25th percentile; 62 min/week) levels of self-reported physica… |
| bb9218735f | rct | 36e42882e6 | 28fd9333e3 | Wert | sleep quality | z | -2.44 | n/a | nein | Quality of sleep ratings from the Daily Sleep Diaries showed that the average gain in sleep quality was significantly greater in the ML 2.5SR group t… |
| bb9218735f | rct | 7ebbe24a69 | 28fd9333e3 | Wert | sleep quality | z | -2.44 | n/a | nein | Quality of sleep ratings from the Daily Sleep Diaries showed that the average gain in sleep quality was significantly greater in the ML 2.5SR group t… |
| fb484d488b | rct | 3172c98126 | 18c9cbfed2 | Wert | depressive symptoms | g | -0.37 | -0.56--0.17 | ja | The standardized mean difference across studies was g = -0.37, 95% confidence interval (-0.56; -0.17), and the null hypothesis of homogeneity within … |
| 2c7ab4d124 | cross_sectional | b6bcefe80b | 8a217ca980 | Wert | depressive symptoms | or | 2.01 | 1.08-3.75 | ja | In multivariate analysis (Table 3), those participants who were illiterate were twice as likely to be depressed compared to those who were literate (… |
| 09843d40d3 | cohort | 8c16a31675 | 8493714013 | Wert | depressive symptoms | beta | -0.024 | n/a | nein | Specifically, for each additional minute of physical exercise time, depressive symptoms scores decreased by an average of 0.024 points ( β=−0.024, p … |
| 334f5f6798 | aggregate | e4d1b9d6b1 | 19d3007b1d | Wert | depressive symptoms | smd | -2.02 | -2.8--1.17 | ja | AE presented the optimal dose at 1000METs-min/week (SMD: -2.02; 95% Crl (-2.80 to -1.17)) in this study, and the minimum effective dose was 350 METs-… |
| b5e492009e | rct | 87aee722db | 06110eb3a5 | Wert | depressive symptoms | smd | -0.82 | -1.19--0.45 | ja | The findings demonstrated a notable improvement in depression symptoms among older persons as an immediate result of engaging in physical exercise [S… |
| 3790c91f96 | cohort | bf76f02078 | 302e393aea | Zitat | depressive symptoms | r | -0.206 | n/a | nein | PA was significantly negatively correlated with emotional depressive symptoms (rs=[−0.150, −0.206]; P < 0.001) and physical depressive symptoms (rs=[… |
| 1faf4b78f0 | cross_sectional | db268ea1b4 | 0bc50c14c1 | Wert | depressive symptoms | beta | -0.08 | n/a | nein | the results also showed that physical exercise had a negative predictive eﬀect on the depression of college students ( β = −0.08, P < 0.05), the dire… |
| 5cbf039f22 | aggregate | 87d5f9d02e | 0245d800c7 | Wert | depressive symptoms | g | -0.28 | -0.43--0.13 | ja | Bayesian random-effects model analysis indicated that compared to the control group, aerobic exercise significantly improved adolescent depression sy… |
| cfc6567ca3 | aggregate | a0a1b6e425 | 95dc509e54 | Wert | depressive symptoms | g | 1.09 | n/a | nein | Results showed that flexibility training had the most significant effect on alleviating depressive symptoms (g = 1.09, P < 0.01), followed by traditi… |

## Betroffene Dokumente

- `3134fdc8c38f475075a70ca32dc4a3d9` (cohort, The risk associated with ultra-processed food intake on depressive sym): 2 Zeilen, 1 Duplikate
- `d0bec407a2a0dd19c0b67aa43f9e1dfb` (cohort, A quantitative bias analysis to estimate measurement error-related att): 2 Zeilen, 1 Duplikate
- `bb9218735fec8fc7f3b6aebbff430aba` (rct, A Multicenter, Placebo-controlled Trial of Melatonin for Sleep Disturb): 3 Zeilen, 2 Duplikate
- `fb484d488b45d21bbdf407cba4b074d5` (rct, The effect of exercise on depressive symptoms in multiple sclerosis ba): 2 Zeilen, 1 Duplikate
- `2c7ab4d1244754e3966780f4bccbfa8c` (cross_sectional, Prevalence of depressive symptoms and its associated factors in older): 2 Zeilen, 1 Duplikate
- `09843d40d3cc2c9ca039d6d1b45ac656` (cohort, Bidirectional relationships between physical exercise and depressive s): 2 Zeilen, 1 Duplikate
- `334f5f679802315eeec71399149b51c3` (aggregate, Optimal dose and type of exercise to improve depressive symptoms in ol): 2 Zeilen, 1 Duplikate
- `b5e492009e4ca350f512d5144fe8bf92` (rct, Impact of exercise type, duration, and intensity on depressive symptom): 2 Zeilen, 1 Duplikate
- `3790c91f96877eb6e260b4d7e0c7e7ee` (cohort, Bidirectional association between cognitive function and depressive sy): 2 Zeilen, 1 Duplikate
- `1faf4b78f05cd156029ee647c2e14c51` (cross_sectional, The Effect of Physical Exercise on Depression in College Students: The): 2 Zeilen, 1 Duplikate
- `5cbf039f22f1bfe9f5902cf3f626852f` (aggregate, Aerobic exercise for depression symptoms in adolescents: a systematic): 2 Zeilen, 1 Duplikate
- `cfc6567ca3cb6eec8c47a64a1674a849` (aggregate, The Effect of Exercise on Depressive Symptoms in Adolescents: A System): 2 Zeilen, 1 Duplikate

Volle Zitate und IDs: `data/golden_effects/duplikate.json`.
