"""
Per-Report Evaluation against the Paket-D golden set
=====================================================
PAKET H: close the evaluation loop on the single-shot Deep-Research reports
(research_agent/deep_research.py). For one deep-research report and one golden
question this scores claim-recall and number-accuracy using the SAME deterministic
helpers as quality_eval.py (Paket D), and appends the per-question score to a
history file so you can see whether the deep-research pipeline improves over time.

Scoring (identical semantics to quality_eval.run_eval):
    composite = 100 * (0.7 * claim_recall + 0.3 * number_accuracy)
A claim counts as recalled if a *single* report entry covers >= 70% of its
distinctive terms AND states all of its required numbers.

Usage:
    # Score one report file against a matched golden question:
    python -m research_agent.evals.report_eval \\
        --report data/reports/wilson_...md --question "Was ... Wilson-Effekt ..." \\
        --record data/reports/eval_history.jsonl

    # Score by explicit golden id:
    python -m research_agent.evals.report_eval --report ... --golden-id q01_wilson_effect

    # Show the trend from a history file:
    python -m research_agent.evals.report_eval --trend data/reports/eval_history.jsonl

    # Optional: run deep research for the question first, then score it:
    python -m research_agent.evals.report_eval --golden-id q01_wilson_effect --run-deep
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict

from .quality_eval import (
    load_golden_set,
    score_claim,
    _score_gap_checks,
    _significant_terms,
    _idf_weights,
)

ROOT = Path(__file__).resolve().parents[2]
HISTORY_DEFAULT = ROOT / "data" / "reports" / "eval_history.jsonl"


def golden_questions(golden_path: Optional[str] = None) -> List[dict]:
    return load_golden_set(golden_path)["questions"]


def match_golden(question_text: str, questions: List[dict]) -> Optional[dict]:
    """Pick the golden question with the highest distinctive-term overlap."""
    best, best_score = None, 0.0
    qt = set(_significant_terms(question_text))
    for q in questions:
        gt = set(_significant_terms(q["question"]))
        union = len(qt | gt) or 1.0
        sc = len(qt & gt) / union
        if sc > best_score:
            best, best_score = q, sc
    return best


def score_report(report_text: str, golden_q: dict) -> dict:
    """Score one report against one golden question."""
    corpus = [{"type": "report", "text": report_text}]
    lowered = [report_text.lower()]
    big_text = " ".join(lowered)
    idf = _idf_weights(corpus)

    claim_results = [score_claim(c, corpus, idf, lowered) for c in golden_q["claims"]]
    gap_results = _score_gap_checks(golden_q.get("gap_checks", []), big_text)

    n_claims = len(claim_results)
    n_recalled = sum(1 for r in claim_results if r["recalled"])
    req_nums = sum(len(r["numbers_required"]) for r in claim_results)
    matched_nums = sum(len(r["numbers_matched"]) for r in claim_results)
    num_acc = (matched_nums / req_nums) if req_nums else 1.0
    claim_recall = (n_recalled / n_claims) if n_claims else 0.0
    n_gaps = len(gap_results)
    n_gaps_passed = sum(1 for g in gap_results if g["passed"])
    gap_coverage = (n_gaps_passed / n_gaps) if n_gaps else 1.0

    return {
        "golden_id": golden_q["id"],
        "question": golden_q["question"],
        "n_claims": n_claims,
        "n_recalled": n_recalled,
        "claim_recall": round(claim_recall, 3),
        "numbers_required": req_nums,
        "numbers_matched": matched_nums,
        "number_accuracy": round(num_acc, 3),
        "gap_coverage": round(gap_coverage, 3),
        "n_gaps": n_gaps,
        "n_gaps_passed": n_gaps_passed,
        "composite": round(100.0 * (0.7 * claim_recall + 0.3 * num_acc), 1),
        "claims": [
            {
                "recalled": r["recalled"],
                "coverage": r["coverage"],
                "claim": r["claim"],
                "numbers_required": r["numbers_required"],
                "numbers_matched": r["numbers_matched"],
                "numbers_missing": r["numbers_missing"],
                "missing_terms": r.get("missing_terms", []),
            }
            for r in claim_results
        ],
    }


def fmt_report(res: dict) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append(f"REPORT EVAL  [{res['golden_id']}]")
    lines.append(f"Q: {res['question']}")
    lines.append("=" * 70)
    lines.append(f"  composite     = {res['composite']}")
    lines.append(f"  claim_recall  = {res['claim_recall']:.2f} "
                 f"({res['n_recalled']}/{res['n_claims']})")
    lines.append(f"  num_accuracy  = {res['number_accuracy']:.2f} "
                 f"({res['numbers_matched']}/{res['numbers_required']})")
    if res.get("n_gaps"):
        lines.append(f"  gaps          = {res['gap_coverage']:.2f} "
                     f"({res['n_gaps_passed']}/{res['n_gaps']})")
    src = res.get("sources_gathered")
    clen = res.get("extractable_content_len")
    if src is not None or clen is not None:
        lines.append(
            f"  gather        = {src if src is not None else '?'} sources, "
            f"{clen if clen is not None else '?'} chars extracted"
        )
    for c in res["claims"]:
        flag = "OK  " if c["recalled"] else "MISS"
        num = ""
        if c["numbers_missing"]:
            num = f"  [missing nums: {', '.join(c['numbers_missing'])}]"
        lines.append(f"   {flag} cov={c['coverage']:.2f} | {c['claim'][:90]}{num}")
    lines.append("=" * 70)
    return "\n".join(lines)


def _write_history(path: Path, res: dict, report_file: str, extra: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "report_file": report_file,
        **{k: v for k, v in res.items() if k != "claims"},
    }
    row.update(extra)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def fmt_trend(path: Path) -> str:
    if not path.exists():
        return f"no history file at {path}"
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    if not rows:
        return f"history file empty: {path}"
    lines = ["TREND (best ... newest):"]
    for r in rows[-10:]:
        lines.append(
            f"  {r.get('timestamp', '')[:19]}  gold={r.get('golden_id','?')}  "
            f"composite={r.get('composite')}  recall={r.get('claim_recall')}  "
            f"num={r.get('number_accuracy')}"
        )
    comps = [r["composite"] for r in rows if "composite" in r]
    if len(comps) >= 2:
        lines.append(
            f"  -> composite {min(comps)} ... {max(comps)}; last={comps[-1]} "
            f"(first={comps[0]}) across {len(comps)} runs"
        )
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", help="Path to a deep-research markdown report.")
    ap.add_argument("--question", help="Free-text question (matched to golden set).")
    ap.add_argument("--golden-id", help="Explicit golden question id (e.g. q01_wilson_effect).")
    ap.add_argument("--golden", help="Path to golden_answers.json (default: Paket D built-in).")
    ap.add_argument("--record", help="Append the score to this history JSONL.")
    ap.add_argument("--run-deep", action="store_true",
                    help="Optionally run deep research for the question first (needs Ollama/network).")
    ap.add_argument("--max-sources", type=int, default=6)
    ap.add_argument("--trend", help="Instead of scoring, print the trend from a history file.")
    args = ap.parse_args(argv)

    if args.trend:
        print(fmt_trend(Path(args.trend)))
        return 0

    questions = golden_questions(args.golden)
    if args.golden_id:
        golden_q = next((q for q in questions if q["id"] == args.golden_id), None)
        if not golden_q:
            print(f"ERROR: unknown golden id '{args.golden_id}'", file=sys.stderr)
            return 2
        question_text = golden_q["question"]
    elif args.question:
        question_text = args.question
        golden_q = match_golden(question_text, questions)
        if not golden_q:
            print("ERROR: could not match question to a golden entry", file=sys.stderr)
            return 2
    else:
        print("ERROR: need --report with --question or --golden-id", file=sys.stderr)
        return 2

    # Optional: run deep research to produce the report.
    if args.run_deep:
        import asyncio
        from ..deep_research import DeepResearch

        async def _produce(question: str, topic: str, max_sources: int):
            dr = DeepResearch()
            try:
                rep = await dr.run(question=question, topic=topic, max_sources=max_sources)
            finally:
                await dr.close()
            return rep

        rep = asyncio.run(_produce(question_text, question_text, args.max_sources))
        report_text = rep.markdown
        report_file = rep.file_path
    else:
        if not args.report:
            print("ERROR: provide --report (or --run-deep)", file=sys.stderr)
            return 2
        report_file = args.report
        try:
            report_text = Path(args.report).read_text(encoding="utf-8")
        except OSError as e:
            print(f"ERROR: cannot read report: {e}", file=sys.stderr)
            return 2

    res = score_report(report_text, golden_q)

    # Diagnostic metrics: distinguish 'search found nothing' (gather=0) from
    # 'search found sources but extraction failed' (gather>0, low chars).
    if args.run_deep:
        res["sources_gathered"] = rep.sources_gathered
        res["extractable_content_len"] = rep.extractable_content_len
    elif report_file:
        res["sources_gathered"] = None
        res["extractable_content_len"] = len(report_text)

    print(fmt_report(res))

    if args.record:
        extra = {"question_input": question_text}
        _write_history(Path(args.record), res, report_file, extra)
        print(f"\n[history appended -> {args.record}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())