# Dedup-Register: 83 Zugangsliste gegen die drei eingeschlossenen Studien

Stand: 2026-11-08. Zweck: Vor der Auswertung der Fernleihe-Lieferung
verhindern, dass eine Doppelpublikation als zusätzliche Studie gezählt wird.
Eine Studie bleibt eine Zeile, auch wenn sie in zwei Zeitschriften erscheint.

## Die drei eingeschlossenen Studien

| Kürzel | PMC | PMID | DOI | Register | Population | Dauer |
|---|---|---|---|---|---|---|
| S1 MENDS | PMC3489506 | 23129488 | 10.1136/bmj.e6664 | ISRCTN05534585 | Kinder mit Entwicklungsstörung | 12 Wochen |
| S2 Sechsmonatsstudie | PMC2933606 | 20712869 | 10.1186/1741-7015-8-51 | NCT00397189 | Erwachsene, primäre Insomnie (65–80: N 137/144; Low excretors: N 86/86) | 6 Monate |
| S3 Dosisfindung | PMC2952772 | 20668840 | 10.1007/s00213-010-1962-0 | ISRCTN20033346 | Kinder 6–12, chronische SOL-Insomnie, n = 72 | 1 Woche |

## Kategorie A - sichere Doppelpublikation

| PMID | Journal | Jahr | gegen | Beleg |
|---|---|---|---|---|
| 23098680 | Health Technology Assessment 16(40) | 2012 | **S1 MENDS** | HTA-Bericht der MENDS-Studie; SOL Tagebuch −37,49 min (95 %-CI −55,27 bis −19,71) und Aktigraphie −45,34 (−68,75 bis −21,93) sind **zeichengenau identisch** mit PMC3489506. Titel nennt „MENDS". |

**Behandlung:** 23098680 wird nicht als eigene Studie geführt. Beim Eintreffen
der Lieferung: nicht extrahieren, als Duplikat von S1 vermerken. Falls der
HTA-Bericht zusätzliche Angaben enthält (z. B. eine andere Tabelle mit
Streuungen), dürfen daraus Werte für **S1** ergänzt werden - aber k bleibt 1
für diese Studie.

## Kategorie B - Verdacht, bei Lieferung prüfen

| PMID | Titel | Verdacht | Prüfmerkmal |
|---|---|---|---|
| 21091391 | Prolonged release melatonin in the treatment of primary insomnia: evaluation of the age cut-off | Sekundäranalyse von **S2** (gleiche Population, Altersgrenze) | NCT00397189? n = 480/281? Autorengruppe Wade? |
| 16919138 | Randomized controlled trial of melatonin for children with autistic spectrum disorders and sleep | gleiche Population wie **S1** (ASD als Teilmenge der Entwicklungsstörungen) | ISRCTN05534585? n = 146? Rekrutierungszeitraum 2005–2009? |

Beide sind **nicht** in den Referenzlisten der drei Studien enthalten (anders
als die Fälle in Kategorie C) - ein Ausschluss ist damit nicht belegt. Die
Entscheidung braucht den Volltext: Register-ID, Stichproben-n, Zentren und
Autorengruppe vergleichen.

## Kategorie C - geprüft, keine Doppelpublikation

| PMID | Titel (Anfang) | Grund |
|---|---|---|
| 17875243 | Efficacy of prolonged release melatonin in insomnia patients aged 55-80 years | wird von **S2** zitiert (Referenzliste) → externe Arbeit |
| 19584739 | The effect of prolonged-release melatonin on sleep measures … elderly | wird von **S2** zitiert → externe Arbeit |
| 15910516 | Prediction of melatonin efficacy by pretreatment dim light melatonin onset … | wird von **S3** zitiert → externe Arbeit |
| 11292231 | Melatonin for chronic sleep onset insomnia in children (Smits 2001) | wird von **S3** zitiert → externe Arbeit |
| 14566165 | Melatonin improves health status and sleep in children … (Smits 2003) | wird von **S3** zitiert → externe Arbeit |
| 18078449 | … controlled release melatonin treatment of delayed sleep phase … | wird von **S3** zitiert → externe Arbeit |
| 28364493 | Effects of Melatonin and Bright Light Treatment … | andere Intervention (Licht + Melatonin), andere Rekrutierung |

## Verdacht innerhalb der 83 (nicht gegen die drei)

Diese Paare könnten dieselbe Kohorte in zwei Publikationen sein. Sie sind
**nicht** gegen die drei Studien gerichtet, sondern untereinander - beim
Eintreffen der Lieferung zuerst gegenprüfen:

| Gruppe | PMIDs | Verdacht |
|---|---|---|
| Wade | 17875243, 19584739, 21091391 | gleiche Autorengruppe, überlappende Altersgruppen (55–80, elderly, age cut-off) |
| Smits | 11292231, 14566165 | gleiche Autorengruppe, Kinder mit chronischer SOL-Insomnie, 2001/2003 |

Wenn zwei davon dieselbe Randomisierung berichten (gleiches n, gleiche
Zentren, gleicher Rekrutierungszeitraum), zählt nur eine Zeile.

## Prüfregel für die Lieferung

1. **Register-ID zuerst.** ISRCTN05534585, NCT00397189, ISRCTN20033346 gegen
   die Angaben im Volltext prüfen. Gleiche ID → Doppel, keine neue Zeile.
2. **Dann Stichprobe.** n randomisiert, Zentren, Rekrutierungszeitraum,
   Altersbereich. Drei von vier identisch → Verdacht, Autoren anschreiben
   oder als Doppel führen.
3. **Titel allein reicht nicht.** Der MENDS-Fall zeigt: Der HTA-Bericht hat
   einen anderen Titel als der BMJ-Artikel und wäre über Titelähnlichkeit
   (Jaccard 0,33) nur als „Kandidat" aufgefallen. Die Identität kam über die
   identischen Effekte.
4. **Nie zwei Zeilen derselben Studie poolen.** Auch nicht, wenn eine Zeile
   adjustiert und eine unadjustiert ist.

## Woher die Zuordnung kommt

- PMID/DOI der drei aus den XML-Metadaten (`<article-id>`).
- Referenzlisten der drei XML: `<ref>` mit `<pub-id pub-id-type="pmid">`.
- Titelähnlichkeit: Jaccard über Inhaltswörter, Stoppwörter entfernt.
- Der MENDS-Beleg: Vergleich der SOL-Werte aus `volltext/23098680.txt` mit
  `pooling_sol3_20261108.md`.

Keine Netzabfrage für dieses Register; alle Angaben stammen aus den lokalen
XML und der Zugangsliste.
