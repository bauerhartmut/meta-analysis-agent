# Designprüfung fb484

## fb484d488b: `parallel_rct` → `aggregate`

**Anlass:** Prüfung der neun Kalibrierungsdokumente vor der Annotation.

**Ankerpunkt:**
- Titel: „The effect of exercise on depressive symptoms in multiple sclerosis
  based on a meta-analysis and critical review of the literature“.
- Abstract, Zeile 39: „The purpose of this study was to perform a systematic
  review of the literature on the effects of exercise on depressive symptoms
  in patients with multiple sclerosis (MS), as well as to apply
  meta-analytical procedures to the results.“
- Abstract: „Fifteen randomized controlled trial studies were identified
  including a total of 331 exercising subjects and 260 controls. … The
  meta-analysis included 12 studies reflecting a total of 476 subjects. The
  standardized mean difference across studies was g = -0.37, 95% confidence
  interval (-0.56; -0.17) …“.

**Befund:** Die Arbeit ist eine systematische Übersicht mit Metaanalyse über
15 RCTs (12 in der gepoolten Analyse). Nach 5.1 ist eine Metaanalyse über
RCTs `aggregate`; `parallel_rct` wäre nur ein einzelner RCT.

**Entscheidung:** `design_category` = `aggregate`; `design_verbatim` bleibt
„meta-analysis of randomized controlled trials“ (bereits korrekt);
`stratum: rct` bleibt als Auswahlschicht. Der gepoolte SMD ist eine Zeile
mit `is_primary: false`.

**Wirkung:**
- `documents.json`, A und B sind konsistent.
- Das Arbeitsblatt fb484 zeigt „Schicht: rct | Design: aggregate“.
- Die Vollannotations-Checkliste und das Kalibrierungs-Arbeitsblatt führen
  fb484 unter „5.8 gepoolt“.

**Prüfung:**
- JSON-Check: fb484 in `documents.json`, A und B: `aggregate` / `rct` /
  „meta-analysis of randomized controlled trials“.
- `python scripts/pruefe_goldstandard.py --entwurf` für A und B: Exit 0,
  30 offen.
- A und B bleiben leer; es wird keine Effektzeile erfunden.
