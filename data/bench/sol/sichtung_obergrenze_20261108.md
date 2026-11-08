# Sichtungsliste: Obergrenze der SOL-Kandidaten

Stand: 2026-11-08T12:29:00. Seed `20261108`. Erzeugt von `scripts/sample_sol_candidates.py`.

## Wozu diese Liste

Die Obergrenze aus Paket A fragt: Wie viele der 946 SOL-Kandidaten enthalten ueberhaupt einen poolbaren SOL-Effekt (Melatonin gegen Placebo, Mittelwert plus Streuung je Arm)? Ohne diese Zahl laesst sich ein verlorener Effekt nicht als legitim oder als Leserdefekt einordnen.

## Auswahl

| Stratum | Bedeutung | Umfang | Auswahl |
|---|---|---:|---|
| A | poolbare SOL-Zeile gespeichert (Intervention ungeprueft) | 9 | Zensus |
| B | SOL-Zeile gespeichert, nicht poolbar | 1 | Zensus |
| C | Effektzeilen ohne SOL-Label | 40 | Zensus |
| D | Titel nennt Einschaflatenz | 7 | Zensus |
| E | Rest der SOL-Kandidaten | 889 | Zufall, 60 von 889 |
| X | Nicht-Kandidaten (Fehlerprobe) | 110 | Zufall, 30 von 110 |

## Hochrechnung

- Zensus: 57 Dokumente (A-D), davon 9 mit einer poolbaren SOL-Zeile.
- Engere Frage (Melatonin gegen Placebo): 1 dieser Dokumente nennt Melatonin schon im Titel. Der Zensus belegt nur, dass eine poolbare SOL-Zeile existiert, nicht fuer welche Intervention - das entscheidet die Sichtung.
- Rest: 889 Dokumente, davon 60 gesichtet.
- Einseitige 95-%-Obergrenze der Praevalenz bei 0 Treffern in der Stichprobe: **4.9 %**.
- Daraus die Obergrenze fuer den ganzen Korpus: **49.4 Dokumente mit poolbarer SOL-Zeile** (Zensus-Treffer plus Obergrenze fuer den Rest).

Die Zahl ist eine Obergrenze, keine Schaetzung: sie gilt, wenn in der gesichteten Stichprobe kein weiterer poolbarer Effekt gefunden wird. Jeder Treffer erhoeht den Zensus und senkt den unsicheren Rest.

## Sichtungsanleitung

1. Dokument oeffnen (PMC-ID bei Europe PMC oder NCBI; XML liegt, wo vorhanden, unter `data/bench/sol/xml/`).
2. Ergebnistabellen ansehen, nicht den Abstract: gesucht ist eine Zeile mit Einschaflatenz (SOL) oder Schlafbeginn, Mittelwert und Streuung (SD oder SE) je Arm, Interventionsarm Melatonin gegen Placebo.
3. Urteil vergeben: `poolbar` (Armdaten vorhanden), `nur Baseline` (Wert ist Tag 0 oder vor Intervention), `kein SOL` (anderes Zielmass), `kein RCT` (Review, Beobachtung), `kein Volltext` (Zugang fehlt).
4. Treffer sofort in die Mess-DB aufnehmen, damit der Zensus waechst.
5. Nach 20 `nein` in Folge in Stratum E darf die Sichtung dort enden - das ist die Abbruchregel; sie wird im Protokoll vermerkt.

## Arbeitsliste

### Stratum A - poolbare SOL-Zeile gespeichert (Intervention ungeprueft) (9)

