# Entwicklungsauftrag: Research-Agent auf wissenschaftliches Forschungsniveau bringen

*(eingegangen 03.11.2026; übernimmt die Phasen 0–9 des ersten Auftrags und präzisiert sie. Verwaltet in IMPLEMENTATION_LOG.md, ab Sprint 16.)*

---

## 1. Übergeordnetes Entwicklungsziel

Analysiere und verbessere die bestehende Research-Agent-Architektur mit dem Ziel, einen möglichst autonomen wissenschaftlichen Forschungsagenten zu entwickeln.

Der Agent soll langfristig in der Lage sein, selbstständig:

1. Wissenschaftliche Forschungsfragen zu analysieren und zu operationalisieren.
2. Relevante wissenschaftliche Literatur möglichst vollständig zu finden.
3. Volltexte zu beschaffen und kritisch zu untersuchen.
4. Studiendesigns und Evidenzqualität korrekt zu beurteilen.
5. Quantitative Daten zuverlässig zu extrahieren.
6. Metaanalysen methodisch korrekt durchzuführen.
7. Widersprüche zwischen Studien zu erkennen und aufzulösen.
8. Forschungslücken zu identifizieren.
9. Neue Suchstrategien und Forschungsfragen abzuleiten.
10. Seine eigenen Ergebnisse kritisch zu hinterfragen und zu überprüfen.
11. Einen wissenschaftlich belastbaren Abschlussbericht zu erstellen.

Es geht ausdrücklich **nicht** darum, möglichst viele Hypothesen, Quellen oder Fakten zu generieren.

Es geht darum, **möglichst zuverlässige Erkenntnisse** zu gewinnen.

**Wichtig:** Bestehende funktionierende Architektur nicht unnötig ersetzen. Zuerst den vorhandenen Code, die Datenbank, die Agentenlogik und die bisherigen Workflows analysieren. Anschließend gezielt verbessern.

---

## 2. Höchste Priorität: Effektgrößenextraktion reparieren

Der aktuelle Forschungsbericht zeigt das größte Problem bei der quantitativen Datenextraktion.

Im letzten Lauf wurden 8 Effektzeilen extrahiert, aber **keine einzige konnte für eine Metaanalyse verwendet werden.**

Damit kann der Agent seine zentrale Aufgabe noch nicht zuverlässig erfüllen.

### 2.1 Strukturierte Extraktion

Implementiere eine robuste Extraktionspipeline, die folgende Informationen erkennt:

- Studienpopulation
- Stichprobengröße
- Interventionsgruppe
- Kontrollgruppe
- Studiendesign
- Intervention und Dosierung
- Messzeitpunkt
- Primärer und sekundärer Endpunkt
- Mittelwerte
- Standardabweichungen
- Standardfehler
- Konfidenzintervalle
- p-Werte
- Effektgrößen
- Anzahl der Messungen
- Korrelationen bei wiederholten Messungen

Die Extraktion muss auch **komplexe Tabellen, Abbildungen, Supplementary Materials und PDF-Volltexte** berücksichtigen.

### 2.2 Crossover-Studien korrekt behandeln

Besonders wichtig ist die korrekte Verarbeitung von Within-Subject- und Crossover-Designs.

Der Agent darf diese Studien nicht wie gewöhnliche Parallelgruppenstudien behandeln.

Implementiere eine explizite Erkennung von:

- Randomisiereten Parallelgruppenstudien
- Randomisiereten Crossover-Studien
- Cluster-RCTs
- Faktoriellen Studiendesigns
- Wiederholten Messungen
- Mehrarmigen Studien

Bei Crossover-Studien müssen insbesondere **gepaarte Effektgrößen** und die **Within-Subject-Korrelation** berücksichtigt werden.

Wenn notwendige Daten fehlen, darf der Agent keine scheinbar präzisen Effektgrößen erfinden.

Stattdessen soll er:
1. Nach ergänzenden Informationen suchen.
2. Fehlende Werte als fehlend kennzeichnen.
3. Gegebenenfalls begründete Sensitivitätsanalysen durchführen.
4. Die Studie bis zur Klärung vom entsprechenden Pool ausschließen.

### 2.3 Doppel-Extraktion verbessern

Die zwei unabhängigen Extraktionsdurchläufe sollen erhalten bleiben.

Erweitere sie um:

- Vergleich auf Ebene einzelner Datenfelder.
- Automatische Erkennung numerischer Abweichungen.
- Prüfung von Einheiten und Vorzeichen.
- Prüfung der Gruppenzuordnung.
- Abgleich mit den Originaltabellen.
- Erkennung unterschiedlicher Interpretationen desselben Studienergebnisses.

