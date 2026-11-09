# Volle Testsuite nach den lokalen Patches (2026-11-09)

Modellaufrufe: 0 · Tokens: 0 · Netz: 0. Ausgeführt mit
`.venv/bin/python.exe -m pytest research_agent/tests -q`.

## Lauf 1 - 1 Fehler, der nicht von den Patches kam

```
1 failed, 1330 passed, 2 skipped, 3 warnings in 521.14s (0:08:41)
EXIT=1
FAILED research_agent/tests/test_research_engine.py::
  TestCircuitEscalation::test_a_provider_that_was_quiet_starts_fresh
```

Assertion: `599.9999999999998 != 300 within 2 delta`.

**Ursache.** Der Test setzte `_last_penalty["openalex"] = 0.0` und verliess
sich darauf, dass `time.monotonic() - 0` groesser ist als
`CIRCUIT_QUIET_SECONDS = 1800.0` (`research_agent/research/search.py:140`).
`time.monotonic()` ist die Systemlaufzeit; waehrend des Vollaufs lag sie bei
rund 1386 s, also unter der Schwelle. Der zweite `penalize` galt damit als
Wiederholung (Streak 2, Fenster 600 s statt 300 s). Isoliert lief derselbe
Test dreimal gruen, weil die Uptime inzwischen ueber 1800 s lag.

**Fix** (`63bc122`). Die Vorbedingung ist jetzt explizit:
`_last_penalty = time.monotonic() - CIRCUIT_QUIET_SECONDS - 1.0`. Die
Assertions sind unveraendert - keine Toleranz, kein Skip.

## Lauf 2 - gruen

```
1331 passed, 2 skipped, 3 warnings in 467.92s (0:07:47)
EXIT=0
```

Die 14 zusaetzlichen Tests gegenueber dem Lauf vom 08.11. (1317) sind
`test_rve_weights.py` (8) und `test_pruefe_report_patch.py` (6).

## Einordnung

- Die drei lokalen Patches (`pooling.py` mit `weights="random"` und
  `rows`/`rows_collapsed`, `report.py` mit M=1-Hinweis, `rve_re`-Zeile und
  Zeilenbasis) brechen keinen Aufrufer ausserhalb der Report-Suite.
- Der Fehler in Lauf 1 war ein Testdefekt, der nur nach einem frischen Boot
  auftritt; er hatte mit den Patches nichts zu tun.
- Beide Logs sind gitignored (`data/*.log`); diese Datei haelt das Ergebnis
  fest.
