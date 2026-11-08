# Validierung der gepoolten SOL-Schaetzung (k = 3)

Stand: 2026-11-08. Grundlage: `pooling_sol3_20261108.json`,
`pruefung_kandidaten_20261108.md`, die drei PMC-XML und der HTA-Bericht.
Alle Zahlen sind aus diesen Quellen oder aus dem JSON nachgerechnet.

## Antwort auf die Leitfrage

**Kann man dem Ergebnis von -26,29 Minuten vertrauen?**

Als **Richtungsaussage mit grober Groessenordnung: ja**. In allen drei
Studien senkt Melatonin die Einschaflatenz, in keiner Sensitivitaet dreht
sich das Vorzeichen, und der Punktschaetzer liegt in jedem
Leave-one-out-Szenario zwischen -20,8 und -34,6 min.

Als **Praezisionsaussage: nein**. Das 95%-CI reicht von -55,6 bis +3,0 min,
p = 0,061, und tau^2 = 104,5 min^2 entspricht einer Standardabweichung
zwischen den Studien von rund 10 min - fast so gross wie der Effekt selbst.
Die drei Studien untersuchen ausserdem Populationen, die sich nicht
ueberschneiden (Kinder mit Entwicklungsstoerung, 65-80-jaehrige Erwachsene,
Kinder mit chronischer Einschlafinsomnia).

**Was fehlt:** mindestens zwei bis drei weitere unabhaengige, methodisch
vergleichbare Studien (k >= 5), damit Subgruppen und eine belastbare
Heterogenitaetsaussage moeglich werden. Der Weg dorthin ist die Fernleihe
der 83 nicht beschafften Dokumente, nicht eine weitere Modellvariante.

---

## Aufgabe 1: Klinische und methodische Vergleichbarkeit

### Vergleichstabelle

| Merkmal | PMC3489506 (MENDS, Gringras 2012) | PMC2933606 (Wade 2010) | PMC2952772 (van Geijlswijk 2010) |
|---|---|---|---|
| Design | randomisiert, doppelblind, placebokontrolliert, 19 Kliniken | randomisiert, doppelblind, placebokontrolliert, multizentrisch | randomisiert, doppelblind, placebokontrolliert, Dosisfindung |
| Population | 146 Kinder von 3 Jahren bis 15 Jahren 8 Monaten | 791 Erwachsene 18-80; hier die praedefinierte Subgruppe 65-80 (137/144) | 72 Kinder 6-12 Jahre |
| Diagnose | neurologische und Entwicklungsstoerungen mit schwerem Schlafproblem (Einschlafen > 1 h oder < 6 h Durchschlaf) | primaere Insomnia nach DSM-IV, SOL > 20 min | chronische Einschlafinsomnia (CSOI), SOL > 30 min, Schlafonset spaeter als 20:30 bis 22:00 je Alter |
| Praeparat | Melatonin mit sofortiger Freisetzung, Kapsel | Prolonged-release Melatonin (Circadin) | Melatonin, Tablette |
| Dosierung | 0,5 mg Start, titriert auf 2, 6, 12 mg nach Ansprechen | 2 mg fix | 0,05 mg/kg (Arme 0,1 und 0,15 mg/kg) |
| Einnahme | 45 min vor der Schlafenszeit | 2 h vor der Schlafenszeit | 17:30-19:30, 1-2 h vor DLMO |
| Dauer | 12 Wochen | 3 Wochen | 1 Woche |
| Messmethode | Schlaftagebuch der Eltern + Aktigraphie | Schlaftagebuch | Schlaf-Log der Eltern + Aktigraphie |
| Messzeitpunkt | Baseline und Woche 12 | Baseline und Woche 3 | Baseline-Woche und Behandlungswoche |
| Endpunktstatus | SOL nach Amendment sekundaer (urspruenglich primaer) | praedefinierter sekundaerer Endpunkt in einer Subgruppe | primaerer Endpunkt |
| Effekt (adjustiert) | -37,5 min (-55,3 bis -19,7) | -15,6 min (-25,3 bis -6,0), p = 0,002 | -31 min (SE 10; berichtetes CI 9 bis 54) |
| n in der Analyse | 54 Melatonin / 59 Placebo | 137 / 144 | 16 / 17 |

