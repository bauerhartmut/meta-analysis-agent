# Zielmass-Schnitt der gespeicherten Zeilen (2026-11-08)

Frage: Wie viele der gespeicherten Effektzeilen betreffen die
Einschlaflatenz, das Zielmass der Untersuchung?

Deterministisch auf dem normalisierten Outcome-Namen; kein Modell,
kein Netz. Label-Codes wie "T2" oder "Model 1" zaehlen als
"ohne Label", nicht als "daneben".

## Gesamt

| Klasse | Zeilen | Anteil |
|---|---:|---:|
| sol | 0 | 0.0 % |
| schlaf | 20 | 47.6 % |
| anderes | 19 | 45.2 % |
| ohne_label | 3 | 7.1 % |
| leer | 0 | 0.0 % |
| **Summe** | **42** | |

Zielmass-Anteil: 0.0 %.

## Je Leser

| Leser | Zeilen | SOL | Schlaf | anderes | ohne Label | leer | poolbar | poolbar SOL |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| effektspalten | 28 | 0 | 15 | 10 | 3 | 0 | 0 | 0 |
| arm_tabelle | 14 | 0 | 5 | 9 | 0 | 0 | 14 | 0 |
| fliesstext | 0 | - | - | - | - | - | - | - |
| veraenderung | 0 | - | - | - | - | - | - | - |

## Die SOL-Zeilen im Einzelnen

Keine Zeile liegt auf dem Zielmass.

## Grenzen

- Der Schnitt prueft den Outcome-Namen, nicht den studierten
  Zusammenhang. Eine Zeile kann Einschlaflatenz messen und trotzdem
  eine andere Intervention betreffen; das entscheidet die Populations-
  und Interventionsspalte, nicht dieses Skript.
- Der Anteil ist eine Untergrenze: Labels, die das Zielmass umschreiben
  ("latency to persistent sleep"), werden nicht erkannt und landen
  unter "anderes". Die Synonymtabelle ist bewusst kurz und belegt.

