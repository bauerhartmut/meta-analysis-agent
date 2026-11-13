# Projektstatus Meta-Analysis Agent

**Stand:** 13.11.2026
**Basis:** vorhandene Artefakte in `public_benchmark/`, `data/golden_effects/` und `docs/internal/`
**Art des Dokuments:** Bestandsaufnahme, Einordnung und Richtungsentscheidung; kein Modell- oder Netzlauf

---

## 1. Kurzfassung

Das Projekt hat einen funktionierenden Agentenrahmen und eine belastbare statistische Schicht. Der Engpass ist nicht mehr die Architektur, sondern die **validierte numerische Extraktion** aus Studien.

Die wichtigsten aktuellen Befunde:

1. **C1/Yun ist technisch sauber, aber nicht freigegeben.** Der eingefrorene Testlauf v6c erreicht **992/1308 exakte Felder (75,8 %)** und **148/249 vollständig exakte Records (59,4 %)**. Es gibt **0 Halluzinationen** und **0 Parse-/Schemafehler**. Die Gates G2–G5 sind nicht bestanden; G1 ist bestanden. Entscheidung: **Option C – neuer Kandidat auf unabhängigen Daten**.
2. **Der unabhängige Holdout fehlt weiterhin.** Die P0-Beschaffung ist weit fortgeschritten, aber weder ein 30-Artikel-/100-Record-Holdout noch ein G5-fähiges Manifest sind eingefroren. Ohne G5 ist keine autonome Freigabe möglich.
3. **B ist weiterhin offen.** A hat 69 Effektzeilen und 13 Begründungen; B hat 0 Zeilen und 30 offene Dokumente. Es gibt keinen B-Rücklauf, keinen B-Abgabe-Hash, keinen A/B-Vergleich und keine Kappa-Berechnung.
4. **Der dCBT-I-Review-Abgleich bestätigt nur eine Studie.** Von 9 projektinternen CBT-I-Studien ist nur **Freeman 2017** in **Lee 2023** enthalten; Hwang 2025 enthält keine. Die 30 eingefrorenen Volltexte sind ein gemischtes Methoden-Sample mit **0 dCBT-I-Studien**.
5. **Die Zeitpunktsegmentierung ist deutlich gehärtet, aber auf den echten Annotationen noch schmal.** Der Parser trennt Post-Treatment, Follow-up, Mid-Treatment und unsichere Median-/±-Angaben. In Goldstandard A sind von 69 Effektzeilen nur 2 als `uncertain` segmentiert; 40 bleiben `unparsed`, weil reale Zeitpunktstrings wie `T1`, `baseline` oder `cross-sectional` nicht in Wochenwerte auflösbar sind.

**Richtung:** Das Projekt ist auf dem richtigen Pfad, wenn es **Validierung vor Modellläufen** stellt. Der nächste kritische Schritt ist ein unabhängiger, menschlich annotierter G5-Holdout. Ein weiterer Prompt-Lauf auf dem verbrauchten 249er-Test wäre kein Erkenntnisgewinn.

---

## 2. Projektziel und Architektur

Der Agent soll zu einer Forschungsfrage selbstständig Literatur finden, Volltexte lesen, Effektmaße belegt extrahieren, Hypothesen adversarial prüfen, statistisch poolen und einen zitierfähigen Bericht erzeugen.

Zentrale Designentscheidungen:

- **Verbatim-Kontrakt:** Zitate und Zahlen werden gegen den Quelltext geprüft; keine freie Nacherzählung als Zahlenquelle.
- **Doppel-Lesung bei Vision-Tabellen:** Abweichungen werden als `disputed` markiert, nie gemittelt.
- **LLM-freie Statistik:** Pooling und Metaregression rechnen deterministisch, nicht über ein Sprachmodell.
- **Read-only-Dashboard:** Lauf-Datenbanken werden vom UI nicht verändert.
- **Geschützte Kernbausteine:** `research_agent/orchestrator.py`, `research_agent/report.py` und `research_agent/meta/pooling.py` sind gitignored und werden nicht committet.

Die aktuelle Arbeit ist in drei Stränge geteilt:

