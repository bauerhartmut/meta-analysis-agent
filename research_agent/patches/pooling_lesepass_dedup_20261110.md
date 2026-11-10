# pooling.py: nur die tragende Lesung geht in den Pool (2026-11-10)

**Entscheidung:** `pooling.py` und `extraction.py` bleiben gitignored
(Kerndateien). Committet sind die Regel als Marker im Pruefskript, der
Testfall und dieser Eintrag.

## Anlass

Der Doppelpass auf T1b und T4 (siehe
`data/bench/validierung/doppelpass_20261110.md`) hat gezeigt: Bei Einigkeit
speichert `extract` beide Paesse, `_normalize` vergibt je Zeile eine neue
`gen_id()`, und `pooling.py` verwarf bisher nur `disputed` - nicht den
Lesepass. Damit trug jeder bestaetigte Effekt zweimal in den Pool: gleiche
Zahl, gleiches SE, doppeltes Gewicht, halber Varianzanteil, zu schmales
Intervall. Bei T1b waeren das 10 Zeilen fuer 5 Effekte gewesen.

## Ankerpunkt

`research_agent/meta/pooling.py`, `standardize`, direkt nach der
`disputed`-Pruefung und vor der `rejection_reason`-Pruefung:

    try:
        lesepass = int(row.get("extraction_pass") or 1)
    except (TypeError, ValueError):
        lesepass = 1
    if lesepass > 1:
        return None, None, "", "zweite Lesung (Prüfspur, kein zweiter Effekt)"

Fehlt das Feld, gilt die Zeile als Erstlesung - aeltere Zeilen und Zeilen aus
`arm_level`/`effect_columns` bleiben unberuehrt.

`research_agent/meta/extraction.py`, `resolve_third_attempt`, im Zweig
"Zweitlesung bestaetigt": dort wird zusaetzlich
`second_row["extraction_pass"] = 1` gesetzt. Ohne diese Hebung wuerde der
Filter genau die einzige vom dritten Leser bestaetigte Zeile verwerfen, weil
sie als Pass 2 gespeichert ist. Die Erstlesung bleibt `disputed = 1` und damit
draussen; gemittelt wird nichts.

## Wirkung

- Ein Effekt erscheint hoechstens einmal im Pool, unabhaengig davon, wie oft
  er gelesen wurde.
- Die Zweitlesung bleibt als Pruefspur in `study_effects` und wird im Report
  als abgelehnte Zeile mit Grund gezaehlt, nicht stillschweigend entfernt.
- Die dritte Lesung (Klaerungshilfe) ist ebenfalls nicht poolbar; sie kann
  keinen dritten Arm erzeugen.
- Wird eine Zweitlesung bestaetigt, traegt sie allein - die widerlegte
  Erstlesung bleibt strittig und draussen.
- Nebenwirkung, bewusst: Eine Zeile, die nur Pass B liest und die Pass A
  nicht hat, geht nicht in den Pool. Sie ist nicht gegengelesen; die
  konservative Regel ist gewollt.
- `screening.py` zaehlt `poolable_primary` ueber dieselbe Funktion und wird
  damit ebenfalls korrekt.

## Pruefung

1. `pytest research_agent/tests/test_meta_lesepass_dedup.py` - 9 Tests:
   Pass 2 und Pass 3 nicht poolbar, Pass 1 und fehlendes Feld poolbar,
   Doppellesung ergibt k = 1 mit einem Ablehnungsgrund, zwei verschiedene
   Studien bleiben k = 2, bestaetigte Zweitlesung wird zur tragenden Lesung,
   bestaetigte Erstlesung bleibt allein, ungeklaert bleibt beides draussen.
2. Volle Nachbarschaft: `test_meta_pooling`, `test_meta_extraction`,
   `test_meta_quality_gates`, `test_meta_targets`, `test_meta_cohort`,
   `test_rve_weights`, `test_pooling_reference`, `test_pruefe_report_patch` -
   zusammen 175 passed.
3. `python scripts/pruefe_report_patch.py` - Exit 0.

## Lokale Sicherung

`local_patches/pooling_20261110.py`, `local_patches/extraction_20261110_lesepass.py`
(Stand vor der Aenderung).

## Grenze

Die Regel ist mit 9 Tests und der Nachbarschaft belegt, aber **nicht** in
einem echten Lauf mit `_store` und anschliessendem Pooling gemessen. Wer die
Wirkung auf ein echtes Ergebnis sehen will, braucht einen Lauf, der speichert
und danach `build_analysis` aufruft - das ist der naechste Schritt, nicht
dieser.
