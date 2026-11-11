# dCBT-I-Nachbau: Ergebnisse und warum B notwendig bleibt

## 1. Kurzfassung

Der Nachbau der Metaanalyse von Tsai et al. 2022 ist gelungen. Aus den
vier Primärstudien ergibt sich post-treatment ein gepoolter Effekt von
**Hedges g = -0,584** (95 %-KI **-1,029 bis -0,139**), k = 4,
**I² = 83,7 %**, tau² = 0,161. Die Publikation berichtet
**g = -0,58** (95 %-KI **-1,03 bis -0,13**), k = 4, **I² = 84 %**,
tau² = 0,17. Effekt und KI sind damit innerhalb der Toleranz
reproduziert.

Das ist ein mittlerer bis großer durchschnittlicher Vorteil der digitalen
CBT-I bei der subjektiven Schlafqualität. Der Wert ist aber kein
einheitlicher Effekt: Die vier Studien streuen stark, eine Studie zeigt
sogar einen numerischen Vorteil der Kontrolle, und die Heterogenität ist
mit 84 % sehr hoch. Der Pool ist deshalb ein guter Nachweis, dass die
Rechnung und die Extraktion der vier Armwerte stimmen, aber noch kein
Beleg dafür, dass die Extraktionsregeln auf beliebige andere Dokumente
übertragbar sind.

Genau dafür braucht es die unabhängige B-Annotation. A ist die erste
Annotation, B die zweite, blinde menschliche Gegenlesung. Ohne B gibt es
keine belastbare Inter-Rater-Reliabilität, keine systematische
Konflikterkennung und keinen unabhängigen Maßstab für die Pipeline. Der
erfolgreiche dCBT-I-Nachbau ersetzt B nicht.

## 2. Was wurde untersucht?

Die Frage der Publikation ist:

> Wie wirksam ist digital gelieferte CBT-I bei Jugendlichen und jungen
> Erwachsenen im Hinblick auf die subjektive Schlafqualität direkt nach
> der Behandlung?

Die vier eingeschlossenen randomisierten kontrollierten Studien
vergleichen eine digitale CBT-I mit einer Kontrollbedingung. Der
Zielzeitpunkt ist **post-treatment**, nicht der spätere Follow-up. Die
Instrumente unterscheiden sich:

- **PSQI:** Pittsburgh Sleep Quality Index, globaler Score von 0 bis 21;
  höher = schlechter.
- **ISI:** Insomnia Severity Index; höher = stärkere Insomnie.
- **HSDQi:** Holland Sleep Disorder Questionnaire, Insomnie-Subskala;
  höher = stärkere Insomnie.

Die Instrumente messen nicht exakt dasselbe Konstrukt. PSQI erfasst die
allgemeine Schlafqualität, ISI und HSDQi eher die Insomnieschwere. Die
Metaanalyse standardisiert die Werte deshalb zu einer gemeinsamen
Effektgröße. Das macht die Zahlen poolbar, aber nicht beliebig
austauschbar.

## 3. Die vier Studien im Einzelnen

| Studie | Instrument | Zeitpunkt | dCBT-I | Kontrolle | g | 95 %-KI | Gewicht |
|---|---|---|---:|---:|---:|---:|---:|
| Morris 2015 | PSQI | 6 Wochen | 5,17 (2,50); n = 48 | 6,68 (3,37); n = 47 | -0,506 | -0,91; -0,10 | 25,3 % |
| Freeman 2017 | ISI | Woche 10 | 9,23 (5,18); n = 1891 | 12,95 (5,27); n = 1864 | -0,712 | -0,81; -0,61 | 31,4 % |
| Fucito 2017 | PSQI | Woche 5 | 10,85 (2,02); n = 21 | 10,13 (1,97); n = 21 | +0,354 | -0,26; +0,96 | 20,2 % |
| de Bruin 2018 | HSDQi | post-treatment | 2,86 (0,71); n = 39 | 3,74 (0,62); n = 39 | -1,307 | -1,80; -0,82 | 23,1 % |

Die Gewichte stammen aus dem Forest Plot der Review. Sie sind keine
einfachen Prozentanteile der Stichprobe, sondern die Gewichte des
Random-Effects-Modells.

### 3.1 Morris 2015

