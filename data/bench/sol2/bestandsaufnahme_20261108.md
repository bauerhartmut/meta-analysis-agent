# Bestandsaufnahme: was wissenschaftlich herausgekommen ist

Stand: 2026-11-08. Diese Datei beantwortet vier Fragen: was tatsächlich getan
wurde, was der Forschungsstand ist, was die Arbeit rechtfertigt und was als
Nächstes zu tun ist. Jede Zahl nennt ihre Quelldatei; geschätzt wird nichts.

## Kurzfassung vorweg

Wissenschaftlich herausgekommen ist **eine Studie mit zwei Zeilen - und beide
Zeilen sind dieselbe Studie, zweimal gemessen**. Alles andere war
Infrastruktur, Diagnose und Dokumentation. Die früher genannte Zahl "34
gelesene Volltexte" war irreführend: daraus wurde keine Studienzeile
extrahiert.

---

# Aufgabe 1 - Was tatsächlich gemacht wurde

## Gelesene Dokumente

| Was | Anzahl | Beleg |
|---|---:|---|
| PMC-Volltexte (XML) aus dem Q2-Abzug | 31 | `extended.json` (`documents_total: 31`), `xml/` 31 Dateien |
| davon nach Titelscreening als Melatonin-Studie gescreent | 20 | `extended.json` (`screened_in: 20`) |
| Textdateien für die Normalisierungs-Regression | 34 | `fulltext/*.txt`, 997.366 Zeichen; 31 mit PMC-ID im Kopf, alle 31 XML abgedeckt |
| Bestellte PDFs gelesen | **0** | `volltext/` enthält nur `.gitkeep` |
| Dokumente ohne Volltext, ungelesen | 83 | `zugangsliste_20261108.csv` |

Die 34 Textdateien wurden **nicht** auf Effekte gelesen. Sie dienten
ausschließlich dem Test, ob die Textnormalisierung Sätze und Tabellen
zerstört. Daraus entstand kein Studienbefund.

## Wissenschaftlich ausgewertete Studien

**Genau eine:** PMC3489506, Gringras et al. 2012, *BMJ*,
doi:10.1136/bmj.e6664 - placebokontrollierte RCT, Kinder mit
Entwicklungsstörungen, 12 Wochen. Aus dieser Studie zwei Zeilen:

| Zeile | Melatonin | Placebo | g | SE | n |
|---|---|---|---:|---:|---:|
| Einschaflatenz, Schlaftagebuch | 54,8 ± 51,9 (n=54) | 92,4 ± 63,0 (n=59) | −0,644 | 0,193 | 113 |
| Einschaflatenz, Aktigraphie | 68,4 ± 41,0 (n=24) | 104,1 ± 59,5 (n=25) | −0,685 | 0,294 | 49 |

Beleg: `extended.json` → `documents[7].effects`, jeweils mit wörtlichem
Zitat. **Das sind keine zwei Studien**, sondern zwei Messmethoden derselben
Population (Tagebuch und Aktigraphie, Tabelle 3). Für ein Pooling zählt das
als eine Studie; für eine Metaanalyse müsste festgelegt werden, welche
Erhebung der primäre Endpunkt ist.

## Extrahierte Daten, die nicht verwertbar waren

| Extraktion | Zeilen | Ergebnis | Beleg |
|---|---:|---|---|
| Arm-Zeilen erster Durchgang | 13 | **11 davon Baseline-Merkmale** (Alter, Geschlecht, BMI, PSQI), z. B. g = 0,004 für "Male, n (%)" | `arm_level.md` |
| Direkte Effektspalten | 16 gespeichert | **0 auf der Einschaflatenz** | `direct.json` |
| Fließtext-Leser | 4.733 Sätze | 0 Kandidaten, 0 gespeichert | `text_arms.json` |
| Zweiter Durchgang (Screening, Klammer-SD, Zeitpunkte) | 2 | **2 Zeilen SOL** | `extended.json` |

## Berechnungen

- Hedges g für die zwei Zeilen. Gegenprobe: 54,8 vs. 92,4 bei gepoolter SD
  ≈ 58 ergibt g ≈ −0,64; der gespeicherte Wert −0,644 ist plausibel.
- **Kein Pooling.** k = 1; kein gepoolter Wert, kein CI, kein I².
- Binomialrechnung zur Erfolgsschwelle (p = 0,20): k ≥ 5 aus fünf Artikeln
  unter 1 %, aus 25 Dokumenten rund 58 % (`schwelle_k5_20261108.md`).
