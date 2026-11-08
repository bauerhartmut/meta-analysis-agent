# Lohnt ein Spaltenaufloeser oder Vision-Lauf? Messung statt Annahme

Stand: 2026-11-08. Frage: Die Leser scheiterten an 26 Tabellenzeilen, weil
Kopfzeile und Zelle nicht dieselbe Spaltenzahl haben (`colspan`). Wenn diese
Zeilen Effektspalten tragen, waere ein Spaltenaufloeser (Text) oder ein
Vision-Lauf (Bild) gerechtfertigt. Wenn nicht, ist beides bezahlte Arbeit ohne
Ziel.

**Antwort: 0 von 26 Zeilen tragen eine Effektspalte. Beides lohnt nicht.**

## Messung

Kriterium: Die Kopfzeile enthaelt eine Effektbezeichnung (`g`, `smd`, `d`,
`or`, `rr`, `hr`, `beta`, `mean diff`, `md`, `ci`). Gezaehlt werden nur Zeilen,
deren Kopf- und Zellenzahl auseinanderfaellt - genau die, die der Leser
verwirft.

| Korpus | XML | Mismatch-Zeilen | davon Kopf mit Effektspalte |
|---|---:|---:|---:|
| Nachgeladene Dokumente (`xml_fetch_ncbi`) | 10 | 26 | **0** |
| Q1-Stichprobe (`xml_q1`) | 23 | 316 | 5 (alle falsch positiv) |
| **Summe** | **33** | **342** | **0 echte** |

## Warum die 5 Treffer keine sind

Alle fuenf stammen aus `PMC13454318` und haben dieselbe Form:

```
header  Characteristics | Almond group (n = 88) Mean (SD) (95%CI) | Control group ...
cells   Objective sleep parameters (polysomnography)          (4 Spalten gegen 1 Zelle)
```

Der Regex schlaegt auf das `CI` in `Mean (SD) (95%CI)` an. Die Zelle ist aber
ein **Abschnittstitel** ("Objective sleep parameters"), kein Messwert. Das ist
eine Gruppen-Kopfzeile, die der Leser zu Recht verwirft.

## Was das fuer die offenen Punkte heisst

| Punkt | vorher | jetzt |
|---|---|---|
| P2 Vision-Fallback | offen, braucht Original-PDFs | **erledigt (negativ)**: kein Ziel im Korpus, 0 von 26 Zeilen mit Effektspalte |
| P4 Vision-Seitenbudget | offen | **entfaellt** - ohne Ziel kein Budget |
| F3 Vision-Zeilen ersetzen/behalten | offen | **entfaellt** - es gibt keine Vision-Zeilen |
| F6 Seitenbudget erhoehen | offen | **entfaellt** |

Der Vision-Fallback liest **Bilder**. Die 26 Zeilen scheitern aber an einer
Spaltenstruktur im Text: eine Zeile mit vier Werten gegen einen Kopf mit einer
Zelle. Ein Bild derselben Tabelle haette dasselbe Problem - optisch sogar
schlechter, weil die Zuordnung dann geraten wird.

## Grenzen

- Die Messung prueft die **Kopfzeile** auf eine Effektbezeichnung, nicht den
  Inhalt der Zellen. Eine Zeile mit Kopf "Mean (SD)" und zwei Armen koennte
  theoretisch einen Behandlungseffekt tragen; sie wird aber vom Arm-Leser
  bearbeitet, nicht von diesem Gate, und der hat sie bereits geprueft
  (0 konvertierbar).
- Gezaehlt wurde auf den 33 XML der Stichprobe, nicht auf dem ganzen Korpus
  (1.056 XML). Fuer eine Aussage ueber den Gesamtkorpus waere derselbe Lauf
  dort zu wiederholen - offline und billig, aber eine andere Frage.

## Nachweis

Die Messung ist ein Lauf ueber `research_agent.research.jats_tables.parse_jats`
ohne Netz und ohne Modell. Sie steht als Skript in
`scripts/measure_colspan_rows.py` und ist damit wiederholbar.
