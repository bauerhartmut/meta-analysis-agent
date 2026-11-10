# Versuchsplan Kalibrierungslauf — Entscheidungsvorlage (2026-11-10)

Status: **Plan, keine Modellaufrufe gestartet.** Freigabe offen.
Grundgesamtheit: 1 291 Volltexte in `data/fulltext/`, davon 199 mit mindestens
einer gespeicherten Effektzeile. Alle Zahlen unten sind aus DB, Log oder
`data/baseline/` abgeleitet; Schätzungen sind als solche markiert.

---

## 1. Korrektur meiner Call-Schätzung

Meine Angabe „200–400 Calls" war eine grobe Schätzung ohne Rechnung. Die
belegte Rechnung sieht so aus:

| Größe | Wert | Quelle |
|---|---:|---|
| Baseline gesamt | 17 628 Calls | `data/baseline/exercise-bbb324-metrics.json` |
| Baseline Volltexte | 293 | ebd. |
| **Calls pro Volltext (gesamter Zyklus)** | **60,2** | 17 628 / 293 |
| Tokens pro Call (gesamt) | 1 434 | 25,3 Mio / 17 628 |
| Phase `working` (Volltext-/Extraktionsarbeit) | 2 938 Calls, 1 961 Tokens/Call | `data/research-usage.db`, 27.10.–05.11. |
| Phase `analyzing` | 4 497 Calls, 2 047 Tokens/Call | ebd. |
| Phase `critiquing` | 7 731 Calls, 731 Tokens/Call | ebd. |

**Die 60 Calls pro Volltext sind der gesamte Zyklus** — Suche, Screening,
Fakten, Hypothesen, Kritik, Extraktion. Ein Kalibrierungslauf macht davon nur
Volltext + Extraktion + Qualitätskontrolle. Aus der `working`-Phase ergibt sich
rund **10 Calls pro Volltext** für die Dokumentarbeit; mit Doppellesung und
Nachbesserung rechne ich mit **15–20 Calls pro Dokument**.

Damit: **12 Dokumente × 20 = 240 Calls**, harte Obergrenze **400 Calls**. Die
Hochrechnung „60 × 12 = 720" gilt für einen vollen Forschungszyklus, nicht für
diesen Extraktionstest.

**Tokens:** 240 × ~1 960 ≈ **0,47 Mio**, Deckel **0,8 Mio** Tokens
(400 × 2 000).

**Monetäre Kosten:** TUDaGPT ist ein institutionelles Backend; einen Tarif
kenne ich nicht und erfinde keinen. Die Umrechnung ist
`Tokens / 1 000 000 × Tarif`. Bitte den Tarif nennen, dann steht die Zahl im
Plan; bis dahin ist das Budget in Calls und Tokens verbindlich.

---

## 2. Goldstandard: 30 Dokumente, unabhängig annotiert

### Auswahl

Geschichtet aus den 1 291 Volltexten, **nicht** aus den Modellergebnissen:

| Schicht | Anzahl | Kriterium |
|---|---:|---|
| Parallel-RCT | 6 | Designlabel RCT, Intervention vs. Kontrolle |
| Crossover/Within-subject | 3 | `crossover|within|paired` im Design |
| Prospektive Kohorte | 7 | Kohorte, Inzidenz/Verlauf |
| Querschnitt/Fall-Kontroll | 5 | Prävalenz, Odds Ratio |
| Übersichtsarbeit (Aggregat) | 4 | „meta-analysis/systematic review" im Design |
| **Dokumente ohne erwartete Effektzeile** | **5** | falsch-positive Kontrolle |
| **Summe** | **30** | |

Layout-Schichtung: mindestens 8 Dokumente mit Tabellen-Captions
(`^Table N.`), mindestens 3 ohne Textebene (Vision-Pfad), mindestens 5 mit
Fließtext-Effekten. Effekttypen: OR, RR, HR, MD, SMD/g, beta, r — jede
Kategorie mindestens 2 Dokumente.

### Annotation

1. **Zwei unabhängige Annotatoren** (Mensch), dieselbe Anleitung, kein Zugriff
   auf DB-Zeilen oder Modellausgaben.