- Technische Regression: 34 Dateien, 0 veränderte Ziffernfolgen, 0 verlorene
  Tabellenzeilen (`normalisierung_echte_texte_20261108.md`).

## Echt vs. Simulation vs. Technik

| Kategorie | Was | Beleg |
|---|---|---|
| **Echtes wissenschaftliches Ergebnis** | k = 1; g = −0,644 / −0,685 aus PMC3489506; 9 Dokumente mit SOL-Zeilen, davon 4 Crossover | `extended.json`, `schwelle_analyse.json` |
| **Diagnose (empirisch, aber kein Effekt)** | 0 von 7 SOL-Zeilen mit CI-Kopf (von 30 gescreenten) mit genanntem Effektwort; 4 von 9 Dokumenten Crossover; 11 von 13 Arm-Zeilen Baseline | `ergebnis_direkte_effekte_20261108.md`, `arm_level.md` |
| **Simulation** | `probelauf/` k = 3, `probelauf_bindestrich/` k = 1, Prüf-Lieferung k = 4 - alle aus synthetischen PDFs | `probelauf/*.json`, `triage_pruefung_20261108.md` |
| **Reine Technik** | Triage, Plausibilitätsprüfung, Normalisierung, Test-PDFs, Warteliste, Bestellmail, Stand-Dokumente | Commits `6d9812c` … `0c53c89` |

---

# Aufgabe 2 - Der tatsächliche Forschungsstand

## Von 114 Treffern zu einer poolbaren Studie

| Stufe | Anzahl | Quelle |
|---|---:|---|
| Q2-Suchtreffer | 114 | `manifest_q2.json` |
| mit PMC-Volltext gelesen | 31 | `extended.json` |
| nach Titelscreening Melatonin-Studie | 20 | `extended.json` |
| mit Einschaflatenz-Zeilen | 9 | `schwelle_analyse.json` (`docs_with_sol: 9`), 83 Zeilen |
| davon Crossover (nicht poolbar mit SE(g)) | 4 | PMC12903794, PMC4425994, PMC4365553, PMC11103136 |
| davon Parallelstudien | 5 | — |
| davon mit poolbarer Zeile | **1** | PMC3489506 |
| ohne Volltext, ungelesen | 83 | `zugangsliste_20261108.csv` |

**Unstimmigkeit, die hier nicht aufgelöst wird:** `bewertung_q2_20261108.md`
nennt 17 von 31 Titeln als "keine Melatonin-Studie" (also 14 gescreent),
`extended.json` nennt 20 gescreent. Zwei Screening-Versionen, nicht
abgeglichen. Für die Aussage k = 1 unerheblich, für die Nachvollziehbarkeit
nicht.

## Ausgeschlossen und warum

| Grund | Dokumente | Beleg |
|---|---:|---|
| Kein Mittelwert mit eindeutiger Streuung in zwei Spalten | 7 | `extended.json` → `reasons` je Dokument |
| Nicht genau zwei Spalten mit Mittelwert und Streuung | 4 | ebd. |
| Zu wenige Spalten | 2 | ebd. |
| Median/IQR statt Mittelwert mit SD/SE/CI | 1 | ebd. |
| Crossover: n je Arm nicht unabhängig | 1 | ebd. |
| Gemischte Zeitpunkte (Baseline und Follow-up) | 1 | ebd. |
| Keine SOL-Zeile im Dokument | 11 | ebd. |

Die vier offenen Parallelstudien im Einzelnen:

- **PMC2933606** - prolonged-release Melatonin, 21 SOL-Zeilen,
  Klammerformat und zwei Skalen in einer Tabelle.
- **PMC2952772** - Dosisfindung, mehrere Arme, 24 Zeilen.
- **PMC5774131** - Effekt als Verhältnis 1,37, keine Minutendifferenz.
- **PMC10131443** - ein Wert je Arm ohne Streuung.

## Vorhandene Effektstärken

| Studie | Endpunkt | Effekt | Quelle |
|---|---|---|---|
| PMC3489506 | SOL Tagebuch, unadjustiert | g = −0,644 (SE 0,193, n = 113) | eigene Rechnung, `extended.json` |
| PMC3489506 | SOL Aktigraphie, unadjustiert | g = −0,685 (SE 0,294, n = 49) | ebd. |
| PMC3489506 | SOL Tagebuch, adjustiert (Studienangabe) | **−37,5 min (95 % CI −55,3 bis −19,7)** | Zitat in `extended.json`: "−37.5 (−55.3 to −19.7)" |
| PMC3489506 | SOL Aktigraphie, adjustiert (Studienangabe) | **−45,3 min (95 % CI −68,8 bis −21,9)** | ebd. |

