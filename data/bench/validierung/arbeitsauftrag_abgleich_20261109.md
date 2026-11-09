# Abgleich Arbeitsauftrag vom 9.11.2026

Format nach Abschnitt 6 des Auftrags. Jeder Punkt: Aufgabe, Handlung,
Ergebnis, wissenschaftlicher Neuheitswert, Offenes, Modellaufrufe,
Reproduktion.

**Modellaufrufe in diesem Abgleich: 0. Guthabenverbrauch: 0.**

## Punkt 1 - E4l Browserpruefung

- **Aufgabe**: Darstellung der Meta-Karte visuell bestaetigen.
- **Handlung**: `scripts/serve_dashboard_stub.py` neu; `app.js` um drei
  Renderbloecke ergaenzt (Zeilenbasis, RVE, RVE-RE); Server auf DB-Kopie
  gestartet, Tab `meta` geoeffnet, DOM gelesen, Screenshots erstellt.
- **Ergebnis**: MACE `Basis: 6 Zeilen, 4 nach dem Kollaps (2
  zusammengelegt)`, `RVE (M=3): 0.751 [0.182; 1.319]`, `RVE-RE: 0.751
  [0.182; 1.319] - Breite x1.00`. incident CVD `RVE (M=4): -0.130
  [-0.849; 0.589]` vs. `RVE-RE: 0.295 [-0.600; 1.191] - Breite x1.25`.
  `node --check app.js` Exit 0, keine JS-Fehler, `/api/metaanalysis` 200.
- **Wissenschaftlich neu**: **Nein.** Bestaetigt bereits belegte Zahlen in
  der Oberflaeche.
- **Offen**: Betrieb mit laufendem Orchestrator; Viewport-Screenshot zeigt
  trotz Scroll den Seitenkopf - belastbar sind DOM-Text und Full-Page-Shot.
- **Reproduktion**: `.venv/bin/python.exe scripts/serve_dashboard_stub.py`
  (Port 8099), dann `http://127.0.0.1:8099` -> Tab Meta-Analysis.

## Punkt 2 - Betriebspruefung

- **Aufgabe**: Ist `current_topic`, paralleles Lesen/Schreiben lokal
  abgedeckt?
- **Handlung**: Codepfade geprueft (`dashboard/server.py:226`,
  `database.py:55` WAL), Testabdeckung gesucht.
- **Ergebnis**: `current_topic` wird an einer Stelle gelesen, aber nicht mit
  zwei Themen getestet; WAL ist gesetzt, gleichzeitiges Schreiben waehrend
  Lesen ist nicht getestet. Beides ist ohne Modell pruefbar.
- **Wissenschaftlich neu**: **Nein.**
- **Offen**: Zwei kleine lokale Tests; kein Voll-Lauf.
- **Beleg**: `betriebspruefung_matrix_20261109.md`.

## Punkt 3 - IP-Entscheidungsvorlage

- **Aufgabe**: Entscheidungsgrundlage fuer die gitignored Dateien.
- **Handlung**: Zweck, proprietaere Teile, Abhaengigkeiten,
  Reproduzierbarkeit, Risiken und vier Alternativen zusammengestellt.
- **Ergebnis**: Empfehlung Status quo plus Vorbereitung einer privaten
  Ablage; Veroeffentlichung erst mit geplanter Publikation.
- **Wissenschaftlich neu**: **Nein.** Keine Datei veraendert.
- **Offen**: Entscheidung des Projektverantwortlichen.
- **Beleg**: `ip_entscheidungsvorlage_20261109.md`.

## Punkt 4A - Evidenzluecken und Beschaffung

- **Aufgabe**: Liste der nicht beschaffbaren Volltexte, Status je Titel,
  priorisierte Fernleihliste.
- **Handlung**: Bereits am 8.11. erhoben; hier geprueft, nicht wiederholt.
- **Ergebnis**: 83 Dokumente ohne PMC-Volltext; gegen 1127 Textdateien,
  1136 XML und 36 PDFs geprueft - **0 lokal vorhanden**. Europe PMC: 77
  kein OA-PDF, 2 x 403, 3 ohne DOI; OpenAlex: 1 Treffer (Nunes 2008), nicht
  poolbar (SOL nur als PSQI-Komponente). Priorisierung A 5 / B 20 / C 39 /
  D 19; die 5 A-Titel stehen mit DOI und PMID in der Bestellanfrage.
  Kategorien sind nicht addiert, sondern je Dokument vergeben.
