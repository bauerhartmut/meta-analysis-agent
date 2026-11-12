# Abschlussbericht 2026-11-11 und Aufgaben für 2026-11-12

Stand: 2026-11-11, Tagesabschluss
Status: **C1-Testlauf abgeschlossen; Option C entschieden; Gates v1 aktiv**
Nächster Arbeitstag: **2026-11-12**

**Nachtrag 2026-11-12:** Der Holdout-Plan ist geprüft. Aus den vorhandenen
C1-Daten ist **kein belastbarer unabhängiger Holdout** verfügbar; alle 275
nutzbaren Records sind vergeben. Die neun Volltexte/XML-Tabellen der 33
`unverifiable`-Records wurden geprüft: **3 vollständig belegbar**
(PMC3654355), **4 teilweise** (PMC3136370, SDs fehlen), **26 nicht belegbar**.
Der einzige vollständige Kandidat ist ein **3-Record-Smoke-Test**, kein
G5-Holdout. Details:
[`holdout_fulltext_audit_20261112.md`](holdout_fulltext_audit_20261112.md)
und [`holdout_plan_20261112.md`](holdout_plan_20261112.md). Es gab keinen
Modelllauf.

## 1. Status zum Tagesabschluss

- Der freigegebene C1-Testlauf `c1_test_20261111_v6c` ist vollständig
  ausgewertet.
- **v6c wird nicht für eine autonome oder ungeprüfte Meta-Analyse
  freigegeben.**
- **Option C ist angenommen:** neuer Kandidat auf unabhängigen Daten.
- Die **Gates G1–G5 v1** sind als Projektstandard festgelegt.
- Der **249er-Test ist verbraucht** und darf nicht zur Entwicklung des
  nächsten Kandidaten wiederverwendet werden.
- Es läuft **kein C1-Testprozess**.
- Der bestehende **B-Watcher** läuft weiter und wartet auf
  `data/golden_effects/goldstandard_B_ruecklauf.json`; er wurde nicht
  verändert.
- Alle C1-Artefakte sind committed und nach `origin/master` gepusht.
  Unrelated Worktree-Änderungen wurden nicht angefasst.

## 2. Aktuelles Testergebnis

| Kennzahl | Wert |
|---|---:|
| Records | 249/249 |
| erwartete Felder | 1.308 |
| abgedeckt | 1.168/1.308 (89,3 %) |
| exakt | **992/1.308 (75,8 %)** |
| fehlend | 140 |
| falsch | 176 |
| halluziniert | 0 |
| vollständig exakte Records | **148/249 (59,4 %)** |
| Records mit mindestens einem Fehler | 101/249 (40,6 %) |
| MAE | 1,5305 |
| Parse-/Schemafehler | 0 |
| Null-Disziplin | 684/684 (100 %) |

### Nach Outcome-Typ

| Typ | Records | exakt | vollständig exakt |
|---|---:|---:|---:|
| continuous | 156 | 678/936 (72,4 %) | 79/156 |
| binary | 93 | 314/372 (84,4 %) | 69/93 |

### Fehlerbild

- **32 Records** nur fehlend, **69 Records** nur falsch, **0** mit beidem.
- **18 Records** haben kein exaktes Feld.
- Größte Blöcke: 23 kontinuierliche Records mit allen vier Mean/SD-Feldern
  falsch; 11 Records mit beiden Mean/SD-Armen fehlend; bei binären Records
  7 mit allen vier Feldern fehlend und 7 mit beiden Event-Feldern falsch.
- Kein durchgängiger Richtungsbias; 0 Halluzinationen und 0 Parse-Fehler.

Details: [`runs_test/c1_test_20261111_v6c/test_result.md`](runs_test/c1_test_20261111_v6c/test_result.md)
und [`runs_test/c1_test_20261111_v6c/test_error_analysis.md`](runs_test/c1_test_20261111_v6c/test_error_analysis.md).

## 3. Entscheidungen

1. **v6c nicht autonome freigeben.**
2. **Option C:** neuer Kandidat auf unabhängigen Daten.
3. **Assistierte Nutzung** nur mit 100 % menschlicher Prüfung aller
   numerischen Werte und ohne automatisches Pooling.
4. **Gates G1–G5 v1** sind bindend; keine nachträgliche Lockerung.
5. **249er-Test nicht wiederverwenden** — auch nicht als unabhängiger
   Holdout für den nächsten Kandidaten.
6. **Kein neuer Modelllauf** ohne ausdrückliche Freigabe.

Dokumente: [`decision_v6c.md`](decision_v6c.md) und
[`c1_acceptance_gates_v1.md`](c1_acceptance_gates_v1.md).

## 4. Was heute abgeschlossen wurde

