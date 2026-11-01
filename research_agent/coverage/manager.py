"""Fulltext coverage manager for systematic-review / meta-analysis runs.

Tracks, per identified study (DOI), where it stands in the legal
acquisition -> fulltext -> extraction chain. The manager never fetches
anything from the network itself; acquisition happens in
``scripts/fulltext_acquisition.py`` under the same licence rules. Its two
jobs once integrated into the agent:

1. Serve local inbox files (``data/fulltext_inbox/<doi>.xml|.pdf``) before
   any network fulltext attempt is made elsewhere (orchestrator hook).
2. Compute coverage numbers for the dashboard (fulltext, manual backlog,
   author requests, extraction state).

Tables are additive (CREATE IF NOT EXISTS) and never touch existing ones.
"""

from __future__ import annotations

import html
import json
import logging
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# The canonical workflow states (Auftrag §2). Older acquisition-script
# statuses (DISCOVERED, MANUAL_REQUIRED, LICENSE_UNCLEAR, FAILED, ...) map
# straight onto this list.
STATUSES = [
    "DISCOVERED",
    "ABSTRACT_AVAILABLE",
    "FULLTEXT_SEARCHING",
    "OPEN_ACCESS_AVAILABLE",
    "LICENSE_VERIFIED",
    "DOWNLOADED",
    "MANUAL_REQUIRED",
    "AUTHOR_REQUEST_PENDING",
    "AUTHOR_VERSION_RECEIVED",
    "DATA_EXTRACTED",
    "DATA_VALIDATED",
    "EXCLUDED",
    "LICENSE_UNCLEAR",
    "FAILED",
]

FULLTEXT_STATUSES = {"DOWNLOADED", "AUTHOR_VERSION_RECEIVED"}
TERMINAL_BAD = {"MANUAL_REQUIRED", "LICENSE_UNCLEAR", "FAILED", "EXCLUDED"}

