# Abschlussbericht: Kann der Harness aus guten Studien eine korrekte Metaanalyse erstellen?

Stand: 2026-11-08. Read-only-Validierung: kein Netz, kein Modellaufruf, keine
Aenderung an Pipeline oder Analysedaten. Alle Zahlen stammen aus den
Einzelberichten in diesem Verzeichnis und den dort genannten JSON-Dateien.

## Antwort in einem Satz

**Rechnen ja, lesen nein.** Die Pooling-Engine reproduziert die Referenzwerte
auf sieben Nachkommastellen und besteht alle sieben Verhaltensfaelle; die
Extraktion findet an einer guten Primaerstudie (MENDS) **0 von 2** berichteten
Effekten, obwohl beide als Wert mit Intervall in einer Tabellenzelle stehen -
der Blocker ist die Kopfzeilen- und Spaltenzuordnung, nicht die Datenlage. Die
Kette ist damit nur so gut wie die Struktur der Tabelle, aus der sie liest.

## Pruefaufbau

Drei Ebenen, jede einzeln gegen einen Sollwert aus belegten Zahlen. E2 zuerst,
weil es ohne Netz und ohne Modell in unter einer Sekunde pruefbar ist; E1 danach
auf dem deterministischen Lesepfad, weil der LLM-Extraktor Modellaufrufe
braucht und dafuer keine Freigabe vorliegt.

| Ebene | Gegenstand | Ergebnis | Bericht |
|---|---|---|---|
| E2 | `meta/pooling.py`, 3 Studienwerte, DL + HKSJ | **PASS** | `e2_pooling_20261108.md` |
| E1 | `meta/extraction.py` auf MENDS-Text, 2 Effekte | **FAIL** (0/2) | `e1_extraktion_20261108.md` |
| Blocker | warum E1 scheitert, auf MENDS und auf 120 Dateien | Kopf + Spalten | `kopf_blocker_mends_20261108.md`, `kopf_blocker_korpus_20261108.md` |
| Stichprobe | sind die verschlossenen Zeilen die gesuchten Effekte? | **0 von 20** | `nur_kopf_stichprobe_20261108.md`, `nur_kopf_bewertung_20261108.md` |

## Befund 1 (E2): die Rechnung ist in Ordnung

Referenz: `data/bench/sol2/pooling_sol3_20261108.json`, Analyse "Hauptanalyse",
k = 3, Methode `hksj`, Gewichtung `DL`, Toleranz 0,01.

| Kennzahl | Soll | Ist | Abweichung |
|---|---:|---:|---:|
| Gepoolter Effekt (min) | -26,287199 | -26,287207 | 7,96e-06 |
| Untere 95%-KI (min) | -55,571872 | -55,571878 | 5,90e-06 |
| Obere 95%-KI (min) | 2,997474 | 2,997464 | 1,00e-05 |
| tau^2 (min^2) | 104,496184 | 104,495670 | 5,14e-04 |
| Cochran Q | 5,409473 | 5,409443 | 2,98e-05 |
| I^2 (%) | 63,027820 | 63,027616 | 2,04e-04 |

Alle sechs Abweichungen liegen um Groessenordnungen unter der Toleranz und sind
Rundungsartefakte. Zusaetzlich bestehen sieben Verhaltensfaelle (U1-U7) gegen
**von Hand nachgerechnete** Werte: identische SE, stark unterschiedliche SE,
eine Studie mit SE 60, keine Heterogenitaet, k = 1, ungueltige Eingaben,
fehlende Streuung. Laufzeit 0,92 s.

Zwei Einschraenkungen gehoeren zum Befund:

- Die sechs Kennzahlen pruefen **Reproduzierbarkeit** des hauseigenen
  Referenzlaufs (`pool_sol3_20261108.json`), nicht Uebereinstimmung mit einer
  fremden Implementierung. Der unabhaengige Teil von E2 sind die sieben
  Handwert-Faelle; ein Abgleich gegen R `metafor` oder `statsmodels` steht aus.
- **U7 deckt eine stille Schwaeche auf:** eine Zeile ohne SE faellt ohne
  Fehlermeldung heraus, `k` sinkt von 3 auf 2, und die `excluded`-Liste bleibt
  leer. Formal bestanden, praktisch eine Falle: der Aufrufer erfaehrt nicht,
  dass eine Studie fehlt.
- **Korrektur am Testentwurf:** U3 erwartete zuerst pooled = -10,0 und lief auf
  FAIL mit Abweichung 3,33e-02. Falsch war der Sollwert, nicht die Engine:
  die Studie mit SE 60 traegt 0,11 % Gewicht, korrekt ist -10,0333 bei
  tau^2 = 0. Angepasst wurde der Sollwert, kein Harness-Ergebnis.

## Befund 2 (E1): die Extraktion findet die MENDS-Effekte nicht

Eingabe `data/bench/sol2/volltext/23098680.txt` (831.660 Zeichen, 48
Tabellenbloecke). Soll: Tagebuch -37,49 min (95% CI -55,27 bis -19,71),
Aktigraphie -45,34 (-68,75 bis -21,93). Gefunden: **nichts**.

- `text_arm_candidates`: 0, `change_candidates`: 0, Tabellenpfad: 0 Effekte.
- Haeufigster Ablehnungsgrund: `keine Effektspalte im Kopf` - **378** von 724
  abgelehnten Zeilen; danach Spaltenzahl-Konflikte zwischen Kopf und Zeile.