| Strang | Frage | Aktueller Status |
|---|---|---|
| **A/B-Goldstandard** | Wie gut ist die Annotation der 30 Volltexte? | A fertig, B offen, kein Vergleich |
| **C1/Yun** | Wie gut extrahiert die Pipeline numerische Armwerte? | Test gelaufen, nicht freigegeben, G5 offen |
| **dCBT-I-Review-Abgleich** | Passt das Projekt zu Hwang 2025 und Lee 2023? | 1 von 9 Studien bestätigt |

Hinzu kommt die **Zeitpunkt-/Schema-Arbeit** als Querschnitt: Sie soll verhindern, dass Follow-up- oder Median-Werte als Post-Treatment-Treffer gezählt werden.

---

## 3. Goldstandard A/B

### 3.1 Stand

| Gegenstand | Wert |
|---|---|
| Dokumente | 30 |
| A-Effektzeilen | 69 |
| A-Begründungen ohne Effektzeile | 13 |
| A offene Dokumente | 0 |
| B-Effektzeilen | 0 |
| B offene Dokumente | 30 |
| Konsensdatei | nicht vorhanden |
| A/B-Vergleich | nicht verfügbar |
| Kappa/Konflikte | nicht gestartet |

A-Hash: `d9bb867c303dc19ddaf90cce3414ada0f4484b5a03881d65261950db0762a810`
B-Gerüst-Hash: `93802e1798ae5e54ef3896e162e2fdeb2d783486a40239df590ddfa0dfe46d20`

### 3.2 Einordnung

A ist eine vollständige Erstannotation, aber **keine unabhängige Zweitannotation**. B ist ein leeres, verblindetes Gerüst. Solange B nicht zurückkommt und eingefroren ist, gibt es keine belastbare Inter-Rater-Reliabilität und keinen A/B-Vergleich.

Das ist methodisch der wichtigste offene Punkt außerhalb von C1: Ohne B bleibt unklar, ob A systematisch anders annotiert als eine unabhängige Person. Die 69 Zeilen und 13 Begründungen sind wertvoll, aber sie sind kein Ersatz für eine Zweitannotation.

---

## 4. C1/Yun: numerische Extraktion

### 4.1 Datenbasis

Yun et al. 2024 ist der einzige öffentliche Kandidat mit echten Armwerten (N, Mean, SD, Ereigniszahlen) für eine numerische Metaanalyse.

| Ebene | Anzahl |
|---|---:|
| ICO-Records im Release | 699 |
| streng vollständige Records | 410 |
| davon für C1 nutzbar | 275 |
| strukturell ausgeschlossen | 57 |
| numerisch nicht ausreichend belegt | 78 |
| nutzbare Records, kontinuierlich | 174 |
| nutzbare Records, binär | 101 |

Die 275 nutzbaren Records stammen aus 70 Artikeln. Der Dev-Split umfasst **26 Records aus 6 Artikeln**, der Test-Split **249 Records aus 64 Artikeln**. Der Testsplit ist gesperrt und als einmaliger Test verbraucht.

Der Vollaudit dokumentiert:

- **239** Records exakt belegt,
- **35** über Tabellen-/Ergebniskontext belegt,
- **1** mit Quelle korrigiert (Record 12: Interventions-SD 23,34 → 12,34),
- **57** strukturell ausgeschlossen,
- **78** nicht ausreichend belegt.

### 4.2 Dev-Ergebnis

Der akzeptierte Dev-Kandidat `c1_dev_20261111_v6c` mit Prompt `c1-dev-extract-v6` erreicht:

| Kennzahl | Wert |
|---|---:|
| Records | 26/26 |
| erwartete Felder | 140 |
| exakt | **140/140 (100 %)** |
| Abdeckung | 100 % |
| fehlend | 0 |
| falsch | 0 |
| halluziniert | 0 |
| Parse-/Schemafehler | 0 |
| vollständig exakte Records | 26/26 |
| MAE | 0,0 |

Der Dev-Wert ist ein **Ceiling**, keine Generalisierungsschätzung. Die 26 Records stammen aus nur 6 Artikeln; der Test umfasst 249 Records aus 64 Artikeln.

### 4.3 Test-Ergebnis v6c

