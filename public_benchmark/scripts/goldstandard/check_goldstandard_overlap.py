"""Prueft Ueberschneidungen zwischen Goldstandard-Kandidaten und den
bestehenden Datensaetzen (Yun, G5, Cross-Validation v1).

Verglichen werden PMCIDs und DOIs. Fuer Datensaetze, die nur PMIDs fuehren
(PICO-Corpus), werden die eigenen PMCIDs ueber Europe PMC auf PMIDs abgebildet.

Ausgabe: ``dataset_overlap_report.json``. Alle Abfragen sind lesend; es wird
nichts in bestehenden Referenzdaten veraendert.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve()
BENCH = HERE.parents[2]
CROSSVAL = BENCH / "evaluation" / "multi_model_cross_validation"
GOLD = CROSSVAL / "goldstandard_datasets"
OUT = CROSSVAL / "dataset_overlap_report.json"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UA = {"User-Agent": "meta-analysis-agent/overlap-check"}


def norm_doi(value: str) -> str:
    text = (value or "").strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:", "https://dx.doi.org/"):
        if text.startswith(prefix):
            text = text[len(prefix) :]
    return text


def pmcids(path: Path, field: str) -> set[str]:
    ids = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line).get(field)
        if value:
            text = str(value)
            ids.add(text if text.upper().startswith("PMC") else f"PMC{text}")
    return ids


def europepmc(query: str) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode(
        {"query": query, "format": "json", "resultType": "lite", "pageSize": 100}
    )
    request = urllib.request.Request(f"{EPMC}?{params}", headers=UA)
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.load(response)
    time.sleep(0.4)
    return payload.get("resultList", {}).get("result", [])


def resolve_dois(dois: list[str]) -> dict[str, dict[str, str]]:
    resolved: dict[str, dict[str, str]] = {}
    for doi in dois:
        try:
            hits = europepmc(f'DOI:"{doi}"')
        except Exception as error:  # Netzfehler dokumentieren, nicht verschweigen
            resolved[doi] = {"error": str(error)}
            continue
        if hits:
            hit = hits[0]
            resolved[doi] = {
                "pmid": hit.get("pmid", ""),
                "pmcid": hit.get("pmcid", ""),
                "title": (hit.get("title") or "")[:120],
            }
        else:
            resolved[doi] = {"pmid": "", "pmcid": ""}
    return resolved


def resolve_pmcids(ids: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for start in range(0, len(ids), 20):
        chunk = ids[start : start + 20]
        query = " OR ".join(f"PMCID:{item}" for item in chunk)
        try:
            hits = europepmc(query)
        except Exception:
            continue
        for hit in hits:
            pmcid = hit.get("pmcid", "")
            if pmcid:
                mapping[f"PMC{pmcid}" if not pmcid.upper().startswith("PMC") else pmcid] = hit.get(
                    "pmid", ""
                )
    return mapping


def main() -> int:
    yun = set()
    for name in ("yun_c1_frozen_275.jsonl", "yun_c1_dev_26.jsonl", "yun_c1_test_249.jsonl"):
        yun |= pmcids(BENCH / "processed_data" / name, "study_id")

    availability = json.loads((CROSSVAL / "fulltext_availability_v1.json").read_text(encoding="utf-8"))
    crossval_pmc = {row["pmcid"] for row in availability["records"]}
    crossval_doi = {norm_doi(row.get("doi", "")) for row in availability["records"]} - {""}

    g5_manifest = json.loads(
        (BENCH / "evaluation" / "c1_pilot" / "holdout_p0_20261112" / "fulltext_retrieval_manifest_v1.json").read_text(
            encoding="utf-8"
        )
    )
    g5_pmc = {row["pmcid"] for row in g5_manifest["records"]}
    g5_doi = {norm_doi(row.get("doi", "")) for row in g5_manifest["records"]} - {""}

    eu_records = [
        json.loads(line)
        for line in (GOLD / "eururology_v1" / "records.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    eu_doi = {norm_doi(row["trial_doi"]) for row in eu_records} - {""}
    eu_resolved = resolve_dois(sorted(eu_doi))
    eu_pmc = {item.get("pmcid", "") for item in eu_resolved.values() if item.get("pmcid")}

    pico_dir = GOLD / "pico_corpus_v1" / "records.jsonl"
    pico_pmid: set[str] = set()
    pico_note = "Adapter nicht erzeugt"
    if pico_dir.exists():
        pico_rows = [json.loads(line) for line in pico_dir.read_text(encoding="utf-8").splitlines() if line.strip()]
        pico_pmid = {str(row.get("pmid", "")) for row in pico_rows if row.get("pmid")}
        pico_note = f"{len(pico_rows)} Records, {len(pico_pmid)} PMIDs"

    our_pmc = crossval_pmc | g5_pmc | yun
    our_pmid_map = resolve_pmcids(sorted(our_pmc))

    import gzip

    glass_path = GOLD / "glass_v1" / "original" / "trialreviewbench-study-results-v1.0.0.jsonl.gz"
    glass_pmid: set[str] = set()
    glass_records = 0
    if glass_path.exists():
        with gzip.open(glass_path, "rt", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                glass_records += 1
                glass_pmid.update(json.loads(line)["input"].get("study_pmids", []))

    payload = {
        "created": "2026-11-13",
        "method": "PMCID- und DOI-Vergleich; PMID-Abbildung ueber Europe PMC",
        "sets": {
            "yun_articles": len(yun),
            "g5_articles": len(g5_pmc),
            "crossval_articles": len(crossval_pmc),
        },
        "eururology": {
            "trials": len({row["trial_name_raw"] for row in eu_records}),
            "dois": len(eu_doi),
            "doi_resolved": sum(1 for item in eu_resolved.values() if item.get("pmcid")),
            "overlap_yun_pmcid": sorted(eu_pmc & yun),
            "overlap_g5_pmcid": sorted(eu_pmc & g5_pmc),
            "overlap_crossval_pmcid": sorted(eu_pmc & crossval_pmc),
            "overlap_doi": sorted(eu_doi & (crossval_doi | g5_doi)),
            "resolution": eu_resolved,
        },
        "pico_corpus": {
            "note": pico_note,
            "pmids": len(pico_pmid),
            "overlap_pmid": sorted(pico_pmid & set(our_pmid_map.values())),
        },
        "glass_trialreviewbench": {
            "records": glass_records,
            "pmids": len(glass_pmid),
            "overlap_pmid": sorted(glass_pmid & set(our_pmid_map.values())),
        },
        "our_pmids_resolved": len(our_pmid_map),
        "verdict": {},
    }
    verdict = payload["verdict"]
    verdict["eururology_independent"] = not (
        payload["eururology"]["overlap_yun_pmcid"]
        or payload["eururology"]["overlap_g5_pmcid"]
        or payload["eururology"]["overlap_crossval_pmcid"]
        or payload["eururology"]["overlap_doi"]
    )
    verdict["pico_independent"] = not payload["pico_corpus"]["overlap_pmid"]
    verdict["glass_independent"] = not payload["glass_trialreviewbench"]["overlap_pmid"]
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("sets", "verdict")}, ensure_ascii=False))
    print(
        "EU: doisl", len(eu_doi), "aufgeloest", payload["eururology"]["doi_resolved"],
        "Overlap", payload["eururology"]["overlap_yun_pmcid"],
        payload["eururology"]["overlap_g5_pmcid"],
        payload["eururology"]["overlap_crossval_pmcid"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
