# Suchhypothese: SOL als Zwei-Arm-Deskriptivum (2026-11-08)

Dieses Dokument ist der Entwurf fuer **einen** moeglichen Netzlauf. Es wird
nichts gestartet: kein Lauf ohne ausdrueckliche Freigabe, hoechstens 2-3 Laeufe
pro Frage.

## 1. Befund, aus dem die Hypothese folgt

Aus dem Lauf 2026-11-08 (alles offline gemessen):

| Kennzahl | Wert |
|---|---:|
| Dokumente im Korpus (SOL-RCT-Muster) | 946 |
| SOL-Tabellenzeilen | 1.367 |
| davon von einem Leser gelesen | 18 |
| gespeicherte SOL-Zeilen | 13 aus 7 Quellen |
| SOL-Saetze mit Mittelwert +- SD | 316 |
| davon als Zwei-Arm-Paar gelesen | 0 |
| Zielmass-Abdeckung | 1,2 % |

Die bisherige Suche (`scripts/sol_corpus_search.py`) fragt Europe PMC nach
`melatonin AND "sleep onset latency" AND (randomized OR randomised)` - also
Volltext-Treffer irgendwo im Dokument. Genau dort liegt das Problem: 45 % der
Nichttreffer enthalten SOL **irgendwo** in einer Tabelle, aber nur 7 Dokumente
berichten SOL als auswertbares Zwei-Arm-Ergebnis.

## 2. Hypothese

**H:** Dokumente, deren **Abstract** SOL als berichtetes Ergebnis nennt
(zusammen mit einer Effekt- oder Mittelwertangabe), liefern deutlich haeufiger
eine lesbare SOL-Zeile als Dokumente, die SOL nur im Volltext erwaehnen.

Falsifizierbar, weil vorab beziffert:

- Basisrate heute: 7 von 946 Dokumenten mit lesbarer SOL-Zeile = **0,7 %**.
- Vorhersage: in einer Stichprobe von 40 Dokumenten aus der Abstract-Suche
  finden sich **mindestens 4** mit lesbarer SOL-Zeile (>= 10 %, also
  mindestens Faktor 14 ueber der Basisrate).
- Widerlegt ist H, wenn nach 40 geprueften Dokumenten **hoechstens 1** eine
  lesbare SOL-Zeile hat.

## 3. Suchbegriffe (Europe PMC, ein Lauf, drei Abfragen)

Reihenfolge nach erwarteter Praezision, jede Abfrage mit `HAS_FULLTEXT:y`
(sonst ist kein XML beschaffbar). Die Feldnamen `TITLE` und `HAS_FULLTEXT`
sind im Projekt bereits belegt (`scripts/seed_local_corpus.py`); `ABSTRACT`
ist zu **verifizieren**, bevor die Abfrage zaehlt (Schritt 1 unten).

**Q1 - Abstract nennt SOL und ein Design:**
```
(TITLE:"melatonin" OR ABSTRACT:"melatonin")
AND (ABSTRACT:"sleep onset latency" OR ABSTRACT:"sleep latency" OR ABSTRACT:"SOL")
AND (ABSTRACT:randomized OR ABSTRACT:randomised OR ABSTRACT:placebo
     OR ABSTRACT:"double-blind" OR ABSTRACT:crossover)
AND HAS_FULLTEXT:y
```

**Q2 - Abstract nennt zusaetzlich eine Ergebnisform:**
```
Q1 AND (ABSTRACT:"mean difference" OR ABSTRACT:"effect size"
        OR ABSTRACT:Hedges OR ABSTRACT:"95% CI" OR ABSTRACT:"standard deviation")
```

**Q3 - Titel nennt SOL und Melatonin (hohe Praezision, kleine Menge):**
```
TITLE:"sleep onset latency" AND TITLE:melatonin AND HAS_FULLTEXT:y
```

Crossref-Gegenprobe (eine Abfrage, keine Boolesche Syntax):
`melatonin sleep onset latency randomized placebo mean difference` - dient nur
der Vollstaendigkeitspruefung, nicht der Auswahl.

## 4. Vorgehen (ein Lauf, fuenf Schritte)

1. **Syntax-Probe (1 Request je Abfrage):** Trefferzahl und Feldnamen pruefen.
   Liefert `ABSTRACT:` einen Syntaxfehler, wird auf `TITLE:`/Volltext
   zurueckgefallen und das im Protokoll vermerkt.
2. **Auswahl:** je Abfrage die ersten 100 Treffer, Dubletten gegen den
   bestehenden Korpus (1.056 PMCID) entfernen. Erwartet: 150-250 neue
   Dokumente.
3. **Beschaffung:** XML nur fuer Treffer mit PMCID; Fehlschlaege zaehlen und
   nennen (wie beim letzten Mal: 3 von 1.059).
