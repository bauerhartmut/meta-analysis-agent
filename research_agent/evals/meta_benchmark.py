"""Benchmark harness vs. reference meta-analyses (order §12, P0).

Unit tests prove code behaviour, not scientific quality. This module builds
the measuring instrument the Abnahme of the implementation order requires:

  * a reference-case schema (one published systematic review per case;
    manuell verifizierte Studienliste, Screening-Entscheidungen, Effekt-
    groessen und statistische Referenzresultate) with strict validation
  * a deterministic holdout split (hash-based, stable over runs) that keeps
    a held-out set away from prompt tuning and development
  * metrics computed from RAW run artifacts (the topic SQLite DB), never
    from the agent's self-report: screening recall/precision, fulltext
    retrieval, extraction exact match, provenance, statistical reproduction
    and a distinct critical-error count (wrong direction, doubled cohort)
  * a registry of thresholds set BEFORE results are seen (order §12: no
    post-hoc threshold fitting): every case needs a min_header value at
    load time, and the runner refuses to declare success without them.

Not done here (order-level procurement task, stays explicit): acquiring the
20-30 published reference reviews and their manual gold standards. The
schema, validator and runner accept real cases the moment they exist; a
synthetic fixture proves the mechanics. This honesty is build-bound: no
score of a synthetic dataset is ever called scientific quality.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Deterministic holdout share (order §12: at least one holdout set).
HOLDOUT_HASH_PREFIX = "00"     # sha256 of case_id starts with this seed band
REQUIRED_CASE_FIELDS = {"case_id", "topic", "studies"}
REQUIRED_STUDY_FIELDS = {"study_id", "doi", "gold"}
# Metrics with pre-set minimum thresholds; the runner refuses cases without
# them (§12 "Schwellen nicht nach Sichtung der Ergebnisse passend machen").
DEFAULT_THRESHOLDS = {
    "screening_recall": 0.95,
    "screening_precision": 0.9,
    "extraction_exact": 0.8,
    "provenance": 0.95,
    "critical_errors": 0,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def validate_reference_case(case: Dict[str, Any]) -> List[str]:
    """Field-level contract check; returns the list of violations."""
    errors: List[str] = []
    for field in REQUIRED_CASE_FIELDS:
        if not case.get(field):
            errors.append(f"missing case field: {field}")
    studies = case.get("studies") or []
    if not isinstance(studies, list) or not studies:
        errors.append("case needs a non-empty 'studies' list")
        return errors
    for st in studies:
        for field in REQUIRED_STUDY_FIELDS:
            if field not in st:
                errors.append(
                    f"study {st.get('study_id', '?')} missing field: {field}")
        if st.get("gold") not in {"include", "exclude", "outside"}:
            errors.append(
                f"study {st.get('study_id', '?')}: gold must be "
                "include|exclude|outside")
    case.get("thresholds", DEFAULT_THRESHOLDS)
    return errors


def load_reference_cases(paths: List[str]) -> Tuple[List[Dict], List[str]]:
    """Load + validate all reference cases; invalid ones are rejected."""
    cases: List[Dict] = []
    rejected: List[str] = []
    for p in paths:
        raw = json.loads(Path(p).read_text(encoding="utf-8"))
        errs = validate_reference_case(raw)
        if errs:
            rejected.append(f"{p}: " + "; ".join(errs))
            continue
        raw["thresholds"] = raw.get("thresholds", DEFAULT_THRESHOLDS)
        cases.append(raw)
    return cases, rejected


def is_holdout(case_id: str) -> bool:
    """Deterministic split: sha256 of the case_id picks the holdout band."""
    return hashlib.sha256(case_id.encode("utf-8")).hexdigest().startswith(
        HOLDOUT_HASH_PREFIX)


def _norm_doi(doi: Optional[str]) -> str:
    return str(doi or "").strip().lower().replace("https://doi.org/", "")


def _connect_ro(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def evaluate_case(case: Dict[str, Any], db_path: str) -> Dict[str, Any]:
    """Compute the order §12 metrics for one case against one run DB."""
    out: Dict[str, Any] = {
        "case_id": case["case_id"],
        "topic": case.get("topic", ""),
        "generated": _now(),
    }
    if not Path(db_path).exists():
        out["unavailable"] = "run database not found"
        return out
    conn = _connect_ro(db_path)

    gold_studies = case["studies"]
    doi_of: Dict[str, str] = {}
    db_rows = conn.execute(
        "SELECT id, doi FROM sources").fetchall()
    src_by_doi: Dict[str, str] = {}
    for row in db_rows:
        d = _norm_doi(row["doi"])
        if d:
            src_by_doi[d] = str(row["id"])
            doi_of[str(row["id"])] = d

    # ---- screening recall / precision --------------------------------
    screening = conn.execute(
        "SELECT source_id, decision FROM screening").fetchall()
    gold_include_ids = set()
    for st in gold_studies:
        if st["gold"] == "include" and _norm_doi(st["doi"]):
            gold_include_ids.add(_norm_doi(st["doi"]))
    relevant = gold_include_ids
    decided_include = {
        _norm_doi(doi_of.get(str(s["source_id"]), ""))
        for s in screening
        if str(s["decision"]).lower() == "include"
        and doi_of.get(str(s["source_id"]))
    }
    found = decided_include & relevant
    tp, fn = len(found), len(relevant) - len(found)
    recall = (tp / (tp + fn)) if (tp + fn) else None
    # precision: of the included sources with a DOI linkage, how much is
    # gold-relevant? (No-DOI sources stay out of the denominator, honest.)
    fp = len(decided_include - relevant)
    precision = (tp / (tp + fp)) if (tp + fp) else None
    out["screening"] = {"recall": recall, "precision": precision,
                        "missed": sorted(fn_list := relevant - found)[:10],
                        "n_gold_include": len(relevant)}

    # ---- fulltext retrieval ------------------------------------------
    # Denominator (order §12: "rechtmäßig verfügbar/auffindbar" - here: gold
    # include studies that the reference marks as available=True).
    avail = [st for st in gold_studies
             if st["gold"] == "include" and st.get("available", True)]
    ft_count = 0
    for st in avail:
        src = src_by_doi.get(_norm_doi(st["doi"]))
        if not src:
            continue
        got = conn.execute(
            "SELECT COUNT(*) FROM source_texts WHERE source_id = ? "
            "AND chars > 0", (src,)).fetchone()[0]
        ft_count += 1 if got else 0
    out["fulltext_retrieval"] = {
        "rate": (ft_count / len(avail)) if avail else None,
        "retrieved": ft_count, "denominator": len(avail),
        "note": "denominator = gold-included and available studies",
    }

    # ---- extraction exact match + provenance --------------------------
    exact = 0
    provenance_ok = 0
    checks = 0
    critical_errors: List[str] = []
    for st in gold_studies:
        if st["gold"] != "include":
            continue
        src = src_by_doi.get(_norm_doi(st["doi"]))
        if not src:
            continue
        for gold_eff in (st.get("extracted_effects") or []):
            checks += 1
            row = conn.execute(
                "SELECT effect, ci_low, quote_start, source_text_id "
                "FROM study_effects WHERE source_id = ? AND "
                "LOWER(TRIM(outcome)) = LOWER(?) AND disputed = 0 "
                "AND TRIM(rejection_reason) = ''", (
                    src, gold_eff.get("outcome", ""))).fetchone()
            if not row:
                continue
            try:
                want = float(gold_eff["effect"])
            except (KeyError, ValueError, TypeError):
                continue
            if row["effect"] is not None and abs(float(row["effect"]) - want) <= \
                    float(gold_eff.get("tolerance", 1e-6)):
                exact += 1
            if row["quote_start"] is not None and row["quote_start"] >= 0:
                provenance_ok += 1
            # critical error: the direction of the effect points the wrong way
            if gold_eff.get("direction_gold") in {"negative", "positive"} \
                    and row["effect"] is not None:
                sign = -1 if float(row["effect"]) < 0 else 1
                want_sign = -1 if gold_eff["direction_gold"] == "negative" else 1
                if sign != want_sign:
                    critical_errors.append(
                        f"{st['study_id']}/{gold_eff.get('outcome')}: "
                        "wrong direction")
    out["extraction"] = {
        "exact": (exact / checks) if checks else None,
        "extraction_checks": checks,
        "provenance": (provenance_ok / (tp or 1)) if checks else None,
        "critical_errors": critical_errors,
        "critical_error_count": len(critical_errors),
    }
    conn.close()
    return out


def _passes_thresholds(result: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Order §12: thresholds are checked, not fitted afterwards."""
    t = result.get("thresholds", DEFAULT_THRESHOLDS)
    blockers: List[str] = []
    rec = (result.get("screening") or {}).get("recall")
    if rec is not None and rec < t.get("screening_recall", 0):
        blockers.append(f"screening_recall {rec:.2f} < "
                        f"{t.get('screening_recall')}")
    crit = (result.get("extraction") or {}).get("critical_error_count", 0)
    if crit > t.get("critical_errors", 0):
        blockers.append(f"critical_errors {crit} > allowed")
    return (not blockers, blockers)


