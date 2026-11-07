# Fliesstext-Arme -> Hedges g

Stand: 2026-11-07T17:44:37. Leser: `research_agent/meta/arm_text.py` (deterministisch, kein LLM). Gespeichert wird nur, wenn beide Arme Fallzahl und SD tragen, das Gate besteht und das Zitat woertlich im Dokument steht.

| Kennzahl | Wert |
|---|---:|
| Dokumente | 1056 |
| Saetze geprueft | 315857 |
| Kandidaten | 1 |
| **gespeichert** | **1** |
| verworfen (Store) | 0 |
| fehlende XML | 3 |

## Warum Saetze abgelehnt wurden

- 242564  kein Mittelwert mit Streuung im Satz
- 46010  Tabellen-/Zitationsrest statt Ergebnissatz
- 20185  Baseline-/Veraenderungsmuster statt Gruppenvergleich
-  3095  Stichproben- oder Designbeschreibung statt Ergebnis
-  1747  Streuung als SEM/SE im Satz (nicht SD)
-  1138  Median/IQR statt Mittelwert mit SD
-   711  nicht genau zwei Mittelwerte mit Streuung im Satz
-   403  Fallzahl je Arm fehlt
-     2  Arm-Etikett fehlt
-     1  kein Interventionsarm - Gruppenvergleich ohne Intervention

## Gespeicherte Effekte

### 10.1371/journal.pmed.1002587

| Outcome | g | SE | n | Zeitpunkt | Arme |
|---|---:|---:|---:|---|---|
| DLMO | 0.412957 | 0.308968 | 43 | - | Following melatonin treatmen: 0.73 +- 1.21 (n=23); following placebo: 0.24 +- 1.11 (n=20) |

