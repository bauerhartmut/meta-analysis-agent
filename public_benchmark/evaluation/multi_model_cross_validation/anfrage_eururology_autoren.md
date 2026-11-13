# Anfrage an die Autoren des European-Urology-Goldstandards

Stand: 2026-11-13
Bezug: [`public_goldstandard_dataset_review.md`](public_goldstandard_dataset_review.md)

## Warum diese Anfrage

Die unter <https://osf.io/8fzps/> veröffentlichten Arbeitsmappen enthalten 104
verwertbare Records aus 20 Trials. Der Artikel nennt 105 Trials. Für unsere
Cross-Validation fehlt zu jeder Zahl die Belegstelle (Seite, Tabelle,
Zellposition) und der Zeitpunkt. Beides ist in den Arbeitsmappen nicht
enthalten, aber mit hoher Wahrscheinlichkeit in den Extraktionstabellen der
Autoren vorhanden.

Die Anfrage ist bewusst eng gefasst: keine Rohdatenberge, keine PDFs, sondern
die vorhandenen Tabellen mit Belegspalten. Das ist für die Autoren ein
überschaubarer Aufwand und für uns der Unterschied zwischen „nutzbar mit
Einschränkung" und „vollständig schema-konform".

## Was genau gebraucht wird

1. Die vollständigen Tabellen beider Reviews (41 binäre, 64 kontinuierliche
   Trials) als CSV oder XLSX, nicht nur die in die gepoolten Analysen
   eingegangenen Trials.
2. Je extrahiertem Wert zusätzlich: Seite, Tabellen- oder Abbildungsnummer
   und, falls vorhanden, die zitierte Textstelle.
3. Der Zeitpunkt des Outcomes, sofern die Review ihn definiert.
4. Eine kurze Bestätigung, ob die Werte unabhängig zweitgeprüft wurden und
   wie Konflikte aufgelöst wurden.
5. Eine Aussage zur Lizenz oder zu den Bedingungen der Nachnutzung.

## E-Mail-Entwurf (Englisch, versandfertig)

> Subject: Request for the full extraction tables of your BMC Med Res Methodol
> data-extraction study (doi 10.1186/s12874-025-02729-5)
>
> Dear Dr. Liu, dear Dr. Wang,
>
> We are preparing an independent multi-model comparison of numerical data
> extraction from randomised controlled trials, and we read your study
> "Assessing data extraction in randomized clinical trials with large language
> models" (BMC Medical Research Methodology 2026;26:33) with great interest.
>
> We downloaded the four workbooks from your OSF project (osf.io/8fzps) and
> were able to reconstruct 104 trial-outcome rows from 20 trials
> (41 binary, 63 continuous). Two things would help us enormously, and both
> concern material you likely already have:
>
> 1. The complete extraction tables of the two European Urology reviews
>    (the 41 binary and 64 continuous trials), rather than only the trials that
>    entered the pooled analyses.
> 2. For each extracted value, the source location in the trial report: page,
>    table or figure number, and — where available — the quoted text or cell.
>    If your forms also recorded the outcome time point and a note on
>    independent verification (who extracted, who checked, how disagreements
>    were resolved), we would be very grateful for those columns as well.
>
> We would use the data solely for a methodological comparison of extraction
> accuracy, will cite your paper and the OSF project, and will not redistribute
> the tables beyond derived aggregate results. If a licence or specific terms
> apply, please let us know so that we can comply.
>
> If the full tables are no longer available, even a confirmation of which
> trials were eligible but not extracted would help us describe the dataset
> correctly.
>
> Thank you very much for considering this request.
>
> Kind regards,
> [Name], [Institution]
> [E-Mail]

## Wenn keine Antwort kommt

- Der Datensatz bleibt `usable_with_limitations` mit 104 Records.
- Stufe 1 (externe Validierung) läuft dann ohne Belegstellen, also nur auf
  Zahlen- und Armgenauigkeit.
- Die Referenzannotation der 25 Artikel bleibt in jedem Fall notwendig, weil
  nur sie die fünf Provenienzfelder aus `schema_v1` liefert.

## Was nicht angefragt wird

- Keine PDFs der Trials (die beschaffen wir selbst, soweit open access).
- Keine personenbezogenen Daten.
- Keine Modellausgaben der Autoren; die `*_AI`-Spalten der Arbeitsmappen werden
  nicht als Referenz verwendet.
