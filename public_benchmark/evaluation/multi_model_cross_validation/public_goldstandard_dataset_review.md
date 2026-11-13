# Prüfung öffentlich verfügbarer Goldstandard-Datensätze

Stand: 2026-11-13
Maschinenlesbar: [`public_goldstandard_dataset_review.json`](public_goldstandard_dataset_review.json)
Überschneidungen: [`dataset_overlap_report.json`](dataset_overlap_report.json)
Skripte: `public_benchmark/scripts/goldstandard/`

## Entscheidung vorweg

**Nein, die Cross-Validation lässt sich nicht vollständig ohne neue menschliche
Annotation durchführen.** Kein öffentlich verfügbarer Datensatz liefert die
Provenienzfelder aus `schema_v1.json` (`page`, `table_or_section`,
`source_cell_or_location`, `source_context`, `timepoint_id`) zusammen mit
numerischen Armwerten.

**Ja für eine vorgeschaltete externe Validierung.** Zwei Datensätze enthalten
menschlich geprüfte Armwerte, die sich ohne neue Annotation auswerten lassen:
die European-Urology-Teilmenge (104 Records aus 20 Trials) und GLASS (81
Records aus 45 Publikationen). Beide sind disjunkt zu Yun, G5 und unserer
Auswahl.

## Vorgehen

1. Yun als Referenz für Schema, Umfang und Qualität gelesen (lokal vorhanden,
   nicht erneut als Testdatensatz verwendet).
2. European-Urology-Publikation geprüft, Supplemente und
   Datenverfügbarkeitsangabe verfolgt, OSF-Projekt `8fzps` heruntergeladen und
   die Arbeitsmappen zeilenweise ausgewertet.
3. Weitere Kandidaten recherchiert: EvidenceOutcomes, EBM-NLP, PICO-Corpus,
   GLASS/TrialReviewBench, Kataoka et al., „What level of automation“, SRDR+.
4. Jeden Datensatz gegen die elf Kriterien geprüft und eingestuft.
5. Für die zwei brauchbaren Datensätze Adapter gebaut, Originale archiviert,
   Hashes erzeugt, Mapping auf `schema_v1` dokumentiert.
6. Überschneidungen automatisch geprüft (DOI, PMCID, PMID).

## European-Urology-Datensatz: der wichtigste Befund

Der Artikel nennt 105 Trials (41 binär, 64 kontinuierlich). Die unter
<https://osf.io/8fzps/> veröffentlichten vier Arbeitsmappen enthalten **nicht**
diese 105 Trials, sondern nur die Trials, die in die gepoolten Analysen
eingegangen sind:

| Kennzahl | Wert |
|---|---:|
| Arbeitsmappen | 4 (Prompt 1/2 × ChatGPT/Claude) |
| Gold-Records nach Bereinigung | 104 |
| davon binär | 41 |
| davon kontinuierlich | 63 |
| verschiedene Trials | 20 |
| verschiedene Trial-DOIs | 18 |
| Outcomes | 9 binär, 12 kontinuierlich |
| Zeilen ohne jeden Goldwert (entfernt) | 36 |
| gepoolte Zeilen ohne Armwerte (entfernt) | 4 |
| Records mit einzelnen fehlenden Zellen | 22 |

Die Gold-Spalten (`R1_rct`, `N1_rct`, `R2_rct`, `N2_rct`, `Mean1_RCT`,
`SD1_RCT`, `N1_RCT`, `Mean2_RCT`, `SD2_RCT`, `N2_RCT`) sind in allen vier
Arbeitsmappen **identisch**; nur die Trial- und Outcome-Schreibweisen
variieren. Die `*_AI`-Spalten sind Modellausgaben und wurden nicht übernommen,
ebenso die Spalte mit den zusammengefassten „overall mortality“-Zeilen (fünf
Trials in einem Feld).

Was fehlt: Seitenzahl, Tabellen- oder Abschnittsangabe, Zellposition,
Textschnipsel, Zeitpunkt. Was vorhanden ist: Armbezeichnungen (Intervention,
Kontrolle), Gruppengrößen, Ereigniszahlen, Mittelwerte, Standardabweichungen,
Trial-DOI, Review-DOI, Outcome-Bezeichnung.

Rechtlich: Das OSF-Projekt führt **keine Lizenz**. Eine Nutzung für
Forschung ist üblich, aber nicht ausdrücklich erlaubt; das ist im
Methodenteil zu benennen.

