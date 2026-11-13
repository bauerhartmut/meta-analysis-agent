# PMC13590641 — Quellenprüfung der Arm-Nenner in Tabelle 3

## Gegenstand

Vier Sicherheits-Outcomes aus `PMC13590641` (ADVANCE) waren zuvor als
Zeilenbefund markiert, weil die Ereigniszahlen in der jeweiligen Tabellenzeile
stehen, die Nenner aber nur im Arm-Header von Tabelle 3. Geprüft wird, ob diese
Header-Nenner als zulässige Quelle für `total` gelten.

## Referenzierte Tabelle

- Label: **Table 3**
- Caption: **Most common adverse events of any cause in > 5%**
- Headerzeile im XML:

> Adverse event | Control group No. (%) (N = 19) | Experiment group No. (%) (N = 24) | P

Die Nenner sind damit unmittelbar über den jeweiligen Armspalten ausgewiesen
und den Armen eindeutig zugeordnet. Es handelt sich nicht um einen Treffer
irgendwo in der Tabelle oder in einem anderen Dokumentteil.

## Generatorprüfung

Der Audit-Generator prüft für diese Ausnahme nicht mehr nur das Vorkommen der
Zahl irgendwo im Tabellentext. Er liest die konkrete Headerzeile, ordnet die
Zelle mit `Control group` dem Kontrollarm und die Zelle mit `Experiment group`
dem Interventionsarm zu und verlangt `N = 19` beziehungsweise `N = 24` genau in
diesen beiden Zellen. Zusätzlich muss die Caption von Tabelle 3 exakt passen.
Ein N-Wert an anderer Stelle derselben Tabelle erfüllt die Ausnahme nicht.

## Slotprüfung

| Slot | Outcome | Interventionszeile | Kontrollzeile | N Intervention | N Kontrolle | Header-N zulässig |
|---:|---|---|---|---:|---:|---|
| 1 | Any adverse event, any grade | `Any events`: 23 (95.8) | `Any events`: 15 (78.9) | 24 | 19 | ja |
| 2 | Neutropenia, any grade | `Neutropenia`: 4 (16.7) | `Neutropenia`: 10 (52.6) | 24 | 19 | ja |
| 3 | Nausea, any grade | `Nausea`: 0 (0.0) | `Nausea`: 5 (26.3) | 24 | 19 | ja |
| 4 | Rash, any grade | `Rash`: 6 (25.0) | `Rash`: 1 (5.3) | 24 | 19 | ja |

Die Prozentwerte in Tabelle 3 sind mit diesen Nennern konsistent, zum Beispiel
`23/24 = 95.8 %`, `15/19 = 78.9 %`, `4/24 = 16.7 %`, `10/19 = 52.6 %`,
`0/24 = 0.0 %`, `5/19 = 26.3 %`, `6/24 = 25.0 %` und `1/19 = 5.3 %`.

## Entscheidung zur Quellenzulässigkeit

**Zulässigkeit: ja.** Ein armweise ausgewiesener N-Wert im Header derselben Tabelle ist eine
zulässige Quelle für den Nenner, sofern:

1. der Header den Arm und den N-Wert ausdrücklich nennt,
2. die referenzierte Outcome-Zeile eindeutig zu diesem Header gehört und
3. keine Werte aus einer anderen Tabelle oder aus Fließtext ersetzt werden.

Alle drei Bedingungen sind für die vier Slots erfüllt. Die Nenner `24` und `19`
sind nicht aus anderen Quellen abgeleitet, sondern stehen als
`(N = 24)` beziehungsweise `(N = 19)` in der referenzierten Tabelle 3.

## Auswirkung

- Die vier früheren Zeilenbefunde werden als **akzeptierte Header-Nenner**
  aufgelöst.
- Die Quellenprüfung weist damit **18/18** Tabellen-Outcomes als quellengedeckt
  aus: 12 Einzelzeilen zeilenexakt, 4 Einzelzeilen mit zulässigem Header-N und
  2 Kosten-Outcomes mit getrennten Zeilen.
- Die Outcome-Werte und die Zähler **8 unabhängig / 6 überlappend /
  22 nicht verwendbar / 14 formal verwendbar** bleiben unverändert.
- Dies ist keine finale Eignungs- oder Einschlussentscheidung; die
  menschliche Prüfung bleibt erforderlich.
