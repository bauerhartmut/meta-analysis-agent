# Crossover-Regel: vorab fixiert am 2026-11-08

Zweck: Festlegen, wie Studien mit Crossover-Design in Extraktion und Pooling
eingehen - **bevor** die zwölf bestellten Volltexte eintreffen. Die Regel
darf nach Sichtung der Ergebnisse nicht geändert werden; Anpassungen sind nur
als zusätzliche, klar benannte Sensitivität zulässig.

Betroffen sind mindestens drei der zwölf bestellten Titel (20535539,
16919138, 9566656) und vier weitere aus der Klasse B (18078449, 15275698,
11211063, 26569624).

## Warum das vorab geklärt werden muss

Bei einem Crossover sieht jede Person beide Behandlungen. Die Differenz
innerhalb einer Person ist präziser als der Vergleich zweier Gruppen, weil
die Zwischenpersonen-Varianz herausfällt. Wer trotzdem die Streuung der
Gruppenmittelwerte verwendet, überschätzt den Standardfehler und unterschätzt
das Gewicht der Studie.

Zahlenbeispiel mit SD = 50 min in beiden Armen und n = 20:

| Annahme | SD der Differenz | SE | Verhältnis zur gepaarten SE |
|---|---:|---:|---:|
| gepaart, r = 0,8 | 31,6 | 7,1 | 1,00 |
| gepaart, r = 0,5 | 50,0 | 11,2 | 1,58 |
| gepaart, r = 0,0 | 70,7 | 15,8 | 2,24 |
| ungepaart (wie Parallelstudie) | - | 15,8 | 2,24 |

Die ungepaarte Rechnung ist bei r > 0 also konservativ: Sie verzerrt den
Punktschätzer nicht, macht das Intervall aber zu breit. Das ist der sichere
Fehler - aber er kostet Präzision, und bei k = 3 fällt das ins Gewicht.

## Die Regeln

**C1 - Hauptanalyse: gepaarte Differenz.** Der Effekt ist die mittlere
Differenz innerhalb der Personen (Verum minus Placebo). Der Standardfehler
ist SE = SD_diff / Wurzel(n), mit n = Anzahl der Personen, nicht der
Beobachtungen. Liegt ein Konfidenzintervall für die gepaarte Differenz vor,
wird SE daraus abgeleitet: SE = (obere - untere Grenze) / 3,919928.

**C2 - Fehlt SD_diff: Korrelation r = 0,5.** Dann gilt
SD_diff = Wurzel(SD_verum² + SD_placebo² - 2 · r · SD_verum · SD_placebo).
r = 0,5 ist der von Cochrane empfohlene Ausgangswert, wenn die Korrelation
nicht berichtet ist. Die Schätzung wird in der Extraktionstabelle als
"r geschätzt" markiert.

**C3 - Sensitivität für r.** Zusätzlich werden r = 0 und r = 0,8 gerechnet.
Das zeigt die Spanne, die allein aus der unbekannten Korrelation folgt. Bei
r = 0 ist die gepaarte Rechnung identisch mit der ungepaarten.

**C4 - Sensitivität ungepaart.** Als konservative Untergrenze der Präzision
wird zusätzlich die ungepaarte SE gerechnet:
SE = Wurzel(SD_verum²/n + SD_placebo²/n). Diese Variante überschätzt die
Unsicherheit, verzerrt aber nicht. Sie ist die Rückfalllinie, wenn weder
SD_diff noch eine brauchbare Korrelation verfügbar ist.

**C5 - Carryover und Periodeneffekte.** Wenn kein Washout berichtet ist, ein
Periodeneffekt signifikant war oder die Baseline zwischen den Perioden
differiert, wird die Studie in der Hauptanalyse nicht mit dem gepoolten
Crossover-Effekt geführt. Stattdessen: Auswertung der ersten Periode allein
(wie eine Parallelstudie) oder Ausschluss aus der Hauptanalyse und Führung
nur in der Sensitivität. Die Entscheidung wird je Studie begründet.

**C6 - Mehrere Dosen oder Perioden.** Von einer Crossover-Studie mit mehreren
Dosierungen geht nur die Dosis ein, die der Auswahlregel entspricht
(`auswahlregel_pooling_20261108.md`). Dieselben Personen dürfen nicht
mehrfach als unabhängige Beobachtungen gezählt werden.

**C7 - Keine erfundene Korrelation.** Wird r geschätzt, steht das im
Datensatz und im Bericht. Es wird nicht der Eindruck erweckt, r sei
berichtet worden. Wenn eine der bestellten Studien individuelle
Differenzwerte oder SD_diff berichtet, hat diese Angabe Vorrang vor jeder
Schätzung.

## Anwendung auf die bestellten Studien

| PMID | Design | Was im Abstract steht | Vorgehen nach C1-C7 |
|---|---|---|---|
| 20535539 | Crossover, 3 Monate je Arm, max. 10 mg | Verbesserung um 47 min, keine Streuung | SD_diff oder CI suchen; sonst C2 mit r = 0,5, C3 zusätzlich |
| 16919138 | Crossover, 11 Kinder | 1,06 h vs. 1,91 h mit 95%-CI | SE aus dem CI der Differenz ableiten, wenn das CI die Differenz meint; sonst C2 |
| 9566656 | Crossover, Rett-Syndrom | 42,1 ± 12,0 auf 19,1 ± 5,3 min (SE) | C2; zusätzlich C4, weil die Streuung als SE und nicht als SD berichtet ist - Umrechnung prüfen |
| 18078449 | Crossover, 5 mg CR | "etwa 30 min", keine Streuung | C2, C3 |
| 15275698 | Crossover, 25 Patienten | nur p = 0,019 | C2, C3; ohne Zahlen nur Sensitivität |
| 11211063 | Crossover, 20 Erwachsene, PSG | "signifikant", keine Werte | C2, C3 |
| 26569624 | Crossover, 48 Kinder, 3 mg | SOL unklar berichtet | erst prüfen, ob SOL überhaupt ein Endpunkt ist |

## RoB 2 für Crossover

Die RoB-2-Bewertung wird für Crossover-Studien um die Domäne "Bias arising
from period and carryover effects" ergänzt. Bewertet werden: Washout-Dauer im
Verhältnis zur Halbwertszeit, Test auf Periodeneffekt, stabile Baseline
zwischen den Perioden, mögliche Übertragungseffekte. Das Urteil dieser
Domäne kann das Gesamturteil der Studie anheben.

## Was ausdrücklich nicht gemacht wird

- Keine Studie wird zweimal gezählt (einmal je Periode).
- Keine Korrelation wird erfunden, um ein engeres Intervall zu erhalten.
- Keine nachträgliche Änderung der Regel, nachdem die Ergebnisse bekannt
  sind - neue Varianten nur als zusätzliche Sensitivität mit Kennzeichnung.
- Kein Pooling einer Crossover-Studie mit einer Parallelstudie ohne
  Kennzeichnung des Designs in der Sensitivitätstabelle.

## Prüfplan nach Lieferung

1. Design je Volltext bestätigen (Crossover, Parallel, faktoriell).
2. Berichtete Streuung suchen: SD_diff, SE_diff, CI der Differenz.
3. Fehlt sie, C2 anwenden und r = 0,5 dokumentieren.
4. C3 und C4 als Sensitivitäten rechnen.
5. C5 prüfen (Washout, Periodeneffekt) und RoB-Domäne ergänzen.
6. Erst danach pooled rechnen - mit Design als Stratifizierungsmerkmal in
   der Sensitivitätstabelle.
