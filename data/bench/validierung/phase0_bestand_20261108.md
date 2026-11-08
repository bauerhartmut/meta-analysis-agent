# Phase 0 - Technischer Bestand

Stand: 2026-11-08. Read-only erhoben, kein Netz, kein Modell. Zeilennummern
beziehen sich auf den Arbeitsstand `6a6f633`; sie verschieben sich mit dem
Code.

## Einstiegspunkte

| Baustein | Ort | Aufgabe |
|---|---|---|
| `standardize(row)` | `research_agent/meta/pooling.py:151` | Eine gespeicherte Zeile auf eine poolbare Skala bringen; liefert `(est, se, scale, grund)` |
| `pool(effects, method)` | `pooling.py:333` | Random Effects auf bereits standardisierten Zeilen; DL-tau^2, HKSJ als Standardintervall |
| `pool_rve(...)` | `pooling.py:444` | Robust variance estimation fuer abhaengige Effekte |
| `subgroups(...)` | `pooling.py:537` | Subgruppen ab k >= 3 |
| `leave_one_out(...)` | `pooling.py:591` | Leave-one-out |
| `egger(...)` | `pooling.py:618` | Egger-Regression |
| `forest_table(...)` | `pooling.py:669` | Textzeilen fuer die Forest-Tabelle |
| `build_analysis(...)` | `pooling.py:923` | Klammer um alles: Standardisieren, Gruppieren, Gates, Pools |
| `_collapse_same_study(...)` | `pooling.py:742` | Gemeinsame Kontrollarme / dieselbe Studie |

## Datenfluss

```
Volltext/PDF  --(LLM, meta/extraction.py)-->  study_effects (SQLite)
                                                     |
                                          standardize()  (Skala: g / z / log / raw)
                                                     |
                                     Protokoll-Gates (Exposure, Population, Design)
                                                     |
                                               pool()  (DL, HKSJ)
                                                     |
                              forest_table / leave_one_out / egger / subgroups
                                                     |
                                      report.py  (deterministisch, ohne LLM)
```

Der Rechenteil ab `standardize()` ist **LLM-frei und offline** lauffaehig:
`pool()` nimmt eine Liste von Dicts mit `est`, `se`, `label` und braucht
nichts weiter. Das ist der Ansatzpunkt fuer E2.

## Abhaengigkeiten

- `pooling.py` importiert `math`, `re`, `typing` sowie `.designs` und
  `.targets`; `scipy` (chi2, t, norm) wird erst im Aufruf geladen.
- Kein Import zieht LLM, HTTP oder Konfiguration. Der E2-Lauf braucht daher
  weder Netz noch Schluessel (belegt: 1,1 s Laufzeit, keine Modellaufrufe).
- scipy ist installiert (1.15.2); fehlt es, weicht das HKSJ-Intervall auf
  1,96 aus (`_t_quantile` liefert dann None) - ein stiller Moduswechsel, den
  der Bericht nicht kennzeichnet.

## Versionsstand und Ignore-Regel

Drei Kernmodule sind **gitignored** und damit nicht Teil des Repos:

| Datei | Regel |
|---|---|
| `research_agent/orchestrator.py` | `.gitignore:55` |
| `research_agent/meta/pooling.py` | `.gitignore:61` |
| `research_agent/meta/extraction.py` | `.gitignore:62` |

Folge fuer die Validierung: Sie laeuft nur im Arbeitsbaum. Ein frischer Clone
kann sie nicht wiederholen, und 18 Testmodule brechen dort mit ImportError ab
(`plan_ausbeute_validierung_status_20261108.md`, Frage 5). Ein Pruefbericht
ohne diese Dateien ist nicht reproduzierbar - das wird in jedem Bericht als
Grenze genannt.

## Vorhandene Tests

| Test | Deckt ab |
|---|---|
| `research_agent/tests/test_pooling_reference.py` | unabhaengige Zweitimplementierung von FE, Q, DL-tau^2, HKSJ, Prediction Interval; Kleinst-k-Hinweise |
| `research_agent/tests/test_meta_pooling.py` | Verhalten von `pool` und `build_analysis` |
| `research_agent/evals/meta_benchmark.py` | Benchmark-Runner gegen Referenzfaelle (Feld `evaluate_case`, `run_benchmark`) |
| `data/goldstandard/` | Referenzkorpus (derzeit Kaffee akut vs. Placebo, Reaktionszeit) |

## Was fuer isolierte Tests fehlt

- Ein externer Abgleich der Formeln (R `metafor`, `statsmodels`) - in dieser
  Umgebung nicht verfuegbar; die Zweitimplementierung rechnet dieselben
  Formeln, ein gemeinsamer Schreibfehler bliebe unsichtbar.
- Ein Referenzfall mit SOL-Daten im Benchmark-Schema. Die Zahlen liegen
  dokumentiert vor (`mends_hta_zusatz_20261108.md`,
  `pooling_sol3_20261108.json`), sind aber nicht als `case_id` eingetragen.
- `pool()` zaehlt verworfene Zeilen nicht: `excluded` bleibt leer, obwohl der
  Filter Zeilen ohne `est`/`se` entfernt (in E2, Fall U7, gemessen). Das
  Zaehlen passiert eine Ebene hoeher in `build_analysis`; wer `pool()` direkt
  aufruft, sieht die Verluste nicht.

## Fazit

E2 ist ohne Modell und ohne Netz pruefbar: `pool()` direkt aufrufen, sechs
Kennzahlen gegen die dokumentierte Referenz stellen. Genau das macht
`scripts/validate_pooling_e2.py`.