- Die Zellen sind lesbar: `-37.49 (-55.27 to -19.71)` liefert
  `parse_effect_cell` sauber `(-37,49; -55,27; -19,71)`. Die zugehoerigen
  Kopfzellen sind `(SD)` und `571.26 (71.98)` - daraus erkennt
  `header_effect_kind` keine Effektspalte.

Der Fehler ist damit lokalisiert: **die Zahl liegt maschinenlesbar vor, die
Kopfzeile sagt dem Leser nicht, dass es ein Effekt ist.** Der Effekt steht
zusaetzlich als Satz im Fliesstext (Textzeilen 125/413/1729/1769 bzw.
126/415/1730/1776) - ein frueherer Bericht behauptete, er stehe *nur* dort; das
war falsch und ist als Korrektur am Befundtext ausgewiesen, nicht als
nachgebessertes Messergebnis.

## Befund 3: der Blocker ist strukturell, nicht ein Einzelfall

Gemessen wurde, wie viele abgelehnte Zeilen einen lesbaren Effekt samt Intervall
tragen:

| Korpus | Dateien | Bloecke | abgelehnt | lesbar | Anteil | `nur_kopf` | `kopf_und_spalten` |
|---|---:|---:|---:|---:|---:|---:|---:|
| MENDS | 1 | 48 | 724 | 23 | 3,18 % | 3 | 20 |
| Stichprobe `sol/fulltext` | 120 | 276 | 5.445 | 530 | 9,73 % | 187 | 343 |

`position_daneben` kommt in beiden Korpren **0-mal** vor: es fehlt nie nur die
Position der Effektspalte, es fehlt die Effektspalte selbst oder die
Spaltenzuordnung ist verschoben. Ein reiner Kopfzeilen-Fix rettet auf MENDS
hoechstens 3 Zeilen.

## Befund 4: die verschlossenen Zeilen sind nicht die gesuchten Effekte

Deterministische Stichprobe (Seed 20261108) von 20 der 187 `nur_kopf`-Zeilen,
einzeln nach Label, Zelle, Kopfzelle und Caption beurteilt:

| Urteil | Zeilen | Anteil |
|---|---:|---:|
| kein Effekt (Baseline, Median/IQR, Textzelle, Teststatistik) | 13 | 65 % |
| Veraenderung innerhalb einer Gruppe | 3 | 15 % |
| Effektschaetzer aus einer Uebersicht/Metaanalyse | 4 | 20 % |
| **Between-Group-Effekt einer Primaerstudie** | **0** | **0 %** |

Beispiele fuer die Fehllesung: `Fat-free mass (kg)` / `58.6 (50.5-68.8)` ist
eine Baseline-Charakteristik, `2 mg/day, 1-2 hr before going to bed` ein
Dosistext, der als `[2; 1; 2]` gelesen wird, `t = 0.93, p = 0.47; BCa [...]`
eine Teststatistik. Fuenf der 20 Zeilen sind solche falsch positiven
Zelllesungen. Die vier echten Effekte (`OR 2.29`, `g = -0.16`, `IRR 1.07`,
`-1.80 [-2.86, -0.73]`) stammen aus Uebersichtsarbeiten - sie in den eigenen
Pool zu nehmen waere eine Doppelzaehlung der Teilnehmer.

Hochrechnung: erwartete gesuchte Effekte **0 von 187**; die exakte obere
95 %-Grenze bei 0 von 20 ist `1 - 0.05^(1/20) = 13,9 %`, also hoechstens rund
26 Zeilen als Obergrenze. Etwa 37 echte Effektschaetzer anderer Art und rund 28
arm-interne Veraenderungen sind zu erwarten.

## Was die drei Befunde zusammen bedeuten

1. **Die Rechenstufe ist nicht der Engpass.** Wer die Engine pruefen will, ist
   mit E2 fertig: sie tut, was dokumentiert ist, und sie tut es schnell.
2. **Die Lesestufe ist der Engpass, und sie scheitert an der Form, nicht am
   Inhalt.** Beim MENDS-Fall - einer guten Studie mit sauber berichtetem
   Ergebnis - liegt die Zahl lesbar in der Tabelle, und der Leser kommt nicht
   heran. Genau diese Kette sollte die Frage beantworten.
3. **Der naheliegende Fix ist keine Loesung.** Wer die Kopfzeilenerkennung
   lockert, oeffnet ueberwiegend Baseline-Zahlen, Altersangaben, Dosistexte und
   Teststatistiken - und in 20 % der Faelle fremde Pooling-Schaetzer. Der
   erste Teil ist Rauschen, der zweite ist ein Designfehler.
4. **Damit ist die Frage beantwortet, nicht das Werkzeug repariert.** Der
   Harness kann aus strukturell intakten Tabellen eine korrekte Metaanalyse
   rechnen; aus realen Volltexttabellen mit `(SD)`-Kopfzeilen und
   Spaltenverschiebungen liest er die Primaereffekte nicht zuverlaessig.

## Belastbarkeit: was traegt, was nicht

**Traegt:**

- E2-PASS gegen sechs Referenzkennzahlen und sieben Handwertfaelle.
- E1-FAIL ist kein Messfehler: die Zellen sind reproduzierbar lesbar, die
  Kopfzellen reproduzierbar als "keine Effektspalte" klassifiziert.
- 0 von 20 gesuchten Effekten in der Stichprobe; die Einzelurteile sind im
  Bewertungsdokument nachpruefbar.
- Der Blocker ist auf zwei unabhaengigen Korpren gemessen (1 Datei / 120
  Dateien).

**Traegt nicht:**

