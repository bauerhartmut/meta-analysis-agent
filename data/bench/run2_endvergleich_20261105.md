# T0 — Endvergleich Run 1 vs. Run 2 (Melatonin)

Stand: 07.11.2026. Run 2 wurde **nicht regulär beendet**, sondern brach am
05.11. um 22:44 im Rate-Limit-Backoff ab (kein Prozess mehr, Session-Status
`active`, `end_time` leer, letzter Log-Eintrag mitten in einem 20s-Wait).
Die Zahlen sind daher ein Zwischenstand bei Zyklus 22/23, kein Endstand.

## Kennzahlen

| Kennzahl | Run 1 (15:12–19:14) | Run 2 (19:29–22:44, Abbruch) |
|---|---|---|
| Quellen (`sources`) | 134 | 101 |
| Quelltexte abstract / html / pdf | 37 / 16 / 17 | 25 / 15 / 19 |
| Zeichen gesamt | 1.885.693 | 1.831.346 |
| Studien registriert | 26 | 22 |
| davon `has_fulltext=1` | 9 (35 %) | 10 (45 %) |
| Screening include / exclude | 18 / 37 | 14 / 18 |
| Effekte | 19 | 8 |
| davon mit CI | 0 | 2 |
| davon mit SE | 1 | 2 |
| davon mit Zitat | 18 | 8 |
| Hypothesen | 63 | 46 |
| RoB high / some / crit. low | 3 / 2 / 4 | 1 / 1 / 1 |
| RoB disputed | 4 | 2 |

## Vision-Fallback-Telemetrie (Plan-Kennzahl T0)

- `grep -i vision` im Lauf-Log: nur zwei DB-Migrationsmeldungen
  (`vision_status`, `vision_meta`), **keine** Trigger-Aktivität.
- `study_effects.vision_status`: alle 8 Effekte leer (`''`).
- Kein OCR-/Bild-/Layer-2-Eintrag im Log (die 25 `fallback`-Treffer sind
  „snippet fallback" bei fehlendem Abstract, nicht der Bildpfad).

**Lesart:** Der Vision-Fallback ist im Lauf **null Mal gefeuert**. Das ist
weder Bestätigung noch Widerlegung seiner Wirkung — bei 19 PDF-Quellen und
2 SE/2 CI gab es keinen Trigger. Die Ursache ist vor der Trigger-Schwelle zu
suchen (PDF-Text ohne Tabellenkandidaten), nicht im Vision-Pfad selbst.

## Zyklus-Abbrüche (neu gefunden)

Siebenmal im Lauf, jeweils in Phase 7b (Counterarguments, jeder 3. Zyklus):

```
TypeError: An asyncio.Future, a coroutine or an awaitable is required
  orchestrator.py, _run_cycle -> asyncio.gather(_analyze_one(h) for h in ...)
```

`asyncio.gather` bekam einen Generator statt entpackter Coroutines; der
komplette Zyklus wurde verworfen (Log: „Cycle N error: ..."). Fix lokal
angewendet (`*[...]`), Regressionstest
`research_agent/tests/test_async_gather_guards.py` prüft die Fehlerklasse
statisch über alle Module.

## Bewertung

- Run 2 hat trotz Abbruch in 3,25 h mehr Volltexte (10 vs. 9) und erstmals
  CI-Effekte (2) geliefert, aber deutlich weniger Effekte insgesamt (8 vs. 19)
  und weniger Quellen (101 vs. 134).
- Die SE/CI-Quote bleibt der Engpass: 2 von 8 Effekten mit CI (25 %) gegen
  0 von 19 in Run 1; in beiden Läufen kommen fast alle Effekte ohne
  Unsicherheitsmaß aus den Textpfaden.
- Für belastbare Aussagen fehlt ein Lauf ohne Phase-7b-Abbrüche und ohne
  429-Dominanz; beides ist adressiert (Fix + Circuit-Breaker-Verhalten prüfen).
