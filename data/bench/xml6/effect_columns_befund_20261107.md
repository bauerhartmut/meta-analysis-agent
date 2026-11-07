# Direkte Effektspalten: Modul, Tests, Messung

Stand: 07.11.2026. Leser: `research_agent/meta/effect_columns.py`
(`effect-column/1`), Tests: `research_agent/tests/test_effect_columns.py`,
Messung: `scripts/read_effect_columns_xml6.py`.

## Was der Leser tut

Der Spaltenkopf bestimmt den Effekttyp (`Hedges g`, `OR`, `RR`, `HR`, `IRR`,
`beta`, `SMD`) und das berichtete Niveau (`95 %`, `90 %`, `99 %`); die Zelle
liefert Punktwert und Intervall (`-0.22 (-0.32 to -0.17)`,
`2.78 (1.80-4.30)`, `1.38 (0.91, 2.11)`). Der Standardfehler kommt aus
`derive_se` - derselbe Verteilungsschluessel wie im Effekt-Extraktor, kein
Modell. Gespeichert wird nur, wenn das Zitat woertlich im Dokument steht
(`locate_quote`) und die Plausibilitaetspruefung besteht.

Ohne Intervall gibt es keine Zeile: ein Punktwert allein hat keinen
Standardfehler. `Median (IQR)`, `P value` und `No. of pairs` sind keine
Effektspalten. `Adjusted OR` wird als `adjusted = 1` markiert, die crude
Variante als `0` - beide bleiben getrennt, nichts wird gemittelt.

## Die Spaltenbreite ist die eigentliche Falle

`parse_jats` hat `colspan` in Kopfzeilen ignoriert: bei jamanetworkopen
stehen fuenf Kopfzellen ueber sieben Datenspalten, weil `Median (IQR)` zwei
Arme umfasst. Ohne Expansion haette der Leser `19.0 (14.6 to 23.2)` (Placebo-
Median) als Effekt gelesen. `jats_tables._rows_from` expandiert Kopfzellen
jetzt auf ihre echte Breite; Datenzellen bleiben unangetastet, weil eine
zusammengefasste Datenzelle ihren Wert doppeln wuerde. 89 Zeilen
bleiben mit unterschiedlicher Kopf- und Zellenzahl bewusst ungelesen.

## Tests

57 passed Tests gruen (Leser, Arm-Rechner, JATS-Parser, XML-first-Pfad).
Abgedeckt: Kopfvarianten und Niveaus, adjustierte Spalte, Zellformate mit
Unicode-Minus und Gedankenstrich, Punktwert ausserhalb des Intervalls,
fehlendes Intervall, colspan-Mismatch, fehlende Effektspalte, Zitat-Gate und
die Ablehnung eines negativen OR durch das Plausibilitaetsgate.

## Messung auf den sechs XML-Dokumenten

354 Tabellenzeilen, 245 mit passender Kopfbreite,
**31 gespeicherte Effekte** (Typen: g 15, or 16).

| Grund fuer Zeilen ohne Effekt | Zeilen |
|---|---:|
| keine Effektspalte im Kopf | 222 |
| Kopfbreite != Zellenzahl (colspan/rowspan) | 26 |
| Kopfbreite != Zellenzahl (colspan/rowspan) | 26 |
| keine Kopfzeile | 20 |
| Kopfbreite != Zellenzahl (colspan/rowspan) | 13 |
| Kopfbreite != Zellenzahl (colspan/rowspan) | 11 |
| Kopfbreite != Zellenzahl (colspan/rowspan) | 8 |
| Kopfbreite != Zellenzahl (colspan/rowspan) | 2 |
| Kopfbreite != Zellenzahl (colspan/rowspan) | 1 |
| Kopfbreite != Zellenzahl (colspan/rowspan) | 1 |
| Kopfbreite != Zellenzahl (colspan/rowspan) | 1 |

Beispiele, jeweils gegen die Rohzeile geprueft:

* `jamanetworkopen.2026.26983`: `% Stage REM` g = -0.22 (95 % CI -0.32 bis -0.11),
  SE 0.053572 aus dem Intervall; 15 Outcomes aus einer Effektspalte.
* `pcd20.230198`: `Short sleep duration` OR 2.78 (1.80-4.30), SE 0.637767;
  daneben dieselbe Zeile adjustiert OR 2.37 (1.50-3.76), `adjusted = 1`.

## Grenzen

* 89 Zeilen mit colspan/rowspan in Datenzellen bleiben unlesbar.
* Kein `n` in diesen Tabellen - die Zeilen sind poolbar, aber nicht
  gewichtet.
* Keine Umrechnung zwischen Massen (OR bleibt OR, g bleibt g).
* Alle gespeicherten Effekte stammen aus zwei der sechs Dokumente; die
  anderen vier fuehren keine Effektspalte mit Intervall.

## Konsequenz

Der direkte Spaltenleser liefert aus denselben sechs Dokumenten 31 poolbare
Zeilen, wo der Arm-Rechner 0 und der LLM-Extraktor 1 lieferte. Der Hebel war
nicht die SMD-Formel, sondern das Ablesen dessen, was die Tabelle schon
berichtet - plus die Reparatur der Kopfzeilenbreite, ohne die jede Zahl
um eine Spalte verrutscht waere.
