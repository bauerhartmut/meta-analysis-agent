# Vorhaben: Literaturbestellung (12 Artikel)

Stand: 2026-11-08. Dieses Dokument beschreibt **das Vorhaben**, nicht ein
Ergebnis. Es haelt fest, was bestellt wird, warum, in welcher Reihenfolge und
was dafuer noch fehlt. Zahlen stammen aus den genannten Dateien; nichts ist
geschaetzt.

## Zweck in einem Satz

Die Evidenzbasis der Melatonin-Analyse verbreitern: zwoelf Artikel beschaffen,
die ueber den vorhandenen Zugang nicht erreichbar sind, damit k von 3 auf etwa
5 steigt und die Heterogenitaet pruefbar wird.

## Ausgangslage

- Suche: 114 Treffer, davon 31 als XML, 20 gegen die Kriterien geprueft, drei
  eingeschlossen (`stand_kurz_20261108.md`).
- Ergebnis bei k = 3: **-26,29 min (95%-CI -55,57 bis 3,00), p = 0,0610**;
  das Intervall schliesst die Null ein (`pooling_sol3_20261108.json`).
- Nicht beschaffbar: **83 Dokumente** - 77 ohne freien Volltext, 14 mit
  Verlags-403, 0 lokal vorhanden (`zugangsliste_20261108.csv`).
- Konsequenz: Die Luecke ist keine Rechenfrage. Weitere Statistik am Korpus
  bringt nichts; nur Zugang bringt Studien.

## Was bestellt wird

Zwoelf Zeitschriftenartikel, jeder mit DOI und PMID, in zwei Gruppen
(`bestellanfrage_20261108.md`, Abschnitt "Warum genau diese zwoelf"):

| Gruppe | Anzahl | Auswahlgrund |
|---|---:|---|
| 1 | 5 | vorrangige Treffer der Zugangsliste (Prioritaet A): Melatonin, RCT-Signal, Einschaflatenz oder Insomnie als Endpunkt |
| 2 | 7 | nach Abstract-Triage als sicher poolbar eingestuft (Klasse A): randomisiert, placebokontrolliert, SOL als Endpunkt, Zahlen im Abstract erkennbar |

**Nicht bestellt** (5 Dokumente, in der Triage Klasse D):

| PMID | Grund |
|---|---|
| 40791136 | Walnuss-Intervention, kein Melatonin |
| 34293628 | Melatonin gegen Triclofos, kein Placebo |
| 29619605 | Melatonin gegen Meloxicam, kein Placebo |
| 23098680 | HTA-Bericht der MENDS-Studie, Duplikat von S1, lokal vorhanden |
| 9737496 | Notaerzte nach Nachtschicht, kein SOL-Endpunkt berichtet |

**Vorgemerkt, nicht Teil dieser Bestellung:** sieben B-Dokumente der Klasse B
(30160043, 20025642, 18078449, 15275698, 11211063, 26569624, 17404779) - nur
falls die zwoelf Titel nicht ausreichen.

## Wie die Bestellung rausgeht

1. **Mail-Fassung** (`bestellanfrage_20261108.txt`): Betreff, Anschreiben,
   zwoelf Titel mit DOI/PMID, Bitte um PDF **mit Textebene** und die Zusage,
   die Gebuehren zu uebernehmen.
2. **Fernleih-/Formularfassung** (`bestellanfrage_fernleihe_20261108.txt`):
   dieselben Titel fuer Portale, die nur Einzelfelder erheben; ohne
   Projektkontext und ohne Absender, weil das Formular beides selbst abfragt.
3. **Signatur**: `[Name]` und `[Einrichtung, Fachbereich]` stehen in der
   Vorlage als Platzhalter. Sie lassen sich nicht aus dem Projekt ableiten und
   werden nicht geraten. Vorbereitet ist ein Einsetzschritt
   (`scripts/bestellung_fertig.py`), der genau diese zwei Zeilen ersetzt und
   abbricht, wenn sich mehr als zwei Zeilen aendern wuerden.

## Was von wem kommt

