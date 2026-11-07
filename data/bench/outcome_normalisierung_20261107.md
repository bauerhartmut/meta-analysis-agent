# Outcome-Namen normalisiert: was zusammengefuehrt wurde - und was nicht

Stand: 07.11.2026. Neu: `research_agent/meta/outcome_labels.py`. Offline
gemessen, kein Netzaufruf, kein LLM.

## Regeln

1. Kleinschreibung, Gedankenstriche und Markup entfernen.
2. Klammerinhalt: bekanntes Skalenkuerzel (PSQI, ESS, ISI, PDSS, WASO,
   TST, SOL, AHI, MSLT, VAS) wird angehaengt, anderer Text faellt weg.
3. Einheit wird als Token angehaengt statt geloescht (`min`, `pct`, `sec`,
   `hour`, `events_per_hour`).
4. Abschliessendes `score` faellt weg (`PSQI score` -> `psqi`).
5. Gepruefte Synonymtabelle, keine Aehnlichkeitsheuristik.

Damit fallen zusammen: `Sleep onset latency, min` = `Sleep latency (min)`
= `SOL, min`; `WASO, min` = `Wake after sleep onset (min)`; `PSQI score` =
`Overall sleep quality (PSQI)`; `ESS` = `Excessive daytime sleepiness (ESS)`.
Getrennt bleiben: `% Stage N1` vs `Stage N1 time (min)` (Prozent gegen
Minuten), `REM latency, min` vs `Sleep onset latency, min`, und ein nacktes
`Overall sleep quality` ohne Kuerzel (kann ein anderes Instrument sein).

## Messung

| Korpus | Zeilen | Gruppen | k >= 2 |
|---|---:|---:|---:|
| SOL, 100 XML | 15 | 15 | 0 |
| Melatonin, 43 XML | 31 | 19 | 0 |
| beide zusammen | 46 | 23 | 0 |

Tests: 101 passed (Pooling, Outcome-Labels, Effektspalten, JATS).

## Ergebnis

Die Normalisierung greift und ist getestet; an der Leitfrage aendert sie
nichts. Der reparierte SOL-Korpus hat 15 Zeilen aus **einer** Studie, also
kann kein Label daraus zwei unabhaengige Studien machen. Die frueheren
Nominalpaare (`Sleep onset latency` 0.07 vs -10.13) waren der Skalenfehler
aus `Effect size (95% CI)`, kein Namensproblem. Auch die Vereinigung beider
Korpora ergibt kein k >= 2.

## Grenzen

* Die Verdrahtung sitzt in `pooling.py`; diese Datei ist - wie
  `extraction.py` - gitignored und damit nur lokal wirksam. Im Repo
  versioniert ist das Normalisierungsmodul samt Tests.
* Die Synonymtabelle deckt nur belegte Wortlaute ab; neue Endpunkte bleiben
  getrennt, bis ein Eintrag mit Belegzeile dazukommt.
* Bei der Vereinigung zaehlt dieselbe DOI aus beiden Korpora als eine
  Studie (gleiche `source_id`, Kollaps greift).

