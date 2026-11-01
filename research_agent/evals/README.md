# Ground-Truth Quality Eval (Paket D)

Deterministisches Ground-Truth-Evaluations-Tool, das misst, ob und wie gut die
aktuelle Wissensbasis des Research-Agenten ein goldenes Set aus Seed-Fragen
abdeckt. Zweck: den früheren Zustand „benchmark.py misst nur Zeit, keine
Korrektheit“ beheben und „wird besser?“ messbar machen.

## Dateien

| Datei | Zweck |
|---|---|
| `golden_answers.json` | Golden-Set: 10 Seed-Fragen mit je 2–4 goldenen Claims + optional `gap_checks`. |
| `quality_eval.py` | Score-Mechanismus + CLI-Einstieg (Korpus: DB-Facts/-Hypothesen/-Evidenz + Reports aus `data/dataset/*.md` und `data/reports/*.md`). |
| `report_eval.py` | Evaluationsschleife für die Single-Shot-Deep-Research-Reports (PAKET H): scoret einen einzelnen Report gegen den passenden goldenen Claim und schreibt einen Score-Verlauf (`eval_history.jsonl`) für den Trend. |
| `README.md` | Diese Doku. |

## Report-Eval (PAKET H) verwenden

```bash
# Einen Deep-Research-Report gegen die passende goldene Frage scoren + Verlauf speichern:
python -m research_agent.evals.report_eval \
    --report data/reports/wilson_20260831_120000.md \
    --question "Was demonstriert der Wilson-Effekt...?" \
    --record data/reports/eval_history.jsonl

# Oder explizit per golden id; optional Deep Research direkt laufen lassen:
python -m research_agent.evals.report_eval --golden-id q01_wilson_effect --record data/reports/eval_history.jsonl
python -m research_agent.evals.report_eval --golden-id q01_wilson_effect --run-deep --record data/reports/eval_history.jsonl

# Trend aus der History:
python -m research_agent.evals.report_eval --trend data/reports/eval_history.jsonl
```

`report_eval` verwendet exakt die gleichen deterministischen Heuristiken wie
`quality_eval` (Claim-Recall + Number-Accuracy gegen den besten Einzeleintrag) und
`geschäftet` per `--record` jede Messung mit Zeitstempel, golden id und Dateinamen
an. So siehst du, ob die Deep-Research-Pipeline über Läufe hinweg besser wird.

## Was wird gemessen (pro Frage und gesamt)

1. **Claim Recall** (0–1): Für jeden goldenen Claim wird geprüft, ob EIN EINZELNER
   Wissenseintrag mindestens 70 % der charakteristischen Terme des Claims abdeckt
   (IDF-gewichtet: seltene, unterscheidende Terme zählen mehr) **und** alle vom
   Claim behaupteten Zahlen enthält. Matching gegen den besten Einzeltreffer
   (nicht den zusammengeklebten Korpus) verhindert, dass redundante Einträge
   fehlende Evidenz vortäuschen.
2. **Number/Fact Accuracy** (0–1): Anteil der konkreten Zahlenwerte in den goldenen
   Claims, die in der Wissensbasis vorkommen (flexible Schreibweisen z. B.
   `0.80` / `80 %`, `3,952` / `3952`).
3. **Gap Checks** (0–1): Optional pro Frage definierte erwartete Identifikatoren
   (z. B. konkrete Länder, benannte ethische Rahmenwerke, quantitative IQ-Gewinn-
   Angabe). Ein Gap Check ist erfüllt, wenn einer seiner exakten Strings irgendwo
   im Korpus auftaucht. Sie decken erwartete Inhalte auf, die aktuell FEHLEN.

Composite je Frage und gesamt:
`100 * (0.7 * claim_recall + 0.3 * number_accuracy)`. Gap Checks werden separat
ausgewiesen, damit kein Signal verwischt.

## Wie ausführen

```bash
# Standardlauf gegen die aktuelle research.db (Korpus = Facts + Hypothesen +
# Evidenz + Synthese-Reports; schreibgeschützt, keine Agent-Logik-Änderung)
python -m research_agent.evals.quality_eval

# Explizite DB / Report als JSON
python -m research_agent.evals.quality_eval --db research_agent/data/research.db
python -m research_agent.evals.quality_eval --json eval_report.json

# Größeren Korpus einbeziehen (rohe Quellen-Titel/Summaries bzw. alle
# Journal-Findings) – erhöht die Abdeckung, kann aber echte Lücken maskieren
python -m research_agent.evals.quality_eval --with-sources
python -m research_agent.evals.quality_eval --with-journal
```

## Wie lesen

- `claim_recall = 1.00 (3/3)` → alle 3 goldenen Claims der Frage von der
  Wissensbasis getragen.
- `num_acc = 1.00 (5/5)` → alle 5 behaupteten Zahlen vorhanden.
- `gaps = 0.00 (0/1)` → der erwartete Identifikator fehlt (OK, dass der Eval das
  zeigt; das ist der gewünschte „ist besser geworden?“-Signal).
- `OVERALL composite` → Gesamtwert; steigt, wenn die Wissensbasis im Laufe der
  Zyklen Claims und konkrete Zahlen zuvor fehlender Topics aufnimmt.

## Grundsätze / Grenzen

- Golden Claims werden NUR aus vorhandenen Daten/Quellen übernommen – kein
  erfundener Fachinhalt. Quelle je Claim ist im JSON notiert.
- Der Eval ist strikt ausgelagert: öffnet die DB schreibgeschützt, legt keine
  Agent-Logik an, ändert keine Dateien außerhalb `research_agent/evals/`.
- Matching ist ein deterministischer Proxy; für subjektive Qualität kann als
  nächster Schritt ein `LLM-as-Judge`-Modus ergänzt werden.

## Wichtiger Baseline-Befund (31.08.2026)

Das Golden-Set wurde am 31.08.2026 um **9 re-recherchierte, extern belegte Claims**
erweitert (fremdquellen, NICHT aus `research.db` abgeleitet), um den ursprünglich
saturierten Score zu de-saturieren: Polderman 2015 (h²-Meta, 2 748 Studien/49 %), Lee 2018
(1,1 Mio./1 271 Varianten), Savage 2018 (n=269 867/205 Loci), Yengo 2022 (5,4 Mio./12 111
SNPs/40 %), HFEA PGT-M (>2 000 monogene Erkrankungen), Agar 2004 (Liberal Eugenics),
Bratsberg & Rogeberg 2018 (730 000 Wehrpflichtige, −0,2 P/Jahr), Turley 2021 und
Karavani 2019 (≈2,5 IQ-Punkte Embryoselektion).

Neue Gesamt-Baseline gegen die aktuelle `research.db` (40 Claims): **composite ≈ 69,8**,
claim_recall ≈ 0,80 (32/40), number_accuracy ≈ 0,46 (18/39) — deutlich unter 100 und damit
wieder differenzierend. Die Fragen mit den neuen Außenzahlen (q02 GWAS, q04 height-SNPs,
q09 Norwegen, q10 IQ-Gewinn) fallen am stärksten ab; das sind die gezielten Lücken.

Wichtig: Werden diese Claims in einem Deep-Research-Report korrekt mit Zahlen + Quelle
abgedeckt, steigt der Score wieder — der Report-Eval misst also jetzt echte Wissens-/Zahlen-
abdeckung statt bloßer DB-Tautologie.

Die 3 Gap-Checks (Länder, benanntes Rahmenwerk, IQ-Gewinn-Schätzung) bleiben ausstehende
erwartete Inhalte (alle MISS) und sind unabhängige Lücken-Signale.