- E2 ist kein externer Abgleich; metafor/statsmodels fehlen.
- Nur der deterministische Lesepfad wurde geprueft. Der LLM-Extraktor
  (`EffectExtractor`) lief nie - ob er die MENDS-Zeile findet, ist **offen**
  und nicht Teil dieses Berichts.
- E1 stuetzt sich auf eine Studie. Dass die Kette an MENDS scheitert, ist ein
  belegter Einzelfall mit Korpus-Rueckhalt, keine Quote fuer den Gesamtbestand.
- Die Stichprobe hat n = 20 (10,7 %), Einzelbewertung ohne Zweitleser. Die
  Hochrechnung ist eine Extrapolation, als solche gekennzeichnet.
- Geprueft wurde die Textebene (`23098680.txt`), nicht das PDF. Die
  Produktionskette liest das PDF; Fehler der PDF-Extraktion sind hier nicht
  abgedeckt.

## Was ausdruecklich nicht folgt

- **Kein Kopfzeilen-Fix.** Er verschiebt das Problem von "findet nichts" zu
  "findet Baseline-Zahlen und fremde Pooling-Schaetzer" - der zweite Zustand
  ist schlechter, weil er plausibel aussieht.
- **Kein E3-Kettentest ohne Freigabe.** Er kostet Modellaufrufe und wuerde bei
  diesem Stand vor allem die bereits belegte Lesegrenze reproduzieren.
- **Keine Nachbesserung der Testentwuerfe, um PASS zu erzeugen.** Die einzige
  Korrektur betraf einen falschen Sollwert (E2/U3) und ist offengelegt.

## Reproduktion

```bash
export PYTHONIOENCODING=utf-8
.venv/bin/python.exe scripts/validate_pooling_e2.py        # 0,92 s, PASS
.venv/bin/python.exe scripts/validate_extraction_e1.py     # 0,98 s, FAIL 0/2
.venv/bin/python.exe scripts/messe_kopf_blocker.py --file data/bench/sol2/volltext/23098680.txt
.venv/bin/python.exe scripts/messe_kopf_blocker.py --dir data/bench/sol/fulltext --max-dateien 120
.venv/bin/python.exe scripts/pruefe_nur_kopf.py            # Seed 20261108, 20 von 187
```

Alle Laeufe sind ohne Netz und ohne Modellaufruf reproduzierbar. Die
Harness-Kernmodule (`meta/extraction.py`, `meta/pooling.py`) sind gitignored;
die Validierung ist deshalb nur im Arbeitsbaum reproduzierbar, nicht aus einem
frischen Clone.

## Offene Punkte

1. LLM-Extraktor gegen MENDS: **beantwortet** (Nachtrag unten). Er findet
   keinen der beiden Effekte, obwohl der Satz im Prompt steht - er liest 1 von
   3 Effekten des Absatzes. Die Frage, ob die Kette ueber den Modellpfad
   rettbar ist, ist damit offen, nicht bejaht.
2. Externer Pooling-Abgleich gegen `metafor` (R) oder `statsmodels`, damit E2
   nicht nur Reproduzierbarkeit belegt.
3. `pool()` sollte fehlende SE-Zeilen melden statt sie still zu verwerfen
   (Befund U7) - Code-Aenderung, keine Validierung.

## Nachtrag: der LLM-Extraktor (E3a)

Ein Lauf, ein Pass, ein Dokument - freigegeben und durchgefuehrt. Kosten
5.444 Tokens, 5,3 s, keine Engine-Fehler. Ergebnis: **0 von 2** Sollwerten.
Das Modell las den Ergebnisabsatz und zitierte den TST-Effekt
(22,43 [0,52; 44,34]) korrekt, gab aber die beiden SOL-Effekte im naechsten Satz nicht als Zeilen
zurueck, obwohl der Prompt sie woertlich enthaelt und mehr Vollstaendigkeit
verlangt.

Zwei Zusatzbefunde:

- **Der Selektor ist selbst ein Filter.** `select_text` kuerzt 841.300 auf
  25.582 Zeichen nach Topic-Woertern. Mit `melatonin` stehen beide Sollzahlen
  im Prompt, mit `melatonin and sleep outcomes` und `sleep` keine. Die
  Vorauswahl entscheidet damit, ob ein berichteter Effekt den Leser ueberhaupt
  erreicht.
- **Die beiden Pfade scheitern verschieden, am selben Punkt.** E1 sieht die
  Zelle nicht (Kopfzeile), E3a sieht den Satz und gibt ihn nicht als Zeile
  zurueck. Fuer k = 3 ist beides gleich toedlich.

Der Befund stuetzt sich auf einen Lauf ohne Zweitleser; er ist ein
Einzelurteil, keine Haeufigkeitsaussage. Details: `e3_llm_20261108.md`.

### Nachtrag 2: der isolierte Satz (E3b)

