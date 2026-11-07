"""Tests for the pooling engine: analytic anchors, coverage, determinism, locks.

The claim under test is not "the function returns a number": it is that the number
is the right one where the answer can be computed by hand, that its interval
actually covers the truth about 95 % of the time, and that the engine refuses
rather than invents when the material cannot support a pooled estimate.
"""

import math
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.meta.designs import classify_design, is_paired_design
from research_agent.meta.extraction import z_for_level
from research_agent.meta.pooling import (
    aggregate_design, build_analysis, egger, forest_table, leave_one_out, pool,
    standardize, subgroups, SCALE_G, SCALE_LOG, SCALE_Z,
    SCALE_RAW,
)


def _effect(est, se, label="Study", **extra):
    row = {"est": est, "se": se, "label": label}
    row.update(extra)
    return row


class TestScales(unittest.TestCase):
    def test_correlation_becomes_fisher_z(self):
        est, se, scale, reason = standardize(
            {"effect_type": "r", "effect": 0.5, "n": 100, "quote_start": 0}
        )
        self.assertEqual(scale, SCALE_Z)
        self.assertEqual(reason, "")
        self.assertAlmostEqual(est, math.atanh(0.5), places=10)
        self.assertAlmostEqual(se, 1.0 / math.sqrt(97), places=10)

    def test_r_without_n_cannot_be_standardised(self):
        _, _, _, reason = standardize({"effect_type": "r", "effect": 0.3, "quote_start": 0})
        self.assertIn("n > 3", reason)

    def test_ratio_is_pooled_on_the_log_scale(self):
        est, se, scale, reason = standardize({
            "effect_type": "or", "effect": 2.0, "quote_start": 0,
            "ci_low": 1.2, "ci_high": 3.3, "ci_level": 0.95,
        })
        self.assertEqual(scale, SCALE_LOG)
        self.assertEqual(reason, "")
        self.assertAlmostEqual(est, math.log(2.0), places=10)
        z = z_for_level(0.95)
        self.assertAlmostEqual(se, (math.log(3.3) - math.log(1.2)) / (2 * z), places=10)

    def test_heritability_stays_its_own_scale(self):
        _, _, scale, reason = standardize(
            {"effect_type": "heritability", "effect": 0.8, "se": 0.05, "quote_start": 0}
        )
        self.assertEqual(reason, "")
        self.assertIn("heritability", scale)

    def test_missing_precision_is_refused_with_a_reason(self):
        _, _, _, reason = standardize({"effect_type": "smd", "effect": 0.4, "quote_start": 0})
        self.assertIn("Standardfehler", reason)

    def test_mixed_scales_are_not_pooled_together(self):
        rows = [
            {"effect_type": "smd", "effect": 0.4, "se": 0.1, "outcome": "cognition", "quote_start": 0},
            {"effect_type": "r", "effect": 0.3, "se": 0.05, "outcome": "cognition",
             "n": 500, "quote_start": 0},
        ]
        analysis = build_analysis(rows)
        self.assertEqual(len(analysis["groups"]), 2,
                         "SMD and Fisher-z must not share a pooled estimate")
        for group in analysis["groups"].values():
            self.assertEqual(group["k"], 1)
            self.assertIsNone(group["pooled"])


