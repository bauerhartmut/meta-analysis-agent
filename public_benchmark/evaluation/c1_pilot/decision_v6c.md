# Entscheidungsvorlage: v6c für die Meta-Analyse?

Stand: 2026-11-11
Status: **ENTSCHIEDEN (2026-11-11)**
Entscheidungseigentümer: Nutzer
Entscheidung: **Option C - neuer Kandidat auf unabhängigen Daten**

## 1. Entscheidungsfrage

Reicht der eingefrorene C1-Kandidat `c1_dev_20261111_v6c` (Prompt
`c1-dev-extract-v6`) als numerische Extraktionskomponente für die
Meta-Analyse aus, oder braucht es einen neuen Kandidaten auf unabhängigen
Daten?

Die Frage betrifft **nicht** den gesamten Research Agent und nicht die
statistische Pooling-Engine. Sie betrifft nur die Frage, ob die von v6c
extrahierten Armwerte (N, Mean, SD, Ereigniszahlen) ohne vollständige
menschliche Nachprüfung in eine Meta-Analyse übernommen werden dürfen.

## 2. Beschluss

**Beschlossen: Option C - neuer Kandidat auf unabhängigen Daten. v6c reicht
nicht für eine autonome oder ungeprüfte Meta-Analyse.**

Die Gates G1–G5 sind als Projektstandard v1 festgelegt:
[`c1_acceptance_gates_v1.md`](c1_acceptance_gates_v1.md).

v6c ist technisch sauber und auf Dev perfekt, aber auf dem eingefrorenen
Testlauf nur in **992/1308 Feldern (75,8 %)** exakt und in **148/249 Records
(59,4 %)** vollständig exakt. **101/249 Records (40,6 %)** enthalten
mindestens einen Fehler. Für eine quantitative Synthese ist das zu hoch:
Falsche N/Mean/SD können den gepoolten Effekt verzerren, fehlende Blöcke
reduzieren die Zahl der poolbaren Studien.

Eine **assistierte Nutzung** mit 100 % menschlicher Prüfung aller
Modellwerte ist als Interimslösung möglich. Sie ist aber keine Freigabe für
automatische Extraktion und keine Antwort auf die Frage, ob v6c
„ausreicht“.

## 3. Evidenzbasis

| Quelle | Inhalt |
|---|---|
| [`runs_test/c1_test_20261111_v6c/test_result.md`](runs_test/c1_test_20261111_v6c/test_result.md) | Primärresultat des einen Testlaufs |
| [`runs_test/c1_test_20261111_v6c/test_error_analysis.md`](runs_test/c1_test_20261111_v6c/test_error_analysis.md) | Record-, Feld- und Blockmuster |
| [`test_release_checklist_v6c.md`](test_release_checklist_v6c.md) | Freigabe- und Stoppregeln |
| [`README.md`](README.md) | Protokoll, Dev-Historie, Zeitpunktregel |
| [`../../evaluation/README.md`](../../evaluation/README.md) | C1-Metriken und Auswertungseinheit |
| [`../../../METAANALYSE.md`](../../../METAANALYSE.md) | Anforderungen an numerische Extraktion und Pooling |
| [`../../../ENTWICKLUNGSAUFTRAG_v2.md`](../../../ENTWICKLUNGSAUFTRAG_v2.md) | Abnahmekriterien; Zielwerte müssen benchmarkspezifisch festgelegt werden |

Zum Zeitpunkt der Testauswertung lag **kein formaler C1-Schwellenwert** vor.
Mit dieser Entscheidung sind die Gates in Abschnitt 5 als Projektstandard v1
festgelegt; sie gelten für den nächsten Kandidaten.

## 4. Was der Testlauf zeigt

### Gesamt

