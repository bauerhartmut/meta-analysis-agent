# Ausbeute-Funnel SOL-Korpus

Stand: 2026-11-07T21:12:16. Leser unveraendert; der Funnel zaehlt nur mit. Kein LLM, kein Netzzugriff.

## Stufen

| Stufe | Zahl |
|---|---:|
| Manifest-Eintraege | 1059 |
| XML vorhanden | 1056 |
| XML fehlend | 3 |
| SOL-RCT-Kandidaten | 946 |
| Tabellen erkannt | 2735 |
| Tabellenzeilen | 41821 |
| Saetze (Fliesstext) | 315857 |
| Kandidaten (alle Leser) | 1179 |
| gespeichert (DBs) | 1099 |
| poolbar (Zeilen, nicht Gruppen) | 422 |

## Verlust-Rangliste

| Von | Nach | Eingang | Ausgang | verloren | Anteil |
|---|---|---:|---:|---:|---:|
| dokumente | sol_kandidaten | 1056 | 946 | 110 | 10.4 % |
| zeilen | kandidaten | 41821 | 1179 | 40642 | 97.2 % |
| kandidaten | gespeichert | 1179 | 1099 | 80 | 6.8 % |
| gespeichert | poolbar | 1099 | 422 | 677 | 61.6 % |

## Groesster Verlust

**zeilen -> kandidaten**: 40642 von 41821 (97.2 %) gehen verloren.

## Leser im Detail

### effektspalten

- Eingang: 41821, Kandidatenzeilen: 537, Effekte: 1016, abgelehnt: 41284, Summe stimmt: ja
- Gates: {'tabellenrest': 41258, 'design': 26}

| Grund | Zahl |
|---|---:|
| keine Effektspalte im Kopf | 30177 |
| keine Kopfzeile | 3054 |
| Kopfzeile (4 Spalten) passt nicht zur Zeile (3 Zellen) - colspan nicht aufloesbar | 450 |
| Kopfzeile (4 Spalten) passt nicht zur Zeile (1 Zellen) - colspan nicht aufloesbar | 432 |
| Effektspalte ohne lesbares Intervall | 404 |
| Kopfzeile (3 Spalten) passt nicht zur Zeile (2 Zellen) - colspan nicht aufloesbar | 401 |
| Kopfzeile (6 Spalten) passt nicht zur Zeile (5 Zellen) - colspan nicht aufloesbar | 378 |
| Kopfzeile (5 Spalten) passt nicht zur Zeile (1 Zellen) - colspan nicht aufloesbar | 358 |
| Kopfzeile (7 Spalten) passt nicht zur Zeile (6 Zellen) - colspan nicht aufloesbar | 358 |
| Kopfzeile (9 Spalten) passt nicht zur Zeile (8 Zellen) - colspan nicht aufloesbar | 355 |
| Kopfzeile (6 Spalten) passt nicht zur Zeile (1 Zellen) - colspan nicht aufloesbar | 353 |
| Kopfzeile (3 Spalten) passt nicht zur Zeile (1 Zellen) - colspan nicht aufloesbar | 303 |

### arm_tabelle

- Eingang: 41821, Kandidatenzeilen: 161, Effekte: 161, abgelehnt: 41660, Summe stimmt: ja
- Gates: {'tabellenrest': 36768, 'sonstig': 3961, 'design': 534, 'median': 396, 'sem_se': 1}

| Grund | Zahl |
|---|---:|
| kein Mittelwert mit eindeutiger Streuung in zwei Spalten | 30591 |
| zu wenige Spalten | 3567 |
| nicht genau zwei Spalten mit Mittelwert und Streuung | 2610 |
| direkter Effekt mit OR/RR/HR - nicht Aufgabe des Arm-Rechners | 2077 |
| Fallzahl je Arm fehlt | 1884 |
| Median/IQR statt Mittelwert mit SD/SE/CI (kein SMD) | 396 |
| Baseline-Zeile (Tag 0 / vor Intervention) - kein Behandlungseffekt | 339 |
| kein Interventionsarm - Querschnitts- oder Gruppenvergleich | 195 |
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