class TestAnalyticAnchors(unittest.TestCase):
    def test_two_equal_variances_equal_their_mean(self):
        # Equal variances, different estimates: both models must return the
        # arithmetic mean, and the difference between the studies must show up as
        # heterogeneity instead of being averaged away.
        analysis = pool([_effect(0.2, 0.1, "A"), _effect(0.6, 0.1, "B")])
        self.assertAlmostEqual(analysis["fixed"], 0.4, places=10)
        self.assertAlmostEqual(analysis["pooled"], 0.4, places=10)
        self.assertGreater(analysis["tau2"], 0.0)

    def test_zero_heterogeneity_makes_random_effects_equal_fixed_effect(self):
        # Q = 0 with identical estimates: tau^2 stays at zero, so the random
        # effects weights are the fixed effect weights.
        rows = [_effect(0.5, 0.1, "A"), _effect(0.5, 0.2, "B")]
        analysis = pool(rows)
        self.assertAlmostEqual(analysis["tau2"], 0.0, places=12)
        self.assertAlmostEqual(analysis["pooled"], analysis["fixed"], places=10)
        self.assertAlmostEqual(analysis["i2"], 0.0, places=6)

    def test_sign_flip_flips_the_pooled_effect_and_keeps_the_interval(self):
        rows = [_effect(0.2, 0.1, "A"), _effect(0.5, 0.1, "B")]
        flipped = [_effect(-0.2, 0.1, "A"), _effect(-0.5, 0.1, "B")]
        first, second = pool(rows), pool(flipped)
        self.assertAlmostEqual(first["pooled"], -second["pooled"], places=10)
        self.assertAlmostEqual(first["ci_high"] - first["ci_low"],
                               second["ci_high"] - second["ci_low"], places=10)

    def test_heterogeneity_is_reported_not_hidden(self):
        rows = [_effect(-0.2, 0.1, "A"), _effect(0.8, 0.1, "B"),
                _effect(1.1, 0.1, "C")]
        analysis = pool(rows)
        self.assertGreater(analysis["tau2"], 0.05)
        self.assertGreater(analysis["i2"], 70)
        self.assertIsNotNone(analysis["pi_low"])
        # A prediction interval is wider than the confidence interval.
        self.assertLess(analysis["pi_low"], analysis["ci_low"])
        self.assertGreater(analysis["pi_high"], analysis["ci_high"])


class TestCoverage(unittest.TestCase):
    """The 95 % interval must cover the true effect about 95 % of the time."""

    def test_hksj_interval_covers_the_truth(self):
        random.seed(20261027)
        true_effect, tau, se, k, reps = 0.30, 0.25, 0.12, 8, 400
        covered = 0
        for _ in range(reps):
            rows = []
            for index in range(k):
                study = random.gauss(true_effect, math.sqrt(tau ** 2 + se ** 2))
                rows.append(_effect(study, se, f"S{index}"))
            analysis = pool(rows, method="hksj")
            if analysis["ci_low"] <= true_effect <= analysis["ci_high"]:
                covered += 1
        coverage = covered / reps
        # The interval is a statistic: 0.94-0.96 expected, 0.90 tolerated for the
        # small k. Anything below that means the interval is too narrow.
        self.assertGreater(coverage, 0.90, f"HKSJ coverage too low: {coverage:.3f}")
        self.assertLess(coverage, 0.995, f"HKSJ coverage implausibly high: {coverage:.3f}")

    def test_tau2_estimate_recovers_the_true_value(self):
        random.seed(7)
        true_effect, tau, se, k, reps = 0.0, 0.30, 0.10, 20, 300
        estimates = []
        for _ in range(reps):
            rows = [
                _effect(random.gauss(true_effect, math.sqrt(tau ** 2 + se ** 2)),
                        se, f"S{i}")
                for i in range(k)
            ]
            estimates.append(pool(rows)["tau2_reml"])
        mean_estimate = sum(estimates) / len(estimates)
        self.assertLess(abs(mean_estimate - tau ** 2), 0.05,
                        f"REML tau^2 off: {mean_estimate:.3f} vs {tau ** 2:.3f}")