| # | PMC | Jahr | Titel | Zeilen | SOL-Zeilen | poolbar | gelesen | Urteil |
|---:|---|---:|---|---:|---:|---:|---|---|
| 1 | PMC11256039 | 2024 | Evening regular activity breaks extend subsequent free-living sleep time in healthy adults | 18 | 2 | 2 | ja | |
| 2 | PMC11893541 | 2025 | A replicate crossover trial on the interindividual variability of sleep indices in respons | 12 | 3 | 3 | ja | |
| 3 | PMC13265460 | 2026 | Efficacy of repetitive transcranial magnetic stimulation for insomnia disorder: a systemat | 17 | 1 | 1 | ja | |
| 4 | PMC13357889 | 2026 | The Effect of 6 Months of Dietary Counselling on Sleep Outcomes Among Patients With Cardio | 16 | 4 | 4 | ja | |
| 5 | PMC13448793 | 2026 | Melatonin Use and Polysomnographic Sleep Architecture in Children. | 15 | 1 | 1 | ja | |
| 6 | PMC4517991 | 2015 | Comparisons of Objective Sleep Quality Between Elderly Individuals With and Without Catara | 12 | 4 | 4 | ja | |
| 7 | PMC7381312 | 2020 | Efficacy of Tasimelteon (HETLIOZ®) in the Treatment of Jet Lag Disorder Evaluated in an 8- | 14 | 1 | 1 | ja | |
| 8 | PMC7953207 | 2021 | The evening light environment in hospitals can be designed to produce less disruptive effe | 9 | 2 | 2 | ja | |
| 9 | PMC9570822 | 2022 | Cognitive Behavioral Therapy for Chronic Insomnia in Outpatients with Major Depression-A R | 46 | 4 | 4 | ja | |

### Stratum B - SOL-Zeile gespeichert, nicht poolbar (1)

| # | PMC | Jahr | Titel | Zeilen | SOL-Zeilen | poolbar | gelesen | Urteil |
|---:|---|---:|---|---:|---:|---:|---|---|
| 1 | PMC11302522 | 2024 | Washed Microbiota Transplantation Improves the Sleep Quality in Patients with Inflammatory | 5 | 1 | 0 | ja | |

### Stratum C - Effektzeilen ohne SOL-Label (40)

