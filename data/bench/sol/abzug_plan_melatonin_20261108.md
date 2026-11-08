# Gezielter Abzug Melatonin/Einschaflatenz — Protokoll (ohne Lauf)

Stand 2026-11-08. Die Zahlen sind Zaehlabfragen gegen PubMed
E-utilities und Europe PMC (nur Metadaten, kein Volltextabruf, keine Pipeline).
Zweck: die Frage beantworten, ob der Agent mit guten Primaerstudien eine gute
Metaanalyse erzeugt - mit einer Zahl statt mit einem Gefuehl.

## 1. Queries

**Q1 breit** (Suche nach Kandidaten):
`melatonin[tiab] AND ("sleep onset latency"[tiab] OR "sleep latency"[tiab] OR "sleep onset"[tiab]) AND (randomized controlled trial[pt] OR randomi*[tiab] OR placebo[tiab])`
-> **329 Treffer**

**Q2 streng** (Grundlage des Laufs):
`melatonin[tiab] AND ("sleep onset latency"[tiab] OR "sleep latency"[tiab]) AND randomized controlled trial[pt]`
-> **114 Treffer**, davon 113 mit humans[mh]

**Zugang innerhalb von Q2:** 31 mit PMC-Volltext, 41 mit freiem Volltext.
Europe PMC zaehlt fuer dieselbe Frage 193, davon 20 mit OPEN_ACCESS:y - also
rund ein Fuenftel offen, der Rest braucht den Bibliothekszugang (TU Darmstadt,
in Arbeit). Fuer den Test heisst das: nicht jeder Treffer wird lesbar, und das
ist eingeplant.

## 2. Erwartete Ausbeute

Publizierte Metaanalysen poolen fuer dieselbe Frage 15 bis 26 Trials
(Ferracioli-Oda 2013: 19 Studien, 15 fuer SOL; Cruz-Sanabria 2024: 26 RCTs).
Bei 114 Treffern und rund 40 offenen Volltexten ist **k von 8 bis 15**
realistisch, also weit ueber der Schwelle k >= 2.

Der Engpass ist nicht die Zahl der Studien, sondern die **Arm-Ebene**: SOL als
Mittelwert mit Streuung je Arm, nicht als p-Wert oder Abbildung. Genau daran
sind die 43 Melatonin-Trials im alten Korpus gescheitert (34 nannten SOL ohne
Streuung, 3 mit Streuung, 0 mit Arm-Mittelwerten).

## 3. Ablauf (ein Netzlauf, vier Schritte)

1. **Metadaten**: esearch/efetch fuer Q2, Speichern von PMID, DOI, PMCID, Titel, Jahr.
2. **Volltext**: PMC-XML per efetch, wo vorhanden; alles andere wird als
   `Zugang offen` gefuehrt und **nicht** repariert (Paywall wird nicht umgangen).
3. **Extraktion**: die vorhandenen Leser, **unveraendert** - der Test soll den
   Agenten messen, nicht unsere Optimierung.
4. **Pooling und Bericht**: k, Einheit, Modell, CI; Vergleich mit der Referenz.

## 4. Erfolgskriterien (vor dem Lauf festgelegt)

| Kriterium | Schwelle |
|---|---|
| D1 Daten | Schritt-Ziel **k >= 2**, Gesamtziel **k >= 5** RCTs mit Arm-Mittelwerten in Minuten, jede Zeile mit quote_start (Praezisierung in 4a) |
| D2 Rechnung | gepoolte MD negativ und im publizierten CI -9,75 bis -4,37 min; bei ueberlappender Trialmenge zusaetzlich abs(Delta) <= 2 min |
| D3 Ehrlichkeit | Bericht nennt k, Einheit, Modell (HKSJ), CI; bei k < 2 kein gepoolter Wert |
| D4 Nachvollziehbarkeit | jede Zahl aus der DB rekonstruierbar; PRISMA-Zeilen = DB-Zeilen |

**Abbruch/Fehlschlag:** eine erfundene Zahl, eine falsche Einheit (min gegen h),
ein gepoolter Wert ausserhalb des Referenz-CI ohne Erklaerung, oder ein
gepoolter Wert trotz k < 2.

### 4a. Schwellen, praezisiert am 2026-11-08

Die urspruengliche Schwelle k >= 5 galt fuer die ganze Frage, wurde aber am
ersten Zugang gemessen - an fuenf bestellten Artikeln. Die Messung in
`data/bench/sol2/schwelle_k5_20261108.md` zeigt: von neun Dokumenten mit
Einschaflatenz-Zeilen sind vier Crossover, und von fuenf parallelen Studien
konvertiert eine. Bei dieser Quote erwartet man aus fuenf Artikeln **eine**
Studie; k >= 5 erreicht erst die A+B-Liste (25 Dokumente) mit rund 58 Prozent
Wahrscheinlichkeit.

Deshalb zwei Stufen:

| Ziel | Schwelle | Gilt fuer |
|---|---|---|
| Schritt-Ziel | k >= 2 | die fuenf A-Artikel |
| Gesamtziel | k >= 5 | A + B (25 Dokumente) |

Unveraendert bleibt: bei k < 2 kein gepoolter Wert (D3), und Crossover-Studien
werden ohne Within-Subject-Korrektur nicht mit SE(g) fuer unabhaengige Gruppen
gepoolt. Das Gesamtziel ist damit nicht abgeschwaecht, sondern an die Menge
gebunden, die es tragen kann.

## 5. Was bewusst nicht passiert

- Keine Aenderung an Lesern, Pooling oder k-Gate vor dem Lauf.
- Kein Umgehen von Paywalls; fehlende Volltexte bleiben als Luecke sichtbar.
- Keine zweite Frage gleichzeitig, kein zweiter Lauf ohne neue Freigabe.

## 6. Aufwand und Risiko

Ein Lauf: 114 Metadaten, rund 41 Volltexte offen, Rest als Luecke.
Extraktion und Bericht laufen offline. Risiken: Europe PMC antwortet bekannt
mit HTTP 500 (dann NCBI-Weg), Rate-Limits (eine Anfrage je 0,4 s), und ein
Query, der zu breit greift (329 Treffer) - deshalb wird Q2 verwendet,
nicht Q1.

## 7. Was der Lauf beantwortet

Wenn D1 bis D4 halten, ist die Frage belegt: der Agent kann aus guten
Primaerstudien eine belastbare, zur Literatur passende Metaanalyse erstellen -
und die Extraktionsarbeit der letzten Wochen war nicht umsonst, sondern hat
nur auf den falschen Korpus gewartet. Wenn D2 reisst, ist der Engpass
benannt (Rechnung oder Extraktion), und zwar zum ersten Mal an einer Stelle,
an der es etwas zu gewinnen gibt.
