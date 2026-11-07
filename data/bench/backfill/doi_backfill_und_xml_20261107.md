# DOI-Backfill per Crossref und XML-Ausbeute danach

Stand: 07.11.2026. Arbeit auf **Kopien** (`data/bench/backfill/run1.db`,
`run2.db`); die Lauf-DBs selbst blieben unveraendert (nur gelesen).

## Vorgehen

1. DOI aus der URL, wenn vorhanden (`10.xxxx/...` im Pfad).
2. Sonst Crossref `query.bibliographic` (3 Treffer, `select=title,DOI,type`).
3. Uebernahme nur bei **Titeldeckung >= 0.85** der kuerzeren Tokenmenge,
   **mindestens 6 gemeinsamen Tokens** und **>= 0.6 Abdeckung der Quell-Tokens**;
   sonst verworfen.

Die dritte Bedingung kam nach der ersten Messung dazu: kurze, generische
Treffer wie "Clinical Aspects of Alzheimer Disease" oder "Role of Melatonin
in the Regulation of Sleep" deckten eine lange Quellzeile scheinbar
vollstaendig ab (Score 1.0) und waren 8x die falsche Arbeit. Mit der
verschaerften Regel wurden 31 statt 14 Kandidaten verworfen.

## DOIs

| Lauf | Quellen | DOI vorher | aus URL | aus Crossref | verworfen | DOI nachher |
|---|---:|---:|---:|---:|---:|---:|
| Run 1 | 134 | 26 (19 %) | 18 | 74 | 16 | **118 (88 %)** |
| Run 2 | 101 | 22 (22 %) | 10 | 49 | 15 | **81 (80 %)** |

## Europe-PMC-XML vorher/nachher (gleiche Messmethode)

| Kennzahl | vorher (Original-DBs) | nachher (Backfill-Kopien) |
|---|---:|---:|
| DOIs geprueft | 55 | **161** |
| mit PMCID | 11 (20 %) | **58 (36 %)** |
| mit `fullTextXML` | 6 (11 %) | **42 (26 %)** |
| davon mit Tabellen | 5 | **39** |
| DOIs mit CI-Zeilen | 1 | **6** |
| DOIs mit SE-Zeilen | 1 | **7** |

Je Lauf nachher: Run 1 116 DOIs / 42 PMCID / 30 XML / 4 mit CI-Zeilen;
Run 2 81 DOIs / 30 PMCID / 22 XML / 2 mit CI-Zeilen.

## Die sechs ergiebigen XML-Quellen

| DOI | Tabellen | stat. Zeilen | SE-Zeilen | CI-Zeilen |
|---|---:|---:|---:|---:|
| 10.1001/jamanetworkopen.2026.26983 | 3 | 15 | 0 | 15 |
| 10.3389/fnut.2026.1890075 | 4 | 27 | 27 | 27 |
| 10.3390/healthcare13020180 | 4 | 1 | 0 | 1 |
| 10.3390/ijms27146320 | 4 | 3 | 0 | 1 |
| 10.3390/medicina62040662 | 3 | 6 | 0 | 6 |
| 10.5888/pcd20.230198 | 3 | 16 | 8 | 8 |

Zusammen 68 stat-reiche Zeilen, davon 35 mit SE und 58 mit CI - deutlich mehr
Unsicherheitsmaße als beide Laeufe zusammen aus ihren PDFs geholt haben
(Run 1: 1 SE/0 CI, Run 2: 2 SE/2 CI). Fuenf der sechs Quellen sind reine
OA-Zeitschriften (JAMA Netw Open, Frontiers, MDPI, Preventing Chronic
Disease), also genau die Fraktion, die der XML-Pfad erreicht.

## Grenzen

- Geprueft wird nur der Titel, keine Autoren oder Jahre. Die verschaerfte
  Regel verwirft kurze generische Treffer, eine Stichprobe der uebernommenen
  DOIs (z. B. 10 zufaellige gegen den Verlag) steht aber noch aus.
- Gemessen ist die **Verfuegbarkeit**, nicht die Extraktionsqualitaet: kein
  LLM, kein Netzlauf. Ob aus den 68 Zeilen poolbare Effekte werden und ob
  die Arme/Zeitpunkte richtig zugeordnet sind, ist offen.
- `check_xml_availability.py` zaehlt Tabellenzeilen mit SE/CI-Flags, nicht
  Effektwerte; die Zeilen sind Kandidaten, keine Ergebnisse.
- Der Backfill lief auf Kopien; fuer einen echten Lauf muss der Agent die
  DOI selbst mitbringen oder der Schritt gehoert in die Pipeline (dann
  kostet er pro Lauf ~150 Crossref-Anfragen).
