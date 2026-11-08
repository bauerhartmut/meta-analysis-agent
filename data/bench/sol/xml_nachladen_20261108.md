# Die 10 fehlenden Korpus-Dokumente: nachgeladen, gelesen, ausgezaehlt

Stand: 2026-11-08. Frage: Aendert sich der Befund "0 lesbare SOL-Zeilen",
wenn man die 10 Dokumente liest, die in Lauf 1 nur an einem HTTP-500 des
Anbieters scheiterten? **Antwort: nein - 0 von 10.**

Damit ist die im Abschlussbericht notierte Grenze ("10 Dokumente ungeprueft")
aufgeloest: **33 von 33 Korpus-Dokumenten sind jetzt gelesen.**

## 1. Beschaffung: Europe PMC scheitert, NCBI liefert

| Versuch | Anfragen | Ergebnis |
|---|---:|---|
| Europe PMC `fullTextXML` (Lauf 1) | 10 (+10 Nachladen) | 20 x HTTP 500 |
| Europe PMC `fullTextXML` (dieser Schritt) | 10 | 10 x HTTP 500 |
| **NCBI `efetch.fcgi?db=pmc`** | **10** | **10 x HTTP 200, 8.625-100.555 Bytes** |

Die zehn PMCIDs sind also nicht gesperrt, sondern beim Europe-PMC-REST-Endpunkt
defekt. NCBI liefert vollstaendige JATS-Artikel; die Groesse von
`PMC4425994` (100 KB) spricht fuer den kompletten Volltext, nicht fuer ein
Abstract.

Nachweise: `xml_fetch_20261108.json` (Europe PMC, 0/10),
`xml_fetch_ncbi_20261108.json` (NCBI, 10/10), Dateien in
`data/bench/sol/xml_fetch_ncbi/`.

## 2. Lesen: 62 Tabellenzeilen, 0 Effekte

Beide Leser laufen unveraendert (kein Code angefasst), nur auf dem neuen
Verzeichnis:

| Leser | Zeilen | Kandidaten | gespeichert |
|---|---:|---:|---:|
| Effektspalten | 62 | 0 | 0 |
| Arm-Deskriptiva | 62 | 0 (konvertierbar) | 0 |
| Zielmass-Schnitt | 0 | - | 0 |
| **lesbare SOL-Zeilen** | | | **0** |

Ablehnungsgruende des Effektspalten-Lesers (Summe 62):

| Grund | Zeilen |
|---|---:|
| keine Effektspalte im Kopf | 36 |
| Kopfzeile (9) passt nicht zur Zeile (8) - colspan nicht aufloesbar | 20 |
| Kopfzeile (9) passt nicht zur Zeile (1) - colspan nicht aufloesbar | 4 |
| Kopfzeile (2) passt nicht zur Zeile (1) | 2 |

Ablehnungsgruende des Arm-Lesers (Summe 62):

| Grund | Zeilen |
|---|---:|
| kein Mittelwert mit eindeutiger Streuung in zwei Spalten | 33 |
| nicht genau zwei Spalten mit Mittelwert und Streuung | 19 |
| zu wenige Spalten | 6 |
| Fallzahl je Arm fehlt | 3 |
| gemischte Zeitpunkte (Baseline und Follow-up) | 1 |

Nur 36 der 62 Zeilen haben ueberhaupt gleich viele Kopf- wie Zellenwerte; die
restlichen 26 scheitern an `colspan`/`rowspan`-Aufloesung. Das ist derselbe
Befund wie im Korpus: die Tabellen dieser Dokumente sind Uebersichts- und
Demografietabellen, keine Zwei-Arm-Effekttabellen.

## 3. Was das fuer den Bericht heisst

Der Abschlussbericht fuehrt als Grenze: "3 XML des Korpus und 10 XML der
Q1-Stichprobe fehlen (HTTP 500). Die 10 ungeprueften Dokumente koennten die
Null des Abstract-Laufs veraendern." Diese Grenze ist **erledigt**: alle 33
Dokumente der Stichprobe sind gelesen, die Null bleibt.

Zahlen nach diesem Schritt:

| Kennzahl | Wert |
|---|---:|
| Q1-Stichprobe | 33 |
| gelesen (XML vorhanden) | **33** |
| lesbare SOL-Zeilen | **0** |
| SOL-Zeilen im Gesamtkorpus (unveraendert) | 11 aus 5 Quellen, k = 1 |

## 3b. Nachtrag: auch der Gesamtkorpus ist vollstaendig

Derselbe Weg schliesst die zweite Luecke. Im Korpus fehlten 3 von 1.059 XML:

| PMCID | DOI | Bytes | Tabellenzeilen | Effekte |
|---|---|---:|---:|---:|
| PMC7163627 | (Poster-Sammelband) | 5.331 | 4 | 0 |
| PMC8959415 | 10.3389/fnins.2022.825246 | 243.677 | (enthalten) | 0 |
| PMC9554922 | 10.1016/j.brainresbull.2022.05.002 | 530.063 | (enthalten) | 0 |

Beide Leser zusammen: 4 Tabellenzeilen, alle vier ohne Effektspalte im Kopf,
0 konvertierbar, 0 SOL. Die beiden inhaltlich passenden Dokumente (Melatonin-
Stoffwechsel bei psychiatrischen Patienten, translationale Schlaf-Regulation)
sind Review- bzw. Uebersichtsarbeiten ohne Zwei-Arm-Effekttabelle.

**Damit gilt: 1.059 von 1.059 Korpus-XML und 33 von 33 Stichproben-XML sind
gelesen, und der Befund bleibt 0 lesbare SOL-Zeilen aus diesem Nachschub.**

## 4. Grenzen

- Die 10 Dokumente wurden ueber einen anderen Anbieter geholt als die 23 aus
  Lauf 1. Ein Vergleich der Leserquote zwischen beiden Gruppen ist deshalb
  nicht sauber; die 0 steht fuer sich.
- 26 der 62 Zeilen waren wegen `colspan` gar nicht auswertbar. Ein
  Spaltenaufloeser fuer diese Dokumente wuerde die Zahl der **Zeilen** erhoehen,
  nach Lage der Kopfzeilen aber nicht die Zahl der **Effekte**.
- Die Aussage "0 SOL" gilt fuer die gelesenen XML-Dateien, nicht fuer
  Abbildungen in den Original-PDFs. Fuer die braucht es einen Vision-Lauf
  (offen, siehe Statusliste).
