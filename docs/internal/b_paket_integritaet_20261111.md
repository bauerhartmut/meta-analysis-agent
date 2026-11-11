# B-Paketintegrität (2026-11-11)

## Zweck

Read-only-Prüfung des vorliegenden `blind_b_20261110.zip` ohne
inhaltliche Bewertung der B-Annotation. A wurde nicht geöffnet.

## Ergebnis

| Gegenstand | Wert |
|---|---|
| Datei | `blind_b_20261110.zip` |
| Größe | 605.293 Bytes |
| SHA-256 | `2f9db202c218abaf34bbabbb332c7e31d64693b0faed467dda3854e5a3b9b173` |
| Soll-Hash laut Übergabenotiz | `2f9db202c218abaf34bbabbb332c7e31d64693b0faed467dda3854e5a3b9b173` |
| Hash-Vergleich | identisch |
| ZIP-Test | `unzip -t`: keine Fehler |
| ZIP-Einträge | 67 |
| Volltexte im ZIP | 30 |
| Arbeitsblätter im ZIP | 30 |
| B-Rücklauf-JSON | `data/golden_effects/goldstandard_B_ruecklauf.json` fehlt |
| B-Gerüst-Hash | `93802e1798ae5e54ef3896e162e2fdeb2d783486a40239df590ddfa0dfe46d20` (unverändert) |

## Einordnung

Das ZIP ist laut Übergabenotiz das **ausgehende Blind-Paket** für die
externe Zweitannotation, nicht die B-Abgabe. Der Paket-Hash ist damit als
Transportreferenz bestätigt und festgehalten.

Ein B-Rücklauf als JSON liegt nicht vor. Deshalb ist **kein
B-Abgabe-Hash eingefroren**. Der Hash des B-Gerüsts bleibt unverändert;
er ist ebenfalls kein Abgabe-Hash.

## Nächster Schritt

1. Externen B-Rücklauf unter
   `data/golden_effects/goldstandard_B_ruecklauf.json` ablegen.
2. Zuerst nur prüfen:

       .venv/bin/python.exe scripts/pruefe_b_ruecklauf.py data/golden_effects/goldstandard_B_ruecklauf.json --keine-notiz

3. Bei 0 Fehlern und 0 offenen Dokumenten ohne `--keine-notiz` laufen
   lassen und den B-Abgabe-Hash einfrieren.
4. Erst danach A öffnen oder vergleichen.

## Abgrenzung

- Keine inhaltliche Bewertung der B-Annotation.
- Keine Änderung an `blind_b_20261110.zip` oder am B-Gerüst.
- Keine A-Datei gelesen.
- Kein Modellaufruf und kein Netzlauf.