Morris untersuchte Studierende, die Stressmanagement lernen wollten. Die
Insomnia-Relief-Gruppe hatte post-treatment einen PSQI von 5,17
(SD 2,50), die Kontrolle 6,68 (SD 3,37). Das ergibt g = -0,506, einen
moderaten Vorteil der Intervention.

Wichtig: Die Tabelle nennt 48 bzw. 47 randomisierte Personen, die
Post-Werte beruhen aber auf 36 bzw. 44 Completern. Die Review verwendet
die randomisierten N. Mit den Completer-N ergäbe sich g = -0,50 statt
-0,51. Diese Inkonsistenz ist klein, aber sie ist ein gutes Beispiel
dafür, warum eine unabhängige Zweitannotation die N- und
Completer-Entscheidung prüfen muss.

### 3.2 Freeman 2017

Freeman ist die größte Studie: 1891 Personen in der Interventionsgruppe
und 1864 in der Kontrolle, post-treatment 733 bzw. 1142. Die ISI lag
unter der Intervention bei 9,23 (SD 5,18), in der Kontrolle bei 12,95
(SD 5,27). Das ergibt g = -0,712, einen deutlichen Vorteil.

Freeman hat mit 31,4 % das größte Gewicht. Wegen der hohen
Zwischenstudienheterogenität dominiert die große Stichprobe den Pool
aber nicht so stark, wie es ein Fixed-Effect-Modell tun würde.

Ein methodischer Punkt: Die ISI ist in der Primärarbeit ein
Sekundärendpunkt; der primäre Schlafwert ist die SCI-8. Die Review
verwendet die ISI. Das ist eine legitime, aber erklärungsbedürftige
Entscheidung. Eine unabhängige B-Annotation würde genau hier prüfen, ob
der Zielwert korrekt gewählt wurde.

### 3.3 Fucito 2017

Fucito ist die kleinste Studie: 21 Personen pro Arm, 19 Completer pro
Arm. Die PSQI-Werte in Woche 5 liegen bei 10,85 (SD 2,02) unter
„Call it a Night“ und 10,13 (SD 1,97) unter „Healthy Behaviors“. Der
SMD ist mit **+0,354** positiv: Die Kontrolle lag numerisch etwas
besser, der Unterschied ist aber nicht signifikant, das KI schließt null
ein.

Die Besonderheit: Die Arbeit berichtet den PSQI nur als
modellgeschätzten Mittelwert mit Standardfehler, nicht als rohen
Mittelwert mit SD. Die Review verwendet daraus SD = SE * sqrt(21) =
2,02 bzw. 1,97. Das ist rechnerisch nachvollziehbar, aber ein
Extrapolationsschritt. Eine zweite Annotation muss diesen Schritt
unabhängig prüfen.

Fucito ist kein Beleg dafür, dass dCBT-I schadet. Es ist eine kleine
Pilotstudie mit aktivem Kontrollprogramm, und der Effekt ist unsicher.
Aber Fucito zeigt, dass der gepoolte Effekt nicht in jeder Studie
positiv ausfällt.

### 3.4 de Bruin 2018

de Bruin hatte drei Arme: Internet-CBT-I (IT), Gruppen-CBT-I (GT) und
Warteliste (WL). Für die digitale Fragestellung ist der IT-Arm
maßgeblich: 2,86 (SD 0,71) gegen WL 3,74 (SD 0,62), g = -1,307. Das ist
der größte Effekt im Pool.

Der GT-Arm hat andere Werte: 3,01 (SD 0,59). Würde man GT statt IT
verwenden, ergäbe sich ein anderes Bild. Die Review verwendet IT gegen
WL; das ist für dCBT-I korrekt. Aber die Armauswahl ist eine der
Stellen, an denen eine unabhängige B-Annotation die Extraktion
absichern muss.

## 4. Was der gepoolte Wert bedeutet

### 4.1 Hedges g

Hedges g ist eine standardisierte Mittelwertdifferenz:

\[
g = \frac{\bar{x}_{dCBT-I} - \bar{x}_{Kontrolle}}{s_{gepoolt}}
\]

mit einer kleinen Korrektur für kleine Stichproben. Ein negativer Wert
bedeutet hier: Die Interventionsgruppe hat einen niedrigeren
Schlafscore, also eine bessere Schlafqualität. Das gilt für alle drei
Instrumente, weil höhere Werte jeweils schlechtere Werte bedeuten.

