# P0: Externer C1-Holdout - Beschaffungsplan

Stand: 2026-11-12
Status: **ABSTRACT SCREENED - 152 ausgeschlossen, 65 manuell, 379 vorlaeufig fuer Volltext; nicht eingefroren, nicht G5-valid**
Ziel: 30 Artikel, 100 Records, artikeldisjunkt zu Dev und zum verbrauchten Test

## 1. Entscheidung

| Feld | Festlegung |
|---|---|
| Quelle | **PMC Open Access Subset**, abgerufen über die **Europe PMC REST API** |
| Suchoberfläche | `https://www.ebi.ac.uk/europepmc/webservices/rest/search` |
| Volltext | `https://www.ebi.ac.uk/europepmc/webservices/rest/PMC<ID>/fullTextXML` |
| Ziel-Artikelzahl | **30** |
| Ziel-Recordzahl | **100** (ca. 3-4 Records pro Artikel) |
| Annotationsverantwortlich | **bauerhartmut** (Projektleitung; Primärannotation und klinische Freigabe) |
| Technische Unterstützung | Codebuff/Assistenz bei Screening und Formalprüfung, **keine klinische Verantwortung** |
| Manifest | [`holdout_manifest_p0_20261112.json`](holdout_manifest_p0_20261112.json) |
| Manifest-Schema | [`holdout_manifest_schema.json`](holdout_manifest_schema.json) |
| Status des Manifests | `draft`; Artikel-IDs und Hashes werden erst nach der Auswahl befüllt |

Die Quelle ist offen zugänglich und liefert strukturierte Volltexte. Sie ist
nicht mit dem Yun-699-Bestand identisch; die Artikeldisjunktheit wird vor der
Aufnahme explizit geprüft.

### 1.1 Ausführung 2026-11-12

Die breite P0-Query ergab **109.833** Treffer. Vor der Sichtung einzelner
Treffer wurde der Export auf einen vollständig indexierten Monatsframe
begrenzt: **Erstpublikation 2026-09-01 bis 2026-09-30**. Das ist eine
dokumentierte Frame-Entscheidung, keine Auswahl nach Ergebnissen.

| Kennzahl | Wert |
|---|---:|
| Treffer im Monatsframe | 596 |
| Exportierte Records | 596 |
| Eindeutige PMCIDs | 596 |
| Ohne PMCID | 0 |
| Mit Abstract | 596 |
| Mit Journal | 596 |
| Überschneidung Yun | 0 |
| Überschneidung Freeze/Dev/Test | 0 |
| **Artikeldisjunkt** | **596** |
| Duplikate | 0 |

Die 596 sind **Query-Label-RCTs** und noch keine endgültig geeigneten
Holdout-Artikel. Das Abstract-Screening ist abgeschlossen; Volltextscreening
auf Parallelgruppen, zwei Arme und extrahierbare N/Mean/SD/Events steht aus.

Artefakte:
[`candidate_summary.md`](holdout_p0_20261112/candidate_summary.md),
[`candidates.jsonl`](holdout_p0_20261112/candidates.jsonl),
[`article_disjoint_check.json`](holdout_p0_20261112/article_disjoint_check.json).

### 1.2 Abstract-Screening 2026-11-12

Regelbasierte Erstprüfung der 596 Kandidaten nach
[`screening_criteria_v1.json`](holdout_p0_20261112/screening_criteria_v1.json)
(Kriterienversion 1.1). Kein Modellaufruf, keine Volltextprüfung.

| Entscheidung | Anzahl |
|---|---:|
| Ausschluss | **152** |
| Manuelle Prüfung | **65** |
| Vorlaeufig fuer Volltext | **379** |
| **Gesamt** | **596** |

Jeder Ausschluss ist mit PMCID, Regel-ID, Begruendung und Textbeleg in
[`screening_exclusions_v1.jsonl`](holdout_p0_20261112/screening_exclusions_v1.jsonl)
dokumentiert. Alle Entscheidungen stehen in
[`screening_decisions_v1.jsonl`](holdout_p0_20261112/screening_decisions_v1.jsonl).

Die 379 Volltextkandidaten sind **nicht** endgueltig eingeschlossen. Die 65
manuellen Faelle sind vor der Volltextauswahl zu adjudizieren. Mehrfachgruende
sind moeglich; die Regelzahlen sind nicht additiv.

## 2. Auswahlkriterien

### 2.1 Einschluss

- Englischsprachige RCTs aus dem PMC-Open-Access-Subset.
- Parallelgruppen-Design mit genau zwei relevanten Armen (Intervention und
  Comparator/Kontrolle).
