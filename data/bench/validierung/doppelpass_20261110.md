# Doppelpass auf T1b und T4: was der zweite Leser wirklich prueft

Stand: 2026-11-10. Skript `scripts/pruefe_doppelpass_20261110.py`, Messwerte
`doppelpass_20261110.json`. Aufruf in derselben Reihenfolge wie
`EffectExtractor.extract`, aber ohne `_store`: keine Datenbank, keine
Persistenz. Topic `melatonin`, Pass A `effect_first` bei 0,2, Pass B
`precision_first` bei 0,4, Klaerer nur bei Konflikt.

## Zeilen gegen die Tabellen

| Fall | Pass A | Pass B | gemeinsam verglichen | Konflikte | Klaerer | Soll |
|---|---|---|---|---|---|---|
| T1b BMJ | 5 Zeilen, 5 mit SE | 5 Zeilen, 5 mit SE | 3 Schluessel | 1 (direction) | 1 zugunsten A | **3 von 3** |
| T4 Sugumaran | 13 Zeilen, 6 numerisch | 6 Zeilen, 6 numerisch | 3 Schluessel | **3 (Quote 1,0)** | 0 zugunsten A, 0 zugunsten B, **3 ungeklaert** | **1 von 1** (8,36) |

T1b: Beide Paesse lesen dieselben fuenf Werte (TST 22,4; SOL -37,5; TST 13,3;
SOL -45,3; Sleep efficiency 4,03). Der einzige Konflikt betrifft die
Richtungsangabe bei SOL; der dritte Leser bestaetigt Pass A, Pass B bleibt
strittig. Alle drei belegten Tabellenwerte (-37,5; -45,3; 22,4) werden von
A, B und dem Endstand getroffen.

T4: Beide Paesse lesen dieselben sechs Zahlen, aber nur drei davon unter
demselben Schluessel (PSQI 1,87; ESS 1,25; NMSS 6,11). Dort widersprechen sie
sich in **allen drei** Faellen bei `unit`, `direction` und `population`:
Pass A sagt "points / higher score", Pass B "PSQI points / lower score" - bei
identischem Zahlenwert. Das ist die Vorzeichenfrage (hoeherer Score =
schlechter), und der Klaerer entscheidet sie nicht: 3 von 3 bleiben
ungeklaert. Die uebrigen drei Zahlen werden nie gegengelesen, weil die Labels
abweichen: PDQ-39 8,12, Polysomnographie-Latenz 8,36 (A) gegen "Sleep latency"
(B), Polysomnographie-TST 14,51 gegen "Total sleep time".

## Drei Befunde

**B1 - Duplikate im Pool.** `extract` speichert bei Einigkeit beide Paesse
(`_store(first)` plus `_store(second)`), `_normalize` vergibt je Zeile eine
neue `gen_id()`, `_insert` schreibt `INSERT OR REPLACE` - es entstehen zwei
Zeilen mit derselben Zahl und demselben SE, beide `disputed = 0`.
`pooling.py:169` verwirft nur strittige Zeilen, nicht `extraction_pass`. Folge:
jeder bestaetigte Effekt traegt doppelt in den Pool, bei halbem Varianzanteil -
das Konfidenzintervall wird zu schmal. Bei T1b waeren das 10 Zeilen fuer 5
Effekte. **Das ist ein Codebefund, nicht im Pooling gemessen**: der Lauf rief
`_store` nicht auf.

**B2 - der Schluesselvergleich ist stringbasiert.** `_match_key` vergleicht
Outcome, Vergleich und Richtung als Text. Zwei Lesungen desselben Effekts mit
anderer Formulierung finden sich nicht, gelten damit stillschweigend als
einvernehmlich und bleiben beide poolbar. Bei T4 betrifft das drei der sechs
Zahlen, darunter den Sollwert 8,36, der so als **zwei** Zeilen in die Analyse
geht.

**B3 - der Klaerer hilft nur bei Feldern, nicht bei Richtungen.** Bei T1b
loest er den einen Konflikt auf; bei T4 stimmt seine Lesung mit keiner Seite
ueberein, und alle drei Widersprueche bleiben offen. Ungeklaert heisst hier:
sechs Zeilen, keine davon poolbar - das ist die ehrliche, aber unbrauchbare
Ausbeute fuer dieses Dokument.

## Was das fuer die Frage "mehr Zeilen" bedeutet

Die Huelle hat das Ein-Objekt-Problem geloest, aber der zweite Leser erzeugt
aus 5 Zeilen 9 poolbare und aus 6 numerischen Zeilen 6 poolbare - nicht weil
er mehr findet, sondern weil er Doppel zaehlt und Nicht-Matches als
Uebereinstimmung behandelt. Die Zahl der Zeilen ist damit **kein**
Qualitaetsmass; belastbar ist nur die Zahl der gegengelesenen Schluessel
(T1b 3, T4 3).

## Kosten

Sieben Aufrufe (ein Health-Check, je Dokument A + B + Klaerer), 52.395 Tokens
(42.167 Prompt, 10.228 Completion), 161,7 Sekunden, 0 Fehler. Der Einfachlauf
zuvor brauchte 18.775 Tokens - Faktor 2,8. Der dritte Leser kostet je Dokument
rund 9.000 Tokens.

## Grenzen

n = 1 je Dokument und Pass, `temperature` 0,2 bzw. 0,4, kein `_store`, keine
Datenbank, kein Pooling. Ob B1 im echten Lauf zum Tragen kommt, haengt daran,
ob eine spaetere Stufe `extraction_pass` filtert - im Code ist keine zu
finden; gemessen ist es nicht.
