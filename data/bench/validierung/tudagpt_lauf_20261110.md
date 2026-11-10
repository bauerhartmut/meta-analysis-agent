# TUDaGPT-Lauf ueber neun Volltexte: eine Zeile pro Dokument

Stand: 2026-11-10. Test-ID `tudagpt-lauf-20261110`. Skript:
`scripts/pruefe_harness_tudagpt_20261110.py`, Rohdaten
`tudagpt_lauf_20261110.json`.

Aufbau: neun Dokumente, je **ein** Pass (`double_pass=False`), Topic
`melatonin`, `temperature=0.2`, `_one_pass` ohne Persistenz. Vor jedem Aufruf
wurde kostenlos geprueft, ob der belegte Sollwert im Prompt steht.

## Ergebnis

| Fall | Zeichen | Prompt | Soll im Prompt | Zeilen | SOL-Zeilen | Soll getroffen | Dauer |
|---|---:|---:|---|---:|---:|---|---:|
| T1 HTA-Text | 831.660 | 25.026 | ja | 1 | 0 | nein | 8 s |
| T1b BMJ-PDF | 53.914 | 26.161 | ja | 1 | 0 | nein | 27 s |
| T2 Wade | 79.042 | 26.161 | - | 1 | 0 | - | 4 s |
| T3 van Geijlswijk | 49.036 | 26.161 | - | 1 | 1 (-35,0, ohne SE/CI) | - | 11 s |
| T4 Sugumaran | 47.680 | 26.161 | ja | 1 | 0 | nein | 4 s |
| T5 Hayashi | 47.558 | 26.161 | ja | 1 | 1 (-17,0, ohne SE/CI) | nein | 5 s |
| T6 McArthur | 41.187 | 26.161 | - | 1 | 0 | - | 7 s |
| T7 Wright | 50.364 | 26.161 | - | 1 | 0 | - | 7 s |
| T8 Nunes | 29.322 | 26.161 | - | 1 | 0 | - | 4 s |

Tokens gesamt 62.619, Engine-Fehler 0. Vier Faelle hatten einen belegten
Sollwert (T1, T1b, T4, T5); **keiner** wurde getroffen. Zwei Faelle lieferten
ueberhaupt eine Zeile mit dem Outcome "sleep onset latency", beide ohne SE und
ohne Intervall - also nicht poolbar.

## Der eigentliche Befund

**Jedes der neun Dokumente ergab genau eine Zeile.** Das ist kein
dokumentabhaengiges Ergebnis, sondern ein konstantes Verhalten des Pfads. Bei
T1 war die eine Zeile "total night-time sleep time" - derselbe Ausgang wie in
E3a am 8.11. Damit liegt der Fehler zum dritten Mal vor (E3a, E3b, dieser
Lauf) und zum ersten Mal ueber acht verschiedene Dokumente hinweg.

Die Kette sieht den Satz: `soll_im_prompt` ist fuer T1, T1b, T4 und T5 wahr,
der Sollwert steht also im 26k-Prompt. Sie gibt ihn trotzdem nicht als Zeile
zurueck.

## Was der Lauf nicht zeigt

- **Die Ursache.** Gespeichert sind die normalisierten Zeilen, nicht die
  Rohantwort. Ob das Modell nur ein Objekt liefert oder `unwrap_json_list`
  eine verschachtelte Antwort zusammenzieht, ist damit offen. E3b sprach fuer
  das Modell (isolierter Satz, ebenfalls eine Zeile), aber bewiesen ist es
  nicht.
- **Haeufigkeit.** n = 1 Lauf je Dokument, keine Wiederholung; bei
  `temperature=0.2` kann ein zweiter Lauf anders ausgehen.
- **Die volle Kette.** Persistenz, Quote-Verifikation, zweiter Leser und
  dritter Klaerer liefen nicht (`double_pass=False`). Genau die Mechanik, die
  Vollstaendigkeit erzwingen soll, war aus.

## Bestandsaufnahme der Volltexte

Elf PDFs liegen in `data/bench/sol2/volltext/`, neun davon brauchbar:

- `Download.pdf` ist byte-identisch mit `19030713.pdf` (md5 `4072853751`) -
  ein Duplikat, kein zweiter Volltext.
- `35120753.pdf` ist HTML (2.737 Byte), kein PDF.
- `23098680.pdf` ist mit pypdf nicht lesbar (AES, `cryptography>=3.1` fehlt);
  fuer T1 wurde deshalb der lokale Text `23098680.txt` verwendet.

## Naechster Schritt (nicht in diesem Lauf)

Eine Rohantwort sichern (`llm.chat_json` direkt, ohne Normalisierung) und
`unwrap_json_list` gegen diesen Text pruefen - das kostet einen Aufruf und
entscheidet, ob der Fix im Parser oder im Prompt liegt. Erst danach ist ein
zweiter Lauf mit `double_pass=True` sinnvoll.

## Reproduktion

```bash
export PYTHONIOENCODING=utf-8
.venv/bin/python.exe scripts/pruefe_harness_tudagpt_20261110.py
```
