# Fehler und neues Vorhaben

Stand: 2026-11-08. Anlass sind zwei Rueckfragen des Nutzers: "Baust du gerade
die Metaanalyse zusammen oder macht es der Harness mit TudaGPT?" und "wir
testen aktuell nur den Harness, deswegen brauchen wir keine wirklichen
Studien". Dieses Dokument nennt die Fehler zuerst und das daraus folgende
Vorhaben danach. Keine Zahlen sind geschaetzt; jede hat eine Quelle.

## Teil 1: Fehler

### F1 - Falsche Achse: am Ergebnis statt an der Faehigkeit gearbeitet

**Was ich getan habe.** Die gepoolte Schaetzung selbst gerechnet:
`scripts/pool_sol3.py` auf Werten, die ich per Hand aus den Volltexten gezogen
und in Markdown-Tabellen dokumentiert habe. Ergebnis -26,29 min
[-55,57; 3,00], tau^2 = 104,5, Q = 5,409, I^2 = 63,0 %
(`pooling_sol3_20261108.json`).

**Was das nicht zeigt.** Nichts ueber den Harness. Die Zahl beweist, dass ich
rechnen und die Extraktion belegen kann - nicht, dass die Kette
`meta/extraction.py` -> `meta/pooling.py` -> `report.py` aus einem Korpus eine
richtige Metaanalyse erzeugt.

**Was der Harness tatsaechlich lieferte.** `data/harness_local.db`,
ausgewertet in `data/bench/harness_run_final.md`: 34 Studien, 21 Effektzeilen,
davon 16 `mean_diff` - aber nur **2 mit Konfidenzintervall** und 4 mit SE.
Daraus entsteht kein poolbarer Satz. Das ist die Kennzahl, die zaehlt, und ich
habe sie nie als Ergebnis meiner Arbeit genannt.

### F2 - Studienbeschaffung zum Hebel erklaert

In drei aufeinanderfolgenden Antworten lautete die Empfehlung "Bestellung
absenden", "k von 3 auf 5 heben", "83 Volltexte fehlen". Dazu entstanden die
Bestellanfrage, die Fernleihfassung und ein eigenes Bestellvorhaben. Fuer
einen Harness-Test ist das gegenstandslos: Testmaterial mit bekanntem Sollwert
genuegt, und die Beschaffung laeuft separat ueber den Uni-Zugang. Ich habe
einen Engpass bearbeitet, der nicht der Engpass der Frage war.

### F3 - Harness-Befund als Analyse-Limitation verbucht

Der MENDS-Befund - von 48 Tabellenbloecken hat kein Kopf Effektwort und KI,
die Schaetzung steht nur als Satz im Fliesstext (`-37,49 min, 95% CI -55,27 bis
-19,71`) - ist eine Aussage **ueber die Lesekette**. Genau das ist die
Faehigkeit, die geprueft werden soll. Ich habe ihn als Limitation der Analyse
dokumentiert und den Ausbau des Lesers ausdruecklich verworfen, statt den Fall
als Testfall zu nehmen.

### F4 - Ziel nicht erfragt

Vier Empfehlungen, keine einzige Rueckfrage, ob das Ziel Harness-Faehigkeit
oder Evidenzgewinn ist. Die Fehlannahme stand von Anfang an in meiner
Arbeitsweise; Wiederholung hat sie nicht korrigiert.

### F5 - Nebenprodukte mit Anspruch

`bestellvorhaben_20261108.md`, `scripts/bestellung_fertig.py`, die Nachtraege
in `stand_kurz_20261108.md` und `validierung_sol3_20261108.md`: handwerklich
sauber und geprueft, aber sie beantworten eine Frage, die nicht gestellt war.
Sie bleiben als Nebenprodukt liegen und werden nicht weiterverfolgt.

### Was strukturell dahinter steckt

Ich habe "hat der Agent eine Metaanalyse" mit "kann der Agent eine Metaanalyse"
verwechselt. Fuer eine Arbeit, die die Faehigkeit messen soll, ist ein selbst
gerechnetes Ergebnis kein Beleg, sondern eine Umgehung der zu pruefenden Kette.

