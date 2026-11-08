# Zugangsliste: Melatonin-Trials ohne PMC-Volltext

Stand: 2026-11-08T13:06:18. Quelle: `data/bench/sol2/manifest_q2.json`, 114 Treffer, davon 83 ohne Volltext.
Kein Netz. Die Prioritaet ist eine Lesehilfe, keine Bewertung.

| Prioritaet | Anzahl | Bedeutung |
|---|---:|---|
| A | 5 | Melatonin + RCT-Signal + Einschaflatenz/Insomnie im Titel |
| B | 20 | Melatonin + RCT-Signal, Endpunkt offen |
| C | 39 | Melatonin, aber anderer Wirkstoff oder kein Schlafendpunkt |
| D | 19 | Melatonin nicht im Titel - nicht anfordern |

Mit DOI bestellbar: 80 von 83.

## Prioritaet A

| PMID | DOI | Jahr | Zeitschrift | Titel |
|---|---|---:|---|---|
| 41122831 | 10.1111/jpc.70224 | 2026 | Journal of paediatrics and child health | A Pilot Randomised Controlled Trial of Sublingual Melatonin for Sleep Onset Insomnia in Children With Foetal A |
| 33157425 | 10.1016/j.sleep.2020.10.018 | 2020 | Sleep medicine | Efficacy of melatonin for sleep disturbance in middle-aged primary insomnia: a double-blind, randomised clinic |
| 28364493 | 10.1093/sleep/zsw038 | 2017 | Sleep | Effects of Melatonin and Bright Light Treatment in Childhood Chronic Sleep Onset Insomnia With Late Melatonin  |
| 14566165 | 10.1097/01.chi.0000085756.71002.86 | 2003 | Journal of the American Academy of Child | Melatonin improves health status and sleep in children with idiopathic chronic sleep-onset insomnia: a randomi |
| 11292231 | 10.1177/088307380101600204 | 2001 | Journal of child neurology | Melatonin for chronic sleep onset insomnia in children: a randomized placebo-controlled trial. |

## Prioritaet B

| PMID | DOI | Jahr | Titel |
|---|---|---:|---|
| 42533530 | 10.1080/07357907.2025.2563202 | 2026 | The Effect of Melatonin on Sleep Quality, Anxiety, and Depression in Patients with Primary Breast Cancer Under |
| 41369870 | 10.1007/s12098-025-05873-4 | 2026 | Oral Melatonin Supplementation for Sleep Disturbances in Children with Cerebral Palsy: A Randomized Double-Bli |
| 40791136 | 10.1039/d5fo00971e | 2025 | Daily walnut consumption increases 6-sulfatoxymelatonin urinary levels and can improve sleep quality: a random |
| 39437460 | 10.1016/j.sleep.2024.10.020 | 2024 | Melatonin on sleep in Parkinson's disease: A randomized double blind placebo controlled trial. |
| 34181143 | 10.1007/s10803-021-05139-w | 2022 | Melatonin Treatment and Adequate Sleep Hygiene Interventions in Children with Autism Spectrum Disorder: A Rand |
| 34293628 | 10.1016/j.ejpn.2021.06.006 | 2021 | Efficacy and tolerability of Melatonin vs Triclofos to achieve sleep for pediatric electroencephalography: A s |
| 30160043 | 10.1111/pai.12978 | 2018 | The effects of melatonin administration on disease severity and sleep quality in children with atopic dermatit |
| 29619605 | 10.1007/s00737-018-0838-x | 2018 | Both melatonin and meloxicam improved sleep and pain in females with primary dysmenorrhea-results from a doubl |
| 26569624 | 10.1001/jamapediatrics.2015.3092 | 2016 | Melatonin Supplementation for Children With Atopic Dermatitis and Sleep Disturbance: A Randomized Clinical Tri |
| 23098680 | 10.3310/hta16400 | 2012 | The use of MElatonin in children with neurodevelopmental disorders and impaired sleep: a randomised, double-bl |
| 20535539 | 10.1007/s10803-010-1036-5 | 2011 | Melatonin versus placebo in children with autism spectrum conditions and severe sleep problems not amenable to |
| 20025642 | 10.1111/j.1600-079X.2009.00726.x | 2010 | Melatonin improves sleep and reduces nitrite in the exhaled breath condensate in cystic fibrosis--a randomized |
| 19299778 | 10.1213/ane.0b013e31819a6cf0 | 2009 | The effect of melatonin on sleep quality after laparoscopic cholecystectomy: a randomized, placebo-controlled  |
| 18078449 | 10.1111/j.1600-079X.2007.00528.x | 2008 | A randomized, placebo-controlled trial of controlled release melatonin treatment of delayed sleep phase syndro |
| 17404779 | 10.1007/s00415-006-0390-x | 2007 | Effect of exogenous melatonin on sleep and motor dysfunction in Parkinson's disease. A randomized, double blin |
| 16919138 | 10.1111/j.1365-2214.2006.00616.x | 2006 | Randomized controlled trial of melatonin for children with autistic spectrum disorders and sleep problems. |
| 15275698 | 10.1016/S0387-7604(03)00197-9 | 2004 | Melatonin in wake-sleep disorders in children, adolescents and young adults with mental retardation with or wi |
| 11211063 | 10.1097/00006842-200101000-00005 | 2001 | A randomized, double-blind, placebo-controlled crossover study of the effect of exogenous melatonin on delayed |
| 9737496 | 10.1016/s0196-0644(98)70010-1 | 1998 | Randomized clinical trial of melatonin after night-shift work: efficacy and neuropsychologic effects. |
| 9566656 | 10.1111/j.1469-8749.1998.tb15445.x | 1998 | Sleep dysfunction in Rett syndrome: a trial of exogenous melatonin treatment. |

## Prioritaet C und D (nur Zaehlung)

39 Dokumente mit anderem Wirkstoff oder ohne Schlafendpunkt, 19 ohne Melatonin im Titel. Beide Gruppen stehen vollstaendig in der JSON- und CSV-Datei, aber nicht in dieser Bestellliste.

## Wie die Liste benutzt wird

1. Prioritaet A zuerst bestellen (DOI ist angegeben, PMID als Rueckfall).
2. B nachziehen, wenn A nicht reicht.
3. Nach Erhalt: XML mit `scripts/read_q2_extended.py`, PDFs mit
   `scripts/read_pdf_corpus.py` lesen. Fuer A gilt das Schritt-Ziel k >= 2,
   das Gesamtziel k >= 5 ist an A + B gebunden.

Grenze: Die Einordnung liest nur den Titel. Ein Trial kann in A stehen
und am Volltext scheitern (kein Arm-Mittelwert) oder in B stehen und
die Einschaflatenz doch berichten. Die Liste ersetzt kein Screening.
