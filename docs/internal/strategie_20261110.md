# Strategie 2026-11-10 — vom Validieren zum Forschen

Stand nach Commit `4678022` (Arbeitsstand seit `f5eb24b`). Adressat: Projekt-
inhaber und externe Begutachtung. Alle Zahlen stammen aus dem Repository
(`IMPLEMENTATION_LOG.md`, Baseline-Artefakte, Testläufe, eigene Messungen) —
keine Schätzungen ohne Kennzeichnung.

## Kurzfassung

Das Harness ist technisch weit und wissenschaftlich nicht fertig. Die
Statistik-, Berichts- und Laufsteuerung sind produktionsreif; der Engpass ist
die **Effektgrößenextraktion**: 129 Zeilen aus 293 Volltexten, davon 93 im
Zielmaß, am Ende **ein** Pool mit k = 19. Für diesen einen Pool hat der Lauf
17 628 Modellaufrufe und 25,3 Mio Tokens gebraucht.

Die laufende Validierungsreihe ist am Ende ihrer Rendite: Die letzten drei
Audits haben **kein gepooltes Ergebnis geändert**. Der nächste sinnvolle
Schritt ist kein weiteres Audit, sondern ein kleiner, budgetierter
Extraktionslauf mit vorher definiertem Zielwert.

---

## 1. Wo steht das Harness tatsächlich?

### Komponenten

| Komponente | Status | Beleg |
|---|---|---|
| Suche, Screening, Volltextbeschaffung | **produktionsreif** | 440 Quellen, 293 Volltexte (8,9 Mio Zeichen, 1 463 Seiten) in einem Lauf |
| Work-Queue, Resume, Abbruch/Neustart | **produktionsreif** | eigener Lauf über 73 Zyklen / 262 028 s mit Closing-Report nach Stop |
| Statistik (`meta/`) | **produktionsreif, gut validiert** | HKSJ, RVE, Subgruppen, Leave-one-out, Prediction, Egger; 1 353 gesammelte Tests, letzte Vollläufe 1 154–1 184 grün |
| Orchestrator Ende-zu-Ende | **funktioniert, mit Fake-Backend geprüft** | `test_e2e` 2/2 grün, 81 s |
| Bericht | **funktioniert** | zwei erzeugte Berichte (Kognition, `run-2026-10-27.md`), Prüfspur neu |
| Effektgrößenextraktion | **funktioniert, unzureichend validiert — der Engpass** | 129 Zeilen aus 293 Volltexten, 93 im Zielmaß, 50 verworfen, 1 Pool k = 19 |
| Tabellen-Extraktion | **MVP, nicht abgenommen** | Goldset 3 Layouts statt ≥ 30 (Auftrag §4.2) |
| Vision-Fallback | **implementiert, Grenzen dokumentiert** | Doppellesung + Textlayer-Gegenprobe; fehlerkorrelierte Fehllesung offen |

### Die entscheidende Kennzahl

Der Exercise-Baseline-Lauf ergab:

- 17 628 Modellaufrufe, 15 davon fehlgeschlagen, 25,3 Mio Tokens;
- 129 Effektzeilen aus 293 Volltexten, also **0,44 Zeilen pro Volltext**;
- 93 im Zielmaß, 50 am Plausibilitätsgate verworfen, 6 strittig;
- **1 gepoolter Pool mit k = 19**.

Das sind rund **196 000 Tokens pro verwendbarer Effektzeile**. Von den 50
Verwürfen entfallen 37 auf „kein Effektwert gelesen" und 13 auf „unbekannter
Effekttyp '(leer)'". Der Entwicklungsauftrag formuliert dasselbe Problem in §2:
„8 Effektzeilen extrahiert, aber keine einzige konnte für eine Metaanalyse
verwendet werden."

### Was einen vollständigen Durchlauf blockiert

1. **Extraktionsausbeute** — 0,44 poolbare Zeilen pro Volltext sind zu wenig
   für belastbare Pools, insbesondere bei heterogeneity-tragenden Fragen.
2. **Goldstandard** — 3 Layouts statt 30; ohne ihn ist keine
   Genauigkeitsaussage zulässig (Auftrag §13).
3. **Zeilenniveau-Attribution** — Tabellenwerte werden lesbar, aber nicht
   automatisch zu poolbaren Zeilen.
4. **Kosten und Laufzeit** — 73 h und 25 Mio Tokens pro Thema ohne
   Budgetdeckel.
