# Entscheidungsvorlage: gitignored Kerndateien

Stand: 2026-11-09. Auftrag Punkt 3. Keine Aenderung an `.gitignore`, kein
Commit der Dateien. Die Entscheidung liegt beim Projektverantwortlichen.

## Betroffene Dateien

| Datei | Zweck | Groesse |
|---|---|---|
| `research_agent/meta/pooling.py` | Pooling-Engine: FE/RE, DL/tau2, HKSJ, RVE, Gates, Sensitivitaeten | rund 1400 Zeilen |
| `research_agent/report.py` | Berichtsrendering: Meta-Abschnitt, Formulierungen, Zeilenbasis | rund 900 Zeilen |

Regel im Repo: `research_agent/patches/README.md`, Pruefskript
`scripts/pruefe_report_patch.py`, Sicherung in `local_patches/`.

## Proprietaere Bestandteile

- **RVE-Verdrahtung**: `weights="fixed"` vs. Random-Effects-Gewichte mit
  CR0-Sandwich und t auf M-1; die Formel selbst liegt committet in
  `meta/rve_weights.py`.
- **Gate-Logik**: `pool_gates.py` (committet), Aufrufreihenfolge und
  Schwellen in `pooling.py` (nicht committet).
- **Report-Sprache**: die Saetze, die Scheinpraezision vermeiden
  ("reiner Modellwechsel", "kein KI, weil nur ein unabhaengiger Cluster").
- **Zeilenbasis**: Kollaps gleichnamiger Zeilen, `rows`/`rows_collapsed`.

## Abhaengigkeiten

`pooling.py` importiert `rve_weights`, `pool_gates`, `extraction`. Ohne die
Datei laufen `build_analysis`-Tests nicht; die API liefert dann keine
Gruppen. `report.py` wird von `scripts/zeige_rve_im_report.py` und dem
Berichtsbau genutzt.

## Reproduzierbarkeit ohne Veroeffentlichung

Die numerischen Aussagen sind nachrechenbar: `scripts/messe_rve_modell.py`
und `scripts/pruefe_metaanalysis_api.py` liegen im Repo, die Referenzzahlen
stehen in `abschluss_e4e_e4k_20261109.md`. Ein Dritter kann die Ergebnisse
pruefen, aber nicht ohne Weiteres dieselbe Engine betreiben.

## Risiken einer Veroeffentlichung

| Risiko | Einschaetzung |
|---|---|
| Kopie durch Dritte ohne Attribution | moeglich, aber urheberrechtlich benannt |
| Erwartung von Support/Wartung | steigt mit Sichtbarkeit |
| Wettbewerbsnachteil bei Methodik | gering: die Methoden sind publiziert (HKSJ, RVE) |
| Widerspruch zur bisherigen IP-Linie | vorhanden, aber aufloesbar |

## Alternativen

1. **Status quo**: gitignored, Patch-Nachweis, Sicherung in `local_patches/`.
   Aufwand 0, Risiko 0, Nachvollziehbarkeit ueber die Dokumentation.
2. **Private Ablage** (separates privates Repo, Submodul): gleiche Wirkung,
   aber mit Versionshistorie und ohne Patch-Prozedur.
3. **Getrennte Veroeffentlichung** als Methodenpaket (Engine + Tests, ohne
   Projekttexte): maximale Reproduzierbarkeit, erfordert Lizenzwahl.
4. **Zeitverzoegerte Veroeffentlichung** nach Abschluss der Studienreihe.

## Empfehlung

**Alternative 1 beibehalten, Alternative 2 vorbereiten.** Grund: Die
Validierungsreihe ist mit 1331 Tests und dokumentierten Patch-Nachweisen
nachvollziehbar; eine Veroeffentlichung bringt derzeit keinen
Erkenntnisgewinn, kostet aber Entscheidungszeit. Sobald eine Publikation
geplant ist, ist Alternative 3 der passende Schritt - dann mit Lizenz und
Namensnennung.

Keine Datei wurde in diesem Schritt veraendert.
