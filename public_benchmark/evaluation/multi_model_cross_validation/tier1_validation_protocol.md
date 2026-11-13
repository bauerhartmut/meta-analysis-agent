# Protokoll Stufe 1: externe Validierung ohne neue Annotation

Stand: 2026-11-13
Datensatz: [`tier1_validation_set_v1.jsonl`](tier1_validation_set_v1.jsonl)
Dokumentlage: [`tier1_documents_v1.json`](tier1_documents_v1.json)
Skripte: `public_benchmark/scripts/goldstandard/`

## Zweck

Prüfen, wie gut Qwen 3.5 397B, DeepSeek V4.1 Flash und GLM 5.3 numerische
Armwerte aus RCT-Publikationen extrahieren, **bevor** Zeit in die
Referenzannotation der 25 Artikel geht. Stufe 1 ersetzt die Annotation nicht:
Sie prüft nur Zahlen und Armzuordnung, nicht die Provenienzfelder.

## Datenbasis

| Kennzahl | Wert |
|---|---:|
| Records | 185 |
| Zellen | 744 |
| European Urology: Records / Zellen | 104 / 486 |
| GLASS: Records / Zellen | 81 / 258 |
| Cluster: Urology-Trials | 20 |
| Cluster: GLASS-Publikationen | 45 |
| Records ohne Zellwerte | 0 |

Jede Zelle hat `cell_id`, `label`, `arm` (bei GLASS `null`), `statistic` und
`value`. Werte fehlen, wo die Quelle sie nicht nennt; sie wurden nicht ergänzt.

## Dokumentverfügbarkeit

Abfrage über Europe PMC am 13.11.2026:

| Status | Records |
|---|---:|
| open-access Volltext vorhanden | 75 |
| nur Abstract | 103 |
| nicht gefunden | 7 |

Davon European Urology: 20 Volltext, 77 nur Abstract, 7 nicht gefunden.
GLASS: 55 Volltext, 26 nur Abstract.

Damit gibt es zwei Varianten:

- **Variante A (sofort):** 75 Records mit OA-Volltext. Klein, aber ohne
  Beschaffungsaufwand.
- **Variante B (vollständig):** 185 Records, dafür PDFs der übrigen 110
  Publikationen beschaffen. Das ist organisatorisch, nicht technisch begrenzt.

## Aufgabe für die Modelle

Je Record: Volltext (XML oder PDF) plus Outcome-Bezeichnung und Armnamen; das
Modell liefert je Zelle Wert, Arm und Statistiktyp. Kein Few-Shot-Beispiel aus
demselben Record, keine Nachbearbeitung durch ein zweites Modell.

GLASS-Zellen haben keinen Armbezug in den Golddaten. Dort wird nur
Label-plus-Wert geprüft; Armvertauschungen sind für GLASS nicht definiert.

## Metriken

- **Zellgenauigkeit**: exakter Treffer je Zelle (Toleranz 1e-6).
- **Record-Genauigkeit**: alle Zellen eines Records richtig.
- **Coverage**: Anteil beantworteter Zellen.
- **Armvertauschung** (nur European Urology): Wert stimmt exakt mit dem
  Gegenarm überein und nicht mit dem eigenen.
- **Cluster-Bootstrap** über Studien, 1.000 Runden, Seed 20261113, für die
  Zellgenauigkeit.

Ausgewertet wird getrennt nach Datensatz, nie gepoolt über beide.

## Was Stufe 1 nicht leistet

- Keine Provenienzbewertung: Seite, Tabelle, Zelle, Zeitpunkt fehlen im
  Goldstandard selbst.
- Keine Aussage über unsere 25 Artikel.
- Keine Zeitpunkt-Genauigkeit, weil kein Datensatz Zeitpunkte führt.
- GLASS-Felder sind heterogen (HR, Events/Total, sample); ein Wertvergleich
  über verschiedene Feldnamen hinweg ist nicht sinnvoll, deshalb
  Label-Bindung.

## Machbarkeit und Grenzen

- 20 Urology-Cluster sind wenig. Der Bootstrap wird breit sein; ein nicht
  signifikanter Unterschied bleibt ein Nicht-Ergebnis.
- 20 der 104 Urology-Records haben OA-Volltext; die übrigen brauchen PDFs.
- Die Urology-Goldwerte sind in vier Arbeitsmappen identisch, aber ohne
  Belegstelle. Ein Treffer belegt also die Zahl, nicht den Fundort.

## Ablauf

1. `build_tier1_validation_set.py` — Datensatz bauen (erledigt).
2. `prepare_tier1_documents.py` — Dokumentlage prüfen (erledigt).
3. PDFs für Variante B beschaffen, falls gewünscht.
4. Extraktionslauf je Modell — **erst nach ausdrücklicher Freigabe**, mit
   `max_tokens` 12000 für GLM.
5. `evaluate_tier1.py --predictions ... --out ... --bootstrap 1000`.

Der Lauf selbst ist nicht Teil dieses Schritts.
