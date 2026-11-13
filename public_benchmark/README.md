# Öffentliches B-Experiment: Recherche- und Kompatibilitätsbericht

Stand: 2026-11-11

Arbeitsbereich: `public_benchmark/`

Status: **Recherche und Referenzaudit abgeschlossen; 275 C1-Records eingefroren; Dev-Pilot vorbereitet, nicht gestartet; kein Modelllauf; keine Änderung an A oder B.**

## Kurzentscheidung

Das bisherige B-Experiment wird **nicht** ersetzt. Die öffentlichen Quellen
sind unterschiedlich gut geeignet:

- **Yun et al. 2024** ist der einzige Kandidat mit echten Armwerten
  (N, Mean, SD, Ereigniszahlen) und damit der primäre Kandidat für ein
  neues **Experiment C** zur numerischen Extraktion. Der Audit zeigt jedoch,
  dass die Referenz vor C kuratiert werden muss; Yun ist noch kein
  einsatzfähiger Goldstandard.
- **Evidence Inference 2.0** ist wertvoll für die semantische Prüfung von
  Intervention, Comparator, Outcome und Evidenzstellen, liefert aber keine
  numerischen Metaanalyse-Werte.
- Der **DTA-Korpus** ist diagnostische Testgenauigkeit (2x2) und keine
  Intervention-vs-Kontrolle-Metaanalyse; er ist kein B-Ersatz.

A wurde nicht geöffnet. B ist weiterhin nicht zurückgeliefert; es gibt
keinen B-Abgabe-Hash und keinen A/B-Vergleich. Der B-Watcher bleibt
unverändert. Der Yun-Referenzaudit ist abgeschlossen; er begründet keine
Ablösung von B, sondern einen Kuratierungsschritt vor Experiment C.

## 1. Ausgangslage

Unser bisheriges Design:

- **A:** erste Annotation durch den Assistenten, 30 dCBT-I-Volltexte,
  69 Effektzeilen und 13 Begründungen ohne Effektzeile.
- **B:** unabhängige menschliche Zweitannotation auf denselben 30 Texten;
  das Gerüst enthält 30 Dokumente und 30 leere Arbeitsblätter.
- **Ziel:** unabhängige Evaluation von Intervention, Comparator, Outcome,
  Zeitpunkt, N, Mean und SD.

Der dCBT-I-Nachbau von Tsai et al. 2022 ist abgeschlossen und reproduziert
(eigener gepoolter Hedges g = −0,584 [−1,029; −0,139] gegenüber publiziert
−0,58 [−1,03; −0,13]). Diese Arbeit ist von der Benchmark-Frage getrennt.

## 2. Gefundene Datensätze und direkte Links