### Was gleich ist

1. **Endpunkt**: Einschaflatenz in Minuten als Change vom Baseline-Wert.
2. **Design**: randomisiert, doppelblind, placebokontrolliert.
3. **Schaetzung**: alle drei Effekte sind baseline-adjustierte Differenzen
   (ANCOVA bzw. lineares Regressionsmodell mit Baseline als Kovariate).
4. **Richtung**: alle drei zeigen eine Verkuerzung.

### Was sich unterscheidet

1. **Alter**: 3-15,8 Jahre / 65-80 Jahre / 6-12 Jahre. Die Populationen
   ueberschneiden sich nicht; eine gemeinsame Referenzpopulation existiert
   nicht.
2. **Diagnose**: breite neurodevelopmental disorders vs. primaere Insomnia
   bei aelteren Erwachsenen vs. umschriebene CSOI bei gesunden Kindern.
3. **Praeparat und Dosis**: 0,05 mg/kg (bei 30 kg rund 1,5 mg) vs. 2 mg
   prolonged release vs. Titration bis 12 mg. Das sind teils mehr als
   sechsfache Dosisunterschiede und unterschiedliche Freisetzungskinetic.
4. **Dauer**: 1 Woche vs. 3 Wochen vs. 12 Wochen. Kurze Studien messen
   eher den Akuteffekt, lange Studien enthalten Gewoehnung oder
   Verhaltensaenderungen.
5. **Messmethode**: Tagebuch (Eltern) vs. Tagebuch (Erwachsene) vs.
   Log + Aktigraphie. Tagebuch und Aktigraphie messen systematisch
   verschiedene Dinge; bei MENDS differieren die beiden Methoden um 7,8 min
   (-37,5 vs. -45,3).
6. **Endpunktstatus**: primaer / praedefiniert-sekundaer / nach Amendment
   sekundaer. Die MENDS-Zahl ist eine sekundaere Analyse, was die
   Verzerrungsanfaelligkeit erhoeht.

### Ist die gemeinsame Schaetzung wissenschaftlich sinnvoll interpretierbar?

**Eingeschraenkt ja - als beschreibende Zusammenfassung, nicht als
Schaetzung eines gemeinsamen Effekts.**

Dafuer spricht: Der Endpunkt ist in allen drei Studien derselbe
(minutengenaue SOL als Change), alle drei sind placebokontrolliert und
baseline-adjustiert, und die Richtung ist einheitlich. Ein gewichteter
Mittelwert beantwortet dann die Frage "Wie gross ist die Verkuerzung im
Durchschnitt dieser drei Kontexte?" - und das ist eine legitime, wenn auch
grobe Aussage.

Dagegen spricht: Mit tau^2 = 104,5 min^2 ist die Zwischenstudienvarianz
etwa so gross wie der Effekt. Ein Random-Effects-Modell unterstellt, dass
die drei Effekte Realisierungen einer gemeinsamen Verteilung um einen
wahren Mittelwert sind. Diese Annahme ist hier nicht pruefbar (k = 3) und
inhaltlich fragwuerdig: Es gibt keinen Grund anzunehmen, dass eine
80-Jaehrige mit primaerer Insomnia und ein 8-jaehriges Kind mit
Entwicklungsstoerung denselben wahren Effekt haben. Der Wert -26,29 min
gilt fuer **keine** der drei Populationen einzeln; er ist ein Artefakt der
Gewichtung.

**Praktische Konsequenz:** In einem Bericht sollte nicht "Melatonin senkt
die Einschaflatenz um 26 min" stehen, sondern "in drei Studien mit sehr
verschiedenen Populationen lag die Verkuerzung zwischen 16 und 38 min; der
gepoolte Punktschaetzer von 26 min ist mit erheblicher Unsicherheit behaftet
(95%-CI -55,6 bis +3,0)".

