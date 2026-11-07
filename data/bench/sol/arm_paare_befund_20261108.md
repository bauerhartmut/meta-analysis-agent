# Getrennte Mittelwert-/SD-Spalten im Arm-Rechner (2026-11-08)

Frage: Werden die 1.115 SOL-Tabellenzeilen lesbar, die an "keine Effektspalte
im Kopf" scheitern, wenn der Arm-Rechner Mittelwert und Streuung aus zwei
getrennten Spalten paart?

## Aenderung

`research_agent/meta/arm_level.py`:

- Neue Paarbildung `_paired_arms`: steht der Mittelwert in einer Spalte und die
  Streuung in der Nachbarspalte (`Melatonin Mean | Melatonin SD | Placebo Mean |
  Placebo SD`), werden beide zu einem Arm verbunden.
- Nur reine Zahlen werden gepaart; ein Bereich in der Streuungsspalte ist ein
  CI und bleibt dem Zwei-Zellen-Fall vorbehalten.
- `_role_columns` erkennt jetzt auch "Melatonin n" als Fallzahlspalte, nicht
  nur die Schreibweise "n = 25".
- Die Zwei-Zellen-Lesart ("38.2 (4.1)", "38.2 ± 4.1") bleibt vorrangig; die
  Paarung ergaenzt nur, sie ersetzt nichts.

Sechs neue Tests in `research_agent/tests/test_arm_level_pairs.py`
(Zwei-Arm-Paarung, g-Berechnung, SE-Umrechnung ueber sqrt(n), Intervall wird
nicht gepaart, Ein-Zellen-Arm bleibt vorrangig, fehlende Fallzahl wird
abgelehnt).

## Messung an den 1.367 SOL-Zeilen

| Kennzahl | vorher | nachher |
|---|---:|---:|
| SOL-Tabellenzeilen | 1.367 | 1.367 |
| davon von einem Leser gelesen | **18** | **18** |
| in den 7 Treffern | 13 | 13 |
| im Rest | 5 | 5 |

**Kein Gewinn.** Die Paarung greift, aber keine der 1.349 ungelesenen
SOL-Zeilen ist eine Zwei-Arm-Tabelle mit getrennten Mittelwert- und
SD-Spalten.

## Warum nicht: die echten Gruende (Stichprobe 260 Dokumente)

| Grund | Zeilen | Beispiel |
|---|---:|---|
| kein Mittelwert mit eindeutiger Streuung in zwei Spalten | 327 | Erzählspalte "CGA significantly shortened sleep latency ... (p = 0.043)" |
| direkter Effekt mit OR/RR/HR | 42 | Übersichtstabelle mit Textzellen zu Rebound |
| Fallzahl je Arm fehlt | 31 | "SOL was reduced in BB (12.0 ± 7.0 minutes) vs. Cx (19.0 ± 11.0)" - Textzelle, kein Zellpaar |
| nicht genau zwei Spalten mit Mittelwert und Streuung | 31 | Zeitreihe einer Gruppe: Baseline, Week 2-5 |
| zu wenige Spalten | 15 | Zeile "Sleep onset latency (min)" ohne Werte |

Die SOL-Zeilen sind also überwiegend **Erzähl- und Übersichtstabellen** oder
**Within-Subject-Zeitreihen** (eine Gruppe, mehrere Zeitpunkte). Beides ist
kein Zwei-Arm-Deskriptivum; die Ablehnung ist dort korrekt, nicht reparierbar.

## Was das fuer die naechsten Schritte heisst

- Weitere Tabellenfixes haben bei SOL wenig Aussicht: der groesste Posten ist
  Text in Tabellenzellen, kein Zahlenpaar.
- Der einzige passende Leser fuer diese Zeilen ist der **Fliesstext-Leser**
  (`arm_text`), der genau Saetze wie "SOL was reduced in BB (12.0 ± 7.0
  minutes) vs. Cx (19.0 ± 11.0 minutes)" verarbeitet - er fand im ganzen
  Korpus aber nur **1** Kandidaten. Dort liegt der naechste pruefbare Hebel.
- Die Faehigkeit selbst bleibt sinnvoll: sie erschliesst Zwei-Arm-Tabellen in
  anderen Endpunkten (im Gesamtkorpus 97 Arm-Zeilen), nur nicht bei SOL.

## Grenzen

- Die Grundverteilung stammt aus 260 von 946 Kandidaten (Stichprobe, nicht
  Gesamtlauf); die Lesbarkeitszahl 18 ist dagegen über alle 946 gerechnet.
- "Gelesen" heisst: ein Leser nimmt die Zeile an - nicht, dass die Zahl
  klinisch richtig ist.
- Die Paarung ist konservativ: ohne Fallzahlspalte wird weiter abgelehnt.

## Reproduktion

```
.venv/bin/python.exe scripts/sol_hit_profile.py --out data/bench/sol/sol_profil_arm_20261108
```

Vorher-Stand: `data/bench/sol/sol_profil_20261108_vorher.json`.
