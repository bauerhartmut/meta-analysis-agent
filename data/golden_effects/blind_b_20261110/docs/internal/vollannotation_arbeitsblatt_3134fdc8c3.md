# Arbeitsblatt: The risk associated with ultra-processed food intake on depressive sym

- Dokument-ID: `3134fdc8c38f475075a70ca32dc4a3d9`
- Volltext: `fulltext/3134fdc8c38f475075a70ca32dc4a3d9.txt` (85,910 Zeichen)
- Jahr: 2025
- Schicht: cohort | Design: observational
- Design laut Dokument: Target trial emulation (longitudinal cohort)

**Für A und B identisch.** Getrennt ausfüllen und während der
Annotation nicht austauschen. Nur Volltext, Anleitung und Schema
verwenden; keine DB-, Modell- oder Fremdausgaben.

## Vorgehen
1. Volltext vollständig lesen, nicht nur Abstract.
2. Jede Stelle mit quantifiziertem Effekt und Unsicherheit markieren.
3. Je Kombination aus Outcome, Vergleich, Zeitpunkt, Adjustierung und
   Population eine Zeile.
4. Quote exakt kopieren und `quote_start`/`quote_end` im Volltext setzen.
5. Dokument abschließen: Zeilen oder `no_effect_reason`.

## Tabellenfundstellen

| Tabelle | Zeile | Auszug |
|---|---|---|
| Table 1 | 109 | A target trial emulation was applied based on the ASPREE longitudinal data. The study protocol for a hypothetical randomised control trial was framed by rigorously defining eligibility criteria, assignment procedures (i… |
| Table 1 | 111 | Table 1 Summary of a target trial protocol and its emulations to estimate the effect of ultra-processed food on depressive symptoms in older adults using ASPREE data |
| Table 2 | 177 | At the baseline of the trial, the mean (standard deviation) age of participants was 74.9 (4.07) years and 53.7% were females. In our study, at time zero, most participants ( n = 8490, 90.1%) had good social support, and… |
| Table 2 | 179 | Table 2 Baseline characteristics of ASPREE study participants included in the target trial emulation stratified by intervention strategies before and after IPTW |
| Table 2 | 183 | The time zero socio-cultural, body composition characteristics, comorbidities, and medication intake of participants in the intervention and control arm were similar. However, as indicated in Table 2 , participants in t… |
| Table 3 | 193 | As shown in Table 3 , higher UPF consumption was associated with an increased risk of depressive symptoms among older adults; the associated risk of depressive symptoms among older adults who consumed high UPF (4 or mor… |
| Table 3 | 195 | Table 3 Model-based risk ratios estimating the risk of depressive symptoms under UPF intervention strategies of the longitudinal cohort study in Australian older adults |
| Table 4 | 219 | Analysis using serving quartiles of UPF indicated that the between-group mean difference of MCS in the intervention group (i.e. quartile 4 of UPF serving) decreased by 0.57 units compared to the control group ( β : − 0.… |
| Table 4 | 221 | Table 4 Model-based estimate showing the effect of UPF on mental health quality of life of Australian older adults ( n = 11,201) |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 199 | The E-value estimate for the main comparison was 1.43, in which unmeasured confounders must be correlated with both consumption of UPF and risk of depressive symptoms by a risk ratio of at least 1.43 to fully explain aw… |
| 29 | A total of 11,192 participants (3415 intervention and 7777 control) were eligible for the emulation. High UPF consumption at time zero was associated with an increased risk of depressive symptoms at follow-ups (RR: 1.10… |
| 155 | To maintain the exchangeability assumption (i.e. participants in the intervention and control group have the same potential outcomes on average), the distribution of confounders across the trial arms was compared after … |
| 157 | For the primary outcome, inverse probability weights were included in the marginal structural model (MSM) by employing the generalised estimated equations with a log link, CES-D 10 ≥ 8 as the dichotomised outcome, and i… |
| 159 | For the secondary outcome, MSM was fitted using generalised estimated equations assuming a Gaussian distribution with an identity link function and repeated (follow-up) MCS SF-12 scores as a continuous outcome variable … |
| 183 | The time zero socio-cultural, body composition characteristics, comorbidities, and medication intake of participants in the intervention and control arm were similar. However, as indicated in Table 2 , participants in t… |
| 187 | Absolute standardised mean difference (SMD) for comparisons of baseline characteristics before and after IPTW |
| 193 | As shown in Table 3 , higher UPF consumption was associated with an increased risk of depressive symptoms among older adults; the associated risk of depressive symptoms among older adults who consumed high UPF (4 or mor… |
| 195 | Table 3 Model-based risk ratios estimating the risk of depressive symptoms under UPF intervention strategies of the longitudinal cohort study in Australian older adults |
| 203 | We performed sub-group analyses using sex-specific UPF quartiles of serving and portion size. The associated risk of depressive symptoms among older adults in the fourth UPF serving quartile was increased by 10% as comp… |
| 211 | Replicating the analyses confined to the ASPREE trial period (time zero in 2012 to 2017) indicated that high consumption of UPF adversely impacted the risk of depressive symptoms, similar to the main analysis (RR: 1.12;… |
| 217 | The between-group mean difference in MCS was significant, and there was a 0.40-unit decrease in mean MCS in the intervention group (high UPF consumption) compared to the control group (low UPF consumption) ( β : − 0.40;… |
| 219 | Analysis using serving quartiles of UPF indicated that the between-group mean difference of MCS in the intervention group (i.e. quartile 4 of UPF serving) decreased by 0.57 units compared to the control group ( β : − 0.… |
| 285 | Standardised mean difference |

Die Auszüge sind **Fundstellen, keine Annotation**. Werte nicht
übernehmen, ohne sie am Volltext zu prüfen.

## Pflichtfelder je Effektzeile

| Feld | Pflicht |
|---|---|
| `effect_id` | ja (Schema) |
| `outcome_verbatim` | ja (Schema) |
| `outcome_normalized` | ja (Schema) |
| `comparison_verbatim` | ja (Schema) |
| `effect_type` | ja (Schema) |
| `effect` | ja (Schema) |
| `ci_low` | ja (Schema) |
| `ci_high` | ja (Schema) |
| `quote` | ja (Schema) |
| `quote_start` | ja (Schema) |
| `quote_end` | ja (Schema) |
| `design_verbatim` | ja (Schema) |
| `certainty` | ja (Schema) |
| `is_primary` | ja (Schema) |

Zusätzlich ausfüllen, wenn berichtet: `se`, `ci_level`, `p_value`, `n`,
`adjusted`, `time_point`, `population`, `section`, `page`,
`source_table`, `notes`.

## Dokument-Check

Pflichtfelder Dokument: `document_id`, `path`, `title`, `design_verbatim`, `design_category`, `stratum`, `has_text_layer`, `effects`, `no_effect_reason`.

- [ ] Jede Zeile hat `quote` exakt und `quote_start`/`quote_end` passend.
- [ ] Kein Effekt umgerechnet, keine Zahl gerundet.
- [ ] Entweder mindestens eine Zeile oder `no_effect_reason`.
- [ ] Grenzfälle nach Anleitung geprüft: 5.2 (Ratio), 5.6 (Median/IQR),
      5.8 (Uebersichtsarbeit), 5.11 (Spannweite über Zeitpunkte).
