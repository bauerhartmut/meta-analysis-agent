# Patches an geschuetzten Kerndateien

Die Dateien unter "Kernbausteine: nicht oeffentlich" in `.gitignore`
(`orchestrator.py`, `report.py`, `meta/pooling.py`, `meta/extraction.py`, ...)
bleiben aus dem Repo heraus. Aenderungen daran sind erlaubt - sie muessen aber
nachvollziehbar bleiben, ohne dass der Quellcode ins Repo wandert.

## Regel (entschieden 2026-11-08)

1. Die Datei bleibt gitignored. Es wird kein Ausschnitt davon committet, auch
   kein Diff - ein Diff ist Quellcode.
2. Jede Aenderung bekommt hier einen Eintrag `<datei>_<thema>_<datum>.md` mit
   Anlass, betroffener Datei, Ankerpunkt, Wirkung, Pruefschritten und dem
   Stand der lokalen Sicherung.
3. Die lokale Sicherung liegt in `local_patches/` (gitignored). Der Eintrag
   nennt sie beim Namen, nicht ihren Inhalt.
4. Ein versioniertes Pruefskript macht den Zustand objektiv pruefbar:
   `python scripts/pruefe_report_patch.py`. Exit 0 = Patch wirksam,
   Exit 1 = mindestens ein Marker fehlt.
5. Eine Aenderung ohne Eintrag gilt als nicht dokumentiert - auch wenn sie
   lokal funktioniert.

## Warum kein Diff im Repo

Ein Patch von 20 Zeilen ist immer noch Quellcode aus einer Datei, die bewusst
nicht oeffentlich ist. Der Eintrag beschreibt deshalb den Ankerpunkt und die
Wirkung in Prosa; die Sicherung liegt lokal. Wer den Stand pruefen will, ruft
das Skript auf, statt den Code zu lesen.

## Bestehende Eintraege

| Eintrag | Datei | Status |
|---|---|---|
| `report_single_cluster_20261108.md` | `research_agent/report.py` | wirksam, Pruefskript Exit 0 |
