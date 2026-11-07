# SOL-Korpus auf 1067 Treffer erweitert: erstmals echte k >= 2?

Stand: 07.11.2026. Dieselbe Europe-PMC-Query, jetzt ueber alle Seiten
(`cursorMark`). Kein LLM, keine Zyklen; beide Leser deterministisch.

## Suche und Download

| Kennzahl | Wert |
|---|---:|
| Treffer (hitCount) | 1068 |
| zurueckgeliefert | 1067 |
| mit PMCID | 1059 |
| Crossref-Ueberlappung | 3 |
| XML geladen (neu) | 298 |
| XML bereits vorhanden | 758 |
| Download-Fehler | 3 |
| Manifest-Eintraege | 1059 |

## Effektspalten-Leser

| Kennzahl | Wert |
|---|---:|
| Tabellenzeilen | 42396 |
| gespeicherte Effekte | 513 |
| Modelltabellen uebersprungen | 19 |
| Pooling-Gruppen | 154 |
| **Gruppen mit k >= 2** | **0** |

## Arm-Rechner

| Kennzahl | Wert |
|---|---:|
| Tabellenzeilen | 42771 |
| umrechenbar | 8 |
| gespeichert | 8 |
| Pooling-Gruppen | 8 |
| **Gruppen mit k >= 2** | **0** |

## Fazit

Auch der erweiterte Korpus liefert **keine** Gruppe mit k >= 2.

Vergleich zum 100-Dokument-Lauf: dort 15 Effektspalten-Zeilen (alle
k = 1) und 3 Arm-Zeilen nach dem Design-Gate (alle k = 1).

## Grenzen

* Europe PMC liefert 1067 der 1068 Treffer; ein Datensatz fehlt in der
  Blaetterung.
* Nur Dokumente mit PMCID und verfuegbarem `fullTextXML` sind im
  Korpus; die Download-Fehler stehen oben.
* k >= 2 heisst hier 'zwei unabhaengige Studien mit nutzbarer
  Praezision in derselben Gruppe' - die Design-Gates des Arm-Rechners
  sind aktiv, ersetzen aber keine Risk-of-Bias-Bewertung.

