# report.py: Pruefspur der Doppellesung im Bericht (2026-11-10)

**Entscheidung:** `report.py` und `meta/pooling.py` bleiben gitignored
(Kerndateien). Committet sind der Test, der Marker im Pruefskript und dieser
Eintrag.

## Anlass

Die Dedup-Regel (siehe `pooling_lesepass_dedup_20261110.md`) verwirft eine
Zweitlesung, wenn sie eine gueltige Erstlesung kopiert. Im Bericht war das
unsichtbar: verworfene Zeilen erschienen nur in der Liste "Warum Zeilen nicht
gepoolt wurden", und poolbare Zeilen aus Pass B ohne Zwilling sahen aus wie
jede andere Zeile. Der Leser konnte nicht unterscheiden, ob eine Zahl auf
einer Gegenlesung beruht oder auf einer einzelnen Lesung.

## Ankerpunkt

`research_agent/meta/pooling.py`: die Gruppe reicht `extraction_pass` je Zeile
durch (`"extraction_pass": _lesepass(row)` im `standardised`-Eintrag), damit
der Bericht zaehlen kann, ohne die Datenbank erneut zu lesen.

`research_agent/report.py`: neue Funktion `_pruefspur_counts(analysis)` und
der Abschnitt "Pruefspur: zweite Lesungen" nach der Liste der nicht gepoolten
Zeilen. Zwei Zahlen, getrennt gehalten:

- **verworfene Kopien**: `excluded`-Eintraege mit Grund "zweite Lesung ...".
  Das ist eine Doppelzaehlung, die nicht passiert ist.
- **poolbare Zeilen ohne Gegenlesung**: Zeilen in den Gruppen mit
  `extraction_pass > 1`. Sie stehen im Pool, sind aber nie gegengelesen -
  keine Doppelzaehlung, eine offene Pruefung.

Der Abschnitt erscheint nur, wenn mindestens eine der beiden Zahlen groesser
als null ist. Fehlt das Passfeld, gilt die Zeile als Erstlesung.

## Wirkung

- Der Bericht sagt jetzt, wie viele Zeilen als Pruefspur aus dem Pool fielen
  und wie viele Poolzeilen ohne Gegenprobe sind.
- Die beiden Faelle werden nicht vermischt: eine verworfene Kopie ist ein
  verhinderter Fehler, eine ungepruefte Zeile ist eine Einschraenkung.
- Die Zaehlung ist deterministisch, ohne Modellaufruf, und liest nur die
  Analyse, die der Bericht ohnehin berechnet.

## Pruefung

1. `pytest research_agent/tests/test_meta_pruefspur.py` - 4 Tests: Kopie und
   ungepruefte Zeile getrennt gezaehlt, fehlendes Passfeld als Erstlesung,
   dritte Lesung als ungepruefte Zeile, leere Analyse.
2. Report-Nachbarschaft: `test_report`, `test_report_honesty`,
   `test_meta_report`, `test_meta_lesepass_dedup`,
   `test_pruefe_report_patch`.
3. `python scripts/pruefe_report_patch.py` - Exit 0 (report.py 7 Marker,
   pooling.py 6 Marker).

## Lokale Sicherung

`local_patches/report_20261110.py` und
`local_patches/pooling_20261110_lesepass.py` (Stand vor der Aenderung).

## Grenze

Die Zaehlung bezieht sich auf die Zeilen, die `build_analysis` gesehen hat.
Zeilen, die schon vorher am Zielmass oder am Exposure-Gate scheitern, stehen
in `off_target` bzw. `excluded` und werden hier nicht als Pruefspur gezaehlt -
sie sind ohnehin nicht im Pool.
