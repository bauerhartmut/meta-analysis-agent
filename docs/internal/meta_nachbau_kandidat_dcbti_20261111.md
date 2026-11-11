# Ersatzkandidat: Digitale CBT-I bei Jugendlichen (2026-11-11)

## Anlass

Der CBT-I-Pilot von Mei et al. 2024 ist blockiert, weil nur eine von sechs
Primärstudien einen freien PMC-PDF-Zugang hat. Gesucht wurde deshalb eine
Metaanalyse mit kleinem k, klarem Zielwert und vollständig frei erreichbaren
Primärtexten.

## Kandidat

**Effectiveness of Digital Cognitive Behavioral Therapy for Insomnia in Young
People: Preliminary Findings from Systematic Review and Meta-Analysis.**

- Zeitschrift: Journal of Personalized Medicine 2022;12(3):481
- DOI: `10.3390/jpm12030481`
- PMC: `PMC8949345`
- PMID: `35330480`
- Zielwert: subjektive Schlafqualität nach Behandlung
- Gepoolter Effekt: **Hedges g = −0,58 (95 %-KI −1,03 bis −0,13), k = 4**
- Heterogenität: im Text mit **I² = 84 %** für den Post-Treatment-Wert berichtet

Der Zielwert ist noch nicht nachgerechnet. Er wird erst in den
Antwortschlüssel übernommen, wenn die vier Primärtexte extrahiert und die
Studienwerte gepoolt sind.

## Primärstudien und Zugang

| Studie | PMID | PMC | Freier Volltext |
|---|---|---|---|
| Morris et al. 2015 | 26079158 | nein | Accepted Version, White Rose Research Online |
| Freeman et al. 2017 (OASIS) | 28888927 | `PMC5614772` | PMC, zusätzlich Strathprints-PDF |
| Fucito et al. 2017 | 28118486 | `PMC5378596` | PMC-Autorenmanuskript |
| de Bruin et al. 2018 | 29052846 | nein | UvA-DARE-Repository, zusätzlich Wiley bronze |

### Geprüfte PDF-Links

- Morris 2015:
  `https://eprints.whiterose.ac.uk/89162/3/Internet.pdf`
  (HTTP 200, `application/pdf`, 524.906 Bytes)
- Freeman 2017:
  `https://strathprints.strath.ac.uk/61758/1/Freeman_etal_LP_2017_effects_of_improving_sleep_on_mental_health_OASIS_a_randomised_controlled_trial.pdf`
  (HTTP 200, `application/pdf`, 509.421 Bytes)
- Fucito 2017:
  `https://pmc.ncbi.nlm.nih.gov/articles/PMC5378596/`
  (PMC-Volltext frei; PDF-Download über die PMC-Seite)
- de Bruin 2018:
  `https://pure.uva.nl/ws/files/24145097/Improvements_of_adolescent_psychopathology_after_insomnia_treatment.pdf`
  (HTTP 200, `application/pdf`, 453.617 Bytes)

## Zugangsbewertung

**Alle vier Primärtexte sind frei erreichbar.** Damit ist die praktische
Zugangshürde beseitigt.

**Aber:** Die strenge Vorgabe „alle über PubMed/PMC“ ist auch hier nicht
erfüllt. Zwei Studien liegen in PMC, zwei in Universitätsrepositorien bzw.
beim Verlag. PubMed verlinkt diese Repositorien nicht zwingend. Wer strikt
nur PMC akzeptiert, muss weiter suchen; für den Nachbau ist der Zugang
dennoch gesichert.

## Eignung und Risiken

- Klein und klar: vier RCTs, ein publizierter Zielwert, kein Netzwerk.
- Alle Primärtexte frei; keine Beschaffung über Bibliothek nötig.
- Hohe Heterogenität (I² = 84 %) und kleines k: der Nachbau prüft
  Pooling und Heterogenität, nicht die Stabilität einer großen Evidenzbasis.
- Zwei Texte sind Repository-Versionen (Morris, de Bruin), keine
  Verlags-PDFs. Das ist für die Datenextraktion zulässig, muss aber im
  Protokoll vermerkt werden.
- Der Zielwert ist noch nicht unabhängig nachgerechnet.

## Nächster Schritt

1. Neues Pilotprotokoll nur mit den vier Studien und ohne Zielwert anlegen.
2. Alle vier PDFs nach `data/meta_nachbau/pilot_dcbti/volltexte/` legen.
3. Studienwerte für subjektive Schlafqualität extrahieren und den Pool
   unabhängig nachrechnen.
4. Erst danach den Antwortschlüssel einfrieren und die Pipeline starten.

Bis dahin bleibt der CBT-I-Fall von Mei et al. blockiert; der neue Fall ist
ein Kandidat, kein bereits validierter Pilot.
