# Arbeitsblatt: Bidirectional association between cognitive function and depressive sy

- Dokument-ID: `3790c91f96877eb6e260b4d7e0c7e7ee`
- Volltext: `fulltext/3790c91f96877eb6e260b4d7e0c7e7ee.txt` (70,784 Zeichen)
- Jahr: 2026
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
| Table 1 | 325 | median age (interquartile range) of participants at baseline was 66 years. Table 1 presents the baseline character - |
| Table 1 | 330 | See Table 1 for details. |
| Table 2 | 345 | positively correlated (rs=[0.281, 0.447]; P < 0.001). See Table 2 and Figure 2 for details. |
| Table 3 | 361 | indicate good model fit. Detailed results are presented in Table 3. |
| Table 1 | 367 | Table 1. Basic characteristics of research subjects. |
| Table 2 | 402 | Table 2. Correlation matrix between variables in each variable. |
| Table 3 | 433 | Table 3. Correlation matrix between variables in each variable. |
| Table 4 | 454 | CI=[−0.002, 0]). Detailed results are presented in Table 4 and Fig 4. |
| Table 4 | 459 | Table 4. Statistical results of longitudinal mediation analysis. |
| Table 5 | 489 | tent with the main mediation findings. Detailed results are presented in Table 5. |
| Table 5 | 490 | Table 5. Standardized path coefficients and model fit indices for longitudinal mediated and cross-lagged models. |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 75 | toms through T2-PA (β = −0.002, 95% CI=[−0.004, −0.001]), with the mediation effect |
| 77 | through T2-PA was not significant (β = −0.001, 95% CI=[−0.002, 0]). |
| 449 | the indirect effect between variables was significant (β = −0.002, 95% CI=[−0.004, −0.001]). That is, PA mediated the effect |
| 487 | (β = −0.001, 95% CI=[−0.002, 0]), indicating that the sensitivity analysis did not support a reverse mediation pathway. The |
| 460 | Path parameters β 95%CI Mediation effect proportion |
| 484 | 95% CI=[−0.004, −0.001]), indicating that PA mediated the longitudinal association from earlier CF to later depressive |

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
