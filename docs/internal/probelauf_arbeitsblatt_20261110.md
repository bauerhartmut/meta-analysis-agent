# Probelauf-Annotation: Arbeitsblatt (2026-11-10)

Drei Dokumente, zwei unabhängige Annotatoren (A/B), Blindheit. Ziel:
Format- und Ablauftest (Pflichtfelder, Quotes, Design, Abgabe). Der
Zeilen-Kappa wird erst nach der Vollannotation aller 30 Dokumente
gemessen; Schwelle 0,80.

## Die drei Dokumente

| Dokument | Stratum | Design (Gerüst) | Zeichen | Volltext |
|---|---|---|---|---|
| `7111ea978757a185d44ea9de90b453c3` | cohort | observational; "Prospective multicenter cohort" | 97 367 | `data/fulltext/7111ea978757a185d44ea9de90b453c3.txt` |
| `bb9218735fec8fc7f3b6aebbff430aba` | rct | parallel_rct; "randomized, placebo-controlled study" | 71 085 | `data/fulltext/bb9218735fec8fc7f3b6aebbff430aba.txt` |
| `203c831dbeb178297006a888608f4f10` | aggregate | aggregate; "Prospective cohort studies (meta-analysis)" | 114 459 | `data/fulltext/203c831dbeb178297006a888608f4f10.txt` |

## Vor der Abgabe korrigiert

- `203c831dbe`: `design_category` stand in beiden Gerüsten und in
  `documents.json` auf `observational`. Eine Metaanalyse ist nach 5.1
  `aggregate`; A, B und die Auswahlmetadaten sind korrigiert. Der gepoolte
  Schätzer bekommt `is_primary: false`.

## Fallstricke

**7111 (Kohorte, Mediterran/Präeklampsie):** Ratio-Maße (OR/RR/HR) mit KI;
mehrere Adjustierungsmodelle und Untergruppen. Jede Kombination aus Outcome,
Vergleich, Zeitpunkt, Adjustierung und Population ist eine eigene Zeile.
Review-Passagen ohne eigenen Schätzer sind keine Zeile.

**bb92 (RCT, Melatonin):** Tabellen mit zwei Captions. z-Werte ohne KI/SE
sind erfassbar, aber `certainty` nur hoch, wenn die Unsicherheit klar ist;
p-only ist keine Zeile. Parallel-RCT, kein Crossover.

**203c (Aggregat, Mediterran/Rezidiv):** Nur der gepoolte Schätzer ist eine
Zeile, `is_primary: false`. Einzelstudien aus der Übersicht nicht übernehmen.
Wald-KI und Heterogenitäts-KI nicht vermischen; in `notes` festhalten, welches
KI berichtet ist.

## Ablauf

1. A und B getrennt; nur Volltext, Anleitung v1.1 und Schema. Keine Einsicht
   in `study_effects`, Pipeline-Ausgaben oder die Datei des anderen.
2. Gerüst füllen: `effects` oder `no_effect_reason`; Quote exakt mit
   `quote_start`/`quote_end`.
3. `.venv/bin/python.exe scripts/pruefe_probelauf_abgabe.py`; Exit 0,
   SHA-256 notieren.
4. Format auswerten: Zeilen und Begründungen je Dokument, die drei
   Designfälle. Keine Kappa-Zahl in diesem Schritt.
5. Kappa erst nach der Vollannotation aller 30 Dokumente:
   `.venv/bin/python.exe scripts/werte_kappa_probe.py` (ohne
   `--probelauf`, Schwelle 0,80); Konflikte mit dritter Stimme.

## Stand (Start)

- Gerüste: 30 Dokumente, 3 mit `probelauf: true`, 0 Zeilen, 0 Begründungen.
- `--entwurf`: 0 Fehler, 30 offen je Datei.
- Kappa: `null`; der Probelauf ist kein Kappa-Lauf, die Messung folgt
  nach der Vollannotation.
