# Bestellanfrage an die Bibliothek

Stand: 2026-11-08. Versandfertig bis auf zwei Angaben: **Name** und
**Einrichtung** (siehe Checkliste unten). Quelle der bibliografischen Daten:
PubMed-Metadaten (`data/bench/sol2/zitation_a.json`), keine Volltexte abgerufen.

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

Zur Einordnung: Ich bereite eine quantitative Zusammenfassung randomisierter
Studien zu Melatonin und der Einschaflatenz vor. Aus einer systematischen Suche
mit 114 Treffern sind 83 ueber unseren Zugang nicht zugaenglich; die fuenf
genannten sind davon die vorrangig relevanten randomisierten Studien mit
Einschaflatenz als Endpunkt. Ausgewertet werden ausschliesslich Mittelwerte und
Streuungen je Behandlungsarm, keine personenbezogenen Daten - und ohne diese
Volltexte stuetzte sich die Auswertung auf eine einzige Studie. Diese Luecke
laesst sich nicht durch Statistik schliessen, nur durch Zugang.

Falls einzelne Titel nur ueber Fernleihe oder Dokumentlieferung zugaenglich
sind, bitte ich um diesen Weg. Bitte stellen Sie die Volltexte, wenn moeglich,
als durchsuchbares PDF mit Textebene bereit; ein reiner Scan ohne Textebene ist
fuer die Auswertung nicht verwendbar. Die anfallenden Gebuehren uebernehmen
wir; eine Kostenstelle nenne ich Ihnen gern, sobald Sie die Kosten beziffern
koennen.

Fuer Rueckfragen antworten Sie bitte einfach auf diese E-Mail.

Vielen Dank und freundliche Gruesse
[Name]
[Einrichtung, z. B. TU Darmstadt, Fachbereich ...]
```

## Vor dem Senden

Nur zwei Felder sind offen, beide stehen in der Signatur:

| Feld | Warum es offen bleibt |
|---|---|
| `[Name]` | Name des Absenders - nicht aus dem Projekt ableitbar |
| `[Einrichtung, ...]` | Einrichtung und Fachbereich tragen die Kostenuebernahme |

Alles andere ist bewusst ohne Angabe formuliert, damit nichts erfunden wird:

- **Betrag:** entfallen. Statt einer Obergrenze steht die Zusage, die Kosten zu
  uebernehmen und die Kostenstelle nach Nennung des Betrags nachzureichen. Wer
  eine Obergrenze braucht, kann sie hier eintragen; sie ist nicht noetig.
- **Kostenstelle:** entfallen, gleiche Begruendung (siehe oben).
- **Telefon und E-Mail:** entfallen. "Antworten Sie auf diese E-Mail" nutzt die
  Adresse, aus der die Mail versendet wird - nichts zu tippen, nichts falsch.

Nach dem Ausfuellen: Text aus dem Codeblock in das Mailprogramm uebernehmen,
die beiden Felder ersetzen, senden. Die fertige Fassung ohne Markdown liegt
daneben in `bestellanfrage_20261108.txt`; beide Dateien werden gleich gepflegt.

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
- Falls eine Kostenstelle vorab gebraucht wird: kurz nachfragen lassen, sie
  wird innerhalb eines Werktags nachgereicht.

## Nach Erhalt

Die PDFs in `data/bench/sol2/volltext/` ablegen, dann den Triage-Ablauf
starten:

```bash
.venv/bin/python.exe scripts/triage_lieferung.py \
  --dir data/bench/sol2/volltext \
  --json data/bench/sol2/lieferung.json \
  --md data/bench/sol2/lieferung.md
```

Der Bericht nennt je Datei den Zustand (poolbar, Scan, Endpunkt nicht
berichtet) und schreibt k gegen das Schritt-Ziel fort. Zeigt er "kein
Textlayer", gehoert die Datei nachbestellt oder abgetippt, nicht als leere
Studie verbucht (siehe `scan_grenze_20261108.md`). Fuer diese fuenf Artikel gilt
das Schritt-Ziel k >= 2 poolbare Zeilen auf der Einschaflatenz; das Gesamtziel
k >= 5 ist an die A+B-Liste gebunden, weil fuenf Artikel im Schnitt eine poolbare
Studie liefern (`schwelle_k5_20261108.md`).
