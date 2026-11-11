# Annotationsregeln und Prompts

Dieses Verzeichnis dokumentiert, was die drei öffentlichen Quellen tatsächlich
zur Annotation veröffentlichen. Es enthält keine nachträglich erfundenen
Regeln und keine aus Testdaten abgeleiteten Prompt-Anpassungen.

## Yun et al. 2024

- `yun_annotation_schema.md`: das in Paper und Repository dokumentierte
  Extraktionsschema.
- Menschliche Annotation Guidelines als separates Dokument: **nicht
  veröffentlicht**.
- Die YAML-Dateien unter
  `raw_data/yun_llm_meta_analysis/evaluation/templates/` sind
  **Modell-Prompts**, keine menschlichen Annotationsinstruktionen.
- Auswertungscode: `evaluation/run_task.py`,
  `evaluation/evaluate_output.py`, `evaluation/calculate_metrics.py`.

## Evidence Inference 2.0

- `evidence_inference_roles.md`: Rollen von Prompt-Generator, Annotator und
  Verifier sowie die verfügbaren individuellen Labels.
- Vollständige Prozessbeschreibung im Rohrepo:
  `raw_data/evidence_inference/README.annotation_process.md`.
- Spaltenbeschreibung:
  `raw_data/evidence_inference/annotations/README.md`.

## DTA-Korpus

- `dta_scope.md`: diagnostische 2x2-Extraktion, keine kontinuierlichen
  Interventions-/Kontrollwerte.
- Readme im Archiv:
  `raw_data/dta_cochrane/CL145_open_set_20181101/readme.txt`.

## Grundsatz

Die drei Ebenen werden strikt getrennt:

1. **Publizierte menschliche Referenzannotation** (Yun, DTA),
2. **individuelle menschliche Annotationen** (Evidence Inference),
3. **adjudizierte bzw. konsolidierte Endannotation** (Yun nach Konsens,
   DTA nach Cochrane-Extraktion).

Nur Ebene 2 erlaubt eine Aussage über Inter-Rater-Reliabilität. Yun und DTA
liefern Ebenen 1/3, nicht die unabhängigen Einzelurteile.
