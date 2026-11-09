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

`research_agent/dashboard/templates/app.js`: ein Helfer `metaFehler(text)`
rendert die rote Zeile und setzt die Zähler auf `–`. Beide Fehlerwege laufen
dorthin: der 500-Fall (`!r.ok||d.error`) und der zuvor leere `catch(e){}` bei
 einem Netzwerkfehler. Die Karte setzt `dataset.state` auf `ok`, `leer` oder
`fehler`.

Gemessen im Browser für den Netzwerkfall: `fetch` für `/api/metaanalysis`
auf `Failed to fetch` gesetzt, dann `pollMeta()` aufgerufen. Ergebnis:

```text
vorher:  metaFehler = function, state = ok,   maUsable = 36
nachher: text = "Metaanalyse nicht verfügbar: Failed to fetch"
         state = fehler, maUsable = –, maEffectRows = –
```

`research_agent/tests/test_dashboard_contract.py`: Der statische Test hält
`!r.ok||d.error` und den Text `Metaanalyse nicht verfügbar` fest und verbietet
ein leeres `}catch(e){}` in `pollMeta`, damit der Netzwerkfall nicht wieder
still endet.

## Grenzen

- Geprüft wurden 500-Fall, 200-Fall mit Daten und der Netzwerkfall per
  `fetch`-Mock. Ein Serverausfall und eine defekte Zieldefinition sehen beide
  als Fehlerzeile aus; den Unterschied trägt nur der Text indirekt.
- Kein automatisierter DOM-Test; der Nachweis ist ein Browserlauf plus ein
  statischer Contract-Test.
- Der Fehlertext stammt aus der Python-Exception und ist englisch. Für die
  Diagnose ist das nützlich, für eine Bedienoberfläche roh.