## Teil 2: Neues Vorhaben

**Ziel.** Messen, ob der Harness aus guten Studien eine korrekte Metaanalyse
erzeugt. Nicht: eine Metaanalyse erzeugen. Die Studien sind Pruefmaterial mit
bekanntem Sollwert, keine Evidenz, die beschafft werden muss.

Drei Ebenen, aufsteigend. Jede hat einen Sollwert aus belegten Zahlen.

| Ebene | Eingabe | Sollwert | Was geprueft wird |
|---|---|---|---|
| E1 Extraktion | MENDS-Text (liegt lokal) | Tagebuch -37,49 min (95% CI -55,27 bis -19,71), SE 9,08; Aktigraphie -45,34 (-68,75 bis -21,93), SE 11,96 | Liest der Harness die berichtete Zeile ueberhaupt? |
| E2 Pooling | die drei Studienwerte mit SE | -26,29 [-55,57; 3,00], tau^2 = 104,5, Q = 5,409, I^2 = 63,0 % | Rechnet die Engine richtig? |
| E3 Kette | Referenzfaelle aus `data/goldstandard/goldstandard.csv` | Abweichung je Feld gegen die Toleranzen in `pflegeblatt.md` | Traegt Suche -> Screening -> Extraktion -> Bericht? |

**Reihenfolge und Abbruch.** E2 zuerst: ohne Netz und ohne Modell in Sekunden
pruefbar, und wenn das Pooling nicht reproduziert, ist jede weitere Messung
wertlos. Dann E1: findet der Leser die Zeile, die im Text steht? Erst wenn E1
und E2 gruen sind, hat E3 eine Aussagekraft; E3 kostet Modellaufrufe und
braucht daher eine eigene Freigabe.

**Erfolgskriterium.** Ein Satz mit Zahl, zum Beispiel "Die Engine reproduziert
alle drei Sollwerte mit Abweichung < 0,01" oder "Der Leser findet 0 von 2
berichteten SOL-Effekten". Beides ist ein Ergebnis. "Die Analyse steht bei
-26,29" ist keins.

### Was ich dafuer brauche

1. **Entscheidung zum Testkorpus.** Der Goldstandard ist derzeit Kaffee akut
   vs. Placebo, Reaktionszeit (`data/goldstandard/README.md`). Die SOL-Zahlen
   sind belegt, aber nicht als Referenzfall eingetragen. Bleibt es beim
   Kaffee-Korpus, oder wird SOL der Testfall?
2. **Freigabe fuer einen Offline-Lauf** (E1, E2): kein Netz, kein Modell,
   Laufzeit Sekunden.
3. **Spaeter fuer E3:** Freigabe fuer Modellaufrufe, weil jeder Lauf Budget
   kostet.

### Was ich nicht mehr tue

- keine Netzlaeufe zur Studienbeschaffung,
- keine Bestellungen, keine Fernleihe, keine Beschaffungsempfehlung,
- keine Erweiterung der Tabellen- oder Fliesstextleser ohne vorherige Messung,
- keine Empfehlung, die auf "mehr Studien" zielt.

## Teil 3: Regel fuer die naechsten Schritte

Vor jedem Schritt eine Zeile: **Verbessert das die Faehigkeit der Kette oder
nur das Ergebnis?** Nur das Ergebnis heisst: nicht machen, ausser der Nutzer
verlangt es ausdruecklich.

## Belege

`data/harness_local.db` und `data/bench/harness_run_final.md` (Harness-Stand),
`pooling_sol3_20261108.json` (eigene Rechnung),
`gegencheck/mends_kopf_20261108.md` (Lese-Befund),
`mends_hta_zusatz_20261108.md` (Sollwerte und SE),
`data/goldstandard/README.md` und `pflegeblatt.md` (Referenzkorpus),
`research_agent/evals/meta_benchmark.py` (Benchmark-Runner),
`plan_ausbeute_validierung_status_20261108.md` (offene Pakete B-b, D).
