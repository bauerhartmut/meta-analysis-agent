# Protokoll: Digitale CBT-I bei jungen Menschen

## Aufgabe

Extrahiere aus den vier unten genannten randomisierten kontrollierten
Studien die subjektive Schlafqualität nach der Behandlung (post-treatment)
und berechne daraus einen gepoolten standardisierten
Mittelwertdifferenz-Effekt.

## PICO

- Population: Jugendliche und junge Erwachsene (überwiegend Studierende)
  mit Insomnie, erhöhten Insomniewerten oder Schlafproblemen.
- Intervention: digital gelieferte CBT-I (web- oder appbasiert).
- Kontrolle: Warteliste, übliche Versorgung oder ein aktives
  Schlafhygiene-/Gesundheitsprogramm.
- Outcome: subjektive Schlafqualität am Ende der Behandlung
  (post-treatment, nicht Follow-up).
- Design: randomisierte kontrollierte Studien.

## Einzuschließende Studien

Genau diese vier Studien; keine weiteren ergänzen:

1. Morris 2015, DOI `10.1080/10615806.2015.1058924`
2. Freeman 2017, DOI `10.1016/S2215-0366(17)30328-0`
3. Fucito 2017, DOI `10.1111/acer.13342`
4. de Bruin 2018, DOI `10.1111/jcpp.12834`

## Extraktion

Pro Studie:

- Behandlungsgruppe: n, Mittelwert, SD des Schlafscores post-treatment.
- Kontrollgruppe: n, Mittelwert, SD des Schlafscores post-treatment.
- Verwendetes Instrument und exakter Zeitpunkt.
- Exakte Textstelle mit Seite und Tabelle als Beleg.

Instrumente und Zeitpunkte:

- Morris 2015: PSQI, sechs Wochen nach Beginn.
- Freeman 2017: ISI, Woche 10.
- Fucito 2017: PSQI, Woche 5.
- de Bruin 2018: HSDQi, direkt nach der Behandlung.

Regeln für die Armwerte:

- Die randomisierten N je Arm verwenden; Completer-N separat notieren.
  Wenn die berichteten Post-Treatment-Werte nur auf Completern beruhen,
  das im Ergebnis kennzeichnen.
- Fucito berichtet den PSQI als modellgeschätzten Mittelwert mit
  Standardfehler. Die SD aus Standardfehler und Arm-N herleiten
  (`SD = SE * sqrt(n)`) und die Herleitung dokumentieren.
- Bei de Bruin den Internet-CBT-I-Arm (IT) gegen die Warteliste (WL)
  verwenden, nicht den Gruppen-CBT-I-Arm (GT).

Berechne daraus die SMD (Hedges-g-Korrektur) mit negativem Vorzeichen,
wenn die Intervention den Score senkt. Pool mit einem Random-Effects-Modell
(DerSimonian-Laird). Berichte k, SMD, 95-%-KI, Q, I² und tau².

## Ausgabe

Ein JSON mit:

- `studies`: je Studie ID, n, Mittelwerte, SDs, Instrument, Zeitpunkt,
  SMD, 95-%-KI und Quelle.
- `pooled`: SMD, 95-%-KI, k, Q, I², tau², Modell.
- `notes`: Auffälligkeiten, insbesondere abweichende N, unklare Zeitpunkte
  oder unvollständige SDs.

## Grenzen

Nur die vier Volltexte und dieses Protokoll verwenden. Keine Metaanalyse,
keine Forest Plots, keine gepoolten Ergebnisse, keine Datenbankwerte und
keine A-Dateien als Quelle nutzen.
