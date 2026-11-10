# Kalibrierungsphase: 12 Dokumente (2026-11-10)

Die 12 Kalibrierungsdokumente sind die **erste Arbeitsmenge** der
Vollannotation, kein separater Kappa-Lauf. A und B annotieren
getrennt; kein Austausch und keine Zwischenabgabe. Die Abgabe und der
Zeilen-Kappa folgen nach allen 30 Dokumenten.

## Reihenfolge

1. Die 12 Dokumente in der Tabellenreihenfolge.
2. Danach die 18 Ergänzungen; die fünf Negativkontrollen zuletzt.
3. Keine Zwischenabgabe: Die Dateien bleiben bis zur Gesamtabgabe
   offen; ein Zwischenvergleich würde die Blindheit brechen.

## Dokumente

| Dokument | Schicht | Design | Zeichen | Tabellen | Effektstellen | Punkt |
|---|---|---|---|---|---|---|
| [7111ea9787](vollannotation_arbeitsblatt_7111ea9787.md) | cohort | aggregate | 97,367 | 4 | 30 | 5.8 |
| [3134fdc8c3](vollannotation_arbeitsblatt_3134fdc8c3.md) | cohort | observational | 85,910 | 9 | 14 | 5.1 |
| [d0bec407a2](vollannotation_arbeitsblatt_d0bec407a2.md) | cohort | observational | 3,199 | 0 | 4 | 5.1 |
| [bb9218735f](vollannotation_arbeitsblatt_bb9218735f.md) | rct | parallel_rct | 71,085 | 14 | 0 | 5.7 |
| [fb484d488b](vollannotation_arbeitsblatt_fb484d488b.md) | rct | aggregate | 9,659 | 0 | 6 | 5.8 gepoolt |
| [3bbb142c71](vollannotation_arbeitsblatt_3bbb142c71.md) | crossover | crossover_rct | 40,445 | 2 | 0 | 5.1 |
| [87079ba88a](vollannotation_arbeitsblatt_87079ba88a.md) | crossover | crossover_rct | 38,131 | 6 | 1 | 5.1 |
| [2c7ab4d124](vollannotation_arbeitsblatt_2c7ab4d124.md) | cross_sectional | observational | 39,970 | 7 | 19 | 5.1 |
| [09843d40d3](vollannotation_arbeitsblatt_09843d40d3.md) | cohort | observational | 65,491 | 7 | 0 | 5.1 |
| [334f5f6798](vollannotation_arbeitsblatt_334f5f6798.md) | aggregate | aggregate | 79,745 | 6 | 1 | 5.1 |
| [203c831dbe](vollannotation_arbeitsblatt_203c831dbe.md) | aggregate | aggregate | 114,459 | 11 | 27 | 5.8 gepoolt |
| [2675c25aab](vollannotation_arbeitsblatt_2675c25aab.md) | cross_sectional | observational | 55,267 | 13 | 0 | 5.1 |

Summe: 12 Dokumente, 79 Tabellenstellen, 102 Effektstellen.

### Schichten

| Schicht | Dokumente |
|---|---|
| cohort | 4 |
| rct | 2 |
| crossover | 2 |
| cross_sectional | 2 |
| aggregate | 2 |

## Prüfpunkte

- **5.8:** 5.8: narrativer Ueberblick ohne eigenen gepoolten Schaetzer; keine Zeile, `no_effect_reason`.
- **5.1:** 5.1: Design am Volltext; nur Effekte mit Unsicherheit; Quote exakt.
- **5.7:** 5.7: p-Wert ohne Effektgroesse ist keine Zeile; Mittelwerte +/- SD pruefen.
- **5.8 gepoolt:** 5.8: gepoolte Schaetzer als je eine Zeile mit `is_primary: false`; Dosis-Wirkungs-Peak und Sensitivitaetsanalyse in `notes`.

## Ablauf

1. Arbeitsblatt und Volltext vollständig lesen.
2. Jede Effektzeile mit Quote und Unsicherheit erfassen; Dokument
   abschließen (Zeilen oder `no_effect_reason`).
3. `.venv/bin/python.exe scripts/pruefe_goldstandard.py --entwurf data/golden_effects/goldstandard_A.json` (bzw. B) bis 0 Fehler.
4. Nach den 12 weiter mit den 18 Ergänzungen; keine Zwischenabgabe.
5. Nach allen 30: Abgabe, Hashes eintragen, Kappa mit
   `werte_kappa_probe.py` (ohne `--probelauf`).

## Stand (Start)

- A: 26 Zeilen, 0 Begründungen, 10 offen (von 12).
- B: 0 Zeilen, 0 Begründungen, 12 offen (von 12).
- Hash A: `b31f06e7a7fefd58c663bb046ee30435e43d1a048bffe5006b295dea455a0672`
- Hash B: `2030d8a186ab19f242aefc854bc2a1c350bb97f9d1067a6b8b7da5b38daed0bc`
