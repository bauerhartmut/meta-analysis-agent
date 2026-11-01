"""Independent reviewer roles (order Phase 3 / §6).

Rollen sind logische Pruefaufgaben mit getrennten Eingaben, strukturierten
Outputs und begrenztem Budget. Nothing here invents numbers: the Statistical
Reviewer reports validity rule violations only, the Decision Resolver class-
ifies existing double-extraction disputes either by the original evidence or
by escalation - never by majority, never by averaging.

Structured output fields per role (order §6): decision, evidence, rationale,
confidence, unresolved_questions. All outputs are written to ``review_reports``
unchanged (immutable versioning), so every adjudication is traceable.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

REPORT_VERSION = "reviewer-roles/1"


@dataclass
class RoleReport:
    """One structured review update (order §6 field set)."""
    role: str
    decision: str
    evidence: str = ""
    rationale: str = ""
    confidence: float = 0.0
    unresolved_questions: List[str] = field(default_factory=list)
    detail: Optional[Dict[str, Any]] = None
    version: str = REPORT_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "decision": self.decision,
            "evidence": self.evidence,
            "rationale": self.rationale,
            "confidence": self.confidence,
            "unresolved_questions": self.unresolved_questions,
            "detail": self.detail or {},
            "version": self.version,
        }


# -------------------------------------------------------------------------
# Extractor A/B independence (order §6: B never sees A)
# -------------------------------------------------------------------------

def extractor_independence_check(messages_second_pass: Sequence[dict],
                                 first_pass_values: Sequence[str]) -> List[str]:
    """Contract audit: the second pass's messages must not carry A's values.

    Called with the raw message list another pass would see and the string
    values the first pass produced. Returns violations (empty list = pass).
    The EffectExtractor builds both passes from the document alone, so this
    check fails loudly (test-side) the moment anyone wires A's results into
    B's context - no silent contract change.
    """
    joined = "\n".join(
        str(m.get("content") or "") for m in messages_second_pass
    ).lower()
    viol: List[str] = []
    for value in first_pass_values:
        v = str(value or "").strip().lower()
        if len(v) >= 8 and v in joined:
            viol.append(v)
    return viol


# -------------------------------------------------------------------------
# Statistical Reviewer (order §6: no free-hand computation)
# -------------------------------------------------------------------------

def statistical_review(rows: Sequence[Dict]) -> RoleReport:
    """Validity rules only - reports findings, computes nothing.

    Rules mirror meta.extraction.check_plausibility plus the dependency
    question (§5.2/§7.2): every finding names the row and the rule that
    failed. Decision = 'no_statistical_findings' or 'findings_reported'.
    """
    findings: List[Dict[str, Any]] = []
    for row in rows:
        rid = str(row.get("id") or "?")
        eff = row.get("effect")
        se = row.get("se")
        lo, hi = row.get("ci_low"), row.get("ci_high")
        # a standard error of zero or less makes the estimate weightless
        if se is not None and float(se) <= 0:
            findings.append({"row": rid, "rule": "se_nonpositive"})
        # CI bounds inverted or not containing the point estimate
        if (lo is not None and hi is not None
                and float(lo) > float(hi)):
            findings.append({"row": rid, "rule": "ci_inverted"})
        if (lo is not None and hi is not None and eff is not None
                and not (float(lo) <= float(eff) <= float(hi))):
            findings.append({"row": rid, "rule": "effect_outside_ci"})
        # ratio families cannot carry non-positive values
        if str(row.get("effect_type") or "").lower() in {"or", "rr", "hr"} \
                and eff is not None and float(eff) <= 0:
            findings.append({"row": rid, "rule": "ratio_nonpositive"})
        # correlations stay within [-1, 1]
        if str(row.get("effect_type") or "").lower() == "r" \
                and eff is not None and not (-1.0 <= float(eff) <= 1.0):
            findings.append({"row": rid, "rule": "correlation_out_of_range"})
    return RoleReport(
        role="statistical_reviewer",
        decision=("no_statistical_findings" if not findings
                  else "findings_reported"),
        evidence="; ".join(f"{f['row']}:{f['rule']}" for f in findings) or "",
        rationale=("rule-based validity checks on stored rows; no values "
                   "recalculated"),
        confidence=1.0 if findings else 0.9,
        unresolved_questions=(
            ["statistical reviewer found rule violations - check the "
             "extraction at the original document before pooling"]
            if findings else []),
        detail={"findings": findings},
    )


# -------------------------------------------------------------------------
# Decision Resolver (order §6: fieldwise, evidence or escalation)
# -------------------------------------------------------------------------

def _verified(row: Dict) -> bool:
    # quote_start >= 0 AND a stored text id: the reading is anchored to the
    # document; the pool already refuses unverifiable readings on its own.
    return (row.get("quote_start", -1) is not None
            and int(row.get("quote_start", -1)) >= 0
            and str(row.get("source_text_id") or "").strip() != "")


def resolve_disputes(db, rows: Sequence[Dict]) -> Tuple[RoleReport, int]:
    """Classify double-extraction disputes fieldwise; store reports.

    Classification rules (order §6):
      * exactly one reading verifiable at the original evidence -> resolved
        (the verifiable reading carries the number; the other fades out of
        the pool by its own unverifiable status; nothing is averaged)
      * both verified but differing -> methodical discretion question, ESCALATED
      * neither verified -> ESCALATED (original evidence cannot decide)
    Disputes never merge and no third value is invented; the report layer is
    documentation, not a data change.
    """
    disputed = [r for r in rows if int(r.get("disputed") or 0) == 1]
    findings: List[Dict[str, Any]] = []
    escalations = 0
    groups: Dict[Tuple[str, str], List[Dict]] = {}
    for row in disputed:
        key = (str(row.get("outcome") or ""), str(row.get("comparison") or ""))
        groups.setdefault(key, []).append(row)
    for (outcome, comparison), sched in groups.items():
        verified = [r for r in sched if _verified(r)]
        if len(verified) == 1:
            other = [r for r in sched if not _verified(r)]
            findings.append({
                "outcome": outcome, "comparison": comparison,
                "resolution": "resolved_by_original_evidence",
                "kept_row": verified[0].get("id"),
                "dropped_rows": [r.get("id") for r in other],
                "evidence": str(verified[0].get("quote") or "")[:160],
            })
        else:
            escalations += len(sched)
            findings.append({
                "outcome": outcome, "comparison": comparison,
                "resolution": "escalated",
                "rows": [r.get("id") for r in sched],
                "reason": ("beide Lesungen am Original verifiziert - "
                           "methodische Ermessensfrage" if len(verified) > 1
                           else "keine der Lesungen am Original verifizierbar"),
                "unresolved_questions": [
                    "am Originaldokument entscheiden, welche Lesung die "
                    "korrekte Zahlen/Y-Bedingung trägt"],
            })
    report = RoleReport(
        role="decision_resolver",
        decision=("ro_disputes_resolved" if findings else
                  ("escalated" if escalations else "no_disputes")),
        evidence="; ".join(f.get("evidence") or "" for f in findings)[:400],
        rationale=("fieldwise; never averaged; resolved only where the "
                   "original evidence is unambiguous, otherwise escalated"),
        confidence=0.9 if findings and escalations == 0 else 0.6,
        unresolved_questions=[f"dispute {f['outcome']} escalated"
                              for f in findings
                              if f["resolution"] == "escalated"],
        detail={"resolutions": findings, "version": REPORT_VERSION},
    )
    _store_reports(db, [report])
    return report, escalations


def _store_reports(db, reports: Sequence[RoleReport]) -> None:
    """Immutable review-report store (order §6: outputs versioned)."""
    import uuid
    with db._conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS review_reports (
                id TEXT PRIMARY KEY,
                role TEXT DEFAULT '',
                decision TEXT DEFAULT '',
                evidence TEXT DEFAULT '',
                rationale TEXT DEFAULT '',
                confidence REAL DEFAULT 0.0,
                unresolved_questions TEXT DEFAULT '[]',
                detail TEXT DEFAULT '{}',
                version TEXT DEFAULT '',
                created_at TEXT DEFAULT ''
            );
            """)
        for r in reports:
            conn.execute(
                """INSERT INTO review_reports
                        (id, role, decision, evidence, rationale, confidence,
                         unresolved_questions, detail, version, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
                (uuid.uuid4().hex, r.role, r.decision, r.evidence, r.rationale,
                 r.confidence,
                 json.dumps(r.unresolved_questions, ensure_ascii=False),
                 json.dumps(r.detail or {}, ensure_ascii=False), r.version))


import json  # kept at file end on purpose: no top-level circularity


def review_segment(db, rows: Sequence[Dict]):
    """Run the independent-review segment over one source's stored rows.

    Both reports (statistical reviewer, decision resolver) are stored;
    returns (statistical_report, resolver_report, escalations).
    """
    stats = statistical_review(rows)
    _store_reports(db, [stats])
    resolved, escalations = resolve_disputes(db, rows)
    return stats, resolved, escalations
