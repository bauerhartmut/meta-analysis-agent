# C1-Volltextprüfung der 33 unverifizierten Records

Stand: 2026-11-12
Status: **ABGESCHLOSSEN - 3/33 vollständig belegbar, 4/33 teilweise, 26/33 nicht belegbar**
Entscheidung: **3-Record-Smoke-Test möglich; kein belastbarer G5-Holdout**

## 1. Ziel und Umfang

Geprüft wurden die **33 `unverifiable`-Records aus 9 Artikeln**, die außerhalb des eingefrorenen 275er-Bestands liegen. Für jeden Record wurde untersucht, ob die in `missing_fields` genannten Werte in den verfügbaren Volltexten und XML-Tabellen exakt belegbar sind.

Quellen:

- Evidence-Inference-Plaintext: `public_benchmark/raw_data/evidence_inference/annotations/txt_files/PMC<ID>.txt`
- Yun-Abstract-/Results-XML mit `table-wrap`-Blöcken: `public_benchmark/raw_data/yun_llm_meta_analysis/evaluation/data/abstract_and_results_xml_files/PMC<ID>.xml`
- Audit und Missing-Felder: `public_benchmark/validation/yun_audit_410.jsonl`

## 2. Methode

1. Die 33 Records wurden über `audit_status=unverifiable` und `pmcid` außerhalb des Freeze bestimmt.
2. Für jedes fehlende Feld wurde der Referenzwert als Zahlvariante gesucht; Unicode-Minuszeichen wurden normalisiert.
3. Ein Treffer zählt nur, wenn die umgebende Tabellenzeile den richtigen Arm und das richtige Outcome nennt. Bloße Ziffernfolgen, Literaturzitate oder andere Outcomes zählen nicht.
4. Es gab keine Schätzung, keine Umrechnung von CI/SE in SD und keine Zusammenführung getrennter Arme.
5. Zusätzlich wurden die `table-wrap`-Blöcke der XML-Dateien gegen die Plaintext-Dateien abgeglichen, weil mehrere Plaintext-Dateien nur Tabellenüberschriften enthalten.

## 3. Ergebnis

| Status | Records | Bedeutung |
|---|---:|---|
| `fully_recoverable` | **3** | Alle fehlenden Felder exakt belegt; Record vollständig |
| `partially_recoverable` | **4** | Ein Teil der fehlenden Felder exakt belegt; Record bleibt unvollständig |
| `not_recoverable` | **26** | Kein fehlendes Feld belegbar |
| **Gesamt** | **33** | 69 fehlende Felder: **13 belegt, 56 nicht belegt** |

### 3.1 Vollständig belegbar: 3 Records aus PMC3654355

| Record | Outcome | Fehlende Felder | Beleg |
|---:|---|---|---|
| 274 | Body weight | Intervention-Mean, Comparator-Mean | Tabelle 2, Zeile `Body weight (kg)`; Means und SDs exakt |
| 275 | Fat mass | Intervention-Mean, Comparator-Mean | Tabelle 2, Zeile `Fat mass (kg)`; Means und SDs exakt |
| 276 | Visceral fat | Intervention-Mean | Tabelle 2, Zeile `Visceral fat area (cm2)`; Mean, SDs und Comparator-Mean exakt |

Diese drei Records sind artikeldisjunkt zum Freeze und wären als **3-Record-Smoke-Test** technisch verwendbar.

### 3.2 Teilweise belegbar: 4 Records aus PMC3136370

| Record | Outcome | Belegt | Nicht belegt |
|---:|---|---|---|
| 556 | FIQ | Intervention-Mean, Comparator-Mean | beide SDs |
| 557 | FIQ | Intervention-Mean, Comparator-Mean | beide SDs |
| 558 | CES-D | Intervention-Mean, Comparator-Mean | beide SDs |
| 559 | CES-D | Intervention-Mean, Comparator-Mean | beide SDs |

Die Mittelwerte stehen in der Per-Protocol-Analyse von Tabelle 1; die zugehörigen SDs sind weder in der Tabelle noch im Text berichtet. Die Records bleiben unvollständig und sind keine Holdout-Records.

### 3.3 Nicht belegbar: 26 Records

| Artikel | Records | Hauptgrund |
|---|---:|---|
| PMC4319071 | 6 | Tabelle 2 berichtet Mean (SE), nicht SD; keine fehlenden SDs belegbar |
| PMC5056957 | 6 | Tabelle 2 berichtet Differenzen/95%-CI, keine Arm-SDs |
| PMC5380326 | 5 | Mean (SE)/Delta, keine SDs; `551` ist nur Teil von `6,551.06` |
| PMC4357072 | 4 | Nur Tabellenüberschriften, keine Zeilen; keine Means/SDs/Events |
| PMC1574360 | 2 | Nur Tabellenüberschriften; Effekte als Differenz/CI, keine SDs |
| PMC5079604 | 2 | Getrennte Arme 17/16/15; kombinierte 33er-Gruppe nicht direkt berichtet |
| PMC2363753 | 1 | Kein `table-wrap`; nur Abstract/Results, keine Gruppengrößen |
| **Gesamt** | **26** | |

### 3.4 Record-Übersicht (alle 33)

