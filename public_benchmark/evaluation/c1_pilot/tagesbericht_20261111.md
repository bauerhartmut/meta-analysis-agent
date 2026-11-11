# Tagesbericht 2026-11-11: C1-v6c, Testlauf und Entscheidung

Stand: 2026-11-11
Status: **Testlauf abgeschlossen; Option C entschieden; Gates v1 festgelegt**
Nächster Meilenstein: **unabhängiger Holdout für den nächsten C1-Kandidaten**

## 1. Kurzfassung

- Der Dev-Kandidat **v6c** erreicht auf den 26 Dev-Records **140/140 exakte
  Felder** und **26/26 vollständig exakte Records**.
- Der einmalige Testlauf über **249 Records** ist abgeschlossen:
  **992/1308 exakte Felder (75,8 %)**, **148/249 vollständig exakte Records
  (59,4 %)**, **0 Parse-/Schemafehler**, **0 Halluzinationen**.
- **101/249 Records (40,6 %)** enthalten mindestens einen Fehler.
- Die Fehler sind recordgetrennt: **32 nur fehlend**, **69 nur falsch**,
  **0 mit beidem**.
- **v6c wird nicht für eine autonome oder ungeprüfte Meta-Analyse
  freigegeben.** Eine assistierte Nutzung ist nur mit 100 % menschlicher
  Prüfung zulässig.
- **Option C ist angenommen:** neuer Kandidat auf unabhängigen Daten.
- Die Gates **G1–G5** sind als Projektstandard v1 festgelegt.
- Der **249er-Test ist verbraucht** und darf nicht zur Entwicklung des
  nächsten Kandidaten wiederverwendet werden.
- Es gab **keinen weiteren Modelllauf** nach dem Test und **keine
  Prompt-Änderung** nach Testbeginn.

## 2. Ausgangslage

C1 ist die numerische Extraktion von Armwerten aus Yun et al. 2024 für die
Meta-Analyse. Der eingefrorene C1-Datensatz umfasst **275 nutzbare Records**:

- **26 Dev-Records** aus 6 Artikeln,
- **249 Test-Records** aus 64 Artikeln,
- davon **156 kontinuierliche** und **93 binäre** Records,
- **1.308 erwartete Felder** (156 × 6 + 93 × 4).

Der Testsplit war vor dem Lauf gesperrt. Die Testreferenz wurde im Runner
nicht geladen; der separate Evaluator lud sie erst nach dem Output-Freeze.

### 2.1 Weitere heutige Arbeiten

| Arbeitsblock | Ergebnis |
|---|---|
| dCBT-I-Nachbau | Eigener gepoolter Hedges g = **-0,584 [-1,029; -0,139]** gegenüber publiziert **-0,58 [-1,03; -0,13]**; Pool verifiziert. |
| B-Paket | Integrität geprüft und Hash festgehalten; B-Rücklauf angefordert; B-Watcher unverändert. |
| Yun-Audit 30 | **4/104** harte Zahlenfehler (3,8 %), **6/30** strukturelle Fehler (20,0 %), **8/30** Records mit klarem Fehler (26,7 %). |
| Yun-Audit 410 | **275/410** für C1 nutzbar: 239 `verified_exact`, 35 `verified_table`, 1 `corrected_with_source`; 57 strukturell ausgeschlossen, 78 nicht ausreichend belegt. |
| C1-Freeze | **275 Records aus 70 Artikeln**, davon 26 Dev und 249 Test; Dev-/Testtrennung gehasht und eingefroren. |

Details stehen in [`../../README.md`](../../README.md) und
[`../../validation/README.md`](../../validation/README.md).

## 3. Dev-Historie

| Kandidat | Prompt | Dev-Ergebnis | Status |
|---|---|---|---:|---|
| v1 | `c1-dev-extract-v1` | 93/140 (66,4 %) | historischer Messpunkt |
| v2 | `c1-dev-extract-v2` | 93/140 (66,4 %) | keine Verbesserung |
| v3 | `c1-dev-extract-v3` | 123/140 (87,9 %) | nicht testreif |
| v4 | `c1-dev-extract-v4` | 126/140 (90,0 %) | nicht testreif |
| v5 | `c1-dev-extract-v5` | 136/140 (97,1 %) | ein offener Record |
| v6 | `c1-dev-extract-v6` | 135/140 (96,4 %) | verworfen |
| v6b | `c1-dev-extract-v6b` | 125/140 (89,3 %) | verworfen |
| **v6c** | **`c1-dev-extract-v6`** | **140/140 (100 %)** | **Testkandidat** |

