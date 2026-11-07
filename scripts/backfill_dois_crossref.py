"""Fehlende DOIs per Titel-Abgleich mit Crossref nachfuellen.

Warum: In Run 1 und Run 2 trugen nur 19-22 % der Quellen eine DOI. Ohne DOI
greift weder Europe-PMCs ``fullTextXML`` noch eine gezielte Repositorien-
Suche - der XML-first-Pfad kann diese Quellen gar nicht erreichen.

Der Abgleich ist bewusst streng: ein DOI wird nur uebernommen, wenn sich die
Titel stark decken (>= 0.85 der kuerzeren Tokenmenge, mindestens 4 gemeinsame
inhaltstragende Woerter). Ein falscher DOI waere schlimmer als keiner, weil
er eine fremde Arbeit als Volltext ins Korpus zieht.

Arbeitet auf einer Kopie (das Skript prueft das nicht, der Aufrufer schon):
Lauf-Datenbanken sind Evidenzartefakte und bleiben unveraendert.

Usage:
    python scripts/backfill_dois_crossref.py data/bench/backfill/run1.db \
        --json data/bench/backfill/run1_dois.json
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CROSSREF = "https://api.crossref.org/works"
MAILTO = "research@freebuff.ai"
UA = "Mozilla/5.0 (Research Agent; Academic Use)"
DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s\"'<>&?#]+)", re.I)
_STRICT_DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")

STOP = {
    "the", "a", "an", "of", "and", "in", "on", "for", "to", "with", "by",
    "from", "study", "analysis", "between", "their", "its", "effect",
    "effects", "trial", "randomized", "randomised", "controlled", "review",
    "systematic", "meta", "meta-analysis", "versus", "vs",
}


def _terms(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {w for w in words if len(w) > 2 and w not in STOP}


def title_match(query: str, candidate: str) -> float:
    """Deckung der kuerzeren Tokenmenge (0.0 bis 1.0)."""
    a, b = _terms(query), _terms(candidate)
    if len(a) < 3 or len(b) < 3:
        return 0.0
    shared = len(a & b)
    return shared / min(len(a), len(b))


def doi_from_url(url: str) -> str:
    match = DOI_RE.search(url or "")
    return match.group(1).rstrip(").,;") if match else ""


def _get(url: str, timeout: int, attempts: int = 3) -> tuple[int, bytes]:
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 503) and attempt < attempts:
                time.sleep(5 * attempt)
                continue
            return exc.code, b""
        except Exception:
            if attempt < attempts:
                time.sleep(2 * attempt)
                continue
            return 0, b""
    return 0, b""


def lookup_title(title: str, timeout: int, rows: int = 3) -> dict:
    """Crossref-Suche nach Titel; liefert den besten Treffer mit Score."""
    query = urllib.parse.urlencode({
        "query.bibliographic": title[:250],
        "rows": rows,
        "select": "title,DOI,type",
        "mailto": MAILTO,
    })
    status, body = _get(f"{CROSSREF}?{query}", timeout)
    if status != 200 or not body:
        return {}
    try:
        items = (json.loads(body.decode("utf-8", "ignore"))
                 .get("message", {}) or {}).get("items", []) or []
    except ValueError:
        return {}
    query_tokens = _terms(title)
    best: dict = {}
    for item in items:
        candidate = (item.get("title") or [""])[0] or ""
        doi = str(item.get("DOI") or "").strip()
        if not _STRICT_DOI_RE.match(doi):
            continue
        score = title_match(title, candidate)
        shared = len(query_tokens & _terms(candidate))
        coverage = shared / max(1, len(query_tokens))
        if score > best.get("score", 0.0):
            best = {"doi": doi, "matched_title": candidate, "score": round(score, 3),
                    "shared": shared, "cov_query": round(coverage, 3),
                    "type": item.get("type") or ""}
    return best


def backfill(db_path: Path, timeout: int, sleep: float, min_score: float,
             limit: int = 0, min_shared: int = 6,
             min_coverage: float = 0.6) -> dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, title, url, doi FROM sources ORDER BY rowid").fetchall()
    results = []
    stats = {"sources": len(rows), "with_doi_before": 0, "from_url": 0,
             "from_crossref": 0, "rejected_low_score": 0, "no_candidate": 0,
             "still_without_doi": 0}
    pending = []
    for row in rows:
        if (row["doi"] or "").strip():
            stats["with_doi_before"] += 1
            continue
        doi = doi_from_url(row["url"] or "")
        if doi:
            conn.execute("UPDATE sources SET doi = ? WHERE id = ?",
                         (doi, row["id"]))
            stats["from_url"] += 1
            results.append({"id": row["id"], "title": row["title"],
                            "doi": doi, "method": "url", "score": 1.0})
        else:
            pending.append(row)
    conn.commit()

    if limit:
        pending = pending[:limit]

    for number, row in enumerate(pending, start=1):
        title = (row["title"] or "").strip()
        if len(title) < 15:
            stats["no_candidate"] += 1
            results.append({"id": row["id"], "title": title, "doi": "",
                            "method": "title-too-short", "score": 0.0})
            continue
        best = lookup_title(title, timeout)
        if not best:
            stats["no_candidate"] += 1
            results.append({"id": row["id"], "title": title, "doi": "",
                            "method": "no-candidate", "score": 0.0})
        elif (best["score"] < min_score
              or best.get("shared", 0) < min_shared
              or best.get("cov_query", 0.0) < min_coverage):
            # Ein kurzer, generischer Titel ("Clinical Aspects of Alzheimer
            # Disease") deckt eine lange Quelle scheinbar vollstaendig ab und
            # war in der ersten Messung 8x die falsche Arbeit. Deshalb neben
            # der Token-Deckung auch absolute Trefferzahl und Abdeckung der
            # Quelltokens verlangen.
            stats["rejected_low_score"] += 1
            results.append({"id": row["id"], "title": title, "doi": "",
                            "method": "rejected", "score": best["score"],
                            "shared": best.get("shared", 0),
                            "cov_query": best.get("cov_query", 0.0),
                            "matched_title": best.get("matched_title", "")})
        else:
            conn.execute("UPDATE sources SET doi = ? WHERE id = ?",
                         (best["doi"], row["id"]))
            conn.commit()
            stats["from_crossref"] += 1
            results.append({"id": row["id"], "title": title, "doi": best["doi"],
                            "method": "crossref", "score": best["score"],
                            "matched_title": best.get("matched_title", "")})
        if number % 20 == 0:
            print(f"  ... {number}/{len(pending)} Titel geprueft", flush=True)
        time.sleep(sleep)

    stats["still_without_doi"] = conn.execute(
        "SELECT COUNT(*) FROM sources WHERE TRIM(COALESCE(doi, '')) = ''"
    ).fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    stats["with_doi_after"] = total - stats["still_without_doi"]
    conn.close()
    return {"db": str(db_path), "stats": stats, "results": results}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dbs", nargs="+", help="Kopien der Lauf-Datenbanken")
    ap.add_argument("--json", default="", help="Pfad fuer den JSON-Report")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--sleep", type=float, default=0.3)
    ap.add_argument("--min-score", type=float, default=0.85)
    ap.add_argument("--min-shared", type=int, default=6,
                    help="mindestens so viele gemeinsame Titel-Tokens")
    ap.add_argument("--min-coverage", type=float, default=0.6,
                    help="Anteil der Quell-Tokens, der im Treffer vorkommt")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    reports = []
    for raw in args.dbs:
        path = Path(raw)
        if not path.exists():
            print(f"fehlt: {path}", file=sys.stderr)
            continue
        print(f"== {path.name} ==", flush=True)
        reports.append(backfill(path, args.timeout, args.sleep,
                                args.min_score, args.limit,
                                args.min_shared, args.min_coverage))
        stats = reports[-1]["stats"]
        print(f"  DOI vorher {stats['with_doi_before']} -> nachher "
              f"{stats['with_doi_after']} (+{stats['from_url']} URL, "
              f"+{stats['from_crossref']} Crossref, "
              f"{stats['rejected_low_score']} verworfen, "
              f"{stats['no_candidate']} ohne Kandidat)", flush=True)

    if args.json:
        payload = {"generated": datetime.now(timezone.utc).isoformat(),
                   "reports": reports}
        Path(args.json).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
