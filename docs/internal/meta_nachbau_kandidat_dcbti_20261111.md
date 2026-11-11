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

Der Zielwert ist am 2026-11-11 aus den vier Primärtexten nachgerechnet
worden. Die Reproduktion liegt in
`data/meta_nachbau/pilot_dcbti/ergebnis.md`.

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
- Der Zielwert ist unabhängig nachgerechnet und innerhalb der Toleranz
  reproduziert.

## Stand 2026-11-11

1. Das Pilotprotokoll liegt unter
   `data/meta_nachbau/pilot_dcbti/protokoll.md` und enthält keinen Zielwert.
2. Die vier PDFs liegen lokal unter
   `data/meta_nachbau/pilot_dcbti/volltexte/`.
3. Die Studienwerte sind extrahiert; der Pool ist nachgerechnet:
   g = -0,584 [-1,029; -0,139], k = 4, I² = 83,7 %, tau² = 0,161.
4. Antwortschlüssel und Prüfskript liegen vor; das Prüfskript läuft grün.

Der Modelllauf wurde nicht gestartet. Er bleibt bis zum B-Rücklauf und zur
ausdrücklichen Freigabe blockiert. Der CBT-I-Fall von Mei et al. bleibt
zugangsblockiert; der dCBT-I-Fall ist ein validierter Nachbau, kein
Pipeline-Ergebnis.
