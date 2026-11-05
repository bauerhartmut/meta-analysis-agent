# T1 + T2 — Zwischenergebnisse (Implementierungsplan 05.11.2026)

**Stand:** 05.11.2026 · Run 2 läuft noch (Endvergleich T0 folgt nach Laufende).

---

## T1 — Referenz-Reports end-to-end (Abnahme: erfüllt)

Gezogener Reports aus **byte-identischen DB-Kopien** (`data/bench/regreports/`), damit
die Original-DBs unangetastet bleiben. Provenance: `data/bench/regreports/t1_summary.json`.

| DB | Report (MD+PDF) | Effektzeilen | gepoolter Effekt (HKSJ) | Fixe-Referenz |
|---|---|---|---|---|
| Exercise | `data/reports/20261105-2104-Exercise-…`](129 | **−0.586** [−1.319; 0.147] als k=3 | −0.437 (Fix-Effekt) ✓ exakt |
| Mediterrane | `data/reports/20261105-2104-Mediterrane-…` | 91 | **0.298** [−8.066; 8.662] k=2 | – |
| Kognition | `data/reports/20261105-2104-Kognition-…` | 127 | k<2 → kein Wert | – |

Nachrechnung gegen das Effekt-KI-Paar der 3 gepoolten Studien im Exercise-Report:

- Fix-Effekt aus den KIs berechnet: −0.437 (Report −0.437, exakt)
- DL-Zufallseffekt: −0.586 (Report −0.586, exakt); τ² = 0.0891, k=3
- **Pooling- und Report-Pfad mathematisch bestätigt** (delta=0 bis zur Rundung)

Kognitions-Komplexe: 20 poolbare Zeilen, aber über Zielmaß-Gruppen verteilt
alle k<2 in derselben Gruppe. Das ist eine Dokumentation der Fragmentierung,
keinesfalls ein sog. Pooling-Bug.

**Fakten:**

- `scripts/build_reference_reports.py` (neu, commit folgt)
- Ski-Füße: Original-DBs byte-identisch unveraendert (sha256 before/after)
- Reports inkl. PDF erzeugt, alle Evidenz-Zitate/Pooling-Tabellen im PDF

---

## T2 — XML-Content-Diagnostik der 62 OA-Volltexte (read-only)

`scripts/diagnose_statistical_content.py`, Ergebnis:

- 50/62 XMLs mit JATS-Tabellen, 155 Tabellen gesamt
- **26 Dokumente mit 211 stat-reichen Tabellenzeilen** (SE/CI/±SD/N im Zellenkontext)
- 29 Dokumente mit SE-Tokens, 35 mit CI-Tokens, 27 mit Supplement-Referenzen
- Detail: `data/bench/xml_diagnostics_20261105.json` + `xml_diagnose_20261105.md`

**Stärkster nachgewiesener Engpass (Plan-Phase 4):**

Die JATS-Tabellen werden bei der Volltexteinbindung (coverage/manager.py
`_xml_to_text`) **abgeflacht**: Der Flatten wirft die Tabellenstruktur weg, und
Zellen mit SE bzw. CI (±SD/N) bleiben beim LLM-Fließtext-Aufruf ungenutzt.
Dann wird in dieser 62-corpus-Kohorte (keine Melatonin-Netzlauf-DB) immer
noch geprüft: 211 Kandidatenzeilen in einem lokalen Seed-Korpus, der als
Harness-Quelle läuft, nicht als Quelle der aktuellen Netzläufe. Der SE/CI-Loss
kommt soweit primär von Netzlauf-PDFs (Run 1: pdf=17, SE=1), also der
PDF-Tabellen-/Vision-Pfad.

**Bei Netzlauf-Quellen** (Run 1/2 DBs): 0 der 62 XML-DOIs sind
in der Run-1 bzw. Run-2-DB. Die Restaurierung läuft deshalb über:

1. PDF-Tabellenextraktion + Vision-Trigger (bereits erweitert, 3a-i)
2. für die Seeding-Quellen (T4): JATS-Tabellenparser (JUnit in
   `research_agent/research/table_extractor.py` existiert für PDFs)]
3. substrate: Run-Berichte von der Nettzapfen-Seite (-ammlung im Plan Abschnitt 5)

---

## Was noch offen bleibt (T0, T3–T12)

- **T0 Run-2-Endvergleich:** wartet auf Laufende (~22:30–23:00).
- **T3/T4 (Gemeinsames Evidence-Schema, JATS-Parser)** ist der
  stärkste Fix für das Seeding-Korpus; für die **Netzlaufroute** sind zuerst
  PDF-Tabellen-/Vision-Trigger-Telemetrie auszuwerten (kann bei T0 passieren).
- Rate-Limit-Manager (T9), Vision-Budget-Telemetrie (T10), Goldstandard (T11):
  noch offen, geplant nach T0/T5–T7.
