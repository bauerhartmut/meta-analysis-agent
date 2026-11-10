# Tabellenprüfung 09843 und 2c7ab (2026-11-10)

Geprüft: Tabelle 2 und 3 in `09843` sowie Tabelle 3 in `2c7ab`.
Keine Annotation; die Zeilen sind Kandidaten mit Effekt und Unsicherheit.
Die endgültige Zeilenwahl treffen A und B.

## 09843 (cohort, observational)

Tabelle 2: OLS, Querschnitt 2016, N = 7782, Outcome „Depressive Symptoms“.
Tabelle 3: Individual Fixed Effects, 2016 → 2018, N = 5757,
cluster-robuste Standardfehler.

| Modell | Prädiktor | beta | SE | p | Zeitpunkt | belastbar |
|---|---|---|---|---|---|---|
| OLS 1 | kategorial (Sport ja/nein), unadjustiert | -1.309 | 0.106 | <0.001 | 2016 | ja |
| OLS 2 | kategorial, adjustiert | -0.536 | 0.101 | <0.001 | 2016 | ja |
| OLS 3 | kontinuierlich (Minuten/Tag), unadjustiert | -0.134 | 0.011 | <0.001 | 2016 | ja |
| OLS 4 | kontinuierlich, adjustiert | -0.056 | 0.010 | <0.001 | 2016 | ja |
| FE 1 | kategorial | -0.210 | 0.103 | <0.05 (Stern) | 2016 → 2018 | ja |
| FE 2 | kontinuierlich | -0.024 | 0.110 | Stern <0.05, aber beta/SE = -0.22 | 2016 → 2018 | nein |

**Befund:** Fünf Zeilen sind belastbar: die vier OLS-Modelle und das
FE-Modell mit der kategorialen Exposition. Die SE stehen in Klammern;
KI werden nicht berichtet, der Code kann sie aus den SE berechnen.

**Widerspruch bei FE 2:** beta = -0.024, SE = 0.110, Stern p < 0.05.
beta/SE = -0.22; ein p < 0.05 ist damit nicht vereinbar (p wäre ca. 0.83).
Entweder ist die SE ein Tippfehler (0.010 wie in Tabelle 2) oder der Stern
ist falsch. Vor der Annotation klären; ohne Klärung keine Zeile.

**Cross-lagged (Fig. 1):** beta = -0.073 (T1 → T2), -0.068 und -0.082,
jeweils p < 0.001, aber keine SE/CI im Text. Fig. 1 ist eine Abbildung;
im Text keine Unsicherheit. Daher keine Zeile; 5.11 nur in `notes`.

**Spezifikationen:** Die vier OLS-Modelle sind kategorial/kontinuierlich
und unadjustiert/adjustiert, keine Sensitivitätsanalysen; jede ist eine
eigene Zeile. Die adjustierten Modelle (OLS 2/4, FE 1) sind die
Hauptschätzer; OLS 1/3 sind unadjustierte Zusatzzeilen.

## 2c7ab (cross_sectional, observational)

Tabelle 3: logistische Regression, N = 303, Outcome Depression (GDS-15),
Querschnitt. Die Tabelle berichtet für **alle 16 Faktoren** eine univariate
OR mit 95-%-KI; multivariate aORs mit KI gibt es für fünf Faktoren.
`*` bedeutet p ≤ 0.05; „n.s.“ heißt KI schließt 1 ein.

