# C1-Zeitpunktregel

Stand: 2026-11-11
Status: **entschieden und verbindlich für künftige C1-Läufe**

Umsetzungsstand: `c1-dev-extract-v2` hat die Regel nicht umgesetzt (93/140).
`c1-dev-extract-v3` priorisiert die Post-test-Spalte explizit und erreicht
123/140 (87,9 %); 32 der 39 Zeitpunktfelder sind korrigiert. v3 ist noch nicht
testreif: 224 und 226 bleiben Follow-up-Ausreißer, 190 wählt 3 statt 12
Monate. Die Regel braucht für solche longitudinalen binären Outcomes eine
explizite Record-Zeitpunktangabe.

## Regel

Für jeden Record und jedes Outcome gilt genau ein Zeitpunkt:

1. Nennt die ICO einen Zeitpunkt, gilt dieser.
2. Sonst gilt der unmittelbare Post-Test: die erste berichtete Messung nach
   dem Ende der Intervention, die nicht als Follow-up bezeichnet ist.
3. Ist der Post-Test nicht für beide Arme berichtet, gilt der früheste
   Follow-up, für den beide Arme vollständig berichtet sind.
4. Baseline, Change-Scores, Peakwerte und gemischte Zeitpunkte sind unzulässig.
5. Beide Armwerte müssen aus demselben Zeitpunkt und derselben
   Outcome-Definition stammen; es wird nicht zwischen Zeitpunkten oder Armen
   zusammengeführt.
6. Wird der Zielwert nur als Median, Prozentwert ohne N, Change-Score oder
   Grafik berichtet, bleibt das Feld `null`.
7. Die `source_note` nennt den gewählten Zeitpunkt und die Tabelle bzw. Zeile.

## Begründung

Die Regel ist deterministisch und verhindert, dass das Extraktionssystem den
spätesten, den günstigsten oder den gerade besser passenden Zeitpunkt frei
wählt. Sie ist mit der eingefrorenen Dev-Referenz vereinbar: Bei PMC5498715
verwendet die Referenz den Post-Test, wenn er für beide Arme berichtet ist;
bei Agility, Flexibility, Muscular endurance und Cardiorespiratory endurance
fehlt der Post-Test, dort verwendet sie den Follow-up nach vier Monaten.

Im C1-Dev-Pilot erklärt diese Regel **39 der 43 falschen Felder**: Das Modell
hatte dort durchgehend den 4-Monats-Follow-up statt des Post-Tests gewählt.
Die Regel ändert den historischen Primärwert des v1-Laufs nicht; sie legt fest,
wie der nächste Lauf den Zeitpunkt behandeln muss.

## Geltung und Grenzen

- Die Regel gilt ab dem nächsten C1-Prompt; der Lauf `c1_dev_20261111` mit
  `c1-dev-extract-v1` bleibt als historischer Messpunkt unverändert.
- `c1-dev-extract-v2` hat die Regel im Prompt codiert, aber im Dev-Test nicht
  umgesetzt; er ist nicht für eine Testfreigabe freigegeben.
- `c1-dev-extract-v3` setzt die Spaltenpriorisierung weitgehend um, ist aber
  wegen der vier offenen Records (120, 224, 226, 190) noch nicht testreif.
- Sie ist eine Benchmark-Entscheidung, keine klinische Empfehlung. Für eine
  spätere gepoolte Analyse kann ein studienübergreifend einheitlicher
  klinischer Zeitpunkt sinnvoller sein; dann muss die Referenz neu eingefroren
  werden, nicht stillschweigend uminterpretiert.
- Der Testsplit `yun_c1_test_249.jsonl` wurde für diese Entscheidung nicht
  geöffnet und bleibt gesperrt.
- Record 120 bleibt ein separates ICO-Problem (DTPA-Subgruppe vs. Rezidiv).
- Record 190 zeigt eine Grenze der Fallback-Regel: Die Referenz nutzt den
  12-Monats-Wert, die Regel würde den frühesten Follow-up (3 Monate) wählen.
  Dieser Record braucht vor einer Testfreigabe einen expliziten Zeitpunkt.
- Record 226 zeigt einen zusätzlichen Tabellenfehler: Der Post-Test ist
  berichtet, wird aber als leer behandelt.

## Prüfung

Die Regel wurde ausschließlich an den 26 Dev-Records und den öffentlichen
Quelltexten geprüft. Die Belegstellen stehen in
[`runs/c1_dev_20261111/manual_review.md`](runs/c1_dev_20261111/manual_review.md).
