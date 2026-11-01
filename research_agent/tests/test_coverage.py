"""Tests for the fulltext coverage manager (legal-first status tracking)."""

import os
import tempfile
import unittest

from research_agent.coverage.manager import (
    STATUSES,
    CoverageManager,
    _xml_to_text,
)


class TestCoverageManager(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db_path = os.path.join(self.tmp, "data", "research.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.inbox_dir = os.path.join(self.tmp, "data", "fulltext_inbox")
        os.makedirs(self.inbox_dir, exist_ok=True)
        self.mgr = CoverageManager(self.db_path, inbox_dir=self.inbox_dir)

    # ------------------------------------------------------------ statuses
    def test_all_auftrag_statuses_defined(self):
        expected = [
            "DISCOVERED", "ABSTRACT_AVAILABLE", "FULLTEXT_SEARCHING",
            "OPEN_ACCESS_AVAILABLE", "LICENSE_VERIFIED", "DOWNLOADED",
            "MANUAL_REQUIRED", "AUTHOR_REQUEST_PENDING",
            "AUTHOR_VERSION_RECEIVED", "DATA_EXTRACTED", "DATA_VALIDATED",
            "EXCLUDED", "LICENSE_UNCLEAR", "FAILED",
        ]
        self.assertEqual(STATUSES, expected)

    def test_register_and_status_flow(self):
        self.mgr.register_study("10.1234/abc", title="Exercise vs placebo")
        self.assertEqual(self.mgr.study("10.1234/abc")["title"],
                         "Exercise vs placebo")
        # Re-registering keeps existing values, only fills empty ones.
        self.mgr.register_study("10.1234/abc", journal="BMJ Sleep")
        row = self.mgr.study("10.1234/abc")
        self.assertEqual(row["journal"], "BMJ Sleep")
        self.assertEqual(row["title"], "Exercise vs placebo")

        self.mgr.record_status("10.1234/abc", "LICENSE_VERIFIED", "cc-by")
        self.mgr.record_status("10.1234/abc", "DATA_EXTRACTED", "3 endpoints")
        row = self.mgr.study("10.1234/abc")
        self.assertEqual(row["status"], "DATA_EXTRACTED")
        rows = self.mgr._conn.execute(
            "SELECT status FROM studies_status_log WHERE doi = ?",
            ("10.1234/abc",)).fetchall()
        # registered (loged once) + license + extracted
        self.assertEqual(len(rows), 3)

    def test_invalid_status_rejected(self):
        with self.assertRaises(AssertionError):
            self.mgr.record_status("10.1/x", "NOT_A_STATUS")

    def test_validated_transition_counts_in_stats(self):
        """A clean double-pass extraction lifts a study to DATA_VALIDATED,
        and coverage_stats reports it - the dashboard never shows validated
        coverage the oracle did not accept."""
        self.mgr.register_study("10.1234/val", title="Validated reading")
        self.mgr.record_status("10.1234/val", "DATA_EXTRACTED", "2 effect rows")
        stats = self.mgr.coverage_stats()
        self.assertEqual(stats["data_extracted"], 1)
        self.assertEqual(stats["data_validated"], 0)
        self.mgr.record_status("10.1234/val", "DATA_VALIDATED",
                               "both extraction passes agree")
        row = self.mgr.study("10.1234/val")
        self.assertEqual(row["status"], "DATA_VALIDATED")
        stats = self.mgr.coverage_stats()
        self.assertEqual(stats["data_extracted"], 0)
        self.assertEqual(stats["data_validated"], 1)

    def test_downloaded_sets_has_fulltext(self):
        self.mgr.register_study("10.1234/light", title="Light")
        self.mgr.record_status("10.1234/light", "DOWNLOADED", "pmc xml")
        self.assertEqual(self.mgr.study("10.1234/light")["has_fulltext"], 1)

    def test_exclude_and_extraction(self):
        self.mgr.register_study("10.5555/out", title="Out of scope")
        self.mgr.exclude("10.5555/out", "not an RCT")
        row = self.mgr.study("10.5555/out")
        self.assertEqual(row["status"], "EXCLUDED")
        self.assertEqual(row["excluded_reason"], "not an RCT")
        self.mgr.set_extraction("10.5555/out", "n/a", endpoints_available=0)

    # ------------------------------------------------------------ inbox
    def test_inbox_xml_served(self):
        xml = ("<?xml version='1.0'?>\n<article><front/><body><p>"
               + "Exercise reduces depressive symptoms. " * 80
               + "</p></body></article>")
        name = self.mgr.sanitize_doi_value("10.1234/bmc") + ".xml"
        with open(os.path.join(self.inbox_dir, name), "w",
                  encoding="utf-8") as fh:
            fh.write(xml)
        found = self.mgr.inbox_text("10.1234/bmc")
        self.assertIsNotNone(found)
        kind, text = found
        self.assertEqual(kind, "xml")
        self.assertIn("depressive", text)
        self.assertNotIn("<", text)

    def test_inbox_missing_returns_none(self):
        self.assertIsNone(self.mgr.inbox_text("10.9999/none"))

    def test_xml_to_text_strips_back_matter(self):
        raw = ("<?xml?><article><ref-list><ref>x</ref></ref-list>"
               "<body><p>Methods section text.</p>"
               "<table-wrap><t>q</t></table-wrap></body></article>")
        out = _xml_to_text(raw)
        self.assertIn("Methods section text.", out)
        self.assertNotIn("<ref", out)
        # Implementation order §4.2: a table-wrap WITHOUT table rows still
        # stays an omission marker; one WITH rows now renders as caption +
        # pipe rows, so the deterministic table locator can find the numbers.
        self.assertIn("table omitted", out)

    def test_xml_to_text_keeps_table_rows(self):
        raw = ("<?xml?><article><body><p>Methods text.</p>"
               "<table-wrap><caption>Baseline characteristics.</caption>"
               "<tr><td>Age, years</td><td>63.2</td></tr>"
               "<tr><td>BMI</td><td>27.4</td></tr></table-wrap>"
               "</body></article>")
        out = _xml_to_text(raw)
        self.assertIn("Baseline characteristics.", out)
        self.assertIn("|Age, years|63.2", out)
        self.assertIn("|BMI|27.4", out)

    # ------------------------------------------------------------ author requests
    def test_author_request_user_gate(self):
        req_id = self.mgr.queue_author_request(
            "10.1234/closed", authors=["Dr. A"],
            draft_text="Dear Dr. A, ...")
        self.assertEqual(
            self.mgr.author_requests("pending_user_approval")[0]["doi"],
            "10.1234/closed")
        self.assertEqual(
            self.mgr.study("10.1234/closed")["status"],
            "AUTHOR_REQUEST_PENDING")
        self.assertTrue(self.mgr.approve_author_request(req_id))
        # approval is one-shot; double-click does not reset the gate
        self.assertFalse(self.mgr.approve_author_request(req_id))
        self.mgr.mark_author_version_received(req_id, "PDF attached")
        self.assertEqual(self.mgr.author_requests()[0]["status"], "received")
        self.assertEqual(self.mgr.study("10.1234/closed")["status"],
                         "AUTHOR_VERSION_RECEIVED")

    # ------------------------------------------------------------ stats
    def test_coverage_stats(self):
        self.mgr.register_study("10.1/a", title="A")
        self.mgr.queue_author_request("10.1/b", draft_text="Could you ...")
        # Same POOLABLE clause the pooling engine uses, mirrored from
        # study_effects in the same topic database.
        self.mgr._conn.execute(
            "CREATE TABLE study_effects (disputed INTEGER, "
            "rejection_reason TEXT, se REAL, ci_low REAL, ci_high REAL)")
        self.mgr._conn.execute(
            "INSERT INTO study_effects VALUES (0, '', 0.2, NULL, NULL)")
        self.mgr._conn.execute(
            "INSERT INTO study_effects VALUES (1, '', 0.2, NULL, NULL)")
        stats = self.mgr.coverage_stats()
        self.assertEqual(stats["identified"], 2)
        self.assertEqual(stats["author_requests_awaiting_approval"], 1)
        self.assertEqual(stats["poolable_effects"], 1)
        self.assertIn("fulltext_coverage_pct", stats)

    def test_import_acquisition_status(self):
        self.mgr.import_acquisition_status({
            "doi": "10.2/x", "title": "X", "status": "DOWNLOADED",
            "authors": [], "oa_status": "gold", "license": "cc-by",
        })
        row = self.mgr.study("10.2/x")
        self.assertEqual(row["has_fulltext"], 1)
        self.assertEqual(row["oa_status"], "gold")


if __name__ == "__main__":
    unittest.main()
