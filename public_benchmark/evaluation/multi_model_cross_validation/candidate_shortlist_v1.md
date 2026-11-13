# Cross-Validation: Artikelauswahl v1

Stand: 2026-11-13
Status: **selected_pending_fulltext_check**
Kein Modellaufruf, kein Netzzugriff.

## Auswahlregel

1. Nur Kandidaten mit `decision == include_for_fulltext`.
2. Ausschluss aller G5-Artikel (30 Shortlist + 36 bestaetigte Einschluesse).
3. Ausschluss aller Yun-Artikel (Freeze 275, Dev 26, Test 249).
4. Rangfolge: `sha256("crossval-20261113-v1:<PMCID>")` aufsteigend.
5. 25 Primaerartikel, 10 Reserve.

## Pruefungen

| Pruefung | Ergebnis |
|---|---|
| Primerzahl = 25 | True |
| Reservezahl = 10 | True |
| PMCIDs eindeutig | True |
| Schnittmenge mit G5 (36 Artikel) | leer |
| Schnittmenge mit Yun (70 Artikel) | leer |
| Kandidatenpool nach Ausschluss | 372 |

## Auswahltrichter

| Schritt | Artikel |
|---|---:|
| Abstract-Freigabe, ohne G5 und ohne Yun | 379 |
| davon mit RCT-Publikationstyp | 374 |
| davon ohne Zusammenfassung/Korrektur/Protokoll | 372 |

## Primaerartikel

