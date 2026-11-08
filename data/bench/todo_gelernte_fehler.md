# TODO: Gelernte Fehler aus den Läufen (2026-11-05)

Quellen: net_run_final.md, harness_run_final.md, lauf_vergleich_20261105.md,
Logbefunde („Meta extraction: … 0 poolable"), Biz-Scanner-Warnungen.

## Priorität 1 — Pooling-Kette installieren
- [x] 1a. Diagnose: Abgeschlossen. Das Gate lehnt KORREKT ab — die Zeilen
      scheitern am Kontrakt, nicht am Filter: 12/19 Zeilen ohne Effektwert
      (rejection_reason „kein Effektwert gelesen"), nur 1 Zeile mit SE,
      0 Zeilen mit CI, 4 disputed.
- [x] 1b. Kriterium: Kein Fix nötig — Kontrakt (SE oder CI) ist
      methodisch richtig; die Ursache liegt in der Extraktionstiefe.
- [x] 1c. Pooling bereits installiert: `research_agent/meta/pooling.py`
      (HKSJ-Standard, RVE für Cluster, `build_analysis`), eingebunden in
      `report.py` (Zeile 924), Referenztests vorhanden
      (`test_pooling_reference.py`, `test_meta_pooling.py`). Der Schritt
      wurde im Netzlauf nie wirksam, weil nie >=2 poolbare Zeilen
      zusammenkamen — Blocker bleibt § 3a (Volltexttiefe).

## Priorität 2 — Relevanz-Gate: Themen-Drift drosseln
- [x] 2a. Erledigt (orchestrator.py, lokal — gitignored, kein Commit):
      (1) `_REJECT_ARXIV_CATS` war definiert, wurde aber nie angewendet und
      verglich Groß-/Kleinschreibung gegen eine lowercased URL — jetzt
      case-insensitive + Legacy-Archive-Präfixe (chao-dyn, astro-ph, …)
      dazugefügt. (2) Moderne numerische arXiv-Ids (Kategorie nicht in der
      URL) müssen jetzt ≥2 Themengruppen matchen statt 1 — Sam 3D/Quanten-
      banking/REBOUND-Klasse fällt raus, legitime (DLMO-Sensorik) bleibt.
      (3) Neue Domänengruppe sleep_medicine; davor scheiterte sogar ein
      legitimer Melatonin-PubMed-Treffer am Gate (0 Gruppen-Matches).
      (4) Blacklist wird word-bounded gematcht — 'led' feuerte sonst im
      Wort 'controlLED' und nahm legitime Zeilen raus. Tests:
      `research_agent/tests/test_topic_gate_arxiv.py` (5 Cases, committed
      fc5bcdd, gepusht), Gesamtsuite 1018 passed / 2 skipped.

## Priorität 3 — Abstract-only-Falle quantifizieren (läuft schon)
- [x] 3a-i. Vision-Fallback-Trigger erweitert (Befund im Run-2-Log: 0 Aufrufe,
      obwohl VISION_TABLE_ENABLED an war — der Trigger feuerte nur bei
      `not rows`, aber der Text-Layer produzierte Zeilen OHNE Effektwert/
      SE/CI, die ihn blockierten). Neu in `research_agent/orchestrator.py`
      (lokal, gitignored): statische Bedingung `_vision_fallback_due` +
      `_count_poolable`; Bildlesung läuft jetzt auch, wenn Zeilen existieren,
      aber keine davon SE oder CI trägt. Pinned durch 6 neue Cases in
      `research_agent/tests/test_sprint30_vision.py` (commit de4cd5c,
      gepusht). Suite 1024 passed / 2 skipped.
- [x] 3a-ii. Repeat-Lauf (62 Volltexte) abwarten; Endvergleich Effekt-/CI-Rate
      gegen Run 1; nur wenn Tiefe steigt, hat 1c genug Material. Zusätzlich
      offen: PDF-Nachschub für Quellen ohne Original-PDF (OA-XML-rein) — der
      Fallback kann nur Original-PDFs rasterisieren.
      Erledigt (08.11.2026): Die Tiefe stieg (523 -> 1.099 gespeicherte
      Zeilen, 152 -> 422 poolbar), beim Zielmass aber nicht: 11 SOL-Zeilen
      aus 5 Quellen, k = 1. Der PDF-Nachschub ist ebenfalls erledigt -
      33 von 33 Dokumenten der Stichprobe sind lesbar (10 davon ueber NCBI
      efetch, nach 20 x HTTP 500 bei Europe PMC). Der Vision-Fallback hat
      nach Messung kein Ziel: 342 colspan-Zeilen, 0 mit Effektspalte
      (`colspan_befund_20261108.md`).

## P4 — Biz-Scanner-Selbstwarnung (30 Hypothesen : 1 Befund)
- [x] 4a. Dokumentiert im Vergleichsbericht — die Selbstwarnung ist korrekt
      und bleibt stehen (31 Hypothesen : 2 quantifizierte Befunde ist
      tatsächlich ein Veröffentlichungs-Bias-Signal eines zu frühen Laufs,
      kein Scanner-Fehler).

## Fazit nach Durchlauf
Die Pty welche dem Pooling im Weg steht, ist die Extraktionstiefe (SE/CI
vom Volltext), nicht die Pipeline-Logik. Konsequente Reihenfolge: § 3a
wartet auf den laufenden Repeat, dann Endvergleich + ggf. gepooltes
Ergebnis aus dem Report. Relevanz-Gate-Fix (§ 2a) bleibt der eine echte
Code-Fix dieser Liste.