class TestLocks(unittest.TestCase):
    def test_no_effects_means_no_pooled_value(self):
        analysis = pool([])
        self.assertIsNone(analysis["pooled"])
        self.assertIn("keine poolbaren", analysis["note"])

    def test_one_study_is_not_pooled(self):
        analysis = pool([_effect(0.4, 0.1, "A")])
        self.assertIsNone(analysis["pooled"])
        self.assertIn("kein Pooling", analysis["note"])
        self.assertIsNotNone(analysis["fixed"])

    def test_rows_without_precision_are_excluded_and_counted(self):
        rows = [
            {"effect_type": "smd", "effect": 0.4, "se": 0.1, "outcome": "cog", "quote_start": 0},
            {"effect_type": "smd", "effect": 0.9, "outcome": "cog", "quote_start": 0},  # no precision
        ]
        analysis = build_analysis(rows)
        group = analysis["groups"]["cog [hedges_g]"]
        self.assertEqual(group["k"], 1)
        self.assertEqual(len(analysis["excluded"]), 1)
        self.assertIn("Standardfehler", analysis["excluded"][0]["reason"])

    def test_disputed_rows_are_never_pooled(self):
        # Two readings of the same sentence that disagree are not a number:
        # averaging them would hide the disagreement the double pass found.
        rows = [
            {"effect_type": "smd", "effect": 0.4, "se": 0.1, "outcome": "cog", "quote_start": 0},
            {"effect_type": "smd", "effect": 0.9, "se": 0.1, "outcome": "cog",
             "disputed": 1},
        ]
        analysis = build_analysis(rows)
        self.assertEqual(analysis["groups"]["cog [hedges_g]"]["k"], 1)
        self.assertEqual(analysis["excluded"][0]["reason"],
                         "Doppel-Extraktion widersprüchlich")

    def test_rejected_rows_are_excluded_with_their_reason(self):
        rows = [
            {"effect_type": "smd", "effect": 0.4, "se": 0.1, "outcome": "cog", "quote_start": 0},
            {"effect_type": "smd", "effect": 1.9, "se": 0.1, "outcome": "cog",
             "rejection_reason": "KI enthält den Punktschätzer nicht"},
        ]
        analysis = build_analysis(rows)
        self.assertEqual(analysis["groups"]["cog [hedges_g]"]["k"], 1)
        self.assertIn("Plausibilitätsgate", analysis["excluded"][0]["reason"])
        self.assertIn("Punktschätzer", analysis["excluded"][0]["reason"])

    def test_the_same_cohort_under_two_urls_counts_once(self):
        # Two rows of one cohort would count the same people twice and narrow the
        # interval without adding information.
        rows = [
            {"effect_type": "smd", "effect": 0.4, "se": 0.2, "outcome": "cog",
             "doi": "10.1/one", "label": "Paper (A)", "quote_start": 0},
            {"effect_type": "smd", "effect": 0.42, "se": 0.1, "outcome": "cog",
             "doi": "10.1/one", "label": "Paper (B)", "quote_start": 0},
        ]
        analysis = build_analysis(rows)
        group = analysis["groups"]["cog [hedges_g]"]
        self.assertEqual(group["k"], 1)
        # The more precise reading is the one that stays.
        self.assertAlmostEqual(group["rows"][0]["est"], 0.42, places=6)
        self.assertIn("dieselbe Studie", analysis["excluded"][0]["reason"])
        self.assertIn("10.1/one", analysis["excluded"][0]["reason"])

    def test_rows_without_a_doi_are_not_merged_by_guesswork(self):
        rows = [
            {"effect_type": "smd", "effect": 0.4, "se": 0.1, "outcome": "cog", "quote_start": 0},
            {"effect_type": "smd", "effect": 0.42, "se": 0.1, "outcome": "cog", "quote_start": 0},
        ]
        analysis = build_analysis(rows)
        self.assertEqual(analysis["groups"]["cog [hedges_g]"]["k"], 2)
        self.assertEqual(analysis["excluded"], [])

    def test_determinism(self):
        rows = [_effect(0.2, 0.1, "A"), _effect(0.5, 0.15, "B"),
                _effect(0.35, 0.2, "C")]
        first, second = pool(rows), pool(rows)
        self.assertEqual(first["pooled"], second["pooled"])
        self.assertEqual(first["ci_low"], second["ci_low"])
        self.assertEqual(first["tau2"], second["tau2"])


class QuoteContractTest(unittest.TestCase):
    """Phase 8: a number lives only as long as its verbatim reading does.

    The extractor stores quote_start = -1 for quotes that never verified;
    such a row keeps its data but is never pooled (one reason, visible in
    the report), and the POOLABLE filter agrees.
    """

    def test_unverified_span_is_a_pooling_rejection(self):
        est, se, scale, reason = standardize(_row(quote_start=-1))
        self.assertIsNone(est)
        self.assertIsNone(se)
        self.assertEqual(reason, "Kein verifizierter Beleg (Zitat-Span fehlt)")

    def test_span_zero_is_a_valid_start(self):
        est, se, scale, reason = standardize(_row(quote_start=0))
        self.assertEqual(est, -0.4)
        self.assertEqual(reason, "")

    def test_poolable_filter_includes_the_quote_term(self):
        from research_agent.database import Database
        db = Database(":memory:")
        self.assertIn("quote_start >= 0", db.POOLABLE)


