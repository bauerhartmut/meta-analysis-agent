# Batch-2-Audit: Zwischenstand seit der letzten Markdown

**Stand:** 2026-11-13

**Bezugspunkt:** [`fulltext_review_batch2_pmc13590641_n_source_v1.md`](fulltext_review_batch2_pmc13590641_n_source_v1.md), Commit `855fc59`

**Status:** Audit technisch abgeschlossen; menschliche Prüfung offen; keine finalen Eignungsentscheidungen.

## 1. Ausgangslage

Die Batch-2-Prüfung umfasst **9 Artikel** und **36 Outcome-Slots**. Die Quellenprüfung war zuletzt auf die konkret referenzierte Tabellenzeile begrenzt. Für vier Sicherheits-Outcomes aus `PMC13590641` standen die Ereigniszahlen in der Zeile, die Nenner aber im Arm-Header von Tabelle 3.

Die damalige Quellennotiz dokumentierte diese Header-Nenner als zulässige Quelle. Seitdem wurden drei technische Schritte umgesetzt, ohne Outcome-Werte oder Zähler zu verändern.

## 2. Änderungen seit dem Bezugspunkt

| Commit | Änderung | Ergebnis |
|---|---|---|
| `6c35d67` | Header-N-Ausnahme auf konkrete Arm-Header-Zellen verschärft | `N = 19/24` muss exakt in der jeweiligen `th`-Zelle stehen; kein Treffer irgendwo in der Tabelle |
| `2327ac8` | Zahlprüfung auf exakte Tokens umgestellt | Keine Treffer mehr wie `4` in `14`; Tausendertrennzeichen wie `12,103.32` werden korrekt normalisiert; ungenutzte Sonderlogik entfernt |
| `89a2239` | Armweise Spaltenzuordnung für Nicht-Header-Outcomes ergänzt | Strukturierte Werte werden in den aus dem Tabellenkopf abgeleiteten Interventions-/Kontrollspannen geprüft |

Die Tabellenkopf-Erkennung berücksichtigt `colspan`, ordnet die Armlabels den Spaltenbereichen zu und prüft Zahlen nur innerhalb der jeweiligen Armspanne.

## 3. Ergebnisse

### 3.1 Unveränderte Zähler

| Kennzahl | Wert |
|---|---:|
| Artikel | 9 |
| Outcome-Slots | 36 |
| Unabhängig verwendbar | 8 |
| Überlappend, nicht unabhängig | 6 |
| Nicht verwendbar/nicht berichtet | 22 |
| Formal verwendbar inkl. überlappend | 14 |

**Summen:** 8 + 6 + 22 = 36; 8 + 6 = 14. Die Zähler sind gegenüber dem Bezugspunkt unverändert.

### 3.2 Quellenprüfung

| Prüfung | Ergebnis |
|---|---:|
| Slots mit Quelleintrag | 36/36 |
| Exakte Results-Textzitate | 17 |
| Tabellenverweise | 19 |
| Tabellen-Outcomes quellengedeckt | 18/18 |
| Davon zeilenexakt | 12/16 Einzelzeilen |
| Davon mit zulässigem Arm-Header-N | 4/16 Einzelzeilen |
| Kosten-Outcomes mit getrennten Armzeilen | 2/2 |
| Strukturierte Zahlen im Quelleintrag | 20/20 |
| Offene Audit-Befunde | 0 |

Die vier `PMC13590641`-Slots bleiben quellengedeckt:

| Slot | Outcome | Intervention | Kontrolle | Header-N |
|---:|---|---:|---:|---:|
| 1 | Any adverse event, any grade | 23/24 | 15/19 | 24/19 |
| 2 | Neutropenia, any grade | 4/24 | 10/19 | 24/19 |
| 3 | Nausea, any grade | 0/24 | 5/19 | 24/19 |
| 4 | Rash, any grade | 6/24 | 1/19 | 24/19 |

### 3.3 Armspaltenzuordnung

| Gruppe | Anzahl | Prüfung |
|---|---:|---|
| Nicht-Header-Outcomes mit strukturierten Werten | 8 | Werte in den jeweiligen Armspannen geprüft |
| Nicht-Header-Outcomes ohne strukturierte Werte | 4 | nur Zeilenlabel (`PMC13610533`) |
| Kosten-Outcomes | 2 | getrennte Interventions-/Kontrollzeilen (`PMC13574397`) |

Beispiele der aufgelösten Armspannen:

