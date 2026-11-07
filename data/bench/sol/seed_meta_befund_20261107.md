# Saat-Korpus aus der Melatonin-Metaanalyse: sieben Trials, null offene Volltexte

Stand: 07.11.2026. Auftrag: aus der gefundenen Metaanalyse einen Saat-Korpus
ihrer eingeschlossenen Trials bauen und pruefen, ob daraus ein belegtes
k >= 2 entsteht. Ergebnis vorweg: **nein** - die sieben Trials sind nicht
offen zugaenglich, und der einzige erreichbare Volltext liefert keine Zeile.

## Die Metaanalyse

| Feld | Wert |
|---|---|
| Titel | Efficacy and safety of melatonin for sleep onset insomnia in children and adolescents: a meta-analysis of randomized controlled trials |
| DOI | 10.1016/j.sleep.2019.02.017 |
| Journal | Sleep Medicine, 2020 |
| PMID | 31982807 |
| Europe PMC | kein PMCID, `isOpenAccess = N`, `inEPMC = N` |
| Volltext | nicht abrufbar (Verlagszugang) |

Ihr Abstract nennt die Zielwerte, gegen die ein Saat-Korpus validierbar
waere:

| Endpunkt | Effekt (MD) | 95 %-CI |
|---|---|---|
| Sleep onset time (SOT) | -0,62 h | -0,80 bis -0,45 |
| DLMO | -0,82 h | -1,23 bis -0,41 |
| SOL | -0,36 h | -0,49 bis -0,24 |
| Total sleep time | +0,38 h | 0,09 bis 0,66 |
| Drop-out gesamt (OR) | 1,51 | 0,57 bis 4,05 |
| Drop-out unerwuenscht (OR) | 3,35 | 0,13 bis 86,03 |

Eingeschlossen: **7 Trials, 387 Teilnehmer**, Qualitaet "low to moderate".

## Wie der Saat-Korpus gebaut wurde

1. **Referenzliste** der Metaanalyse ueber die Europe-PMC-References-API
   geholt: 46 Referenzen (die API liefert fuer MED-Datensaetze keine DOIs
   mit, nur Titel und Jahre).
2. **Trial-Kandidaten gefiltert** ueber Titel: "melatonin" und
   ("random" oder "placebo" oder "controlled" oder "trial"): 8 Treffer.
3. **DOIs aufgeloest** ueber Europe-PMC-Titelsuche, Crossref als Rueckfall:
   8 von 8 aufgeloest.
4. **PMC-Zuordnung** ueber den NCBI-ID-Konverter und die Europe-PMC-Suche.
5. **Volltext geladen**, wo ein PMCID existiert.

Ergebnis der Zuordnung:

| DOI | Jahr | PMCID | im Korpus |
|---|---|---|---|
| 10.3109/07420528.2012.719962 | 2012 | keiner | nein |
| 10.1177/088307380101600204 | 2001 | keiner | nein |
| 10.1097/01.chi.0000085756.71002.86 | 2003 | keiner | nein |
| 10.1093/sleep/zsw038 | 2017 | keiner | nein |
| 10.1016/s0387-7604(03)00197-9 | 2004 | keiner | nein |
| 10.1111/j.1469-8749.1998.tb15445.x | 1998 | keiner | nein |
| 10.1034/j.1600-079x.2000.290105.x | 2000 | keiner | nein |
| 10.3390/healthcare6010023 | 2018 | PMC5872230 | nein |

**7 von 8 ohne PMC-Volltext**, zwei unabhaengige Pruefungen stimmen ueberein
(Europe-PMC-Titelsuche ohne `pmcid`, NCBI-ID-Konverter mit `status = error`).
Der einzige erreichbare Volltext ist die Langzeit-Follow-up-Studie von 2018 -
also gerade nicht einer der sieben randomisierten Kurzzeit-Trials.

Auch der Treffer im eigenen Korpus hilft nicht: `PMC6005466`
(`10.1371/journal.pmed.1002587`) ist die PLOS-Med-Studie zu Melatonin plus
Verhaltenstherapie bei **delayed sleep-wake phase disorder**, nicht eine der
sieben Kinder-Studien. Der eine Effekt, den unsere Leser belegen koennen
(DLMO, g = 0,413), liegt damit ausserhalb der Evidenzbasis der Metaanalyse -
eine Validierung gegen deren gepoolte Werte ist nicht moeglich.

## Lauf der vier Leser auf dem Saat-Korpus

Seed-Manifest: 1 Dokument (PMC5872230), XML lokal geladen (122.035 Bytes).

| Leser | Zeilen | Ablehnungen im Dokument |
|---|---:|---|
| Arm-Rechner | 0 | 23 Zeilen ohne Mittelwert mit Streuung in zwei Spalten |
| Fliesstext | 0 | 1 Satz ohne zwei Mittelwerte mit Streuung |
| Veraenderungswerte | 0 | 2 Saetze als Design-/Stichprobenbeschreibung |
| Effektspalten | nicht gelaufen (keine Effekttabelle im Dokument) |

**k >= 2 = 0.** Es gibt nicht einmal eine Zeile, geschweige denn zwei
unabhaengige Studien zum selben Endpunkt.

## Was das methodisch bedeutet

1. **Die Schranke ist der Zugang, nicht die Extraktion.** Fuer diese Frage
   existiert eine belastbare Evidenzbasis - sieben RCTs, 387 Kinder, ein
   gepooltes SOL-Ergebnis mit engem CI - und sie ist zu 100 % hinter
   Verlagszugang. Kein Leser, kein LLM und keine groessere Suche aendert das.
   Der offene Korpus enthaelt die Studien nicht, weil sie nicht offen sind.

2. **"Open Access" ist ein Filter mit Bias.** Die Europe-PMC-Query mit
   `OPEN_ACCESS:y` hat 1.056 Dokumente geliefert und dabei genau die
   klassische, hochwertige Kinder-Literatur ausgeschlossen, auf der die
   einzige publizierte Metaanalyse beruht. Ein Negativbefund aus diesem
   Korpus ist deshalb kein Befund ueber die Literatur, sondern ueber die
   offene Teilmenge - das gehoert in jede Interpretation.

3. **Der pragmatische Ausweg ist eine Handtabelle, kein Programm.** Sieben
   Zeilen (SOT/SOL je Arm mit SD) aus der Metaanalyse oder den PDFs von Hand
   zu erfassen, kostet Minuten und liefert per Konstruktion k = 7. Diese
   Tabelle ist dann Referenzdatensatz: sie validiert das Pooling und zeigt,
   ob unsere g-zu-MD-Umrechnung zu den publizierten -0,36 h passt.

## Grenzen

* Die Trial-Liste stammt aus der **Referenzliste** der Metaanalyse, nicht aus
  ihrer Included-Studies-Tabelle (die ist paywalled). Die 8 Kandidaten sind
  damit eine Obergrenze; welcher der acht ausgeschlossen wurde, ist offen.
* Der Titel-Filter kann Trials uebersehen, deren Titel kein
  Randomisationswort traegt, und Nicht-Trials einschliessen.
* `status = error` beim ID-Konverter heisst "DOI nicht in PMC"; ein
  PMC-Volltext unter abweichendem DOI ist damit nicht zu 100 % ausgeschlossen,
  aber die Europe-PMC-Titelsuche hat unabhaengig keinen PMCID geliefert.
* Unpaywall/Verlagsrepositorien wurden nicht abgefragt (kein Zugang, keine
  Zugangsdaten im Projekt).
