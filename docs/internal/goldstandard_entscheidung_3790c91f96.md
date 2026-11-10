# Entscheidung: Zitat-Zwilling 3790c91f96 (2026-11-10)

## Anlass

Der Abgleich Goldstandard gegen Pipeline verwarf bei `3790c91f96` eine von
zwei Zeilen als Zitat-Zwilling: beide tragen denselben Zitatspan
(29497-29676), aber die Werte -0,150 und -0,206. Die Frage war, ob dahinter
emotionale und koerperliche depressive Symptome als zwei Outcomes stehen.

## Befund

- Beide Pipeline-Zeilen (`302e393aea`, Pass 1, r = -0,150; `bf76f02078`,
  Pass 2, r = -0,206) haben `outcome = depressive symptoms`; die
  Praezisierung steht nur im Zitat.
- Der Satz lautet: "PA was significantly negatively correlated with
  **emotional** depressive symptoms (rs=[-0.150, -0.206]; P < 0.001) and
  **physical** depressive symptoms (rs=[-0.225, -0.266]; P < 0.001)".
- Beide gespeicherten Werte gehoeren also zu **emotionalen** Symptomen. Die
  koerperlichen Werte (-0,225/-0,266) hat die Pipeline nicht erfasst.
- Tabelle 2 (Datei bei 33908) loest die Werte auf: PA x EDS T1 -0,17,
  T2 -0,206, T3 -0,199; PA x PDS T1 -0,248, T2 -0,265, T3 -0,266.
  Zusaetzlich enthaelt die Matrix Kreuzkorrelationen: T3-PA mit T1-EDS
  -0,15, T3-PA mit T1-PDS -0,226.
- Damit sind -0,150 und -0,206 **verschiedene Zeitpunktpaare**
  (T3-PA x T1-EDS bzw. T2-PA x T2-EDS), keine zwei Outcomes.
- Die Zeilen tragen keinen `time_point`; `moderators` nennt nur
  "time point (T1-T3)". Der Zeitpunkt fehlt in der Zeile.

## Entscheidung

1. **Emotionale und koerperliche Symptome sind zwei Outcomes** und damit
   getrennte Goldstandard-Zeilen. Die Anleitung (mehrere Outcomes) verlangt
   das, und Tabelle 2 belegt beide Reihen.
2. **Die beiden Pipeline-Zeilen sind nicht diese zwei Outcomes.** Beide sind
   emotional; koerperlich fehlt vollstaendig.
3. **Der Zitat-Zwilling ist fachlich kein Zwilling derselben Schaetzung.**
   Die Dedupe-Regel verwirft ihn, weil sie den Zeitpunkt nicht kennt und
   derselbe Beleg als Kopie gilt. Konservativ ist das fuer die Ausbeute
   richtig, fuer den Recall dieses Dokuments nicht.
4. Fuer den Goldstandard ist **Tabelle 2 die Quelle**: PA x EDS und PA x PDS
   je Zeitpunkt getrennt, mit Tabellenzitat. Die genaue Zeilenzahl legt der
   Annotator fest; mindestens zwei Outcomes, Zeitpunkte getrennt.

## Konsequenz fuer den Abgleich

- Der Fall bleibt als 1 von 13 Duplikaten dokumentiert; die Dedupe-Zahl
  aendert sich nicht.
- Sobald der Goldstandard PA x PDS und die Zeitpunkte enthaelt, faellt der
  Recall fuer dieses Dokument. Das ist ein echter Extraktionsbefund
  (fehlender Outcome, fehlender Zeitpunkt), kein Matching-Fehler.
- Die Regel im Pooling (`_drop_zweitlesungen`) ist davon ebenfalls betroffen:
  Sie kennt den Zeitpunkt nicht. Eine Aenderung waere ein Eingriff in eine
  geschuetzte Kerndatei und ist hier nicht Teil des Auftrags.

## Pruefung

- Volltext `data/fulltext/3790c91f96877eb6e260b4d7e0c7e7ee.txt`, Satz bei
  29434-29676, Tabelle 2 bei 33908.
- Die Pipeline-Zeilen sind in
  `data/research-exercise-and-depressive-symptoms-in-adul-bbb324.db`
  reproduzierbar (`source_text_id = 3790c91f...`).
