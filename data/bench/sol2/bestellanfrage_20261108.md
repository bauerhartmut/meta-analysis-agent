# Bestellanfrage an die Bibliothek

Stand: 2026-11-08. Fertig zum Kopieren; Platzhalter in
eckigen Klammern ausfuellen. Quelle der Angaben: PubMed-Metadaten
(`data/bench/sol2/zitationen_a.json`), keine Volltexte abgerufen.

```text
Betreff: Literaturbestellung - 5 Artikel zu Melatonin und Einschaflatenz (DOI/PMID angegeben)

Sehr geehrte Damen und Herren,

fuer ein Forschungsprojekt zu Melatonin und der Einschaflatenz benoetige ich
fuenf Artikel, die ueber unseren Zugang nicht als Volltext erreichbar sind.
Die bibliografischen Angaben stehen unten; alle Titel sind ueber die DOI
eindeutig aufloesbar.

[1] Chandler-Mather N, Shelton D, Donovan C, Till H, Theroux BM, Dawe S. A Pilot Randomised Controlled Trial of Sublingual Melatonin for Sleep Onset Insomnia in Children With Foetal Alcohol Spectrum Disorder (FASD). J Paediatr Child Health. 2026;62(1):16-22. doi:10.1111/jpc.70224 (PMID: 41122831)
[2] Xu H, Zhang C, Qian Y, Zou J, Li X, Liu Y et al. Efficacy of melatonin for sleep disturbance in middle-aged primary insomnia: a double-blind, randomised clinical trial. Sleep Med. 2021;76:113-119. doi:10.1016/j.sleep.2020.10.018 (PMID: 33157425)
[3] van Maanen A, Meijer AM, Smits MG, van der Heijden KB, Oort FJ. Effects of Melatonin and Bright Light Treatment in Childhood Chronic Sleep Onset Insomnia With Late Melatonin Onset: A Randomized Controlled Study. Sleep. 2017;40(2). doi:10.1093/sleep/zsw038 (PMID: 28364493)
[4] Smits MG, van Stel HF, van der Heijden K, Meijer AM, Coenen AM, Kerkhof GA. Melatonin improves health status and sleep in children with idiopathic chronic sleep-onset insomnia: a randomized placebo-controlled trial. J Am Acad Child Adolesc Psychiatry. 2003;42(11):1286-93. doi:10.1097/01.chi.0000085756.71002.86 (PMID: 14566165)
[5] Smits MG, Nagtegaal EE, van der Heijden J, Coenen AM, Kerkhof GA. Melatonin for chronic sleep onset insomnia in children: a randomized placebo-controlled trial. J Child Neurol. 2001;16(2):86-92. doi:10.1177/088307380101600204 (PMID: 11292231)

Falls einzelne Titel nur ueber Fernleihe oder Dokumentlieferung zugaenglich
sind, bitte ich um diesen Weg. Bitte stellen Sie die Volltexte, wenn moeglich,
als durchsuchbares PDF mit Textebene bereit; ein reiner Scan ohne Textebene ist
fuer die Auswertung nicht verwendbar. Die anfallenden Gebuehren uebernehmen wir
bis zur Hoehe von [Betrag eintragen]; Kostenstelle: [Kostenstelle eintragen].

Fuer Rueckfragen erreichen Sie mich unter [Telefon] oder [E-Mail].

Vielen Dank und freundliche Gruesse
[Name]
[Einrichtung / Arbeitsgruppe]
```

## Warum genau diese fuenf

Es sind die einzigen Treffer des Q2-Abzugs ohne PMC-Volltext, deren Titel
gleichzeitig Melatonin, ein RCT-Signal und Einschaflatenz oder Insomnie
nennt. Alle anderen 78 Dokumente ohne Volltext stehen in
`zugangsliste_20261108.csv` unter B bis D.

## Wenn die Bibliothek nachfragt

- Die DOIs loesen alle auf; PMIDs sind als Rueckfall angegeben.
- Es handelt sich um Zeitschriftenartikel, keine Buchkapitel oder
  Konferenzbeitraege.
- Benoetigt werden die Volltexte als PDF mit Textebene (born digital oder
  OCR-durchsuchbar); eine Weitergabe an Dritte ist nicht vorgesehen.
- Bei einem Scan ohne Textebene bitte ich um den Hinweis, damit ich keine
  Zeilen als "nicht berichtet" fehlverbuchen muss.

## Nach Erhalt

Die PDFs in `data/bench/sol2/volltext/` ablegen, dann die PDF-Kette
(`scripts/read_pdf_corpus.py --dir data/bench/sol2/volltext`) darauf ansetzen.
Zeigt der Bericht `Zeichen 0` oder `zu wenig Text`, ist die Datei ein Scan und
gehoert nachbestellt oder abgetippt, nicht als leere Studie verbucht (siehe
`scan_grenze_20261108.md`). Fuer diese fuenf Artikel gilt das Schritt-Ziel
k >= 2 poolbare Zeilen auf der Einschaflatenz; das Gesamtziel k >= 5 ist an die
A+B-Liste gebunden, weil fuenf Artikel im Schnitt eine poolbare Studie
liefern (`schwelle_k5_20261108.md`).
