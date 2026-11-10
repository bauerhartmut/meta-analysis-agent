# Arbeitsblatt: Mediterranean diet in preeclampsia prevention: mechanisms of action an

- Dokument-ID: `7111ea978757a185d44ea9de90b453c3`
- Volltext: `fulltext/7111ea978757a185d44ea9de90b453c3.txt` (99,296 Zeichen)
- Jahr: 2025
- Schicht: cohort | Design: observational
- Design laut Dokument: Prospective multicenter cohort

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
| 217 | preeclampsia in a dose-dependent manner (relative risk, 0.82; 95% CI, |
| 225 | preeclampsia by more than 60% (odds ratio, 0.38; 95% CI, 0.20 to 0.74) |
| 227 | in preventing preterm preeclampsia (relative risk, 0.62; 95% CI, 0.45 |
| 234 | (relative risk, 0.49; 95% CI, 0.39 to 0.61), with efficacy observed |
| 248 | shown to reduce the risk of preeclampsia (odds ratio, 0.59; 95% CI, 0.37 |
| 466 | quartile (RR 0.58; 95% CI, 0.42, 0.81). This study provided valuable |
| 477 | high adherence (OR 3.8; 95% CI 1.3–11.4, p = 0.019) ( 43). |
| 491 | vs. lowest quartile: 0.31 [95% CI: 0.11, 0.87], P-trend = 0.03), |
| 501 | lowest tertile aOR 0.78, 95% CI 0.64–0.96). Notably, the protective effect |
| 510 | preeclampsia (aOR 0.72, 95% CI 0.55–0.93). A dose–response |
| 534 | reduction in the prevalence of preeclampsia (aOR 0.76, 95% CI |
| 542 | hypertension (1.9% vs. 2.3%, RR 1.20, 95% CI 0.42–3.41) or |
| 543 | preeclampsia (1.1% vs. 0.8%, RR 0.72, 95% CI 0.11–4.62) ( 49). |
| 551 | CI, 0.32–1.57) and preeclampsia (RR 0.62; 95% CI, 0.20–1.87), |
| 561 | in the Mediterranean diet group (RR 0.61; 95% CI, 0.37–1.01) ( 51). |
| 570 | 95% CI, 0.24–1.85) ( 52). |
| 683 | 0.58; 95% CI, 0.42, 0.81) |
| 809 | (aOR 0.76, 95% CI 0.56– |
| 864 | RR 1.20, 95% CI 0.42–3.41) |
| 866 | 0.8%, RR 0.72, 95% CI 0.11– |
| 986 | (adjusted RR [95% CI], Q4 |
| 1025 | aOR 0.78, 95% CI 0.64– |
| 1093 | 0.72, 95% CI 0.55–0.93); |
| 1130 | 0.67; 95% CI, |
| 1180 | Alternate Mediterranean Diet; MSDS, Mediterranean-Style Diet Score; aMed, Alternate Mediterranean Diet; RCT, Randomized Controlled Trial; RR, Relative Risk; OR, Odds Ratio; aOR, Adjusted Odds Ratio; CI, Confidence Inter… |

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