- `PMC13626740`: CBT-Spalten und ST-Spalten werden getrennt geprüft; Mittelwerte und SDs liegen jeweils in der richtigen Armspanne.
- `PMC13596784`: Control-Arm und MATILDA-Arm werden getrennt geprüft; die 6-Monats-Werte liegen innerhalb der jeweiligen Armspanne.
- `PMC13590641`: Kontroll- und Experimentarm werden getrennt geprüft; die Ereigniszahlen liegen in der jeweiligen Armspanne, die Nenner in den konkreten Header-Zellen.

## 4. Aktuelle Artefakte

- Audit: [`fulltext_review_batch2_audit_v1.md`](fulltext_review_batch2_audit_v1.md)
- Menschliche Checkliste: [`fulltext_review_batch2_human_checklist_v1.md`](fulltext_review_batch2_human_checklist_v1.md)
- Quellennotiz zu `PMC13590641`: [`fulltext_review_batch2_pmc13590641_n_source_v1.md`](fulltext_review_batch2_pmc13590641_n_source_v1.md)
- Generator: [`../../../scripts/build_p0_review_batch2_checklist.py`](../../../scripts/build_p0_review_batch2_checklist.py)
- Batch-2-Daten: [`fulltext_review_batch2_v1.json`](fulltext_review_batch2_v1.json), [`fulltext_review_batch2_v1.csv`](fulltext_review_batch2_v1.csv), [`fulltext_review_batch2_v1.md`](fulltext_review_batch2_v1.md)

## 5. Durchgeführte Prüfungen

- Generator erfolgreich ausgeführt; `py_compile` erfolgreich.
- 18/18 Tabellen-Outcomes und 0 offene Befunde bestätigt.
- 36 Checklisten-Zeilen und vier Header-N-Markierungen bestätigt.
- Armspannen für die betroffenen Tabellen verifiziert.
- Negativprüfung: Interventionswerte werden in der Kontrollspanne abgelehnt und umgekehrt.
- `git diff --check` bestanden.
- Keine chinesischen Zeichen in den erzeugten Dokumenten.
- Kein Modell- oder Netzlauf.
- Batch-2-JSON/CSV/Markdown ohne inhaltlichen Diff.

## 6. Offene Grenzen

1. **Keine finale menschliche Freigabe.** Die Checkliste bleibt offen; die technische Prüfung ersetzt keine fachliche Eignungsentscheidung.
2. **Armspaltengenau, nicht zeitpunktgenau.** Die Armspannen umfassen alle Zeitpunkte einer Armspalte. Eine separate Zeitpunktzuordnung wurde in diesem Schritt nicht implementiert.
3. **Vier Outcomes ohne strukturierte Werte.** `PMC13610533` wird nur über Zeilenlabel und Quelle geprüft; es gibt keine armweisen Mean/SD-Werte.
4. **Zwei Kosten-Outcomes.** `PMC13574397` verwendet getrennte Armzeilen statt Armspalten.
5. **Header-N ist eine dokumentierte Ausnahme.** Die Nenner sind zulässig, weil sie armweise und tabellenintern im Header stehen; sie sind keine Zeilenwerte.

## 7. Nächste Schritte

1. **Menschliche Checkliste abschließen.** Zuerst die vier `PMC13590641`-Slots prüfen und die Header-N-Quelle bestätigen. Danach die übrigen 32 Slots abhaken.
2. **Keine neuen Outcome-Werte erzeugen.** Die bestehenden Werte und Zähler bleiben eingefroren.
3. **Optional: Zeitpunktspaltenzuordnung.** Falls künftig Zeitpunktverwechslungen ausgeschlossen werden sollen, könnte der Generator zusätzlich die Zeitpunktspalte aus dem Tabellenkopf auflösen. Das ist ein separater technischer Schritt und für den aktuellen Stand nicht erforderlich.
4. **Kein neuer Netz- oder Modelllauf.** Für die verbleibende Prüfung reicht die menschliche Sichtprüfung der lokalen Quellen.

## 8. Kurzfazit

Die Quellenprüfung ist von der zeilenweiten Prüfung auf eine armspaltengenaue Prüfung erweitert worden. Die vier Header-N-Fälle sind exakt dokumentiert, die acht übrigen bewertbaren Nicht-Header-Outcomes armweise geprüft, und die Zähler **8/6/22/14** sowie alle Outcome-Werte bleiben unverändert. Die technische Prüfung ist abgeschlossen; die menschliche Freigabe steht noch aus.
