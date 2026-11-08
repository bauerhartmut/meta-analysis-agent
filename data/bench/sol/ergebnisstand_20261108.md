# Ergebnisstand der SOL-Untersuchung (zitierfaehig)

Stand: 2026-11-08. Alle Zahlen stammen aus den unten genannten Artefakten
dieses Repos und sind mit den dort genannten Skripten nachrechenbar.

## Befund

Der Melatonin-Korpus traegt **keine gepoolte Aussage zur Einschaflatenz**.
Von 1099 gespeicherten Effektzeilen betreffen 13 das Zielmass
(1,2 %), sie stammen aus 7 Quellen; nach den Design- und
Baseline-Gates bleiben **11 Zeilen aus 5 Quellen**. Fuer orales Melatonin
bleibt **k = 1**. Ein gepoolter Wert wird nicht berichtet.

Der Korpus ist vollstaendig ausgewertet: 1059 Manifest-Eintraege, alle
Volltexte gelesen (1.056 aus dem Lauf plus 3 ueber NCBI nachgeladen; 33 von 33
der Suchstichprobe, davon 10 ebenfalls ueber NCBI, nach 30 x HTTP 500 bei
Europe PMC).

## Kennzahlen

| Kennzahl | Wert |
|---|---:|
| Manifest-Eintraege | 1059 |
| gespeicherte Effektzeilen | 1099 |
| davon poolbar (technisch) | 422 |
| SOL-Zeilen / Anteil | 13 / 1,2 % |
| SOL-Quellen | 7 |
| SOL-Zeilen nach Gates / Quellen | 11 / 5 |
| unabhaengige Melatonin-Studien mit SOL in Minuten | **1** |

## Die vier widerlegten Ausbeute-Hebel

Jeder wurde gebaut, einzeln gemessen und hatte bei der Einschaflatenz **null**
Wirkung - bei deutlichem Gewinn an Gesamtzeilen:

| Hebel | Wirkung auf die Ausbeute | Wirkung auf SOL |
|---|---|---|
| Mehrzeilige Kopfzeilen, colspan/rowspan | Kandidaten 539 -> 1.115 (+576), gespeichert 523 -> 1099 | 13 -> 13 (**0**) |
| Outcome-Label aus Zwischenueberschrift/Caption | Zeilen ohne Label 232 -> 2 | 13 -> 13 (**0**) |
| Arm-Rechner paart getrennte Mean-/SD-Spalten | poolbare Zeilen 152 -> 422 | lesbar 18 -> 18 (**0**) |
| Fliesstext-Leser (5.820 SOL-Saetze, 316 mit SD) | 1 zusaetzliche Zeile | 0 lesbar (**0**) |

Dazu zwei weitere, ebenfalls gemessene Hebel:

| Hebel | Messung | Ergebnis |
|---|---|---|
| Spaltenaufloeser / Vision-Fallback | 342 Zeilen mit Kopf/Zellen-Mismatch | 5 Kopfzeilen mit Effektbezeichnung, davon **0 echte** -> kein Ziel |
| Weiteres SOL-Kriterium (`latenc`, `sleep onset`, `SOL`) | 14 echte SOL-Zeilen aus 8 Quellen | 3 neue Quellen, **keine Melatonin-Studie** -> k = 1 bleibt |

Zur Abgrenzung derselben Messung: 7 Treffer sind WASO- oder
REM-Latenz und 4 sind Baseline-Zeilen. Ohne diese Trennung waere die
Ausbeute um ueber 70 % zu hoch.

## Nachtrag: die zehn fehlenden Dokumente

Die 10 Dokumente, die Europe PMC mit HTTP 500 verweigerte, kamen ueber NCBI
efetch und wurden gelesen: 62 Tabellenzeilen, 0 Effekte,
0 SOL. Die frueher notierte Unsicherheit ("10 Dokumente ungeprueft") ist damit
aufgeloest.

## Was daraus folgt

1. Weitere Leser-Fixes an diesem Korpus haben keine Grundlage: vier gemessene
   Hebel brachten bei SOL null, die zwei zusaetzlichen haben nachweislich kein
   Ziel.
2. Ein breiteres Zielmass-Kriterium erzeugt Varianten derselben Studien, keine
   neuen Studien.
3. Was fehlt, ist **anderer Korpus** (Population, Interventionsdefinition),
   nicht ein besserer Leser und nicht ein anderes Label.

## Belege

| Datei | Inhalt |
|---|---|
| `zeilen_summe_20261108.json` | 1099 gespeicherte, 422 poolbare Zeilen (aus den vier Mess-DBs gezaehlt) |
| `zielmass_schnitt_label2_20261108.json` | 13 SOL-Zeilen, Anteil 1,2 % |
| `schaetzer_pruefung_20261108.md` | 11 SOL-Zeilen aus 5 Quellen, k = 1, Leserfehler-Korrektur |
| `effect_columns_paired_20261108.md` | 37 korrigierte Werte (u. a. zsaa194: -1,7 statt -5,1) |
| `colspan_befund_20261108.md` | 342 Mismatch-Zeilen, 0 mit Effektspalte |
| `sol_kriterium_befund_20261108.md` | 14 Zeilen aus 8 Quellen, 3 neue ohne Melatonin |
| `xml_nachladen_20261108.md` | 10 Dokumente ueber NCBI, 62 Zeilen, 0 Effekte |
| `probleme_und_offene_fragen_status_20261108.md` | Endstand der elf Punkte |
