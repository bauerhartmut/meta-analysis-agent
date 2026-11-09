# Fernleih-Bestellliste: 5 A- und 20 B-Titel

Stand: 2026-11-09. Grundlage ist die Zugangsliste der 83 Dokumente ohne PMC-Volltext (`zugangsliste_20261108.csv`, Prioritaeten A 5, B 20, C 39, D 19). Je Eintrag stehen die Felder, die ein Fernleihformular verlangt: Autor, Titel, Quelle, DOI, PMID.

Alle Angaben sind maschinell aus lokalen Dateien uebernommen, nichts ist abgetippt oder ergaenzt: A aus `zitationen_a.json` (PubMed-Metadaten), B aus `abstracts_b_20261108.xml` (PubMed-efetch). Erzeugt von `scripts/erstelle_fernleihliste.py`.

**Fuenf der zwanzig B-Titel sind nach der Abstract-Triage nicht zu bestellen** (Klasse D: kein Placebo, kein Melatonin, Duplikat oder kein SOL-Endpunkt). Sie stehen in Teil 2 mit dem Vermerk `entfaellt` und sind in Abschnitt 4 begruendet. Die bestellfaehige Menge sind 5 + 15 = 20 Titel.

## 1. Uebersicht

| Nr | Teil | PMID | DOI | Jahr | Triage |
|---:|---|---|---|---:|---|
| 1 | A | 41122831 | 10.1111/jpc.70224 | 2026 | - |
| 2 | A | 33157425 | 10.1016/j.sleep.2020.10.018 | 2021 | - |
| 3 | A | 28364493 | 10.1093/sleep/zsw038 | 2017 | - |
| 4 | A | 14566165 | 10.1097/01.chi.0000085756.71002.86 | 2003 | - |
| 5 | A | 11292231 | 10.1177/088307380101600204 | 2001 | - |
| 6 | B | 42533530 | 10.1080/07357907.2025.2563202 | 2026 | C |
| 7 | B | 41369870 | 10.1007/s12098-025-05873-4 | 2026 | A |
| 8 | B | 40791136 | 10.1039/d5fo00971e | 2025 | D |
| 9 | B | 39437460 | 10.1016/j.sleep.2024.10.020 | 2024 | A |
| 10 | B | 34181143 | 10.1007/s10803-021-05139-w | 2022 | A |
| 11 | B | 34293628 | 10.1016/j.ejpn.2021.06.006 | 2021 | D |
| 12 | B | 30160043 | 10.1111/pai.12978 | 2018 | B |
| 13 | B | 29619605 | 10.1007/s00737-018-0838-x | 2018 | D |
| 14 | B | 26569624 | 10.1001/jamapediatrics.2015.3092 | 2016 | B |
| 15 | B | 23098680 | 10.3310/hta16400 | 2012 | D |
| 16 | B | 20535539 | 10.1007/s10803-010-1036-5 | 2011 | A |
| 17 | B | 20025642 | 10.1111/j.1600-079X.2009.00726.x | 2010 | B |
| 18 | B | 19299778 | 10.1213/ane.0b013e31819a6cf0 | 2009 | A |
| 19 | B | 18078449 | 10.1111/j.1600-079X.2007.00528.x | 2008 | B |
| 20 | B | 17404779 | 10.1007/s00415-006-0390-x | 2007 | B |
| 21 | B | 16919138 | 10.1111/j.1365-2214.2006.00616.x | 2006 | A |
| 22 | B | 15275698 | 10.1016/S0387-7604(03)00197-9 | 2004 | B |
| 23 | B | 11211063 | 10.1097/00006842-200101000-00005 | 2001 | B |
| 24 | B | 9737496 | 10.1016/s0196-0644(98)70010-1 | 1998 | D |
| 25 | B | 9566656 | 10.1111/j.1469-8749.1998.tb15445.x | 1998 | A |

## 2. Prioritaet A: fuenf Titel mit Einschaflatenz im Titel

