# Abschluss E4e bis E4k (2026-11-09)

Zeitraum: `c4aa70e` (E4e) bis `9add0b8`. Modellaufrufe in dieser Reihe:
**0**. Tokens: **0**. Netzlaeufe: **0**. Alle Rechnungen liefen read-only auf
DB-Kopien.

Die Reihe beantwortet eine Frage: Wo taeuscht das Harness Praezision vor, und
was folgt daraus fuer Pooling, Report und Oberflaeche?

## 1. Was jede Stufe geprueft hat

| Stufe | Frage | Befund | Beleg | Commit |
|---|---|---|---|---|
| E4e | Gehoert die Exposition in den Kollaps-Schluessel? | Ja: 6 von 38 Gruppen aendern sich, sonst kollabieren Zeilen aus verschiedenen Expositionsgruppen | `e4e_vergleich_20261108.md` | `c4aa70e` |
| E4f | Wie breit sind die Intervalle bei Clusterung nach Quelle? | 3 der betroffenen Gruppen haben nur einen Cluster; MACE wird deutlich breiter (1,82) | `e4f_rve_20261108.md` | `ae249be` |
| E4g | Was folgt fuer das Pooling? | Gate: bei M < 2 kein Intervall; greift bei 3 von 10 Gruppen mit k >= 2 | `e4g_m_gate_20261108.md` | `658be4f` |
| E4g-Korrektur | War "KI vorher" korrekt? | Nein, zeigte Nachher-Werte; zweiter Lauf mit deaktiviertem Gate | `e4g_m_gate_20261108.md` | `36ece84` |
| Dashboard | Wie rendert ein fehlendes KI? | `Number(null)` haette `[0,000; 0,000]` gezeigt; jetzt Hinweis | `dashboard_render_protokoll_20261108.md` | `15144e4` |
| E4h | Erklaert der Report das fehlende KI? | Ja, eigener Zweig; Ursache war `_meta_num(None)` in der immer gedruckten Pool-Zeile | `report_meta_ausschnitt_20261108.txt` | `d9564b2`, `3931cce` |
| Regel | Wie bleiben Patches an geschuetzten Dateien nachvollziehbar? | Patch-Eintrag + Pruefskript, kein Diff im Repo | `research_agent/patches/README.md` | `eb5864e` |
| E4i | Wie viel der RVE-Verbreiterung ist Modell? | MACE: 0 %; RVE-FE und RVE-RE bitgleich, weil tau2 = 0 | `e4i_rve_modell_20261108.json` | `15a5b89` |
| E4i-Report | Steht die Trennung dort, wo gelesen wird? | Zweite RVE-Zeile mit Faktor | `report_rve_re_20261109.txt` | `afbfc2b` |
| E4j | Haelt der 1,25-Faktor bei incident CVD? | Ja als Modellwechsel; Cluster 1,49 und Duplikation 0,78 heben sich teilweise auf (Summe 1,17) | `e4i_rve_modell_20261108.md` | `8255848` |
| E4k | Auf welcher Zeilenbasis steht die RVE? | Basiszeile: 6 Zeilen, davon 4 nach dem Kollaps | `report_rve_re_20261109.txt` | `0610319` |
| Suite | Bricht ein Aufrufer ausserhalb der Report-Suite? | Nein; ein zeitabhaengiger Test war rot und ist gefixt | `testsuite_20261109.md` | `63bc122`, `9add0b8` |

## 2. Die Zahlen, auf die es ankommt

**Gate (E4g).** 10 Gruppen mit k >= 2, davon 3 ohne zweite Quelle:

| Gruppe | k | M | Punktschaetzer | KI vorher (ohne Gate) |
|---|---:|---:|---:|---|
| preeclampsia [log_ratio] | 5 | 1 | -0,309 | [-0,491; -0,126] |
| frailty index [raw:beta] | 2 | 1 | 0,142 | [0,088; 0,197] |
| depressive symptoms [fisher_z] | 2 | 1 | -0,180 | [-0,548; 0,187] |

**Zerlegung (E4i/E4j), Breiten:**

| Gruppe | HKJ(koll) | HKJ(alle) | RVE-FE | RVE-RE | Cluster (log) | Duplikation (log) | Modell (log) |
|---|---:|---:|---:|---:|---:|---:|---:|
| MACE | 0,624 | 0,411 | 1,137 | 1,137 | 1,018 | -0,417 | 0,000 |
| incident CVD | 1,529 | 1,200 | 1,438 | 1,791 | 0,401 | -0,242 | 0,220 |

