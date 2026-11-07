# Befund: Erkennt ein Gate Baseline-Tabellen und SE-Spalten? (2026-11-08)

Frage vor einer Erweiterung des Zielmasses auf "sleep latency": Fängt ein Gate
die beiden Fehlerquellen ab, die im Abstract-Lauf aufgefallen sind - eine
Ausgangslagentabelle und eine Spalte mit Standardfehlern statt
Standardabweichungen?

Messung mit `scripts/measure_baseline_gate.py`, read-only, kein Modell, kein
Netz, zwei Reihen: die Q1-Stichprobe (22 Dokumente, 42 gespeicherte Zeilen) und
der ganze Korpus (1.027 Dokumente, 1.097 gespeicherte Zeilen). Zuordnung Zeile
-> Tabelle laeuft ueber das gespeicherte Zitat; in beiden Reihen waren 100 % der
Zeilen zuordenbar.

## 1. Wie haeufig sind solche Tabellen?

| Merkmal | Tabellen | Zeilen |
|---|---:|---:|
| Baseline-Caption | 499 von 2.704 (18,5 %) | 10.998 von 41.423 (26,6 %) |
| SE-Kopf ohne SD | 103 von 2.704 (3,8 %) | 1.733 von 41.423 (4,2 %) |

Jede vierte Tabellenzeile im Korpus steht also in einer Ausgangslagentabelle.
Das ist keine Randerscheinung, sondern die Regel in Studien mit
Demografietabelle.

## 2. Was das heutige Gate durchlaesst

| Reihe | Zeilen | Baseline-Caption | SE im Kopf | SE-Rolle erkannt | Baseline oder SE |
|---|---:|---:|---:|---:|---:|
| Q1-Stichprobe | 42 | 14 | 11 | 11 | 14 (33,3 %) |
| Korpus | 1.097 | 243 | 45 | 63 | 273 (24,9 %) |

In der Q1-Stichprobe sind **alle 14 Arm-Zeilen** aus Baseline-Tabellen
(Demografie, PSQI, ESS, Schlafeffizienz) - der Leser hat die
Ausgangslagentabelle vollstaendig als Behandlungseffekte gelesen.

## 3. Was das fuer die SOL-Zeilen bedeutet - Korrektur vom 08.11.

Die Messung oben arbeitet auf der Caption. Die Einzelpruefung der Zitate zeigt,
dass das fuer die vier Zeilen aus `10.1111/jsr.70311` ein **Falsch-Positiv**
war: ihre `comparison` lautet "Adjusted mean difference between groups", das
Zitat enthaelt Baseline-Werte, 6-Monats-Werte und die adjustierte Differenz
(3,8 min, 95 %-CI -3,5 bis 11,1). Gelesen wurde also die Differenz, nicht der
Ausgangswert.

| Quelle | Zeile | Urteil nach Zitatpruefung |
|---|---|---|
| `10.2147/nss.s460882` | OR 2,56 | Praediktortabelle zum Ausgangsstand ("A Better Outcome" gegen "Not") - kein Behandlungseffekt |
| `10.1111/jsr.70311` | 3,8 / 3,4 / 5,7 / 4,6 | **adjustierte Differenz zwischen Gruppen** - brauchbar |
| `10.3389/fnins.2026.1816963` | MD 2,12 | gepoolte Metaanalyse-Zeile - kein Primaerstudieneffekt |

Damit sind **2 der 13 Zeilen** unbrauchbar, nicht 6. Die Lehre: eine
Caption-Marke allein reicht nicht; das Gate muss die verwendeten Spalten
pruefen (siehe `baseline_columns_gate_20261108.md`).

## 4. Der SE-Teil ist kein Erkennungsproblem, sondern ein Lesefehler

Gemessen am Beispielkopf `Particulars | Placebo ( n = 35), mean +- SE | VE (
n = 37), mean +- SE`:

```
_col_semantics(header)  -> {1: 'se', 2: 'se'}          # erkannt
_role_columns(header)   -> {'sd': [], 'se': [1, 2], ...} # weitergereicht
parse_mean_spread("74.26 +- 5.24", role="se") -> (74.26, 5.24, "sd")
parse_mean_spread("74.26 +- 5.24", role="")   -> (74.26, 5.24, "sd")
```

Die Rolle ist also bekannt und wird **verworfen**: In
`research_agent/meta/arm_level.py` gibt der Zweig fuer "Wert +- Wert" unbedingt
`"sd"` zurueck, bevor `role` oder das Wort "SE" im Kopf ueberhaupt gelesen wird.
Ein Gate auf Zeilenebene kann das nicht reparieren; es ist ein Fehler im Leser.

Wirkung, nachgerechnet (nicht gespeichert, aus denselben Zellen):

| Groesse | mit `+-` als SD (heute) | mit `+-` als SE |
|---|---:|---:|
| SD Placebo / VE | 5,24 / 8,20 | 31,0 / 49,9 (aus SE und n) |
| Hedges g fuer "Sleep latency" | **-2,16** | **-0,36** |

Der Faktor zwischen beiden ist 6. Der gespeicherte Wert ist damit nicht nur
falsch etikettiert, sondern um eine Groessenordnung zu gross.

## 5. Antwort auf die Frage

- **Baseline-Tabellen: nur auf Spaltenebene.** Das Caption-Muster markiert
  Ausgangslagentabellen (14 von 14 Zeilen eines Dokuments), trifft aber auch
  Tabellen mit Baseline- und Follow-up-Spalten, in denen die adjustierte
  Differenz steht - bei `10.1111/jsr.70311` waeren so vier brauchbare
  SOL-Zeilen verloren gegangen. Die Spaltenpruefung verwirft 0 der 13
  SOL-Zeilen und 36 Zeilen im Korpus.
- **Kosten:** Eine reine Caption-Sperre wuerde bei `10.1111/jsr.70311` die
  ganze Tabelle verwerfen - dort stehen Baseline- und 6-Monats-Spalten
  nebeneinander, und die adjustierte Differenz derselben Tabelle ist
  moeglicherweise brauchbar. Ein Gate muss deshalb auf Spalten- und
  Zeitpunktebene greifen, nicht auf Tabellenebene.
- **SE-Spalten: nein, nicht als Gate.** Die Erkennung funktioniert; der Leser
  ignoriert das Ergebnis. Das ist ein Einzeiler in `parse_mean_spread`, kein
  neues Gate.
- **Zusaetzlich noetig:** ein Gate gegen gepoolte Metaanalyse-Zeilen
  (`MD [95%CI]` neben `I2` und `p`), sonst zaehlt eine Metaanalyse als Studie.

## 6. Grenzen

- Das Caption-Muster ist eine Untergrenze: Ausgangslagentabellen ohne das Wort
  "baseline" (etwa "Table 1. Participants") bleiben unentdeckt.
- Die Praezision ist an den 5 markierten SOL-Zeilen geprueft, nicht an allen
  243. Falsch-Positive unter den Nichttreffern sind nicht ausgeschlossen.
- Die Messung sagt nichts darueber, wie viele brauchbare SOL-Zeilen ein Gate
  kosten wuerde; dafuer muesste man die 7 verbleibenden Zeilen einzeln pruefen.
- Die Rechnung in Abschnitt 4 nutzt die Formel SD = SE * sqrt(n) und ist als
  Nachrechnung markiert, nicht als gespeicherter Wert.