g = -0,58 heißt nicht „0,58 Punkte besser“ und auch nicht „58 %
besser“. Es heißt: Der Unterschied entspricht 0,58 gepoolten
Standardabweichungen. Als grobe Orientierung gelten 0,2 als klein,
0,5 als mittel und 0,8 als groß; die Review selbst stuft 0,56 bis 1,2
als großen Effekt ein. Der beobachtete Wert liegt damit im mittleren bis
großen Bereich.

### 4.2 Warum der Pool nicht einfach der Mittelwert der vier g ist

Die vier Studien haben unterschiedliche Präzision und unterschiedliche
Gewichte. Der Random-Effects-Pool gewichtet sie mit der inversen
Varianz plus der Zwischenstudienvarianz tau². Daraus folgen die
Gewichte:

- Freeman: 31,4 %
- Morris: 25,3 %
- de Bruin: 23,1 %
- Fucito: 20,2 %

Der Pool von -0,58 ist also eine gewichtete Mischung aus -0,51, -0,71,
+0,35 und -1,31. Besonders wichtig: Das positive Fucito-Ergebnis zieht
den Pool nach oben, also in Richtung null. Die negative de-Bruin-Studie
zieht ihn nach unten. Ohne Fucito ergibt die Sensitivitätsanalyse der
Review **g = -0,80** (95 %-KI -1,14 bis -0,45), k = 3, I² = 70 %.
Das zeigt, wie stark ein einzelner Gegenbefund den Gesamtwert
beeinflusst.

### 4.3 Hohe Heterogenität

I² = 84 % bedeutet: Ein großer Teil der beobachteten Unterschiede
zwischen den Studien ist nicht bloß Zufall der Stichproben, sondern
echte Variation zwischen den Studien. Dafür gibt es mehrere Gründe:

- unterschiedliche Populationen: Studierende mit Stress, Studierende mit
  Insomnie, Studierende mit Alkoholproblemen, Jugendliche mit Insomnie;
- unterschiedliche Interventionen: „Insomnia Relief“, „Sleepio“,
  „Call it a Night“, internetbasierte CBT-I mit Therapeutenkontakt;
- unterschiedliche Kontrollen: Warteliste, aktives
  Schlafhygiene-/Gesundheitsprogramm;
- unterschiedliche Instrumente: PSQI, ISI, HSDQi;
- unterschiedliche Zeitpunkte und Stichprobengrößen.

Die Review zeigt das auch in der Subgruppenanalyse: Bei primärer
Insomnie liegt der Effekt bei **-0,96** (95 %-KI -1,53 bis -0,38), bei
komorbider Insomnie bei **-0,11** (95 %-KI -0,95 bis +0,73). Der
Gesamtwert von -0,58 verdeckt diesen Unterschied. Er ist ein
Durchschnitt über sehr verschiedene Fälle, kein universeller
Behandlungseffekt.

### 4.4 Was der Wert nicht sagt

- Er sagt nichts über **objektive** Schlafparameter. Die Review findet
  für die Aktigraphie keine signifikanten Effekte: Schlafeffizienz
  g = 0,64 (95 %-KI -0,27 bis 1,55), Gesamtschlafzeit g = 0,34
  (95 %-KI -0,02 bis 0,70). Subjektive Verbesserung und objektive
  Messung fallen hier auseinander.
- Er sagt nichts über die **Langfristigkeit**. Der Follow-up-Wert der
  Review ist g = -0,68, aber das KI (-1,50 bis 0,13) schließt null ein.
- Er sagt nichts über **klinische Signifikanz** im Einzelfall. Ein
  mittlerer Effekt kann bedeuten, dass einige deutlich profitieren und
  andere nicht.
- Er sagt nichts über die **Qualität der Extraktion** in anderen
  Dokumenten. Genau hier setzt die B-Annotation an.

## 5. Reproduktion der Publikation

| Quelle | g | 95 %-KI | Q | tau² | I² |
|---|---:|---:|---:|---:|---:|
| Review (publiziert) | -0,58 | -1,03; -0,13 | 18,25 | 0,17 | 84,00 % |
| aus SMD und KI | -0,5849 | -1,0356; -0,1342 | 18,2133 | 0,1659 | 83,53 % |
| aus N, M und SD | -0,5842 | -1,0295; -0,1389 | 18,3788 | 0,1615 | 83,68 % |

