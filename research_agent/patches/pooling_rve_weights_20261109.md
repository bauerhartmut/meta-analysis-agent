# pooling.py: pool_rve mit Random-Effects-Gewichten (2026-11-09)

**Entscheidung:** `pooling.py` bleibt gitignored (Kerndatei). Die Mathematik
ist committet (`research_agent/meta/rve_weights.py`), lokal ist nur die
Verdrahtung - derselbe Schnitt wie bei `pool_gates.py`.

## Anlass

E4f hat RVE (Fixed Effect, `w = 1/v`) gegen HKJ (Random Effects,
`w = 1/(v + tau2)`) gestellt und dabei Modell- und Cluster-Effekt vermischt.
MACE war der Einzelfall: RVE 1,137 gegen HKJ 0,624, Faktor 1,82, ohne
Trennung. Die Behauptung "Scheinpraezision" war damit nicht belegt.

## Ankerpunkt

`research_agent/meta/pooling.py`, Funktion `pool_rve`:

- Signatur um `weights="fixed"` und `tau2_method="dl"` erweitert.
- Neuer Zweig `weights="random"` nach der Clusterbildung und vor den
  Fixed-Effect-Gewichten: `fe_theta` aus `1/v`, dann tau2 ueber
  `_tau2_dersimonian_laird` (oder `_tau2_reml`), dann Aufruf von
  `rve_weights.random_effects_rve` mit denselben Zeilen.
- `build_analysis` setzt zusaetzlich `analysis["rve_re"]`. Der Report liest
  weiterhin `rve`; das Gate bleibt unveraendert.

## Wirkung

- Default `weights="fixed"`: Verhalten und Rueckgabe unveraendert, alle
  bestehenden Tests gruen.
- `weights="random"`: Punkt und Sandwich mit `1/(v + tau2)`, CR0 mit
  `M/(M-1)` und t auf `M-1` df. tau2 steht in beiden, damit die
  CR0-Identitaet gilt.

## Pruefung

1. `pytest research_agent/tests/test_rve_weights.py
   research_agent/tests/test_meta_pooling.py
   research_agent/tests/test_pool_gates.py -q` - 70 passed.
2. `python scripts/messe_rve_modell.py` - 10 Gruppen, RVE-RE bei 7
   verfuegbar; Ergebnis in `data/bench/validierung/e4i_rve_modell_20261108.*`.
3. `python scripts/pruefe_report_patch.py` - Exit 0 (Marker in `pooling.py`
   erweitert, damit die Verdrahtung mitgeprueft wird).

## Lokale Sicherung

`local_patches/pooling_20261109.py`.

## Grenze

tau2 wird aus den Zeilen vor dem Kollaps geschaetzt, HKJ schaetzt es aus den
kollabierten Zeilen. Der Vergleich ist deshalb eine Annaeherung an "dasselbe
Modell auf demselben Material", kein exakter Modellvergleich.
