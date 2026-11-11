# DTA-Korpus: Umfang und Abgrenzung

Quelle: Cochrane DTA Reference Dataset, Zenodo-Record 1303259, Datei
`CL145_open_set_20181101.zip`, Lizenz CC BY-NC 4.0. Das Paper liegt unter
PMC6371350; Zenodo-Record 2574710 enthält nur das Paper-PDF, nicht den
Datensatz.

## Inhalt

- 63 systematische Reviews.
- 1.354 diagnostische Tests (Testdefinitionen).
- 1.738 eingeschlossene Studie-Review-Einträge; daraus 1.663 eindeutige
  `study_id`-Werte, weil Studien in mehreren Reviews vorkommen können.
- 6.433 `result`-Elemente; 5.848 davon enthalten eine vollständige
  2x2-Tabelle (`tp`, `fp`, `fn`, `tn`).
- 585 Findings-Testblöcke in 57 Reviews; 6 Reviews haben keinen
  Findings-Block.
- 6.699 ausgeschlossene Referenzen.
- Forest-Plot-Bilder und Review-/Studienmetadaten.

## Warum es nicht unser B ist

Der Korpus extrahiert **diagnostische Testgenauigkeit**:

- Index-Test gegen Referenzstandard,
- Target Condition,
- TP/FP/FN/TN, Sensitivität, Spezifität.

Unsere Aufgabe ist **Intervention gegen Comparator** mit kontinuierlichen
oder binären Outcomes, N, Mean, SD und Zeitpunkt. Diese Felder fehlen im
DTA-Korpus. Es enthält außerdem keine Volltexte der Primärstudien, sondern
die aus Cochrane-Reviews extrahierten Datensätze und Forest Plots.

## Mögliche Nebenverwendung

Als kleine, unabhängige Prüfung für strukturierte 2x2-Extraktion aus
Review-Tabellen ist der Korpus brauchbar. Wegen der CC-BY-NC-4.0-Lizenz und
der fachlichen Differenz sollte er nicht der primäre Benchmark für unser
B-Experiment sein.
