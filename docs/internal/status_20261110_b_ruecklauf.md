# Status B-Rücklauf und Prüfskript (2026-11-10)

Bezug: Stand seit `vollannotation_abgabe_checkliste_20261110.md`.
A und B bleiben getrennt; es gab keinen Vergleich zwischen A und B.

## Kurzfassung

- A ist vollständig: 69 Zeilen, 13 Begründungen, 0 offene Dokumente.
- B ist unverändert leer: 0 Zeilen, 0 Begründungen, 30 offene Dokumente.
- Das Prüfskript für den B-Rücklauf ist fertig, getestet und gepusht.
- Ein echter B-Rücklauf liegt noch nicht vor; es wurde kein Abgabe-Hash
  für B eingefroren.
- Kappa und Konfliktklärung sind noch nicht gestartet.

## Seit dem letzten Stand erledigt

### 1. Annotation A abgeschlossen

- 30 Dokumente bearbeitet, davon 12 Kalibrierungsdokumente und
  18 Ergänzungen.
- Ergebnis: 69 Effektzeilen, 13 Begründungen ohne Zeile, 0 offen.
- `pruefe_goldstandard.py --entwurf` meldet keine Regelverstöße.
- A-Hash:
  `d9bb867c303dc19ddaf90cce3414ada0f4484b5a03881d65261950db0762a810`
- Commits: `6b84ba1`, `9284cd0`, `f945e1d`.

### 2. Designkorrektur b5e492

- `b5e492` war als `parallel_rct` geführt, ist im Volltext aber eine
  Metaanalyse mit gepoolten Schätzern.
- Korrigiert auf `design_category: aggregate` und
  `design_verbatim: "meta-analysis of randomized controlled trials"`;
  `stratum: rct` bleibt.
- `documents.json`, A, B und die Checkliste sind konsistent.
- Dokumentiert in `docs/internal/goldstandard_design_b5e492.md`.

### 3. Blind-Paket für die externe Zweitannotation

- Vorlage im Repo: `data/golden_effects/blind_b_20261110/`.
- Enthält B-Gerüst, Anleitung v1.2, Schema, 30 Arbeitsblätter,
  Manifest, SHA256SUMS und Prüfer.
- Portables ZIP: `blind_b_20261110.zip` mit den 30 Volltexten.
- Im entpackten ZIP geprüft: B hat 0 Fehler und 30 offen; keine Datei
  mit `goldstandard_A` im Namen.
- Das ZIP ist absichtlich untracked und nicht committed.
- Commit der Vorlage: `04a9a15`.

### 4. Prüfskript für den B-Rücklauf

- Datei: `scripts/pruefe_b_ruecklauf.py`.
- Liest nur B-Gerüst, Rücklauf, Schema und Volltexte; A wird nicht
  geöffnet.
- Prüft:
  - `annotator: "B"` und `blind: true`;
  - genau 30 Dokumente und identischen ID-Satz;
  - keine doppelten, fehlenden oder zusätzlichen IDs;
  - unveränderte Designmetadaten;
  - je Dokument Zeilen oder `no_effect_reason`, nie beides;
  - eindeutige `effect_id`s;
  - alle Regeln des bestehenden Prüfers ohne `--entwurf`.
- Schreibt nur bei 0 Fehlern und 0 offenen Dokumenten eine Abgabenotiz
  mit SHA-256 und Vollständigkeitstabelle. Eine vorhandene Notiz wird
  nicht überschrieben.
- Schutzregeln: A-Dateien werden abgewiesen; Rücklauf und Gerüst
  dürfen nicht dieselbe Datei sein.
- Commit: `c74e23e`.

## Aktueller Stand

