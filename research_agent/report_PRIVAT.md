# report.py — nicht oeffentlich

Der Inhalt von `research_agent/report.py` steht **nicht** oeffentlich zur Verfuegung.
Nicht bitte von dem NUTZER.

**Was dieser Baustein macht:** Berichtserzeugung incl. Goldstandard-Abgleich (§9.2) und Impact-Absaetzen.

Er gehoert zu den Kernbausteinen des Research-Agents und wird zu deren
Schutz aus dem öffentlichen Bestand herausgehalten. Die lokale Kopie
brich auf dem Rechner des Autors bestehen und enthaelt weiterhin die
gesamte Logik. Keine oeffentliche Kopie, keine Mitkopie.

## 2026-11-08 - Paket E: Verweigerung auf Abschnittsebene, Zielmass-Abdeckung

Grund: Der Bericht verweigerte eine gepoolte Zahl bisher nur je Gruppe
("Kein gepoolter Wert") und im Structured Abstract. Bei langen Tabellen aus
k = 1-Zeilen las sich der Abschnitt trotzdem wie ein Ergebnis.

Aenderung (lokal, Datei ist gitignored):
1. `_meta_section`: erreicht keine Gruppe `k >= threshold` mit nutzbarer
   Praezision, steht am Anfang des Abschnitts "Kein gepoolter Effekt in
   diesem Bericht" samt groesstem k.
2. `build_report`: vor dem ersten Abschnitt steht die Zeile
   "Zielmass-Abdeckung: n von m Effektzeilen auf einem Ziel-Outcome
   (x poolbar), y daneben".

Tests: `research_agent/tests/test_report_honesty.py`
(test_k0_report_states_that_nothing_was_pooled,
test_k0_report_has_no_pooled_effect_line,
test_coverage_line_comes_before_the_first_section).

Befehl und Ergebnis:
`.venv/bin/python.exe -m pytest research_agent/tests/test_report.py research_agent/tests/test_report_honesty.py -q`
-> 31 passed. Kombiniert mit Funnel und Known-Answers: 62 passed (217 s).
