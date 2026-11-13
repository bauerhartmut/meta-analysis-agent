# Zweiter Goldstandard mit Armwerten: Prüfung und Vorgehen

Stand: 2026-11-13
Frage: Kann ein zweiter öffentlicher Goldstandard mit Armwerten die 28
GLASS-Cluster sinnvoll erweitern?
Kurzantwort: **Technisch ja, praktisch nein — außer über Cochrane (Lizenz) oder
ClinicalTrials.gov (anderer Extraktionsgegenstand).**

## Was geprüft wurde

| Quelle | Armwerte | Records | Cluster | Volltext | Lizenz | Urteil |
|---|---|---:|---:|---|---|---|
| GLASS / TrialReviewBench | nein | 81 | 45 | 54 von 81 | Labels MIT, Artikel eigene Rechte | erschöpft |
| European Urology (OSF) | ja (`arm_1.n`, `arm_1.events`, `arm_2.*`) | 104 | 20 Trials | 20 Records aus 2 PMIDs | keine Lizenz angegeben | zu klein nutzbar |
| Cochrane CDSR (über BEAR) | ja (`events1`, `total1`, `events2`, `total2`, `mean1`, `sd1`, ...) | 760.486 Ergebniszeilen, 90.042 Review-Studie-Paare, 6.619 Reviews | 6.619 Reviews | über PMID/DOI beschaffbar | nicht-kommerziell, KI-Nutzung nur mit Genehmigung | stark, aber blockiert |
| AACT / ClinicalTrials.gov | ja (`outcome_counts`, `outcome_measurements`, 907.566 Zeilen) | Registersätze | viele | Registertabelle, kein PDF | Public Domain | nutzbar, aber anderer Gegenstand |
| PICO-Corpus | teils (Armbezug) | 5.024 Zahlen | 1.011 Abstracts | nur Abstracts | keine Lizenzdatei | keine Outcome-Zuordnung |

## Befund 1: GLASS lässt sich nicht erweitern

Der Originaldatensatz enthält **81 Ergebniszeilen insgesamt** — nicht 81 von
mehreren hundert. Die Zielzeilen tragen `HR`/`sample`/`Name` oder
`Events`/`Total`/`n`; **per-Arm-Spalten gibt es nicht**. Mehr Records oder
Armwerte sind aus dieser Quelle nicht zu holen, unabhängig vom Aufwand. Die 28
Cluster sind die Obergrenze des Datensatzes, nicht eine Auswahl daraus.

## Befund 2: European Urology hat Armwerte, aber fast keinen Volltext

Die 104 Records führen echte Armzellen (`arm_1.n`, `arm_1.events`,
`arm_2.n`, `arm_2.events`), verteilt auf 20 Trials. Für die Extraktionsprüfung
braucht es aber den Volltext, aus dem das Modell lesen soll:

- 20 der 104 Records haben über Europe PMC einen offenen Volltext,
- diese 20 Records stammen aus **2 Publikationen** (PMID 29624800, 34986007),
- 77 Records sind nur als Abstract verfügbar, 7 gar nicht.

Damit bringt der Datensatz **etwa 2 Cluster** statt 20. Der Zugewinn an
statistischer Power ist marginal, der Aufwand (Adapter, Prompt-Erweiterung,
Lauf) dagegen vollständig.

## Befund 3: Cochrane wäre der richtige Datensatz, ist aber lizenzrechtlich zu

Der über BEAR aufbereitete CDSR-Auszug ist genau das, was fehlt: 760.486
Ergebniszeilen mit `events1`, `total1`, `events2`, `total2`, `mean1`, `sd1`,
`mean2`, `sd2`, dazu Studienname, Review-DOI, Outcome-Name und Effektmaß. Rund
90.000 Review-Studie-Paare in 6.619 Reviews, binär und kontinuierlich.

Die Cochrane-Nutzungsbedingungen sind jedoch eindeutig:

- nicht-kommerzielle Nutzung, Zustimmung zu den Bedingungen beim Download,
- „AI developers must obtain authorization before using data from Cochrane
  reviews for AI development, training, or implementation",
- „no implied permission exists without a licence".

Eine Auswertung, in der Sprachmodelle auf Cochrane-Daten geprüft werden, fällt
unter diese Klausel. Ohne schriftliche Genehmigung ist der Datensatz nicht
verwendbar, auch nicht für eine reine Evaluierung. Zusätzlich ist die
Weitergabe abgeleiteter Annotationen ungeklärt.

## Befund 4: ClinicalTrials.gov ist frei, aber ein anderer Task

AACT enthält armweise Ergebniszahlen frei und ohne Registrierung (Public
Domain, Flat Files 2,35 GB, `outcome_counts` 907.566 Zeilen). Damit ließe sich
ein großer Arm-Datensatz bauen — aber der Extraktionsgegenstand wäre die
Registertabelle, nicht die Publikation. Für die Frage „findet das Modell die
Armzahlen im PDF" wäre das ein Methodenwechsel, kein Zugewinn. Brauchbar wäre
es nur als zweite, getrennte Forschungsfrage.