Wesentliche Dev-Entscheidungen:

- **Record 120:** DTPA-Befund „partial obstruction“ mit **8/20 vs. 13/44**;
  nicht die Rezidiv-/Reoperationszeile.
- **Record 226:** Post-test **25,78 ± 3,30 vs. 26,53 ± 3,53**.
- Die Overrides für 190/226 sind strikt auf `split="dev"` begrenzt.
- v6c priorisiert die direkt gemessene Outcome-Zeile; v6b wurde wegen
  falscher Leerzellen-Erkennung verworfen.

## 4. Testvorbereitung

- `c1_test_projection.py` erzeugte getrennte Dateien:
  `test_input.jsonl` und `test_reference.jsonl`.
- Projektion: **249 Records**, **64 Artikel**, **156/93 Typen**,
  **1.308 Felder**.
- Input-SHA-256:
  `b8a2f3d17c2ee4a41473811ccb72632175f1d786b05b9e16e2d8c18d64204368`
- Referenz-SHA-256:
  `84b5c925340af82eb72717b36b2e4c5a2fa04760d6a6d01e63b742d0689e0629`
- `verify_c1_test_projection.py`: **26 Checks, PASSED, 0 Abweichungen**.
- `run_c1_test_pilot.py` verweigert den Start ohne `--approve-test`.
- `evaluate_c1_test_pilot.py` prüft Output-, Input- und Referenzhash, bevor
  die Testreferenz geladen wird.
- Freigabe: `test_approval_v6c.json` mit `test_run_approved=true` und
  `allowed_runs=1`.
- Das Release-Manifest `release_v6c.json` bleibt der **Pre-Run-Stand** mit
  `test_run_approved=false`; die separate Approval-Datei ist die Freigabe.
- Release-Manifest-SHA-256:
  `0068395e354b97b6ec4d7cc053ae481fe52fdfea8135a65cd89d6297f3ee2689`.

## 5. Testlauf

| Feld | Wert |
|---|---|
| Run-ID | `c1_test_20261111_v6c` |
| Modell | `gwdg/qwen3.5-397b-a17b` |
| Prompt | `c1-dev-extract-v6` |
| Temperatur | 0 |
| `max_tokens` | 900 |
| Concurrency | 3 |
| Start | 2026-11-11 23:21:22 |
| Ende | 2026-11-11 23:32:34 |
| Laufzeit | 11:12 |
| Ausgabezeilen | 249/249 |
| Parse-/Schemafehler | 0 |
| Halluzinationen | 0 |
| `reference_loaded` im Runner | false |
| `test_split_used` | true |
| Output-SHA-256 | `977493541634fa3ecb7d6794cf65839749848702a5c722d15d3e80b4b26cd9f9` |
| Raw-SHA-256 | `91934b21b93d3d689952d1022a13eebded88f01a4a71822c39615f18216e4f05` |

## 6. Aktuelle Testergebnisse

### Gesamt

| Kennzahl | Wert |
|---|---:|
| Records mit Ausgabe | 249/249 |
| erwartete Felder | 1.308 |
| abgedeckt | 1.168/1.308 (89,3 %) |
| exakt | **992/1.308 (75,8 %)** |
| fehlend | 140 (10,7 %) |
| falsch | 176 (13,5 %) |
| halluziniert | 0 |
| vollständig exakte Records | **148/249 (59,4 %)** |
| Records mit mindestens einem Fehler | 101/249 (40,6 %) |
| MAE über gepaarte Felder | 1,5305 |
| Null-Disziplin | 684/684 (100 %) |
| Parse-/Schemafehler | 0 |

### Nach Outcome-Typ

| Typ | Records | erwartet | exakt | fehlend | falsch | vollständig exakt |
|---|---:|---:|---:|---:|---:|---:|
| continuous | 156 | 936 | **678 (72,4 %)** | 106 | 152 | 79/156 |
| binary | 93 | 372 | **314 (84,4 %)** | 34 | 24 | 69/93 |
| **gesamt** | **249** | **1.308** | **992 (75,8 %)** | **140** | **176** | **148/249** |

### Feldebene

