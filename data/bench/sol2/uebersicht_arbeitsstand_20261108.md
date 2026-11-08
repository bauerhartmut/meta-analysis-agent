# Arbeitsstand Melatonin und Einschaflatenz: Was seit der Kandidatenpruefung entstanden ist

Stand: 2026-11-08. Bezugspunkt ist die A-D-Abgabe der Kandidatenpruefung
(`pruefung_kandidaten_20261108.md`, Commits `8635d38` und `f76a4a1`).
Alles danach ist hier chronologisch aufgefuehrt, jeweils mit dem Artefakt,
der Umsetzung und der Pruefung.

## 1. Ausgangslage nach dem Screening

- 114 Treffer aus der Suche, 31 davon als XML beschafft, 20 gescreent.
- Nach der Screening-Regel blieb genau eine poolbare Studie uebrig.
- Offene Frage damals: Reicht eine Studie fuer eine Metaanalyse, oder lassen
  sich die uebrigen Kandidaten so weit aufbereiten, dass k steigt?

## 2. Chronologie

| # | Commit | Artefakt | Was gemacht wurde | Wie umgesetzt | Pruefung |
|---|---|---|---|---|---|
| 1 | `8635d38` | `pruefung_kandidaten_20261108.md` | A-D-Abgabe: vier Kandidaten gegen die Einschlusskriterien geprueft, Zitate aus den XML | Zitate aus den PMC-XML extrahiert, jede Zahl mit Fundstelle | Jede Aussage mit Studien-ID und Zitatstelle |
| 1b | `f76a4a1` | `pruefung_kandidaten_20261108.md` | Rechenfehler bei der gepaarten SE korrigiert | Eine Zeile geaendert, Diff im Commit sichtbar | Nachgerechnet, danach unveraendert uebernommen |
| 2 | `18ad505` | `pooling_sol3_20261108.md/.json`, `scripts/pool_sol3.py` | Pooling der drei kompatiblen Studien, Random Effects mit HKSJ | Aufruf der vorhandenen Engine `research_agent.meta.pooling.pool`, Skript nur als Wrapper | Unabhaengige Nachrechnung von Hand, Abweichung 0,000000; Engine-Referenztests 8/8 |
| 3 | `26a452f` | `volltext_beschaffung_20261108.md` | Pruefung, ob die 83 Dokumente ohne PMC lokal oder frei verfuegbar sind | Abgleich gegen 1127 lokale Texte, 1136 XML, 36 PDFs; Europe PMC und OpenAlex abgefragt | 0 von 83 lokal, 0 PMC-Treffer, 1 OpenAlex-Treffer (nicht poolbar) |
| 4 | `4e9cd8e` | `dedup_register_20261108.md/.json` | Doppelpublikationen der 83 gegen die drei eingeschlossenen Studien pruefen | Titel-, Autoren- und Registerabgleich; Register-IDs per grep verifiziert | Kategorie A: 1 sicher (HTA = MENDS); B: zwei Verdachtsfaelle; C: acht geprueft |
| 5 | `47fdd55` | `mends_hta_zusatz_20261108.md`, S8/S9 in `pooling_sol3.json` | HTA-Bericht auf zusaetzliche Arm-Mittelwerte und Streuungen pruefen | `pdftotext -layout` auf 841.300 Zeichen, Tabellenvergleich HTA gegen BMJ zeilenweise | Tabelle 7 identisch mit BMJ Tabelle 3; neu nur die unadjustierte Differenz mit CI |
| 6 | `20ddb66`, `8ce7ad6` | `forest_sol3_20261108.md`, `scripts/forest_sol3.py` | Forest-Tabelle mit Effekt, CI und Gewichten fuer alle Analysen | Gewichte aus SE und tau^2 des JSON neu berechnet, ASCII-Balken, Achse | Gewichtssumme je Analyse 100,000000 %; Quelle PMC2952772 Tabelle 2 im XML gegengeprueft |

## 3. Inhaltliche Entscheidungen und ihre Begruendung

### Auswahlregel vor der Rechnung

In `auswahlregel_pooling_20261108.md` wurde vor der gepoolten Berechnung
festgelegt, welche Zeile je Studie eingeht:

- **PMC2933606**: groessere Population (65-80 Jahre) statt der
  Low-excretor-Untergruppe.
- **PMC2952772**: von den Autoren empfohlene Dosis 0,05 mg/kg statt 0,1 oder
  0,15 mg/kg.
- **PMC3489506**: vollstaendigste Messmethode, also Schlaftagebuch statt
  Aktigraphie.

Damit ist die Auswahl nicht nachtraeglich an das Ergebnis angepasst; die
Alternativen stehen als S1 bis S3 in der Sensitivitaetsliste.

### Doppelpublikationen

Der HTA-Bericht 23098680 ist eine Doppelpublikation des BMJ-Artikels
PMC3489506 (MENDS). Er zaehlt nicht als zweite Studie, k bleibt 3. Das ist
im Dedup-Register als Kategorie A dokumentiert.

### Endpunkt der groessten Studie

