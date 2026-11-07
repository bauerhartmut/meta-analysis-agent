# DOI-Backfill per Crossref und XML-Ausbeute danach

Stand: 07.11.2026. Arbeit auf **Kopien** (`data/bench/backfill/run1.db`,
`run2.db`); die Lauf-DBs selbst blieben unveraendert (nur gelesen).

## Vorgehen

1. DOI aus der URL, wenn vorhanden (`10.xxxx/...` im Pfad).
2. Sonst Crossref `query.bibliographic` (3 Treffer, `select=title,DOI,type`).
3. Uebernahme nur bei Titeldeckung >= 0.85 der kuerzeren Tokenmenge und
   mindestens 3 inhaltstragenden Tokens; sonst verworfen.

## DOIs

| Lauf | Quellen | DOI vorher | aus URL | aus Crossref | verworfen | DOI nachher |
|---|---:|---:|---:|---:|---:|---:|
| Run 1 | 134 | 26 (19 %) | 18 | 84 | 6 | **128 (96 %)** |
| Run 2 | 101 | 22 (22 %) | 10 | 56 | 8 | **88 (87 %)** |

## Europe-PMC-XML vorher/nachher (gleiche Messmethode)

| Kennzahl | vorher (Original-DBs) | nachher (Backfill-Kopien) |
|---|---:|---:|
| DOIs geprueft | 55 | **174** |
| mit PMCID | 11 (20 %) | **60 (34 %)** |
| mit `fullTextXML` | 6 (11 %) | **43 (25 %)** |
| davon mit Tabellen | 5 | **40** |
| DOIs mit CI-Zeilen | 1 | **6** |
| DOIs mit SE-Zeilen | 1 | **7** |

Je Lauf nachher: Run 1 125 DOIs / 43 PMCID / 30 XML / 4 mit CI-Zeilen;
Run 2 88 DOIs / 31 PMCID / 23 XML / 2 mit CI-Zeilen.

## Die sechs ergiebigen XML-Quellen

| DOI | Tabellen | stat. Zeilen | SE-Zeilen | CI-Zeilen |
|---|---:|---:|---:|---:|
| 10.1001/jamanetworkopen.2026.26983 | 3 | 15 | 0 | 15 |
| 10.3389/fnut.2026.1890075 | 4 | 27 | 27 | 27 |
| 10.3390/healthcare13020180 | 4 | 1 | 0 | 1 |
| 10.3390/ijms27146320 | 4 | 3 | 0 | 1 |
| 10.3390/medicina62040662 | 3 | 6 | 0 | 6 |
| 10.5888/pcd20.230198 | 3 | 16 | 8 | 8 |

Zusammen 68 stat-reiche Zeilen, davon 35 mit SE und 58 mit CI - mehr
Unsicherheitsmaße als beide Laeufe zusammen aus ihren PDFs geholt haben
(Run 1: 1 SE/0 CI, Run 2: 2 SE/2 CI).

## Grenzen

- Der Abgleich prueft nur Titel, keine Autoren/Jahre. Ein falscher DOI wuerde
  eine fremde Arbeit als Volltext ins Korpus ziehen; die Schwelle 0.85 ist
  deshalb streng gewaehlt und 14 Kandidaten wurden verworfen. Eine Stichprobe
  der uebernommenen DOIs steht noch aus.
- Gemessen ist die **Verfuegbarkeit**, nicht die Extraktionsqualitaet: es lief
  kein LLM und kein Netzlauf. Ob aus den 68 Zeilen poolbare Effekte werden,
  ist damit noch offen.
- `check_xml_availability.py` zaehlt Tabellenzeilen mit SE/CI-Flags, nicht
  Effektwerte; die Zeilen sind Kandidaten, keine Ergebnisse.
