# Architektur: Evidence-based Record Verification

Stand: 13.11.2026
Status: Prototyp implementiert; 20-Record-Pilot gelaufen; keine unabhaengige Validierung.

## 1. Grundsatz

Kein numerischer Record gelangt in den primaeren Pool, solange er nicht den
Status `verified` traegt. Ein Record wird nur verifiziert, wenn

1. beide Extraktionspfade jeden Pflichtwert liefern oder ein dokumentierter
   Grund fuer "nicht berichtet" vorliegt,
2. der Wert in einer konkreten Originalzelle mit Zeilen-, Spalten- und
   Zeitpunktkontext belegt ist,
3. der deterministische Vergleich keine offene Abweichung zeigt,
4. die Plausibilitaetspruefung keinen harten Fehler meldet und
5. keine nachtraegliche Aenderung an Quelle oder Extraktion die Freigabe
   invalidiert hat.

Zwei Modelluebereinstimmungen allein sind **keine** Verifikation. Pipeline B
liest unabhaengig von Pipeline A aus der Quelle; der Vergleich ist LLM-frei.
Der Vision-Adapter ist vorhanden, wurde im Pilot aber nicht gestartet.

## 2. Datenfluss

```text
Originaldokument / Tabelle
  ├─ Pipeline A: eingefrorene v6c-Extraktion (read-only)
  └─ Pipeline B: Layout-Tabellenleser (offline) oder Vision-Adapter (optional)
        │
        ├─ Evidenz: Dokument-Hash, Tabelle, Zeile, Spalte, Rohzelle, Excerpt
        ├─ deterministischer Feldvergleich (match / numeric_match / mismatch /
        │  missing_a / missing_b / both_missing / evidence_missing / ambiguous)
        ├─ Plausibilitaet (error / warning, keine automatische Korrektur)
        ├─ Statusmaschine + hash-verkettetes Audit-Journal
        └─ hartes Gate vor meta.pooling.build_analysis
```

## 3. Evidenzmodell

Jede Evidenz traegt:

- `document_id`, `document_hash`
- `table_id`, `table_caption`
- `line_start`, `line_end` (bei PDF spaeter `page`, `bbox`)
- `row_label`, `column_label`
- `raw_cell`, `excerpt`
- `field`, `value_text`, `exact`
- `evidence_hash`, `evidence_id`

Eine Zelle gilt nur dann als Beleg, wenn sie den Wert enthaelt und der
Zeilen-/Spaltenkontext nicht leer ist. Eine Baseline-Zelle kann keinen
Post-Treatment-Wert verifizieren. Follow-up ist ohne dokumentierte Regel
ebenfalls nicht austauschbar.

## 4. Tabellenrekonstruktion

`research_agent/verification/tables.py` liest die gespeicherten
Markdown-/Texttabellen deterministisch:

- Tabellenlabel und Caption
- mehrstufige Header-Zeilen
- Spaltenpositionen aus Einrueckung und Zellabstaenden
- Zeilenlabels und Gruppenueberschriften
- wiederholte Header nach dem Trenner
- exakte Zeichen- und Zeilenoffsets

Der bestehende JATS-Parser (`research_agent/research/jats_tables.py`) bleibt
fuer XML-Tabellen nutzbar. Der bestehende PDF-/Vision-Pfad
(`table_extractor.py`, `vision_table.py`) bleibt unveraendert; der
Vision-Adapter in `verification/pipelines.py` ist die spaetere Bruecke.

Grenze des Pilots: Die Yun-Quellen liegen als Markdown vor, nicht als
Original-PDF. Pipeline B lief daher als Layout-Geometrie, nicht als
Bildlesung. Das ist im Ergebnis ausdruecklich als `vision_used: false`
markiert.

## 5. Zwei Pfade

**Pipeline A** liest den eingefrorenen v6c-Output. Sie bekommt keine
Pipeline-B-Ausgabe und wird nicht neu ausgefuehrt.

**Pipeline B** liest ausschliesslich ICO-Spezifikation und Originaltext. Sie
erhaelt keine A-Werte. Sie waehlt Tabelle, Zeile, Armspalte und Zeitpunkt
selbst und liefert pro Feld eine eigene Evidenzzelle.

**Vision B** ist ein separater Adapter auf den vorhandenen
`VisionTableReader`. Er wird nur mit ausdruecklicher Freigabe und ohne
gemeinsame Eingabe mit A gestartet.

## 6. Vergleichsregeln

- Text: normalisierte, case-insensitive Gleichheit.
- Zaehlwerte: gleiche ganze Zahl.
- Zahlen: exakt oder `numeric_match` bei absoluter Differenz `<= 0.005`.
- Die Toleranz ist absichtlich klein und wird im Ergebnis als Regel
  gespeichert. Sie ist keine Erlaubnis, verschiedene Messwerte zu mitteln.