class TestSubgroupsAndBias(unittest.TestCase):
    def test_two_clearly_different_subgroups_raise_q_between(self):
        """Auftrag v2 §5.2: die k-Gate-Schwelle (3) ist hier gerade erfüllt."""
        rows = [
            _effect(-0.6, 0.1, f"A{index}", design="twin") for index in range(3)
        ] + [
            _effect(0.8, 0.1, f"B{index}", design="cohort") for index in range(3)
        ]
        result = subgroups(rows, "design")
        self.assertEqual(len(result["groups"]), 2)
        self.assertGreater(result["q_between"], 10)
        self.assertLess(result["p"], 0.01)
        self.assertEqual(result["below_gate"], {})

    def test_single_study_group_is_shown_but_never_interpreted(self):
        """k-Gate §5.2: eine k=1-Gruppe bleibt sichtbar, trägt aber
        keine Moderatoren-Aussage - Q_between entfällt."""
        rows = [
            _effect(-0.6, 0.1, f"A{index}", design="twin") for index in range(3)
        ]
        rows.append(_effect(2.0, 0.05, "X", design="cohort"))
        result = subgroups(rows, "design")
        self.assertEqual(result.get("below_gate"), {"cohort": 1})
        self.assertIn("twin", result.get("groups", {}))
        self.assertIn("cohort", result.get("groups", {}))
        self.assertIsNone(result.get("q_between"))

    def test_gate_blocked_group_does_not_distort_q_between(self):
        """k=2-Gruppe mit einem Heiß-Effekt verfälscht die Q-Aussage nicht."""
        base = [
            _effect(-0.6, 0.1, f"A{index}", design="twin") for index in range(3)
        ] + [
            _effect(0.8, 0.1, f"B{index}", design="cohort") for index in range(3)
        ]
        without_small = subgroups(base, "design")
        hot = base + [_effect(3.0, 0.05, f"C{index}", design="case-control")
                      for index in range(2)]
        with_small = subgroups(hot, "design")
        self.assertEqual(with_small.get("below_gate"), {"case-control": 2})
        self.assertAlmostEqual(
            with_small.get("q_between"), without_small.get("q_between"), places=10)

    def test_leave_one_out_reports_the_range(self):
        rows = [_effect(0.2, 0.05, "A"), _effect(0.25, 0.05, "B"),
                _effect(0.3, 0.05, "C"), _effect(1.4, 0.6, "outlier")]
        result = leave_one_out(rows)
        self.assertTrue(result["available"])
        self.assertEqual(len(result["entries"]), 4)
        low, high = result["range"]
        self.assertLess(low, high)
        without_outlier = min(e["estimate"] for e in result["entries"])
        self.assertNotAlmostEqual(without_outlier, result["estimate"], places=6)

    def test_egger_intercept_sees_an_asymmetric_funnel(self):
        """Small-study bias shows up as a non-zero intercept, not as a slope.

        Asymmetric: the observed effect grows as the study shrinks
        (effect = 0.2 + 0.3 * se). Symmetric: the same effect at every precision,
        with a little noise so the residuals are not exactly zero.
        """
        ses = [0.05, 0.10, 0.20, 0.30, 0.50]
        asymmetric = [_effect(0.2 + 0.3 * se, se, f"small{index}")
                      for index, se in enumerate(ses)]
        symmetric = [_effect(0.30 + (0.01 if index % 2 else -0.01), se, f"even{index}")
                     for index, se in enumerate(ses)]

        bad, good = egger(asymmetric), egger(symmetric)

        self.assertTrue(bad["available"])
        self.assertLess(bad["p"], 0.05)
        self.assertGreater(abs(bad["intercept"]), abs(good["intercept"]))
        self.assertGreater(good["p"], 0.05)

    def test_egger_needs_three_studies(self):
        result = egger([_effect(0.2, 0.1), _effect(0.3, 0.2)])
        self.assertFalse(result["available"])
        self.assertIn("k < 3", result["note"])


