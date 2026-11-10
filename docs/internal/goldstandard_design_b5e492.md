# Designprüfung b5e492

## Anlass

Das Gerüst führte `b5e492` als `parallel_rct` mit
`design_verbatim: "randomized controlled trials"`. Der Volltext ist
jedoch eine Übersichtsarbeit mit gepoolten Schätzern.

## Ankerpunkt

- Abstract: „There are 15 articles reported 20 studies, with a total of
  1,346 patients ... The findings demonstrated a notable improvement in
  depression symptoms ... [SMD = -0.82, 95% CI (-1.19, -0.45)].“
- Results: „A total of 18 studies ... a random-effects model was used to
  combine the results.“ Danach Subgruppen nach Interventionsdauer,
  Intensität und Trainingsart.

## Befund

Die Arbeit fasst 20 Studien zusammen und berichtet gepoolte SMDs. Nach
5.1 ist eine Metaanalyse über RCTs `aggregate`; `parallel_rct` wäre nur
ein RCT, der über sich selbst berichtet. Die bisherige Angabe beschrieb
die eingeschlossenen Studien, nicht das Design der Arbeit.

## Entscheidung

- `design_category`: `aggregate`
- `design_verbatim`: `"meta-analysis of randomized controlled trials"`
- `stratum`: `rct` bleibt unverändert.

## Wirkung

- `documents.json`, A und B sind konsistent.
- A enthält genau eine Zeile für den Hauptschätzer (SMD -0.82) mit
  `is_primary: false`; die Subgruppen-SMDs stehen in `notes`.
- Die Vollannotations-Checkliste führt b5e492 als `aggregate`.

## Prüfung

- `.venv/bin/python.exe scripts/pruefe_goldstandard.py --entwurf data/golden_effects/goldstandard_A.json data/golden_effects/goldstandard_B.json`
  bis 0 Fehler.
- B bleibt leer; es wird keine Effektzeile erfunden.
