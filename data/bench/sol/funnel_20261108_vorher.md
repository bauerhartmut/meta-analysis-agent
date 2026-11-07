# Ausbeute-Funnel SOL-Korpus

Stand: 2026-11-07T19:46:49. Leser unveraendert; der Funnel zaehlt nur mit. Kein LLM, kein Netzzugriff.

## Stufen

| Stufe | Zahl |
|---|---:|
| Manifest-Eintraege | 1059 |
| XML vorhanden | 1056 |
| XML fehlend | 3 |
| SOL-RCT-Kandidaten | 946 |
| Tabellen erkannt | 2735 |
| Tabellenzeilen | 42771 |
| Saetze (Fliesstext) | 315857 |
| Kandidaten (alle Leser) | 539 |
| gespeichert (DBs) | 523 |
| poolbar (Zeilen, nicht Gruppen) | 152 |

## Verlust-Rangliste

| Von | Nach | Eingang | Ausgang | verloren | Anteil |
|---|---|---:|---:|---:|---:|
| dokumente | sol_kandidaten | 1056 | 946 | 110 | 10.4 % |
| zeilen | kandidaten | 42771 | 539 | 42232 | 98.7 % |
| kandidaten | gespeichert | 539 | 523 | 16 | 3.0 % |
| gespeichert | poolbar | 523 | 152 | 371 | 70.9 % |

## Groesster Verlust

**zeilen -> kandidaten**: 42232 von 42771 (98.7 %) gehen verloren.

## Leser im Detail

### effektspalten

- Eingang: 42771, Kandidatenzeilen: 260, Effekte: 529, abgelehnt: 42511, Summe stimmt: ja
- Gates: {'tabellenrest': 42485, 'design': 26}

| Grund | Zahl |
|---|---:|
| keine Effektspalte im Kopf | 29184 |
| keine Kopfzeile | 5448 |
| Kopfzeile (4 Spalten) passt nicht zur Zeile (1 Zellen) - colspan nicht aufloesbar | 418 |
| Kopfzeile (4 Spalten) passt nicht zur Zeile (3 Zellen) - colspan nicht aufloesbar | 411 |
| Kopfzeile (9 Spalten) passt nicht zur Zeile (8 Zellen) - colspan nicht aufloesbar | 387 |
| Kopfzeile (6 Spalten) passt nicht zur Zeile (5 Zellen) - colspan nicht aufloesbar | 383 |
| Kopfzeile (3 Spalten) passt nicht zur Zeile (2 Zellen) - colspan nicht aufloesbar | 379 |
| Kopfzeile (5 Spalten) passt nicht zur Zeile (1 Zellen) - colspan nicht aufloesbar | 329 |
| Kopfzeile (7 Spalten) passt nicht zur Zeile (6 Zellen) - colspan nicht aufloesbar | 313 |
| Kopfzeile (6 Spalten) passt nicht zur Zeile (1 Zellen) - colspan nicht aufloesbar | 309 |
| Kopfzeile (5 Spalten) passt nicht zur Zeile (4 Zellen) - colspan nicht aufloesbar | 298 |
| Kopfzeile (7 Spalten) passt nicht zur Zeile (1 Zellen) - colspan nicht aufloesbar | 275 |

### arm_tabelle

- Eingang: 42771, Kandidatenzeilen: 8, Effekte: 8, abgelehnt: 42763, Summe stimmt: ja
- Gates: {'tabellenrest': 38564, 'sonstig': 3432, 'design': 399, 'median': 367, 'sem_se': 1}

| Grund | Zahl |
|---|---:|
| kein Mittelwert mit eindeutiger Streuung in zwei Spalten | 32774 |
| zu wenige Spalten | 3603 |
| nicht genau zwei Spalten mit Mittelwert und Streuung | 2187 |
| Fallzahl je Arm fehlt | 1952 |
| direkter Effekt mit OR/RR/HR - nicht Aufgabe des Arm-Rechners | 1480 |
| Baseline-Zeile (Tag 0 / vor Intervention) - kein Behandlungseffekt | 370 |
| Median/IQR statt Mittelwert mit SD/SE/CI (kein SMD) | 367 |
| kein Interventionsarm - Querschnitts- oder Gruppenvergleich | 29 |
| Streuung nicht eindeutig (SD/SE/CI) | 1 |

### arm_text

- Eingang: 315857, Kandidatenzeilen: 1, Effekte: 1, abgelehnt: 315856, Summe stimmt: ja
- Gates: {'sonstig': 243680, 'tabellenrest': 46010, 'design': 23281, 'sem_se': 1747, 'median': 1138}

| Grund | Zahl |
|---|---:|
| kein Mittelwert mit Streuung im Satz | 242564 |
| Tabellen-/Zitationsrest statt Ergebnissatz | 46010 |
| Baseline-/Veraenderungsmuster statt Gruppenvergleich | 20185 |
| Stichproben- oder Designbeschreibung statt Ergebnis | 3095 |
| Streuung als SEM/SE im Satz (nicht SD) | 1747 |
| Median/IQR statt Mittelwert mit SD | 1138 |
| nicht genau zwei Mittelwerte mit Streuung im Satz | 711 |
| Fallzahl je Arm fehlt | 403 |
| Arm-Etikett fehlt | 2 |
| kein Interventionsarm - Gruppenvergleich ohne Intervention | 1 |

### change

- Eingang: 315857, Kandidatenzeilen: 1, Effekte: 1, abgelehnt: 315856, Summe stimmt: ja
- Gates: {'sonstig': 259478, 'tabellenrest': 50336, 'design': 3340, 'sem_se': 1763, 'median': 939}

| Grund | Zahl |
|---|---:|
| kein Veraenderungswert im Satz | 220850 |
| Tabellen-/Zitationsrest statt Ergebnissatz | 50336 |
| nicht genau zwei Arme mit Veraenderung im Satz | 38393 |
| Stichproben- oder Designbeschreibung statt Ergebnis | 3340 |
| Streuung als SEM/SE im Satz (nicht SD) | 1763 |
| Median/IQR statt Mittelwert mit SD | 939 |
| Fallzahl je Arm fehlt | 235 |

## Offen

- Die Obergrenze (Dokumente mit einem tatsaechlich poolbaren SOL-Effekt) ist nicht gemessen; sie braucht menschliche Sichtung der SOL-Kandidaten.
- Stufe 'gespeichert' stammt aus den Mess-DBs, nicht aus diesem Lauf; ohne --*-db bleibt sie 0.
