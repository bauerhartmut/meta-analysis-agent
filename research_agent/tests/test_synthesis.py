"""Tests for pooling experiments into one estimate (experiments/synthesis.py).

Offline and deterministic: pooling is arithmetic over stored numbers, so it is
tested against hand-computed expectations rather than a live LLM.

What these tests pin down is the scientific claim, not the implementation: a
precise study outweighs a noisy one, disagreement between studies shows up as
heterogeneity instead of being averaged away, and evidence is never pooled
across different hypotheses.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from research_agent.experiments.synthesis import group_by_hypothesis, pool
from research_agent.report import build_report


def _experiment(value, low=None, high=None, verdict="supports", hid="h1", values=None):
    result = {"value": value, "p_value": 0.01}
    if low is not None and high is not None:
        result.update({"ci_low": low, "ci_high": high})
    if values is not None:
        result["values"] = values
    return {
        "id": f"e-{value}-{low}-{high}",
        "hypothesis_id": hid,
        "claim": "claim",
        "status": "completed",
        "verdict": verdict,
        "result": json.dumps(result),
        "replication_rate": 1.0,
        "deviations": "[]",
        "duration_s": 1.0,
    }


class TestPooling(unittest.TestCase):
    def test_precise_study_dominates_the_estimate(self):
        # Narrow interval (precise) at 0.10, wide interval (noisy) at 0.50.
        pooled = pool([
            _experiment(0.10, 0.09, 0.11),
            _experiment(0.50, -0.50, 1.50),
        ])
        self.assertIsNotNone(pooled)
        self.assertEqual(pooled.k, 2)
        self.assertLess(pooled.pooled, 0.20, "the noisy study must not drag the estimate")
        self.assertLess(pooled.ci_low, pooled.pooled)
        self.assertGreater(pooled.ci_high, pooled.pooled)

    def test_agreeing_studies_have_no_heterogeneity(self):
        pooled = pool([_experiment(0.20, 0.18, 0.22), _experiment(0.21, 0.19, 0.23)])
        self.assertLess(pooled.heterogeneity, 0.35)

    def test_disagreeing_studies_show_heterogeneity(self):
        pooled = pool([_experiment(0.20, 0.18, 0.22), _experiment(-0.20, -0.22, -0.18)])
        self.assertGreater(pooled.heterogeneity, 0.9, "a sign conflict is heterogeneity")

    def test_verdicts_and_replications_are_counted(self):
        pooled = pool([
            _experiment(0.2, 0.1, 0.3, verdict="supports", values=[0.2, 0.2, 0.2]),
            _experiment(0.1, 0.0, 0.2, verdict="neutral", values=[0.1, 0.1]),
            _experiment(-0.1, -0.2, 0.0, verdict="contradicts"),
        ])
        self.assertEqual((pooled.supports, pooled.neutral, pooled.contradicts), (1, 1, 1))
        self.assertEqual(pooled.replications, 6)

    def test_missing_intervals_still_pool(self):
        pooled = pool([_experiment(0.30), _experiment(0.50)])
        self.assertAlmostEqual(pooled.pooled, 0.40)
        self.assertEqual(pooled.heterogeneity, 0.0, "no precision data, no heterogeneity claim")

    def test_incomplete_experiments_are_ignored(self):
        rows = [_experiment(0.2, 0.1, 0.3)]
        rows.append({**rows[0], "status": "failed", "verdict": ""})
        self.assertEqual(pool(rows).k, 1)

    def test_nothing_to_pool(self):
        self.assertIsNone(pool([]))
        self.assertIsNone(pool([{**{k: v for k, v in _experiment(0.1).items()},
                                "status": "not_testable"}]))

    def test_grouping_keeps_hypotheses_apart(self):
        grouped = group_by_hypothesis([
            _experiment(0.1, hid="a"), _experiment(0.2, hid="a"), _experiment(0.3, hid="b"),
            {**_experiment(0.4), "hypothesis_id": ""},
        ])
        self.assertEqual(len(grouped["a"]), 2)
        self.assertEqual(len(grouped["b"]), 1)
        self.assertNotIn("", grouped)


class TestReport(unittest.TestCase):
    def setUp(self):
        from research_agent.database import Database
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(":memory:")
        from research_agent.models import gen_id, now_iso
        self.hid = gen_id()
        self.db.save_hypothesis({
            "id": self.hid,
            "claim": "Sleep loss raises error rates",
            "status": "active",
            "confidence": 0.5,
            "date_added": now_iso(),
        })

    def tearDown(self):
        self.tmp.cleanup()

    def _save(self, **overrides):
        from research_agent.models import gen_id, now_iso
        row = {
            "id": gen_id(),
            "hypothesis_id": self.hid,
            "claim": "Sleep loss raises error rates",
            "status": "completed",
            "verdict": "supports",
            "result": json.dumps({"value": 0.2, "p_value": 0.001,
                                  "values": [0.2, 0.21, 0.19]}),
            "replication_rate": 1.0,
            "deviations": json.dumps(["n=900 deviates from the preregistered n=400"]),
            "sensitivity": "[]",
            "duration_s": 2.0,
            "created_at": now_iso(),
            "updated_at": now_iso(),
        }
        row.update(overrides)
        self.db.save_experiment(row)
        return row

    def _report(self) -> str:
        path = build_report(self.db, "sleep", reason="budget reached", out_dir=self.tmp.name)
        return Path(path).read_text(encoding="utf-8")

    def test_report_shows_replication_and_deviations(self):
        self._save()
        text = self._report()
        self.assertIn("repliziert", text)
        self.assertIn("100%", text)
        self.assertIn("preregistered n=400", text)

    def test_report_pools_repeated_experiments(self):
        self._save()
        self._save(verdict="neutral", result=json.dumps({"value": 0.1, "p_value": 0.4}))
        text = self._report()
        self.assertIn("Gepoolte Schätzung", text)
        self.assertIn("2 (", text)

    def test_report_lists_unconfirmed_findings(self):
        self._save(verdict="neutral")
        self.assertIn("Nicht bestätigt", self._report())


if __name__ == "__main__":
    unittest.main()
