# Direkte Effektspalten: k bleibt 1

Stand: 2026-11-08T13:02:02. Deterministisch, kein Netz, kein Modell.

## Strikter Durchgang

| Kennzahl | Wert |
|---|---:|
| gescreente Dokumente | 20 |
| gespeicherte Effektzeilen | 16 |
| davon auf der Einschaflatenz | **0** |
| Dokumente mit poolbarer SOL-Zeile (k) | **0** |

Die 16 gespeicherten Zeilen betreffen andere Endpunkte. Gruende, warum
SOL-Zeilen nicht durchkommen (Top 5):

-   473  keine Effektspalte im Kopf
-   103  Kopfzeile (7 Spalten) passt nicht zur Zeile (5 Zellen) - colspan nicht
-    44  Kopfzeile (6 Spalten) passt nicht zur Zeile (1 Zellen) - colspan nicht
-    38  keine Kopfzeile
-    26  Kopfzeile (6 Spalten) passt nicht zur Zeile (5 Zellen) - colspan nicht

## Warum keine SOL-Zeile durchkommt

Diagnose ueber alle gescreenten Dokumente: 30 SOL-Zeilen, davon 8 mit einem
Intervall in der Zeile und 7 mit einem Kopf, der ein CI nennt. In **keiner**
dieser 7 erkennt der Leser ein Effektwort. Die drei Faelle:

- **PMC3489506, Tabelle 9**: Kopf "Sleep onset latency (SOL) Estimate
  (95% CI)", Zelle "WMD: -13.2 (-27.3 to 0.9)". Das ist die
  Zusammenfassung fremder Metaanalysen, keine Studienzeile - sie muss
  draussen bleiben, sonst werden dieselben Trials doppelt gezaehlt.
- **PMC5774131**: Kopf "Treatment effect estimate (95% CI)", Zeile
  "Sleep latency, minimum b" mit 1.37 (1.26 to 1.48) - ein Verhaeltnis,
  keine Minutendifferenz.
- **PMC2933606**: Kopf "Short term Estimate (95% CI) P-value", Zelle
  -0.6 (-14.0, 12.7). Sieht nach Minuten aus - ist aber nicht belegt:

  In derselben Tabelle steht "Sleep latency: -9.0 (50.5)" und direkt
  darunter "Sleep onset: -0.15 (0.89)". Zwei verschiedene Skalen in einer
  Tabelle, und der Kopf nennt keine Einheit. Die Zahl als Minuten zu lesen
  waere eine Annahme, keine Messung.

## Annahme-Durchgang (Einheit aus der Zeile)

Ergebnis: 0 Zeilen, k = 0. Auch hier nichts, weil die
Zeile die Einheit nicht nennt ("Sleep latency" ohne "(min)"). Der
Durchgang bleibt im Repo, dokumentiert aber nur, dass die Annahme nicht
tragfaehig ist.

## Folgerung

**k bleibt bei 1.** Der direkte Weg hebt die Ausbeute in diesem Korpus
nicht: die vorhandenen SOL-Effekte sind entweder gepoolte Schaetzungen aus
Uebersichtsarbeiten oder Schaetzungen ohne genannte Skala. Das ist kein
Leserfehler, den man mit mehr Regeln beheben koennte, ohne Werte zu
erfinden.

Damit steht der Befund: aus den 31 offenen Volltexten des Q2-Abzugs ist
eine poolbare Melatonin-SOL-Metaanalyse nicht zu bauen - k = 1, nicht 5.
Die 83 Dokumente ohne PMC-Volltext sind der naechste echte Hebel.
