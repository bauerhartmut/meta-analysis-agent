"""Phase 9: RoB 2 signalling-question algorithms (deterministic rules).

The verdicts below are the official RoB 2 rules, code as rules: Y/PY
collapse, N/PN collapse, NI carries domain-specific weight. Cases come
from the algorithm's own decision nodes; the two arms the literature
flags as diagram-dependent stay deliberately conservative and are pinned
by these same tests, so a future diagram check cannot drift silently.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.meta.rob2_signalling import (
    HIGH, LOW, ROB2_QUESTIONS, ROB2_DOMAIN_ORDER, SOME,
    overall_rob2, rob2_domain_rating, rob2_pass_summary,
)


def _s(**answers):
    return {k: v for k, v in answers.items()}


class Domain1Test(unittest.TestCase):
    def test_clean_randomisation_with_no_baseline_problem_is_low(self):
        rating = rob2_domain_rating("randomisation", _s(**{
            "1.1": "y", "1.2": "y", "1.3": "n"}))
        self.assertEqual(rating, LOW)
        self.assertEqual(
            rob2_domain_rating("randomisation", _s(**{
                "1.1": "py", "1.2": "py", "1.3": "pn"})), LOW)

    def test_concealed_but_baseline_problem_is_concerns(self):
        rating = rob2_domain_rating("randomisation", _s(**{
            "1.1": "y", "1.2": "y", "1.3": "y"}))
        self.assertEqual(rating, SOME)

    def test_unconcealed_cannot_reach_low(self):
        self.assertEqual(rob2_domain_rating("randomisation", _s(**{
            "1.1": "y", "1.2": "n", "1.3": "n"})), SOME)

    def test_unclear_process_plus_baseline_problem_is_high(self):
        self.assertEqual(rob2_domain_rating("randomisation", _s(**{
            "1.1": "ni", "1.2": "ni", "1.3": "y"})), HIGH)
        self.assertEqual(rob2_domain_rating("randomisation", _s(**{
            "1.1": "n", "1.2": "pn", "1.3": "ni"})), HIGH)

    def test_unclear_without_baseline_problem_is_concerns(self):
        self.assertEqual(rob2_domain_rating("randomisation", _s(**{
            "1.1": "n", "1.2": "n", "1.3": "n"})), SOME)


class Domain2AssignmentTest(unittest.TestCase):
    def test_blinded_with_appropriate_analysis_is_low(self):
        s = _s(**{"2.1": "n", "2.2": "n", "2.6": "y"})
        self.assertEqual(rob2_domain_rating("deviations_assignment", s),
                         LOW)

    def test_unblinded_without_deviation_impact(self):
        s = _s(**{"2.1": "y", "2.2": "n", "2.3": "n", "2.6": "y"})
        self.assertEqual(rob2_domain_rating("deviations_assignment", s),
                         LOW)

    def test_inappropriate_analysis_with_substantial_impact_is_high(self):
        s = _s(**{"2.1": "y", "2.2": "y", "2.3": "n", "2.6": "n",
                  "2.7": "y"})
        self.assertEqual(rob2_domain_rating("deviations_assignment", s),
                         HIGH)

    def test_inappropriate_analysis_without_impact_is_concerns(self):
        s = _s(**{"2.1": "y", "2.2": "y", "2.3": "n", "2.6": "pn",
                  "2.7": "n"})
        self.assertEqual(rob2_domain_rating("deviations_assignment", s),
                         SOME)

    def test_unbalanced_deviations_affecting_outcome_is_high(self):
        s = _s(**{"2.1": "y", "2.3": "y", "2.4": "y", "2.5": "n",
                  "2.6": "y"})
        self.assertEqual(rob2_domain_rating("deviations_assignment", s),
                         HIGH)

    def test_balanced_deviations_stay_concerns(self):
        s = _s(**{"2.1": "y", "2.3": "y", "2.4": "y", "2.5": "y",
                  "2.6": "y"})
        self.assertEqual(rob2_domain_rating("deviations_assignment", s),
                         LOW)


class Domain3Test(unittest.TestCase):
    def test_all_data_available_is_low(self):
        self.assertEqual(rob2_domain_rating("missing_outcome_data", _s(**{
            "3.1": "y"})), LOW)
        self.assertEqual(rob2_domain_rating("missing_outcome_data", _s(**{
            "3.1": "py"})), LOW)

    def test_missing_data_corrected_is_low(self):
        self.assertEqual(rob2_domain_rating("missing_outcome_data", _s(**{
            "3.1": "n", "3.2": "y"})), LOW)

    def test_missingness_without_value_dependence_stays_conservative(self):
        # RECONSTRUCTED arm, pinned conservatively (no low overclaim).
        self.assertEqual(rob2_domain_rating("missing_outcome_data", _s(**{
            "3.1": "n", "3.2": "n", "3.3": "n"})), SOME)

    def test_value_dependence_likely_is_high(self):
        self.assertEqual(rob2_domain_rating("missing_outcome_data", _s(**{
            "3.1": "n", "3.2": "n", "3.3": "y", "3.4": "y"})), HIGH)

    def test_value_dependence_not_likely_is_concerns(self):
        self.assertEqual(rob2_domain_rating("missing_outcome_data", _s(**{
            "3.1": "n", "3.2": "pn", "3.3": "py", "3.4": "n"})), SOME)


class Domain4Test(unittest.TestCase):
    def test_blinded_assessor_is_low(self):
        self.assertEqual(rob2_domain_rating("measurement", _s(**{
            "4.1": "n", "4.2": "n", "4.3": "n"})), LOW)

    def test_inappropriate_method_is_high_reconstructed(self):
        self.assertEqual(rob2_domain_rating("measurement", _s(**{
            "4.1": "y"})), HIGH)

    def test_differential_ascertainment_is_concerns_reconstructed(self):
        self.assertEqual(rob2_domain_rating("measurement", _s(**{
            "4.1": "n", "4.2": "y"})), SOME)

    def test_aware_assessor_could_influence_is_high(self):
        self.assertEqual(rob2_domain_rating("measurement", _s(**{
            "4.1": "n", "4.2": "n", "4.3": "y", "4.4": "y"})), HIGH)

    def test_aware_assessor_could_not_influence_is_low(self):
        self.assertEqual(rob2_domain_rating("measurement", _s(**{
            "4.1": "n", "4.2": "n", "4.3": "y", "4.4": "n"})), LOW)

    def test_unclear_influence_stays_concerns(self):
        self.assertEqual(rob2_domain_rating("measurement", _s(**{
            "4.1": "n", "4.2": "n", "4.3": "ni"})), SOME)


class Domain5Test(unittest.TestCase):
    def test_prespecified_with_no_selection_is_low(self):
        self.assertEqual(
            rob2_domain_rating(
                "selection_reported_result",
                _s(**{"5.1": "y", "5.2": "n", "5.3": "n"})),
            LOW)

    def test_selected_measure_only_is_concerns(self):
        self.assertEqual(
            rob2_domain_rating(
                "selection_reported_result",
                _s(**{"5.1": "y", "5.2": "y", "5.3": "n"})),
            SOME)
        self.assertEqual(
            rob2_domain_rating(
                "selection_reported_result",
                _s(**{"5.1": "y", "5.2": "ni", "5.3": "n"})),
            SOME)

    def test_both_selections_is_high(self):
        self.assertEqual(
            rob2_domain_rating(
                "selection_reported_result",
                _s(**{"5.1": "y", "5.2": "y", "5.3": "y"})),
            HIGH)


class OverallTest(unittest.TestCase):
    def test_all_low_is_low(self):
        domains = {d: LOW for d in ROB2_DOMAIN_ORDER}
        self.assertEqual(overall_rob2(domains), LOW)

    def test_any_high_is_high(self):
        domains = {d: LOW for d in ROB2_DOMAIN_ORDER}
        domains["measurement"] = HIGH
        self.assertEqual(overall_rob2(domains), HIGH)

    def test_single_concern_is_some(self):
        domains = {d: LOW for d in ROB2_DOMAIN_ORDER}
        domains["randomisation"] = SOME
        self.assertEqual(overall_rob2(domains), SOME)

    def test_multiple_concerns_substantially_lower_confidence(self):
        domains = {d: SOME for d in ROB2_DOMAIN_ORDER}
        domains["randomisation"] = LOW
        domains["measurement"] = LOW
        self.assertEqual(overall_rob2(domains), HIGH)


class RegistryTest(unittest.TestCase):
    def test_question_registry_covers_22_signalling_questions(self):
        counts = {d: len(qs) for d, qs in ROB2_QUESTIONS.items()}
        self.assertEqual(counts, {
            "randomisation": 3, "deviations_assignment": 7,
            "missing_outcome_data": 4, "measurement": 5,
            "selection_reported_result": 3})
        self.assertEqual(sum(counts.values()), 22)

    def test_pass_summary_knows_missing_answers_as_ni(self):
        # No answers at all: the algorithm reads NI, which is HIGH in
        # domain 1 (unclear process + baseline unknown) and concerns
        # elsewhere - never low.
        summary = rob2_pass_summary({})
        self.assertEqual(summary["overall"], HIGH)


if __name__ == "__main__":
    unittest.main()