Bei Diskrepanzen soll ein **dritter unabhängiger Extraktionsversuch** stattfinden.

Bleibt der Widerspruch bestehen, muss die Zeile als **ungeklärt** markiert werden.

Die Extraktionen dürfen niemals einfach gemittelt werden.

---

## 3. Literaturrecherche grundlegend verbessern

Der letzte Bericht dokumentiert erhebliche Ausfälle bei Semantic Scholar und OpenAlex.

Das ist problematisch, weil eine unvollständige Literaturbasis die gesamte nachfolgende Analyse verfälschen kann.

### 3.1 Mehrere unabhängige Suchquellen

Implementiere eine robuste Sucharchitektur mit mehreren wissenschaftlichen Datenquellen.

Mögliche Quellen:

- PubMed
- Europe PMC
- OpenAlex
- Crossref
- Semantic Scholar
- CORE
- Unpaywall
- Google Scholar, sofern technisch und rechtlich zulässig

Die einzelnen Quellen sollen nicht einfach parallel abgefragt werden.

Implementiere eine intelligente Suchsteuerung:

1. Relevante Datenbanken anhand der Forschungsfrage auswählen.
2. Suchanfragen für die jeweiligen Datenbanken optimieren.
3. Ergebnisse zusammenführen.
4. Duplikate anhand von DOI, PMID und weiteren Identifikatoren erkennen.
5. Fehlgeschlagene Suchanfragen protokollieren.
6. Alternative Datenquellen verwenden.
7. Unvollständige Suchläufe erkennen.
8. Bei Bedarf automatisch erneut suchen.

Ein fehlgeschlagener API-Aufruf darf nicht unbemerkt zu einer scheinbar vollständigen Recherche führen.

### 3.2 Citation Chaining

Implementiere systematische Vorwärts- und Rückwärtssuche.

Der Agent soll:

- Referenzlisten relevanter Studien untersuchen.
- Studien identifizieren, die relevante Arbeiten zitieren.
- Neue Studien anhand ihrer Zitationsbeziehungen finden.
- Die Suche iterativ erweitern.
- Den zusätzlichen Erkenntnisgewinn jeder Suchrunde messen.

Beende die Suche erst, wenn nachvollziehbare Sättigungskriterien erfüllt sind oder ein transparentes Ressourcenlimit erreicht wurde.

### 3.3 Suchvollständigkeit messen

Führe eine Suchabdeckung ein.

Dokumentiere:

- Welche Datenbanken durchsucht wurden.
- Welche Suchstrings verwendet wurden.
- Wie viele Ergebnisse jede Quelle geliefert hat.
- Welche Quellen ausgefallen sind.
- Wie viele Duplikate entfernt wurden.
- Wie viele Studien ausgeschlossen wurden.
- Welche Ausschlussgründe vorlagen.
- Wann die Suche zuletzt aktualisiert wurde.

**Der Agent muss zwischen einer abgeschlossenen Recherche und einer lediglich budgetbedingt abgebrochenen Recherche unterscheiden.**

---

## 4. Studienqualität und Risk-of-Bias verbessern

Der aktuelle Bericht verwendet maschinelle Risk-of-Bias-Bewertungen.

Diese dürfen nicht als gleichwertig zu einer validierten menschlichen Bewertung behandelt werden.

Implementiere etablierte Bewertungsverfahren.

Je nach Studiendesign:

- RoB 2 für randomisierte Studien.
- ROBINS-I für nicht randomisierte Interventionsstudien.
- AMSTAR 2 für systematische Reviews.
- QUADAS-2 für diagnostische Genauigkeitsstudien, sofern relevant.

Die Bewertung soll auf einzelnen Domänen beruhen und nicht nur ein pauschales Gesamturteil erzeugen.

Für jede Bewertung müssen gespeichert werden:

1. Bewertete Domäne.
2. Konkrete Textstelle.
3. Begründung.
4. Urteil.
5. Konfidenz der maschinellen Bewertung.
6. Mögliche alternative Interpretation.

**Besonders wichtig:** Das Modell muss zwischen fehlenden Informationen und tatsächlich schlechtem Studiendesign unterscheiden.

Ein **nicht berichteter** Aspekt ist **nicht automatisch** ein nachgewiesener methodischer Fehler.

---

## 5. Metaanalyse-Engine ausbauen

Die Metaanalyse muss zu einer eigenständigen, zuverlässig überprüfbaren Komponente werden.

### 5.1 Effektgrößen

Unterstütze mindestens:

