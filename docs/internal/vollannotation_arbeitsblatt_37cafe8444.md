# Arbeitsblatt: A Cross-Sectional Study of Food Insecurity, Mediterranean Diet Adheren

- Dokument-ID: `37cafe8444a2d0edd125109341865251`
- Volltext: `fulltext/37cafe8444a2d0edd125109341865251.txt` (73,766 Zeichen)
- Jahr: 2026
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
| Table 1 | 113 | The sociodemographic, lifestyle, and cardiometabolic characteristics of participants with type 2 diabetes, stratified by combined food insecurity and Mediterranean diet adherence categories, are presented in Table 1 . A… |
| Table 2 | 221 | Boldface p -values indicate statistical significance at p < 0.05. Data are presented as mean ± standard deviation and median (in parentheses) for continuous variables and as numbers (percentages) for categorical variabl… |
| Table 2 | 247 | The grouping variable combining food insecurity and Mediterranean diet adherence (FI−/MDA↓, FI+/MDA↓, FI−/MDA↑, FI+/MDA↑) was created to compare the cumulative characteristics of participants according to their food sec… |
| Table 2 | 249 | Table 2 presents the adjusted odds ratios (AORs) from the primary multinomial logistic regression analysis examining associations between combined food insecurity and Mediterranean diet adherence (MDA) patterns and the … |
| Table 3 | 253 | Adjusted mean values of macronutrient intake according to serum TMAO concentration are presented in Table 3 . Here, participants are divided into two groups based on median serum TMAO concentration, and, after adjustmen… |
| Table 4 | 433 | Adjusted mean values of macronutrient intake according to serum L-carnitine concentration are shown in Table 4 . Participants are classified into two groups based on median serum L-carnitine concentration, and, after ad… |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 55 | Objective : This study aimed to investigate the combined associations of food insecurity and Mediterranean diet adherence with glycemic control and to determine whether gut-derived metabolites differ according to food i… |
| 249 | Table 2 presents the adjusted odds ratios (AORs) from the primary multinomial logistic regression analysis examining associations between combined food insecurity and Mediterranean diet adherence (MDA) patterns and the … |
| 623 | Emerging evidence indicates that, among adults with diabetes, food insecurity is associated with poorer glycemic control through multiple social, behavioral, and nutritional pathways [ 32 ]. In this context, the role of… |
| 629 | Serum TMAO originates from dietary trimethylamine and the metabolism of compounds such as carnitine, betaine, and choline, which are abundant in animal-based foods. The gut microbiota converts these substrates into trim… |
| 631 | Gut microbiota-derived metabolites, particularly trimethylamine N -oxide (TMAO), have been implicated in the development of metabolic and cardiovascular diseases. Elevated serum TMAO levels are linked to oxidative stres… |
| 633 | L-carnitine, the active form of dietary carnitine and a key precursor of TMAO, has drawn increasing attention for its dual role in cardiovascular health: while essential for fatty acid oxidation and cardiac energy metab… |
| 111 | The ANCOVAs were hypothesis-driven and focused on a predefined set of dietary variables selected a priori based on their biological relevance to gut-derived metabolites. Therefore, nominal p -values are reported. To fac… |
| 223 | Adjusted odds ratios (AORs) for combined food insecurity–Mediterranean diet adherence patterns across HbA1c tertiles from the primary multinomial logistic regression analysis among patients with T2DM. Reference outcome:… |
| 227 | HbA1c 6.62–8.22 vs. <6.62 AOR (95% CI) |
| 229 | HbA1c > 8.22 vs. <6.62 AOR (95% CI) |
| 615 | Adjusted mean (±standard error) values of serum TMAO and L-carnitine concentrations according to macrovascular complications and food insecurity status among patients with T2DM. ( A ) Serum TMAO concentrations according… |
| 617 | Adjusted mean (±standard error) values of serum TMAO and L-carnitine concentrations according to macrovascular complications and food insecurity status among patients with T2DM. ( A ) Serum TMAO concentrations according… |

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
