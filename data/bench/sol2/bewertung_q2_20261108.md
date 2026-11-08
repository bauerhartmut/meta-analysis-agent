# Q2-Lauf: Bewertung gegen die vier Kriterien

Stand 2026-11-08. Ein Netzlauf (esearch + efetch), danach alles offline.
Die Leser liefen unveraendert, wie im Protokoll festgelegt.

## 1. Was gelaufen ist

| Schritt | Ergebnis |
|---|---:|
| esearch Q2 | 114 Treffer |
| Metadaten (efetch) | 114 |
| Volltext-XML aus PMC | 31 (27 %) |
| ohne PMC-Volltext | 83, als "Zugang offen" gefuehrt, nicht repariert |
| Tabellenzeilen geprueft | 1.016 |
| Saetze geprueft (Fliesstext-Leser) | 4.733 |
| gespeicherte Arm-Zeilen | 13 |
| gespeicherte Fliesstext-Zeilen | 0 |
| **Zeilen auf der Einschaflatenz** | **0** |

Der Schnitt gegen das Zielmass findet in den neuen Mess-DBs: 5 Zeilen
"Schlaf" (ohne Einschaflatenz), 8 "anderes", 0 SOL.

## 2. Die vier Kriterien

| Kriterium | Schwelle | Ergebnis | Urteil |
|---|---|---|---|
| **D1 Daten** | k >= 5 RCTs mit Arm-Mittelwerten in Minuten | k = 0 | **nicht erfuellt** |
| **D2 Rechnung** | gepoolte MD im CI -9,75 bis -4,37 min | nicht berechenbar (k < 2) | **nicht pruefbar** |
| **D3 Ehrlichkeit** | kein erfundener Wert, k und Einheit genannt | kein gepoolter Wert erzeugt (richtig), aber 11 von 13 Zeilen sind Baseline-Charakteristika | **teilweise** |
| **D4 Nachvollziehbarkeit** | jede Zeile mit belegtem Zitat | alle 13 Zeilen tragen ein woertliches Zitat | **erfuellt** |

Zu D3 im Detail: von den 13 gespeicherten Zeilen sind 11 Baseline-Merkmale
(Alter, Geschlecht, BMI, PSQI zu Studienbeginn), keine Behandlungseffekte.
Beispiel: "Male, n (%)" mit einem g von 0,004 und einer Streuung von 270,4.
Das Gate hat alle 13 durchgelassen, weil es Form prueft, nicht Plausibilitaet.
Waere eine dieser Zeilen poolbar gewesen, waere sie als Effekt berichtet worden.

Zu D4: Nachvollziehbarkeit ist kein Qualitaetsnachweis. Ein Zitat belegt, dass
die Zahl im Dokument steht, nicht dass sie das Richtige misst.

> **Nachtrag 2026-11-08** (nach der Messung in `schwelle_k5_20261108.md`):
> Die Schwelle D1 wird zweistufig gefuehrt - Schritt-Ziel k >= 2 fuer die fuenf
> A-Artikel, Gesamtziel k >= 5 fuer A + B. Das Urteil dieses Laufs (k = 0,
> D1 nicht erfuellt) bleibt unveraendert; geaendert ist nur, woran der naechste
> Schritt gemessen wird.

## 3. Warum k = 0: der Leser, nicht die Literatur

Von den 31 Dokumenten enthalten **12 Einschaflatenz-Zeilen in Tabellen**,
zusammen 93 Zeilen. Nach Form:

| Form | Zeilen | Beispiel |
|---|---:|---|
| A: zwei Arme, mean +- SD | 3 | `28.06 ± 27.46 | 21.02 ± 17.45 | .037` |
| B: mean (SD) in Klammern | 14 | `102.0 (72.6) | 54.8 (51.9)` |
| C: vier Werte (Baseline + Follow-up) | 2 | `58.4 ± 15.5 | 54.3 ± 15.3 | 53.2 ± 16.9 | 46.9 ± 11.0` |
| D: Median/IQR | 1 | `25 (15–55) | 23 (13–52)` |
| E: nur ein Arm / Verlauf | 2 | `23.6 ± 19.1` |
| F: kein Zahlenwert in der Zeile | 69 | Anteilswerte, Verweise, Kopfzeilen |

