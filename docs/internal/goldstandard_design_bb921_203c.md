# Designprüfung bb921 und 203c

## bb9218735f: `parallel_rct` bestätigt

**Anlass:** Prüfauftrag nach der Korrektur von 7111ea.

**Ankerpunkt:**
- Zeile 81: „A multicenter, randomized, placebo-controlled clinical trial of
  2 dose formulations of oral melatonin … Subjects with Alzheimer’s disease
  and nighttime sleep disturbance were randomly assigned to 1 of 3 treatment
  groups: placebo, 2.5-mg slow-release melatonin, or 10-mg melatonin.“
- Zeile 105: „This was a multicenter, randomized, placebo-controlled study …
  Subjects were randomly assigned (blocked by study site) in a double-blind
  fashion to 1 of 3 groups: placebo (PLA), 2.5 mg SR melatonin (ML 2.5SR),
  and 10 mg immediate-release melatonin (ML 10).“

**Befund:** randomisierte, parallele Gruppen mit Placebo; keine
Crossover- oder Within-Subject-Anlage. Die Angaben `design_category:
parallel_rct`, `stratum: rct` und `design_verbatim: "randomized,
placebo-controlled study"` sind korrekt.

**Entscheidung:** keine Änderung.

## 203c831dbe: `aggregate` bestätigt, `design_verbatim` präzisiert

**Anlass:** Prüfauftrag.

**Ankerpunkt:**
- Titel: „… A Systematic Review and Meta-Analysis.“
- Abstract: „This systematic review and meta-analysis evaluated the
  association between post-diagnosis MD adherence and outcomes of cancer
  recurrence and CRF …“
- Zeile 123: „This systematic review and meta-analysis was conducted in
  accordance with the PRISMA 2020 guidelines …“
- Gepoolte Schätzer: HR 0,83 (95 % CI 0,70–0,99); MD 0,29 (95 % CI −0,58
  bis 1,16).

**Befund:** Die Arbeit ist eine systematische Übersicht mit Metaanalyse.
`design_category: aggregate` und `stratum: aggregate` sind korrekt.
`design_verbatim: "Prospective cohort studies (meta-analysis)"` beschreibt
die eingeschlossenen Studien, nicht das Design der Arbeit.

**Entscheidung:** `design_verbatim` = `"systematic review and meta-analysis"`
(wörtlich aus Titel, Abstract und Zeile 123; ebenso im geprüften Beispiel
`data/golden_effects/example_annotation.json`). `design_category` und
`stratum` bleiben unverändert.

## Wirkung

- Die Designangabe ist in `documents.json`, A und B konsistent.
- Das Arbeitsblatt 203c zeigt jetzt „Design laut Dokument: systematic review
  and meta-analysis“.
- 7111ea bleibt `aggregate` / `narrative review`; bb921 bleibt
  `parallel_rct` / `rct`.

## Prüfung

- JSON-Check: bb921 `parallel_rct` / `rct`; 203c `aggregate` / `aggregate` /
  `systematic review and meta-analysis`.
- `python scripts/pruefe_goldstandard.py --entwurf` für A und B: Exit 0.
- A und B bleiben leer; es wird keine Effektzeile erfunden.
