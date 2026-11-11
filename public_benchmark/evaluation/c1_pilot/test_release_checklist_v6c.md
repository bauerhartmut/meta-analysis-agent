# C1-Testfreigabe: v6c

Stand: 2026-11-11
Kandidat: `c1_dev_20261111_v6c`, Prompt `c1-dev-extract-v6`
Status: **TEST COMPLETED - Ergebnis dokumentiert**

Der Kandidat ist auf Dev vollständig; der eine freigegebene Testlauf ist
durchgeführt und ausgewertet. Das Ergebnis ist dokumentiert, nicht zur
Prompt-Optimierung verwendet und wird nicht wiederholt.

## 1. Nachweis

| Gegenstand | Beleg |
|---|---|
| Kandidaten-Commit | `5745f03` |
| Dev-Ergebnis | 140/140 exakt, 140/140 Abdeckung, 0 falsch, 0 fehlend, 0 halluziniert, MAE 0,0 |
| Dev-Records | 26/26 vollständig exakt, 0 Parse-/Schemafehler |
| Modell | `gwdg/qwen3.5-397b-a17b`, Temperatur 0, `max_tokens=900`, `concurrency=3` |
| Prompt-Hash aller 26 Records | `d0300215ff6bfd9dfbb81664f3cadaf19fa5bc3c019cce40db09c6e3524dca14` |
| Dev-Input-Hash | `198fc2a20d6c98001defc10fb1b4d5758b5c6f5554d885c5785e44cbdaa18374` |
| Modellkonfigurations-Hash | `75bb627f214ef6ace9714818ecc928ff4641fc130dc63c74c7d271da31145725` |
| Output-Hash | `abe92e7ee4f452eaf7bcf16418968cf6b955b4d03ee78f19f643c5ac0cafd195` |
| Raw-Hash | `f90519b6ce66313b624d1a2e6d5ff17b32bbd7535a21df54ab45896f326c4683` |
| Freeze 275 | 275 Records, 70 Artikel; SHA-256 `567d54b81ca07163979684e43ab333a740812909614b7215c2de5edd200bf13c` |
| Dev 26 | 26 Records, 6 Artikel; SHA-256 `e1b75d63059727047edf9387fc429be4622b44759248b2f74921760c1504c0d5` |
| Test 249 | 249 Records, 64 Artikel; SHA-256 `7eb1bc43b2ca044dea739c36f1a6c7f86fa577d4e25174d01ef8ebac8ce00da2` |
| Test-Policy | `locked=true`, `used_for_prompt_optimization=false` |
| Testsplit gelesen | für die Projektion ja, für keinen Modelllauf; `test_split_used=false` in allen v6-Läufen |
| Release-Manifest | `release_v6c.json`, SHA-256 `0068395e354b97b6ec4d7cc053ae481fe52fdfea8135a65cd89d6297f3ee2689`; `test_run_approved=false` |

## 2. Umsetzung und harte Blocker

Umgesetzt und geprüft:

- [x] **B1: Test-Runner vorhanden.** `run_c1_test_pilot.py` startet nur mit
  `--approve-test`, verwendet ausschließlich `test_input.jsonl` und importiert
  keine Testreferenz.
- [x] **B2: Input und Referenz getrennt und erzeugt.** Die 249er-Projektion
  liegt lokal unter `test_locked/`: `test_input.jsonl` ohne Referenzfelder
  (SHA-256 `b8a2f3d17c2ee4a41473811ccb72632175f1d786b05b9e16e2d8c18d64204368`)
  und separate `test_reference.jsonl`
  (SHA-256 `84b5c925340af82eb72717b36b2e4c5a2fa04760d6a6d01e63b742d0689e0629`).
- [x] **B3: Record-Overrides sind split-gebunden.** Die 190/226-Overrides
  greifen nur bei `split="dev"`; der Isolationstest prüft Test-Records mit
  denselben IDs und findet keine Dev-Werte im Testprompt.

Abgeschlossen:

- [x] **Ausdrückliche Testlauf-Freigabe.** [`test_approval_v6c.json`](test_approval_v6c.json)
  autorisiert genau einen Lauf; `allowed_runs=1`, `test_run_approved=true`.
