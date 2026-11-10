# Spannweiten über Zeitpunkte in den 30 Goldstandard-Dokumenten (2026-11-10)

Read-only, kein Modellaufruf. Anlass: Regel 5.11 der Annotationsanleitung
soll vor der Annotation bekannt sein. Gesucht wurde in allen 30 Volltexten
nach Korrelationen in eckigen Klammern, `range`/`from ... to`, Zeitpunkt-
formulierungen und Zwei-Zahlen-Klammern.

## Ergebnis

- 30 Dokumente, 0 fehlende Dateien, **127 Regex-Treffer**, 8 Dokumente ohne
  Treffer.
- Treffer nach Art: 74 `range`, 23 `von_bis`, 7 `zeitpunkte`,
  17 `klammer_zwei_zahlen`, 6 `korrelation_spanne`.
- **Ein echter 5.11-Fall: `3790c91f96`.** Alle sechs
  `korrelation_spanne`-Treffer liegen in diesem Dokument; die Spannweiten
  für emotionale und körperliche Symptome sind bereits in
  `goldstandard_entscheidung_3790c91f96.md` aufgelöst.
- **Kein weiteres Dokument** berichtet eine Spannweite über Zeitpunkte.
- Zwei Klammer-Kandidaten sind Konfidenzintervalle, keine Zeitpunktspannen:
  `87079ba88a` (`[-9.22, -4.56]`, 95%-KI) und `2675c25aab` (sechs
  `CI [..]`-Klammern). Dasselbe gilt für `5cbf039f22`.
- Die übrigen Treffer sind Skalenbereiche (z. B. CES-D 0–30), Altersspannen,
  Erhebungsjahre, Follow-up-Dauern, Interventionsdauern (5–22 Wochen),
  Sitzungsdauern (30–90 min) und Dosisbereiche (600–970 METs). Sie sind
  keine Effektzeilen und lösen 5.11 nicht aus.

## Geprüfte Kandidaten

| Dokument | Stratum | Treffer | Bewertung |
|---|---|---|---|
| `3790c91f96` | cohort | 6 × `korrelation_spanne` | **5.11 ja**: EDS `rs=[−0.150, −0.206]`, PDS `rs=[−0.225, −0.266]`; Tabelle 2 löst sechs Zeilen auf. Dokumentiert. |
| `87079ba88a` | crossover | `klammer_zwei_zahlen` | nein: 95%-KI `[-9.22, -4.56]`. |
| `2675c25aab` | cross_sectional | 6 × `klammer_zwei_zahlen` | nein: `CI [..]`, Konfidenzintervalle. |
| `5cbf039f22` | aggregate | `klammer_zwei_zahlen`, `range` | nein: KIs; Interventionsdauern 5–22 Wochen. |
| `7111ea9787` | cohort | `zeitpunkte`, `range` | nein: Assessment-Zeitpunkte (8–13, 16–22, 24–29 Wochen); Effektspanne 22–69 % über Studien, nicht über Zeitpunkte. |
| `09843d40d3` | cohort | `zeitpunkte` | nein: Panel T1–T3, keine Effektspanne. |
| `334f5f6798` | aggregate | `range` | nein: Dosisbereiche 600–970 METs. |
| `203c831dbe` | aggregate | `range` | nein: Rezidivraten 30–80 %. |
| `cfc6567ca3` | aggregate | `range` | nein: Sitzungsdauern 30–90 min. |
| `71c86b675b` | rct | `von_bis` | nein: 93 % auf 48 % nach 6 Monaten, ein Vorher-Nachher-Wert. |

Die vollständige Trefferliste mit Satzkontext steht in
`data/golden_effects/spannweiten.json`.

## Konsequenz

- Regel 5.11 bleibt wie ergänzt; eine weitere Schärfung ist nach dieser
  Prüfung nicht nötig.
- Die Regex ist ein Suchnetz, keine Entscheidung. Der einzige echte Fall
  wäre ohne bewusste Prüfung als KI oder Skalenbereich durchgegangen.
- Für `3790c91f96` bleibt es bei der dokumentierten Entscheidung: EDS und
  PDS sind getrennte Outcomes je Zeitpunkt; die Pipeline hat zwei EDS-Zeilen
  ohne `time_point` und keine PDS-Zeile. Der Abgleich wertet das als
  Recall-Lücke.

## Prüfung

- Skript: `scripts/pruefe_spannweiten.py` (read-only, kein Modellaufruf).
- Rohdaten: `data/golden_effects/spannweiten.json`.
- Stichprobe der Treffer in der Konsole gesichtet; die Bewertung oben ist
  menschlich, nicht automatisch.
