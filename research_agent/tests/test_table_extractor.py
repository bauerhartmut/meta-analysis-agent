"""Unit tests for research.table_extractor (Phase 1 of the 2026-11-01 order).

Deterministic, no network, no LLM. Real-format cases taken from stored
full texts under data/fulltext; the golden cases live in data/golden_tables
and are annotated by hand.

InOut contract: every block body the extractor reports must be a literal
substring of the original document, because meta.extraction verifies quotes
against the stored document text.
"""

import json
import sys
import unittest
from pathlib import Path
from typing import List, Optional, Tuple
from unittest import mock

from research_agent.research.table_extractor import (
    EffectCell,
    TableBlock,
    _parse_effect_line,
    find_effect_cells,
    find_table_blocks,
    augment_document_text,
)

# --- format cases -----------------------------------------------------------

_REAL_TEXT = Path("data/fulltext/0171a4d5d731852f9caac7aae79446a9.txt")
_GOLDEN_DIR = Path("data/golden_tables")


class EffectLineParsingTest(unittest.TestCase):
    def test_beta_bracket_with_negative_ci(self):
        cell = _parse_effect_line(
            "[β  = -0.05, 95% CI = -0.06 – (-0.04)]. Individuals", 0, False)
        self.assertIsNotNone(cell)
        self.assertEqual(cell.keyword, "β")
        self.assertEqual(cell.value, "-0.05")
        self.assertEqual(cell.ci_low, "-0.06")
        self.assertEqual(cell.ci_high, "-0.04")

    def test_beta_bracket_split_across_lines_is_not_faked(self):
        # In stored preprints the bracket can continue on the next line; the
        # extractor stays single-line and reports no cell rather than guessing.
        cell = _parse_effect_line("a 0.05 SD lower score [β  = -0.06, 95% CI = - 0.12 –", 0, False)
        # The bare value is real (it is on this line); the interval is not.
        self.assertIsNotNone(cell)
        self.assertEqual(cell.value, "-0.06")
        self.assertEqual(cell.ci_low, "")
        self.assertEqual(cell.ci_high, "")

    def test_hazard_ratio_with_en_dash(self):
        cell = _parse_effect_line("HR 0.72 (95% CI 0.55–0.94)", 0, False)
        self.assertEqual((cell.keyword, cell.value, cell.ci_low, cell.ci_high),
                         ("HR", "0.72", "0.55", "0.94"))

    def test_odds_ratio_with_hyphen(self):
        cell = _parse_effect_line("OR 0.92 (95% CI 0.85-0.99)", 0, False)
        self.assertEqual((cell.keyword, cell.value, cell.ci_low, cell.ci_high),
                         ("OR", "0.92", "0.85", "0.99"))

    def test_beta_standard_error(self):
        cell = _parse_effect_line("beta 0.14 (SE 0.03)", 0, False)
        self.assertIsNotNone(cell)
        self.assertEqual(cell.keyword, "beta")
        self.assertEqual(cell.value, "0.14")
        self.assertEqual(cell.se, "0.03")


class NegativeCasesTest(unittest.TestCase):
    def test_lowercase_prose_or_is_not_a_keyword(self):
        self.assertIsNone(_parse_effect_line("zero or 1+, and pre-", 0, False))
        self.assertIsNone(_parse_effect_line(
            "erate intensity as 3 to 6 METS or 4.8 to 7.1 METS.", 0, False))


class TableBlockTest(unittest.TestCase):
    def test_real_document_blocks_and_prosa_caption_ignored(self):
        text = _REAL_TEXT.read_text(encoding="utf-8", errors="ignore")
        blocks = find_table_blocks(text)
        labels = [b.table_label for b in blocks]
        self.assertIn("Table 1", labels)
        self.assertIn("Table 2", labels)
        # The narrative reference "Table 1. No sensitivity analyses were
        # performed..." must not become a block.
        for b in blocks:
            self.assertNotIn("No sensitivity analyses", b.caption)
        # Verbatim invariant: block bodies are substrings of the document.
        for b in blocks:
            if b.body.strip():
                self.assertIn(b.body[:40], text)

    def test_block_body_is_verbatim_substring(self):
        doc = ("Results\nHealth outcomes predicting cognitive ability\n"
               "BMI was associated with a 0.05 SD lower score [β = -0.05, "
               "95% CI = -0.06 – (-0.04)] reported in Table 3 below.\n"
               "Table 3. Cognitive ability at age 12 years. \n"
               "var1 1 2 3 4 1.9 2.0 0.88 0.99 \n"
               "orientation group 2 1.1 1.3 0.9 2.4 1.14 1.5 \n"
               "control third row with 3 1.0 0.4 1.82 2.0 1.03 \n"
               "Another paragraph of plain narrative text goes here.\n")
        new_text, blocks = augment_document_text(doc)
        self.assertEqual(len(blocks), 1)
        self.assertIn("Table 3", blocks[0].caption)
        # The appended body is literally part of the original document - a
        # quote the extractor takes from the table will verify.
        self.assertIn(blocks[0].body, doc)
        self.assertIn(blocks[0].body, new_text)

    def test_no_blocks_in_prose_only_document(self):
        doc = ("Table 1. No sensitivity analyses were performed due to the lack "
               "of significant causal associations. \n"
               "Results narrative sentences without digits continue here.\n")
        new_text, blocks = augment_document_text(doc)
        self.assertEqual(blocks, [])
        self.assertEqual(new_text, doc)


if __name__ == "__main__":
    unittest.main()
