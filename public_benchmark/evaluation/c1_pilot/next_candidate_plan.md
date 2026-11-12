# Plan: Nächster C1-Kandidat

Stand: 2026-11-12
Status: **PLANNED - kein Modelllauf, kein Testzugriff, G5 offen**
Ausgangspunkt: v6c nicht freigegeben; Gates G1-G5 v1 bindend

## 1. Ausgangslage

| Befund | Wert |
|---|---:|
| v6c Test exakt | 992/1308 (75,8 %) |
| v6c Test vollständig exakt | 148/249 (59,4 %) |
| v6c Records mit mindestens einem Fehler | 101/249 (40,6 %) |
| G1 | bestanden |
| G2 | 217/249 = 87,1 %, nicht bestanden |
| G3 | 75,8 %; kritische Mean/SD-/Event-Felder 66,7-81,7 %, nicht bestanden |
| G4 | 148/249 = 59,4 %, nicht bestanden |
| G5 | kein unabhängiger Holdout, nicht bestanden |

Die 26 Dev-Records sind mit Qwen v6c bereits **140/140** exakt. Dev ist damit
kein Ort für eine „bessere“ Quote, sondern nur für Regressionen und
Mechanik-Tests. Der 249er-Test ist verbraucht; er darf weder zur
Prompt-Optimierung noch als unabhängiger Nachweis dienen. Die
Volltextprüfung der 33 verbleibenden `unverifiable`-Records ergab nur
**3 vollständig belegbare Records** (PMC3654355); das ist ein Smoke-Test,
kein G5-Holdout.

## 2. Ziel

Ein neuer Kandidat soll die **Record-Vollständigkeit und Feldgenauigkeit**
auf einem unabhängigen Holdout verbessern, ohne die Gates zu lockern.

Prioritäten:

1. vollständige Record-Blöcke statt einzelner geratener Felder,
2. Mean/SD und Comparator-Arm,
3. binäre Event-Zähler und Zeilennenner,
4. Zeitpunkt- und Spaltenbindung,
5. keine Halluzinationen, keine Parse-Fehler.

## 3. Nicht-Ziele

- Kein Modelllauf in dieser Planungsphase.
- Keine Prompt-Änderung auf dem 249er-Test.
- Keine Wiederverwendung des 249er-Tests als Holdout.
- Kein Training oder Tuning auf dem 3-Record-Smoke-Test.
- Keine Lockerung von G1-G5.
- Keine autonome Freigabe ohne neuen Holdout.
- Keine Änderung an `research_agent/orchestrator.py`, `report.py` oder
  `meta/pooling.py`; diese Dateien sind geschützt.

## 4. Arbeitshypothesen

Die v6c-Fehleranalyse ist deskriptiv und dient nur zur Ableitung allgemeiner
Mechanik, nicht zur Anpassung an einzelne Test-Records.

| Hypothese | Erwartete Wirkung | Messung |
|---|---|---|
| H1: Explizite Blockprüfung verhindert, dass ein Arm nur teilweise gefüllt wird | weniger Records mit fehlendem Mean/SD- oder Event-Block | Record-Vollständigkeit, Blockmuster |
| H2: Mean/SD werden gemeinsam aus derselben Zeile gelesen | weniger falsche Mean/SD-Paare | exakte Mean/SD-Felder |
| H3: Der Comparator-Arm wird symmetrisch zum Interventionsarm geprüft | weniger comparator-spezifische N-/Mean/SD-Fehler | Feldebene nach Arm |
| H4: Binäre Zeilen übernehmen N aus dem Zeilennenner | weniger falsche Event/N-Paare | Event- und N-Genauigkeit |
| H5: Spalten-/Zeitpunktprüfung vor der Zahlenextraktion reduziert Follow-up- und Baseline-Verwechslungen | höhere Record-Genauigkeit | Zeitpunkt-Audit, G4 |

Die Hypothesen sind allgemein formuliert. Keine Regel darf einen konkreten
Test-Record, Testwert oder Testtabellenausschnitt als Sonderfall enthalten.

## 5. Entwicklungsprotokoll

### 5.1 Daten

- Entwicklung ausschließlich auf den 26 Dev-Records aus 6 Artikeln.
- Keine Test- oder Holdout-Daten während der Entwicklung öffnen.
- Keine Referenzwerte in den Prompt aufnehmen.
- Neue Entwicklungsdaten nur, wenn sie artikeldisjunkt und vorab dokumentiert
  sind.

### 5.2 Experimente

- Eine Prompt-/Pipeline-Änderung pro Experiment.
- Jede Version vor dem Lauf hashen.
- Jede Version mit `run_id`, Prompt-Hash und Modellkonfiguration manifestieren.
- Ergebnisse nach Record, Feld, Arm und Fehlerblock berichten.
- Dev-Regressionen sind Abbruchkriterien, keine Schönheitsfehler.
- Wegen des Dev-Ceilings ist ein Gleichstand kein Wirksamkeitsnachweis; die
  Entscheidung fällt erst auf dem neuen Holdout.

### 5.3 Kein Testzugriff

Der 249er-Test bleibt versiegelt. Ein Testlauf ist erst zulässig, wenn:

- ein neuer Holdout nach Schema eingefroren ist,
- Input, Referenz und Manifest gehasht sind,
- Prompt und Modellkonfiguration eingefroren sind,
- genau eine Freigabe dokumentiert ist.

## 6. Messplan

Primärmetriken bleiben die Gates:

