# Arbeitsauftrag abgearbeitet: vier Kandidaten, Crossover, Screening, Endpunkt

Stand: 2026-11-08. Grundlage: `Arbeitsauftrag_Coding_Agent_Metaanalyse_2026-11-08.pdf`.
Geprüft an den Original-XML unter `data/bench/sol2/xml/`, ohne neuen Parser, ohne
Simulation, ohne Netzzugang.

## Ergebnis in einem Satz

**k steigt von 1 auf 3.** Zwei der vier offenen Kandidaten tragen poolbare
Minuten-Effekte (PMC2933606, PMC2952772), zwei nicht (PMC5774131, PMC10131443).
Von den vier Crossover-Studien ist keine für die Hauptanalyse geeignet, zwei
kommen für eine Sensitivitätsanalyse in Frage. Die Screening-Differenz ist bis
auf einen Rest aufgelöst: 31 - 20 = 11 Ausschlüsse, alle nach einer
dokumentierten Regel; die alte Zahl 14 stammt aus einer nicht dokumentierten
manuellen Sichtung und ist nicht rekonstruierbar.

---

# Aufgabe A - vier Kandidaten

## A1 PMC2933606 - poolbar

Studie: Nachtbehandlung mit prolongiertem Melatonin (PRM) vs. Placebo,
3 Wochen, Erwachsene mit primärer Insomnie; Tabelle 3 ist die primäre
Wirksamkeitstabelle.

| Population | N PRM / Placebo | Baseline SOL, min | 3 Wochen SOL, min | Change (SD) | Differenz (95 % CI) | p |
|---|---|---|---|---|---|---|
| Low excretors | 86 / 86 | 74,1 (54,9) / 75,5 (58,5) | 65,1 (59,9) / 66,5 (51,6) | −9,0 (50,5) / −9,0 (48,7) | −0,6 (−14,0 bis 12,7) | 0,924 |
| 65–80 Jahre | 137 / 144 | 76,7 (63,7) / 72,5 (51,4) | 57,6 (51,8) / 70,9 (54,0) | −19,1 (47,3) / −1,7 (47,8) | **−15,6 (−25,3 bis −6,0)** | 0,002 |

Zitat (Tabelle 3): „Change from baseline: mean (SD) | -9.0 (50.5) | -9.0 (48.7)
| -0.6 (-14.0, 12.7) | 0.924" und „-19.1 (47.3) | -1.7 (47.8) | -15.6 (-25.3,
-6.0), | 0.002". Text: „a significant difference in favour of PRM was found
for patients aged 65-80 years (-15.6 min; 95% CI -25.3 to -6.0, P = 0.002)".

**Urteil: poolbar.** Einheit Minuten, zwei Arme, N je Arm, Streuung als SD der
Veränderung, Zeitpunkt 3 Wochen. SE aus dem CI: (25,3 − 6,0) / 3,92 = **4,9 min**.
Gegenprüfung unadjustiert aus den Change-SDs: −17,4 min, SE = 5,7 - konsistent.

**Offene Entscheidung:** Die Studie berichtet zwei Populationen. Die Auswahl
ist nachträglich (beide Ergebnisse sind bekannt), deshalb Hauptanalyse mit einer
Population, Sensitivitätsanalyse mit der anderen. Die 65–80-Population ist
größer (281 vs. 172) und die einzige mit signifikantem Effekt - eine Auswahl
nach Signifikanz wäre Bias und ist hier ausdrücklich als solche markiert.

## A2 PMC2952772 - poolbar

Studie: Dosisfindung, Kinder 6–12 Jahre mit chronischer Einschaflatenz-
Insomnie, 1 Woche, vier Gruppen (Placebo n = 17; 0,05 mg/kg n = 16;
0,1 mg/kg n = 19; 0,15 mg/kg n = 18).

| Dosis | SOL-Differenz vs. Placebo | SE | 95 % CI |
|---|---:|---:|---|
| 0,05 mg/kg | 31 min | 10 | 9 bis 54 |
| 0,1 mg/kg | 36 min | 10 | 15 bis 57 |
| 0,15 mg/kg | 42 min | 9 | 22 bis 62 |

