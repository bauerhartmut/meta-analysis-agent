# Betriebstest: zwei Themen und Schreiben während Lesen

Stand: 2026-11-09. Beantwortet die zwei offenen Zeilen aus
`betriebspruefung_matrix_20261109.md`. Beide Tests laufen auf DB-Kopien, ohne
Netz und ohne Modellaufruf. Skript: `scripts/pruefe_betrieb_20261109.py`.

## Test A — reagiert der Endpunkt auf `current_topic`?

Ein Server, drei Zustände, dazwischen wird nur `stub.current_topic` geändert.
Zusätzlich liegt eine Effektzeile mit dem Outcome `betriebstest ohne thema` in
der Kopie, den kein Thema führt.

| Zustand | Gruppen | PRISMA `included` | PRISMA `excluded` | `off_target` |
|---|---:|---:|---:|---:|
| ohne Thema (`""`) | 14 | 148 | 56 | 0 |
| Thema 1 (Mediterrane Ernährung) | 2 | 148 | 56 | 22 |
| Thema 2 (Betriebstest) | 0 | 147 | 3 | 35 |

Die zwei Gruppen unter Thema 1 sind genau die beiden Ziele des Themas:
`Incident cardiovascular disease [log_ratio]` und
`Major adverse cardiovascular events [log_ratio]`. Ohne Thema sind es 14.

**Befund:** `current_topic` wirkt stark. Es filtert nicht über eine
Themenspalte in `study_effects` (die es nicht gibt), sondern über
`review_targets`: `load_targets(db, topic)` liefert die Ziel-Labels, und
`build_analysis` gruppiert nur, was auf ein Ziel passt. Der Rest landet in
`off_target` — 22 Zeilen unter Thema 1, 35 unter Thema 2.

Zwei Nebenbefunde:

1. **Gruppennamen ändern sich mit dem Thema.** Unter Thema 1 heißen die
   Gruppen `... [log_ratio]`, ohne Thema anders. Wer Gruppen über Namen
   vergleicht (Dashboards, Caches, Tests), vergleicht dann nicht dieselbe
   Sache. Für den Bericht ist das unkritisch, weil er Gruppen nicht über
   Namen adressiert.
2. **Ein fehlerhaftes Ziel-Payload ergibt HTTP 200 mit `error`-Feld.** Mein
   erster Testlauf schrieb `outcomes` als Liste von Strings; `target_labels`
   erwartet Objekte mit `label` und warf `'str' object has no attribute 'get'`.
   Der Endpunkt fing das ab und antwortete mit `groups: {}` und
   `error: "..."`, nicht mit 500. Das ist für den Betrieb gut (kein Absturz),
   aber für Monitoring schlecht: Eine kaputte Zieldefinition sieht wie eine
   leere Auswertung aus. Der Zustand ist von „keine Studien" nicht zu
   unterscheiden, wenn man nur den Statuscode liest.

## Test B — verfälscht gleichzeitiges Schreiben das Lesen?

200 Effektzeilen geschrieben, während 200 GETs auf `/api/metaanalysis` liefen,
auf einer Kopie mit `journal_mode=WAL`.

| Messgröße | Wert |
|---|---|
| Schreibvorgänge | 200/200 ok, 0 Fehler |
| Lesevorgänge | 200/200 ok, 0 Fehler |
| Zeilen in der Kopie danach | 200 |
| Dauer | 34,5 s |
| Latenz min / median / p95 / max | 159 / 166 / 192 / 354 ms |
| `database is locked` | nein |

**Befund:** WAL trägt die Mischlast. Kein einzelner Leser scheiterte, kein
Schreibvorgang ging verloren. Die p95-Latenz von 192 ms liegt in derselben
Größenordnung wie im Ruhezustand (der frühere API-Test brauchte für einen
einzelnen GET deutlich unter einer Sekunde); die Schreiblast verdoppelt die
Antwortzeit nicht.

Grenze der Aussage: Der Test schreibt nur neue Zeilen, er ändert und löscht
nichts. Ein `UPDATE` auf eine Zeile, die ein Leser gerade aggregiert, ist
nicht abgedeckt. Ebenso wenig mehrere gleichzeitige Schreiber — SQLite
serialisiert Schreiber, und dieser Test hatte genau einen.

## Was das für die Matrix bedeutet

| Zeile | vorher | jetzt |
|---|---|---|
| Reagiert der Endpunkt auf `current_topic`? | kein Test mit zwei Themen | belegt: 14 → 2 → 0 Gruppen, Ziel-Labels steuern die Gruppierung |
| Verfälscht gleichzeitiges Schreiben das Lesen? | kein Test | belegt: 200/200 in beiden Richtungen, kein Lock |

Der Voll-Lauf mit Modellaufrufen bleibt unnötig: Beide Fragen sind lokal
beantwortet, und keine der Antworten hinge an einem Prompt oder einem
Netzabruf.

## Reproduktion

```text
export PYTHONIOENCODING=utf-8
.venv/bin/python.exe scripts/pruefe_betrieb_20261109.py --beide --n 200
```

Exit 0, wenn beide Tests grün sind. `--themen` und `--nebenlaeufig` laufen
einzeln; `--n` ändert die Last (Standard 200).

## Grenzen

- Ein Testlauf, keine Wiederholungsserie. Die Latenzen sind Momentwerte auf
  diesem Rechner, keine Lastkurve.
- Test A prüft die Filterwirkung, nicht die inhaltliche Richtigkeit der
  Ziele. Ob ein Ziel sinnvoll geschnitten ist, entscheidet die Ableitung, nicht
  dieser Test.
- Test B nutzt einen Schreiber. Zwei gleichzeitige Schreiber können sich sehr
  wohl blockieren; das ist SQLite-Verhalten und hier nicht gemessen.
- Die Kopien werden nach jedem Lauf gelöscht; die Original-DB wird nur
  gelesen.
