# MENDS-HTA-Bericht: Was steht dort, was der BMJ-Artikel nicht hat?

Stand: 2026-11-08. Quellen: `volltext/23098680.txt` (Appleton et al. 2012,
*Health Technology Assessment* 16(40), DOI 10.3310/hta16400) und
`xml/PMC3489506.xml` (Gringras et al., *BMJ* 2012, DOI 10.1136/bmj.e6664).
Beide berichten dieselbe Studie (MENDS), siehe `dedup_register_20261108.md`.

## Befund in einem Satz

Der HTA-Bericht liefert **keine neuen Arm-Mittelwerte oder Streuungen** für
SOL - die Tabelle 7 ist die bereits bekannte Tabelle - aber er berichtet
zusätzlich die **unadjustierte Differenz der Change-Werte mit 95 %-CI**.
Daraus lassen sich zwei Sensitivitätsvarianten (S8/S9) rechnen.

## Vergleich der Tabellen

### Schlaftagebuch, SOL (Minuten)

| | Melatonin Baseline | Melatonin W12 | Melatonin Change | Placebo Baseline | Placebo W12 | Placebo Change |
|---|---|---|---|---|---|---|
| HTA Tab. 7 | 101,98 (72,56) | 54,82 (51,91) | −47,16 (64,38) | 102,09 (57,72) | 92,36 (63,02) | −9,72 (49,64) |
| BMJ Tab. 3 | 102,0 (72,6) | 54,8 (51,9) | −47,2 (64,4) | 102,1 (57,7) | 92,4 (63,0) | −9,7 (49,6) |

### Aktigraphie, SOL (Minuten)

| | Melatonin Baseline | Melatonin W12 | Melatonin Change | Placebo Baseline | Placebo W12 | Placebo Change |
|---|---|---|---|---|---|---|
| HTA Tab. 7 | 126,75 (71,45) | 68,42 (41,03) | −58,32 (53,65) | 107,83 (54,88) | 104,12 (59,53) | −3,71 (47,37) |
| BMJ Tab. 3 | 126,8 (71,5) | 68,4 (41,0) | −58,3 (53,7) | 107,8 (54,9) | 104,1 (59,5) | −3,71 (47,4) |

Die Unterschiede sind Rundung. n ist identisch: Tagebuch 54/59,
Aktigraphie 24/25.

## Die neue Zahl

| Endpunkt | Differenz der Change-Werte (unadjustiert) | 95 %-CI | p | SE |
|---|---|---|---|---|
| SOL Tagebuch | −37,44 min | −58,77 bis −16,11 | 0,007 | 10,88 |
| SOL Aktigraphie | −54,61 min | −83,67 bis −25,56 | 0,0004 | 14,82 |

Zum Vergleich die adjustierte Differenz (Hauptanalyse): Tagebuch −37,49
(−55,27 bis −19,71), SE 9,08; Aktigraphie −45,34 (−68,75 bis −21,93),
SE 11,96.

Die unadjustierte Aktigraphie-Differenz (−54,61) ist deutlich größer als die
adjustierte (−45,34). Das ist plausibel: Die Aktigraphie-Baseline war in der
Melatonin-Gruppe höher (126,75 vs. 107,83), und die Adjustierung korrigiert
diesen Unterschied. **Die adjustierte Schätzung ist die richtige**; die
unadjustierte ist eine rohe Gegenprobe.

## Was der Bericht sonst enthält - und nicht enthält

- **Keine Zwischenzeitpunkte mit SOL.** Es gibt nur Baseline (T0) und
  Woche 12 (T12); keine Woche-4- oder Woche-8-SOL-Werte.
- **Keine Per-Protocol-SOL-Werte.** Der Bericht verweist für
  Sensitivitätsanalysen auf Appendix 6 (nicht Teil des extrahierten Texts).
- **Keine Subgruppen-SOL-Mittelwerte.** Tabelle 14 (ASMT/AANAT-Mutationen)
  enthält nur Ja/Nein-Angaben zu Schlafstörung und Ansprechen, keine
  Mittelwerte. Die explorativen Regressionen (BMJ Tab. 8) liefern
  Treatment-Effekte für Subgruppen, aber keine Arm-SDs.
- **Keine Streuung der adjustierten Differenz** außer dem CI; die SE ist
  daraus abgeleitet, nicht berichtet.
- Die Zahl der Kinder in der Primäranalyse ist 51/59 (TST-Tagebuch) bzw.
  54/59 (SOL-Tagebuch); das ist kein Widerspruch, sondern verschiedene
  Outcomes mit verschiedener Datenvollständigkeit.

## Konsequenz für die Analyse

1. Die Extraktion für PMC3489506 bleibt unverändert: adjustierte Differenz
   −37,5 (SE 9,08), Tagebuch; Sensitivität Aktigraphie −45,3 (SE 11,96).
2. **Neu:** zwei Sensitivitäten mit der unadjustierten Differenz - S8
   (Tagebuch, −37,44, SE 10,88) und S9 (Aktigraphie, −54,61, SE 14,82).
   Ergebnisse: S8 −25,43 (−54,37 bis 3,50), S9 −30,12 (−76,83 bis 16,59).
3. Kein neues k, keine neue Studie: Der HTA-Bericht ist eine
   Doppelpublikation, kein unabhängiger Datensatz.
4. Die Rohdaten des Berichts (Appendix-Tabellen, falls die Lieferung sie
   enthält) könnten später die fehlende SE der adjustierten Differenz
   ersetzen - nötig ist das nicht, weil das CI die SE bereits bestimmt.

## Artefakte

- Extraktion: dieses Dokument, Tabellen oben.
- Rechnung: `scripts/pool_sol3.py`, Analysen S8/S9 in
  `pooling_sol3_20261108.json`.
- Beleg der Identität: `dedup_register_20261108.md`, Kategorie A.
