# Designzuordnung 7111ea: narrative Übersicht statt Kohorte

## Anlass

`documents.json` und die Gerüste A/B führten `7111ea` als `observational`
mit `design_verbatim: "Prospective multicenter cohort"`. Der Volltext
widerspricht dem.

## Ankerpunkt

`data/fulltext/7111ea978757a185d44ea9de90b453c3.txt`, Zeilen 372-376:

> This narrative review was conducted to synthesize and analyze the
> existing literature on the Mediterranean diet and its role in
> preeclampsia prevention. While we followed a structured approach to
> literature search and selection, this review was not conducted according
> to PRISMA guidelines, as it is not a systematic review or meta-analysis.

Zeile 446: „The literature search yielded 12 studies that met our inclusion
criteria“ — die Studien werden narrativ zusammengefasst. Ein eigener
gepoolter Schätzer wird nicht berichtet.

## Entscheidung

- `design_verbatim`: `"narrative review"` (wörtlich aus dem Volltext).
- `design_category`: `aggregate` (Übersichtsarbeit, Anleitung 5.1 und 5.8).
- `stratum`: bleibt `cohort`. Die Schicht ist die Auswahlschicht, aus der
  das Dokument stammt; sie ist nicht das Design.
- `expected_effects`: bleibt `null`. Die Übersicht berichtet keinen eigenen
  gepoolten Schätzer; Einzelstudien werden nach 5.8 nicht übernommen.
- Für die Annotation: Wenn kein eigener gepoolter Schätzer vorliegt, ist
  `effects: []` mit `no_effect_reason` die richtige Abgabe — nicht die
  Übernahme von Einzelstudien aus Tabelle 1.

## Wirkung

- Die Designangabe ist in `documents.json`, A und B konsistent.
- Die Stratifikationszählung bleibt bei 7 Kohorten; `aggregate` ist hier
  eine Designkategorie, keine Schicht.
- Der Probelauf prüft damit einen echten Übersichtsfall, nicht eine
  verkleidete Kohorte.

## Prüfung

- `python scripts/pruefe_goldstandard.py --entwurf` muss Exit 0 liefern.
- Arbeitsblatt 7111ea wird neu erzeugt und zeigt `aggregate` /
  `narrative review`.
- A und B bleiben leer; es wird keine Effektzeile erfunden.