### 1) A Pilot Randomised Controlled Trial of Sublingual Melatonin for Sleep Onset Insomnia in Children With Foetal Alcohol Spectrum Disorder (FASD)

```text
Autor: Chandler-Mather N, Shelton D, Donovan C, Till H, Theroux BM, Dawe S
Titel: A Pilot Randomised Controlled Trial of Sublingual Melatonin for Sleep Onset Insomnia in Children With Foetal Alcohol Spectrum Disorder (FASD)
Quelle: J Paediatr Child Health. 2026;62(1):16-22
DOI: 10.1111/jpc.70224
PMID: 41122831
```

### 2) Efficacy of melatonin for sleep disturbance in middle-aged primary insomnia: a double-blind, randomised clinical trial

```text
Autor: Xu H, Zhang C, Qian Y, Zou J, Li X, Liu Y et al.
Titel: Efficacy of melatonin for sleep disturbance in middle-aged primary insomnia: a double-blind, randomised clinical trial
Quelle: Sleep Med. 2021;76:113-119
DOI: 10.1016/j.sleep.2020.10.018
PMID: 33157425
```

### 3) Effects of Melatonin and Bright Light Treatment in Childhood Chronic Sleep Onset Insomnia With Late Melatonin Onset: A Randomized Controlled Study

```text
Autor: van Maanen A, Meijer AM, Smits MG, van der Heijden KB, Oort FJ
Titel: Effects of Melatonin and Bright Light Treatment in Childhood Chronic Sleep Onset Insomnia With Late Melatonin Onset: A Randomized Controlled Study
Quelle: Sleep. 2017;40(2)
DOI: 10.1093/sleep/zsw038
PMID: 28364493
Hinweis: Andere Intervention (Melatonin plus Licht), keine Doppelpublikation.
```

### 4) Melatonin improves health status and sleep in children with idiopathic chronic sleep-onset insomnia: a randomized placebo-controlled trial

```text
Autor: Smits MG, van Stel HF, van der Heijden K, Meijer AM, Coenen AM, Kerkhof GA
Titel: Melatonin improves health status and sleep in children with idiopathic chronic sleep-onset insomnia: a randomized placebo-controlled trial
Quelle: J Am Acad Child Adolesc Psychiatry. 2003;42(11):1286-93
DOI: 10.1097/01.chi.0000085756.71002.86
PMID: 14566165
Hinweis: Von S3 zitiert, externe Arbeit; mit 11292231 auf gleiche Kohorte pruefen.
```

### 5) Melatonin for chronic sleep onset insomnia in children: a randomized placebo-controlled trial

```text
Autor: Smits MG, Nagtegaal EE, van der Heijden J, Coenen AM, Kerkhof GA
Titel: Melatonin for chronic sleep onset insomnia in children: a randomized placebo-controlled trial
Quelle: J Child Neurol. 2001;16(2):86-92
DOI: 10.1177/088307380101600204
PMID: 11292231
Hinweis: Von S3 zitiert, externe Arbeit; mit 14566165 auf gleiche Kohorte pruefen.
```

## 3. Prioritaet B: zwanzig Titel, Endpunkt offen

### 6) The Effect of Melatonin on Sleep Quality, Anxiety, and Depression in Patients with Primary Breast Cancer Undergoing Adjuvant Chemotherapy Type: A Randomized, Double-Blind, Placebo-Controlled Trial

```text
Autor: SeddighShamsi M, Esfandbod M, Jalali S, Etesam F, Jahangard Rafsanjani Z, Ghorani V et al.
Titel: The Effect of Melatonin on Sleep Quality, Anxiety, and Depression in Patients with Primary Breast Cancer Undergoing Adjuvant Chemotherapy Type: A Randomized, Double-Blind, Placebo-Controlled Trial
Quelle: Cancer Invest. 2026;44(8):845-854
DOI: 10.1080/07357907.2025.2563202
PMID: 42533530
Triage: Klasse C
```

