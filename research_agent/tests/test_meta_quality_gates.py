"""Regressionstests fuer die drei Metaanalyse-Quality-Fixes (01.11.2026).

Grundlage war die Qualitaetspruefung des Abschlussberichts
'20261101-1221-Exercise-and-depressive-symptoms-in-adul.md':

1. GRADE-Defekt: die Imprecision-Abwertung las ``Stichprobensumme 0 < 200``,
   weil die standardisierten Pool-Zeilen das Feld ``n`` nicht durchreichten -
   mechanisch very_low in jedem Pool, egal wie gross die Studien sind.
2. Konstrukt-Defekt: der log_ratio-Pool mischte Depressions-Assoziationen
   verschiedener Expositionen (UPF-Konsum, Analphabetismus, ADL-Behinderung),
   weil build_analysis nur nach Outcome gruppierte - ein Exposure-Gate fehlte.
3. Protokoll-Defekt: eine Adoleszenten-Studie landete still im Pool, obwohl
   das eingefrorene Protokoll 'adults (18+)' festlegt - Population wird jetzt
   an der Gruppe markiert statt still gepoolt.
"""

import unittest

from research_agent.meta import grade as meta_grade
from research_agent.meta.pooling import build_analysis

_OUTCOME = ["depressive symptoms"]


def _row(**over):
    base = {
        "source_id": "s1",
        "title": "Physical activity study",
        "year": "2020",
        "outcome": "depressive symptoms",
        "outcome_key": "depressive symptoms",
        "comparison": "physically active vs inactive",
        "effect_type": "or",
        "effect": 1.25,
        "se": 0.2,
        "ci_low": 1.0,
        "ci_high": 1.56,
        "ci_level": 0.95,
        "n": 500,
        "design": "cohort",
        "population": "older adults",
        "disputed": 0,
        "rejection_reason": "",
    }
    base.update(over)
    return base


class ImprecisionUsesRealSampleSizes(unittest.TestCase):
    """n der Studien erreicht grade_group statt mechanisch 0."""

    def _graded(self, n_a, n_b):
        rows = [
            _row(source_id="s1", effect_type="smd", effect=-0.30, se=0.12,
                 n=n_a, design="randomized", ci_low=None, ci_high=None,
                 comparison="aerobic exercise vs usual care"),
            _row(source_id="s2", effect_type="smd", effect=-0.60, se=0.14,
                 n=n_b, design="randomized", ci_low=None, ci_high=None,
                 comparison="aerobic exercise vs waitlist"),
        ]
        analysis = build_analysis(rows)
        group = analysis["groups"]["depressive symptoms [hedges_g]"]
        self.assertIsNotNone(group.get("pooled"), "k=2 muss poolen")
        return meta_grade.grade_group(group)

    def test_large_body_keeps_precision_level(self):
        graded = self._graded(500, 400)
        # Der eigentliche Bug war die mechanische 0-Summe; die unabhaengige
        # KI-Breiten-Regel darf bei k=2 gerne feuern, sie wiegt nichts mit n.
        self.assertFalse(
            any("Stichprobensumme 0 <" in d for d in graded["downgrades"]),
            f"mechanische 0-Summe ist weg: {graded['downgrades']}"
        )

    def test_small_body_downgrades_with_the_real_sum(self):
        graded = self._graded(50, 40)
        self.assertTrue(
            any("Stichprobensumme 90 < 200" in d for d in graded["downgrades"]),
            f"die echte Summe 90 muss in der Begruendung stehen: "
            f"{graded['downgrades']}"
        )


