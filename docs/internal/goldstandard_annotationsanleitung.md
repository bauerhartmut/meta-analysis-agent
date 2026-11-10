# Annotationsanleitung Goldstandard — Effektzeilen (v1.1, 2026-11-10)

Ziel: Ein unabhängiger, wiederholbarer Maßstab für die Effektgrößen-Extraktion.
Zwei Personen annotieren **dieselben 30 Dokumente getrennt**. Gemessen wird
gegen den Konsens, nicht gegen die Datenbank. v1.1 ergänzt den Grenzfall 5.11
(Spannweite über Zeitpunkte).

Das JSON-Schema steht in `docs/internal/goldstandard_schema.json`, ein
geprüftes Beispiel in `data/golden_effects/example_annotation.json`. Der
Formatprüfer ist `scripts/pruefe_goldstandard.py`.

---

## 1. Rollen und Blindheit

- **Annotator A** und **Annotator B** arbeiten unabhängig, ohne Austausch
  während der Annotation.
- **Blindheit:** Keine Einsicht in `study_effects`, Modellausgaben, frühere
  Extraktionen oder die Datei des anderen. Nur der Volltext, diese Anleitung
  und das Schema.
- **Konsens:** Nach Abschluss vergleicht eine dritte Person (oder A und B
  gemeinsam, erst nach Abgabe) Zeile für Zeile. Einigung wird dokumentiert;
  bleibt ein Konflikt, entscheidet ein dritter Annotator. Konflikte werden
  gezählt, nicht stillschweigend geglättet.
- **Einfrieren:** Nach der Abgabe wird die Datei per SHA-256 eingefroren
  (Ausgabe des Prüfskripts), committed und nicht mehr geändert. Korrekturen
  erzeugen eine neue Version mit neuem Datum.

---

## 2. Ablauf

1. Dokument im Volltext vollständig lesen (nicht nur Abstract).
2. Alle Stellen markieren, die einen **quantifizierten Effekt mit
   Unsicherheit** berichten — Fließtext, Tabelle, Abbildungsunterschrift.
3. Jede Stelle als eine Effektzeile erfassen (Definition unten).
4. Quote exakt kopieren und `quote_start`/`quote_end` bestimmen (die
   Prüfskript-Ausgabe zeigt die Abweichung, wenn der Span nicht passt).
5. Dokument abschließen: entweder Zeilen oder `no_effect_reason`.
6. Datei abgeben, Hash notieren, erst danach vergleichen.

**Regel gegen Optimierung:** Nicht raten, nicht ergänzen, nicht aus anderen
Tabellen rechnen. Was nicht dasteht, ist keine Zeile. Eine fehlende Zeile ist
ein echter Befund, keine Lücke, die man schließen muss.

---

## 3. Was ist eine Effektzeile?

Eine Zeile = **eine geschätzte Effektgröße** für genau eine Kombination aus:

- Outcome,
- Vergleich (Intervention vs. Kontrolle, Expositionsgruppe vs. Referenz),
- Zeitpunkt,
- Adjustierung (adjustiert vs. unadjustiert),
- Analysepopulation (Gesamt oder stratifiziert).

**Getrennte Zeilen** entstehen bei:

- mehreren Outcomes (Rezidiv, Mortalität, Fatigue),
- mehreren Kontrasten (hoch vs. niedrig, mittel vs. niedrig),
- mehreren Zeitpunkten (6 Monate, 12 Monate),
- mehreren Adjustierungsmodellen, wenn beide berichtet werden,
- mehreren Studienarmen (Dosis A, Dosis B), sofern je Arm ein eigener Effekt
  mit Unsicherheit steht,
- Subgruppen (Männer/Frauen), sofern getrennt berichtet.

**Keine eigene Zeile** sind:

- derselbe Effekt in zwei Darstellungen (Text und Tabelle) — einmal erfassen,
  die klarere Stelle als Quote wählen und in `notes` auf die Dopplung
  hinweisen,