---

## Aufgabe 2: Leave-one-out-Analyse

### Ergebnisse

| Ausgeschlossene Studie | k | Effekt (min) | 95%-CI | p | tau^2 | I^2 |
|---|---:|---:|---|---:|---:|---:|
| keine (Hauptanalyse) | 3 | -26,29 | -55,57 bis 3,00 | 0,061 | 104,5 | 63,0 |
| PMC3489506 (MENDS) | 2 | -20,84 | -113,55 bis 71,87 | 0,214 | 56,5 | 47,6 |
| PMC2933606 (Wade) | 2 | -34,56 | -75,67 bis 6,54 | 0,059 | 0,0 | 0,0 |
| PMC2952772 (van Geijlswijk) | 2 | -25,22 | -163,32 bis 112,88 | 0,259 | 186,4 | 77,7 |

p-Werte aus t = Effekt / SE(HKSJ) mit df = k - 1 (df = 1 bei k = 2),
zweiseitig; scipy 1.15.2, t-Verteilung.

### Beurteilung: dominiert eine Studie?

**Nein im statistischen Sinn, ja im inhaltlichen Sinn - und zwar PMC2933606.**

- **Gewicht**: PMC2933606 traegt 43,1 % des Gewichts, die anderen beiden
  29,7 % und 27,2 %. Das ist eine Mehrheit, aber keine Dominanz; keine
  Studie hat mehr als die Haelfte.
- **Einfluss auf den Punktschaetzer**: Ohne PMC2933606 steigt der Effekt
  von -26,3 auf -34,6 min, also um 8,3 min. Ohne PMC3489506 faellt er auf
  -20,8, ohne PMC2952772 auf -25,2. PMC2933606 ist damit der groesste
  einzelne Einfluss - weil sie den kleinsten Effekt mit der kleinsten
  Streuung verbindet.
- **Richtung**: In keinem Szenario dreht das Vorzeichen. Die Spanne
  -20,8 bis -34,6 min ist die belastbarste Aussage dieser Analyse.
- **Signifikanz**: Kein Leave-one-out-Szenario ist signifikant
  (p = 0,059 bis 0,259). Bei df = 1 sind die Intervalle ohnehin extrem
  breit; das ist ein Artefakt von k = 2, kein inhaltlicher Befund.
- **tau^2 = 0 ohne PMC2933606**: Das ist kein Hinweis auf Homogenitaet,
  sondern die Folge davon, dass mit zwei Beobachtungen und aehnlichen
  Effekten (-37,5 und -31) die DL-Schaetzung null ergibt. I^2 = 0 bei
  k = 2 ist nicht interpretierbar.

**Fazit:** Keine einzelne Studie bestimmt das Ergebnis allein. Aber die
Wahl der Wade-Subgruppe (65-80 statt Low excretors) daempft den Effekt um
rund 8 min - das ist der groesste Hebel innerhalb der Daten, und er ist
eine Auswahlentscheidung, keine Beobachtung.

---

## Aufgabe 3: SE-Diskrepanz bei PMC2952772

### Die beiden Angaben

Die Quelle (Tabelle 2) berichtet fuer 0,05 mg/kg:

| Angabe | Wert |
|---|---|
| Differenz zu Placebo | 31 min (Konvention der Studie: positiv = Vorverlegung) |
| Standard error | 10 min |
| 95%-CI | 9 bis 54 min |
| df | 29,6 |
| p | 0,007 |

Aus dem CI folgt: SE = (54 - 9) / 2 / t(0,975; 29,6) = 22,5 / 2,045 =
**11,00 min**. Mit SE 10 und t = 2,045 waere das CI 10,6 bis 51,4, also
11 bis 51 - nicht 9 bis 54. Mit SE 11,0 ergibt sich 8,5 bis 53,5, gerundet
9 bis 54. **Das CI ist mit SE 11,0 konsistent, mit SE 10 nicht.**