| Kennzahl | Wert |
|---|---:|
| Records mit Ausgabe | 249/249 |
| erwartete Felder | 1.308 |
| abgedeckt | 1.168/1.308 (89,3 %) |
| exakt | **992/1.308 (75,8 %)** |
| fehlend | 140 (10,7 %) |
| falsch | 176 (13,5 %) |
| halluziniert | 0 |
| Parse-/Schemafehler | 0 |
| vollständig exakte Records | **148/249 (59,4 %)** |
| Records mit mindestens einem Fehler | **101/249 (40,6 %)** |
| MAE über gepaarte Felder | 1,5305 |
| Null-Disziplin | 684/684 (100 %) |

Nach Outcome-Typ:

| Typ | Records | exakt | vollständig exakt |
|---|---:|---:|---:|
| kontinuierlich | 156 | 678/936 (72,4 %) | 79/156 (50,6 %) |
| binär | 93 | 314/372 (84,4 %) | 69/93 (74,2 %) |

Kritische Felder:

| Feld | exakt |
|---|---:|
| `intervention_mean` | 110/156 (70,5 %) |
| `comparator_mean` | 105/156 (67,3 %) |
| `intervention_sd` | 106/156 (68,0 %) |
| `comparator_sd` | 104/156 (66,7 %) |
| `intervention_events` | 76/93 (81,7 %) |
| `comparator_events` | 76/93 (81,7 %) |

Das Fehlerbild ist strukturell sauber, aber numerisch nicht ausreichend:

- 32 Records haben nur fehlende Werte, 69 nur falsche, 0 beides.
- 23 kontinuierliche Records haben alle vier Mean/SD-Felder falsch, während beide N-Felder exakt sind.
- 11 Records haben beide Mean/SD-Arme fehlend.
- Bei binären Records haben 7 alle vier Felder fehlend und 7 beide Event-Felder falsch.
- Kein durchgängiger Richtungsbias; 0 Halluzinationen und 0 Parse-Fehler.

### 4.4 Gates v1

Die Gates sind als Projektstandard v1 bindend und dürfen nicht nachträglich gelockert werden.

| Gate | Anforderung | v6c | Status |
|---|---|---|---|
| G1 Integrität | 249/249 Ausgabezeilen, 0 Parse-/Schemafehler, 0 Halluzinationen | 249/249, 0, 0 | **bestanden** |
| G2 Record-Vollständigkeit | ≥ 95 % Records ohne fehlende Pflichtfelder | 217/249 (87,1 %) | **nicht bestanden** |
| G3 Feldgenauigkeit | ≥ 95 % gesamt und je kritischem Feld | 75,8 %; kritisch 66,7–87,1 % | **nicht bestanden** |
| G4 Record-Genauigkeit | ≥ 90 % Records vollständig exakt | 148/249 (59,4 %) | **nicht bestanden** |
| G5 Unabhängige Validierung | neuer, vorab eingefrorener Holdout; kein Reuse des 249er-Tests | kein Holdout-Manifest | **nicht bestanden** |

**Konsequenz:** v6c ist ein technisch sauberer Kandidatengenerator, aber **keine validierte Extraktion**. Eine assistierte Nutzung ist nur mit 100 % menschlicher Prüfung aller numerischen Werte zulässig; automatisches Pooling ist ausgeschlossen.

### 4.5 Modell-Screening

Auf dem Dev-Set wurde geprüft, ob andere Modelle Qwen schlagen:

| Modell | exakt | Abdeckung | fehlend | falsch | vollständig exakt | Latenz |
|---|---:|---:|---:|---:|---:|---:|
| Qwen 3.5 397B (Baseline) | **140/140 (100 %)** | 100 % | 0 | 0 | 26/26 | 6,67 s |
| DeepSeek V4.1 Flash | 134/140 (95,7 %) | 95,7 % | 6 | 0 | 24/26 | 2,83 s |
| GLM 5.3 | 34/140 (24,3 %) | 24,3 % | 106 | 0 | 6/26 | 5,46 s |

GLM 5.3 war technisch unbrauchbar: 19 leere Antworten und eine abgeschnittene JSON-Antwort. DeepSeek ist näher an Qwen, aber nicht gleichwertig; die 6 fehlenden Felder betreffen zwei Records. **Kein Modell schlägt Qwen auf Dev.** Wegen des Dev-Ceilings ist das ohnehin kein Wirksamkeitsnachweis.

---

## 5. Externer Yun-Benchmark

