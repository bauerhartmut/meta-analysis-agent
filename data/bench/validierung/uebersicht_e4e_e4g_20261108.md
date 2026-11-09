# Uebersicht E4e bis E4g

Stand: 2026-11-08. Zeitraum: Commit `c4aa70e` (E4e) bis HEAD.
Modellaufrufe in diesem Zeitraum: **0**. Tokens: **0**.

## Was dazukam

| Schritt | Frage | Befund | Artefakt | Commit |
|---|---|---|---|---|
| E4e | Gehoert die Exposition in den Kollaps-Schluessel? | Ja: 6 von 38 Gruppen aendern sich, weil Zeilen aus verschiedenen Expositionsgruppen sonst kollabieren | `e4e_vergleich_20261108.md` | `c4aa70e` |
| E4f | Wie breit sind die Intervalle, wenn man nach Quelle clustert? | 3 der 6 betroffenen Gruppen haben nur einen Cluster; nur MACE wird deutlich breiter | `e4f_rve_20261108.md` | `ae249be` |
| E4g | Was folgt daraus fuer das Pooling? | Gate: bei `M < 2` kein Intervall; greift bei 3 von 10 Gruppen mit k >= 2 | `e4g_m_gate_20261108.md` | `658be4f` |
| Dashboard | Wie rendert die Oberflaeche ein fehlendes KI? | `Number(null)` haette `[0,000; 0,000]` gezeigt; jetzt Hinweis auf den einen Cluster | `dashboard/templates/app.js` | `15144e4` |
| E4g-Korrektur | War die Spalte "KI vorher" korrekt? | Nein, sie zeigte die Nachher-Werte; jetzt zweiter Lauf mit deaktiviertem Gate | `e4g_m_gate_20261108.md` | `dieser Commit` |

## Kernbefund in einem Satz

Der Kollaps-Schluessel mit Exposition repariert eine falsch zugeordnete Zeile
(RA statt Mittelmeer-Diaet), erzeugt aber Gruppen, deren Zeilen aus **einer**
Quelle stammen; dort ist kein Intervall schaetzbar, und das naive
HKJ-Intervall taeuscht Unabhaengigkeit vor.

## Zahlen

- Gruppen mit k >= 2: **10**. Davon ohne zweite Quelle: **3**.
- preeclampsia [log_ratio]: k = 5, M = 1, KI vorher [-0,491; -0,126], jetzt keins.
- frailty index [raw:beta]: k = 2, M = 1, KI vorher [0,088; 0,197], jetzt keins.
- depressive symptoms [fisher_z]: k = 2, M = 1, KI vorher [-0,548; 0,187], jetzt keins.
- MACE: HKJ-Breite 0,624, RVE-Breite 1,137 (Faktor 1,82) - der einzige klare
  Fall von Scheinpraezision unter den Gruppen mit mehr als einer Quelle.
- Ueber alle 7 schaetzbaren Gruppen: Median-Faktor RVE/HKJ **0,86** - RVE ist
  meist schmaler, weil es ein Fixed-Effect-Schaetzer ist.
- Tests: **92 gruen** (`test_pool_gates.py` mit 6 neuen Faellen).

## Offen

1. Der Report zeigt fuer die drei Gruppen `[-; -]` ohne Begruendung
   (`report.py` ist gitignored; ein erklaerender Satz waere eine lokale,
   nicht committbare Aenderung).
2. RVE traegt kein tau2. Der Breitenvergleich gegen HKJ ist nur bei gleichem
   Modell aussagekraeftig; `depressive symptoms [log_ratio]` zeigt das
   Extrem (0,748 gegen 0,068).
3. Die Dashboard-Aenderung ist nur syntaktisch geprueft (`node --check`),
   nicht im Browser gesehen.
4. Im Working Tree liegen weiterhin fremde, uncommittete Dateien
   (`data/bench/sol/`, `data/bench/backfill/`, `regreports/`); sie wurden
   nicht angefasst.
5. `research_agent/meta/pooling.py` ist lokal gepatcht und absichtlich nicht
   im Index (`git ls-files` leer).

## Abschluss E4h (2026-11-08)

| Punkt | Ergebnis |
|---|---|
| P1 Report | Ursache von `[-, -]`: `forest_table` druckt die gepoolte Zeile immer, `_meta_num(None)` gibt `-` zurueck. `report.py` hat jetzt einen eigenen `single_cluster`-Zweig mit Text und unterscheidet Datenmangel von nicht schaetzbarer Unsicherheit. Kein KI erfunden. Geprueft an einer DB-Kopie: 279 Zeilen, Hinweis genau einmal. |
| P2 RVE | Modellannahmen stehen in `e4f_rve_20261108.md`: HKJ ist Random Effects mit tau^2 in den Gewichten, RVE ist Fixed Effect ohne. Der Breitenvergleich ist damit kein Beweis fuer Scheinpraezision; MACE bleibt Einzelfall. |
| P3 Dashboard | Render-Test mit injizierter API-Antwort: `preeclampsia` zeigt "kein KI (nur ein unabhaengiger Cluster)", MACE `[0.430; 1.050]`, nirgends `[0,000; 0,000]`. Screenshot `dashboard_gate_20261108.png`, Protokoll `dashboard_render_protokoll_20261108.md`. |
| P4 Repo | Sicherungen von `pooling.py`, `report.py`, `pool_gates.py` in `local_patches/` (gitignored). Fremde uncommittete Dateien unangetastet. Volle Suite: **1317 passed, 2 skipped**, EXIT 0, 6:52. |

