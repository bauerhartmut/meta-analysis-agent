# Konverterlauf mit den neuen Kopfzeilen (2026-11-08)

Frage: Wie viele der Kandidaten aus dem Kopf-Fix ueberleben Zitat-Gate,
Standardfehler-Herleitung und Plausibilitaetspruefung?

## Ergebnis

| Leser | Kandidaten (Funnel) | Kandidaten (Konverter) | gespeichert | verworfen |
|---|---:|---:|---:|---:|
| Effektspalten | 1.016 | 1006 | 1000 | 6 |
| Arm-Tabelle | 97 | 97 | 97 | 0 |
| Fliesstext (bestehende DB) | 1 | - | 1 | 0 |
| Veraenderung (bestehende DB) | 1 | - | 1 | 0 |
| **Summe** | **1.115** | 1.103 | **1.099** | 6 |

Der Unterschied 1.016 zu 1.006 Kandidaten kommt vom Konverter: er
ueberspringt 19 Modelltabellen (366 Zeilen), in denen eine Intercept-Zeile
beweist, dass die uebrigen Zeilen Praediktoren und keine Behandlungseffekte
sind. Der Funnel zaehlt diese Zeilen mit.

## Funnel-Stufen nach dem Lauf

| Stufe | vor dem Kopf-Fix | nach Konverterlauf |
|---|---:|---:|
| gespeichert | 523 | 1.099 |
| poolbar (Zeilen) | 152 | 422 |

## Was die 576 neuen Zeilen sind - und was nicht

- Effektspalten: 1000 Zeilen, 323 poolbar, Typen: or 393, mean_diff 289, beta 270, smd 19, g 15, rr 12, hr 2
- Arm-Tabellen: 97 Zeilen, 97 poolbar, Typen: g 97
- vorher (Effektspalten): 513 Zeilen, 142 poolbar, Typen: beta 197, or 160, mean_diff 112, g 15, smd 15, rr 12, hr 2
- vorher (Arm-Tabellen): 8 Zeilen, 8 poolbar, Typen: g 8

Die neuen Zeilen sind bisher ungelesene Tabellenzeilen, kein neues
Ergebnis. Poolbar sind davon nur die standardisierten Familien g, SMD und
Mitteldifferenz; OR (393), beta (270), RR (12) und HR (2) sind es nicht -
das ist eine Eigenschaft der Effektart, kein Fehler.

## Verlust im Speicher-Gate

Gesamt: 6 Zeilen.
Gruende der 6 verworfenen Zeilen:
-   6  unbekannter Effekttyp 'irr'


## Grenzen

- Alle Zahlen stammen aus den beiden JSON-Berichten und den beiden neuen
  Mess-DBs (`data/bench/sol/direct_kopf.db`, `arm_kopf.db`), nachrechenbar
  mit `scripts/funnel_sol.py --direct-db ... --arm-db ...`.
- 3 XML fehlen weiterhin (HTTP 500 bei der Beschaffung).
- Die Zeilen sind gespeichert, aber nicht gegen Zielmasse geschnitten;
  die Frage "wie viele betreffen Einschlaflatenz" ist damit nicht beantwortet.
