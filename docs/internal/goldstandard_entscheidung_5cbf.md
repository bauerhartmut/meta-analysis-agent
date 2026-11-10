# Entscheidung 5cbf: Dosis-Wirkungs-Peak

## Frage

Ist der Peak bei ca. 740 METs-min/Woche (Hedges’ g = -0.44, 95% CrI
-0.27 to -0.73) eine eigene Effektzeile oder nur der gepoolte
Hauptschätzer (g = -0.28, 95% CrI -0.43 to -0.13)?

## Ankerpunkt

- Zeile 31: „The Bayesian meta-analysis revealed that aerobic exercise
  intervention significantly improved depression symptoms in adolescents
  compared to control groups, demonstrating a small effect size (Hedges’
  g = -0.28, 95% credible interval (CrI): -0.43 to -0.13). The dose-response
  analysis revealed a significant nonlinear relationship … peaking at
  approximately 740 METs-min/week (Hedges’ g = -0.44, 95% CrI: -0.27 to
  -0.73) …“.
- Zeile 35: „It is crucial to emphasize that this is a point estimate
  derived from the available data, and its precision is reflected in the
  associated credible intervals.“
- Zeile 221: „The sensitivity analysis (Fig. 6) showed that after excluding
  high-risk studies (2 of the 12 studies), the re-estimated overall effect
  size was 0.29 (95% CI [0.21, 0.38]), while the main estimate remained
  0.28 …“.

## Regel

- Abschnitt 3: Eine Zeile = eine geschätzte Effektgröße für genau eine
  Kombination aus Outcome, Vergleich, Zeitpunkt, Adjustierung und Population.
  Die Dosis ist keines dieser Merkmale.
- 5.8: Der gepoolte Schätzer ist **eine** Zeile mit `is_primary: false`,
  `design_category: aggregate`.
- 5.9: Je Arm eine Zeile, wenn ein eigener Effekt mit Unsicherheit berichtet
  wird; ist nur ein gemeinsamer Effekt über Arme berichtet, ist es eine Zeile
  mit `notes`.
- 5.11 analog: Eine Spannweite oder Kurve ist keine einzelne Effektzeile;
  nur aufgelöste Punkte mit eigenem Zeitpunkt sind Zeilen.

## Entscheidung

Nur der Hauptschätzer ist eine Effektzeile:

- `effect_type`: `g`
- `effect`: -0.28
- `ci_low`: -0.43
- `ci_high`: -0.13
- `is_primary`: false
- `design_category`: `aggregate`
- `notes`: „Dosis-Wirkungs-Peak bei ca. 740 METs-min/Woche: g = -0.44
  (95% CrI -0.27 to -0.73, Reihenfolge wie berichtet);
  Sensitivitätsanalyse ohne 2 Hochrisikostudien: 0.29 (95% CI 0.21-0.38);
  keine eigenen Zeilen.“

## Begründung

- Der Peak ist eine Modellvorhersage auf derselben Dosis-Wirkungs-Kurve, kein
  unabhängiger Vergleich. Eine eigene Zeile würde dieselben 12 Studien
  doppelt zählen.
- Das berichtete CrI ist ungeordnet (-0.27 bis -0.73). Als Zeile müsste man
  die Grenzen umdrehen, was die Anleitung (keine Umrechnung) nicht erlaubt.
- Die Sensitivitätsanalyse betrifft dieselbe Kombination nach Ausschluss von
  zwei Studien; sie ist kein eigener Vergleich und bleibt in `notes`.

## Wirkung

- A/B: 5cbf bekommt genau eine Zeile, nicht zwei oder drei.
- Die Vollannotations-Checkliste führt 5cbf unter „5.8 gepoolt“; die
  Erklärung nennt Peak und Sensitivitätsanalyse als `notes`.
- Die Pipeline hat 2 Zeilen; sie ist kein Goldstandard. Der Abgleich wird den
  Peak gegebenenfalls als FP zählen; das ist beabsichtigt.

## Prüfung

- A und B bleiben leer; es wird keine Effektzeile erfunden.
- `python scripts/pruefe_goldstandard.py --entwurf` für A und B: Exit 0,
  30 offen.
- Die Anleitung ist v1.2; 5.9 nennt Peak und Sensitivitätsanalyse
  ausdrücklich als `notes`.