Der externe Benchmark prüft die C1-Ausgabe gegen die 275 kuratierten Yun-Records.

| Kennzahl | Wert |
|---|---:|
| Referenzrecords | 275 |
| Records mit Ausgabe | 249 |
| Records ohne Ausgabe | 26 |
| erwartete Felder | 1.308 |
| exakt | **993/1.308 (75,9 %)** |
| akzeptabel | **1.005/1.308 (76,8 %)** |
| falsch | 163 |
| fehlend | 140 |
| Abdeckung | 89,3 % |
| MAE gepaart | 1,5211 |
| Kategorien | 151 bestätigt / 98 widersprüchlich / 26 nicht extern validierbar |
| Halluzinationen | 0 |
| Parse-/Schemafehler | 0 |
| A/B-Vergleich | nicht verfügbar |
| Modell-/Netzlauf | nein |

**Zählregel-Hinweis:** Der externe Benchmark weist 993 exakte und 1.005 akzeptable Felder aus, weil er 12 Rundungsabweichungen separat als akzeptabel zählt. Der C1-Testlauf bleibt beim strengen Primärwert **992/1.308 exakt** und **176 falsch**. Die Differenz von einem exakten Feld ist eine Zählregel-/Normalisierungsdifferenz, kein neuer Lauf und keine neue Datenbasis.

Der Benchmark bestätigt damit dasselbe Bild wie C1: Die Struktur ist sauber, die numerische Genauigkeit reicht nicht für eine autonome Freigabe.

---

## 6. dCBT-I-Review-Abgleich

### 6.1 Datenbasis

Im Projekt liegen **9 CBT-I-Primärstudien** mit DOI: 4 aus dem dCBT-I-Pilot und 6 aus dem CBT-I-Pilot, eine Studie in beiden Listen.

Die im Auftrag genannten **30 dCBT-I-Studien existieren so nicht.** `data/golden_effects/documents.json` enthält 30 gemischte Volltexte, davon 5 mit Schlafbezug und **0 dCBT-I-Studien**.

### 6.2 Treffer

| Review | eingeschlossene RCTs | Treffer |
|---|---:|---:|
| Hwang 2025, npj Digital Medicine 8:157 | 29 | **0** |
| Lee 2023, npj Digital Medicine 6:52 | 22 | **1** |

Der einzige Treffer ist **Freeman 2017 (OASIS)** in **Lee 2023**:

- DOI `10.1016/S2215-0366(17)30328-0`, PMCID `PMC5614772`
- N gesamt 3.755, im Projekt und im Review identisch
- Outcomes im Review: ISI, PHQ-9, GAD-7
- Outcomes im Projekt: ISI
- Outcome-Überschneidung: **nur ISI**
- Zeitpunkt Review: 10 Wochen post-treatment
- Zeitpunkt Projekt: post-treatment (Woche 10)
- Wochenvergleich: 10,0 vs. 10,0, Differenz 0,0 (Toleranz 0,5)

Die Review-Tabelle nennt **keine armweisen Mittelwerte oder SD**. Eine numerische Bestätigung der Extraktion ist daraus nicht möglich, nur eine Bestätigung von Studie, Outcome, Zeitpunkt und N.

### 6.3 Nicht zugeordnete Studien

Für die übrigen 8 Studien enthält keine der beiden Review-Listen einen Treffer nach DOI oder Autor/Jahr. Die Ausschlussgründe sind aus den publizierten Kriterien und Abstracts abgeleitet und **plausibel, nicht von den Reviews bestätigt**:

| Studie | Hauptgrund | Konfidenz |
|---|---|---|
| chan_2021 | Jugendliche (M 14,7), Präventionsprogramm | hoch |
| chan_2022 | „youths“ (M 20,0 ± 2,5), keine Depression-/Angst-Outcomes, Publikationsjahr 2022 | niedrig/mittel |
| de_bruin_2015 | 13–19 Jahre, geleitete Self-Help-Sitzungen | hoch |
| de_bruin_2018 | Jugendliche (M 15,6) | hoch |
| egbegi_2021 | In-School-Adoleszente, Gruppen-CBT vor Ort | hoch |
| fucito_2017 | Heavy-Drinking-College-Students, keine Depression-/Angst-Outcomes | mittel |
| morris_2015 | Studierende, Diagnose/Automatisierung unklar | mittel |
| tomfohr_madsen_2020 | 12–18 Jahre, nicht digital | hoch |

