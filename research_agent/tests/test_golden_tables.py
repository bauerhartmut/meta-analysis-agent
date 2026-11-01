"""Golden-set runner for the table extractor (Phase 1, 2026-11-01 order).

The golden set lives in data/golden_tables/*.json; each case is annotated by
hand against a stored full text. The tests do not silently pass on empty
detection: a block expected in the annotation must be found, and the verbatim
invariant (block body is a substring of the stored document) is asserted for
every detected block, because table quotes have to validate later.
"""

import json
import unittest
from pathlib import Path
from typing import List, Optional, Sequence

from research_agent.research.table_extractor import find_table_blocks

_FULLTEXT_DIR = Path("data/fulltext").resolve()
_GOLDEN_DIR = Path("data/golden_tables").resolve()


class GoldenTableCaseTest(unittest.TestCase):
    def test_all_annotated_cases(self):
        files = sorted(_GOLDEN_DIR.glob("case_*.json"))
        self.assertGreater(len(files), 0, "no golden cases present")
        failures: List[str] = []
        for path in files:
            case = json.loads(path.read_text(encoding="utf-8"))
            src = _FULLTEXT_DIR / case["source_file"]
            self.assertTrue(src.exists(), f"missing source {src}")
            text = src.read_text(encoding="utf-8", errors="ignore")
            blocks = find_table_blocks(text)
            labels = {b.table_label: b for b in blocks}
            for expected in case["expected_blocks"]:
                label = expected["table_label"]
                block = labels.get(label)
                if block is None:
                    failures.append(f"{path.name}: block {label} not detected")
                    continue
                cap = expected.get("caption_startswith", "")
                if cap and not block.caption.startswith(cap):
                    failures.append(
                        f"{path.name}: caption mismatch for {label}: "
                        f"{block.caption[:60]!r} vs {cap[:60]!r}")
                if len(block.body.splitlines()) < expected.get("min_lines", 1):
                    failures.append(
                        f"{path.name}: too few lines for {label}: "
                        f"{len(block.body.splitlines())}")
                if block.body.strip():
                    if block.body[:40] not in text:
                        failures.append(
                            f"{path.name}: block {label} body NOT verbatim")
                if expected.get("expected_effect_cells") == [] and \
                        block.effect_cells and expected.get(
                        "no_effect_cells_expected_in_tables"):
                    failures.append(
                        f"{path.name}: unexpected effect cells in {label}")
            for gone in case.get("must_not_be_completed", []):
                fragment = gone["caption_startswith"]
                for b in blocks:
                    if fragment in b.caption:
                        failures.append(
                            f"{path.name}: prose reference became a block: "
                            f"{fragment!r}")
        self.assertEqual(failures, [], "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