2. Pro Effektzeile: Outcome, Vergleich, Effekttyp, Effekt, SE oder KI,
   Design, Quote-Span (Start/Ende), Seite/Abschnitt.
3. Konflikt → dritter Annotator, Mehrheit; Konflikte werden gezählt, nicht
   geglättet.
4. **Einfrieren vor dem Lauf:** Goldstandard als JSON mit SHA-256-Hash,
   committed, danach unverändert. Der Kalibrierungslauf liest ihn nicht.
5. Inter-Annotator-Kappa wird berichtet; unter 0,80 ist der Goldstandard
   selbst zu prüfen, bevor er als Maßstab dient.

---

## 3. Die zwölf Dokumente für den Kalibrierungslauf

Ausgewählt aus den 199 Volltexten mit Effektzeilen (Stratifikation nach
Design, Layout, Effekttyp), keines im bestehenden Goldset. Die alten DB-Zeilen
dienen **nur der Auswahl**, nicht als Referenz — der Maßstab ist die neue
Annotation.

| # | Datei (Anfang) | Design | Typen | Layout | Zeichen | Warum |
|---|---|---|---|---:|---:|---|
| 1 | `7111ea9787` | Kohorte | or, rr | Text | 97 367 | größter Fall, zwei Ratio-Typen |
| 2 | `3134fdc8c3` | Kohorte | rr | Text | 85 910 | RR ohne OR, Ultra-processed food |
| 3 | `d0bec407a2` | Kohorte | hr | Text | 3 199 | HR, kleines Dokument (Billigfall) |
| 4 | `bb9218735f` | Parallel-RCT | z | Text | 71 085 | RCT mit Fisher-z |
| 5 | `fb484d488b` | Parallel-RCT | g | Text | 9 659 | kleiner RCT, Hedges g |
| 6 | `3bbb142c71` | Crossover | (leer/other) | Text | 40 445 | testet die Effekttyp-Erkennung |
| 7 | `87079ba88a` | Crossover | mean_diff | Text | 38 131 | Crossover + MD |
| 8 | `2c7ab4d124` | Querschnitt | or | **3 Captions** | 39 970 | Tabelle + OR |
| 9 | `09843d40d3` | Längsschnitt | beta | **3 Captions** | 65 491 | Tabelle + beta |
| 10 | `334f5f6798` | Übersicht | smd | Text | 79 745 | Aggregat-Gate + SMD |
| 11 | `203c831dbe` | Übersicht | hr | Text | 114 459 | Aggregat-Gate, bereits geprüfter Fall |
| 12 | `2675c25aab` | Querschnitt | r | **6 Captions** | 55 267 | Korrelation + stärkstes Tabellenlayout |

**Reserve** (bei Ausfall): `33a2bd3187` (beta), `b3c35c1d63` (MD, 3 Captions),
`3561d107ac` (beta, klein), `4f4c7daf4b` (RR).

**Technischer Hinweis:** Die zwölf Dokumente liegen bereits in Themen-DBs. Für
den Lauf wird eine **frische Kalibrierungs-DB** mit den zwölf Quellen und
Volltexten angelegt, `study_effects` bleibt leer, die Extraktion wird
erzwungen. Sonst würde der Resume-Pfad die alten Zeilen wiederverwenden und
nichts gemessen.

---

## 4. Was seit der Baseline tatsächlich getestet wird

| Änderung | Commit | Erwartete Wirkung |
|---|---|---|
| Effekttyp-Erkennung / `effects`-Hülle | `a3ffeaa`, `0cd0920`, `26063fb` | behebt „unbekannter Effekttyp '(leer)'" (13 Baseline-Zeilen) |
| Doppelpass-Dedup nur bei echten Zwillingen | `f5eb24b`, `3660d2c` | weniger falsche Verwürfe, Herkunft belegt |
| Prüfspur im Bericht | `325a9c3` | Sichtbarkeit, keine Pool-Änderung |
| Beleglose Zwilling-Schlüssel gehärtet | `3660d2c` | keine falschen Kopien mehr |
| SE-Skalen-Konvention geprüft | `8e3f21e` | keine Änderung nötig (Ratio-SE linear, KI gewinnt) |

