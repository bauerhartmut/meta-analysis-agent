# Stand in einer Seite

Stand: 2026-11-08. Alle Zahlen stammen aus den genannten Dateien; nichts
geschaetzt. Vorgaengerfassung dieses Dokuments (k = 1) ist damit ueberholt.
Langfassung: `stand_melatonin_20261108.md`, Chronologie:
`uebersicht_arbeitsstand_20261108.md`.

## Frage

Kann der Agent aus guten Primaerstudien eine Metaanalyse bauen - messbar an der
Zahl poolbarer Studien (k), nicht an der Zahl gebauter Werkzeuge?

## Antwort heute

**Die Analyse steht, die Evidenz traegt sie nicht.** k = 3, gepoolt
-26,29 min (95%-CI -55,57 bis 3,00), das Intervall schliesst die Null ein.
Alle methodischen Schritte sind vollstaendig und nachgerechnet; offen ist
ausschliesslich Material: 83 Dokumente ohne Volltext.

## Kennzahlen

| Kennzahl | Wert | Quelle |
|---|---:|---|
| poolbare Studien (k) | **3** | `pooling_sol3_20261108.json` |
| gepoolter Effekt (RE, HKSJ) | **-26,29 min** | ebd. |
| 95%-CI | -55,57 bis 3,00 | ebd. |
| p-Wert | 0,0610 | ebd. |
| tau^2 / Q / I^2 | 104,5 / 5,41 / 63,0 % | ebd. |
| ausgewertete Personen | 427 (113 + 281 + 33) | ebd. |
| Fixed-Effect (Vergleich) | -22,22 [-30,01; -14,43] | ebd. |
| Sensitivitaetsanalysen | 11, Spanne -20,8 bis -34,6 min | `forest_sol3_20261108.md` |
| RoB 2 | 1 hoch, 2 einige Bedenken | `rob2_sol3_20261108.md` |
| GRADE | sehr niedrig (5 Domaenen) | `grade_sol3_20261108.md` |
| bestellte Volltexte | 12, eingetroffen 0 | `bestellanfrage_20261108.md` |
| ohne Volltext insgesamt | 83 (77 kein OA, 14 Verlags-403) | `zugangsliste_20261108.csv` |

## Was fertig ist

1. **Auswahl.** 114 Treffer, 31 XML, 20 gegen die Kriterien geprueft, drei
   Studien eingeschlossen. Die Auswahlregel (welche Zeile je Studie) wurde
   *vor* der Rechnung festgelegt (`auswahlregel_pooling_20261108.md`); die
   Alternativen stehen als Sensitivitaeten S1-S4 daneben.
2. **Pooling und Validierung.** Handnachrechnung mit Abweichung 0,000000,
   Engine-Referenztests 8/8. Leave-one-out: ohne Gringras -20,84, ohne Wade
   -34,56, ohne van Geijlswijk -25,22. Keine Studie traegt mehr als 43 %
   Gewicht; die Richtung bleibt in allen elf Analysen negativ.
3. **Bewertung.** RoB 2 je Domaene mit Zitaten, gegen die Register geprueft:
   SOL ist bei allen drei Studien primaer registriert, bei MENDS per
   Amendment herabgestuft. GRADE: sehr niedrig, fuenf schwerwiegende
   Domaenen, jede mit Gegenargument dokumentiert.
4. **Werkzeuge fuer die Erweiterung.** Crossover-Regel C1-C7 vorab fixiert;
   Extraktionsformular mit 54 Feldern und CSV-Vorlage, an S1-S3 getestet und
   per SHA-256 eingefroren; Triage der 20 B-Dokumente; Bestellliste.

## Was offen bleibt

| Offen | Blockiert durch | Was es bringt |
|---|---|---|
| 12 bestellte Volltexte | Versand der Anfrage (nur Name und Einrichtung in der Signatur fehlen) | k 3 -> bis etwa 5 |
| 7 B-Titel (Triage) | keine Zahlen im Abstract | poolbar nur bei berichteten Werten |
| 4 Crossover-Studien | Extraktion nach der C1-C7-Regel | k erhoeht sich, gepaarte SE noetig |
| 12 leere Zeilen der Extraktionsvorlage | Volltexte | Erweiterung ohne Neuaufbau |
| k >= 5 | Beschaffung | Inkonsistenz und Unpraezision pruefbar, GRADE-Hebel |
| Publikationsbias | k < 10 | Funnel und Egger nicht aussagekraeftig |

Was **nicht** offen ist: Methodik, Rechenweg, Bewertung und Reproduktion. Ein
weiterer Durchgang am alten Korpus bringt bei der Einschaflatenz nichts - vier
gemessene Hebel ergaben dort null.

## Naechste Schritte

1. **Bestellung absenden** (12 Titel, 5 A-Prioritaet plus 7 aus der Triage).
   Das ist der einzige Schritt, der k bewegt.
2. **Nach Eingang:** `triage_lieferung.py`, dann `pruefe_lieferung.py`;
   Extraktion in die eingefrorene Vorlage, danach `freeze_extraktion.py
   --check`.
3. **Bei k >= 5:** erneutes Pooling, dann Subgruppen nach Alter und Dosis -
   erst dann ist die Heterogenitaet aufloesbar.
4. **Bei k = 3 (keine Lieferung):** Abschluss mit dem Befund, dass der
   Berichtsstil dieser Literatur keine armweisen Mittelwerte traegt.

## Reproduktion

```bash
.venv/bin/python.exe scripts/pool_sol3.py
.venv/bin/python.exe scripts/forest_sol3.py
.venv/bin/python.exe scripts/freeze_extraktion.py --check
```