Die kleinen Abweichungen bei Q, tau² und I² sind Rundungs- und
Implementierungsunterschiede. Review Manager berechnet die Varianz und
die Hedges-Korrektur etwas anders als das Prüfskript. Entscheidend ist:
**Punktschätzer und 95 %-KI liegen innerhalb der Toleranz.** Das
Prüfskript endet mit Exit 0.

## 6. Methodische Fallstricke

Die Reproduktion ist nur so gut wie die Entscheidungen, die in sie
eingehen. Die wichtigsten sind:

1. **Randomisierte N vs. Completer-N.** Die Review verwendet die
   randomisierten N, obwohl die Post-Werte bei Morris auf Completern
   beruhen. Das ist konsistent mit dem Forest Plot, aber methodisch
   angreifbar.
2. **Fucito-PSQI aus Modellschätzungen.** Die SD wurde aus dem
   Standardfehler und n = 21 hergeleitet. Das ist nachvollziehbar, aber
   kein roher Tabellenwert.
3. **de Bruin: IT vs. GT.** Die digitale Intervention ist IT; GT ist
   Gruppen-CBT-I. Die Armauswahl verändert den Effekt deutlich.
4. **Freeman: ISI als Sekundärendpunkt.** Die Review verwendet ISI, nicht
   die primäre SCI-8. Das ist eine Outcome-Entscheidung, keine reine
   Rechenentscheidung.
5. **Unterschiedliche Instrumente.** PSQI, ISI und HSDQi werden
   standardisiert gepoolt. Das ist üblich, aber inhaltlich nicht
   identisch.
6. **Kleines k und hohe Heterogenität.** Vier Studien sind zu wenig für
   belastbare Subgruppen- oder Meta-Regressionsanalysen; tau² ist
   entsprechend unsicher.

Diese Punkte sind nicht nur Fußnoten. Sie sind der Grund, warum eine
zweite, unabhängige Annotation nötig ist.

## 7. Warum die B-Ergebnisse notwendig sind

### 7.1 Was A und B sind

- **A** ist die erste Annotation: 69 Effektzeilen, 13 Begründungen ohne
  Zeile, 30 Dokumente, 0 offen. Sie wurde vom Assistenten erstellt.
- **B** ist die unabhängige Zweitannotation durch eine externe Person.
  Das B-Gerüst enthält 30 Dokumente, 0 Zeilen und 30 offene Dokumente;
  das Blind-Paket enthält 30 Volltexte und 30 Arbeitsblätter.
- B sieht nur Volltexte, Anleitung, Schema und das eigene Arbeitsblatt.
  A ist nicht Teil des Pakets und darf vor dem Einfrieren von B nicht
  geöffnet oder verglichen werden.

B ist keine zweite Metaanalyse und kein Modelllauf. B ist ein
Annotationstext mit Effektzeilen oder Begründungen, den ein Mensch
unabhängig erstellt.

### 7.2 Vier Funktionen von B

1. **Inter-Rater-Reliabilität.** A und B werden zeilen- und
   dokumentweise verglichen. Cohen's Kappa misst die Übereinstimmung
   über den Zufall hinaus. Die Projektvorgabe ist eine Schwelle von
   0,80. Ohne B gibt es keine Kappa-Zahl.
2. **Konflikterkennung.** Wo A und B unterschiedliche Zeilen,
   Zeitpunkte, Arme oder Begründungen wählen, wird sichtbar, ob die
   Anleitung eindeutig ist. Konflikte gehen an eine dritte Stimme; sie
   werden nicht stillschweigend geglättet.
3. **Unabhängiger Maßstab für die Pipeline.** Die Pipeline soll später
   gegen einen Goldstandard geprüft werden. Wenn nur A existiert, ist
   dieser Maßstab selbst vom Assistenten erstellt. Die Pipeline könnte
   dieselben blinden Flecken haben wie A. B bricht diese Zirkularität.
4. **Qualitätssicherung der Regeln.** B zeigt, ob das Schema und die
   Anleitung wirklich ausreichen. Wenn zwei unabhängige Personen bei
   denselben Dokumenten systematisch unterschiedlich entscheiden, ist
   nicht die Pipeline das Problem, sondern die Aufgabe.

