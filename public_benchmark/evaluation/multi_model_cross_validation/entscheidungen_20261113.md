# Entscheidungen: Multi-Model Cross-Validation

Stand: 2026-11-13
Grundlage: [`experiment_plan.md`](experiment_plan.md), [`offene_fragen.md`](offene_fragen.md)
Status: **ENTSCHIEDEN - Schritt 1 umgesetzt, kein Modellaufruf**

## 1. Die sechs Entscheidungen

| Nr. | Entscheidung | Konsequenz im Plan |
|---|---|---|
| F1 | **A - neues PMC-Set**, 25 Artikel, 60-80 Records, 10 Reserve vorab, Disjunktheit zu Yun/Dev/Test/G5 | Artikelauswahl liegt vor (Abschnitt 3) |
| F2 | **B - zwei unabhängige Annotatoren, sonst A als vorläufige Explorationsreferenz mit dokumentierter Einschränkung.** Kappa >= 0,80 ist keine pauschale Voraussetzung | Referenzmetriken: exakte Übereinstimmung, absolute Abweichung, ICC für numerische Werte; Kappa nur für kategoriale Variablen |
| F3 | **A - ein diagnostischer Aufruf mit Freigabe**, vollständige Protokollierung; bei Ausfall Ersatzmodell, Wechsel dokumentiert | GLM bleibt Pflichtbestandteil oder wird sichtbar ersetzt; stilles Weglassen unzulässig |
| F4 | **A - `schema_v1.json` mit Beleg je Zahl** (Wert, Einheit, Seite, Tabelle/Abschnitt, Kontext, Arm-ID, Outcome-ID, Zeitpunkt, Zuordnungssicherheit, Prüfstatus, Record-ID); `source_note` bleibt | Kategorien 5 und 6 werden bestimmbar; Schema ist Teil des Freeze |
| F5 | **C - Qwen primär, viertes Modell als Kontrolle, sofern verfügbar**, beide verblindet; Selbstwahlquote und Selbstwahlkorrektheit berichten | Zwei Adjudikationsdateien, gemeinsame Konfliktliste |
| F6 | **A mit Prüfung von B** - Power-Abschätzung vor dem Einfrieren; 60-80 Records, Erweiterung auf >= 100 wenn nötig; kleinste nachweisbare Differenz im Abschlussbericht; sonst explorativ | Power-Block ist Teil von Phase 0; Reserve deckt eine Erweiterung auf 35 Artikel ab |

Verbindlich übernommen: Ein nicht signifikanter Unterschied ist kein Nachweis
gleicher Modellleistung. Die Adjudikation ist nie Ground Truth.

## 2. Verbindliche Reihenfolge mit Stand

| # | Schritt | Stand |
|---:|---|---|
| 1 | Datensatz auswählen, G5-Disjunktheit prüfen | **erledigt** (Abschnitt 3) |
| 2 | Referenzannotatoren organisieren | offen - organisatorisch, nicht im Repo lösbar |
| 3 | GLM diagnostisch testen | **erledigt** - verwendbar ab `max_tokens` 8000 |
| 4 | Schema und Quellenbelege implementieren | **erledigt** - `schema_v1.json` mit 10 Tests |
| 5 | Adjudikationsverfahren festlegen | **umgesetzt** - verblindeter Batch und Auswertung mit 3 Tests |
| 6 | Power-Abschätzung | **erledigt** - MDD 7,9-8,8 pp bei 60 Records |
| 7 | `dataset_manifest.json` | **Entwurf erstellt** - Disjunktheit geprüft, Referenz offen |
| 8 | `reference.jsonl` annotieren und einfrieren | offen |
| 9 | Prompts und Schema einfrieren | offen |
| 10 | `freeze.json` | offen |
| 11 | Drei Modellläufe | **gesperrt** bis 8-10 erledigt |

Abbruchregel übernommen: ohne eingefrorene Referenz und nachgewiesene
G5-Disjunktheit keine regulären Modellläufe.

## 3. Schritt 1: Artikelauswahl v1

Erzeugt durch `public_benchmark/scripts/select_crossval_articles.py`
(deterministisch, ohne Modell, ohne Netz):

- Ausgabe: [`candidate_shortlist_v1.json`](candidate_shortlist_v1.json),
  [`candidate_shortlist_v1.md`](candidate_shortlist_v1.md)
- Test: `public_benchmark/tests/test_crossval_g5_exclusion.py` (5 Tests, grün)

Auswahltrichter:

| Schritt | Artikel |
|---|---:|
| Abstract-Freigabe, ohne G5, ohne Yun | 379 |
| davon mit RCT-Publikationstyp | 374 |
| davon ohne Zusammenfassung/Korrektur/Protokoll | 372 |
| ausgewählt (Primär / Reserve) | 25 / 10 |

Disjunktheit, geprüft gegen die eingefrorenen Quellen:

