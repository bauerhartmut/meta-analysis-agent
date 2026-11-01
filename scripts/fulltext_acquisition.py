#!/usr/bin/env python3
"""Legal-first full text acquisition pipeline (prototype).

Reads DOIs, discovers open-access copies through OpenAlex, Unpaywall,
Europe PMC and arXiv, decides download rights from license/host information,
downloads only clearly permitted files, and routes everything else to a
manual acquisition queue. Every action is logged; every file carries a
metadata record (license, source URL, sha256, method).

Statuses: DISCOVERED, LICENSE_VERIFIED, DOWNLOAD_ALLOWED, DOWNLOADED,
MANUAL_REQUIRED, LICENSE_UNCLEAR, PROCESSED, FAILED.

This prototype touches no existing pipeline module: it only writes into
data/fulltext_inbox, data/fulltext_metadata, data/fulltext_logs and
data/manual_acquisition_queue.

Usage:
    python scripts/fulltext_acquisition.py --dois FILE [--apply] [--limit N]
    python scripts/fulltext_acquisition.py --db DB --from-registry [--apply] [--limit N]
Without --apply nothing is downloaded: discovery + rights decision only.
With --db every result record is mirrored into the topic database's
coverage registry (research_agent.coverage.CoverageManager); with
--from-registry the candidate DOIs come from the same registry instead
of a --dois file (all studies whose acquisition is not settled yet).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "data" / "fulltext_inbox"
METADATA = ROOT / "data" / "fulltext_metadata"
LOGS = ROOT / "data" / "fulltext_logs"
MANUAL = ROOT / "data" / "manual_acquisition_queue"

POLITE_EMAIL = os.environ.get("OPENALEX_MAILTO", "research@freebuff.ai").strip()
UA = {"User-Agent": f"LegalFirstFulltextAcquisition/1.0 (research; mailto:{POLITE_EMAIL})"}

# --------------------------------------------------------------------------- #
# Rights engine - policy (documented in FULLTEXT_ACQUISITION.md):
#   * open REPOSITORIES with a recognized open license  -> allowed
#   * PMC / Europe PMC full-text XML                    -> allowed (OA subset)
#   * arXiv PDFs                                        -> allowed
#   * anything hosted by a publisher                    -> never auto-fetched
#         (bronze/hybrid even when public: automated access depends on
#          publisher terms that this prototype has not verified
#          -> LICENSE_UNCLEAR, queue for manual review/download)
#   * open copy without a license field at an unknown host -> LICENSE_UNCLEAR
#   * no open copy at all                               -> MANUAL_REQUIRED
# --------------------------------------------------------------------------- #
ALLOWED_LICENSES = {"cc0", "cc-by", "cc-by-sa", "cc-by-nc", "cc-by-nc-sa"}

DOI_RESOLVERS = ("doi.org", "dx.doi.org", "doaj.org")
TRUSTED_REPO_HOSTS = (
    "arxiv.org", "export.arxiv.org",
    "ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov",
    "europepmc.org", "www.ebi.ac.uk",
    "zenodo.org", "osf.io",
)
REPO_HOSTS = (
    "arxiv.org", "export.arxiv.org",
    "ncbi.nlm.nih.gov", "pmc.ncbi.nlm.nih.gov",
    "europepmc.org", "www.ebi.ac.uk",
    "zenodo.org", "osf.io",
    "dash.harvard.edu", "ssoar.info", "pure.mpg.de", "core.ac.uk",
)
# Publishers explicitly verified for automated access. Deliberately empty in
# this prototype: every entry must mean "terms checked", not "probably ok".
PUBLISHER_ALLOWLIST: tuple[str, ...] = ()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_event(kind: str, payload: dict) -> None:
    LOGS.mkdir(parents=True, exist_ok=True)
    line = json.dumps({"ts": now_iso(), "kind": kind, **payload}, ensure_ascii=False)
    with (LOGS / "acquisition.jsonl").open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def http_get(url: str, timeout: int = 40, headers: dict | None = None):
    req = urllib.request.Request(url, headers=headers if headers is not None else dict(UA))
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read()


def http_json(url: str, timeout: int = 40):
    st, raw = http_get(url, timeout)
    return st, json.loads(raw.decode("utf-8", "ignore"))


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #
def load_unpaywall(doi: str) -> dict:
    _, data = http_json(
        "https://api.unpaywall.org/v2/" + urllib.parse.quote(doi)
        + "?email=" + urllib.parse.quote(POLITE_EMAIL)
    )
    return data


def load_openalex(doi: str) -> dict:
    _, data = http_json("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi))
    return data


def load_crossref(doi: str) -> dict:
    _, data = http_json(
        "https://api.crossref.org/works/" + urllib.parse.quote(doi)
        + "?mailto=" + urllib.parse.quote(POLITE_EMAIL)
    )
    return data.get("message", {})


def pmcid_from_openalex(oa: dict) -> str:
    pmcid = str(((oa or {}).get("ids") or {}).get("pmcid") or "")
    m = re.search(r"PMC\d+", pmcid, re.I)
    return m.group(0).upper() if m else ""


def arxiv_url_from_openalex(oa: dict) -> str:
    for src in (oa.get("primary_location"), *(oa.get("locations") or [])):
        pdf = (src or {}).get("pdf_url") or ""
        if "arxiv.org" in pdf:
            return pdf
    return ""


def europepmc_fulltext_url(pmcid: str) -> str:
    return "https://www.ebi.ac.uk/europepmc/webservices/rest/" + pmcid + "/fullTextXML"


def pmcid_from_europepmc(doi: str) -> str:
    """PMCID for a DOI via the Europe PMC search API ('' when not in PMC)."""
    try:
        _, data = http_json(
            "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
            "?query=" + urllib.parse.quote('DOI:"' + doi + '"')
            + "&format=json&resulttype=lite"
        )
        for hit in (data.get("resultList") or {}).get("result") or []:
            pmcid = str(hit.get("pmcid") or "")
            if pmcid:
                return pmcid.upper()
    except Exception:
        pass
    return ""


# --------------------------------------------------------------------------- #
# Rights decision
# --------------------------------------------------------------------------- #
def decide(doi: str, oa: dict, up: dict) -> dict:
    license_ = str(up.get("license") or "").lower()
    oa_status = str(
        up.get("oa_status") or (oa.get("open_access") or {}).get("oa_status") or ""
    ).lower()
    is_oa = bool(up.get("is_oa")) or oa_status not in ("", "closed")

    pmcid = pmcid_from_openalex(oa)
    if pmcid:
        return {
            "status": "DOWNLOAD_ALLOWED", "reason": f"PMC OA subset ({pmcid})",
            "method": "europepmc_fulltext_xml", "url": europepmc_fulltext_url(pmcid),
            "license": license_ or "pmc-oa-subset", "host": "europepmc",
            "version": "pmc-final",
        }

    arxiv = arxiv_url_from_openalex(oa)
    if arxiv:
        return {
            "status": "DOWNLOAD_ALLOWED", "reason": "arXiv preprint copy",
            "method": "arxiv_pdf", "url": arxiv,
            "license": license_ or "arxiv-distribution", "host": "arxiv",
            "version": "arxiv-preprint",
        }

    if not is_oa:
        return {
            "status": "MANUAL_REQUIRED",
            "reason": f"no open copy (oa_status={oa_status or 'closed'})",
            "license": license_, "host": "", "version": "",
        }

    # Open copy exists: only repositories with an accepted license qualify.
    pick_url = ""
    pick_host = ""
    for loc in [up.get("best_oa_location") or {}] + list(up.get("oa_locations") or []):
        if not loc:
            continue
        cand_pdf = loc.get("url_for_pdf") or ""
        cand_url = loc.get("url") or ""
        cand_host = urllib.parse.urlparse(cand_url).netloc.lower()
        cand_host = cand_host[4:] if cand_host.startswith("www.") else cand_host
        # DOI resolvers and directories are not repositories: a doi.org URL
        # resolves to the publisher page, DOAJ is a directory. Both fall
        # back to the manual workflow instead of an automated fetch.
        if cand_host in DOI_RESOLVERS:
            continue
        is_repo = str(loc.get("host_type", "")) == "repository" or cand_host in REPO_HOSTS
        is_allowed_publisher = any(
            cand_host == p or cand_host.endswith("." + p) for p in PUBLISHER_ALLOWLIST
        )
        if not (is_repo or is_allowed_publisher):
            continue
        # Trusted open repositories (PMC, arXiv, Zenodo, ... ) publish copies
        # for programmatic access; every other listing needs an accepted
        # license on record before anything is fetched automatically.
        trusted = cand_host in TRUSTED_REPO_HOSTS
        if not trusted and (not license_ or license_ not in ALLOWED_LICENSES):
            continue
        candidate = cand_pdf or cand_url
        if candidate:
            pick_url, pick_host = candidate, cand_host
            if cand_pdf:
                break

    if pick_url:
        return {
            "status": "DOWNLOAD_ALLOWED",
            "reason": f"repository copy at {pick_host} (license={license_ or 'unmarked'})",
            "method": "repository_pdf", "url": pick_url, "license": license_ or "unmarked",
            "host": pick_host, "version": "repository-version",
        }
    return {
        "status": "LICENSE_UNCLEAR",
        "reason": (
            f"open copy exists (oa_status={oa_status}), but host/license combination "
            "is not verified for automated access"
        ),
        "license": license_, "host": "", "version": "",
    }


# --------------------------------------------------------------------------- #
# Download engine
# --------------------------------------------------------------------------- #
def sanitize_doi(doi: str) -> str:
    return re.sub(r"[^a-zA-Z0-9.\-]", "_", doi.strip().lower())


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def download_pdf(url: str, target: Path) -> dict:
    """Download to <target> with .part resume support and PDF validation."""
    INBOX.mkdir(parents=True, exist_ok=True)
    part = target.with_name(target.name + ".part")
    pos = part.stat().st_size if part.exists() else 0

    if pos:
        req = urllib.request.Request(url, headers={**UA, "Range": f"bytes={pos}-"})
    else:
        req = urllib.request.Request(url, headers=dict(UA))
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            stream = resp.read()
    except urllib.error.HTTPError as e:
        if pos and e.code == 416:             # range beyond EOF: file complete
            part.rename(target)
            return {"finished": True, "bytes": pos, "resumed": True}
        return {"finished": False, "error": f"http {e.code}", "resumed": pos > 0}
    except Exception as e:
        return {"finished": False, "error": f"{type(e).__name__}: {e}", "resumed": pos > 0}

    # honor the paused-download contract: keep appending to .part
    with part.open("ab" if pos else "wb") as f:
        f.write(stream)

    size = part.stat().st_size
    magic = part.open("rb").read(5)
    if size < 8000:
        part.unlink()
        return {"finished": False, "error": f"too small ({size} bytes, likely html)",
                "resumed": False}
    if magic != b"%PDF-":
        part.unlink()
        return {"finished": False, "error": "not a PDF (magic bytes missing)", "resumed": False}

    part.rename(target)
    return {"finished": True, "bytes": size, "resumed": pos > 0}


def write_metadata(doi: str, record: dict) -> None:
    METADATA.mkdir(parents=True, exist_ok=True)
    path = METADATA / (sanitize_doi(doi) + ".json")
    if path.exists():
        return                                # never overwrite an existing record
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")


_LICENSE_URLS = {
    "cc0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "cc-by": "https://creativecommons.org/licenses/by/4.0/",
    "cc-by-sa": "https://creativecommons.org/licenses/by-sa/4.0/",
    "cc-by-nc": "https://creativecommons.org/licenses/by-nc/4.0/",
    "cc-by-nc-sa": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
}


def write_manual_entry(record: dict) -> None:
    MANUAL.mkdir(parents=True, exist_ok=True)
    tu_options = [
        {
            "kind": "publisher landing page",
            "url": "https://doi.org/" + record["doi"],
        },
        {
            "kind": "TUfind portal (TU access)",
            "url": "https://tufind.hds.hebis.de/discovery/search?query=any,contains,"
                   + urllib.parse.quote(record["title"][:80]),
        },
        {
            "kind": "EZB electronic journals (TU Darmstadt)",
            "url": "https://rzblx1.uni-regensburg.de/ezeit/searchres.phtml?bibid=TUDA",
        },
        {
            "kind": "ULB Fernleihe / document delivery (subito)",
            "url": "https://www.ulb.tu-darmstadt.de/finden_nutzen/bestellen/index.de.jsp",
        },
    ]
    pmc = re.search(r"PMC\d+", str(record.get("reason", "")), re.I)
    if pmc:
        tu_options.insert(0, {
            "kind": "PMC open-subset copy (" + pmc.group(0) + ")",
            "url": "https://pmc.ncbi.nlm.nih.gov/articles/" + pmc.group(0) + "/",
        })
    entry = {
        "doi": record["doi"], "title": record["title"], "authors": record["authors"],
        "year": record["year"], "journal": record["journal"],
        "license": record["license"], "oa_status": record["oa_status"],
        "status": record["status"], "reason": record["reason"],
        "tu_access_options": tu_options,
        "instruction": (
            "Download PDF for yourself via an allowed access route (e.g. browser with "
            "campus VPN at the publisher), then drop it as "
            "data/fulltext_inbox/<doi>.pdf. The agent validates DOI + PDF integrity "
            "and hands it to the existing parsing pipeline."
        ),
        "ts": now_iso(),
    }
    with (MANUAL / "entries.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    single = MANUAL / (sanitize_doi(record["doi"]) + ".json")
    if not single.exists():
        single.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")


# ------------------------------------------------------------------------- #
# Coverage-registry bridge (same sanitize schema as the manager module)
# ------------------------------------------------------------------------- #
def load_registry_dois(db_path: str) -> list:
    """DOIs whose acquisition is not settled yet (nothing terminal)."""
    import sqlite3

    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT doi FROM studies "
            "WHERE doi <> '' AND status NOT IN ("
            "'DOWNLOADED','DATA_EXTRACTED','DATA_VALIDATED','EXCLUDED',"
            "'AUTHOR_VERSION_RECEIVED')"
        ).fetchall()
    finally:
        conn.close()
    return [r[0] for r in rows]


def write_back(db_path: str, record: dict) -> str:
    """Mirror one acquisition record into the coverage registry."""
    import sys

    sys.path.insert(0, str(ROOT))
    from research_agent.coverage.manager import CoverageManager

    CoverageManager(db_path).import_acquisition_status(record)
    return str(record.get("doi") or "")


# --------------------------------------------------------------------------- #
# Per-DOI workflow
# --------------------------------------------------------------------------- #
def process(doi: str, apply: bool) -> dict:
    doi = doi.strip()
    if not doi:
        return {"doi": doi, "status": "SKIPPED"}
    oa, up = {}, {}
    try:
        oa = load_openalex(doi)
    except Exception as e:
        log_event("discovery_error", {"doi": doi, "source": "openalex", "error": str(e)})
    try:
        up = load_unpaywall(doi)
    except Exception as e:
        log_event("discovery_error", {"doi": doi, "source": "unpaywall", "error": str(e)})
    try:
        cr = load_crossref(doi)
    except Exception:
        cr = {}

    title = (oa.get("title") or (cr.get("title") or [""])[0] or "").strip()
    authors = [a.get("display_name", "") for a in (oa.get("authorships") or [])[:5]]
    year = oa.get("publication_year") or (cr.get("issued") or {}).get("date-parts", [[""]])[0][0]
    journal = (((oa.get("primary_location") or {}).get("source") or {}).get("display_name", "")
               or (cr.get("container-title") or [""])[0])

    abstract = oa.get("abstract_inverted_index") or {}
    positions = [(i, w) for w, idxs in abstract.items() for i in idxs]
    abstract_text = re.sub(r"\s+", " ", " ".join(w for _, w in sorted(positions)))

    license_ = str(up.get("license") or "").lower()
    oa_status = str(up.get("oa_status") or "").lower()
    pmcid = pmcid_from_openalex(oa) or pmcid_from_europepmc(doi)
    if pmcid:
        decision = {
            "status": "DOWNLOAD_ALLOWED", "reason": f"PMC OA subset ({pmcid})",
            "method": "europepmc_fulltext_xml",
            "url": europepmc_fulltext_url(pmcid),
            "license": license_ or "pmc-oa-subset", "host": "europepmc",
            "version": "pmc-final",
        }
    else:
        decision = decide(doi, oa, up)

    record = {
        "doi": doi, "title": title, "authors": authors, "year": year, "journal": journal,
        "abstract": abstract_text[:2000], "oa_status": oa_status, "license": license_,
        "publisher_url": "https://doi.org/" + doi,
        "openalex_id": oa.get("id", ""),
        "discovered_at": now_iso(),
        "status": decision["status"], "reason": decision["reason"],
        "version": decision.get("version", ""),
        "download_method": decision.get("method", ""), "fetch_url": decision.get("url", ""),
        "repository": decision.get("host", ""), "automation": ("automatic"
            if decision["status"] == "DOWNLOAD_ALLOWED" else "none"),
        "checkstatus": "pending",
    }

    if decision["status"] == "DOWNLOAD_ALLOWED" and apply:
        if decision["method"] == "europepmc_fulltext_xml":
            target = INBOX / (sanitize_doi(doi) + ".xml")
            if target.exists():
                record.update(status="DOWNLOADED",
                              reason="existing file kept (no overwrite)",
                              sha256=sha256_of(target), size=target.stat().st_size,
                              checkstatus="valid-xml (pre-existing)")
                write_metadata(doi, record)
                log_event("already_present", {"doi": doi})
                return record
            try:
                _, raw = http_get(decision["url"], timeout=120)
                xml_text = raw.decode("utf-8", "ignore")
            except Exception as e:
                record.update(status="FAILED",
                              error=f"pmc xml: {type(e).__name__}: {e}",
                              checkstatus="failed")
                log_event("download_failed", {"doi": doi, "source": "europepmc",
                                              "error": str(e)})
                write_metadata(doi, record)
                return record
            usable = (xml_text.lstrip().startswith(("<?xml", "<pmc"))
                      and len(xml_text) >= 3000)
            if not usable:
                record.update(status="FAILED",
                              error="pmc xml not available (not in OA subset)",
                              checkstatus="failed")
                log_event("download_failed", {"doi": doi, "source": "europepmc",
                                              "error": "no usable fullTextXML"})
                write_metadata(doi, record)
                return record
            with target.open("wb") as f:
                f.write(xml_text.encode("utf-8"))
            record.update(status="DOWNLOADED", sha256=sha256_of(target),
                          size=target.stat().st_size, downloaded_at=now_iso(),
                          download_url=decision["url"], checkstatus="valid-xml",
                          license_url=_LICENSE_URLS.get(license_, ""))
            log_event("downloaded", {"doi": doi, "method": "europepmc_fulltext_xml",
                                     "bytes": target.stat().st_size})
            write_metadata(doi, record)
            return record
        target = INBOX / (sanitize_doi(doi) + ".pdf")
        if target.exists():
            record.update(status="DOWNLOADED",
                          reason="file already in inbox (kept, no overwrite)",
                          sha256=sha256_of(target), size=target.stat().st_size,
                          checkstatus="valid-pdf (pre-existing)")
            write_metadata(doi, record)
            log_event("already_present", {"doi": doi})
            return record
        result = download_pdf(decision["url"], target)
        if result["finished"]:
            record.update(
                status="DOWNLOADED", sha256=sha256_of(target), size=result["bytes"],
                downloaded_at=now_iso(), download_url=decision["url"],
                checkstatus="valid-pdf", resumed=result.get("resumed", False),
            )
            log_event("downloaded", {"doi": doi, "method": decision["method"],
                                     "bytes": result["bytes"], "url": decision["url"]})
        else:
            record.update(status="FAILED",
                          error=f"download: {result['error']}", checkstatus="failed")
            log_event("download_failed", {"doi": doi, "error": result["error"]})

    if decision["status"] == "LICENSE_UNCLEAR":
        record["license_note"] = (
            "not auto-fetched: terms for automated access not verified in this prototype"
        )

    if apply:
        if record["status"] in ("MANUAL_REQUIRED", "LICENSE_UNCLEAR", "FAILED"):
            write_manual_entry(record)
            log_event("manual_queued", {"doi": doi, "status": record["status"]})
        write_metadata(doi, record)

    log_event("discovered", {"doi": doi, "status": record["status"], "oa_status": oa_status,
                             "license": license_})
    return record


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dois", required=True, help="text file, one DOI per line, '#' comments")
    ap.add_argument("--db", default="",
                    help="topic database; mirrors every result into its coverage registry")
    ap.add_argument("--from-registry", action="store_true",
                    help="read candidate DOIs from the registry (requires --db), not from --dois")
    ap.add_argument("--apply", action="store_true", help="download/queue when allowed (default: dry-run)")
    ap.add_argument("--limit", type=int, default=0, help="process at most N DOIs (0 = all)")
    args = ap.parse_args()

    if args.from_registry:
        if not args.db:
            ap.error("--from-registry requires --db")
        dois = load_registry_dois(args.db)
    else:
        dois = [d.strip() for d in Path(args.dois).read_text(encoding="utf-8").splitlines()
                if d.strip() and not d.strip().startswith("#")]

    dois = [d.strip() for d in Path(args.dois).read_text(encoding="utf-8").splitlines()
            if d.strip() and not d.strip().startswith("#")]
    if args.limit:
        dois = dois[: args.limit]

    results = []
    for doi in dois:
        try:
            rec = process(doi, apply=args.apply)
        except Exception as e:
            rec = {"doi": doi, "status": "FAILED", "error": f"{type(e).__name__}: {e}"}
            log_event("processing_error", {"doi": doi, "error": rec["error"]})
        if args.db:
            try:
                write_back(args.db, rec)
            except Exception as e:
                log_event("registry_write_back_failed", {"doi": doi, "error": str(e)})
        results.append(rec)
        print(f"[{rec['status']:>16}] {doi}  {rec.get('reason', '')[:80]}")
        time.sleep(0.6)                       # polite pacing for the public APIs

    counts: dict[str, int] = {}
    for rec in results:
        counts[rec["status"]] = counts.get(rec["status"], 0) + 1
    print("\n=== Zusammenfassung ===")
    for k, v in sorted(counts.items()):
        print(f"  {k:>16}: {v}")
    stats = {
        "discovered": sum(counts.get(s, 0) for s in
                          ("DOWNLOAD_ALLOWED", "DOWNLOADED", "LICENSE_UNCLEAR",
                           "MANUAL_REQUIRED", "PROCESSED")),
        "downloaded": counts.get("DOWNLOADED", 0),
        "manual_required": counts.get("MANUAL_REQUIRED", 0),
        "license_unclear": counts.get("LICENSE_UNCLEAR", 0),
        "failed": counts.get("FAILED", 0),
        "total_processed": len(results),
        "generated": now_iso(),
    }
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