Derselbe Satz allein - 254 Zeichen statt 841.300, Prompt 2.205 statt 25.582
Zeichen, 1.205 Tokens, 7,5 s. Ergebnis: **1 von 2**. Zurueck kam Aktigraphie
-45,34 [-68,75; -21,93] korrekt (se 11,9441, Outcome "Sleep Onset Latency
(SOL)", Comparison "Melatonin vs Placebo (Actigraphy)"), und die Quote war der
ganze Satz - also inklusive des Tagebuch-Intervalls -37,49, das nicht als
Zeile ausgegeben wurde.

Damit ist die Kontextlaenge als Ursache ausgeschlossen: Der Fehler tritt bei
einem Zwoelftel des Prompts unveraendert auf. Was bleibt, ist die Schreibweise
- zwei Messmethoden in einem Satz, verbunden mit "and actigraphy". Das Modell
versteht den Satz, zerlegt ihn aber nicht in zwei Zeilen. Zusammen mit E3a
(eine Zeile: TST) sieht es nach einer Regel "eine Zeile pro Effekt-Aussage"
aus. Fuer die Metaanalyse ist das der teuerste Fehlertyp: Die ankommende Zeile
ist korrekt, das Fehlen der zweiten faellt nur beim Abgleich mit dem Sollwert
auf. Ein Absatz-Chunking wuerde nicht helfen - der Satz war bereits allein.
Details: `e3b_satz_20261108.md`.

### Nachtrag 3: die Prompt-Regel (E3c)

Lokal in `extraction.py` ergaenzt (gitignored, nicht committet): "One row per
measurement method" - bei zwei Messmethoden in einem Satz eine Zeile je
Methode. Prompt 2.417 Zeichen, 953 Tokens, 4,9 s. Ergebnis: **wieder 1 von 2**,
diesmal das Tagebuch-Intervall -37,49 mit `comparison = sleep diaries`.

Die Regel wird gelesen und befolgt - die Comparison nennt jetzt die
Messmethode statt der Gruppengegenueberstellung - aber sie erzeugt keine
zweite Zeile. Drei Laeufe, drei verschiedene Einzelzeilen (TST, Aktigraphie,
Tagebuch): genau eine Zeile, Auswahl variabel.

Das Harness ist als Ursache ausgeschlossen, soweit ohne Rohantwort pruefbar:
`unwrap_json_list` laesst zwei Items in allen vier typischen Antwortformen
durch, der Regex-Fallback halbiert keine reine Array-Antwort, und die
Engine-Statistik zeigt einen einzigen Completion-Aufruf ohne Retry. Eine
Zwei-Zeilen-Antwort waere angekommen.

Konsequenz: Mehr Prompt loest es nicht. Der naechste Hebel ist eine
deterministische Nachpruefung - enthaelt eine Quote zwei CI-Klammern, aber es
kam nur eine Zeile zurueck, muss das als Luecke gemeldet werden statt still
als k = 1 weiterzulaufen. Details: `e3c_regel_20261108.md`.

### Nachtrag 4: die Lueckenpruefung (E4)

Gebaut, ohne Modellaufruf und ohne Eingriff ins Pooling:
`research_agent/meta/quote_gaps.py` zaehlt die CI-Klammern einer Quote und
vergleicht sie mit den Zeilen, die aus ihr stammen. Die harte Aussage ist
die Anzahl; welches Intervall fehlt, ist eine Zuordnung ueber die Zahlen.

Beleg an den drei E3-Artefakten, Zeilen unveraendert aus den JSONs:

| Lauf | Zeilen | Intervalle | Status |
|---|---:|---:|---|
| E3a (TST) | 1 | 1 | ok |
| E3b (Aktigraphie) | 1 | 2 | Luecke: Tagebuch -37,49 fehlt |
| E3c (Tagebuch) | 1 | 2 | Luecke: Aktigraphie -45,34 fehlt |

Gegenproben: mit beiden gemessenen Zeilen `ok`, bei einem Satz ohne
CI-Angabe `nicht_pruefbar` - der Check meldet nicht pauschal. 17 Tests.

Der erste Lauf der Pruefung stufte E3a als `nicht_pruefbar` ein: Seine Quote
schreibt das CI verschachtelt (`[95% confidence interval (CI) 0.52 to
44.34]`), ein Regex auf klammerfreie Inhalte uebersah sie. Der Scanner
zaehlt seitdem die Klammertiefe. Das war ein Fehler der Pruefung, nicht der
Daten - deshalb steht er hier.

Kosten: 0 Modellaufrufe, 0 Tokens. Grenze: Die Pruefung belegt die Luecke,
sie schliesst sie nicht; die fehlende Zeile muss weiterhin gelesen werden.
In die Kette ist sie noch nicht verdrahtet - die Anschlussstelle ist die
Quellen-Review, nicht `pool()`. Details: `e4_quote_luecken_20261108.md`.

### Nachtrag 5: die Haeufigkeit im Bestand (E4b)

Read-only auf Kopien, 65 DBs mit `study_effects`, 0 Lesefehler. Tabellenzeilen
werden nicht beurteilt: Ohne Kopfzeile ist keine Klammer sicher ein
Effektintervall - dieselbe Grenze wie E1. Von 281 Quotes der Themen-Laeufe
sind 34 pruefbar: 28 ok, 6 Luecken. Gelesen sind 5 echte Luecken (jeweils ein
anderer Outcome im selben Satz) und 1 Grenzfall (Model 1/Model 2). Der
MENDS-Typ - dasselbe Outcome ueber zwei Messmethoden - trat nicht erneut auf.
247 Quotes nennen kein CI; dort ist die Pruefung blind. Zusatz: zwei
identische Zeilen (1,33) in einer exercise-Quote. Details:
`e4_bestand_20261108.md`.

### Nachtrag 6: doppelte Zeilen (E4c)

Read-only auf Kopien, 65 DBs. Definition: gleiche Quelle, gleiche Quote,
gleicher Effekt, gleiches KI, gleicher Outcome. In den 9 Themen-DBs stehen
201 Zeilen mit Effekt, davon 64 ueberzaehlige in 61 Duplikat-Gruppen (32 %);
keine Gruppe hat mehrere Extraktoren, es sind echte Kopien.

Das Pooling faengt sie: `build_analysis` ruft `_collapse_same_study` vor
`pool()` und verwirft 39 Zeilen. Die Zaehlung von 64 ist eine Obergrenze ueber
alle Zeilen, auch nicht poolbare; die Differenz ist kein Rest an Dubletten.

Was ohne den Kollaps passieren wuerde, an echten Zeilen gemessen (`pool()`
direkt): Gruppe incident CVD [log_ratio] der mediterranen DB, k 6 statt 5,
gepoolt 0,295 statt 0,240, KI-Breite 1,20 statt 1,53. Die Dublette trug 69 %
des Gewichts. Der Kollaps ist also kein Schoenheitsfehler, sondern der Grund,
warum die Zahl stimmt - und das war vorher nur behauptet, nicht gemessen.

Grenze: Der Kollaps greift je Outcome-Gruppe und zaehlt auch legitime
abhaengige Zeilen (Arme, Kontraste) - bei kognition halbiert er k von 10 auf
5. Das ist Absicht (Unabhaengigkeit), macht die 39 aber zur Obergrenze.
Details: `e4_duplikate_20261108.md`.

### Nachtrag 7: was der Kollaps verwirft (E4d)

Die 39 verworfenen Zeilen wurden gegen ihre Quote klassifiziert (Nachbau der
Kollaps-Logik, Abgleich 39 = 39): 26 exakte Dubletten, 4 mit gleichem Wert
und anderer Belegstelle, 9 mit einem anderen Effekt.

Die 26 exakten Dubletten sind ein Speicherfehler ohne Erkenntnisverlust; der
Kollaps entfernt sie richtig. Bei den 9 anderen Effekten behaelt das Pooling
willkuerlich die praezisere Zeile - und das ist nicht immer die richtige:

- incident CVD: behalten OR 2,65 (Rheumatoide Arthritis), verworfen OR 1,67
  (Mittelmeer-Diaet) - verschiedene Expositionen in einer Outcome-Gruppe.
- MACE: behalten OR 2,2 (abdominale Adipositas), verworfen OR 1,78
  (Ernaehrungsrisiko) - ebenfalls verschiedene Expositionen.
- preeclampsia: 0,78 behalten gegen 0,31/0,72/0,76/0,61 verworfen - vier
  unabhaengige Schaetzungen, teils andere Adjustierung oder anderes Mass.
- frailty: 0,14 (ELSA) gegen 0,15 (LBC1936) - zwei Kohorten.
- depressive symptoms: zwei Wertebereiche aus einer Aussage.

Also: kein Gewichtsfehler (die Dubletten sind weg), aber 9 Zeilen
Informationsverlust, davon mindestens zwei mit falscher Auswahl, weil der
Kollaps nach Quelle und Outcome gruppiert, nicht nach Exposition. Das ist
eine inhaltliche Grenze des Poolings, nicht der Zaehlung.
Details: `e4_kollaps_20261108.md`.

### Nachtrag 8: Exposition im Kollaps-Schluessel (E4e)

Lokal in `pooling.py` (gitignored, nicht committet): Der Kollaps vergleicht
zusaetzlich die berichtete Exposition (`comparison`). Zwei Zeilen derselben
Quelle kollabieren nur, wenn die Exposition gleich oder eine leer ist - oder
wenn Effekt und Standardfehler identisch sind (dann ist es eine Kopie). Die
vier Schluessel-Dicts fuehren Listen von Indizes, damit eine Kopie auch dann
kollabiert, wenn zwischen ihr und dem Original eine andere Exposition steht.

Gemessen auf Kopien, 10 Themen-DBs, 38 Gruppen: 6 aendern sich, 32 nicht.

- preeclampsia [log_ratio]: k 1 -> 5, gepoolt -0,309 [-0,491; -0,126]
  (vorher kein Pool).
- incident CVD [log_ratio]: k 4 -> 5, 0,178 [-0,914; 1,269] ->
  0,240 [-0,524; 1,005]. KI-Breite 2,18 -> 1,53.
- MACE [log_ratio]: k 3 -> 4, 0,770 [0,259; 1,281] -> 0,742 [0,430; 1,053].
  KI-Breite 1,02 -> 0,62.
- depressive symptoms [raw:beta]: k 3 -> 4, -0,023 [-0,545; 0,499] ->
  -0,033 [-0,301; 0,236].
- depressive symptoms [fisher_z]: k 1 -> 2, -0,180 [-0,548; 0,187].
- frailty index [raw:beta]: k 1 -> 2, 0,142 [0,088; 0,197].

Der Gewinn ist die richtige Zeile: Bei incident CVD bleibt die
Mittelmeer-Diaet-Schaetzung neben der Rheumatologie-Zeile stehen, statt
willkuerlich ersetzt zu werden. Der Preis ist Ueberpraezision: Die neuen
Zeilen stammen aus derselben Quelle und sind abhaengig; das KI wird enger
(incident CVD 2,18 -> 1,53), obwohl die Unabhaengigkeit nicht gestiegen ist.
Ohne cluster-robuste Schaetzung (`pool_rve`, gruppiert nach `source_id`) ist
die Regel deshalb nur zusammen mit dem RVE-Pfad vertretbar.

Die exakten Dubletten kollabieren weiter: `height` und `educational
attainment` bleiben unveraendert. Ein erster Messlauf zeigte 16 geaenderte
Gruppen, weil die Kopie-Erkennung fehlte und gleiche Werte mit anderem
comparison-Text getrennt wurden; der Fehler ist behoben und steht hier, weil
er sonst als Wirkung durchgegangen waere.

Grenze: `comparison` unterscheidet nicht zwischen anderer Exposition und
anderer Stufe derselben Exposition (Dosis-Kategorien). Ein Pool mit beiden
zaehlt dieselben Personen doppelt; die Regel ist deshalb nur fuer klar
verschiedene Expositionen richtig. Ruecknahme: die vier Dict-Typen zurueck
auf `Dict[str, int]`, die Hit-Variablen entfernen, `comparison` aus dem
standardisierten Dict streichen. Details: `e4e_vergleich_20261108.md`.

### Nachtrag 9: RVE gegen HKJ (E4f)

Die betroffenen Gruppen cluster-robust gerechnet (`pool_rve`, CR0, t auf
M-1 df), Cluster = Quelle:

| Gruppe | k | M | HKJ-Breite | RVE-Breite | Faktor |
|---|---:|---:|---:|---:|---:|
| preeclampsia [log_ratio] | 5 | 1 | 0,364 | - | - |
| frailty index [raw:beta] | 2 | 1 | 0,108 | - | - |
| depressive symptoms [fisher_z] | 2 | 1 | 0,735 | - | - |
| MACE [log_ratio] | 4 | 3 | 0,624 | 1,137 | 1,82 |
| incident CVD [log_ratio] | 5 | 4 | 1,529 | 1,438 | 0,94 |
| depressive symptoms [raw:beta] | 4 | 3 | 0,536 | 0,458 | 0,86 |

Drei der sechs Gruppen haben nur einen Cluster. Dort ist kein
cluster-robustes Intervall schaetzbar - das HKJ-Intervall von preeclampsia
[-0,491; -0,126] ist scheinpraezise, weil alle fuenf Zeilen aus einer Quelle
stammen. Das ist der staerkste Befund dieser Messung.

Bei den uebrigen ist RVE nur bei MACE deutlich breiter (Faktor 1,82); incident
CVD und raw:beta sind etwas schmaler. Der Grund: `pool_rve` ist ein
Fixed-Effect-Schaetzer und traegt tau2 nicht, waehrend HKJ random effects
rechnet. Bei starker Heterogenitaet (depressive symptoms [log_ratio]:
HKJ 0,748, RVE 0,068) ist RVE viel schmaler - das ist kein Gewinn an
Praezision, sondern ein anderes Modell. Der Breitenvergleich ist deshalb nur
bei gleichem Modell aussagekraeftig.

Konsequenz: Der neue Kollaps-Schluessel ist fuer Gruppen mit M >= 2
vertretbar, wenn das RVE-Intervall daneben berichtet wird; fuer M = 1 darf
kein gepooltes KI stehen, nur eine Sichtung. Details: `e4f_rve_20261108.md`.

### Nachtrag 10: M-Gate (E4g)

`research_agent/meta/pool_gates.py` (neu, committet) entfernt einem Pool mit
`rve.M < 2` alle Intervalle - HKJ, fixed effect und Prediction Interval -,
setzt `single_cluster = True` und laesst den Punktschaetzer als Sichtung
stehen. Verdrahtet in `build_analysis` direkt nach `pool_rve`; die
Pooling-Logik selbst bleibt unveraendert.

Von 10 Gruppen mit k >= 2 greift das Gate bei 3:

| Gruppe | k | M | gepoolt | KI-Breite vorher |
|---|---:|---:|---:|---:|
| preeclampsia [log_ratio] | 5 | 1 | -0,309 | 0,364 |
| frailty index [raw:beta] | 2 | 1 | 0,142 | 0,108 |
| depressive symptoms [fisher_z] | 2 | 1 | -0,180 | 0,735 |

preeclampsia trug vorher [-0,491; -0,126]; dieses Intervall ist jetzt weg,
der Punktschaetzer bleibt. Die 7 uebrigen Gruppen behalten ihr KI. Fehlt
`rve`, greift das Gate nicht - keine Annahme ohne Messung. Details:
`e4g_m_gate_20261108.md`.

Nebenbefund: Das Dashboard rendert `Number(g.ci_low).toFixed(3)`; bei `None`
waere das `[0,000; 0,000]` geworden.Es zeigt jetzt "kein KI (nur ein unabhaengiger Cluster)".

### Nachtrag 11: Report-Hinweis, RVE-Annahmen, Dashboard-Test (E4h)

**Warum `[-, -]`.** `forest_table` druckt die gepoolte Zeile immer; das KI
ist bei M = 1 `None`, und `_meta_num(None)` gibt `-` zurueck. Die Zeile sagte
also nicht "Daten fehlen", sondern "Unsicherheit nicht schaetzbar" - und
sagte das nicht.

**Report.** `report.py` hat jetzt einen eigenen Zweig fuer `single_cluster`:
"Kein Konfidenzintervall: 5 Zeilen, aber nur 1 unabhaengige Quelle. Der
Punktschaetzer -0,309 ist eine Sichtung, keine Schaetzung. Es fehlen nicht die
Daten - es fehlt die zweite unabhaengige Einheit, aus der sich Unsicherheit
schaetzen liesse." Es wird kein Intervall erzeugt. Geprueft an einer Kopie der
mediterranen DB: 279 Zeilen Ausgabe, Hinweis genau einmal, Abschnitt rendert
(`report_meta_ausschnitt_20261108.txt`).

**Entscheidung zu gitignored.** `report.py` bleibt gitignored, wie die Regel
es verlangt. Der Patch ist lokal; die Sicherung liegt in
`local_patches/report_20261108.py` (neu gitignored), die Entscheidung hier.
Dauerhaft versionieren ginge nur ueber eine Aenderung der Repo-Regel - das
ist nicht meine Entscheidung.

**RVE.** In `e4f_rve_20261108.md` stehen jetzt die Modellannahmen: HKJ ist
Random Effects mit tau^2 in den Gewichten, RVE ist Fixed Effect ohne tau^2.
Ein Breitenvergleich ist deshalb kein Beweis fuer Scheinpraezision. MACE
bleibt Einzelfall (0,624 gegen 1,137), ohne Trennung von Modell- und
Cluster-Effekt.

**Dashboard.** Gerendert mit injizierter API-Antwort, weil der Live-Endpunkt
den Orchestrator braucht: preeclampsia zeigt "kein KI (nur ein unabhaengiger
Cluster)", MACE "[0.430; 1.050]", kein "[0,000; 0,000]". Protokoll:
`dashboard_render_protokoll_20261108.md`.