Eine Anfrage an die Autoren ist sinnvoll und zwar gezielt: nach den
vollständigen 105-Trial-Tabellen **mit** Belegstelle. Ohne diese Angabe bleibt
der Datensatz für unsere Provenienzfrage unzureichend.

## Weitere Datensätze

| Datensatz | Umfang | Zahlen | Einstufung |
|---|---|---|---|
| Yun 2024 | 120 RCTs, 699 Records (lokal 70 Artikel, 550 Records) | ja, Armwerte | `usable_with_limitations` (bereits verwendet) |
| European Urology (OSF) | 20 Trials, 104 Records | ja, Armwerte | `usable_with_limitations` |
| PICO-Corpus | 1011 Abstrakts, 5024 Zahl-Spans | ja, ohne Outcome-Bezug | `usable_with_limitations` |
| GLASS TrialReviewBench | 45 Publikationen, 81 Records | ja, heterogene Felder | `usable_with_limitations` |
| EvidenceOutcomes | 640 Abstrakts | nein, nur Outcome-Spans | `unsuitable` |
| EBM-NLP | 4993 Abstrakts | nein, nur PICO-Spans | `unsuitable` |
| Kataoka et al. 2026 | 290 RCTs beansprucht | Daten nicht im Repo | `unsuitable` |
| „What level of automation“ | 58 RCTs | nur auf Anfrage | `unsuitable` |
| SRDR+ | 225 Reviews, ~20.000 Studien | nicht mehr erreichbar | `unsuitable` |

### PICO-Corpus

1011 BRAT-annotierte Abstrakts, 5024 numerische Annotationen mit Armbezug:
`iv-bin-abs` 556, `cv-bin-abs` 465, `iv-bin-percent` 1376, `cv-bin-percent`
1148, `iv-cont-mean` 366, `cv-cont-mean` 327, `iv-cont-sd` 129, `cv-cont-sd`
124, dazu Median und Quartile. 217 Zahlen stehen als Wort („Seven“) und wurden
nicht in eine Zahl umgedeutet.

Grenze: **keine Relationen** zwischen Zahl und Outcome. Der Korpus belegt,
dass eine Zahl im Abstrakt steht und zu welchem Arm sie gehört, nicht zu
welchem Outcome. Zeitpunkte fehlen, Volltexte fehlen, eine Lizenzdatei fehlt.

### GLASS / TrialReviewBench study results

81 Ergebniszeilen aus 45 Publikationen, 19 Outcomes. Felder sind heterogen:
`Events`/`Total`/`n` (binär), `HR`, `sample`, `Study`, teils
studienbezogene Spalten wie `n_MWA`. Jede Zeile nennt die Quell-Arbeitsmappe
und die PMIDs; die Volltexte werden **nicht** mitgeliefert. Lizenz: Labels
MIT, Artikelrechte bei den Verlagen, Teile des Gesamtpakets NonCommercial.

### Kataoka et al. 2026

Der Artikel verweist für die Daten auf
<https://github.com/Tomo-for-lab/automating-DE>. Das Repository enthält 20
Dateien, ausschließlich Notebooks, `requirement.txt`, README und
`.gitignore` — keine Referenzdaten, keine PDFs, keine Extraktionstabelle. Die
Datenverfügbarkeitsangabe deckt sich nicht mit dem Repository-Inhalt. Ohne
Anfrage nicht nutzbar.

### SRDR+

Das AHRQ-Repositorium ist geschlossen: `srdrplus.ahrq.gov` leitet auf eine
Abschiedsseite um (HTTP 301/202 am 13.11.2026). Die früher öffentlichen 225
Reviews mit rund 20.000 Studien sind nicht mehr abrufbar.

## Überschneidungen

Geprüft über DOI-Zeichenketten und, wo möglich, über aufgelöste PMCIDs und
PMIDs (Europe PMC).

| Datensatz | Überschneidung mit Yun | mit G5 | mit Cross-Validation v1 |
|---|---|---|---|
| European Urology | keine | keine | keine |
| PICO-Corpus (718 PMIDs) | keine | keine | keine |
| GLASS (45 PMIDs) | keine | keine | keine |

Einschränkung: Nur 4 der 17 European-Urology-DOIs ließen sich über Europe PMC
auflösen; für die übrigen 13 stützt sich die Aussage allein auf den
DOI-Vergleich. Die Urology-Trials sind älter (2008–2022), unsere Auswahl
stammt aus 2024–2025, deshalb ist eine Überschneidung auch inhaltlich
unwahrscheinlich, aber nicht für jeden einzelnen Trial belegt.

## Integration

Archive und Adapter:

