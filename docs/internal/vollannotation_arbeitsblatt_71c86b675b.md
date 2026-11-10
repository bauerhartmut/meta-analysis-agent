# Arbeitsblatt: Adherence to the Mediterranean diet to prevent or delay hepatic steato

- Dokument-ID: `71c86b675bdc30a57ac17ac779abdce5`
- Volltext: `fulltext/71c86b675bdc30a57ac17ac779abdce5.txt` (69,105 Zeichen)
- Jahr: 2025
- Schicht: rct | Design: parallel_rct
- Design laut Dokument: Longitudinal analysis within a randomized controlled trial (

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
| Table 1 | 353 | fat diet recommendation group are shown in Table 1. There were |
| Table 2 | 360 | Table 2 shows the signiﬁcant changes observed in these values |
| Table 3 | 371 | Table 3 shows the relationship between the study variables |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 387 | 95% CI: −0.198, −0.134; Model 3: β = − 0.172; 95% CI: −0.202, |
| 389 | (β = − 0.001; 95% CI: −0.0013, 0.0006). By contrast, values were |
| 391 | (β = 0.020; 95% CI: 0.017, 0.022) and in those with a higher daily |
| 392 | calorie intake (β = 0.0003; 95% CI: 0.0001, 0.0004). |
| 396 | with EVOO, the HSI was 0.620 units ( β = −0.620, 95%CI: −1.077, |
| 399 | diﬀerence was 0.881 units ( β = −0.881, 95% CI: −1.366, −0.406). |
| 450 | (standardized mean diﬀerence: −1.06, 95% CI: −1.95 to −0.17; p |
| 107 | MedDiet (β = −/zero.tnum./zero.tnum/seven.tnum/five.tnum; /nine.tnum/five.tnum% CI: −/zero.tnum./one.tnum/two.tnum/eight.tnum, −/zero.tnum./zero.tnum/two.tnum/one.tnum). |

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
