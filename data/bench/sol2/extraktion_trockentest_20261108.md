# Trockentest: Formular an den drei eingeschlossenen Studien

Stand: 2026-11-08. Ausgefüllt wurden S1 (Gringras 2012), S2 (Wade 2010) und
S3 (van Geijlswijk 2010) nach `extraktionsformular_20261108.md`. Ergebnis
steht in `extraktion_vorlage_20261108.csv`. Ziel war nicht die Datenerhebung
selbst, sondern die Prüfung, ob die Felder praktisch reichen.

## Ergebnis in einem Satz

Das Formular trägt die drei Studien vollständig. Fünf Felder fehlten und
wurden ergänzt, drei Schwächen bleiben. Der wichtigste Befund ist nicht ein
fehlendes Feld, sondern eine fehlende Unterscheidung: „entfällt" und „nicht
berichtet" sahen im Datensatz gleich aus.

## Was gefüllt wurde

| Feld | S1 Gringras | S2 Wade | S3 van Geijlswijk |
|---|---|---|---|
| design | parallel | parallel | parallel |
| n_randomisiert | 146 | 791 | 72 |
| n je Arm randomisiert | 70 / 76 | nicht berichtet | nicht berichtet |
| n analysiert | 113 | 281 (Subgruppe) | 33 (zwei von vier Armen) |
| n je Arm analysiert | 54 / 59 | 137 / 144 | 16 / 17 |
| Dosis | 0,5 mg titriert auf 2, 6, 12 | 2 mg fix | 0,05 mg/kg |
| Dauer | 12 Wochen | 3 Wochen (Zeitpunkt) | 1 Woche |
| Messmethode | Tagebuch (Eltern) | Tagebuch | Schlaf-Log (Eltern) |
| Verum, Woche n | 54,8 (SD 51,9) | 57,6 (SD 51,8) | nicht berichtet |
| Placebo, Woche n | 92,4 (SD 63,0) | 70,9 (SD 54,0) | nicht berichtet |
| Effekt (min) | −37,5 | −15,6 | −31,0 |
| SE | 9,08 | 4,92 | 10,0 |
| Herkunft | berichtet, adjustiert | berichtet, adjustiert | berichtet mit SE |
| sol_primaer | sekundär nach Amendment | sekundär (Register: primär) | primär |
| Register | ISRCTN05534585, EU-CTR 2006-004025-28 | NCT00397189 | ISRCTN20033346 |
| status | poolbar | poolbar | poolbar |

Alle Zahlen stammen aus `pruefung_kandidaten_20261108.md`,
`results_limitations_20261108.md` und dem XML von PMC3489506. Das Zitat für
S1 ist die Tabellenzeile

```text
|Sleep onset latency (min)|54|102.0 (72.6)|54.8 (51.9)|-47.2 (64.4)||59|102.1 (57.7)|92.4 (63.0)|-9.7 (49.6)|-37.5 (-55.3 to -19.7)†
```

Damit sind Baseline, Woche 12 und Change je Arm belegt; die adjustierte
Differenz −37,5 stimmt mit der unadjustierten Differenz der Changes
(−47,2 − (−9,7) = −37,5) überein.

## Fünf Ergänzungen, die der Test erzwungen hat

**1. Armgrößen getrennt nach Randomisierung und Auswertung.**
`n_randomisiert = 146` und `n_analysiert = 113` allein verschweigen, wie
sich die 33 fehlenden Kinder auf die Arme verteilen. Neu:
`n_verum_randomisiert` und `n_placebo_randomisiert`. Bei S1 aus Tabelle 1
belegt (70/76), bei S2 und S3 nicht berichtet.

**2. `sol_primaer`.** Der Endpunktstatus ist für RoB 2 Domäne 5 zentral und
stand nur im Fließtext. Bei S1 ist er „sekundär nach Amendment", bei S2
„sekundär (Register: primär)" — genau der Widerspruch, der im RoB-Dokument
steht, gehört in eine Spalte und nicht in eine Fußnote.

**3. `register_id`.** Ohne Register-ID lässt sich der Abgleich Publikation
gegen Register nicht wiederholen. Er ist bei allen drei Studien bereits
gemacht worden (`register_pruefung_20261108.md`) und war im Formular nicht
abgebildet.

**4. `adjustierte_kovariaten`.** `adjustiert = ja` sagt nicht, wogegen
adjustiert wurde. Alle drei Effekte sind baseline-adjustiert, aber die
Modelle sind studienintern verschieden — das steht bisher nur im Bericht.

**5. Regel R11: `entfällt` ist nicht `nicht berichtet`.** Bei einer
Parallelstudie sind acht Felder designbedingt leer. Ohne eigene Kennzeichnung
sieht S1 aus wie eine Crossover-Studie mit acht fehlenden Angaben. R11
verlangt `entfällt` für designbedingte Leerstellen und leer für echte
Berichtslücken.

## Drei Schwächen, die bleiben

**1. Mehrarmstudien sprengen den Prüfschritt.** Prüfschritt 5 verlangt, dass
die Summe der Armgrößen `n_analysiert` ergibt. Bei S3 stimmt das nicht:
16 + 17 = 33, randomisiert waren 72 auf vier Arme. Der Schritt muss lauten
„Summe der verwendeten Arme", sonst schlägt er bei jeder Dosisfindungsstudie
falsch an.

**2. Nicht alle poolbaren Studien haben Arm-Mittelwerte.** S3 berichtet nur
die Differenz mit SE. Die Felder `verum_mean` bis `placebo_sd` bleiben leer,
obwohl die Studie poolbar ist. Das ist zulässig, aber der Status „poolbar"
darf nicht davon abhängen, dass alle Felder gefüllt sind — sonst wird eine
gültige Zeile verworfen.

**3. Citationsfelder sind mühsam.** Die Tabellenzeile aus dem XML ist lang
und enthält Pipes. In einem Formular, das von Hand gefüllt wird, ist das
fehleranfällig. Ein Feld „Tabellenzeile als Referenz" plus Kurzzitat wäre
praktischer; bis dahin gilt: lieber die Zeile wörtlich als eine Paraphrase.

## Was der Test über die Zahlen sagt

Nichts Neues — und das ist der Punkt. Die drei Zeilen reproduzieren exakt die
Werte aus `pooling_sol3_20261108.md`: −37,5 (SE 9,08), −15,6 (SE 4,92),
−31,0 (SE 10,0). Der Trockentest hat die Datenlage nicht verändert, sondern
die Erhebung überprüfbar gemacht.

## Nächster Schritt

Die drei Zeilen sind die erste konsistente Datengrundlage der Hauptanalyse.
Wenn die zwölf Volltexte eintreffen, wird nach demselben Schema gefüllt; die
CSV wächst auf 15 Zeilen, ohne dass die bestehenden drei angefasst werden
müssen.
