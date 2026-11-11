# Experiment C: geplant, nicht gestartet

Dieses Verzeichnis enthält noch keine Modellausgaben. Es dokumentiert nur die
Auswertungsstruktur. Ein Lauf benötigt eine ausdrückliche Freigabe.

## Daten

- Primär: Yun et al. 2024, 120 RCT-Auszüge, 699 ICO-Records.
- Referenz: `processed_data/yun_ico_records.jsonl`.
- Entwicklungsanteil: 43 Records aus 10 Artikeln (`split=dev`).
- Testanteil: 656 Records aus 110 Artikeln (`split=test`).
- Numerisch streng vollständig: 410 Records (261 kontinuierlich, 149 binär).
- Auditstand: Alle 410 streng vollständigen Records wurden geprüft. 275 sind
  für C1 nutzbar, 57 strukturell ausgeschlossen und 78 nicht ausreichend
  belegt (`../validation/yun_audit_410.md`).

Die Referenzannotation wird bis zum Abschluss der Extraktion zurückgehalten.
`is_data_complete` wird nicht als verlässliches Einschlusskriterium
übernommen.
Der Testanteil darf **nicht** zur Prompt- oder Pipeline-Optimierung verwendet
werden. Anpassungen sind ausschließlich auf `dev` zulässig.

## Auswertungseinheit

Ein Record ist ein ICO-Tripel. Für den Vergleich werden Study ID,
Intervention, Comparator und Outcome normalisiert, aber die Rohschreibweise
bleibt erhalten. Zusammengefasste oder aufgeteilte Outcomes aus Yun werden
nicht nachträglich zusammengeführt.

## Metriken

### Effektzeilen

- Precision, Recall und F1 auf ICO-Ebene.
- Getrennte Zählung von: richtiges ICO, falsches ICO, fehlende Zeile,
  zusätzliche Zeile.
- Nicht extrahierbare Referenzwerte (`null`) werden als eigene Kategorie
  ausgewiesen und nicht als falsch extrahiert gezählt.

### Numerische Felder

Für N, Mean, SD und Ereigniszahlen:

- exakte Übereinstimmung (gefordert),
- absolute Differenz und mittlerer absoluter Fehler,
- relatives Vorzeichen/Verhältnis nur ergänzend,
- getrennte Auswertung für intervention und comparator,
- getrennte Auswertung für kontinuierlich und binär.

### Kategoriale Felder

- Outcome-Typ: Accuracy, Precision/Recall/F1, Cohen's Kappa nur als
  ergänzendes Maß.
- Zeitpunkt: nur auswertbar, wenn eine eindeutige Kategorie definiert ist;
  Yun liefert kein separates Zeitpunktfeld. Fehlende Zeitpunkte werden
  ausgewiesen, nicht geschätzt.
- Cohen's Kappa ist **kein** Ersatz für numerische Fehlermaße. Für
  N/Mean/SD sind exakte Treffer und absolute Fehler maßgeblich.

### Fehlerklassen

- Wert nicht im Text vorhanden,
- Wert aus falschem Arm,
- Wert aus falschem Zeitpunkt,
- falsches Outcome,
- Zahlendreher oder Einheitenfehler,
- Modell halluziniert einen Wert,
- Referenz selbst fehlerhaft (nur nach manueller Prüfung).

## Mindestbericht

- Anzahl ausgewerteter Records insgesamt und je Split.
- Abdeckung: wie viele Referenzwerte überhaupt vorhanden sind.
- Precision/Recall/F1 je Feld.
- Exakte Trefferquote und MAE je Feld.
- Confusion Matrix für Outcome-Typ.
- Liste der Fehler mit Record-ID und Quelle.
- Explizite Trennung von Modellfehler und Referenzfehler.

## Noch nicht enthalten

- Keine Baseline, kein Prompt, kein Modellaufruf.
- Keine Anpassung an Testdaten.
- Keine Aussage über die Leistungsfähigkeit des Research Agents, solange
  kein freigegebener Lauf vorliegt.
