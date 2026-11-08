# E4 - deterministische Lueckenpruefung an den E3-Artefakten

Stand: 2026-11-08 23:08 · Modellaufrufe: 0 · Tokens: 0

Geprueft wird der MENDS-Satz, aus dem die E3-Zeilen stammen. Die Zeilen
kommen unveraendert aus den drei JSON-Artefakten; nichts wurde
nachgetragen.

Satz (254 Zeichen), 2 Intervalle:

```
A reduction in SOL, adjusted for baseline, was seen for melatonin compared with placebo when measured by sleep diaries (-37.49 minutes, 95% CI -55.27 to -19.71 minutes; p<0.0001) and actigraphy (-45.34 minutes, 95% CI -68.75 to -21.93 minutes; p=0.0003).
```

| Lauf | Zeilen | Intervalle | Status | Befund |
|---|---:|---:|---|---|
| E3a-24k-kontext | 1 | 1 | ok | Quote nennt 1 Intervall(e), 1 Zeile(n) - vollstaendig |
| E3b-isolierter-satz | 1 | 2 | luecke | Quote nennt 2 Intervalle, 1 Zeile(n) extrahiert - nicht belegt: -37.49 [-55.27; -19.71] |
| E3c-prompt-regel | 1 | 2 | luecke | Quote nennt 2 Intervalle, 1 Zeile(n) extrahiert - nicht belegt: -45.34 [-68.75; -21.93] |

## Gegenproben

- Beide gemessenen Zeilen zusammen: **ok** - Quote nennt 2 Intervall(e), 2 Zeile(n) - vollstaendig
- Satz ohne CI-Angabe: **nicht_pruefbar** - Quote nennt kein Konfidenzintervall - Luecke nicht pruefbar (keine falsche Luecke)

## Was das heisst

Die beiden Laeufe, die je eine korrekte Zeile geliefert haben, sind
Luecken: Die Quote nennt zwei Intervalle, die Kette haette k = 1
gepoolt. Der Check findet sie ohne Modellaufruf und ohne Sollwert -
er liest nur die Quote gegen die Zeilen. E3a ist der wichtigste
Negativfall: Seine Quote nennt genau ein Intervall, verschachtelt
geschrieben als `[95% confidence interval (CI) 0.52 to 44.34]`.
Ein Regex auf klammerfreie Inhalte haette sie uebersprungen und
`nicht_pruefbar` gemeldet; der Scanner zaehlt die Klammertiefe.

Grenzen: Die Zuordnung des fehlenden Intervalls laeuft ueber die Zahlen
und ist eine Diagnose. Die harte Aussage ist die Anzahl. Eine Zeile,
die zwei Intervalle zu einem zusammenfasst, gilt ebenfalls als Luecke.
