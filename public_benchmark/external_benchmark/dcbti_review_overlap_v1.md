# dCBT-I-Studienabgleich mit Hwang 2025 und Lee 2023

Stand: 2026-11-13T12:51:33Z

## Befund zur Datenbasis

Im Projekt liegen **9 CBT-I-Primärstudien** mit DOI (4 aus dem dCBT-I-Pilot, 6 aus dem CBT-I-Pilot, eine Studie in beiden Listen). Nicht alle neun sind vollständig digital; die vier dCBT-I-Pilotstudien sind der digitale Kern.

Die im Auftrag genannten **30 dCBT-I-Studien existieren so nicht**: `data/golden_effects/documents.json` enthält 30 gemischte Volltexte (5 mit Schlafbezug, davon **0 dCBT-I**). Der Abgleich wurde deshalb auf die tatsächlich vorhandenen CBT-I-Studien angewendet.

## Geprüfte Studien

| Studie | DOI | PMCID | Jahr |
|---|---|---|---:|
| chan_2021 | `10.1542/peds.2020-006833` | nicht hinterlegt | 2021 |
| chan_2022 | `10.1016/j.jadohealth.2021.11.005` | nicht hinterlegt | 2022 |
| de_bruin_2015 | `10.1016/j.sleep.2014.12.009` | nicht hinterlegt | 2015 |
| de_bruin_2018 | `10.1111/jcpp.12834` | nicht hinterlegt | 2018 |
| egbegi_2021 | `10.1186/s13034-021-00406-1` | PMC8465787 | 2021 |
| freeman_2017 | `10.1016/S2215-0366(17)30328-0` | PMC5614772 | 2017 |
| fucito_2017 | `10.1111/acer.13342` | PMC5378596 | 2017 |
| morris_2015 | `10.1080/10615806.2015.1058924` | nicht hinterlegt | 2015 |
| tomfohr_madsen_2020 | `10.1097/htr.0000000000000504` | nicht hinterlegt | 2020 |

## Ergebnisse

| Review | eingeschlossene RCTs | Treffer |
|---|---:|---:|
| npj Digital Medicine 8:157 (2025) | 29 | 0 |
| npj Digital Medicine 6:52 (2023) | 22 | 1 |

**1 von 9 Studien** konnten zugeordnet werden.

### Treffer: freeman_2017 in Freeman 2017

- Review: Digital cognitive behavioral therapy for insomnia on depression and anxiety: a systematic review and meta-analysis
- DOI: `10.1016/S2215-0366(17)30328-0`; PMCID `PMC5614772`
- Abgleich über: doi, autor_jahr
- Design: 2 parallele Arme (dCBTi, TAU); Sitzungen: 6
- N gesamt: Review 3755, Projekt 3755 → identisch
- Outcomes im Review: ISI, PHQ-9, GAD-7
- Outcomes im Projekt: ISI
- Outcome-Überschneidung: ISI
- Zeitpunkt Review: 10 Wochen post-treatment
- Zeitpunkt Projekt: post-treatment (Woche 10)
- Wochenvergleich (nur Post-Treatment): Projekt [10.0] vs. Review [10.0]; Differenz 0.0 Wochen (Toleranz 0.5); übereinstimmend
- Review nennt nur Studiencharakteristika; Mittelwerte und SD stehen nicht in Tabelle 1.

## Nicht zugeordnete Studien

chan_2021, chan_2022, de_bruin_2015, de_bruin_2018, egbegi_2021, fucito_2017, morris_2015, tomfohr_madsen_2020

Für sie enthält keine der beiden Studienlisten einen Treffer nach DOI oder Autor/Jahr. Das ist **kein** Beleg dafür, dass die Studien fehlerhaft sind; sie sind nur nicht in diesen Reviews enthalten.

## Plausible Ausschlussgründe

Die Reviews dokumentieren keine studiengenauen Ausschlussgründe. Die folgenden Einordnungen sind aus den publizierten Kriterien und den Studienabstracts abgeleitet und als plausibel, nicht als bestätigt markiert.

### chan_2021

