# Arbeitsblatt: Exploring the validity and internal consistency of the 12-point Medite

- Dokument-ID: `2675c25aabf33995fb6c2d3e72221923`
- Volltext: `fulltext/2675c25aabf33995fb6c2d3e72221923.txt` (55,267 Zeichen)
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
| Table 1 | 235 | Table 1 shows the sociodemographic and pregnancy-related characteristics of the study participants. About two-thirds of |
| Table 2 | 239 | Table 2 shows the results of the KMO test and Bartlett’s test of sphericity. The KMO measure (0.583) was greater than |
| Table 3 | 242 | Factor analysis results are shown in Table 3. After removing the alcohol consumption question due to its conceptual |
| Table 4 | 253 | The results of the Multiple Correspondence Analysis are shown in Table 4. The four dimensions accounted for 11.57% of |
| Table 5 | 257 | Table 5 shows the level of MD adherence according to the three tools. Weak adherence was concluded for 45.4% of the |
| Table 5 | 261 | using the FFQ and 19.2% using 24HR. The correlation of the 12-MEDAS scale with FFQ/24HR is also shown in Table 5. |
| Table 1 | 262 | Table 1. Sociodemographic and medical characteristics of study participants (n = 500). |
| Table 2 | 294 | Table 2. KMO and Bartlett’s test. |
| Table 6 | 306 | The agreement between each item of the 12-MEDAS and those of the FFQ and 24HR is shown in Table 6. For the FFQ |
| Table 3 | 314 | Table 3. Factor analysis of the 12-MEDAS scale items. |
| Table 4 | 359 | Table 4. Multiple correspondence analysis of the 12-MEDAS scale items. |
| Table 5 | 406 | Table 5. Correlation between 12-MEDAS adherence categories and FFQ/24HR. |
| Table 6 | 444 | Table 6. Agreement Kappa coefficient between the 12-MEDAS and FFQ/24HR items. |

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