- Mean Difference (MD)
- Standardized Mean Difference (SMD)
- Hedges g
- Risk Ratio (RR)
- Odds Ratio (OR)
- Hazard Ratio (HR)

Die Berechnungen müssen statistisch korrekt implementiert und unabhängig testbar sein.

### 5.2 Statistische Modelle

Implementiere:

- Fixed-Effect-Modelle
- Random-Effects-Modelle
- REML-Schätzung der Between-Study-Varianz
- Hartung-Knapp-Verfahren
- Heterogenitätsanalysen
- Prediction Intervals
- Sensitivitätsanalysen
- Leave-one-out-Analysen
- Subgruppenanalysen
- Meta-Regression, sofern ausreichend Studien vorhanden sind

Die Auswahl des Modells muss begründet werden.

Der Agent darf nicht automatisch ein komplexes statistisches Verfahren anwenden, wenn die Datenbasis dafür nicht ausreicht.

### 5.3 Besondere Datenprobleme

Berücksichtige explizit:

- Mehrere Interventionsarme.
- Mehrere Messzeitpunkte.
- Mehrere Outcomes derselben Studie.
- Abhängige Effektgrößen.
- Fehlende Standardabweichungen.
- Unterschiedliche Messskalen.
- Kleine Stichproben.
- Publikationsbias.

**Vermeide insbesondere die doppelte Verwendung derselben Kontrollgruppe** in mehreren unabhängigen Vergleichen ohne angemessene statistische Behandlung.

### 5.4 Reproduzierbarkeit

Jede Metaanalyse muss vollständig reproduzierbar sein.

Speichere:

- Eingabedaten.
- Verwendete Effektgrößen.
- Berechnungsformeln.
- Statistische Modellparameter.
- Softwareversion.
- Ausschlüsse.
- Sensitivitätsanalysen.
- Endergebnisse.

**Jeder gepoolte Wert muss bis zu den ursprünglichen Studiendaten zurückverfolgbar sein.**

---

## 6. Evidenzbewertung und Hypothesenmanagement überarbeiten

Im aktuellen Bericht existieren Hypothesen mit Konfidenzwerten (z. B. 0,70), obwohl keinerlei Evidenzzeilen vorhanden sind. Das muss geändert werden.

### 6.1 Strikte Trennung

Führe vier getrennte Kategorien ein:

1. Empirisch belegt
2. Durch Evidenz gestützt, aber unsicher
3. Widersprüchlich oder ungeklärt
4. Spekulativ / theoretisch

**Hypothesen ohne empirische Evidenz dürfen nicht als wissenschaftliche Erkenntnisse dargestellt werden.**

### 6.2 Konfidenzbewertung

Konfidenzwerte müssen nachvollziehbar aus der tatsächlichen Evidenz abgeleitet werden:

- Anzahl unabhängiger Studien.
- Studienqualität.
- Stichprobengröße.
- Effektpräzision.
- Konsistenz.
- Heterogenität.
- Direktheit der Evidenz.
- Publikationsbias.
- Unabhängigkeit der Quellen.

Unterscheide ausdrücklich:

- Plausibilität einer Hypothese.
- Qualität der empirischen Evidenz.
- Sicherheit der daraus gezogenen Schlussfolgerung.

**Ein LLM darf nicht allein aufgrund einer überzeugend klingenden Argumentation eine hohe Evidenzsicherheit vergeben.**

### 6.3 Hypothesenbremse

Erweitere die vorhandene Hypothesenbremse.

Eine neue Hypothese soll nur dann dauerhaft in das Forschungsprogramm aufgenommen werden, wenn:

- Sie eine konkrete Forschungsfrage adressiert.
- Sie empirisch überprüfbar ist.
- Sie nicht bereits redundant vorhanden ist.
- Sie eine nachvollziehbare wissenschaftliche Begründung besitzt.

Spekulative Mechanismen sollen in einem separaten Bereich verbleiben.

---

## 7. Autonome Forschungssteuerung verbessern

Das ist eine der wichtigsten langfristigen Aufgaben.

Der Agent soll nicht nur einen festgelegten Workflow abarbeiten, sondern selbstständig entscheiden, welche Forschungsarbeit als Nächstes den größten Erkenntnisgewinn verspricht.

### 7.1 Dynamische Priorisierung

Bewerte offene Aufgaben anhand von:

- Wissenschaftlicher Relevanz.
- Unsicherheit aktueller Erkenntnisse.
- Erwartetem Erkenntnisgewinn.
- Wahrscheinlichkeit einer erfolgreichen Bearbeitung.
- Benötigten Ressourcen.
- Abhängigkeiten von anderen Aufgaben.

Die Priorisierung soll dynamisch angepasst werden.