- Dev-Historie bis v6c dokumentiert: **140/140 auf 26 Dev-Records**.
- Testprojektion erzeugt und mit **26 Checks** unabhängig geprüft.
- Release-Manifest, Hashschutz und genau eine Testfreigabe angelegt.
- 249er-Testlauf ausgeführt: **249/249, 0 Parse-Fehler**.
- Separater Test-Evaluator: **992/1308 exakt**, 0 Halluzinationen.
- Deskriptive Fehleranalyse nach Record, Feld, Typ und Blockmuster.
- Entscheidungsvorlage erstellt, Option C bestätigt, Gates v1 festgelegt.
- Tagesbericht und dieser Abschlussbericht erstellt.

## 5. Risiken und Blocker

| Risiko | Bedeutung | Status |
|---|---|---|
| Kein belastbarer unabhängiger Holdout | G5 nicht erfüllt; 3-Record-Smoke-Test reicht nicht; keine autonome Freigabe möglich | **offen** |
| 249er-Test verbraucht | Neue Auswertung darauf wäre kein unabhängiger Nachweis | **festgeschrieben** |
| 40,6 % fehlerhafte Records | Assistierte Nutzung braucht 100 % Prüfung | **offen** |
| Mean/SD-Blockfehler | Können gepoolte Effekte verzerren | **offen** |
| Fehlende menschliche Prüfkapazität | Assistierter Modus nicht skalierbar | **offen** |
| B-Rücklauf fehlt weiterhin | B-Watcher wartet; kein A/B-Vergleich | **beobachten** |

## 6. Aufgaben für morgen, 2026-11-12

### P0 — Holdout klären

**Ziel:** Entscheiden, ob ein unabhängiger C1-Holdout kurzfristig verfügbar
ist.

**Arbeit:**

- Neue Artikel/Records identifizieren, die weder in den 26 Dev- noch in den
  249 Test-Records enthalten sind.
- Prüfen, ob die Artikel disjunkt sind und ob eine belastbare Annotation
  möglich ist.
- Keine Verwendung des 249er-Tests als Holdout.
- Ergebnis als `holdout_plan_20261112.md` festhalten: Kandidaten, Anzahl,
  Artikeldisjunktheit, offene Lücken, Entscheidung.

**Fertig, wenn:** der Plan entweder einen konkreten Holdout mit Quellen und
Disjunktheitsprüfung nennt oder den Blocker „kein unabhängiger Holdout
verfügbar“ dokumentiert.

**Abhängigkeit:** keine. **Risiko:** Datenbeschaffung, Lizenzen, Annotation.

### P0 — Holdout-Manifest-Schema

**Ziel:** Die G5-Anforderungen vor der Datenerhebung technisch festlegen.

**Arbeit:**

- Schema für `holdout_manifest.json` entwerfen:
  `holdout_id`, `articles`, `records`, `input_sha256`, `reference_sha256`,
  `independent_of_dev`, `excluded_consumed_test`, `articles_disjoint`,
  `pre_registered`, `prompt_frozen_before_run`.
- Keine echten Holdout-Werte eintragen, solange der Holdout nicht existiert.
- Schema gegen [`c1_acceptance_gates_v1.json`](c1_acceptance_gates_v1.json)
  prüfen.

**Fertig, wenn:** ein dokumentiertes Schema und ein leeres Beispiel vorliegen,
das G5 vollständig abbildet.

### P1 — Gate-Checker bauen

**Ziel:** G1–G5 reproduzierbar prüfbar machen.

**Arbeit:**

- `public_benchmark/scripts/check_c1_gates.py` implementieren.
- Eingaben: `test_evaluation.json`, `c1_acceptance_gates_v1.json`,
  optional `holdout_manifest.json`.
- Ausgabe: Pass/Fail je Gate, Kennzahlen, Exitcode.
- Gegen v6c testen: **G1 pass; G2–G4 fail; G5 fail**.
- Keinen Modelllauf auslösen.

**Fertig, wenn:** der Checker auf v6c das erwartete Ergebnis liefert und
ohne Holdout-Manifest G5 sauber als „nicht bestanden“ meldet.

**Status 2026-11-12:** Erledigt. `check_c1_gates.py` ist implementiert; der
v6c-Report liegt unter [`gate_report_v6c.json`](gate_report_v6c.json).
Ergebnis: **G1 pass; G2–G4 fail; G5 fail** (kein Holdout-Manifest).

### P1 — Assistierte Nutzung operationalisieren

**Ziel:** Falls v6c interimistisch genutzt wird, Fehler nicht ins Pooling
lassen.

**Arbeit:**

- Kurze SOP `assisted_use_sop.md`:
  - 100 % menschliche Prüfung aller N-, Mean-, SD- und Event-Werte,
  - ICO- und Zeitpunktprüfung,
  - keine automatische Aufnahme ins Pooling,
  - fehlende Werte bleiben `null`,
  - Korrekturen und Quelle pro Wert dokumentieren.
- Keine Aussage „validiert“ oder „freigegeben“ verwenden.

**Fertig, wenn:** die SOP als Checkliste vorliegt und der Unterschied zu
einem Gate-Pass ausdrücklich benannt ist.

