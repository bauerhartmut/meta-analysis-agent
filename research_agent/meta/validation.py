"""Phase 7: scientific validation layer over the finished corpus.

Everything here is deterministic over stored data - no LLM call, no fitted
threshold. It re-verifies the machine's own evidence chain (effect quotes
against the stored document text), counts what the pipeline already refuses
to pool (disputed rows) and measures the RoB coverage of the effect corpus.
The verdict is a release-gate status, stored append-only:

- BLOCKED: a hard finding - a stored quote is no longer reproducible or a
  number exists without its verbatim evidence. Such a run must not claim
  machine-validated status.
- NEEDS_REVIEW: warnings only - coverage gaps the pipeline would fill with
  more run time (e.g. sources with effects but no bias assessment yet).
- MACHINE_VALIDATED: no blocker, no warning.
- DRAFT: no verdict recorded yet.

Every entry in blockers or warnings carries a machine-readable ``rule`` and
a German ``detail`` sentence naming what was checked - never a judgement
beyond the data.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
import sqlite3
import uuid as _uuid
from typing import Dict, List, Tuple

VERSION = "validation/1"

STATUS_DRAFT = "draft"
STATUS_NEEDS_REVIEW = "needs_review"
STATUS_BLOCKED = "blocked"
STATUS_MACHINE_VALIDATED = "machine_validated"

# Bounded work: re-reading document bodies is cheap but not free; the check
# samples the stored rows in creation order. Rows beyond the cap stay
# counted, never silently dropped. 500 covers whole real corpora (the
# exercise baseline has 129 rows) - the cap only guards future runs.
_MAX_QUOTE_VERIFICATIONS = 500


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _text_for(db, text_id: str) -> str:
    if not text_id:
        return ""
    try:
        return db.read_source_text(str(text_id)) or ""
    except Exception:
        return ""


def _verify_effect_quotes(
    db, limit: int = _MAX_QUOTE_VERIFICATIONS
) -> Tuple[List[dict], List[dict], Dict[str, int]]:
    """Re-check stored effect quotes against the stored document text.

    The invariant mirrors the extractor exactly: a row's (quote, span) pair
    must be reproducible with the same verifier (locate_quote) over the
    stored document body - corruption, migration damage or a lost document
    surfaces here, not inside a pooled claim.

    The contract check rides on top: a row WITHOUT a verbatim span must
    never be poolable (the POOLABLE filter has no quote term yet - Phase 7
    names that violation instead of silently scoring past it).
    """
    try:
        from .extraction import locate_quote  # the same verifier
    except Exception:  # pragma: no cover - verifier plumbing broken
        locate_quote = None

    blockers: List[dict] = []
    warnings: List[dict] = []
    counts: Dict[str, int] = {"total": 0, "checked": 0, "unsupported": 0,
                              "unquoted_poolable": 0}
    try:
        counts["total"] = int(db.count_study_effects() or 0)
        rows = db.get_study_effects(limit=limit) or []
    except Exception as e:  # a broken effect store cannot pass silently
        offenders = [{
            "rule": "effect_store_unreadable", "ids": [],
            "detail": f"Effekt-Store nicht lesbar: {e}",
        }]
        return offenders, [], counts
    counts["checked"] = len(rows)
    poolable = ("COALESCE(disputed, 0) = 0 "
                "AND COALESCE(rejection_reason, '') = '' "
                "AND (se IS NOT NULL "
                "OR (ci_low IS NOT NULL AND ci_high IS NOT NULL))")
    for row in rows:
        ids = [str(row.get("id") or "")]
        quote = str(row.get("quote") or "")
        text = _text_for(db, str(row.get("source_text_id") or ""))
        start = int(row.get("quote_start") or -1)
        end = int(row.get("quote_end") or -1)
        is_poolable = (int(row.get("disputed") or 0) == 0
                       and not str(row.get("rejection_reason") or "")
                       and (row.get("se") is not None
                            or (row.get("ci_low") is not None
                                and row.get("ci_high") is not None)))
        if start < 0 or end <= start:
            counts["unsupported"] += 1
            if is_poolable:
                counts["unquoted_poolable"] += 1
                blockers.append({
                    "rule": "poolable_effect_without_verbatim_quote",
                    "ids": ids,
                    "detail": "Eine poolbare Effektzeile (disputed=0, "
                              "Präzision vorhanden) trägt keinen "
                              "verifizierten Zitatbereich - kein Wert "
                              "ohne wörtlichen Beleg.",
                })
            continue
        if not text:
            # A lost body cannot be re-verified. It only violates the gate
            # when the NUMBER is still live for pooling; rows the pipeline
            # already rejected stay warnings - their release harm is nil.
            entry = {
                "ids": ids,
                "detail": "Effektzitat nicht verifizierbar: der "
                          "Dokumenttext fehlt im Store.",
            }
            if is_poolable:
                entry["rule"] = "poolable_quote_text_missing"
                blockers.append(entry)
            else:
                entry["rule"] = "unverifiable_but_not_poolable"
                warnings.append(entry)
            continue
        if locate_quote is not None:
            span = locate_quote(text, quote)
            span_ok = span is not None and (span.start, span.end) == (start, end)
        else:
            span_ok = text[start:end] == quote
        if not span_ok:
            blockers.append({
                "rule": "quote_mismatch",
                "ids": ids,
                "detail": "Gespeicherte Zitat-Span reproduziert nicht "
                          "mit demselben Verifikator (Text neu indexiert "
                          "oder Doppeleintrag beschädigt).",
            })
    return blockers, warnings, counts


def _disputed_effect_counts(db) -> Tuple[Dict[str, int], List[dict]]:
    """Disputed/rejected rows exist to be excluded from pooling (POOLABLE).

    The layer does not re-judge them - it counts what exists so the release
    gate can show the pipeline state honestly.
    """
    counts: Dict[str, int] = {"disputed": 0, "rejected": 0}
    try:
        rows = db.get_study_effects() or []
    except Exception:
        return counts, []
    for row in rows:
        if int(row.get("disputed") or 0):
            counts["disputed"] += 1
        if str(row.get("rejection_reason") or ""):
            counts["rejected"] += 1
    return counts, []


def _rob_coverage(db) -> Tuple[List[dict], Dict[str, int]]:
    """Coverage gap: sources with effects but no bias assessment yet.

    The RoB machine runs after effect extraction; until then the gap is a
    warning - the report still names it instead of assuming anything.
    """
    warnings: List[dict] = []
    counts: Dict[str, int] = {"without_rob": 0}
    try:
        # The store method's LIMIT 0 returns no rows (limit is a cap, not
        # "unbounded"): the coverage count needs a real, generous cap.
        pending = (db.get_sources_with_effects_without_bias(limit=100000)
                   or [])
        counts["without_rob"] = len(pending)
    except Exception as e:
        warnings.append({
            "rule": "rob_coverage_unreadable", "ids": [],
            "detail": f"RoB-Abdeckung nicht prüfbar: {e}",
        })
    return warnings, counts


def release_gate_status(blockers: List[dict], warnings: List[dict]) -> str:
    if blockers:
        return STATUS_BLOCKED
    if warnings:
        return STATUS_NEEDS_REVIEW
    return STATUS_MACHINE_VALIDATED


def run_validation(db) -> dict:
    """Run every deterministic check and grade one release-gate status."""
    quote_blockers, quote_warnings, quote_counts = _verify_effect_quotes(db)
    if int(quote_counts.get("checked") or 0) < int(
            quote_counts.get("total") or 0):
        quote_warnings.append({
            "rule": "quote_check_capped",
            "ids": [],
            "detail": f"Es wurden nur {quote_counts['checked']} von "
                      f"{quote_counts['total']} Effektzeilen auf Beleg "
                      "verifiziert (Kappung produktiv gewählt).",
        })
    disputed_counts, disputed_warnings = _disputed_effect_counts(db)
    rob_warnings, rob_counts = _rob_coverage(db)
    if rob_counts.get("without_rob"):
        rob_warnings.append({
            "rule": "effects_without_rob",
            "ids": [],
            "detail": f"{rob_counts['without_rob']} Quelle(n) mit "
                      "Effektzeilen haben noch keine maschinelle "
                      "Risk-of-Bias-Lektüre.",
        })
    warnings = list(quote_warnings) + list(disputed_warnings) + list(
        rob_warnings)
    checks = {
        "effect_quotes": quote_counts,
        "disputed": disputed_counts,
        "rob_coverage": rob_counts,
    }
    return {
        "version": VERSION,
        "created_at": _now(),
        "blockers": quote_blockers,
        "warnings": warnings,
        "checks": checks,
        "status": release_gate_status(quote_blockers, warnings),
    }


def record_validation(db, result: dict) -> dict:
    """Append the verdict into the topic database (append-only)."""
    row = {
        "id": _uuid.uuid4().hex,
        "status": result.get("status") or "",
        "version": result.get("version") or "",
        "blockers": _json(result.get("blockers") or []),
        "warnings": _json(result.get("warnings") or []),
        "checks": _json(result.get("checks") or {}),
        "created_at": result.get("created_at") or _now(),
    }
    db.save_validation_result(row)
    return row


class _ReadOnlyAdapter:
    """Cursor-level adapter handing run_validation the ro methods it needs.

    topic databases must never be written just for a verdict - measurement
    stays read-only on every database in the project, matching the rule the
    metrics CLI already follows. Real databases keep the document body in
    fulltext/ files rather than the row: read_source_text mirrors
    Database.read_source_text's file loading so quotes verify identically.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(
            f"file:{Path(db_path).as_posix()}?mode=ro", uri=True, timeout=30)
        self.conn.row_factory = sqlite3.Row

    def _fetch(self, sql: str, params: Tuple = ()) -> List[dict]:
        try:
            rows = self.conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            return []
        return [dict(r) for r in rows]

    def count_study_effects(self) -> int:
        rows = self._fetch("SELECT COUNT(*) AS n FROM study_effects")
        return int(rows[0]["n"]) if rows else 0

    def get_study_effects(self, source_id: str = "", outcome: str = "",
                          limit: int = 0) -> List[dict]:
        sql = "SELECT * FROM study_effects ORDER BY created_at"
        if limit:
            sql += f" LIMIT {int(limit)}"
        return self._fetch(sql)

    def read_source_text(self, text_id: str) -> str:
        rows = self._fetch(
            "SELECT text, path FROM source_texts WHERE id = ?", (text_id,))
        if not rows:
            return ""
        row = rows[0]
        rel_path = str(row["path"] or "")
        if rel_path:
            target = Path(self.db_path).parent / rel_path
            try:
                return target.read_text(encoding="utf-8")
            except OSError:
                return ""
        return str(row["text"] or "")

    def get_sources_with_effects_without_bias(
            self, min_relevance: float = 0.25, limit: int = 10) -> List[dict]:
        return self._fetch(
            "SELECT s.id FROM sources s WHERE EXISTS ("
            "SELECT 1 FROM study_effects e WHERE e.source_id = s.id) "
            "AND NOT EXISTS (SELECT 1 FROM risk_of_bias r "
            "WHERE r.source_id = s.id)")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Deterministische wissenschaftliche Validierung "
                    "(Freigabe-Gate, readonly)")
    parser.add_argument("db", help="Topic-DB, die validiert wird")
    args = parser.parse_args(argv)
    adapter = _ReadOnlyAdapter(args.db)
    result = run_validation(adapter)
    print(_json(result))
    return 0 if result["status"] != STATUS_BLOCKED else 2


if __name__ == "__main__":
    raise SystemExit(main())