Die adjustierten Werte sind die belastbareren: Sie kontrollieren Baseline und
Stratifizierung. Die g-Werte nutzen Week-12-Mittelwerte und sind unadjustiert -
rechnerisch korrekt, aber nicht dasselbe wie der Studienbefund.

## Was momentan vertreten werden kann

**Vertretbar:** "Eine placebokontrollierte RCT an 113 Kindern mit
Entwicklungsstörungen zeigt unter Melatonin eine um 37,5 Minuten kürzere
Einschaflatenz als Placebo (adjustierte Differenz, 95 % CI −55,3 bis −19,7;
Aktigraphie: −45,3 min, CI −68,8 bis −21,9)."

**Nicht vertretbar:** jede gepoolte Schätzung, jeder Vergleich mit der
Referenz-CI −9,75 bis −4,37 min, jede Aussage der Form "Melatonin wirkt im
Mittel um X Minuten". Dafür fehlt die zweite unabhängige Studie.

**Offen, nicht widerlegt:** Ob die 83 ungelesenen Dokumente die Daten
enthalten. k = 1 ist eine Untergrenze, kein Beweis für Evidenzmangel.

---

# Aufgabe 3 - Rechtfertigung der Arbeit

## A - Unmittelbar notwendig

| Artefakt | Warum |
|---|---|
| `scripts/read_q2_extended.py`, `meta/arm_level.py`, `meta/arm_text.py`, `meta/effect_columns.py`, `research/table_extractor.py` | erzeugen die zwei einzigen Studienzeilen; ohne sie kein k |
| `scripts/fetch_q2_corpus.py`, `scripts/fetch_missing_corpus_xml.py` | beschaffen den Korpus (31 XML) |
| `scripts/check_pdf_verfuegbarkeit.py`, `scripts/list_no_pmc_trials.py`, `zugangsliste_20261108.csv` | belegen die 83 Lücken und begründen die Bestellung |
| `research_agent/meta/pooling.py` (gitignored) | vorhanden, aber **noch nicht anwendbar** (k = 1); ohne ihn geht bei k ≥ 2 nichts |

## B - Sinnvolle technische Hilfsarbeit

| Artefakt | Warum B und nicht A |
|---|---|
| `scripts/read_pdf_corpus.py`, `meta/pdf_text.py` | lesen PDFs, aber kein geliefertes PDF wurde je verarbeitet |
| `scripts/triage_lieferung.py`, `scripts/pruefe_lieferung.py` | machen den Tag der Lieferung schneller, haben aber noch kein Dokument gelesen |
| `scripts/probe_normalize_fulltext.py`, `make_text_pdf.py`, `make_scan_probe.py` | haben einen echten Fehler gefunden (verlorene Tabellenblöcke im Zwischenstand, Endmessung 0), liefern aber kein Studienergebnis |
| Bestellmail, Fernleih-Fassung, Warteliste | nötig für den Zugang, keine Erkenntnis |
| 76 Testdateien, 1.292 gesammelte Tests | Sicherheitsnetz; ein großer Teil prüft Werkzeuge, die nie auf echten Lieferdaten liefen |

## C - Nicht notwendig, ohne messbaren Erkenntnisgewinn

| Artefakt | Begründung |
|---|---|
| `probelauf/`, `probelauf_bindestrich/`, simulierte Lieferung mit vier Prüf-PDFs | prüfen Mechanik an erfundenen Daten; k = 3 bzw. 4 ist kein Studienbefund |
| `build_notebook.py`, `build_notebook2.py`, `build_notebook_final.py` | drei Fassungen, keine wird für die Frage gebraucht |
| `kaggle_gpu_server.py`, `pc_gpu_server.py`, `pc_gpu_server_with_ngrok.py`, `deploy_kaggle.py`, `render_pdf_pages.py`, `make_briefing_pdf.py`, `simulate_research.py` | gehören zu anderen Fragestellungen (Koffein, GPU, Visualisierung) |
| 26 Markdown-Berichte und 19 JSON-Dateien in `sol2` (einschließlich dieser Datei), darunter drei Stand-Dokumente | überholen sich gegenseitig; die Entscheidung steht in einer Datei, der Rest ist Ballast |
| "Einheit aus dem Kontext"-Durchgang | lieferte 0 Zeilen; der negative Befund ist eine Zeile wert, nicht einen eigenen Durchgang |

## Werkzeuge: vorhanden vs. fehlend

