# Abschlussbericht SOL: warum 1.056 Dokumente kein k >= 2 ergeben

Stand: 07.11.2026. Frage: verkuerzt Melatonin die Einschlaflatenz (SOL)
gegenueber Placebo? Antwort des Korpus: **mit diesen Lesern nicht
beantwortbar** - nicht weil die Suche zu klein waere, sondern weil die
Literatur die Zahlen nicht in poolbarer Form berichtet. Alle Zahlen unten
stammen aus den Laeufen vom 07.11.2026 (`data/bench/sol/*.json`, `*.db`,
`*_befund_20261107.md`).

## 1. Der Korpus

| Kennzahl | Wert |
|---|---:|
| Europe-PMC-Treffer (`melatonin AND "sleep onset latency" AND randomized AND OPEN_ACCESS:y`) | 1.068 |
| zurueckgeliefert | 1.067 |
| davon mit PMCID | 1.059 |
| XML tatsaechlich geladen | 1.056 |
| Download-Fehler (HTTP 500) | 3 |
| Crossref-Gegenprobe: Ueberlappung | 3 von 100 |
| Crossref-Gegenprobe: Metaanalysen | 1 |

Das ist praktisch die vollstaendige offene Literatur zu dieser Frage in
Europe PMC, nicht eine Stichprobe. 426 der 1.056 Dokumente enthalten
mindestens ein "Mittelwert +- SD"-Paar im Text.

## 2. Vier Leser, alle deterministisch

| Leser | liest | Zeilen | Dokumente | Gruppen | k >= 2 |
|---|---|---:|---:|---:|---:|
| Effektspalten (`effect-column/1`) | fertige Effektspalten in Tabellen | 513 | 18 | 154 | 0 |
| Arm-Rechner (`arm-level/1`) | zwei Arme mit n und Streuung in einer Tabellenzeile | 8 | 4 | 8 | 0 |
| Fliesstext Post-Werte (`arm-text/1`) | Ergebnissatz mit zwei Mittelwerten +- SD | 1 | 1 | 1 | 0 |
| Veraenderungswerte (`arm-change/1`) | gemeldete oder prae/post-Veraenderung | 1 | 1 | 1 | 0 |
| **Summe** | | **523** | | **162** | **0** |

Jede gespeicherte Zeile traegt ein woertliches Zitat, das per
`locate_quote` gegen den XML-Text geprueft wurde. Die 523 Zeilen sind also
nicht "vielleicht richtig", sondern belegt - und trotzdem nicht poolbar.

## 3. Warum k >= 2 nicht entsteht

**(a) Die Effektspalten sind keine SMD.** Von 513 Zeilen sind nur 15 ein
Hedges g und 15 ein SMD; 197 sind Regressionskoeffizienten (`beta`), 160
Odds Ratios, 112 Mittelwertdifferenzen, 12 Risk Ratios, 2 Hazard Ratios.
Ein OR und ein g lassen sich nicht in denselben Pool legen. Von den 513
Zeilen betreffen zudem nur **5** ueberhaupt eine Latenz; der Rest sind
Nebenendpunkte (PSQI, Epworth, Schlafarchitektur, Nebenwirkungen) und
Tabellenreste (`model 1` und `model 2` je 63-mal - Regressionsmodelle,
keine Behandlungseffekte). Die 154 Outcome-Gruppen stammen aus 18
Dokumenten: jedes Papier berichtet seinen eigenen Endpunktsatz, und
selbst wenn zwei dasselbe messen, heisst es einmal
`Sleep onset latency, min` und einmal `Sleep latency (min)`.

**(b) Die Streuung fehlt in der berichteten Form.** Der Fliesstext-Leser
hat 315.857 Saetze geprueft. 242.564 enthalten keinen Mittelwert mit
Streuung; 1.747 nennen SEM oder SE statt SD, 1.138 Median/IQR. Der
Arm-Rechner scheitert an 3.138 Tabellenzeilen ohne Mittelwert mit
eindeutiger Streuung in zwei Spalten und an 182 fehlenden Fallzahlen je
Arm. Eine SMD braucht SD und n je Arm - beides steht selten gemeinsam da.