### 7.3 Konkrete Stellen, an denen B prüft

| Fall | A-Entscheidung | Was B unabhängig prüfen muss |
|---|---|---|
| Morris 2015 | Randomisierte N 48/47, Post-Werte von Completern | N- oder Completer-N? Welche Tabelle ist maßgeblich? |
| Freeman 2017 | ISI, Woche 10 | ISI oder SCI-8? Sekundärendpunkt zulässig? |
| Fucito 2017 | PSQI, Woche 5, SD aus SE | Ist „Subjective Sleep Ratings“ der PSQI? Ist die SE-Umrechnung zulässig? |
| de Bruin 2018 | IT gegen WL | IT, GT oder beide Arme? Welcher Arm ist „digital“? |
| Aggregate/Reviews | Zeilen oder Begründung | Gepoolter Schätzer als eigene Zeile? Einzelstudien nicht übernehmen? |

Das sind genau die Stellen, an denen eine einzelne Annotation
selbstsicher danebenliegen kann. B macht die Entscheidung sichtbar und
prüfbar.

### 7.4 Was ohne B fehlt

Ohne B fehlen:

- keine Kappa-Zahl und damit kein Nachweis, dass die Annotation
  reproduzierbar ist;
- keine unabhängige Kontrolle, ob A Zeilen ausgelassen, doppelt
  aufgenommen oder falsch zugeordnet hat;
- keine belastbare Grundlage für die Pipeline-Evaluation, weil der
  Maßstab nur aus A besteht;
- keine Möglichkeit, Konflikte einer dritten Stimme vorzulegen;
- keine Entscheidung darüber, ob die Anleitung nachgeschärft werden
  muss, bevor die Pipeline bewertet wird.

Der dCBT-I-Nachbau zeigt, dass **eine** Rechnung aus **vier** Studien
reproduzierbar ist. Er zeigt nicht, dass die Extraktionsregeln auf 30
heterogene Dokumente übertragbar sind. Das ist der Unterschied zwischen
„die Zahl stimmt“ und „die Messung ist valide“.

### 7.5 Warum B vor dem Öffnen von A eingefroren werden muss

Die Unabhängigkeit von B ist nur gegeben, wenn B A nicht kennt. Würde A
vorher geöffnet oder verglichen, könnte B durch A beeinflusst werden.
Die Übereinstimmung wäre dann künstlich hoch, und die Kappa-Auswertung
würde die tatsächliche Reliabilität überschätzen. Deshalb gilt:

1. B vollständig annotieren.
2. B gegen das Gerüst und das Schema prüfen.
3. B-Hash einfrieren.
4. Erst danach A öffnen und Kappa/Konflikte berechnen.

Der Paket-Hash `2f9db202...` bestätigt nur die Unversehrtheit des
versandten Blind-Pakets. Er ist **nicht** der B-Abgabe-Hash. Der
B-Abgabe-Hash entsteht erst aus der fertigen B-JSON.

## 8. Aktueller Status

- Der dCBT-I-Nachbau ist abgeschlossen und geprüft.
- Der B-Rücklauf fehlt weiterhin.
- Ein B-Abgabe-Hash ist nicht eingefroren.
- Der B-Watcher läuft und würde bei Eingang nur den Trockenlauf
  ausführen; er friert nicht automatisch ein.
- A wurde nicht geöffnet und nicht mit B verglichen.

## 9. Fazit

Der Nachbau sagt: **Die publizierte Zahl ist aus den vier
Primärstudien nachvollziehbar.** Der Effekt ist mittel bis groß, aber
wegen I² = 84 %, k = 4 und des Gegenbefunds bei Fucito nicht als
einheitlicher oder robuster Effekt zu lesen.

Die B-Ergebnisse sagen etwas anderes: **Ob die Annotation selbst
zuverlässig ist.** Beides ist nötig. Ohne den Nachbau wüsste man nicht,
ob die Pipeline eine bekannte Zahl reproduzieren kann. Ohne B wüsste man
nicht, ob die Extraktionsregeln unabhängig vom Assistenten funktionieren.
Der größte Hebel ist deshalb nicht eine weitere Rechnung, sondern der
eingefrorene B-Hash vor dem Öffnen von A.
