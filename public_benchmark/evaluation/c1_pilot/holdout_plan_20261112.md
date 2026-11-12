# C1-Holdout-Plan 2026-11-12

Stand: 2026-11-12
Status: **PARTIAL - 3/33 Records vollständig belegbar; kein belastbarer G5-Holdout**
Entscheidung: **kein Modelllauf; 3-Record-Smoke-Test optional; externen Holdout beschaffen**
P0-Beschaffung: **PMC Open Access Subset via Europe PMC; 30 Artikel / 100 Records**
(siehe [`p0_external_holdout_20261112.md`](p0_external_holdout_20261112.md))
P0-Query 2026-11-12: **596 artikeldisjunkte Kandidaten** (September-2026-Frame,
0 Überschneidungen). Abstract-Screening v1: **152 ausgeschlossen, 65 manuell,
379 vorläufig für Volltext**; keine endgültige Eignung, kein Modelllauf.

## 1. Ziel

G5 verlangt einen neuen, vorab eingefrorenen und artikeldisjunkten Holdout, der
nicht die 26 Dev- und nicht die 249 Test-Records enthält. Dieser Plan prüft,
ob ein solcher Holdout aus den vorhandenen Yun-Daten gebaut werden kann.

## 2. Dateninventar

| Bestand | Records | Artikel | Status |
|---|---:|---:|---|
| C1-Freeze, nutzbar | **275** | **70** | vollständig vergeben: 26 Dev, 249 Test |
| davon Dev | 26 | 6 | Entwicklung |
| davon Test | 249 | 64 | **verbraucht**, nicht wiederverwenden |
| 410er-Audit | 410 | 85 | 239 `verified_exact`, 35 `verified_table`, 1 `corrected_with_source`, 78 `unverifiable`, 57 `structural_exclude` |
| Yun-Gesamtdaten | 699 | 120 | 410 streng vollständig, 289 nicht streng vollständig |
| Artikel außerhalb des Freeze | - | 50 | keine nutzbaren C1-Records |
| Audit-Records außerhalb des Freeze | 63 | 15 | 33 `unverifiable`, 30 `structural_exclude` |
| Nicht streng vollständig außerhalb des Freeze | 173 | 40 | 0–4 von 6 bzw. 4 Pflichtfeldern |

## 3. Prüfung

### 3.1 Keine versteckten nutzbaren Records

Alle **275** für C1 nutzbaren Records sind im Freeze enthalten. Außerhalb
liegen **keine** `verified_exact`-, `verified_table`- oder
`corrected_with_source`-Records. Eine Wiederverwendung von 249 Test-Records
ist ausgeschlossen, weil der Test verbraucht ist.

### 3.2 Unverifiable Records

- **78 Records** aus **24 Artikeln** sind `unverifiable`.
- **33 Records aus 9 Artikeln** liegen außerhalb des Freeze und wären
  artikeldisjunkt: PMC4319071 (6), PMC5056957 (6), PMC5380326 (5),
  PMC4357072 (4), PMC3136370 (4), PMC3654355 (3), PMC1574360 (2),
  PMC5079604 (2), PMC2363753 (1).
- Die neun Evidence-Inference-Volltexte und die XML-`table-wrap`-Blöcke
  wurden am 2026-11-12 geprüft. Ergebnis: **3 Records vollständig belegbar**
  (PMC3654355), **4 teilweise** (PMC3136370, Mittelwerte ja, SDs nein),
  **26 nicht belegbar**.
- Die vollständige Prüfung steht in
  [`holdout_fulltext_audit_20261112.md`](holdout_fulltext_audit_20261112.md)
  und [`holdout_fulltext_audit_20261112.json`](holdout_fulltext_audit_20261112.json).
- Die 26 nicht belegbaren Records bleiben `unverifiable`; die vier
  teilweise belegbaren Records bleiben unvollständig. Eine Nutzung als
  belastbarer Holdout ist damit nicht möglich.

### 3.3 Strukturell ausgeschlossene Records

- **57 Records** sind strukturell kein gültiger Interventions-Kontroll-
  Vergleich (Baseline, Vorher-Nachher, observational, gepoolt, Median,
  Ein-Arm usw.).
- Auch außerhalb des Freeze sind **30** solche Records; sie sind keine
  Holdout-Kandidaten.

### 3.4 Nicht streng vollständige Records

- **289 Records** sind nicht streng vollständig.
- **173 Records aus 40 Artikeln** liegen außerhalb des Freeze, haben aber nur
  0–4 der required fields; sie sind ohne neue Annotation nicht poolbar.
- Diese Records sind kein unabhängiger Holdout, solange die fehlenden Werte
  nicht belegt ergänzt und geprüft sind.

### 3.5 Volltextprüfung 2026-11-12

- **3/33 Records vollständig belegbar:** Records 274–276 aus PMC3654355
  (Body weight, Fat mass, Visceral fat area; Tabelle 2 mit Mean und SD).
- **4/33 Records teilweise belegbar:** Records 556–559 aus PMC3136370;
  die Per-Protocol-Mittelwerte sind belegt, die zugehörigen SDs fehlen.