_INBOX_DIRNAME = "fulltext_inbox"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _xml_to_text(raw: str) -> str:
    """PMC/Europe-PMC XML -> plain text with paragraph breaks kept."""
    # Drop reference lists and tables: they explode into noise, not evidence.
    raw = re.sub(r"<ref-list[\s\S]*?</ref-list>", " ", raw, flags=re.I)
    raw = re.sub(r"<table-wrap[\s\S]*?</table-wrap>", "[table omitted] ", raw, flags=re.I)
    raw = re.sub(r"</(p|div|title|sec|h\d)>", "\n\n", raw, flags=re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(raw)
    text = re.sub(r"[ \t\r]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    # Superfluous unpaired whitespace again after the rewrites.
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _pdf_to_text(path: Path) -> Optional[str]:
    try:
        import io

        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(path.read_bytes()))
        parts = [(page.extract_text() or "") for page in reader.pages]
        return "\n\n".join(p.strip() for p in parts if p.strip()) or None
    except Exception as e:  # a broken PDF is never a crashed cycle
        logger.debug(f"Could not read inbox PDF {path.name}: {e}")
        return None


class CoverageManager:
    """Own connection on the same topic DB; all schema changes additive."""

    def __init__(self, db_path: str, inbox_dir: Optional[str] = None):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
        self._conn.row_factory = sqlite3.Row
        if inbox_dir:
            self.inbox_dir = Path(inbox_dir)
        else:
            # Mirror the acquisition script's layout: <data>/fulltext_inbox.
            self.inbox_dir = (Path(db_path).parent / _INBOX_DIRNAME) if db_path != ":memory:" else Path("data") / _INBOX_DIRNAME
        self._ensure_tables()

    # ------------------------------------------------------------------ #
    # Schema (additive only)
    # ------------------------------------------------------------------ #
    def _ensure_tables(self) -> None:
        cur = self._conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS studies (
                doi TEXT PRIMARY KEY,
                title TEXT DEFAULT '',
                authors TEXT DEFAULT '[]',
                year INTEGER DEFAULT 0,
                journal TEXT DEFAULT '',
                pmid TEXT DEFAULT '',
                pmcid TEXT DEFAULT '',
                oa_status TEXT DEFAULT '',
                manuscript_version TEXT DEFAULT '',
                license TEXT DEFAULT '',
                has_fulltext INTEGER DEFAULT 0,
                acquisition_source TEXT DEFAULT '',
                extraction_status TEXT DEFAULT '',
                endpoints_available INTEGER DEFAULT 0,
                excluded_reason TEXT DEFAULT '',
                status TEXT DEFAULT 'DISCOVERED',
                priority REAL DEFAULT 0.0,
                source_id TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS studies_status_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doi TEXT DEFAULT '',
                status TEXT DEFAULT '',
                reason TEXT DEFAULT '',
                actor TEXT DEFAULT 'agent',
                created_at TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS author_requests (
                id TEXT PRIMARY KEY,
                doi TEXT DEFAULT '',
                authors TEXT DEFAULT '[]',
                to_email TEXT DEFAULT '',
                institution TEXT DEFAULT '',
                draft_text TEXT DEFAULT '',
                status TEXT DEFAULT 'pending_user_approval',
                approved_at TEXT DEFAULT '',
                received_at TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT ''
            );
            """
        )
        self._conn.commit()

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # Study registry
    # ------------------------------------------------------------------ #
    def register_study(self, doi: str, title: str = "", authors: Optional[List] = None,
                       year: int = 0, journal: str = "", pmid: str = "",
                       pmcid: str = "", oa_status: str = "", license: str = "",
                       manuscript_version: str = "", source_id: str = "") -> None:
        """Insert a study; conflict JSON keeps existing values (no overwrite)."""
        if not doi:
            return
        self._conn.execute(
            """
            INSERT INTO studies (doi, title, authors, year, journal, pmid, pmcid,
                                 oa_status, license, manuscript_version, source_id,
                                 updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(doi) DO UPDATE SET
                title          = CASE WHEN excluded.title  != '' THEN excluded.title  ELSE studies.title END,
                authors        = CASE WHEN excluded.authors != '[]' THEN excluded.authors ELSE studies.authors END,
                year           = CASE WHEN excluded.year   != 0  THEN excluded.year   ELSE studies.year END,
                journal        = CASE WHEN excluded.journal != '' THEN excluded.journal ELSE studies.journal END,
                pmid           = CASE WHEN excluded.pmid   != '' THEN excluded.pmid   ELSE studies.pmid END,
                pmcid          = CASE WHEN excluded.pmcid  != '' THEN excluded.pmcid  ELSE studies.pmcid END,
                oa_status      = CASE WHEN excluded.oa_status != '' THEN excluded.oa_status ELSE studies.oa_status END,
                license        = CASE WHEN excluded.license != '' THEN excluded.license ELSE studies.license END,
                manuscript_version = CASE WHEN excluded.manuscript_version != '' THEN excluded.manuscript_version ELSE studies.manuscript_version END,
                source_id      = CASE WHEN excluded.source_id != '' THEN excluded.source_id ELSE studies.source_id END,
                updated_at     = excluded.updated_at
            """,
            (doi, title, json.dumps(authors or [], ensure_ascii=False), int(year or 0),
             journal, pmid, pmcid, oa_status, license, manuscript_version, source_id,
             _now()),
        )
        self._conn.commit()
        self._log_once(doi, "DISCOVERED", "registered in coverage manager")

    def record_status(self, doi: str, status: str, reason: str = "",
                      actor: str = "agent") -> None:
        assert status in STATUSES, f"unknown coverage status: {status}"
        if not doi:
            return
        self._conn.execute(
            "UPDATE studies SET status = ?, updated_at = ? WHERE doi = ?",
            (status, _now(), doi),
        )
        self._conn.execute(
            "INSERT INTO studies_status_log (doi, status, reason, actor, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (doi, status, reason, actor, _now()),
        )
        if status in FULLTEXT_STATUSES:
            self._conn.execute(
                "UPDATE studies SET has_fulltext = 1 WHERE doi = ?", (doi,))
        self._conn.commit()

    def set_extraction(self, doi: str, extraction_status: str,
                       endpoints_available: Optional[int] = None) -> None:
        self._conn.execute(
            "UPDATE studies SET extraction_status = ?, updated_at = ? WHERE doi = ?",
            (extraction_status, _now(), doi),
        )
        if endpoints_available is not None:
            self._conn.execute(
                "UPDATE studies SET endpoints_available = ? WHERE doi = ?",
                (int(endpoints_available), doi))
        self._conn.commit()

    def exclude(self, doi: str, reason: str) -> None:
        self._conn.execute(
            "UPDATE studies SET excluded_reason = ?, status = 'EXCLUDED', "
            "updated_at = ? WHERE doi = ?", (reason, _now(), doi))
        self._conn.commit()
        self.record_status(doi, "EXCLUDED", reason)

    def _log_once(self, doi: str, status: str, reason: str) -> None:
        exists = self._conn.execute(
            "SELECT 1 FROM studies_status_log WHERE doi = ? AND status = ? LIMIT 1",
            (doi, status)).fetchone()
        if not exists:
            self._conn.execute(
                "INSERT INTO studies_status_log (doi, status, reason, actor, created_at)"
                " VALUES (?, ?, ?, 'agent', ?)", (doi, status, reason, _now()))
            self._conn.commit()

    def study(self, doi: str) -> Optional[Dict]:
        row = self._conn.execute(
            "SELECT * FROM studies WHERE doi = ?", (doi,)).fetchone()
        return dict(row) if row else None

    def studies(self, status: Optional[str] = None) -> List[Dict]:
        if status:
            rows = self._conn.execute(
                "SELECT * FROM studies WHERE status = ? ORDER BY priority DESC, year",
                (status,))
        else:
            rows = self._conn.execute(
                "SELECT * FROM studies ORDER BY priority DESC, year")
        return [dict(r) for r in rows.fetchall()]

    # ------------------------------------------------------------------ #
    # Local inbox (served before any network fetch)
    # ------------------------------------------------------------------ #
    @staticmethod
    def sanitize_doi_value(doi: str) -> str:
        return re.sub(r"[^0-9a-zA-Z._-]+", "_", (doi or "").lower())

    def inbox_path(self, doi: str) -> Optional[Path]:
        for suffix in (".xml", ".pdf"):
            path = self.inbox_dir / (self.sanitize_doi_value(doi) + suffix)
            if path.exists():
                return path
        return None

    def inbox_text(self, doi: str) -> Optional[Tuple[str, str]]:
        """Returns (kind, text) for an inbox fulltext, or None. Never fetches."""
        path = self.inbox_path(doi)
        if not path:
            return None
        try:
            if path.suffix == ".xml":
                text = _xml_to_text(path.read_text(encoding="utf-8", errors="ignore"))
                return ("xml", text) if len(text) >= 1000 else None
            text = _pdf_to_text(path)
            return ("pdf", text) if text else None
        except Exception as e:
            logger.debug(f"Inbox read failed for {doi}: {e}")
            return None

    # ------------------------------------------------------------------ #
    # Author requests (draft + user approval only; sending stays manual)
    # ------------------------------------------------------------------ #
    def queue_author_request(self, doi: str, authors: Optional[List] = None,
                             to_email: str = "", institution: str = "",
                             draft_text: str = "") -> Optional[str]:
        import uuid

        # Every queued request belongs to a tracked study; create it if the
        # discovery stage did not register the DOI yet.
        if not self.study(doi):
            self.register_study(doi)
        author_first = (authors or [""])[0]
        req_id = uuid.uuid4().hex[:12]
        self._conn.execute(
            "INSERT INTO author_requests (id, doi, authors, to_email, institution,"
            " draft_text, status, created_at) VALUES (?, ?, ?, ?, ?, ?, 'pending_user_approval', ?)",
            (req_id, doi, json.dumps(authors or [], ensure_ascii=False), to_email,
             institution or (str(author_first).strip() or "corresponding author"),
             draft_text, _now()))
        self._conn.commit()
        self.record_status(doi, "AUTHOR_REQUEST_PENDING",
                           f"draft queued ({req_id}); sending requires user approval",
                           actor="agent")
        return req_id

    def approve_author_request(self, req_id: str) -> bool:
        """User-only gate: flips a queued draft to 'approved' for manual sending."""
        cur = self._conn.execute(
            "UPDATE author_requests SET status = 'approved', approved_at = ?"
            " WHERE id = ? AND status = 'pending_user_approval'", (_now(), req_id))
        self._conn.commit()
        return cur.rowcount > 0

    def mark_author_version_received(self, req_id: str, note: str = "") -> None:
        doi_row = self._conn.execute(
            "SELECT doi FROM author_requests WHERE id = ?", (req_id,)).fetchone()
        self._conn.execute(
            "UPDATE author_requests SET status = 'received', received_at = ?,"
            " notes = ? WHERE id = ?", (_now(), note, req_id))
        self._conn.commit()
        if doi_row and doi_row[0]:
            self.record_status(doi_row[0], "AUTHOR_VERSION_RECEIVED", note,
                               actor="user")

    def author_requests(self, status: Optional[str] = None) -> List[Dict]:
        sql = "SELECT * FROM author_requests"
        args: Tuple = ()
        if status:
            sql += " WHERE status = ?"
            args = (status,)
        sql += " ORDER BY created_at"
        return [dict(r) for r in self._conn.execute(sql, args).fetchall()]

    # ------------------------------------------------------------------ #
    # Coverage statistics (dashboard)
    # ------------------------------------------------------------------ #
    def coverage_stats(self) -> Dict:
        total = self._conn.execute("SELECT COUNT(*) FROM studies").fetchone()[0]
        full = self._conn.execute(
            "SELECT COUNT(*) FROM studies WHERE has_fulltext = 1").fetchone()[0]
        status_rows = self._conn.execute(
            "SELECT status, COUNT(*) AS n FROM studies GROUP BY status").fetchall()
        status_counts = {r[0]: r[1] for r in status_rows}
        pending_requests = self._conn.execute(
            "SELECT COUNT(*) FROM author_requests"
            " WHERE status IN ('draft','pending_user_approval')").fetchone()[0]
        awaiting_approval = self._conn.execute(
            "SELECT COUNT(*) FROM author_requests"
            " WHERE status = 'pending_user_approval'").fetchone()[0]
        missing_results = self._conn.execute(
            "SELECT COUNT(*) FROM studies WHERE has_fulltext = 1"
            " AND endpoints_available = 0").fetchone()[0]
        # Tie-in to the meta layer: how many effect rows in the same topic
        # database are poolable (the same POOLABLE clause the pooling engine
        # applies). 0 when the topic DB carries no effects table yet.
        try:
            poolable = self._conn.execute(
                "SELECT COUNT(*) FROM study_effects "
                "WHERE COALESCE(disputed, 0) = 0 "
                "AND COALESCE(rejection_reason, '') = '' "
                "AND (se IS NOT NULL OR (ci_low IS NOT NULL AND ci_high IS NOT NULL))"
            ).fetchone()[0]
        except Exception:
            poolable = 0
        return {
            "identified": total,
            "status_counts": status_counts,
            "fulltext_available": full,
            "fulltext_coverage_pct": round(100.0 * full / total, 1) if total else 0.0,
            "manual_required": status_counts.get("MANUAL_REQUIRED", 0),
            "license_unclear": status_counts.get("LICENSE_UNCLEAR", 0),
            "failed": status_counts.get("FAILED", 0),
            "author_requests_pending": pending_requests,
            "author_requests_awaiting_approval": awaiting_approval,
            "data_extracted": status_counts.get("DATA_EXTRACTED", 0),
            "data_validated": status_counts.get("DATA_VALIDATED", 0),
            "fulltext_without_endpoints": missing_results,
            "poolable_effects": poolable,
            "generated": _now(),
        }

    # ------------------------------------------------------------------ #
    # Acquisition-script bridge (status reconciliation)
    # ------------------------------------------------------------------ #
    def import_acquisition_status(self, metadata_json: Dict) -> Optional[str]:
        """Adopt a record from data/fulltext_metadata/<doi>.json."""
        doi = str(metadata_json.get("doi") or "")
        if not doi:
            return None
        pmcid = re.search(r"PMC\d+", str(metadata_json.get("version")
                                         or "") + str(metadata_json.get("fetch_url") or ""))
        self.register_study(
            doi,
            title=str(metadata_json.get("title") or ""),
            authors=metadata_json.get("authors") or [],
            year=int(metadata_json.get("year") or 0),
            journal=str(metadata_json.get("journal") or ""),
            pmcid=pmcid.group(0) if pmcid else "",
            oa_status=str(metadata_json.get("oa_status") or ""),
            license=str(metadata_json.get("license") or ""),
        )
        s = str(metadata_json.get("status") or "")
        mapped = {
            "DOWNLOADED": "DOWNLOADED",
            "MANUAL_REQUIRED": "MANUAL_REQUIRED",
            "LICENSE_UNCLEAR": "LICENSE_UNCLEAR",
            "FAILED": "FAILED",
        }.get(s, "DISCOVERED")
        self.record_status(doi, mapped,
                           str(metadata_json.get("reason") or ""),
                           actor="acquisition-script")
        return doi
