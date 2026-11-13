# Externe Goldstandard-Datensätze: Recherche und Eignung (v1)

Stand: 2026-11-13. Auftrag: Prüfung, ob öffentliche, wissenschaftlich
annotierte Datensätze die Outcome-Extraktion unabhängig validieren können,
ohne die produktiven Studienwerte oder die Zähler 8/6/22/14 zu verändern.

**Kurzfassung:** Für die numerische Extraktion ist **Yun et al. 2024** die
einzige direkt geeignete Referenz. Evidence Inference 2.0 ergänzt die
semantische ICO-Prüfung, enthält aber keine Armwerte. PICO-Corpus ist
thematisch und lizenzrechtlich ungeeignet. SRDR+ ist prinzipiell eine gute
Quelle für Extraktionstabellen, aber ein konkretes dCBT-I-/Insomnie-Projekt
mit öffentlich abrufbarer Tabelle wurde nicht nachgewiesen.

## 1. Methodik

- Nur offizielle Repositories, Archivlinks und Publikationen.
- Originaldaten wurden lokal unverändert archiviert und über Git-Commit
  beziehungsweise SHA-256 gepinnt (`source_registry.json`).
- Keine Modell- oder Netzlaufzeit in diesem Auftrag; der Benchmark wertet
  ausschließlich bereits vorhandene, eingefrorene Ausgaben aus.
- Referenzwerte wurden nicht neu annotiert und nicht korrigiert. Die einzige
  Korrektur (Record 12, SD 23,34 → 12,34) stammt aus dem früheren
  Quellen-Audit und ist als `corrected_with_source` dokumentiert.

## 2. A. Numerical RCT Extraction Benchmark: Yun et al. 2024

| Merkmal | Befund |
|---|---|
| Publikation | Yun, Pogrebitskiy, Marshall, Wallace (2024), *Automatically Extracting Numerical Results from Randomized Controlled Trials with Large Language Models*, PMLR 252 |
| Paper | https://proceedings.mlr.press/v252/yun24a.html |
| PMC | https://pmc.ncbi.nlm.nih.gov/articles/PMC12448672/ |
| Repository | https://github.com/hyesunyun/llm-meta-analysis |
| Commit | `1bc768d4d098c727c9866eeff909297c38a3e84c` |
| Lizenz | Apache-2.0 für Repository und Annotationen; PMC-Volltexte behalten die PMC-Nutzungsbedingungen |
| Lokaler Bestand | `public_benchmark/raw_data/yun_llm_meta_analysis` |
| Download | vollständig vorhanden; JSON 682.536 Bytes, CSV 157.072 Bytes, SHA-256 in `source_registry.json` |

### Umfang und Struktur

- **699 ICO-Records aus 120 RCTs**, nicht 699 RCT-Berichte.
- Split: 43 Records (10 RCTs) Development, 656 Records (110 RCTs) Test.
- 517 kontinuierliche und 182 binäre Records im Release; das Paper nennt
  516/183. Die Abweichung ist dokumentiert und betrifft die Zählung, nicht
  die einzelnen Werte.
- Ein Record ist ein Intervention-Comparator-Outcome-Tripel. Mehrere
  Outcomes pro Artikel sind zulässig; zusammengesetzte Outcomes wurden
  teilweise aufgeteilt.

### Annotierte Variablen

Enthalten: `pmcid`, `intervention`, `comparator`, `outcome`, `outcome_type`,
`intervention_events`, `intervention_group_size`, `comparator_events`,
`comparator_group_size`, `intervention_mean`,
`intervention_standard_deviation`, `comparator_mean`,
`comparator_standard_deviation`, `notes` sowie Tabellen-/Figuren-Flags.

**Nicht enthalten:** separates Zeitpunktfeld, Evidenzspanne oder
Quellenstelle, strukturierte Begründung, Annotator-IDs, individuelle
(pre-adjudikation) Einzelannotationen.

### Verfügbarkeit und Qualität

- 410 Records sind unter einer strengen Feldregel vollständig; 412 tragen
  `is_data_complete=TRUE`. Die zwei zusätzlichen Records (IDs 635/636) haben
  keine Gruppengrößen.