| Angabe | von wem | wofuer |
|---|---|---|
| Name des Absenders | Auftraggeber | Signatur der Mail |
| Einrichtung und Fachbereich | Auftraggeber | Signatur; traegt die Kostenuebernahme |
| Kostenstelle | Auftraggeber, auf Nachfrage | viele Bibliotheken liefern erst nach Nennung |
| Lieferadresse / E-Mail | Formularkonto bzw. Absenderadresse | Zustellung |

Bewusst **nicht** im Anschreiben: Betrag, Kostenstelle, Telefon, E-Mail. Zur
Gebuehrenfrage steht stattdessen die Zusage, die Kosten zu uebernehmen und die
Kostenstelle nach Nennung des Betrags nachzureichen. Lieber eine Angabe
weniger als eine erfundene.

## Pruefungen vor dem Absenden

Bereits erledigt (Skript gegen `triage_b_20261108.md` und `zitationen_a.json`,
ohne Netz):

- Titel im Codeblock, in der `.txt` und in der Fernleihfassung: je 12
- eindeutige DOIs / PMIDs: 12 / 12, keine Dublette
- Codeblock gegen `.txt`: zeichengleich nach Zeilenende-Normalisierung
- Gruppe 1 gegen `zitationen_a.json`: alle 5 PMIDs vorhanden
- Gruppe 2 gegen die Triage: deckungsgleich mit den 7 A-PMDs
- Betreff gegen Text: "12" und "zwoelf" stimmen ueberein

Offen: die zwei Signaturfelder. Ohne sie geht die Mail nicht raus.

## Nach Eingang der Volltexte

1. PDFs nach `data/bench/sol2/volltext/` legen.
2. `scripts/triage_lieferung.py --dir data/bench/sol2/volltext` laufen lassen;
   der Bericht nennt je Datei den Zustand (poolbar, Scan, Endpunkt nicht
   berichtet).
3. "kein Textlayer" heisst nachbestellen oder abtippen - **nicht** als leere
   Studie verbuchen (`scan_grenze_20261108.md`).
4. Extraktion in die eingefrorene Vorlage (54 Felder), danach
   `scripts/freeze_extraktion.py --check`.
5. Bei Crossover-Studien (20535539, 16919138, 9566656) vor der Extraktion die
   gepaarte Streuung klaeren.
6. Bei k >= 5: erneutes Pooling, dann Subgruppen nach Alter und Dosis.

## Grenzen und Risiken

- **Unbekannte Ausbeute.** Bei einer Screeningsquote von 3 von 31 XML (rund
  10 %) waeren von 83 Dokumenten etwa 8 poolbar - das waere genug, um k zu
  verdoppeln; garantiert ist es nicht.
- **Berichtsstil.** Ein Teil der Literatur berichtet keine armweisen
  Mittelwerte mit Streuung; solche Volltexte erhoehen k nicht, sondern nur den
  Ausschlussgrund-Zaehler. Der MENDS-Fall zeigt, wie weit das gehen kann
  (`gegencheck/mends_kopf_20261108.md`).
- **Kosten und Zeit.** Fernleihe kostet Gebuehren und Tage bis Wochen. Der
  Nutzen fuer die Analyse ist gross, der Zeitgewinn null - bis die Lieferung
  da ist, aendert sich keine Zahl.
- **Kein Automatismus.** Die Bestellung ist ein einmaliger Vorgang, kein
  Werkzeug. Ein Skript dafuer waere nur dann sinnvoll, wenn regelmaessig
  bestellt wird.

## Was dieses Vorhaben nicht ist

- Kein Nachweis, dass die 83 uebrigen Dokumente irrelevant sind - nur, dass sie
  ohne Zugang nicht pruefbar sind.
- Kein neues k. Die Zahl bleibt bei 3, bis Volltexte vorliegen und extrahiert
  sind.
- Keine Aenderung an Code, Datenbank oder Analyse.

## Quellen

`stand_kurz_20261108.md`, `bestandsaufnahme_20261108.md`,
`bestellanfrage_20261108.md`, `bestellanfrage_fernleihe_20261108.md`,
`triage_b_20261108.md`, `zugangsliste_20261108.csv`,
`pooling_sol3_20261108.json`, `scan_grenze_20261108.md`,
`gegencheck/mends_kopf_20261108.md`.
