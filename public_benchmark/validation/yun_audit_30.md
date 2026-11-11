# Yun-Referenzaudit: 30 stratifizierte Records plus Problemfälle

Stand: 2026-11-11

Datenbasis: Yun-Release `1bc768d4d098c727c9866eeff909297c38a3e84c`,
`evaluation/data/annotated_rct_dataset.json` und die mitgelieferten
Abstract-/Results-Auszüge. Die Rohdaten wurden nicht verändert.

Status: **Audit abgeschlossen; keine Modellvorhersage; A und B unverändert.**

## 1. Ergebnis

Die Yun-Referenz ist numerisch brauchbar, aber **kein ungeprüfter
Goldstandard**. In der Zufallsstichprobe von 30 Records enthalten

- **8 von 30 Records (26,7 %)** mindestens einen klaren Fehler: sechs
  strukturelle ICO-Fehler und zwei Records mit harten Zahlenfehlern;
- **4 von 104 nichtleeren Referenzfeldern (3,8 %)** einen harten
  Zahlenfehler;
- **4 von 104 Feldern (3,8 %)** Werte, die im bereitgestellten Text nicht
  prüfbar sind;
- **2 von 30 Records** eine leere Referenz, obwohl der Text Werte nennt.

Damit ist die feldfokussierte Fehlerquote niedrig, die recordfokussierte
Quote aber hoch. Für Experiment C ist die Recordebene entscheidend: Ein
strukturell falscher ICO ist auch dann nicht als Interventionseffekt
verwendbar, wenn die Zahlen im Text stehen.

## 2. Stichprobe und Methodik

### 2.1 Auswahl

- 15 kontinuierliche und 15 binäre Records, je ein Record aus einem anderen
  Artikel.
- Zufallsauswahl mit Seed `20261111`.
- Die bekannten Problem-PMCIDs `2667135` und `5777645` wurden aus der
  Zufallsauswahl ausgeschlossen.
- Zusätzlich und bewusst ausgewählt: die Problemfälle 12, 635 und 636.
- Die 30 Zufallsrecords sind in `yun_audit_sample.json` dokumentiert; die
  Ergebnisdaten stehen in `yun_audit_results.json`.

### 2.2 Prüfung

Jeder Record wurde gegen den mitgelieferten Abstract-/Results-Text geprüft.
Gezählt wurden nur nichtleere Referenzfelder:

- kontinuierlich: N, Mean und SD je Arm (maximal 6 Felder),
- binär: N und Ereigniszahlen je Arm (maximal 4 Felder).

Fehlende Werte wurden nicht ergänzt und nicht geschätzt. Ein Wert, der nur in
einer Bildtabelle steht und im Text nicht lesbar ist, wurde als „nicht
prüfbar“ und nicht automatisch als falsch gewertet.

### 2.3 Fehlerklassen

| Klasse | Definition |
|---|---|
| `numeric_error` | Referenzwert widerspricht dem Text, stammt aus dem falschen Arm/der falschen Kohorte oder gibt eine falsche statistische Größe wieder (z. B. Median als Mean). |
| `structural_issue` | Der Record ist kein gültiger Interventions-Kontroll-Vergleich: Baseline-Charakteristik, Ein-Arm-Vorher-Nachher, observationaler Vergleich, kombinierte Arme oder kombinierte Outcomes ohne Armwerte. |
| `unverifiable` | Werte im bereitgestellten Text nicht prüfbar, typischerweise nur als Bildtabelle vorhanden. |
| `incomplete_reference` | Referenz leer, obwohl der Text Werte nennt. |
| `verified_partial` | Vorhandene Felder stimmen; weitere Felder werden im Text nicht berichtet. |
| `verified` | Alle nichtleeren Felder stimmen exakt oder numerisch äquivalent. |
| `flag_error` | `is_data_complete=TRUE`, obwohl Pflichtfelder fehlen. |

`verified_partial` ist kein Fehler. Es bedeutet, dass die Referenz für die
vorhandenen Felder korrekt ist, aber für einen vollständigen Effekt weitere
Angaben fehlen.

## 3. Gesamtquote der 30 Zufallsrecords

| Maß | Zähler / Nenner | Quote | 95-%-CI (Wilson) |
|---|---:|---:|---:|
| Harte Zahlenfehler auf Feldebene | 4 / 104 | 3,8 % | 1,5–9,5 % |
| Nicht prüfbare Felder | 4 / 104 | 3,8 % | 1,5–9,5 % |
| Records mit mindestens einem Zahlenfehler | 2 / 30 | 6,7 % | 1,9–21,3 % |
| Records mit strukturellem ICO-Fehler | 6 / 30 | 20,0 % | 9,5–37,3 % |
| Records mit klarem Fehler (Zahlen- oder Strukturfehler) | 8 / 30 | 26,7 % | 14,2–44,4 % |
| Records mit irgendeinem Befund (inkl. nicht prüfbar/leer) | 11 / 30 | 36,7 % | 21,9–54,5 % |

