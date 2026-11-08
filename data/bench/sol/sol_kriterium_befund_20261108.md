# Bringt ein weiteres SOL-Kriterium mehr? Messung an den vorhandenen Zeilen

Stand: 2026-11-08. Offen war die Sorge, der Zielmass-Schnitt sei zu eng: er
sucht woertlich `sleep onset latency`. Ein weiteres Kriterium ("sleep
latency", "SOL", "latency") koennte mehr Zeilen finden. Geprueft **an den
bereits extrahierten Zeilen** - kein Netz, kein Modell, keine neue Suche.

## Kriterium und Abgrenzung

Gesucht: Outcome enthaelt `latenc`, `sleep onset` oder `SOL`. Danach getrennt,
weil sonst die Zahl geschmeichelt waere:

- **anderer Endpunkt**: `wake after`, `rem`, `arousal` - WASO und REM-Latenz
  sind nicht Einschaflatenz.
- **Baseline**: `baseline`/`follow up` in einer Arm-Tabelle - Ausgangslage,
  kein Behandlungseffekt.
- **sol**: echte Einschaflatenz, inklusive subjektiver und log-skalierter
  Varianten (die Trennung kommt unten zurueck).

## Ergebnis

| Klasse | Zeilen | poolbar | Quellen |
|---|---:|---:|---:|
| **echte SOL** | 14 | 13 | 8 |
| anderer Endpunkt (WASO/REM) | 7 | 7 | 4 |
| Baseline-Zeilen | 4 | 4 | 1 |

Von den 8 Quellen der echten SOL-Zeilen sind 5 die bereits gezaehlten. Drei
sind neu im Zielmass-Schnitt - und **keine davon ist eine Melatonin-Studie**:

| Quelle | Intervention (Titel) | Zeile | warum nicht poolbar mit Melatonin |
|---|---|---|---|
| 10.2147/nss.s460882 | Washed Microbiota Transplantation bei IBD | OR 2,56 (SE 1,27) | kein Melatonin; OR ist nicht poolbar |
| 10.3389/fneur.2020.00611 | Tasimelteon bei Jetlag | Mitteldifferenz -13,9 min (SE 8,11) | Melatonin-**Rezeptoragonist**, andere Indikation, **subjektive** Latenz |
| 10.3389/fnins.2026.1816963 | rTMS bei Insomnie (Metaanalyse) | Mitteldifferenz +2,12 min (SE 7,57) | kein Melatonin; Metaanalyse, keine Primaerstudie |

Damit bleibt die Aussage **k = 1 fuer orales Melatonin** unveraendert. Das
breitere Kriterium liefert Zeilen, aber keine zweite Melatonin-Studie mit
Einschaflatenz in Minuten.

## Zwei Fallen, die die Messung sichtbar macht

1. **Andere Endpunkte sehen wie SOL aus.** 7 der Treffer sind WASO oder
   REM-Latenz - "sleep onset" steckt im Text, ist aber ein anderes Zielmass.
   Ohne die Abgrenzung waere die Ausbeute um 50 % zu hoch.
2. **Baseline-Zeilen sehen wie Effekte aus.** 4 Treffer sind "SOL baseline"
   und "SOL follow up" aus einer Arm-Tabelle. Genau dieser Fehler hat schon
   einmal eine Zeile als Behandlungseffekt gezaehlt (`q1_befund_20261108.md`).

## Hinweis zur Datengrundlage

Die Zeile `doi:10.1093/sleep/zsaa194` erscheint hier mit **-5,1 min**. Das ist
der alte, fehlerhafte Wert aus der Zeit vor dem Leser-Fix; korrekt sind
**-1,7 min (-5,1 bis 1,7)** (`schaetzer_pruefung_20261108.md`). Die
Mess-DBs `direct_label2.db`/`arm_label2.db` sind aelter als die Korrektur; fuer
diese Kriteriumsmessung ist das unerheblich, fuer jede gepoolte Zahl nicht.

## Grenzen

- Gezaehlt auf den gespeicherten Zeilen (1.099), nicht auf allen Saetzen der
  Volltexte. Der Fliesstext-Leser hat in diesem Korpus nur 1 Zeile
  beigetragen; dort ist nichts zu holen.
- Die Interventionszuordnung stammt aus den Manifest-Titeln, nicht aus einer
  Volltextpruefung. Bei den drei neuen Quellen ist sie eindeutig (Titel nennt
  Intervention und Design), bei Grenzfaellen waere sie zu belegen.
- Subjektive und apparative Latenz sind in der Klasse "echte SOL" gemeinsam
  gezaehlt. Fuer ein Pooling muessten sie getrennt werden - das gilt
  unabhaengig vom Kriterium.