- Für den C1-Benchmark wurden 275 Records als nutzbar eingefroren:
  239 exakt, 35 über Tabellenzuordnung, 1 quellenbasiert korrigiert.
  57 Records waren strukturell ausgeschlossen, 78 unzureichend belegt.
- Bekannte Fehler: Record 12 (PMC2667135) hatte im Release SD 23,34 statt
  12,34; IDs 635/636 ohne N; Zählabweichung 517/182 gegenüber 516/183.

### Abbildbarkeit auf unser Schema

| Unser Feld | Yun-Feld | Bewertung |
|---|---|---|
| `study_id` | `pmcid` (mit `PMC`-Präfix) | direkt |
| `intervention` / `comparator` / `outcome` | gleichnamig | direkt |
| `intervention_n` / `comparator_n` | `intervention_group_size` / `comparator_group_size` | direkt |
| `intervention_mean` / `comparator_mean` | gleichnamig | direkt |
| `intervention_sd` / `comparator_sd` | `intervention_standard_deviation` / `comparator_standard_deviation` | direkt |
| `intervention_events` / `comparator_events` | gleichnamig | direkt |
| `timepoint` | nicht vorhanden | **nicht abbildbar** |
| `source_quote` | nicht vorhanden | **nicht abbildbar** |

Fehlende Zellen bleiben `null`; sie werden nie als 0 oder als Schätzung
behandelt. Mediane werden nicht in Mittelwerte umgerechnet.

### Eignung

**Sehr hoch für die numerische Extraktion**, aber nur nach Kuratierung. Yun
ist eine konsolidierte Annotation, kein unabhängiger blinder Zweitbewerter;
Inter-Rater-Reliabilität lässt sich daraus nicht berechnen. Zeitpunkt und
Quellenstelle sind mit diesem Datensatz grundsätzlich nicht prüfbar.

## 3. B. Evidence Inference 2.0

| Merkmal | Befund |
|---|---|
| Publikation | DeYoung et al. (2020), *Evidence Inference 2.0: More Data, Better Models*, BioNLP |
| Paper | https://aclanthology.org/2020.bionlp-1.13/ |
| Repository | https://github.com/jayded/evidence-inference |
| Offizielles Archiv | https://evidence-inference.ebm-nlp.com/v2.0.tar.gz |
| Commit | `a661e8c14f973398380c8865cf2f27a535aaaf6d` |
| Lizenz | MIT für Code und Annotationen; Artikeltexte behalten PMC-Bedingungen |
| Lokaler Bestand | `public_benchmark/raw_data/evidence_inference_v2_0` |

### Umfang

- 24.686 Annotationen, 12.865 Prompts, 3.346 annotierte PMCIDs.
- 4.454 Volltextdateien im offiziellen Archiv.
- Labels: `significantly increased`, `significantly decreased`,
  `no significant difference`; 693 Zeilen mit `significantly increase`
  wurden nur für die Zählung normalisiert.
- 924 Annotationen ohne Evidenzspanne; 365 mit `Valid Label=False`,
  226 mit `Valid Reasoning=False`.

### Struktur und Grenzen

Enthalten sind Prompt, Intervention, Comparator, Outcome, Richtungslabel,
Evidenztext und Zeichenspanne. **Nicht enthalten** sind N, Mean, SD,
Ereigniszahlen und ein separates Zeitpunktfeld.

Die `UserID` ist keine dokumentierte Rollenspalte. Der Prozess unterscheidet
Prompt-Generator, Annotator und Verifier; die Zeilen sind daher keine zwei
gleichwertigen blinden Rater. 96,87 % der Prompts mit mehreren Nutzern sind
unanim, aber das ist keine belastbare Inter-Rater-Statistik.

### Eignung

**Hoch für die semantische Prüfung**, insbesondere ob Intervention,
Comparator und Outcome zusammenpassen und ob eine Textstelle die
Richtungsaussage stützt. **Nicht geeignet** für numerische Werte oder
Zeitpunkte. Ein Vergleich unserer `source_note` mit den Evidenzspannen ist
nur nach manueller Zuordnung möglich, weil unsere Ausgabe Freitext und keine
Zeichenoffsets liefert.

