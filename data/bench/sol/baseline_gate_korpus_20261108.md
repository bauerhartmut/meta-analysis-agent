# Baseline- und SE-Gate: Messung an gespeicherten Zeilen

Stand: 2026-11-07T21:25:22. Read-only; kein Modell, kein Netz.

Dokumente: 1027 | Tabellen: 2704 | Zeilen: 41423

## Wie oft gibt es solche Tabellen ueberhaupt?

| Merkmal | Tabellen | Zeilen |
|---|---:|---:|
| Baseline-Caption | 499 | 10998 |
| SE-Kopf ohne SD | 103 | 1733 |
| alle | 2704 | 41423 |

## Was das heutige Gate durchlaesst

| Leser | Zeilen | zugeordnet | Baseline-Caption | SE im Kopf | SE-Rolle erkannt | Baseline oder SE |
|---|---:|---:|---:|---:|---:|---:|
| effektspalten | 1000 | 1000 | 210 | 30 | 48 | 240 |
| arm_tabelle | 97 | 97 | 33 | 15 | 15 | 33 |

Summe: 1097 Zeilen, davon 273 aus einer Baseline-Tabelle oder einer SE-Spalte. SOL-Zeilen betroffen: 5 von 13.

## Beispiele

* `doi:10.1007/s40520-025-03020-9` - 30–90 min (beta 1.21)
  - Caption: Table 2 Multivariate linear regression results of sleep characteristics and physical functioning
  - Kopf: | Case/% | Handgrip (β-Coefficients (95%CI)) Model 1 | Handgrip (β-Coefficients (95%CI)) Model 2 | Handgrip (β-Coefficients (95%CI)) Model 3 | Handgrip (β-Coeff
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s40520-025-03020-9` - 30–90 min (beta 1.06)
  - Caption: Table 2 Multivariate linear regression results of sleep characteristics and physical functioning
  - Kopf: | Case/% | Handgrip (β-Coefficients (95%CI)) Model 1 | Handgrip (β-Coefficients (95%CI)) Model 2 | Handgrip (β-Coefficients (95%CI)) Model 3 | Handgrip (β-Coeff
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s40520-025-03020-9` - 30–90 min (beta 0.83)
  - Caption: Table 2 Multivariate linear regression results of sleep characteristics and physical functioning
  - Kopf: | Case/% | Handgrip (β-Coefficients (95%CI)) Model 1 | Handgrip (β-Coefficients (95%CI)) Model 2 | Handgrip (β-Coefficients (95%CI)) Model 3 | Handgrip (β-Coeff
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s40520-025-03020-9` - 30–90 min (beta -0.01)
  - Caption: Table 2 Multivariate linear regression results of sleep characteristics and physical functioning
  - Kopf: | Case/% | Handgrip (β-Coefficients (95%CI)) Model 1 | Handgrip (β-Coefficients (95%CI)) Model 2 | Handgrip (β-Coefficients (95%CI)) Model 3 | Handgrip (β-Coeff
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s40520-025-03020-9` - 30–90 min (beta -0.01)
  - Caption: Table 2 Multivariate linear regression results of sleep characteristics and physical functioning
  - Kopf: | Case/% | Handgrip (β-Coefficients (95%CI)) Model 1 | Handgrip (β-Coefficients (95%CI)) Model 2 | Handgrip (β-Coefficients (95%CI)) Model 3 | Handgrip (β-Coeff
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s40520-025-03020-9` - 30–90 min (beta -0.12)
  - Caption: Table 2 Multivariate linear regression results of sleep characteristics and physical functioning
  - Kopf: | Case/% | Handgrip (β-Coefficients (95%CI)) Model 1 | Handgrip (β-Coefficients (95%CI)) Model 2 | Handgrip (β-Coefficients (95%CI)) Model 3 | Handgrip (β-Coeff
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s40520-025-03020-9` - 30–90 min (beta 0.0)
  - Caption: Table 2 Multivariate linear regression results of sleep characteristics and physical functioning
  - Kopf: | Case/% | Handgrip (β-Coefficients (95%CI)) Model 1 | Handgrip (β-Coefficients (95%CI)) Model 2 | Handgrip (β-Coefficients (95%CI)) Model 3 | Handgrip (β-Coeff
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s40520-025-03020-9` - 30–90 min (beta 0.18)
  - Caption: Table 2 Multivariate linear regression results of sleep characteristics and physical functioning
  - Kopf: | Case/% | Handgrip (β-Coefficients (95%CI)) Model 1 | Handgrip (β-Coefficients (95%CI)) Model 2 | Handgrip (β-Coefficients (95%CI)) Model 3 | Handgrip (β-Coeff
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s40520-025-03020-9` - 30–90 min (beta 0.22)
  - Caption: Table 2 Multivariate linear regression results of sleep characteristics and physical functioning
  - Kopf: | Case/% | Handgrip (β-Coefficients (95%CI)) Model 1 | Handgrip (β-Coefficients (95%CI)) Model 2 | Handgrip (β-Coefficients (95%CI)) Model 3 | Handgrip (β-Coeff
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s40520-025-03020-9` - 30–90 min (beta 0.23)
  - Caption: Table 2 Multivariate linear regression results of sleep characteristics and physical functioning
  - Kopf: | Case/% | Handgrip (β-Coefficients (95%CI)) Model 1 | Handgrip (β-Coefficients (95%CI)) Model 2 | Handgrip (β-Coefficients (95%CI)) Model 3 | Handgrip (β-Coeff
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein

## Grenzen

- Die Zuordnung Zeile -> Tabelle laeuft ueber das gespeicherte Zitat.
  Zeilen ohne eindeutige Zuordnung werden als solche gezaehlt und nicht
  bewertet; sie koennen die Quote unterschaetzen.
- Das Caption-Muster erkennt Ausgangslagentabellen nur am Wortlaut.
  Tabellen ohne "baseline" in der Caption, die trotzdem Ausgangswerte
  zeigen, bleiben unentdeckt - die Messung ist eine Untergrenze.
- Gemessen wird, was das Gate heute durchlaesst, nicht was ein neues
  Gate leisten koennte.

