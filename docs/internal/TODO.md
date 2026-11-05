# TODO: Stundenlange Wissensarbeit ermöglichen

**Diagnose:** Der Loop endet nicht an fehlender Zeit, sondern an fehlender Arbeit. Er macht
jeden Zyklus dasselbe (suchen → analysieren → Fakten → Hypothesen); liefert die Suche nichts
Neues, ist der Zyklus leer. Gleichzeitig liegt ein großer Rückstand ungenutzt in der DB.

**Ziel:** Der Agent arbeitet einen persistenten Rückstand ab. Solange Arbeit offen ist, läuft
der Lauf; ist sie erschöpft oder das Budget erreicht, endet er mit einem zitierbaren Bericht.

## Phase 1 — Persistente Arbeitswarteschlange

- [x] Tabelle `work_items` (kind, ref_id, priority, status, attempts, note) + Unique-Index
- [x] Seeder aus dem vorhandenen Rückstand:
  - [x] `full_text` — Quellen unter 400 Zeichen mit URL und (unbewertet oder relevant)
  - [x] `hypothesis_evidence` — aktive Hypothesen ohne eine einzige Evidenzzeile
  - [x] `open_question` — offene Forschungsfragen
  - [x] `citation` — relevante Quellen mit DOI (Schneeball, Phase 4)
- [x] Priorität = Wert × Unsicherheit / Kosten, Neubewertung beim Seeden
- [x] `claim` / `resolve` / `block` / `stats`, idempotent und neustartfest
- [x] Sichtbar in `/api/status` (Feld `work_queue` und `cycle_work`)

## Phase 2 — Der Zyklus arbeitet die Warteschlange ab

- [x] Phase `working` nach der Extraktion: 1–N Items pro Zyklus
- [x] Handler `full_text`: erneuter Volltext-/Abstract-Versuch, nach 2 Fehlschlägen blockiert
- [x] Handler `hypothesis_evidence`: vorhandene Fakten über Retrieval an eine Hypothesen
      ohne Evidenz anbinden und bewerten
- [x] Handler `open_question`: offene Frage wird zur Frage des Zyklus (statt LLM-Neuwahl)
      und nach der Synthese geschlossen
- [x] Leerlauf nur noch, wenn Warteschlange leer **und** Suche ohne Ertrag

## Phase 3 — Budget, Sättigung, Abschlussbericht

- [x] `RUN_BUDGET_MINUTES`, `WORK_ITEMS_PER_CYCLE`, `SATURATION_CYCLES` in Config/.env
- [x] Abschluss bei Budget oder erschöpfter Warteschlange (Grund in Status + Bericht)
- [x] Zitierter Bericht nach `data/reports/` (Fakten mit Quelle, Hypothesen mit Konfidenz
      und Evidenzlage, offene Fragen, Abdeckung)

## Phase 4 — Zitations-Schneeball

- [x] OpenAlex: `referenced_works` und `cited_by` zu einer DOI holen
- [x] Kandidaten über Themen-Keywords und Relevanzfilter aufnehmen
- [x] Neuer Handler `citation`, Ergebnis als normale Quellen speichern (und im selben
      Zyklus analysieren)

## Phase 5 — Absicherung

- [x] Tests: Seeding idempotent, Prioritätsordnung, Claim/Resolve, Handler-Fehler,
      Budget-Stopp, Bericht, Schneeball mit gefälschter API (217 Tests, alle grün)
- [x] Echter Lauf: mehrere Zyklen, Nachweis, dass Zyklen ohne Suchtreffer Arbeit erledigen
- [x] README aktualisieren

## Erfolgskriterium

Ein Zyklus ohne neue Suchtreffer ist kein Leerlauf mehr, sondern erledigt Rückstand.
Nachweis: `work_items` sinkt über Zyklen, Journal-Zeilen nennen erledigte Items,
und der Lauf endet mit Bericht statt mit Wiederholung.