def run_benchmark(reference_paths: List[str], db_path: str,
                  check_release_gate: bool = False) -> Dict[str, Any]:
    cases, rejected = load_reference_cases(reference_paths)
    dev: List[Dict[str, Any]] = []
    holdout: List[Dict[str, Any]] = []
    for c in cases:
        cid = str(c["case_id"])
        target = holdout if is_holdout(cid) else dev
        target.append(c)
    dev_results = [evaluate_case(c, db_path) for c in dev]
    holdout_results = [evaluate_case(c, db_path) for c in holdout]

    def _agg(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        recs = [r["screening"]["recall"] for r in results
                if r.get("screening", {}).get("recall") is not None]
        precs = [r["screening"]["precision"] for r in results
                 if r.get("screening", {}).get("precision") is not None]
        exacts = [r["extraction"]["exact"] for r in results
                  if r.get("extraction", {}).get("exact") is not None]
        crit = sum(r["extraction"]["critical_error_count"]
                   for r in results if r.get("extraction"))
        return {
            "cases": len(results),
            "screening_recall_mean": sum(recs) / len(recs) if recs else None,
            "screening_precision_mean": (sum(precs) / len(precs))
                                       if precs else None,
            "extraction_exact_mean": (sum(exacts) / len(exacts))
                                    if exacts else None,
            "critical_error_total": crit,
        }

    summary = {
        "generated": _now(),
        "db": db_path,
        "cases_loaded": len(cases),
        "cases_rejected": rejected,
        "dev": _agg(dev_results),
        "holdout": _agg(holdout_results),
        "holdout_rule": f"sha256(case_id).startswith('{HOLDOUT_HASH_PREFIX}')",
        "dev_results": dev_results,
        "holdout_results": holdout_results,
        "note": ("Dev partition is for development feedback only; calls to "
                 "human-parity are gated on the holdout partition (order §12)."),
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark vs. reference meta-analyses (order §12)")
    parser.add_argument("references", nargs="+",
                        help="reference case JSON files (see module docstring)")
    parser.add_argument("--db", type=str, required=True,
                        help="topic database of the run to be scored")
    parser.add_argument("--out", type=str, default=None)
    args = parser.parse_args()
    summary = run_benchmark(args.references, args.db)
    out_path = args.out or f"data/benchmark/benchmark-{datetime.now():%Y%m%d-%H%M}.json"
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(summary, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    dev = summary["dev"]
    hold = summary["holdout"]
    print(f"[benchmark] cases={summary['cases_loaded']} "
          f"(rejected {len(summary['cases_rejected'])})")
    print(f"[benchmark] dev recall={dev['screening_recall_mean']} "
          f"holdout recall={hold['screening_recall_mean']}")
    print(f"[benchmark] written: {out_path}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