class TestForestTable(unittest.TestCase):
    def test_table_carries_every_study_and_the_pooled_rows(self):
        analysis = pool([_effect(0.2, 0.1, "Studie A"), _effect(0.6, 0.1, "Studie B"),
                         _effect(0.45, 0.12, "Studie C")])
        table = "\n".join(forest_table(analysis))
        self.assertIn("Studie A", table)
        self.assertIn("Studie B", table)
        self.assertIn("Random Effects", table)
        self.assertIn("Prediction Interval", table)
        analysis = pool([_effect(0.2, 0.1, "Studie A"), _effect(0.6, 0.1, "Studie B"),
                         _effect(0.45, 0.12, "Studie C")])
        self.assertIn(f"{analysis['pooled']:.3f}", table)


class DesignCategoryTest(unittest.TestCase):
    """Auftrag v2 §2.2: die Design-Kategorie entscheidet, zu welcher
    Stichproben-Semantik eine Stored-Präzision gehört - crossover/Mess-
    wiederholung ist die paarige Familie, nicht independent groups."""

    def test_classification_is_deterministic_and_specific(self):
        self.assertEqual(classify_design("randomised, double-masked, "
                                         "placebo-controlled crossover"),
                         "crossover_rct")
        self.assertEqual(classify_design("within-subjects design"),
                         "crossover_rct")
        self.assertEqual(classify_design("repeated measures (3 visits)"),
                         "crossover_rct")
        self.assertEqual(classify_design("cluster randomized trial"),
                         "cluster_rct")
        self.assertEqual(classify_design("2x2 factorial randomized trial"),
                         "factorial")
        self.assertEqual(classify_design("three-arm randomized"), "multi_arm")
        self.assertEqual(classify_design("quasi-experimental with "
                                         "pretest-posttest"),
                         "quasi_experimental")
        self.assertEqual(classify_design("randomized controlled trial"),
                         "parallel_rct")
        self.assertEqual(classify_design("longitudinal cohort"),
                         "observational")
        self.assertEqual(classify_design(""), "")

    def test_crossover_outranks_the_generic_rct_label(self):
        # Ein 'randomized crossover' gehört in die paarige Familie,
        # obwohl im Label auch "randomized" steht - Reihenfolge zählt.
        self.assertEqual(
            classify_design("randomized controlled trial (crossover)"),
            "crossover_rct")
        self.assertTrue(is_paired_design(
            "randomized controlled trial (crossover)"))
        self.assertFalse(is_paired_design("randomized controlled trial"))

    def test_build_analysis_discloses_the_design_mix(self):
        """Der Pool sagt, aus welcher Design-Mischung er besteht -#/.
        Handles a paired and a parallel row in one group."""
        x = _row(source_id="s1", effect=-0.4, se=0.1)
        x["design"] = "randomised controlled trial (crossover)"
        y = _row(source_id="s2", effect=-0.5, se=0.1)
        y["design"] = "randomized controlled trial"
        analysis = build_analysis([x, y])
        group = analysis["groups"]["depressive symptoms [hedges_g]"]
        self.assertEqual(group["design_mix"],
                         {"crossover_rct": 1, "parallel_rct": 1})
        self.assertEqual(group["paired_rows"], 1)
        self.assertEqual(group["k"], 2)  # Mischpool bleibt ein Pool

    def test_pooled_rows_carry_their_category(self):
        x = _row(source_id="s1")
        x["design"] = "cross-over trial"
        analysis = build_analysis([x])
        group = analysis["groups"]["depressive symptoms [hedges_g]"]
        self.assertEqual(group["rows"][0].get("design_category"),
                         "crossover_rct")


def _row(**overrides):
    """A stored effect row as the database hands it over."""
    row = {
        "id": "e1", "source_id": "s1", "title": "Study", "doi": "",
        "outcome": "depressive symptoms", "effect_type": "smd",
        "effect": -0.4, "se": 0.1, "disputed": 0, "rejection_reason": "",
        "design": "randomized controlled trial",
        # Phase 8 contract: the fixture stores a verified span, exactly as
        # the extractor does for every poolable row.
        "quote_start": 0,
    }
    row.update(overrides)
    return row


