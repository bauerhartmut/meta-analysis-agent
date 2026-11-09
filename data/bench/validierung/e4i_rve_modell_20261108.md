# E4i - RVE mit Random-Effects-Gewichten

Stand: 2026-11-09 14:26 · Modellaufrufe: 0 · Tokens: 0

Drei Rechnungen auf demselben Material (Zeilen vor dem Kollaps):

| Kuerzel | Aufruf | Gewichte |
|---|---|---|
| HKJ | `pool(kept)` | `1/(v + tau2)`, DL |
| RVE-FE | `pool_rve(sub_rows)` | `1/v` |
| RVE-RE | `pool_rve(sub_rows, weights="random")` | `1/(v + tau2)`, DL |

Zerlegung auf der Log-Skala (Breiten sind dort additiv):
`ln(w_RE/w_HKJ) = ln(w_RE/w_FE) + ln(w_FE/w_HKJ)` - Modell plus
Cluster. Der Anteil sagt, welcher Teil der Verbreiterung vom
Modellwechsel kommt.

## Zielgruppen

| Gruppe | k | M | HKJ-Breite | RVE-FE | RVE-RE | RE/HKJ | Modellanteil |
|---|---:|---:|---:|---:|---:|---:|---:|
| depressive symptoms [fisher_z] | 2 | 1 | 0.735 | - | - | - | - |
| depressive symptoms [hedges_g] | 3 | 3 | 1.466 | 1.550 | 1.270 | 0.87 | 139% |
| depressive symptoms [log_ratio] | 6 | 6 | 0.748 | 0.068 | 0.659 | 0.88 | -1772% |
| depressive symptoms [raw:beta] | 4 | 3 | 0.536 | 0.458 | 0.772 | 1.44 | 143% |
| frailty index [raw:beta] | 2 | 1 | 0.108 | - | - | - | - |
| incident cardiovascular disease [log_ratio] | 5 | 4 | 1.529 | 1.438 | 1.791 | 1.17 | 139% |
| major adverse cardiovascular events [log_ratio] | 4 | 3 | 0.624 | 1.137 | 1.137 | 1.82 | 0% |
| preeclampsia [log_ratio] | 5 | 1 | 0.364 | - | - | - | - |

## Alle Gruppen

- Gruppen mit k >= 2: 10
- RVE-RE verfuegbar: 7
- RVE-RE breiter als HKJ: 3
- Median Modellanteil: 0%

### Tabelle

| Gruppe | k | M | HKJ | RVE-FE | RVE-RE | RVE-RE(REML) | FE/HKJ | RE/FE | RE/HKJ | Modell | Cluster | Modellanteil |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cardiovascular mortality [log_ratio] | 2 | 2 | 0.578 | 0.164 | 0.164 | 0.164 | 0.28 | 1.00 | 0.28 | 0.000 | -1.263 | -0% |
| depressive symptoms [fisher_z] | 2 | 1 | 0.735 | - | - | - | - | - | - | - | - | - |
| depressive symptoms [hedges_g] | 3 | 3 | 1.466 | 1.550 | 1.270 | 1.298 | 1.06 | 0.82 | 0.87 | -0.199 | 0.055 | 139% |
| depressive symptoms [log_ratio] | 6 | 6 | 0.748 | 0.068 | 0.659 | 1.164 | 0.09 | 9.62 | 0.88 | 2.264 | -2.391 | -1772% |
| depressive symptoms [raw:beta] | 4 | 3 | 0.536 | 0.458 | 0.772 | 0.785 | 0.86 | 1.68 | 1.44 | 0.521 | -0.157 | 143% |
| frailty index [raw:beta] | 2 | 1 | 0.108 | - | - | - | - | - | - | - | - | - |
| health status [log_ratio] | 5 | 5 | 1.059 | 0.206 | 0.806 | 1.193 | 0.19 | 3.92 | 0.76 | 1.365 | -1.638 | -500% |
| incident cardiovascular disease [log_ratio] | 5 | 4 | 1.529 | 1.438 | 1.791 | 1.801 | 0.94 | 1.25 | 1.17 | 0.220 | -0.061 | 139% |
| major adverse cardiovascular events [log_ratio] | 4 | 3 | 0.624 | 1.137 | 1.137 | 1.131 | 1.82 | 1.00 | 1.82 | 0.000 | 0.601 | 0% |
| preeclampsia [log_ratio] | 5 | 1 | 0.364 | - | - | - | - | - | - | - | - | - |

## MACE im Detail

- Breiten: HKJ 0.624, RVE-FE 1.137, RVE-RE 1.137.
- tau2 (HKJ) 0.000, tau2 (RVE-RE, DL) 0.000, REML-Variante 0.002.
- Modellanteil an der Log-Verbreiterung: 0% (Modell 0.000, Cluster 0.601).
- Damit ist die Verbreiterung um Faktor 1.82 praktisch vollstaendig Cluster-Effekt: tau2 ist in beiden Rechnungen null, die Gewichte sind identisch. Modell und Cluster sind hier nicht vermischt.

## Lesart

Ist der Modellanteil gross, war ein Teil der scheinbaren
Cluster-Verbreiterung nur der Wechsel von Fixed zu Random Effects:
RVE-FE unterschlaegt die Heterogenitaet, die HKJ traegt. Bleibt nach
dem Modellwechsel noch ein Clusteranteil uebrig, ist das der echte
Preis fuer haengige Zeilen.

Anteile ausserhalb von 0 bis 100 Prozent sind moeglich: dann wirken
Modell- und Cluster-Beitrag in verschiedene Richtungen und heben sich
teilweise auf. Dort ist der Anteil nur zusammen mit den beiden
Log-Beitraegen lesbar.

## Grenzen

- tau2 wird aus den Zeilen vor dem Kollaps geschaetzt; HKJ schaetzt
  es aus den kollabierten Zeilen. Die Zerlegung ist deshalb eine
  Annaeherung, kein exakter Vergleich zweier identischer Modelle.
- Der Modellanteil ist eine Zerlegung auf der Log-Skala, keine
  Varianzzerlegung. Er sagt nichts ueber die Ursache der
  Heterogenitaet.
- RVE-RE mit REML steht als Sensitivitaet daneben, nicht als
  Hauptzahl; die Hauptzahl benutzt DL wie HKJ.
