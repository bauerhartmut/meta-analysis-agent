# Teststudien für den Harness: acht lokal, zwei fehlen

Stand: 2026-11-09. Zweck ist die **Fähigkeit der Kette**, nicht Evidenz. Regel
für jede Zeile: kein belegter Sollwert, kein Testfall. Eine Studie ohne
bekannte Zahl im vorliegenden Text ist als Testfall wertlos, egal wie gut sie
inhaltlich passt.

Quelle der Sollwerte sind lokale Dateien, nicht Erinnerung:
`data/bench/sol2/volltext/23098680.txt`, `data/bench/sol2/xml/PMC*.xml`,
`data/bench/sol2/abstracts_b_20261108.xml`,
`pooling_sol3_20261108.json`, `volltext/19030713.txt`.

## A. Lokal vorhanden, sofort messbar

| Fall | Studie | Eingabe | Sollwert | Was der Fall prüft |
|---|---|---|---|---|
| T1 | S1 MENDS (23098680) | Text, PDF, XML | −37,49 (−55,27; −19,71); −45,34 (−68,75; −21,93) | Tabellenleser und Kopfzeilenerkennung — der aktuelle Blocker |
| T2 | S2 Wade (PMC2933606) | XML | −15,6 (−25,3; −6,0), SE 4,92 | Parallelstudie, Change statt Endwert |
| T3 | S3 van Geijlswijk (PMC2952772) | XML | −31,0, SE 10,0 | Differenz ohne Arm-Mittelwerte |
| T4 | 39437460 (Parkinson) | Abstract | `8.36 (95 % CI 4.38-12.34)` | SE aus berichtetem CI, Vorzeichen |
| T5 | 34181143 (ASD, 3 Arme) | Abstract | −22,0 / −28,0 / −5,0 min | Armauswahl bei Mehrarmstudien |
| T6 | 9566656 (Rett) | Abstract | 42,1 ± 12,0 → 19,1 ± 5,3 (mean ± SE) | SD/SE-Unterscheidung, Crossover |
| T7 | 20535539 (Crossover) | Abstract | „average of 47 min", keine Streuung | Negativfall: nicht poolbar, nicht schätzen |
| T8 | 19030713 (Nunes 2008) | Text | nur PSQI-Komponente, kein Minutenwert | Negativfall: Endpunkt nicht berichtet |

Acht Fälle, alle ohne Netz und ohne Modell. T1 ist der einzige, der heute schon
ein FAIL liefert (0 von 2).

## B. Fehlt, aber wird gebraucht

| Fall | Was fehlt | Kandidat | Warum es lokal nicht geht |
|---|---|---|---|
| T9 | Crossover-**Volltext** mit gepaarter Streuung (SD_diff, SE_diff oder CI der Differenz) | 9566656 oder 20535539 | Die Abstracts nennen nur Mittelwerte oder „47 min"; die gepaarte Streuung steht, wenn überhaupt, in Ergebnistabellen |
| T10 | Volltext mit **Tabelle, deren Kopf eine Effektspalte trägt** | 19299778 (14 vs. 28 min) oder 39437460 | Gegenprobe zum MENDS-Blocker: findet der Leser eine Tabelle, wenn der Kopf passt? |

Für T10 ist die Notwendigkeit nicht endgültig belegt: S2 und S3 liegen als XML
vor, und deren Tabellen könnten dieselbe Gegenprobe leisten. **Vor einer
Bestellung wird das an den lokalen XML geprüft.** Bleibt es bei zwei
Bestellungen, sind es T9 und T10.

## C. Ausdrücklich nicht nötig

| Gruppe | Grund |
|---|---|
| die übrigen 15 B-Titel | kein Sollwert im vorliegenden Text; sie liefern Evidenz, keine Testfälle |
| die 5 A-Titel | nur Metadaten lokal (`zitationen_a.json`), kein Abstract mit Zahlen |
| 35120753 | als PDF heruntergeladen, ist aber HTML (`<!DOCTY`), kein Volltext; zusätzlich Triage-Klasse D |
| die 36 PDFs in `data/origpdf` | Hash-Namen ohne Zuordnung, in `pdf.json` als 0 auswertbare PDFs geführt |
| weitere Netzabrufe | drei Kontakte haben gezeigt, dass die 83 ohne Bibliothek nicht erreichbar sind |

## D. Reihenfolge

1. **T1** (Blocker beheben, erneut messen) — offline, Sekunden.
2. **T4–T8** — dieselbe Messung, vier Berichtsformen und zwei Negativfälle.
3. **T2, T3** — XML-Tabellen als Gegenprobe; entscheidet, ob T10 überhaupt
   beschafft werden muss.
4. **T9** — erst wenn die lokalen Fälle grün sind, sonst misst man denselben
   Fehler an einem teuren Text.
5. **T10** — nur falls die XML-Gegenprobe nicht reicht.

## E. Was die Liste verhindert

Zwanzig Bestellungen, von denen achtzehn keinen Testfall ergeben. Die
Fernleihliste bleibt für die Evidenz richtig, aber für den Harness-Test
braucht es zwei Volltexte, und der zweite ist vielleicht schon durch die
lokalen XML abgedeckt.

## F. Stopp-Regel

Keine Beschaffung, bevor T1–T8 gemessen sind. Erst die Messung sagt, welche
Textsorte als nächstes fehlt — Tabellenkopf, Crossover-Streuung oder
Einheitenumrechnung. Vorher zu bestellen heißt raten, welche Lücke bleibt.