Die Kategorien überschneiden sich nicht: 2 Zahlenfehler + 6 strukturelle
Fehler = 8 klare Fehler; dazu kommen 2 leere Referenzen und 1 nicht prüfbarer
Record = 11 Records mit irgendeinem Befund.

### 3.1 Statusverteilung

| Status | Records |
|---|---:|
| `verified` | 12 |
| `verified_partial` | 7 |
| `structural_issue` | 6 |
| `numeric_error` | 2 |
| `incomplete_reference` | 2 |
| `unverifiable` | 1 |
| **Summe** | **30** |

### 3.2 Nach Stratum

| Stratum | Records | Felder | Zahlenfehler | Nicht prüfbar | Klare Fehler | Quote klare Fehler | Irgendein Befund | Quote |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Kontinuierlich | 15 | 56 | 4 | 4 | 4 | 26,7 % | 5 | 33,3 % |
| Binär | 15 | 48 | 0 | 0 | 4 | 26,7 % | 6 | 40,0 % |
| **Gesamt** | **30** | **104** | **4** | **4** | **8** | **26,7 %** | **11** | **36,7 %** |

Der Unterschied zwischen den Straten ist inhaltlich wichtig:

- Bei den kontinuierlichen Records liegen alle harten Zahlenfehler; die
  Fehlerquote auf Feldebene beträgt dort 4/56 = 7,1 %.
- Bei den binären Records gibt es keinen harten Zahlenfehler, aber vier
  strukturelle Fehler und zwei leere Referenzen. Die Recordebene ist daher
  trotz perfekter Feldzahlen nicht sauber.

## 4. Recordübersicht

| ID | PMC | Stratum | Status | Felder | Zahlenfehler | Nicht prüfbar | Kurzbegründung |
|---:|---|---|---|---:|---:|---:|---|
| 670 | 4987981 | kontinuierlich | `structural_issue` | 2 | 0 | 0 | Drei Gruppen; kombinierte Arme/Outcomes, keine Arm-Mean/SD |
| 528 | 4411165 | kontinuierlich | `verified_partial` | 2 | 0 | 0 | Diastolischer Blutdruck nur in Abbildung |
| 308 | 4541185 | kontinuierlich | `verified` | 6 | 0 | 0 | Armwerte und N stimmen |
| 390 | 3278655 | kontinuierlich | `verified` | 6 | 0 | 0 | Armwerte und N stimmen |
| 661 | 4458006 | kontinuierlich | `verified_partial` | 4 | 0 | 0 | Woche 6 stimmt; SD fehlt |
| 125 | 4493951 | kontinuierlich | `verified_partial` | 2 | 0 | 0 | Sedierung nur in Abbildung |
| 89 | 3912320 | kontinuierlich | `verified_partial` | 2 | 0 | 0 | Werte in Abbildung; SD fehlt |
| 83 | 3580751 | kontinuierlich | `numeric_error` | 6 | 2 | 0 | N ist Gesamtkohorte, Means/SDs gelten für No-VAP-Untergruppe |
| 303 | 4357072 | kontinuierlich | `unverifiable` | 6 | 0 | 4 | Tabellen nur als Bild; Werte nicht prüfbar |
| 374 | 1475568 | kontinuierlich | `verified_partial` | 2 | 0 | 0 | Nur Gesamt-Mean-Difference berichtet |
| 268 | 3214395 | kontinuierlich | `structural_issue` | 2 | 0 | 0 | Drei BIS-Gruppen; kombinierter Arm ohne Arm-Mean/SD |
| 164 | 5062234 | kontinuierlich | `verified_partial` | 2 | 0 | 0 | VAS nur in Grafik; keine SD |
| 300 | 4355974 | kontinuierlich | `verified_partial` | 4 | 0 | 0 | Mean Change stimmt; SD fehlt |
| 156 | 5055753 | kontinuierlich | `verified` | 6 | 0 | 0 | Armwerte und N stimmen |
| 694 | 5712123 | kontinuierlich | `numeric_error` | 4 | 2 | 0 | Median (IQR) als Mean/SD verwendet |
| 178 | 5086025 | binär | `structural_issue` | 4 | 0 | 0 | Ein-Arm-Vorher-Nachher; kein 2x2 |
| 109 | 4188762 | binär | `verified` | 4 | 0 | 0 | Ereignisse und N stimmen |
| 62 | 3309311 | binär | `structural_issue` | 4 | 0 | 0 | Observationaler MRI-Vergleich, kein RCT |
| 621 | 3493722 | binär | `verified` | 4 | 0 | 0 | ITT-Ereignisse und N stimmen |
| 516 | 4033571 | binär | `verified` | 4 | 0 | 0 | Ereignisse und N stimmen |
| 543 | 3508963 | binär | `structural_issue` | 4 | 0 | 0 | Baseline-Verteilung, kein Outcome |
| 10 | 2363753 | binär | `verified` | 4 | 0 | 0 | Ereignisse und N stimmen |
| 652 | 5976307 | binär | `incomplete_reference` | 0 | 0 | 0 | Referenz leer; Text nennt 17/62 vs. 31/62 |
| 261 | 5771543 | binär | `verified` | 4 | 0 | 0 | Ereignisse und N stimmen |
| 2 | 57750 | binär | `incomplete_reference` | 0 | 0 | 0 | Referenz leer; Ereigniszahlen nicht extrahiert |
| 476 | 4144850 | binär | `verified` | 4 | 0 | 0 | N und Ereignisse stimmen; Ereignisse aus Prozenten abgeleitet |
| 547 | 3263860 | binär | `verified` | 4 | 0 | 0 | 0 Ereignisse in beiden Armen |
| 484 | 3343759 | binär | `structural_issue` | 0 | 0 | 0 | Baseline-Charakteristik; Referenz leer |
| 253 | 5614421 | binär | `verified` | 4 | 0 | 0 | Ereignisse und N stimmen |
| 20 | 2972614 | binär | `verified` | 4 | 0 | 0 | 0 Ereignisse in beiden Armen |