- [x] **Testlauf durchgeführt.** 249/249 Records, 992/1308 exakt, 0
  Parse-/Schemafehler, 0 Halluzinationen. Ergebnis:
  [`runs_test/c1_test_20261111_v6c/test_result.md`](runs_test/c1_test_20261111_v6c/test_result.md).
- [x] **Deskriptive Fehleranalyse.** Fehlende und falsche Werte sind
  Record-getrennt; 148/249 vollständig exakt. Bericht:
  [`runs_test/c1_test_20261111_v6c/test_error_analysis.md`](runs_test/c1_test_20261111_v6c/test_error_analysis.md).
- [x] **B5: Unabhängiger Check bestanden.**
  `verify_c1_test_projection.py` prüft 26 Checks gegen den Freeze, darunter
  Quellzeilen, Referenzwerte, IDs, Schema, Typen, Quellpfade und
  Referenzfreiheit des Inputs. Bericht:
  [`test_projection_verification.md`](test_projection_verification.md).
- [x] Die Projektion ist über `.gitignore` lokal geschützt und nicht
  versioniert.
- [x] **B4: Release-Manifest vorhanden.** [`release_v6c.json`](release_v6c.json)
  pinnt Kandidat, Freeze, Testprojektion, Runner-/Prompt-Hashes und den
  Verifikationsbericht; der Sidecar-Hash steht in
  [`release_v6c.sha256`](release_v6c.sha256). Das Manifest setzt
  `test_run_approved=false`.

Der Testlauf ist abgeschlossen. Es gibt keinen offenen Freigabeschritt mehr;
weitere Testläufe brauchen eine neue Freigabe und einen neuen Kandidaten.

Der Testsplit wurde für die Projektion gelesen, aber nicht für
Prompt-Optimierung oder einen Modelllauf verwendet.

## 3. Checkliste Kandidat

- [x] v6c ist auf allen 26 Dev-Records vollständig und exakt.
- [x] 0 falsche, 0 fehlende, 0 halluzinierte Felder; MAE 0,0.
- [x] Record 120 mit DTPA-Zeile `8/20 vs. 13/44` korrekt.
- [x] Record 226 mit Post-test `25,78 ± 3,30` vs. `26,53 ± 3,53` korrekt.
- [x] v1-v5 erzeugen weiterhin ihre gespeicherten Prompt-Hashes.
- [x] v6c-Run-Manifest und Rohdaten sind vorhanden.
- [x] Der Testsplit wurde für v6c nicht gelesen.
- [x] Nach dem Release-Manifest darf der Runner nicht mehr geändert werden;
  jede Änderung erfordert einen neuen Kandidaten und einen neuen Dev-Lauf.

## 4. Checkliste Daten

- [x] 275er-Freeze, 26 Dev- und 249 Test-Records sind im Manifest gepinnt.
- [x] Test-Policy ist `locked=true`.
- [x] Testsplit wurde nicht zur Prompt-Optimierung verwendet.
- [x] Test-Input projektieren: nur `record_id`, `study_id`, `pmcid`, `split`,
  `outcome_type`, `ico`, `source_text_path`; keine Referenzwerte.
- [x] Test-Input-SHA-256 berechnen und im Projektionsmanifest pinnen.
- [x] Test-Referenz separat halten; während der Inferenz darf sie nicht
  geladen werden.
- [x] Prüfen, dass der Test-Input 249 eindeutige IDs und `split="test"` für
  alle Records enthält.
- [x] Testdatei-Hash nur zur Integritätsprüfung verwenden, niemals Inhalte
  zur Prompt-Anpassung anzeigen.

## 5. Checkliste Runner

- [x] Separates Testskript `run_c1_test_pilot.py` mit explizitem
  `--approve-test`; ohne dieses Flag verweigert es den Start.
- [x] Harte Asserts: 249 Records, `split="test"`, keine Referenzfelder im
  Input.
- [x] Record-Overrides 190/226 nur bei `split="dev"`; im Test keine
  record-spezifischen Dev-Werte.