### 6.4 Einordnung

Der Review-Abgleich ist **kein externer Goldstandard für die 30 Volltexte**. Er bestätigt genau eine Studie und dort nur ISI, Zeitpunkt und N. Für die dCBT-I-Frage ist die Datenbasis zu klein und zu heterogen; für die 30 Volltexte ist sie thematisch falsch.

---

## 7. Zeitpunktparser und Extraktionsschema

### 7.1 Aktuelle Logik

Der Parser in `public_benchmark/scripts/match_dcbti_review_studies.py` trennt:

- **Post-Treatment:** `post`, `post-treatment`, `post-intervention`, `nachbehandlung`, `behandlungsende`
- **Follow-up:** `follow-up`, `katamnese`
- **Sonstige:** `baseline`, `mid-treatment`
- **Unsicher:** Median-/±-Angaben

Nur Post-Treatment-Wochen dürfen einen Treffer erzeugen. Follow-up-Werte werden separat geführt und nie als Treffer verwendet. Nachgestellte Marker wie `12 weeks follow-up` werden korrekt dem Follow-up zugeordnet.

### 7.2 Unsichere Angaben

Für `follow-up (median 5.8 ± 2.5 years)` gilt jetzt:

- Status `uncertain`
- `follow_up_weeks: []`
- `uncertain_weeks: [302.41]` (5,8 Jahre)
- Rohtext bleibt in `raw`

Die ±-Streuung 2,5 Jahre wird **nicht** als 130,35 Wochen gespeichert. Bei `Post 10 weeks ± 2 weeks` bleibt der Zentralwert 10 als Post-Treatment erhalten; nur die Streuung 2 wird als unsicher behandelt und nicht als Zeitpunkt gespeichert.

### 7.3 Schema

`docs/internal/goldstandard_schema.json` enthält das optionale Feld `time_point_segments` mit:

- `status`: `parsed`, `no_marker`, `uncertain`, `unparsed`, `missing`
- `post_treatment_weeks`
- `follow_up_weeks`
- `other_weeks`
- `uncertain_weeks`
- `ambiguous_post_treatment`
- `raw`

`time_point` bleibt die annotierte Quelle. Das Feld ist optional, damit die eingefrorenen A/B-Dateien und ihre Hashes gültig bleiben.

### 7.4 Reale Abdeckung in A

| Status | Effektzeilen |
|---|---:|
| `missing` | 24 |
| `no_marker` | 3 |
| `uncertain` | 2 |
| `unparsed` | 40 |
| `parsed` | 0 |
| **Gesamt** | **69** |

Die zwei Median-Zeilen sind `uncertain` mit `uncertain_weeks: [302.41]` und `follow_up_weeks: []`. **0 Outcome-Felder wurden verändert.**

Die niedrige `parsed`-Zahl ist kein Parserfehler, sondern eine Datenrealität: Die A-Zeitpunkte enthalten überwiegend `T1`, `T2`, `baseline`, `cross-sectional` oder Jahreszahlen, die ohne T-Label-Konvention nicht in Wochenwerte auflösbar sind.

### 7.5 Tests

- **46 Tests** in `public_benchmark/tests` bestanden.
- Goldstandard A: Validator **0 Fehler, 0 offen**.
- Goldstandard B: mit `--entwurf` **0 Fehler, 30 offen**.
- Keine Outcome-Werte geändert.

---

## 8. P0-Holdout: Stand und Blocker

Der einzige Weg zu G5 ist ein neuer, artikeldisjunkter Holdout außerhalb von Dev und dem verbrauchten Test.

### 8.1 Beschaffung

| Kennzahl | Wert |
|---|---:|
| Query-Treffer September-2026-Frame | 596 |
| artikeldisjunkt zu Yun/Freeze/Dev/Test | 596 |
| Abstract-Screening: ausgeschlossen | 181 |
| vorläufig für Volltext | 415 |
| manuelle Einzelfälle | 65 |
| davon menschlich entschieden | 65 |
| davon assistiert | 0 |
| Shortlist-Artikel | 30 |
| XML-Abruf | 30/30 HTTP 200, 0 Fehler |
| Outcome-Slots in der assistierten Volltextprüfung | 56 (20 + 36) |
| unabhängig verwendbar | 16 |
| überlappend, nicht unabhängig | 10 |
| nicht verwendbar/nicht berichtet | 30 |
| formal verwendbar | 26 |