| Kennzahl | Wert |
|---|---:|
| Records mit Ausgabe | 249/249 |
| erwartete Felder | 1.308 |
| abgedeckt | 1.168/1.308 (89,3 %) |
| exakt | 992/1.308 (75,8 %) |
| fehlend | 140 (10,7 %) |
| falsch | 176 (13,5 %) |
| halluziniert | 0 |
| vollständig exakte Records | 148/249 (59,4 %) |
| Records mit mindestens einem Fehler | 101/249 (40,6 %) |
| MAE über gepaarte Felder | 1,5305 |
| Parse-/Schemafehler | 0 |
| Null-Disziplin | 684/684 (100 %) |

### Nach Outcome-Typ

| Typ | Records | exakt | vollständig exakt | Records mit Fehler |
|---|---:|---:|---:|---:|
| continuous | 156 | 678/936 (72,4 %) | 79/156 (50,6 %) | 77/156 (49,4 %) |
| binary | 93 | 314/372 (84,4 %) | 69/93 (74,2 %) | 24/93 (25,8 %) |

### Kritische Felder

| Feld | exakt | fehlend | falsch |
|---|---:|---:|---:|
| `intervention_mean` | 110/156 (70,5 %) | 21 | 25 |
| `comparator_mean` | 105/156 (67,3 %) | 21 | 30 |
| `intervention_sd` | 106/156 (68,0 %) | 21 | 29 |
| `comparator_sd` | 104/156 (66,7 %) | 21 | 31 |
| `intervention_events` | 76/93 (81,7 %) | 8 | 9 |
| `comparator_events` | 76/93 (81,7 %) | 8 | 9 |

Die kontinuierlichen Mean/SD-Felder sind der kritischste Bereich. 21 Records
fehlen jeweils die Mean/SD-Werte eines Arms oder beider Arme; weitere 25–31
Felder sind falsch. Bei binären Outcomes sind die Event-Felder mit 81,7 %
zwar besser, aber ebenfalls nicht auf einem autonomen Freigabeniveau.

### Struktur der Fehler

- **Fehlend und falsch sind recordgetrennt:** 32 Records haben nur fehlende
  Werte, 69 nur falsche, 0 beides.
- **Blockmuster:** 23 kontinuierliche Records haben alle vier Mean/SD-Felder
  falsch, während beide N-Felder exakt sind. 11 Records haben beide
  Mean/SD-Arme fehlend. Bei binären Records haben 7 alle vier Felder
  fehlend und 7 beide Event-Felder falsch.
- **Kein durchgängiger Richtungsbias:** Über- und Unterschätzungen wechseln;
  einzelne Felder zeigen lokale Asymmetrien.
- **Gute Struktur, schwache Werte:** 0 Halluzinationen, 0 Parse-Fehler und
  perfekte Null-Disziplin. Das Modell halluziniert nicht, aber es liest
  vorhandene Werte teilweise falsch oder lässt ganze Blöcke weg.

### Generalisierung

Der Dev-Wert 140/140 (100 %) ist **keine** Schätzung der Testleistung. Die
Differenz zum Testwert beträgt **24,2 Prozentpunkte**. Der Test umfasst 249
Records aus 64 Artikeln; die 26 Dev-Records stammen aus 6 Artikeln. Die
Records sind innerhalb der Artikel geclustert; die berichteten Quoten sind
deskriptiv und keine unabhängigen Artikelstichproben.

## 5. Beschlossene Entscheidungsgates

Die folgenden Gates sind mit Option C als **Projektstandard v1** beschlossen.
Sie gelten für den nächsten C1-Kandidaten und für jede autonome bzw.
ungeprüfte Freigabe. Details und Prüfregeln:
[`c1_acceptance_gates_v1.md`](c1_acceptance_gates_v1.md).