- [x] Prompt-Version, Prompt-Hash, Prompt-Modul-Hash, Modell, Temperatur,
  `max_tokens` und Concurrency werden vor dem ersten Request im Manifest
  festgehalten.
- [x] Kein Resume mit geändertem Prompt. Der Runner prüft Input- und
  Runner-Hash sowie die Modellkonfiguration.
- [ ] Abbruch bei Rate-Limit-/Providerfehlern dokumentieren; kein stiller
  Wechsel des Modells oder Backends.
- [x] Modellausgabe nach Abschluss hashen und einfrieren, bevor die
  Testreferenz geladen wird.
- [x] `evaluate_c1_test_pilot.py` prüft Output-, Input- und Referenzhash,
  bevor es die getrennte Testreferenz lädt.

## 6. Checkliste Lauf

- [x] Ausdrückliche Freigabe durch den Nutzer mit Datum und Umfang.
- [x] Ein primärer Testlauf über alle 249 Records; keine Vortests auf
  Testdaten.
- [x] Konfiguration wie v6c: Temperatur 0, `max_tokens=900`,
  `concurrency=3`.
- [x] Ausgabe: 249 Zeilen, 249 eindeutige IDs, keine fehlenden Records.
- [x] Bei technischem Abbruch: gleiche Konfiguration, neuer Run-ID,
  dokumentierter Grund; keine inhaltliche Prompt-Änderung.
- [x] Laufzeit: 11:12 (23:21:22 bis 23:32:34) für 249 Requests; die lineare
  Extrapolation aus Dev ergab etwa 862 s bzw. 14,4 min und war nur eine
  Schätzung, keine Garantie oder Token-Kostenschätzung.

## 7. Checkliste Auswertung

- [x] Erwartete Felder: 1.308 (156 kontinuierliche × 6 + 93 binäre × 4).
- [x] Primärmetrik: exakte Felder / 1.308; zusätzlich Abdeckung, MAE,
  fehlend, falsch, halluziniert und vollständig exakte Records.
- [ ] Harte Ausgabegates: 249/249 Records und 0 Parse-/Schemafehler sind
  erfüllt; die volle Abdeckung 1.308/1.308 ist **nicht** erreicht
  (1.168/1.308, 89,3 %).
- [ ] Keine nachträglichen Ausschlüsse, keine record-spezifischen
  Sonderauswertungen und keine Anpassung der Metrik nach Sicht der Ergebnisse.
- [x] Die Dev-Adjudikationen 120 (DTPA), 226 (Post-test) und 190
  (12-Monats-Follow-up) gelten nur für Dev; im Test keine Übertragung ohne
  dokumentierte, vorab festgelegte Regel.
- [x] Test-Referenz erst nach dem Output-Freeze laden; Evaluator getrennt vom
  Runner ausführen.
- [ ] Ergebnisse, Fehlerliste, Hashes und Laufzeit als Artefakt ablegen.

## 8. Stoppregeln

Der Lauf wird sofort gestoppt und **nicht** durch Prompt-Tuning wiederholt,
wenn einer der folgenden Fälle eintritt:

- Test-Input-Hash weicht vom Release-Manifest ab.
- Die Testreferenz wird während der Inferenz geladen.
- Ein Dev-Override greift bei einem Test-Record.
- Weniger als 249 Ausgabezeilen oder doppelte/fehlende IDs.
- Parse-/Schemafehler oder Halluzinationen treten auf.
- Ein Providerfehler erzwingt einen Modell- oder Backendwechsel.

Ein Stopp ist ein Ergebnis, kein Grund für einen zweiten Testlauf. Ein
weiterer Lauf braucht eine neue ausdrückliche Freigabe und einen neuen
Kandidaten.

## 9. Freigabeentscheidung

**Testlauf abgeschlossen.**

Der Testlauf ist abgeschlossen: **992/1308 exakt (75,8 %)**, 140 fehlend,
176 falsch, 0 halluziniert, 0 Parse-/Schemafehler; 148/249 Records sind
vollständig exakt. Das Ergebnis wird nicht zur Prompt-Optimierung verwendet
und nicht wiederholt. Der Dev-Wert 140/140 bleibt eine
Kandidatenqualifikation, kein Testresultat.
