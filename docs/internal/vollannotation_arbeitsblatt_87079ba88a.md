# Arbeitsblatt: Withdrawal Symptoms and Executive Functions After 24-Hour Caffeine Abs

- Dokument-ID: `87079ba88ae1f64f00c5fe32725248a6`
- Volltext: `fulltext/87079ba88ae1f64f00c5fe32725248a6.txt` (38,131 Zeichen)
- Jahr: 2026
- Schicht: crossover | Design: crossover_rct
- Design laut Dokument: within-subjects

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
| Table 1 | 267 | Table 1 shows the duration of coffee consumption, |
| Table 1 | 275 | Table 1 The participants’ information regarding coffee and |
| Table 2 | 298 | some participants was unchanged (Table 2). |
| Table 3 | 309 | not change in some participants (Table 3). |
| Table 2 | 310 | Table 2 The scores (Mean±S.D.) of caffeine withdrawal symptoms and the proportion (%) of participants with increased |
| Table 3 | 372 | Table 3 The results (Mean±S.D.) of executive function assessments and the proportion (%) of participants with increased |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 289 | factor 1 (p-value<0.01, Z=-3.72), 2 (p-value<0.01, 95% CI |

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
