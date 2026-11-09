# Browser-Nachweis Meta-Karte (E4l, Phase 1)

Stand: 2026-11-09. Auftrag: visuell bestaetigen, dass die Meta-Analysis-Karte
Zeilenbasis, RVE-Zeile (mit M und KI) und RVE-RE-Zeile (mit
Breitenverhaeltnis) anzeigt.

## Aufbau

`scripts/serve_dashboard_stub.py` startet den **echten** `DashboardServer` auf
`127.0.0.1:8099` gegen eine Kopie von
`data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db`. Der
Orchestrator ist ein `SimpleNamespace` mit `db`, `current_topic` und
`get_status` - kein Modell, kein Netz, kein Schreibzugriff auf das Original.

## Befund im DOM

Nach dem Wechsel auf den Tab `meta` laedt die Seite `/api/metaanalysis`
(kein `liveOnly`-Abbruch, weil der Handler den Endpunkt bedient). Auszug aus
`#maGroups`:

```
major adverse cardiovascular events
k=4 - gepoolt 0.742 [0.430; 1.053] (DL) - I2=0.0% - tau=0.000
Praediktionsintervall: 0.282 bis 1.201
Basis: 6 Zeilen, 4 nach dem Kollaps (2 zusammengelegt)
RVE (M=3): 0.751 [0.182; 1.319]
RVE-RE (tau2 in den Gewichten): 0.751 [0.182; 1.319] - Breite x1.00
GRADE (maschinell): very_low (...)
```

Weitere Gruppen aus demselben Rendering:

| Gruppe | Basis | RVE | RVE-RE | Breite |
|---|---|---|---|---|
| cardiovascular mortality | 2 Zeilen, 2 nach Kollaps | M=2: 1.012 [0.930; 1.094] | 1.012 [0.930; 1.094] | x1.00 |
| incident cardiovascular disease | 6 Zeilen, 5 nach Kollaps (1 zusammengelegt) | M=4: -0.130 [-0.849; 0.589] | 0.295 [-0.600; 1.191] | x1.25 |

Alle drei Informationsbestandteile sind sichtbar und stimmen mit der
API-Antwort ueberein (E4l: `rows=6`, `rows_collapsed=4`, `rve` = `rve_re` =
0.7505 [0.1819; 1.3191]).

Der Unterschied zwischen `RVE` und `RVE-RE` tritt genau dort auf, wo tau2 > 0
ist (incident CVD): Die RE-Gewichtung verbreitert das Intervall um Faktor
1,25. Bei tau2 = 0 (MACE, cardiovascular mortality) sind die Zeilen
identisch - das ist die erwartete, nicht die fehlende Wirkung.

## Technische Beobachtungen

- Der automatisierte Klick auf den Text "Meta-Analysis" wechselte den Tab
  nicht; erst `document.querySelector('.tab[data-tab="meta"]').click()`
  aktivierte ihn (danach `classList` enthielt `active`).
- Vor dem Tabwechsel wurden nur `/api/status`, `/api/journal`,
  `/api/rejected`, `/api/parallel-stats` angefragt; nach dem Wechsel kam
  `/api/metaanalysis` mit 200 hinzu.
- Keine JS-Fehler in der Konsole; `node --check app.js` Exit 0.

## Artefakte

| Datei | Inhalt |
|---|---|
| `browser_meta_sichtbar_20261109.png` | Viewport-Shot bei 1100x2000: alle drei Gruppen mit beiden RVE-Zeilen |
| `browser_meta_full_20261109.png` | Full-Page-Shot: Meta-Tab aktiv, Gruppenliste sichtbar |
| `data/dashboard_stub.log` | Startprotokoll, DB-Kopie-Pfad (gitignored) |

## Grenzen

- Geprueft mit Stub-Orchestrator, nicht mit laufendem Rechercheprozess.
- Bei Standard-Viewport (573x981) greift der Screenshot trotz
  `scrollTop = 1785` den Seitenkopf; nach `resize` auf 1100x2000 zeigt er
  die Karte vollstaendig. Belastbar sind dieser Shot und der DOM-Text.
- Eine Interaktion (Filter, Exclude) wurde nicht geprueft - der Auftrag
  verlangt nur die Darstellung.

Modellaufrufe: 0. Netz: 0.
