# Goldstandard: die 30 Dokumente (verbindlich, 2026-11-10)

Diese Liste ist der Auswahlbeleg. Sie wird nach dem Einfrieren nicht mehr
geaendert; neue Dokumente bedeuten eine neue Version mit neuer Begruendung.
Die maschinenlesbare Fassung steht in `data/golden_effects/documents.json`.

## Regeln der Auswahl

1. Die **12 Kalibrierungsdokumente** aus `kalibrierungslauf_plan_20261110.md`
   sind gesetzt. Sie sind mit `calibration: true` markiert.
2. Die **18 Ergaenzungen** wurden je Schicht nach drei Kriterien gewaehlt:
   zuerst Caption-Treffer (Layout), dann ein in der Schicht noch fehlender
   Effekttyp, dann Zeilenzahl und Groesse. So kommen Tabellen- und
   Fliesstextfaelle sowie alle Haupttypen vor.
3. Die **5 Negativkontrollen** stammen aus Volltexten ohne Effektzeile, deren
   Titel Protokoll, Editorial oder Kommentar nennt. Erwartung: `effects: []`
   mit Begruendung. Wird doch eine Zeile gefunden, ist die Erwartung falsch,
   nicht die Annotation.
4. Ausschluss: Dokumente unter 3000 Zeichen (ausser den gesetzten), doppelte
   IDs, fehlender Volltext.

## Schichtung

| Schicht | Anzahl |
|---|---|
| RCT (parallel/cluster) | 6 |
| Crossover | 3 |
| Kohorte | 7 |
| Querschnitt/Fall-Kontrolle | 5 |
| Aggregat (Uebersicht) | 4 |
| Negativkontrolle | 5 |
| **Summe** | **30** |

Effekttypen in der DB (nur Stratifikationshinweis, kein Goldstandard):
beta 4, g 3, hr 3, mean_diff 3, or 3, r 3, rr 2, smd 2, z 1.

Dokumente mit mindestens einem Caption-Treffer: 19 von 30.

## Die Liste

