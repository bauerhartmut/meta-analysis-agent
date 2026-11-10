# Pruefung der Pass-B-Zeile e8ba18ca3525 (Quelle 85a47de24314)

Stand: 2026-11-10 · read-only · keine Modellaufrufe · keine DB-Aenderung

## Die Zeile

| Feld | Wert |
|---|---|
| Zeilen-ID | `e8ba18ca3525` |
| Quelle | `85a47de24314` (Papamichael et al., Systematic Review and Meta-Analysis, 2026) |
| Outcome | Cancer recurrence or cancer-specific mortality |
| Vergleich | Higher post-diagnosis Mediterranean Diet adherence vs. lower adherence |
| Effekt | HR 0.83 (95%-KI 0.7–0.99, I² = 49%), n = 6697 |
| Gespeicherte SE | 0.073980951 |
| Design | Prospective cohort studies (meta-analysis) |
| Lesepass | 2, nicht strittig, kein Ablehnungsgrund gespeichert |
| Zitat-Span | 2398–2569 |

## Volltextbeleg

Datei `data/fulltext/203c831dbeb178297006a888608f4f10.txt`, Stelle 2398–2569:

> "Eight studies met inclusion criteria: six prospective cohort studies assessed
> recurrence (n = 6697), and two RCTs assessed CRF (n = 76). For recurrence,
> higher post-diagnosis MD adherence was associated with a lower hazard of
> recurrence or cancer-specific mortality (HR = 0.83; 95% CI: 0.70–0.99;
> I 2 = 49%)."

Das Zitat ist wortgleich gespeichert, die Zahl korrekt uebertragen. Die Zeile
ist also **kein Lesefehler**.

## Warum sie nicht in den Pool darf

Der HR ist der **gepoolte Schaetzer einer Uebersichtsarbeit** ueber sechs
prospektive Kohorten, kein Effekt einer Primaerstudie. Wuerde er neben
Primaerstudien gepoolt, gingen dieselben Teilnehmer zweimal ein, gewichtet nach
dem Modell der Uebersichtsarbeit.

Das Gate greift bereits: `aggregate_design("Prospective cohort studies
(meta-analysis)")` erkennt "meta-analy", `standardize` weist die Zeile ab, und
`build_analysis` fuehrt sie in `excluded` mit dem Grund

> Uebersichtsarbeit ('Prospective cohort studies (meta-analysis)'), keine Primaerstudie

Sie steht in keiner Gruppe und auch nicht in `off_target`. **Entscheidung: Die
Zeile bleibt draussen; es ist keine Aenderung noetig.** Sie bleibt als Zeile mit
Zitat und Grund im Bericht sichtbar.

## Zusatzbefund: die SE passt nicht zum berichteten KI

- SE aus dem berichteten 95%-KI: (ln 0.99 - ln 0.70) / (2 * 1.96) = **0.0884**
- gespeichert: **0.0740** - das sind **16.3 % zu klein**
- KI aus der gespeicherten SE: 0.718–0.960 statt 0.7–0.99

Der Punktschaetzer stimmt, die Praezision ist zu optimistisch. Fuer den Pool ist
das hier folgenlos, weil das Aggregat-Gate vorher greift; fuer primaere Zeilen
mit demselben Muster waere es ein Fehler. Die Abweichung ist nicht repariert
worden - sie ist ein Befund, keine stille Korrektur.

## Folge fuer die Klassifikation

Mit `standardize` als Massstab (statt "hat Zahl und SE") sinkt die Zahl der
poolbaren Zeilen unter den 45 von 20 auf **16**. Alle sieben `nur_pass_b`-Zeilen
sind unpoolbar; die zuvor als poolbar gezaehlte Zeile war genau diese
Uebersichtsarbeit. Im Pool stehen weiterhin 4 Zeilen, keine davon aus den
`nur_pass_b`.