**Nicht** getestet werden in diesem Lauf: Suche, Screening, Hypothesen,
Kritik, Statistik. Die sind nicht der Engpass.

---

## 5. Erfolgskriterien

| Kriterium | Technischer Erfolg | Wissenschaftliche Freigabe |
|---|---:|---:|
| Lauf ohne manuellen Eingriff (12/12 Dokumente) | ja | ja |
| Precision (Zeilen im Goldstandard) | ≥ 0,80 | ≥ 0,90 |
| Recall | ≥ 0,55 | ≥ 0,70 |
| Quote-Treue `text_verbatim` | 100 % | 100 % |
| Effekttyp korrekt | ≥ 85 % | ≥ 95 % |
| Anteil poolbarer Zeilen | ≥ 50 % | ≥ 60 % |
| Ausbeute poolbare Zeilen/Volltext | ≥ 1,0 | ≥ 1,5 |
| Inter-Annotator-Kappa | — | ≥ 0,80 |
| Keine Design-Kategorie unter Precision 0,80 | — | ja |

Der technische Erfolg erlaubt die **Erweiterung des Goldstandards auf 30
Dokumente und einen Themenlauf mit 100–150 Volltexten**. Die wissenschaftliche
Freigabe erlaubt den großen Durchlauf. Beides ist bewusst getrennt: Ein
technisch sauberer Lauf mit Precision 0,82 ist noch keine Forschungsgrundlage.

---

## 6. Erwartetes Ergebnis und Konsequenzen

**Erwartung (Schätzung, nicht Messung):** Ausbeute steigt von 0,44 auf
**1,2–1,8 poolbare Zeilen/Volltext**; Effekttyp-Fehler unter 5 %; Precision
0,80–0,90; mindestens ein Dokument liefert eine Vision-/Tabellenzeile.

**Bei Erfolg:**
1. Goldstandard auf 30 Dokumente erweitern (2–3 Tage Annotation).
2. Themenlauf mit 100–150 Volltexten, Budget 3 000–4 000 Calls.
3. Danach erster vollständiger Durchlauf mit Bericht.

**Bei Misserfolg:**
1. Keine weiteren Datenintegritäts-Audits.
2. Ursache isolieren: Chunking, Prompt, Tabellenpfad, Typ-Erkennung.
3. Maximal **zwei** Nachbesserungsrunden mit je 240 Calls; danach
   Architektur-Review der Extraktion, keine weitere Kalibrierung.

**Iterationsgrenze:** **drei Runden insgesamt** (Start + zwei Nachbesserungen).
Wenn nach Runde 3 weder Precision noch Ausbeute steigen, ist das Problem
strukturell (Dokumentzerlegung/Tabellen), nicht kalibrierbar.

---

## 7. Unterbrechbarkeit und Abbruch

- **Call-Deckel:** 400. **Token-Deckel:** 0,8 Mio. **Zeitdeckel:** 4 h.
- Abbruch bei > 20 % fehlgeschlagener Calls oder wenn ein Dokument dreimal
  hintereinander am selben Schritt scheitert.
- `SIGINT` schreibt den Closing-Report (im 73-h-Lauf erprobt); Resume ist
  vorhanden, wird im Kalibrierungslauf aber bewusst **nicht** genutzt, damit
  jede Zeile aus diesem Lauf stammt.

---

## 8. Offene Freigaben

1. **Call-/Token-Budget** (240 Calls / 0,47 Mio Tokens geplant, Deckel 400 /
   0,8 Mio) — Freigabe?
2. **Tarif** für die monetäre Umrechnung, falls eine Zahl im Plan stehen soll.
3. **Goldstandard**: 30 Dokumente parallel annotieren (empfohlen) oder erst
   nach dem Kalibrierungslauf?
4. **Annotatoren**: Wer annotiert die zweite Lesung? Ohne unabhängige zweite
   Annotation ist die Precision-Zahl nicht belastbar.

Ohne Punkt 4 bleibt der Lauf ein technischer Test, keine wissenschaftliche
Freigabe.