## 4. C. PICO-Corpus

| Merkmal | Befund |
|---|---|
| Repository | https://github.com/sociocom/PICO-Corpus |
| Umfang | ca. 1.011 PubMed-Abstracts von Brustkrebs-RCTs |
| Annotation | BRAT-Dateien für Participants, Intervention, Control, Outcome |
| Lizenz | **keine LICENSE-Datei im Repository**; damit ist keine ausdrückliche Nutzungserlaubnis dokumentiert |

Die Annotationen sind auf Abstract-Ebene und teils hierarchisch; Intervention
und Kontrolle sind nicht immer getrennt. Es gibt keine numerischen Armwerte
und keine Zeitpunkte. Wegen des Brustkrebs-Fokus und der fehlenden Lizenz
ist der Corpus für unseren dCBT-I-Kontext **niedrig priorisiert** und wird
nicht als Referenz verwendet.

## 5. D. SRDR+ (AHRQ Systematic Review Data Repository)

| Merkmal | Befund |
|---|---|
| Portal | https://srdr.ahrq.gov/projects/published |
| Träger | Agency for Healthcare Research and Quality |
| Lizenz | öffentlich zugänglich unter Creative-Commons-Bedingungen (SRDR-Open-Access-Policy); pro Projekt prüfen |
| Export | Projekt- und Extraktionstabellen können exportiert werden; API/Download projektabhängig |

Geprüft wurde, ob ein abgeschlossenes Review zu Insomnie, Schlaf oder
dCBT-I mit vollständigen Extraktionstabellen vorliegt. Die Recherche hat
**kein konkretes öffentliches SRDR-Projekt mit belastbarer dCBT-I-Tabelle
nachgewiesen**. Auffindbar ist die AHRQ-Übersicht *Management of Insomnia
Disorder in Adults* (2015, 169 RCTs), aber ohne Nachweis, dass deren
Extraktionsdaten als SRDR-Projekt exportierbar sind.

SRDR-Daten wären auch im Erfolgsfall nicht automatisch Goldstandard: Die
Provenienz, die Version und die Unabhängigkeit der Extraktion müssten pro
Projekt geprüft werden. SRDR+ bleibt eine **sekundäre Option** für eine
spätere, manuell zu prüfende Studie.

## 6. Zusätzlicher Ansatz: externe Reviews zu unseren eigenen Studien

Geprüft wurden publizierte dCBT-I-Reviews:

- **Hwang et al. 2025**, *Systematic review and meta-analysis on fully
  automated digital cognitive behavioral therapy for insomnia*, npj Digital
  Medicine 8:157, 29 RCTs mit 9.475 Teilnehmenden.
  https://www.nature.com/articles/s41746-025-01514-4
- **Lee et al. 2023**, *Digital cognitive behavioral therapy for insomnia on
  depression and anxiety*, npj Digital Medicine 6 (2023).
  https://www.nature.com/articles/s41746-023-00800-3

Beide Reviews berichten aggregierte Effekte, keine maschinenlesbaren
studienweisen Extraktionstabellen im Artikel. Ein Abgleich mit unseren 30
Volltexten würde die Identifikation der eingeschlossenen Studien aus
Supplement beziehungsweise Referenzliste erfordern. Dieser Abgleich ist
**noch nicht durchgeführt** und wird hier nicht als Ergebnis behauptet.

Der Ansatz bleibt trotzdem der vielversprechendste für die klinische
Plausibilisierung, weil Population, Intervention, Comparator und Zeitpunkt
tatsächlich übereinstimmen könnten. Er ist ein manueller Kuratierungsschritt,
kein automatisierbarer Benchmark.

## 7. Empfehlung

1. **Yun et al. 2024 als primäre numerische Referenz verwenden.** Nur die
   275 kuratierten Records, nicht die rohen 699. Zeitpunkt und Quellenstelle
   bleiben nicht prüfbar und müssen so ausgewiesen werden.
2. **Evidence Inference 2.0 komplementär** für die semantische ICO-Prüfung
   einsetzen, sobald unsere Ausgabe Evidenzspans oder eindeutige Zitate
   liefert. Nicht für numerische Metriken verwenden.
