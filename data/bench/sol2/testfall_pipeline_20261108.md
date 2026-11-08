# Testfall der Lieferungs-Pipeline

Stand: 2026-11-08. Synthetische PDFs mit bekanntem Zustand, danach
`triage_lieferung.py` und `pruefe_lieferung.py` darauf. Kein Netz.

Ergebnis: **17 von 17 Erwartungen erfuellt.**

| Erwartung | Ergebnis | Detail |
|---|---|---|
| Triage Exit-Code 0 | ok | rc=0 |
| poolbare Datei erkannt | ok | zustand=poolbar |
| Scan als Scan erkannt | ok | zustand=scan |
| fehlender Endpunkt erkannt | ok | zustand=endpunkt_nicht_berichtet |
| SOL-Zeile ohne poolbaren Effekt erkannt | ok | zustand=sol_nicht_poolbar |
| k = Basis + poolbare Dateien | ok | k_neu=4 basis=3 poolbar=1 |
| k waechst um genau eine Studie | ok | poolbar=1 |
| nicht gelieferter Artikel gemeldet | ok | fehlend=['33157425'] |
| Datei ohne PMID als fremd gemeldet | ok | fremd=['unbekannt_ohne_pmid.pdf'] |
| Scan traegt keine Zeichen | ok | chars=0 |
| Pruefskript meldet keinen Widerspruch | ok | rc=0 |
| Pruefskript findet k konsistent | ok | True |
| Scan wird im Pruefbericht gezaehlt | ok | scan=1 |
| falsches k fuehrt zu Exit 1 | ok | rc=1 |
| falsches k wird als Fehler benannt | ok | ['fehler', 'ok', 'hinweis', 'hinweis', 'ok', 'hinweis', 'hinweis', 'ok'] |
| leeres Verzeichnis fuehrt zu Exit 2 | ok | rc=2 |
| bekannte Luecke: Tabelle ohne Pipes wird nicht gelesen | ok | blocks=0 sol_rows=0 |

## Was der Test abdeckt

- Scan ohne Textebene wird als `scan` gemeldet und zaehlt nicht als
  gelesen; das Pruefskript zaehlt ihn getrennt.
- Ein nicht berichteter Endpunkt wird als `endpunkt_nicht_berichtet`
  gefuehrt, nicht als Kettenfehler.
- Eine Datei ohne PMID im Namen erscheint als `fremd`.
- Ein nicht gelieferter Artikel der Zugangsliste erscheint unter
  `fehlend`.
- Ein Bericht mit falschem k fuehrt bei `pruefe_lieferung.py` zu Exit 1
  und einem Befund der Schwere `fehler`.
- Ein leeres Verzeichnis fuehrt zu Exit 2, nicht zu Exit 0.

## Gefundene Grenzen der Pipeline

1. **Tabellen ohne Trennzeichen werden nicht erkannt.** Eine SOL-Zeile
   in einer Tabelle, die nur durch Spaltenabstand getrennt ist, ergibt
   keinen Block (`blocks = 0`) und damit keine Zeile; der Zustand lautet
   dann `endpunkt_nicht_berichtet`. Mit Pipes als Trenner gelesen ergibt
   dieselbe Zeile `sol_nicht_poolbar`.
2. **`leser_luecke` ist nicht erreichbar.** `triage_dokument` verlangt
   `sol_rows > 0` bei `arm_stored + direct_stored == 0`. `sol_rows` wird
   in `read_pdf_corpus.py` aber ausschliesslich aus den gespeicherten
   Zeilen gebildet (`all_rows = stored_arm + stored_direct`); beide
   Bedingungen schliessen sich aus.
3. Die Folge ist eine Fehlklassifikation, keine verlorene Studie: eine
   berichtete, aber nicht poolbare SOL-Zeile kann als 'Endpunkt nicht
   berichtet' gezaehlt werden. Solche Faelle am Volltext pruefen, nicht
   der Meldung glauben.

## Grenzen

- Der Test prueft die Meldewege, nicht die inhaltliche Extraktion.
- Die PDFs sind minimal (Helvetica, eine Seite); echte Verlags-PDFs
  haben Spalten und Tabellen, die hier nicht vorkommen.
