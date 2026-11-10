# Arbeitsblatt: A Multicenter, Placebo-controlled Trial of Melatonin for Sleep Disturb

- Dokument-ID: `bb9218735fec8fc7f3b6aebbff430aba`
- Volltext: `fulltext/bb9218735fec8fc7f3b6aebbff430aba.txt` (71,085 Zeichen)
- Jahr: 2003
- Schicht: rct | Design: parallel_rct
- Design laut Dokument: randomized, placebo-controlled study

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
| Table 1 | 105 | This was a multicenter, randomized, placebo-controlled study of 2 melatonin formulations (2.5 mg sustained-release (SR) and 10 mg immediate release). Subjects were randomly assigned (blocked by study site) in a double-b… |
| Table 2 | 105 | This was a multicenter, randomized, placebo-controlled study of 2 melatonin formulations (2.5 mg sustained-release (SR) and 10 mg immediate release). Subjects were randomly assigned (blocked by study site) in a double-b… |
| Table 3 | 209 | Wrist actigraphy is generally accepted as the most practical method for obtaining objective, quantitative, sleep-wake cycle data in persons with dementia. 48 , 50 – 53 The actigraphs used in this study were Actiwatch AW… |
| Table 2 | 227 | Caregivers were asked to complete a Daily Sleep Diary form to document bedtimes, lights-out time, time of melatonin administration, and the rare times that the actigraph was left off the subject. The sleep diary also in… |
| Table 3 | 233 | A computerized automated scoring technique was developed at ADCS by one of the authors (AG) to translate the vast amount of wrist-movement data into sleep values. The output of the automated algorithm was identical to t… |
| Table 3 | 249 | We screened 244 potential subjects and enrolled 157. Randomized assignment to the 3 treatment arms was fairly well balanced: PLA: n=52, ML 2.5SR: n=54, and ML 10: n=51. The average age of the subjects was 77.4 ± 8.9 yea… |
| Table 2 | 251 | None of the potential covariates were found to be out of balance at baseline (ie, all P >.30); therefore, no variable examined was included in the final analyses. Also, the groups did not differ on any baseline variable… |
| Table 4 | 255 | Table 4 provides descriptive statistics for the baseline, treatment period, and changes for the primary and secondary sleep variables. In none of the statistical analyses of the primary sleep measures (baseline vs treat… |
| Table 5 | 391 | Table 5 presents the demographic data and baseline and change scores for the secondary measures. Change scores in Mini-Mental State Examination, Alzheimer’s Disease Assessment Scale - cognitive sub-scale, activities of … |
| Table 6 | 483 | There were no differences in the mean number, severity, seriousness, or relatedness ratings of spontaneously reported AEs across the 3 groups (ie, the proportions of each treatment group reporting any AE were equal). Ta… |
| Table 4 | 527 | We have reported the results of the first multicenter clinical trial of a therapeutic agent for sleep disturbance in AD. No significant treatment effects were seen in the actigraph data, although 2 positive trends were … |
| Table 5 | 531 | Although more AEs were reported in the ML 2.5SR group than in the ML 10 group ( Table 5 ), there was no difference between groups in the likelihood of AEs being related to study medication. No AEs were definitely relate… |
| Table 4 | 541 | We do not know whether elevated daytime melatonin levels affected the outcome of this trial. The subject in the ML 10 group with the highest residual daytime level (680 ng/dL at 12:00) gained an average of 49 minutes of… |
| Table 6 | 541 | We do not know whether elevated daytime melatonin levels affected the outcome of this trial. The subject in the ML 10 group with the highest residual daytime level (680 ng/dL at 12:00) gained an average of 49 minutes of… |

## Textstellen mit Effekt und Unsicherheit

Keine Stelle mit den Mustern gefunden; manuell prüfen.

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