### 7) Oral Melatonin Supplementation for Sleep Disturbances in Children with Cerebral Palsy: A Randomized Double-Blind Controlled Trial

```text
Autor: K GP, Mundada S, Zambani J, Joshi T, Khaire P, Pawar S et al.
Titel: Oral Melatonin Supplementation for Sleep Disturbances in Children with Cerebral Palsy: A Randomized Double-Blind Controlled Trial
Quelle: Indian J Pediatr. 2026;93(3):259-264
DOI: 10.1007/s12098-025-05873-4
PMID: 41369870
Triage: Klasse A
```

### 8) Daily walnut consumption increases 6-sulfatoxymelatonin urinary levels and can improve sleep quality: a randomized crossover trial

```text
Autor: Zerón-Rugerio MF, Ibarra-Picón A, Diez-Hernández M, Comas-Basté O, Pérez-Cano FJ, Cambras T et al.
Titel: Daily walnut consumption increases 6-sulfatoxymelatonin urinary levels and can improve sleep quality: a randomized crossover trial
Quelle: Food Funct. 2025;16(18):7023-7035
DOI: 10.1039/d5fo00971e
PMID: 40791136
Triage: Klasse D - entfaellt
```

### 9) Melatonin on sleep in Parkinson's disease: A randomized double blind placebo controlled trial

```text
Autor: Sugumaran R, Sai Krishna KS, Saibaba J, Narayan SK, Sandhiya S, Rajeswari M
Titel: Melatonin on sleep in Parkinson's disease: A randomized double blind placebo controlled trial
Quelle: Sleep Med. 2024;124:502-509
DOI: 10.1016/j.sleep.2024.10.020
PMID: 39437460
Triage: Klasse A
Hinweis: SOL per PSG berichtet, Differenz 8,36 min.
```

### 10) Melatonin Treatment and Adequate Sleep Hygiene Interventions in Children with Autism Spectrum Disorder: A Randomized Controlled Trial

```text
Autor: Hayashi M, Mishima K, Fukumizu M, Takahashi H, Ishikawa Y, Hamada I et al.
Titel: Melatonin Treatment and Adequate Sleep Hygiene Interventions in Children with Autism Spectrum Disorder: A Randomized Controlled Trial
Quelle: J Autism Dev Disord. 2022;52(6):2784-2793
DOI: 10.1007/s10803-021-05139-w
PMID: 34181143
Triage: Klasse A
```

### 11) Efficacy and tolerability of Melatonin vs Triclofos to achieve sleep for pediatric electroencephalography: A single blinded randomized controlled trial

```text
Autor: Lalwani S, Srivastava K, Thakor B, Panda BK, Kaur H, Karmarkar S et al.
Titel: Efficacy and tolerability of Melatonin vs Triclofos to achieve sleep for pediatric electroencephalography: A single blinded randomized controlled trial
Quelle: Eur J Paediatr Neurol. 2021;34:14-20
DOI: 10.1016/j.ejpn.2021.06.006
PMID: 34293628
Triage: Klasse D - entfaellt
```

### 12) The effects of melatonin administration on disease severity and sleep quality in children with atopic dermatitis: A randomized, double-blinded, placebo-controlled trial

```text
Autor: Taghavi Ardakani A, Farrehi M, Sharif MR, Ostadmohammadi V, Mirhosseini N, Kheirkhah D et al.
Titel: The effects of melatonin administration on disease severity and sleep quality in children with atopic dermatitis: A randomized, double-blinded, placebo-controlled trial
Quelle: Pediatr Allergy Immunol. 2018;29(8):834-840
DOI: 10.1111/pai.12978
PMID: 30160043
Triage: Klasse B
```

### 13) Both melatonin and meloxicam improved sleep and pain in females with primary dysmenorrhea-results from a double-blind cross-over intervention pilot study

