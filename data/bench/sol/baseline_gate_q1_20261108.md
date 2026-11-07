# Baseline- und SE-Gate: Messung an gespeicherten Zeilen

Stand: 2026-11-07T21:24:59. Read-only; kein Modell, kein Netz.

Dokumente: 22 | Tabellen: 66 | Zeilen: 923

## Wie oft gibt es solche Tabellen ueberhaupt?

| Merkmal | Tabellen | Zeilen |
|---|---:|---:|
| Baseline-Caption | 17 | 248 |
| SE-Kopf ohne SD | 4 | 48 |
| alle | 66 | 923 |

## Was das heutige Gate durchlaesst

| Leser | Zeilen | zugeordnet | Baseline-Caption | SE im Kopf | SE-Rolle erkannt | Baseline oder SE |
|---|---:|---:|---:|---:|---:|---:|
| effektspalten | 28 | 28 | 0 | 0 | 0 | 0 |
| arm_tabelle | 14 | 14 | 14 | 11 | 11 | 14 |

Summe: 42 Zeilen, davon 14 aus einer Baseline-Tabelle oder einer SE-Spalte. SOL-Zeilen betroffen: 0 von 0.

## Beispiele

* `doi:10.1007/s12325-023-02708-6` - Actual sleep time (min) by WA (g 4.731301)
  - Caption: Table 1 Baseline demographics summary of study participants
  - Kopf: Particulars | Placebo ( n = 35), mean ± SE | VE ( n = 37), mean ± SE
  - Baseline: ja, SE im Kopf: ja, SE-Rolle erkannt: ja
* `doi:10.1371/journal.pone.0321635` - Age (Mean ± SD) (g 0.150129)
  - Caption: Table 1 Demographic Characteristics of Participants.
  - Kopf: Variable | Melatonin n=40 | Placebo n=40
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s12325-023-02708-6` - Age (years) (g -1.777794)
  - Caption: Table 1 Baseline demographics summary of study participants
  - Kopf: Particulars | Placebo ( n = 35), mean ± SE | VE ( n = 37), mean ± SE
  - Baseline: ja, SE im Kopf: ja, SE-Rolle erkannt: ja
* `doi:10.1371/journal.pone.0321635` - BMI (Mean ± SD) (g -0.077308)
  - Caption: Table 1 Demographic Characteristics of Participants.
  - Kopf: Variable | Melatonin n=40 | Placebo n=40
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s12325-023-02708-6` - BMI (kg/m 2 ) (g -0.998528)
  - Caption: Table 1 Baseline demographics summary of study participants
  - Kopf: Particulars | Placebo ( n = 35), mean ± SE | VE ( n = 37), mean ± SE
  - Baseline: ja, SE im Kopf: ja, SE-Rolle erkannt: ja
* `doi:10.1007/s12325-023-02708-6` - Beck anxiety inventory (BAI) (g 1.161635)
  - Caption: Table 1 Baseline demographics summary of study participants
  - Kopf: Particulars | Placebo ( n = 35), mean ± SE | VE ( n = 37), mean ± SE
  - Baseline: ja, SE im Kopf: ja, SE-Rolle erkannt: ja
* `doi:10.1371/journal.pone.0321635` - Duration of infertility (g 0.154571)
  - Caption: Table 1 Demographic Characteristics of Participants.
  - Kopf: Variable | Melatonin n=40 | Placebo n=40
  - Baseline: ja, SE im Kopf: nein, SE-Rolle erkannt: nein
* `doi:10.1007/s12325-023-02708-6` - Epworth sleepiness scale (ESS) (g 0.311142)
  - Caption: Table 1 Baseline demographics summary of study participants
  - Kopf: Particulars | Placebo ( n = 35), mean ± SE | VE ( n = 37), mean ± SE
  - Baseline: ja, SE im Kopf: ja, SE-Rolle erkannt: ja
* `doi:10.1007/s12325-023-02708-6` - Female, n (%) (g -0.008662)
  - Caption: Table 1 Baseline demographics summary of study participants
  - Kopf: Particulars | Placebo ( n = 35), mean ± SE | VE ( n = 37), mean ± SE
  - Baseline: ja, SE im Kopf: ja, SE-Rolle erkannt: ja
* `doi:10.1007/s12325-023-02708-6` - Male, n (%) (g 0.003828)
  - Caption: Table 1 Baseline demographics summary of study participants
  - Kopf: Particulars | Placebo ( n = 35), mean ± SE | VE ( n = 37), mean ± SE
  - Baseline: ja, SE im Kopf: ja, SE-Rolle erkannt: ja

## Grenzen

- Die Zuordnung Zeile -> Tabelle laeuft ueber das gespeicherte Zitat.
  Zeilen ohne eindeutige Zuordnung werden als solche gezaehlt und nicht
  bewertet; sie koennen die Quote unterschaetzen.
- Das Caption-Muster erkennt Ausgangslagentabellen nur am Wortlaut.
  Tabellen ohne "baseline" in der Caption, die trotzdem Ausgangswerte
  zeigen, bleiben unentdeckt - die Messung ist eine Untergrenze.
- Gemessen wird, was das Gate heute durchlaesst, nicht was ein neues
  Gate leisten koennte.

