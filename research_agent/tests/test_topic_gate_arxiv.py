"""Relevanz-Gate: arXiv-Fehlquellen aus dem Melatonin-Netzlauf verwerfen.

Der erste Netzlauf ließ SLAM-, Quantenbanking-, N-body- und Tensor-ArXiv-
Papier durch die Gate-Aktion. Ursache: `_REJECT_ARXIV_CATS` war definiert,
wurde aber nie angewendet, und moderne numerische arXiv-Ids tragen die
Kategorie gar nicht in der URL. Dieser Test hält die reale Abwehr fest:

* legacy arXiv-URL mit rejizierter Kategorie -> hart abgelehnt
* legacy Kategorie mit Thema-Plausible Titel (chao-dyn, Circadian) ->
  trotzdem abgelehnt (Kategoriewort schlägt Titel)
* moderne numerische Id mit nur 1 Themengroup -> abgelehnt
* moderne numerische Id mit >= 2 Themengroups -> zugelassen
* normale (nicht-arxiv) Treffer -> Verhalten unveraendert (>= 1 Gruppe)
"""

import unittest

from research_agent.orchestrator import ResearchOrchestrator


class _Result:
    def __init__(self, url: str, title: str, snippet: str = ""):
        self.url = url
        self.title = title
        self.snippet = snippet


class TopicGateArxivTest(unittest.TestCase):
    def setUp(self):
        self.orch = ResearchOrchestrator.__new__(ResearchOrchestrator)
        self.orch.current_topic = (
            "does melatonin improve sleep onset latency and sleep quality in adults")

    def test_legacy_arxiv_rejected_category(self):
        r = _Result("https://arxiv.org/abs/cs.AI/0112002",
                    "An Agent Framework for Interaction")
        self.assertFalse(self.orch._is_topic_relevant(r))

    def test_legacy_arxiv_category_beats_on_topic_title(self):
        # chao-dyn (physics) mit im Titel thematisch passendem Wort:
        # die Kategorie entscheidet, nicht der Titel.
        r = _Result("https://arxiv.org/abs/chao-dyn/9812014v1",
                    "A Study of Circadian Rhythm and Meteorological Factors "
                    "Influencing Sleep")
        self.assertFalse(self.orch._is_topic_relevant(r))

    def test_modern_arxiv_single_keyword_hit_rejected(self):
        # Aus dem echten Lauf: ein Doppel-Slam und ein N-body-Code kamen
        # mit je nur einem Keyword-Vorrat durch die Gate-Aktion.
        r = _Result("https://arxiv.org/abs/2603.15603v1",
                    "Fast SAM 3D Body: Accelerating SAM 3D Body for "
                    "Real-Time Full Body Reconstruction")
        self.assertFalse(self.orch._is_topic_relevant(r))

    def test_modern_arxiv_two_group_hits_survive(self):
        # Ein legitimer arXiv-Treffer (Sensor-DLMO-Schätzung) matcht
        # mind. zwei Themangruppen (melatonin + sleep) und bleibt drin.
        r = _Result("https://arxiv.org/abs/1908.07483v5",
                    "Sensor-Based Estimation of Dim Light Melatonin Onset "
                    "(DLMO) with Sleep and Actigraphy Data")
        self.assertTrue(self.orch._is_topic_relevant(r))

    def test_non_arxiv_behaviour_unchanged(self):
        r = _Result("https://pubmed.ncbi.nlm.nih.gov/30088881/",
                    "Melatonin improves sleep onset latency in adults "
                    "(randomized, placebo controlled)")
        self.assertTrue(self.orch._is_topic_relevant(r))


if __name__ == "__main__":
    unittest.main()