class TestAggregateDesigns(unittest.TestCase):
    """A review is not a study - its number already contains other studies."""

    def test_review_designs_are_recognised(self):
        for design in ("Network Meta-Analysis", "meta-analysis of randomized trials",
                       "metaanalysis", "meta analysis", "systematic review",
                       "umbrella review of meta-analyses", "pooled analysis of cohorts",
                       "Randomized controlled trial (meta-analysis of 37 RCTs)"):
            self.assertTrue(aggregate_design(design), design)

    def test_primary_designs_pass(self):
        for design in ("randomized controlled trial", "cluster-randomized trial",
                       "prospective cohort", "longitudinal panel study",
                       "cross-over trial"):
            self.assertEqual(aggregate_design(design), "", design)

    def test_an_unknown_design_is_not_dropped(self):
        # Silence is a gap in the extraction, not a finding about the paper.
        self.assertEqual(aggregate_design(""), "")
        self.assertEqual(aggregate_design(None), "")
        self.assertEqual(aggregate_design("unclear"), "")

    def test_a_review_row_is_refused_with_its_reason(self):
        est, se, scale, reason = standardize(
            _row(design="Network Meta-Analysis", effect=-2.02, se=0.42)
        )
        self.assertIsNone(est)
        self.assertIsNone(se)
        self.assertEqual(scale, "")
        self.assertIn("Übersichtsarbeit", reason)
        self.assertIn("keine Primärstudie", reason)

    def test_reviews_do_not_enter_the_pool(self):
        analysis = build_analysis([
            _row(source_id="s1", effect=-0.30),
            _row(source_id="s2", effect=-0.55),
            _row(source_id="s3", design="Network Meta-Analysis", effect=-2.02),
        ])
        group = analysis["groups"]["depressive symptoms [hedges_g]"]
        self.assertEqual(group["k"], 2)
        self.assertAlmostEqual(group["pooled"], -0.425, places=3)
        self.assertEqual(len(analysis["excluded"]), 1)
        self.assertIn("Übersichtsarbeit", analysis["excluded"][0]["reason"])

    def test_a_review_alone_leaves_nothing_to_pool(self):
        analysis = build_analysis([
            _row(source_id="s1", design="meta-analysis of randomized controlled trials")
        ])
        self.assertNotIn("depressive symptoms [hedges_g]", analysis["groups"])
        self.assertEqual(analysis["usable"], 0)
        self.assertEqual(len(analysis["excluded"]), 1)

class TransformationReferenceTest(unittest.TestCase):
    """Order §7.1: every transformation proves itself with reference values."""

    def test_fisher_z_reference(self):
        est, se, scale, _ = standardize(_row(effect_type="r", effect=0.5, n=40))
        self.assertEqual(scale, SCALE_Z)
        self.assertAlmostEqual(est, 0.5493061443, places=6)   # atanh(0.5)
        self.assertAlmostEqual(se, 1.0 / math.sqrt(37.0), places=6)

    def test_log_ratio_from_ci_on_reported_level(self):
        # OR 1.30 (95% CI 1.10-1.50): se = (ln 1.5 - ln 1.1) / (2*z95)
        est, se, scale, _ = standardize(_row(
            effect_type="or", effect=1.30, ci_low=1.10, ci_high=1.50, ci_level=0.95))
        self.assertEqual(scale, SCALE_LOG)
        self.assertAlmostEqual(est, math.log(1.30), places=6)
        self.assertAlmostEqual(se, (math.log(1.5) - math.log(1.1)) /
                               (2 * 1.959963984540054), places=6)

    def test_log_ratio_is_level_sensitive(self):
        # same interval, reported level 0.90 -> wider SE than at 0.95
        _, se90, _, _ = standardize(_row(
            effect_type="or", effect=1.30, ci_low=1.10, ci_high=1.50, ci_level=0.90))
        _, se95, _, _ = standardize(_row(
            effect_type="or", effect=1.30, ci_low=1.10, ci_high=1.50, ci_level=0.95))
        self.assertGreater(se90, se95)

    def test_ratio_zero_refused(self):
        est, se, scale, _ = standardize(_row(
            effect_type="hr", effect=0.0, ci_low=0.1, ci_high=0.9, ci_level=0.95))
        self.assertIsNone(est)
        self.assertEqual(scale, "")

    def test_smd_and_raw_pass_through(self):
        est, se, scale, _ = standardize(_row(effect_type="smd", effect=-0.4, se=0.1))
        self.assertEqual((est, se, scale), (-0.4, 0.1, SCALE_G))
        est, se, scale, _ = standardize(_row(effect_type="beta", effect=1.2, se=0.05))
        # raw pools stay per-effect-type ('heritability' pools against the
        # same proportion kind only)
        self.assertEqual(scale, "raw:beta")


