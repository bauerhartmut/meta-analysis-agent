# Arbeitsblatt: The effect of exercise on depressive symptoms in multiple sclerosis ba

- Dokument-ID: `fb484d488b45d21bbdf407cba4b074d5`
- Volltext: `fulltext/fb484d488b45d21bbdf407cba4b074d5.txt` (9,659 Zeichen)
- Jahr: 2015
- Schicht: rct | Design: parallel_rct
- Design laut Dokument: meta-analysis of randomized controlled trials

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

Keine Tabellen-Erwähnung gefunden; Tabellen am Layout prüfen.

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 39 | Background and purpose: The purpose of this study was to perform a systematic review of the literature on the effects of exercise on depressive symptoms in patients with multiple sclerosis (MS), as well as to apply meta… |
| 179 | N2 - Background and purpose: The purpose of this study was to perform a systematic review of the literature on the effects of exercise on depressive symptoms in patients with multiple sclerosis (MS), as well as to apply… |
| 181 | AB - Background and purpose: The purpose of this study was to perform a systematic review of the literature on the effects of exercise on depressive symptoms in patients with multiple sclerosis (MS), as well as to apply… |
| 107 | Standardized Mean Difference Psychology 50% |
| 109 | Standardized Mean Difference Psychology 50% |
| 111 | Standardized Mean Difference |

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