Die 30 Shortlist-Artikel sind noch **keine endgültige Auswahl**. Für die 36 Slots der zweiten Batch liegt eine menschliche Prüfcheckliste vor; eine finale G5-Freigabe fehlt.

### 8.2 Warum das nicht reicht

- Der Holdout ist noch nicht als 30-Artikel-/100-Record-Datensatz eingefroren.
- Es fehlen finale Artikel-IDs, Input-/Referenz-Hashes und ein G5-fähiges Manifest.
- Die 56 Slots liefern nur 16 unabhängige Outcomes; das ist weit unter 100 Records.
- Der 249er-Test darf nicht als Holdout wiederverwendet werden.
- Der 3-Record-Smoke-Test aus PMC3654355 ist ausdrücklich **kein G5-Holdout**.

**Aktueller Status:** P0 ist fortgeschritten, aber G5 bleibt offen. Kein Modelllauf auf dem Holdout.

---

## 9. Statusmatrix

| Dimension | Status | Bewertung |
|---|---|---|
| Agentenarchitektur | vorhanden | belastbar, aber nicht der Engpass |
| Deterministische Statistik | vorhanden | Pooling, Heterogenität, Sensitivitätsanalysen |
| Quellen-/Zitatprüfung | vorhanden | starkes Alleinstellungsmerkmal |
| Numerische Extraktion | C1 v6c | 75,8 % exakt, nicht freigegeben |
| Unabhängige Validierung | G5 offen | kritischer Blocker |
| Menschliche Zweitannotation B | offen | kein A/B, keine Kappa |
| dCBT-I-Datenbasis | 9 Studien | 1 Review-Treffer, 30 Volltexte thematisch falsch |
| Zeitpunkt-/Schemaarbeit | gehärtet | auf echten Daten noch schmal |
| Assistierte Nutzung | möglich | nur mit 100 % Prüfung |
| Autonome Metaanalyse | nicht erreicht | Gates G2–G5 offen |

---

## 10. Was uns noch fehlt

### 10.1 Unabhängiger G5-Holdout

Das ist der kritischste Pfad. Ohne einen neuen, artikeldisjunkten und vorab eingefrorenen Holdout ist keine belastbare Aussage über einen neuen Kandidaten möglich. Die vorhandenen 30 Shortlist-Artikel und 36 Slots sind ein guter Anfang, aber weder vollständig noch eingefroren.

### 10.2 B-Rücklauf und A/B-Vergleich

B ist seit dem 10.11.2026 ein leeres Gerüst. Es fehlen:

- der externe Rücklauf,
- der B-Abgabe-Hash,
- die Kappa-Berechnung,
- die Konfliktklärung,
- der A/B-Vergleich.

Ohne B bleibt die Annotation qualitativ ungeprüft.

### 10.3 Genauigkeit der numerischen Extraktion

Die Mean/SD- und Comparator-Felder sind der Schwachpunkt. Die Gates fordern 95 % Feldgenauigkeit und 90 % vollständig exakte Records; v6c liegt bei 75,8 % und 59,4 %. Neue Prompt- oder Pipeline-Änderungen müssen auf Dev oder einem neuen Entwicklungsanteil geprüft werden, nicht auf dem verbrauchten Test.

### 10.4 Zeitpunktauflösung für reale Annotationen

`T1`, `baseline`, `cross-sectional` und Jahreszahlen sind keine Wochenwerte. Ohne eine verbindliche T-Label-Konvention bleibt die Segmentierung auf den meisten A-Zeilen wirkungslos. Das ist kein Parsermangel, sondern eine fehlende Annotation­konvention.

### 10.5 Externe numerische Bestätigung für dCBT-I

Die Reviews bestätigen nur eine Studie und dort nur ISI, Zeitpunkt und N. Armweise Mittelwerte und SD fehlen in den Review-Tabellen. Für eine numerische Validierung der dCBT-I-Extraktion braucht es die Primärtexte, nicht die Review-Tabellen.

### 10.6 Menschliche Prüfkapazität