## 5. Problemfälle 12, 635 und 636

Die drei Fälle wurden nicht zufällig gezogen. Ihre Quoten sind daher **keine
Prävalenzschätzung** für Yun, sondern eine gezielte Prüfung bekannter
Auffälligkeiten.

| ID | PMC | Status | Felder | Zahlenfehler | Fehlende N | Befund |
|---:|---|---|---:|---:|---:|---|
| 12 | 2667135 | `numeric_error` | 6 | 1 | 0 | Interventions-SD in Referenz 23,34; Tabelle 12,34. Andere fünf Felder stimmen. |
| 635 | 5777645 | `flag_error` | 4 | 0 | 2 | Means/SDs exakt; Tabelle nennt n=70/70, Referenz-N fehlt; `is_data_complete=TRUE` ist falsch. |
| 636 | 5777645 | `flag_error` | 4 | 0 | 2 | Means/SDs exakt; Tabelle nennt n=70/70, Referenz-N fehlt; `is_data_complete=TRUE` ist falsch. |
| **Summe** | | | **14** | **1** | **4** | 1 harter Zahlenfehler, 2 Flag-Fehler, 4 fehlende N-Felder |

Record 12 zeigt einen klassischen Zahlendreher. 635/636 zeigen ein anderes
Problem: Die numerischen Werte sind korrekt, aber die Gruppengrößen fehlen
und das Vollständigkeitsflag ist trotzdem gesetzt. Damit ist
`is_data_complete` allein kein verlässliches Einschlusskriterium.

## 6. Befunde

### 6.1 Strukturelle Fehler sind das größte Problem

Sechs der 30 Zufallsrecords sind keine gültigen Interventions-Kontroll-
Vergleiche. Die Ursachen:

- Baseline-Charakteristiken statt Outcomes (543, 484),
- Ein-Arm-Vorher-Nachher-Design (178),
- observationaler Vergleich statt RCT (62),
- kombinierte Arme oder Outcomes ohne gemeinsame Arm-Mean/SD (670, 268).

Diese Records können auch mit korrekten Einzelzahlen keinen belastbaren
Interventionseffekt liefern. Für Experiment C müssen sie vor der Auswertung
ausgeschlossen oder als eigene, nicht-estimierbare Kategorie geführt werden.

### 6.2 Harte Zahlenfehler haben drei Muster

- **Falsche Kohorte:** Record 83 verwendet die Gesamt-N, während Means/SDs
  nur für die No-VAP-Untergruppe gelten.
- **Falsche statistische Größe:** Record 694 verwendet Median und IQR als
  Mean und SD.
- **Zahlendreher:** Record 12 vertauscht 12,34 und 23,34.

Das sind keine seltenen Rundungsunterschiede. Es sind Fehler, die einen
gepoolten Effekt verändern können.

### 6.3 Fehlende und nicht prüfbare Werte sind häufig, aber anders zu bewerten