| # | PMC | Jahr | Titel | Zeilen | SOL-Zeilen | poolbar | gelesen | Urteil |
|---:|---|---:|---|---:|---:|---:|---|---|
| 1 | PMC10255271 | 2023 | Hypomagnesemia Is Associated with Excessive Daytime Sleepiness, but Not Insomnia, in Older | 19 | 0 | 0 | ja | |
| 2 | PMC10621812 | 2023 | Associations between sleep habits, quality, chronotype and depression in a large cross-sec | 16 | 0 | 0 | ja | |
| 3 | PMC10629458 | 2023 | Association Between Hypnotic Use and All-Cause Mortality in Patients with Chronic Obstruct | 2 | 0 | 0 | ja | |
| 4 | PMC11414779 | 2024 | Improving sleep after stroke: A randomised controlled trial of digital cognitive behaviour | 8 | 0 | 0 | ja | |
| 5 | PMC11557329 | 2024 | Efficacy of non-invasive brain stimulation for post-stroke sleep disorders: a systematic r | 25 | 0 | 0 | ja | |
| 6 | PMC11850413 | 2025 | Effects of a daylight intervention in the morning on circadian rhythms and sleep in geriat | 4 | 0 | 0 | ja | |
| 7 | PMC11884929 | 2025 | Effectiveness of Acupressure on Sleep Quality Among Inpatients: A Systematic Review and Me | 15 | 0 | 0 | ja | |
| 8 | PMC11976827 | 2025 | Association between sleep characteristics and physical functioning in middle-aged and elde | 194 | 0 | 0 | ja | |
| 9 | PMC12013145 | 2025 | Association between fish consumption and sleep disorders among Chinese adults: a cross-sec | 104 | 0 | 0 | ja | |
| 10 | PMC12198936 | 2025 | Advancing adolescent bedtime by motivational interviewing and text message: a randomized c | 15 | 0 | 0 | ja | |
| 11 | PMC12276649 | 2025 | Acupuncture versus sham acupuncture in the treatment of insomnia for patients with Parkins | 24 | 0 | 0 | ja | |
| 12 | PMC12412596 | 2025 | Magnesium Bisglycinate Supplementation in Healthy Adults Reporting Poor Sleep: A Randomize | 12 | 0 | 0 | ja | |
| 13 | PMC12488620 | 2025 | Five-element music therapy based on emotion classification to improve sleep in patients wi | 16 | 0 | 0 | ja | |
| 14 | PMC12511177 | 2025 | Efficacy and safety of lemborexant vs placebo in treating adults with insomnia disorder: a | 12 | 0 | 0 | ja | |
| 15 | PMC12642372 | 2025 | Effects of kefir on symptoms, sleep, and gut microbiota in children with ADHD: a randomise | 4 | 0 | 0 | ja | |
| 16 | PMC12787598 | 2025 | Heat-Treated &lt;i&gt;Limosilactobacillus fermentum&lt;/i&gt; PS150 Improves Sleep Quality | 17 | 0 | 0 | ja | |
| 17 | PMC13013474 | 2026 | Knowledge, attitude and practice regarding insomnia prevention and treatment among medical | 21 | 0 | 0 | ja | |
| 18 | PMC13033741 | 2025 | Improved executive function and sleep quality in preteens with high-functioning autism fol | 1 | 0 | 0 | ja | |
| 19 | PMC13101811 | 2026 | Factors Affecting Sleep Quality in Pregnant Women During the Second Trimester and Its Asso | 26 | 0 | 0 | ja | |
| 20 | PMC13155930 | 2024 | Association of Evening Eating with Sleep Quality and Insomnia among Adults in a Brazilian  | 72 | 0 | 0 | ja | |
| 21 | PMC13199057 | 2026 | Effects of inhaled aromatherapy on sleep quality and cognitive function in older adults: a | 3 | 0 | 0 | ja | |
| 22 | PMC13269014 | 2026 | The impact of cognitive behavioral therapy for insomnia on cognitive performance and amylo | 1 | 0 | 0 | ja | |
| 23 | PMC13512466 | 2026 | Association of Domain-Specific Physical Activity with Sleep Disorders in U.S. Adults: A Cr | 12 | 0 | 0 | ja | |
| 24 | PMC13583673 | 2026 | Effect of traditional Chinese medicine on sleep and blood pressure in patients with comorb | 12 | 0 | 0 | ja | |
| 25 | PMC2901361 | 2010 | A dietary supplement to improve the quality of sleep: a randomized placebo controlled tria | 4 | 0 | 0 | ja | |
| 26 | PMC3489506 | 2012 | Melatonin for sleep problems in children with neurodevelopmental disorders: randomised dou | 16 | 0 | 0 | ja | |
| 27 | PMC4539464 | 2015 | Clinical Efficacy of Traditional Chinese Medicine, Suan Zao Ren Tang, for Sleep Disturbanc | 8 | 0 | 0 | ja | |
| 28 | PMC6005466 | 2018 | Efficacy of melatonin with behavioural sleep-wake scheduling for delayed sleep-wake phase  | 2 | 0 | 0 | ja | |
| 29 | PMC6276665 | 2017 | The impact of melatonin on the sleep patterns of women undergoing IVF: a double blind RCT. | 6 | 0 | 0 | ja | |
| 30 | PMC6482403 | 2019 | Effectiveness of Internet-Delivered Computerized Cognitive Behavioral Therapy for Patients | 28 | 0 | 0 | ja | |
| 31 | PMC6593378 | 2019 | Diet quality, consumption of seafood and eggs are associated with sleep quality among Chin | 34 | 0 | 0 | ja | |
| 32 | PMC6763980 | 2019 | Effect of Light Flashes vs Sham Therapy During Sleep With Adjunct Cognitive Behavioral The | 11 | 0 | 0 | ja | |
| 33 | PMC6835535 | 2019 | Association between Macronutrient Intake and Excessive Daytime Sleepiness: An Iso-Caloric  | 126 | 0 | 0 | ja | |
| 34 | PMC7111581 | 2020 | Practical Evaluation and Management of Insomnia in Parkinson's Disease: A Review. | 2 | 0 | 0 | ja | |
| 35 | PMC7181488 | 2020 | Associations of bedtime, sleep duration, and sleep quality with semen quality in males see | 14 | 0 | 0 | ja | |
| 36 | PMC7462016 | 2020 | Blue-Enriched White Light Improves Performance but Not Subjective Alertness and Circadian  | 1 | 0 | 0 | ja | |
| 37 | PMC8215288 | 2021 | Effects of Exercise on Sleep Quality and Insomnia in Adults: A Systematic Review and Meta- | 8 | 0 | 0 | ja | |
| 38 | PMC8364763 | 2021 | Meta-analysis of differences in sleep quality based on actigraphs between day and night sh | 4 | 0 | 0 | ja | |
| 39 | PMC8567000 | 2021 | No improvement of sleep from vitamin D supplementation: insights from a randomized control | 27 | 0 | 0 | ja | |
| 40 | PMC8797219 | 2022 | A randomized controlled trial on the effects of blue-blocking glasses compared to partial  | 3 | 0 | 0 | ja | |

