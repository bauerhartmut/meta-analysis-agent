# Eignung der drei Probelauf-Dokumente für einen Zeilen-Kappa (2026-11-10)

## Befund

| Dokument | Design | Pipeline-Zeilen | Erwartete Goldzeilen | Begründung |
|---|---|---|---|---|
| `7111ea9787` | aggregate / narrative review | 7 | 0 | 5.8: Einzelstudien nicht übernehmen; kein eigener gepoolter Schätzer |
| `bb9218735f` | parallel_rct | 3 | 0 | 5.7: Mittelwerte ± SD und p-Werte, keine KI/SE |
| `203c831dbe` | aggregate / systematic review and meta-analysis | 1 | 2 | zwei gepoolte Schätzer (HR und MD); die Pipeline hat nur eine Zeile |
| **Summe** | | **11** | **2** | |

Die erwarteten Goldzeilen sind eine **Einschätzung** aus den Designprüfungen,
keine Annotation. Pipeline-Zeilen sind extrahierte Zeilen, kein Goldstandard;
die Goldannotation kann mehr oder weniger finden.

## Warum zwei Zeilen zu wenig sind

Ein Zeilen-Kappa mit Schwelle 0,80 braucht genügend gemeinsame Schlüssel.
Bei zwei Zeilen kann ein einziger Konflikt den Wert unter die Schwelle
drücken; das ist keine Messung, sondern ein Einzelfall. Der gesamte Korpus
hat 37 Pipeline-Zeilen auf 30 Dokumente; das größte Einzeldokument hat 7
(7111ea, narrativ), die meisten 1–2. Ein einzelnes Ersatzdokument mit 8–12
klaren Zeilen gibt es im Korpus nicht.

## Optionen

1. **Probelauf als Format- und Ablauftest** deklarieren: Pflichtfelder,
   Quotes, Design, Abgabe-Prüfer. Der Zeilen-Kappa wird auf die
   Vollannotation verschoben. Kein zusätzlicher Annotationsaufwand; die
   Aussage ist ehrlich, aber es gibt noch keine Kappa-Zahl.
2. **Kappa über mehrere Dokumente**: sechs Dokumente mit je 2 Pipeline-Zeilen
   (3134, fb484, 334f, b5e49, cfc6, d0bec) ergeben 12 Pipeline-Zeilen und
   erwartet 8–12 Goldzeilen. Das kostet sechs Annotationen, liefert aber
   einen belastbaren Zeilen-Kappa.
3. **Ein Ersatzdokument allein** reicht nicht: Es bringt höchstens 2 Zeilen,
   damit käme man auf 4.

## Kandidaten für Option 2

| Dokument | Schicht | Design | Pipeline-Zeilen | db_effect_rows |
|---|---|---|---|---|
| `3134fdc8c3` | cohort | observational | 2 | 2 |
| `fb484d488b` | rct | parallel_rct | 2 | 2 |
| `334f5f6798` | aggregate | aggregate | 2 | 2 |
| `b5e492009e` | rct | parallel_rct | 2 | 2 |
| `cfc6567ca3` | aggregate | aggregate | 2 | 2 |
| `d0bec407a2` | cohort | observational | 2 | 2 |

Die sechs Dokumente decken Kohorte, RCT und Aggregat ab. Die erwarteten
8–12 Goldzeilen sind eine Schätzung aus den Pipeline-Zahlen, keine
Annotation.

## Vorschlag

**Option 1**, solange die Vollannotation nicht freigegeben ist: Der
Probelauf prüft das Format und den Ablauf, nicht die Interrater-Reliabilität.
Wenn vor der Vollannotation ein Kappa nötig ist, **Option 2** mit den sechs
Dokumenten.

## Prüfung

- Pipeline-Zahlen aus `data/golden_effects/abgleich_pipeline.json`
  (30 Dokumente).
- Erwartete Goldzeilen aus den Designprüfungen 7111ea, bb921 und 203c.
- Keine Modellaufrufe, keine Annotation; A und B bleiben leer.