| Feld | erwartet | exakt | fehlend | falsch | MAE |
|---|---:|---:|---:|---:|---:|
| `intervention_n` | 249 | 214 (85,9 %) | 20 | 15 | 1,0742 |
| `comparator_n` | 249 | 201 (80,7 %) | 20 | 28 | 1,9694 |
| `intervention_mean` | 156 | 110 (70,5 %) | 21 | 25 | 2,4114 |
| `comparator_mean` | 156 | 105 (67,3 %) | 21 | 30 | 2,5808 |
| `intervention_sd` | 156 | 106 (68,0 %) | 21 | 29 | 0,6040 |
| `comparator_sd` | 156 | 104 (66,7 %) | 21 | 31 | 0,3642 |
| `intervention_events` | 93 | 76 (81,7 %) | 8 | 9 | 1,8000 |
| `comparator_events` | 93 | 76 (81,7 %) | 8 | 9 | 1,5647 |

Die kontinuierlichen Mean/SD-Felder sind der schwächste Block. Der
Vergleichsarm ist bei n und Mean/SD etwas schwächer als der
Interventionsarm; die binären Event-Felder sind arm-symmetrisch.

## 7. Fehlerbild

### Record-Ebene

| Typ | vollständig exakt | nur fehlend | nur falsch | fehlend und falsch | 0 exakt |
|---|---:|---:|---:|---:|---:|
| continuous | 79 | 22 | 55 | 0 | 11 |
| binary | 69 | 10 | 14 | 0 | 7 |
| **gesamt** | **148** | **32** | **69** | **0** | **18** |

Fehlende und falsche Werte schließen sich auf Record-Ebene aus. Das spricht
für blockweise Extraktion: Das Modell liefert entweder einen vollständigen
Block (möglicherweise mit falschen Werten) oder lässt einen Block weg.

### Blockmuster

- **continuous, fehlend:** 11 Records mit beiden Mean/SD-Armen fehlend,
  10 Records mit allen sechs Feldern fehlend, 1 Record mit beiden n-Feldern
  fehlend.
- **continuous, falsch:** 23 Records mit allen vier Mean/SD-Feldern falsch
  bei exakten n-Feldern; 10 Records nur mit `comparator_n` falsch; 10 Records
  mit beiden n-Feldern falsch.
- **binary, fehlend:** 7 Records mit allen vier Feldern fehlend, 2 Records
  mit beiden n-Feldern fehlend, 1 Record mit beiden Event-Feldern fehlend.
- **binary, falsch:** 7 Records mit beiden Event-Feldern falsch, 3 Records
  mit beiden n-Feldern falsch, je 2 Records mit nur einem Event-Feld falsch.

### Weitere Befunde

- **0 Halluzinationen.**
- **0 Parse-/Schemafehler.**
- **Null-Disziplin 684/684 (100 %).**
- Kein durchgängiger Richtungsbias; Über- und Unterschätzungen wechseln je
  Feld, einzelne Felder zeigen lokale Asymmetrien.
- Die exakte Metrik bestraft auch kleine Rundungs- oder
  Skalierungsabweichungen. Die Near-Miss-Zahlen stehen in der
  Fehleranalyse; sie ändern aber nichts an den fehlenden Blöcken.

## 8. Bewertung

Der Dev-Wert **140/140** generalisiert nicht auf den Testsplit. Die Differenz
zum Testwert beträgt **24,2 Prozentpunkte**. Für eine ungeprüfte
Meta-Analyse ist das nicht ausreichend:

- **40,6 % der Records** enthalten mindestens einen Fehler.
- **13,5 % aller Felder** sind falsch und **10,7 %** fehlen.
- Besonders kritisch sind Mean/SD und die fehlenden Blöcke.
- Falsche N/Mean/SD können gepoolte Effekte verzerren; fehlende Blöcke
  reduzieren die Zahl der poolbaren Studien.

Gleichzeitig ist die technische Struktur gut: vollständige Ausgabe, keine
Halluzinationen, keine Parse-Fehler und eine perfekte Null-Disziplin. Das
Problem ist die Wertequalität und Blockvollständigkeit, nicht die
Ausgabeform.

## 9. Entscheidung: Option C und Gates v1

**Beschlossen am 2026-11-11:** Option C — neuer Kandidat auf unabhängigen
Daten. v6c wird nicht für eine autonome oder ungeprüfte Meta-Analyse
freigegeben.

### Gates G1–G5