```text
Autor: Keshavarzi F, Mahmoudzadeh F, Brand S, Sadeghi Bahmani D, Akbari F, Khazaie H et al.
Titel: Both melatonin and meloxicam improved sleep and pain in females with primary dysmenorrhea-results from a double-blind cross-over intervention pilot study
Quelle: Arch Womens Ment Health. 2018;21(6):601-609
DOI: 10.1007/s00737-018-0838-x
PMID: 29619605
Triage: Klasse D - entfaellt
```

### 14) Melatonin Supplementation for Children With Atopic Dermatitis and Sleep Disturbance: A Randomized Clinical Trial

```text
Autor: Chang YS, Lin MH, Lee JH, Lee PL, Dai YS, Chu KH et al.
Titel: Melatonin Supplementation for Children With Atopic Dermatitis and Sleep Disturbance: A Randomized Clinical Trial
Quelle: JAMA Pediatr. 2016;170(1):35-42
DOI: 10.1001/jamapediatrics.2015.3092
PMID: 26569624
Triage: Klasse B
Hinweis: Crossover: gepaarte Streuung noetig.
```

### 15) The use of MElatonin in children with neurodevelopmental disorders and impaired sleep: a randomised, double-blind, placebo-controlled, parallel study (MENDS)

```text
Autor: Appleton RE, Jones AP, Gamble C, Williamson PR, Wiggs L, Montgomery P et al.
Titel: The use of MElatonin in children with neurodevelopmental disorders and impaired sleep: a randomised, double-blind, placebo-controlled, parallel study (MENDS)
Quelle: Health Technol Assess. 2012;16(40):i-239
DOI: 10.3310/hta16400
PMID: 23098680
Triage: Klasse D - entfaellt
Hinweis: Zeichengleiche SOL-Werte wie PMC3489506; max. Ergaenzung fuer S1, keine neue Zeile.
```

### 16) Melatonin versus placebo in children with autism spectrum conditions and severe sleep problems not amenable to behaviour management strategies: a randomised controlled crossover trial

```text
Autor: Wright B, Sims D, Smart S, Alwazeer A, Alderson-Day B, Allgar V et al.
Titel: Melatonin versus placebo in children with autism spectrum conditions and severe sleep problems not amenable to behaviour management strategies: a randomised controlled crossover trial
Quelle: J Autism Dev Disord. 2011;41(2):175-84
DOI: 10.1007/s10803-010-1036-5
PMID: 20535539
Triage: Klasse A
Hinweis: Crossover: gepaarte Streuung noetig.
```

### 17) Melatonin improves sleep and reduces nitrite in the exhaled breath condensate in cystic fibrosis--a randomized, double-blind placebo-controlled study

```text
Autor: de Castro-Silva C, de Bruin VM, Cunha GM, Nunes DM, Medeiros CA, de Bruin PF
Titel: Melatonin improves sleep and reduces nitrite in the exhaled breath condensate in cystic fibrosis--a randomized, double-blind placebo-controlled study
Quelle: J Pineal Res. 2010;48(1):65-71
DOI: 10.1111/j.1600-079X.2009.00726.x
PMID: 20025642
Triage: Klasse B
```

### 18) The effect of melatonin on sleep quality after laparoscopic cholecystectomy: a randomized, placebo-controlled trial

```text
Autor: Gögenur I, Kücükakin B, Bisgaard T, Kristiansen V, Hjortsø NC, Skene DJ et al.
Titel: The effect of melatonin on sleep quality after laparoscopic cholecystectomy: a randomized, placebo-controlled trial
Quelle: Anesth Analg. 2009;108(4):1152-6
DOI: 10.1213/ane.0b013e31819a6cf0
PMID: 19299778
Triage: Klasse A
Hinweis: Berichtet Endwerte der ersten postoperativen Nacht, keine Veraenderung; Baseline-Ausgleich pruefen.
```

### 19) A randomized, placebo-controlled trial of controlled release melatonin treatment of delayed sleep phase syndrome and impaired sleep maintenance in children with neurodevelopmental disabilities