Die assistierte Nutzung von v6c setzt 100 % menschliche Prüfung aller N-, Mean-, SD- und Event-Werte voraus. Das ist bei 40,6 % fehlerhaften Records praktisch eine vollständige Nachannotation. Ohne Kapazität bleibt v6c ein Kandidatengenerator.

---

## 11. Risiken

| Risiko | Wirkung | Gegenmaßnahme |
|---|---|---|
| Testwiederverwendung | scheinbare Verbesserung ohne unabhängigen Nachweis | 249er-Test versiegelt lassen |
| Overfitting auf Dev | 140/140 ist kein Generalisierungsmaß | Holdout als einzige Wirksamkeitsprüfung |
| Fehlerhafte Mean/SD-Blöcke | verzerrte gepoolte Effekte | Blockprüfung, 100 % Prüfung im assistierten Modus |
| Kein G5-Holdout | keine autonome Freigabe möglich | P0 abschließen, Manifest einfrieren |
| B bleibt aus | keine unabhängige Annotation | B-Watcher, kein selbst Annotieren |
| 30 Volltexte als dCBT-I missverstehen | falsche Erwartung an Benchmark | als gemischtes Methoden-Sample benennen |
| Zeitpunkt-Freitext | falsche Post-/Follow-up-Zuordnung | Schema plus T-Label-Konvention |
| Zu optimistische Kommunikation | „validiert“ ohne Gate-Pass | Gates und Assistent-SOP beachten |

---

## 12. Richtung des Projekts

Die Richtung ist richtig, aber sie muss **validierungsgetrieben** bleiben:

1. **Keine neuen Modellläufe ohne freigegebenen Holdout.** Der nächste belastbare Schritt ist Datenbeschaffung und Annotation, nicht Prompt-Tuning.
2. **G5 zuerst.** Ein 30-Artikel-/100-Record-Holdout mit menschlicher Annotation und eingefrorenen Hashes ist die Voraussetzung für jede Aussage „besser als v6c“.
3. **B parallel abschließen.** B ist unabhängig von C1 und liefert die fehlende zweite menschliche Perspektive auf die 30 Volltexte.
4. **v6c nur assistiert nutzen.** Kein automatisches Pooling, keine Imputation, keine Aussage „validiert“.
5. **Zeitpunktkonvention vor der nächsten Annotation.** T-Label und Median-/±-Regeln müssen vor der nächsten Runde feststehen, nicht danach.
6. **Danach erst Pooling und Bericht.** Die statistische Schicht ist vorhanden; sie darf nur mit validierten oder vollständig geprüften Zahlen gefüttert werden.

Das Projekt ist damit weniger ein „fertiger autonomer Forscher“ als eine **validierte Extraktions- und Synthese-Pipeline im Aufbau**. Der größte Hebel liegt derzeit nicht in mehr Modellleistung, sondern in **unabhängigen Daten und menschlicher Prüfung**.

---

## 13. Konkrete nächste Schritte

| Priorität | Schritt | Ergebnis | Aufwand/Risiko |
|---|---|---|---|
| P0 | Holdout-Slots final prüfen (Batch 1: 20, Batch 2: 36), 30 Artikel auswählen, 100 Records annotieren | G5-fähiger Holdout | hoch; Datenarbeit, keine Modellkosten |
| P0 | Holdout-Manifest mit Artikel-IDs, Input-/Referenz-Hashes und Disjunktheit einfrieren | G5-Prüfbarkeit | mittel; Formalarbeit |
| P1 | B-Rücklauf prüfen, Hash einfrieren, Kappa/Konflikte berechnen | A/B-Vergleich | mittel; abhängig von externer Person |
| P1 | v6c ausschließlich assistiert einsetzen, SOP anwenden | keine ungeprüften Zahlen im Pool | laufend; Prüfkapazität |
| P2 | T-Label-Konvention für die nächste Annotation festlegen | nutzbare Zeitpunktsegmente | klein; Schemaarbeit |
| P2 | `uncertain_weeks` und `raw` im Bericht sichtbar machen | nachvollziehbare Zeitpunktentscheidungen | klein; Reporting |
| P3 | Neuen Kandidaten auf Dev/neuem Entwicklungsanteil vorbereiten | Kandidat für G5-Lauf | mittel; kein Testzugriff |
| P3 | Genau einen G5-Lauf durchführen und G1–G5 prüfen | belastbare Freigabe oder klare Ablehnung | hoch; einmalig, nicht wiederholbar |