5. **Doppelpass-Abdeckung** — 209 Zweitlesungen auf 7 477 Zeilen (2,8 %). Die
   Prüfschicht ist dünn, nicht defekt.

Für einen autonomen Durchlauf fehlt damit **kein Bauteil**, sondern ein
messbarer Qualitätsnachweis der Extraktion.

---

## 2. Sind die nächsten Audits wirklich noch nötig?

### Die 709 linearen Zeilen ohne KI

**Einschätzung: niedriges Risiko, geschätzt 5–10 % für einen relevanten
Befund.** Begründung aus der eigenen Messung: Die 3 945 linearen Zeilen *mit*
KI stimmen bis auf 2 exakt (Median 0,0 %, zwei Ausreißer > 10 %). Die 709
Zeilen *ohne* KI lassen sich nur auf Plausibilität gegen `n` und Design
prüfen, nicht gegen ein berichtetes Intervall.

**Konsequenz eines auffälligen Befunds:** Einzelfall korrigieren, nicht das
Pooling umbauen. Ein systematischer Fehler wäre nur zu erwarten, wenn die
Extraktion die SE flächendeckend falsch skaliert — das ist bei den linearen
Typen widerlegt.

**Abschluss statt Reihe:** 100 Zufallszeilen plus alle Ausreißer, Kriterium
vorab definiert (SE außerhalb des aus `n` und Design erwartbaren Bereichs).
Wenn unter 2 % auffällig sind, ist der Punkt geschlossen. Aufwand ~1–2 h,
0 Guthaben.

### Weitere blinde Flecken, die schwerer wiegen

- **Extraktionsausbeute** (größter Hebel, siehe oben).
- **13 Zeilen „Effekttyp leer"** in der Baseline: Der Fix existiert, ist auf
  neuen Daten aber nie gemessen worden.
- **`abstract_only`-Quellen**: Der Volltextstatus ist bis heute ein
  `chars > 0`-Proxy (Auftrag §4.1).
- **Vision-Zeilen** ohne dritte Gegenprobe, wenn keine Textebene existiert.
- **Kostenkontrolle**: Ein Lauf kann 73 h laufen, ohne dass ein Budget
  abbricht.

### Wann ist die Unsicherheit vertretbar?

Nicht nach Gefühl, sondern nach einem Kriterium:

> Solange ein offener Befund existiert, der einen gepoolten Wert ändern würde,
> ist die Validierung nicht abgeschlossen. Danach schon.

Für die Datenintegrität ist dieser Punkt nach den letzten drei Audits erreicht
— sie haben null gepoolte Werte geändert. Für die Extraktion ist er es nicht:
Dort ist die Unsicherheit nicht Restrisiko, sondern die zentrale offene Frage.

---

## 3. Plan nach Abschluss der Prüfungen

### Notwendig vor dem ersten vollständigen Durchlauf

1. **Goldstandard-Extraktion**: 30 Dokumente, ≥ 100 annotierte Zellen
   (Auftrag §4.2/§13). Ohne ihn ist keine Genauigkeit behauptbar.
2. **Ausbeute-Zielwert**, z. B. ≥ 1,5 poolbare Zeilen pro Volltext und
   ≥ 60 % im Zielmaß (heute 0,44 und 72 %).
3. **Kosten- und Laufzeitdeckel** pro Lauf: Token-Budget, Call-Deckel,
   Abbruchkriterium.
4. **Abnahmeprotokoll je Kennzahl** mit messbarem Zielwert — so verlangt es
   §13 ausdrücklich.

### Wissenschaftliche Validierung

5. **Kalibrierungslauf** an 10–15 Dokumenten mit echten Calls:
   Precision/Recall der Zeilen gegen Goldstandard, Quote-Treue, Ausbeute.
6. Erst danach ein Themenlauf in voller Länge.

### Optional

7. Vision-Fallback-Ausbau, pypdf-Originalseiten, weitere
   Datenintegritäts-Audits, Dashboard-Komfort.

**Nicht zwingend vor dem ersten Durchlauf:** Tabellen-Extraktion über den
Goldstandard hinaus, eine dritte Vision-Gegenprobe, UI-Arbeit. Das sind
Verbesserungen, keine Blockaden.

---

## 4. Der Weg zum ersten vollständigen Durchlauf

