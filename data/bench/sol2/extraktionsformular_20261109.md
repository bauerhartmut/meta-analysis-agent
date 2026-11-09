# Extraktionsformular für die Fernleih-Lieferung: Register, Crossover, Dedup

Stand: 2026-11-09, angelegt **vor** Eintreffen einer Lieferung. Ersetzt
`extraktionsformular_20261108.md` nicht, sondern erweitert es um die drei
Prüfungen, die dort nur als Feld vorhanden waren. Die drei eingefrorenen
Zeilen in `extraktion_vorlage_20261108.csv` bleiben unberührt.

Drei Gründe, warum dieses Formular vor dem Ausfüllen dieser Blöcke beginnt:

1. **Dedup zuerst.** Die Zugangsliste enthält nachweislich
   Doppelpublikationen: 23098680 (HTA-Bericht) berichtet zeichengleiche
   SOL-Werte wie PMC3489506, 21091391 ist Sekundärpublikation von S2. Ohne
   Prüfung vor der Extraktion kostet dieselbe Kohorte zweimal Arbeit.
2. **Register statt Titelähnlichkeit.** Der MENDS-Fall zeigt die Grenze:
   Jaccard 0,33 auf den Titeln, die Identität kam erst über die Effekte.
   Ohne Register-ID ist ein Dedup nur bei gleichem Titel möglich.
3. **Gepaarte Streuung.** Sieben der zwanzig bestellfähigen Titel sind
   Crossover. Wer dort die Streuung der Gruppenmittelwerte nimmt,
   überschätzt den Standardfehler um bis zu Faktor 2,24 (r = 0,5) und gibt
   der Studie zu wenig Gewicht.

Arbeitsvorlage: `extraktion_vorlage_20261109.csv` — 20 Zeilen (5 A- und
15 B-Titel nach der Triage), nur `pmid`, `doi`, `kurzname` vorbelegt, alles
andere offen. Erzeugt und geprüft von `scripts/pruefe_extraktion_20261109.py`.

## Arbeitsreihenfolge

| Schritt | Frage | Feldgruppe | Abbruch, wenn |
|---|---|---|---|
| 1 | Ist das dieselbe Studie wie S1, S2 oder S3? | I | `dedup_ergebnis = Doppel` |
| 2 | Gibt es eine Register-ID, und stimmt sie mit dem Volltext? | H | keine ID und kein Beleg |
| 3 | Welches Design, und wie ist die Streuung berichtet? | B, F | Design unklar bei Crossover |
| 4 | Zahlen, Arme, Endpunktstatus | C, D, E, F | Armwerte fehlen und keine SE |
| 5 | Fundstelle, Zitat, Status | G, J | Zitat fehlt |

Schritt 1 und 2 vor Schritt 4, weil eine Doppelpublikation nicht extrahiert
wird und eine fehlende Register-ID die spätere Prüfung unmöglich macht.

## H — Register

| Feld | Werte | Pflicht |
|---|---|---|
| `register_id` | `NCT########`, `ISRCTN########`, `EU-CTR 2006-004025-28`, `ACTRN`, `ChiCTR`, `DRKS`, `ohne`, `nicht berichtet` | ja |
| `register_fundstelle` | Abschnitt im Volltext, z. B. `Methoden, Absatz 1` oder `Titelblatt, Trial registration` | ja, außer bei offener Zeile |
| `register_abgleich_n` | `stimmt` / `abweichend` / `nicht pruefbar` | ja bei vorhandener oder fehlender ID |
| `register_abgleich_endpunkt` | `stimmt` / `abweichend` / `nicht pruefbar` | ja |

Die Register-ID wird aus dem Volltext genommen, nicht aus PubMed-Metadaten
und nicht aus einem Abstract: Dort fehlt sie häufig oder ist gekürzt. Wird
sie im Text nicht genannt, lautet der Eintrag `ohne` oder
`nicht berichtet` — beides ist zulässig, aber nur mit Fundstelle.

