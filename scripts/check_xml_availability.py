"""Verfuegbarkeit von Europe-PMC-Volltext-XML fuer die Lauf-DOIs pruefen.

Read-only: liest die DOI-tragenden Quellen aus den Lauf-Datenbanken (SQLite
im Modus ``ro``) und fragt fuer jede DOI bei Europe PMC nach PMCID und
``fullTextXML``. Gezaehlt wird, ob die XML Tabellen mit SE/CI-Zeilen enthaelt
- also ob der XML-first-Pfad die Unsicherheitsmaße ueberhaupt liefern kann.

Kein LLM, keine Schreibzugriffe auf die Lauf-DBs, keine Volltext-PDFs.
Hoefliche Sequenz mit Pause zwischen den Abfragen und begrenzten Retries.

Usage:
    python scripts/check_xml_availability.py \
        data/research-a.db data/research-b.db \
        --json data/bench/xml_verfuegbarkeit_20261107.json \
        --md data/bench/xml_verfuegbarkeit_20261107.md
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research_agent.research.jats_tables import blocks_from_jats  # noqa: E402

SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
UA = "Mozilla/5.0 (Research Agent; Academic Use)"
_PMCID_RE = re.compile(r"PMC\d+", re.I)


def _get(url: str, timeout: int, attempts: int = 3) -> tuple[int, str]:
    """GET with bounded backoff; returns (status, body). Never raises."""
    for attempt in range(1, attempts + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 503) and attempt < attempts:
                time.sleep(5 * attempt)
                continue
            return exc.code, ""
        except Exception:
            if attempt < attempts:
                time.sleep(2 * attempt)
                continue
            return 0, ""
    return 0, ""


def pmcid_for_doi(doi: str, timeout: int) -> str:
    query = urllib.parse.urlencode(
        {"query": f'DOI:"{doi}"', "format": "json", "resulttype": "lite"})
    status, body = _get(f"{SEARCH_URL}?{query}", timeout)
    if status != 200 or not body:
        return ""
    try:
        data = json.loads(body)
    except ValueError:
        return ""
    for hit in ((data.get("resultList") or {}).get("result")) or []:
        pmcid = str((hit or {}).get("pmcid") or "").strip().upper()
        if _PMCID_RE.fullmatch(pmcid):
            return pmcid
    return ""


def table_stats(xml: str) -> dict:
    """Tabellen, stat-reiche Zeilen und Zeilen mit SE/CI aus der JATS-XML."""
    blocks = blocks_from_jats(xml)
    rows = [r for b in blocks for r in b.get("effect_cells") or []]
    return {
        "tables": len(blocks),
        "stat_rows": len(rows),
        "se_rows": sum(1 for r in rows if r.get("has_se")),
        "ci_rows": sum(1 for r in rows if r.get("has_ci")),
        "sd_n_rows": sum(1 for r in rows if r.get("has_sd") and r.get("has_n")),
    }


def doi_rows(db_path: Path) -> list[dict]:
    """DOI-tragende Quellen und Studien einer Lauf-DB (read-only).

    Das Studienregister fuehrt DOIs, die nie eine Quellenzeile bekamen; fuer
    die Frage "welche Studie hat eine XML?" zaehlen beide.
    """
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """
            SELECT s.doi, s.title,
                   (SELECT t.kind FROM source_texts t
                     WHERE t.source_id = s.id ORDER BY t.chars DESC LIMIT 1) AS kind,
                   (SELECT t.chars FROM source_texts t
                     WHERE t.source_id = s.id ORDER BY t.chars DESC LIMIT 1) AS chars
              FROM sources s
             WHERE TRIM(COALESCE(s.doi, '')) != ''
             ORDER BY s.doi
            """
        ).fetchall()
        seen = {str(r["doi"]).strip().lower() for r in rows}
        try:
            studies = conn.execute(
                "SELECT doi, title FROM studies"
                " WHERE TRIM(COALESCE(doi, '')) != '' ORDER BY doi"
            ).fetchall()
        except sqlite3.OperationalError:
            studies = []
        extra = [dict(r) for r in studies
                 if str(r["doi"]).strip().lower() not in seen]
    finally:
        conn.close()
    return [dict(r) for r in rows] + [
        {"doi": r["doi"], "title": r["title"], "kind": "", "chars": 0}
        for r in extra
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dbs", nargs="+", help="Lauf-Datenbanken (read-only)")
    ap.add_argument("--json", default="", help="Pfad fuer den JSON-Report")
    ap.add_argument("--md", default="", help="Pfad fuer den Markdown-Report")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--sleep", type=float, default=0.5)
    ap.add_argument("--limit", type=int, default=0, help="nur die ersten N DOIs")
    args = ap.parse_args()

    per_doi: dict[str, dict] = {}
    for raw_db in args.dbs:
        db_path = Path(raw_db)
        tag = db_path.name.split("-")[0]
        for row in doi_rows(db_path):
            doi = (row.get("doi") or "").strip().lower()
            if not doi:
                continue
            entry = per_doi.setdefault(doi, {
                "doi": doi, "title": row.get("title") or "", "runs": {},
            })
            if not entry["title"]:
                entry["title"] = row.get("title") or ""
            entry["runs"][tag] = {"kind": row.get("kind") or "", "chars": row.get("chars") or 0}

    dois = sorted(per_doi)
    if args.limit:
        dois = dois[: args.limit]

    for number, doi in enumerate(dois, start=1):
        entry = per_doi[doi]
        pmcid = pmcid_for_doi(doi, args.timeout)
        entry["pmcid"] = pmcid
        entry["xml_ok"] = False
        entry["xml_chars"] = 0
        entry["tables"] = entry["stat_rows"] = entry["se_rows"] = 0
        entry["ci_rows"] = entry["sd_n_rows"] = 0
        if pmcid:
            time.sleep(args.sleep)
            status, xml = _get(XML_URL.format(pmcid=pmcid), args.timeout)
            if status == 200 and "<article" in xml:
                entry["xml_ok"] = True
                entry["xml_chars"] = len(xml)
                try:
                    entry.update(table_stats(xml))
                except Exception as exc:  # kaputte XML ist ein Datenpunkt, kein Absturz
                    entry["parse_error"] = f"{type(exc).__name__}: {exc}"
        print(f"[{number}/{len(dois)}] {doi} -> {pmcid or '-'} "
              f"xml={'ja' if entry['xml_ok'] else 'nein'} "
              f"tab={entry['tables']} ci={entry['ci_rows']} se={entry['se_rows']}",
              flush=True)
        time.sleep(args.sleep)

    records = [per_doi[d] for d in dois]
    summary = {
        "dois": len(records),
        "with_pmcid": sum(1 for r in records if r.get("pmcid")),
        "with_xml": sum(1 for r in records if r.get("xml_ok")),
        "with_tables": sum(1 for r in records if r.get("tables")),
        "with_ci_rows": sum(1 for r in records if r.get("ci_rows")),
        "with_se_rows": sum(1 for r in records if r.get("se_rows")),
        "runs": {},
    }
    for raw_db in args.dbs:
        tag = Path(raw_db).name.split("-")[0]
        subset = [r for r in records if tag in r.get("runs", {})]
        summary["runs"][tag] = {
            "dois": len(subset),
            "with_pmcid": sum(1 for r in subset if r.get("pmcid")),
            "with_xml": sum(1 for r in subset if r.get("xml_ok")),
            "with_ci_rows": sum(1 for r in subset if r.get("ci_rows")),
        }

    payload = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "sources": [Path(p).name for p in args.dbs],
        "summary": summary,
        "records": records,
    }
    if args.json:
        Path(args.json).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"JSON: {args.json}")

    if args.md:
        lines = [
            "# Europe-PMC-XML-Verfuegbarkeit fuer die Lauf-DOIs",
            "",
            f"Stand: {payload['generated'][:16].replace('T', ' ')} UTC",
            f"Datenbanken: {', '.join(payload['sources'])}",
            "",
            "## Zusammenfassung",
            "",
            "| Kennzahl | Wert |",
            "|---|---|",
            f"| DOIs gesamt | {summary['dois']} |",
            f"| mit PMCID | {summary['with_pmcid']} |",
            f"| mit fullTextXML | {summary['with_xml']} |",
            f"| davon mit Tabellen | {summary['with_tables']} |",
            f"| mit CI-Zeilen | {summary['with_ci_rows']} |",
            f"| mit SE-Zeilen | {summary['with_se_rows']} |",
            "",
            "## Je Lauf",
            "",
            "| Lauf | DOIs | PMCID | XML | mit CI-Zeilen |",
            "|---|---|---|---|---|",
        ]
        for tag, part in summary["runs"].items():
            lines.append(f"| {tag} | {part['dois']} | {part['with_pmcid']} | "
                         f"{part['with_xml']} | {part['with_ci_rows']} |")
        lines += ["", "## Je DOI", "",
                  "| DOI | PMCID | XML | Tabellen | stat. Zeilen | SE | CI | im Lauf |",
                  "|---|---|---|---|---|---|---|---|"]
        for rec in records:
            runs = ", ".join(
                f"{tag}:{info['kind'] or 'kein Text'}" for tag, info in rec["runs"].items())
            lines.append(
                f"| {rec['doi']} | {rec.get('pmcid') or '-'} | "
                f"{'ja' if rec.get('xml_ok') else 'nein'} | {rec.get('tables', 0)} | "
                f"{rec.get('stat_rows', 0)} | {rec.get('se_rows', 0)} | "
                f"{rec.get('ci_rows', 0)} | {runs} |")
        Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"MD: {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