**Beispiel:** Wenn der Agent feststellt, dass keine einzige Studie für die Metaanalysis poolbar ist, sollte er nicht weitere spekulative Hypothesen generieren, sondern zunächst versuchen, die fehlenden Effektgrößen und statistischen Informationen zu beschaffen.

### 7.2 Selbstständige Fehlerbehebung

Der Agent soll erkennen:

- Wenn eine Extraktionsmethode wiederholt scheitert.
- Wenn eine Datenquelle nicht verfügbar ist.
- Wenn Studien systematisch falsch klassifiziert werden.
- Wenn bestimmte Studiendesigns nicht verarbeitet werden können.
- Wenn die Evidenzbasis unzureichend ist.

Anschließend geeignete alternative Vorgehensweisen auswählen.

### 7.3 Forschungszyklen

Jeder Zyklus soll durchlaufen:

1. Aktuellen Wissensstand analysieren.
2. Größte Wissenslücken identifizieren.
3. Forschungsaufgaben priorisieren.
4. Recherche oder Analyse durchführen.
5. Ergebnisse unabhängig überprüfen.
6. Widersprüche aktualisieren.
7. Wissensstand neu bewerten.
8. Nächsten Zyklus planen.

Jeder Zyklus muss nachvollziehbar dokumentiert werden.

---

## 8. Kritische Selbstprüfung einführen (Critic-Agenten)

Der Agent benötigt einen expliziten adverszialen Prüfprozess.

Nicht Zusammenfassen des Erkenntnisstands, sondern **aktives Widerlegen**:

- Sind die Quellen tatsächlich relevant?
- Sind Zitate korrekt interpretiert?
- Werden Ergebnisse aus Abstracts überinterpretiert?
- Sind Effektgrößen rechnerisch korrekt?
- Wurden Studien doppelt gezählt?
- Wurden negative oder neutrale Ergebnisse übersehen?
- Sind Ausschlussentscheidungen gerechtfertigt?
- Werden Korrelation und Kausalität verwechselt?
- Sind Schlussfolgerungen stärker als die Evidenz?
- Wurden alternative Erklärungen ausreichend berücksichtigt?

Der Critic soll konkrete Fehler und Gegenbelege liefern.

**Ein zweiter LLM-Aufruf mit derselben Aufgabenstellung reicht nicht als unabhängige Validierung.**

Nutze nach Möglichkeit andere Modelle, andere Prompts, deterministische Prüfungen und direkte Quellenkontrollen.

---

## 9. Benchmarks und automatisierte Tests

Ohne objektive Tests lässt sich nicht feststellen, ob die Architektur tatsächlich besser wird.

### 9.1 Testbereiche (separat testen)

- Literaturrecherche.
- Duplikaterkennung.
- Studienklassifikation.
- Datenextraktion.
- Effektgrößenberechnung.
- Crossover-Verarbeitung.
- Risk-of-Bias.
- GRADE.
- Metaanalyse.
- Quellenverifikation.
- Wissenschaftliche Schlussfolgerungen.

### 9.2 Goldstandard-Datensatz

Menschlich verifizierte Referenzw. Vergleiche:

- Precision und Recall der Studienauswahl.
- Fehlerquote bei numerischen Extraktionen.
- Genauigkeit der Effektgrößen.
- Anteil korrekt erkannter Studiendesigns.
- Anteil korrekt erkannter Ausschlussgründe.
- Qualität der Quellenbelege.
- Abweichung von Referenz-Metaanalysen.

### 9.3 Regressionstests

Jede Änderung an der Architektur muss gegen die bestehenden Benchmarks getestet werden.

---

## 10. Technische Zuverlässigkeit und Ressourcenmanagement

Der aktuelle Bericht zeigt 137 offene Aufgaben und einen Abbruch nach Erreichen des Zeitbudgets.

**Ein erreichter Zeit- oder Token-Limit darf nicht zu einem scheinbar abgeschlossenen Forschungsbericht führen.** Der Bericht muss zwischen:

- Wissenschaftlich abgeschlossen.
- **Teilweise abgeschlossen.**
- **Ressourcenlimit erreicht.**
- Technisch blockiert.
- Weitere Evidenz erforderlich.

unterscheiden und zwischen **abgeschlossen** und **nach Budget/abgebrochen** klar trennen.

Zusätzlich:

- Persistente Aufgabenwarteschlange.
- Wiederaufnahme unterbrochener Forschungszyklen.
- Priorisierung kritischer Aufgaben.
- Retry-Strategien mit Backoff.
- API-Fehlerklassifikation.
- Ressourcenbudget pro Teilaufgabe.
- Fortschrittskontrolle.
- Erkennung redundanter Arbeit.
- Abbruch bei fehlendem Erkenntnisgewinn.