`register_abgleich_endpunkt` fragt, ob der im Register hinterlegte primäre
Endpunkt mit dem in der Publikation berichteten übereinstimmt. Der
Widerspruch bei S1 („sekundär nach Amendment") ist genau dieser Fall und
gehört in eine Spalte, nicht in eine Fußnote.

## I — Dedup gegen die drei eingeschlossenen Studien

| Feld | Werte | Pflicht |
|---|---|---|
| `dedup_gegen` | `S1`, `S2`, `S3`, `S1+S2`, `S1+S3`, `S2+S3`, `S1+S2+S3`, `keins` | ja |
| `dedup_merkmal` | was verglichen wurde: `Register-ID`, `n`, `Zentren`, `Rekrutierungszeitraum`, `Autorengruppe`, `Effektwerte` | ja, mehrere mit Semikolon |
| `dedup_ergebnis` | `unabhaengig` / `Verdacht` / `Doppel` / `ungeklaert` | ja |
| `dedup_beleg` | ein Satz mit dem entscheidenden Merkmal | ja |

Die drei Referenzstudien:

| Kürzel | PMID | DOI | Register | Population |
|---|---|---|---|---|
| S1 MENDS | 23129488 | 10.1136/bmj.e6664 | ISRCTN05534585 | Kinder mit Entwicklungsstörung, 12 Wochen |
| S2 Wade | 20712869 | 10.1186/1741-7015-8-51 | NCT00397189 | Erwachsene, primäre Insomnie |
| S3 van Geijlswijk | 20668840 | 10.1007/s00213-010-1962-0 | ISRCTN20033346 | Kinder 6–12, chronische SOL-Insomnie |

Zu prüfen ist gegen **alle drei**, nicht nur gegen die naheliegende. 16919138
trägt bereits einen Verdacht gegen S1 (gleiche Population, Crossover mit
11 Kindern gegen 146 randomisierte) — der ist mit dem Volltext zu klären,
nicht mit dem Abstract.

Regel: `dedup_ergebnis = Doppel` verlangt `status = ausgeschlossen`. Eine
zweite Zeile derselben Personen gibt es auch dann nicht, wenn eine Fassung
adjustiert und eine unadjustiert ist.

## B und F — Crossover und gepaarte Streuung

Drei Felder sind neu, weil das alte Formular die Entscheidung nicht abbildete:

| Feld | Werte | Bedeutung |
|---|---|---|
| `crossover_pfad` | `C1` / `C2` / `C4` / `C5-erste-Periode` / `C5-Ausschluss` | welcher Pfad der Crossover-Regel greift |
| `sd_diff_quelle` | `berichtet` / `aus CI` / `aus r geschaetzt` | Herkunft der gepaarten Streuung |
| `se_unpaired` | Zahl in Minuten | konservative SE nach C4, nur für die Sensitivität |

Die Pfade nach `crossover_regel_20261108.md`:

| Pfad | Bedingung | Was in `se` steht |
|---|---|---|
| C1 | SD_diff, SE_diff oder CI der Differenz berichtet | SE_diff, oder SE aus dem CI: (oben − unten) / 3,919928 |
| C2 | nur Armstreuungen berichtet | SD_diff = √(SD₁² + SD₂² − 2·0,5·SD₁·SD₂), dann SE = SD_diff/√n; `r = 0,5`, `r_geschaetzt = ja` |
| C4 | weder SD_diff noch brauchbare Armstreuung | ungepaarte SE in `se_unpaired`, Hauptzeile bleibt leer, Status `Zahlen fehlen` |
| C5-erste-Periode | kein Washout, Periodeneffekt signifikant oder Baseline schief | Effekt der ersten Periode wie eine Parallelstudie |
| C5-Ausschluss | Carryover problematisch | `status = ausgeschlossen`, Führung nur in der Sensitivität |

Zwei Prüfungen, die das Skript erzwingt: `se` muss kleiner sein als
`se_unpaired` (sonst sind gepaarte und ungepaarte Streuung vertauscht), und
Pfad C2 verlangt r = 0,5 mit `r_geschaetzt = ja`. Ein geschätzter Wert sieht
im Datensatz anders aus als ein berichteter.

## Ausfüllregeln

R1–R11 aus `extraktionsformular_20261108.md` gelten unverändert. Ergänzt:

**R12 — Dedup vor Extraktion.** Schritt 1 wird für jede Zeile ausgefüllt,
bevor Zahlen eingetragen werden. `ungeklaert` ist ein zulässiges Ergebnis,
leer nicht.

**R13 — Register-ID wörtlich.** Die ID wird so eingetragen, wie sie im
Volltext steht, samt Bindestrichen und Leerzeichen. Kein Auffüllen auf ein
vermutetes Format.

**R14 — Keine Registerrecherche im Netz.** Der Abgleich erfolgt gegen den
Volltext und die Registerangaben, die dort zitiert sind. Ein Registerabruf
wäre ein Netzlauf und braucht eine eigene Freigabe.

**R15 — Gepaarte Streuung vor Gruppenstreuung.** Liegt SD_diff vor, wird sie
genommen, auch wenn die Armstreuungen zusätzlich berichtet sind. Die
Armstreuungen gehen nur in `se_unpaired`.

**R16 — r wird nicht optimiert.** Es gilt 0,5 nach C2; 0 und 0,8 sind
Sensitivitäten, keine Alternativen zur Hauptzeile.

**R17 — Crossover bleibt Crossover.** Eine Crossover-Studie wird nicht als
Parallelstudie eingetragen, auch nicht „vereinfachend". Designwechsel nur
über C5 mit Begründung.

**R18 — Doppel zählt nie doppelt.** Auch nicht als Sensitivität.

**R19 — Zahlenformat.** Dezimalkomma wie in den bestehenden Zeilen,
Tausenderpunkt nur bei Bedarf. Das Prüfskript liest beides.

**R20 — Status ist ein Urteil, kein Zwischenstand.** `offen` heißt
unbearbeitet. Sobald Zahlen eingetragen sind, steht einer der übrigen Werte.

## Prüfskript

```text
.venv/bin/python.exe scripts/pruefe_extraktion_20261109.py --vorlage
.venv/bin/python.exe scripts/pruefe_extraktion_20261109.py --check
.venv/bin/python.exe scripts/pruefe_extraktion_20261109.py --selbsttest
```

| Code | Prüfung |
|---|---|
| E01 | Pflichtfeld leer |
| E02 | `status`, `design` oder `crossover_pfad` unzulässig |
| E03 | Crossover ohne gültigen Pfad |
| E04 | Pfad C1 ohne SD_diff, SE_diff oder CI |
| E05 | Pfad C2 ohne r = 0,5 oder ohne `r_geschaetzt = ja` |
| E06 | Pfad C4 ohne `se_unpaired` |
| E07 | Pfad C5 ohne erste Periode bzw. ohne Ausschlussstatus |
| E08 | `se` nicht kleiner als `se_unpaired` (Verwechslung) |
| E09 | `Doppel` ohne `status = ausgeschlossen` |
| E10 | designbedingte Leerstelle leer statt `entfaellt` (Warnung) |
| E11 | Armwerte vorhanden, `streuungsart` fehlt |
| E12 | Einheit nicht Minuten und keine Umrechnung notiert |
| E13 | fehlende Registrierung ohne Fundstelle oder ohne Abgleich |
| E14 | Wert in `dedup_gegen` oder `dedup_ergebnis` unzulässig |
| E15 | `poolbar` ohne Effekt oder ohne SE |
| E16 | bearbeitete Zeile ohne Zitat oder Fundstelle (Warnung) |

Exit 0 nur ohne Fehler. Warnungen allein ändern den Exit-Code nicht.

Solange `status = offen` steht, prüft das Skript nur `studie_id`, `pmid` und
`doi`. Die Fachregeln E02–E16 greifen ab der ersten bearbeiteten Zeile, damit
die frische Vorlage vor der Lieferung mit „20 offen, 0 Fehler" durchläuft und
der Exit-Code eine Aussage hat.

## Zwei Beispielfälle aus der Lieferliste

**16919138 (Garstang 2006, Crossover, 11 Kinder).** Schritt 1:
`dedup_gegen = S1`, `dedup_merkmal = Register-ID; n; Rekrutierungszeitraum`,
`dedup_ergebnis = ungeklaert`, `dedup_beleg = Crossover mit 11 Kindern gegen
146 randomisierte bei S1, Register-ID im Abstract nicht genannt`. Schritt 2
entscheidet: gleiche ID → Doppel, andere ID → unabhängig. Bis dahin bleibt
`status = offen`, und es wird nichts extrahiert.

**9566656 (McArthur 1998, Rett-Syndrom).** Crossover, im Abstract
„42,1 ± 12,0 auf 19,1 ± 5,3 min", ohne Angabe ob SD oder SE. Pfad C2 nur,
wenn die Streuungsart im Volltext geklärt ist; sonst C4 mit `se_unpaired`
und `status = Zahlen fehlen`. Bei n = 11 unterscheidet die Streuungsart die
gepoolte Unsicherheit um Faktor 3,3 — die Zeile ist ohne diese Klärung nicht
poolbar.

## Prüfschritte vor dem Pooling

1. Jede Zeile hat `dedup_ergebnis` und `register_id`, keine ist `offen`.
2. Jede Crossover-Zeile hat `crossover_pfad`; C1/C2 nur mit belegter
   Streuung, sonst C4.
3. `se` < `se_unpaired` in jeder Zeile, in der beide stehen.
4. Keine Zeile mit `Doppel` ist `poolbar`.
5. Jede Zahl hat `fundstelle` und `zitat`.
6. `streuungsart` ist gesetzt, wo Armwerte stehen.
7. `--check` endet mit Exit 0 und ohne Fehler.

## Grenzen

- Das Formular erzwingt Vollständigkeit der Prüfblöcke, nicht ihre
  Richtigkeit. Ein falsch abgeschriebenes n besteht jede Strukturprüfung.
- Registerangaben werden nicht im Netz gegengeprüft (R14). Wer den
  Registerabruf braucht, braucht dafür eine Freigabe.
- Die Zuordnung „welche Studie ist gemeint" bleibt eine menschliche
  Entscheidung; das Skript prüft nur, dass sie dokumentiert ist.
- Bei den fünf gestrichenen B-Titeln (Triage Klasse D) entsteht keine Zeile.
  Sie stehen nur in der Bestellliste, nicht in der Vorlage.