**Repo.** `local_patches/` ist gitignored; dort liegen Sicherungen von
`pooling.py`, `report.py` und `pool_gates.py`. Fremde uncommittete Dateien
wurden nicht angefasst.

## Nachtrag 12 - Entscheidung zur report.py-Regel (2026-11-08)

Die Regel bleibt: `report.py` ist gitignored und wird nicht committet. Der
Grund ist nachgelesen, nicht angenommen: Die `.gitignore`-Sektion
"Kernbausteine: nicht oeffentlich" schuetzt IP - Orchestrierung,
Statistik-Engine, Extraktionslogik. `report.py` hat 2183 Zeilen und war nie
im Repo. Die Regel aufzuheben waere eine Geschaeftsentscheidung ueber die
Veroeffentlichung dieser Logik, keine technische. Ich habe sie deshalb nicht
eigenmaechtig geaendert.

Stattdessen ist die Aenderung jetzt ohne Quellcode nachvollziehbar:

- `research_agent/patches/README.md` haelt die Regel fest. Ein Diff wird
  bewusst nicht abgelegt - ein Diff ist Quellcode aus einer geschuetzten
  Datei.
- `research_agent/patches/report_single_cluster_20261108.md` beschreibt
  Anlass, Ankerpunkt (`_meta_section`, vor dem `elif pooled_enough`-Zweig),
  Wirkung, Pruefschritte und die lokale Sicherung.