| # | PMCID | Jahr | Journal | Titel |
|---:|---|---|---|---|
| 1 | PMC13533546 | 2026 | The international journal of n | Effects of lavender oil preparation silexan on different symptoms of major depression - re |
| 2 | PMC13587535 | 2026 | Annals of medicine | Opioid-free analgesia with esketamine-dexmedetomidine versus opioid-based analgesia after  |
| 3 | PMC13554527 | 2026 | The Journal of international m | Efficacy of a multimodal conservative rehabilitation program for bladder control in indivi |
| 4 | PMC13581780 | 2026 | Frontiers in public health | Effect of a mobile application-based whole-course nutrition management intervention in pat |
| 5 | PMC13544601 | 2026 | Experimental physiology | Physiological and autonomic responses to intermittent low-lung-volume apnoea and pain sens |
| 6 | PMC13613989 | 2026 | Psycho-oncology | Making Interventions More Effective: Changes in Theoretical Constructs During Delivery of  |
| 7 | PMC13493211 | 2026 | Diabetes | Ketone Bodies Derived From Medium-Chain Triglycerides Support Brain Metabolism and Functio |
| 8 | PMC13583812 | 2026 | BMJ open | BLIS study: a feasibility randomised controlled trial assessing compliance, acceptability  |
| 9 | PMC13682724 | 2026 | Journal of clinical oncology : | Mindfulness and Tai Chi for Sleep, Fatigue, and Pain in Distressed People After Cancer Tre |
| 10 | PMC13575558 | 2026 | Clinical cancer research : an  | Biomarker Analysis from Patients with Metastatic PDAC Treated with TGFβ Antibody NIS793 pl |
| 11 | PMC13568562 | 2026 | Gut microbes | Probiotic supplementation increases fecal TLR4 agonists without improving disease activity |
| 12 | PMC13539392 | 2026 | JAMA network open | Care Navigation for Methamphetamine Use Disorder: A Randomized Clinical Trial. |
| 13 | PMC13599780 | 2026 | Rheumatology (Oxford, England) | Subcutaneous versus intravenous ultra-low-dose rituximab in rheumatoid arthritis: a random |
| 14 | PMC13683044 | 2026 | Nature human behaviour | Effects of a randomized controlled trial of unconditional cash transfers on epigenetic mea |
| 15 | PMC13597907 | 2026 | Frontiers in public health | A health promotion behavior intervention for women with polycystic ovary syndrome experien |
| 16 | PMC13591874 | 2026 | BMC oral health | Effect of β-tricalcium phosphate grafting on implant stability and peri-implant radiodensi |
| 17 | PMC13553157 | 2026 | Nursing in critical care | The Effect of Personalised Feedback in Simulation on Knowledge and Skills in the Managemen |
| 18 | PMC13587653 | 2026 | European journal of pain (Lond | To Ask or Not to Ask: Does Inquiring About Participants' Expectations Influence the Placeb |
| 19 | PMC13724892 | 2026 | The Journal of international m | Effects of resistant starch on blood pressure and autonomic function in women with the ris |
| 20 | PMC13610706 | 2026 | Nutrients | Prenatal Folinic Acid in FRAA-Positive Pregnancies: Preschool Neurodevelopmental Outcomes  |
| 21 | PMC13645219 | 2026 | PLoS neglected tropical diseas | High-dose rifampicin and clarithromycin for 4 weeks versus standard-dose rifampicin and cl |
| 22 | PMC13556510 | 2026 | Japanese journal of clinical o | A multicenter randomized phase II/III trial of salvage treatment for refractory primary ce |
| 23 | PMC13632637 | 2026 | Drug design, development and t | Effects of Ciprofol- versus Remimazolam-Based Total Intravenous Anesthesia on Postoperativ |
| 24 | PMC13729219 | 2026 | Microbiology spectrum | Effect of denture and soft tissue disinfection on edentulous biofilms. |
| 25 | PMC13601125 | 2026 | International archives of occu | Improving adaptation in male high-altitude workers through pressurization: a randomized co |

## Reserve (vorab bestimmt)

| # | PMCID | Jahr | Journal | Titel |
|---:|---|---|---|---|
| 26 | PMC13560212 | 2026 | BMC health services research | Process evaluation of a nurse-led transitional care model (Cardiolotse) within a randomize |
| 27 | PMC13624021 | 2026 | European journal of pediatrics | Oral glucose solution for the treatment of persistent asymptomatic neonatal hypoglycemia:  |
| 28 | PMC13610065 | 2026 | Nutrients | Plasma and Brain-Derived Extracellular Vesicle Biomarkers Following a Randomized Controlle |
| 29 | PMC13593208 | 2026 | European heart journal | Cardiac resynchronization therapy with or without atrioventricular node ablation in atrial |
| 30 | PMC13577647 | 2026 | The journal of extra-corporeal | Impact of adenosine in controlled aortic root reperfusion on clinical outcomes among patie |
| 31 | PMC13632614 | 2026 | Clinical interventions in agin | Endovascular Treatment for Patients Aged ≥80 Years with Large Ischemic Stroke. |
| 32 | PMC13607715 | 2026 | International journal of molec | Biomarker Detection of Lung Cancers Before Clinical Symptoms or the Use of Traditional Ima |
| 33 | PMC13609332 | 2026 | Medicina (Kaunas, Lithuania) | A Comparison of 18-Gauge and 20-Gauge Short Peripheral Catheters in Terms of Pain and Proc |
| 34 | PMC13535982 | 2026 | Clinical cardiology | Angiography-Based Index of Microcirculatory Resistance in Assessing the MVO and Infarct Si |
| 35 | PMC13578717 | 2026 | Scientific reports | A prospective randomized controlled pilot study of gut microbiome modulation by Nigella sa |

## Offen nach diesem Schritt

- Volltextpruefung: liefert jeder Artikel tatsaechlich Armwerte fuer
  mindestens einen Vergleich? Die Auswahl ist eine Kandidatenliste,
  keine Einschlussentscheidung.
- Recordzahl feststellen; bei unter 60 Records Reserve nachziehen,
  bei weiterhin zu wenig ein zweites Artikelkontingent ziehen.
- Annotation durch unabhaengige Personen (F2), danach Einfrieren.
- Kein Modellaufruf vor `freeze.json`.
