"""Study-level data model (order Phase 2 / §5): publications vs. studies.

A publication is not a study. Several publications can describe the same
cohort (multi-paper reporting of one trial), and one publication can contain
several studies/outcomes. The model is additive (no schema break): existing
tables keep working; ``study_effects« carries an additive ``study_id`` column
(the empty string means "assignment unknown and unclaimed", never "no
dependency") and a registry keeps every assignment reversible and auditable.
No assignment is automatic: candidates are stored with a rationale and a
status, never silently merged (order §5.2).
"""

from __future__ import annotations

import json
import logging
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def ensure_study_schema(db) -> None:
    """Additive migrations for the study-level model; idempotent."""
    with db._conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta_publications (
                publication_id TEXT PRIMARY KEY,
                doi TEXT DEFAULT '',
                pmid TEXT DEFAULT '',
                title TEXT DEFAULT '',
                year INTEGER DEFAULT 0,
                journal TEXT DEFAULT '',
                source_id TEXT DEFAULT '',
                study_id TEXT DEFAULT '',
                link_reason TEXT DEFAULT '',
                created_at TEXT DEFAULT ''
            );
            """)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta_studies (
                study_id TEXT PRIMARY KEY,
                first_publication_doi TEXT DEFAULT '',
                design TEXT DEFAULT '',
                recruitment TEXT DEFAULT '',
                setting TEXT DEFAULT '',
                follow_up TEXT DEFAULT '',
                created_at TEXT DEFAULT ''
            );
            """)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta_overlap_candidates (
                id TEXT PRIMARY KEY,
                study_id_a TEXT DEFAULT '',
                study_id_b TEXT DEFAULT '',
                doi_a TEXT DEFAULT '',
                doi_b TEXT DEFAULT '',
                reason TEXT DEFAULT '',
                status TEXT DEFAULT 'candidate',
                rationale TEXT DEFAULT '',
                decided_by TEXT DEFAULT '',
                created_at TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            );
            """)
        # additive column on the existing table (kept inside a try: column
        # already existing on older DBs is the normal path, not an error).
        try:
            conn.execute("ALTER TABLE study_effects ADD COLUMN "
                         "study_id TEXT DEFAULT ''")
            logger.info("study_effects: added additive column study_id")
        except sqlite3.OperationalError:
            pass
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_study_effects_study "
            "ON study_effects(study_id)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_meta_publications_doi "
            "ON meta_publications(doi)")


def register_study(db, study_id: str, first_publication_doi: str = "",
                   design: str = "", recruitment: str = "",
                   setting: str = "", follow_up: str = "") -> None:
    with db._conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO meta_studies
                    (study_id, first_publication_doi, design, recruitment,
                     setting, follow_up, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))""",
            (study_id, first_publication_doi, design, recruitment,
             setting, follow_up))
    # the DB helper writes timestamps differently; created_at stays ISO
    # through the generic stores below when a run needs it.


def register_publication(db, publication_id: str, doi: str = "",
                         pmid: str = "", title: str = "", year: int = 0,
                         journal: str = "", source_id: str = "") -> None:
    with db._conn() as conn:
        conn.execute(
            """INSERT OR IGNORE INTO meta_publications
                    (publication_id, doi, pmid, title, year, journal,
                     source_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))""",
            (publication_id, doi, pmid, title, int(year or 0), journal,
             source_id))


def link_publication_to_study(db, publication_id: str, study_id: str,
                              reason: str) -> None:
    """Publication -> study link. MUST carry a rationale (order §5.2)."""
    if not reason.strip():
        raise ValueError("link requires a documented rationale")
    with db._conn() as conn:
        conn.execute(
            """UPDATE meta_publications
               SET study_id = ?, link_reason = ?
               WHERE publication_id = ?""",
            (study_id, reason, publication_id))
        conn.execute(
            """UPDATE study_effects SET study_id = ?
               WHERE source_id = (SELECT source_id FROM meta_publications
                                  WHERE publication_id = ?)
                 AND study_id = ''""",
            (study_id, publication_id))


def mark_overlap_candidate(db, study_id_a: str, study_id_b: str,
                           doi_a: str = "", doi_b: str = "",
                           reason: str = "") -> str:
    """Register a *possible* cohort overlap. Never resolves automatically."""
    import uuid
    cid = uuid.uuid4().hex[:12]
    with db._conn() as conn:
        conn.execute(
            """INSERT INTO meta_overlap_candidates
                    (id, study_id_a, study_id_b, doi_a, doi_b, reason,
                     status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'candidate', datetime('now'))""",
            (cid, study_id_a, study_id_b, doi_a, doi_b, reason))
    return cid


def resolve_overlap(db, candidate_id: str, status: str,
                    rationale: str, decided_by: str) -> bool:
    """Human or fully-evidenced resolution only; the status list is fixed."""
    if status not in {"confirmed_same_cohort", "separate_cohorts",
                      "needs_more_evidence"}:
        raise ValueError("overlap resolution status not allowed")
    if not rationale.strip() or not decided_by.strip():
        raise ValueError("resolution requires rationale and decided_by")
    with db._conn() as conn:
        cur = conn.execute(
            """UPDATE meta_overlap_candidates
               SET status = ?, rationale = ?, decided_by = ?,
                   updated_at = datetime('now')
               WHERE id = ?""",
            (status, rationale, decided_by, candidate_id))
        return cur.rowcount > 0


def overlap_open_counts(db) -> Dict[str, int]:
    with db._conn() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) FROM meta_overlap_candidates "
            "GROUP BY status").fetchall()
    return {str(r[0]): int(r[1]) for r in rows}