| Gate | Vorschlag | v6c | Bewertung |
|---|---|---|---|
| G1 Integrität | 249/249 Ausgabezeilen, 0 Parse-/Schemafehler, 0 Halluzinationen | 249/249, 0, 0 | **bestanden** |
| G2 Record-Vollständigkeit | ≥ 95 % der Records mit allen erwarteten Feldern vorhanden | 217/249 (87,1 %) | **nicht bestanden** |
| G3 Feldgenauigkeit | ≥ 95 % aller Felder exakt; ≥ 95 % je kritischem Mean/SD- und Event-Feld | 75,8 %; 66,7–81,7 % | **nicht bestanden** |
| G4 Record-Genauigkeit | ≥ 90 % der Records vollständig exakt | 59,4 % | **nicht bestanden** |
| G5 Unabhängige Validierung | neuer, vorab eingefrorener Holdout; nicht der verbrauchte 249er-Test | nicht vorhanden | **nicht bestanden** |

**Konsequenz:** v6c besteht nur das Integritätsgate. Die Entscheidung
„ausreichend für autonome Meta-Analyse“ ist damit klar zu verneinen.

Die Gates sind bindend. Änderungen sind nur vor dem nächsten Lauf als neue
Policy-Version zulässig; eine nachträgliche Lockerung nach Sicht der
Ergebnisse wäre keine belastbare Abnahme.

## 6. Optionen

**Gewählt: Option C - neuer Kandidat auf unabhängigen Daten.**

### Option A — v6c ungeprüft akzeptieren

**Nicht empfohlen.** 40,6 % der Records enthalten mindestens einen Fehler;
13,5 % aller erwarteten Felder sind falsch und 10,7 % fehlen. Besonders
kritisch sind Mean/SD und die fehlenden Blöcke. Eine ungeprüfte Übernahme in
das Pooling kann Effekte verzerren und die Studienauswahl verändern.

### Option B — v6c nur assistiert nutzen

**Bedingt möglich, aber kein „ausreichend“.** Zulässig nur, wenn:

- jede numerische Ausgabe und jeder ICO-Bezug menschlich geprüft wird,
- keine automatische Aufnahme in das Pooling erfolgt,
- fehlende Werte nicht geschätzt oder durch Null ersetzt werden,
- die Prüfung dokumentiert und die Quelle je Wert nachvollziehbar bleibt,
- die Kommunikation v6c ausdrücklich als Kandidatengenerator, nicht als
  validierte Extraktion bezeichnet.

Der Nutzen ist vor allem Zeitersparnis bei der Kandidatensuche; die
Fehlerquote von 40,6 % Records bedeutet aber, dass praktisch jeder Record
angefasst werden muss. Ob das ausreicht, ist eine Ressourcenfrage, keine
Genauigkeitsfrage.

### Option C — neuer Kandidat auf unabhängigen Daten

**Empfohlen.** Der neue Kandidat wird:

- auf Dev oder einem neuen Entwicklungsanteil prompt- und pipelineseitig
  verbessert werden,
- **nicht** auf dem verbrauchten 249er-Test optimiert werden,
- auf einem neuen, vorab eingefrorenen und unabhängigen Holdout mit
  denselben Metriken geprüft werden,
- die blockweise Extraktion als primäres Ziel behandeln: vollständiger
  Record, fehlender Block, falscher Block,
- Mean/SD und Comparator-Arm besonders prüfen,
- die Gates aus Abschnitt 5 vor dem Lauf festschreiben.

### Option D — C1 stoppen

**Nicht nötig.** Der Datensatz und die Fehleranalyse sind wertvoll; das
Problem ist die Generalisierung von v6c, nicht die Aufgabe. Ein Stopp wäre
nur sinnvoll, wenn weder ein neuer unabhängiger Holdout noch eine
assistierte Nutzung mit vollständiger Prüfung gewollt ist.

## 7. Beschluss und Auflagen

1. **v6c nicht als autonome Extraktion für die Meta-Analyse freigeben.**
2. **Den 249er-Test nicht für die Entwicklung des nächsten Kandidaten
   verwenden.** Er ist als einmaliger Test verbraucht; die Fehleranalyse hat
   seine Muster sichtbar gemacht. Eine erneute Auswertung auf denselben Daten
   wäre kein unabhängiger Nachweis.
