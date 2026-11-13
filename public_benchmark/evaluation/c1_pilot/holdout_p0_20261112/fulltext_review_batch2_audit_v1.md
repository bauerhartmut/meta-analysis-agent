# Audit Batch 2: Zähler, Quellen und Überlappungen

Stand: 2026-11-13
Status: **AUDIT ABGESCHLOSSEN; MENSCHLICHE PRÜFUNG OFFEN**.

Geprüft wurden ausschließlich die gespeicherten Batch-2-Artefakte und die
lokalen XML-Texte. Es wurden keine Outcome-Werte, Quellen oder
Unabhängigkeitsklassen verändert.

## Ergebnis

| Kennzahl | Wert |
|---|---:|
| Artikel | 9 |
| Outcome-Slots | 36 |
| Unabhängig verwendbar | 8 |
| Überlappend, nicht unabhängig | 6 |
| Nicht verwendbar/nicht berichtet | 22 |
| Formal verwendbar inkl. überlappend | 14 |
| Finale Entscheidungen | 0 |

**Zähler:** 8 + 6 + 22 = 36; 8 + 6 = 14 formal verwendbar. Die Summen sind konsistent.

## Quellenprüfung

- **36/36** Slots haben einen Quelleintrag.
- **17** Results-Textzitate wurden exakt im normalisierten XML gefunden.
- **19** Tabellenverweise: Caption, Zeilenlabel und strukturierte Werte wurden ausschließlich in der jeweils referenzierten Tabellenzeile geprüft; **14/18** Tabellen-Outcomes bestanden die zeilenexakte Prüfung: 12/16 Einzelzeilen und 2/2 Kosten-Outcomes mit getrennten Interventions-/Kontrollzeilen bestanden. 4 binäre AE-Outcomes haben Ereignisse in der Zeile, aber N nur im Arm-Header und bestehen die Zeilenprüfung deshalb nicht. Der ICER-Slot ist ein Tabellenverweis ohne eigene Zeilenwerte.
- **20/20** Outcomes mit strukturierten Zahlen enthalten diese Zahlen im Quelleintrag.

Hinweis: Tabellenquellen sind keine zusammenhängenden Fließtextsätze. Die
Quellenprüfung vergleicht deshalb Caption, Zeilenlabel und strukturierte
Werte ausschließlich in der referenzierten Tabellenzeile; sie
ersetzt nicht die menschliche Sichtprüfung der Tabelle.

## Überlappungen

- `PMC13519320`: Slot 1 ist das Gesamtoutcome; Slots 2-4 sind überlappend.
- `PMC13590641`: Slot 1 ist das Sammeloutcome „Any AE“; Slots 2-4 sind
  spezifische AEs und überlappen damit.
- Keine weiteren Slots sind als überlappend markiert.

Die sechs überlappenden Slots zählen nicht als unabhängige Outcomes.

## Artikelübersicht

| PMC | Slots | Unabhängig | Überlappend | Nicht verwendbar | Quelle |
|---|---:|---:|---:|---:|---|
| PMC13610533 | 4 | 0 | 0 | 4 | 4/4 |
| PMC13743599 | 4 | 1 | 0 | 3 | 4/4 |
| PMC13613700 | 4 | 0 | 0 | 4 | 4/4 |
| PMC13626740 | 4 | 4 | 0 | 0 | 4/4 |
| PMC13688066 | 4 | 0 | 0 | 4 | 4/4 |
| PMC13519320 | 4 | 1 | 3 | 0 | 4/4 |
| PMC13590641 | 4 | 1 | 3 | 0 | 4/4 |
| PMC13596784 | 4 | 0 | 0 | 4 | 4/4 |
| PMC13574397 | 4 | 1 | 0 | 3 | 4/4 |

## Prüfhinweise für die menschliche Runde

- `PMC13610533`: nur Median/IQR; keine Umrechnung in Mean/SD.
- `PMC13743599`: 17/14 randomisiert, aber nur 10/10 mit Post-Werten; post hoc.
- `PMC13613700`: keine armweisen Ereigniszahlen; nur adjustierte Assoziationen.
- `PMC13626740`: T3-Werte mit verfügbarem n; CBT und ST getrennt halten.
- `PMC13688066`: HE nur als Gesamtfrequenz/Subgruppeninteraktion, keine Armzahlen.
- `PMC13519320`: gepoolte BOREAS/NOTUS-Analyse; Slot 1 Gesamt, Slots 2-4 überlappend.
- `PMC13590641`: Any AE als Sammeloutcome; spezifische AEs überlappen; open-label und vorzeitig beendet.
- `PMC13596784`: Mean/SD vorhanden, aber kein armweises n pro Zeitpunkt.
- `PMC13574397`: Striktur 2/10 vs. 7/10; Kosten ohne SD, ICER nur „Dominated“.

## Invarianz

SHA-256 der unveränderten Batch-2-Dateien:

- JSON: `feb48199ebb22549fd936710da41b744fa4daa9f11fb8d9bae7f709591bf0f56`
- CSV: `dcd2d434ea2967ca509ef057edb020ddecebaefecd324d60d47769949d8f271f`
- Markdown: `c2219e6cc573766f10c1ef0993d5f171cd753e35adde0b5a5cd8ec481d50ebff`

## Auditstatus

- Offene Befunde: **4**
- Menschliche Prüfung: **offen**
- Outcome-Werte geändert: **nein**

### Befunde

- PMC13590641 Slot 1: Zeilenquelle nicht in der referenzierten Tabellenzeile caption=True, row_label_in_table=True, row_match=False
- PMC13590641 Slot 2: Zeilenquelle nicht in der referenzierten Tabellenzeile caption=True, row_label_in_table=True, row_match=False
- PMC13590641 Slot 3: Zeilenquelle nicht in der referenzierten Tabellenzeile caption=True, row_label_in_table=True, row_match=False
- PMC13590641 Slot 4: Zeilenquelle nicht in der referenzierten Tabellenzeile caption=True, row_label_in_table=True, row_match=False