tau2 ist zwischen `HKJ(alle)` und `RVE-RE` in **7 von 7** verfuegbaren Gruppen
identisch. Die Aussage "MACE ist reiner Cluster-Effekt" haelt; die Aussage
"der Rest ist Cluster-Korrektur" haelt bei incident CVD nicht und wurde
korrigiert.

**Testsuite.** 1331 passed, 2 skipped, EXIT 0 (7:47). Davon 14 neu in dieser
Reihe: 8 Formeltests fuer RE-RVE, 6 fuer das Patch-Pruefskript.

## 3. Patch-Register

Drei Eintraege, alle wirksam, Pruefskript Exit 0:

| Eintrag | Datei | Wirkung | Sicherung |
|---|---|---|---|
| `report_single_cluster_20261108.md` | `research_agent/report.py` | erklaert fehlendes KI bei M = 1 statt `[-, -]` | `local_patches/report_20261109.py` |
| `pooling_rve_weights_20261109.md` | `research_agent/meta/pooling.py` | `weights="random"`, `rve_re` in `build_analysis`, `rows`/`rows_collapsed` | `local_patches/pooling_20261109.py` |
| `report_rve_re_20261109.md` | `research_agent/report.py` | zweite RVE-Zeile, Modell-Faktor, Zeilenbasis | `local_patches/report_20261109.py` |

Committet und damit im Klon vorhanden: die Mathematik
(`meta/rve_weights.py`), das Gate (`meta/pool_gates.py`), das Pruefskript
(`scripts/pruefe_report_patch.py`), die Mess- und Belegskripte
(`scripts/messe_rve_modell.py`, `scripts/zeige_rve_in_report.py`) und die
Ergebnisdateien. Nicht im Repo: der Quellcode der geschuetzten Dateien -
bewusst, siehe `research_agent/patches/README.md`.

## 4. Verbleibende Grenzen

1. **Der Report-Hinweis ist lokal.** Bei einem frischen Klon fehlen `report.py`
   und `pooling.py`; dann fehlt auch der M=1-Hinweis. Das Pruefskript meldet
   das (`Exit 1`), aber es repariert nichts. Aufheben liesse sich das nur
   durch Veroeffentlichung der Kerndateien - eine Projektentscheidung.
2. **Der Live-Endpunkt `/api/metaanalysis` ist nicht end-to-end getestet.**
   Er braucht den Orchestrator, also einen Lauf. Der Dashboard-Nachweis ist
   ein Rendering-Test mit injizierter API-Antwort.
3. **Der Screenshot ist rechts abgeschnitten** (Karte breiter als der
   Viewport); der relevante Text ist lesbar, eine Interaktionspruefung gibt es
   nicht.
4. **Die Zerlegung ist logarithmisch in den Breiten, keine Varianzzerlegung.**
   Sie sagt nichts ueber die Ursache der Heterogenitaet.
5. **`HKJ(alle)` ist absichtlich naiv**: Es behandelt abhaengige Zeilen als
   unabhaengig - genau der Fehler, den RVE korrigiert. Der Vergleich ist die
   Zerlegung dieses Effekts, kein Vergleich zweier korrekter Modelle.
6. **Hauptzahl ist DL, nicht REML.** REML steht als Sensitivitaet daneben; bei
   MACE weicht es minimal ab (tau2 0,002), was unter der 0,5-%-Schwelle des
   Report-Textes liegt.
7. **Drei Gruppen bleiben prinzipiell unbeantwortbar.** Bei M = 1 gibt es
   keine zweite unabhaengige Einheit; das Gate entfernt das Intervall, statt
   es zu schaetzen. Mehr Daten, nicht mehr Statistik, wuerden das loesen.
8. **Kein CI, ein Lauf pro Zustand.** Die Suite lief auf dieser Maschine;
   der rote Test in Lauf 1 war ein Testdefekt (Uptime < 1800 s), kein
   Produktfehler.

## 5. Reproduktion

```
export PYTHONIOENCODING=utf-8
.venv/bin/python.exe scripts/pruefe_report_patch.py
.venv/bin/python.exe scripts/messe_rve_modell.py
.venv/bin/python.exe scripts/messe_m_gate.py
.venv/bin/python.exe scripts/zeige_rve_im_report.py <db-pfad>
.venv/bin/python.exe -m pytest research_agent/tests -q
```

Alle Rechnungen laufen auf Kopien oder rein im Speicher; keine der Skripte
oeffnet eine laufende Datenbank zum Schreiben und keines ruft ein Modell auf.