- `scripts/pruefe_report_patch.py` prueft read-only drei Marker (Gate
  definiert, Gate aufgerufen, Report erklaert) plus den Byte-Vergleich mit
  `local_patches/report_20261108.py`. Exit 1, wenn der Patch fehlt.
- `research_agent/tests/test_pruefe_report_patch.py` prueft, dass das Skript
  auch den Stand vor dem Patch als "nicht wirksam" erkennt - ein Pruefskript,
  das immer OK sagt, ist keins.
- `AGENTS.md` und `.gitignore` verweisen auf die Regel.

Grenze, unveraendert: Bei einem frischen Klon fehlt der Hinweis trotzdem. Das
ist die Folge des IP-Schutzes, jetzt aber sichtbar (Exit 1) statt still.

## Nachtrag 13 - RVE mit Random-Effects-Gewichten (2026-11-09)

Die offene Frage aus E4f: Wie viel der MACE-Verbreiterung (1,137 gegen 0,624,
Faktor 1,82) kommt vom Fixed-Effect-Modell, wie viel von der
Cluster-Korrektur?

**Umsetzung.** `pool_rve` kann jetzt beides. Die Mathematik liegt committet in
`research_agent/meta/rve_weights.py`: `w = 1/(v + tau2)` fuer Punkt UND
Sandwich, CR0 mit `M/(M-1)`, t auf `M-1` df. Nur so gilt die CR0-Identitaet;
die frueher dokumentierte Sorge betraf den Mischfall FE-Punkt mit
RE-Gewichten. `pooling.py` ist nur verdrahtet (Default bleibt
`weights="fixed"`), Patch-Eintrag `pooling_rve_weights_20261109.md`.

