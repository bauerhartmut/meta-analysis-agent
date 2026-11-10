# Übergabe: Externe B-Annotation (2026-11-10)

## Zweck

Dieses Dokument begleitet das Blind-Paket für die unabhängige
Zweitannotation B des Goldstandards. Es richtet sich an die extern
annotierende Person. A ist nicht Teil des Pakets und darf nicht
eingesehen werden.

## Paket

- Datei: `blind_b_20261110.zip`
- SHA-256:
  `2f9db202c218abaf34bbabbb332c7e31d64693b0faed467dda3854e5a3b9b173`
- Inhalt: 30 Volltexte, 30 Arbeitsblätter, B-Gerüst, Anleitung v1.2,
  Schema, Manifest, Prüfsummen und Prüfer.
- Im ZIP gilt die Struktur `blind_b_20261110/`; alle Befehle werden im
  entpackten Ordner ausgeführt.

## Regeln

- Die Annotation erfolgt unabhängig und manuell am Volltext. A nicht
  öffnen, nicht vergleichen und keine A-abgeleiteten Dateien verwenden.
- Keine Zwischenabgabe: erst alle 30 Dokumente abschließen, dann
  zurückschicken.
- Keine Zahlen umrechnen, nicht runden und keine Werte aus anderen
  Quellen ergänzen.
- Jede Zeile braucht eine exakte `quote` sowie passende
  `quote_start`/`quote_end`.
- Jedes Dokument braucht entweder Effektzeilen oder einen ausgefüllten
  `no_effect_reason`; beides zugleich ist nicht zulässig.
- `year` bleibt ein String.
- `is_primary: false` nur bei gepoolten Schätzern.
- 5.7: p-Wert ohne Effektgröße ist keine Zeile.
- 5.8: keine Einzelstudien aus Übersichtsarbeiten übernehmen.
- 5.11: eine Spannweite über Zeitpunkte ist keine Zeile; je Zeitpunkt
  eine Tabellenzeile.
- Negativkontrollen nur bei einem echten quantifizierten Effekt mit
  Unsicherheit als Zeile erfassen; sonst begründen.
- Design am Volltext bestimmen, nicht aus dem Titel ableiten.
- Maßgeblich sind `goldstandard_annotationsanleitung.md`,
  `goldstandard_schema.json` und das jeweilige Arbeitsblatt.

## Ablauf

1. ZIP entpacken und im Ordner `blind_b_20261110/` arbeiten.
2. Optional die Paketprüfsummen prüfen:

       sha256sum -c SHA256SUMS.txt

   Unter Windows PowerShell alternativ mit `Get-FileHash` arbeiten.
3. Zuerst die 12 Kalibrierungsdokumente bearbeiten, danach die übrigen
   18; die fünf Negativkontrollen zuletzt.
4. Pro Dokument alle relevanten Effekte erfassen oder das Dokument
   begründet als effektlos abschließen.
5. Nach jedem Dokument den Entwurfsprüfer laufen lassen:

       python scripts/pruefe_goldstandard.py --entwurf data/golden_effects/goldstandard_B.json

   Am Anfang ist die Erwartung: 0 Fehler, 30 offen. Nach der
   vollständigen Annotation ohne `--entwurf` prüfen:

       python scripts/pruefe_goldstandard.py data/golden_effects/goldstandard_B.json

   Der Lauf muss mit 0 Fehlern und 0 offenen Dokumenten enden.
6. SHA-256 der fertigen Datei bilden:

       sha256sum data/golden_effects/goldstandard_B.json

   Unter Windows PowerShell:

       Get-FileHash data/golden_effects/goldstandard_B.json -Algorithm SHA256

7. Die Datei nach dem Hash nicht mehr ändern.

## Rückgabe

Zurückzuschicken sind:

- `data/golden_effects/goldstandard_B.json`
- der SHA-256 dieser Datei
- eine kurze Bestätigung, dass alle 30 Dokumente abgeschlossen sind

Bitte keine anderen Dateien verändern und keine Teilstände zurücksenden.
Das Paket wird nach der Rückgabe gegen das Gerüst geprüft; erst danach
wird der Hash eingefroren und A geöffnet.

## Rückfragen

Rückfragen nur zur Anleitung, zum Schema oder zur Technik. Fragen zu
A-Entscheidungen oder ein Vergleich mit A sind während der Annotation
nicht zulässig.