- Fehlende Werte werden nie durch 0, Schaetzung oder Imputation ersetzt.

Die Vergleichsstaende sind:

`match`, `numeric_match`, `mismatch`, `missing_a`, `missing_b`,
`both_missing`, `evidence_missing`, `ambiguous`.

## 7. Plausibilitaet

Harte Fehler:

- Pflichtfeld fehlt
- N ist keine positive ganze Zahl
- SD ist nicht positiv
- Ereigniszahl ist negativ oder groesser als N
- Wert ist keine endliche Zahl
- mehrere Einheiten im selben Record

Warnungen:

- SD ist sehr gross relativ zum Mittelwert
- beide Arme haben N=1
- Zeitpunkt ist nicht dokumentiert

Es gibt **keine automatische Korrektur** aufgrund einer Plausibilitaetsregel.

## 8. Status und Audit

Feldstatus: `extracted`, `cross_checked`, `verified`, `rejected`,
`unresolved`.

Recordstatus: `extracted`, `cross_checked`, `pending_review`, `verified`,
`rejected`.

`research_agent/verification/store.py` schreibt jedes Ereignis mit
`prev_hash` und `hash` in ein JSON-Journal. Eine nachtraegliche Aenderung
bricht die Kette. Menschliche Entscheidungen speichern:

- Aktion
- altes Feld (Status und Wert)
- neuen Wert
- Pruefer
- Begruendung
- Evidenz-ID
- Zeitpunkt

Ein bereits verifizierter Record verliert seine Freigabe, wenn sich
Dokument-Hash oder Extraktions-Hash aendern; alle verifizierten Felder gehen
auf `cross_checked` zurueck.

## 9. Pooling-Gate

`research_agent/meta/verified_pool.py` ist die einzige neue Schnittstelle vor
dem unveraenderten `meta.pooling.build_analysis`.

- Standard: jeder nicht verifizierte Record fuehrt zu
  `UnverifiedRecordError`.
- `allow_unverified=True` liefert die abgelehnten Zeilen separat fuer den
  Bericht, gibt sie aber **nie** an das Pooling weiter.
- Der Report kann `verification_gate` mit Input-, verifizierten und
  abgelehnten Zeilen ausweisen.

## 10. Review-Oberflaeche

`python -m research_agent.verification.review_server --state <audit.json>`
startet lokal auf `127.0.0.1:8765`.

Angezeigt werden:

- Recordstatus und Grund
- Originalzelle, Tabelle, Zeile und Spalte
- Pipeline A und B getrennt
- Vergleichsstatus
- Plausibilitaetswarnungen
- bisherige Entscheidungen

Aktionen: bestaetigen, korrigieren, "nicht berichtet", "unklar",
Record ablehnen. Ohne Pruefername wird nichts gespeichert.

Bestätigen und Korrigieren verifizieren nur mit einem vorhandenen Wert und
einer gespeicherten Evidenzzeile, die den Wert im richtigen Feld tatsächlich
enthält. Fehlt eines davon, bleibt das Feld `unresolved`. Das gilt auch dann,
wenn die Evidenz-ID zwar existiert, aber eine andere Zahl belegt.

Für jedes Feld zeigt der Server alle gespeicherten Evidenzzeilen als
Auswahlliste; die bisherige B-Evidenz bleibt sichtbar und eine passende
A-Quellzeile kann ausgewählt werden. Die Evidenzen für die sieben
Review-Records werden mit `scripts/ergaenze_review_evidenzen_20261113.py`
append-only ergänzt; das Skript verändert keine Werte oder Status.

## 11. Tests

`research_agent/tests/test_verification_system.py` deckt ab:

- fehlende Evidenz
- widerspruechliche Extraktionen
- falsche Gruppen-/Zeitpunkt-Zuordnung
- Rundungsunterschiede
- unzulaessige Statuswechsel
- manipulationssichere Audit-Kette
- Verlust der Freigabe nach Quellenaenderung
- Review-Pflichten
- Gate: keine unverifizierte Zeile erreicht `build_analysis`
- Gate prüft Wert und Evidenz erneut, nicht nur den Feldstatus
- Abschlussprüfung bezieht offene Outcome-/Zeitpunktfelder ein

## 12. Bewusste Nicht-Ziele

- Kein neues Sprachmodell als "Verifikation".
- Kein Prompt-Tuning auf dem 249er-Test.
- Keine Imputation.
- Keine automatische Zahlenkorrektur.
- Kein Umbau von `meta/pooling.py`, `report.py` oder `orchestrator.py`.
- Keine Behauptung, 100 % Sicherheit erreicht zu haben.