- **Hwang 2025:** Die Stichprobe sind Jugendliche mit einem mittleren Alter von 14,7 Jahren; zudem ein Präventionsprogramm bei subklinischer Insomnie, keine Behandlung einer diagnostizierten Insomnie. Kriterium: Erwachsene ≥18 Jahre. Konfidenz: hoch. Beleg: Abstract: 242 adolescents, mean age 14.7 ± 1.8, family history und subthreshold insomnia.
- **Lee 2023:** Die Stichprobe sind Jugendliche mit einem mittleren Alter von 14,7 Jahren. Kriterium: Erwachsene ≥18 Jahre. Konfidenz: hoch. Beleg: Abstract: mean age 14.7 ± 1.8.

### chan_2022

- **Hwang 2025:** Die Stichprobe sind 'youths' mit einem Mittelwert von 20,0 ± 2,5 Jahren, ein Teil kann unter 18 sein. Die E-Mail-Self-Help-Bedingung ist nicht eindeutig als vollständig automatisiert ohne Therapeutenkontakt beschrieben. Kriterium: Erwachsene ≥18 Jahre; vollständig automatisierte dCBT-I. Konfidenz: niedrig. Beleg: Abstract: 135 youths, mean age 20.0 ± 2.5; E-Mail-Self-Help versus Gruppentherapie versus Warteliste.
- **Lee 2023:** Die Outcomes sind Insomnie, präsleep arousal, dysfunktionale Überzeugungen, Schlafhygiene und Tagesfunktion; Depression oder Angst werden nicht berichtet. Die Arbeit ist mit Publikationsjahr 2022 geführt; ob sie vor dem Lee-Suchschluss online verfügbar war, ist nicht belegt. Kriterium: berichtete Depression- oder Angstmaße; Suchschluss 15.01.2022. Konfidenz: mittel. Beleg: Abstract listet keine Depression- oder Angstskala; Publikationsjahr 2022.

### de_bruin_2015

- **Hwang 2025:** Die Stichprobe ist 13-19 Jahre alt (M = 15,9); zudem geleitete Self-Help-Sitzungen, also nicht vollständig automatisiert. Kriterium: Erwachsene ≥18 Jahre; vollständig automatisierte dCBT-I. Konfidenz: hoch. Beleg: Abstract: 32 adolescents, 13-19 years, six guided self-help online CBTI sessions.
- **Lee 2023:** Die Stichprobe ist 13-19 Jahre alt (M = 15,9). Kriterium: Erwachsene ≥18 Jahre. Konfidenz: hoch. Beleg: Abstract: 13-19 years, M = 15.9.

### de_bruin_2018

- **Hwang 2025:** Die Stichprobe besteht aus Jugendlichen mit einem mittleren Alter von 15,6 Jahren. Kriterium: Erwachsene ≥18 Jahre. Konfidenz: hoch. Beleg: Abstract: 116 Teilnehmende, age = 15.6 years, DSM-5-Insomnie.
- **Lee 2023:** Die Stichprobe besteht aus Jugendlichen mit einem mittleren Alter von 15,6 Jahren. Kriterium: Erwachsene ≥18 Jahre. Konfidenz: hoch. Beleg: Abstract: age = 15.6 years; Internet- und Gruppentherapie versus Warteliste.

### egbegi_2021

- **Hwang 2025:** Die Stichprobe sind In-School-Adoleszente; die Intervention war eine gruppenbasierte manualisierte CBT vor Ort, nicht digital. Kriterium: Erwachsene ≥18 Jahre; digital gelieferte dCBT-I. Konfidenz: hoch. Beleg: Abstract: 50 in-school adolescents, weekly group-based manualised CBT-based intervention over 5 weeks.
- **Lee 2023:** In-School-Adoleszente und eine gruppenbasierte Intervention vor Ort, keine digitale CBT-I. Kriterium: Erwachsene ≥18 Jahre; dCBT-I. Konfidenz: hoch. Beleg: Abstract: in-school adolescents, group-based manualised intervention.

### fucito_2017

- **Hwang 2025:** Die Studie rekrutiert ausschließlich Heavy-Drinking-College-Students und adressiert Alkoholkonsum. Das liegt nahe am Hwang-Ausschluss für Alkoholmissbrauch oder -abhängigkeit; eine entsprechende Diagnose ist im Abstract aber nicht belegt. Kriterium: Ausschluss von Alkoholmissbrauch oder -abhängigkeit. Konfidenz: mittel. Beleg: Abstract: 'Heavy-drinking college students (N = 42)', web-basierte Schlaf-plus-Alkohol-Intervention über 4 Wochen.
- **Lee 2023:** Die Intervention kombiniert Schlaf- und Alkoholinhalte; Depression oder Angst werden nicht als Outcomes berichtet. Kriterium: dCBT-I-Programm; berichtete Depression- oder Angstmaße. Konfidenz: mittel. Beleg: Abstract nennt Alkohol- und Schlafoutcomes, keine Depression- oder Angstskala.

