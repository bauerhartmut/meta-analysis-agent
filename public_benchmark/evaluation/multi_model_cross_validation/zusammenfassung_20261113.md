# Zusammenfassung: Multi-Model Cross-Validation

Stand: 2026-11-13
Status: **PLANUNG ABGESCHLOSSEN, DATENSATZ GEWAEHLT, KEIN MODELLAUFRUF**
Belege: [`experiment_plan.md`](experiment_plan.md),
[`entscheidungen_20261113.md`](entscheidungen_20261113.md),
[`candidate_shortlist_v2.md`](candidate_shortlist_v2.md)

## 1. Worum es geht

Lässt sich die numerische Extraktion aus Studien verbessern, wenn drei
verschiedene Modelle unabhängig extrahieren, ein deterministischer Vergleich
die Konflikte findet und Qwen die Konflikte an der Originalquelle auflöst?
Gemessen wird ausschließlich gegen eine vorab eingefrorene menschliche
Referenz - nicht gegen Modellkonfidenzen und nicht gegen Modellübereinstimmung.

Modelle: Qwen 3.5 397B (Arm A), DeepSeek V4.1 Flash (Arm B), GLM 5.3 (Arm C),
Qwen zusätzlich als Adjudikator.

## 2. Entscheidungen

| Nr. | Entscheidung | Stand |
|---|---|---|
| F1 | Neues PMC-Set, 25 Artikel, 60-80 Records, 10 Reserve, disjunkt zu Yun und G5 | umgesetzt |
| F2 | Zwei unabhängige Annotatoren, sonst eine Person als vorläufige Referenz mit dokumentierter Einschränkung; Kappa keine Pauschalvoraussetzung, numerisch exakt plus absolute Abweichung plus ICC | offen (organisatorisch) |
| F3 | Ein diagnostischer GLM-Aufruf mit vollständiger Protokollierung; bei Ausfall Ersatzmodell, Wechsel dokumentiert | offen (Freigabe) |
| F4 | `schema_v1.json` mit Beleg je Zahl: Einheit, Seite, Tabelle, Kontext, Arm-ID, Outcome-ID, Zeitpunkt, Zuordnungssicherheit | offen |
| F5 | Qwen primär und ein viertes Modell als Kontrolle, beide verblindet, Selbstwahlquote berichten | entschieden, Umsetzung offen |
| F6 | Power-Abschätzung vor dem Einfrieren, 60-80 Records, Erweiterung auf 100+ wenn nötig | offen |

Verbindlich: Ein nicht signifikanter Unterschied ist kein Nachweis gleicher
Leistung. Die Adjudikation ist nie Ground Truth.

## 3. Stand der verbindlichen Reihenfolge

| # | Schritt | Stand |
|---:|---|---|
| 1 | Datensatz auswählen, G5-Disjunktheit prüfen | **erledigt** |
| 2 | Referenzannotatoren organisieren | offen |
| 3 | GLM diagnostisch testen | offen |
| 4 | Schema und Quellenbelege implementieren | offen |
| 5 | Adjudikationsverfahren festlegen | entschieden (F5) |
| 6 | Power-Abschätzung | offen |
| 7 | `dataset_manifest.json` | offen |
| 8 | `reference.jsonl` annotieren und einfrieren | offen |
| 9 | Prompts und Schema einfrieren | offen |
| 10 | `freeze.json` | offen |
| 11 | Drei Modellläufe | **gesperrt** bis 8-10 erledigt |

## 4. Datensatz

### Auswahltrichter

| Schritt | Artikel |
|---|---:|
| September-2026-Frame, artikeldisjunkt zu Yun | 596 |
| Abstract-Freigabe | 415 |
| ohne G5 (36 Artikel) und ohne Yun | 379 |
| mit RCT-Publikationstyp | 374 |
| ohne Zusammenfassung/Korrektur/Protokoll | 372 |
| Auswahl v1 (25 primär, 10 Reserve) | 35 |

Rangfolge: `sha256("crossval-20261113-v1:<PMCID>")`, reproduzierbar und
unabhängig von Eingabereihenfolge.

### Volltext und Eignung

