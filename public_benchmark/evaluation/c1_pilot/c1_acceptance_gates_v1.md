# C1-Akzeptanzgates v1

Stand: 2026-11-11
Status: **ADOPTED - Projektstandard für den nächsten C1-Kandidaten**
Entscheidung: **Option C - neuer Kandidat auf unabhängigen Daten**

## 1. Geltung

Diese Gates gelten für jede **autonome oder ungeprüfte** Freigabe eines
C1-Kandidaten als numerische Extraktionskomponente für die Meta-Analyse.

Sie gelten **nicht** als Freigabe für eine assistierte Nutzung mit
vollständiger menschlicher Prüfung. Eine assistierte Nutzung ist ein
getrennter Betriebsmodus und kein Bestehen der Gates.

Der Standard ist versioniert. Änderungen sind nur vor dem nächsten Lauf als
neue Policy-Version zulässig. Eine nachträgliche Lockerung nach Sicht der
Ergebnisse ist unzulässig.

## 2. Entscheidungsregel

Ein Kandidat wird nur freigegeben, wenn **G1, G2, G3, G4 und G5 vollständig
bestanden** sind. Es gibt keinen Teilpass und keine Gewichtung.

Die Metriken stammen aus dem jeweiligen Evaluator. Fehlende Werte werden
nicht durch 0, Schätzungen oder Imputation ersetzt.

## 3. G1 - Integrität

**Ziel:** Der Lauf ist technisch vollständig und strukturell verlässlich.

| Prüfung | Schwelle |
|---|---|
| Ausgabezeilen | `records_with_output == records` |
| Parse-/Schemafehler | `0` |
| Halluzinierte Felder | `0` |
| Null-Disziplin auf nicht erwarteten Feldern | `100 %` |

G1 ist ein hartes Gate. Ein Verstoß beendet die Freigabe unabhängig von allen
anderen Werten.

## 4. G2 - Record-Vollständigkeit

**Ziel:** Für jeden Record liegen alle erwarteten Felder vor.

**Metrik:** Anteil der Records mit `missing_fields == 0` an allen Records.

**Schwelle:** `>= 95 %`.

Fehlende Werte dürfen nicht geschätzt oder durch 0 ersetzt werden. Ein
Record mit einem fehlenden Pflichtfeld zählt als unvollständig, auch wenn die
übrigen Felder exakt sind.

## 5. G3 - Feldgenauigkeit

**Ziel:** Die extrahierten Werte sind auf Feldebene genau genug für das
Pooling.

**Metriken:**

1. `exact_fields / expected_fields_total >= 95 %`.
2. Für **jedes** kritische Feld: `exact_rate >= 95 %`.

**Kritische Felder:**

- `intervention_n`
- `comparator_n`
- `intervention_mean`
- `comparator_mean`
- `intervention_sd`
- `comparator_sd`
- `intervention_events`
- `comparator_events`

Die Feldebene wird getrennt nach `continuous` und `binary` berichtet. Ein
guter Gesamtwert darf kein systematisch schwaches Einzelfeld verdecken.

## 6. G4 - Record-Genauigkeit

**Ziel:** Ein ausreichender Anteil der Records ist als Ganzes verwendbar.

**Metrik:** Anteil der Records, bei denen alle erwarteten Felder exakt sind
(`exact_fields == expected_fields`), an allen Records.

**Schwelle:** `>= 90 %`.

G4 ist bewusst strenger als eine reine Felderquote: Ein Record mit einem
einzigen falschen N-, Mean-, SD- oder Event-Wert ist für das ungeprüfte
Pooling nicht vollständig belastbar.

## 7. G5 - Unabhängige Validierung

**Ziel:** Der Kandidat wird nicht auf den bereits verbrauchten Daten
validiert.

Ein Holdout besteht G5 nur, wenn alle folgenden Punkte vor dem Lauf
dokumentiert und eingefroren sind:

- neuer Holdout, nicht die 26 Dev-Records und nicht die 249 Test-Records;
- Artikel disjunkt zu Dev und dem verbrauchten Test;
- keine Verwendung des Holdouts für Prompt-, Pipeline- oder
  Feature-Entwicklung;
- Input, Referenz und Holdout-Manifest vor dem Lauf gehasht;
- Prompt und Modellkonfiguration vor dem Lauf eingefroren;
- Holdout-Manifest erklärt ausdrücklich:
  `independent_of_dev=true`, `excluded_consumed_test=true`,
  `articles_disjoint=true`, `pre_registered=true`,
  `prompt_frozen_before_run=true`;
- genau ein freigegebener Evaluationslauf auf diesem Holdout.

Der verbrauchte 249er-Test darf als **retrospektiver Diagnose- oder
Regressionstest** genutzt werden, aber nicht als unabhängiger Nachweis für
einen neuen Kandidaten.

## 8. v6c-Baseline

v6c wird mit diesen Gates geprüft und **nicht freigegeben**:

| Gate | v6c | Bewertung |
|---|---|---|
| G1 Integrität | 249/249, 0 Parse, 0 Halluzinationen, 684/684 Null-Disziplin | **bestanden** |
| G2 Record-Vollständigkeit | 217/249 = 87,1 % | **nicht bestanden** |
| G3 Feldgenauigkeit | 992/1308 = 75,8 %; kritische Felder 66,7–87,1 % | **nicht bestanden** |
| G4 Record-Genauigkeit | 148/249 = 59,4 % | **nicht bestanden** |
| G5 Unabhängige Validierung | kein unabhängiger Holdout; 249er-Test verbraucht | **nicht bestanden** |

v6c bleibt als diagnostischer Kandidat und als Fehleranalyse-Basis erhalten.
Es wird nicht nachträglich auf dem Testsplit optimiert und nicht erneut als
Testkandidat verwendet.

## 9. Konsequenz

- **Autonome Freigabe:** verweigert, solange nicht alle Gates bestehen.
- **Assistierte Nutzung:** nur mit 100 % menschlicher Prüfung aller
  numerischen Werte und ohne automatisches Pooling; das ist kein Gate-Pass.
- **Nächster Kandidat:** Entwicklung auf Dev oder einem neuen
  Entwicklungsanteil; Evaluationslauf ausschließlich auf einem neuen,
  unabhängigen Holdout.
- **Kein neuer Modelllauf** allein durch dieses Dokument. Ein Lauf braucht
  eine eigene ausdrückliche Freigabe.

## 10. Bezug

- Entscheidung: [`decision_v6c.md`](decision_v6c.md)
- Testresultat: [`runs_test/c1_test_20261111_v6c/test_result.md`](runs_test/c1_test_20261111_v6c/test_result.md)
- Fehleranalyse: [`runs_test/c1_test_20261111_v6c/test_error_analysis.md`](runs_test/c1_test_20261111_v6c/test_error_analysis.md)
- C1-Metriken: [`../../evaluation/README.md`](../../evaluation/README.md)
- Meta-Analyse-Anforderungen: [`../../../METAANALYSE.md`](../../../METAANALYSE.md)
