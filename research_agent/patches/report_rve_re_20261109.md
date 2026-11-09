# report.py: RVE mit Random-Effects-Gewichten als zweite Zeile (2026-11-09)

**Entscheidung:** `report.py` bleibt gitignored. Wie beim M=1-Hinweis ist nur
die Wirkung dokumentiert und pruefbar, nicht der Code.

## Anlass

E4i hat gemessen, dass bei MACE die gesamte RVE-Verbreiterung (1,137 gegen
HKJ 0,624) Cluster-Effekt ist: tau2 = 0 in beiden Rechnungen. Der Report zeigte
davon nichts - er nannte die RVE-Breite und liess offen, wie viel davon Modell
ist. Die Messung lag nur in `data/bench/validierung/`.

## Ankerpunkt

`research_agent/report.py`, Funktion `_meta_section`, direkt nach dem
RVE-Block (`elif rve and rve.get("reason")`), gleiche Ebene wie dieser.
Neuer Block liest `group["rve_re"]`.

## Wirkung

Zweite Zeile je Gruppe, wenn `rve` und `rve_re` verfuegbar sind:

- Punkt und Intervall mit Random-Effects-Gewichten.
- Ist die Breite innerhalb 0,5 Prozent gleich der Fixed-Effect-Variante, sagt
  der Text: tau2 = 0, der Unterschied ist allein die Cluster-Korrektur.
- Sonst: Faktor zur FE-Variante, ausdruecklich als reiner Modellwechsel
  gekennzeichnet; die Verbreiterung gegenueber dem naiven Intervall enthaelt
  zusaetzlich Cluster-Korrektur und die andere Zeilenbasis.

Nachtrag (2026-11-09, E4j): Die erste Fassung sagte "der restliche Teil kommt
aus der Cluster-Korrektur". Das ist bei `incident CVD` falsch: Cluster 1,49
und Duplikation 0,78 heben sich teilweise auf, die Summe ist 1,17. Der Text
nennt die drei Anteile jetzt nicht mehr als Kausalkette.

Fehlt `rve_re` (aeltere Analysen), rendert der Report unveraendert.

## Pruefung

1. `python scripts/zeige_rve_im_report.py` - rendert den Abschnitt an einer
   DB-Kopie und druckt die RVE-Zeilen.
2. `python scripts/pruefe_report_patch.py` - Exit 0, Marker `rve_re` in
   `report.py`.
3. Inhaltlich: MACE zeigt zwei Zeilen mit identischer Breite und dem Satz
   "reiner Cluster-Effekt"; `preeclampsia` (M = 1) zeigt keine RVE-Zeile.

## Lokale Sicherung

`local_patches/report_20261109.py`.

## Grenze

Der Report liest `rve_re` nur, wenn die Analyse es mitbringt; der Pfad laeuft
ueber `build_analysis` in `pooling.py` (Patch-Eintrag
`pooling_rve_weights_20261109.md`). Beide Patches gehoeren zusammen.
