# Designprüfung 5cbf

## 5cbf039f22: `parallel_rct` → `aggregate`

**Anlass:** Prüfauftrag vor der Vollannotation. `documents.json`, A und B
führten die Arbeit in der Schicht `aggregate`, aber mit
`design_category: parallel_rct` und
`design_verbatim: "Randomized controlled trial (meta-analysis of 12 RCTs)"`.

**Ankerpunkt:**
- Titel, Zeile 1: „Aerobic exercise for depression symptoms in adolescents:
  a systematic review and dose-response meta-analysis“.
- Abstract, Zeile 29: „Inclusion criteria were strictly defined to include
  randomized controlled trials (RCTs) … Data synthesis was performed using
  a Bayesian random-effects model …“.
- Zeile 31: „A total of 12 studies involving 723 participants were included.
  The Bayesian meta-analysis revealed … Hedges’ g = -0.28, 95% credible
  interval (CrI): -0.43 to -0.13.“
- Zeile 89: „This study was conducted according to the Preferred Reporting
  Items for Systematic Reviews and Meta-Analyses (PRISMA) statement …“.
- Zeile 115: „Only randomized controlled trials (RCTs) were included.“ Das
  beschreibt die Einschlusskriterien, nicht das Design der Arbeit.

**Befund:** Die Arbeit ist eine systematische Übersicht mit
Dosis-Wirkungs-Metaanalyse über 12 RCTs. Nach 5.1 ist eine Metaanalyse über
RCTs `aggregate`; `parallel_rct` wäre nur ein RCT, der über sich selbst
berichtet. Die bisherige Angabe beschrieb die eingeschlossenen Studien,
nicht das Design der Arbeit.

**Entscheidung:** `design_category` = `aggregate`;
`design_verbatim` = `"systematic review and dose-response meta-analysis"`
(wörtlich aus Titel und Abstract). `stratum: aggregate` bleibt unverändert.

**Wirkung:**
- `documents.json`, A und B sind konsistent.
- Das Arbeitsblatt 5cbf zeigt „Schicht: aggregate | Design: aggregate“ und
  „Design laut Dokument: systematic review and dose-response meta-analysis“.
- Die Vollannotations-Checkliste führt 5cbf unter „5.8 gepoolt“ statt
  „Design“; der Prüfpunkt verlangt nur die gepoolten Schätzer mit
  `is_primary: false`.

**Prüfung:**
- JSON-Check: 5cbf in `documents.json`, A und B: `aggregate` / `aggregate` /
  `systematic review and dose-response meta-analysis`.
- `python scripts/pruefe_goldstandard.py --entwurf` für A und B: Exit 0,
  30 offen.
- A und B bleiben leer; es wird keine Effektzeile erfunden.
