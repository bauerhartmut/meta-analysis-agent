# Arbeitsblatt: Impact of exercise type, duration, and intensity on depressive symptom

- Dokument-ID: `b5e492009e4ca350f512d5144fe8bf92`
- Volltext: `fulltext/b5e492009e4ca350f512d5144fe8bf92.txt` (48,470 Zeichen)
- Jahr: 2024
- Schicht: rct | Design: parallel_rct
- Design laut Dokument: randomized controlled trials

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
| Table 1 | 272 | Table 1. The study quality and risk assessment are shown in |
| Table 1 | 391 | TABLE 1 Study characteristics. |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 34 | physical exercise [SMD = −0.25, 95% CI ( −0.47, −0.03)], high-intensity physical |
| 35 | exercise [SMD = −0.94, 95% CI (−1.37, −0.51)], resistance exercise [SMD = −0.70, |
| 36 | 95% CI (−1.20, −0.20)], and group exercise [SMD = −0.97, 95% CI (−1.89, −0.05)], |
| 37 | and the exercise intervention time was 3 months [SMD = −0.81, 95% CI ( −1.38, |
| 38 | −0.23)] or 6 months [SMD = −0.93, 95% CI (−1.46, −0.41)] were more effective in |
| 281 | [SMD = −0.82, 95% CI (−1.19, −0.45)], as shown in Figure 2. |
| 290 | Both the three-month [SMD = −0.81, 95% CI (−1.38, −0.23)] and |
| 291 | six-month [SMD = −0.93, 95% CI (−1.46, −0.41)] exercise intervention |
| 297 | [SMD = −0.25, 95% CI ( −0.47, −0.03)] and high physical exercise |
| 298 | intensity [SMD = −0.94, 95% CI (−1.37, −0.51)] had a better effect |
| 305 | The results showed that resistance exercise [SMD = −0.70, 95% |
| 306 | CI (−1.20, −0.20)] and group exercise [SMD = −0.97, 95% CI (−1.89, |
| 24 | analysis using a 95% confidence interval (95% CI) and the standardized mean |
| 33 | 95% CI ( −1.19, −0.45)]. The subgroup analysis showed that moderate-intensity |
| 228 | were continuous variables, the standardized mean difference (SMD) |
| 229 | and 95% confidence intervals (95%CI) were used as effect sizes for the |

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
