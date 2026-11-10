# pooling.py: Doppellesung zaehlt einmal (2026-11-10)

**Entscheidung:** `pooling.py` und `extraction.py` bleiben gitignored
(Kerndateien). Committet sind die Regel als Marker im Pruefskript, der
Testfall, das Messskript und dieser Eintrag.

## Anlass

Der Doppelpass auf T1b und T4 (siehe
`data/bench/validierung/doppelpass_20261110.md`) zeigte: Bei Einigkeit
speichert `extract` beide Paesse, `_normalize` vergibt je Zeile eine neue
`gen_id()`, und das Pooling verwarf bisher nur `disputed` - nicht den
Lesepass. Zwei identische Zeilen tragen dann dasselbe Gewicht zweimal.

## Erster Versuch und warum er verworfen wurde

Die erste Fassung wies in `standardize` jede Zeile mit
`extraction_pass > 1` ab. Die Messung (`scripts/messe_lesepass_dedup_20261110.py`,
Bericht `data/bench/validierung/lesepass_filter_20261110.md`) hat das
widerlegt: Von 209 Zweitlesungen in acht Themen-DBs haben 45 **keinen**
Zwilling in Pass 1 - weder gleicher Wert, gleiche Quote noch gleicher
Textschluessel. Das sind eigenstaendige Aussagen aus Pass B, keine
Doppelzaehlung; der pauschale Filter haette sie aus dem Pool geworfen
(Exercise-DB: k 24 -> 18, Mediterran: 26 -> 15). Ein pauschaler
Lesepass-Filter ist deshalb falsch.

## Ankerpunkt

`research_agent/meta/pooling.py`, neue Funktion `_drop_zweitlesungen`,
aufgerufen am Anfang von `build_analysis`:

- Zwilling ist eine Zeile, die in **Wert** (Quelle, Effekt auf 9 Stellen,
  SE) oder **Quote** (Quelle, normalisierter Zitattext) mit einer
  Erstlesung uebereinstimmt.
- Nur gegen **gueltige** Erstlesungen: eine Zeile mit `disputed != 0` ist
  kein Zwilling. Sonst wuerde die vom dritten Leser bestaetigte Zweitlesung
  als Kopie der widerlegten Erstlesung verschwinden.
- Verworfen wird nur `extraction_pass > 1`. Die Erstlesung bleibt, die
  Zweitlesung zaehlt im Report als abgelehnte Zeile mit Grund
  "zweite Lesung (Zwilling der Erstlesung)".
- Fehlt das Feld, gilt die Zeile als Erstlesung; aeltere Zeilen und Zeilen
  aus `arm_level`/`effect_columns` bleiben unberuehrt.

`research_agent/meta/extraction.py` bleibt unveraendert: Die zwischenzeitlich
eingebaute Hebung einer bestaetigten Zweitlesung auf Pass 1 wurde
zurueckgenommen. Sie war mit dem Zwillingstest unnoetig und haette die
Herkunft der Zeile verfaelscht.

## Wirkung, gemessen

Datenlage (48 DBs, 7897 Zeilen): 7477 Zeilen Pass 1, 412 Pass 2, 8 Pass 3;
15 DBs enthalten Zeilen ueber Pass 1.

Mechanismusprobe an echten Zeilen (`direct_label2.db`, 132 Gruppen mit k >= 2,
je Zeile eine zusaetzliche Zweitlesung):

| | k-Summe | KI-Breite (Median) |
|---|---:|---:|
| Referenz | 830 | - |
| ohne Regel | 1660 | 62,2 % enger (max. 89,3 %) |
| mit Regel | 830 | wie Referenz |

Hauptpfad `build_analysis` auf den echten Zeilen: 209 Zweitlesungen in acht
Themen-DBs, davon verwirft die Regel **3** zusaetzlich (alle in der
Exercise-DB, k 24 -> 21). In den uebrigen DBs aendert sich nichts, weil
`_collapse_same_study` die Kopien dort schon vorher abfaengt. Der Gewinn ist
also nicht "viele Zeilen weg", sondern: die Doppelzaehlung ist jetzt explizit
und begruendet statt eine Nebenwirkung der Kollaps-Reihenfolge.