### Sensitivitaet S10

| Analyse | k | Effekt | 95%-CI | p | tau^2 | I^2 |
|---|---:|---:|---|---:|---:|---:|
| Hauptanalyse (SE 10) | 3 | -26,29 | -55,57 bis 3,00 | 0,0610 | 104,5 | 63,0 |
| S10 (SE 11,0) | 3 | -26,20 | -55,75 bis 3,36 | 0,0624 | 107,1 | 62,1 |

Differenz: 0,09 min im Punktschaetzer, 0,18 min in der oberen
CI-Grenze, p verschiebt sich um 0,0014. Das Gewicht der Studie sinkt von
27,2 auf 25,4 %.

### Welche Angabe ist maßgeblich?

**Fuer die Hauptanalyse bleibt der berichtete SE 10 massgeblich** - mit
einer Einschraenkung:

- Der berichtete SE ist die explizite Angabe der Autoren; ihn durch eine
  eigene Ableitung zu ersetzen, hiesse, die Quelle zu ueberschreiben.
- Die Diskrepanz ist numerisch irrelevant: 0,09 min bei einem Effekt von
  26 min und einem CI von 58 min Breite. Keine Schlussfolgerung aendert
  sich.
- Wenn man sich zwischen zwei unvereinbaren Angaben entscheiden muss, ist
  die CI-basierte 11,0 die **konservativere** (groesseres SE, kleineres
  Gewicht) und die besser belegte (das CI steht mit zwei Dezimalstellen in
  der Tabelle, der SE nur mit einer).
- Fuer eine Publikation sollten beide Werte offengelegt werden, nicht
  stillschweigend einer gewaehlt.

**Empfehlung:** Hauptanalyse mit SE 10 belassen (Autorenangabe), S10 als
dokumentierte Sensitivitaet fuehren, Diskrepanz im Methodenteil nennen.
Das ist die einzige Variante, die weder die Quelle verfaelscht noch die
Unsicherheit versteckt.

---

## Aufgabe 4: Methodische Gesamtbewertung

### Drei Unsicherheitsquellen, getrennt betrachtet

**1. Statistische Unsicherheit (im Modell abgebildet)**

- 95%-CI -55,6 bis +3,0 min, p = 0,061: Die Null ist nicht ausschliessbar.
- tau^2 = 104,5 min^2, I^2 = 63 %: erhebliche Zwischenstudienvarianz.
- df = 2 beim HKSJ-Intervall: Die t-Kritische Schranke ist 4,303 statt
  1,96 - das Intervall ist deshalb mehr als doppelt so breit wie ein
  naives. Das ist korrekt, nicht uebertrieben.
- Das Prediction Interval (-187 bis 134) ist bei df = 1 unbrauchbar und
  wird nicht interpretiert.

**2. Klinische Heterogenitaet (nicht im Modell abgebildet)**

Das Modell behandelt die drei Effekte als austauschbar. Inhaltlich sind
sie es nicht: unterschiedliche Altersgruppen, Diagnosen, Praeparate,
Dosierungen, Behandlungsdauern und Messmethoden. I^2 = 63 % misst die
Streuung, aber nicht ihre Ursache. Bei k = 3 laesst sich nicht trennen,
wie viel davon Population, Dosis oder Methode zukommt. Die
Sensitivitaeten S1-S4 zeigen: Allein der Wechsel der Messmethode oder der
Dosierung verschiebt den Effekt um 2 bis 12 min.

**3. Verzerrung durch unvollstaendige Beschaffung**

- 83 Dokumente aus der Suche waren nicht beschaffbar (77 ohne freien
  Volltext, 14 Verlags-403, 0 lokal vorhanden).
- Unbekannt ist, wie viele davon poolbar waeren. Bei einer
  Screeningsquote von 3 von 31 XML (rund 10 %) waeren es etwa 8 von 83 -
  das waere genug, um k zu verdoppeln.
