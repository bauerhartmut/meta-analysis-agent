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

## Empfehlung

Die Repo-Regel fuer `report.py` entscheiden: Der Patch existiert nur lokal.
Solange die Regel gilt, ist der Hinweis bei jedem neuen Klon wieder weg.
Das ist keine technische, sondern eine Projektentscheidung.