| Faktor (Vergleich) | OR | 95 % CI | aOR | 95 % CI | belastbar |
|---|---|---|---|---|---|
| Älter (≥75) vs jünger | 1.9* | 1.1–3.3 | — | — | ja (1) |
| Weiblich vs männlich | 2.1* | 1.3–3.3 | — | — | ja (1) |
| Unverheiratet/getrennt/verwitwet/geschieden vs verheiratet | 2.0* | 1.2–3.3 | — | — | ja (1) |
| Analphabet vs alphabetisiert | 3.1* | 1.9–5.2 | 2.01* | 1.1–3.7 | ja (2) |
| Alleinlebend vs nicht | 3.8 | 0.8–17.3 | — | — | ja (1, n.s.) |
| Haushaltsmitglied (nicht Haushaltsvorstand) vs Haushaltsvorstand | 2.3* | 1.3–4.2 | — | — | ja (1) |
| Physische Unterstützung erhalten vs nicht | 0.4* | 0.2–0.8 | — | — | ja (1) |
| Finanzielle Unterstützung erhalten vs nicht | 0.5* | 0.25–0.96 | — | — | ja (1) |
| Respektiert gefühlt vs nicht | 0.05* | 0.01–0.22 | — | — | ja (1) |
| Keine Berücksichtigung vs Berücksichtigung | 8.25* | 4.48–15.20 | 4.02* | 2.01–8.04 | ja (2) |
| Keine Zeit vs Zeit | 8.76* | 3.62–21.18 | 3.55* | 1.29–9.76 | ja (2) |
| Nicht misshandelt vs misshandelt | 0.13* | 0.04–0.43 | — | — | ja (1) |
| Raucher vs Nichtraucher | 1.02 | 0.6–1.7 | — | — | ja (1, n.s.) |
| Alkohol trinkend vs nicht | 1.1 | 0.6–1.8 | — | — | ja (1, n.s.) |
| Körperliche Gesundheitsprobleme vs keine | 2.0* | 1.2–3.5 | 1.97* | 1.03–3.8 | ja (2) |
| Immobil (kann Haus nicht verlassen) vs mobil | 5.3* | 1.8–15.5 | 5.62* | 1.76–18.0 | ja (2) |

**Befund:** 21 belastbare Zeilen: 16 univariate ORs plus 5 multivariate
aORs. Die frühere Annahme „univariate ORs nur p-Werte“ stammt aus dem
Narrativ, nicht aus Tabelle 3. Die Tabelle ist die Primärquelle.

**Richtung und Reziproke:**
- Alter: Tabelle „≥75 Jahre“ OR 1.9; Narrativ „60–74 Jahre“ OR 1.93.
  Die Werte sind fast gleich; die Tabelle ist die Primärquelle. Die
  Altersgruppe im Narrativ ist zu prüfen.
- „Lack of consideration“ OR 8.25 und „considered“ OR 0.12 sind
  reziprok; „Lack of time“ 8.76 und „spent time“ 0.11 ebenfalls.
  Je Faktor eine Zeile, Richtung nach Tabelle; keine Doppelzeile.
- „Status in the family as household member“ OR 2.3 entspricht dem
  Narrativ „not head of household“ OR 2.31; gleiche Richtung.

**Rundung (Tabelle vs Abstract):**
- Illiteracy aOR: Tabelle 2.01 (1.1–3.7); Abstract 2.01 (1.08–3.75).
- Immobility aOR: Tabelle 5.62 (1.76–18.0); Abstract 5.59 (1.75–17.93).
- Physical health aOR: Tabelle 1.97 (1.03–3.8); Abstract 1.03–3.77.
Tabelle als Primärquelle; Abweichungen in `notes`.

**Adjustierung:** Die univariaten ORs sind unadjustiert, die aORs
adjustiert; das sind getrennte Zeilen. Die elf Faktoren ohne aOR haben
keine multivariate Zeile; die univariate OR mit KI bleibt.

## Konsequenz

- `09843`: 5 belastbare Zeilen; FE 2 vor Annotation klären; cross-lagged
  p-only, keine Zeile.
- `2c7ab`: 21 belastbare Zeilen (16 univariat + 5 aOR), nicht nur 5.
- Der Prüfpunkt `2c7ab` in `kalibrierung_pruefpunkte_20261110.md` ist
  entsprechend präzisiert: 5.2, nicht 5.2 + 5.7.
- A und B bleiben leer; keine Effektzeile erfunden.

## Quellen

- `09843`: Tabelle 2 (Zeile 288), Tabelle 3 (Zeile 345–361).
- `2c7ab`: Tabelle 3 (Zeile 571–605), Abstract (Zeile 1–30).