4. **Lesen:** dieselben Leser wie heute (Effektspalten, Arm, Fliesstext,
   Veraenderung) plus Funnel und Zielmass-Schnitt. Kein Modell, keine
   Extraktion.
5. **Entscheiden** anhand der Kriterien in Abschnitt 6.

## 5. Aufwand

| Posten | Schaetzung |
|---|---|
| Requests | 3 Syntax-Proben + 3 Suchseiten + 150-250 XML-Downloads |
| Laufzeit Beschaffung | 30-50 min (bei ~2 s je Dokument) |
| Laufzeit Auswertung | 10-15 min (Funnel + Konverter + Schnitt, offline) |
| Guthaben | keine Modellkosten; nur API-Zeit |
| Sitzungen | 1 |

## 6. Abbruchkriterien (vorab festgelegt, hart)

- **A1 - Praezision:** Nach 40 beschafften Dokumenten aus Q1 wird gelesen.
  Weniger als 2 mit lesbarer SOL-Zeile -> Q1 abbrechen, nicht weiter
  herunterladen.
- **A2 - Zugang:** Fehlt bei mehr als 30 % der Treffer ein PMCID, wird die
  Abfrage auf `HAS_FULLTEXT:y` verengt; bleibt es ueber 30 %, wird der Lauf
  beendet (Bezahlschranke, kein Umweg ueber andere Quellen).
- **A3 - Ertrag:** Nach allen drei Abfragen weniger als **3 neue unabhaengige
  Quellen** mit lesbarer SOL-Zeile -> kein zweiter Lauf, Bericht bleibt bei
  k = 1 und 1,2 %.
- **A4 - Kosten:** kein zweiter Lauf ohne Telemetrie-Auswertung des ersten und
  ohne neue Freigabe; maximal 2 Laeufe fuer diese Frage.

## 7. Erfolgskriterium (was ein Ergebnis waere)

Ein Lauf gilt als erfolgreich, wenn mindestens eines zutrifft:

- **Kombinierbar:** >= 2 unabhaengige Studien berichten SOL als
  Mitteldifferenz in **derselben** Einheit (min, nicht log-min), dann ist
  k = 2 mit mean_diff moeglich.
- **Standardisiert:** >= 3 unabhaengige Studien liefern g oder SMD.

Alles darunter ist eine Erweiterung der Einzeldarstellung, kein Pool - und
wird auch so berichtet.

## 8. Was nicht wiederholt wird

- Keine weiteren Leser-Fixes an diesem Korpus: vier Verbesserungen (Kopfzeilen,
  Labels, Arm-Paare, Fliesstext) hatten bei SOL null Wirkung, bei +576
  gespeicherten Zeilen insgesamt.
- Keine breitere Volltextsuche ohne Abstract-Bedingung: sie hat 946 Dokumente
  fuer 13 Zeilen geliefert.
- Keine Rueckrechnung von Median/IQR oder SEM in SD, kein Ergaenzen fehlender
  Fallzahlen.

## 9. Grenzen und Risiken

- Die Abstract-Bedingung ist eine Annahme ueber Berichtsgewohnheiten, keine
  Messung. Genau deshalb die bezifferte Vorhersage und der fruehe Abbruch nach
  40 Dokumenten.
- Europe PMC deckt nicht alle Schlafzeitschriften vollstaendig; `HAS_FULLTEXT:y`
  schliesst bezahlte Volltexte aus, auch wenn sie SOL-Zwei-Arm-Daten enthalten.
- Die 7 bisherigen Quellen bleiben im Korpus; neue Treffer werden gegen sie
  dedupliziert, damit keine Studie doppelt zaehlt.
- Ein erfolgreicher Lauf liefert hoechstens einzelne Studien; die Aussagekraft
  bleibt durch Studiendesign und Risiko fuer Verzerrung begrenzt, nicht durch
  die Zahl der Zeilen.

## 10. Freigabe

Der Lauf startet erst nach ausdruecklicher Freigabe. Die Telemetrie des letzten
Netzlaufs ist ausgewertet: `data/bench/sol/telemetrie_befund_20261108.md`.
Ergebnis fuer diesen Entwurf: Europe PMC und Crossref hatten im letzten Lauf
kein einziges 429, waehrend OpenAlex (94 Circuit-Breaks), Semantic Scholar (82)
und PubMed (ESearch/ESummary 429) den Lauf in den Backoff trieben. Deshalb
bleiben Q1-Q3 auf Europe PMC, Crossref dient nur der Gegenprobe, und PubMed,
OpenAlex und Semantic Scholar werden nicht angefragt. Die Suche kostete zuletzt
566 Tokens je Aufruf - die drei Abfragen sind kostenmaessig unerheblich.
