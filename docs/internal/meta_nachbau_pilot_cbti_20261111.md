# Pilot: Nachbau einer CBT-I-Metaanalyse (2026-11-11)

## Zweck

Externer Reproduktionstest für Extraktion und Pooling, unabhängig von der
menschlichen B-Annotation. Die Pipeline sieht ausschließlich die
Primärstudien und das Protokoll; die Metaanalyse selbst, ihre Tabellen,
Forest Plots und der Antwortschlüssel bleiben verdeckt.

## Fall

- Quelle: Mei Z, Cai C, Luo S, Zhang Y, Lam C, Luo S. *The efficacy of
  cognitive behavioral therapy for insomnia in adolescents: a systematic
  review and meta-analysis of randomized controlled trials.* Frontiers in
  Public Health, 2024. DOI `10.3389/fpubh.2024.1413694`, PMC `PMC11613502`.
- Lokaler Volltext:
  `data/bench/sol/fulltext/ceab2005d69c001877e3752b992e3cb8.txt`
- Zieloutcome: Insomnie-Schweregrad, **post-treatment** (nicht Follow-up).
- Effektmaß: standardisierte Mittelwertdifferenz (SMD), negative Werte
  bedeuten einen Vorteil für CBT-I.
- Modell: Random-Effects, DerSimonian-Laird.
- Publiziertes Ergebnis: **SMD = -1.06, 95-%-KI -1.65 bis -0.47**,
  k = 6, I² = 87.18 %, tau² = 0.45, Q = 39.01.

## Rechnerische Prüfung

Aus den sechs im Forest Plot berichteten SMDs und ihren KIs ergibt sich:

- SMD = **-1.0635** [-1.6567; -0.4704]
- Q = 39.3577, df = 5
- tau² = 0.449820
- I² = 87.30 %

Das ist praktisch identisch mit dem publizierten Wert; die kleinen
Abweichungen stammen aus der Rundung der berichteten Werte.

Zusätzlich aus den Mittelwerten und SDs mit Hedges-g-Korrektur:

- SMD = **-1.0404** [-1.6221; -0.4587]
- Q = 37.7638, tau² = 0.4300, I² = 86.76 %

Damit ist der Fall als sauberer Pilot geeignet. Der publizierte Pool ist
aus den Studienwerten reproduzierbar.

## Sechs Studien im primären Insomnie-Pool

1. Chan 2022 — DOI `10.1016/j.jadohealth.2021.11.005`
2. Chan 2021 — DOI `10.1542/peds.2020-006833`
3. de Bruin 2018 — DOI `10.1111/jcpp.12834`
4. de Bruin 2015 — DOI `10.1016/j.sleep.2014.12.009`
5. Egbegi 2021 — DOI `10.1186/s13034-021-00406-1`
6. Tomfohr-Madsen 2020 — DOI `10.1097/htr.0000000000000504`

Clarke 2015 und Goodhines 2022 sind in der Gesamtstudie enthalten, gehören
aber nicht zum post-treatment Insomnie-Pool. Sie dürfen nicht ergänzt
werden.

## Pipeline-Eingabe

Die Pipeline erhält nur:

- `data/meta_nachbau/pilot_cbti/protokoll.md`
- die sechs Primärstudien-Volltexte in
  `data/meta_nachbau/pilot_cbti/volltexte/`

Nicht erlaubt:

- der Metaanalyse-Artikel oder seine Supplemente,
- Forest Plots, Tabellen oder gepoolte Ergebnisse,
- `antwortschluessel.json`,
- A-Dateien oder andere Goldstandard-Dateien.

## Antwortschlüssel

`data/meta_nachbau/pilot_cbti/antwortschluessel.json` enthält Study-Level-
Werte, publizierten Pool und die Nachrechnung. Er wird nicht an die
Pipeline übergeben.

## Bewertung

- k = 6 exakt.
- Study-Level: Mittelwerte, SDs und N müssen aus den Primärtexten
  extrahierbar sein; SMD-Toleranz ±0,10 gegenüber dem berichteten Wert.
- Gepoolter SMD: Toleranz ±0,05 gegenüber -1.06; KI-Toleranz ±0,05.
- I²: Toleranz ±1 Prozentpunkt; tau²: ±0,02.
- Richtung: negativ bedeutet Vorteil für CBT-I; positive oder gedrehte
  Werte sind ein kritischer Fehler.
- Keine Studien ergänzen oder entfernen.

## Aktueller Stand

Die sechs Primärtexte sind lokal **nicht** vorhanden. Sie müssen in
`data/meta_nachbau/pilot_cbti/volltexte/` abgelegt werden. Danach wird
zuerst die Extraktion geprüft, dann der Pool gerechnet. Es wurde noch kein
Modell- oder Netz-Lauf für die Pipeline gestartet.

## Verworfener Kandidat

`203c` (Mediterranean Diet und Krebsrezidiv) wurde verworfen: Der
publizierte Pool 0.83 [0.70; 0.99] mit I² 49,3 % ist aus den sechs
Tabellenwerten nicht reproduzierbar; die Rechnung ergibt 0.828 [0.761;
0.900] mit I² 0 %. Zusätzlich spricht die Tabelle bei Kenfield und Van
Blarigan für dieselbe HPFS-Kohorte (je 4577), und McCullough ist im Zitat
eine Brustkrebs-Arbeit, in der Tabelle aber als kolorektal geführt.Der Fall bleibt als Auditfall dokumentiert, nicht als sauberer Pilot.

## Zugangsstatus (2026-11-11)

Der CBT-I-Pilot ist **blockiert**: Nur Egbegi 2021 hat einen freien
PMC-PDF-Zugang. Chan 2021 und de Bruin 2018 haben freie PDFs auf
Verlags-/Repositoriumsseiten, aber nicht in PMC. Für Chan 2022,
de Bruin 2015 und Tomfohr-Madsen 2020 wurde kein gesicherter freier
PDF-Zugang gefunden. Details:
`docs/internal/meta_nachbau_zugang_20261111.md`.
