# Lizenzprüfung

Stand: 2026-11-11. Dies ist eine technische Inventur, keine Rechtsberatung.

## Yun et al. 2024

| Gegenstand | Befund |
|---|---|
| Repository-Code und -Daten | Apache License 2.0 (`LICENSE` im Repo) |
| Paper | PMLR/PMC-Veröffentlichung; Paper selbst nicht Teil des Repos |
| 120 Markdown-/XML-Texte | Auszüge aus PMC-Open-Access-Artikeln (Abstract + Results) |
| Lizenzmetadaten in den 120 XML-Dateien | **keine** `<license>`-Elemente; die Dateien sind inhaltsreduzierte Fragmente |
| Weitergabe der Artikeltexte | nicht allein durch Apache-2.0 gedeckt; die Bedingungen der jeweiligen PMC-Artikel müssen geprüft werden |
| Annotationen | als Teil des Repos unter Apache-2.0 veröffentlicht |

**Konsequenz:** Code und Annotationen sind klar nutzbar. Für eine
Weiterverbreitung der 120 Artikelauszüge ist die Lizenz jedes PMC-Artikels
separat zu prüfen. Für die lokale Evaluation ist das unkritisch; für ein
öffentliches Benchmark-Paket nicht.

## Evidence Inference 2.0

| Gegenstand | Befund |
|---|---|
| Repository-Code und Annotationen | MIT (`LICENSE`) |
| Offizielles v2.0-Archiv | Annotationen und Textdateien; README ohne eigene Lizenz, Repository ist MIT |
| Artikeltexte | 4.454 Textdateien aus PMC-Open-Access-Artikeln |
| Einzellizenzen der Artikel | nicht in der CSV; pro Artikel zu prüfen |
| Besonderheit | offizielles Archiv und Repo-Snapshot unterscheiden sich bei `annotations_merged.csv` und der Zahl der Textdateien |

**Konsequenz:** Annotationen und Code sind unter MIT nutzbar. Die
Artikeltexte sind nicht automatisch MIT-lizenziert; die jeweilige
PMC-Lizenz bleibt maßgeblich.

## DTA-Korpus

| Gegenstand | Befund |
|---|---|
| Datensatz | CC BY-NC 4.0 |
| Quellen | Cochrane-Reviews, überwiegend CC BY-NC |
| Kommerzielle Nutzung | ausgeschlossen |
| Volltexte | keine Primärstudien-Volltexte, nur Review-Extraktionen und Forest Plots |
| Zitation | Norman, Leeflang, Névéol, AMIA 2018 |

**Konsequenz:** Für nicht-kommerzielle Forschung nutzbar, aber wegen
NC-Bedingung und fehlender Primärtexte nicht als primärer B-Benchmark
geeignet.

## Unsere A/B-Dateien

Die bestehenden A- und B-Dateien wurden nicht verändert. Es wurden keine
A-Inhalte geöffnet und keine B-Rücklaufdaten eingefroren. Die neuen Dateien
liegen ausschließlich unter `public_benchmark/`.