### Stratum D - Titel nennt Einschaflatenz (7)

| # | PMC | Jahr | Titel | Zeilen | SOL-Zeilen | poolbar | gelesen | Urteil |
|---:|---|---:|---|---:|---:|---:|---|---|
| 1 | PMC11537953 | 2024 | A randomized study on the effect of a wearable device using 0.75 Hz transcranial electrica | 0 | 0 | 0 | ja | |
| 2 | PMC11848184 | 2025 | Association of rapid eye movement sleep latency with multimodal biomarkers of Alzheimer's  | 0 | 0 | 0 | ja | |
| 3 | PMC12392164 | 2025 | The optimal system of care for the management of delayed sleep onset in adult ADHD in the  | 0 | 0 | 0 | ja | |
| 4 | PMC2952772 | 2010 | Dose finding of melatonin for chronic idiopathic childhood sleep onset insomnia: an RCT. | 0 | 0 | 0 | ja | |
| 5 | PMC3111733 | 2011 | Evaluation of sleep, puberty and mental health in children with long-term melatonin treatm | 0 | 0 | 0 | ja | |
| 6 | PMC4274876 | 2014 | Differential effects of theta/beta and SMR neurofeedback in ADHD on sleep onset latency. | 0 | 0 | 0 | ja | |
| 7 | PMC6243118 | 2018 | Complexity of Wake Electroencephalography Correlates With Slow Wave Activity After Sleep O | 0 | 0 | 0 | ja | |

### Stratum E - Rest der SOL-Kandidaten (60)

