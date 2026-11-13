# Statusübersicht: Multi-Model Cross-Validation

Stand: 2026-11-13
Letzte Commits: `f6c0994` (Vorbereitung abgeschlossen), `c03fa56` (Status nachgezogen)
Vollständiger Bericht: [`crossval_preparation_report.md`](crossval_preparation_report.md)

## Kurzstatus

Die Vorbereitung ist abgeschlossen. Es gibt **keinen regulären Modelllauf** auf
den 25 Hauptartikeln, **keine Referenzannotation** und **keinen Freeze**. Der
Datensatz ist ein Entwurf (`draft_pending_annotation`).

| Baustein | Status |
|---|---|
| Artikelauswahl v2 (25 + 10 Reserve) | fest, disjunkt zu G5 und Yun |
| Volltexte (50 XML) | vorhanden, SHA-256 dokumentiert |
| GLM 5.3 | verwendbar ab `max_tokens` 8000, empfohlen 12000 |
| Eignungsprüfung | 1 von 25 bestätigt, 24 brauchen menschliche Prüfung |
| Schema v1 | fertig, 10 Tests |
| Referenzannotation | Workflow fertig, Annotation **nicht begonnen** |
| Power | 60-80 Records nur für Effekte ab 7-9 pp ausreichend |
| Adjudikation | verblindeter Batch und Auswertung implementiert, 3 Tests |
| Manifest | Entwurf, Disjunktheit geprüft, Referenz offen |

## Zahlen

- Auswahl: 25 Hauptartikel, 10 Reserveartikel; Pool 372, Volltexte 50/50 als
  JATS-XML (6,13 MB).
- Disjunktheit: 0 Überschneidungen mit der G5-Shortlist (30 PMCIDs) und den 70
  Yun-Artikeln (275 Freeze + 26 Dev + 249 Test = 699 Records).
- Schema v1 SHA-256: `84d5960625fc9f8966c811f94c29e0d49f137d348a2caa70421472e537fe84ee`.
- Eignung der Hauptartikel: 1 `eligible_confirmed`, 3 `eligible_uncertain`,
  10 `manual_review_required`, 11 `ineligible`.
- Eignung der Reserve: 1 bestätigt, 3 unsicher, 2 manuell, 4 nicht geeignet.
- GLM-Diagnose: bei 900/2000 Tokens `content` leer und `finish_reason: length`;
  bei 8000/16000 valides JSON mit korrekten Werten (8/20 vs. 13/44),
  2544-4035 Completion-Tokens, 14,0-20,4 s.
- Power (McNemar, Feldebene, Diskordanz 0,25, Power 0,80): kleinste
  nachweisbare Differenz 7,85-8,76 pp bei 60 Records und 6,50-7,85 pp bei 100
  Records. Für 5 pp wären 893-1112 Felder nötig.

## Dateien in diesem Ordner

| Datei | Inhalt |
|---|---|
| `crossval_preparation_report.md` | Abschlussbericht mit acht Abschnitten |
| `experiment_plan.md` | Design, Metriken, Ablauf |
| `entscheidungen_20261113.md` | Entscheidungen F1-F6 mit Status |
| `zusammenfassung_20261113.md` | Stand vor der Vorbereitungsphase |
| `offene_fragen.md` | offene methodische Fragen |
| `candidate_pool_v1.json` | 372 Kandidaten |
| `candidate_shortlist_v2.json` / `.md` | 25 + 10 mit Rollen |
| `fulltext_availability_v1.json` / `.md` | 50 XML mit Hashes |
| `fallmix_profile_v1.json` / `.md` | Fallmix, Tabellen, Trial-Dubletten |
| `crossval_eligibility_review_v1.json` / `.md` | Eignung der 25 |
| `crossval_eligibility_reserve_v1.json` / `.md` | Eignung der Reserve |
| `schema_v1.json` | Schema mit 13 Pflichtfeldern je Zahl |
| `schema_v1_documentation.md` | Felder, Konfliktkategorien C1-C6 |
| `annotation_workflow_v1.md` | Rollen, Schritte, Ein-Personen-Fallback |
| `adjudication_protocol_v1.md` | Verblindung, Rollen, Auswertung |
| `power_estimation_v1.json` / `.md` | MDD-Tabellen und Folgerung |
| `dataset_manifest.json` | Entwurf mit Hashes und Disjunktheit |
| `diagnostics/glm_20261113/` | Diagnosebericht und acht Rohantworten |

Skripte liegen in `public_benchmark/scripts/`: `select_crossval_articles.py`,
`fetch_crossval_fulltext.py`, `profile_crossval_articles.py`,
`review_crossval_eligibility.py` (`--role primary|reserve`),
`validate_crossval_annotation.py`, `estimate_crossval_power.py`,
`build_adjudication_batch.py`, `evaluate_adjudication.py`,
`build_crossval_manifest.py`, `diagnose_glm.py`.

## Reproduktion

```bash
export PYTHONIOENCODING=utf-8
.venv/bin/python public_benchmark/scripts/review_crossval_eligibility.py
.venv/bin/python public_benchmark/scripts/review_crossval_eligibility.py --role reserve
.venv/bin/python public_benchmark/scripts/estimate_crossval_power.py
.venv/bin/python public_benchmark/scripts/build_crossval_manifest.py
.venv/bin/python -m pytest public_benchmark/tests/test_crossval_manifest.py \
  public_benchmark/tests/test_crossval_schema.py \
  public_benchmark/tests/test_crossval_adjudication.py \
  public_benchmark/tests/test_crossval_case_mix.py \
  public_benchmark/tests/test_crossval_g5_exclusion.py \
  public_benchmark/tests/test_timepoint_schema.py -q
```

33 Tests, alle grün (0,6 s). Der Modelllauf selbst ist nicht Teil der
Reproduktion; er braucht die Referenzannotation und eine Freigabe.

## Blocker

1. **Keine Referenzannotation** - ohne sie keine Genauigkeitsaussage und kein
   Freeze.
2. **24 von 25 Artikeln nicht bestätigt** - Volltextprüfung vor der Annotation
   nötig, sonst geht Annotationszeit verloren.
3. **Reserve reicht nicht** - 11 ungeeignete Hauptartikel, aber nur 4 brauchbare
   Reserveartikel; Ersetzung braucht eine dokumentierte Freigabe.
4. **Prompt für `schema_v1` fehlt** - ohne eingefrorenen Prompt kein Lauf.
5. **Viertes Adjudikationsmodell unbestimmt** - Kontrollinstanz noch nicht
   ausgewählt.
6. **Stichprobe klein** - 60-80 Records nur explorativ, 5 pp nicht nachweisbar.

## Nächste Schritte

1. Volltextprüfung der 25 Artikel durch eine fachlich geeignete Person.
2. Prompt für `schema_v1` bauen und einfrieren.
3. Zwei unabhängige Annotationen, Vergleich, Konsolidierung, `reference_v1.jsonl`.
4. Power-Entscheidung: 60-80 Records explorativ oder Erweiterung auf ~150.
5. Viertes Adjudikationsmodell festlegen.
6. `freeze.json` erst danach; dann GLM mit `max_tokens` 12000.

## Grenzen dieser Übersicht

Alle Zahlen stammen aus den genannten Artefakten oder aus Skriptläufen. Es gibt
keine Messung zur Extraktionsqualität, weil noch keine Referenz existiert. Die
Eignungsprüfung ist konservativ und ersetzt keine menschliche Sichtprüfung.
