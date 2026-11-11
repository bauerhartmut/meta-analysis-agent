# C1-Testfreigabe: v6c

Stand: 2026-11-11
Kandidat: `c1_dev_20261111_v6c`, Prompt `c1-dev-extract-v6`
Status: **NO-GO - nicht freigegeben**

Der Kandidat ist auf Dev vollständig, aber der Testlauf ist noch nicht
freigabefähig. Die Testdaten bleiben gesperrt. Diese Checkliste ist die
verbindliche Gate-Liste; sie ersetzt keine ausdrückliche Freigabe.

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
| Testsplit gelesen | nein; `test_split_used=false` in allen v6-Läufen |

## 2. Harte Blocker

Diese Punkte müssen vor einer Freigabe geschlossen werden:

- [ ] **B1: Test-Runner fehlt.** Es gibt derzeit kein Skript, das den
  Testsplit als Input verwendet; `run_c1_dev_pilot.py` ist auf
  `dev_input.jsonl` festgelegt.
- [ ] **B2: Test-Input und Test-Referenz sind nicht getrennt.** Der
  Testlauf braucht eine projektierte Input-Datei ohne Referenzwerte und eine
  davon getrennte Referenzdatei. Die Referenz darf erst nach dem Einfrieren
  der Modellausgabe geladen werden.
- [ ] **B3: Record-Overrides sind nicht split-gebunden.** Die Bedingungen für
  Record 190 und 226 prüfen nur `record_id`, nicht `split == "dev"`. Bei
  gleicher ID im Test würden Dev-Werte in den Testprompt gelangen. Vor dem
  Test müssen beide Overrides auf Dev begrenzt und im Test durch einen
  Assertion blockiert werden.
- [ ] **B4: Kein Release-Manifest und keine ausdrückliche Freigabe.** Der
  Freeze-Manifest beschreibt den Datenstand, nicht den freigegebenen
  Testlauf; sein `pilot.status` ist noch `prepared_not_run`. Ein separates
  Release-Manifest muss Kandidat, Hashes, Test-Input-Hash, Metriken und
  Freigabezeitpunkt pinnen.
- [ ] **B5: Kein unabhängiger Check der Testprojektion.** Die 249 ICOs und
  Quellpfade müssen ohne Referenzfelder projiziert und von einer zweiten
  Person oder einem separaten Skript gegen den Freeze geprüft werden.

## 3. Checkliste Kandidat

- [x] v6c ist auf allen 26 Dev-Records vollständig und exakt.
- [x] 0 falsche, 0 fehlende, 0 halluzinierte Felder; MAE 0,0.
- [x] Record 120 mit DTPA-Zeile `8/20 vs. 13/44` korrekt.
- [x] Record 226 mit Post-test `25,78 ± 3,30` vs. `26,53 ± 3,53` korrekt.
- [x] v1-v5 erzeugen weiterhin ihre gespeicherten Prompt-Hashes.
- [x] v6c-Run-Manifest und Rohdaten sind vorhanden.
- [x] Der Testsplit wurde für v6c nicht gelesen.
- [ ] Nach dem Release-Manifest darf der Runner nicht mehr geändert werden;
  jede Änderung erfordert einen neuen Kandidaten und einen neuen Dev-Lauf.

## 4. Checkliste Daten

- [x] 275er-Freeze, 26 Dev- und 249 Test-Records sind im Manifest gepinnt.
- [x] Test-Policy ist `locked=true`.
- [x] Testsplit wurde nicht zur Prompt-Optimierung verwendet.
- [ ] Test-Input projektieren: nur `record_id`, `study_id`, `pmcid`, `split`,
  `outcome_type`, `ico`, `source_text_path`; keine Referenzwerte.
- [ ] Test-Input-SHA-256 berechnen und im Release-Manifest pinnen.
- [ ] Test-Referenz separat halten; während der Inferenz darf sie nicht
  geladen werden.
- [ ] Prüfen, dass der Test-Input 249 eindeutige IDs und `split="test"` für
  alle Records enthält.
- [ ] Testdatei-Hash nur zur Integritätsprüfung verwenden, niemals Inhalte
  zur Prompt-Anpassung anzeigen.

## 5. Checkliste Runner

- [ ] Separates Testskript, z. B. `run_c1_test_pilot.py`, mit explizitem
  `--approve-test`; ohne dieses Flag verweigert es den Start.
- [ ] Harte Asserts: 249 Records, `split="test"`, keine Dev-IDs, keine
  Referenzfelder im Input.
- [ ] Record-Overrides 190/226 nur bei `split="dev"`; im Test keine
  record-spezifischen Dev-Werte.
- [ ] Prompt-Version, Prompt-Hash, Modell, Temperatur, `max_tokens` und
  Concurrency werden vor dem ersten Request im Manifest festgehalten.
- [ ] Kein Resume mit geändertem Prompt. Ein technischer Retry ist nur bei
  fehlender oder unvollständiger Ausgabe zulässig und verwendet exakt
  dieselbe Konfiguration.
- [ ] Abbruch bei Rate-Limit-/Providerfehlern dokumentieren; kein stiller
  Wechsel des Modells oder Backends.
- [ ] Modellausgabe nach Abschluss hashen und einfrieren, bevor die
  Testreferenz geladen wird.

## 6. Checkliste Lauf

- [ ] Ausdrückliche Freigabe durch den Nutzer mit Datum und Umfang.
- [ ] Ein primärer Testlauf über alle 249 Records; keine Vortests auf
  Testdaten.
- [ ] Konfiguration wie v6c: Temperatur 0, `max_tokens=900`,
  `concurrency=3`.
- [ ] Laufzeit und Requestzahl protokollieren. Die lineare Extrapolation aus
  Dev (26 Records in 90 s) ergibt für 249 Records etwa 862 s bzw. 14,4 min;
  das ist keine Garantie und keine Token-Kostenschätzung.
- [ ] Ausgabe: 249 Zeilen, 249 eindeutige IDs, keine fehlenden Records.
- [ ] Bei technischem Abbruch: gleiche Konfiguration, neuer Run-ID,
  dokumentierter Grund; keine inhaltliche Prompt-Änderung.

## 7. Checkliste Auswertung

- [ ] Erwartete Felder: 1.308 (156 kontinuierliche × 6 + 93 binäre × 4).
- [ ] Primärmetrik: exakte Felder / 1.308; zusätzlich Abdeckung, MAE,
  fehlend, falsch, halluziniert und vollständig exakte Records.
- [ ] Harte Ausgabegates: 249/249 Records, 1.308/1.308 Abdeckung,
  0 Parse-/Schemafehler, 0 Halluzinationen.
- [ ] Keine nachträglichen Ausschlüsse, keine record-spezifischen
  Sonderauswertungen und keine Anpassung der Metrik nach Sicht der Ergebnisse.
- [ ] Die Dev-Adjudikationen 120 (DTPA), 226 (Post-test) und 190
  (12-Monats-Follow-up) gelten nur für Dev; im Test keine Übertragung ohne
  dokumentierte, vorab festgelegte Regel.
- [ ] Test-Referenz erst nach dem Output-Freeze laden; Evaluator getrennt vom
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

**Aktuell: NO-GO.**

Freigabefähig ist der Lauf erst, wenn B1-B5 geschlossen sind, das
Release-Manifest vorliegt und der Nutzer den Testlauf ausdrücklich freigibt.
Der Dev-Wert 140/140 ist eine Kandidatenqualifikation, kein Testresultat.