## Was das für die Power bedeutet

Gerechnet mit `estimate_crossval_power.py` (8 Felder je Record, gepaarter
McNemar-Test, Alpha 0,05 zweiseitig, Power 0,80):

| Szenario | Records | Cluster | Felder | MDD (ICC 0,1 / 0,2 / Diskordanz 0,15) |
|---|---:|---:|---:|---|
| heute (GLASS) | 54 | 28 | 432 | 7,02 / 7,32 / 5,44 pp |
| + EU-Volltext | 74 | 24 | 592 | 6,31 / 6,83 / 4,89 pp |
| + EU komplett (Autorentabellen) | 158 | 42 | 1.264 | 4,45 / 4,90 / 3,44 pp |
| AACT, 60 Trials | 60 | 60 | 480 | 6,38 / 6,38 / 4,94 pp |
| AACT, 120 Trials | 120 | 120 | 960 | 4,52 / 4,52 / 3,50 pp |
| Cochrane, 200 Zeilen / 80 Reviews | 200 | 80 | 1.600 | 3,75 / 3,99 / 2,91 pp |

Der Sprung von 7,2 auf unter 5 Prozentpunkte braucht **mindestens 158 Records
aus 42 Clustern** — also entweder die vollständigen EU-Tabellen oder Cochrane.
Mit dem EU-Volltext allein (74/24) bleibt es bei 6,3 pp und damit praktisch
beim heutigen Stand.

## Vorgehen, in dieser Reihenfolge

**Stufe 1 — Anfrage an die European-Urology-Autoren (schon vorbereitet).**
Gegenstand: die im Artikel genannten 105 Trials statt der veröffentlichten 20,
mit Armwerten und Belegstelle. Erwartung: 104 zusätzliche Records aus 20
Trials, MDD 4,45 pp. Aufwand: eine Mail, kein Code. Abbruchkriterium: keine
Antwort nach vier Wochen oder Ablehnung.
Datei: `anfrage_eururology_autoren.md`.

**Stufe 2 — Cochrane-Genehmigung anfragen, nicht vorab nutzen.**
Gegenstand: nicht-kommerzielle Forschungsnutzung der CDSR-Ergebnisdaten zur
Evaluierung von Extraktionsmodellen, inklusive Klärung, ob abgeleitete
Annotationen (Gold-Zeilen ohne Originalzitate) weitergegeben werden dürfen.
Erwartung bei Zusage: 200 Zeilen aus 80 Reviews, MDD 3,75 pp. Aufwand: Mail an
Cochrane/Wiley, danach ein Adapter auf `events1/total1/events2/total2` und
Volltextbeschaffung über PMID. Risiko: Ablehnung oder Schweigen; dann bleibt
Stufe 1.

**Stufe 3 — nur falls beides scheitert: Bericht ohne zweiten Datensatz.**
Die 54 Records tragen dann die Aussage: rund 58-60 Prozent Recall, kein
Modellunterschied nachweisbar, MDD 7,2 pp. Das ist eine belastbare
Absoluteinschätzung und eine schwache Rangfolge — beides ehrlich so zu
benennen ist besser als ein methodisch verschobener Zusatzdatensatz.

**Nicht empfohlen:** EU-Volltext nachziehen (2 Cluster Zugewinn), AACT als
Ersatz (anderer Task), weitere GLASS-Records suchen (es gibt keine).

## Metriken für den Arm-Teil, wenn er kommt

Falls Stufe 1 oder 2 greift, kommen vier Kennzahlen dazu, die der heutige
Record-Vergleich nicht liefert:

1. Armzuordnung: Anteil Zellen im richtigen Arm (Intervention vs. Kontrolle).
2. Vertauschungsrate: Anteil Records, in denen beide Arme vertauscht sind.
3. 2x2-Exaktheit: Anteil Records mit allen vier Zellen korrekt.
4. Fehlende Zellen: Anteil nicht extrahierter Armzahlen.

Die Vertauschungsrate ist die interessante Größe — sie ist der Fehler, der eine
Metaanalyse am stärksten verzerrt und der in der bisherigen Auswertung
strukturell unsichtbar war.

## Grenzen dieser Prüfung

- Die Cochrane-Zahlen stammen aus der BEAR-Aufbereitung (Snapshot 20.11.2025),
  nicht aus einem eigenen CDSR-Download; die Rohdaten wurden nicht geladen.
- Die Aussage zur EU-Volltextlage stützt sich auf Europe PMC (resultType=lite);
  ein Zugriff über Verlagslizenzen oder Fernleihe könnte mehr als 20 Records
  liefern und wurde nicht geprüft.
- Die Power-Zahlen sind asymptotische Abschätzungen mit angenommenem ICC, keine
  Zusicherung.
- AACT wurde anhand von Dokumentation und Schema geprüft, nicht durch einen
  Testdownload der 2,35 GB.
