# Klärung 09843: Fixed-Effects-Widerspruch

## Quellen

- Artikel-PDF: `https://www.nature.com/articles/s41598-025-00947-x.pdf`,
  Seite 6, Tabelle 3: `Continuous Variable −0.024*(0.110)`.
- HTML-Tabelle 3: `https://www.nature.com/articles/s41598-025-00947-x/tables/3`;
  derselbe Wert.
- Tabelle 2, Fußnote im PDF: `*p < 0.05, **p < 0.01, ***p < 0.001,
  same as later`. Damit meint der Stern in Tabelle 3 p < 0.05.
- Supplement-ZIP:
  `https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-025-00947-x/MediaObjects/41598_2025_947_MOESM1_ESM.zip`,
  `Table S4.pdf` (IPW):
  `D_Physical Exercise -0.023* 0.011 -2.07 0.039 [-0.044, -0.001]`,
  N = 5757.
- `Figure S2-S13.pdf`, Abbildung S12: Individual Fixed Effects mit
  kontinuierlicher Bewegung, cluster-robuste SE. Die Abbildung ist ein
  Bild; der `pypdf`-Text enthält nur die Caption. Die Bild-Extraktion
  scheitert, weil Pillow fehlt; die Pillow-Installation scheitert an
  fehlenden zlib-Headern. `pdftoppm`, `pdftocairo`, `gs` und `magick`
  sind nicht verfügbar. Die exakte FE-SE aus S12 ist daher nicht
  verifiziert.

## Rechnung

- β/SE = −0.024 / 0.110 = −0.218; zweiseitig ergibt das p ≈ 0.83.
- Der Stern p < 0.05 und der Text „β = −0.024, p < 0.05“ sind mit
  SE = 0.110 nicht vereinbar.
- Die OLS-SE für die kontinuierliche, adjustierte Exposition ist 0.010
  (Tabelle 2); die IPW-SE ist 0.011 (Tabelle S4). Beide liegen in der
  Größenordnung, die zu p < 0.05 passt.
- Die 0.110 liest sich wie 0.010 mit einer zusätzlichen 1. Das ist die
  wahrscheinlichste Erklärung, aber kein bestätigter Wert: Die OLS- und
  IPW-SE stammen aus anderen Modellen, nicht aus dem FE-Modell.

## Befund

Die veröffentlichte Tabelle 3 ist in sich widersprüchlich. Die SE 0.110
ist als Unsicherheit der FE-kontinuierlichen Zeile nicht verwendbar.
Die Datenlage stützt einen Tippfehler (0.010), beweist ihn aber nicht;
die direkte FE-Ausgabe in Abbildung S12 konnte nicht gelesen werden.

## Entscheidung

- Die **5 belastbaren Zeilen** bleiben: vier OLS-Modelle und das
  FE-Modell mit der kategorialen Exposition.
- Die FE-kontinuierliche Zeile wird **nicht** als Primärzeile annotiert,
  solange die SE nicht korrigiert oder aus S12 bestätigt ist.
- Die IPW-Schätzung (`−0.023`, SE 0.011, p 0.039) ist eine
  Sensitivitätsanalyse derselben Exposition. Nach 5.9 gehört sie in
  `notes`, nicht als eigene Primärzeile.
- Wird die FE-Zeile dennoch gebraucht, ist die SE 0.010 eine
  Plausibilitätsgröße aus Tabelle 2, keine berichtete FE-SE; sie muss
  als Schätzung markiert werden, nicht als Zitat.
- Die Cross-lagged-Betas bleiben p-only ohne SE/CI; keine Zeilen.

## Grenze

Die exakte FE-SE aus Abbildung S12 ist offen. Für die Entscheidung
reichen die veröffentlichte Tabelle und Tabelle S4: Die 0.110 ist
nicht verwendbar, und die 5 belastbaren Zeilen sind unverändert.