## Pruefung

1. `pytest research_agent/tests/test_meta_lesepass_dedup.py` - 9 Tests:
   Zweitlesung ohne Zwilling bleibt poolbar, Wert-Zwilling und Zitat-Zwilling
   werden verworfen, dritte Lesung mit Zwilling ebenfalls, zwei Studien
   bleiben k = 2, `standardize` filtert nicht mehr, fehlendes Passfeld gilt
   als Erstlesung, widerlegte Erstlesung ist kein Zwilling, zwei strittige
   Zeilen ergeben keinen Pool.
2. Nachbarschaft: `test_meta_pooling`, `test_meta_extraction`,
   `test_meta_quality_gates`, `test_meta_targets`, `test_meta_cohort`,
   `test_rve_weights`, `test_pooling_reference`, `test_pruefe_report_patch` -
   zusammen 175 passed.
3. `python scripts/pruefe_report_patch.py` - Exit 0 (pooling.py 4 Marker,
   darunter `_drop_zweitlesungen`).
4. `python scripts/messe_lesepass_dedup_20261110.py` - Exit 0, 0
   Modellaufrufe, 1 uebersprungene DB ohne `study_effects`.

## Lokale Sicherung

`local_patches/pooling_20261110.py` und
`local_patches/extraction_20261110_lesepass.py` (Stand vor der Aenderung).

## Grenzen

- 45 Zweitlesungen ohne Zwilling bleiben poolbar. Sie sind nicht doppelt,
  aber auch nicht gegengelesen - das ist ein Qualitaetsthema fuer Gate und
  Report, nicht fuer diese Regel.
- Der Zitat-Zwilling vergleicht die ersten 200 normalisierten Zeichen. Zwei
  verschiedene Arme mit identischem Zitattext werden als Kopie behandelt;
  das ist die konservative Richtung (eine Zeile faellt raus, keine kommt
  doppelt rein).
- Die Regel wirkt in `build_analysis`. Skripte, die `standardize` und `pool`
  direkt aufrufen, umgehen sie - dort muss der Aufrufer die Zeilen selbst
  deduplizieren.

## Nachtrag: Schluessel ohne Beleg (gleicher Tag)

Die Klassifikation der 45 Pass-B-Zeilen ohne Zwilling hat einen Fehler in den
Zwilling-Schluesseln aufgedeckt. `_wert_zwilling` gab fuer eine Zeile ohne
Effekt `("", None, None)` zurueck und `_zitat_zwilling` fuer eine Zeile ohne
Quote `("", "")` - beides fuer alle solche Zeilen identisch. Damit galt eine
Zweitlesung ohne Effekt als Kopie jeder Erstlesung ohne Effekt, und eine ohne
Quote als Kopie jeder Erstlesung ohne Quote, jeweils unabhaengig von der Quelle.

Wirkung: Die Menge der Zeilen "ohne Zwilling" war zu klein, weil beleglose
Zeilen faelschlich als Kopien zaehlten. Auf den Hauptpfad hatte der Fehler
keine Wirkung - die drei zusaetzlich verworfenen Zeilen in der Exercise-DB
sind echte Wert- oder Zitat-Zwillinge (k bleibt 24 -> 21, abgelehnt 105 -> 108).

Behoben: Beide Schluessel tragen ohne Beleg die Zeilen-ID und sind damit nur
mit sich selbst gleich; dann entscheidet allein der jeweils andere Vergleich.
Zwei Tests halten das fest (Zeile ohne Effekt, Zeile ohne Quote), 11 Tests im
Modul gruen. Nach der Korrektur ergibt die Klassifikation exakt 45 Zeilen.
