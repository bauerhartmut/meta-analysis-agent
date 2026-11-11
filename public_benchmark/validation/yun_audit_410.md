# Yun-Referenzaudit: 410 streng vollständige Records

Stand: 2026-11-11

Datenbasis: Yun-Release `1bc768d4d098c727c9866eeff909297c38a3e84c`.
Geprüft wurden alle 410 Records, die die strenge Feldregel erfüllen
(261 kontinuierlich, 149 binär) aus 85 Artikeln.

Status: **Vollaudit abgeschlossen; keine Modellvorhersage; A und B unverändert.**

## 1. Ergebnis

| Auditstatus | Records | Bedeutung |
|---|---:|---|
| `verified_exact` | 239 | Beide Armwerte stehen als Paar im Text; keine strukturelle Auffälligkeit. |
| `verified_table` | 35 | Alle Referenzwerte stehen im Text/Tabellenkontext; keine vollständige klinische Einzelprüfung. |
| `corrected_with_source` | 1 | Referenzwert mit Textstelle korrigiert. |
| `structural_exclude` | 57 | Kein gültiger Interventions-Kontroll-Vergleich. |
| `unverifiable` | 78 | Mindestens ein Referenzwert im bereitgestellten Text nicht belegbar. |
| **Summe** | **410** | |

**Für C1 nutzbar:** 275 Records (`verified_exact` + `verified_table` +
`corrected_with_source`). **Nicht nutzbar:** 135 Records (57 strukturell,
78 nicht ausreichend belegt).

Nach Outcome-Typ:

| Typ | Verifiziert exakt | Tabelle | Korrigiert | Strukturell | Nicht belegt | Nutzbar |
|---|---:|---:|---:|---:|---:|---:|
| Kontinuierlich | 172 | 1 | 1 | 34 | 53 | 174 |
| Binär | 67 | 34 | 0 | 23 | 25 | 101 |
| **Gesamt** | **239** | **35** | **1** | **57** | **78** | **275** |

## 2. Methodik

1. Auswahl aller 410 Records mit vollständigen Pflichtfeldern.
2. Exakte Suche nach den Armwerten im mitgelieferten Abstract-/Results-Text,
   inklusive Zahlenvarianten und Tabellenkontext.
3. Paarweise Prüfung, ob mittlerer Wert und SD bzw. Ereigniszahl und N
   räumlich zusammenstehen.
4. Manuelle Strukturprüfung der auffälligen Records: Baseline-Outcome,
   Vorher-Nachher-Vergleich, observationales Design, gepoolte Analyse,
   Median-Outcome, Ein-Arm-Studie.
5. Keine Ergänzung fehlender Werte; keine Schätzung. `unverifiable` bedeutet
   nicht „falsch“, sondern „mit dem bereitgestellten Text nicht belegbar“.

Die Referenzwerte und die kuratierten Werte sind getrennt. Die Rohdaten und
`annotated_rct_dataset.json` wurden nicht verändert.

## 3. Strukturelle Ausschlüsse

| Grund | Records |
|---|---:|
| Baseline-Charakteristik statt Outcome | 25 |
| Vorher-Nachher- oder Baseline-Comparator | 17 |
| Observationales Design ohne Randomisierung | 6 |
| Gepoolte Analyse statt einzelner RCT | 6 |
| Median statt Mittelwert | 1 |
| Quasi-experimentelle Kohorte mit falschem N | 1 |
| Ein-Arm-Vorher-Nachher-Studie | 1 |
| **Summe** | **57** |

Wichtige Fälle:

- **PMC3309311 (IDs 61-66):** observationaler MRI-Vergleich von drei
  Rückenschmerzgruppen, keine Randomisierung.
- **PMC3687098 (IDs 84-87):** gepoolte Sicherheitsanalyse aus 25 Studien,
  keine einzelne RCT-2x2-Tabelle.
- **PMC4230312 (IDs 531/532):** gepoolte Daten aus vier Studien.
- **PMC3195393 (IDs 51-53):** Vorher-Nachher-Vergleich einer
  Restraint-Reduktionsmaßnahme.
- **PMC3580751 (ID 83):** quasi-experimentelle Studie; N 940/1831 ist die
  Gesamtkohorte, nicht die No-VAP-Untergruppe des Outcomes.
- **PMC5086025 (ID 178):** Ein-Arm-Studie mit 26 Postinterventionsfällen.
- **PMC4678179 (ID 398):** Median Overall Survival, kein Mean/SD.

## 4. Korrektur

Record **12 (PMC2667135)**:

- Referenz: Interventions-SD `23,34`
- Tabelle: `25.4 (12.34)` vs. `13.5 (9.49)`
- Kuratiert: `12,34`
- Die Originalreferenz bleibt in `reference_values` erhalten; die Korrektur
  steht separat in `correction`.

## 5. Nicht ausreichend belegte Records

78 Records haben mindestens ein Referenzfeld, das im bereitgestellten
Abstract-/Results-Text nicht vollständig belegbar ist. Häufige Ursachen:

- SD aus CI/SE zurückgerechnet, ohne dass die Rechnung im Einzelfall
  nachvollzogen werden konnte,
- Ereigniszahlen aus Prozenten oder Inzidenzraten abgeleitet,
- Werte nur in Abbildungen oder Grafiktabellen,
- Gruppengrößen aus Tabellen inferiert.

Diese Records bleiben im Audit-Ledger, sind aber für C1 nicht freigegeben.
Ein späterer Volltext-Audit kann sie gegebenenfalls hochstufen; ohne
Textbeleg werden sie nicht als verifiziert gezählt.

## 6. Artefakte

| Datei | Inhalt |
|---|---|
| `yun_audit_410.jsonl` | 410 kuratierte Records mit Status, Werten und Korrektur |
| `yun_audit_410_summary.json` | Zählungen nach Status, Typ und Ausschlussgrund |
| `yun_audit_410_ledger.json` | Arbeitsledger mit Evidenzsnippets; lokal, nicht versioniert |
| `yun_audit_30.md` | Vorheriger 30-plus-3-Audit |

## 7. Grenzen

- Der Audit prüft die von Yun bereitgestellten Abstract-/Results-Auszüge,
  nicht die vollständigen PDFs.
- `verified_table` ist eine Text-/Tabellenprüfung, keine vollständige
  klinische Neuannotation.
- Die 78 nicht belegten Records sind nicht automatisch falsch; sie sind
  lediglich nicht belastbar verifiziert.
- Kein Modelllauf, keine Prompt-Anpassung, kein A/B-Vergleich.

## 8. Empfehlung

Für C1 die **275 nutzbaren Records** verwenden und die 135 übrigen getrennt
als ausgeschlossen/nicht belegt berichten. Vor dem Testlauf den kuratierten
Datensatz hashen und einfrieren. Die 78 nicht belegten Records erst nach
einem Volltext-Audit wieder aufnehmen.
