# Referenzannotation: Workflow v1

Stand: 2026-11-13
Bezug: [`schema_v1.json`](schema_v1.json), [`candidate_shortlist_v2.json`](candidate_shortlist_v2.json)
Status: **vorbereitet, nicht gestartet** - es existiert keine menschliche Annotation

## 1. Zweck

Die Referenz ist der einzige Maßstab, gegen den die Modelle bewertet werden.
Sie muss unabhängig von den Modellen entstehen, vor dem ersten Modellaufruf
vollständig sein und nach dem Einfrieren unverändert bleiben.

## 2. Rollen

| Rolle | Aufgabe | Voraussetzung |
|---|---|---|
| Annotator A | vollständige Armwerte für alle 25 Artikel | klinisch oder methodisch geschult, Erfahrung mit RCT-Tabellen, sicher in Englisch |
| Annotator B | dieselben 25 Artikel, unabhängig, ohne Sicht auf A | dieselbe Qualifikation, keine Einsicht in A-Dateien oder Modellausgaben |
| Schlichter/in (dritte Person) | Auflösung verbleibender Konflikte anhand der Originalquelle | fachlich gleichwertig, sieht beide Annotationen und die Quelle |
| Projektleitung | Freigabe, Versionierung, Einfrieren | dokumentiert Freigabe mit Datum und Hash |

Mindestqualifikation: Interpretation von Mean/SD, SE, 95%-KI, Ereigniszahlen,
Per-Protocol- versus Intention-to-Treat-Populationen, Post-Test versus
Follow-up. Wer diese Begriffe nicht sicher zuordnet, annotiert nicht.

## 3. Was tatsächlich geprüft werden muss

Je Artikel und je Outcome-Zeile:

1. **Arme:** Welche Gruppen sind Interventions- und Kontrollarm? Gibt es
   Mehrarm-Designs, und welche zwei Arme gehören zum Vergleich?
2. **Fallzahl:** n je Arm aus derselben Population wie der Outcome-Wert
   (nicht die randomisierte Zahl, wenn der Wert nur für Per-Protocol gilt).
3. **Werte:** Mittelwert und Streuung (SD, SE oder 95%-KI mit Angabe, was
   berichtet ist), oder Ereignisse und Nenner.
4. **Zeitpunkt:** Post-Test, Follow-up, mehrere Zeitpunkte; Baseline ist kein
   Behandlungseffekt.
5. **Beleg:** Seite, Tabelle oder Abschnitt, Spalte/Zeile, wörtlicher Kontext.
6. **Zuordnungssicherheit:** hoch, mittel, niedrig, mit Begründung bei niedrig.
7. **Supplement:** nur wenn der Haupttext den Wert nicht enthält; dann
   Supplementtabelle als Quelle nennen.

Keine Schätzung, keine Umrechnung ohne berichtete Grundlage, keine Imputation,
kein Auffüllen aus dem Modelloutput.

## 4. Ablauf

| Schritt | Artefakt | Regel |
|---|---|---|
| 1 | `annotation_A_v1.jsonl`, `annotation_B_v1.jsonl` | dieselben 25 Artikel, gleiche Schema-Version, getrennte Ablage |
| 2 | je Person ein Hash | `sha256` beim Abschluss, vor jedem Vergleich |
| 3 | `reference_diff_v1.json` | deterministischer Vergleich je Record, Feld und Zahl |
| 4 | `reference_conflicts_v1.jsonl` | alle Abweichungen, ohne Auflösung |
| 5 | `reference_adjudication_v1.jsonl` | Schlichter/in entscheidet je Konflikt mit Quelle |
| 6 | `reference_v1.jsonl` | konsolidierte Referenz, gegen `schema_v1.json` validiert |
| 7 | `reference_manifest_v1.json` | Hash, Datum, Annotatoren, offene Fälle, Status |

Verbindlich:

- Vor Schritt 3 sieht keine Person die Datei der anderen.
- Vor Schritt 6 sieht niemand Modellausgaben.
- Nach Schritt 7 ist die Referenz eingefroren; Änderungen nur als
  `reference_v2` mit eigenem Manifest und Begründung.

## 5. Vergleich und Konflikte

Der Vergleich ist deterministisch und modellfrei: pro Record und Feld werden
Werte mit Toleranz 0 verglichen (nach Normierung von Dezimalkomma und
Einheiten). Jede Abweichung wird als Konflikt geführt, auch wenn nur die
Belegstelle abweicht. Konflikte werden nach Quelle entschieden, nicht nach
Mehrheit und nicht nach Plausibilität.

Metriken zwischen A und B (deskriptiv, kein Gate):

- exakte Übereinstimmung je Feld,
- mittlere absolute Differenz je numerischem Feld,
- ICC(2,1) für kontinuierliche Werte,
- Cohen's Kappa nur für kategoriale Felder (Zeitpunkt, Armzuordnung),
- Anteil Felder, die nur eine Person gefüllt hat.

Ein Kappa-Schwellenwert ist **keine** Voraussetzung. Die Entscheidung fällt
über die Konfliktauflösung an der Quelle.

## 6. Eine Person statt zwei

Ist keine zweite qualifizierte Person verfügbar:

- Die Referenz heißt `reference_preliminary_v1.jsonl`.
- Das Manifest trägt `independent_second_annotator: false`.
- Die Auswertung weist die Einschränkung im Ergebnisteil aus und darf nicht
  von "validierter Referenz" sprechen.
- Ein späterer B-Rücklauf erzeugt eine neue Version, keine stille Korrektur.

## 7. Aufwand

Für 25 Artikel und geschätzt 60-80 Records mit je 4-8 Zahlenfeldern sind
600-900 Einzelwerte zu prüfen, dazu Belegstellen. Die Erfahrung aus dem
Goldstandard-A-Lauf (30 Dokumente, 69 Effektzeilen) zeigt, dass die
Quellenprüfung, nicht das Eintippen, die Zeit kostet.

## 8. Was dieser Workflow ausdrücklich nicht tut

- Er simuliert keine Annotation und ersetzt sie nicht durch Modellausgaben.
- Er übernimmt keinen Modellkonsens als Wahrheit.
- Er ändert die eingefrorene Artikelauswahl nicht.
