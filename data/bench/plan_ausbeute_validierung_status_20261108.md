# Plan „Ausbeute, Validierung, Ehrlichkeit" — Abgleich mit dem Arbeitsstand

Stand: 08.11.2026. Quelle des Plans: PDF „Plan: Metaanalyse-Agent – Ausbeute,
Validierung, Ehrlichkeit" (07.11.2026, 8 Seiten), Bezug:
`docs/briefing_modell_20261107.md`. Geprüft wird paketweise, was im Repo
tatsächlich existiert und was nicht.

## Kurzbilanz

| Paket | Status | Beleg | Offen |
|---|---|---|---|
| A — Ausbeute-Funnel | umgesetzt, ohne Obergrenze | `scripts/funnel_sol.py`, `data/bench/sol/funnel_20261108.{json,md}`, `research_agent/tests/test_funnel_sol.py` | Obergrenze (menschliche Sichtung), Trennung legitim/Defekt |
| E — ehrlicher Bericht | umgesetzt | `report.py` (Abschnittsverweigerung, PRISMA-Tabelle), `test_report_honesty.py`, `test_meta_report.py` | keiner; der fehlende PRISMA-Test wurde am 08.11. ergänzt |
| C — Tabellenpfad härten | gemessen statt gebaut, gestoppt | `colspan_befund_20261108.md`, `ergebnisstand_20261108.md` | Hold-out 70/30, Präzisions-Audit, Benchmark-Fixtures |
| B-a — Referenz (Mathematik) | teilweise | `research_agent/tests/test_pooling_reference.py` | externer Datensatz, `fixtures/reference/`, `scripts/compare_reference.py` |
| B-b — Referenz (End-to-End) | blockiert | — | Zugang zu den 7 Trials |
| D — Screening gegen Thementrift | nicht begonnen | `meta/screening.py` ist der Review-Rahmen, nicht das Vor-Gate | `screening_eval.py`, `annotated.json`, die drei Screening-Tests |

## A — Ausbeute-Funnel

