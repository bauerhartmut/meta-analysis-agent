# Protokoll: Dashboard-Rendering des M-Gates

Stand: 2026-11-08. Modellaufrufe: 0. Tokens: 0.

## Aufbau

- Server: `research_agent/dashboard/standalone_server.py` (read-only),
  Port 8080, Datenbank
  `data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db`
  (die Datei, in der `preeclampsia [log_ratio]` liegt).
- Browser: lokaler Chromium, Seite `http://localhost:8080/`, Meta-Tab.

## Warum kein End-to-End-Test

`/api/metaanalysis` steht in `LIVE_ONLY_APIS`; der Standalone-Server
beantwortet ihn mit `supported: false`. Der Live-Server
(`dashboard/server.py`) rechnet `build_analysis()` erst mit einem
`orchestrator` - den zu starten waere ein Agentenlauf und ist ohne Freigabe
nicht erlaubt.

Deshalb wurde der **Render-Pfad** getestet: `pollMeta()` aus `app.js` wurde
im geladenen Browser mit einer injizierten API-Antwort aufgerufen
(`window.fetch` ueberschrieben, `dashCaps.live_only` geleert). Das prueft
genau die geaenderte Zeile, aber nicht die Kette DB -> Endpunkt -> Browser.

## Eingespielte Daten

| Gruppe | k | pooled | ci_low | ci_high | single_cluster | M |
|---|---:|---:|---|---|---|---:|
| preeclampsia [log_ratio] | 5 | -0.309 | null | null | true | 1 |
| MACE [log_ratio] | 4 | 0.740 | 0.430 | 1.050 | - | 3 |

## Ergebnis im DOM (`#maGroups.innerText`)

```
preeclampsia [log_ratio]
k=5 · gepoolt -0.309 · kein KI (nur ein unabhaengiger Cluster) (random)
MACE [log_ratio]
k=4 · gepoolt 0.740 [0.430; 1.050] (random) · I²=20.0%
```

- Kein `[0.000; 0.000]` bei `preeclampsia` - der Fehler ist behoben.
- Der Hinweis auf den einen unabhaengigen Cluster erscheint.
- Die Gruppe mit `M = 3` zeigt unveraendert ihr regulaeres Intervall.

Screenshot: `data/bench/validierung/dashboard_gate_20261108.png`.

## Grenze

Der Test belegt das Rendering, nicht die Datenkette. Ein End-to-End-Test
braucht den Live-Server mit Orchestrator, also einen Lauf mit Freigabe.