- **26/33 Records nicht belegbar:** fehlende Werte stehen nicht in den
  verfügbaren Volltexten/XML-Tabellen; einzelne Zahlentreffer sind
  Literaturzitate, andere Outcomes oder bloße Ziffernfolgen.
- **69 fehlende Felder:** 13 belegt, 56 nicht belegt. Keine Schätzung,
  keine CI-/SE-Umrechnung, keine Zusammenführung getrennter Arme.

### 3.6 Artikeldisjunktheit

- **50 Artikel** der 699er-Daten liegen außerhalb des Freeze.
- **15** davon enthalten auditierte, aber nicht nutzbare Records
  (33 `unverifiable`, 30 `structural_exclude`).
- **40** enthalten nicht streng vollständige Records.
- **0** enthalten einen aktuell nutzbaren C1-Record.
- Die 9 Artikel mit den 33 `unverifiable`-Records sind die einzige potenzielle
  artikeldisjunkte Gruppe — aber ohne verifizierte Werte.

## 4. Entscheidung

**G5 ist mit den vorhandenen Daten nicht erfüllt.** Es gibt keinen
belastbaren, bereits verifizierten Holdout. Der einzige vollständige Kandidat
umfasst **3 Records aus einem Artikel** (PMC3654355), alle kontinuierlich.
Das ist ein möglicher Smoke-Test, aber kein belastbarer G5-Holdout. Deshalb:

- **kein Modelllauf** auf einem provisorischen Holdout,
- **kein Einfrieren** des 3-Record-Kandidaten als G5-Holdout,
- **keine Wiederverwendung** der 249 Test-Records,
- **keine Behandlung** von `unverifiable` als Wahrheit,
- **keine autonome Freigabe** von v6c.

## 5. Optionen

### Option A - 33 unverifiable Records mit Volltexten prüfen

**Geprüft; Ergebnis unzureichend.** Die neun Volltexte/XML-Tabellen belegen
nur 3 vollständige Records (PMC3654355) und 4 teilweise (PMC3136370). Der
3-Record-Kandidat ist artikeldisjunkt, aber zu klein und nur kontinuierlich;
er ist höchstens ein Smoke-Test, kein G5-Holdout.

### Option B - neuen externen Holdout beschaffen

**Empfohlen.** Neue Artikel/Records außerhalb der Yun-699 und außerhalb des
Freeze annotieren, artikeldisjunkt halten und vor dem Lauf hashen. Das ist
der einzige Weg zu einem belastbaren, nicht bereits verbrauchten G5-Nachweis.

### Option C - 249er-Test erneut verwenden

**Ausgeschlossen.** Der Test ist verbraucht; eine erneute Auswertung wäre kein
unabhängiger Nachweis.

### Option D - nur assistiert arbeiten

**Fallback.** v6c nur mit 100 % menschlicher Prüfung und ohne automatisches
Pooling; kein Gate-Pass und keine autonome Freigabe.

## 6. Empfehlung

1. **Option B priorisieren:** neuen externen Holdout beschaffen.
2. **Option A ist geprüft und als G5-Holdout verworfen:** nur 3 vollständige
   Records aus einem Artikel; optional als `smoke_test_only` verwenden.
3. **Kein Modelllauf**, solange kein Holdout-Manifest mit Hashes und
   Artikeldisjunktheit vorliegt.
4. **Holdout-Manifest-Schema** aus
   [`holdout_manifest_schema.json`](holdout_manifest_schema.json) verwenden.

## 7. Nächste Schritte

1. **Neue externe Daten annotieren**; die 9 Volltexte sind geprüft, aber
   nicht ausreichend.
2. Holdout-Kandidaten artikeldisjunkt auswählen; keine 249/26-Records.
3. Quellen und Werte prüfen; `unverifiable` nicht als verifiziert zählen.
4. Input, Referenz, Prompt und Modellkonfiguration vor dem Lauf hashen.
5. `holdout_manifest.json` nach Schema anlegen und G5 prüfen.
6. Erst dann einen neuen Kandidaten entwickeln und einen freigegebenen
   Evaluationslauf planen.

## 8. Artefakte

- Volltext-Audit: [`holdout_fulltext_audit_20261112.md`](holdout_fulltext_audit_20261112.md)
- Volltext-Audit JSON: [`holdout_fulltext_audit_20261112.json`](holdout_fulltext_audit_20261112.json)
- Schema: [`holdout_manifest_schema.json`](holdout_manifest_schema.json)
- Gates: [`c1_acceptance_gates_v1.md`](c1_acceptance_gates_v1.md)
- Entscheidung: [`decision_v6c.md`](decision_v6c.md)
- Freeze: [`../../validation/c1_freeze_manifest.json`](../../validation/c1_freeze_manifest.json)
- Audit: [`../../validation/yun_audit_410_summary.json`](../../validation/yun_audit_410_summary.json)

**Kein Modelllauf. Keine Prompt-Änderung. Keine Test-Wiederverwendung.**