class PoolingConditionsTest(unittest.TestCase):
    """pooling/2: adjustment and timepoint never silently merge (§7.1)."""

    def test_mixed_adjustment_splits_pools(self):
        a = _row(source_id="s1", effect=-0.4, se=0.1)
        a["adjusted"] = 1
        b = _row(source_id="s2", effect=-0.5, se=0.1)
        b["adjusted"] = 0
        analysis = build_analysis([a, b])
        keys = list(analysis["groups"])
        self.assertEqual(len(keys), 2)
        self.assertTrue(any("Adjustierung: adjusted" in k for k in keys))
        self.assertTrue(any("Adjustierung: unadjusted" in k for k in keys))
        self.assertTrue(all(g["pool_version"] == "pooling/2"
                            for g in analysis["groups"].values()))

    def test_unknown_adjustment_stays_in_its_own_pool(self):
        a = _row(source_id="s1", effect=-0.4, se=0.1)
        a["adjusted"] = 1
        res = build_analysis([a, _row(source_id="s2", effect=-0.5, se=0.1)])
        keys = list(res["groups"])
        self.assertEqual(len(keys), 2)
        self.assertTrue(any("Adjustierung: unknown" in k for k in keys))

    def test_timepoint_mixture_splits(self):
        t1 = _row(source_id="s1", effect=-0.4, se=0.1)
        t1["time_point"] = "12-month follow-up"
        t2 = _row(source_id="s2", effect=-0.5, se=0.1)
        t2["time_point"] = "6-month follow-up"
        analysis = build_analysis([t1, t2])
        keys = list(analysis["groups"])
        self.assertEqual(len(keys), 2)
        self.assertTrue(any("| T: 12-month" in k for k in keys))

    def test_study_id_collapse_with_min_se_rule(self):
        a = _row(source_id="s1", doi="", effect=-0.4, se=0.14)
        a["study_id"] = "coh-A"
        b = _row(source_id="s2", doi="", effect=-0.40, se=0.08)
        b["study_id"] = "coh-A"
        analysis = build_analysis([a, b])
        group = analysis["groups"]["depressive symptoms [hedges_g]"]
        self.assertEqual(group["k"], 1)   # one cohort, one estimate
        self.assertEqual(group["rows"][0]["se"], 0.08)  # the more precise one


if __name__ == "__main__":
    unittest.main()


