# Arbeitsblatt: The effects of an 8-week Taekwondo exercise intervention on inhibitory

- Dokument-ID: `ca2c52d13aaec47ebbeccdedb3ee1d8e`
- Volltext: `fulltext/ca2c52d13aaec47ebbeccdedb3ee1d8e.txt` (79,256 Zeichen)
- Jahr: 2025
- Schicht: crossover | Design: crossover_rct
- Design laut Dokument: Mixed experimental design (repeated measures ANOVA)

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
| Table 1 | 265 | Comparison of Basic Information of University Students with Depressive Symptoms. Before the experiment, a difference test was conducted on the age, height, weight, BMI, PARS-3, and BDI-II scores of the two groups of par… |
| Table 1 | 267 | Table 1 Baseline sample characteristics of University students with depressive symptoms |
| Table 2 | 273 | Table 2 Comparison of BDI-II scores between the Exercise Group and Control Group before and after 8 weeks of intervention |
| Table 2 | 277 | The 8-week Taekwondo exercise intervention significantly improved depressive symptoms in the exercise group (with a significant decrease in BDI-II scores), while depressive symptoms in the control group worsened, althou… |
| Table 3 | 285 | In the behavioral results of the response inhibition task (Go/Nogo), repeated measures ANOVA showed(Table 3 ) that there were no significant differences between groups under both Go and Nogo conditions in the pre-test p… |
| Table 3 | 289 | Table 3 Comparison of the Effect of 8 weeks of Taekwondo Training on Response Inhibition in University students with depressive symptoms |
| Table 4 | 297 | In the response inhibition task (Go/Nogo), the results of the repeated measures ANOVA for N2 amplitude showed significant main effects for time (Table 4 ; Fig. 6 ), F(1,39) = 4.217, P < 0.047, ƞp 2 = 0.098; for conditio… |
| Table 4 | 305 | Table 4 N2 ERP amplitudes (µV) across condition and time |
| Table 5 | 309 | The results of the repeated measures ANOVA for N2 latency indicated significant main effects for condition (Table 5 ; Fig. 6 ), F(1,39) = 32.957, P < 0.001, ηp 2 = 0.458; and for electrode site, F(3,117) = 15.914, P < 0… |
| Table 5 | 313 | Table 5 N2 ERP latency (ms) across condition and time |

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
