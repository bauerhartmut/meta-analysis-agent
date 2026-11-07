# Schätzer-Prüfung der SOL-Zeilen (Stand 08.11.2026)

Frage: Lassen sich die drei Mitteldifferenzen in Minuten (`jsr.70311` 3,8 ·
`zsae250` −4,2 · `zsaa194` −5,1) zu einer k=3-Gruppe zusammenlegen?

Grundlage: `data/bench/sol/direct_design.db` (838 gespeicherte Effektzeilen,
davon 11 SOL aus 5 Quellen), Tabellenleinträge aus `data/bench/sol/xml/`.
Read-only, kein Netz, kein Modell.

**Ergebnis: nein.** Die drei Zeilen sind keine drei Studien zu einer Frage,
und eine davon war falsch gespeichert.

## 1. Was tatsächlich in den elf Zeilen steht

| Quelle | Zeilen | Schätzer | Zeitpunkt / Design |
|---|---:|---|---|
| 10.1111/jsr.70311 | 4 | adjustierte Gruppendifferenz, 6 Monate | RCT, n = 112, **ein** Trial: ITT 3,8 (−3,5 bis 11,1) · Subgruppe „poor sleepers at baseline" 3,4 (−15,2 bis 22,0) · Per protocol I 5,7 (−3,3 bis 14,7) · Per protocol II 4,6 (−6,7 bis 16,0) |
| 10.1093/sleep/zsae250 | 3 | „Main effect of trial", Differenz der Change-Scores | Crossover, 18 Personen / 72 Beobachtungen, **ein** Trial: Vergleich 1 (Nacht 3 − Nacht 1) −4,2 (−14,6 bis 6,2) · Vergleich 2 (Nacht 5 − Nacht 1) −2,3 (−10,1 bis 5,5) · Vergleich 3 (Mittel post − Baseline) 1,3 (−6,2 bis 8,8) |
| 10.1093/sleep/zsaa194 | 1 | Differenz Blue-depleted vs. Standard-Licht | PSG im Schlaflabor, **eine** Stichprobe: −1,7 (−5,1 bis 1,7) |
| 10.2188/jea.jear20140201 | 2 | Differenz CS vs. kein CS, **log min** | Beobachtungsstudie, 174 vs. 863: altersadjustiert −0,1 (−0,2 bis 0,1) · voll adjustiert −0,002 (−0,2 bis 0,2) |
| 10.1001/jamanetworkopen.2026.26983 | 1 | Hedges g | 342 gematchte Paare: 0,07 (−0,04 bis 0,17) |

Damit gilt:

* **Abhängigkeit:** 4 Zeilen aus `jsr.70311` und 3 aus `zsae250` sind
  Analysen desselben Trials (ITT/Subgruppe/Per protocol bzw. drei
  Vergleichsfenster). Für ein Pooling zählt je Studie **eine** Zeile.
  Unabhängige Studien im SOL-Set: **5**, nicht 11.
* **Skalen:** nur 3 der 5 Quellen berichten Minuten (`jsr.70311`,
  `zsae250`, `zsaa194`); `jea` berichtet log-Minuten, `jamanetworkopen`
  Hedges g. Rohminuten und log-Minuten sind nicht ohne Umrechnung mischbar.
* **Interventionen:** Bewegungs-RCT bei Herzpatienten, Bewegungs-Crossover
  bei 18 Personen, Blaulichtfilter-Brille im Schlaflabor. Eine gemeinsame
  Differenz dieser drei wäre keine Antwort auf eine Frage — und schon gar
  keine zu Melatonin.
* **Melatonin:** im Set ist genau **eine** SOL-Zeile, `jamanetworkopen`
  (g = 0,07). k = 1.

## 2. Der gefundene Fehler: CI-Grenze als Punktschätzer

`zsaa194` speicherte −5,1 min mit CI −5,1 bis 1,7. In Tabelle 2 stehen
Punktwert und Intervall in **zwei** Spalten („Difference Estimate" /
„Difference 95% CI"); gespeichert wurde die erste Zahl der CI-Zelle, also
die untere Grenze. Der richtige Wert: **−1,7 min (−5,1 bis 1,7)**, SE 1,73
(aus der Intervallbreite, unverändert korrekt).

Ursache in `research_agent/meta/effect_columns.py`: `parse_effect_cell`
las die erste Zahl der Zelle als Punktwert, ohne zu prüfen, ob sie außerhalb
des Intervalls steht. Eine reine Intervallzelle hat keinen Punktwert.

Behoben durch zwei Änderungen:

1. `parse_effect_cell` verwirft Zellen, deren einzige Zahlen das Intervall
   sind (`ci_only_range`).
2. Steht links daneben eine Punktspalte mit Effektwort im Kopf
   („Difference Estimate"), wird sie gepaart — nur wenn ihr Wert im
   Intervall liegt und sie selbst kein Intervall führt. Arm-Statistiken
   („Mean (SD)") sind damit ausgeschlossen.

## 3. Wirkung auf den Korpus

Neuaufbau mit dem Fix (`direct_paired.db`, dann nach `direct_design.db`
übernommen), gleiches Manifest und gleiche Gates:

| | vorher | nachher |
|---|---:|---:|
| gespeicherte Zeilen | 838 | 838 |
| SOL-Zeilen / Quellen | 11 / 5 | 11 / 5 |
| Zeilen mit korrigiertem Wert | — | **37** |
| neu gespeichert / entfallen | — | 0 / 0 |

Die 37 Korrekturen betreffen ausschließlich Zellen, in denen die CI-Grenze
als Schätzer gelesen wurde (u. a. alle 9 PSG-Zeilen aus `zsaa194`,
`10.2196/12686` −8,9 → −6,84). Die Ausbeute ändert sich nicht; die
Genauigkeit schon. Tests: `research_agent/tests/test_effect_columns.py`,
6 neue Fälle, 54 Tests der berührten Dateien grün.

## 4. Entscheidung

* **Keine k=3-Gruppe.** Die drei Minutenzeilen gehören zu drei
  Interventionen und zwei Designs (between/within). Ein gepoolter Effekt
  wäre nicht interpretierbar.
* **Melatonin-SOL bleibt k=1** (g = 0,07, 342 Paare). Kein gepoolter
  Schätzer, keine Heterogenität, kein funnel plot.
* **Vor jedem späteren Pooling:** Regel „eine Zeile je Studie" mit
  Vorrang für die Hauptanalyse (ITT vor Per protocol, Vorher-nachher-Kontrast
  vor Einzelvergleichen). Ohne sie zählt `jsr.70311` vierfach und
  `zsae250` dreifach.

## 5. Nachweise

* Code: `research_agent/meta/effect_columns.py` (`effect_word`,
  `ci_only_range`, `_paired_point`), Tests in
  `research_agent/tests/test_effect_columns.py`.
* Messung: `scripts/read_effect_columns_xml6.py` mit
  `--manifest data/bench/sol/manifest_all.json`; Ausgabe
  `data/bench/sol/effect_columns_paired_20261108.{json,md}`.
* Tabellen: Tabelle 3 (`jsr.70311`), Tabelle 2 (`zsae250`), Tabelle 2
  (`zsaa194`), Tabelle 2 (`jea`), Tabelle 3 (`jamanetworkopen`) aus
  `data/bench/sol/xml/`.