| Gate | Anforderung | v6c |
|---|---|---|
| **G1 Integrität** | Alle Records, 0 Parse-/Schemafehler, 0 Halluzinationen, 100 % Null-Disziplin | **bestanden** |
| **G2 Record-Vollständigkeit** | ≥ 95 % der Records mit allen erwarteten Feldern | 217/249 = **87,1 %**, nicht bestanden |
| **G3 Feldgenauigkeit** | ≥ 95 % gesamt und ≥ 95 % je kritischem Feld | 75,8 %; 66,7–87,1 %, nicht bestanden |
| **G4 Record-Genauigkeit** | ≥ 90 % vollständig exakt | 148/249 = **59,4 %**, nicht bestanden |
| **G5 Unabhängige Validierung** | neuer, artikeldisjunkter Holdout; nicht der 249er-Test | kein Holdout, nicht bestanden |

**Regel:** Alle fünf Gates müssen bestehen. Es gibt keinen Teilpass und keine
nachträgliche Lockerung. Änderungen nur als neue Policy-Version vor dem
nächsten Lauf.

**Assistierte Nutzung:** möglich, aber nur mit 100 % menschlicher Prüfung
aller numerischen Werte, ohne automatisches Pooling. Das ist kein Gate-Pass.

## 10. Was heute nicht gemacht wurde

- Keine Prompt-Änderung nach Testbeginn.
- Kein zweiter Testlauf.
- Keine Optimierung auf dem Testsplit.
- Keine autonome Freigabe von v6c.
- Keine Wiederverwendung des 249er-Tests als unabhängiger Holdout.
- Kein neuer Modelllauf nach der Entscheidung.

## 11. Offene Punkte

1. **Unabhängiger Holdout fehlt.** Ohne neuen, artikeldisjunkten Holdout ist
   G5 nicht erfüllbar.
2. **Ressourcen für assistierte Nutzung:** 100 % menschliche Prüfung ist
   Voraussetzung; die 40,6 % fehlerhaften Records sind kein automatischer
   Durchlauf.
3. **Nächster Kandidat:** Entwicklung auf Dev oder einem neuen
   Entwicklungsanteil; keine Testoptimierung.
4. **Gate-Prüfung:** G1–G5 vor dem nächsten Lauf einfrieren; genau einen
   freigegebenen Evaluationslauf durchführen.

## 12. Nächste Schritte

1. Neuen unabhängigen Holdout beschaffen oder neu annotieren:
   artikeldisjunkt zu Dev und dem verbrauchten 249er-Test.
2. Input, Referenz und Holdout-Manifest vor dem Lauf hashen.
3. Nächsten Kandidaten auf Dev/neuem Entwicklungsanteil entwickeln.
4. Gates v1 vor dem Lauf unverändert festschreiben.
5. Genau einen freigegebenen Evaluationslauf durchführen und G1–G5 prüfen.

## 13. Artefakte

| Artefakt | Pfad |
|---|---|
| Tagesbericht | `public_benchmark/evaluation/c1_pilot/tagesbericht_20261111.md` |
| Testresultat | `public_benchmark/evaluation/c1_pilot/runs_test/c1_test_20261111_v6c/test_result.md` |
| Test-Evaluation | `.../test_evaluation.md` und `.../test_evaluation.json` |
| Fehleranalyse | `.../test_error_analysis.md` und `.../test_error_analysis.json` |
| Test-Manifest | `.../test_manifest.json` |
| Entscheidung | `public_benchmark/evaluation/c1_pilot/decision_v6c.md` |
| Gates v1 | `public_benchmark/evaluation/c1_pilot/c1_acceptance_gates_v1.md` |
| Gates v1, maschinenlesbar | `public_benchmark/evaluation/c1_pilot/c1_acceptance_gates_v1.json` |
| Testfreigabe | `public_benchmark/evaluation/c1_pilot/test_approval_v6c.json` |
| Release-Manifest | `public_benchmark/evaluation/c1_pilot/release_v6c.json` |
| Fehleranalyse-Skript | `public_benchmark/scripts/analyze_c1_test_errors.py` |

## 14. Commit-Historie (2026-11-11)