| # | PMC | Jahr | Titel | Zeilen | SOL-Zeilen | poolbar | gelesen | Urteil |
|---:|---|---:|---|---:|---:|---:|---|---|
| 1 | PMC10123665 | 2023 | Traumatic Brain Injury, Sleep, and Melatonin-Intrinsic Changes with Therapeutic Potential. | 0 | 0 | 0 | ja | |
| 2 | PMC10534299 | 2023 | Melatonin Use in Pediatric Intensive Care Units: A Single-Center Experience. | 0 | 0 | 0 | ja | |
| 3 | PMC11005158 | 2024 | Effects of cognitive behavioural therapy and bright light therapy for insomnia in youths w | 0 | 0 | 0 | ja | |
| 4 | PMC11136869 | 2024 | Examining the Effects of Supplemental Magnesium on Self-Reported Anxiety and Sleep Quality | 0 | 0 | 0 | ja | |
| 5 | PMC11188797 | 2024 | Interventions for insomnia in cancer patients and survivors-a comprehensive systematic rev | 0 | 0 | 0 | ja | |
| 6 | PMC11201524 | 2024 | Sex Differences in Children with Uncomplicated Attention Deficit/Hyperactivity Disorder an | 0 | 0 | 0 | ja | |
| 7 | PMC11265033 | 2024 | A clinical-translational review of sleep problems in neurodevelopmental disabilities. | 0 | 0 | 0 | ja | |
| 8 | PMC11292074 | 2024 | The role of arousal in maintaining the relationship between insomnia and gastrointestinal  | 0 | 0 | 0 | ja | |
| 9 | PMC11353953 | 2024 | Comprehensive Review of Chronic Stress Pathways and the Efficacy of Behavioral Stress Redu | 0 | 0 | 0 | ja | |
| 10 | PMC11512775 | 2024 | Sleep Habits and Disturbances in Healthcare Workers: A Cross-Sectional Survey in French Pu | 0 | 0 | 0 | ja | |
| 11 | PMC12006942 | 2025 | Protocol MelatoSom-Kids-PTSD: sleep disturbances in children and adolescents with post-tra | 0 | 0 | 0 | ja | |
| 12 | PMC12020265 | 2025 | Acupoint massage: a comprehensive descriptive review of its forms, applications, and under | 0 | 0 | 0 | ja | |
| 13 | PMC12112657 | 2025 | Expert Consensus on the Use of Diphenhydramine for Short-Term Insomnia: Efficacy, Safety,  | 0 | 0 | 0 | ja | |
| 14 | PMC12166720 | 2025 | The prognosis of patients with myocardial infarction after light therapy: A preliminary st | 0 | 0 | 0 | ja | |
| 15 | PMC12474699 | 2025 | Pathophysiological Insights and Multimodal Interventions in Chronic Tinnitus, Anxiety, and | 0 | 0 | 0 | ja | |
| 16 | PMC12523188 | 2025 | BioClock-optimizing Bright Light Therapy for adults with depression: a study protocol for  | 0 | 0 | 0 | ja | |
| 17 | PMC12678987 | 2025 | Optimizing Sleep in Athletes: The Potential of α-Lactalbumin in Nutrition Intervention. | 0 | 0 | 0 | ja | |
| 18 | PMC12745477 | 2025 | Exploring the mediating role of meaning in life and psychological resilience in the relati | 0 | 0 | 0 | ja | |
| 19 | PMC12839077 | 2026 | Circadian Clock Genes in Colorectal Cancer: From Molecular Mechanisms to Chronotherapeutic | 0 | 0 | 0 | ja | |
| 20 | PMC12847286 | 2025 | Effects of music on post-stroke sleep disorders and treatment perspectives: review and nar | 0 | 0 | 0 | ja | |
| 21 | PMC12856098 | 2026 | Physical Activity as a Tool to Improve Sleep Quality for Secure Psychiatric Inpatients: A  | 0 | 0 | 0 | ja | |
| 22 | PMC12909313 | 2026 | A 12-Week, Open-Label, Multicenter Pilot Study to Evaluate the Efficacy and Safety of Lemb | 0 | 0 | 0 | ja | |
| 23 | PMC12938722 | 2026 | Circadian Rhythm and Sleep Disturbances in Young Adult Athletes: A Review About Risk Facto | 0 | 0 | 0 | ja | |
| 24 | PMC12958652 | 2026 | Social networking site use, depressive and anxiety symptoms in adolescents: evidence from  | 0 | 0 | 0 | ja | |
| 25 | PMC12999190 | 2026 | Effectiveness of Adaptive Digital Interventions Triggered by Passive Sensing for Sleep Imp | 0 | 0 | 0 | ja | |
| 26 | PMC13091462 | 2026 | Influenza vaccine response is predicted by chronotype and differentially associated with p | 0 | 0 | 0 | ja | |
| 27 | PMC13108063 | 2026 | Comparative Evaluation of Ashwagandha (&lt;i&gt;Withania somnifera&lt;/i&gt;) Root Extract | 0 | 0 | 0 | ja | |
| 28 | PMC13176156 | 2026 | Digital treatment for insomnia in adolescents: study protocol for a randomized controlled  | 0 | 0 | 0 | ja | |
| 29 | PMC13227767 | 2026 | Effects of bright light therapy on cognition, sleep and psychological stress in older adul | 0 | 0 | 0 | ja | |
| 30 | PMC13254761 | 2026 | Non-invasive electrical stimulation for sleep disturbances in adults: protocol for an evid | 0 | 0 | 0 | ja | |
| 31 | PMC13263438 | 2026 | Correlation between sleep problems and physical activity in children with autism spectrum  | 0 | 0 | 0 | ja | |
| 32 | PMC13570694 | 2026 | Efficacy of an Oral Melatonin Suspension in Idiopathic Nocturnal Irritability among Infant | 0 | 0 | 0 | ja | |
| 33 | PMC13705235 | 2026 | Salivary Melatonin Levels in Comparison with Disease Features and Antihistamine Use: Prosp | 0 | 0 | 0 | ja | |
| 34 | PMC3610349 | 2013 | Melatonin supplementation in patients with complete tetraplegia and poor sleep. | 0 | 0 | 0 | ja | |
| 35 | PMC3630934 | 2010 | New approaches in the treatment of short term and middle of the night insomnia: emerging e | 0 | 0 | 0 | ja | |
| 36 | PMC3630941 | 2010 | Management of insomnia: update and new approaches. | 0 | 0 | 0 | ja | |
| 37 | PMC3710611 | 2013 | Efficacy and safety of acupuncture in preterm and term infants. | 0 | 0 | 0 | ja | |
| 38 | PMC4502736 | 2015 | A Preliminary Study of the Effects of SurAsleep on Relieving Symptoms of Sleep Disorders. | 0 | 0 | 0 | ja | |
| 39 | PMC5741691 | 2017 | Non-24-Hour Sleep-Wake Rhythm Disorder in the Totally Blind: Diagnosis and Management. | 0 | 0 | 0 | ja | |
| 40 | PMC6164454 | 2018 | Insomnia in Adolescence. | 0 | 0 | 0 | ja | |
| 41 | PMC6316321 | 2018 | The Benefits of Closed-Loop Transcranial Alternating Current Stimulation on Subjective Sle | 0 | 0 | 0 | ja | |
| 42 | PMC6478829 | 2019 | Psychological Sleep Interventions for Migraine and Tension-Type Headache: A Systematic Rev | 0 | 0 | 0 | ja | |
| 43 | PMC7432549 | 2020 | Does Sars-Cov-2 threaten our dreams? Effect of quarantine on sleep quality and body mass i | 0 | 0 | 0 | ja | |
| 44 | PMC7437697 | 2020 | Does Fibre-fix provided to people with irritable bowel syndrome who are consuming a low FO | 0 | 0 | 0 | ja | |
| 45 | PMC7901882 | 2021 | Daily Morning Blue Light Therapy for Post-mTBI Sleep Disruption: Effects on Brain Structur | 0 | 0 | 0 | ja | |
| 46 | PMC8077706 | 2021 | Does the guided online cognitive behavioral therapy for insomnia "i-Sleep youth" improve s | 0 | 0 | 0 | ja | |
| 47 | PMC8150598 | 2021 | Nutritional Interventions to Improve Sleep in Team-Sport Athletes: A Narrative Review. | 0 | 0 | 0 | ja | |
| 48 | PMC8273250 | 2021 | Effects of Supplementation With Antioxidant Agents on Sleep in Autism Spectrum Disorder: A | 0 | 0 | 0 | ja | |
| 49 | PMC8354724 | 2021 | Advances in the Treatment of Chronic Insomnia: A Narrative Review of New Nonpharmacologic  | 0 | 0 | 0 | ja | |
| 50 | PMC8593056 | 2021 | Impact of Pharmacotherapy on Insomnia in Patients with Alzheimer's Disease. | 0 | 0 | 0 | ja | |
| 51 | PMC8700927 | 2021 | Parents' Experiences of Weighted Blankets' Impact on Children with Attention-Deficit/Hyper | 0 | 0 | 0 | ja | |
| 52 | PMC8889980 | 2022 | Sleep-wake circadian rhythm pattern in young adults by actigraphy during social isolation. | 0 | 0 | 0 | ja | |
| 53 | PMC8987601 | 2022 | Efficacy and safety of lemborexant over 12 months in Asian adults with insomnia disorder. | 0 | 0 | 0 | ja | |
| 54 | PMC9124464 | 2022 | Is There a Place for Medicinal Cannabis in Treating Patients with Sleep Disorders? What We | 0 | 0 | 0 | ja | |
| 55 | PMC9219335 | 2020 | Sleep and stress in the acute phase of concussion in youth. | 0 | 0 | 0 | ja | |
| 56 | PMC9251053 | 2022 | Trends in Prescriptions for Insomnia in a Province in China Between 2015 and 2019. | 0 | 0 | 0 | ja | |
| 57 | PMC9554245 | 2022 | Repetitive transcranial magnetic stimulation for insomnia in patients with autism spectrum | 0 | 0 | 0 | ja | |
| 58 | PMC9650229 | 2022 | Circadian disruption and cancer- and treatment-related symptoms. | 0 | 0 | 0 | ja | |
| 59 | PMC9897137 | 2018 | What do Cochrane systematic reviews say about interventions for insomnia? | 0 | 0 | 0 | ja | |
| 60 | PMC9902977 | 2023 | &lt;i&gt;Light on Shedding&lt;/i&gt;: A Review of Sex and Menstrual Cycle Differences in t | 0 | 0 | 0 | ja | |

