"""Phase 5: instrument routing, ROBINS-I/AMSTAR-2 semantics, storage field.

The design field alone selects the instrument (machine-decided, not guessed).
ROBINS-I vocabulary collapses deterministically onto the report scale, AMSTAR 2
overall ratings are fixed rules, and every rating without a verbatim quote is
no_information - the blanket rule from the 31.10.2026 decision.
"""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.risk_of_bias import (
    AMSTAR2_ITEMS, domains_for_design, instrument_for_design,
    overall_amstar2, overall_rating,
)


def _meta_lines(db):
    from research_agent.report import _meta_section
    lines: list = []
    _meta_section(lines.append, db, "Thema")
    return lines


class InstrumentMappingTest(unittest.TestCase):
    """The design field alone selects the instrument - not a model guess."""

    def test_design_mapping(self):
        self.assertEqual(instrument_for_design("rct"), "rob2")
        self.assertEqual(instrument_for_design("Randomized"), "rob2")
        self.assertEqual(instrument_for_design(""), "robins_i")
        self.assertEqual(instrument_for_design("cohort"), "robins_i")
        self.assertEqual(
            instrument_for_design("meta-analysis of randomized trials"),
            "amstar2")
        self.assertEqual(instrument_for_design("systematic review"),
                         "amstar2")
        self.assertEqual(instrument_for_design(
            "umbrella review"), "amstar2")

    def test_robins_i_vocabulary_in_overall(self):
        # critical/serious dominate like `high`, moderate reads as concerns.
        self.assertEqual(
            overall_rating([{"rating": "low"}, {"rating": "serious"}]),
            "high")
        self.assertEqual(
            overall_rating([{"rating": "low"}, {"rating": "critical"}]),
            "high")
        self.assertEqual(
            overall_rating([{"rating": "low"}, {"rating": "moderate"}]),
            "some_concerns")
        self.assertEqual(
            overall_rating([{"rating": "low"}, {"rating": "low"}]),
            "low")

    def test_robins_i_adds_seventh_domain(self):
        self.assertIn("classification_of_interventions",
                      domains_for_design("cohort"))
        # RoB-2 set unchanged for randomised work.
        self.assertEqual(
            domains_for_design("rct"),
            ["randomisation", "allocation_concealment", "blinding_participants",
             "blinding_outcome", "incomplete_outcome_data",
             "selective_reporting"])

    def test_amstar_item_registry_has_disjoint_flags(self):
        critical = {k for (k, c, _q) in AMSTAR2_ITEMS if c}
        non_critical = {k for (k, c, _q) in AMSTAR2_ITEMS if not c}
        self.assertTrue(critical)
        self.assertTrue(non_critical)
        self.assertFalse(critical & non_critical)


class AMSTAR2RuleTest(unittest.TestCase):
    """overall_amstar2 is deterministic over stored item answers."""

    def setUp(self):
        self.all_yes = [{"domain": k, "rating": "yes"}
                        for (k, _c, _q) in AMSTAR2_ITEMS]

    def _clone(self, replacements):
        rows = [dict(r) for r in self.all_yes]
        for domain, rating in replacements.items():
            for r in rows:
                if r["domain"] == domain:
                    r["rating"] = rating
        return rows

    def test_clean_review_is_high(self):
        self.assertEqual(overall_amstar2(self.all_yes), "high")

    def test_critical_weakness_is_critically_low(self):
        crit = next(k for (k, c, _q) in AMSTAR2_ITEMS if c)
        self.assertEqual(overall_amstar2(self._clone({crit: "no"})),
                         "critically low")
        # No verbatim quote, no rating: no_information counts the same way.
        self.assertEqual(
            overall_amstar2(self._clone({crit: "no_information"})),
            "critically low")

    def test_non_critical_weaknesses_scale(self):
        nc = [k for (k, c, _q) in AMSTAR2_ITEMS if not c]
        self.assertEqual(overall_amstar2(self._clone({nc[0]: "no"})),
                         "moderate")
        self.assertEqual(
            overall_amstar2(self._clone({nc[0]: "no", nc[1]: "no"})),
            "moderate")
        self.assertEqual(
            overall_amstar2(self._clone({d: "no" for d in nc[:3]})),
            "low")

    def test_unknown_items_belong_to_no_known_domain(self):
        rows = self.all_yes + [{"domain": "not_an_item", "rating": "no"}]
        self.assertEqual(overall_amstar2(rows), "high")


class BiasInstrumentStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="meta_instrument_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        db_path = os.path.join(self.tmp, "data", "research.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db = Database(db_path)

    def test_instrument_field_roundtrip(self):
        record = {
            "source_id": "s9", "design": "meta-analysis",
            "instrument": "amstar2",
            "domains": '[{"domain": "protocol_registered", '
                       '"rating": "no_information"}]',
            "overall": "critically low", "assessor": "rob_assessor_v1",
            "extraction_pass": 1, "disputed": 0,
            "source_text_id": "t9", "created_at": "2026-01-01T00:00:00Z",
        }
        self.db.save_bias_assessment(record)
        loaded = self.db.get_bias_assessment("s9")
        self.assertEqual(loaded["instrument"], "amstar2")
        self.assertEqual(loaded["overall"], "critically low")

    def test_missing_instrument_defaults_to_empty(self):
        record = {"source_id": "s10", "design": "rct", "domains": "[]",
                  "overall": "low", "assessor": "x",
                  "created_at": "2026-01-01T00:00:00Z"}
        self.db.save_bias_assessment(record)
        self.assertEqual(
            self.db.get_bias_assessment("s10")["instrument"], "")


    def test_report_counts_amstar_separately(self):
        # One study-level RoB reading, one review audit: the table keeps the
        # vocabularies apart.
        rob = {"source_id": "st1", "design": "rct", "domains": "[]",
               "overall": "high", "assessor": "rob_assessor_v1",
               "disputed": 0, "created_at": ""}
        audit = {"source_id": "rev1", "design": "systematic review",
                 "instrument": "amstar2", "domains": "[]",
                 "overall": "critically low", "assessor": "rob_assessor_v1",
                 "disputed": 0, "created_at": ""}
        self.db.save_bias_assessment(rob)
        self.db.save_bias_assessment(audit)
        lines = _meta_lines(self.db)
        self.assertIn("| high | 1 |", lines)
        self.assertIn("| some_concerns | 0 |", lines)
        self.assertIn("| AMSTAR 2: critically low | 1 |", lines)

    def test_report_reviews_do_not_enter_rob_counts(self):
        self.db.save_bias_assessment({
            "source_id": "rev2", "design": "meta-analysis",
            "instrument": "amstar2", "domains": "[]",
            "overall": "low", "assessor": "x",
            "disputed": 0, "created_at": ""})
        self.db.save_bias_assessment({
            "source_id": "st2", "design": "rct", "domains": "[]",
            "overall": "low", "assessor": "x",
            "disputed": 0, "created_at": ""})
        lines = _meta_lines(self.db)
        self.assertIn("| AMSTAR 2: low | 1 |", lines)
        rob_line = next(line for line in lines if line.startswith("| low |"))
        self.assertTrue(rob_line.endswith("| 1 |"))


if __name__ == "__main__":
    unittest.main()
