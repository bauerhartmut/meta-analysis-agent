# E5 - Wirkung des Lesepass-Filters auf Pool und Intervall

Stand: 2026-11-10 17:29 · Modellaufrufe: 0 · Tokens: 0

Read-only auf Kopien. Teil B ist eine Konstruktion an echten Zeilen,
kein Messwert ueber die Datenlage.

## A. Datenlage: welche Lesepaesse sind gespeichert?

48 DBs mit 7897 Zeilen gelesen.

| extraction_pass | Zeilen |
|---|---:|
| 1 | 7477 |
| 2 | 412 |
| 3 | 8 |

DBs mit mindestens einer Zeile ueber Pass 1: **15**.

## B. Mechanismusprobe: was eine Doppellesung anrichten wuerde

Datenbasis: `data/bench/sol/direct_label2.db`, 132 Gruppen mit k >= 2.
Je Gruppe drei Rechnungen: Referenz (echte Zeilen), ohne Regel
(jede Zeile zusaetzlich als Erstlesung) und mit Regel (zusaetzliche
Zeile als Zweitlesung).

- k-Summe: 830 Referenz, 1660 ohne Regel, 830 mit Regel.
- In 132 von 132 Gruppen verdoppelt die Rechnung ohne Regel das k.
- KI-Breite ohne Regel im Median 62.2% enger, maximal 89.3%.
- Filter haelt die Referenz in allen Gruppen: ja.

| Outcome | Skala | n | k ref | k ohne | k mit | gepoolt ref | KI-Breite ref | Breite ohne | enger um |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| wake after sleep onset | raw:mean_diff | 2 | 2 | 4 | 2 | -2.703416 | 135.663116 | 14.525186 | 89.3% |
| teaes | log_ratio | 2 | 2 | 4 | 2 | 0.042436 | 2.070383 | 0.226559 | 89.1% |
| 7 observational studies 1 randomized trial | hedges_g | 2 | 2 | 4 | 2 | 0.398059 | 4.2842 | 0.588408 | 86.3% |
| sleep period time min | raw:mean_diff | 2 | 2 | 4 | 2 | 12.776517 | 365.867752 | 52.371217 | 85.7% |
| factors of practice based univariable and multivariable logistic regression | log_ratio | 2 | 2 | 4 | 2 | 0.067556 | 7.105478 | 1.01957 | 85.7% |
| zheng et al hour | raw:mean_diff | 2 | 2 | 4 | 2 | 1.515286 | 31.580499 | 4.53754 | 85.6% |
| r dlpfc | raw:mean_diff | 2 | 2 | 4 | 2 | -4.455969 | 30.810689 | 4.440698 | 85.6% |
| teaes leading to study withdrawal | log_ratio | 2 | 2 | 4 | 2 | 0.405887 | 8.414967 | 1.21246 | 85.6% |
| ess | raw:mean_diff | 2 | 2 | 4 | 2 | -0.609754 | 24.120115 | 3.483673 | 85.6% |
| girls | log_ratio | 2 | 2 | 4 | 2 | 1.265139 | 2.842434 | 0.410323 | 85.6% |
| borderline sleep quality | log_ratio | 2 | 2 | 4 | 2 | 0.178196 | 0.106318 | 0.015374 | 85.5% |
| boys | log_ratio | 2 | 2 | 4 | 2 | -1.286728 | 3.429431 | 0.495764 | 85.5% |

## C. Hauptpfad `build_analysis` auf den echten Zeilen

| Datei | Zeilen | Pass > 1 | Gruppen | k alt | k neu | abgelehnt alt | abgelehnt neu |
|---|---:|---:|---:|---:|---:|---:|---:|
| data/harness_local.db | 21 | 12 | 1 | 1 | 1 | 20 | 20 |
| data/research-does-acute-caffeine-versus-placebo-affec-972eac.db | 8 | 4 | 0 | 0 | 0 | 8 | 8 |
| data/research-does-caffeine-intake-affect-short-term-m-783a51.db | 12 | 6 | 0 | 0 | 0 | 12 | 12 |
| data/research-does-melatonin-improve-sleep-onset-laten-382747.db | 19 | 9 | 1 | 1 | 1 | 18 | 18 |
| data/research-exercise-and-depressive-symptoms-in-adul-bbb324.db | 129 | 63 | 13 | 24 | 21 | 105 | 108 |
| data/research-kognition-und-gesundheit-ist-der-zusamme-ec45a1.db | 127 | 62 | 7 | 12 | 12 | 115 | 115 |
| data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db | 91 | 49 | 14 | 26 | 26 | 65 | 65 |
| data/research2-does-melatonin-improve-sleep-onset-laten-382747.db | 8 | 4 | 2 | 2 | 2 | 6 | 6 |

## D. Paarung: hat jede Zweitlesung eine Erstlesung?

Schluessel wie `_match_key`: Quelle, Outcome, Vergleich, Richtung.
Ohne Pendant ist die Zeile eine Aussage nur aus Pass B - sie faellt
durch den Filter aus dem Pool, ohne je gegengelesen worden zu sein.

| Datei | Pass > 1 | Text-Zwilling | Wert-Zwilling | Zitat-Zwilling | ohne jeden Zwilling |
|---|---:|---:|---:|---:|---:|
| data/harness_local.db | 12 | 3 | 10 | 9 | 2 |
| data/research-does-acute-caffeine-versus-placebo-affec-972eac.db | 4 | 4 | 4 | 4 | 0 |
| data/research-does-caffeine-intake-affect-short-term-m-783a51.db | 6 | 1 | 4 | 3 | 1 |
| data/research-does-melatonin-improve-sleep-onset-laten-382747.db | 9 | 5 | 8 | 8 | 0 |
| data/research-exercise-and-depressive-symptoms-in-adul-bbb324.db | 63 | 14 | 48 | 44 | 11 |
| data/research-kognition-und-gesundheit-ist-der-zusamme-ec45a1.db | 62 | 20 | 46 | 39 | 13 |
| data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db | 49 | 18 | 30 | 23 | 18 |
| data/research2-does-melatonin-improve-sleep-onset-laten-382747.db | 4 | 1 | 4 | 4 | 0 |

## Grenzen


- Teil B verdoppelt jede Zeile einer Gruppe, auch unabhaengige Arme.
  Das ist die Obergrenze des Fehlers, nicht sein typischer Wert.
- Teil B nutzt `pool` ohne `_collapse_same_study`. Im Hauptpfad faengt
  der Kollaps gleiche Quelle und gleiches Outcome bereits ab; deshalb
  ist Teil C die ehrliche Zahl fuer den Berichtspfad.
- Ohne gespeicherte Doppelpässe kann Teil C die Regel nicht zeigen -
  die Null dort ist eine Aussage ueber die Daten, nicht ueber den Code.
