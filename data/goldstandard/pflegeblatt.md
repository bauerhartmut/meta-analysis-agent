# Pflegeblatt: so wird der Goldstandard gegen Läufe geprüft (§9.2/§9.3)

## Was verglichen wird

Pro Goldstandard-Eintrag prüft der Benchmark-Runner drei Dinge:

1. **Studienauswahl (k):** wie viele poolbare Effektzeilen/Quellen der
   Lauf für denselben Ausschnitt liefert. Publizierte Metaanalysen
   decken mehr ab als eine autonome Runde — der Vergleich ist eine
   **Decken-Warnung**, kein Fehlerscore (dafür steht die
   Precision/Recall-Messung der Studienauswahl).
2. **Zahlenextraktion:** trägt der Agent Einzelwerte (Wert, SE, CI)
   verbatim aus den Quellen, ohne Verfälschung? Geprüft über den
   verbatim-Zitierkontrakt (Sprint-7-Regel: verbatim oder Warnung).
3. **Pool-Abweichung:** liegt der vom Agenten gepoolte Wert (auf die
   Skala des Goldstandards normalisiert) in der Toleranzzone um den
   Referenzwert?

## Toleranzen (fest, nicht pro Lauf verhandelbar)

| Vergleich | Toleranz | Folgen |
|---|---|---|
| Agent-Hedges_g vs. Goldstandard-Hedges_g (gleiche Population) | \|Δ g\| ≤ 0,15 UND CI-Überschneidung | PASS |
| etwas weiter draußen | \|Δ g\| ≤ 0,30 | grenzwertig (Report-Eintrag, kein FAIL) |
| darüber hinaus | jede weitere Abweichung | FAIL (Benchmark schlägt an) |
| Population nicht übereinstimmend (z. B. schlafdepriviert) | kein Zahlenvergleich | nur „Populations-Kontrast" ausweisen |

## Strenge (die Realitätsprüfung, nie der Tonfall)

- Ein Poolwert des Agenten zählt nur, wenn er mit gepoolter SE/CI und
  k ≥ META_MIN_STUDIES berichtet wird (wie im Bericht).
- Ein Goldstandard-Eintrag ohne menschliche Abnickung
  (Status „agent-Sekundärquelle") erzeugt keinen FAIL: die
  Abweichungsbewertung läuft, der Report merkt aber an, dass die
  Referenz noch nicht menschlich verifiziert ist. Der Auftrag verlangt
  „menschlich verifizierte Referenzwerte" — nichts geht still darüber
  hinweg.

## Wie die Referenzwerte nachgeprüft werden (für die Abnickung)

- Kløve & Petersen 2025: PMID 40335666 → PubMed-Abstract öffnen,
  Zahlen gegenprüfen (RT g = 0,28 / ACC g = 0,27 mit den CIs).
- Calvo 2021 / Oliver 2022 / Diaz-Lara 2024: DOI öffnen — das
  Abstract-Zitat steht wörtlich in goldstandard.md, Ziffern vergleichen.
- Irwin 2020: Verlags-PDF laden (Repository-Link im Eintrag), danach
  Journal + Band nachtragen.

## Pflege

Neue Referenz? Zeile in `goldstandard.csv` plus Abschnitt in
`goldstandard.md` (mit Zitat, URL und Status). Immer genau eine Quelle
pro Zahlenwert pflegen — Doppelhaltung vermeiden.
