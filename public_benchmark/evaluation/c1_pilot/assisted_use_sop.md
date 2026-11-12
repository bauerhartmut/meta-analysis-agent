# SOP: Assistierte C1-Nutzung mit 100 % menschlicher Prüfung

Stand: 2026-11-12
Status: **ACTIVE - Interimsfreigabe, kein Gate-Pass**
Geltung: v6c und jeder andere C1-Kandidat, der G1-G5 nicht vollständig besteht

## 1. Zweck und Abgrenzung

Diese SOP regelt die **assistierte** Nutzung eines C1-Extraktionskandidaten.
Sie ist keine Freigabe für autonome oder ungeprüfte numerische Extraktion und
kein Bestehen der [Gates v1](c1_acceptance_gates_v1.md).

Zulässig ist nur:

- der Kandidat erzeugt einen **Vorschlag** pro Record,
- ein Mensch prüft **100 % aller N-, Mean-, SD- und Event-Werte**,
- nur bestätigte Werte dürfen in eine nachgelagerte Meta-Analyse,
- fehlende Werte bleiben `null`,
- es gibt **kein automatisches Pooling**.

Unzulässig ist:

- die Bezeichnung „validiert“, „freigegeben“ oder „autonom“,
- die Übernahme ungeprüfter Modellwerte,
- Schätzen, Imputieren oder Ersetzen durch 0,
- die Zusammenführung getrennter Arme, Outcomes oder Zeitpunkte,
- die Verwendung des verbrauchten 249er-Tests zur Entwicklung.

## 2. Rollen und Voraussetzungen

| Rolle | Aufgabe |
|---|---|
| Operator | startet den freigegebenen Lauf, verwaltet Record-Queue und Artefakte |
| Reviewer | prüft jeden Record vollständig gegen die Quelle; muss ein Mensch sein |
| Quelle | im Record referenzierter Abstract-/Results-Text bzw. Tabelle |

Vor jedem Record müssen feststehen:

- `record_id`, `study_id`, `pmcid`,
- Intervention, Comparator und Outcome aus der ICO,
- `outcome_type` (`continuous` oder `binary`),
- der nach der [Zeitpunktregel](timepoint_rule.md) gültige Zeitpunkt,
- der Pfad zur Quelle,
- Prompt-Version und Modell-ID des Laufs.

Der Reviewer darf keine Referenzwerte aus dem Testsplit und keine
Golden-/Audit-Werte als alleinige Quelle verwenden. Die Prüfung erfolgt gegen
den Studientext, nicht gegen die Modellausgabe.

## 3. Prüfablauf pro Record

### 3.1 ICO und Zeitpunkt

1. Intervention, Comparator und Outcome wörtlich gegen die ICO abgleichen.
2. Prüfen, ob der Record wirklich ein Interventions-Kontroll-Vergleich ist.
3. Zeitpunkt nach der verbindlichen Regel bestimmen:
   - ICO-Zeitpunkt, sonst
   - unmittelbarer Post-Test, sonst
   - frühester vollständiger Follow-up für beide Arme.
4. Baseline, Change-Score, Peak und gemischte Zeitpunkte ausschließen.
5. Zeitpunkt und Tabellen-/Zeilenangabe in der Prüfnotiz festhalten.

### 3.2 Quelle und Zelle

1. Die genannte Tabelle, Zeile und Spalte in der Quelle öffnen.
2. Armbezeichnungen und Einheiten prüfen.
3. Bei Tabellen mit mehreren Zeitpunkten die richtige Spalte wählen.
4. Bei binären Zeilen `x/N` den Nenner der Zeile verwenden, nicht die
   Gesamtgruppengröße, sofern die ICO nichts anderes vorgibt.
5. Bei fehlender Zelle prüfen, ob ein anderer vollständiger Zeitpunkt
   existiert; nicht zwischen Armen oder Outcomes mischen.

### 3.3 Numerische Prüfung

Jedes erwartete Feld einzeln prüfen:

- `intervention_n`
- `comparator_n`
- `intervention_mean`
- `intervention_sd`
- `comparator_mean`
- `comparator_sd`
- `intervention_events`
- `comparator_events`

Für jedes Feld genau einen Status vergeben:

| Status | Bedeutung | Weitergabe |
|---|---|---|
| `confirmed` | Modellwert stimmt exakt mit der Quelle überein | ja |
| `corrected` | Modellwert war falsch; korrigierter Wert und Quelle dokumentiert | ja, nur mit Korrekturbeleg |
| `missing` | Wert ist in der Quelle nicht berichtet | nein, `null` |
| `rejected` | Quelle, Arm, Zeitpunkt oder Outcome nicht eindeutig | nein, Record ausschließen |

Zusätzlich prüfen:

- N ist die analysierte Gruppengröße für dieses Outcome.
- Events liegen zwischen 0 und N.
- Mean/SD gehören zum selben Arm, Outcome und Zeitpunkt.
- Einheiten sind konsistent; keine stillschweigende Skalierung.
- `source_note` nennt Zeitpunkt und Tabelle/Zeile, keine freie Begründung.

### 3.4 Korrekturen

Eine Korrektur ist nur zulässig, wenn die Quelle den Wert direkt zeigt.
Dokumentiert werden mindestens:

- Record-ID und Feld,
- alter Modellwert,
- korrigierter Wert,
- wörtliche Quellenstelle oder Tabellen-/Zeilenangabe,
- Zeitpunkt und Einheit,
- Reviewer und Datum,
- Grund der Korrektur.

Keine Korrektur durch „plausibles“ Schätzen, CI-/SE-Umrechnung oder
Expertenwissen. Wenn die Quelle den Wert nicht direkt berichtet, bleibt er
`null`.

## 4. Record-Entscheidung

Ein Record darf nur weitergegeben werden, wenn:

- alle erwarteten Felder geprüft sind,
- jedes Feld `confirmed`, `corrected` oder `missing` ist,
- keine `rejected`-Felder offen sind,
- die ICO- und Zeitpunktprüfung dokumentiert ist,
- die Quelle für jeden korrigierten Wert nachvollziehbar ist.

Bei einem `rejected`-Record:

1. Record nicht ins Pooling geben.
2. Grund und Quelle dokumentieren.
3. Keine Ersatzwerte erfinden.
4. Den Record als ausgeschlossen markieren.

## 5. Übergabe und Pooling

- Export nur bestätigter bzw. belegter Werte.
- `missing` bleibt `null`; der Record kann je nach Analyse ausgeschlossen
  werden.
- Kein automatisches Pooling, keine automatische Studienauswahl.
- Die Übergabe enthält pro Wert Status und Quellenbeleg.
- Die Bezeichnung lautet **„assistiert geprüft“**, nicht „validiert“ oder
  „Gate-bestanden“.

Empfohlene Prüfdatei `assisted_review.jsonl` mit einer Zeile pro Record:

```json
{
  "record_id": 0,
  "study_id": "",
  "pmcid": "",
  "candidate_run_id": "",
  "reviewer": "",
  "reviewed_at": "",
  "ico_confirmed": true,
  "timepoint": "",
  "fields": {
    "intervention_n": {"status": "confirmed", "value": null, "source": ""},
    "comparator_n": {"status": "confirmed", "value": null, "source": ""},
    "intervention_mean": {"status": "confirmed", "value": null, "source": ""},
    "intervention_sd": {"status": "confirmed", "value": null, "source": ""},
    "comparator_mean": {"status": "confirmed", "value": null, "source": ""},
    "comparator_sd": {"status": "confirmed", "value": null, "source": ""},
    "intervention_events": {"status": "confirmed", "value": null, "source": ""},
    "comparator_events": {"status": "confirmed", "value": null, "source": ""}
  },
  "record_status": "accepted",
  "notes": ""
}
```

## 6. Stop-Regeln

Der Record wird sofort gestoppt und als `rejected` markiert, wenn:

- ICO oder Outcome nicht eindeutig ist,
- der Zeitpunkt nicht regelkonform bestimmbar ist,
- zwei Tabellen/Zeilen widersprüchliche Werte nennen,
- Armzuordnung oder Einheit unklar ist,
- N und Events nicht zusammenpassen und die Quelle den Widerspruch nicht
  auflöst,
- die Quelle fehlt oder nicht lesbar ist,
- der Modellwert nur durch Schätzung „gerettet“ werden könnte.

Ein Stopp ist kein Modellfehler, sondern ein Prüfergebnis. Er wird dokumentiert,
nicht überschrieben.

## 7. Grenzen

- Diese SOP erzeugt **keinen** G1-G5-Pass.
- Sie ersetzt keine unabhängige Holdout-Validierung.
- Sie sagt nichts über die autonome Genauigkeit des Kandidaten aus.
- Der 249er-Test bleibt verbraucht und darf nicht zur Entwicklung oder
  Optimierung verwendet werden.
- v6c hat 101/249 Records mit mindestens einem Fehler; die Prüfung ist
  deshalb praktisch für jeden Record erforderlich.

## 8. Referenzen

- [Gates v1](c1_acceptance_gates_v1.md)
- [Entscheidung v6c](decision_v6c.md)
- [Zeitpunktregel](timepoint_rule.md)
- [Test-Fehleranalyse](runs_test/c1_test_20261111_v6c/test_error_analysis.md)
- [Holdout-Plan](holdout_plan_20261112.md)

**Kein Modelllauf. Keine Prompt-Änderung. Keine automatische Freigabe.**