- 7 der 30 Records sind `verified_partial`: Die vorhandenen Felder stimmen,
  weitere Werte werden im Text nicht berichtet.
- 4 Felder in Record 303 sind nur in Bildtabellen und im bereitgestellten
  Text nicht prüfbar.
- 2 binäre Referenzen sind leer, obwohl der Text Werte nennt.

„Nicht prüfbar“ ist nicht dasselbe wie „falsch“. Für einen Benchmark muss es
aber eine eigene Kategorie geben, sonst wird eine Nichtprüfbarkeit
fälschlich als Modellfehler oder als korrekte Referenz gezählt.

### 6.4 Das Vollständigkeitsflag ist nicht verlässlich

Die beiden als vollständig geflaggten Records 635/636 haben keine
Gruppengrößen. Schon die frühere Fünf-Record-Prüfung hatte diesen Fehler
gezeigt; der breitere Audit bestätigt ihn. Vor C muss die Referenz daher
einen eigenen Auditstatus erhalten, der nicht auf `is_data_complete` beruht.

## 7. Grenzen

- Geprüft wurden 30 Zufallsrecords plus 3 bewusst gewählte Problemfälle,
  nicht alle 699 Records. Die 95-%-Intervalle sind wegen des kleinen
  Stichprobenumfangs weit.
- Die Prüfung stützt sich auf die von Yun mitgelieferten Abstract-/Results-
  Auszüge, nicht auf vollständige PDFs. Ein im Auszug nicht sichtbarer Wert
  kann daher als „nicht prüfbar“ erscheinen, obwohl er im Volltext steht.
- Die Problemfälle 12, 635 und 636 sind keine Zufallsstichprobe; ihre Quote
  darf nicht auf Yun hochgerechnet werden.
- Es wurden keine Werte korrigiert und keine fehlenden Werte ergänzt. Die
  Rohdaten und die Referenzdatei bleiben unverändert.
- Es gab keinen Modelllauf, keine Prompt-Anpassung und keinen A/B-Vergleich.
- Die Auditkarten mit Artikelzitaten sind nur lokal als Arbeitsexemplar
  vorhanden und werden wegen der Artikelrechte nicht versioniert.

## 8. Empfehlung

**B bleibt unverändert.** Es gibt keinen B-Rücklauf und keinen B-Hash; A
bleibt geschlossen. Yun ersetzt B nicht, sondern ist weiterhin ein
zusätzlicher numerischer Benchmark (Experiment C).

Vor C:

1. **Vollaudit der 410 streng vollständigen Records.** Die 5-%-Schwelle aus
   dem bisherigen Plan ist auf Feldebene mit 3,8 % knapp unterschritten,
   auf Recordebene mit 26,7 % aber deutlich überschritten. Für die
   Entscheidung ist die Recordebene maßgeblich. Alle 410 Records prüfen;
   mindestens alle strukturellen Auffälligkeiten und alle kontinuierlichen
   Zahlenfelder.
2. **Kuratierte Referenz mit Auditstatus.** Pro Record mindestens
   `verified`, `corrected_with_source`, `structural_exclude` oder
   `unverifiable` führen. Korrekturen nur mit Textstelle und getrennt von
   den Originalwerten dokumentieren.
3. **Test einfrieren.** Erst nach dem Audit den Yun-Test-Split und die
   Referenzdatei hashen und als unveränderlich markieren.
4. **C1-Pilot auf Dev.** Danach einen ausdrücklich freigegebenen Lauf auf
   den 43 Dev-Records planen; keine Testdaten zur Prompt-Optimierung.
5. **B nicht anfassen.** Kein A öffnen, keinen B-Hash erfinden, keinen
   A/B-Vergleich vor dem Rücklauf.

Der größte Hebel ist jetzt nicht ein Modelllauf, sondern die Kuratierung der
Referenz. Ein C-Lauf auf den ungeprüften 410 Records würde einen Teil der
hier sichtbaren Referenzfehler als Modellfehler messen.

## 9. Reproduzierbarkeit

| Datei | Inhalt |
|---|---|
| `yun_audit_sample.json` | Auswahl, Seed, Stratifizierung und Problemfälle |
| `yun_audit_results.json` | Recordbefunde, Feldzahlen, Status und Quoten |
| `yun_audit_30.md` | Dieser Bericht |
| `yun_sample_check.md` | Frühere Fünf-Record-Prüfung mit Record 12 |

Die Zufallsauswahl wird durch `yun_audit_sample.json` gepinnt. Die
Recordbefunde sind manuelle Prüfungen; sie sind keine automatisch
reproduzierbare Modellausgabe. Die Quoten in diesem Bericht wurden aus
`yun_audit_results.json` gegengeprüft.