class ExposureGate(unittest.TestCase):
    """Assoziationszeilen ohne Aktivitaets-Exposure landen im Ausschluss."""

    def test_foreign_exposure_is_excluded_with_a_reason(self):
        rows = [
            _row(source_id="upf", title="UPF intake study",
                 comparison="High UPF consumption (>=4 servings/day) vs Low"),
            _row(source_id="adl", title="ADL disability study",
                 comparison="ADL disability vs no ADL disability"),
        ]
        analysis = build_analysis(rows, outcomes=_OUTCOME)
        self.assertIsNone(
            analysis["groups"].get("depressive symptoms [log_ratio]"),
            "fremde Expositionen duerfen keinen Pool bilden")
        reasons = " | ".join(e["reason"] for e in analysis["excluded"])
        self.assertIn("Exposure-Gate", reasons)
        self.assertIn("UPF", reasons)

    def test_activity_exposure_survives_the_gate(self):
        rows = [_row(source_id="pa", title="Physical activity study")]
        analysis = build_analysis(rows, outcomes=_OUTCOME)
        group = analysis["groups"]["depressive symptoms [log_ratio]"]
        labels = [r["label"] for r in group["rows"]]
        self.assertEqual(labels, ["Physical activity study (2020)"])

    def test_intervention_rows_are_not_gated(self):
        # smd/g vergleichen Behandlungsarme ('usual care' ohne Aktivitaetswort).
        rows = [_row(source_id="rct", title="RCT arm study",
                     effect_type="smd", effect=-0.4, se=0.15,
                     n=120, design="randomized",
                     comparison="usual care")]
        analysis = build_analysis(rows, outcomes=_OUTCOME)
        self.assertIn("depressive symptoms [hedges_g]", analysis["groups"])

    def test_gate_needs_an_aim(self):
        # Ohne Zielmass (generische Analyse) greift das Gate nicht.
        rows = [_row(source_id="upf", title="UPF intake study",
                     comparison="High UPF consumption vs Low")]
        analysis = build_analysis(rows)
        self.assertIn("depressive symptoms [log_ratio]", analysis["groups"])

    def test_title_or_moderator_names_the_activity(self):
        # Der echter Fehl-Exklusionsfall aus dem 12:21-Bericht: comparison
        # benennt die Referenzkategorie, die Exposition steht im Moderator.
        rows = [_row(source_id="role", title="The role of physical activity",
                     effect_type="beta", effect=0.216, se=0.059,
                     ci_low=0.1, ci_high=0.332, n=7279,
                     comparison="chronic disease incidence predicting future "
                                "depressive symptoms",
                     moderators="baseline physical activity levels")]
        analysis = build_analysis(rows, outcomes=_OUTCOME)
        group = analysis["groups"]["depressive symptoms [raw:beta]"]
        self.assertEqual(
            [r["label"] for r in group["rows"]],
            ["The role of physical activity (2020)"])


class PopulationScopeFlag(unittest.TestCase):
    """Protokollverstoess werden markiert, nicht still gepoolt."""

    def test_adolescents_are_flagged_at_the_group(self):
        rows = [
            _row(source_id="adult1", title="Adult PA study",
                 population="adults of European ancestry"),
            _row(source_id="teens", title="Teen PA study",
                 population="Japanese adolescents (11-14 years)"),
        ]
        analysis = build_analysis(rows, outcomes=_OUTCOME)
        group = analysis["groups"]["depressive symptoms [log_ratio]"]
        self.assertEqual(len(group["scope_flags"]), 1)
        flagged_label, flagged_text = group["scope_flags"][0]
        self.assertEqual(flagged_label, "Teen PA study (2020)")
        self.assertIn("nicht Erwachsene", flagged_text)
        # Die Zeile bleibt im Pool, aber die Markierung haengt nur an ihr:
        self.assertTrue(all(r.get("scope_flag") == ""
                            for r in group["rows"]
                            if r["label"] == "Adult PA study (2020)"))

    def test_adult_population_is_not_flagged(self):
        rows = [_row(source_id="adults", title="Adult PA study",
                     population="adults (18-65 years)")]
        analysis = build_analysis(rows, outcomes=_OUTCOME)
        group = analysis["groups"]["depressive symptoms [log_ratio]"]
        self.assertEqual(group["scope_flags"], [])


if __name__ == "__main__":
    unittest.main()