**Vorhanden und funktionsfähig:** XML-Extraktion (Klammer-SD,
Zeitpunktspalten, Fallzahl aus Text), PDF-Text-Normalisierung mit
Tabellenschutz, Arm-Level-Umrechnung zu Hedges g, Effektspalten-Leser, DB mit
Pflichtzitat, Pooling (Hartung-Knapp-Sidik-Jonkman) - letzteres ungetestet an
echten Daten.

**Fehlt, und zwar genau das:**

1. **Zugang zu 83 Volltexten** - kein Werkzeug löst das.
2. **Leser für vier konkrete Layouts** (PMC2933606, PMC2952772, PMC5774131,
   PMC10131443) - vier Regeln, kein neues System.
3. **Crossover-Korrektur** (Within-Subject-Korrelation) - würde bis zu vier
   Studien öffnen, ist aber häufig nicht berichtet.
4. **Eine Protokollentscheidung**: Tagebuch oder Aktigraphie als primärer
   Endpunkt bei PMC3489506.

Punkt 2 und 4 sind keine Softwareprobleme. Punkt 2 lässt sich von Hand lösen.

---

# Aufgabe 4 - Die eine nächste Handlung

**Die vier offenen Parallelstudien manuell aus den vorhandenen XML kodieren -
mit wörtlichem Zitat und einer zweiten, unabhängigen Durchsicht - und
feststellen, ob k dadurch auf 2 bis 5 steigt.**

Warum diese und keine andere: Sie braucht **keinen Netzzugang, kein neues
Werkzeug und keine Lieferung**. Die Texte liegen seit dem Q2-Lauf unter
`data/bench/sol2/xml/`. Sie beantwortet die eigentliche Frage direkt - ob der
Korpus eine Metaanalyse trägt oder der Berichtsstil sie verhindert - und
trennt zwei Dinge, die bisher vermischt sind: "der Leser kann das Layout
nicht" (behebbar, vier Fälle) gegen "die Studie berichtet keine
Arm-Mittelwerte" (nicht behebbar).

Erwartung, ausdrücklich als Erwartung: PMC2933606 hat 21 SOL-Zeilen im
Klammerformat und ist der wahrscheinlichste Kandidat; PMC2952772
(Dosisfindung) ist ohne Arm-Auswahl nicht poolbar; PMC5774131 berichtet ein
Verhältnis; PMC10131443 hat einen Wert je Arm ohne Streuung. Realistisch ist
**eine** zusätzliche Studie, k = 2 - der erste Fortschritt bei k seit dem
Q2-Lauf. Gelingt es nicht, ist die Antwort auf die Ausgangsfrage empirisch
belegt: nicht der Agent, die Literatur.

Danach, und erst danach: A + B bestellen (25 Dokumente), weil k ≥ 5 ohne
Zugang nicht erreichbar ist.

---

# Was falsch gemacht wurde

1. **Werkzeuge mit Erkenntnis verwechselt.** Neun Schritte Software, k
   unverändert 1. Die Messlatte hätte lauten müssen: neues Dokument,
   geschlossene Fehlerquelle oder verändertes k.
2. **"34 Volltexte gelesen" war irreführend.** Gelesen wurden sie nur zur
   Textprüfung, nicht zur Extraktion.
3. **Simulationen als Ergebnis erzählt.** k = 3 und k = 4 aus synthetischen
   PDFs sind Mechanismustests, keine Literaturbefunde.
4. **Zu viele Dokumente, zu wenige Entscheidungen.** 25 Berichte in einem
   Ordner, drei davon "Stand" - das erschwert genau die Nachvollziehbarkeit,
   die hier gefordert ist.

Der eine Satz, der den wissenschaftlichen Stand trägt: **Eine RCT zeigt einen
deutlichen Effekt auf die Einschaflatenz; eine quantitative Zusammenfassung
ist mit dem bisher gelesenen Material nicht möglich, und ob das an der
Literatur oder am Leser liegt, ist mit vier Studien im Haus entscheidbar -
ohne neue Software.**

## Quellenverzeichnis

Alle Angaben stammen aus Dateien in `data/bench/sol2/`:
`manifest_q2.json`, `extended.json`, `extended.md`, `direct.json`,
`arm_level.md`, `text_arms.json`, `schwelle_analyse.json`,
`schwelle_k5_20261108.md`, `bewertung_q2_20261108.md`,
`ergebnis_direkte_effekte_20261108.md`, `lieferung.json`,
`lieferung_pruefung.json`, `zugangsliste_20261108.csv`,
`normalisierung_echte_texte_20261108.md`, `triage_pruefung_20261108.md`,
`xml/PMC3489506.xml`.