Der Funnel existiert und ist reproduzierbar. Seine Stufen (`funnel_20261108.md`):
1.059 Manifest-Einträge, 1.056 XML vorhanden, 3 fehlend, 946 SOL-RCT-Kandidaten,
2.735 erkannte Tabellen, 41.821 Tabellenzeilen, 315.857 Sätze, 1.115 Kandidaten
aller Leser, 523 gespeichert, 152 poolbar. Größter Verlust: `zeilen -> kandidaten`
mit 40.706 von 41.821 (97,3 %). Die Tests decken Stufensummen, erschöpfende
Ablehnungsgründe („unbekannt" nur als Zähler), Verlust-Rangliste und den
Endpunkt gegen die Mess-DBs ab; der Endpunkt-Test überspringt sich, wenn die
gitignorten DBs fehlen.

**Abweichung vom Plan, bewusst:** Der Plan sagt „Die 3 HTTP-500-PMCIDs werden
nicht nachgeladen", weil 3 von 1.059 vernachlässigbar seien. Sie wurden
nachgeladen (NCBI efetch statt Europe PMC), ebenso die 10 fehlenden Dokumente
der Stichprobe: 13 XML, 62 + 4 Tabellenzeilen, 0 Effekte. Grund: der Befund
lautet „kein poolbarer Effekt"; über ungelesene Dokumente wäre das eine
Behauptung, nicht eine Messung.

**Offen — die Obergrenze.** Sie ist als Dokumentmenge nicht gemessen; sie
braucht die vom Plan vorgesehene menschliche Sichtung der SOL-Kandidaten. Was
gemessen ist: nach Design- und Baseline-Gates bleiben 11 SOL-Zeilen aus 5
Quellen, und unabhaengig davon ist k = 0 (seit der Vorsichtung vom 08.11.) (`ergebnisstand_20261108.md`). Ohne die
Obergrenze bleibt die Trennung „legitim verloren / Leserdefekt" offen.

## E — ehrlicher Bericht

Umgesetzt ist mehr, als der Plan verlangt: `report.py` verweigert den gepoolten
Abschnitt auf Abschnittsebene, wenn keine Gruppe die Schwelle erreicht
(„Kein gepoolter Effekt in diesem Bericht."), die PRISMA-Tabelle zählt nur
DB-Zeilen, und die Zeile „Zielmaß-Abdeckung:" steht vor dem ersten Abschnitt.
`test_report_honesty.py` prüft k = 0 strukturell (keine Zeile
„Gepoolter Effekt (Random Effects"), `test_meta_report.py` prüft zusätzlich
k = 1 („Kein gepoolter Wert", „k = 1", kein gepoolter Effekt).

**Am 08.11. ergänzt:** `PrismaMatchesDatabaseTest` — die drei tragenden
PRISMA-Zeilen (Quellen im Bestand, Effektzeilen gesamt, davon diskrepant)
werden gegen eine unabhängige SQL-Zählung geprüft, nicht gegen die Funktion,
die den Bericht füllt. Genau dieser Test fehlte aus dem Plan.

## C — Tabellenpfad

C ist als Umbau nicht begonnen, aber der Plan nennt selbst ein Abbruchkriterium:
„zwei Sitzungen in Folge ohne Zuwachs an poolbaren SOL-Zeilen". Dieses
Kriterium ist erfüllt — gemessen, nicht geschätzt:

| Hebel | Ausbeute | SOL |
|---|---|---|
| Mehrzeilige Kopfzeilen (colspan/rowspan) | +576 Kandidaten, 523 → 1.099 gespeichert | 13 → 13 (0) |
| Outcome-Label aus Zwischenüberschrift/Caption | Zeilen ohne Label 232 → 2 | 13 → 13 (0) |
| Arm-Rechner paart getrennte Mean-/SD-Spalten | poolbar 152 → 422 | 18 → 18 (0) |
| Fließtext-Leser | 1 zusätzliche Zeile | 0 lesbar (0) |

Dazu die Messung, die den Spaltenauflöser begründen sollte: 342 Zeilen mit
Kopf/Zellen-Mismatch, davon 5 Kopfzeilen mit Effektbezeichnung und **0 echte**
(`colspan_befund_20261108.md`). C wird damit nicht „verschoben", sondern durch
seine eigene Regel beendet.

Offen bleiben die drei Zusatzauflagen des Plans, die unabhängig vom Zuwachs
sinnvoll wären: Hold-out 70/30 per DOI-Hash, Präzisions-Audit geretteter
Zeilen, Regressions-Fixtures in `research_agent/evals/meta_benchmark.py`.

## B — Referenzdatensatz

B-a ist teilweise erfüllt: `test_pooling_reference.py` rechnet Fixed-Effect,
Cochran Q, DerSimonian-Laird, Hartung-Knapp und das Prediction Interval mit
einer unabhängigen Zweitimplementierung nach. Das Testmodul sagt selbst, was
fehlt: ein Abgleich gegen `metafor` (z. B. `dat.normand1999`) oder statsmodels
ist in dieser Umgebung nicht möglich. Es gibt weder
`research_agent/tests/fixtures/reference/` noch `scripts/compare_reference.py`.
B-b braucht Zugang zu den 7 Trials der Sleep-Medicine-Metaanalyse — ohne den
kein End-to-End-Vergleich und damit kein Satz „validiert" ohne Zusatz.

## D — Screening

`research_agent/meta/screening.py` existiert, ist aber der Review-Rahmen
(Protokoll einfrieren, Entscheidungen mit Grund, PRISMA-Zählung) — nicht das
deterministische Vor-Gate gegen Thementrift. Es fehlen
`scripts/screening_eval.py`, `data/bench/screening/annotated.json` und die drei
Tests (`test_screening_rejects_known_offtopic`,
`test_screening_keeps_annotated_positives`, `test_screening_reason_present`).
Ohne menschliche Labels gibt es keine Precision/Recall-Wahrheit; das Gate allein
wäre eine Behauptung.

## Die fünf offenen Fragen des Plans

1. **Zugang B-b** — offen, menschlich (Bibliothek, VPN, Fernleihe,
   Autorenanfrage).
2. **Fragenwahl** — entscheidbar geworden: k = 0 ist strukturell (keine der 11 SOL-Zeilen aus 5 Quellen stammt nach den Gates aus einer Melatonin-RCT), kein Leserfehler. Entweder Melatonin bleibt
   bewusst die Negativ-Demonstration, oder die Pipeline zeigt sich an einer
   Frage mit offener RCT-Evidenz. Entscheidung beim Nutzer.
3. **Annotation** — offen, menschlich: Obergrenze (A) und Screening-Labels (D).
4. **Lauf-Daten** — beantwortet und im Repo belegt:
   `data/research-does-melatonin-improve-sleep-onset-laten-382747.db` (Netzlauf),
   `data/harness_local.db` (Harness), dazu die Fragen-DBs zu Koffein, Exercise
   und Kognition. Der annotierte Satz für D lässt sich daraus offline bauen.
5. **Geschützte Module und Tests** — beantwortet: Alle drei Dateien sind
   gitignored (`git check-ignore` bestätigt für `orchestrator.py`,
   `meta/extraction.py`, `meta/pooling.py`). 18 Testmodule importieren sie,
   keines mit Skip-Marker, und es gibt kein `conftest.py`, das Ersatzmodule
   anlegt (`q5_probe_20261108.json`). Auf einem frischen Clone bricht die
   Sammlung dieser 18 Module mit ImportError ab, bevor ein Test läuft.
   Empfehlung: `pytest.importorskip` je Modul am Dateikopf — die Module selbst
   bleiben unberührt und gitignored, der Kern bleibt sammelbar.

## Was daraus folgt

Von den fünf Paketen sind zwei fertig (A ohne Obergrenze, E), eines durch sein
eigenes Abbruchkriterium beendet (C), eines halb belegt (B-a) und zwei offen
(B-b, D). Der nächste echte Erkenntnisgewinn liegt nicht in weiterer
Extraktionsarbeit — die ist gemessen ausgeschöpft —, sondern in der Obergrenze
(menschliche Sichtung) und in B-a mit einem externen Datensatz.
