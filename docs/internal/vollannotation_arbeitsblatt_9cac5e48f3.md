# Arbeitsblatt: Protocol for Objective Measurement of Infants’ Physical Activity using

- Dokument-ID: `9cac5e48f3873753223db0c3b5f2b501`
- Volltext: `fulltext/9cac5e48f3873753223db0c3b5f2b501.txt` (44,012 Zeichen)
- Jahr: 2018
- Schicht: negative_control | Design: unknown
- Design laut Dokument: nicht berichtet

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
| Table 1 | 79 | The sample description regarding the characteristics of the infants and mothers is presented in Table 1 . The sample was composed of 90 infants, with a mean (SD) age of 12.9 (1.70) months. Furthermore, the sample presen… |
| Table 1 | 81 | TABLE 1 Socioeconomic characteristics and mean acceleration of the sample (Pelotas, RS, Brazil (2016)). Open multimedia modal |
| Table 1 | 83 | TABLE 1 Socioeconomic characteristics and mean acceleration of the sample (Pelotas, RS, Brazil (2016)). |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 45 | The mean (SD) age was 12.9 (1.70) months; the mean acceleration varied between 25.8 m g (95% confidence interval (CI), 14.3–52.7) and 27.3 m g (95% CI, 17.9–44.5) using the wrist placement, and between 24.9 m g (95% CI,… |
| 79 | The sample description regarding the characteristics of the infants and mothers is presented in Table 1 . The sample was composed of 90 infants, with a mean (SD) age of 12.9 (1.70) months. Furthermore, the sample presen… |
| 89 | Figures 2 A and B present the ICC comparing the mean acceleration of 1 to 5 d of measurement and the mean acceleration of 6 measurement days, stratified by walking status, with the accelerometer placed on the wrist and … |
| 91 | FIGURE 2 Open multimedia modal A, ICC and respective 95% CI comparing the mean acceleration of 1 to 5 measurement days and the mean acceleration of 6 measurement days, stratified by walking status with the accelerometer… |
| 93 | A, ICC and respective 95% CI comparing the mean acceleration of 1 to 5 measurement days and the mean acceleration of 6 measurement days, stratified by walking status with the accelerometer placed on the wrist. B, ICC an… |
| 95 | In the group with the ankle placement of the device ( Fig. 2 B), there was greater variability among the results than that found with the wrist analyses. Among infants capable of walking, the threshold of 0.8 was reache… |
| 105 | Furthermore, Figure 4 shows the Bland–Altman plot comparing wrist and ankle placement regarding the 6-d mean acceleration, restricted for infants who used the device in both placements simultaneously, stratified by walk… |

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
