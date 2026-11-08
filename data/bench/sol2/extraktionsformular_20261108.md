# Extraktionsformular für die zwölf bestellten Studien

Stand: 2026-11-08, angelegt **vor** Eintreffen der Volltexte. Bezug:
`auswahlregel_pooling_20261108.md` (Regeln 1-3, 10) und
`crossover_regel_20261108.md` (C1-C7).

Zweck: Jede Zahl, die später in ein Pooling eingeht, hat hier eine Zeile mit
Arm, n, Mittelwert, Streuung und Fundstelle. Was nicht berichtet ist, bleibt
leer und wird als "nicht berichtet" geführt - nicht geschätzt, nicht
übersprungen.

Arbeitsvorlage: `extraktion_vorlage_20261108.csv` (Kopfzeile und zwölf
Zeilen mit PMID, sonst leer).

## Feldgruppen

### A - Identität

| Feld | Bedeutung | Pflicht |
|---|---|---|
| `studie_id` | Kurz-ID, z. B. `S11_wright2011` | ja |
| `pmid` | PubMed-ID | ja |
| `doi` | DOI aus dem Volltext | ja |
| `kurzname` | Erstautor und Jahr | ja |
| `studiengruppe` | Kinder Entwicklungsstörung / Erwachsene / andere | ja |

### B - Design

| Feld | Bedeutung | Pflicht |
|---|---|---|
| `design` | `parallel`, `crossover`, `faktoriell` | ja |
| `n_perioden` | Anzahl Messperioden bei Crossover | bei Crossover |
| `washout` | Dauer und Einheit, z. B. `7 d`; `kein`; `nicht berichtet` | bei Crossover |
| `periodeneffekt` | `geprüft, nicht signifikant` / `signifikant` / `nicht berichtet` | bei Crossover |
| `carryover_bewertung` | `unproblematisch` / `fraglich` / `problematisch`, mit Begründung | bei Crossover |
| `erste_periode_auswertbar` | `ja` / `nein`, falls C5 greift | bei Crossover |

### C - Population

| Feld | Bedeutung | Pflicht |
|---|---|---|
| `population` | Diagnose oder Setting, wörtlich aus dem Volltext | ja |
| `altersgruppe` | Spanne in Jahren | ja |
| `n_randomisiert` | Gesamtzahl randomisiert | ja |
| `n_analysiert` | Zahl in der Auswertung | ja |
| `n_verum` / `n_placebo` | Armgrößen | ja |
| `dropout` | Zahl und Grund, falls berichtet | nein |

### D - Intervention

| Feld | Bedeutung | Pflicht |
|---|---|---|
| `dosis_mg` | Absolutdosis in mg | ja, wenn angegeben |
| `dosis_mg_kg` | gewichtsbezogen, falls berichtet | nein |
| `dauer` | Behandlungsdauer, z. B. `12 wk` | ja |
| `einnahmezeit` | Uhrzeit relativ zur Schlafenszeit | nein |
| `praeparat` | Formulierung, z. B. `prolonged release` | nein |

### E - Outcome

| Feld | Bedeutung | Pflicht |
|---|---|---|
| `messmethode` | `PSG` / `Tagebuch` / `Aktigraphie` / `Fragebogen` | ja |
| `outcome_name` | wörtlich, z. B. `sleep onset latency` | ja |
| `zeitpunkt` | Zeitpunkt der Erhebung, z. B. `Woche 12` | ja |
| `verum_mean` / `verum_sd` | Mittelwert und Streuung Verum | ja |
| `placebo_mean` / `placebo_sd` | Mittelwert und Streuung Placebo | ja |
| `streuungsart` | `SD` / `SE` / `95%-CI` / `IQR` | ja |
| `einheit` | `min`; alles andere wird umgerechnet und die Rechnung notiert | ja |

### F - Effekt und Streuung

| Feld | Bedeutung | Pflicht |
|---|---|---|
| `effekt_min` | Verum minus Placebo in Minuten | ja |
| `se` | Standardfehler des Effekts | ja |
| `herkunft_effekt` | `berichtet` / `aus CI abgeleitet` / `aus Armen gerechnet` | ja |
| `sd_diff` | Streuung der individuellen Differenz (Crossover) | wenn berichtet |
| `se_diff` | SE der gepaarten Differenz | wenn berichtet |
| `ci_untere` / `ci_obere` | berichtetes CI des Effekts | wenn berichtet |
| `r` | Korrelation, nur nach C2/C7 | wenn geschätzt |
| `r_geschaetzt` | `ja` / `nein` | ja |
| `adjustiert` | `ja` (Studienangabe) / `nein` (eigene Rechnung) | ja |

### G - Prüfung und Herkunft

