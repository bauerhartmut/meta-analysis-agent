# Telemetrie des letzten Laufs (Run 2) und Vorschlag fuer einen gezielten Lauf

Stand: 07.11.2026. Alle Zahlen read-only aus `data/research2-usage.db`,
`data/research-usage.db`, der Run-2-Themen-DB und dem Lauf-Log
`data/runs/melatonin_net_run2.log`. Run 2 ist am 05.11. um 22:44 im
Rate-Limit-Backoff abgebrochen (Session `active`, `end_time` leer).

## Run 2: was der Lauf gekostet hat

| Kennzahl | Wert |
|---|---:|
| LLM-Aufrufe | 1324 |
| Tokens gesamt | 1632777 |
| LLM-Zeit (Summe der Aufrufe) | 8495.6 s |
| Fehler | 0 |
| Quellen | 101 |
| Tokens je Quelle | 16166 |
| Studien | 22 |
| Tokens je Studie | 74217 |
| Effekte | 8 (SE 2, CI 2) |
| Tokens je Effekt | 204097 |
| Suchanfragen (`query_stats`) | 154 Zeilen, 22 verschiedene |
| HTTP 429 im Log | 636 |
| Zyklen abgeschlossen / Fehler | 15 / 7 |

### Tokens je Phase

| Phase | Aufrufe | Tokens | Sekunden | Anteil |
|---|---:|---:|---:|---:|
| hypothesizing | 352 | 481810 | 1802.4 | 29.5 % |
| analyzing | 247 | 466976 | 2125.0 | 28.6 % |
| critiquing | 476 | 336627 | 2918.6 | 20.6 % |
| working | 182 | 267945 | 1187.7 | 16.4 % |
| synthesizing | 17 | 50342 | 296.9 | 3.1 % |
| searching | 46 | 26044 | 132.3 | 1.6 % |
| planning | 3 | 3006 | 29.0 | 0.2 % |
| idle | 1 | 27 | 3.7 | 0.0 % |

**78.7 % der Tokens** gingen in Hypothesen, Analyse und
Kritik. Die Suche kostete 26044 Tokens in 46 Aufrufen -
also rund 1184 Tokens je Suchanfrage.

Zum Vergleich das Themen-Konto `data/research-usage.db` (enthaelt
mehrere Laeufe, Tage 2026-10-27 bis 2026-11-05): 21891 Aufrufe,
31028477 Tokens. Run 1 allein ist daraus
nicht isolierbar - die Zahlen oben fuer Run 2 sind es, weil dessen
Usage-DB nur den 05.11. enthaelt.

## Was die Telemetrie ueber den Engpass sagt

* Das Lauf-Log enthaelt 636 429-Zeilen und 635 Rate-Limit-Nennungen; der Lauf starb
  im Backoff, nicht an einem Logikfehler.
* 1324 Aufrufe fuer 8 Effekte heisst: 166 LLM-Aufrufe je Effekt. Der
  groesste Teil davon sind Hypothesen- und Kritikschleifen, die zur
  Effektgewinnung nichts beitragen.
* Nur 2 von 8 Effekten tragen eine
  Praezision; aus den Textpfaden kommt fast nichts Poolbares.
* Die 43 XML-Dokumente des Korpus liefern deterministisch 31 Effekte
  (15 g, 16 OR) - ohne einen einzigen LLM-Aufruf. Der teure Teil des
  Laufs ist also nicht die Effektgewinnung, sondern die Hypothesen-
  und Analysesimulation.

## Vorschlag: ein gezielter Lauf auf genau ein Outcome

**Ziel:** mindestens zwei unabhaengige Studien mit Effekt **und**
Praezision zum selben Outcome auf derselben Skala - die kleinste
Einheit, aus der `build_analysis` eine gepoolte Schaetzung bildet.

**Outcome:** Sleep onset latency (SOL) in Minuten (mean difference)
oder standardisiert (Hedges g), je nachdem, was die Studien berichten.

**Ablauf, bewusst ohne Zyklen, Hypothesen und Kritik:**

1. **Zwei Suchen** (Limit aus `AGENTS.md`: 2-3 pro Frage):
   Europe PMC `(melatonin) AND (sleep onset latency) AND (randomized)`
   mit Filter `OPEN_ACCESS:y`, und Crossref als Gegenprobe auf
   Metaanalysen, deren eingeschlossene Studien als Seed dienen.
2. **Korpus deterministisch ziehen:** DOIs/PMCIDs der Treffer nehmen,
   Europe-PMC-XML laden (kein LLM), Reader laufen lassen
   (`effect_columns`, `arm_level`).
3. **Vor der Extraktion `mean_diff` ergaenzen:** Schlafstudien berichten
   SOL meist als Minuten-Differenz mit 95 %-CI, nicht als g. Ohne
   diesen Typ faellt genau die haeufigste Zeile weg.
4. **Pooling** mit `build_analysis`, Regel 'adjustiert vor crude',
   Gruppen nur auf gleicher Skala.
5. **Abbruchkriterium:** weniger als zwei unabhaengige Studien mit
   Praezision nach 40 XML-Dokumenten -> Frage als 'Korpus zu klein'
   berichten, nicht in einen zweiten Lauf investieren.

**Aufwand (geschaetzt, aus den Messwerten abgeleitet):**

* Netz: 2 Suchanfragen x 5 Provider plus ~40 XML-Downloads.
* LLM: 0 Tokens fuer Schritt 2-4. Nur wenn eine Relevance-Pruefung
  gewuenscht ist, kostet sie nach Run-2-Massstab ~1184
  Tokens je Anfrage - Groessenordnung 10^4 statt 1,6 x 10^6.
* Zeit: Minuten statt 3,25 h; kein 429-Risiko, weil keine
  Schleifen laufen.

**Risiko:** SOL steht haeufig nur als Arm-Mittelwert ohne Fallzahl je
Arm in den Tabellen (genau der Befund aus `arm_level_befund`). Dann
bleibt es bei k = 1, obwohl der Korpus gross genug ist. Deshalb ist
Schritt 3 (mean_diff) Pflicht, bevor der Lauf startet.

**Erfolgskriterium:** mindestens eine Gruppe mit k >= 2 und
berichteter Praezision; andernfalls dokumentierter Negativbefund.

