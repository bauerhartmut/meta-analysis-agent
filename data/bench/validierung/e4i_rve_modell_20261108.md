# E4i - RVE mit Random-Effects-Gewichten

Stand: 2026-11-09 14:33 · Modellaufrufe: 0 · Tokens: 0

| Kuerzel | Aufruf | Material | Gewichte |
|---|---|---|---|
| HKJ | `pool(kept)` | kollabierte Zeilen | `1/(v + tau2)`, DL |
| HKJ(alle) | `pool(sub_rows)` | Zeilen vor dem Kollaps | `1/(v + tau2)`, DL |
| RVE-FE | `pool_rve(sub_rows)` | Zeilen vor dem Kollaps | `1/v` |
| RVE-RE | `pool_rve(sub_rows, weights="random")` | Zeilen vor dem Kollaps | `1/(v + tau2)`, DL |

Zerlegung auf der Log-Skala, jede Stufe auf gleichen Gewichten:

- **Cluster**: `ln(RE_RVE / HKJ(alle))` - gleiche Zeilen, gleiche tau2,
  naiver SE gegen Cluster-Sandwich.
- **Duplikation**: `ln(HKJ(alle) / HKJ(koll))` - mehr Zeilen als
  unabhaengig gezaehlt; negativ heisst: die naive Rechnung wird
  scheinbar praeziser, je mehr abhaengige Zeilen sie sieht.
- **Modell**: `ln(RE_RVE / RVE_FE)` - der Wechsel der Gewichte.

## Zielgruppen

| Gruppe | k | Zeilen | M | HKJ(koll) | HKJ(alle) | RVE-FE | RVE-RE | RE/HKJ | RE/HKJ(alle) | Modell |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| depressive symptoms [fisher_z] | 2 | 2 | 1 | 0.735 | 0.735 | - | - | - | - | - |
| depressive symptoms [hedges_g] | 3 | 4 | 3 | 1.466 | 0.805 | 1.550 | 1.270 | 0.87 | 1.58 | 0.82 |
| depressive symptoms [log_ratio] | 6 | 11 | 6 | 0.748 | 0.507 | 0.068 | 0.659 | 0.88 | 1.30 | 9.62 |
| depressive symptoms [raw:beta] | 4 | 4 | 3 | 0.536 | 0.536 | 0.458 | 0.772 | 1.44 | 1.44 | 1.68 |
| frailty index [raw:beta] | 2 | 2 | 1 | 0.108 | 0.108 | - | - | - | - | - |
| incident cardiovascular disease [log_ratio] | 5 | 6 | 4 | 1.529 | 1.200 | 1.438 | 1.791 | 1.17 | 1.49 | 1.25 |
| major adverse cardiovascular events [log_ratio] | 4 | 6 | 3 | 0.624 | 0.411 | 1.137 | 1.137 | 1.82 | 2.77 | 1.00 |
| preeclampsia [log_ratio] | 5 | 5 | 1 | 0.364 | 0.364 | - | - | - | - | - |

## Alle Gruppen

- Gruppen mit k >= 2: 10
- RVE-RE verfuegbar: 7
- tau2 in HKJ(alle) und RVE-RE identisch: 7 von 7

### Tabelle

| Gruppe | k | M | HKJ(koll) | HKJ(alle) | RVE-FE | RVE-RE | RVE-RE(REML) | Cluster (log) | Duplikation (log) | Modell (log) | RE/HKJ | RE/HKJ(alle) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| cardiovascular mortality [log_ratio] | 2 | 2 | 0.578 | 0.578 | 0.164 | 0.164 | 0.164 | -1.263 | 0.000 | 0.000 | 0.28 | 0.28 |
| depressive symptoms [fisher_z] | 2 | 1 | 0.735 | 0.735 | - | - | - | - | 0.000 | - | - | - |
| depressive symptoms [hedges_g] | 3 | 3 | 1.466 | 0.805 | 1.550 | 1.270 | 1.298 | 0.456 | -0.600 | -0.199 | 0.87 | 1.58 |
| depressive symptoms [log_ratio] | 6 | 6 | 0.748 | 0.507 | 0.068 | 0.659 | 1.164 | 0.262 | -0.389 | 2.264 | 0.88 | 1.30 |
| depressive symptoms [raw:beta] | 4 | 3 | 0.536 | 0.536 | 0.458 | 0.772 | 0.785 | 0.365 | 0.000 | 0.521 | 1.44 | 1.44 |
| frailty index [raw:beta] | 2 | 1 | 0.108 | 0.108 | - | - | - | - | 0.000 | - | - | - |
| health status [log_ratio] | 5 | 5 | 1.059 | 0.547 | 0.206 | 0.806 | 1.193 | 0.388 | -0.661 | 1.365 | 0.76 | 1.47 |
| incident cardiovascular disease [log_ratio] | 5 | 4 | 1.529 | 1.200 | 1.438 | 1.791 | 1.801 | 0.401 | -0.242 | 0.220 | 1.17 | 1.49 |
| major adverse cardiovascular events [log_ratio] | 4 | 3 | 0.624 | 0.411 | 1.137 | 1.137 | 1.131 | 1.018 | -0.417 | 0.000 | 1.82 | 2.77 |
| preeclampsia [log_ratio] | 5 | 1 | 0.364 | 0.364 | - | - | - | - | 0.000 | - | - | - |

## MACE im Detail

- Breiten: HKJ(koll) 0.624, HKJ(alle) 0.411, RVE-FE 1.137, RVE-RE 1.137.
- tau2: HKJ(koll) 0.0000, HKJ(alle) 0.0000, RVE-RE 0.0000 (6 Zeilen, 3 Cluster).
- Cluster-Beitrag: 1.018 (169% der Gesamtverbreiterung), Duplikation: -0.417 (-69%), Summe: 0.601 = RE/HKJ 1.82.
- Modellwechsel FE -> RE: 0.000 (Faktor 1.00), separat zu lesen.

## incident CVD im Detail

- Breiten: HKJ(koll) 1.529, HKJ(alle) 1.200, RVE-FE 1.438, RVE-RE 1.791.
- tau2: HKJ(koll) 0.3469, HKJ(alle) 0.3431, RVE-RE 0.3431 (6 Zeilen, 4 Cluster).
- Cluster-Beitrag: 0.401 (253% der Gesamtverbreiterung), Duplikation: -0.242 (-153%), Summe: 0.158 = RE/HKJ 1.17.
- Modellwechsel FE -> RE: 0.220 (Faktor 1.25), separat zu lesen.

## Lesart

tau2 wird in HKJ(alle) und RVE-RE aus denselben Zeilen mit derselben
Methode geschaetzt; der Unterschied zwischen beiden ist damit reine
Cluster-Korrektur. Die Duplikation ist der Preis der kollabierten
Rechnung: Sie sieht weniger Zeilen und wird dadurch breiter - aber
nicht, weil sie ehrlicher waere, sondern weil ihr Information fehlt.

Der Modellwechsel FE -> RE ist keine Stufe dieser Kette: Er
beantwortet die Frage, ob die Gewichte die Heterogenitaet tragen.

## Grenzen

- HKJ(alle) behandelt abhaengige Zeilen als unabhaengig - genau der
  Fehler, den RVE korrigiert. Der Vergleich ist die Zerlegung dieses
  Effekts, kein Modellvergleich zweier korrekter Rechnungen.
- Die Zerlegung ist logarithmisch in den Breiten, keine
  Varianzzerlegung.
- RVE-RE mit REML steht als Sensitivitaet daneben, nicht als
  Hauptzahl; die Hauptzahl benutzt DL wie HKJ.
