# Zielmass-Schnitt der gespeicherten Zeilen (2026-11-08)

Frage: Wie viele der gespeicherten Effektzeilen betreffen die
Einschlaflatenz, das Zielmass der Untersuchung?

Deterministisch auf dem normalisierten Outcome-Namen; kein Modell,
kein Netz. Label-Codes wie "T2" oder "Model 1" zaehlen als
"ohne Label", nicht als "daneben".

## Gesamt

| Klasse | Zeilen | Anteil |
|---|---:|---:|
| sol | 13 | 1.1 % |
| schlaf | 338 | 29.1 % |
| anderes | 792 | 68.2 % |
| ohne_label | 18 | 1.6 % |
| leer | 0 | 0.0 % |
| **Summe** | **1161** | |

Zielmass-Anteil: 1.1 %.

## Je Leser

| Leser | Zeilen | SOL | Schlaf | anderes | ohne Label | leer | poolbar | poolbar SOL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| effektspalten | 1000 | 13 | 315 | 670 | 2 | 0 | 323 | 12 |
| arm_tabelle | 161 | 0 | 23 | 122 | 16 | 0 | 161 | 0 |
| fliesstext | 0 | - | - | - | - | - | - | - |
| veraenderung | 0 | - | - | - | - | - | - | - |

## Die SOL-Zeilen im Einzelnen

13 Zeilen aus 7 Quellen, davon 12 poolbar.

| Leser | Quelle | Outcome | Typ | Effekt | poolbar |
|---|---|---|---|---:|---:|
| effektspalten | doi:10.3389/fnins.2026.1816963 | SOL | mean_diff | 2.12 | ja |
| effektspalten | doi:10.2147/nss.s460882 | Sleep latency | or | 2.56 | nein |
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