**Status 2026-11-12:** Erledigt. Die SOP liegt unter
[`assisted_use_sop.md`](assisted_use_sop.md); sie fordert 100 % menschliche
Prüfung, dokumentierte Korrekturen und schließt automatisches Pooling aus.

### P2 — Nächsten Kandidaten vorbereiten

**Ziel:** Entwicklungsarbeit ohne Testkontamination starten.

**Arbeit:**

- Blockbasierte Extraktionsziele aus der Fehleranalyse ableiten:
  vollständiger Record, fehlender Block, falscher Block.
- Mean/SD- und Comparator-Schwächen priorisieren.
- Änderungen nur auf Dev oder einem neuen Entwicklungsanteil planen.
- Keine Prompt-Änderung auf dem 249er-Test.

**Fertig, wenn:** ein kurzer `next_candidate_plan.md` mit Hypothesen,
Dev-Metriken und Abbruchkriterien vorliegt; noch kein Modelllauf.

**Status 2026-11-12:** Erledigt. Der Plan liegt unter
[`next_candidate_plan.md`](next_candidate_plan.md); P0 ist die Beschaffung
eines externen Holdouts, danach folgen Dev-Experimente und genau ein
Holdout-Lauf. Kein Modelllauf gestartet.

### P2 — B-Status prüfen

**Ziel:** B-Watcher unverändert lassen und Status dokumentieren.

**Arbeit:**

- Prüfen, ob `data/golden_effects/goldstandard_B_ruecklauf.json` vorhanden
  ist.
- Wenn nicht: Watcher weiterlaufen lassen, keine Datei erzeugen, keinen
  A/B-Vergleich behaupten.
- Status im Abschluss-/Tagesprotokoll vermerken.

**Fertig, wenn:** der B-Status klar dokumentiert ist.

### P2 — Tagesabschluss morgen

- Ergebnisse der P0/P1-Aufgaben committen.
- Offene Blocker und Entscheidungen aktualisieren.
- Keine C1-Testläufe ohne neue ausdrückliche Freigabe.

## 7. Was morgen ausdrücklich nicht getan wird

- Kein zweiter v6c-Testlauf.
- Keine Prompt-Optimierung auf dem 249er-Test.
- Keine Wiederverwendung des 249er-Tests als unabhängiger Holdout.
- Keine autonome Freigabe von v6c.
- Kein Modelllauf ohne neue Freigabe.
- Keine Änderung an B oder A ohne separaten Auftrag.
- Keine Secrets in Dateien, Commits oder Chat; `.env` bleibt unberührt.

## 8. Startcheckliste für morgen

1. `git status` prüfen; keine unerwarteten C1-Änderungen.
2. `git log -1` prüfen; letzter Commit ist dieser Abschlussbericht.
3. B-Watcher-Status prüfen.
4. [`decision_v6c.md`](decision_v6c.md) und
   [`c1_acceptance_gates_v1.md`](c1_acceptance_gates_v1.md) lesen.
5. Holdout-Verfügbarkeit klären, bevor irgendein Kandidat entwickelt wird.
6. Erst danach Gate-Checker und Entwicklungsplan bearbeiten.

## 9. Definition of Done für morgen

- Holdout-Plan oder dokumentierter Holdout-Blocker liegt vor.
- Holdout-Manifest-Schema bildet G5 vollständig ab.
- Gate-Checker ist implementiert und auf v6c geprüft.
- Assistierte Nutzung ist als SOP dokumentiert oder ausdrücklich verworfen.
- Nächster Kandidat hat einen Dev-Plan, aber noch keinen Testlauf.
- B-Status ist dokumentiert; B-Watcher unverändert.

## 10. Artefakte und Referenzen

- Tagesbericht: [`tagesbericht_20261111.md`](tagesbericht_20261111.md)
- Testresultat: [`runs_test/c1_test_20261111_v6c/test_result.md`](runs_test/c1_test_20261111_v6c/test_result.md)
- Fehleranalyse: [`runs_test/c1_test_20261111_v6c/test_error_analysis.md`](runs_test/c1_test_20261111_v6c/test_error_analysis.md)
- Entscheidung: [`decision_v6c.md`](decision_v6c.md)
- Gates v1: [`c1_acceptance_gates_v1.md`](c1_acceptance_gates_v1.md)
- Gates v1, JSON: [`c1_acceptance_gates_v1.json`](c1_acceptance_gates_v1.json)
- Testfreigabe: [`test_approval_v6c.json`](test_approval_v6c.json)
- Release-Manifest: [`release_v6c.json`](release_v6c.json)
- C1-README: [`README.md`](README.md)

## 11. Schlussbemerkung

Der Tag endet mit einem belastbaren, aber unbequemen Ergebnis: v6c ist
technisch sauber und auf Dev perfekt, aber auf dem Testsplit nicht gut genug
für eine ungeprüfte Meta-Analyse. Die Entscheidung ist dokumentiert, die
Gates sind verbindlich, und der nächste Engpass ist die Datenbeschaffung für
einen unabhängigen Holdout — nicht ein weiterer Prompt-Lauf.