PMC3489506 fuehrt SOL urspruenglich als primaeren Endpunkt und stuft ihn per
Amendment zu einem sekundaeren herab. Der Effekt bleibt berichtbar, ist aber
in der Bewertung entsprechend zu kennzeichnen.

### Streuungen

Keine SD wurde geschaetzt, wo keine berichtet war. Wo ein CI vorlag, wurde
die SE daraus abgeleitet ((obere - untere Grenze) / 3,919928); das ist im
Bericht als Ableitung markiert.

## 4. Zahlenstand

Hauptanalyse: **-26,29 min (95 %-CI -55,57 bis 3,00), k = 3, p = 0,061,
tau^2 = 104,5, I^2 = 63,0 %**. Fixed-Effect zum Vergleich -22,22
(-30,01 bis -14,43).

Zehn Sensitivitaeten (S1 bis S5c, S3b, S8, S9) liegen zwischen -20,84 und
-34,56 min; keine dreht das Vorzeichen. Details in
`pooling_sol3_20261108.md` und `forest_sol3_20261108.md`.

Die Gewichte der Hauptanalyse: PMC2933606 43,1 %, PMC3489506 29,7 %,
PMC2952772 27,2 %. Die Studie mit dem kleinsten Effekt traegt das groesste
Gewicht, weil ihre SE am kleinsten ist.

## 5. Was nicht ging

- **83 Dokumente ohne PMC**: 77 ohne freien Volltext, 14 mit Verlags-403.
  Beschaffung nur ueber Fernleihe oder institutionellen Zugang. Keine
  Paywall-Umgehung.
- **`cryptography` nicht installierbar**: fuer verschluesselte PDFs wurde
  stattdessen das vorhandene `/ucrt64/bin/pdftotext` genutzt.
- **Kein k >= 5**: ohne die 83 Volltexte nicht erreichbar; Subgruppen und
  belastbare Heterogenitaetsaussagen sind damit nicht moeglich.

## 6. Pruefungen im Ueberblick

- Unabhaengige Nachrechnung aller Pooling-Formeln von Hand: Abweichung
  0,000000 zur Engine.
- Ein Rechenfehler bei der gepaarten SE wurde gefunden und in `f76a4a1`
  korrigiert, nicht stillschweigend ueberschrieben.
- Engine-Referenztests: 8 von 8 gruen, Engine unveraendert.
- Gewichtssummen der Forest-Tabelle: je Analyse 100,000000 %.
- Quellpruefung PMC2952772 Tabelle 2 im XML: Differenz 0:31, SE 0:10,
  CI 0:09-0:54, df 29,6.
- Jeder Lauf mit Exit-Status geprueft, nicht nur mit sichtbarer Ausgabe.

## 7. Offene Punkte

1. **PMC2952772**: SE 10 berichtet, CI 9-54 impliziert SE 11,0. Eine
   Sensitivitaet S10 mit 11,0 wuerde die Rundungsfrage schliessen
   (erwartete Verschiebung rund 0,5 min).
2. **21091391** gegen NCT00397189 pruefen: Verdacht auf Sekundaeranalyse von
   PMC2933606. Kategorie B im Dedup-Register.
3. **Appendix 6/7 des HTA-Berichts** sind im extrahierten Text nicht
   enthalten; dort koennten Per-Protocol-Werte fuer SOL stehen.
4. **Fernleihe** der 83 Dokumente ist der einzige Weg zu k >= 5.

## 8. Empfehlung

Der groesste Hebel ist k, nicht das Modell. Vor der Fernleihe lohnt der
kleine Schritt S10 (eine Zeile, kein Netzzugriff, keine Kosten), damit die
Sensitivitaetsliste konsistent ist. Danach: 21091391 pruefen, dann
Fernleihe anfordern.

## 9. Artefaktverzeichnis

| Datei | Inhalt |
|---|---|
| `bestandsaufnahme_20261108.md` | Treffer, XML, Screening-Stand |
| `pruefung_kandidaten_20261108.md` | A-D-Abgabe mit Zitaten |
| `auswahlregel_pooling_20261108.md` | vorab fixierte Auswahl- und Modellregeln |
| `pooling_sol3_20261108.md/.json` | Hauptanalyse und Sensitivitaeten |
| `forest_sol3_20261108.md` | Forest-Tabelle mit Gewichten |
| `volltext_beschaffung_20261108.md` | Beschaffungsnachweis der 83 Dokumente |
| `dedup_register_20261108.md/.json` | Doppelpublikations-Register |
| `mends_hta_zusatz_20261108.md` | HTA-Zusatzdaten und S8/S9 |
| `zugangsliste_20261108.csv` | 83 Dokumente mit DOI |
| `scripts/pool_sol3.py` | Pooling-Aufruf |
| `scripts/forest_sol3.py` | Forest-Tabelle |
| `scripts/fetch_oa_zugangsliste.py` | Open-Access-Pruefung, read-only |
| `scripts/fetch_openalex_zugangsliste.py` | OpenAlex-Pruefung, read-only |
| `scripts/match_zugangsliste_volltexte.py` | Abgleich lokale Texte |
| `scripts/match_zugangsliste_xml.py` | Abgleich lokale XML |