| Kandidat | Paper | Repository / Download | Lokaler Pfad |
|---|---|---|---|
| Yun et al. 2024 | [PMLR](https://proceedings.mlr.press/v252/yun24a.html), [PMC12448672](https://pmc.ncbi.nlm.nih.gov/articles/PMC12448672/) | [GitHub](https://github.com/hyesunyun/llm-meta-analysis) | `raw_data/yun_llm_meta_analysis` |
| Evidence Inference 2.0 | [ACL Anthology](https://aclanthology.org/2020.bionlp-1.13/) | [GitHub](https://github.com/jayded/evidence-inference), [v2.0.tar.gz](https://evidence-inference.ebm-nlp.com/v2.0.tar.gz) | `raw_data/evidence_inference`, `raw_data/evidence_inference_v2_0` |
| DTA-Korpus | [PMC6371350](https://pmc.ncbi.nlm.nih.gov/articles/PMC6371350/) | [Zenodo 2574710](https://zenodo.org/record/2574710) (nur Paper), [Datensatz 1303259](https://zenodo.org/api/records/1303259) | `raw_data/dta_cochrane/CL145_open_set_20181101` |

Der DTA-Datensatz liegt **nicht** unter Zenodo 2574710. Dort befindet sich
nur das Paper-PDF. Die eigentliche Datei ist
`CL145_open_set_20181101.zip` unter Zenodo 1303259.

## 3. Yun et al. 2024

### 3.1 Was veröffentlicht ist

- 120 RCT-Artikel, ausschließlich **Abstract + Results** als
  Markdown- und XML-Auszüge; keine vollständigen PDFs und keine
  Methoden-/Diskussionsteile.
- 699 ICO-Records: 10 Artikel / 43 Records im Dev-Split, 110 Artikel /
  656 Records im Test-Split.
- Nach Releasedaten: **517 kontinuierlich, 182 binär**. Das Paper nennt
  516/183; die Abweichung ist dokumentiert, nicht korrigiert.
- 410 Records sind unter einer strengen Feldregel vollständig:
  261 kontinuierlich und 149 binär. Das Release-Flag
  `is_data_complete` steht bei 412 Records auf `TRUE`; zwei davon
  (IDs 635/636) haben keine Gruppengrößen.
- 516 Records haben einen nichtleeren `notes`-Eintrag. Das sind informelle
  Anmerkungen, keine strukturierte Begründung.
- 471 Records verweisen auf eine relevante Tabelle, 98 auf eine Abbildung,
  105 auf eine Tabelle in Grafikform.
- 73 Outcome-Texte enthalten einen Zeitmarker (Tag/Woche/Monat/Jahr), aber
  es gibt **kein separates Zeitpunktfeld**.

Die vollständigen Referenzwerte stehen in
`evaluation/data/annotated_rct_dataset.json` und `.csv`; die Texte liegen
unter `evaluation/data/no_attributes_markdown_files/` (120 Dateien) sowie
als XML vor. Es gibt zusätzlich vier Fallstudien-Dokumente, die nicht Teil
der 699 Records sind.

### 3.2 Feldabdeckung

| Unser Feld | Yun | Bemerkung |
|---|---|---|
| Study ID | ja | `pmcid` |
| Intervention | ja | Freitext |
| Comparator | ja | Freitext |
| Outcome | ja | Freitext, teils mit Zeitpunkt im Text |
| Zeitpunkt | **nein** | kein eigenes Feld; nur teils in `outcome`/`notes` |
| Intervention N | ja | `intervention_group_size` |
| Comparator N | ja | `comparator_group_size` |
| Intervention Mean | ja | nur kontinuierliche Records |
| Intervention SD | ja | nur kontinuierlich; teils aus KI zurückgerechnet |
| Comparator Mean | ja | nur kontinuierlich |
| Comparator SD | ja | nur kontinuierlich |
| Quellenstelle | **nein** | keine Evidenzspanne, kein Zitat |
| Begründung | teilweise | `notes`, nicht strukturiert |

### 3.3 Annotatoren und Individualannotationen

Laut Paper annotierten **zwei Co-Autoren mit Informatik-Hintergrund** jeden
Record zunächst unabhängig und stimmten sich anschließend in regelmäßigen
Treffen auf die endgültige Annotation ab. Eine klinische Forscherin wurde
bei Grenzfällen konsultiert.

Veröffentlicht wurden nur die **konsolidierten** Records. Es gibt keine
Annotator-IDs, keine unabhängigen Einzelannotationen und keine
Adjudikationsakte. Damit ist Yun eine menschliche Referenzannotation
(Ebene 1/3), aber **keine unabhängige Zweitannotation** im Sinne unseres B.

### 3.4 Stichprobenprüfung

Fünf Records wurden gegen die mitgelieferten Texte geprüft. Details stehen
in `validation/yun_sample_check.md`.

- **4 von 5** sind exakt nachvollziehbar.
- **Record 12 (PMC2667135):** Referenz-SD Intervention = 23,34; die Tabelle
  im Artikel zeigt 12,34. Das ist wahrscheinlich ein Zahlendreher in der
  Referenz. Der Wert wurde nicht korrigiert.
- Zusätzlich: IDs 635/636 sind als vollständig geflaggt, obwohl N fehlt.

Diese fünf Fälle waren der Anlass für den größeren Audit in Abschnitt 3.7.
Sie sind nicht die Entscheidungsgrundlage; die Prüfung von 30
stratifizierten Records plus drei Problemfällen ersetzt diese kleine
Stichprobe.

### 3.5 Technische Befunde

1. Paper und Release unterscheiden sich bei den Outcome-Typen (516/183 vs.
   517/182).
2. Paper nennt 413 ausreichend vollständige Records; Release: 412 per Flag,
   410 per strenger Feldregel.
3. Zwei als vollständig geflaggte Records haben keine Gruppengrößen.
4. Mindestens ein Referenzwert weicht vom Artikeltext ab (Record 12).
5. Kein Zeitpunktfeld, keine Quellenstelle, keine individuellen Labels.
6. Keine separaten menschlichen Annotation Guidelines; die YAML-Dateien
   unter `evaluation/templates/` sind Modell-Prompts.
7. Die 120 XML-Auszüge enthalten keine Lizenzmetadaten; die Artikelrechte
   müssen pro PMC-Artikel geprüft werden.

### 3.6 Lizenz

Repository und Annotationen: **Apache-2.0**. Die Artikelauszüge stammen aus
PMC-Open-Access-Artikeln, sind aber nicht durch Apache-2.0 allein
re-lizenziert. Für lokale Forschung unkritisch; für eine öffentliche
Weitergabe der Texte ist die Einzellizenz jedes Artikels zu prüfen.

### 3.7 Referenzaudit: 30 stratifizierte Records plus Problemfälle

Geprüft wurden 15 kontinuierliche und 15 binäre Zufallsrecords (Seed
`20261111`, je ein Record aus einem anderen Artikel) sowie die bewusst
ausgewählten Problemfälle 12, 635 und 636. Die 30 Zufallsrecords umfassen
104 nichtleere Referenzfelder.

| Maß | Zähler / Nenner | Quote |
|---|---:|---:|
| Harte Zahlenfehler auf Feldebene | 4 / 104 | 3,8 % |
| Nicht prüfbare Felder | 4 / 104 | 3,8 % |
| Records mit strukturellem ICO-Fehler | 6 / 30 | 20,0 % |
| Records mit klarem Fehler (Zahlen- oder Strukturfehler) | 8 / 30 | 26,7 % |
| Records mit irgendeinem Befund (inkl. nicht prüfbar/leer) | 11 / 30 | 36,7 % |
| Leere Referenzen trotz Werten im Text | 2 / 30 | 6,7 % |

Die harten Zahlenfehler betreffen die Records 83 (falsche Kohorte) und 694
(Median/IQR als Mean/SD). Vier Felder in Record 303 sind nur in Bildtabellen
und daher nicht prüfbar. Sechs Records sind strukturell kein gültiger
Interventions-Kontroll-Vergleich: 670, 268 (kombinierte Arme/Outcomes), 178
(Ein-Arm-Vorher-Nachher), 62 (observational), 543 und 484 (Baseline).

Die 30er-Stichprobe bestätigt die drei Problemfälle: Record 12 hat eine
falsche Interventions-SD (23,34 statt 12,34), 635 und 636 haben korrekte
Means/SDs, aber fehlende Gruppengrößen und trotzdem
`is_data_complete=TRUE`. Die drei Fälle sind bewusst ausgewählt und nicht in
die 30er-Quote eingerechnet.

Die bisherige 5-%-Schwelle ist auf Feldebene mit 3,8 % knapp
unterschritten, auf Recordebene mit 26,7 % aber deutlich überschritten. Für
die Entscheidung ist die Recordebene maßgeblich, weil ein strukturell
falscher ICO auch mit korrekten Einzelzahlen nicht als Effekt nutzbar ist.
Vor Experiment C sind daher die 410 streng vollständigen Records zu
auditieren und zu kuratieren. Details, Recordtabelle und 95-%-Intervalle:
`validation/yun_audit_30.md`.

### 3.8 Vollaudit der 410 streng vollständigen Records

Der Vollaudit ist abgeschlossen. Von 410 Records sind **275 für C1 nutzbar**:
239 exakt belegt, 35 über Tabellen-/Ergebniskontext belegt und einer mit
Quelle korrigiert. **57 Records sind strukturell ausgeschlossen** (25
Baseline, 17 Vorher-Nachher, 6 observational, 6 gepoolt, 1 Median, 1
quasi-experimentell, 1 Ein-Arm). **78 Records sind numerisch nicht
ausreichend belegt** und bleiben im Ledger, werden aber nicht für C1
freigegeben.

Die Korrektur betrifft Record 12: Interventions-SD `23,34` wird mit der
Tabelle `12.34` auf `12,34` korrigiert; der Originalwert bleibt erhalten.
Details: `validation/yun_audit_410.md`, `validation/yun_audit_410.jsonl`.

Die 275 nutzbaren Records sind eingefroren: 26 Dev-Records aus 6 Artikeln
und 249 Test-Records aus 64 Artikeln. Der Testsplit ist gesperrt. SHA-256 und
Dateigrößen stehen in `validation/c1_freeze_manifest.json`; der Dev-Pilot
ist unter `evaluation/c1_pilot/` vorbereitet, aber nicht gestartet.

## 4. Evidence Inference 2.0

### 4.1 Was veröffentlicht ist

Offizielles v2.0-Archiv:

- 12.865 ICO-Prompts aus 3.372 Artikeln.
- 24.686 Annotationszeilen aus 3.346 Artikeln.
- 8 UserIDs.
- 4.454 Textdateien; alle 3.346 annotierten PMCIDs haben einen Text.
- Labels: 11.129 `no significant difference`, 7.630
  `significantly increased`, 5.927 `significantly decreased`.
- 365 Zeilen mit `Valid Label = False`, 226 mit
  `Valid Reasoning = False`.
- 924 Zeilen ohne gültige Evidenzspanne (`-1`).

Der Repo-Snapshot (Commit `a661e8c`) enthält 4.470 Textdateien und eine
andere `annotations_merged.csv` als das offizielle Archiv. Das offizielle
Archiv enthält 693 Zeilen mit dem Tippfehler `significantly increase`; für
die Zählung wurden sie zu `significantly increased` normalisiert. Die
Rohdaten wurden nicht verändert.

### 4.2 Annotatoren und Individualannotationen

Der Prozess hat **drei Rollen**:

1. Prompt-Generator,
2. Annotator (M.D.),
3. Verifier.

Der Verifier sieht die Antworten von Prompt-Generator und Annotator, ohne
zu wissen, welche Rolle welche Antwort geliefert hat. Er akzeptiert oder
verwirft Label und Begründung. Es gibt **keine einzelne adjudizierte
Endannotation** pro Prompt.

Die UserIDs sind sichtbar, aber die Rolle ist nicht als Spalte
dokumentiert. Die Verteilung (UserID 0 mit 12.180 von 24.686 Zeilen) passt
zum Prompt-Generator, ist aber aus den Daten allein nicht bewiesen.

Von 10.739 Prompts mit mehreren UserIDs sind 96,87 % der Gruppen
unanim. Eine naive paarweise Cohen's Kappa lag je nach User-Paar bei
etwa 0,74–1,00. Das ist **kein belastbares B-IRR-Maß**, weil hier Rollen
und teils mehrere Evidenzzeilen pro Prompt/User verglichen werden, nicht
zwei gleichwertige, verblindete Zweitannotatoren.

### 4.3 Feldabdeckung

| Unser Feld | Evidence Inference |
|---|---|
| Study ID | ja (`PMCID`) |
| Intervention | ja |
| Comparator | ja |
| Outcome | ja |
| Zeitpunkt | nein (kein separates Feld) |
| Intervention N | nein |
| Comparator N | nein |
| Intervention Mean / SD | nein |
| Comparator Mean / SD | nein |
| Quellenstelle | ja (`Annotations`, `Evidence Start/End`) |
| Begründung | ja, Evidenztext; Verifier-Flags |

### 4.4 Eignung

Evidence Inference ist **kein numerischer B-Ersatz**. Es ist ein guter
komplementärer Benchmark für die semantische ICO-Zuordnung und die
Evidenzstellen-Retrieval. Für N/Mean/SD fehlen sämtliche Werte.

### 4.5 Lizenz

Code und Annotationen: **MIT**. Die 4.454 Textdateien stammen aus PMC-
Open-Access-Artikeln; die MIT-Lizenz deckt diese Texte nicht automatisch.
Die Einzellizenzen sind pro Artikel zu prüfen.

## 5. DTA-Korpus

### 5.1 Was veröffentlicht ist

- 63 systematische Reviews.
- 1.354 diagnostische Tests.
- 1.738 eingeschlossene Studie-Review-Einträge; daraus 1.663 eindeutige
  `study_id`-Werte, weil Studien in mehreren Reviews vorkommen können.
- 6.699 ausgeschlossene Referenzen.
- 6.433 `result`-Elemente; **5.848** enthalten eine vollständige
  2x2-Tabelle (`tp`, `fp`, `fn`, `tn`).
- 585 Findings-Testblöcke; 6 Reviews haben keinen Findings-Block.
- Forest-Plot-Bilder und Review-/Studienmetadaten.

Die Datei ist eine HTML/XML-Struktur mit eingebetteten Review-Daten, keine
Sammlung von Primärstudien-Volltexten.

### 5.2 Feldabdeckung

| Unser Feld | DTA |
|---|---|
| Study ID | ja (`review_id` + `study_id`) |
| Intervention | nur Index-Test, kein Behandlungseffekt |
| Comparator | Referenzstandard, keine Kontrollgruppe |
| Outcome | Target Condition / diagnostische Genauigkeit |
| Zeitpunkt | nein |
| Intervention N | nur aus 2x2 ableitbar |
| Comparator N | nur aus 2x2 ableitbar |
| Mean / SD | nein |
| Quellenstelle | nein (nur Review-Daten, keine Primärtexte) |
| Begründung | nein |

### 5.3 Eignung und Lizenz

Fachlich ist DTA **diagnostische Testgenauigkeit**, nicht unsere
Intervention-vs-Kontrolle-Aufgabe. Es fehlen Primärtexte und kontinuierliche
Armwerte. Lizenz: **CC BY-NC 4.0**, also nicht kommerziell. Als kleiner
Nebencheck für 2x2-Extraktion denkbar, nicht als primärer B-Benchmark.

## 6. Kompatibilitätsmatrix

| Feld | Yun 2024 | Evidence Inference 2.0 | DTA |
|---|---|---|---|
| Study ID | ja | ja | ja |
| Intervention | ja | ja | nein (Index-Test) |
| Comparator | ja | ja | nein (Referenzstandard) |
| Outcome | ja | ja | nein (Target Condition) |
| Zeitpunkt | nein | nein | nein |
| Intervention N | ja (643/699) | nein | nur 2x2 |
| Comparator N | ja (643/699) | nein | nur 2x2 |
| Intervention Mean | ja (316/699) | nein | nein |
| Intervention SD | ja (276/699) | nein | nein |
| Comparator Mean | ja (310/699) | nein | nein |
| Comparator SD | ja (275/699) | nein | nein |
| Quellenstelle | nein | ja | nein |
| Begründung | teilweise (`notes`) | ja (Evidenztext) | nein |
| Individuelle Labels | nein | ja, mit Rollen-Caveat | nein |
| Numerische Metaanalyse | ja, 410 vollständig | nein | nein |

## 7. Bewertung 0–10

Bewertung aus Sicht **unseres numerischen B-Experiments**; die Gewichtung
ist auf unser Ziel bezogen, nicht allgemein.

| Kriterium | Yun 2024 | Evidence Inference | DTA |
|---|---:|---:|---:|
| Inhaltliche Übereinstimmung | 8 | 4 | 2 |
| Qualität der Referenzannotation | 4 | 7 | 8 |
| Verfügbarkeit der Volltexte | 7 | 8 | 1 |
| Unabhängigkeit der Annotatoren | 5 | 6 | 3 |
| Numerische Extraktion | 9 | 1 | 3 |
| Reproduzierbarkeit | 8 | 8 | 7 |
| **Gesamt für unser B** | **6,5 (vorläufig)** | **4,5** | **2,5** |

Die Gesamtnote ist eine qualitative Gewichtung für unser B-Ziel, kein
arithmetisches Mittel der Kriterien.

Einordnung:

- Yun: einziger numerischer Kandidat, aber konsolidierte Annotation,
  strukturelle ICO-Fehler und einzelne harte Datenfehler. Für Experiment C
  erst nach Vollaudit und Kuratierung geeignet, nicht als B-Ersatz. Die
  Abwertung von 7,5 auf 6,5 ist vorläufig und folgt aus der hohen
  Record-Fehlerquote, nicht aus einem neuen Modelllauf.
- Evidence Inference: gut für semantische ICO-/Evidenzprüfung, aber ohne
  N/Mean/SD. Als B-Ersatz ungeeignet.
- DTA: hohe fachliche Qualität, aber falsche Aufgabe und keine
  Primärtexte. Als B-Ersatz ungeeignet.

## 8. Goldstandard, Zweitannotation und Adjudikation

Die drei Ebenen sind methodisch nicht identisch:

1. **Existierende menschliche Goldstandard-Annotation:** Yun (konsolidiert),
   DTA (Cochrane-Extraktion).
2. **Unabhängige menschliche Zweitannotation:** unser B; bei Evidence
   Inference nur eingeschränkt, weil die Rollen Prompt-Generator/Annotator/
   Verifier nicht zwei gleichwertige Rater sind.
3. **Adjudizierte Endannotation:** Yun nach Konsens; DTA nach
   Review-Extraktion. Evidence Inference hat keine einzelne adjudizierte
   Endannotation pro Prompt.

Für Yun und DTA ist daher **keine Inter-Rater-Reliabilität** berechenbar.
Für Evidence Inference ist eine naive Kappa-Berechnung möglich, aber wegen
der Rollenmischung und wiederholter Evidenzzeilen nicht als B-IRR
interpretierbar.

Cohen's Kappa ist nur für kategoriale Felder sinnvoll (z. B. Outcome-Typ,
Richtung, Vorhandensein eines Werts). Für N/Mean/SD sind exakte Treffer,
absolute Fehler und MAE/RMSE die passenden Maße; Kappa ersetzt sie nicht.

## 9. Empfohlene Experimentstruktur

### Experiment A — bestehend

Unverändert: unsere Annotation auf den 30 dCBT-I-Dokumenten. A bleibt
geschlossen, solange B nicht ordnungsgemäß eingefroren ist.

### Experiment B — bestehend, weiterhin vorgesehen

Unabhängige menschliche Zweitannotation auf denselben 30 Dokumenten. B ist
weiterhin blockiert, weil kein Rücklauf vorliegt. Kein A/B-Vergleich und
keine Kappa-Berechnung, bevor der B-Hash eingefroren ist.

### Experiment C — neu, öffentlich

**C1 (primär, numerisch): Yun et al. 2024.**

- Vor C: die 410 streng vollständigen Records vollständig auditieren und
  kuratieren; `is_data_complete` nicht als Wahrheit übernehmen.
- Originaltexte verwenden, Referenzannotation bis zum Abschluss der
  Extraktion zurückhalten.
- Unser Schema auf Yun abbilden; alle Transformationen dokumentieren.
- Dev-Split (43 Records) nur für Entwicklung/Prompt-Anpassung.
- Test-Split (656 Records) einmalig und ohne Anpassung auswerten.
- Nach der Kuratierung alle 699 Records auswerten, aber 410 streng
  vollständige und 289 unvollständige getrennt berichten; strukturell nicht
  estimierbare Records als eigene Kategorie führen.
- Metriken: Precision/Recall/F1 auf ICO-Ebene; exakte Treffer und MAE je
  Feld; getrennte Fehlerklassen; keine erfundenen Werte.

**C2 (komplementär, semantisch): Evidence Inference 2.0.**

- Nur ICO-Zuordnung und Evidenzstellen bewerten.
- Keine N/Mean/SD-Auswertung.
- Rollen-Caveat dokumentieren; keine B-IRR-Behauptung.

**C3 (optional, diagnostisch): DTA.**

- Nur 2x2-Extraktion, nicht unsere primäre Aufgabe.
- Wegen CC BY-NC 4.0 nur nicht-kommerziell.

## 10. Konkreter nächster Schritt

**Kein Modelllauf in diesem Schritt.** Empfohlen:

1. **Yun-Audit abgeschlossen:** 30 stratifizierte Records plus die
   Problemfälle 12, 635 und 636 wurden geprüft. Ergebnis: 4/104 harte
   Zahlenfehler (3,8 %), 6/30 strukturelle Fehler (20,0 %) und 8/30 Records
   mit mindestens einem klaren Fehler (26,7 %). Details in
   `validation/yun_audit_30.md`.
2. **Vollaudit und Kuratierung abgeschlossen:** 410 Records geprüft; 275
   sind für C1 nutzbar, 57 strukturell ausgeschlossen und 78 nicht
   ausreichend belegt. Die kuratierte Referenz steht in
   `validation/yun_audit_410.jsonl`; die 135 nicht nutzbaren Records bleiben
   im Ledger.
3. **Freeze abgeschlossen:** Der 275er-Datensatz ist mit SHA-256 gepinnt
   (`validation/c1_freeze_manifest.json`); 26 Dev- und 249 Test-Records sind
   getrennt. Der Test bleibt gesperrt.
4. **C1-Dev-Pilot vorbereitet:** Eingabe und Referenz für 26 Dev-Records
   liegen unter `evaluation/c1_pilot/`. Ein Lauf benötigt eine ausdrückliche
   Freigabe; keine Testdaten zur Prompt-Optimierung.
5. **B unverändert lassen:** Der B-Watcher wird nicht angefasst; vor einem
   Eingriff Status prüfen, kein A öffnen, kein B-Hash erfinden.

Der größte Hebel ist jetzt die Kuratierung der Referenz. Ein Modelllauf auf
den ungeprüften 410 Records würde einen Teil der sichtbaren Referenzfehler
als Modellfehler messen.

## 11. Artefakte und Reproduzierbarkeit

| Datei | Inhalt |
|---|---|
| `dataset_inventory.json` | Zählungen, Vollständigkeit, Felder, bekannte Probleme |
| `source_registry.json` | Quellen, Commits, Archive, SHA-256 |
| `schema_mapping.json` | Feldmapping und Transformationsregeln |
| `license_audit.md` | Lizenzprüfung je Kandidat |
| `annotation_guidelines/` | Yun-Schema, Evidence-Rollen, DTA-Abgrenzung |
| `processed_data/yun_ico_records.jsonl` | 699 verlustfreie Yun-Projektionen |
| `validation/yun_sample_check.md` | Fünf-Record-Prüfung inkl. Fehler |
| `validation/yun_audit_30.md` | Auditbericht: 30 stratifizierte Records plus Problemfälle |
| `validation/yun_audit_results.json` | Recordbefunde, Status und Fehlerquoten |
| `validation/yun_audit_sample.json` | Auswahl, Seed und Stratifizierung |
| `validation/yun_audit_410.md` | Vollaudit der 410 streng vollständigen Records |
| `validation/yun_audit_410.jsonl` | Kuratierte Referenz mit Auditstatus und Korrektur |
| `validation/yun_audit_410_summary.json` | Statuszählungen des 410er-Audits |
| `validation/c1_freeze_manifest.json` | SHA-256 und Splitzahlen des 275er-Freeze |
| `processed_data/yun_c1_frozen_275.jsonl` | Eingefrorene C1-Referenz |
| `processed_data/yun_c1_dev_26.jsonl` | 26 Dev-Records |
| `processed_data/yun_c1_test_249.jsonl` | 249 gesperrte Test-Records |
| `evaluation/c1_pilot/` | Dev-Eingabe, Referenz und Pilotprotokoll |
| `scripts/build_c1_freeze.py` | reproduzierbarer Freeze-Generator |
| `validation/checksums.sha256` | SHA-256 für Archive und Schlüsseldateien |
| `evaluation/README.md` | geplantes Experiment C, noch kein Lauf |
| `scripts/build_inventory.py` | reproduzierbare Inventarerzeugung |
| `external_benchmark/external_benchmark_research_v1.md` | Recherche zu Yun, Evidence Inference, PICO und SRDR+ |
| `external_benchmark/external_benchmark_schema_v1.json` | einheitliches Referenzschema |
| `external_benchmark/external_benchmark_results_v1.json` | maschinenlesbare Benchmark-Ergebnisse |
| `external_benchmark/external_benchmark_results_v1.md` | Benchmark-Bericht mit Fehleranalyse |
| `external_benchmark/external_benchmark_errors_v1.csv` | Einzelabweichungen je Feld |
| `scripts/run_external_benchmark.py` | reproduzierbarer externer Benchmark |
| `external_benchmark/dcbti_review_overlap_v1.md` | Abgleich der 9 CBT-I-Studien mit Hwang 2025 und Lee 2023 |
| `external_benchmark/dcbti_review_overlap_v1.json` | maschinenlesbarer Review-Abgleich inkl. Zeitpunktsegmenten |
| `scripts/match_dcbti_review_studies.py` | Abgleich und Zeitpunktparser (Post-Treatment, Follow-up, Mid) |
| `scripts/segment_timepoint_schema.py` | ergänzt `time_point_segments` in einer Kopie der Goldstandard-Datei |
| `tests/test_external_benchmark.py` | Tests für Normalisierung, Metriken und Kategorien |
| `tests/test_dcbti_review_overlap.py` | Tests für Review-Abgleich und Zeitpunktsegmentierung |
| `tests/test_timepoint_schema.py` | Tests für Schemafeld und unveränderte Outcome-Werte |

Reproduktion:

```bash
python public_benchmark/scripts/build_inventory.py
python public_benchmark/scripts/run_external_benchmark.py
```

Die Rohdaten unter `public_benchmark/raw_data/` sind lokal vorhanden, aber
wegen Größe und Lizenz nicht mitcommittet. Sie sind über Git-Commits und
SHA-256 gepinnt:

- Yun: `1bc768d4d098c727c9866eeff909297c38a3e84c`
- Evidence Inference: `a661e8c14f973398380c8865cf2f27a535aaaf6d`
- Evidence-v2.0-Archiv: `6abe0d4ec0d331834981c0171c3c79d47515761867f82f1dc6066e43863a1586`
- DTA-Archiv: `f921cf6f1a9236c86f89e7c646497639f45e8ff8fcf56008c1b27422829fec4f`

## 12. Grenzen

- Keine Rechtsberatung; die PMC-Einzellizenzen der Artikeltexte wurden
  nicht pro Artikel geprüft.
- Kein vollständiges Audit aller 699 Yun-Records; geprüft wurden 30
  stratifizierte Records plus die drei Problemfälle.
- Keine neuen Modellvorhersagen in diesem Auftrag; die Genauigkeitsmessung
  bezieht sich auf den vorhandenen eingefrorenen C1-Testlauf.
- Keine unabhängige Zweitannotation und kein B-Rücklauf; A/B bleiben
  unverändert.
- Die Zahlen zu Yun und Evidence Inference stammen aus den gepinnten
  Releases; Paper und Release weichen in einzelnen Zählungen ab.

## Entscheidungsregel

Die Entscheidung, das bestehende B-Experiment zu ersetzen, wird **nicht**
getroffen. Der Audit bestätigt die Datenqualität nicht vorbehaltlos: Yun
bleibt ein zusätzliches Experiment C, aber erst nach Vollaudit und
Kuratierung der Referenz. Evidence Inference ergänzt die semantische
Prüfung. DTA bleibt eine optionale diagnostische Nebenprüfung.
