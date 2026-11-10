# Arbeitsblatt: Bidirectional association between ADL disability and depressive sympto

- Dokument-ID: `17c7628ed0e8f01d4ec063e2b730dc36`
- Volltext: `fulltext/17c7628ed0e8f01d4ec063e2b730dc36.txt` (61,790 Zeichen)
- Jahr: 2025
- Schicht: cohort | Design: observational
- Design laut Dokument: longitudinal cohort

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
| Table 1 | 115 | In the analysis of the impact of ADL on the risk of DS, a total of 8,994 participants were included. During the longitudinal follow-up from 2015 to 2018, 2,292 participants developed probable DS, yielding a cumulative i… |
| Table 1 | 117 | Table 1 Baseline characteristics of participants by risk of DS. |
| Table 2 | 121 | In the analysis of the impact of DS on the risk of ADL disability, a total of 9,673 participants were included. During the longitudinal follow-up from 2015 to 2018, 2,292 participants developed probable ADL disability, … |
| Table 2 | 123 | Table 2 Baseline characteristics of participants by risk of ADL disability. |
| Table 3 | 131 | Table 3 Cox proportional hazards regression model results for DS and ADL disability incidence. |
| Table 3 | 151 | To further validate our findings, we conducted a sensitivity analysis based on Model 4. Participants with baseline values for ADL disability and depressive symptoms DS below the 15th percentile were excluded. The result… |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 23 | This study investigates the bidirectional relationship between Activities of Daily Living (ADL) disability and depressive symptoms (DS) among middle-aged and older adults in China, utilizing data from the China Health a… |
| 129 | We employed Cox proportional hazards regression models to examine the impact of ADL disability on the risk of DS. In the unadjusted model, the ADL disability score in 2015 was a significant predictor of DS, with each on… |
| 193 | Hazard ratios |

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