Grenze: Der Live-Endpunkt `/api/metaanalysis` wurde nicht end-to-end geprueft -
er braucht den Orchestrator, also einen Lauf mit Freigabe.

## Entscheidung zur report.py-Regel (2026-11-08)

`report.py` bleibt gitignored - die Sektion "Kernbausteine: nicht oeffentlich"
schuetzt IP, eine Aufhebung waere eine Veroeffentlichungsentscheidung. Der
Patch ist stattdessen nachvollziehbar: Regel in `research_agent/patches/README.md`,
Eintrag `report_single_cluster_20261108.md` mit Ankerpunkt und Wirkung, und
`scripts/pruefe_report_patch.py` als objektiver Nachweis (Exit 0 = wirksam,
Exit 1 = fehlt). Kein Diff und kein Quellcode im Repo.

## E4i - RVE mit Random-Effects-Gewichten (2026-11-09)

`pool_rve(weights="random")` rechnet Punkt und Sandwich mit `1/(v + tau2)`;
die Formel steht committet in `meta/rve_weights.py`, `pooling.py` ist nur
verdrahtet. Messung `e4i_rve_modell_20261108.json`:

| Gruppe | HKJ | RVE-FE | RVE-RE | Modellanteil |
|---|---:|---:|---:|---:|
| MACE | 0,624 | 1,137 | 1,137 | 0 % |
| incident CVD | 1,529 | 1,438 | 1,791 | 139 % |
| depressive [raw:beta] | 0,536 | 0,458 | 0,772 | 143 % |
| depressive [hedges_g] | 1,466 | 1,550 | 1,270 | 139 % |
| depressive [log_ratio] | 0,748 | 0,068 | 0,659 | -1772 % |

MACE: tau2 = 0 in beiden Rechnungen, RVE-FE und RVE-RE identisch - die
Verbreiterung ist reiner Cluster-Effekt. Bei den anderen vier Gruppen heben
sich Modell- und Clusterbeitrag teilweise auf; dort ist kein generelles
Urteil ablesbar.

## Nachtrag: RVE-RE im Report (2026-11-09)

Der Report zeigt jetzt zwei RVE-Zeilen: Fixed Effect und Random Effects, mit
dem Faktor zwischen beiden. Bei MACE steht ausdruecklich "Breite identisch
(tau2 = 0): reiner Cluster-Effekt". Beleg `report_rve_re_20261109.txt`,
Patch-Eintrag `report_rve_re_20261109.md`, 66 Report-Tests gruen.

## Nachtrag: tau2 auf demselben Material (2026-11-09)

tau2 ist in `HKJ(alle)` und `RVE-RE` identisch (7 von 7); die Zerlegung ist
damit konsistent. Dreiteilig: Modell (RE/FE), Cluster (RE_RVE/HKJ_alle) und
Duplikation (HKJ_alle/HKJ_koll). Bei `incident CVD` haelt der 1,25-Faktor
exakt, aber Cluster 1,49 und Duplikation 0,78 heben sich teilweise auf -
der Report-Satz dazu war falsch und ist korrigiert.

## Nachtrag: Zeilenbasis im RVE-Block (2026-11-09)

Vor dem RVE-Block steht jetzt die Basis: Anzahl Effektzeilen, davon nach dem
Kollaps, Anzahl zusammengelegter Zeilen. Bei `MACE` sind das 6 und 4 -
damit ist klar, dass die 1,82 nicht allein die Cluster-Korrektur ist.
38 Report-Tests gruen, Pruefskript Exit 0 mit fuenf Markern.

## Volle Testsuite (2026-11-09)

Lauf 1: 1330 passed, 2 skipped, **1 failed** - ein zeitabhaengiger Test
(`_last_penalty = 0.0` gegen eine Uptime von 1386 s bei
`CIRCUIT_QUIET_SECONDS = 1800`). Fix in `63bc122` ohne Aenderung der
Assertions. Lauf 2: **1331 passed, 2 skipped, EXIT 0** in 7:47.
Details: `testsuite_20261109.md`.

## Empfehlung

Die Validierungsreihe abschliessen: Die offenen Punkte aus E4e bis E4k sind
abgearbeitet und belegt; ein Bericht ueber alle Nachweise mit den jeweiligen
Grenzen (Report-Hinweis nur lokal, Live-Endpunkt ungetestet) waere der
naechste sinnvolle Schritt.
