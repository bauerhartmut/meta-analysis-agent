# extraction.py: Effekt-Prompt als effects-Huelle (2026-11-10)

**Entscheidung:** `extraction.py` und `llm/engine.py` bleiben gitignored
(Kerndateien). Committet sind Prompt-Anker im Pruefskript, Test-Anpassung,
Patch-Eintrag und der Messlauf.

## Anlass

Der Lauf ueber neun Volltexte ergab fuer **jedes** Dokument genau eine
Effektzeile, keine mit SE. Die gesicherte Rohantwort zeigte warum: Das Modell
liefert ein flaches JSON-Objekt mit 18 Feldern, kein Array. Ursache ist ein
Widerspruch im Aufbau - der Systemprompt verlangte "Return a JSON array",
`chat_json` sendet aber `response_format: json_object`, und ein nacktes
Top-Level-Array ist dort nicht erlaubt. Das Modell liefert deshalb ein Objekt
und waehlt den ersten Effekt.

## Ankerpunkt

`research_agent/meta/extraction.py`, `EffectExtractor._messages`, Ende des
Systemprompts (vorher zwei Zeilen):

- Die Leerform heisst jetzt `{"effects": []}` statt "an empty array []".
- Danach statt "Return a JSON array with: <Felder>." die Anweisung
  "Answer with ONE JSON object of the form {"effects": [...]} - the array
  holds one object per row; each element has: <Felder>."
- Die Feldliste und ihre Reihenfolge (`effect_first`/`se_first`) sind
  unveraendert; nur der Rahmen um sie ist neu.

`research_agent/llm/engine.py`, `_LIST_ENVELOPE_KEYS`: `effects`,
`effect_rows` und `rows` stehen jetzt **vor** den bisherigen Tasten. Sie
greifen nur, wenn eine Antwort mehrere Listenwerte traegt - dann gewinnt die
Effektliste statt `[result]`.

## Wirkung

- Der Prompt passt zum erzwungenen `json_object`; das Modell kann die Huelle
  jetzt bilden, statt ein Einzelobjekt zu waehlen.
- `unwrap_json_list` entpackt die Huelle ohne weitere Aenderung
  (`len(list_values) == 1`).
- Responses mit zwei Listenwerten (`effects` plus z. B. `notes`) landen nicht
  mehr in einer Pseudo-Zeile.
- Kein Eingriff in `_normalize`, `check_plausibility` oder die Feldbedeutung.
- Ohne Backend-Aufruf ist das Verhalten nicht messbar; die Gegenprobe steht
  unten.

## Pruefung

1. `pytest research_agent/tests/test_meta_extraction.py
   research_agent/tests/test_llm_engine.py -q` - 90 passed (der Testanker in
   `test_meta_extraction.py` wurde auf den neuen Wortlaut gezogen, die
   Assertions sind unveraendert).
2. `python scripts/pruefe_report_patch.py` - Exit 0, extraction.py 3 Marker,
   engine.py 1 Marker.
3. `python scripts/pruefe_effekt_huellen_20261110.py` - zwei Dokumente:
   T1b 5 Zeilen / 5 mit SE / beide Sollwerte getroffen, T4 13 Items / 6 mit
   SE / Sollwert getroffen. Ergebnis in
   `data/bench/validierung/effekt_huellen_20261110.*`.

## Lokale Sicherung

`local_patches/extraction_20261110.py`, `local_patches/engine_20261110.py`
(Stand vor der Aenderung).

## Grenze

Ein Lauf je Dokument bei `temperature=0.2`, `double_pass=False`, ohne
Persistenz. Die Huelle behebt das Ein-Objekt-Problem; ob der zweite Leser und
der dritte Klaerer danach vollstaendig arbeiten, ist nicht gemessen.