3. **PICO-Corpus nicht verwenden** (Thema, fehlende Lizenz, keine Armwerte).
4. **SRDR+ zurückstellen**, bis ein konkretes Insomnie-Projekt mit
   exportierbarer Tabelle identifiziert und lizenzrechtlich geprüft ist.
5. **Externe dCBT-I-Reviews manuell abgleichen**, sobald die 30 Studien
   anhand ihrer PMCIDs/DOIs gegen die Supplementary-Liste von Hwang 2025
   geprüft sind. Das ist der einzige Weg, auch Zeitpunkt und klinische
   Plausibilität unabhängig zu stützen.

## 8. Benchmark-Ergebnis (Kurzfassung)

Vollständig in `external_benchmark_results_v1.md`, maschinenlesbar in
`external_benchmark_results_v1.json`, Einzelfälle in
`external_benchmark_errors_v1.csv`.

- 275 Referenzrecords, davon 249 mit eingefrorener C1-Testausgabe;
  26 Dev-Records waren nicht Teil des Testlaufs.
- 1.308 erwartete numerische Felder; 993 exakt (75,9 %), 1.005 mit
  Rundung/Skalierung akzeptabel (76,8 %), 163 abweichend, 140 fehlend,
  0 Referenzlücken, 0 Schemafehler, 0 vermutete Armvertauschungen.
- Abdeckung 89,3 %, MAE gepaart 1,52.
- 149 Records vollständig exakt, 151 vollständig akzeptabel.
- Kategorien: **151 automatisch bestätigt**, **98 automatisch
  widersprüchlich**, **26 nicht extern validierbar** (Dev-Records ohne
  Ausgabe in diesem Lauf).
- Kontinuierlich 841/1.122 exakt (75,0 %), binär 567/684 (82,9 %).

**Abgleich mit der bestehenden Auswertung:** Diese nennt 992/1.308 exakt und
176 falsch. Die Differenz erklärt sich vollständig aus (a) dem einen
quellenbasiert korrigierten Record 12 (23,34 → 12,34) und (b) 12 Feldern,
die hier als Rundung beziehungsweise konsistente Skalierung eingeordnet
sind. Es wurden keine Werte verändert.

**A/B:** Es liegt keine separate B-Ausgabe vor. Die vorhandene C1-Ausgabe
ist ein Pipeline-Lauf, keine unabhängige menschliche Zweitannotation. Ein
A/B-Vergleich wurde daher **nicht** durchgeführt.

## 9. Entscheidungsfrage

**Wie viel manuelle Prüfung ersetzt das?**

- **Numerische Werte:** Für 151 von 249 laufbezogenen Records (60,6 %)
  bestätigt Yun die Zahlen vollständig; für 98 Records liefert der Benchmark
  eine konkrete Arbeitsliste. Die numerische Sichtprüfung dieser 151 kann
  entfallen, sofern man die Referenzfehler akzeptiert.
- **Zeitpunkt, Quellenstelle, Population, Outcome-Text:** **0 Records** sind
  dafür automatisch bestätigt. Yun hat diese Felder nicht. Hier bleibt eine
  menschliche Prüfung nötig, zumindest als Stichprobe.
- **Studien-/Arm-/Outcome-Erkennung:** nicht geprüft, weil der Lauf die ICO-
  Vorgabe erhielt. Dafür wäre ein anderer Benchmark nötig.
- **Klinisch-wissenschaftliche Freigabe:** nicht ersetzbar. Auch Kategorie 1
  ist nur eine numerische Bestätigung gegen eine selbst fehleranfällige
  Referenz. Die fachliche Entscheidung über Eignung, Zeitpunkt und
  Studieneinschluss bleibt bei einer qualifizierten Person.

Kurz: **Die numerische Prüflast sinkt deutlich, die klinisch-methodische
Freigabe bleibt vollständig menschlich.** Der nächste sinnvolle Schritt ist
der manuelle Abgleich unserer 30 Studien mit den Supplementary-Listen der
dCBT-I-Reviews; er adressiert genau die Dimensionen, die Yun nicht abdeckt.