- ein p-Wert ohne Effekt und ohne Unsicherheit,
- eine reine Beschreibung ohne Zahl,
- ein Review-Aggregat, das als solches erkannt wird: **eine** Zeile mit
  `is_primary: false` und `design_category: aggregate` (siehe 5.8).

---

## 4. Feldregeln

| Feld | Regel |
|---|---|
| `document_id` | Dateistamm des Volltexts ohne `.txt` |
| `title` | Titel wie im Dokument, nicht gekürzt |
| `year` | Erscheinungsjahr aus dem Dokument; `null`, wenn nicht erkennbar |
| `design_verbatim` | Designbezeichnung **wörtlich** aus dem Dokument |
| `design_category` | Zuordnung nach 5.1 |
| `stratum` | Auswahlschicht, aus der das Dokument stammt |
| `has_text_layer` | `true`, wenn der Text durchsuchbar ist; `false` bei reiner Bild-PDF |
| `effect_id` | `<document_id>-01`, `-02`, … in Lesereihenfolge |
| `outcome_verbatim` | Outcome **wörtlich** aus der Quelle |
| `outcome_normalized` | Vereinheitlicht (z. B. „Depressive symptoms", „Sleep onset latency") |
| `comparison_verbatim` | Vergleichsgruppe wörtlich |
| `effect_type` | `or`, `rr`, `hr`, `md`, `smd`, `g`, `beta`, `r`, `z`, `other` |
| `effect` | Zahl **wie berichtet**, nicht umgerechnet, nicht gerundet |
| `se` | Standardfehler, falls berichtet; sonst `null` |
| `ci_low`, `ci_high` | Grenzen wie berichtet; sonst `null` |
| `ci_level` | 0,95, wenn nicht anders angegeben; sonst der berichtete Wert |
| `n` | analysierte Stichprobe der Zeile, falls berichtet |
| `adjusted` | `true`/`false`, wenn erkennbar; `null` bei unklarer Angabe |
| `quote` | **exakter** Textausschnitt, der Effekt und Unsicherheit enthält |
| `quote_start`, `quote_end` | Zeichenpositionen im Volltext, `quote_end` exklusiv |
| `certainty` | `high` (Zahl und Unsicherheit eindeutig), `medium` (eine Angabe muss interpretiert werden), `low` (unklar, aber belegt) |
| `is_primary` | `false` nur für gepoolte Schätzer aus Übersichtsarbeiten |
| `notes` | Nur Beobachtungen zum Beleg, keine Bewertung |

**Nie umrechnen.** Kein Logarithmieren, kein Standardisieren, kein
Zusammenfassen. Umgerechnet wird später im Code, nachvollziehbar.

---

## 5. Entscheidungsregeln für Grenzfälle

### 5.1 Designzuordnung

| `design_category` | Erkennungsmerkmal |
|---|---|
| `parallel_rct` | randomisiert, parallele Gruppen |
| `crossover_rct` | randomisiert, within-subject, Crossover, repeated measures |
| `cluster_rct` | Randomisierung auf Cluster-Ebene |
| `quasi_experimental` | nicht randomisiert, Pretest-Posttest, natürliche Gruppe |
| `observational` | Kohorte, Fall-Kontroll, Querschnitt, Register |
| `aggregate` | Metaanalyse, systematische Übersicht, gepoolter Schätzer |
| `unknown` | Design nicht erkennbar |

Bei mehreren Merkmalen gilt das spezifischste (Crossover vor RCT, Cluster vor
RCT). Ein RCT, der über sich selbst berichtet, ist `parallel_rct`; eine
Metaanalyse über RCTs ist `aggregate`.

### 5.2 Ratio-Maße (OR, RR, HR)

- `effect` ist der berichtete Wert (z. B. 0,83), nicht der Logarithmus.
- `ci_low`/`ci_high` sind die berichteten Grenzen (0,70/0,99).
- `se` nur übernehmen, wenn sie **explizit** dasteht. Nicht aus dem KI
  ableiten — das macht der Code, und zwar dokumentiert.

### 5.3 Mittelwertsdifferenzen und standardisierte Maße

