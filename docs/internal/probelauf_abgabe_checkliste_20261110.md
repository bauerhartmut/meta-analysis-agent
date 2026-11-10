# Abgabe-Checkliste Probelauf (2026-11-10)

Für A und B identisch, aber getrennt auszufüllen. Während der
Annotation kein Austausch; nur Volltext, Anleitung und Schema.

## Stand

| Datei | Zeilen | Begründungen | offen | Probelauf-Dokumente |
|---|---|---|---|---|
| `goldstandard_A.json` | 0 | 0 | 3 | 3 |
| `goldstandard_B.json` | 0 | 0 | 3 | 3 |

Aktuelle Hashes (Stand nach der Designkorrektur):

- A: `d11b28301475840b90af51a2fd0d1aabe1d5d9eab765d19b9a54455e8d584f91`
- B: `3b3759e7df357791fc9dd0dae3c14ba8687fc2209564c5bf895eb557f23fe327`

Die Hashes sind **Startwerte**. Nach dem Ausfüllen ändern sie sich;
der Abgabe-Hash wird vom Prüfer ausgegeben und unten eingetragen.

## Die drei Designfälle

### 7111ea9787

- Design: `aggregate` / `narrative review`
- Schicht: `cohort`
- Prüfpunkt: 5.8: Hat das Dokument einen eigenen gepoolten Schaetzer? Wenn nein, keine Zeile und no_effect_reason; Einzelstudien nicht uebernehmen.

### bb9218735f

- Design: `parallel_rct` / `randomized, placebo-controlled study`
- Schicht: `rct`
- Prüfpunkt: 5.7: p-Wert ohne Effektgroesse ist keine Zeile; nur berichtete Effekte mit Unsicherheit.

### 203c831dbe

- Design: `aggregate` / `systematic review and meta-analysis`
- Schicht: `aggregate`
- Prüfpunkt: 5.8: gepoolte Schaetzer als je eine Zeile mit is_primary: false; Einzelstudien nicht uebernehmen.

## Vor der Abgabe (je Annotator)

- [ ] Nur die drei Probelauf-Dokumente bearbeitet; die übrigen 27
      bleiben unberührt.
- [ ] Jedes der drei Dokumente hat Zeilen oder `no_effect_reason`.
- [ ] Alle 14 Pflichtfelder je Zeile und 9 Dokumentpflichtfelder sind
      gesetzt.
- [ ] Jede `quote` ist exakt; `quote_start`/`quote_end` passen.
- [ ] Kein Effekt umgerechnet, keine Zahl gerundet.
- [ ] Ratio-Werte positiv; Effekt liegt im KI.
- [ ] `is_primary: false` nur bei gepoolten Schätzern.
- [ ] `design_category` nach 5.1; 5.11 bei Spannweiten über Zeitpunkte.
- [ ] 5.7 geprüft: p-Wert ohne Effektgröße ist keine Zeile.
- [ ] 5.8 geprüft: Einzelstudien aus Übersichten nicht übernehmen.

## Abgabe

1. `python scripts/pruefe_probelauf_abgabe.py` ausführen; Exit 0.
2. Den ausgegebenen SHA-256 unten eintragen.
3. Datei committen und nicht mehr ändern.
4. Erst danach vergleichen.

## Nach der Abgabe

- `python scripts/werte_kappa_probe.py --probelauf`
- `python scripts/berichte_kappa_konflikte.py --probelauf`
- `python scripts/priorisiere_kappa_konflikte.py`
- Konflikte für die dritte Stimme; Schwelle Zeilen-Kappa 0,80.

## Abgabe-Hashes

- A: ______________________________
- B: ______________________________

