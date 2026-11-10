# Arbeitsblatt: Optimal dose and type of exercise to improve depressive symptoms in ol

- Dokument-ID: `334f5f679802315eeec71399149b51c3`
- Volltext: `fulltext/334f5f679802315eeec71399149b51c3.txt` (79,745 Zeichen)
- Jahr: 2024
- Schicht: aggregate | Design: aggregate
- Design laut Dokument: Network Meta-Analysis

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
| Table 8 | 121 | The MBNMAdose package based on R statistical environment (V.4.2.2, www.r-project.org ) was used to perform random-effects Bayesian Model-Based Network Meta-Analysis (MBNMA)[ 36 ] to summarize the dose–response associati… |
| Table 9 | 121 | The MBNMAdose package based on R statistical environment (V.4.2.2, www.r-project.org ) was used to perform random-effects Bayesian Model-Based Network Meta-Analysis (MBNMA)[ 36 ] to summarize the dose–response associati… |
| Table 1 | 139 | Figure 2 showed the direct comparison and sample size distribution between the exercise types. Compared with the CON, 6 (85.7%) of 7 exercise types significantly relieved symptoms of depression, and the SMDs (95% CrI) r… |
| Table 1 | 149 | Table 1 League table of depression symptoms |
| Table 2 | 153 | Heterogeneity results showed moderate to high (I 2 = 70.8%, τ 2 = 0.1962, p < 0.0001). The results of network meta-regression showed that participant's age (Beta: 0.36, 95% Crl (0.05; 0.68)) and exercise dose (Beta: -0.… |
| Table 2 | 155 | Table 2 Network Meta-Regression. Below we present the results from the changes in heterogeneity in each meta-regression model |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 117 | A network plot was drawn using Stata (release 14, Stata- Corp LLC, TX, USA) to present the geometry of the network of comparisons across trials to ensure the network meta-analyses were feasible. Based on the R statistic… |

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