- `md` für Differenzen in Originaleinheiten (z. B. Punkte auf einer Skala).
- `smd`/`g` für standardisierte Differenzen; `g` nur, wenn Hedges g explizit
  genannt ist, sonst `smd`.
- Einheit in `notes` festhalten (z. B. „Punkte, PHQ-9").

### 5.4 Regressionskoeffizienten (`beta`)

- `beta` mit SE oder KI erfassen, Einheit und Skala in `notes`.
- Standardisierte und unstandardisierte Koeffizienten sind verschiedene
  Zeilen, wenn beide berichtet werden.

### 5.5 Korrelationen (`r`) und Fisher-z (`z`)

- `r` nur, wenn die Korrelation selbst berichtet ist; `z` nur, wenn
  Fisher-z dasteht.
- Ein KI auf r-Skala bleibt auf r-Skala. Nicht in z umrechnen.
- Nennt der Text eine Spannweite über Zeitpunkte (z. B. `rs=[a, b]`), gilt 5.11.

### 5.6 Median und Interquartilsabstand

Wenn nur Median und IQR berichtet sind und kein Mittelwert/SE: **keine
Effektzeile**, sondern `no_effect_reason` mit dem Hinweis „nur Median/IQR".
Die Umrechnung ist eine Modellannahme, keine Extraktion. (Falls das Projekt
sie später erlaubt, wird sie als eigene, markierte Zeile geführt.)

### 5.7 p-Wert ohne Effektgröße

Keine Zeile. `no_effect_reason`: „nur p-Wert, keine Effektgröße".

### 5.8 Übersichtsarbeiten

- Der gepoolte Schätzer ist **eine** Zeile mit `is_primary: false`,
  `design_category: aggregate`.
- Einzelstudien-Ergebnisse, die die Übersicht zitiert, werden **nicht**
  übernommen — sie gehören zur Primärstudie, nicht zu diesem Dokument.
- Wird die Übersicht selbst extrahiert (Kalibrierungsfall), ist die Zeile
  trotzdem korrekt annotiert; das Gate im Code entscheidet über den Pool.

### 5.9 Mehrere Arme und Dosis

Je Arm eine Zeile, wenn ein eigener Effekt mit Unsicherheit berichtet wird.
Ist nur ein gemeinsamer Effekt über Arme berichtet, ist es **eine** Zeile mit
`notes`: „gepoolt über Arme".

### 5.10 Negativkontrolle

Dokumente der Schicht `negative_control` haben keine erwartete Effektzeile.
`effects: []` und `no_effect_reason` mit Begründung (z. B. „nur deskriptive
Statistik", „Review ohne eigene Zahl", „nur p-Werte"). Eine trotzdem
gefundene Zeile wird erfasst — dann ist die Erwartung falsch, nicht die
Annotation.

### 5.11 Spannweite über Zeitpunkte

Nennt der Fließtext eine Spannweite über Zeitpunkte ("rs=[−0.150, −0.206]",
"range across T1-T3"), ist das **keine** einzelne Effektzeile: Die Einheit
verlangt einen Zeitpunkt (Abschnitt 3).

- **Tabelle oder Abbildung ist die Quelle**, wenn sie die Werte je Zeitpunkt
  auflöst. Je Zeitpunkt eine Zeile, mit `time_point` und Tabellenzitat.
- **Keine Tabelle und keine Auflösung:** keine Zeile raten.
  `no_effect_reason` mit "Spannweite ohne Zeitpunktauflösung"; die Spanne in
  `notes` nennen.
- Eine Spanne ist **kein KI**. `ci_low`/`ci_high` bleiben den berichteten
  Konfidenzgrenzen vorbehalten; Min/Max über Zeitpunkte gehören nicht hinein.
- Bei Korrelationen nennt `notes` das Zeitpunktpaar (z. B. "T3-PA × T1-EDS"),
  weil eine Korrelationsmatrix auch Kreuzkorrelationen enthält.
- Ist nur ein Zeitpunkt genannt und zusätzlich eine Spanne, gilt der genannte
  Zeitpunkt; die Spanne steht in `notes`.

**Beispiel `3790c91f96`:** Der Satz nennt PA × emotionale Symptome
`rs=[−0.150, −0.206]` und PA × körperliche Symptome `rs=[−0.225, −0.266]`.
Tabelle 2 löst auf: emotional T1 −0,17, T2 −0,206, T3 −0,199; körperlich
T1 −0,248, T2 −0,265, T3 −0,266. Das sind sechs Zeilen, nicht zwei. Die
Pipeline speicherte zwei emotionale Zeilen ohne `time_point` und keine
körperliche Zeile; der Abgleich wertet das als Recall-Lücke, nicht als
Matching-Fehler (siehe `goldstandard_entscheidung_3790c91f96.md`).

---

## 6. Quote und Positionen

- `quote` ist ein **exakter** Ausschnitt des Volltexts, keine Paraphrase,
  keine Auslassung mit „…".
- Der Ausschnitt muss Effekt **und** Unsicherheit enthalten, wenn beide
  dastehen. Bei Tabellenzeilen genügt die Zelle mit Effekt und KI/SE, sofern
  Outcome und Vergleich aus der Zeilenbeschriftung hervorgehen — beides in
  `notes` festhalten.
- `quote_start`/`quote_end` beziehen sich auf den gespeicherten Text
  (`data/fulltext/<id>.txt`), nicht auf das PDF.
- Das Prüfskript vergleicht `text[start:end] == quote` und meldet jede
  Abweichung. Ein fehlgeschlagener Vergleich ist ein Fehler, keine Warnung.

---

## 7. Qualitätskontrolle

1. Jede Datei läuft durch `scripts/pruefe_goldstandard.py` (Exit 0).
2. Der Prüfer meldet: fehlende Pflichtfelder, unbekannte Enum-Werte,
   Quote-Abweichung, Effekt außerhalb des KI, doppelte `effect_id`,
   Dokument ohne Zeile **und** ohne Begründung.
3. Nach der Vollannotation: Precision/Recall je Dokument und je Schicht;
   Kappa zwischen A und B. Unter **0,80** wird die Anleitung geschärft und
   die betroffene Schicht neu annotiert, bevor der Goldstandard gilt.
4. Der Konsens wird aus A und B gebildet, Konflikte mit dritter Stimme. Die
   Konsensdatei hat `annotator: "consensus"`.

---

## 8. Abgabe

**Probelauf (Format- und Ablauftest):** `scripts/erzeuge_annotationsgeruest.py`
legt die leeren Dateien an (drei Dokumente mit `probelauf: true`). Nach dem
Ausfüllen prüft `scripts/pruefe_probelauf_abgabe.py` Pflichtfelder, Quotes und
Design (Exit 0); eine Kappa-Zahl entsteht dabei nicht. Der Zeilen-Kappa wird
erst nach der Vollannotation aller 30 Dokumente mit
`scripts/werte_kappa_probe.py` (ohne `--probelauf`) gemessen; Schwelle 0,80.

- Dateinamen: `data/golden_effects/goldstandard_A.json`,
  `goldstandard_B.json`, `goldstandard_consensus.json`.
- Eine Datei enthält alle Dokumente des jeweiligen Annotators.
- Nach Abgabe: Hash notieren (`pruefe_goldstandard.py` gibt ihn aus), Datei
  committen, nicht mehr ändern.

---

## 9. Kurzcheck vor der Abgabe

- [ ] Jedes Dokument hat entweder Zeilen oder eine Begründung.
- [ ] Kein Effekt umgerechnet, keine Zahl gerundet.
- [ ] Jede Quote exakt, inklusive Bindestrichen und Gedankenstrichen.
- [ ] Ratio-Werte positiv, KI plausibel (`ci_low < effect < ci_high`).
- [ ] `is_primary: false` nur bei Übersichtsarbeiten.
- [ ] `design_category` nach 5.1, nicht nach Bauchgefühl.
- [ ] Spannweite über Zeitpunkte: je Zeitpunkt eine Zeile aus der Tabelle,
      `time_point` gesetzt (5.11).
- [ ] Prüfskript Exit 0, Hash notiert.