### Stratum X - Nicht-Kandidaten (Fehlerprobe) (30)

| # | PMC | Jahr | Titel | Zeilen | SOL-Zeilen | poolbar | gelesen | Urteil |
|---:|---|---:|---|---:|---:|---:|---|---|
| 1 | PMC10001099 | 2023 | Chronic Insomnia Disorder across Europe: Expert Opinion on Challenges and Opportunities to | 0 | 0 | 0 | ja | |
| 2 | PMC10109150 | 2021 | O029 Predictors of acute insomnia during the COVID-19 pandemic beyond perceived stress | 0 | 0 | 0 | ja | |
| 3 | PMC10109439 | 2021 | O028 Effectiveness of digital brief behavioural therapy for insomnia with wearable technol | 0 | 0 | 0 | ja | |
| 4 | PMC10399894 | 2023 | Effects of nature-adapted lighting solutions ("Virtual Sky") on subjective and objective c | 0 | 0 | 0 | ja | |
| 5 | PMC11099861 | 2023 | Effect of yoga-based exercises on functional capacity, dyspnea, quality of life, depressio | 0 | 0 | 0 | ja | |
| 6 | PMC11815106 | 2025 | CLINICAL EPIDEMIOLOGY OF THE EFFECT OF NOVEL HYPNOTICS ON PRESCRIBING CHANGES IN PATIENTS  | 0 | 0 | 0 | ja | |
| 7 | PMC11852718 | 2025 | The Role of Oxidative Stress in Autism Spectrum Disorder Pathophysiology, Diagnosis and Tr | 0 | 0 | 0 | ja | |
| 8 | PMC12109102 | 2025 | Juvenile Primary Fibromyalgia Syndrome: Advances in Etiopathogenesis, Clinical Assessment  | 0 | 0 | 0 | ja | |
| 9 | PMC12403384 | 2025 | Effects of programs on sleep improvement in shift-work nurses: a systematic review and met | 0 | 0 | 0 | ja | |
| 10 | PMC12695116 | 2025 | Cannabinoids for Anxiety and Sleep Disturbances: A Scoping Review. | 0 | 0 | 0 | ja | |
| 11 | PMC13085561 | 2026 | Sleep, rest-activity rhythm, cognitive and emotional symptoms in adult ADHD: unraveling th | 0 | 0 | 0 | ja | |
| 12 | PMC13397976 | 2026 | Mechanisms of Heat-Induced Sleep Disruption in Aging: A Narrative Review. | 0 | 0 | 0 | ja | |
| 13 | PMC13441412 | 2026 | Sleep Disturbance and Atopic Dermatitis: A Bidirectional Relationship With Clinical and Th | 0 | 0 | 0 | ja | |
| 14 | PMC13628168 | 2026 | The bidirectional relationship between epilepsy and sleep: a narrative review. | 0 | 0 | 0 | ja | |
| 15 | PMC13723161 | 2026 | The Cutaneous Melatoninergic System: Endogenous Biology and Potential for Therapeutic Targ | 0 | 0 | 0 | ja | |
| 16 | PMC3852502 | 2013 | Self-reported sleep disturbances in renal transplant recipients. | 0 | 0 | 0 | ja | |
| 17 | PMC4008810 | 2014 | Sleep in elite athletes and nutritional interventions to enhance sleep. | 0 | 0 | 0 | ja | |
| 18 | PMC4813276 | 2016 | Nocturnal Pruritus: The Battle for a Peaceful Night's Sleep. | 0 | 0 | 0 | ja | |
| 19 | PMC5905517 | 2018 | Abstracts for the Sixth Biennial SIRS Conference | 0 | 0 | 0 | ja | |
| 20 | PMC6707934 | 2019 | Impact of traumatic brain injury on sleep: an overview. | 0 | 0 | 0 | ja | |
| 21 | PMC7027846 | 2020 | Melatonin for rapid eye movement sleep behavior disorder in Parkinson's disease: A randomi | 0 | 0 | 0 | ja | |
| 22 | PMC7722668 | 2020 | Current and potential pharmacological treatment options for insomnia in patients with alco | 0 | 0 | 0 | ja | |
| 23 | PMC7905198 | 2021 | Behavioral and exercise interventions for sleep dysfunction in the elderly: a brief review | 0 | 0 | 0 | ja | |
| 24 | PMC8465965 | 2021 | A Systematic Review on the Contribution of Artificial Intelligence in the Development of M | 0 | 0 | 0 | ja | |
| 25 | PMC8567713 | 2021 | Efficacy of the acupressure wrist-ankle strap in mild insomnia patients with anxiety disor | 0 | 0 | 0 | ja | |
| 26 | PMC8604464 | 2021 | Dermatology for the internist: optimal diagnosis and management of atopic dermatitis. | 0 | 0 | 0 | ja | |
| 27 | PMC8701940 | 2021 | Objective Assessment of Sleep Patterns among Night-Shift Workers: A Scoping Review. | 0 | 0 | 0 | ja | |
| 28 | PMC8911317 | 2022 | Blue Light Blocking Treatment for the Treatment of Bipolar Disorder: Directions for Resear | 0 | 0 | 0 | ja | |
| 29 | PMC9952101 | 2023 | Neuroprotective Effect of Melatonin on Sleep Disorders Associated with Parkinson's Disease | 0 | 0 | 0 | ja | |
| 30 | PMC9969269 | 2023 | Mechanism of action and promising clinical application of melatonin from a dermatological  | 0 | 0 | 0 | ja | |

## Belege

- `sichtung_obergrenze_20261108.json` - dieselbe Auswahl maschinenlesbar.
- `funnel_label2_20261108.json` - Kandidatenmenge (946 von 1.056 Dokumenten).
- `manifest_all.json` - PMC, DOI, Titel, Jahr je Dokument.
- Mess-DBs `direct_label2.db`, `arm_label2.db`, `text_arms.db`, `change_arms.db` - gespeicherte Zeilen und SOL-Labels.