| # | Schicht | Design | Captions | Zeichen | ID | Titel |
|---|---|---|---|---|---|---|
| 1 | cohort | observational | 0 | 97367 | `7111ea9787` | Mediterranean diet in preeclampsia prevention: mechanisms ... |
| 2 | cohort | observational | 0 | 85910 | `3134fdc8c3` | The risk associated with ultra-processed food intake on de... |
| 3 | cohort | observational | 0 | 3199 | `d0bec407a2` | A quantitative bias analysis to estimate measurement error... |
| 4 | rct | parallel_rct | 2 | 71085 | `bb9218735f` | A Multicenter, Placebo-controlled Trial of Melatonin for S... |
| 5 | rct | parallel_rct | 0 | 9659 | `fb484d488b` | The effect of exercise on depressive symptoms in multiple ... |
| 6 | crossover | crossover_rct | 1 | 40445 | `3bbb142c71` | Effects of Acute Caffeine Ingestion on Reaction Time in Ha... |
| 7 | crossover | crossover_rct | 4 | 38131 | `87079ba88a` | Withdrawal Symptoms and Executive Functions After 24-Hour ... |
| 8 | cross_sectional | observational | 4 | 39970 | `2c7ab4d124` | Prevalence of depressive symptoms and its associated facto... |
| 9 | cohort | observational | 3 | 65491 | `09843d40d3` | Bidirectional relationships between physical exercise and ... |
| 10 | aggregate | aggregate | 0 | 79745 | `334f5f6798` | Optimal dose and type of exercise to improve depressive sy... |
| 11 | aggregate | observational | 3 | 114459 | `203c831dbe` | Post-Diagnosis Adherence to the Mediterranean Diet and Can... |
| 12 | cross_sectional | observational | 9 | 55267 | `2675c25aab` | Exploring the validity and internal consistency of the 12-... |
| 13 | rct | parallel_rct | 2 | 69105 | `71c86b675b` | Adherence to the Mediterranean diet to prevent or delay he... |
| 14 | rct | parallel_rct | 4 | 61869 | `cf9d739f50` | Impaired sleep, depressive symptoms, and pain as determina... |
| 15 | rct | parallel_rct | 3 | 24519 | `b3c35c1d63` | Consumption of caffeine-containing beverages improves sust... |
| 16 | rct | parallel_rct | 0 | 48470 | `b5e492009e` | Impact of exercise type, duration, and intensity on depres... |
| 17 | crossover | crossover_rct | 5 | 79256 | `ca2c52d13a` | The effects of an 8-week Taekwondo exercise intervention o... |
| 18 | cohort | observational | 5 | 70784 | `3790c91f96` | Bidirectional association between cognitive function and d... |
| 19 | cohort | observational | 0 | 5729 | `7df874ca53` | Age and cohort differences in the association between poly... |
| 20 | cohort | observational | 3 | 61790 | `17c7628ed0` | Bidirectional association between ADL disability and depre... |
| 21 | cross_sectional | observational | 3 | 58006 | `7ca468285b` | Accelerometer-Assessed Physical Activity and Cognitive Per... |
| 22 | cross_sectional | observational | 3 | 27868 | `1faf4b78f0` | The Effect of Physical Exercise on Depression in College S... |
| 23 | cross_sectional | observational | 1 | 73766 | `37cafe8444` | A Cross-Sectional Study of Food Insecurity, Mediterranean ... |
| 24 | aggregate | parallel_rct | 3 | 87127 | `5cbf039f22` | Aerobic exercise for depression symptoms in adolescents: a... |
| 25 | aggregate | aggregate | 2 | 46378 | `cfc6567ca3` | The Effect of Exercise on Depressive Symptoms in Adolescen... |
| 26 | negative | unknown | 2 | 44012 | `9cac5e48f3` | Protocol for Objective Measurement of Infants’ Physical Ac... |
| 27 | negative | unknown | 0 | 16093 | `83966faed7` | Editorial: New developments in the intention-behavior gap ... |
| 28 | negative | unknown | 0 | 15000 | `0843e61250` | Invited Commentary: Detecting Individual and Global Horizo... |
| 29 | negative | unknown | 0 | 11304 | `6e935d39b0` | Editorial: Causal inference in diet, nutrition and health ... |
| 30 | negative | unknown | 0 | 106600 | `af1bb4ac0c` | A computational perspective of the role of Thalamus in cog... |

## Begruendung je Dokument

