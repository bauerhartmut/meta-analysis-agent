# Abschlussbericht Lauf 2026-11-08: Ausbeute, Zielmass, Konsequenz

Frage des Laufs: Traegt der SOL-Korpus eine gepoolte Aussage zur
Einschlaflatenz (SOL) unter Melatonin?

Kurze Antwort: **Nein.** 13 der 1.099 gespeicherten Effektzeilen betreffen das
Zielmass (1,2 %), sie stammen aus 7 Quellen, sind auf zwei Skalen verteilt und
enthalten genau eine standardisierte Zeile. Ein gepoolter Wert wird nicht
behauptet.

Alle Zahlen unten stammen aus den Messdateien dieses Laufs (Funnel, Konverter,
Zielmass-Schnitt, Textmessung) und sind mit den genannten Skripten
nachrechenbar. Es gab in diesem Lauf keinen Netzzugriff und keinen Modellaufruf.

## 1. Korpus und Ausbeute

| Stufe | Zahl | Quelle |
|---|---:|---|
| Manifest-Eintraege | 1.059 | `funnel_20261108.json` |
| XML vorhanden / fehlend | 1.056 / 3 | ebenda |
| SOL-RCT-Kandidaten (Muster) | 946 | ebenda |
| erkannte Tabellen | 2.735 | ebenda |
| Tabellenzeilen | 41.821 | ebenda |
| Saetze (Fliesstext) | 315.857 | ebenda |
| Kandidaten (Effekte) | 1.115 | ebenda |
| gespeichert | **1.099** | `effect_columns_label2_*.json`, `arm_level_label2_*.json` |
| durch Pruefungen verworfen | 6 | ebenda |
| poolbar (Zeilen) | 422 | `funnel` mit den neuen DBs |

Die 6 Verwuerfe haben einen einzigen Grund: `unbekannter Effekttyp 'irr'` im
Plausibilitaetsgate. Kein Zitatfehler, kein fehlender Standardfehler.

Zusammensetzung der 422 poolbaren Zeilen: 323 aus Effektspalten (Mitteldifferenz
289, SMD 19, g 15), 97 aus Arm-Tabellen (alle g), 2 aus dem Fliesstext. Nicht
poolbar sind OR (393), beta (270), RR (12) und HR (2) - eine Eigenschaft der
Effektart, kein Fehler. Von den 422 sind nur 131 standardisiert (g + SMD);
289 rohe Mitteldifferenzen sind nur innerhalb derselben Skala poolbar.

## 2. Zielmass-Abdeckung

| Klasse | Zeilen | Anteil |
|---|---:|---:|
| **SOL (Einschlaflatenz)** | **13** | **1,2 %** |
| Schlaf, andere Endpunkte | 333 | 30,3 % |
| Andere Endpunkte | 751 | 68,3 % |
| Ohne brauchbares Label | 2 | 0,2 % |
| Summe | 1.099 | |

Quelle: `zielmass_schnitt_label2_20261108.json`. Der Schnitt prueft den
normalisierten Outcome-Namen, nicht den studierten Zusammenhang; Umschreibungen
wie "latency to persistent sleep" landen unter "anderes", der Anteil ist also
eine Untergrenze.

## 3. Was in den 13 SOL-Zeilen steht

- **7 Quellen**, 12 Zeilen poolbar.
- Effektarten: **11 rohe Mitteldifferenzen**, 1 standardisiertes g (0,07,
  `10.1001/jamanetworkopen.2026.26983`), 1 OR (2,56 - als OR nicht poolbar).
- Skalen gemischt: `10.2188/jea.je20140201` meldet "log min" (-0,1; -0,002),
  die uebrigen "min" (-4,2; -5,1; 3,8; 4,6 ...). Ein gemeinsamer Mittelwert
  ueber beide Skalen waere falsch.
- Zwei Quellen liefern 4 bzw. 3 Zeilen (`10.1111/jsr.70311`,
  `10.1093/sleep/zsae250`); bei derselben Studie sind das abhaengige Zeilen.

**Folge:** Es gibt keine Gruppe, in der mehrere unabhaengige Studien dieselbe
Groesse auf derselben Skala berichten. Der Bericht gibt daher keinen gepoolten
Effekt aus, sondern die Zeilen einzeln mit Grund.

## 4. Warum die Ausbeute trotz 576 neuer Zeilen nicht beim Zielmass ankommt

Drei Verbesserungen wurden in diesem Lauf gebaut und **einzeln gemessen**:

| Aenderung | Gewinn bei SOL |
|---|---|
| mehrzeilige Kopfzeilen, colspan/rowspan (`0cfd1cc`) | 0 (Kandidaten 539 -> 1.115, SOL unveraendert) |
| Outcome-Label aus Zwischenueberschrift/Caption (`0e8f3a9`) | 0 (ohne Label 232 -> 2, SOL 13 -> 13) |
| Arm-Rechner paart getrennte Mean-/SD-Spalten (`857b924`) | 0 (lesbar 18 -> 18) |
| Messung des Fliesstext-Lesers (`6514a60`) | 0 (316 SOL-Saetze mit SD, keiner lesbar) |

Die Gruende sind inhaltlich, nicht technisch: die SOL-Tabellenzeilen sind
Erzaehl- und Uebersichtstabellen (327 von 446 in der Stichprobe), Zeitreihen
einer Gruppe (31) oder Textzellen ohne Zellpaar (31). Von 5.820 SOL-Saetzen
enthalten 316 einen Mittelwert mit SD; 139 beschreiben eine Veraenderung
innerhalb einer Gruppe, 82 sind Tabellenreste, 42 geben SEM statt SD, 20 haben
nicht zwei Mittelwerte, 18 einen Median mit IQR, 13 keine Fallzahl je Arm.

**Der Korpus enthaelt keine SOL-Stelle, aus der ein bestehender Leser ohne
Umdeutung ein Zwei-Arm-Paar gewinnen kann.** Das ist ein Befund ueber den
Korpus, nicht ueber die Leser.

## 5. Was daraus folgt

1. **Kein gepoolter SOL-Effekt in diesem Lauf.** Die ehrliche Aussage ist:
   von 1.056 gelesenen Volltexten betrifft 1,2 % der gespeicherten Zeilen das
   Zielmass, und diese 13 Zeilen sind nicht poolbar, weil Skala, Effektart und
   Abhaengigkeit es nicht zulassen.
2. **Weitere Leser-Fixes an diesem Korpus bringen nichts.** Drei Versuche mit
   messbarer Wirkung auf die Gesamtausbeute (+576 Zeilen) hatten bei SOL
   null Wirkung. Ein vierter haette keine Grundlage.
3. **Ein neuer Netzlauf braucht eine andere Suchhypothese**, nicht mehr
   Dokumente: gesucht werden Studien, die SOL als Zwei-Arm-Deskriptivum
   berichten (Mittelwert/SD je Arm, oder fertige Effektspalte), nicht Studien,
   die SOL erwaehnen. Vor jedem Lauf: Telemetrie des letzten Laufs, Freigabe,
   maximal 2-3 Laeufe.
4. **Die Ausbeute-Arbeit ist trotzdem nicht verloren.** Der Funnel, die
   Kopfzeilen-Aufloesung, die Label-Ableitung und die Arm-Paarung sind
   allgemein wirksam (1.099 statt 523 gespeicherte Zeilen, 422 statt 152
   poolbare Zeilen) - nur nicht fuer diese eine Frage.

## 6. Grenzen dieses Berichts

- Die Zielmass-Klassifikation ist eine Namenspruefung; Population und
  Intervention werden nicht geprueft. Eine SOL-Zeile kann eine andere
  Intervention betreffen.
- Die Grundverteilung der Ablehnungsgruende stammt aus einer Stichprobe von
  260 der 946 Kandidaten; die Lesbarkeitszahlen (18, 0) sind ueber alle 946
  gerechnet.
- Die Mess-DBs (`direct_label2.db`, `arm_label2.db`) sind lokal und nicht
  versioniert; die Zahlen sind ueber die Konverterbefehle reproduzierbar, die
  in `konverter_kopf_20261108.md` stehen.
- 3 XML fehlen weiterhin (HTTP 500 bei der Beschaffung).

## 7. Nachweise

| Datei | Inhalt |
|---|---|
| `funnel_20261108.json/.md` | neun Stufen, Verlust-Rangliste, Gates je Leser |
| `konverter_kopf_20261108.md` | Konverterlauf vor der Label-Reparatur |
| `effect_columns_kopf_20261108.json`, `arm_level_kopf_20261108.json` | 1.000 + 97 gespeichert, 6 Verwuerfe |
| `label_fix_20261108.md`, `zielmass_schnitt_label2_20261108.json` | Label-Reparatur, 13 SOL-Zeilen |
| `sol_profil_befund_20261108.md` | 1.367 SOL-Zeilen, 18 lesbar |
| `arm_paare_befund_20261108.md` | Spaltenpaarung, 18 -> 18 |
| `sol_text_20261108.json/.md` | 5.820 SOL-Saetze, 316 mit SD, 0 lesbar |
