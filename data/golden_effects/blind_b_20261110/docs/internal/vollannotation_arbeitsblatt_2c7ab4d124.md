# Arbeitsblatt: Prevalence of depressive symptoms and its associated factors in older

- Dokument-ID: `2c7ab4d1244754e3966780f4bccbfa8c`
- Volltext: `fulltext/2c7ab4d1244754e3966780f4bccbfa8c.txt` (39,970 Zeichen)
- Jahr: 2017
- Schicht: cross_sectional | Design: observational
- Design laut Dokument: cross-sectional

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
| Table 1 | 110 | described in Table 1. |
| Table 2 | 163 | (21.1%) and severe depression (11.8%) respectively. Table 2 shows the socio -demographic |
| Table 3 | 174 | Table 3 reports the factors associated with depression on univariate and multivariate analyses. |
| Table 3 | 186 | In multivariate analysis (Table 3), those participants who were illiterate were twice as likely to |
| Table 1 | 539 | Table 1: Socio-demographic information of two study VDCs in the Kathmandu district |
| Table 2 | 549 | Table 2: Demographic characteristics of participants |
| Table 3 | 571 | Table 3: Logistic regression analysis of factors associated with depression |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 19 | = 2.01, 95% CI: 1.08–3.75), physical immobility (aOR = 5.59, 95% CI: 1.75–17.93), the |
| 20 | presence of physical health problems (aOR = 1.97, 95% CI: 1.03 –3.77), not having any |
| 21 | time spent with family members (aOR = 3.55, 95% CI: 1.29 –9.76) and not being |
| 22 | considered in family decision making (aOR = 4. 02, 95% CI: 2.01 –8.04) were |
| 175 | In univariate analysis, participants in the age group 60-74 years (OR = 1.93, p = 0.016), who |
| 176 | were female (OR = 2.06, p = 0.003), illiterate (OR=3.13, p < 0.001) or did not have the status |
| 177 | of head of the household (OR = 2.31, p = 0.005) were more likely to suffer from depression. |
| 179 | home (OR=5.27, p =0.002) and who had physical health problems (OR=2.0, p = 0.012) were |
| 181 | health problems. Conversely, participants who received physical support ( OR = 0.37, p = |
| 182 | 0.012), financial support (OR = 0.48, p = 0.038), who felt respected in the family (OR = 0.05, |
| 183 | p < 0.001), were considered in family decisions (OR = 0.12, p < 0.001), spent time with family |
| 184 | members (OR = 0.11, p < 0.001) and were not mistreated ( OR = 0.13, p = 0.001) were less |
| 187 | be depressed compared to those who were literate (adjusted OR (aOR) = 2.01, 95% CI: 1.08- |
| 189 | five times more likely to be depressed (aOR = 5.59, 95% CI: 1.75-17.93) than participants who |
| 190 | were able to leave home. Likewise, the presence of physical health problems (aOR = 1.97, 95% |
| 191 | CI: 1.03–3.8), lack of time spent with family members (aOR = 3.55, 95% 1.29-9.76), and lack |
| 192 | of consideration in family decisions making (aOR = 4.02, 95% CI 2.01-8.04) were associated |
| 578 | OR 95% CI aOR 95% CI |
| 605 | *Signifies statistical significance (p ≤0.05), aOR = adjusted Odds Ratio |

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
