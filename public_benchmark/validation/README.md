# Validierung

## Inhalt

- `checksums.sha256`: SHA-256 für die beiden Archive, die
  Yun-Referenzdateien, die offiziellen Evidence-Inference-CSV-Dateien, die
  DTA-Dateien sowie alle 120 Yun-Markdown- und 120 Yun-XML-Texte.
- `yun_sample_check.md`: manuelle Prüfung von fünf Yun-Records gegen die
  mitgelieferten Texte.

## Prüfprinzip

- Rohdaten wurden nicht verändert.
- Git-Repositories sind zusätzlich über ihren Commit-SHA gepinnt:
  - Yun: `1bc768d4d098c727c9866eeff909297c38a3e84c`
  - Evidence Inference: `a661e8c14f973398380c8865cf2f27a535aaaf6d`
- Archive sind über SHA-256 gepinnt; damit ist auch ihr gesamter Inhalt
  reproduzierbar.
- `null` in der Projektion bedeutet „nicht berichtet“, nicht „null“ und
  nicht „geschätzt“.

## Grenzen

- Kein vollständiges Audit aller 699 Yun-Records.
- Keine Modellvorhersagen und keine Genauigkeitsmessung; dieser Schritt ist
  reine Dateninventur.
- Keine Prüfung der individuellen PMC-Lizenz jedes Artikels. Die
  Yun-XML-Auszüge enthalten keine Lizenzmetadaten.
- Keine unabhängige Zweitannotation und kein B-Rücklauf; A/B bleiben
  unverändert.