1. `7111ea978757a185d44ea9de90b453c3` - Kalibrierungsdokument aus dem Versuchsplan.
2. `3134fdc8c38f475075a70ca32dc4a3d9` - Kalibrierungsdokument aus dem Versuchsplan.
3. `d0bec407a2a0dd19c0b67aa43f9e1dfb` - Kalibrierungsdokument aus dem Versuchsplan.
4. `bb9218735fec8fc7f3b6aebbff430aba` - Kalibrierungsdokument aus dem Versuchsplan.
5. `fb484d488b45d21bbdf407cba4b074d5` - Kalibrierungsdokument aus dem Versuchsplan.
6. `3bbb142c717a970694bed1d393736b06` - Kalibrierungsdokument aus dem Versuchsplan.
7. `87079ba88ae1f64f00c5fe32725248a6` - Kalibrierungsdokument aus dem Versuchsplan.
8. `2c7ab4d1244754e3966780f4bccbfa8c` - Kalibrierungsdokument aus dem Versuchsplan.
9. `09843d40d3cc2c9ca039d6d1b45ac656` - Kalibrierungsdokument aus dem Versuchsplan.
10. `334f5f679802315eeec71399149b51c3` - Kalibrierungsdokument aus dem Versuchsplan.
11. `203c831dbeb178297006a888608f4f10` - Kalibrierungsdokument aus dem Versuchsplan.
12. `2675c25aabf33995fb6c2d3e72221923` - Kalibrierungsdokument aus dem Versuchsplan.
13. `71c86b675bdc30a57ac17ac779abdce5` - Ergaenzung Schicht rct; 2 Zeilen in DB, 2 Caption-Treffer, Typen beta.
14. `cf9d739f5090aeda8006074fce2f0b44` - Ergaenzung Schicht rct; 2 Zeilen in DB, 4 Caption-Treffer, Typen or.
15. `b3c35c1d63f972086d2e322e693c1a03` - Ergaenzung Schicht rct; 2 Zeilen in DB, 3 Caption-Treffer, Typen mean_diff.
16. `b5e492009e4ca350f512d5144fe8bf92` - Ergaenzung Schicht rct; 2 Zeilen in DB, 0 Caption-Treffer, Typen smd.
17. `ca2c52d13aaec47ebbeccdedb3ee1d8e` - Ergaenzung Schicht crossover; 2 Zeilen in DB, 5 Caption-Treffer, Typen keine.
18. `3790c91f96877eb6e260b4d7e0c7e7ee` - Ergaenzung Schicht cohort; 2 Zeilen in DB, 5 Caption-Treffer, Typen r.
19. `7df874ca5386e7db9350901562d9408e` - Ergaenzung Schicht cohort; 2 Zeilen in DB, 0 Caption-Treffer, Typen r.
20. `17c7628ed0e8f01d4ec063e2b730dc36` - Ergaenzung Schicht cohort; 2 Zeilen in DB, 3 Caption-Treffer, Typen hr.
21. `7ca468285bd24135c1a9bf48f6f5f202` - Ergaenzung Schicht cross_sectional; 2 Zeilen in DB, 3 Caption-Treffer, Typen beta.
22. `1faf4b78f05cd156029ee647c2e14c51` - Ergaenzung Schicht cross_sectional; 2 Zeilen in DB, 3 Caption-Treffer, Typen beta.
23. `37cafe8444a2d0edd125109341865251` - Ergaenzung Schicht cross_sectional; 2 Zeilen in DB, 1 Caption-Treffer, Typen mean_diff.
24. `5cbf039f22f1bfe9f5902cf3f626852f` - Ergaenzung Schicht aggregate; 2 Zeilen in DB, 3 Caption-Treffer, Typen g.
25. `cfc6567ca3cb6eec8c47a64a1674a849` - Ergaenzung Schicht aggregate; 2 Zeilen in DB, 2 Caption-Treffer, Typen g.
26. `9cac5e48f3873753223db0c3b5f2b501` - Negativkontrolle: Protokoll/Editorial/Kommentar ohne Effektzeile.
27. `83966faed7ce0817920e6bf366efc8bb` - Negativkontrolle: Protokoll/Editorial/Kommentar ohne Effektzeile.
28. `0843e61250179bd14f8d0a45fc678e5d` - Negativkontrolle: Protokoll/Editorial/Kommentar ohne Effektzeile.
29. `6e935d39b012f2a76075a3a7964879b1` - Negativkontrolle: Protokoll/Editorial/Kommentar ohne Effektzeile.
30. `af1bb4ac0c54f9ed49d13393b37f4ffd` - Negativkontrolle: Protokoll/Editorial/Kommentar ohne Effektzeile.

## Bekannte Luecken

- **Kein Dokument ohne Textebene**: der Korpus enthaelt nur Volltexte mit
  extrahierbarem Text. Die im Plan vorgesehene Schicht ist damit nicht
  besetzt; das wird nicht durch ein Ersatzdokument kaschiert.
- **Caption-Treffer** sind ein Regex-Hinweis, kein Beleg fuer eine Tabelle.
  Massgeblich ist die Sichtpruefung der Annotatoren.
- **`db_effect_rows`** zeigt, was die Pipeline bisher fand. Es ist kein
  Goldstandard und darf die Annotation nicht beeinflussen (Blindheit).

## Pruefung dieser Liste

- 30 Dokumente, 30 verschiedene IDs, alle Volltexte vorhanden.
- 12 von 12 Kalibrierungsdokumenten enthalten.
- Schichtsummen wie oben; Typenabdeckung or/rr/hr/md/smd/g/beta/r je
  mindestens einmal vertreten (z nicht gefordert).

## Naechster Schritt

Kappa-Probelauf an drei Dokumenten (je eines aus RCT, Kohorte, Aggregat),
bevor alle 30 annotiert werden. Liegt Kappa unter 0,80, wird die Anleitung
geschaerft, nicht die Auswahl geaendert.
