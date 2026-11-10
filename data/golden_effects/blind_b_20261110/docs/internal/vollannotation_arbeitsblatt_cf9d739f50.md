# Arbeitsblatt: Impaired sleep, depressive symptoms, and pain as determinants of physi

- Dokument-ID: `cf9d739f5090aeda8006074fce2f0b44`
- Volltext: `fulltext/cf9d739f5090aeda8006074fce2f0b44.txt` (61,869 Zeichen)
- Jahr: 2025
- Schicht: rct | Design: parallel_rct
- Design laut Dokument: randomized clinical trial

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
| Table 3 | 105 | Self-reported average duration of sleep during the night was categorized as < 6 h, ≥ 6–<7 h, ≥ 7–<8 h, ≥ 8–<9 h, and ≥ 9 h. The recommended sleep duration for older adults is ≥ 7–<8 h per night [ 36 ]. Sleep quality was… |
| Table 1 | 133 | A total of 1100 participants (87.4%) had PA data available at both baseline and 2-year visits (Fig. 1 ). At baseline, there were no significant differences between intervention and control groups. Overall, compared with… |
| Table 4 | 133 | A total of 1100 participants (87.4%) had PA data available at both baseline and 2-year visits (Fig. 1 ). At baseline, there were no significant differences between intervention and control groups. Overall, compared with… |
| Table 5 | 133 | A total of 1100 participants (87.4%) had PA data available at both baseline and 2-year visits (Fig. 1 ). At baseline, there were no significant differences between intervention and control groups. Overall, compared with… |
| Table 1 | 135 | Table 1 Baseline characteristics of the FINGER participants with available physical activity data at both baseline and the 2-year follow-up |
| Table 2 | 143 | Participants sleeping either < 6 h or ≥ 9 h were significantly less likely to be adherent compared with participants sleeping ≥ 7–<8 h, (OR 0.46, 95% CI 0.21–0.99) and (OR 0.38, 95% CI 0.20–0.74), respectively (Model 1,… |
| Table 2 | 145 | Table 2 The impact of baseline sleep duration and quality, and pain on exercise adherence in the intervention group |
| Table 3 | 151 | As expected, participants who were physically active at baseline were more likely to remain physically active also after 2 years, regardless of the randomization group (OR 7.60, 95% CI 5.51–10.48). PA increased signific… |
| Table 3 | 153 | Table 3 Intervention effect on PA after 2 years, stratified by baseline sleep duration and quality, depressive symptoms, and pain |
| Table 4 | 159 | Compared with a sleep duration of ≥ 7–<8 h sleep, participants who slept < 6 h at baseline were less likely to be physically active at two years, (OR 0.36, 95% CI 0.18–0.72) (Model 1, Table 4 ). Results were consistent … |
| Table 4 | 161 | Table 4 Overall impact of baseline sleep duration and quality, depressive symptoms, and pain on physical activity after 2 years (intervention and control participants combined, including participants with physical activ… |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 29 | Adherence to the exercise intervention was less likely with sleep duration < 6 h or ≥ 9 h per night compared with 7–8 h. OR (95% CI) were 0.46 (0.21–0.99) and 0.38 (0.20–0.74), respectively. The intervention group was m… |
| 133 | A total of 1100 participants (87.4%) had PA data available at both baseline and 2-year visits (Fig. 1 ). At baseline, there were no significant differences between intervention and control groups. Overall, compared with… |
| 141 | Of the intervention group participants, 48% adhered to the exercise training program. Adherence varied by sleep duration. The lowest adherence rates (32% and 33%) were observed among participants with the longest (≥ 9 h… |
| 143 | Participants sleeping either < 6 h or ≥ 9 h were significantly less likely to be adherent compared with participants sleeping ≥ 7–<8 h, (OR 0.46, 95% CI 0.21–0.99) and (OR 0.38, 95% CI 0.20–0.74), respectively (Model 1,… |
| 151 | As expected, participants who were physically active at baseline were more likely to remain physically active also after 2 years, regardless of the randomization group (OR 7.60, 95% CI 5.51–10.48). PA increased signific… |
| 159 | Compared with a sleep duration of ≥ 7–<8 h sleep, participants who slept < 6 h at baseline were less likely to be physically active at two years, (OR 0.36, 95% CI 0.18–0.72) (Model 1, Table 4 ). Results were consistent … |

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
