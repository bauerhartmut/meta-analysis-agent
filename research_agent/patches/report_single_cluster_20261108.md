# report.py: fehlendes Intervall bei einem Cluster erklaeren (2026-11-08)

**Entscheidung:** `report.py` bleibt gitignored. Der Patch wandert nicht ins
Repo; dokumentiert und pruefbar ist seine Wirkung.

## Anlass

Befund E4f/E4g: `single_cluster_gate` (committet in
`research_agent/meta/pool_gates.py`) entfernt bei weniger als zwei
unabhaengigen Clustern die Intervalle eines Pools - HKJ, Fixed Effect und
Prediction Interval. Richtig, aber der Report druckte danach `[-, -]` ohne
Begruendung. Ein Leser sieht eine kaputte Tabelle, keinen Befund. Betroffen
waren drei von zehn Gruppen: `preeclampsia` (k = 5, M = 1), `frailty`
(k = 2, M = 1), `fisher_z` (k = 2, M = 1).

## Ankerpunkt

`research_agent/report.py`, Funktion `_meta_section`, je Gruppe direkt vor dem
`elif pooled_enough`-Zweig (Arbeitsstand: Zeilen 818 bis 835). Neuer Zweig mit
der Bedingung `pooled_enough and group.get("single_cluster")`.

## Wirkung

- Eine Textzeile statt Intervall: k Zeilen, aber nur M unabhaengige Quelle;
  der Punktschaetzer ist eine Sichtung, keine Schaetzung; es fehlt die zweite
  unabhaengige Einheit, nicht die Daten.
- Keine Zahl wird erfunden. Der Punktschaetzer bleibt stehen, weil er aus den
  Zeilen berechenbar ist.
- Ohne das Flag rendert der Report unveraendert wie vorher; der Zweig greift
  nur bei gesetztem `single_cluster`.

## Pruefung

1. `python scripts/pruefe_report_patch.py` - Exit 0, drei Dateien OK.
2. `python -m pytest research_agent/tests/test_pruefe_report_patch.py -q`.
3. Inhaltlich an einer DB-Kopie (nie an der laufenden DB):
   `preeclampsia` zeigt den Hinweis genau einmal, `MACE` (M = 3) zeigt
   weiterhin sein Intervall. Beleg:
   `data/bench/validierung/report_meta_ausschnitt_20261108.txt`.

## Lokale Sicherung

`local_patches/report_20261108.py`, identisch mit dem Arbeitsstand vom
2026-11-08 (vom Pruefskript per Byte-Vergleich bestaetigt). Wiederherstellung
durch Zurueckkopieren nach `research_agent/report.py`.

## Grenze

Bei einem frischen Klon fehlt der Hinweis, weil die Datei fehlt - das ist die
bewusst akzeptierte Folge des IP-Schutzes. Der Eintrag und das Pruefskript
machen den Zustand sichtbar: Exit 1 statt stillem Fehlen.
