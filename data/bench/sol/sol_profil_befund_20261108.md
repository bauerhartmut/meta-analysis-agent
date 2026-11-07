# Was die 7 SOL-Treffer von den uebrigen 939 unterscheidet (2026-11-08)

Frage: Der Korpus hat 946 Dokumente, die das grobe SOL-RCT-Muster erfuellen,
aber nur 7 liefern eine gespeicherte Einschlaflatenz-Zeile. Woran liegt das -
an der Suche oder am Lesen?

Offline, ohne Netz und ohne Modell, auf `data/bench/sol/xml/`.

## Gruppenvergleich (Merkmale je Dokument, Median)

| Merkmal | 7 Treffer | 939 uebrige | Regel (Recall / Basis) |
|---|---:|---:|---|
| gespeicherte Kandidaten | 12 | **0** | >= 1: 100 % / 5 % |
| lesbare SOL-Zeile | 1 | 0 | >= 1: 100 % / 0 % |
| Effektspalte im Tabellenkopf | 1 | 0 | >= 1: 57 % / 11 % |
| SOL in einer Tabellenzeile | 1 | 0 | >= 1: 100 % / 45 % |
| Tabellen | 3 | 2 | >= 1: 100 % / 86 % |
| Zeilen | 42 | 30 | >= 1: 100 % / 86 % |
| SOL-Nennungen im Text | 10 | 5 | >= 1: 100 % / 100 % |

Zwei Dinge fallen auf:

1. **SOL steht fast immer in irgendeiner Tabellenzeile** - bei 45 % der
   Nichttreffer. Die Suche ist also nicht das Problem: das Material ist da.
2. **Nur die Treffer haben gespeicherte Kandidaten** (Median 12 gegen 0).
   Der Unterschied entsteht beim Lesen der Zeile, nicht beim Finden des
   Dokuments.

## Die SOL-Zeilen selbst

| Kennzahl | Wert |
|---|---:|
| SOL-Tabellenzeilen im Korpus | 1.367 |
| davon von einem Leser gelesen | **18** |
| davon in den 7 Treffern | 13 |
| davon im Rest | 5 |

Gate der 1.349 ungelesenen SOL-Zeilen:

| Grund | Zeilen |
|---|---:|
| keine Effektspalte im Kopf | **1.115** |
| keine Kopfzeile | 65 |
| Kopfzeile passt nicht zur Zeile (colspan) | 61 (uebrige Faelle einzeln) |

**1.115 von 1.349** SOL-Zeilen sind Arm-Tabellen: Mittelwert und Streuung
stehen als Deskriptiva da, nicht als fertige Effektspalte. Der Arm-Rechner
verlangt aber "einen Mittelwert mit eindeutiger Streuung in zwei Spalten" und
verwirft den Rest (im Gesamtlauf 30.680 Zeilen genau mit diesem Grund).

## Was daraus fuer die Suchstrategie folgt

- **Keine breitere Suche.** Der Korpus enthaelt 1.367 SOL-Zeilen; ein neuer
  Netzlauf wuerde mehr Dokumente holen, nicht mehr lesbare Zeilen.
- **Keine schaerfere Keyword-Regel.** Die Merkmale trennen die Gruppen nur
  schwach: SOL in einer Tabellenzeile hat 100 % Recall, aber 45 % Basis; eine
  Regel daraus spart die Haelfte des Korpus und riskiert die Treffer.
- **Der Hebel ist der Arm-Rechner.** Wenn Mittelwert und SD in getrennten
  Spalten stehen (Kopf `Melatonin Mean | Melatonin SD | Placebo Mean |
  Placebo SD`), muss die Spaltenrolle aus dem Kopf kommen - die Rollenlogik
  (`_col_semantics`) existiert bereits, der Arm-Rechner nutzt sie aber nicht
  fuer die Paarbildung.

## Grenzen

- **Sieben Treffer sind keine Stichprobe fuer eine Prognose.** Die
  Recall-Werte sind an denselben Dokumenten gemessen, aus denen die Regel
  stammt; als Diagnose taugen sie, als Klassifikator nicht.
- "Lesbar" heisst: ein Leser nimmt die Zeile an, nicht: die Zahl ist richtig.
- Die 5 lesbaren SOL-Zeilen ausserhalb der 7 Treffer stammen aus Dokumenten,
  deren Outcome-Label nicht auf SOL normalisiert - sie fehlen im Zielmass-
  Schnitt, nicht im Korpus.

## Reproduktion

```
.venv/bin/python.exe scripts/sol_hit_profile.py
```

Ausgabe: `data/bench/sol/sol_profil_20261108.json` (Merkmale je Dokument,
Gruppenvergleich, Gate-Zaehler).