- G5 (30 Shortlist-Artikel plus 36 menschlich bestätigte Einschlüsse):
  Schnittmenge leer.
- Yun Freeze (70 Artikel), Dev (6), Test (64): Schnittmenge leer.

Rangfolge: `sha256("crossval-20261113-v1:<PMCID>")` aufsteigend. Damit ist die
Auswahl reproduzierbar und unabhängig von Eingabereihenfolge oder Zufall.

## 4. Was dieser Schritt nicht leistet

- **Keine Einschlussentscheidung.** Die Liste ist eine Kandidatenliste; erst die
  Volltextprüfung zeigt, ob ein Artikel Armwerte für mindestens einen Vergleich
  berichtet.
- **Keine Recordzahl.** 60-80 Records aus 25 Artikeln sind eine Zielgröße, keine
  Messung. Die tatsächliche Zahl wird nach der Volltextprüfung festgestellt.
  Reicht sie nicht, werden Reserveartikel nachgezogen; reicht auch das nicht,
  wird ein zweites Kontingent nach derselben Regel gezogen.
- **Keine Erweiterung auf 100 Records.** F6 erlaubt sie, aber erst nach der
  Power-Abschätzung und nur mit zusätzlicher Annotation.
- **Kein Modellaufruf, kein Netzzugriff.**

## 5. Nächster Schritt

Schritt 2 und 3 sind unabhängig und laufen parallel: Annotation organisieren
(Zugriff auf Volltexte erst nach Zusage der Personen, damit keine
Vorabkenntnis entsteht) und den GLM-Diagnoseaufruf mit den in F3 genannten
Feldern durchführen. Danach kann das Schema (Schritt 4) gebaut werden, weil
erst dann feststeht, ob drei Modelle antreten.

## 6. Schritt 1b: Fallmix, Volltextverfuegbarkeit, Dubletten

Vorgezogene Pruefung der Auswahl, damit keine Annotationszeit auf untauglichen
Artikeln verloren geht. Skripte:
`public_benchmark/scripts/fetch_crossval_fulltext.py` und
`public_benchmark/scripts/profile_crossval_articles.py`; Test:
`public_benchmark/tests/test_crossval_case_mix.py` (8 Tests, gruen).

### Erweiterte Kriterien

1. **Volltext abgerufen.** Europe-PMC-XML, SHA-256 im Manifest. Kein
   PDF-Fallback, kein Modell.
2. **Kein Review-/Summary-Titel.** Reine Zusammenfassungen und Korrekturen
   liefern keine eigenen Armwerte.
3. **Armwert-Signal.** Entweder eine Tabelle mit Mittelwert und Streuung
   beziehungsweise Ereigniszellen und mindestens sechs Zahlenzellen, oder
   mindestens zwei Zahlensignale im Fliesstext. Artikel ohne beides werden
   ausgeschlossen (`no_arm_data`).
4. **Keine Trial-Dublette.** Gleiche Register-ID (NCT, ISRCTN, ChiCTR, DRKS,
   CTRI, UMIN, ACTRN, EudraCT, IRCT, jRCT, TCTR) oder gleiches Trial-Akronym
   im Titel. Der hoeher gerankte Artikel bleibt, der spaetere wird
   ausgeschlossen (`duplicate_trial`).

### Ergebnis

- 35 Artikel aus v1 plus 15 Ersatzartikel aus dem gerankten Pool abgerufen:
  **50/50 XML**, zusammen 6,13 MB.
- 49 geeignet, 1 ausgeschlossen (`PMC13682720`, keine Armwerte).
- **0 Trial-Dubletten** in der Auswahl. 35 der 50 Artikel fuehren eine
  Register-ID, alle eindeutig; 3 weitere tragen nur ein Titel-Akronym.
- Auswahl v2: **25 primaer + 10 Reserve**, alle mit Volltext und Hash.

### Fallmix der Primaerauswahl

| Merkmal | Artikel |
|---|---:|
| kontinuierliches Tabellensignal | 15 |
| binaeres Tabellensignal | 14 |
| beide Signale | 9 |
| Mehrarm-Hinweis | 4 |
| Pilot/Feasibility | 10 |
| sekundaere Analyse | 3 |
| mit Supplement | 16 |
| Tabellen gesamt | 88 |

### Grenzen

- Die Eignung ist ein Tabellen- und Textsignal, keine bestaetigte
  Extraktion. Die Volltextpruefung vor der Annotation bleibt der letzte
  Schritt.
- **Kein Crossover-Artikel in der Primaerauswahl** (1 in der Reserve), 10 von
  25 sind Pilot/Feasibility. Das ist eine Eigenschaft dieser Stichprobe, keine
  Zielverfehlung: die Kriterien verlangen Vielfalt, keine Quote.
- Dubletten werden nur ueber Register-IDs und Titel-Akronyme erkannt. Ein
  Zweitartikel desselben Trials ohne beides bleibt unentdeckt; das ist der
  verbleibende, nicht messbare Rest.