```text
Autor: Wasdell MB, Jan JE, Bomben MM, Freeman RD, Rietveld WJ, Tai J et al.
Titel: A randomized, placebo-controlled trial of controlled release melatonin treatment of delayed sleep phase syndrome and impaired sleep maintenance in children with neurodevelopmental disabilities
Quelle: J Pineal Res. 2008;44(1):57-64
DOI: 10.1111/j.1600-079X.2007.00528.x
PMID: 18078449
Triage: Klasse B
Hinweis: Crossover: gepaarte Streuung noetig.
```

### 20) Effect of exogenous melatonin on sleep and motor dysfunction in Parkinson's disease. A randomized, double blind, placebo-controlled study

```text
Autor: Medeiros CA, Carvalhedo de Bruin PF, Lopes LA, Magalhães MC, de Lourdes Seabra M, de Bruin VM
Titel: Effect of exogenous melatonin on sleep and motor dysfunction in Parkinson's disease. A randomized, double blind, placebo-controlled study
Quelle: J Neurol. 2007;254(4):459-64
DOI: 10.1007/s00415-006-0390-x
PMID: 17404779
Triage: Klasse B
```

### 21) Randomized controlled trial of melatonin for children with autistic spectrum disorders and sleep problems

```text
Autor: Garstang J, Wallis M
Titel: Randomized controlled trial of melatonin for children with autistic spectrum disorders and sleep problems
Quelle: Child Care Health Dev. 2006;32(5):585-9
DOI: 10.1111/j.1365-2214.2006.00616.x
PMID: 16919138
Triage: Klasse A
Hinweis: Dedup-Verdacht gegen S1 (MENDS): Register-ID im Volltext pruefen, bevor extrahiert wird.
```

### 22) Melatonin in wake-sleep disorders in children, adolescents and young adults with mental retardation with or without epilepsy: a double-blind, cross-over, placebo-controlled trial

```text
Autor: Coppola G, Iervolino G, Mastrosimone M, La Torre G, Ruiu F, Pascotto A
Titel: Melatonin in wake-sleep disorders in children, adolescents and young adults with mental retardation with or without epilepsy: a double-blind, cross-over, placebo-controlled trial
Quelle: Brain Dev. 2004;26(6):373-6
DOI: 10.1016/S0387-7604(03)00197-9
PMID: 15275698
Triage: Klasse B
Hinweis: Crossover: gepaarte Streuung noetig.
```

### 23) A randomized, double-blind, placebo-controlled crossover study of the effect of exogenous melatonin on delayed sleep phase syndrome

```text
Autor: Kayumov L, Brown G, Jindal R, Buttoo K, Shapiro CM
Titel: A randomized, double-blind, placebo-controlled crossover study of the effect of exogenous melatonin on delayed sleep phase syndrome
Quelle: Psychosom Med. 2001;63(1):40-8
DOI: 10.1097/00006842-200101000-00005
PMID: 11211063
Triage: Klasse B
Hinweis: Crossover, PSG: gepaarte Streuung noetig.
```

### 24) Randomized clinical trial of melatonin after night-shift work: efficacy and neuropsychologic effects

```text
Autor: Wright SW, Lawrence LM, Wrenn KD, Haynes ML, Welch LW, Schlack HM
Titel: Randomized clinical trial of melatonin after night-shift work: efficacy and neuropsychologic effects
Quelle: Ann Emerg Med. 1998;32(3 Pt 1):334-40
DOI: 10.1016/s0196-0644(98)70010-1
PMID: 9737496
Triage: Klasse D - entfaellt
```

### 25) Sleep dysfunction in Rett syndrome: a trial of exogenous melatonin treatment

```text
Autor: McArthur AJ, Budden SS
Titel: Sleep dysfunction in Rett syndrome: a trial of exogenous melatonin treatment
Quelle: Dev Med Child Neurol. 1998;40(3):186-92
DOI: 10.1111/j.1469-8749.1998.tb15445.x
PMID: 9566656
Triage: Klasse A
Hinweis: Crossover: gepaarte Streuung noetig.
```

## 4. Vor dem Absenden zu streichen