**Messung** auf denselben Zeilen vor dem Kollaps
(`e4i_rve_modell_20261108.json`):

| Gruppe | HKJ | RVE-FE | RVE-RE | RE/HKJ | Modellanteil |
|---|---:|---:|---:|---:|---:|
| MACE | 0,624 | 1,137 | 1,137 | 1,82 | 0 % |
| incident CVD | 1,529 | 1,438 | 1,791 | 1,17 | 139 % |
| depressive [raw:beta] | 0,536 | 0,458 | 0,772 | 1,44 | 143 % |
| depressive [hedges_g] | 1,466 | 1,550 | 1,270 | 0,87 | 139 % |
| depressive [log_ratio] | 0,748 | 0,068 | 0,659 | 0,88 | -1772 % |

**MACE.** tau2 ist in beiden Rechnungen 0,000 (REML 0,002), die Gewichte sind
identisch, RVE-FE und RVE-RE bitgleich. Die Verbreiterung ist damit
**vollstaendig Cluster-Effekt** - das Modell traegt nichts dazu bei. Was E4f
also offen liess ("interessant, aber nicht entschieden"), ist entschieden: Die
naive Rechnung unterschätzt die Unsicherheit hier allein wegen abhaengiger
Zeilen.

**Die anderen Gruppen sind anders zu lesen.** Bei `hedges_g`, `raw:beta`,
`log_ratio` und `incident CVD` wirken Modell- und Cluster-Beitrag teilweise
gegeneinander; Anteile ueber 100 Prozent oder negativ zeigen das. Dort ist die
Zahl kein "Anteil Scheinpraezision", sondern nur zusammen mit den beiden
Log-Beitraegen lesbar. Ein generelles Urteil "RVE war zu breit" folgt daraus
nicht - fuer MACE schon.

