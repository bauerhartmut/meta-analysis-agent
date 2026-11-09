# Fernleihe: was bestellt wird, warum, und was danach passiert

Stand: 2026-11-09. Erklärt das Vorhaben hinter
`fernleihliste_20261109.md`. Das Dokument bestellt nichts — es begründet die
Liste und die Reihenfolge.

## 1. Abgrenzung

Niemand in diesem Projekt hat ein Bibliothekskonto, und es gibt keinen Auftrag,
der über eine Bestellliste hinausgeht. Geliefert wird eine druckfertige Liste;
abgesendet wird sie dort, wo das Fernleihkonto liegt. Es gibt in diesem
Dokument keine Kontonummer, keine Kostenstelle und keine Lieferadresse.

## 2. Warum Fernleihe und nicht Download

Die 83 Dokumente der Zugangsliste sind nicht die, die man beim Recherchieren
übersieht. Es sind die, für die PubMed Central **keinen** Volltext hat —
`fetch_log.json` führt für alle 83 den Status „kein PMC".

Geprüft wurde das dreifach, ohne Volltext:

| Quelle | Ergebnis |
|---|---|
| Europe PMC, 83 DOIs | 77 kein OA-PDF, 2 × HTTP 403, 3 ohne DOI, 1 unlesbar, **0 geholt** |
| OpenAlex, 83 DOIs | 65 kein OA-PDF, 14 Download-/Lesefehler, **1 geholt** |
| lokal (Texte, XML, PDFs) | 1127 Texte, 1136 XML, 36 PDFs — **0 Treffer** |

Der eine Treffer (Nunes 2008) berichtet Einschaflatenz nur als PSQI-Komponente,
nicht als Minuten-Mittelwert mit Streuung, und ist damit nicht poolbar.

Bleibt der Weg über eine Bibliothek, die eine Kopie aus einer anderen
Bibliothek beschafft. Das ist der einzige Zugang, der noch nicht ausgeschöpft
ist.

## 3. Was bestellt wird

**20 Titel**, nicht 25:

- **5 A-Titel** — Melatonin, RCT-Signal, Einschaflatenz im Titel.
- **15 B-Titel** — Melatonin, RCT-Signal, Endpunkt offen.

Von den 20 B-Dokumenten sind fünf gestrichen, weil sie keine poolbare Zeile
liefern können:

| PMID | Grund |
|---|---|
| 40791136 | Walnuss-Intervention, kein Melatonin |
| 34293628 | Melatonin gegen Triclofos, kein Placebo |
| 29619605 | Melatonin gegen Meloxicam, kein Placebo |
| 23098680 | HTA-Bericht, Doppelpublikation von S1, liegt lokal vor |
| 9737496 | Notärzte nach Nachtschicht, kein SOL-Endpunkt berichtet |

Fünf bezahlte Fehlversuche weniger. Die vollständige Liste mit Autor, Quelle,
DOI und PMID steht in `fernleihliste_20261109.md` und
`fernleihliste_20261109.txt`.

Zwei Hinweise für das Formular: Die **DOI** ist das verlässlichste Feld, weil
sie unabhängig von abweichender Bandzählung auflöst. Und bestellt wird **PDF
mit Textebene** — ein Scan ohne Textebene ist für die Auswertung wertlos, weil
die Zahlen sonst abgetippt werden müssten.

## 4. Was nach der Lieferung passiert

Die Reihenfolge ist vorab festgelegt (`extraktionsformular_20261109.md`):

1. **Dedup zuerst.** 23098680 und 21091391 haben gezeigt, dass die Liste
   Doppelpublikationen enthält. Register-ID, n, Zentren und
   Rekrutierungszeitraum gegen S1–S3 prüfen, bevor eine Zahl eingetragen wird.
2. **Register-ID** aus dem Volltext, mit Fundstelle und Abgleich gegen den dort
   genannten Endpunkt.
3. **Design und Streuung.** Sieben der 20 sind Crossover. Dort entscheidet die
   gepaarte Streuung über das Gewicht der Studie: Bei r = 0,5 ist die
   ungepaarte SE um Faktor 2,24 größer als die gepaarte.
4. **Erst dann Zahlen**, jede mit Fundstelle und Zitat, dann Pooling.

Das Prüfskript (`scripts/pruefe_extraktion_20261109.py --check`) erzwingt die
Blöcke und bricht bei fehlender Register-ID, fehlendem Crossover-Pfad oder
einer Doppelpublikation ohne Ausschlussstatus ab.

## 5. Was es realistisch bringt

Theoretisch k von 3 auf bis zu 10. Realistisch deutlich weniger: Die
Abstract-Triage fand sieben Titel mit Zahlen im Abstract, sieben ohne, einen
mit bloßer Subskala. Bei Crossover-Studien fehlt zudem oft die gepaarte
Streuung. Erwartbar sind ein bis vier zusätzliche poolbare Zeilen.

Diese Zeilen stammen aus anderen Populationen: Zerebralparese, Parkinson,
Autismusspektrum, Rett-Syndrom, atopische Dermatitis, postoperative
Erwachsene. Für die Frage „senkt Melatonin die Einschaflatenz bei primärer
Insomnie" ist das eine Stratifizierung, kein größeres k. Der Aufwand kann also
auch ergeben, dass die Heterogenität steigt statt der Präzision.

Ausgangslage, gegen die gemessen wird: −26,29 min (95 %-CI −55,57 bis 3,00),
p = 0,061, k = 3, τ² = 104,5, I² = 63 %.

## 6. Kosten und Risiken

Die Gebühr pro Bestellung hängt an Bibliothek und Kontingent und ist im Projekt
nicht bekannt; sie wird hier nicht geschätzt. Die übrigen Risiken sind
überschaubar: Lieferzeit, einzelne Fehlschläge (bei Europe PMC waren es zwei
403er), und die Möglichkeit, dass ein Volltext die Zahlen nicht berichtet.

Deshalb: **A zuerst.** Fünf Bestellungen zeigen, ob der Weg trägt, bevor 15
weitere folgen.

## 7. Quellen im Projekt

| Datei | Inhalt |
|---|---|
| `fernleihliste_20261109.md` / `.txt` | die 20 Positionen, druckfertig |
| `zugangsliste_20261108.csv` | 83 Dokumente mit Priorität A/B/C/D |
| `triage_b_20261108.md` | Klassen der 20 B-Dokumente, fünf gestrichen |
| `volltext_beschaffung_20261108.md` | warum kein Dokument lokal oder per OA erreichbar ist |
| `dedup_register_20261108.md` | die aufgelösten Doppelpublikationen |
| `extraktionsformular_20261109.md` | Dedup, Register, Crossover-Pfad |
| `scripts/erstelle_fernleihliste.py` | erzeugt die Liste aus den Metadaten |
| `scripts/pruefe_extraktion_20261109.py` | prüft die Extraktion nach der Lieferung |
