# Anforderung B-Rücklauf (2026-11-11)

## Status

- `blind_b_20261110.zip` ist das ausgehende Blind-Paket, nicht der
  Rücklauf. Der Paket-Hash ist in
  `docs/internal/b_paket_integritaet_20261111.md` festgehalten.
- `data/golden_effects/goldstandard_B_ruecklauf.json` fehlt.
- Es ist kein B-Abgabe-Hash eingefroren.
- Im Workspace ist keine Empfängeradresse und kein E-Mail-Kanal
  hinterlegt. Der Versand muss daher über den vorgesehenen externen
  Weg erfolgen.

## Versandfertige Nachricht

**Betreff:** B-Rücklauf zum Blind-Paket `blind_b_20261110`

Hallo,

bitte senden Sie den vollständigen B-Rücklauf zurück:

- Datei: `data/golden_effects/goldstandard_B.json` aus dem Paket
- zusätzlich: SHA-256 dieser Datei
- Bestätigung, dass alle 30 Dokumente abgeschlossen sind

Bitte senden Sie keine Teilstände und keine anderen Dateien. Wir legen
die Datei als `data/golden_effects/goldstandard_B_ruecklauf.json` ab und
prüfen sie zuerst nur mit dem Trockenlauf. Erst bei 0 Fehlern und 0
offenen Dokumenten wird der B-Abgabe-Hash eingefroren. A bleibt bis
dahin geschlossen.

Das versandte Paket hat den SHA-256
`2f9db202c218abaf34bbabbb332c7e31d64693b0faed467dda3854e5a3b9b173`.
Bitte prüfen Sie vor der Rücksendung, dass Sie mit diesem Paket
gearbeitet haben.

Vielen Dank.

## Eingangskontrolle

Nach Eingang zuerst nur prüfen:

```bash
.venv/bin/python.exe scripts/pruefe_b_ruecklauf.py data/golden_effects/goldstandard_B_ruecklauf.json --keine-notiz
```

Der Lauf schreibt keine Abgabenotiz und friert nichts ein. Erst bei
Exit 0, 0 Fehlern und 0 offenen Dokumenten darf der Lauf ohne
`--keine-notiz` wiederholt werden.

## Automatischer Watcher

`scripts/b_ruecklauf_eingang.py` beobachtet die Rücklaufdatei und ruft
bei Änderungen ausschließlich den Trockenlauf mit `--keine-notiz` auf.
Der Watcher friert nie selbst ein.

## Abgrenzung

- Keine A-Datei geöffnet.
- Keine inhaltliche Bewertung des B-Rücklaufs.
- Kein Modellaufruf und kein Netzlauf.