| Schritt | Status |
|---|---|
| 1. Letzte Qualitätskontrollen (709 Zeilen, 2 SMD-Ausreißer) | **offen**, ~1–2 h, 0 Guthaben |
| 2. Freigabe der Komponenten | **teilweise**: Statistik/Report ja, Extraktion nein (Goldstandard fehlt) |
| 3. Literaturbeschaffung und Volltextverarbeitung | **implementiert und erprobt** (293 Volltexte) |
| 4. Extraktion mit echten Modellaufrufen | **implementiert, Ausbeute unzureichend** → Kalibrierung nötig |
| 5. Qualitätskontrolle der Extraktionen | **Gates vorhanden** (Quote, `disputed`, Aggregat, Vision), Doppelpass 2,8 % |
| 6. Statistische Auswertung inkl. abhängiger Effekte | **implementiert und getestet** (RVE, Cluster, Min-SE, Subgruppen) |
| 7. Fertiger Evidenzbericht | **implementiert**, zwei Berichte erzeugt |

Der Weg ist also nicht „erst bauen, dann forschen", sondern: Schritt 1
abschließen, für die Extraktion Schritt 2 nachholen (Goldstandard), dann
Schritt 4 kalibrieren und direkt in einen echten Lauf gehen. Schritt 3, 6 und
7 sind fertig.

---

## 5. Wann wieder Modellaufrufe?

**Jetzt — aber begrenzt und mit Abbruchkriterium.** Kein nächster 73-h-Lauf,
sondern ein **Kalibrierungslauf**: ein Thema, 10–15 bereits vorhandene
Volltexte, Budget etwa 200–400 Calls. Ziel ist nicht ein Bericht, sondern drei
Zahlen:

1. poolbare Zeilen pro Volltext,
2. Anteil im Zielmaß,
3. Quote-Trefferquote gegen den Goldstandard.

Begründung: Die Offline-Audits haben den Altbestand bis zur Erschöpfung
vermessen. Die neue Dedup-Regel, die Effekttyp-Korrektur und der
Prüfspur-Abschnitt sind auf **neuen** Zeilen noch nie gelaufen. Und die einzige
Kennzahl, die den Forschungszweck bestimmt — wie viele brauchbare Effekte ein
Volltext liefert — lässt sich ohne Calls nicht messen.

---

## 6. Empfehlung und offene Entscheidungen

**Empfehlung:** Zuerst die 709 Zeilen in einer Stichprobe abschließen (1–2 h,
kein Guthaben), dann den Kalibrierungslauf mit 12 Volltexten und einem
vorher festgelegten Ausbeute-Zielwert starten. Der Goldstandard (30 Dokumente)
sollte parallel entstehen, nicht davor — sonst verschiebt sich der erste
echte Lauf um Wochen.

**Offene Entscheidungen des Projektinhabers:**

1. Freigabe für Netto-Modellaufrufe im Kalibrierungslauf (Budgetrahmen).
2. Zielwert der Ausbeute: 1,5 Zeilen/Volltext als Anspruch oder ein
   realistischerer Startwert?
3. Goldstandard vor oder parallel zum Kalibrierungslauf?

**Meine Position in einem Satz:** Ein weiteres Datenintegritäts-Audit wäre
billig, aber wirkungslos; der nächste sinnvolle Schritt ist ein kleiner,
budgetierter Extraktionslauf mit vorher definiertem Zielwert.

---

## Anhang: Belege und Grenzen

- Baseline-Zahlen: `IMPLEMENTATION_LOG.md` (Exercise-Lauf, abgeschlossen),
  `data/baseline/exercise-bbb324-metrics.{json,md}`.
- Teststand: 1 353 gesammelte Tests; letzte Vollläufe 1 154, 1 184 und
  1 165 passed, je 2 skipped (`data/runs/suite_*.log`).
- Eigene Messungen dieses Zeitraums:
  `lesepass_filter_20261110.md`, `pass_b_ohne_zwilling_20261110.md`,
  `pruefung_pass_b_zeile_20261110.md`, `se_ki_konsistenz_20261110.md`,
  `arbeitsstand_20261110.md`.
- **Grenze der Aussagen:** Die Baseline stammt aus einem Lauf vor den
  Extraktions-Fixes. Die Ausbeute nach den Fixes ist unbekannt — genau das
  soll der Kalibrierungslauf messen. Die 5–10 %-Schätzung zum 709er-Audit ist
  eine Einschätzung, keine Messung, und als solche gekennzeichnet.
