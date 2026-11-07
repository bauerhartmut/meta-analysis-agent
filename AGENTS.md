# Arbeitsregeln für dieses Repository

Diese Datei hält fest, wie in diesem Projekt gearbeitet wird. Sie gilt für
jede Sitzung.

## Antworten und Sprache

- Antworten auf Deutsch.
- **Keine chinesischen Zeichen** in Code, Kommentaren, Commits oder Dateien.
- Keine Secrets im Chat und im Code. `.env` nie lesen oder ausgeben.

## Commits

- Kleine, thematische Commits. Jeder Commit endet mit:

  ```
  🤖 Generated with Codebuff
  Co-Authored-By: Codebuff <noreply@codebuff.com>
  ```

- Push ist dauerhaft freigegeben; kein Force-Push, keine History-Rewrites.
- `research_agent/orchestrator.py` ist gitignored und geschützt: lokal ändern
  ist erlaubt, **niemals committen**.

## Läufe und Kosten

- Netzläufe sind teuer und rate-limit-anfällig: höchstens 2-3 pro
  Untersuchungsfrage, keinen Lauf ohne ausdrückliche Freigabe starten oder
  abbrechen.
- Vor einem neuen Netzlauf: Telemetrie des letzten Laufs auswerten, nicht
  blind wiederholen.

## Qualitätsregeln

- Keine erfundenen Werte. Jede Zahl im Bericht muss aus DB, Log oder einer
  nachrechenbaren Quelle stammen; Schätzungen werden als solche markiert.
- Diagnosen zuerst read-only und auf DB-Kopien, nie auf laufenden Datenbanken.
- Jeder Arbeitsschritt hinterlässt ein Artefakt (Skript, JSON, Markdown) und
  einen Commit.

## Am Ende jeder Antwort

- Eine kurze, konkrete **Empfehlung für den nächsten Schritt** mit Begründung
  (was bringt den größten Hebel, was kostet Zeit/Guthaben, was ist riskant).