Fuenf Dokumente tragen arm-level Einschaflatenz (PMC11103136, PMC10796483,
PMC4365553, PMC3489506, PMC2933606). **Keines** wurde zu einer poolbaren
Zeile. Die Ablehnungsgruende sind mechanisch und benennbar:

- **n fehlt in der Tabelle** (A): `28.06 ± 27.46 | 21.02 ± 17.45 | .037` wird
  abgelehnt, obwohl die Fallzahl im Text steht.
- **Klammerformat** (B): 14 Zeilen, davon 10 aus PMC2933606 (prolonged-release
  Melatonin bei primaerer Insomnie) - der Leser kennt nur `+-`.
- **Zeitpunkte** (C): vier Werte je Zeile werden als "gemischte Zeitpunkte"
  verworfen, statt Baseline von Follow-up zu trennen.

Der Leser deckt damit **eine von sechs** vorkommenden Formen ab.

## 4. Ein zweiter Fehler: das Screening fehlt

Von 31 Titeln sind **17 keine Melatonin-Studien** (Baldrian, Sauerkirsche,
Ramelteon, Tasimelteon, Dexmedetomidin, Sport, Vitamin E). Sie treffen den
Query, weil Melatonin im Abstract als Vergleichs- oder Hintergrundbegriff
auftaucht - die Suche fragt `[tiab]`, nicht den Titel.

Die einzige konvertierte SOL-Zeile des Laufs stammt aus **PMC10796483
(Valeriana officinalis)**: `Sleep latency (min) by WA | 74.26 ± 5.24 |
89.39 ± 8.20`. Ohne Titelscreening waere ein Baldrian-Effekt als
Melatonin-Effekt gepoolt worden. Das ist kein Randfall, sondern der
wahrscheinlichste Weg zu einer falschen Metaanalyse.

## 5. Antwort auf die Frage

**Kann der Agent mit guten Primaerstudien eine gute Metaanalyse erstellen?
Derzeit nicht - aber nicht wegen der Studien und nicht wegen der Rechnung.**

Der Korpus ist jetzt richtig: 114 Treffer, 12 Dokumente mit Einschaflatenz-
Zeilen, darunter die klassischen Melatonin-Insomnie-Trials. Die Statistik
wurde nie erreicht; sie ist nicht der Engpass. Der Engpass ist die Abdeckung
der Tabellenlayouts (1 von 6 Formen) plus das fehlende Titelscreening.

Das ist die erste Diagnose in dieser Untersuchung, die an einer Stelle sitzt,
an der ein Fix etwas bewirkt: Die Daten sind da, sie werden nur nicht gelesen.

## 6. Was ein zweiter Durchgang braucht (Schaetzung, nicht gemessen)

- Leser fuer Form B (Klammer-SD), C (Baseline vs. Follow-up) und n aus dem
  Text: 19 Zeilen in 5 Dokumenten.
- Titelfilter `melatonin` plus Ausschluss von Agonisten und Co-Interventionen:
  14 statt 31 Dokumente.
- Erwartung nach Screening: **k = 3 bis 5** (Schaetzung). Die Schwelle D1
  (k >= 5) ist damit erreichbar, aber nicht gesichert.
- Kosten: **kein Netzlauf** - die 31 XML liegen unter `data/bench/sol2/xml`.

## 7. Grenzen

- 83 Dokumente ohne PMC sind nicht gelesen; k = 0 ist eine Untergrenze, kein
  Beweis, dass es keine Daten gibt.
- Nur Tabellen und Fliesstext; Abbildungen (Kaplan-Meier, Forest-Plots) sind
  nicht lesbar.
- Die Formklassifikation ist eine Heuristik auf Zelltexten, keine manuelle
  Kodierung; die 5 Dokumente mit arm-level SOL sind gesichtet, nicht
  vollstaendig verifiziert.