| Feld | Bedeutung | Pflicht |
|---|---|---|
| `fundstelle` | Seite, Tabelle, Spalte oder Absatz | ja |
| `zitat` | wörtlicher Satz mit den Zahlen | ja |
| `rob2_domaene_periode` | Urteil der Crossover-Domäne | bei Crossover |
| `status` | `poolbar` / `Zahlen fehlen` / `Endpunkt nicht berichtet` / `ausgeschlossen` | ja |
| `anmerkung` | alles, was sonst nirgends passt | nein |
| `extrahiert_von` / `datum` | Kürzel und Datum | ja |

## Ausfüllregeln

**R1 - Nur berichtete Werte.** Jede Zahl braucht `fundstelle` und `zitat`.
Gibt es beides nicht, bleibt das Feld leer und `status` wird
`Zahlen fehlen`.

**R2 - SD und SE nie verwechseln.** `streuungsart` ist Pflicht. Ist die
Streuung als SE berichtet, wird sie nicht als SD eingetragen; die Umrechnung
erfolgt erst in der Auswertung und wird in `anmerkung` notiert (SE · √n = SD).

**R3 - Effekt aus dem CI.** SE = (obere − untere Grenze) / 3,919928. Das
Ergebnis wird auf zwei Nachkommastellen geführt und als `aus CI abgeleitet`
markiert.

**R4 - Effekt aus den Armen.** Bei Parallelstudien: Differenz der
Endwerte, SE = √(SD_verum²/n_verum + SD_placebo²/n_placebo). Baseline-Werte
werden nicht als Endwerte eingetragen; bei Change-Werten ist die
Veränderung einzutragen, nicht der Ausgangswert.

**R5 - Crossover.** Nach C1-C7: gepaarte Differenz, SE = SD_diff/√n mit
n = Personenzahl. Fehlt SD_diff, wird r = 0,5 gesetzt und `r_geschaetzt = ja`
markiert. Die ungepaarte SE kommt zusätzlich in die Sensitivitätstabelle,
nicht in die Hauptzeile.

**R6 - Einheit Minuten.** Stunden werden mit 60 multipliziert; die Rechnung
steht in `anmerkung`. log-Werte, Scores und Kategorien sind kein
Minuten-Endpunkt und führen zu `status = Endpunkt nicht berichtet`.

**R7 - Vorzeichen.** `effekt_min` ist Verum minus Placebo. Ein negativer
Wert bedeutet: Melatonin senkt die Einschaflatenz. Ein positiver Wert wird
nicht stillschweigend umgedreht.

**R8 - Eine Zeile je Studie.** Mehrere Dosen, Populationen oder
Messmethoden derselben Studie erzeugen keine zweite Zeile, sondern eine
Auswahl nach den Regeln 4-6 der Auswahlregel; die verworfene Alternative
kommt in `anmerkung`.

**R9 - Keine Schätzung ohne Kennzeichnung.** Jede abgeleitete Zahl trägt
`herkunft_effekt` oder `r_geschaetzt`. Ein geschätzter Wert sieht im
Datensatz anders aus als ein berichteter.

**R10 - Unlesbares wird gemeldet, nicht geraten.** Scan ohne Textebene,
fehlende Tabelle, abgeschnittene Spalte: `status = nicht auswertbar` und
Hinweis, welche Seite fehlt.

## Beispielzeile (echte Werte aus dem Abstract, Streuungsart ungeprüft)

| Feld | Wert |
|---|---|
| studie_id | S12_mcarthur1998 |
| pmid | 9566656 |
| design | crossover |
| population | Rett-Syndrom |
| messmethode | Tagebuch (im Volltext prüfen) |
| verum_mean | 19,1 |
| placebo_mean | 42,1 |
| streuungsart | im Abstract als ± angegeben, ob SD oder SE ist offen |
| effekt_min | −23,0 |
| status | poolbar, sobald Streuungsart geklärt |
| fundstelle | Abstract, Ergebnisse |

Die Zeile zeigt den wichtigsten Punkt: Ohne Klärung, ob die Streuung SD oder
SE ist, darf der Effekt nicht gepoolt werden. Bei n = 11 unterscheidet sich
die gepoolte Unsicherheit um den Faktor 3,3.

## Was nicht eingetragen wird

- Keine Werte aus Sekundärquellen (Reviews, HTA-Berichte), wenn der
  Primärtext vorliegt.
- Keine aus Grafiken abgelesenen Zahlen ohne Kennzeichnung.
- Keine Fortschreibung fehlender Mittelwerte aus p-Werten.
- Keine zweite Zeile für dieselben Personen.

## Prüfschritte vor dem Pooling

1. Alle zwölf Zeilen haben `status`; leere Felder sind erklärt.
2. Jede Zahl hat `fundstelle` und `zitat`.
3. `streuungsart` ist bei jeder Zeile gesetzt.
4. Bei Crossover sind `washout`, `periodeneffekt` und `r_geschaetzt` gefüllt.
5. Die Summe der Armgrößen stimmt mit `n_analysiert` überein.
6. Vorzeichen und Einheit sind über alle Zeilen gleich.