- `goldstandard_datasets/eururology_v1/original/` — die vier Arbeitsmappen
  unverändert, SHA-256 im Manifest.
- `goldstandard_datasets/eururology_v1/records.jsonl` — 104 Records, je Record
  Arme, Werte, DOI, Outcome, Provenienzfeld (Arbeitsmappe, ohne Zelle).
- `goldstandard_datasets/pico_corpus_v1/records.jsonl` — 5024 Records, je
  Record Arm, Statistiktyp, Wert, Zeichenoffsets; `outcome_id` bleibt leer.
- `manifest.json` je Datensatz mit Hashes, Zählungen und Lizenzhinweis.

Mapping auf `schema_v1.json`:

| schema_v1-Feld | European Urology | PICO-Corpus |
|---|---|---|
| `value` | vorhanden | vorhanden, außer 217 Wortzahlen |
| `unit` | implizit (Anzahl, Punkte) | aus Label (`bin-abs`, `cont-mean`, …) |
| `source_document` | Arbeitsmappe + DOI | `.ann`-Datei |
| `page` | fehlt | fehlt (Abstrakt) |
| `table_or_section` | „sheet“ | „abstract“ |
| `source_context` | fehlt | Textschnipsel vorhanden |
| `source_cell_or_location` | fehlt | Zeichenoffsets |
| `arm_id` | vorhanden | vorhanden |
| `outcome_id` | vorhanden | fehlt |
| `timepoint_id` | fehlt | fehlt |
| `assignment_confidence` | hoch (verifiziert) | mittel |
| `verification_status` | `verbatim` | `verbatim` |
| `uncertainty_note` | fehlende Zellen markiert | Wortzahlen markiert |

Es wurde nichts ergänzt: fehlende Felder sind `null`, fehlende Zellen stehen
in `missing_gold_fields`.

## Was genau fehlt

Für eine vollständige Cross-Validation nach `schema_v1` fehlen in **allen**
öffentlichen Datensätzen:

1. Seitenzahl und Tabellen-/Abschnittsangabe (Belegstelle),
2. Zellposition oder Textausschnitt als Nachweis,
3. Zeitpunkt des Outcomes,
4. eine Lizenz, die die Weitergabe der abgeleiteten Annotationen erlaubt.

Für die European-Urology-Daten zusätzlich: die im Artikel genannten 105 Trials
statt der veröffentlichten 20, und eine Bestätigung der unabhängigen
Zweitprüfung je Zahl.

## Vorgeschlagenes Design, falls vorhandene Daten genutzt werden

**Stufe 1 — externe Validierung ohne neue Annotation (sofort machbar):**

- Datenbasis: European Urology (104 Records, 20 Trials) + GLASS (81 Records,
  45 Publikationen) = 185 Records, geclustert nach Trial.
- Aufgabe: Armwerte extrahieren (Ereignisse, Gruppengrößen, Mittelwert, SD)
  und dem richtigen Arm zuordnen.
- Metriken: exakte Übereinstimmung je Zelle, Record-Genauigkeit, Vertauschung
  von Armen, Anteil fehlender Werte.
- Power: 185 Records liegen oberhalb der 100er-Zeile der bestehenden
  Rechnung; die kleinste nachweisbare Differenz wäre kleiner als 6,5
  Prozentpunkte (ICC 0,1). Ein exakter Wert für 185 wurde nicht neu gerechnet.
- Grenze: keine Provenienzbewertung, keine Zeitpunkte, kein Volltextbezug.

**Stufe 2 — Referenzannotation der 25 Artikel (bleibt nötig):**

Nur sie liefert die fünf Provenienzfelder und die Zeitpunkte. Sie bleibt der
Kern des geplanten Designs; Stufe 1 ersetzt sie nicht, sondern liefert eine
vorherige, unabhängige Plausibilitätsprüfung der Modelle.

## Grenzen dieses Berichts

- Die Prüfung der European-Urology-Daten stützt sich auf die vier
  OSF-Arbeitsmappen; die Supplemente der beiden Original-Reviews wurden nicht
  ausgewertet. Dort können weitere Tabellen liegen.
- Ob die 20 veröffentlichten Trials die einzigen mit extrahierbaren Werten
  sind oder eine Auswahl darstellen, lässt sich aus den Dateien nicht
  entscheiden.
- Die Kriterien „unabhängige Prüfung“ und „Lizenz“ sind aus Publikation und
  Repository abgeleitet, nicht rechtlich geprüft.
- Keine Modellläufe, keine neuen Referenzwerte, keine Änderung an Yun.
