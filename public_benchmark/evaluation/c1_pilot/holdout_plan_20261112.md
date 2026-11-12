# C1-Holdout-Plan 2026-11-12

Stand: 2026-11-12
Status: **BLOCKED - kein unabhängiger Holdout aus den vorhandenen C1-Daten verfügbar**
Entscheidung: **kein Modelllauf; zuerst Datenbeschaffung und Volltextprüfung**

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
- Die vorhandenen Quellen sind Yun-Abstract-/Results-Markdowns; die
  Referenzwerte sind darin nicht belegbar. Die vier PDFs im Yun-Repo sind
  Beispiel-Forest-Plots bzw. eine Fallstudie, keine Artikelvolltexte.
- Eine Nutzung als Holdout ist erst nach externer Volltextbeschaffung und
  erneuter klinischer Prüfung möglich. Der aktuelle Status bleibt
  `unverifiable`.

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

### 3.5 Artikeldisjunktheit

- **50 Artikel** der 699er-Daten liegen außerhalb des Freeze.
- **15** davon enthalten auditierte, aber nicht nutzbare Records
  (33 `unverifiable`, 30 `structural_exclude`).
- **40** enthalten nicht streng vollständige Records.
- **0** enthalten einen aktuell nutzbaren C1-Record.
- Die 9 Artikel mit den 33 `unverifiable`-Records sind die einzige potenzielle
  artikeldisjunkte Gruppe — aber ohne verifizierte Werte.

## 4. Entscheidung

**G5 ist mit den vorhandenen Daten nicht erfüllbar.** Es gibt keinen
unabhängigen, bereits verifizierten Holdout. Deshalb:

- **kein Modelllauf** auf einem provisorischen Holdout,
- **keine Wiederverwendung** der 249 Test-Records,
- **keine Behandlung** von `unverifiable` als Wahrheit,
- **keine autonome Freigabe** von v6c.

## 5. Optionen

### Option A - 33 unverifiable Records mit Volltexten prüfen

**Möglich, aber nicht sofort.** Voraussetzung: 9 Artikelvolltexte beschaffen
und die 33 Records klinisch gegen die Referenz prüfen. Erst danach kann aus
ihnen ein kleiner Holdout werden. Die Stichprobe wäre klein und müsste vor
dem Lauf als ausreichend oder nicht ausreichend bewertet werden.

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
2. **Option A nur als Fallback:** 9 Volltexte beschaffen und die 33 Records
   prüfen; erst bei verifizierten Werten als Holdout-Kandidaten führen.
3. **Kein Modelllauf**, solange kein Holdout-Manifest mit Hashes und
   Artikeldisjunktheit vorliegt.
4. **Holdout-Manifest-Schema** aus
   [`holdout_manifest_schema.json`](holdout_manifest_schema.json) verwenden.

## 7. Nächste Schritte

1. Entscheiden, ob 9 Volltexte beschafft oder neue externe Daten annotiert
   werden.
2. Holdout-Kandidaten artikeldisjunkt auswählen; keine 249/26-Records.
3. Quellen und Werte prüfen; `unverifiable` nicht als verifiziert zählen.
4. Input, Referenz, Prompt und Modellkonfiguration vor dem Lauf hashen.
5. `holdout_manifest.json` nach Schema anlegen und G5 prüfen.
6. Erst dann einen neuen Kandidaten entwickeln und einen freigegebenen
   Evaluationslauf planen.

## 8. Artefakte

- Schema: [`holdout_manifest_schema.json`](holdout_manifest_schema.json)
- Gates: [`c1_acceptance_gates_v1.md`](c1_acceptance_gates_v1.md)
- Entscheidung: [`decision_v6c.md`](decision_v6c.md)
- Freeze: [`../../validation/c1_freeze_manifest.json`](../../validation/c1_freeze_manifest.json)
- Audit: [`../../validation/yun_audit_410_summary.json`](../../validation/yun_audit_410_summary.json)

**Kein Modelllauf. Keine Prompt-Änderung. Keine Test-Wiederverwendung.**
