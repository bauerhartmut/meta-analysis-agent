# Telemetrie des letzten Netzlaufs: Befund fuer die SOL-Freigabe (2026-11-08)

Read-only ausgewertet: `data/research2-usage.db`, `data/research2-...-382747.db`
und `data/runs/melatonin_net_run2.log`. Erzeugt mit
`scripts/telemetry_report.py` nach `data/bench/telemetrie_20261108.json`
und `data/bench/telemetrie_run2_20261108.md`. Alle Zahlen unten stammen aus
diesen Quellen; die Datenbanken wurden im Modus `mode=ro` geoeffnet.

## 1. Der Lauf

| Kennzahl | Run 2 |
|---|---:|
| Log-Spanne | 05.11. 19:29:29 bis 22:44:37 (3 h 15 min) |
| Session-Status | `active`, `end_time` leer - **nicht beendet** |
| LLM-Aufrufe | 1.324 |
| Tokens | 1.632.777 |
| LLM-Zeit (Summe) | 8.495,6 s |
| Fehler in der Buchhaltung | 0 |
| Quellen / Studien / Effekte | 101 / 22 / 8 |
| Effekte mit SE und CI | 2 |
| Suchanfragen | 154 Zeilen, 22 verschiedene |
| Tokens je Effekt | 204.097 |

Zum Vergleich Run 1: 1.042 429-Zeilen im Log, 30 abgeschlossene Zyklen,
7 Zyklusfehler.

## 2. Wohin die Tokens gingen

| Phase | Aufrufe | Tokens | Anteil |
|---|---:|---:|---:|
| hypothesizing | 352 | 481.810 | 29,5 % |
| analyzing | 247 | 466.976 | 28,6 % |
| critiquing | 476 | 336.627 | 20,6 % |
| working | 182 | 267.945 | 16,4 % |
| synthesizing | 17 | 50.342 | 3,1 % |
| searching | 46 | 26.044 | 1,6 % |
| planning | 3 | 3.006 | 0,2 % |

Hypothesen, Analyse und Kritik zusammen: **1.285.413 Tokens = 78,7 %**. Die
Suche kostete 566 Tokens je Aufruf (26.044 / 46) beziehungsweise 1.184 Tokens
je der 22 Abfragen.

## 3. Rate-Limits

636 Log-Zeilen enthalten `429`. Aufteilung nach Provider:

| Provider | Befund im Log |
|---|---|
| OpenAlex | 272 `rate limited`-Zeilen, **94 Circuit-Breaks** (je 1.800 s Sperre) |
| Semantic Scholar | 254 `rate limited`-Zeilen, **82 Circuit-Breaks** |
| PubMed | `ESearch returned status 429` und `ESummary returned status 429` |
| Europe PMC | **0** Zeilen von 636 |
| Crossref | **0** Zeilen von 636 |

Europe PMC und Crossref liefen durch: 198 erfolgreiche Aufrufe im Log, kein
einziges 429. Der Lauf starb im Backoff von OpenAlex und Semantic Scholar -
der letzte Log-Eintrag ist `attempt 2/3` nach 20 s Wartezeit um 22:44:37,
unmittelbar nachdem OpenAlex zum 94. Mal in Folge geoeffnet wurde.

## 4. Abbrueche

- 15 Zyklen `complete`, 7 Zyklen `error`. Letzter Zyklus: 22 `complete`
  um 22:41:47.
- Alle 7 Fehler haben denselben Wortlaut: `An asyncio.Future, a coroutine or
  an awaitable is required` - und zwar in den Zyklen 3, 6, 9, 12, 15, 18, 21,
  also **jeder dritte Zyklus ab Zyklus 3**. Der Lauf machte danach weiter.
- Der Abbruch kam nicht von diesem Fehler, sondern vom Rate-Limit: nach dem
  letzten abgeschlossenen Zyklus lief nur noch Backoff, dann endet das Log.
  Die Session steht bis heute auf `active`.

## 5. Was das fuer den SOL-Lauf bedeutet

1. **Nur Europe PMC, Crossref als Gegenprobe.** Genau die zwei Provider, die
   im letzten Lauf kein 429 hatten. PubMed (ESearch/ESummary 429), OpenAlex
   und Semantic Scholar bleiben draussen; sie haben den Lauf gekostet, nicht
   bereichert.
2. **Kein Orchestrator, keine Zyklen, keine Hypothesenschleife.** Der geplante
   Lauf nutzt `scripts/sol_corpus_search.py` plus Leser - dort gibt es keinen
   `Cycle`-Pfad, also auch nicht den asyncio-Fehler aus Abschnitt 4.
3. **Kosten sind kein Argument mehr.** Drei Suchabfragen kosten nach dem
   letzten Massstab rund 1.700 Tokens; der Lauf braucht nur Netz und
   Rechenzeit. Die 1,63 Mio Tokens von Run 2 kamen zu 78,7 % aus Phasen, die
   bei SOL nichts liefern.
4. **Zeitbudget:** ein Lauf mit 150-250 XML-Downloads bleibt unter einer
   Stunde; Run 2 brauchte 3 h 15 min, davon der groesste Teil LLM-Zeit
   (8.495,6 s) und Backoff.
5. **Die Zwei-Laeufe-Grenze bleibt.** Aus der Telemetrie folgt keine
   Berechtigung fuer einen dritten Lauf.

## 6. Offen und nicht untersucht

- Die Ursache des asyncio-Fehlers liegt in `research_agent/orchestrator.py`
  (gitignored). Nicht Teil dieser Auswertung; fuer den SOL-Lauf irrelevant,
  fuer kuenftige Orchestrator-Laeufe ein bekanntes Risiko.
- Warum OpenAlex und Semantic Scholar dauerhaft 429 liefern (Schluessel,
  Kontingent, IP), ist aus dem Log nicht entscheidbar. Deshalb der Verzicht
  statt einer Reparatur.
- Die Session von Run 2 ist formal nie beendet worden. Das ist ein
  Buchhaltungsartefakt, kein laufender Prozess.
