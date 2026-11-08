# Volltextbeschaffung der 83: Prüfung und Ergebnis

Stand: 2026-11-08. Auftrag: Analyse auf die 83 Dokumente der Zugangsliste
erweitern, alle SOL-Mittelwerte mit Streuung extrahieren, k auf 5–8 bringen.

**Ergebnis: k bleibt 3.** Keines der 83 Dokumente liefert einen neuen
poolbaren SOL-Effekt. Die 83 sind genau die Dokumente ohne PMC-Volltext; sie
sind überwiegend verlagsgebunden und nur über Fernleihe oder Lizenzzugang
erreichbar.

## Was lokal geprüft wurde

| Bestand | Umfang | Treffer unter den 83 |
|---|---|---|
| `data/bench/sol/fulltext` (Text) | 1093 | 0 |
| `data/bench/sol2/fulltext` (Text) | 34 | 0 |
| `data/bench/sol/xml` | 1056 | 0 |
| `data/bench/sol2/xml` | 31 | 0 |
| `data/bench/xml_all` + `xml6` | 49 | 0 |
| `data/origpdf` (PDF) | 36 | 0 |

Zusammen 1127 Texte, 1136 XML, 36 PDFs: **kein einziges der 83 Dokumente
liegt lokal**. Der scheinbare Titeltreffer im 1093er-Korpus war ein Review
(Cruz-Sanabria 2023), das eine der Studien zitiert - kein Primärbericht.

Die Zuordnung lief über PMID und DOI, nicht über Titel: In den XML steht die
PMID in `<article-id pub-id-type="pmid">`. Zwei Skripte, beide read-only:
`scripts/match_zugangsliste_volltexte.py`, `scripts/match_zugangsliste_xml.py`.

## Warum die 83 fehlen

`data/bench/sol2/fetch_log.json` zeigt für alle 83 den Status „kein PMC".
Es sind also nicht Dokumente, die man nur noch hätte herunterladen müssen,
sondern solche, für die PubMed Central keinen Volltext hat. Die Zugangsliste
ist die Bestellliste der Fernleihe, nicht eine Liste verpasster Downloads.

## Netzprüfung (drei Kontakte, danach abgebrochen)

| Quelle | Ergebnis |
|---|---|
| Europe PMC, 83 DOIs | 77 kein OA-PDF, 2 × HTTP 403, 3 ohne DOI, 1 PDF unlesbar, **0 geholt** |
| OpenAlex, 83 DOIs | 65 kein OA-PDF, 14 Download/Lesefehler, 3 ohne DOI, **1 geholt** |
| Retry auf 3 Repositorien-URLs | 1 lesbar (via `pdftotext`), 1 × 401, 1 × 403 |

Stichprobe Europe PMC (10.1111/jpc.70224, 10.1016/j.sleep.2020.10.018):
`isOpenAccess: N`, `fullTextUrlList` enthält nur „Subscription required".
Der Filter war also nicht zu streng.

## Der eine Treffer: 19030713

Nunes et al. 2008, *Braz J Med Biol Res* 41:926-931, COPD-Patienten,
Melatonin vs. Placebo, 3 Wochen.

SOL steht im Text nur als **PSQI-Komponente** („sleep latency", Skala 0–3),
nicht als Minuten-Mittelwert mit Streuung. Die berichteten p-Werte
(PSQI-Gesamt p = 0,012; Komponente Schlafbeginn p = 0,008) sind
Komponenten-Scores, keine Einschaflatenz in Minuten.

**Urteil: nicht poolbar** für eine MD-Analyse in Minuten. Kein k-Beitrag.

## Der zweite lesbare Text ist eine Doppelpublikation

23098680 (Appleton et al. 2012, *Health Technology Assessment* 16(40)) ist
der HTA-Bericht der **MENDS-Studie** - derselben Studie wie PMC3489506:

- SOL Tagebuch: −37,49 min (95 %-CI −55,27 bis −19,71), p < 0,0001
- SOL Aktigraphie: −45,34 min (95 %-CI −68,75 bis −21,93), p = 0,0003

Das sind exakt die Werte, die bereits als PMC3489506 in der Analyse stehen.
Der Bericht ist ausführlicher, aber keine unabhängige Studie. **k bleibt 1
für diese Studie**, nicht 2.

Das ist methodisch der wichtigste Befund der Beschaffungsprüfung: Die
Zugangsliste enthält Doppelpublikationen. Beim Screening nach der Lieferung
muss auf Studienebene dedupliziert werden (ISRCTN/Trial-Register, nicht
Titel), sonst zählt dieselbe Stichprobe doppelt.

## Konsequenz

- **k vorher 3 → nachher 3.** Keine neue poolbare Zeile.
- Die gepoolte Schätzung bleibt −26,3 min (95 %-CI −55,6 bis 3,0), k = 3,
  τ² = 104,5 (siehe `pooling_sol3_20261108.md`).
- Die 79 nicht geprüften Dokumente sind ohne Bibliothekszugang nicht
  erreichbar. Die Bestellung (`bestellanfrage_fernleihe_20261108.md`) ist
  der einzige Weg; ein weiterer Netzlauf bringt nichts, was die drei
  Kontakte nicht schon gezeigt hätten.
- Beim Eintreffen der Lieferung: zuerst Doppelpublikationen gegen die
  bestehenden Studien abgleichen, dann SOL-Zeilen extrahieren.

## Artefakte

| Datei | Inhalt |
|---|---|
| `match_volltexte_20261108.json` | 83 gegen 1127 Textdateien, 0 Treffer |
| `match_xml_20261108.json` | 83 gegen 1136 XML, 0 Treffer |
| `oa_status_20261108.json` | Europe-PMC-Status je DOI |
| `oa_openalex_20261108.json` | OpenAlex-Status je DOI, 1 Treffer |
| `volltext/19030713.txt` | Nunes 2008, nicht poolbar |
| `volltext/23098680.txt` | MENDS-HTA, Duplikat von PMC3489506 |
| `scripts/match_zugangsliste_*.py` | Zuordnung PMID/DOI, read-only |
| `scripts/fetch_oa_zugangsliste.py`, `scripts/fetch_openalex_zugangsliste.py` | OA-Prüfung, nur freie PDFs |