- Die Richtung der Verzerrung ist offen: Fehlende Studien koennen kleinere
  oder groessere Effekte haben. Bei k = 3 ist weder ein Funnel-Plot noch
  ein Egger-Test sinnvoll; eine Aussage ueber Publikationsbias ist nicht
  moeglich.
- Das ist keine "fehlende Information", sondern ein systematisches
  Risiko: Der Punktschaetzer ist nur fuer die beschaffbaren Studien
  gueltig.

### Nachtrag: der Tabellenleser erreicht S1 nicht

Das ist keine Rechenunsicherheit, sondern eine Eigenschaft der
Datenaufnahme - hier festgehalten, damit sie nicht als stiller Fehler
weiterlaeuft.

- **Befund.** In `volltext/23098680.txt` (MENDS) werden 48
  Tabellenbloecke erkannt. Kein einziger Kopf enthaelt Effektwort und KI
  (47-mal beides nicht, 1-mal KI ohne Effektwort); die Koepfe sind
  Fragmente von Baseline-, Labor- und Missing-Data-Tabellen. Die
  SOL-Zeile in Block 6 lautet
  `SOL (minutes) | -3.71 (47.37) | (p=0.007) | (p<0.0001)` - das ist der
  Placebo-Change-Wert aus HTA-Tabelle 7, kein Effekt mit Intervall.
- **Wo der Effekt steht.** Als Satz im Fliesstext: "the mean difference
  ... was -37.49 minutes (95% CI -55.27 to -19.71 minutes)" fuer das
  Schlaftagebuch und "-45.34 minutes (95% CI -68.75 to -21.93 minutes)"
  fuer die Aktigraphie, beide adjustiert fuer die Baseline.
- **Folge.** `effects_from_row` arbeitet ausschliesslich auf Zeilen
  erkannter Bloecke; ein Satz ist kein Block. S1 wird von der Automatik
  also nicht gelesen, obwohl die Zahl im Volltext steht. Die Extraktion
  stuetzt sich deshalb auf HTA-Tabelle 7, wo dieselbe adjustierte
  Differenz von -37,49 (SE 9,08) berichtet wird
  (`mends_hta_zusatz_20261108.md`).
- **Nicht betroffen.** Der gepoolte Wert -26,29 min beruht nicht auf
  einer automatisch gelesenen Zeile, sondern auf der dokumentierten
  Tabellenextraktion. Der Volltextsatz bestaetigt ihn nachtraeglich; die
  Zahl ist belegt, nicht geschaetzt.
- **Grenze fuer die Erweiterung.** Ein Fliesstext-Leser wuerde aus
  demselben Satz zwei Effekte liefern (Tagebuch und Aktigraphie). Ohne
  Duplikatpruefung entstuende daraus eine Doppelzaehlung von S1, die die
  Schaetzung still verzerrt. Deshalb bleibt es bei der dokumentierten
  Einzelextraktion je Design statt bei einer automatischen Satzsuche.

Beleg: `gegencheck/mends_kopf_20261108.md` (Blockstatistik, SOL-Zeilen,
beide Satzfunde). Read-only erhoben, kein Netz, kein Modell.

### Welche Schluesse sind bei k = 3 zulaessig?

**Zulaessig:**

1. In allen drei eingeschlossenen Studien senkt Melatonin die
   Einschaflatenz; die Richtung ist konsistent.
2. Die Einzeleffekte liegen zwischen -15,6 und -37,5 min; der gepoolte
   Punktschaetzer betraegt -26,3 min.
3. Die Unsicherheit ist gross: Das 95%-CI schliesst die Null ein
   (p = 0,061).
4. Die Studien sind klinisch heterogen; eine gemeinsame Referenzpopulation
   existiert nicht.
5. Keine Aussage ueber Dosis, Alter, Behandlungsdauer oder
   Publikationsbias.

**Nicht zulaessig:**

