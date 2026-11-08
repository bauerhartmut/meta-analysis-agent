# Triage-Bericht gegen die Erwartung geprueft

Stand: 2026-11-08T14:26:09. Bericht: `data/bench/sol2/lieferung.json`. Kein Netz, kein Modell.

Erwartung aus `data/bench/sol2/schwelle_k5_20261108.md`: p = 0.2 poolbare Studien je gelesenem Dokument; Schritt-Ziel k >= 2, Gesamtziel k >= 5. Die Quote ist eine Annahme, keine Messung.

## Kennzahlen

| Kennzahl | Wert |
|---|---:|
| PDFs im Bericht | 0 |
| gelesen (ohne Scans) | 0 |
| poolbar | 0 |
| Scans ohne Textebene | 0 |
| Ausbeute (poolbar / gelesen) | - |
| Erwartungswert bei p = 0.2 | 0.0 |
| P(null poolbare Studie) | 1.0 |
| k nach Bericht | 1 |
| k aus den Dateien nachgerechnet | 1 |
| nicht geliefert (A-Liste) | 5 von 5 |

## Befunde

| Schwere | Befund |
|---|---|
| leer | Keine PDF gelesen (Verzeichnis: data/bench/sol2/volltext) - nichts zu pruefen, k bleibt bei 1. |
| hinweis | nicht geliefert: 11292231, 14566165, 28364493, 33157425, 41122831 |

## Was hier gerechnet und was angenommen ist

- Gerechnet: k = Basis + poolbare Dateien, Ausbeute, Erwartungswert
  n x p, Wahrscheinlichkeit einer Nullrunde (1 - p)^n, Abstand zum Ziel.
- Angenommen: p selbst. Der Wert stammt aus der Schwellenrechnung
  (1 von 5 Parallelstudien mit arm-level SOL) und ist dort als Annahme
  markiert. Weicht die gemessene Ausbeute deutlich ab, gehoert die
  Annahme fortgeschrieben - nicht dieses Skript.
- Nicht geprueft: ob die Extraktion inhaltlich richtig ist. Dafuer
  braucht es die Zitate in der DB je Zeile.
