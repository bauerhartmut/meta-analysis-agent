# Goldstandard-Fundus (Entwicklungsauftrag v2 §9.2)

Referenzwerte aus **echten, veröffentlichten Metaanalysen**, gegen die die
Architektur gemessen wird: Precision/Recall der Studienauswahl, Fehlerquote
bei Zahlensextraktion, Abweichung der gepoolten Werte.

## Verifizierungsstatus — ehrlich benannt

Der Auftrag verlangt „menschlich verifizierte Referenzwerte". Der Stand:

- **agent-geprüft (Auszug verbatim):** Wert wurde aus dem zugänglichen
  Volltext/Abstract wörtlich entnommen, Quelle + Zitat stehen dabei.
- **agent-Sekundärquelle:** Wert aus zwei unabhängigen Sekundärquellen, der
  Original-Abstract war in der Recherchesession nicht ladbar (DOI angegeben,
  gegenprüfung möglich).
- **Kandidat:** nicht am Original geprüft, nur für spätere Erweiterung.

Du kannst jeden Eintrag in Minuten nachprüfen: DOI öffnen, den beigefügten
wörtlichen Vergleichszitaten (Ziffern beachten) gegenüberstellen. Sobald
ein Eintrag von dir abgenickt (oder korrigiert) ist, wird der Status
auf **menschlich verifiziert** gehoben. Der Benchmark-Harness behandelt
nicht verifizierte Einträge als informativ (Warnkommentar), nicht als
harte Abweichungsnorm — nichts gibt fehlende Verifikation geruhsam aus.

## Dateien

- `goldstandard.csv` — maschinenlesbare Einträge (Grundlage für den
  Benchmark-Runner aus §9.3).
- `goldstandard.md` — alle Einträge menschlich lesbar mit Zitaten und URLs.
- `pflegeblatt.md` — Pflegeblatt: was verglichen wird, Toleranzen, Strenge.

## Themenwahl

Das Thema ist der aktuelle Benchmark-Korpus des Runs (Kaffee akut vs.
Placebo, Reaktionszeit, gesunde Erwachsene) — der Goldstandard prüft genau
die Frage, für die es eine fertige Testrunde gibt.