1. "Melatonin verkuerzt die Einschaflatenz um 26 min" als gesicherte
   Aussage.
2. Subgruppenvergleiche (Kinder vs. Erwachsene) - jede Subgruppe waere
   eine einzelne Studie.
3. Dosis-Wirkungs-Aussagen aus dem Vergleich 0,05 vs. 0,15 mg/kg - das
   ist eine Sensitivitaet an einer Studie, keine Dosisanalyse.
4. I^2 = 63 % als "moderate Heterogenitaet" im Sinne der GRADE-Lesart -
   bei k = 3 ist das eine Zahl ohne Konfidenz.
5. Jede Aussage ueber Publikationsbias.

### Gesamturteil

Die Metaanalyse ist **methodisch korrekt gerechnet, aber inhaltlich noch
nicht belastbar**. Die Rechnung (Random Effects, DL, HKSJ) ist die
richtige Wahl fuer k = 3 mit Heterogenitaet; die Datenbasis traegt aber
keine praezise Effektschaetzung. Der Wert -26,29 min ist ein Zwischenstand,
kein Ergebnis.

---

## Aufgabe 5: Vorbereitung der Fernleihe

Es werden **keine neuen Skripte** gebaut. Es existiert bereits
`bestellanfrage_fernleihe_20261108.md/.txt` (5 priorisierte Titel,
Fassung A als Feldliste, Fassung B als Freitext) sowie
`zugangsliste_20261108.csv` (83 Zeilen, 80 mit DOI).

### Bestellliste nach Prioritaet

| Prioritaet | Anzahl | Inhalt | Bestellstatus |
|---|---:|---|---|
| A | 5 | direkte SOL-RCTs bei Kindern/Erwachsenen | in `bestellanfrage_fernleihe_20261108` erfasst |
| B | 20 | wahrscheinlich poolbar, Pruefung offen | Nachbestellung nach A |
| C | 39 | moeglicherweise poolbar, schlechtere Datenlage | Nachbestellung nach B |
| D | 19 | vermutlich nicht poolbar | zurueckgestellt |

Die 5 A-Titel mit DOI:
10.1111/jpc.70224, 10.1016/j.sleep.2020.10.018, 10.1093/sleep/zsw038,
10.1097/01.chi.0000085756.71002.86, 10.1177/088307380101600204.

### Was in der Bestellung stehen muss

1. DOI und PMID (aus der CSV), damit die Bibliothek nicht suchen muss.
2. Der Hinweis "PDF mit Textebene" - ein Scan ohne Textebene ist fuer die
   Extraktion nicht verwendbar.
3. Keine Angabe von Befunden oder Ergebnissen, nur die bibliografischen
   Daten.

### Was nach Eingang passiert (festgelegt, nicht neu zu bauen)

1. Screening nach dem dokumentierten Protokoll (20 von 31 XML).
2. Doppelpublikationspruefung gegen `dedup_register_20261108.md`.
3. Extraktion nach der Auswahlregel in `auswahlregel_pooling_20261108.md`.
4. Erneutes Pooling erst ab k >= 4; Subgruppen erst ab k >= 5.

---

## Zusammenfassung in fuenf Saetzen

1. Die drei Studien messen denselben Endpunkt, aber in nicht
   ueberschneidenden Populationen mit verschiedenen Praeparaten, Dosen,
   Dauern und Messmethoden.
2. Die gemeinsame Schaetzung von -26,29 min ist als Richtungsaussage
   brauchbar, als Punktschaetzung nicht.
3. Keine einzelne Studie dominiert das Ergebnis; die Wade-Subgruppe
   daempft es um 8 min, das ist die groesste Einzelentscheidung.
4. Die SE-Diskrepanz bei PMC2952772 ist numerisch irrelevant (S10: -26,20),
   sollte aber offengelegt werden.
5. Was fehlt, sind nicht mehr Modellvarianten, sondern mehr unabhaengige
   Studien - erreichbar ueber die Fernleihe der 83 Dokumente.