Diese fuenf B-Titel sind nach `triage_b_20261108.md` Klasse D. Sie kosten fuenf Fernleihen ohne Aussicht auf eine poolbare Zeile.

| PMID | DOI | Grund |
|---|---|---|
| 40791136 | 10.1039/d5fo00971e | Walnuss-Intervention, kein Melatonin |
| 34293628 | 10.1016/j.ejpn.2021.06.006 | Melatonin gegen Triclofos (EEG-Sedierung), kein Placebo |
| 29619605 | 10.1007/s00737-018-0838-x | Melatonin gegen Meloxicam, kein Placebo |
| 23098680 | 10.3310/hta16400 | HTA-Bericht der MENDS-Studie, Duplikat von S1, liegt lokal vor |
| 9737496 | 10.1016/s0196-0644(98)70010-1 | Notaerzte nach Nachtschicht, kein SOL-Endpunkt berichtet |

Bleiben 15 B-Titel. Zusammen mit den fuenf A-Titeln sind es **20 Bestellungen**.

## 5. Freitextfassung fuer ein einzelnes Bestellfeld

Fassung ohne die fuenf D-Titel (20 Bestellungen):

```text
Bitte beschaffen Sie zwanzig Aufsaetze zu Melatonin und Einschaflatenz; alle sind ueber die DOI aufloesbar: 
10.1111/jpc.70224, 10.1016/j.sleep.2020.10.018, 10.1093/sleep/zsw038,
10.1097/01.chi.0000085756.71002.86, 10.1177/088307380101600204,
10.1080/07357907.2025.2563202, 10.1007/s12098-025-05873-4,
10.1016/j.sleep.2024.10.020, 10.1007/s10803-021-05139-w,
10.1111/pai.12978, 10.1001/jamapediatrics.2015.3092,
10.1007/s10803-010-1036-5, 10.1111/j.1600-079X.2009.00726.x,
10.1213/ane.0b013e31819a6cf0, 10.1111/j.1600-079X.2007.00528.x,
10.1007/s00415-006-0390-x, 10.1111/j.1365-2214.2006.00616.x,
10.1016/S0387-7604(03)00197-9, 10.1097/00006842-200101000-00005,
10.1111/j.1469-8749.1998.tb15445.x.
Bitte als PDF mit Textebene bereitstellen; ein reiner Scan ohne Textebene ist fuer die Auswertung nicht verwendbar.
```

Falls auch die fuenf gestrichenen Titel bestellt werden sollen, kommen diese DOIs hinzu: 10.1039/d5fo00971e, 10.1016/j.ejpn.2021.06.006, 10.1007/s00737-018-0838-x, 10.3310/hta16400, 10.1016/s0196-0644(98)70010-1.

## 6. Pruefung

| Pruefung | Ergebnis |
|---|---|
| Eintraege gesamt | 25 (5 A, 20 B) |
| eindeutige PMIDs | 25 |
| Eintraege mit DOI | 25 |
| Eintraege mit Autor und Titel | 25 |
| bestellfaehig nach Triage | 20 (5 A, 15 B) |
| gestrichen | 5 (Klasse D) |

Das Skript bricht bei Abweichung ab (`assert`). Es liest nur lokale Dateien, kein Netzaufruf, kein Modellaufruf.

## 7. Grenzen

- Die Einordnung A/B stammt aus dem Titel allein, die Triage aus den Abstracts. Beides ersetzt kein Screening am Volltext.
- Bei Crossover-Studien (20535539, 9566656, 18078449, 15275698, 11211063, 26569624) fehlt im Abstract fast immer die gepaarte Streuung. Ob eine Zeile entsteht, entscheidet der Volltext.
- 16919138 und 23098680 sind vor der Extraktion gegen S1 zu pruefen; das Dedup-Register nennt die Merkmale.
- Keine Angaben zu Gebuehren, Lieferart oder Bibliothekskonto: Das Formular erhebt sie selbst, sie lassen sich nicht aus dem Projekt ableiten.