**Nicht als nächster Schritt geeignet:** ein weiterer Prompt-Lauf auf dem 249er-Test, eine autonome Freigabe von v6c oder eine numerische Metaanalyse aus den 30 gemischten Volltexten.

---

## 14. Artefaktindex

### Goldstandard

- `data/golden_effects/goldstandard_A.json`
- `data/golden_effects/goldstandard_B.json`
- `docs/internal/goldstandard_schema.json`
- `docs/internal/goldstandard_annotationsanleitung.md`
- `docs/internal/HANDOFF_STATUS.md`

### C1/Yun

- `public_benchmark/validation/yun_audit_410.md`
- `public_benchmark/validation/yun_audit_410_summary.json`
- `public_benchmark/validation/c1_freeze_manifest.json`
- `public_benchmark/processed_data/yun_c1_frozen_275.jsonl`
- `public_benchmark/evaluation/c1_pilot/README.md`
- `public_benchmark/evaluation/c1_pilot/decision_v6c.md`
- `public_benchmark/evaluation/c1_pilot/c1_acceptance_gates_v1.md`
- `public_benchmark/evaluation/c1_pilot/gate_report_v6c.json`
- `public_benchmark/evaluation/c1_pilot/runs_test/c1_test_20261111_v6c/test_result.md`
- `public_benchmark/evaluation/c1_pilot/runs_test/c1_test_20261111_v6c/test_error_analysis.md`
- `public_benchmark/evaluation/c1_pilot/model_screen_20261112.md`

### Externer Benchmark

- `public_benchmark/external_benchmark/external_benchmark_results_v1.json`
- `public_benchmark/external_benchmark/external_benchmark_results_v1.md`
- `public_benchmark/external_benchmark/external_benchmark_errors_v1.csv`
- `public_benchmark/scripts/run_external_benchmark.py`

### dCBT-I und Zeitpunkt

- `public_benchmark/external_benchmark/dcbti_review_overlap_v1.md`
- `public_benchmark/external_benchmark/dcbti_review_overlap_v1.json`
- `public_benchmark/scripts/match_dcbti_review_studies.py`
- `public_benchmark/scripts/segment_timepoint_schema.py`
- `public_benchmark/tests/test_dcbti_review_overlap.py`
- `public_benchmark/tests/test_timepoint_schema.py`

### Holdout

- `public_benchmark/evaluation/c1_pilot/p0_external_holdout_20261112.md`
- `public_benchmark/evaluation/c1_pilot/holdout_plan_20261112.md`
- `public_benchmark/evaluation/c1_pilot/holdout_manifest_p0_20261112.json`
- `public_benchmark/evaluation/c1_pilot/holdout_fulltext_audit_20261112.md`
- `public_benchmark/evaluation/c1_pilot/holdout_p0_20261112/fulltext_review_batch1_v1.md`
- `public_benchmark/evaluation/c1_pilot/holdout_p0_20261112/fulltext_review_batch2_v1.md`
- `public_benchmark/evaluation/c1_pilot/holdout_p0_20261112/fulltext_review_batch2_human_checklist_v1.md`

---

## 15. Grenzen dieses Berichts

- Der Bericht ist eine **Synthese vorhandener Artefakte**, kein neuer Modell- oder Netzlauf.
- Die Zahlen aus C1-Test und externem Benchmark unterscheiden sich je nach Zählregel (streng exakt vs. akzeptabel inkl. Rundung). Beide Werte sind getrennt ausgewiesen.
- B ist leer; es gibt keine unabhängige Zweitannotation und keine Kappa-Aussage.
- Der G5-Holdout ist nicht eingefroren; alle Aussagen zur Generalisierung bleiben vorläufig.
- Die dCBT-I-Ausschlussgründe sind plausibel, aber nicht von den Reviews bestätigt.
- Die Zeitpunktsegmentierung ist auf den echten A-Daten nur für wenige Zeilen numerisch auflösbar; `unparsed` ist dort ein Datenbefund, kein Parserfehler.
- Es wurden keine Outcome-Werte verändert und keine geschützten Kernbausteine angefasst.
