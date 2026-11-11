# Protokoll: CBT-I bei Insomnie im Jugendalter

## Aufgabe

Extrahiere aus den sechs unten genannten randomisierten kontrollierten
Studien die Wirksamkeit von CBT-I auf den Insomnie-Schweregrad
(post-treatment) und berechne daraus einen gepoolten standardisierten
Mittelwertdifferenz-Effekt.

## PICO

- Population: Jugendliche mit Insomnie oder erhöhten Insomniewerten.
- Intervention: CBT-I (Gruppen-, Einzel- oder Online-CBT-I).
- Kontrolle: Warteliste, keine Behandlung oder übliche Versorgung.
- Outcome: Insomnie-Schweregrad am Ende der Behandlung
  (post-treatment, nicht Follow-up).
- Design: randomisierte kontrollierte Studien.

## Einzuschließende Studien

Genau diese sechs Studien; keine weiteren ergänzen:

1. Chan 2022, DOI `10.1016/j.jadohealth.2021.11.005`
2. Chan 2021, DOI `10.1542/peds.2020-006833`
3. de Bruin 2018, DOI `10.1111/jcpp.12834`
4. de Bruin 2015, DOI `10.1016/j.sleep.2014.12.009`
5. Egbegi 2021, DOI `10.1186/s13034-021-00406-1`
6. Tomfohr-Madsen 2020, DOI `10.1097/htr.0000000000000504`

Clarke 2015 und Goodhines 2022 gehören nicht zum primären
post-treatment-Insomnie-Pool und dürfen nicht ergänzt werden.

## Extraktion

Pro Studie:

- Behandlungsgruppe: n, Mittelwert, SD des Insomnie-Scores post-treatment.
- Kontrollgruppe: n, Mittelwert, SD des Insomnie-Scores post-treatment.
- Verwendetes Instrument und Zeitpunkt.
- Exakte Textstelle als Beleg.

Berechne daraus die SMD (Hedges-g-Korrektur) mit negativem Vorzeichen,
wenn CBT-I den Score senkt. Pool mit einem Random-Effects-Modell
(DerSimonian-Laird). Berichte k, SMD, 95-%-KI, Q, I² und tau².

## Ausgabe

Ein JSON mit:

- `studies`: je Studie ID, n, Mittelwerte, SDs, Instrument, Zeitpunkt,
  SMD, 95-%-KI und Quote.
- `pooled`: SMD, 95-%-KI, k, Q, I², tau², Modell.
- `notes`: Auffälligkeiten, insbesondere unklare Zeitpunkte oder
  unvollständige SDs.

## Grenzen

Nur die Volltexte und dieses Protokoll verwenden. Keine Metaanalyse, keine
Forest Plots, keine gepoolten Ergebnisse, keine Datenbankwerte und keine
A-Dateien als Quelle nutzen.
