# Validierung

## Inhalt

- `checksums.sha256`: SHA-256 für die beiden Archive, die
  Yun-Referenzdateien, die offiziellen Evidence-Inference-CSV-Dateien, die
  DTA-Dateien sowie alle 120 Yun-Markdown- und 120 Yun-XML-Texte.
- `yun_sample_check.md`: manuelle Prüfung von fünf Yun-Records gegen die
  mitgelieferten Texte.
- `yun_audit_sample.json`: Auswahl der 15 kontinuierlichen und 15 binären
  Records (Seed `20261111`) sowie die drei Problemfälle.
- `yun_audit_results.json`: Recordbefunde, Feldzahlen, Status und Quoten des
  Audits.
- `yun_audit_30.md`: Auditbericht mit Methodik, Recordtabelle, Fehlerquoten,
  Problemfällen und Empfehlung.
- `yun_audit_410.md`: Vollaudit aller 410 streng vollständigen Records.
- `yun_audit_410.jsonl`: kuratierte Referenz mit Auditstatus, Werten und
  Korrektur; 275 von 410 Records sind für C1 nutzbar.
- `yun_audit_410_summary.json`: Zählungen nach Status, Outcome-Typ und
  Ausschlussgrund.
- `c1_freeze_manifest.json`: SHA-256, Größen und Splitzahlen des
  eingefrorenen 275er-C1-Datensatzes.
- `yun_audit_cards.md`: lokales Arbeitsexemplar mit Artikelzitaten; wird
  nicht versioniert.

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

- Kein vollständiges Audit aller 699 Yun-Records; die 410 streng
  vollständigen Records wurden geprüft, nicht die 289 unvollständigen.
- Der Audit ist keine unabhängige Zweitannotation und keine
  Modellgenauigkeitsmessung.
- `verified_table` und die 78 nicht belegten Records sind keine vollständige
  klinische Neuannotation; die Grenzen stehen in `yun_audit_410.md`.
- Keine Modellvorhersagen und keine Genauigkeitsmessung; dieser Schritt ist
  reine Dateninventur und Referenzprüfung.
- Keine Prüfung der individuellen PMC-Lizenz jedes Artikels. Die
  Yun-XML-Auszüge enthalten keine Lizenzmetadaten.
- Keine unabhängige Zweitannotation und kein B-Rücklauf; A/B bleiben
  unverändert.
