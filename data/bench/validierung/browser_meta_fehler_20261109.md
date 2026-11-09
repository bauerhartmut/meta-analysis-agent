# Meta-Karte bei HTTP 500: Nachweis im Browser

Stand: 2026-11-09. Prüft, was die Karte anzeigt, wenn der Endpunkt wegen einer
defekten Zieldefinition mit 500 antwortet, und ob der Fehler nach der
Frontend-Änderung sichtbar ist.

Aufbau: `scripts/serve_dashboard_stub.py --kaputtes-ziel` legt in der Kopie
ein `review_targets`-Payload mit `outcomes` als String-Liste ab und setzt
`current_topic` auf dieses Thema. Der echte `DashboardServer` läuft auf
`127.0.0.1:8099`, die Original-DB bleibt unberührt.

## Vorher — aus dem Code abgeleitet, nicht gemessen

`pollMeta()` las den Body ohne Statusprüfung:

```js
const r=await fetch(API+'/api/metaanalysis');const d=await r.json();
...
const groups=Object.entries(d.groups||{});
if(box)box.innerHTML=groups.length? ... :'<div class="empty">Noch keine poolbaren Effektzeilen</div>';
```

Bei 500 enthält der Body `groups: {}` und `error`. `d.groups||{}` ergibt eine
leere Liste, die Karte fällt in den Leer-Zweig. Der alte Zustand ist damit
belegt, aber nicht im Browser gemessen — gemessen wurde nur der Zustand nach
der Änderung.

## Nachher — gemessen

Zustand mit kaputtem Ziel, `document.getElementById('maGroups')`:

```text
Metaanalyse nicht verfügbar: 'str' object has no attribute 'get'
```

`maUsable` und `maEffectRows` stehen auf `–` statt auf `0`. Die Konsole zeigt
`GET /api/metaanalysis → 500`, keine JavaScript-Ausnahme. Die Karte bleibt
also bedienbar, meldet aber die Störung.

## Gegencheck mit intaktem Ziel

Zweiter Stub-Lauf ohne `--kaputtes-ziel`, gleiche Seite:

| Feld | Wert |
|---|---|
| `maUsable` | 36 |
| `maEffectRows` | 91 |
| Fehlertext in der Karte | nein |
| Erste Gruppenzeile | `agreement between 12 medas and 24hr …` |

Die Karte rendert normal. Der Fehlerzweig greift nur bei `!r.ok || d.error`,
nicht bei einer gültigen Antwort.

## Was geändert wurde

`research_agent/dashboard/templates/app.js`, in `pollMeta()`: Statusprüfung
vor dem Rendern, bei Fehler eine rote Zeile mit dem Fehlertext und `–` in den
Zählern statt `0`. Zusätzlich setzt die Karte `dataset.state` auf `ok` oder
`leer`, damit sich die beiden Zustände später unterscheiden lassen.

`research_agent/tests/test_dashboard_contract.py`: Der statische Test hält
`!r.ok||d.error` und den Text `Metaanalyse nicht verfügbar` fest, damit der
Zweig bei einer UI-Änderung nicht still verschwindet.

## Grenzen

- Geprüft wurde der 500-Fall und der 200-Fall mit Daten. Ein Netzwerkfehler
  (Server nicht erreichbar) läuft weiterhin in den `catch`-Zweig und wird
  nicht angezeigt; das ist ein eigener Fall.
- Kein automatisierter DOM-Test; der Nachweis ist ein Browserlauf plus ein
  statischer Contract-Test.
- Der Fehlertext stammt aus der Python-Exception und ist englisch. Für die
  Diagnose ist das nützlich, für eine Bedienoberfläche roh.