| Gegenstand | Stand |
|---|---|
| `goldstandard_A.json` | 69 Zeilen, 13 Begründungen, 0 offen, 30 Dokumente |
| A-Hash | `d9bb867c303dc19ddaf90cce3414ada0f4484b5a03881d65261950db0762a810` |
| `goldstandard_B.json` | 0 Zeilen, 0 Begründungen, 30 offen, 30 Dokumente |
| B-Hash (Gerüst) | `93802e1798ae5e54ef3896e162e2fdeb2d783486a40239df590ddfa0dfe46d20` |
| B-Rücklauf | liegt nicht vor |
| B-Abgabe-Hash | nicht eingefroren |
| Prüfskript | vorhanden, getestet, gepusht |
| Kappa | nicht gestartet |

## Ausgeführte Prüfungen

Am Prüfskript sind folgende Fälle getestet:

| Fall | Erwartung | Ergebnis |
|---|---|---|
| `py_compile` | 0 | 0 |
| leeres B-Gerüst | Exit 1, 30 offen, keine Notiz | erfüllt |
| A-Datei als Eingabe | Exit 1, keine Notiz | erfüllt |
| B als eigene Referenz | Exit 1 | erfüllt |
| synthetischer vollständiger Rücklauf | Exit 0, Notiz mit 30 Zeilen | erfüllt |
| ID-Abweichung | Exit 1, fehlende und zusätzliche ID | erfüllt |
| vorhandene Notiz | Exit 1, kein Überschreiben | erfüllt |

Der synthetische Rücklauf trug nur Testbegründungen. Sein Hash
`d728d49af5310f8c5732f054cfd2147815c5f3e570093ecb4270c3397fade6dc`
ist kein Abgabe-Hash und wurde nach dem Test gelöscht.

## Offene Punkte und Risiken

- Ohne echten B-Rücklauf ist nur die Struktur und Vollständigkeit
  geprüft, nicht die inhaltliche Annotation.
- B darf erst eingefroren werden, bevor A geöffnet oder verglichen
  wird; sonst ist die Blindheit verletzt.
- Es wurden keine Netzläufe und keine Modellaufrufe gestartet.
- Das portable ZIP bleibt untracked; es enthält Volltexte und gehört
  nicht ins Repository.

## Nächster Ablauf

1. Externen B-Rücklauf entgegennehmen und unter
   `data/golden_effects/goldstandard_B_ruecklauf.json` ablegen.
2. Zuerst nur prüfen:

       .venv/bin/python.exe scripts/pruefe_b_ruecklauf.py data/golden_effects/goldstandard_B_ruecklauf.json --keine-notiz

3. Bei Fehlern den Rücklauf an die annotierende Person zurückgeben;
   keine inhaltlichen Korrekturen selbst vornehmen.
4. Bei 0 Fehlern und 0 offenen Dokumenten ohne `--keine-notiz` laufen
   lassen und die Abgabenotiz mit SHA-256 erzeugen.
5. B-Hash in der Abgabe-Checkliste eintragen; B nicht mehr ändern.
6. Erst danach A öffnen und Kappa/Konflikte berechnen:

       .venv/bin/python.exe scripts/werte_kappa_probe.py
       .venv/bin/python.exe scripts/berichte_kappa_konflikte.py --md docs/internal/kappa_konflikte_vollannotation_20261110.md --out data/golden_effects/kappa_konflikte_vollannotation.json
       .venv/bin/python.exe scripts/priorisiere_kappa_konflikte.py --quelle data/golden_effects/kappa_konflikte_vollannotation.json --md docs/internal/kappa_konflikte_priorisiert_vollannotation_20261110.md --out data/golden_effects/kappa_konflikte_priorisiert_vollannotation.json

## Empfehlung

Den B-Rücklauf abwarten und anschließend nur das Prüfskript laufen
lassen. Das kostet keinen Netzlauf und keinen Modellaufruf. Der größte
Hebel ist der eingefrorene B-Hash vor dem Öffnen von A; ein vorgezogener
Vergleich würde die Unabhängigkeit der Zweitannotation zerstören und
die Kappa-Auswertung entwerten.