class RVETest(unittest.TestCase):
    """CR0 sandwich variance with M/(M-1) correction over real clusters."""

    def _rows(self):
        # Four rows, two cohorts of two (same study_id). se = 1 -> w = 1.
        # theta = 11/4 = 2.75; D_1 = (1-2.75)+(2-2.75) = -2.5,
        # D_2 = (3-2.75)+(5-2.75) = 2.5; Var = (12.5/16)*2 = 1.5625;
        # se = 1.25; t(0.975, 1) = 12.706 -> ci +/- 15.8828...
        bibli = [
            {"est": 1.0, "se": 1.0, "study_id": "cohort-a", "source_id": "s1"},
            {"est": 2.0, "se": 1.0, "study_id": "cohort-a", "source_id": "s1"},
            {"est": 3.0, "se": 1.0, "study_id": "cohort-b", "source_id": "s2"},
            {"est": 5.0, "se": 1.0, "study_id": "cohort-b", "source_id": "s2"},
        ]
        return bibli

    def test_reference_case_two_clusters_of_two(self):
        from research_agent.meta.pooling import pool_rve
        result = pool_rve(self._rows())
        self.assertTrue(result["available"])
        self.assertAlmostEqual(result["pooled"], 2.75, places=10)
        self.assertAlmostEqual(result["se"], 1.25, places=10)
        self.assertAlmostEqual(result["M"], 2)
        self.assertEqual(result["df"], 1)
        from research_agent.meta.pooling import _t_quantile
        expected_half = _t_quantile(0.975, 1) * 1.25
        self.assertAlmostEqual(result["ci_low"], 2.75 - expected_half, places=6)
        self.assertAlmostEqual(result["ci_high"], 2.75 + expected_half, places=6)
        # The interval is enormous on purpose: M = 2 clusters means df = 1.
        self.assertGreater(result["ci_high"] - result["ci_low"], 10.0)

    def test_cluster_key_falls_back_to_source(self):
        from research_agent.meta.pooling import pool_rve
        rows = [
            {"est": 1.0, "se": 1.0, "source_id": "s1"},   # no study_id
            {"est": 2.0, "se": 1.0, "source_id": "s1"},   # same paper: arms
            {"est": 4.0, "se": 1.0, "source_id": "s2"},
        ]
        result = pool_rve(rows)
        # clusters: s1 (2 rows), s2 (1 row) -> M = 2, theta = (1+2+4)/3
        self.assertTrue(result["available"])
        self.assertEqual(result["M"], 2)
        self.assertAlmostEqual(result["pooled"], 7.0 / 3.0, places=10)

    def test_single_cluster_refuses(self):
        from research_agent.meta.pooling import pool_rve
        rows = [
            {"est": 1.0, "se": 1.0, "study_id": "one", "source_id": "s1"},
            {"est": 2.0, "se": 1.0, "study_id": "one", "source_id": "s2"},
        ]
        result = pool_rve(rows)
        self.assertFalse(result["available"])
        self.assertIn("mindestens 2", result["reason"])

    def test_rows_without_identity_are_own_clusters(self):
        from research_agent.meta.pooling import pool_rve
        rows = [
            {"est": 1.0, "se": 1.0}, {"est": 2.0, "se": 1.0},
            {"est": 3.0, "se": 1.0},
        ]
        result = pool_rve(rows)
        # three unrelated rows -> M = 3, independent seeds
        self.assertTrue(result["available"])
        self.assertEqual(result["M"], 3)

    def test_standardize_carries_rve_block(self):
        from research_agent.meta.pooling import build_analysis
        rows = [
            self._db_row("s1", 1.0, "cohort-a"),
            self._db_row("s1", 2.0, "cohort-a"),
            self._db_row("s2", 3.0, "cohort-b"),
        ]
        result = build_analysis(rows)
        self.assertTrue(result.get("groups"))
        # The Min-SE collapse still documents its merge; RVE is the view
        # that keeps every dependent row (they coexist on purpose).
        self.assertEqual(len(result.get("excluded")), 1)
        first = next(iter(result["groups"].values()))
        rve = first.get("rve")
        self.assertIsNotNone(rve)
        # 3 rows, 2 study-id clusters -> dependent row survives for RVE
        self.assertEqual(rve["M"], 2)
        self.assertTrue(rve["available"])

    def _db_row(self, source_id, est, study_id=None):
        # minimal db-shaped row that build_analysis accepts (quote contract).
        return {
            "outcome": "cognition", "effect_type": "smd", "effect": est,
            "se": 1.0, "ci_low": None, "ci_high": None, "n": 40,
            "design": "rct", "direction": "higher cognition",
            "quote_start": 0, "quote_text": "x",
            "disputed": 0, "rejected": 0, "source_id": source_id,
            "study_id": study_id or "",
        }


class TestOutcomeGrouping(unittest.TestCase):
    """Normalisierte Outcome-Namen teilen eine Gruppe, Einheiten nicht."""

    @staticmethod
    def _row(source_id, outcome, effect):
        return {
            "source_id": source_id, "study_id": source_id, "outcome": outcome,
            "effect_type": "smd", "effect": effect, "se": 0.1, "adjusted": 0,
            "quote_start": 0,
        }

    def test_two_studies_with_different_labels_form_one_group(self):
        result = build_analysis([
            self._row("s1", "Sleep onset latency, min", -0.22),
            self._row("s2", "Sleep latency (min)", -0.18),
        ])
        self.assertEqual(len(result["groups"]), 1, list(result["groups"]))
        analysis = next(iter(result["groups"].values()))
        self.assertEqual(analysis["k"], 2)
        self.assertEqual(analysis["outcome"], "sleep onset latency min")

    def test_units_still_split_the_group(self):
        result = build_analysis([
            self._row("s1", "% Stage N1", -0.05),
            self._row("s2", "Stage N1 time (min)", -6.07),
        ])
        self.assertEqual(len(result["groups"]), 2, list(result["groups"]))
