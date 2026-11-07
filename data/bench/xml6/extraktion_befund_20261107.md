# Was aus den sechs XML-Dokumenten wirklich herauskommt

Stand: 07.11.2026. Kette wie im Orchestrator: `_xml_to_text` →
`save_source_text` → `blocks_from_jats` + `augment_document_text` →
`EffectExtractor` mit zwei unabhaengigen Lesungen. Kein Netzlauf, nur die
sechs Europe-PMC-XML unter `data/bench/xml6/`.

## Ergebnis in einer Zeile

Von 68 stat-reichen Tabellenzeilen bleiben nach der echten Extraktion
**14 Effektzeilen, davon 1 poolbar** (SE/CI vorhanden, nicht strittig,
Zitat per `locate_quote` belegt).

## Zahlen

| Kennzahl | Wert |
|---|---:|
| Dokumente | 6 |
| JATS-Tabellen | 21 |
| Tabellenzeilen gesamt | 354 |
| davon stat-reich (SE/CI/SD+N) | 68 |
| davon mit Effektmetrik in der Zeile | 7 |
| extrahierte Effektzeilen | 14 |
| davon mit SE | 5 |
| davon mit CI | 3 |
| strittig (disputed) | 4 |
| abgelehnt ("kein Effektwert gelesen") | 9 |
| Zitat nicht auffindbar | **0** |
| **poolbar** | **1** |

Je Dokument: `10.1001/jamanetworkopen.2026.26983` 3 Zeilen / 1 poolbar,
`10.3389/fnut.2026.1890075` 2 / 0, `10.3390/healthcare13020180` 2 / 0,
`10.3390/ijms27146320` 2 / 0, `10.3390/medicina62040662` 2 / 0,
`10.5888/pcd20.230198` 3 / 0.

Die eine poolbare Zeile: Sleep onset latency, Hedges g = 0.07,
SE = 0.0536, 95 % CI -0.04 bis 0.17 (jamanetworkopen).

## Warum so wenig — die Diagnose

1. **Die 68 Zeilen sind ueberwiegend Gruppen-Mittelwerte, keine
   Effektschätzer.** Beispiele aus den JATS-Zellen: `['% Stage REM
   (primary)', '342', '16.7 (11.6 to 22.0)', '19.0 (14.6 to 23.2)']`,
   `['Melatonin (pg/mL)', '15.6 ± 16.0', '8.6 ± 11.3', '19.1 ± 19.4']`.
   Das sind Arm-Deskriptiva. Der Extraktor darf per Vertrag nicht rechnen
   ("Never estimate, never compute"), also bleibt `effect` leer und die
   Zeile wird mit "kein Effektwert gelesen" abgelehnt - korrekt, aber
   unproduktiv. Nur 7 Zeilen tragen einen Effektbegriff in der Zeile
   selbst; bei `pcd20.230198` steht das OR nur im Spaltenkopf, die Zellen
   tragen `2.78 (1.80-4.30)`.
2. **Die Verfuegbarkeitsmessung ueberschaetzt den Ertrag um Faktor 7-14.**
   `check_xml_availability.py` zaehlt Zeilen mit SE/CI-Flags; daraus
   folgen noch keine poolbaren Effekte. Die 6 Dokumente lieferten im Lauf
   zusammen 3 SE/2 CI - hier ist es 1 poolbare Zeile statt 35 SE- und
   58 CI-Zeilen als Kandidaten.
3. **Doppelte Zeilen:** Der jamanetworkopen-Effekt steht dreimal im Store
   (Pass A, Pass B, dritte Lesung), zwei Kopien als strittig markiert.
   Die Zeilenzahl 14 ist also nach oben verzerrt; real sind es ~8
   verschiedene Aussagen.
4. **Die Renderer-Treue haelt:** 0 von 14 Zitaten waren im gespeicherten
   Text nicht auffindbar. Die Pipe-Zeilen aus dem XML sind also zitierbar,
   das Problem ist nicht die Wiedergabe, sondern der Inhalt der Tabellen.

## Grenzen

- Sechs Dokumente, ein Lauf, kein `targets`-Block (im echten Lauf wuerde
  der Aim die Outcome-Namen vorgeben) und Themenpassung nur teilweise:
  `ijms27146320` und `medicina62040662` sind keine Melatonin-Schlaf-Studien
  im engeren Sinn. Die 1 poolbare Zeile ist damit eine Untergrenze fuer
  diese Auswahl, keine Schaetzung fuer den ganzen Korpus.
- "Kein Effektwert gelesen" ist eine Extraktionsentscheidung, keine
  Gewissheit: ob ein Modell mit anderem Prompt die Arm-Mittelwerte in
  eine SMD umrechnen duerfte, ist eine Designfrage (es duerfte es rechnen,
  wenn die Rohwerte da sind - der Prompt verbietet es bewusst).
- Nicht gemessen: ob `pooling.py` die eine Zeile in eine Analyse
  aufnimmt (dafuer fehlt eine zweite Studie zum selben Outcome).

## Konsequenz fuer die Pipeline

Der Engpass ist nicht die Beschaffung, sondern die **Umrechnung von
Arm-Deskriptiva in Effektschätzer**. Solange der Extraktor nur abliest, was
als Effekt dasteht, bringt jedes zusaetzliche XML-Dokument wenig. Zwei
Auswege: (a) ein eigener, regelbasierter Rechner fuer Mittelwert/SD/n pro
Arm (deterministisch, nachpruefbar, kein LLM) oder (b) ein Extraktionsfeld
"arm_level" mit anschliessender SMD-Berechnung. Beides ist ein neuer
Schritt, keine Reparatur des bestehenden Pfads.