```text
7f20d58 00:09 Notiz fuer morgen und sauberen Shutdown hinterlegen
20533ec 00:10 Tippfehler in der Notiz fuer morgen korrigieren
1be894f 18:42 CBT-I-Pilot fuer den Metaanalyse-Nachbau anlegen
23054a5 18:53 Zugangspruefung fuer den CBT-I-Piloten dokumentieren
ab02d4d 19:02 Ersatz-Metaanalyse mit frei zugaenglichen Primaertexten dokumentieren
58c31ea 19:18 dCBT-I-Metaanalyse nachbauen und Pool verifizieren
d4f90e3 19:29 B-Paketintegritaet pruefen und Hash festhalten
fed4bd6 20:35 B-Ruecklauf anfordern und Eingangspruefung vorbereiten
3260fd4 20:47 dCBT-I-Ergebnisse und B-Notwendigkeit erklaeren
c7aa893 21:08 Oeffentliche B-Benchmarks pruefen und dokumentieren
78ed6d1 21:22 Yun-Referenzaudit auf 30 stratifizierte Records dokumentieren
5baea2c 21:52 Yun-Referenz auf 410 vollstaendige Records kuratieren
4e75a06 21:57 C1-Referenz einfrieren und Dev-Pilot vorbereiten
a017c8b 21:57 C1-Freeze-Zeilenenden stabilisieren
3081b3f 22:22 Yun-C1-Dev-Pilot ausfuehren und gegen Referenz auswerten
4de2454 22:24 C1-Zeitpunktregel verbindlich festlegen
707cbd3 22:26 C1-Prompt um Zeitpunktregel versionieren
d419a75 22:30 C1-Prompt-v2-Test dokumentieren
4d5e0cc 22:34 C1-Prompt v3 mit Post-test-Prioritaet
c4501b0 22:35 C1-Prompt-v3-Test dokumentieren
28faaeb 22:41 C1-Prompt v4 mit Zellverifikation testen
dc64957 22:44 C1-Prompt v5 mit robuster Zellpruefung testen
643dee1 22:47 Record 120 fuer C1 adjudizieren
5745f03 22:56 C1-Prompt v6 mit Outcome-Zeilen-Prioritaet testen
daa9084 23:00 C1-Testfreigabe-Checkliste fuer v6c anlegen
159660a 23:12 C1-Testpfad mit getrenntem Input und Dev-Overrides bauen
9f68847 23:13 Testpfad-Hashes fuer Prompt und Referenz absichern
3745c89 23:16 C1-Testprojektion erzeugen und unabhaengig pruefen
77aaad9 23:19 C1-Release-Manifest fuer v6c anlegen
a2662a0 23:19 C1-Release-Hashdatei auf LF festlegen
46e7cd0 23:21 C1-v6c-Testlauf freigeben
fbcf7cd 23:35 C1-Testlauf v6c auswerten und dokumentieren
02729d5 23:40 C1-Testfehler deskriptiv analysieren
3c377d0 23:48 Entscheidungsvorlage fuer C1-v6c erstellen
176152f 23:52 Option C und C1-Akzeptanzgates v1 festschreiben
```

## 15. Prüfungen

- `verify_c1_test_projection.py`: **26 Checks, PASSED, 0 Abweichungen**.
- `sha256sum -c release_v6c.sha256`: **OK**.
- Testlauf: **249/249 Records**, **0 Parse-/Schemafehler**.
- Test-Evaluation: **1.308 erwartete Felder**, **992 exakt**, **0
  Halluzinationen**.
- Fehleranalyse: Invarianten **32/69/0**, **148/249 vollständig exakt**.
- Gate-JSON: **adopted**, Option C, G1–G5 konsistent.
- CJK- und Secret-Musterprüfung: **OK**.
- `git diff --check`: **OK**.
- Kein Modelllauf nach dem Test; keine Prompt-Änderung nach Testbeginn.

## 16. Quellen

- [`README.md`](README.md)
- [`runs_test/c1_test_20261111_v6c/test_result.md`](runs_test/c1_test_20261111_v6c/test_result.md)
- [`runs_test/c1_test_20261111_v6c/test_error_analysis.md`](runs_test/c1_test_20261111_v6c/test_error_analysis.md)
- [`decision_v6c.md`](decision_v6c.md)
- [`c1_acceptance_gates_v1.md`](c1_acceptance_gates_v1.md)
- [`../../../METAANALYSE.md`](../../../METAANALYSE.md)
- [`../../../ENTWICKLUNGSAUFTRAG_v2.md`](../../../ENTWICKLUNGSAUFTRAG_v2.md)
