"""Golden-table annotation workflow (Phase 1, order §4.2).

Builds machine-annotated *candidates* for the golden table set from stored
full texts. A candidate is NOT a golden case: it carries the extractor's own
proposal and stays in ``data/golden_tables/pending_reviews/`` until human
review promotes it to ``data/golden_tables/*.json`` (the promotion script or
manual move). This keeps the quantitative Abnahme (>=30 tables / >=100
annotated cells) honest instead of scoring the extractor against itself.

Usage:
    python -m research_agent.research.table_annotation build --count 30 \
        --source-dir data/fulltext --out data/golden_tables/pending_reviews
    python -m research_agent.research.table_annotation promote <file> ...
"""

from __future__ import annotations

import argparse
import json
import logging
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .table_extractor import find_table_blocks, find_effect_cells

logger = logging.getLogger(__name__)

PENDING_SUBDIR = "pending_reviews"


def _stable_choice(files: List[Path], count: int, seed: int = 20261101) -> List[Path]:
    """Deterministic sample order (roadmap: reproducible benchmark inputs)."""
    rng = random.Random(seed)
    pool = sorted(files)
    return rng.sample(pool, k=min(count, len(pool)))


def build_candidates(source_dir: Path, out_dir: Path, count: int,
                     min_caption_chars: int = 25) -> List[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(Path(source_dir).glob("*.txt"))
    picked = _stable_choice(files, count * 2)[: count * 2]
    written: List[Path] = []
    for path in picked:
        text = path.read_text(encoding="utf-8", errors="ignore")
        blocks = find_table_blocks(text)
        if not blocks:
            continue
        cells = find_effect_cells(text)
        cand: Dict[str, Any] = {
            "case_id": f"pending_{path.stem[:12]}",
            "source_file": path.name,
            "annotated_by": "machine-candidate (order §4.2: needs human review)",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expected_blocks": [
                {
                    "table_label": b.table_label,
                    "caption_startswith": b.caption[:60],
                    "min_lines": max(3, b.n_lines // 2),
                    "expected_effect_cells": len(b.effect_cells),
                    "body_preview_first_3_lines": b.body.splitlines()[:3],
                }
                for b in blocks
            ],
            "effect_cells_total_in_document": len(cells),
            "annotations_needed": [
                {
                    f"block_{i}": {
                        "confirm_or_fix_caption": True,
                        "mark_cell_values": [
                            {
                                "line_first_50": c.line[:50],
                                "keyword": c.keyword,
                                "value": c.value,
                                "ci_low": c.ci_low,
                                "ci_high": c.ci_high,
                            }
                            for c in b.effect_cells
                        ],
                    }
                }
                for i, b in enumerate(blocks)
            ],
        }
        out = out_dir / f"{cand['case_id']}.json"
        out.write_text(json.dumps(cand, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(out)
        if len(written) >= count:
            break
    return written


def promote(candidate_files: List[str], golden_dir: Path) -> int:
    """Promote a machine candidate to golden status only after human review."""
    golden_dir = Path(golden_dir)
    golden_dir.mkdir(parents=True, exist_ok=True)
    moved = 0
    for raw in candidate_files:
        p = Path(raw)
        case = json.loads(p.read_text(encoding="utf-8"))
        case["annotated_by"] = case.get(
            "annotated_by", "machine-candidate"
        ) + " -> human-reviewed, promoted " + datetime.now(timezone.utc).isoformat()
        case.pop("annotations_needed", None)
        case["case_id"] = case["case_id"].replace("pending_", "case_" + ("100") + "_") \
            if False else case["case_id"].replace("pending_", "case_")
        status_key = golden_dir / p.name.replace("pending_", "case_")
        status_key.write_text(json.dumps(case, ensure_ascii=False, indent=2), encoding="utf-8")
        moved += 1
    return moved


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Golden table annotation workflow (build/promote)")
    parser.add_argument("cmd", choices=["build", "promote"])
    parser.add_argument("--count", type=int, default=30)
    parser.add_argument("--source-dir", type=str, default="data/fulltext")
    parser.add_argument("--out", type=str, default="data/golden_tables/pending_reviews")
    parser.add_argument("--files", nargs="*", default=[])
    args = parser.parse_args()

    if args.cmd == "build":
        cands = build_candidates(Path(args.source_dir), Path(args.out), args.count)
        print(f"[golden] pending candidates written: {len(cands)} -> {args.out}")
        for c in cands[:5]:
            print("  -", c)
        return 0
    moved = promote(args.files, Path("data/golden_tables"))
    print(f"[golden] promoted: {moved} case(s) into data/golden_tables/")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
