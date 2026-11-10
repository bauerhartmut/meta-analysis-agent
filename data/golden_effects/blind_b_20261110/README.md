# Blind-Paket B (2026-11-10)

Dieses Paket enthaelt ausschliesslich die Zweitannotation B. Es enthaelt
keine A-Datei, keine A-Hashes, keine Checklisten und keine A-abgeleiteten
Entscheidungen. Bitte A nicht oeffnen und nicht vergleichen.

## Inhalt

- `data/golden_effects/goldstandard_B.json`: leeres Geruest, 30 Dokumente,
  Annotator B, blind.
- `docs/internal/goldstandard_annotationsanleitung.md`: Anleitung v1.2.
- `docs/internal/goldstandard_schema.json`: Schema.
- `docs/internal/vollannotation_arbeitsblatt_*.md`: 30 Arbeitsblaetter mit
  Tabellen- und Textfundstellen.
- `manifest.json`: Dokumente, Volltextpfade und SHA-256 von Volltext und
  Arbeitsblatt.
- `SHA256SUMS.txt`: Pruefsummen der Paketdateien.
- Im ZIP zusaetzlich: `data/fulltext/` mit den 30 Volltexten.

Das ZIP spiegelt die Repo-Struktur, damit der mitgelieferte Pruefer ohne
Anpassung laeuft. Es enthaelt nur Standardbibliothek, keine Projektabhaengigkeit.

## Ablauf

1. ZIP entpacken und im entpackten Ordner arbeiten.
2. Jedes Dokument im Volltext lesen; je Kombination aus Outcome, Vergleich,
   Zeitpunkt, Adjustierung und Population eine Zeile.
3. Quote exakt kopieren, `quote_start`/`quote_end` setzen.
4. Jedes Dokument abschliessen: Zeilen oder `no_effect_reason`.
5. Pruefen:

       python scripts/pruefe_goldstandard.py --entwurf data/golden_effects/goldstandard_B.json

   Erwartung am Anfang: 0 Fehler, 30 offen. Nach der Annotation ohne
   `--entwurf` pruefen, bis 0 Fehler.
6. Den ausgegebenen SHA-256 von `goldstandard_B.json` notieren und die Datei
   nicht mehr aendern. Erst danach darf A geoeffnet werden.

## Regeln

- Keine Zahlen umrechnen, nicht runden, keine Werte aus anderen Quellen.
- Keine Einzelstudien aus Uebersichtsarbeiten uebernehmen (5.8).
- p-Wert ohne Effektgroesse ist keine Zeile (5.7).
- Spannweiten ueber Zeitpunkte sind keine Zeile (5.11).
- `is_primary: false` nur bei gepoolten Schaetzern.
- `year` ist im Geruest ein String; das bestehende Format nicht aendern.

## Pruefung des Pakets

- 30 Dokumente, 30 Arbeitsblaetter, im ZIP 30 Volltexte.
- Keine Datei mit `goldstandard_A` im Namen.
- `manifest.json` und `SHA256SUMS.txt` stimmen mit den Dateien ueberein.