---

## 11. Wissenschaftlichen Abschlussbericht verbessern

Jeder Bericht soll enthalten:

1. Forschungsfrage und Protokoll.
2. Suchstrategie.
3. PRISMA-Flussdiagramm.
4. Eingeschlossene und ausgeschlossene Studien.
5. Charakteristika der Studien.
6. Risk-of-Bias-Eintritt.
7. Extrahierte Effektgrößen.
8. Metaanalyse mit Konfidenzintervallen.
9. Heterogenitätsanalyse.
10. Sensitivitätsanalysen.
11. GRADE-Evaluation.
12. Widersprüchliche Evidenz.
13. Forschungslücken.
14. Limitationen.
15. Reproduzierbare Daten und Berechnungsschritte.
16. Abschließendes wissenschaftliches Urteil.

Wenn keine Metaanalyse möglich ist, soll der Agent eine **strukturierte narrative Synthese** durchführen. Er darf niemals eine quantitative Aussage vortäuschen, wenn die Daten dafür nicht ausreichen.

---

## 12. Konkreter Implementierungsplan

**Phase 1 – Bestandsaufnahme:** Gesamte Architektur untersuchen; Fehlerquellen des letzten Berichts identifizieren; konkrete techn. Vorschläge. Noch keine unnötigen Refactorings.

**Phase 2 – Kritische Fehler beheben:** Effektgrößenextraktion; Crossover; Doppel-Extraktion; Widersprüche; Suchrecherchem; falsche Konfidenz-Werte.

**Phase 3 – Wissenschaftliche Methoden:** RoB-Verfahren; Metaanalyse-Engine erweitern; GRADE verbessern; Publikationsbias und Sensitivitätsanalysen.

**Phase 4 – Autonomie:** Dynamische Forschungsplanung; Selbstständige Fehlerbehebung; Adversarial Critic; Iterative Wissensaktualisierung; Erkenntnisbasierte Aufgabenpriorisierung.

**Phase 5 – Validierung:** Goldstandard-Datensatz; Benchmark-Suite; Regressionstests; Schwachstellen dokumentieren.

---

## 13. Abnahmekriterien

- Jede extrahierte Zahl ist auf eine konkrete Originalquelle zurückführbar.
- Numerische Extraktionen erreichen eine hohe Genauigkeit auf einem menschlich verifizierten Testdatensatz.
- Crossover- und Parallelgruppenstudien werden korrekt unterschieden.
- Effektgrößen werden unabhängig nachgerechnet.
- Widersprüchliche Extraktionen werden zuverlässig erkannt.
- Quellen- und Suchausfälle werden transparent behandelt.
- Metaanalysen stimmen innerhalb definierter Toleranzen mit validierten Referenzberechnungen überein.
- Risk-of-Bias-Bewertungen sind domänenbasiert und nachvollziehbar.
- Hypothesen ohne Evidenz werden nicht als empirisch gestützte Erkenntnisse dargestellt.
- Forschungszyklen können nach Unterbrechungen fortgesetzt werden.
- Der Critic kann konkrete Fehler und unbelegte Schlussfolgerungen identifizieren.
- Alle Ergebnisse sind reproduzierbar.

**Für jede Kennzahl muss ein messbarer Zielwert anhand eines definierten Testdatensatzes festgelegt werden. Behaupte keine erreichte Genauigkeit ohne entsprechende Benchmark-Ergebnisse.**

---

## Abschließende Anweisung

**Arbeite nicht einfach die Liste mechanisch ab.** Denke wie ein Softwarearchitekt und Wissenschaftsmethodiker:

- Untersuche zuerst, welche bestehenden Komponenten bereits gut funktionieren und wo die tatsächlichen Engpässe liegen.
- Bevorzuge Verbesserungen, die mehrere nachgelagerte Probleme gleichzeitig lösen.
- Vermeide unnötige Komplexität, redundante Agenten und bloße Feature-Erweiterungen ohne messbaren wissenschaftlichen Nutzen.
- Dokumentiere jede relevante Architekturänderung.

**Das langfristige Ziel ist ein autonomer Forschungsagent, der auf menschlichem Niveau wissenschaftliche Literatur recherchieren, bewerten, quantitativ synthetisieren, seine Ergebnisse kritisch überprüfen und neue Erkenntnisse gewinnen kann.**

**Nicht die Menge der produzierten Informationen ist der Erfolgsmaßstab, sondern deren wissenschaftliche Richtigkeit.**