**Grenzen.** tau2 wird aus den Zeilen vor dem Kollaps geschaetzt, HKJ aus den
kollabierten Zeilen; das ist eine Annaeherung. Die Zerlegung ist eine
Log-Breiten-Zerlegung, keine Varianzzerlegung. Sechs neue Tests
(`test_rve_weights.py`) pruefen die Formel gegen handgerechnete Werte,
darunter `tau2 = 0` gegen den FE-Fall.

## Nachtrag 14 - RVE-RE als zweite Zeile im Report (2026-11-09)

Die Messung aus Nachtrag 13 lag nur in `data/bench/validierung/`. Der Report
nannte die RVE-Breite und liess den Modellanteil offen - an der Stelle, an der
er gelesen wird, fehlte die Trennung.

**Patch.** `_meta_section` bekommt nach dem RVE-Block eine zweite Zeile aus
`rve_re`: Punkt und Intervall mit Random-Effects-Gewichten, dazu der Faktor
zur Fixed-Effect-Variante. Sind beide Breiten gleich (tau2 = 0), sagt der Text
es ausdruecklich. Patch-Eintrag `report_rve_re_20261109.md`, Sicherung
`local_patches/report_20261109.py`.

**Beleg** (`report_rve_re_20261109.txt`, DB-Kopie, 282 Zeilen):

- MACE: `RVE (M = 3): 0.751 [0.182; 1.319]` und `RVE mit Random-Effects-
  Gewichten (M = 3): 0.751 [0.182; 1.319]. Breite identisch ... reiner
  Cluster-Effekt.`
- incident CVD: FE-Breite `[-0.849; 0.589]`, RE `0.295 [-0.600; 1.191]`,
  Faktor 1.25 - hier wirkt das Modell mit.
- preeclampsia: nur der M=1-Hinweis, keine RVE-Zeile (unveraendert).

**Pruefung.** 66 Report-Tests gruen (u. a. `test_meta_report`,
`test_report_honesty`); `pruefe_report_patch.py` Exit 0 mit vier Markern in
`report.py`; Sicherung byte-identisch. Fehlt `rve_re` (aeltere Analysen),
rendert der Report unveraendert.

## Nachtrag 15 - tau2 auf demselben Material (2026-11-09)

Frage: Haelt der 1,25-Faktor bei `incident CVD`?

**Antwort: ja, aber er ist nicht das, was der Report zuerst behauptete.**

- tau2: `HKJ(alle)` und `RVE-RE` benutzen dieselben Zeilen und dieselbe
  DL-Schaetzung; in 7 von 7 verfuegbaren Gruppen ist die Zahl identisch. Die
  Zerlegung Modell/Cluster ist damit konsistent - die frueher vermutete
  Ungenauigkeit durch zwei verschiedene Zeilenbasen existiert fuer diesen
  Vergleich nicht.
- `incident CVD`: Modell `ln(RE/FE)` = 0,220 (Faktor 1,25), Cluster
  `ln(RE_RVE/HKJ_alle)` = 0,401 (1,49), Duplikation
  `ln(HKJ_alle/HKJ_koll)` = -0,242 (0,78), Summe 0,159 = RE/HKJ 1,17.
- `MACE`: Modell 0, Cluster 1,018 (2,77), Duplikation -0,417 (0,66), Summe
  0,601 = 1,82.

Damit war der Satz im Report ("der restliche Teil der Verbreiterung kommt aus
der Cluster-Korrektur") falsch: Bei `incident CVD` heben sich Cluster und
Duplikation teilweise auf. Der Text nennt den Faktor jetzt "reiner
Modellwechsel" und sagt, dass die Verbreiterung gegenueber dem naiven
Intervall zusaetzlich Cluster-Korrektur und die andere Zeilenbasis enthaelt.

| Gruppe | HKJ(koll) | HKJ(alle) | RVE-FE | RVE-RE | Cluster | Duplikation "
"| Modell |
|---|---:|---:|---:|---:|---:|---:|---:|
| MACE | 0,624 | 0,411 | 1,137 | 1,137 | 1,018 | -0,417 | 0,000 |
| incident CVD | 1,529 | 1,200 | 1,438 | 1,791 | 0,401 | -0,242 | 0,220 |
| depressive [raw:beta] | 0,536 | 0,536 | 0,458 | 0,772 | 0,365 | 0,000 | 0,521 |
| depressive [hedges_g] | 1,466 | 0,805 | 1,550 | 1,270 | 0,456 | -0,600 | -0,199 |
| depressive [log_ratio] | 0,748 | 0,507 | 0,068 | 0,659 | 0,262 | -0,389 | 2,264 |

Die Duplikationsspalte ist der Preis der kollabierten Rechnung: Sie sieht
weniger Zeilen und wird breiter, nicht weil sie ehrlicher waere, sondern weil
ihr Information fehlt. Bei `MACE` und den depressiven Gruppen ist der Effekt
deutlich; bei `raw:beta` ist er null, weil der Kollaps dort nichts entfernt.

**Umsetzung.** Nur das Messskript wurde geaendert (`pool(sub_rows)` als
dritte Rechnung, dreiteilige Zerlegung), `pooling.py` bleibt unangetastet.
Damit entfaellt ein neuer Patch-Eintrag; der Report-Text wurde im bestehenden
Eintrag `report_rve_re_20261109.md` nachgezogen.