Zitat (Tabelle 2): „SOL shift | 0:42 | 0:09 | 0:22 | 1:02 | 31.5 | <0.001".
Text: „SOL was reduced by 12 min in the placebo group and by 43–54 min in the
melatonin treatment groups"; „The difference between placebo treatment and
melatonin treatment for SOL shift was 31–42 min".

**Urteil: poolbar.** Einheit Minuten, Differenz gegen Placebo, SE berichtet,
N je Arm bekannt. Keine Arm-Mittelwerte, aber die Differenz mit SE ist für eine
MD-Metaanalyse ausreichend.

**Offene Entscheidung:** drei Dosen gegen dasselbe Placebo - **eine** Zeile
wählen, sonst Mehrfachzählung. Die Autoren empfehlen 0,05 mg/kg; die höchste
Dosis zeigt den größten Effekt. Auswahl nachträglich, Sensitivitätsanalyse mit
allen drei Dosen.

## A3 PMC5774131 - nicht poolbar

Studie: Melatonin vs. Placebo nach Schädel-Hirn-Trauma, 4 Wochen, Crossover,
Actigraphie; SOL ist primärer Endpunkt.

Zitat: „Sleep latency, minimum b | 31 | 1.37 (1.26 to 1.48) | 1.42 (1.31 to
1.53) | -0.05 (-0.14 to 0.03) | 0.18 | 0.23". Text: „placebo 1.42, log units;
difference -0.05; 95% CI, -0.14 to 0.03; p = 0.23".

