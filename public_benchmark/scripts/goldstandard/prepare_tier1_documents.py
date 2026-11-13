#!/usr/bin/env python3
"""Prueft, fuer welche Records des externen Validierungssatzes ein
open-access-Volltext ueber Europe PMC verfuegbar ist.

Das ist die Vorbedingung fuer Stufe 1: ohne Volltext kann kein Modell
extrahieren. Es wird nichts heruntergeladen, nur der Status abgefragt.

Ausgabe: ``tier1_documents_v1.json``.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

CROSSVAL = Path(__file__).resolve().parents[2] / "evaluation" / "multi_model_cross_validation"
SET = CROSSVAL / "tier1_validation_set_v1.jsonl"
OUT = CROSSVAL / "tier1_documents_v1.json"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UA = {"User-Agent": "meta-analysis-agent/tier1-docs"}


def query(term: str) -> dict[str, Any]:
    params = urllib.parse.urlencode(
        {"query": term, "format": "json", "resultType": "lite", "pageSize": 5}
    )
    request = urllib.request.Request(f"{EPMC}?{params}", headers=UA)
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.load(response)
    time.sleep(0.4)
    hits = payload.get("resultList", {}).get("result", [])
    return hits[0] if hits else {}


def lookup(study_ref: str, dataset: str) -> dict[str, Any]:
    ref = study_ref.strip()
    if not ref:
        return {"status": "no_reference"}
    try:
        if dataset == "eururology":
            hit = query(f'DOI:"{ref.replace("https://doi.org/", "")}"')
        else:
            hit = query(f"EXT_ID:{ref} AND SRC:MED")
    except Exception as error:
        return {"status": "error", "error": str(error)}
    if not hit:
        return {"status": "not_found"}
    pmcid = hit.get("pmcid", "")
    return {
        "status": "full_text_available" if pmcid and hit.get("isOpenAccess") == "Y" else "abstract_only",
        "pmid": hit.get("pmid", ""),
        "pmcid": pmcid,
        "is_open_access": hit.get("isOpenAccess", ""),
        "title": (hit.get("title") or "")[:100],
    }


def main() -> int:
    records = [
        json.loads(line) for line in SET.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    cache: dict[tuple[str, str], dict[str, Any]] = {}
    per_record = []
    for record in records:
        key = (record["dataset"], record["study_ref"])
        if key not in cache:
            cache[key] = lookup(record["study_ref"], record["dataset"])
        per_record.append({"record_id": record["record_id"], **cache[key]})

    counts: dict[str, int] = {}
    for item in per_record:
        counts[item["status"]] = counts.get(item["status"], 0) + 1

    payload = {
        "created": "2026-11-13",
        "source": "Europe PMC REST, resultType=lite",
        "records": len(per_record),
        "unique_studies": len(cache),
        "status_counts": dict(sorted(counts.items())),
        "by_dataset": {
            dataset: dict(
                sorted(
                    {
                        status: sum(
                            1
                            for item in per_record
                            if item["status"] == status and item["record_id"].startswith(prefix)
                        )
                        for status in counts
                    }.items()
                )
            )
            for dataset, prefix in (("eururology", "eu::"), ("glass_trialreviewbench", "glass::"))
        },
        "details": per_record,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("records", "unique_studies", "status_counts", "by_dataset")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
