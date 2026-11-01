"""
Deterministic ground-truth quality evaluation (Paket D).

Scores how well the current knowledge base (facts / hypotheses / evidence /
sources / journal syntheses + research reports) covers a golden set of seed
questions. Two sub-scores are produced per question and per claim:

  * Claim recall  - fraction of golden claims whose distinctive key terms are
                    found in the knowledge base.
  * Number/fact accuracy - fraction of the concrete numeric values asserted in
                    each golden claim that appear in the knowledge base.

Composite = 100 * (0.7 * claim_recall + 0.3 * number_accuracy).

Runs fully out-of-band: it only opens the SQLite DB read-only and reads
research-report markdown files. It never modifies agent logic or the DB.

Usage:
    python -m research_agent.evals.quality_eval                     # console report
    python -m research_agent.evals.quality_eval --db /path/research.db
    python -m research_agent.evals.quality_eval --json report.json   # also write JSON
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Golden set
# ---------------------------------------------------------------------------

GOLDEN_PATH = Path(__file__).resolve().parent / "golden_answers.json"


def load_golden_set(path: Optional[str] = None) -> dict:
    p = Path(path) if path else GOLDEN_PATH
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Locate the database
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def resolve_db_path(explicit: Optional[str] = None) -> str:
    """Resolve the research.db path: explicit arg > env > known locations > config."""
    if explicit:
        return explicit
    root = _repo_root()
    candidates: List[Path] = []
    env = os.environ.get("DATABASE_URL")
    if env:
        candidates.append(Path(env))
    # Canonical database lives at the project root; the nested
    # research_agent/data copy is a legacy artifact (pre path-unification).
    candidates += [
        root / "data" / "research.db",
        root / "research_agent" / "data" / "research.db",
    ]
    try:
        from ..config import get_config  # noqa: E402
        v = get_config().database_url
        p = Path(v)
        if not p.is_absolute():
            p = root / p
        candidates.append(p)
    except Exception:
        pass
    for c in candidates:
        try:
            if c.exists():
                return str(c)
        except OSError:
            continue
    return str(candidates[0])


def _connect_readonly(db_path: str) -> sqlite3.Connection:
    uri = f"file:{Path(db_path).resolve()}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
        conn.execute("PRAGMA query_only=ON")
        return conn
    except sqlite3.Error:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA query_only=ON")
        return conn


# ---------------------------------------------------------------------------
# Corpus assembly
# ---------------------------------------------------------------------------

def _json_list(value) -> List[str]:
    """Best-effort parse of a JSON-array column into a list of strings."""
    if not value:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    try:
        data = json.loads(value)
        if isinstance(data, list):
            return [str(v) for v in data]
    except Exception:
        pass
    return []


def _gather_reports() -> List[Tuple[str, str]]:
    """Read every research-report/story markdown as a synthesis entry."""
    entries: List[Tuple[str, str]] = []
    # dataset synthesis exports + the single-shot deep-research reports
    for base in ("data/dataset", "research_agent/data/dataset",
                 "data/reports", "research_agent/data/reports"):
        d = _repo_root() / base
        if not d.exists():
            continue
        for md in sorted(d.glob("*.md")):
            try:
                text = md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if text.strip():
                entries.append(("synthesis", f"{md.name}\n{text[:20000]}"))
    return entries


def load_knowledge_base(
    db_path: Optional[str] = None,
    include_journal: bool = False,
    include_sources: bool = False,
) -> List[dict]:
    """Build a list of {type, text} knowledge entries.

    Default scope = the distilled knowledge base: facts, hypotheses, evidence and
    the synthesis research reports. Raw source titles/summaries and the highly
    redundant journal findings are OPT-IN so they cannot mask genuine gaps by
    restating everything.

    Args:
        include_journal: also include every journal findings/updated_beliefs item.
        include_sources: also include source titles/summaries + key_claims.
    """
    db_path = resolve_db_path(db_path)
    corpus: List[dict] = []

    try:
        conn = _connect_readonly(db_path)
    except sqlite3.Error:
        return corpus

    def add(kind: str, text: str):
        text = (text or "").strip()
        if len(text) >= 8:
            corpus.append({"type": kind, "text": text})

    with conn:
        for row in conn.execute("SELECT content FROM facts"):
            add("fact", row[0])
        for row in conn.execute(
            "SELECT claim FROM hypotheses "
            "WHERE status IN ('active','proposed','plausible','supported','confirmed','contested')"
        ):
            add("hypothesis", row[0])
        for row in conn.execute(
            "SELECT content FROM evidence WHERE evidence_type IN ('supports','contradicts')"
        ):
            add("evidence", row[0])
        if include_sources:
            for row in conn.execute("SELECT title, summary FROM sources"):
                add("source", f"{(row[0] or '')}. {(row[1] or '')}")
            for row in conn.execute("SELECT key_claims FROM sources"):
                for kc in _json_list(row[0]):
                    add("source_keyclaim", kc)
        if include_journal:
            for row in conn.execute(
                "SELECT important_findings, updated_beliefs FROM journal_entries"
            ):
                for item in _json_list(row[0]) + _json_list(row[1]):
                    add("journal", item)
    conn.close()

    for kind, text in _gather_reports():
        corpus.append({"type": kind, "text": text})

    return corpus


# ---------------------------------------------------------------------------
# Text / number helpers
# ---------------------------------------------------------------------------

_STOP_TERMS = {
    "about", "after", "again", "against", "allow", "also", "among", "another",
    "available", "because", "been", "being", "between", "both", "case",
    "could", "current", "data", "each", "effect", "even", "every", "fact",
    "found", "from", "have", "having", "into", "level", "made", "make",
    "many", "might", "more", "most", "much", "must", "other", "over",
    "part", "per", "range", "ranges", "ranging", "rather", "related",
    "research", "result", "results", "said", "same", "should", "show",
    "shown", "shows", "some", "such", "than", "that", "their", "these",
    "they", "this", "though", "through", "thus", "under", "using", "very",
    "were", "what", "when", "where", "which", "while", "with", "within",
    "would", "according", "degree", "likely", "often", "total", "overall",
    "however", "study", "studies", "increases", "increase", "increased",
}


def _significant_terms(text: str) -> List[str]:
    toks = re.findall(r"[a-z][a-z0-9]*", (text or "").lower())
    return [t for t in toks if len(t) >= 4 and t not in _STOP_TERMS and not t.isdigit()]


def _number_variants(token: str) -> set:
    """Expand one numeric token into the literal forms it may appear as."""
    t = token.strip()
    variants = {t}
    if "%" in t:
        base = t.replace("%", "").strip()
        variants.add(base)
        try:
            f = float(base)
            variants.add(f"{f:g}")
        except ValueError:
            pass
    else:
        try:
            f = float(t)
            if 0 < f < 1:
                variants.add(f"{f * 100:.0f}")
                variants.add(f"{f * 100:.0f}%")
                variants.add(f"{f:.1f}")
                variants.add(f"{f:.2f}")
            elif f == int(f):
                big = int(f)
                variants.add(f"{big:,}")
        except ValueError:
            pass
    # ignore whitespace-only / empty variants
    return {v for v in variants if v.strip()}


def _numbers_in_claim(claim: dict) -> List[str]:
    return [str(n) for n in claim.get("numbers", [])]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def _match_token(token: str, big_text: str) -> bool:
    return token in big_text


def _idf_weights(corpus_entries: List[dict]) -> Dict[str, float]:
    """Inverse-document-frequency weight per term. Rare, distinctive terms weigh more."""
    n = len(corpus_entries)
    df: Dict[str, int] = {}
    for e in corpus_entries:
        for t in set(_significant_terms(e["text"])):
            df[t] = df.get(t, 0) + 1
    idf: Dict[str, float] = {}
    for t, f in df.items():
        idf[t] = (n / (1.0 + f)) if f else n
    return idf


_COVERAGE_THRESHOLD = 0.7


def _score_gap_checks(gap_checks: List[dict], big_text: str) -> List[dict]:
    """Evaluate explicit 'gap checks' for a question.

    A gap check asserts an expected identifier/numerical theme that an ideal
    answer to the question should surface. It passes if ANY of its value strings
    appears anywhere in the corpus (any_of semantics). These are specific, exact
    tokens or phrases, so corpus redundancy cannot falsely satisfy them the way
    fuzzy term-overlap can.
    """
    results = []
    for gc in gap_checks or []:
        values = [str(v).lower() for v in gc.get("values", [])]
        if gc.get("type") == "any_of":
            passed = bool(values) and any(v in big_text for v in values)
        else:
            passed = all(not (v in big_text) for v in values)
        results.append({"label": gc.get("label", ""), "passed": passed, "values": values})
    return results


def score_claim(
    claim: dict,
    corpus_entries: List[dict],
    idf: Dict[str, float],
    lowered_entries: List[str],
) -> dict:
    """Score one golden claim against the knowledge base.

    A claim is 'recalled' if some SINGLE knowledge entry covers >= `_COVERAGE_THRESHOLD`
    of the claim's distinctive terms (weighted by IDF) AND contains all of the
    claim's required numbers. Matching against the best single entry (instead of the
    whole merged corpus) avoids the false inflation caused by corpus redundancy.
    """
    terms = _significant_terms(claim["claim"])
    numbers = _numbers_in_claim(claim)
    number_variants = {n: _number_variants(n) for n in numbers}

    best_coverage = 0.0
    best_entry_idx = -1
    matched_counts: Dict[str, int] = {}  # term -> matched

    for idx, e in enumerate(corpus_entries):
        el = lowered_entries[idx]
        # If the claim asserts numbers, the corroborating entry must state them.
        if numbers and not all(any(v in el for v in number_variants[n]) for n in numbers):
            continue
        cov, hits = _entry_coverage(terms, idf, el)
        if cov > best_coverage:
            best_coverage = cov
            best_entry_idx = idx
            matched_counts = hits

    matched_terms = []
    missing_terms = []
    for t in terms:
        if matched_counts.get(t, 0) > 0:
            matched_terms.append(t)
        else:
            missing_terms.append(t)

    matched_nums = []
    missing_nums = []
    if best_entry_idx >= 0:
        bel = lowered_entries[best_entry_idx]
        for n in numbers:
            if any(v in bel for v in number_variants[n]):
                matched_nums.append(n)
            else:
                missing_nums.append(n)
    else:
        missing_nums = list(numbers)

    recalled = (best_coverage >= _COVERAGE_THRESHOLD) and (not numbers or not missing_nums)

    return {
        "claim": claim["claim"],
        "source": claim.get("source", ""),
        "numbers_required": numbers,
        "numbers_matched": matched_nums,
        "numbers_missing": missing_nums,
        "coverage": round(best_coverage, 3),
        "covering_entry": best_entry_idx if best_entry_idx >= 0 else None,
        "matched_terms": matched_terms,
        "missing_terms": missing_terms,
        "recalled": recalled,
    }


def _entry_coverage(terms: List[str], idf: Dict[str, float], entry_lower: str) -> Tuple[float, Dict[str, int]]:
    total = sum(idf.get(t, 1.0) for t in terms) or 1.0
    hits: Dict[str, int] = {}
    matched = 0.0
    for t in terms:
        if t in entry_lower:
            hits[t] = 1
        else:
            # allow a normalized fallback (e.g. plural/tense mismatch)
            if _fuzzy_term(t) in entry_lower or _fuzzy_term(t).rstrip("s") in entry_lower:
                hits[t] = 1
            else:
                hits[t] = 0
        if hits[t]:
            matched += idf.get(t, 1.0)
    return matched / total, hits


def _fuzzy_term(tok: str) -> str:
    return tok.replace("-", " ").replace("_", " ")


def _match_token(token: str, big_text: str) -> bool:
    return token in big_text


def run_eval(
    db_path: Optional[str] = None,
    golden_path: Optional[str] = None,
    include_journal: bool = False,
    include_sources: bool = False,
) -> dict:
    golden = load_golden_set(golden_path)
    corpus = load_knowledge_base(db_path, include_journal, include_sources)
    lowered_entries = [e["text"].lower() for e in corpus]
    big_text = " ".join(lowered_entries)
    idf = _idf_weights(corpus)

    question_results = []
    total_relevant = 0
    total_recalled = 0
    total_numbers = 0
    total_numbers_matched = 0

    gap_results_total = 0
    gap_passed_total = 0

    for q in golden["questions"]:
        claim_results = [score_claim(c, corpus, idf, lowered_entries) for c in q["claims"]]
        gap_results = _score_gap_checks(q.get("gap_checks", []), big_text)
        n_gaps = len(gap_results)
        n_gaps_passed = sum(1 for g in gap_results if g["passed"])
        gap_coverage = (n_gaps_passed / n_gaps) if n_gaps else 1.0

        n_claims = len(claim_results)
        n_recalled = sum(1 for r in claim_results if r["recalled"])

        req_nums = sum(len(r["numbers_required"]) for r in claim_results)
        matched_nums = sum(len(r["numbers_matched"]) for r in claim_results)
        num_acc = (matched_nums / req_nums) if req_nums else 1.0

        claim_recall = (n_recalled / n_claims) if n_claims else 0.0
        composite = 100.0 * (0.7 * claim_recall + 0.3 * num_acc)

        question_results.append({
            "id": q["id"],
            "question": q["question"],
            "n_claims": n_claims,
            "n_recalled": n_recalled,
            "claim_recall": round(claim_recall, 3),
            "numbers_required": req_nums,
            "numbers_matched": matched_nums,
            "number_accuracy": round(num_acc, 3),
            "gap_checks": gap_results,
            "gap_coverage": round(gap_coverage, 3),
            "n_gaps": n_gaps,
            "n_gaps_passed": n_gaps_passed,
            "composite": round(composite, 1),
            "claims": claim_results,
        })

        total_relevant += n_claims
        total_recalled += n_recalled
        total_numbers += req_nums
        total_numbers_matched += matched_nums
        gap_results_total += n_gaps
        gap_passed_total += n_gaps_passed

    overall_recall = (total_recalled / total_relevant) if total_relevant else 0.0
    overall_num_acc = (total_numbers_matched / total_numbers) if total_numbers else 0.0
    overall_composite = 100.0 * (0.7 * overall_recall + 0.3 * overall_num_acc)
    gap_coverage_overall = (gap_passed_total / gap_results_total) if gap_results_total else None

    return {
        "db_path": resolve_db_path(db_path),
        "scope": {
            "include_journal": include_journal,
            "include_sources": include_sources,
        },
        "corpus_entries": len(corpus),
        "corpus_breakdown": _count_types(corpus),
        "questions": question_results,
        "overall": {
            "total_claims": total_relevant,
            "total_recalled": total_recalled,
            "claim_recall": round(overall_recall, 3),
            "numbers_required": total_numbers,
            "numbers_matched": total_numbers_matched,
            "number_accuracy": round(overall_num_acc, 3),
            "gap_checks_total": gap_results_total,
            "gap_checks_passed": gap_passed_total,
            "gap_coverage": round(gap_coverage_overall, 3) if gap_coverage_overall is not None else None,
            "composite": round(overall_composite, 1),
        },
    }


def _count_types(corpus: List[dict]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for e in corpus:
        counts[e["type"]] = counts.get(e["type"], 0) + 1
    return counts


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _fmt_report(data: dict) -> str:
    lines = []
    lines.append("=" * 78)
    lines.append("GROUND-TRUTH QUALITY EVAL (deterministic)")
    lines.append("-" * 78)
    lines.append(f"DB:           {data['db_path']}")
    lines.append(f"Corpus:       {data['corpus_entries']} entries "
                 f"{data['corpus_breakdown']}")
    lines.append("Score formula: composite = 100 * (0.7*claim_recall + 0.3*number_accuracy)")
    lines.append("=" * 78)

    for q in data["questions"]:
        lines.append("")
        lines.append(f"[{q['id']}] {q['question']}")
        gapinfo = ""
        if q.get("n_gaps"):
            gapinfo = (f"  gaps={q['gap_coverage']:.2f} "
                       f"({q['n_gaps_passed']}/{q['n_gaps']})")
        lines.append(f"  composite={q['composite']:5.1f}  "
                     f"claim_recall={q['claim_recall']:.2f} "
                     f"({q['n_recalled']}/{q['n_claims']})  "
                     f"num_acc={q['number_accuracy']:.2f} "
                     f"({q['numbers_matched']}/{q['numbers_required']}){gapinfo}")
        for i, c in enumerate(q["claims"], 1):
            flag = "OK " if c["recalled"] else "MISS"
            numinfo = ""
            if c["numbers_required"]:
                if c["numbers_missing"]:
                    numinfo = f"  [missing nums: {', '.join(c['numbers_missing'])}]"
            cov = c["coverage"]
            lines.append(f"    {flag} cov={cov:.2f} | {c['claim']}{numinfo}")

    o = data["overall"]
    lines.append("")
    lines.append("-" * 78)
    gapinfo = ""
    if o.get("gap_checks_total"):
        gapinfo = (f"  gap_coverage={o['gap_coverage']:.2f} "
                   f"({o['gap_checks_passed']}/{o['gap_checks_total']})")
    lines.append(f"OVERALL  composite={o['composite']:.1f}  "
                 f"claim_recall={o['claim_recall']:.2f} "
                 f"({o['total_recalled']}/{o['total_claims']})  "
                 f"number_accuracy={o['number_accuracy']:.2f} "
                 f"({o['numbers_matched']}/{o['numbers_required']}){gapinfo}")
    if o.get("gap_checks_total"):
        lines.append("\nUncovered expected content (gap checks):")
        for q in data["questions"]:
            for g in q.get("gap_checks", []):
                status = "OK  " if g["passed"] else "MISS"
                lines.append(f"  {status} [{q['id']}] {g['label']}")
    lines.append("=" * 78)
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the ground-truth quality eval.")
    parser.add_argument("--db", help="Path to research.db (read-only access).")
    parser.add_argument("--golden", help="Path to golden_answers.json (default: built-in).")
    parser.add_argument("--json", dest="json_out",
                        help="Also write a JSON report to this path.")
    parser.add_argument("--with-journal", action="store_true",
                        help="Also include every journal finding in the corpus.")
    parser.add_argument("--with-sources", action="store_true",
                        help="Also include source titles/summaries + key claims.")
    args = parser.parse_args(argv)

    db_path = resolve_db_path(args.db)
    if not Path(db_path).exists():
        print(f"[eval] ERROR: database not found: {db_path}", file=os.sys.stderr)
        return 2

    report = run_eval(db_path=db_path, golden_path=args.golden,
                      include_journal=args.with_journal,
                      include_sources=args.with_sources)

    print(_fmt_report(report))

    if args.json_out:
        out = Path(args.json_out)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n[json report written to {out}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())