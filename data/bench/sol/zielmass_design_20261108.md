# Zielmass-Schnitt der gespeicherten Zeilen (2026-11-08)

Frage: Wie viele der gespeicherten Effektzeilen betreffen die
Einschlaflatenz, das Zielmass der Untersuchung?

Deterministisch auf dem normalisierten Outcome-Namen; kein Modell,
kein Netz. Label-Codes wie "T2" oder "Model 1" zaehlen als
"ohne Label", nicht als "daneben".

## Gesamt

| Klasse | Zeilen | Anteil |
|---|---:|---:|
| sol | 11 | 1.1 % |
| schlaf | 316 | 31.7 % |
| anderes | 656 | 65.8 % |
| ohne_label | 14 | 1.4 % |
| leer | 0 | 0.0 % |
| **Summe** | **997** | |

Zielmass-Anteil: 1.1 %.

## Je Leser

| Leser | Zeilen | SOL | Schlaf | anderes | ohne Label | leer | poolbar | poolbar SOL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| effektspalten | 838 | 11 | 293 | 534 | 0 | 0 | 247 | 11 |
| arm_tabelle | 159 | 0 | 23 | 122 | 14 | 0 | 159 | 0 |
| fliesstext | 0 | - | - | - | - | - | - | - |
| veraenderung | 0 | - | - | - | - | - | - | - |

## Die SOL-Zeilen im Einzelnen

11 Zeilen aus 5 Quellen, davon 11 poolbar.

| Leser | Quelle | Outcome | Typ | Effekt | poolbar |
|---|---|---|---|---:|---:|
| effektspalten | doi:10.1093/sleep/zsae250 | Sleep latency (min) | mean_diff | -4.2 | ja |
| effektspalten | doi:10.1093/sleep/zsae250 | Sleep latency (min) | mean_diff | -2.3 | ja |
| effektspalten | doi:10.1093/sleep/zsae250 | Sleep latency (min) | mean_diff | 1.3 | ja |
| effektspalten | doi:10.1111/jsr.70311 | Sleep onset latency | mean_diff | 3.8 | ja |
| effektspalten | doi:10.1111/jsr.70311 | Sleep onset latency | mean_diff | 3.4 | ja |
| effektspalten | doi:10.1111/jsr.70311 | Sleep onset latency | mean_diff | 5.7 | ja |
| effektspalten | doi:10.1111/jsr.70311 | Sleep onset latency | mean_diff | 4.6 | ja |
| effektspalten | doi:10.1093/sleep/zsaa194 | Sleep onset latency | mean_diff | -5.1 | ja |
| effektspalten | doi:10.2188/jea.je20140201 | Sleep onset latency, log min | mean_diff | -0.1 | ja |
| effektspalten | doi:10.2188/jea.je20140201 | Sleep onset latency, log min | mean_diff | -0.002 | ja |
| effektspalten | doi:10.1001/jamanetworkopen.2026.26983 | Sleep onset latency, min | g | 0.07 | ja |

## Grenzen

- Der Schnitt prueft den Outcome-Namen, nicht den studierten
  Zusammenhang. Eine Zeile kann Einschlaflatenz messen und trotzdem
  eine andere Intervention betreffen; das entscheidet die Populations-
  und Interventionsspalte, nicht dieses Skript.
- Der Anteil ist eine Untergrenze: Labels, die das Zielmass umschreiben
  ("latency to persistent sleep"), werden nicht erkannt und landen
  unter "anderes". Die Synonymtabelle ist bewusst kurz und belegt.

