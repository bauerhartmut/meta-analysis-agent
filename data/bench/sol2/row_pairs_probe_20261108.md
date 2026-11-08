# Zeilenpaarung: Probe vor dem Bau

Stand: 2026-11-08T13:00:21. Read-only auf den 31 XML, kein Netz.

Frage: Gibt es Tabellen, in denen derselbe Endpunkt einmal je Arm in
einer eigenen Zeile steht (z. B. PRM-Zeile und Placebo-Zeile)? Nur
solche Tabellen waeren paarbar.

| Kennzahl | Wert |
|---|---:|
| gescreente Dokumente | 20 |
| Tabellen mit SOL-Zeilen | 19 |
| davon mit Einzelarm-Zeilen | 3 |
| Einzelarm-Zeilen insgesamt | 5 |
| **paarbare Tabellen** | **0** |

## Befund je Tabelle

| PMC | Tabelle | SOL-Zeilen | Einzelarm | paarbar |
|---|---:|---:|---|---|
| PMC12903794 | 1 | 2 | - | - |
| PMC12903794 | 2 | 1 | - | - |
| PMC12903794 | 3 | 1 | - | - |
| PMC11103136 | 1 | 1 | - | - |
| PMC10131443 | 2 | 1 | Sleep Latency | - |
| PMC5774131 | 0 | 1 | - | - |
| PMC5774131 | 1 | 1 | - | - |
| PMC4365553 | 0 | 1 | - | - |
| PMC4365553 | 1 | 1 | - | - |
| PMC4365553 | 2 | 1 | - | - |
| PMC4425994 | 1 | 2 | - | - |
| PMC4425994 | 2 | 2 | - | - |
| PMC3489506 | 0 | 2 | - | - |
| PMC3489506 | 2 | 2 | - | - |
| PMC3489506 | 8 | 3 | - | - |
| PMC2933606 | 3 | 2 | Sleep latency, Sleep onset | - |
| PMC2933606 | 5 | 2 | Sleep latency, Sleep onset | - |
| PMC2952772 | 1 | 3 | - | - |
| PMC2952772 | 2 | 1 | - | - |

## Folgerung

Zeilenpaarung wuerde in diesem Korpus **keine einzige Zeile**
hinzufuegen: es gibt keine Tabelle, in der beide Arme denselben
Endpunkt in getrennten Zeilen tragen. Die Funktion wird deshalb nicht
gebaut.

PMC2933606, der groesste Trial im Korpus, berichtet die
Einschaflatenz als Veraenderung im PRM-Arm plus einen direkt
berichteten Gruppenunterschied mit Konfidenzintervall
(-0,6; 95 %-KI -14,0 bis 12,7). Das ist ein direkter Effekt, kein
Arm-Deskriptivum - er gehoert in den Effektspalten-Leser, nicht in den
Arm-Rechner.