### morris_2015

- **Hwang 2025:** Die Stichprobe sind Studierende mit Angst- und/oder Insomniesymptomen. Der Abstract belegt weder eine formale Insomniediagnose noch, dass der Insomnie-Arm ohne Therapeutenkontakt lief. Kriterium: Erwachsene mit formaler Insomniediagnose; vollständig automatisierte dCBT-I ohne Therapeutenkontakt. Konfidenz: mittel. Beleg: Abstract: zwei getrennte Programme ('Anxiety Relief', 'Insomnia Relief'), 6 Wochen, STAI und PSQI; keine Angabe zu Diagnose oder Guidance.
- **Lee 2023:** Transdiagnostisches Angst-/Insomnie-Programm; der Insomnie-Arm ist nicht als multimodales CBT-I mit beiden geforderten Komponenten beschrieben. Angst wurde erhoben, Depression nicht. Kriterium: dCBT-I mit kognitiver Umstrukturierung plus Stimuluskontrolle/Schlafrestriktion; Depression- oder Angstmaß. Konfidenz: mittel. Beleg: Abstract: STAI als Angstmaß, PSQI als Schlafmaß; keine Beschreibung von Cognitive Restructuring plus Stimuluskontrolle/Schlafrestriktion.

### tomfohr_madsen_2020

- **Hwang 2025:** Die Stichprobe ist 12-18 Jahre alt (M = 15,0); die CBT-I wird nicht als digitale, vollständig automatisierte Intervention beschrieben. Kriterium: Erwachsene ≥18 Jahre; vollständig automatisierte dCBT-I. Konfidenz: hoch. Beleg: Abstract: N = 24, 12-18 years, M = 15.0, CBT-I versus TAU.
- **Lee 2023:** Die Stichprobe ist 12-18 Jahre alt (M = 15,0). Kriterium: Erwachsene ≥18 Jahre. Konfidenz: hoch. Beleg: Abstract: 12-18 years, M = 15.0.

## Einordnung

- Der einzige belastbare Treffer ist **Freeman 2017 (OASIS)** in Lee 2023. Studie, ISI als Schlafoutcome, Zeitpunkt 10 Wochen und Gesamt-N 3755 stimmen überein.
- Lee 2023 extrahiert zusätzlich PHQ-9 und GAD-7; diese Outcomes wurden im Projekt nicht extrahiert. Die Outcome-Überschneidung ist daher nur ISI.
- Hwang 2025 enthält Freeman 2017 nicht, obwohl die Arbeit als Hintergrundquelle zitiert wird. Zitierung ist keine Aufnahme.
- Hwang 2025 enthält Chan 2023 (Hongkong, smartphone-delivered), nicht unsere Chan-Studien 2021/2022.
- Keine der beiden Tabellen nennt armweise Mittelwerte oder SD. Eine numerische Bestätigung unserer Werte ist aus den Review-Tabellen nicht möglich, nur eine Bestätigung von Studie, Outcome, Zeitpunkt und N.

## Grenzen

- Die Review-Tabellen nennen keine PMCIDs; PMCID-Abgleich ist nur fuer Studien moeglich, deren PMCID im Projekt oder in der Referenzliste steht.
- DOI steht in Tabelle 1 nur bei der bestaetigten Zeile; weitere DOIs wurden nicht aus der Referenzliste rekonstruiert.
- Tabelle 1 nennt keine armweisen Mittelwerte oder SD; eine numerische Bestaetigung der Extraktion ist daraus nicht moeglich.
- Die Supplementary-PDFs enthalten keine Studienliste; massgeblich ist Tabelle 1.

## Empfehlung

Der Review-Abgleich bestätigt genau eine Studie und dort nur ISI, Zeitpunkt und N. Als externer Goldstandard für die 30 Volltexte ist er ungeeignet. Sinnvoller ist, die 30 Volltexte zuerst als das zu benennen, was sie sind (gemischtes Methoden-Sample), und für die dCBT-I-Frage die vier vorhandenen Primärstudien gezielt gegen Lee 2023 und die Primärtexte zu prüfen.
