# Prüfpunkte der neun Kalibrierungsdokumente (2026-11-10)

Geprüft: die 12 Kalibrierungsdokumente ohne die drei Startdokumente
`7111ea`, `bb921` und `203c`. Keine Annotation; die Fragen sind
Prüfhinweise, keine Vorgaben. Anker sind kurze Volltextzitate.

## Befund

| Dokument | Schicht / Design | Prüfpunkt | Anker | Frage |
|---|---|---|---|---|
| `fb484` | rct / **aggregate** (vorher `parallel_rct`) | 5.1 + 5.8 | Abstract: „systematic review … meta-analytical procedures“; „g = -0.37, 95% confidence interval (-0.56; -0.17)“ | Metaanalyse, kein RCT (15 RCTs, 12 in der Metaanalyse); gepoolter SMD eine Zeile, `is_primary: false`. |
| `09843` | cohort / observational | 5.4 + 5.11 | Tabelle 3: `−0.210*(0.103)`, `−0.024*(0.110)`; Table S4 (IPW): `−0.023*`, SE 0.011, p 0.039; Abstract: T1→T2 `β=−0.073` | 5 belastbare Zeilen (4 OLS + FE kategorial). FE kontinuierlich `−0.024 (0.110)` ist mit Stern p<0.05 unvereinbar (β/SE ≈ −0.22); SE 0.110 ist Tippfehler, exakte FE-SE nicht bestätigt. Keine Primärzeile; IPW in `notes`; cross-lagged p-only. |
| `2c7ab` | cross_sectional / observational | 5.2 | Tabelle 3: alle 16 univariaten ORs mit 95 % KI (z. B. `OR 3.1, 1.9-5.2`), 5 multivariate aORs (z. B. `aOR 2.01, 1.1-3.7`) | Tabelle als Primärquelle: univariate ORs mit KI sind Zeilen, nicht nur die aORs. Richtung beachten: Narrativ nennt bei Alter 60-74, Tabelle ≥75; `considered` 0.12 ist reziprok zu `lack of consideration` 8.25, `spent time` 0.11 zu `lack of time` 8.76. |
| `334f` | aggregate / aggregate | 5.8 + 5.9 + 5.4 | Abstract: 47 Studien, 2895 Teilnehmer; `Beta: 0.36 (0.05; 0.68)`, `Beta: -0.51 (-0.80; -0.22)`; `SMD: -0.97 (-1.30 to -0.63)` bei 800 METs | Netzwerkschätzer als Zeilen; Dosis-Kurve/Peak in `notes`; Meta-Regressions-Betas mit CrI als 5.4-Zeilen. |
| `2675` | cross_sectional / observational | 5.5 | Statistik: „Spearman’s rank correlation“, Kappa, Cronbach alpha | Nur Korrelationen mit KI sind Zeilen; Kappa/Alpha sind keine Schema-Effekttypen; sonst `no_effect_reason`. |
| `87079` | crossover / crossover_rct | 5.11 + 5.7 | Abstract: „mean score … greater … (all p-values<0.05)“; „preceded by a baseline measure“ | Baseline vs 24-h-Abstinenz; Mittelwerte/p allein keine Zeile; nur eine Mean Difference mit KI/SE wäre eine Zeile. |
| `3bbb` | crossover / crossover_rct | 5.3 + 5.7 + 5.9 | Methods: „Cohen’s d and partial eta-squared“; Fig. 2: „Error bars show the standard error“ | Cohen’s d → `smd`; η² kein Schema-Typ; ohne KI/SE keine Zeile; Crossover-Bedingungen getrennt prüfen. |
| `3134` | cohort / observational | 5.2 + 5.4 + 5.9 | Zeile 193: `RR: 1.10; 95% CI: (1.04–1.18)`; Zeile 219: `β: −0.40; 95% CI: −0.65 to −0.15`; median follow-up 5,8 ± 2,5 Jahre | Haupt-RR und MCS-Beta sind Zeilen; Sensitivitäts-/Subgruppen-RRs in `notes` oder eigene Population; median follow-up kein Effekt. |
| `d0bec` | cohort / observational | 5.2 | `HR 0.95 (95% CI: 0.87, 1.05) before and 0.78 (95% CI: 0.47, 1.28) after bias adjustment` | Zwei HRs (unadjustiert/bias-adjustiert) sind zwei Zeilen; Validitätskoeffizient und Attenuationsfaktor keine Effektzeilen. |

## Was kein Prüfpunkt ist

- `3134`: median follow-up (5,8 ± 2,5 Jahre) ist eine Studiencharakteristik,
  kein Effekt.
- `87079`: „beta 2 power“ ist EEG-Leistung, kein Regressionskoeffizient.
- `2675`: die Formel zur Stichprobengröße ist kein Zeitpunkt und keine
  Spannweite.
- `3bbb`/`87079`: Literaturzitate und Hintergrundtreffer sind keine
  Effektstellen.
- `334f`: Dosis-Wirkungs-Kurvenpunkte (800/1000 METs) sind keine eigenen
  Zeilen; sie gehören in `notes`.

## Konsequenz

- `fb484` ist vor der Annotation von `parallel_rct` auf `aggregate`
  korrigiert; `stratum: rct` bleibt Auswahlschicht.
- Die übrigen acht bleiben in ihrer Designkategorie; die Prüfpunkte sind
  Regelanwendungen, keine Änderungen.
- Die Tabellenprüfung 09843/2c7ab hat die 2c7ab-Regel präzisiert:
  univariate ORs mit KI sind Zeilen; 09843 hat fünf belastbare Zeilen.
- Die Klärung 09843 steht in `goldstandard_klaerung_09843.md`.
- A und B bleiben leer; es wird keine Effektzeile erfunden.