| Record | PMC | Fehlende Felder | Status | Kurzbefund |
|---:|---|---|---|---|
| 6 | 1574360 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 7 | 1574360 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 10 | 2363753 | intervention_group_size, comparator_group_size | `not_recoverable` | fehlende Werte nicht belegt |
| 110 | 4319071 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 111 | 4319071 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 112 | 4319071 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 113 | 4319071 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 114 | 4319071 | intervention_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 115 | 4319071 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 158 | 5056957 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 159 | 5056957 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 160 | 5056957 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 161 | 5056957 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 162 | 5056957 | intervention_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 163 | 5056957 | intervention_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 173 | 5079604 | intervention_group_size | `not_recoverable` | kombinierte 33er-Gruppe nicht direkt berichtet |
| 174 | 5079604 | intervention_group_size | `not_recoverable` | kombinierte 33er-Gruppe nicht direkt berichtet |
| 202 | 5380326 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | 551 nur Teil von 6,551.06 |
| 203 | 5380326 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 205 | 5380326 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 206 | 5380326 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 207 | 5380326 | intervention_standard_deviation, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 274 | 3654355 | intervention_mean, comparator_mean | `fully_recoverable` | Tabelle 2, Body weight |
| 275 | 3654355 | intervention_mean, comparator_mean | `fully_recoverable` | Tabelle 2, Fat mass |
| 276 | 3654355 | intervention_mean | `fully_recoverable` | Tabelle 2, Visceral fat area |
| 302 | 4357072 | intervention_mean, intervention_standard_deviation, comparator_mean, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 303 | 4357072 | intervention_standard_deviation, comparator_mean, comparator_standard_deviation | `not_recoverable` | fehlende Werte nicht belegt |
| 304 | 4357072 | intervention_events | `not_recoverable` | kein Event-Wert; 14 ist Literaturstelle |
| 305 | 4357072 | comparator_events | `not_recoverable` | kein Event-Wert; 5 ist Literaturstelle/Baseline |
| 556 | 3136370 | intervention_mean, intervention_standard_deviation, comparator_mean, comparator_standard_deviation | `partially_recoverable` | Means belegt; SDs fehlen |
| 557 | 3136370 | intervention_mean, intervention_standard_deviation, comparator_mean, comparator_standard_deviation | `partially_recoverable` | Means belegt; SDs fehlen |
| 558 | 3136370 | intervention_mean, intervention_standard_deviation, comparator_mean, comparator_standard_deviation | `partially_recoverable` | Means belegt; SDs fehlen |
| 559 | 3136370 | intervention_mean, intervention_standard_deviation, comparator_mean, comparator_standard_deviation | `partially_recoverable` | Means belegt; SDs fehlen |

Die vollständigen Quellenangaben und Begründungen pro Record stehen in der JSON-Datei.

## 4. Kann daraus ein Holdout werden?

**Ein 3-Record-Smoke-Test ja, ein belastbarer G5-Holdout nein.**

- Der einzige vollständig belegbare Kandidat umfasst **3 Records aus einem Artikel** (PMC3654355), alle kontinuierlich, drei verschiedene Outcomes.
- Es gibt **keine binären Records** und **keine Artikelstreuung**; ein einzelner Fehler verschiebt jede Quote um 33 Prozentpunkte.
- Damit sind G2 (Record-Vollständigkeit), G3 (Feldgenauigkeit) und G4 (Record-Genauigkeit) nicht sinnvoll prüfbar. Ein formales G5-Manifest wäre technisch baubar, würde aber keinen belastbaren Nachweis liefern.
- Die vier teilweise belegbaren Records aus PMC3136370 haben weiterhin fehlende SDs; sie dürfen nicht durch Imputation oder CI-Umrechnung ergänzt werden.
- Die 26 übrigen Records bleiben `unverifiable`; die vorhandenen Volltexte belegen die fehlenden Werte nicht.

## 5. Entscheidung und Empfehlung

1. **Keinen G5-Holdout aus diesen 33 Records einfrieren.**
2. **Keinen Modelllauf** auf dem 3-Record-Kandidaten; er ist höchstens ein technischer Smoke-Test.
3. **Keine Wiederverwendung** des 249er-Tests und keine Prompt-Änderung.
4. **Externen Holdout beschaffen:** neue, artikeldisjunkte Artikel außerhalb der Yun-699 und außerhalb des Freeze annotieren und vor dem Lauf hashen.
5. Falls kurzfristig ein Smoke-Test benötigt wird: Records 274–276 aus PMC3654355 mit Tabelle 2 als Referenz verwenden, ausdrücklich als `smoke_test_only` kennzeichnen und nicht als G5-Nachweis zählen.

## 6. Artefakte

- JSON: [`holdout_fulltext_audit_20261112.json`](holdout_fulltext_audit_20261112.json)
- Holdout-Plan: [`holdout_plan_20261112.md`](holdout_plan_20261112.md)
- Gates: [`c1_acceptance_gates_v1.md`](c1_acceptance_gates_v1.md)
- Audit: [`../../validation/yun_audit_410.jsonl`](../../validation/yun_audit_410.jsonl)

**Kein Modelllauf. Keine Prompt-Änderung. Keine Test-Wiederverwendung.**
