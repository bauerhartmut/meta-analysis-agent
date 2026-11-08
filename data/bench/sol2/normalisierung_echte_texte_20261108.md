# Normalisierung an echten Volltexten: gehen Sätze oder Tabellen kaputt?

Datum: 2026-11-08
Frage: Zerstört die normalisierte PDF-Kette (`research_agent/meta/pdf_text.py`)
Sätze oder Tabellen in den 34 vorhandenen Volltexten?
Korpus: `data/bench/sol2/fulltext` (34 `.txt`, 997.366 Zeichen)
Prüfskript: `scripts/probe_normalize_fulltext.py`
Rohdaten: `data/bench/sol2/normalisierung_echte_texte_20261108.json`

## Ergebnis in einer Zeile

Kein harter Fehler, keine verlorene Tabellenzeile, keine veränderte Zahl;
ein Satz geht nicht kaputt. Auffällig ist nur eine Blockgrenze in einem
mathematiklastigen Paper, und dort wird **mehr** Text als Tabelle geschützt,
nicht weniger.

## Messwerte

| Prüfung | Befund |
|---|---|
| Dateien geprüft | 34 |
| Harte Fehler | **0** |
| Zahlen vor/nach (Ziffernfolgen) | identisch in allen 34 Dateien |
| Tabellarische Zeilen verloren | **0** |
| Tabellenblöcke (Summe) | 3 → 2 in einer Datei, sonst unverändert |
| Blockzeilen (Summe) | −37 (mehr erkannte Zeilen, siehe unten) |
| arm-Kandidaten | 0 → 0 |
| Dateien mit Warnung | 1 |

Harte Fehler heißt hier: eine Ziffernfolge aus dem Rohtext fehlt im
normalisierten Text oder steht in anderer Reihenfolge. Das trat nicht auf.
Damit sind auch Messwerte in Ergebnistabellen (Mittelwerte, SD, n, p) vor
einer stillen Veränderung geschützt.

## Der eine Warnfall: `94145c845eba5189f2cbc8824ed4fc7c.txt`

Rohtext: 3 Tabellenblöcke. Normalisiert: 2 Blöcke.

Nachgesehen (read-only, Blockgrenzen und Segmente verglichen):

- Die ersten beiden Blöcke (Zeichen 9.738–10.060 und 10.447–10.832) liegen
  nach der Normalisierung in **einem** Block 9.736–11.063 mit 16 Zeilen.
  Die Lücke dazwischen war nur Zeilenumbruch-/Leerraum-Struktur; der Inhalt
  beider Formelblöcke ist unverändert vorhanden.
- Der dritte Block wächst nach links: Er beginnt jetzt bei 11.176 und
  schluckt den Prosa-Absatz „assuming A = A(t, r) and B = B(t, r) in (9) …".
  Dieser Absatz steht danach **verbatim** im geschützten Block.

Bewertung: Das ist eine gröbere Blockgrenze, kein Textverlust. Geschützter
Bereich bedeutet „unverändert durchreichen", also bleibt der Absatz exakt
erhalten. Der Preis ist ein falsch-positiver Tabellenbereich von ca. 4.600
Zeichen in einem Paper zur Riemann-Geometrie. Für die Extraktion ist das
folgenlos: arm-Kandidaten 0 vor und 0 nach der Normalisierung, und dieses
Dokument ist keine Interventionsstudie.

## Warum „−37 Blockzeilen" kein Verlust ist

Die Zählung vergleicht erkannte Tabellenzeilen vor und nach der
Normalisierung. Ein negativer Wert heißt: nach der Normalisierung werden
**mehr** Zeilen als tabellarisch erkannt, weil zuvor zusammengeklebte
Zeilen wieder getrennt sind. Weniger erkannte Struktur wäre ein positiver
Wert — der tritt nicht auf.

## Was die Prüfung nicht abdeckt

- Keine Aussage über Scans ohne Textlayer (weiterhin 0 Zeichen, kein OCR
  vorhanden). Diese Dokumente bleiben Lücke, nicht Reparaturfall.
- Keine Aussage über PDFs, die erst nach dem TU-Darmstadt-Zugang dazukommen;
  die Prüfung ist wiederholbar (`scripts/probe_normalize_fulltext.py`).
- Die Prüfung vergleicht Rohtext gegen normalisierten Text, nicht gegen das
  PDF. Fehler der PDF-Extraktion selbst (Spaltenreihenfolge, Ligaturen)
  werden dadurch nicht aufgedeckt.

## Reproduktion

```
export PYTHONIOENCODING=utf-8
.venv/bin/python.exe scripts/probe_normalize_fulltext.py \
  --dir data/bench/sol2/fulltext \
  --json data/bench/sol2/normalisierung_echte_texte_20261108.json
```

Exit-Code 1 bedeutet mindestens ein harter Fehler. Beide Probeläufe
(`probelauf/` k = 3, `probelauf_bindestrich/` k = 1) liefern nach der
Änderung dieselben Werte wie vorher.
