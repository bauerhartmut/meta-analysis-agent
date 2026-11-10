# Arbeitsblatt: Accelerometer-Assessed Physical Activity and Cognitive Performance amo

- Dokument-ID: `7ca468285bd24135c1a9bf48f6f5f202`
- Volltext: `fulltext/7ca468285bd24135c1a9bf48f6f5f202.txt` (58,006 Zeichen)
- Jahr: 2022
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
| Table 1 | 117 | Table 1 shows the descriptive characteristics of the sample. It indicates that a over half of the participants were women (58.2%). Age ranged between 50 and 99 (Mean = 70.6, S.D = 8.9). About 71.5% had secondary educati… |
| Table 2 | 161 | Table 2 displays the outcomes of the Pearson correlations between the dependent variable (cognitive performance), the independent variable (intensity gradient), the mediators (depressive symptoms and contact frequency),… |
| Table 3 | 223 | Table 3 shows the results of the multiple mediation model (PROCESS model 4). The results indicated a significant total direct effect (path c; without mediators) of the intensity gradient on cognitive performance (B = 0.… |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 49 | Background: Cognitive decline is a major public health concern worldwide and it is vital to identify and better understand effective population-based means to improve cognitive performance in old age. The current study … |
| 223 | Table 3 shows the results of the multiple mediation model (PROCESS model 4). The results indicated a significant total direct effect (path c; without mediators) of the intensity gradient on cognitive performance (B = 0.… |

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
