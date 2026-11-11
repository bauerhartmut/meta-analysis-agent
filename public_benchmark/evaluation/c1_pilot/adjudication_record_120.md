# Adjudikation Record 120

Stand: 2026-11-11
Status: **entschieden**
Entscheidung: **Record 120 bleibt in C1, mit präzisiertem Ziel-Outcome.**

## Zieldefinition

- **Outcome:** DTPA-Scan, „partial obstruction“ einen Monat nach der
  Pyeloplastik.
- **Analysegruppe:** Patienten mit DTPA-Untersuchung in beiden randomisierten
  Armen: 20 mit internem Drainage-/Stent-Arm, 44 im stentlosen Arm.
- **Referenzwerte:** 8/20 vs. 13/44.
- **Nicht das Ziel:** „Recurrence of stenosis – reoperation“ 0/30 vs. 1/52.

Die 20/44 sind eine DTPA-untersuchte Untergruppe, nicht die randomisierten
30/52-Arme. Das ist zulässig, weil das targetierte Outcome nur für die
DTPA-untersuchten Patienten berichtet wird; es wird ausdrücklich als
Subgruppen-Analyse geführt.

## Begründung

Die ICO „ureteropelvic junction obstruction“ nennt die Erkrankung, aber weder
Diagnostikweg noch Ergebniszeile. Tabelle 2 enthält mehrere mögliche Zeilen.
Die DTPA-Zeile quantifiziert die Obstruktion direkt; die Rezidiv-/Reoperations-
Zeile ist ein anderes klinisches Ereignis. Die Referenz ist mit der
DTPA-Zeile exakt belegt und bleibt unverändert.

## Folgen

- Der v5-Lauf bleibt bei **136/140 exakt (97,1 %)**; die vier falschen Felder
  sind genau Record 120.
- Die Referenz und der eingefrorene Input werden nicht geändert.
- Ein künftiger Prompt muss bei der Auswahl der Ergebniszeile die direkt
  gemessene Obstruktion (DTPA) gegenüber Komplikationen/Reoperationen
  priorisieren, wenn die ICO die Ergebniszeile nicht nennt.
- Der Testsplit wurde nicht geöffnet und bleibt gesperrt.

## Alternative, bewusst nicht gewählt

Ein Ausschluss von Record 120 aus dem C1-Scoring wäre möglich, würde die
Dev-Abdeckung aber künstlich auf 136/136 heben und die Ambiguität aus dem
Benchmark entfernen. Die Adjudikation mit explizitem Ziel erhält den
schwierigen Fall und macht die Referenz entscheidbar.
