# Passt die gespeicherte SE zum KI - und wo zählt sie? (2026-11-10)

48 Datenbanken, read-only auf Kopien, 0 Modellaufrufe. 1 DBs ohne Tabelle (siehe JSON).

## Der Code entscheidet, welche Abweichung zählt

- **Ratio-Typ (`or`, `rr`, `hr`) mit KI:** `standardize` rechnet die log-SE aus dem KI. Die gespeicherte `se` wird **nicht** benutzt.
- **Ratio-Typ ohne KI:** `se` wird als Standardfehler des log-Ratio gelesen. Steht sie auf der Ratio-Skala, ist die Zeile um den Faktor `effect` zu unpräzise.
- **Linear (`beta`, `mean_diff`, `g`, `smd`, `z`, `heritability`):** `se` wird direkt gelesen.

## A. Auf welcher Skala liegt die SE bei Ratio-Typen?

| Typ | Zeilen mit KI | passt linear (±5 %) | passt log (±5 %) | näher an linear |
|---|---:|---:|---:|---:|
| `hr` | 40 | 40 | 4 | 40 |
| `or` | 2516 | 2512 | 281 | 2512 |
| `rr` | 80 | 80 | 10 | 80 |

## B. Wo die SE in den Pool eingeht

| Pfad | Zeilen |
|---|---:|
| `linear_se_genutzt` | 3947 |
| `ratio_mit_ki_se_unbenutzt` | 2636 |

**Kritisch:** 0 Ratio-Zeilen haben eine SE, aber kein brauchbares KI. Dort liest `standardize` die SE als log-SE. Median `se/effect` = None — liegt der Wert nahe 0,1 bis 0,3, ist die SE auf der log-Skala gespeichert und alles ist in Ordnung; liegt er nahe 1, wurde linear gespeichert und die Zeile ist zu unpräzise.

### Linear: Abweichung der genutzten SE nach Typ

| Gruppe | n | passt (±5 %) | >10 % | >20 % | Median |r| | P90 |r| |
|---|---:|---:|---:|---:|---:|---:|
| `beta` | 1884 | 1884 | 0 | 0 | 0.0% | 0.0% |
| `mean_diff` | 1733 | 1733 | 0 | 0 | 0.0% | 0.0% |
| `g` | 195 | 195 | 0 | 0 | 0.0% | 0.0% |
| `smd` | 131 | 129 | 2 | 0 | 0.0% | 0.0% |
| `heritability` | 4 | 4 | 0 | 0 | 0.0% | 0.0% |

### Linear: nach Design

| Gruppe | n | passt (±5 %) | >10 % | >20 % | Median |r| | P90 |r| |
|---|---:|---:|---:|---:|---:|---:|
| `(unklassifiziert)` | 3886 | 3886 | 0 | 0 | 0.0% | 0.0% |
| `observational` | 31 | 31 | 0 | 0 | 0.0% | 0.0% |
| `parallel_rct` | 28 | 26 | 2 | 0 | 0.0% | 2.3% |
| `crossover_rct` | 2 | 2 | 0 | 0 | 0.0% | 0.0% |

### Linear: nach Bestand

| Gruppe | n | passt (±5 %) | >10 % | >20 % | Median |r| | P90 |r| |
|---|---:|---:|---:|---:|---:|---:|
| `andere` | 3901 | 3900 | 1 | 0 | 0.0% | 0.0% |
| `themen` | 46 | 45 | 1 | 0 | 0.0% | 0.0% |

### Linear: nach Lesepass

| Gruppe | n | passt (±5 %) | >10 % | >20 % | Median |r| | P90 |r| |
|---|---:|---:|---:|---:|---:|---:|
| `pass 1` | 3900 | 3900 | 0 | 0 | 0.0% | 0.0% |
| `pass 2` | 46 | 44 | 2 | 0 | 0.0% | 0.0% |
| `pass 3` | 1 | 1 | 0 | 0 | 0.0% | 0.0% |

## Beispiele mit mehr als 10 % Abweichung (linear, SE genutzt)

- research-exercise-and-depressive-symptoms-in-adul-bbb324.db `0d6b1b995a0c` (smd, parallel_rct): Effekt -0.24, KI -0.45–-0.03, SE gespeichert 0.1200 vs. aus KI 0.1071 (+12.0%)
- research-exercise-and-depressive-symptoms-in-adul-bbb324.db `0d6b1b995a0c` (smd, parallel_rct): Effekt -0.24, KI -0.45–-0.03, SE gespeichert 0.1200 vs. aus KI 0.1071 (+12.0%)