- Mindestens ein Outcome, für das die C1-Felder direkt berichtet werden:
  - kontinuierlich: N, Mean, SD für beide Arme,
  - binär: N und Events für beide Arme.
- Volltext mit Tabelle oder Results-Abschnitt, aus dem die Werte direkt
  hervorgehen.
- Artikel nicht in den Yun-699-Artikeln und nicht im C1-Freeze enthalten.
- Kein Artikel aus dem verbrauchten 249er-Test.
- Eindeutiger Zeitpunkt nach der [C1-Zeitpunktregel](timepoint_rule.md)
  bestimmbar.

### 2.2 Ausschluss

- Crossover-, Cluster- oder Ein-Arm-Studien.
- Nur Abstract ohne ausreichende Werte.
- Nur Median, Range, CI oder SE ohne direkt berichteten Mean/SD.
- Sekundäranalysen ohne eigenständige Armwerte.
- Studien mit unklarer Armzuordnung oder unklarem Outcome.
- Artikel, die bereits im Yun-699-Bestand oder im Freeze vorkommen.
- Nicht offen lizenzierte Volltexte.

### 2.3 Suchfilter

Ausgangsquery für Europe PMC:

```text
(OPEN_ACCESS:Y) AND (HAS_FT:Y)
AND (PUB_TYPE:"Randomized Controlled Trial")
AND (LANG:"eng")
```

Die Query wird vor der Auswahl dokumentiert. Für den ersten Export wurde der
Frame auf September 2026 begrenzt, weil die ungefilterte Query 109.833
Treffer liefert. Die Kandidaten werden nach Titel/Abstract gescreent; die
endgültige Aufnahme erfolgt erst nach Volltextprüfung.

### 2.4 Artikeldisjunktheit

Vor der Aufnahme wird jedes PMC-ID gegen folgende Mengen geprüft:

- alle PMCIDs im Yun-699-Bestand,
- alle PMCIDs im C1-Freeze (Dev + Test),
- alle bereits verwendeten Holdout- oder Smoke-Test-Artikel.

Ein Artikel mit Überschneidung wird verworfen, nicht umetikettiert. Die
Prüfung wird als `article_disjoint_check.json` dokumentiert.

## 3. Stichprobe und Power

- **30 Artikel** sind das Minimum; weniger Artikel werden nicht als Holdout
  eingefroren.
- **100 Records** sind das Ziel; weniger als 100 werden nur akzeptiert, wenn
  die Artikelzahl 30 erreicht und die Rekrutierung vorab dokumentiert
  angepasst wurde.
- Zielverteilung: mindestens **40 kontinuierliche** und **40 binäre**
  Records; der Rest darf ergänzt werden, sofern beide Typen ausreichend
  vertreten sind.
- Die Zielgröße ist eine Präzisions- und Machbarkeitsvorgabe, **keine formale
  Power-Rechnung**. Sie verhindert vor allem die Überinterpretation eines
  3-Record-Smoke-Tests.
- Die Records werden artikelweise ausgewählt, nicht als zufällige Einzelwerte.
- Ein 3-Record-Smoke-Test ersetzt diesen Holdout nicht.

## 4. Annotation

### 4.1 Verantwortlichkeit

**Primärannotation und klinische Freigabe: bauerhartmut.**

Die Annotation erfolgt nach der [SOP für assistierte Nutzung](assisted_use_sop.md)
mit dem Unterschied, dass hier die Referenzwerte für den Holdout erstellt
werden:

- 100 % menschliche Prüfung aller N-, Mean-, SD- und Event-Werte,
- ICO-, Zeitpunkt- und Tabellenprüfung,
- Quellenbeleg pro Wert,
- keine Imputation, keine CI-/SE-Umrechnung,
- keine Zusammenführung getrennter Arme.

Technische Assistenz darf Texte extrahieren und Formalprüfungen vornehmen.
Die klinische Entscheidung und die Freigabe des Referenzwerts bleiben
menschlich.

### 4.2 Zweitprüfung

Eine unabhängige Zweitprüfung von **20 % der Records** ist empfohlen. Bis ein
zweiter Reviewer benannt ist, bleibt das Manifest `draft`. Die Beschaffung
kann starten; das Einfrieren erst nach der Zweitprüfung oder nach einer
dokumentierten Entscheidung, dass die Primärprüfung ausreicht.

### 4.3 Record-Status

Jeder Record erhält vor dem Einfrieren einen Status:

- `verified_exact`: Werte direkt und exakt aus der Quelle,
- `verified_table`: Werte aus einer Tabelle, mit Zeilen-/Spaltenbeleg,
- `corrected_with_source`: Modell-/Vorwert korrigiert, Quelle dokumentiert.

`unverifiable` ist im Holdout nicht zulässig. Nicht belegbare Kandidaten
werden verworfen, nicht als `null` in den Holdout aufgenommen.

## 5. Manifest-Lebenszyklus

1. **Draft:** `holdout_manifest_p0_20261112.json` mit Quelle, Zielgröße und
   Verantwortlichkeit; keine Artikel-IDs, keine Hashes.
2. **Selected:** 30 Artikel und 100 Records ausgewählt; `article_ids` und
   `record_ids_sha256` ergänzt.
3. **Verified:** Referenzwerte geprüft; `record_status_distribution` gefüllt.
4. **Frozen:** Input, Referenz, Prompt, Modellkonfiguration und Gate-Policy
   gehasht; `status=frozen`; `prompt_frozen_before_run=true`.
5. **Evaluated:** genau ein Lauf; `status=evaluated`; Gate-Report mit
   [`check_c1_gates.py`](../../scripts/check_c1_gates.py).

Das Draft-Manifest ist **absichtlich nicht G5-valid**. Es darf nicht als
Nachweis für eine Freigabe verwendet werden.

## 6. Artefakte und Ablage

| Artefakt | Pfad |
|---|---|
| Screening-Liste | `public_benchmark/evaluation/c1_pilot/holdout_p0_20261112/candidates.jsonl` |
| Screening-Kriterien | `public_benchmark/evaluation/c1_pilot/holdout_p0_20261112/screening_criteria_v1.json` |
| Alle Screening-Entscheidungen | `public_benchmark/evaluation/c1_pilot/holdout_p0_20261112/screening_decisions_v1.jsonl` |
| Ausschluesse mit Beleg | `public_benchmark/evaluation/c1_pilot/holdout_p0_20261112/screening_exclusions_v1.jsonl` |
| Disjunktheitsprüfung | `public_benchmark/evaluation/c1_pilot/holdout_p0_20261112/article_disjoint_check.json` |
| Holdout-Input | `public_benchmark/evaluation/c1_pilot/holdout_p0_20261112/input.jsonl` |
| Holdout-Referenz | `public_benchmark/evaluation/c1_pilot/holdout_p0_20261112/reference.jsonl` |
| Manifest | `public_benchmark/evaluation/c1_pilot/holdout_manifest_p0_20261112.json` |
| Gate-Report | `public_benchmark/evaluation/c1_pilot/gate_report_holdout_p0.json` |

## 7. Stopp- und Abbruchregeln

Die Beschaffung wird gestoppt, wenn:

- weniger als 30 artikeldisjunkte RCTs übrig bleiben,
- weniger als 100 belegbare Records erreicht werden und keine vorab
  dokumentierte Erweiterung erfolgt,
- ein Artikel nicht eindeutig artikeldisjunkt ist,
- die Volltexte nicht offen verfügbar sind,
- die Referenzwerte nur über CI/SE/Median ableitbar wären,
- die Zweitprüfung oder die klinische Freigabe nicht dokumentiert ist,
- Artikel-IDs oder Hashes im Manifest fehlen.

Bei einem Stopp wird das Manifest nicht eingefroren. Es wird auch nicht
nachträglich aufgeweicht.

## 8. Nächster konkreter Schritt

1. **Erledigt:** Europe-PMC-Query ausgeführt; 596 artikeldisjunkte
   Kandidaten exportiert.
2. **Erledigt:** Abstract-Screening; 152 ausgeschlossen, 65 manuell,
   379 vorlaeufig fuer Volltext.
3. **Als Naechstes:** 65 manuelle Faelle adjudizieren; 379 Volltext-
   kandidaten pruefen und 30 Artikel auswaehlen.
4. 100 Records nach C1-Regeln annotieren.
5. Disjunktheit, Quellen und Werte prüfen.
6. Manifest befüllen, hashen und einfrieren.
7. Erst dann den Kandidatenlauf planen.

**Kein Modelllauf. Keine Prompt-Änderung. Keine Test-Wiederverwendung.**

## 9. Referenzen

- [Nächster-Kandidat-Plan](next_candidate_plan.md)
- [Holdout-Plan](holdout_plan_20261112.md)
- [Manifest-Schema](holdout_manifest_schema.json)
- [SOP assistierte Nutzung](assisted_use_sop.md)
- [Gates v1](c1_acceptance_gates_v1.md)
- [Gate-Checker](../../scripts/check_c1_gates.py)