- **Wissenschaftlich neu**: **Nein** (Stand 8.11.).
- **Offen**: Lieferung der Fernleihe; danach Screening, Dedup, Extraktion.
- **Belege**: `volltext_beschaffung_20261108.md`,
  `bestellanfrage_fernleihe_20261108.md`, `zugangsliste_20261108.csv`,
  `dedup_register_20261108.md`.

## Punkt 4B - Klinische Vergleichbarkeit

- **Aufgabe**: Strukturierte Matrix der drei gepoolten Studien.
- **Ergebnis**: 14 Merkmale (Design, Population, Diagnose, Praeparat, Dosis,
  Einnahmezeit, Dauer, Messmethode, Messzeitpunkt, Endpunktstatus, Effekt,
  n). Urteil: gemeinsame Schaetzung nur als beschreibende Zusammenfassung
  interpretierbar, nicht als Effekt einer Referenzpopulation; Empfehlung
  fuer getrennte oder narrative Darstellung, falls keine vergleichbaren
  Studien dazukommen.
- **Wissenschaftlich neu**: **Nein** (Stand 8.11., hier nur geprueft).
- **Offen**: nichts, ausser Aktualisierung bei neuen Studien.
- **Beleg**: `validierung_sol3_20261108.md`, Aufgabe 1.

## Punkt 4C - Audit der Extraktion

- **SE-Diskrepanz PMC2952772**: berichtet SE 10, aus CI 9-54 folgt 11,0 bei
  df 29,6; S10 mit SE 11,0 ergibt -26,20 statt -26,29 (Differenz 0,09 min).
  Hauptanalyse bleibt bei SE 10 (Autorenangabe), Diskrepanz wird
  offengelegt.
- **Trial-ID**: 21091391 ist Sekundaerpublikation von S2 (NCT00397189);
  Beleg ist der Reference-Abschnitt des Registereintrags. Kein zweiter
  Datensatz, k bleibt 1 fuer S2.
- **HTA / MENDS**: 23098680 ist der HTA-Bericht von S1; SOL-Werte
  zeichengenau identisch (-37,49 bzw. -45,34). Wird nicht als eigene Studie
  gefuehrt; Zusatzangaben duerfen nur S1 ergaenzen.
- **Wissenschaftlich neu**: **Nein** (alles am 8.11. aufgeloest).
- **Belege**: `validierung_sol3_20261108.md` Aufgabe 3,
  `dedup_register_20261108.md`, `register_pruefung_20261108.md`,
  `mends_hta_zusatz_20261108.md`.

## Punkt 4D - Statistische Robustheit

- **Leave-one-out**: ohne MENDS -20,84 [-113,55; 71,87], p = 0,214; ohne
  Wade -34,56 [-75,67; 6,54], p = 0,059; ohne van Geijlswijk -25,22
  [-163,32; 112,88], p = 0,259. Kein Szenario signifikant, kein
  Vorzeichenwechsel.
- **Fixed Effect**: -22,22 (-30,01 bis -14,43) nur als Vergleich; HKSJ
  bleibt Hauptanalyse.
- **Keine** Aussagen zu Publikationsbias, Subgruppen oder Moderatoren; I2
  und tau2 ausdruecklich als bei k = 3 nicht belastbar markiert.
- **Wissenschaftlich neu**: **Nein**.
- **Beleg**: `validierung_sol3_20261108.md` Aufgabe 2,
  `pooling_sol3_20261108.md`.

## Punkte 9-11 (Phase 3)

- **Nicht bearbeitet**, weil Voraussetzung fehlt: keine neuen Volltexte.
  Ohne verifizierte Extraktion keine Aktualisierung der Metaanalyse, ohne
  belegten Engpass keine neue Software.

## Fazit

Der Auftrag war in Phase 2 zu grossen Teilen bereits am 8.11. erledigt; neu
hinzugekommen sind die Browserpruefung, die Betriebs-Matrix und die
IP-Vorlage. **Wissenschaftlich neu ist in diesem Lauf nichts** - das ist
die ehrliche Bilanz und zugleich der Grund, jetzt auf die Fernleihe zu
setzen statt auf weitere Technik.
