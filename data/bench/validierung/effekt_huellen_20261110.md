# effects-Huelle: aus einer Zeile werden fuenf und dreizehn

Stand: 2026-11-10. Skript `scripts/pruefe_effekt_huellen_20261110.py`,
Messwerte `effekt_huellen_20261110.json`, Rohantworten
`effekt_huellen_T1b_20261110.txt` und `effekt_huellen_T4_20261110.txt`.
Zwei Dokumente, je ein Pass, `temperature=0.2`, `double_pass=False`, Topic
`melatonin`.

## Vorher und nachher

| Fall | vorher (flaches Objekt) | nachher (effects-Huelle) | Soll getroffen |
|---|---|---|---|
| T1b BMJ | 1 Zeile, 0 mit SE, Rohantwort 522 Zeichen | **5 Zeilen, 5 mit SE**, Rohantwort 3.108 Zeichen | **2 von 2** (-37,5 und -45,3) |
| T4 Sugumaran | 1 Zeile, 0 mit SE, keine SOL | **13 Items, davon 6 numerisch mit SE**, Rohantwort 11.309 Zeichen | **1 von 1** (8,36) |

Die fuenf Zeilen aus T1b: Total sleep time 22,4; Sleep onset latency -37,5;
Total sleep time 13,3; Sleep onset latency -45,3; Sleep efficiency 4,03. Alle
fuenf mit abgeleitetem SE, alle fuenf vom Plausibilitaets-Gate akzeptiert.

Die sechs numerischen Zeilen aus T4 tragen PSQI 1,87, ESS 1,25, NMSS 6,11,
PDQ-39 8,12, Polysomnographie-Latenz 8,36 und Polysomnographie-TST 14,51. Die
uebrigen sieben Items nennen nur Nebenwirkungen ohne Zahl (Drowsiness, Nausea,
Dizziness, Fatigue, Headache, Decreased appetite, ...); das Gate verwirft sie
mit "kein Effektwert gelesen". Das ist die gewuenschte Reaktion, kein Verlust.

## Antwortform

Beide Antworten sind jetzt `{"effects": [...]}` - die Huelle, die
`unwrap_json_list` ohne weitere Aenderung entpackt. Die zuvor belegte
Ein-Objekt-Form ist verschwunden.

## Kosten

Drei Aufrufe (ein Health-Check plus zwei Extraktionen), 18.775 Tokens,
0 Fehler, 102 Sekunden. T1b: 8.008 Prompt- und 1.040 Completion-Tokens in
22,8 s. T4: 5.958 Prompt- und 3.742 Completion-Tokens in 79,1 s.

## Was der Lauf zeigt und was nicht

Gezeigt: Der Widerspruch zwischen "Return a JSON array" und
`response_format: json_object` war die Ursache der konstant einen Zeile. Mit
passender Huelle liefern beide Dokumente mehrere Zeilen, alle Sollwerte
werden getroffen, und zum ersten Mal kommt eine poolbare Zeile mit SE heraus.

Nicht gezeigt: Reproduzierbarkeit (n = 1 je Dokument bei `temperature=0.2`),
Vollstaendigkeit gegen die Tabellen (T1b hatte mindestens sechs berichtete
Effekte, fuenf kamen zurueck), und das Verhalten des zweiten Lesers und des
dritten Klaerers - die liefen nicht.
