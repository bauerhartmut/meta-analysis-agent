# dCBT-I-Studienabgleich mit Hwang 2025 und Lee 2023

Stand: 2026-11-13T12:18:15Z

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
- Zeitpunkt übereinstimmend: ja
- Review nennt nur Studiencharakteristika; Mittelwerte und SD stehen nicht in Tabelle 1.

## Nicht zugeordnete Studien

chan_2021, chan_2022, de_bruin_2015, de_bruin_2018, egbegi_2021, fucito_2017, morris_2015, tomfohr_madsen_2020

Für sie enthält keine der beiden Studienlisten einen Treffer nach DOI oder Autor/Jahr. Das ist **kein** Beleg dafür, dass die Studien fehlerhaft sind; sie sind nur nicht in diesen Reviews enthalten.

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
