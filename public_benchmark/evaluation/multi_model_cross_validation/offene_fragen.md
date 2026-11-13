# Offene Fragen: Multi-Model Cross-Validation

Stand: 2026-11-13
Bezug: [`experiment_plan.md`](experiment_plan.md)
Zweck: Entscheidungsblatt. Jede Frage blockiert einen konkreten Schritt. Ohne
Antwort auf F1-F3 ist kein Phase-0-Aufbau sinnvoll.

**Beantwortet am 2026-11-13.** Die Entscheidungen und der Umsetzungsstand stehen
in [`entscheidungen_20261113.md`](entscheidungen_20261113.md). Dieses Blatt
bleibt als Fragenstand erhalten und wird nicht nachträglich verändert.

Legende: **[empfohlen]** = Vorschlag aus dem Plan, mit Begründung.

---

## F1 - Welcher Datensatz?

**Warum:** Es gibt derzeit keinen Referenzdatensatz, der alle Bedingungen des
Auftrags erfüllt. Yun-Dev ist zu klein und am Ceiling, Yun-Test ist verbraucht,
P0 ist der G5-Holdout, Goldstandard A hat keine Armwerte.

**Optionen:**

- **A [empfohlen] - neues PMC-Set.** 25 Artikel aus dem vorhandenen
  September-2026-Frame (596 artikeldisjunkt, 415 für Volltext vorgemerkt),
  ohne die 30 G5-Shortlist-Artikel. Ziel 60-80 Armwert-Records.
  *Kosten:* eine vollständige menschliche Annotation. *Risiko:* Ausbeute je
  Artikel unbekannt, Reserveartikel nötig.
- **B - Goldstandard A armweise nachannotieren.** 30 Dokumente vorhanden und
  gehasht, aber 18 von 30 sind aggregat oder observational und es fehlen alle
  Armfelder. Kostet eine Vollerhebung auf ungeeigneten Designs.
- **C - Yun-Dev verwenden.** 26 Records, Qwen bereits 140/140. Kein
  Verbesserungsnachweis möglich, kein neuer Datensatz.
- **D - Andere Quelle vorgeben.**

**Antwort:** ______________________

---

## F2 - Wer annotiert die Referenz, und bis wann?

**Warum:** Phase D bewertet gegen menschliche Werte. Ohne eingefrorene Referenz
gibt es keine Genauigkeitsaussage; die Modelle dürfen die Referenz vorher nicht
sehen.

**Optionen:**

- **A [empfohlen] - eine Person (bauerhartmut), Vorlage abgeleitet aus
  `fulltext_extraction_template_v1.md`**, Zeitfenster vor dem ersten
  Modellaufruf.
- **B - zwei Personen, Konfliktlösung durch Dritte.** Höhere Belastbarkeit,
  deutlich mehr Aufwand.
- **C - auf den B-Rücklauf warten** (Kappa >= 0,80), dann annotieren. Verschiebt
  das Experiment, erhöht aber die Referenzqualität.

**Zusatzfrage:** Reicht eine Erstannotation, oder ist Kappa >= 0,80
Voraussetzung?

**Antwort:** ______________________

---

## F3 - GLM 5.3: reparieren oder ersetzen?

**Warum:** GLM liefert im vorhandenen Dev-Lauf 19 von 26 leeren Content und eine
abgeschnittene Antwort. Ohne Klärung ist das Experiment zweimodellig.

**Optionen:**

- **A [empfohlen] - ein diagnostischer Aufruf mit Freigabe.** Antwort
  vollständig protokollieren: `finish_reason`, `usage`, `reasoning_content`,
  `content`, Antwortlänge. Danach entscheiden, ob `max_tokens` oder das
  Response-Feld die Ursache ist.
- **B - GLM durch ein anderes verfügbares Modell ersetzen.**
- **C - als Zweimodell-Vergleich deklarieren** (Qwen + DeepSeek) und GLM aus
  dem Auftrag streichen.

**Antwort:** ______________________

---

## F4 - Schema um Belege je Zahl erweitern?

**Warum:** Das v6-Schema liefert nur eine `source_note`. Die Konfliktkategorien
5 (gleicher Wert, andere Quelle) und 6 (gleiche Zahl, andere Zuordnung zu Arm,
Outcome oder Zeitpunkt) sind damit nicht bestimmbar.

**Optionen:**

- **A [empfohlen] - `schema_v1.json` mit Seite, Tabelle/Abschnitt,
  Originalkontext, Einheit und Zuordnungssicherheit je Zahl.**
- **B - beim bestehenden Schema bleiben** und Kategorien 5/6 als "nicht
  messbar" berichten.

**Antwort:** ______________________

---

## F5 - Wer adjudiziert?

**Warum:** Qwen 3.5 ist Arm A und soll gleichzeitig richten. Das erzeugt
Selbstpräferenz; ohne Verblindung misst man Modelltreue, nicht Genauigkeit.

**Optionen:**

- **A [empfohlen] - Qwen wie gefordert, Kandidaten als `candidate_1..3`
  verblindet**, Zuordnungstabelle getrennt, Selbstwahlquote im Bericht.
- **B - viertes, unbeteiligtes Modell als Adjudikator.** Sauberer, aber nicht
  der beauftragte Aufbau.
- **C - beide Varianten**, Qwen als Primär und ein Viertes als Kontrolle.

**Antwort:** ______________________

---

## F6 - Wie groß muss die Stichprobe sein?

**Warum:** Bei 60-80 Records und 6-8 Feldern je Record sind nur größere
Differenzen statistisch entscheidbar. Ohne vorab dokumentierte Power-Abschätzung
wird ein Nullergebnis später als "kein Unterschied" fehlgedeutet.

**Optionen:**

- **A [empfohlen] - Power-Abschätzung vor dem Einfrieren rechnen und die
  kleinste nachweisbare Differenz im Bericht nennen.**
- **B - Stichprobe auf 100+ Records erhöhen** (mehr Annotation).
- **C - auf Signifikanztests verzichten**, nur deskriptiv berichten.

**Antwort:** ______________________

---

## Nicht verhandelbar (keine Frage, nur Erinnerung)

- Yun-Test (249 Records) wird nicht verwendet.
- Die 30 G5-Shortlist-Artikel bleiben G5-reserviert.
- Keine Modellantwort wird überschrieben; `unresolved` ist ein gültiges
  Ergebnis; unaufgelöste Konflikte gehen nicht ins Pooling.
- Kein Modellaufruf vor `freeze.json`.

## Nächster Schritt nach Beantwortung

F1 und F2 beantworten, dann Phase 0 aufsetzen: `dataset_manifest.json`,
`reference.jsonl`, `prompt_v1.md`, `schema_v1.json`, `freeze.json`.
