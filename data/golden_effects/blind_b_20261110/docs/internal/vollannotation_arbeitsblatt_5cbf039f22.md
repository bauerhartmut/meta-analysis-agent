# Arbeitsblatt: Aerobic exercise for depression symptoms in adolescents: a systematic

- Dokument-ID: `5cbf039f22f1bfe9f5902cf3f626852f`
- Volltext: `fulltext/5cbf039f22f1bfe9f5902cf3f626852f.txt` (87,127 Zeichen)
- Jahr: 2026
- Schicht: aggregate | Design: aggregate
- Design laut Dokument: systematic review and dose-response meta-analysis

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
| Table 1 | 173 | The basic characteristics of the included studies are summarized in Table 1 . The 12 studies included a total of 723 adolescent participants, with sample sizes ranging from 22 to 151. The participants’ ages ranged from … |
| Table 1 | 175 | Table 1 Basic characteristics of the included studies |
| Table 2 | 205 | Table 2 shows the model fit after adjusting for age, gender, baseline depression, and total intervention duration. The moderator analysis revealed that the percentage of female participants had a significant negative mo… |
| Table 2 | 207 | Table 2 Moderator analysis |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 221 | The sensitivity analysis (Fig. 6 ) showed that after excluding high-risk studies (2 of the 12 studies), the re-estimated overall effect size was 0.29 (95% CI [0.21, 0.38]), while the main estimate remained 0.28 (95% CI … |
| 141 | Standardized mean difference (Standardized Mean Difference, SMD) was used as the effect size metric for continuous variables, and Hedges’ g was applied for small sample bias correction. These calculations were performed… |
| 239 | This study demonstrates a statistically significant improvement effect of aerobic exercise on depressive symptoms in adolescents. This is consistent with previous systematic reviews and meta-analyses, indicating that re… |

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