3. **Einen neuen Kandidaten auf unabhängigen Daten entwickeln.** Wenn kein
   neuer Holdout beschafft oder annotiert werden kann, ist eine belastbare
   Freigabe für automatische Extraktion nicht möglich.
4. **Bis dahin nur assistierte Nutzung** mit 100 % menschlicher Prüfung und
   ohne automatisches Pooling.
5. **Die Gates vor dem nächsten Lauf festschreiben** und danach nicht
   nachträglich ändern.

## 8. Was den Beschluss ändern würde

- Eine neue dokumentierte Entscheidung senkt den Scope ausdrücklich auf
  „Vorschlagsgenerator mit vollständiger menschlicher Prüfung“ und akzeptiert
  die 40,6 % fehlerhaften Records als Prüfaufwand.
- Ein neuer, unabhängiger Holdout bestätigt die Gates aus Abschnitt 5.
- Es wird nachgewiesen, dass die Fehler auf Rundung/Skalierung beschränkt
  sind und die gepoolten Effekte innerhalb einer vorab definierten Toleranz
  bleiben. Dieser Nachweis fehlt derzeit.
- Es gibt keine belastbare Möglichkeit, die 249er-Testdaten durch einen
  neuen unabhängigen Holdout zu ersetzen. Dann bleibt nur assistierte
  Nutzung oder eine neue Datenerhebung.

## 9. Offene Punkte für die Entscheidung

| Frage | Warum sie entscheidend ist |
|---|---|
| Soll C1 autonom oder assistiert eingesetzt werden? | Autonom braucht strengere Gates; assistiert verschiebt die Verantwortung auf die Prüfung. |
| Welche Fehlerquote ist für das Pooling akzeptabel? | Es gibt keinen formalen C1-Schwellenwert; die 95/90-Gates sind ein Vorschlag. |
| Gibt es menschliche Kapazität für 100 % Prüfung? | Ohne sie ist v6c nicht einsetzbar. |
| Gibt es einen neuen unabhängigen Holdout? | Ohne ihn ist kein unabhängiger Nachweis für einen neuen Kandidaten möglich. |
| Werden neue Daten annotiert oder externe Daten genutzt? | Das ist eine Daten-/Kuratierungsaufgabe, kein Modelllauf. |

## 10. Nächste Schritte

1. Gates v1 als verbindlichen Standard [verlinkt](c1_acceptance_gates_v1.md)
   verwenden; keine Änderung nach Sicht neuer Ergebnisse.
2. Unabhängigen Holdout beschaffen oder neu annotieren; 249er-Test nicht
   wiederverwenden.
3. Neuen Kandidaten auf Dev/neuem Entwicklungsanteil entwickeln; keine
   Testoptimierung.
4. Genau einen freigegebenen Evaluationslauf auf dem neuen Holdout
   durchführen; G1–G5 vor dem Lauf einfrieren.
5. Ergebnis, Fehleranalyse und Gate-Status wie bei v6c dokumentieren.

**In diesem Schritt:** keine Prompt-Änderung, kein neuer Modelllauf, keine
Freigabe für automatische Extraktion.

## 11. Entscheidungsprotokoll

| Feld | Eintrag |
|---|---|
| Entscheidung | **Option C angenommen** |
| Option | neuer Kandidat auf unabhängigen Daten |
| Begründung | 992/1308 exakt (75,8 %), 148/249 vollständig exakt (59,4 %); G2–G5 nicht bestanden |
| Datum | 2026-11-11 |
| Entscheidungseigentümer | Nutzer |
| Auflagen | Gates v1; neuer unabhängiger Holdout; kein Test-Reuse; v6c nur assistiert mit 100 % Prüfung |
| Nächste Überprüfung | nach Holdout-Manifest, vor dem nächsten Lauf |
