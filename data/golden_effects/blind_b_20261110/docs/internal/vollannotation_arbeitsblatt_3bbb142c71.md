# Arbeitsblatt: Effects of Acute Caffeine Ingestion on Reaction Time in Habitual and L

- Dokument-ID: `3bbb142c717a970694bed1d393736b06`
- Volltext: `fulltext/3bbb142c717a970694bed1d393736b06.txt` (40,445 Zeichen)
- Jahr: 2026
- Schicht: crossover | Design: crossover_rct
- Design laut Dokument: Randomised controlled trial (crossover)

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
| Table 1 | 306 | Table 1 shows descriptive values for the DVA parameters |
| Table 1 | 366 | Table 1 Descr iptive values (mean ± s tandard deviation) for the dynamic visual acuity parameters assessed at the different measurement moments |

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