**(c) Die Studien berichten armeise, nicht kontrastweise.** Der
Change-Leser hat 38.393 Saetze abgelehnt, weil sie die Veraenderung nur
fuer **einen** Arm nennen ("SOL sank in der Melatoningruppe von 32,1 auf
18,3 min"). In den ersten 120 Dokumenten gibt es genau einen Satz mit zwei
prae/post-Paaren, und der ist eine Tabellenunterschrift. Der
Zwei-Arm-Kontrast, den ein Effekt braucht, existiert im Text meist nicht
als Satz - er existiert nur in der Tabelle, und dort ohne SD.

**(d) Der einzige scheinbare Treffer ist ein Artefakt.** Die Vereinigung
aller vier Leser ergibt 162 Outcome-Gruppen; genau eine traegt zwei
Studien, der Schluessel `low`. Dort steht ein OR ("Low", 10.1002/fsn3.1050)
neben einer Tertilzeile ("Low (< 9.49)", 10.1186/s12889-026-26824-4) -
zwei Bedeutungen von "low" und zwei nicht vergleichbare Effektmasse.
Gefiltert auf Effekttyp g bleibt k = 1. Der einzige fruehere k = 2-Pool
(`total sleep time min`, 100-Dokument-Lauf) war ebenfalls falsch: eine
Querschnittstabelle (aktive vs. inaktive Kinder) plus ein
Baseline-Kontrast (`Day 0`). Beide Faelle sind der Grund, warum das
Design-Gate im Arm-Rechner existiert.

## 4. Was das methodisch bedeutet

1. **k >= 2 ist keine Funktion der Korpusgroesse, sondern der
   Berichtsform.** Der Korpus wuchs von 100 auf 1.056 Dokumente (10,6x);
   die Zahl poolbarer Gruppen blieb 0. Eine groessere Suche haette 10x
   mehr Fragmente erzeugt, nicht einen Pool. Die Grenze liegt im
   Publikationsformat, nicht im Retrieval.

2. **Deterministische Leser haben eine Nachweisgrenze, und sie ist hier
   erreicht.** Was fehlt, ist nicht Rechenleistung, sondern Information:
   SD je Arm, Zwei-Arm-Kontraste, einheitliche Endpunktnamen. Ein LLM
   wuerde dieselbe Luecke nicht fuellen - es wuerde sie ueberschreiben.
   Genau das ist in der Fruehphase passiert: 11 Zeilen mit Alter, BMI und
   Tabellenresten, 10 Regressionskoeffizienten als Behandlungseffekt, 16
   Zeilen ohne benannte Skala, 5 Zeilen aus einer fremden Metaanalyse, 47
   Baseline-Zeilen und 10 Querschnittsvergleiche - alle inzwischen durch
   Gates abgelehnt. Diese Fehlerhistorie ist der eigentliche Ertrag: sie
   sagt, welche Fehlgriffe ein automatischer Leser in dieser
   Literaturgattung macht.

3. **Ein negativer Befund ist hier ein Ergebnis, kein Scheitern.** Die
   belegte Aussage lautet: die offene Europe-PMC-Literatur zu Melatonin
   und SOL enthaelt nicht genug kongruent berichtete Zwei-Arm-Daten, um
   eine SMD zu poolen. Wer trotzdem poolt, muss Zahlen erfinden oder
   Skalen mischen. Ein Bericht, der "k = 1, g = 0,413" ausgibt, ist
   ehrlicher als einer mit CI aus zwei unvergleichbaren Zeilen.

4. **Der eine belegte Effekt bleibt.** `10.1371/journal.pmed.1002587`
   (PMC6005466), DLMO: Melatonin +0,73 +- 1,21 h (n = 23) gegen Placebo
   +0,24 +- 1,11 h (n = 20), g = 0,413 (SE 0,309, n = 43), Zitat exact.
   Post-Wert- und Change-Leser finden denselben Satz und rechnen denselben
   Effekt - das ist die beste Verfuegbarkeitspruefung, die dieser Korpus
   hergibt. Die Studie selbst schreibt, die Differenz sei nicht
   signifikant (P > 0,05).

## 5. Was hier nicht gehoert wird

* **Keine Risk-of-Bias-Bewertung.** Die Gates pruefen Berichtsform, nicht
  Studienqualitaet. Verblindung, Allokation, ITT sind nirgends erfasst.
* **Kein Publikationsbias.** Bei k = 0 ist ein Funnel-Plot sinnlos; die
  Frage bleibt offen.
* **Keine Abbildungen.** Ein grosser Teil der RCTs zeigt SOL als
  Forest- oder Balkendiagramm. Diese Daten sind im XML nicht als Zahl
  vorhanden und wurden nicht digitalisiert.
* **Kein Satzuebergriff.** Ein Arm im Satz n und der andere im Satz n+1
  wird nicht zusammengefuehrt - bewusst, weil das ohne Semantik
  fehleranfaellig ist.
* **3 von 1.059 Dokumenten fehlen** (HTTP 500 bei Europe PMC). Bei diesem
  Ergebnis unerheblich, fuer eine spaetere Zaehlung zu vermerken.
* **Outcome-Normalisierung ist grob.** Der Fall `low` zeigt, dass
  Label-Kollisionen echte Pools vortaeuschen koennen. Jede k-Aussage
  braucht deshalb den Filter auf Effekttyp.

## 6. Empfehlung

Der offene Korpus ist ausgeschoepft; weitere Leser auf denselben 1.056
Dokumenten verschieben das Ergebnis nicht. Der groesste Hebel ist ein
**Saat-Korpus aus einer publizierten Metaanalyse**: die Crossref-Gegenprobe
fand genau eine ("Efficacy and safety of melatonin for sleep onset insomnia
in children and adolescents"). Deren eingeschlossene Trials liefern per
Konstruktion k >= 2 mit extrahierbaren Werten - und erlauben die einzige
saubere Validierung, die noch fehlt: unsere Zeilen gegen ein bekanntes
gepooltes Ergebnis zu halten. Kosten: eine gezielte Suche plus
Datenextraktion; Risiko: die Metaanalyse ist paywalled und ihre Tabelle
muss aus dem Abstract oder Supplement kommen.