- G1: Integrität,
- G2: Anteil Records ohne fehlende Pflichtfelder,
- G3: Gesamt- und kritische Feldgenauigkeit,
- G4: Anteil vollständig exakter Records,
- G5: unabhängiger, artikeldisjunkter Holdout.

Zusätzlich deskriptiv:

- Blockvollständigkeit je Record,
- fehlende vs. falsche Blöcke,
- Mean/SD-Paargenauigkeit,
- Comparator-vs.-Intervention-Fehler,
- Event-/N-Konsistenz,
- Zeitpunkt-/Spaltenfehler,
- Latenz und Parse-Fehler.

Die Gates werden nicht nachträglich an ein Ergebnis angepasst.

## 7. Abbruchkriterien

Ein Kandidat wird nicht weiterverfolgt, wenn:

- er auf Dev Regressionen erzeugt, die nicht erklärt und behoben sind,
- er Halluzinationen oder Parse-Fehler einführt,
- er ohne dokumentierte Prompt-/Pipeline-Version läuft,
- er den Testsplit liest oder Testwerte im Prompt enthält,
- der Holdout nicht artikeldisjunkt, nicht vorab eingefroren oder nicht
  gehasht ist,
- die kritischen Felder nach dem Holdout-Lauf unter 95 % bleiben,
- die Record-Vollständigkeit unter 95 % bleibt,
- die vollständige Record-Genauigkeit unter 90 % bleibt.

## 8. Arbeitspakete

### P0 - Holdout sichern

**Vor jedem Kandidatenlauf.** Neuen externen Holdout beschaffen oder
annotieren; Artikel disjunkt zu Dev und zum verbrauchten Test; Manifest nach
[`holdout_manifest_schema.json`](holdout_manifest_schema.json) einfrieren.
Ohne P0 kein G5 und kein belastbarer Lauf.

**Konkretisierung 2026-11-12:** Quelle ist die **PMC Open Access Subset**
über die Europe PMC REST API; Ziel sind **30 Artikel** und **100 Records**.
Primärannotation und klinische Freigabe: **bauerhartmut**. Draft-Manifest:
[`holdout_manifest_p0_20261112.json`](holdout_manifest_p0_20261112.json);
Details: [`p0_external_holdout_20261112.md`](p0_external_holdout_20261112.md).
Die Query wurde ausgeführt: **596 artikeldisjunkte Kandidaten** aus dem
September-2026-Frame (0 Überschneidungen mit Yun/Freeze/Dev/Test). Das
Abstract-Screening ist als regelbasierte Erstprüfung abgeschlossen:
**152 ausgeschlossen, 65 manuell, 379 vorläufig für Volltext**. Die 379 sind
keine endgültigen Einschlüsse; das Draft-Manifest ist nicht G5-valid.

### P1 - Blockmechanik spezifizieren

Allgemeine Regeln für vollständige Mean/SD- und Event-Blöcke formulieren;
keine testrecordspezifischen Ausnahmen. Akzeptanz: Regeln sind auf Dev
anwendbar, ohne Testwissen.

### P2 - Dev-Experimente

Kleine, dokumentierte Änderungen auf Dev; jede Version mit Hashes und
Ergebnis. Kein Testsplit. Ziel ist Mechanik und Regression, nicht eine
Dev-Bestquote.

### P3 - Kandidat einfrieren

Prompt, Modellkonfiguration, Input, Referenz und Holdout-Manifest vor dem
Lauf hashen. Genau eine Freigabe dokumentieren.

### P4 - Ein Holdout-Lauf

Genau ein Lauf; danach G1-G5 mit
[`check_c1_gates.py`](../../scripts/check_c1_gates.py) prüfen. Keine
Nachbesserung nach Sicht der Ergebnisse.

## 9. Risiken

| Risiko | Wirkung | Gegenmaßnahme |
|---|---|---|
| Dev-Ceiling | 140/140 lässt keine Verbesserung erkennen | Holdout als einzige Wirksamkeitsprüfung |
| Testkontamination | neue Regeln passen nur auf bekannte Testfälle | Test versiegelt; keine Testwerte in Prompts |
| Kleine Holdout-Stichprobe | Quoten sind instabil | Artikeldisjunktheit, ausreichende Recordzahl, Unsicherheit berichten |
| 3-Record-Smoke-Test wird überinterpretiert | scheinbare Validierung ohne Aussage | ausdrücklich `smoke_test_only`; kein G5 |
| Modell-/API-Instabilität | leere Antworten wie bei GLM 5.3 | Health-Check, Parse-Fehler als hartes G1-Kriterium |
| Annotation inkonsistent | falsche Referenz | unabhängige Prüfung und Auditstatus pro Record |

## 10. Nächster konkreter Schritt

**P0 zuerst:** externen Holdout beschaffen und nach Schema einfrieren. Erst
danach P1/P2 starten. In dieser Phase:

- kein Modelllauf,
- keine Prompt-Änderung,
- keine Testwiederverwendung,
- keine Gate-Lockerung.

## 11. Referenzen

- [Gates v1](c1_acceptance_gates_v1.md)
- [Entscheidung v6c](decision_v6c.md)
- [Test-Fehleranalyse](runs_test/c1_test_20261111_v6c/test_error_analysis.md)
- [Holdout-Plan](holdout_plan_20261112.md)
- [Holdout-Manifest-Schema](holdout_manifest_schema.json)
- [Gate-Checker](../../scripts/check_c1_gates.py)
- [Assistierte Nutzung](assisted_use_sop.md)

**Kein Modelllauf. Keine Prompt-Änderung. Keine Test-Wiederverwendung.**
