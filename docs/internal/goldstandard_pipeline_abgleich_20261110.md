# Goldstandard gegen Pipeline: Abgleich (2026-11-10)

Kein Modellaufruf. Quelle: `data/golden_effects/goldstandard_A.json`, Datenbanken:
research-does-acute-caffeine-versus-placebo-affec-972eac.db, research-does-caffeine-intake-affect-short-term-m-783a51.db, research-does-melatonin-improve-sleep-onset-laten-382747.db, research-exercise-and-depressive-symptoms-in-adul-bbb324.db, research-kognition-und-gesundheit-ist-der-zusamme-ec45a1.db, research-mediterrane-ernaehrung-und-kardiovaskula-475855.db, harness_local.db.

```
Goldstandard: data/golden_effects/goldstandard_A.json
Dokumente: 30 | annotiert: 0 | offen: 30
Pipelinezeilen: 37 | Toleranz: 1% | Schwelle: 0.55
Keine Annotation: es gibt nichts auszuwerten. Die Pipeline-Zahlen stehen nur als Baseline.
```

## Was gezaehlt wird

- **TP**: Goldzeile und Pipelinezeile wurden gepaart.
- **FP**: Pipelinezeile ohne Goldzeile.
- **FN**: Goldzeile ohne Pipelinezeile.
- **Precision** = TP / (TP + FP), **Recall** = TP / (TP + FN).
- **Typquote** = gepaarte Zeilen mit gleichem `effect_type` / TP.
- **Wertquote** = gepaarte Zeilen mit Effekt innerhalb 1% / TP.
- **Poolbar** = Anteil der Pipelinezeilen mit `Database.POOLABLE`
  (`disputed=0`, kein `rejection_reason`, `quote_start >= 0`, SE oder KI).
- **Ausbeute** = poolbare Pipelinezeilen je annotiertem Volltext.

Die Ausbeute zaehlt nur Zeilen **annotierter** Dokumente; offene Dokumente
liefern keine Quote. `nur_akzeptiert` aendert die Poolbarkeit nicht, weil
die POOLABLE-Definition Verworfenes und Strittiges ohnehin ausschliesst.

Gepaart wird greedy nach Aehnlichkeit aus Outcome-Tokens, Vergleich,
Effekttyp und Wertnaehe; Schwelle 0.55. Das ist eine
nachvollziehbare Heuristik, kein semantisches Urteil. Dokumente ohne Zeile
und ohne Begruendung gelten als **offen** und werden nicht gewertet.

## Stand

Noch keine Annotation. Der Bericht ist eine Baseline ueber die Pipeline-Zeilen, keine Guetemessung.

Die Datei wird nach jeder Annotation neu erzeugt.