**Urteil: nicht poolbar.** Die Werte sind logarithmierte Actigraphie-Werte
(„log units"), keine Minuten. Eine Rücktransformation wäre möglich, aber sie
setzt die Verteilung und den Bezugspunkt voraus - beides nicht berichtet. Eine
Umrechnung in Minuten wäre eine Annahme, keine Messung. Als Ratio-Effekt
(exp(−0,05) ≈ 0,95) nicht kompatibel mit den Minuten-Studien.

## A4 PMC10131443 - nicht poolbar

Studie: Melatonin vs. Placebo bei Reizdarm, 8 Wochen, 34 je Arm.

Zitat (Tabelle 3): „Sleep Latency | Melatonin | < 15 min | 0 (0%) | 12 (35.3%) |
13 (38.2%) | 15 (44.1%)".

**Urteil: nicht poolbar.** SOL liegt nur als Kategorien vor (< 15, 16–30,
31–60, > 60 min). Kein Mittelwert, keine Streuung, auch nicht im Text. Aus
Kategorieanteilen lässt sich kein Gruppenmittelwert ohne Annahme über die
Verteilung rekonstruieren.

## Zwischenstand A

| Studie | Design | Population | Endpunkt | Urteil | k-Beitrag |
|---|---|---|---|---|---|
| PMC3489506 | parallel, RCT | Kinder, Entwicklungsstörung | SOL Tagebuch/Aktigraphie | poolbar (2 Zeilen, 1 Studie) | 1 |
| PMC2933606 | parallel, RCT | Erwachsene, primäre Insomnie | SOL Tagebuch | **poolbar** | +1 |
| PMC2952772 | parallel, RCT, Dosisfindung | Kinder, CSOI | SOL Schlafprotokoll | **poolbar** | +1 |
| PMC5774131 | crossover | Erwachsene nach SHT | SOL Actigraphie (log) | nicht poolbar | 0 |
| PMC10131443 | parallel, RCT | Erwachsene, Reizdarm | SOL kategorial | nicht poolbar | 0 |

**k vorher 1 → nachher 3.**

---

# Aufgabe B - Crossover-Studien

| Studie | Design | n | Washout | SOL-Daten | Within-Korrelation | Urteil |
|---|---|---:|---|---|---|---|
| PMC12903794 | randomisiert, crossover, non-inferiority | 33 | nicht berichtet | Mittelwerte 8,30 (SD 6,42) vs. 10,14 (SD 8,07) | nicht berichtet | **nicht kompatibel**: Vergleich Melatonin vs. partieller Schlafentzug, kein Placebo |
| PMC4425994 | crossover, doppelblind | 11 | 1 Woche | Placebo 19,0 (20,1), Melatonin 7,8 (5,9), Differenz 11,4 (9,4), p = 0,02 | nicht berichtet | **bedingt**: signifikanter Carryover, Auswertung nur Phase 1 |
| PMC4365553 | crossover Teil 1, danach 4 parallele Gruppen | 40 (10 je Gruppe in Teil 2) | 3 Tage zwischen den Nächten | NL 71,4 (25,6), NLP 61,3 (20,6), NLEE 46,6 (21,6), NLM 33,7 (10,5) | nicht berichtet | **bedingt**: Teil 2 ist parallel, gesunde Probanden |
| PMC11103136 | crossover | 64 | ≥ 1 Tag | Placebo 28,06 (27,46), Melatonin 21,02 (17,45), p = 0,037 | nicht berichtet | **bedingt**: gesunde Freiwillige, SOL als Nebenbefund |

## Einzelbegründungen

**PMC12903794.** Der Vergleich lautet Melatonin vs. partieller Schlafentzug,
nicht vs. Placebo („melatonin versus sleep deprivation for sleep induction in
nap electroencephalography"). Damit fehlt die für unsere Frage nötige
Kontrollbedingung; das Design ist nicht das Problem, der Vergleich ist es. Ein
Washout wird nicht berichtet.

**PMC4425994.** Crossover mit 1 Woche Washout, aber die Autoren berichten
„Significant carry over effects were seen, analysis performed as difference
from baseline for phase 1 only". Damit ist die Auswertung faktisch ein
Parallelvergleich der ersten Periode mit n = 11. Die Differenz 11,4 min
(SD 9,4) ergibt SE = 9,4 / √11 = 2,8. Verwendbar nur als Sensitivitätsanalyse,
weil (a) Carryover, (b) sehr kleine Stichprobe, (c) die Autoren selbst den
Rangsummen- statt Vorzeichenrang-Test verwenden.

**PMC4365553.** Teil 1 ist ein Crossover (Baseline vs. Lärm/Licht), Teil 2
randomisiert 40 Probanden auf vier **parallele** Bedingungen (NL, NLP, NLEE,
NLM), je 10. Die SOL-Werte der Tabelle 3 sind damit unabhängige Gruppen:
NLM 33,7 (10,5) vs. NLP 61,3 (20,6), MD = −27,6 min, SE = 7,3. Aber: gesunde
Probanden in simulierter Intensivstation, keine Insomnie-Population.

**PMC11103136.** Crossover, 2 mg prolongiertes Melatonin vs. Placebo, n = 64,
mindestens ein Tag Abstand. SOL ist nicht der primäre Endpunkt (die Studie
untersucht Speichelcortisol und Amylase). Gepaarte SD je Bedingung, keine
Korrelation. Mit konservativer ungepaarter SE: 4,1 min; mit angenommener
Korrelation r = 0,5: 3,0 min (Var = 16,54 − 2·0,5·27,46·17,45/64 = 9,05). Nur Sensitivität, weil Population gesund.

## Konsequenz für die Hauptanalyse

Keine der vier Crossover-Studien kommt in die Hauptanalyse. Zwei Gründe, die
nichts mit „Crossover" zu tun haben: fehlender Placebo-Vergleich
(PMC12903794) und gesunde statt Insomnie-Population (PMC4365553,
PMC11103136). PMC4425994 wäre populationsseitig passend, scheitert aber am
Carryover und an n = 11.

**Sensitivitätsanalyse** (wenn überhaupt): PMC4425994 als ungepaarte
Phase-1-Differenz, PMC11103136 mit r = 0,5. Beide getrennt ausweisen, nie in
die Hauptschätzung mischen.

---

# Aufgabe C - Screening-Register

## Regelversionen

| Version | Regel | Ergebnis |
|---|---|---|
| erster Durchgang (`bewertung_q2_20261108.md`) | manuelle Sichtung, kein Titelfilter | „17 von 31 keine Melatonin-Studien" → 14 |
| zweiter Durchgang (`read_q2_extended.py`, Zeilen 156–157) | Titel enthält „melatonin" UND nicht `ramelteon|tasimelteon|agomelatine|valerian|cherry|vitamin|exercise|dexmedetomidine|temazepam|zolpidem|melatonin receptor agonist` | 20 von 31 |

## Die 11 Ausschlüsse, einzeln

| PMC | Ausschlussgrund | Regel greift |
|---|---|---|
| PMC10796483 | Baldrian (Valeriana officinalis) | „kein melatonin im Titel" |
| PMC11123999 | Aloysia citrodora | „kein melatonin im Titel" |
| PMC11801451 | Dexmedetomidin | „kein melatonin im Titel" |
| PMC12106789 | Aerobes Training | „kein melatonin im Titel" |
| PMC12878997 | Sauerkirschprodukt | „kein melatonin im Titel" |
| PMC2647789 | Ramelteon | „kein melatonin im Titel" |
| PMC3014244 | Ramelteon | „kein melatonin im Titel" |
| PMC3133468 | Sauerkirschsaft | „kein melatonin im Titel" |
| PMC7726118 | Ernährung | „kein melatonin im Titel" |
| PMC2269113 | Melatonin **und Temazepam** | Ausschlusswort „temazepam" |
| PMC12449008 | Melatonin-**Agonist** Tasimelteon | Ausschlusswort „tasimelteon" |

Alle 20 eingeschlossenen Titel enthalten „melatonin" und keines der
Ausschlusswörter. Die Regel ist damit deterministisch und reproduzierbar:
31 − 11 = 20.

## Die Differenz 14 vs. 20

Sie beträgt 6. Die alte Zahl 17 ist **nicht namentlich dokumentiert** - es gibt
keine Liste der 17. Damit ist die Differenz nicht belegbar aufzulösen, nur zu
erklären: Die manuelle Sichtung im ersten Durchgang hat zusätzlich sechs
Melatonin-Studien als „keine Melatonin-Studie" gezählt, die nach der heutigen
Regel eingeschlossen sind. Als Kandidaten kommen die sechs Studien in Frage,
deren Population oder Endpunkt nicht zur Frage passt:

PMC4066551 (Tetraplegie, Melatonin-Ersatz), PMC3443766 (Hypertonie unter
Beta-Blockern), PMC6302692 (Cholecystektomie), PMC3679650 (Nachtschicht),
PMC9819026 (liposomales Melatonin, Case-Control), PMC9433621 (Bioverfügbarkeit).

**Status: Hypothese, nicht Beleg.** Für die Auswertung gilt die maschinelle
Regel (20), weil sie reproduzierbar ist; die Differenz bleibt als offene
Dokumentationslücke stehen. Zahlen werden nicht rückwirkend geändert.

---

# Aufgabe D - Endpunkt PMC3489506

## Was das Protokoll sagt

Zitate aus dem Volltext:

- „The trial was originally designed with two primary outcomes: total sleep
  time according to the sleep diary and sleep onset latency measured with
  actigraphy."
- „During trial recruitment we observed high rates of missing data (66%) for
  actigraphy so we re-designated sleep onset latency as a secondary outcome and
  removed the Bonferroni multiplicity adjustment in a protocol amendment."
- „The primary outcome was total sleep time, measured by diaries completed by
  parents."
- Registrierung: „ISRCT No 05534585".

## Entscheidung

1. **Protokollkonform** ist TST (Tagebuch) der primäre Endpunkt und SOL ein
   sekundärer. Für unsere Forschungsfrage ist SOL der Zielendpunkt - das ist
   eine **nachträgliche** Festlegung, keine protokollkonforme, und wird so
   gekennzeichnet.
2. **Hauptanalyse:** SOL aus dem **Schlaftagebuch** (n = 113). Begründung:
   vollständigere Erhebung (73 % bzw. 78 % der randomisierten Kinder), während
   die Aktigraphie 66 % fehlende Daten hatte und deshalb zum sekundären
   Endpunkt wurde.
3. **Sensitivitätsanalyse:** SOL aus der **Aktigraphie** (n = 49).
4. Die beiden Messmethoden werden **nie** als zwei Studien gezählt. k = 1 für
   diese Studie.
5. **Adjustierte Originaleffekte** bleiben getrennt von selbst berechneten
   Werten:

| Quelle | Endpunkt | Effekt | Herkunft |
|---|---|---|---|
| Studie, adjustiert | SOL Tagebuch | −37,5 min (−55,3 bis −19,7) | Studienangabe, Tabelle 3 |
| Studie, adjustiert | SOL Aktigraphie | −45,3 min (−68,8 bis −21,9) | Studienangabe, Tabelle 3 |
| eigene Rechnung, unadjustiert | SOL Tagebuch | g = −0,644 (SE 0,193, n = 113) | Week-12-Mittelwerte |
| eigene Rechnung, unadjustiert | SOL Aktigraphie | g = −0,685 (SE 0,294, n = 49) | Week-12-Mittelwerte |

Die adjustierten Werte sind für eine MD-Metaanalyse die richtige Grundlage
(SE aus dem CI: 9,1 bzw. 12,0 min); die g-Werte dienen nur dem Abgleich mit
SMD-basierten Übersichten.

---

# Kurzformat

| Feld | Angabe |
|---|---|
| **Neue Evidenz** | vier XML-Volltexte geprüft (PMC2933606, PMC2952772, PMC5774131, PMC10131443) plus vier Crossover-Studien; keine neuen Dokumente beschafft |
| **Extraktion** | SOL-Mittelwerte/Streuungen aus PMC2933606 (Tab. 3), SOL-Differenzen mit SE aus PMC2952772 (Tab. 2), log-Werte aus PMC5774131 (Tab. 2), Kategorien aus PMC10131443 (Tab. 3) - jeweils mit Zitat |
| **Poolbarkeit** | PMC2933606 ja (MD, SD, N, 3 Wochen); PMC2952772 ja (MD, SE, N, 1 Woche); PMC5774131 nein (log-Einheiten); PMC10131443 nein (nur Kategorien); Crossover keine für die Hauptanalyse |
| **k vorher → nachher** | 1 → **3** (PMC3489506, PMC2933606, PMC2952772) |
| **Offene Unsicherheit** | Auswahl der Population bei PMC2933606 und der Dosis bei PMC2952772 (beide nachträglich); Heterogenität nach Alter und Behandlungsdauer; Screening-Differenz 14 vs. 20 nur als Hypothese erklärt |
| **Nächster Schritt** | gepoolte MD mit den drei Studien (HKSJ), Hauptanalyse Tagebuch-SOL bei PMC3489506, Sensitivität mit Aktigraphie und mit den alternativen Populations-/Dosiszeilen |

## Grenzen dieser Prüfung

- **Zweitprüfung:** Es gab keine unabhängige zweite Person. Die Gegenprüfung
  bestand aus erneutem Lesen der XML-Tabellenzeilen (nicht des gerenderten
  Textes) und Nachrechnen der SE aus den berichteten CIs. Das ersetzt keine
  unabhängige Doppelkodierung und wird hier nicht als solche ausgegeben.
- **Keine Simulation, kein neuer Parser.** Alle Zahlen stammen aus den
  XML-Tabellen; die Extraktion war Handarbeit.
- **Populationen sind heterogen:** Kinder (6–12) und Erwachsene (65–80),
  1 Woche und 12 Wochen Behandlungsdauer. Eine gepoolte Zahl wird deshalb
  Heterogenität zeigen; I² bei k = 3 ist nicht belastbar interpretierbar.