| Prüfung | Ergebnis |
|---|---:|
| XML abgerufen (35 plus 15 Ersatz) | 50/50, 6,13 MB |
| geeignet nach Fallmix-Prüfung | 49 |
| ausgeschlossen ohne Armwerte | 1 |
| Trial-Dubletten in der Auswahl | 0 |
| Artikel mit Register-ID | 35 von 50, alle eindeutig (3 weitere nur mit Titel-Akronym) |

Ausschlussgründe sind im Profil dokumentiert: `no_arm_data`,
`duplicate_trial`, `review_or_summary`, `no_fulltext`.

### Fallmix der Primärauswahl

| Merkmal | Artikel |
|---|---:|
| kontinuierliches Tabellensignal | 15 |
| binäres Tabellensignal | 14 |
| beide Signale | 9 |
| Mehrarm-Hinweis | 4 |
| Pilot/Feasibility | 10 |
| sekundäre Analyse | 3 |
| mit Supplement | 16 |
| Tabellen gesamt | 88 |

## 5. Artefakte

| Datei | Inhalt |
|---|---|
| `experiment_plan.md` | Infrastrukturprüfung, Blocker, Phasen A-E, Freeze-Checkliste |
| `offene_fragen.md` | ursprünglicher Fragenstand (beantwortet, unverändert) |
| `entscheidungen_20261113.md` | Entscheidungen, Reihenfolge, Schritt 1 und 1b |
| `candidate_pool_v1.json` | gerankter Pool, 372 Artikel |
| `candidate_shortlist_v1.json/.md` | Auswahl vor der Eignungsprüfung, 35 Artikel |
| `fulltext_availability_v1.json/.md` | Abrufmanifest mit HTTP-Status und SHA-256 |
| `fallmix_profile_v1.json/.md` | Profile, Designsignale, Ausschlüsse |
| `candidate_shortlist_v2.json/.md` | Auswahl für die Annotation, 25 + 10 |
| `zusammenfassung_20261113.md` | dieses Dokument |

Skripte: `public_benchmark/scripts/select_crossval_articles.py`,
`fetch_crossval_fulltext.py`, `profile_crossval_articles.py`.

## 6. Tests

| Modul | Prüft | Stand |
|---|---|---|
| `test_crossval_g5_exclusion.py` | 25/10, Disjunktheit zu G5 und Yun, Screening-Herkunft, Rangfolge | 5 grün |
| `test_crossval_case_mix.py` | Hashes, Dublettenfreiheit, Mindest-Fallmix, Ausschlussgründe, Reihenfolge | 8 grün |

Kein Modellaufruf, kein Netzzugriff in den Tests.

## 7. Was noch blockiert

1. **GLM 5.3** liefert im vorhandenen Dev-Lauf 19 von 26 leere Antworten und
   eine abgeschnittene. Ohne Klärung ist das Experiment zweimodellig.
2. **Referenzannotation** fehlt vollständig. Ohne sie gibt es keine
   Feldgenauigkeit und keine Antwort auf die Forschungsfrage.
3. **Schema v1** existiert noch nicht; das v6-Schema liefert nur eine
   `source_note` und trägt die Konfliktkategorien 5 und 6 nicht.
4. **Power-Abschätzung** fehlt; ohne sie ist unklar, welche Differenz die
   Stichprobe überhaupt nachweisen kann.

## 8. Nächster Schritt

GLM-Diagnoseaufruf freigeben und parallel die Annotation für die 25 Artikel
organisieren. Der Aufruf entscheidet in Minuten, ob Schema und Adjudikation für
zwei oder drei Modelle gebaut werden; die Annotation entscheidet, ob Phase D
überhaupt stattfinden kann. Alles andere ist danach mechanisch.

## 9. Grenzen dieser Zusammenfassung

- Die Eignung der Artikel ist ein Tabellen- und Textsignal, keine bestätigte
  Extraktion. Der abschließende Volltextblick vor der Annotation steht aus.
- Kein Artikel wurde manuell gelesen; alle Zahlen stammen aus den
  eingefrorenen JSON-/XML-Artefakten.
- Die Dublettenerkennung greift nur über Register-IDs und Titel-Akronyme.
- Die Fallmix-Zahlen beschreiben diese Stichprobe, nicht die Grundgesamtheit
  der September-2026-RCTs.
