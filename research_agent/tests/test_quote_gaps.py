"""Tests for the quote-gap check.

The property under test: a quote that names two confidence intervals and
yields one extracted row must be reported as a gap - and a complete reading
must not be. The fixtures are the real MENDS sentence and the three rows the
model actually returned in E3a/E3b/E3c, so the check is anchored on measured
output, not on invented text.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.meta.quote_gaps import (
    audit_quote, audit_rows, find_intervals, summarize,
)

MENDS = (
    "A reduction in SOL, adjusted for baseline, was seen for melatonin compared "
    "with placebo when measured by sleep diaries (-37.49 minutes, 95% CI -55.27 "
    "to -19.71 minutes; p<0.0001) and actigraphy (-45.34 minutes, 95% CI -68.75 "
    "to -21.93 minutes; p=0.0003)."
)


def _row(effect, ci_low, ci_high, comparison="", rejection=""):
    return {
        "outcome": "Sleep Onset Latency (SOL)", "comparison": comparison,
        "effect_type": "mean_diff", "effect": effect, "se": 10.0,
        "ci_low": ci_low, "ci_high": ci_high, "n": None,
        "quote": MENDS, "rejection_reason": rejection,
    }


DIARY = _row(-37.49, -55.27, -19.71, "sleep diaries")
ACTIGRAPHY = _row(-45.34, -68.75, -21.93, "Melatonin vs Placebo (Actigraphy)")


class TestFindIntervals(unittest.TestCase):
    def test_mends_sentence_names_two_intervals_with_their_points(self):
        intervals = find_intervals(MENDS)
        self.assertEqual(len(intervals), 2)
        self.assertAlmostEqual(intervals[0].low, -55.27)
        self.assertAlmostEqual(intervals[0].high, -19.71)
        self.assertAlmostEqual(intervals[0].point, -37.49)
        self.assertAlmostEqual(intervals[1].low, -68.75)
        self.assertAlmostEqual(intervals[1].high, -21.93)
        self.assertAlmostEqual(intervals[1].point, -45.34)

    def test_bracketed_interval_is_found(self):
        intervals = find_intervals("SOL fell 12.4 min [-18.9, -5.9].")
        self.assertEqual(len(intervals), 1)
        self.assertAlmostEqual(intervals[0].low, -18.9)
        self.assertAlmostEqual(intervals[0].high, -5.9)

    def test_nested_ci_bracket_is_found(self):
        # E3a's actual quote: the CI sits inside a square bracket.
        quote = ("The difference in TST was 22.43 minutes [95% confidence "
                 "interval (CI) 0.52 to 44.34 minutes; p=0.04] measured using "
                 "sleep diaries.")
        intervals = find_intervals(quote)
        self.assertEqual(len(intervals), 1)
        self.assertAlmostEqual(intervals[0].low, 0.52)
        self.assertAlmostEqual(intervals[0].high, 44.34)
        self.assertIsNone(intervals[0].point)
        report = audit_quote(quote, [{"effect": 22.43, "ci_low": 0.52,
                                      "ci_high": 44.34}])
        self.assertEqual(report.status, "ok")

    def test_p_value_and_spread_brackets_are_not_intervals(self):
        self.assertEqual(find_intervals("The effect was significant (p<0.0001)."), [])
        self.assertEqual(find_intervals("SOL was 10.0 (2.0) minutes."), [])
        self.assertEqual(find_intervals("SOL was 10.0 (SD 2.0)."), [])

    def test_study_size_is_not_an_interval(self):
        self.assertEqual(find_intervals("(n = 20, n = 30)"), [])

    def test_unicode_minus_and_decimal_comma_are_accepted(self):
        intervals = find_intervals("SOL sank (\u221237,49; 95% CI \u221255,27 "
                                   "to \u221219,71).")
        self.assertEqual(len(intervals), 1)
        self.assertAlmostEqual(intervals[0].low, -55.27)
        self.assertAlmostEqual(intervals[0].high, -19.71)


class TestAudit(unittest.TestCase):
    def test_one_of_two_intervals_is_a_gap(self):
        report = audit_quote(MENDS, [DIARY])
        self.assertEqual(report.status, "luecke")
        self.assertTrue(report.is_gap)
        self.assertEqual(len(report.missing), 1)
        self.assertAlmostEqual(report.missing[0].low, -68.75)
        self.assertIn("-68.75", report.message)

    def test_the_other_single_row_is_a_gap_too(self):
        # E3b returned actigraphy only: the gap does not depend on the choice.
        report = audit_quote(MENDS, [ACTIGRAPHY])
        self.assertEqual(report.status, "luecke")
        self.assertAlmostEqual(report.missing[0].low, -55.27)

    def test_two_rows_are_complete(self):
        report = audit_quote(MENDS, [DIARY, ACTIGRAPHY])
        self.assertEqual(report.status, "ok")
        self.assertEqual(report.missing, ())
        self.assertEqual(report.matched, 2)

    def test_no_rows_at_all_is_a_gap(self):
        report = audit_quote(MENDS, [])
        self.assertEqual(report.status, "keine_zeile")
        self.assertTrue(report.is_gap)

    def test_single_interval_with_one_row_is_not_a_gap(self):
        # E3a's TST reading: one interval, one row.
        quote = ("Total sleep time increased by 22.43 minutes (95% CI 0.52 to "
                 "44.34; p=0.04).")
        row = {"effect": 22.43, "ci_low": 0.52, "ci_high": 44.34, "quote": quote}
        report = audit_quote(quote, [row])
        self.assertEqual(report.status, "ok")

    def test_a_rejected_row_does_not_close_a_gap(self):
        report = audit_quote(MENDS, [ACTIGRAPHY, dict(DIARY, rejection_reason="x")])
        self.assertEqual(report.status, "luecke")
        self.assertEqual(report.rejected, 1)

    def test_quote_without_interval_is_not_counted_as_gap(self):
        report = audit_quote("Melatonin reduced SOL in both arms.", [])
        self.assertEqual(report.status, "nicht_pruefbar")
        self.assertFalse(report.is_gap)

    def test_rounding_tolerance_is_honoured(self):
        row = _row(-37.4901, -55.2702, -19.7098)
        report = audit_quote(MENDS, [row, ACTIGRAPHY])
        self.assertEqual(report.status, "ok")


class TestAuditRows(unittest.TestCase):
    def test_rows_are_grouped_by_their_quote(self):
        other = ("SOL was 10.0 (2.0) minutes in the diary arm (95% CI 8.1 to "
                 "11.9).")
        rows = [DIARY, ACTIGRAPHY,
                {"effect": 10.0, "ci_low": 8.1, "ci_high": 11.9, "quote": other}]
        reports = audit_rows(rows)
        self.assertEqual(len(reports), 2)
        self.assertEqual([r.status for r in reports], ["ok", "ok"])

    def test_summary_counts_the_gap(self):
        counts = summarize(audit_rows([DIARY]))
        self.assertEqual(counts["quotes"], 1)
        self.assertEqual(counts["luecken"], 1)
        self.assertEqual(counts["fehlende_intervalle"], 1)
        self.assertEqual(counts["zeilen"], 1)

    def test_rows_without_quote_are_reported_as_uncheckable(self):
        counts = summarize(audit_rows([{"effect": 1.0, "quote": ""}]))
        self.assertEqual(counts["nicht_pruefbar"], 1)
        self.assertEqual(counts["luecken"], 0)


if __name__ == "__main__":
    unittest.main()
