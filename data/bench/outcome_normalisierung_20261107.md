# Outcome-Namen normalisiert: was die Gruppen zusammengefuehrt hat

Stand: 07.11.2026. Neu: `research_agent/meta/outcome_labels.py`,
verdrahtet in `pooling.build_analysis`. Rein offline gemessen, kein
Netzaufruf, kein LLM.

## Regeln

1. Kleinschreibung, Gedankenstriche und Markup entfernen.
2. Klammerinhalt: bekanntes Skalenkuerzel (PSQI, ESS, ISI, PDSS, WASO,
   TST, SOL, AHI, MSLT, VAS) wird angehaengt, anderer Text faellt weg.
3. Einheit wird als Token angehaengt statt geloescht: `min`, `pct`,
   `sec`, `hour`, `events_per_hour`.
4. Abschliessendes `score` faellt weg (`PSQI score` -> `psqi`).
5. Gepruefte Synonymtabelle, keine Aehnlichkeitsheuristik.

Damit werden `Sleep onset latency, min`, `Sleep latency (min)` und
`SOL, min` zu `sleep onset latency min`; `% Stage N1` und
`Stage N1 time (min)` bleiben getrennt, ebenso `REM latency, min` und
`Sleep onset latency, min` sowie `Overall sleep quality` (ohne Kuerzel)
und `PSQI score`.

## Messung

| Korpus | Zeilen | Gruppen | k >= 2 |
|---|---:|---:|---:|
| SOL, 100 XML | 15 | 15 | 0 |
| Melatonin, 43 XML | 31 | 19 | 0 |
| beide zusammen | 46 | 23 | 0 |

Tests: 44 passed (test_outcome_labels + test_effect_columns + test_jats_tables).

## Ergebnis

Die Normalisierung greift, aendert an der Leitfrage aber nichts: Der
reparierte SOL-Korpus enthaelt 15 Zeilen aus **einer** Studie (eine
Kohortenstudie mit `Hedges g (95 % CI)`), also kann kein Label daraus
zwei unabhaengige Studien machen. Die frueheren Nominalpaare
(`Sleep onset latency` 0.07 vs -10.13) waren ein Skalenfehler, kein
Namensproblem. Auch die Vereinigung beider Korpora bringt kein k >= 2.

## Grenzen

* Die Synonymtabelle deckt nur Wortlaute ab, die in den beiden Korpora
  belegt sind; neue Endpunkte bleiben getrennt, bis ein Eintrag mit
  Belegzeile dazukommt.
* Bei der Vereinigung zaehlt dieselbe DOI aus beiden Korpora als eine
  Studie (gleiche `source_id`, Kollaps greift).

