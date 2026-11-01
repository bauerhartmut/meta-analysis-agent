# Protokoll — Bewegung und depressive Symptome bei Erwachsenen

Eingefroren am 2026-10-29, vor der ersten Suche. Dieses Dokument legt fest, welche
Studien aufgenommen und welche Zahlen gepoolt werden. Es wird nicht
überschrieben: ein Protokoll, das sich nach den Ergebnissen ändert, wäre keine
Vorabfestlegung.

## Frage (PICO)

- **Population:** Erwachsene ab 18 Jahren mit depressiven Symptomen (oberhalb des
  Cut-offs einer validierten Skala) oder mit diagnostizierter depressiver Störung.
  Postpartale Depression ist ausgeschlossen.
- **Intervention/Exposition:** strukturiertes, geplantes körperliches Training
  (aerob, Kraft- oder kombiniertes Training) mit angeleiteten Einheiten,
  definierter Häufigkeit und Dauer. Sport als Zusatz zur üblichen Versorgung
  zählt, wenn die Kontrollgruppe dieselbe Versorgung ohne Sport erhält.
- **Comparison:** keine Behandlung, Warteliste, übliche Versorgung oder
  Aufmerksamkeits-/Placebokontrolle. Primärer Kontrast ist Sport gegen eine
  inaktive Kontrolle; aktive Vergleiche (Psychotherapie, Medikament) werden
  getrennt berichtet und nicht mit dem primären Pool vermischt.
- **Outcome:** Schwere der depressiven Symptome am Ende der Intervention, gemessen
  mit einer validierten Selbst- oder Fremdbeurteilungsskala (BDI, BDI-II, PHQ-9,
  CES-D, HAM-D/HDRS, MADRS, SCL-20, IDS, DASS-Depression).

## Einschlusskriterien

- randomisierte kontrollierte Studie (individuell oder Cluster-randomisiert)
- Erwachsene ab 18 Jahren (Mittelwert oder Einschlusskriterium der Studie)
- depressive Symptomatik ist Einschlusskriterium oder wird als Outcome gemessen
- eine Effektgröße ist berichtbar: Mittelwerte und Standardabweichungen je Gruppe,
  Mittelwertdifferenz mit Konfidenzintervall, SMD/Hedges' g mit
  Konfidenzintervall, oder t-/p-Wert zusammen mit den Stichprobengrößen
- Interventionsdauer mindestens vier Wochen; kürzere Studien laufen nur in der
  Sensitivitätsanalyse mit

## Ausschlusskriterien

- postpartale Depression oder Schwangerschaft als Zielpopulation
- nicht randomisierte Designs, Einzelfallberichte, kontrollierte Studien ohne
  Randomisierung
- Sport nur als Ko-Intervention ohne eigenen Arm, oder Sport in beiden Armen
- keine Zahl zur Depressivität (nur „signifikant besser", nur p-Wert ohne n)
- Reviews, Protokolle, Kommentare, Leitlinien, Tierstudien
- doppelte Publikation derselben Kohorte: je Outcome zählt die präzisere Lesung
  einmal (Abgleich über DOI und Stichprobe)

## Primäres Outcome

Schwere depressiver Symptome am Interventionsende, gepoolt als standardisierte
Mittelwertdifferenz (Hedges' g, `smd`), negatives Vorzeichen = weniger depressive
Symptome. Höhere Skalenwerte bedeuten mehr Symptome; läuft eine Skala in die
Gegenrichtung, wird das Vorzeichen vor dem Pooling gedreht.

Sekundär und nicht mit dem primären Pool vermischt: aktive Vergleiche (Sport gegen
Psychotherapie oder Medikament), Nachbeobachtung nach Interventionsende,
Abbruchquoten.

## Geplante Zählungen

Berichtet werden, jeweils mit Ausschlussgrund in der Tabelle `screening`:
gefundene Quellen, bewertete Quellen, ausgeschlossene Quellen, eingeschlossene
Studien, Studien mit nutzbarer Effektzeile, poolbare Zeilen (nicht `disputed`,
nicht verworfen, mit `se` oder Konfidenzintervall), strittige Zeilen aus der
Doppel-Extraktion, vom Plausibilitätsgate verworfene Zeilen, und gelesene Zeilen,
die nicht im Zielmaß liegen.

## Externer Referenzwert

Kein Bestandteil der Auswahl, nur eine Plausibilitätsmarke für das Ergebnis: die
Cochrane-Übersicht von 2026 (CD004366, PubMed 41500513) findet für Sport gegen
inaktive Kontrolle 57 RCTs mit SMD −0,67 (95 %-KI −0,82 bis −0,52); in der
Teilmenge mit adäquater Verdeckung, Intention-to-treat und verblindeter Messung
−0,46 (−0,88 bis −0,04). Weicht der gepoolte Schätzer stark nach oben ab, ist die
naheliegendste Erklärung eine selektive OA-Stichprobe kleiner positiver Studien —
nicht ein größerer wahrer Effekt.

## Grenzen, die auch nach diesem Lauf gelten

Kein Risk-of-Bias-Instrument (RoB 2, ROBINS-I), keine GRADE-Bewertung, keine
Registrierung, keine menschliche Doppelcodierung: das Ergebnis ist eine quantitative
Synthese, keine systematische Übersichtsarbeit. Der Korpus ist OA-lastig, und im
Abstract fehlt häufig der Standardfehler; was fehlt, wird als fehlend berichtet
statt geschätzt.
