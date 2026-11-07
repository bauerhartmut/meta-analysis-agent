# XML-first-Volltextpfad (T4 Stufe 2)

Stand: 07.11.2026. Ziel war der im T0-Endvergleich benannte Engpass: SE/CI
fehlten in beiden Netzlaeufen, weil Volltexte als PDF kamen (Run 1: 17 PDFs,
1 SE, 0 CI). Europe PMC liefert fuer OA-Artikel strukturierte JATS-XML; die
wurde bisher nur genutzt, wenn die PMC-ID in der URL stand.

## Was jetzt passiert

1. **Aufloesung DOI -> PMCID** (`ContentExtractor._pmcid_for_doi`, Europe-PMC-
   Suche). Ohne sie ging jede DOI-Quelle direkt an Unpaywall, also an PDF.
2. **XML vor PDF** in `fetch_open_access_text`: erst `fullTextXML`, dann
   arXiv-PDF, dann Unpaywall. Ein PMC-Treffer beendet die Kette.
3. **Tabellen bleiben Tabellen**: der XML-Text wird mit Pipe-Zeilen gerendert
   (`coverage.manager._xml_to_text`) statt per Tag-Strip zu Fliesstext
   verschmolzen. Jede Zeile ist ein woertlicher Teilstring des gespeicherten
   Texts, also weiterhin zitierfaehig.
4. **Strukturierte Bloecke**: `jats_tables.blocks_from_jats` liefert je Tabelle
   Label, Caption, Zeilen und die stat-reichen Zeilen mit SE/CI/SD/N-Flags;
   der Orchestrator legt sie ueber `save_extracted_tables` als Artefakt ab
   (Parser-Kennung `jats-table/1`). Keine erfundenen Effektgroessen, nur
   Zellen und Flags.

## Zwei Renderer-Fehler, die dabei auffielen

- **Leere Zellen als `<td/>`** fielen aus der Zeile; alle folgenden Werte
  rutschten eine Spalte nach links (Arm und Zahl vertauscht). Der Renderer
  parst die Tabelle jetzt mit dem XML-Parser, Regex nur noch als Fallback.
- **`<.001` in einer Zelle** wurde vom nachfolgenden Tag-Strip als Tag
  gelesen und loeschte den Rest der Zeile. Zelltext wird vor dem Strip
  escaped und danach wieder unescaped.

## Messung auf dem 62-Dokumente-Korpus (`data/fulltext_inbox/*.xml`)

| Kennzahl | Wert |
|---|---|
| Tabellenbloecke | 149 |
| Zeilen gesamt | 2177 |
| Zeilen exakt im gerenderten Text | 2176 |
| Zeilen ueber `locate_quote` auffindbar | 1 |
| ohne Treffer | 0 |

Vor den Renderer-Fixes waren 752 Zeilen nicht auffindbar, 480 nach der
`<td/>`-Korrektur, 0 nach der Escape-Korrektur.

## Tests

- `research_agent/tests/test_xml_first_fulltext.py` (9 Tests): XML-first vor
  Unpaywall, PMCID-Lookup nur bei Bedarf, Tabellenzeilen im Text,
  strukturierte Bloecke im Ergebnis, Renderer-Treue (leere Zellen, `<.001`),
  Body-Zeilen als Teilstring des Texts.
- Betroffene Bestandssuiten gruen (173 passed: coverage, fulltext,
  llm_engine, table_extractor, meta_extraction, gather-Guard, jats_tables).

## Grenzen

- Der Netzpfad selbst wurde **nicht** neu gefahren (Lauf-Budget, keine
  Freigabe). Belegt ist die Offline-Kette vom XML bis zum zitierfaehigen
  Text und Artefakt; der Europe-PMC-Abruf ist ueber Fakes getestet, nicht
  gegen den Live-Endpunkt.
- `orchestrator.py` bleibt gitignored: die Ablage der JATS-Bloecke ist dort
  lokal verdrahtet und nicht Teil des Commits.
