"""Tests for the `## Metaanalyse` section of the closing report.

The claim under test is not "there is a heading": it is that the section is
honest. A pooled value appears only when at least `META_MIN_STUDIES` studies carry
a usable precision, rows that could not be pooled stay visible with their reason,
and the same database produces the same text twice.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.database import Database
from research_agent.meta.screening import DECISION_EXCLUDE, record_decision
from research_agent.report import build_report


class MetaReportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="meta_report_")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.db = Database(":memory:")

    def source(self, sid, relevance=0.8, title=None, author="Doe, Jane",
               year="2024-03-01"):
        self.db.save_source({
            "id": sid, "title": title or f"Paper {sid}", "author": author,
            "publication_date": year, "url": f"https://doi.org/10.1/{sid}",
            "source_type": "paper", "relevance": relevance, "relevance_scored": 1,
            "date_added": "2026-01-01T00:00:00Z",
        })

    def effect(self, eid, sid, effect, se=None, ci=None, outcome="Kognition",
               disputed=0, rejection="", design="cohort"):
        row = {
            "id": eid, "source_id": sid, "outcome": outcome, "effect_type": "smd",
            "effect": effect, "ci_level": 0.95, "n": 1000, "design": design,
            "disputed": disputed, "rejection_reason": rejection,
            "quote": f"effect {effect} (unit: SD)", "quote_start": 0,
            "quote_end": 24, "unit": "SD", "created_at": "2026-01-01T00:00:00Z",
        }
        if se is not None:
            row["se"] = se
        if ci is not None:
            row["ci_low"], row["ci_high"] = ci
        self.db.save_study_effect(row)

    def section(self, topic="Kognition", **kwargs):
        path = build_report(self.db, topic, reason="test", out_dir=self.tmp,
                            **kwargs)
        text = Path(path).read_text(encoding="utf-8")
        self.assertIn("## Metaanalyse", text)
        start = text.index("## Metaanalyse")
        stop = text.index("## Limitationen")
        return text[start:stop]

    def test_section_sits_between_the_result_and_the_limitations(self):
        path = build_report(self.db, "Kognition", reason="test", out_dir=self.tmp)
        text = Path(path).read_text(encoding="utf-8")
        positions = [text.index("## Ergebnis"), text.index("## Metaanalyse"),
                     text.index("## Limitationen")]
        self.assertEqual(positions, sorted(positions))

    def test_without_any_effect_row_the_section_says_so(self):
        self.source("s1")
        section = self.section()
        self.assertIn("Keine Effektgröße aus der Literatur", section)
        self.assertNotIn("Gepoolter Effekt", section)
        self.assertIn("| Effektzeilen gesamt | 0 |", section)

    def test_one_study_is_listed_but_never_called_pooled(self):
        self.source("s1")
        self.effect("e1", "s1", 0.4, se=0.1)
        section = self.section()
        self.assertIn("Paper s1", section)
        self.assertIn("Kein gepoolter Wert", section)
        self.assertNotIn("Gepoolter Effekt", section)
        self.assertIn("k = 1", section)

    def test_two_studies_with_precision_produce_the_pooled_value(self):
        self.source("s1")
        self.source("s2")
        self.effect("e1", "s1", 0.2, se=0.1)
        self.effect("e2", "s2", 0.6, se=0.1)
        section = self.section()
        self.assertIn("Gepoolter Effekt (Random Effects", section)
        self.assertIn("k = 2 Studien", section)
        # Equal variances: the random-effects estimate is the arithmetic mean.
        self.assertIn("0.400", section)
        self.assertIn("Heterogenität: Q =", section)
        # With k = 2 there is no prediction interval (it needs k - 2 > 0), and the
        # section must not print one: t with zero degrees of freedom is not a
        # number.
        self.assertNotIn("Prediction Interval", section)

    def test_three_studies_add_the_prediction_interval_and_leave_one_out(self):
        self.source("s1")
        self.source("s2")
        self.source("s3")
        self.effect("e1", "s1", 0.2, se=0.1, design="twin")
        self.effect("e2", "s2", 0.4, se=0.1, design="twin")
        self.effect("e3", "s3", 0.6, se=0.1, design="cohort")
        section = self.section()
        self.assertIn("Gepoolter Effekt (Random Effects", section)
        self.assertIn("Prediction Interval", section)
        self.assertIn("Leave-one-out", section)

    def test_two_filled_design_groups_raise_the_between_group_test(self):
        for sid in ("s1", "s2", "s3", "s4"):
            self.source(sid)
        self.effect("e1", "s1", -0.6, se=0.1, design="twin")
        self.effect("e2", "s2", -0.5, se=0.1, design="twin")
        self.effect("e3", "s3", 0.8, se=0.1, design="cohort")
        self.effect("e4", "s4", 0.9, se=0.1, design="cohort")
        section = self.section()
        self.assertIn("Subgruppen nach Design: Q_between", section)
        self.assertIn("p = 0.000", section)

    def test_the_configured_minimum_study_count_gates_the_pooled_value(self):
        self.source("s1")
        self.source("s2")
        self.effect("e1", "s1", 0.2, se=0.1)
        self.effect("e2", "s2", 0.6, se=0.1)
        section = self.section(meta_min_studies=3)
        self.assertNotIn("Gepoolter Effekt", section)
        self.assertIn("META_MIN_STUDIES = 3", section)

    def test_disputed_rows_are_named_and_not_pooled(self):
        self.source("s1")
        self.source("s2")
        self.effect("e1", "s1", 0.2, se=0.1)
        self.effect("e2", "s2", 0.9, se=0.1, disputed=1)
        section = self.section()
        self.assertIn("Doppel-Extraktion widersprüchlich", section)
        self.assertNotIn("Gepoolter Effekt", section)

    def test_rows_without_precision_are_counted_with_their_reason(self):
        self.source("s1")
        self.source("s2")
        self.effect("e1", "s1", 0.2, se=0.1)
        self.effect("e2", "s2", 0.6, ci=(0.3, 0.9))  # OR-style interval, not smd
        section = self.section()
        self.assertIn("Warum Zeilen nicht gepoolt wurden", section)

    def test_exclusion_reasons_appear_in_the_counts(self):
        self.source("s1")
        self.source("s2")
        self.effect("e1", "s1", 0.2, se=0.1)
        self.effect("e2", "s2", 0.6, se=0.1)
        record_decision(self.db, "Kognition", "s2", DECISION_EXCLUDE,
                        "keine Kohorte mit Outcome")
        section = self.section()
        self.assertIn("Ausschlussgründe:", section)
        self.assertIn("keine Kohorte mit Outcome: 1", section)

    def test_same_database_gives_the_same_section_twice(self):
        self.source("s1")
        self.source("s2")
        self.effect("e1", "s1", 0.2, se=0.1)
        self.effect("e2", "s2", 0.6, se=0.12)
        self.assertEqual(self.section(), self.section())


class MetaTargetReportTest(MetaReportTest):
    """The report has to say what the synthesis was aimed at, and what missed it."""

    def aim(self, topic="Kognition"):
        from research_agent.meta.targets import save_targets

        save_targets(self.db, topic, {
            "question": "Is the cognition-health association causal?",
            "outcomes": [{
                "label": "Kognition",
                "aliases": ["IQ", "cognitive ability"],
                "direction": "higher = better cognition",
                "scale": "smd",
            }],
        })

    def test_the_section_names_the_aim_and_its_coverage(self):
        self.aim()
        self.source("s1")
        self.source("s2")
        self.effect("e1", "s1", 0.2, se=0.1, outcome="IQ")
        self.effect("e2", "s2", 0.6, se=0.12, outcome="Kognition")
        section = self.section()
        self.assertIn("### Zielmaß der Synthese", section)
        self.assertIn("**Kognition**", section)
        self.assertIn("2 von 2 gespeicherten Effektzeilen", section)
        self.assertIn("Gepoolter Effekt", section)

    def test_two_wordings_pool_once_the_aim_is_known(self):
        self.aim()
        self.source("s1")
        self.source("s2")
        # Same construct, two labels - with the aim they are one group of two.
        for eid, sid, outcome in (("e1", "s1", "IQ"), ("e2", "s2", "Kognition")):
            row = {"id": eid, "source_id": sid, "outcome": outcome,
                   "outcome_key": "Kognition", "effect_type": "smd",
                   "effect": 0.3, "se": 0.1, "ci_level": 0.95, "n": 900,
                   "design": "cohort", "unit": "SD", "disputed": 0,
                   "quote": "effect 0.30 (unit: SD)", "quote_start": 0,
                   "quote_end": 24, "rejection_reason": "",
                   "created_at": "2026-01-01T00:00:00Z"}
            self.db.save_study_effect(row)
        section = self.section()
        self.assertIn("aus k = 2 Studien", section)

    def test_rows_beside_the_aim_are_listed_instead_of_silently_dropped(self):
        self.aim()
        self.source("s1")
        self.source("s2")
        self.effect("e1", "s1", 0.2, se=0.1, outcome="Kognition")
        self.effect("e2", "s2", 0.4, se=0.1, outcome="Blutdruck")
        section = self.section()
        self.assertIn("### Gelesen, aber nicht im Zielmaß", section)
        self.assertIn("Blutdruck: 1", section)

    def test_without_an_aim_the_section_says_so(self):
        self.source("s1")
        self.effect("e1", "s1", 0.2, se=0.1)
        section = self.section()
        self.assertIn("Kein Zielmaß abgeleitet", section)


if __name__ == "__main__":
    unittest.main()
