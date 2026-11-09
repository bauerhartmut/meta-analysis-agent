# Betriebspruefung: Frage - Beleg - Luecke - Test

Stand: 2026-11-09. Auftrag Punkt 2: pruefen, ob `current_topic`, parallele
Zugriffe und Schreibpfade lokal ausreichend abgedeckt sind. Kein teurer Lauf
ohne nachgewiesene Luecke.

## Matrix

| Frage | Vorhandener Beleg | Verbleibende Luecke | Guenstigster Test |
|---|---|---|---|
| Liefert der Live-Endpunkt die RVE-Felder korrekt? | `pruefe_metaanalysis_api.py` (Exit 0), Browser-Nachweis `browser_meta_20261109.md` | keine | - |
| Reagiert der Endpunkt auf `current_topic`? | `dashboard/server.py:226` liest `getattr(orchestrator, "current_topic", "")`; `test_dashboard_contract.py:112` sichert, dass das Frontend `liveOnly('/api/metaanalysis')` nutzt | kein Test mit **zwei** Themen in einer DB | Stub mit zwei Themen und je einer Effektzeile, zwei GETs, Vergleich der Gruppenzahl |
| Verfaelscht gleichzeitiges Schreiben das Lesen? | `database.py:55` setzt `PRAGMA journal_mode=WAL` | kein Test: Lesen waehrend Schreiben | Thread schreibt 200 Zeilen in eine Kopie, waehrend 200 GETs laufen; beide muessen fehlerfrei sein |
| Funktioniert der Schreibpfad der Effektextraktion? | `test_meta_cohort.py`, `test_meta_pooling.py`, `test_meta_quality_gates.py` (build_analysis mit Fixtures) | Extrahieren aus Volltext im Lauf nicht abgedeckt | nicht noetig: Extraktion ist nicht Teil der API-Frage |
| Verhaelt sich der Orchestrator beim Start/Stop korrekt? | `test_supervisor.py`, `test_program.py` mit `current_topic` | echter Lauf mit Modellaufrufen | nur mit Guthaben; Erkenntnisgewinn rechtfertigt das nicht |

## Bewertung

**Kein Orchestrator-Lauf noetig.** Die offenen Punkte sind zwei lokale Tests
(Schreiben waehrend Lesen, zwei Themen), die ohne Modell und ohne Netz
laufen. Ein Voll-Lauf wuerde dieselben Codepfade durchlaufen wie die Tests,
zusaetzlich aber Prompts, Netzabrufe und Kosten erzeugen - er beantwortet
keine Frage, die lokal offen ist.

## Empfohlene Reihenfolge

1. Zwei-Themen-Test (klein, deckt `current_topic`-Filter ab).
2. Nebenlaeufiger Lese-/Schreibtest (deckt WAL-Verhalten ab).
3. Erst wenn beide gruen sind und eine echte Laufzeitfrage bleibt: Lauf mit
   dokumentiertem Zweck, erwarteter Beobachtung, Kosten und Abbruchbedingung.

Modellaufrufe fuer diese Pruefung: 0.
