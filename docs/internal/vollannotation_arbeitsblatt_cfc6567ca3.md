# Arbeitsblatt: The Effect of Exercise on Depressive Symptoms in Adolescents: A System

- Dokument-ID: `cfc6567ca3cb6eec8c47a64a1674a849`
- Volltext: `fulltext/cfc6567ca3cb6eec8c47a64a1674a849.txt` (46,378 Zeichen)
- Jahr: 2016
- Schicht: aggregate | Design: aggregate
- Design laut Dokument: meta-analysis

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
| Table 1 | 112 | detailed search strategy used for PubMed is shown in (Table 1). |
| Table 1 | 113 | Table 1: PubMed search strategy. |
| Table 2 | 254 | (BDI), which measured the severity of depressive symptoms in participants. The basic characteristics of the included studies are summarized in (Table 2). |
| Table 2 | 255 | Table 2: Basic characteristics of included studies. |

## Textstellen mit Effekt und Unsicherheit

| Zeile | Auszug |
|---|---|
| 296 | intervention effect (g = 1.09, 95% CI = 0.57–1.60, P < 0.01). |
| 297 | Traditional health-preserving exercises (g = 0.80, 95% CI = |
| 298 | 0.15–1.44, P < 0.01), anaerobic exercises (g = 0.78, 95% CI = |
| 299 | 0.63–1.38, P < 0.01) and aerobic exercises (g = 0.70, 95% CI = |
| 302 | cycling (g = 1.60, 95% CI = 1.23–2.19, P < 0.05) and yoga (g |
| 303 | = 1.26, 95% CI = 0.70–1.82, P < 0.01) significantly improved |
| 305 | (g = 0.16, 95% CI = -0.15–0.47, P < 0.01). The main pooled |
| 311 | duration of ≥90 minutes (g = 0.77, 95% CI = 0.41–1.13, P < |
| 312 | 0.01), exercising 3-4 times per week (g = 0.79, 95% CI = 0.38– |
| 314 | 0.90, 95% CI = 0.21–1.59, P < 0.01) and low-intensity exercise |
| 315 | interventions (g = 0.95, 95% CI = 0.39–1.51, P < 0.01). The |
| 195 | corrected indicator for the standardized mean difference (SMD). |

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
