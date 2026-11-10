# Rohantwort gesichert: das Modell liefert ein Objekt, der Parser ist unschuldig

Stand: 2026-11-10. Skript `scripts/rohantwort_tudagpt_20261110.py`,
Rohantwort `rohantwort_20261110.txt`, Messwerte `rohantwort_20261110.json`.
Ein Modellaufruf, Dokument T1b (`bmj.e6664.full.pdf`), Topic `melatonin`,
`temperature=0.2`, `max_tokens=4096`.

## Messung

| Posten | Wert |
|---|---|
| Prompt | 26.161 Zeichen |
| Rohantwort | **522 Zeichen** |
| endet geschlossen (`]`/`}`) | ja - nicht abgeschnitten |
| `json.loads` | ok |
| Top-Typ | `dict`, 18 Schluessel |
| Listenwerte im Objekt | keine |
| dict-Objekte im Roh-JSON | **1** |
| `unwrap_json_list` | 1 Item |
| `EffectExtractor._normalize` | 1 Zeile |
| Wert-mit-Intervall im Rohtext | 1 |

Die eine Zeile:

```
outcome      "Total sleep time"
effect       22.4
se           11.173674706649921   (aus 0.5/44.3 abgeleitet)
ci_low       0.5     ci_high 44.3
effect_type  mean_diff
quote        "22.4 (0.5 to 44.3)*"
```

Das ist Tabelle 3 des BMJ-Papiers, Zeile **Total sleep time** - korrekt
gelesen, aber es ist nicht die gesuchte Zeile (SOL, -37,5). Die Antwort ist ein
einzelnes flaches Objekt, kein Array.

## Befund

**Der Parser verliert nichts.** `json.loads` liefert genau ein Objekt, und
`unwrap_json_list` gibt es korrekt als ein Item zurueck. Es gibt keine zweite
Zeile, die verloren gehen koennte.

**Die Ursache liegt im Zusammenspiel von Prompt und Antwortformat.** Der
Systemprompt verlangt woertlich "Return a JSON array with: ..." (in
`EffectExtractor._messages`), aber `chat_json` sendet auf
OpenAI-kompatiblen Backends `response_format: json_object` - ein nacktes
Top-Level-Array ist dort nicht erlaubt. Das ist im Repo selbst dokumentiert
(Docstring von `unwrap_json_list`: "a bare top-level array is not accepted in
that mode"). Das Modell muss also ein Objekt liefern und waehlt das
naheliegendste: den ersten berichteten Effekt.

Damit ist die Konstanz aus dem Neun-Dokumente-Lauf erklaert: **genau eine
Zeile pro Dokument, weil genau ein Objekt zurueckkommt** - unabhaengig davon,
wie viele Effekte im Text stehen. Der Fehler ist nicht dokumentabhaengig, er
ist formatbedingt.

## Zweite Schwachstelle, unabhaengig davon

`_LIST_ENVELOPE_KEYS` in `research_agent/llm/engine.py` kennt die Schluessel
`claims, facts, items, results, data, entries, list, hypotheses, questions,
queries, search_plans, plans, counterarguments, findings` - aber **nicht**
`effects` oder `rows`. Liefert ein Modell `{"effects": [...], "notes": [...]}`
mit zwei Listenwerten, greift keine der bekannten Tasten und
`unwrap_json_list` gibt `[result]` zurueck: eine Pseudo-Zeile mit leerem
`outcome` statt der Effektliste. Bei nur einem Listenwert (`{"effects": [...]}`)
funktioniert es dagegen, weil dann `len(list_values) == 1` greift.

## Was daraus folgt (nicht in diesem Schritt umgesetzt)

Der kleinste Fix ist eine Prompt-Aenderung: statt "Return a JSON array" die
Form `{"effects": [...]}` verlangen. Damit passt die Anweisung zum erzwungenen
`json_object`, und `unwrap_json_list` entpackt die Liste ohne Aenderung.

Die Datei ist `research_agent/meta/extraction.py`, also eine geschuetzte
Kerndatei: Aenderung nur mit Eintrag in `research_agent/patches/` und
`python scripts/pruefe_report_patch.py`, Sicherung in `local_patches/`.

## Grenzen

- Ein Dokument, ein Aufruf. Dass die Form `{"effects": [...]}` das Verhalten
  aendert, ist nicht gemessen - nur, dass die aktuelle Form ein Objekt erzwingt.
- Die Rohantwort ist gespeichert; der Parser-Teil ist damit offline
  wiederholbar, der Modellaufruf nicht.
