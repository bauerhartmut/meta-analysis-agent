#!/usr/bin/env python3
"""Build reproducible inventory artifacts for the public benchmark review.

Reads only the downloaded/cloned raw data, never modifies it. Writes:
- dataset_inventory.json
- source_registry.json
- schema_mapping.json
- processed_data/yun_ico_records.jsonl
- validation/checksums.sha256

The JSONL projection deliberately leaves timepoint, source_quote and
structured rationale empty when the source does not provide them.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "raw_data"
YUN = RAW / "yun_llm_meta_analysis"
EI = RAW / "evidence_inference"
EI_V2 = RAW / "evidence_inference_v2_0"
DTA = RAW / "dta_cochrane" / "CL145_open_set_20181101"
DOWNLOADS = RAW / "downloads"

YUN_COMMIT = "1bc768d4d098c727c9866eeff909297c38a3e84c"
EI_COMMIT = "a661e8c14f973398380c8865cf2f27a535aaaf6d"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_yun() -> list[dict]:
    return json.loads(
        (YUN / "evaluation" / "data" / "annotated_rct_dataset.json").read_text(
            encoding="utf-8"
        )
    )


CONT_KEYS = [
    "intervention_group_size",
    "intervention_mean",
    "intervention_standard_deviation",
    "comparator_group_size",
    "comparator_mean",
    "comparator_standard_deviation",
]
BIN_KEYS = [
    "intervention_events",
    "intervention_group_size",
    "comparator_events",
    "comparator_group_size",
]


def strict_complete(rec: dict) -> bool:
    keys = CONT_KEYS if rec["outcome_type"] == "continuous" else BIN_KEYS
    return all(str(rec.get(key, "")).strip() for key in keys)


def numeric(value) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "")
    if text.lower() in {"", "na", "n/a", "nan", "none", "null"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def as_int(value) -> int | None:
    number = numeric(value)
    return int(number) if number is not None else None


def as_float(value) -> float | None:
    return numeric(value)


def yun_inventory(rows: list[dict]) -> dict:
    complete = [r for r in rows if strict_complete(r)]
    flag_complete = [r for r in rows if str(r.get("is_data_complete", "")).upper() == "TRUE"]
    by_split = Counter(r["split"] for r in rows)
    by_type = Counter(r["outcome_type"] for r in rows)
    by_split_type = Counter((r["split"], r["outcome_type"]) for r in rows)
    complete_by_split = Counter(r["split"] for r in complete)
    complete_by_type = Counter(r["outcome_type"] for r in complete)
    fields = CONT_KEYS + BIN_KEYS + ["notes"]
    time_marker = re.compile(
        r"\b(day|days|week|weeks|month|months|year|years|hour|hours|baseline|follow[- ]?up|at\s+\d+)\b",
        re.I,
    )
    return {
        "source": "Yun et al. 2024",
        "records": len(rows),
        "articles": len({r["pmcid"] for r in rows}),
        "records_by_split": dict(sorted(by_split.items())),
        "outcome_types": dict(sorted(by_type.items())),
        "outcome_types_by_split": {
            f"{split}_{otype}": count
            for (split, otype), count in sorted(by_split_type.items())
        },
        "records_per_article": {
            "min": min(Counter(r["pmcid"] for r in rows).values()),
            "max": max(Counter(r["pmcid"] for r in rows).values()),
        },
        "strict_complete": {
            "total": len(complete),
            "by_type": dict(sorted(complete_by_type.items())),
            "by_split": dict(sorted(complete_by_split.items())),
        },
        "is_data_complete_flag_true": len(flag_complete),
        "flag_vs_strict_difference": len(flag_complete) - len(complete),
        "field_nonempty": {
            field: sum(bool(str(r.get(field, "")).strip()) for r in rows)
            for field in fields
        },
        "outcomes_with_time_marker_text": sum(bool(time_marker.search(r["outcome"])) for r in rows),
        "table_flags": {
            "is_relevant_data_in_table_true": sum(
                str(r.get("is_relevant_data_in_table", "")).upper() == "TRUE" for r in rows
            ),
            "is_data_in_figure_graphics_true": sum(
                str(r.get("is_data_in_figure_graphics", "")).upper() == "TRUE" for r in rows
            ),
            "is_table_in_graphic_format_true": sum(
                str(r.get("is_table_in_graphic_format", "")).upper() == "TRUE" for r in rows
            ),
        },
        "available_fields": [
            "pmcid (Study ID)",
            "intervention",
            "comparator",
            "outcome",
            "outcome_type",
            "intervention_events",
            "intervention_group_size",
            "comparator_events",
            "comparator_group_size",
            "intervention_mean",
            "intervention_standard_deviation",
            "comparator_mean",
            "comparator_standard_deviation",
            "notes (informal annotator note)",
            "figure/table flags",
            "split",
        ],
        "absent_fields": [
            "separate timepoint field",
            "source quotation / evidence span",
            "structured rationale",
            "annotator ID",
            "individual (pre-adjudication) annotations",
        ],
        "known_issues": [
            "Dataset has 517 continuous and 182 binary records; the paper reports 516/183.",
            "412 records carry is_data_complete=TRUE, but only 410 satisfy all required fields; IDs 635/636 have no group sizes.",
            "PMC2667135 (record 12) has intervention SD 23.34 in the reference, while the article table shows 12.34; the value was not corrected.",
            "The paper reports 413 records (59.08%) with sufficient data; the released JSON yields 410 under a strict field rule and 412 under the released flag.",
        ],
    }


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", errors="replace", newline="") as fh:
        return list(csv.DictReader(fh))


def evidence_inventory() -> dict:
    ann = read_csv(EI_V2 / "annotations_merged.csv")
    prompts = read_csv(EI_V2 / "prompts_merged.csv")
    norm = {"significantly increase": "significantly increased"}
    labels = Counter(norm.get(r["Label"], r["Label"]) for r in ann)
    users = Counter(r["UserID"] for r in ann)
    by_prompt_user: dict[tuple[str, str], set[str]] = defaultdict(set)
    for r in ann:
        by_prompt_user[(r["PromptID"], r["UserID"])].add(norm.get(r["Label"], r["Label"]))
    by_prompt: dict[str, list[str]] = defaultdict(list)
    for (prompt_id, _user), values in by_prompt_user.items():
        if "invalid prompt" not in values:
            by_prompt[prompt_id].append(next(iter(values)))
    multi = {pid: vals for pid, vals in by_prompt.items() if len(vals) >= 2}
    unanimous = sum(len(set(vals)) == 1 for vals in multi.values())
    txt = {p.stem.replace("PMC", "") for p in (EI_V2 / "txt_files").glob("*.txt")}
    ann_pmcids = {r["PMCID"] for r in ann}
    return {
        "source": "Evidence Inference 2.0",
        "release": "v2.0 (official archive)",
        "annotations": len(ann),
        "prompts": len({r["PromptID"] for r in prompts}),
        "pmcids_annotated": len(ann_pmcids),
        "pmcids_with_prompts": len({r["PMCID"] for r in prompts}),
        "annotator_user_ids": dict(sorted(users.items())),
        "labels_normalized": dict(labels),
        "label_normalization": norm,
        "valid_label": dict(Counter(r["Valid Label"] for r in ann)),
        "valid_reasoning": dict(Counter(r["Valid Reasoning"] for r in ann)),
        "annotations_without_evidence_span": sum(
            r["Evidence Start"] in ("", "-1") or r["Evidence End"] in ("", "-1")
            for r in ann
        ),
        "fulltext_files": len(txt),
        "annotated_pmcids_without_fulltext": len(ann_pmcids - txt),
        "prompts_with_multiple_user_ids": len(multi),
        "unanimous_share_of_multi_user_prompts": round(unanimous / len(multi), 4),
        "available_fields": [
            "UserID",
            "PromptID",
            "PMCID (Study ID)",
            "Outcome",
            "Intervention",
            "Comparator",
            "Label (direction only)",
            "Annotations (evidence quote)",
            "Evidence Start/End",
            "Valid Label / Valid Reasoning (verifier)",
        ],
        "absent_fields": [
            "intervention N",
            "comparator N",
            "intervention mean / SD",
            "comparator mean / SD",
            "binary event counts",
            "separate timepoint field",
            "single adjudicated final label per prompt",
        ],
        "known_issues": [
            "The official v2.0 archive contains 693 rows labelled 'significantly increase'; they were normalized to 'significantly increased' for counting only.",
            "The repository snapshot (commit a661e8c) has a different annotations_merged.csv hash and 4,470 text files; the official archive has 4,454.",
            "UserID is not accompanied by a documented role column; the process description distinguishes prompt generator, annotator and verifier, so the rows are not two equivalent blinded raters.",
            "Some prompt/user pairs contain multiple evidence rows, including 1,027 rows with conflicting labels in the repository snapshot.",
        ],
    }


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child(element, name: str):
    for item in list(element):
        if local(item.tag) == name:
            return item
    return None


def dta_inventory() -> dict:
    root = ET.parse(DTA / "data.xml").getroot()
    reviews = [x for x in root.iter() if local(x.tag) == "review"]
    included_refs = 0
    excluded_refs = 0
    tests = 0
    findings_tests = 0
    results = 0
    complete_results = 0
    study_ids: list[str] = []
    for review in reviews:
        inc = child(review, "included")
        exc = child(review, "excluded")
        tst = child(review, "tests")
        fnd = child(review, "findings")
        inc_refs = [x for x in (inc.iter() if inc is not None else []) if local(x.tag) == "reference"]
        exc_refs = [x for x in (exc.iter() if exc is not None else []) if local(x.tag) == "reference"]
        included_refs += len(inc_refs)
        excluded_refs += len(exc_refs)
        for ref in inc_refs:
            sid = child(ref, "study_id")
            if sid is not None:
                study_ids.append("".join(sid.itertext()).strip())
        tests += sum(1 for x in (tst.iter() if tst is not None else []) if local(x.tag) == "test")
        findings_tests += sum(1 for x in (fnd.iter() if fnd is not None else []) if local(x.tag) == "test")
        for res in (x for x in review.iter() if local(x.tag) == "result"):
            results += 1
            names = {local(v.attrib.get("name", "")) for v in res if local(v.tag) == "value"}
            if {"tp", "fp", "fn", "tn"} <= names:
                complete_results += 1
    return {
        "source": "Norman, Leeflang, Neveol 2018 (Cochrane DTA)",
        "reviews": len(reviews),
        "included_references": included_refs,
        "unique_study_ids": len(set(study_ids)),
        "excluded_references": excluded_refs,
        "tests": tests,
        "findings_tests": findings_tests,
        "results": results,
        "results_with_complete_2x2": complete_results,
        "primary_fulltexts_included": False,
        "available_fields": [
            "review_id",
            "study_id",
            "index test",
            "target condition / reference standard",
            "tp / fp / fn / tn",
            "sensitivity / specificity",
            "forest plot image",
        ],
        "absent_fields": [
            "intervention mean / SD",
            "comparator mean / SD",
            "continuous outcome",
            "primary-study full text",
            "per-value source quotation",
        ],
        "known_issues": [
            "1,738 included study-review entries correspond to 1,663 unique study_id values.",
            "6,433 result elements exist, but only 5,848 contain a complete 2x2 table.",
            "The archive contains review-level extracted data and forest plots, not the primary RCT full texts.",
            "License is CC BY-NC 4.0; commercial use is excluded.",
        ],
    }


def schema_mapping() -> dict:
    return {
        "our_field": {
            "study_id": {
                "yun2024": "pmcid (prefixed PMC)",
                "evidence_inference": "PMCID",
                "dta": "review_id + study_id",
            },
            "intervention": {
                "yun2024": "intervention",
                "evidence_inference": "Intervention",
                "dta": "index test (not a treatment comparison)",
            },
            "comparator": {
                "yun2024": "comparator",
                "evidence_inference": "Comparator",
                "dta": "reference standard / comparison (not a treatment arm)",
            },
            "outcome": {
                "yun2024": "outcome",
                "evidence_inference": "Outcome",
                "dta": "target condition / diagnostic accuracy",
            },
            "timepoint": {
                "yun2024": None,
                "evidence_inference": None,
                "dta": None,
            },
            "intervention_n": {
                "yun2024": "intervention_group_size",
                "evidence_inference": None,
                "dta": "tp + fn (derived only)",
            },
            "comparator_n": {
                "yun2024": "comparator_group_size",
                "evidence_inference": None,
                "dta": "fp + tn (derived only)",
            },
            "intervention_mean": {
                "yun2024": "intervention_mean",
                "evidence_inference": None,
                "dta": None,
            },
            "intervention_sd": {
                "yun2024": "intervention_standard_deviation",
                "evidence_inference": None,
                "dta": None,
            },
            "comparator_mean": {
                "yun2024": "comparator_mean",
                "evidence_inference": None,
                "dta": None,
            },
            "comparator_sd": {
                "yun2024": "comparator_standard_deviation",
                "evidence_inference": None,
                "dta": None,
            },
            "source_quote": {
                "yun2024": None,
                "evidence_inference": "Annotations + Evidence Start/End",
                "dta": None,
            },
            "rationale": {
                "yun2024": "notes (informal, not adjudication rationale)",
                "evidence_inference": "Annotations (evidence quote); verifier flags",
                "dta": None,
            },
        },
        "coverage": {
            "yun2024": {
                "numeric_meta_analysis": "full for 410 strict-complete records",
                "semantic_ico": "yes",
                "timepoint": "no separate field",
                "individual_annotations": "no",
            },
            "evidence_inference": {
                "numeric_meta_analysis": "no",
                "semantic_ico": "yes",
                "timepoint": "no separate field",
                "individual_annotations": "yes, with role caveat",
            },
            "dta": {
                "numeric_meta_analysis": "no (diagnostic 2x2 only)",
                "semantic_ico": "partial / different task",
                "timepoint": "no",
                "individual_annotations": "no (published Cochrane extraction)",
            },
        },
        "transformation_rules": [
            "Yun PMCID is prefixed with PMC to form study_id.",
            "Empty Yun numeric cells become null, never zero.",
            "Yun notes are stored as annotator_notes, not as a structured rationale.",
            "Yun timepoint and source_quote are null because no such fields exist.",
            "Yun split is lowercased in the projection.",
            "Evidence Inference labels 'significantly increase' are normalized to 'significantly increased' only for counting.",
        ],
    }


def build_projection(rows: list[dict]) -> None:
    out = ROOT / "processed_data" / "yun_ico_records.jsonl"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            rec = {
                "record_id": r["id"],
                "source": "yun2024",
                "study_id": f"PMC{r['pmcid']}",
                "pmcid": r["pmcid"],
                "split": r["split"].lower(),
                "intervention": r["intervention"],
                "comparator": r["comparator"],
                "outcome": r["outcome"],
                "outcome_type": r["outcome_type"],
                "timepoint": None,
                "intervention_n": as_int(r.get("intervention_group_size")),
                "comparator_n": as_int(r.get("comparator_group_size")),
                "intervention_events": as_int(r.get("intervention_events")),
                "comparator_events": as_int(r.get("comparator_events")),
                "intervention_mean": as_float(r.get("intervention_mean")),
                "intervention_sd": as_float(r.get("intervention_standard_deviation")),
                "comparator_mean": as_float(r.get("comparator_mean")),
                "comparator_sd": as_float(r.get("comparator_standard_deviation")),
                "source_quote": None,
                "annotator_notes": r.get("notes") or None,
                "is_data_complete_flag": str(r.get("is_data_complete", "")).upper() == "TRUE",
                "strict_complete": strict_complete(r),
                "figure_table_flags": {
                    "data_in_figure_graphics": r.get("is_data_in_figure_graphics"),
                    "relevant_data_in_table": r.get("is_relevant_data_in_table"),
                    "table_in_graphic_format": r.get("is_table_in_graphic_format"),
                },
                "raw_numeric_values": {
                    field: r.get(field)
                    for field in CONT_KEYS + BIN_KEYS
                },
                "source_text_path": (
                    "raw_data/yun_llm_meta_analysis/evaluation/data/"
                    f"no_attributes_markdown_files/PMC{r['pmcid']}.md"
                ),
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def build_checksums() -> None:
    paths = [
        DOWNLOADS / "v2.0.tar.gz",
        DOWNLOADS / "CL145_open_set_20181101.zip",
        YUN / "evaluation" / "data" / "annotated_rct_dataset.json",
        YUN / "evaluation" / "data" / "annotated_rct_dataset.csv",
        YUN / "evaluation" / "data" / "DATASET.md",
        EI_V2 / "annotations_merged.csv",
        EI_V2 / "prompts_merged.csv",
        EI_V2 / "README.md",
        DTA / "data.xml",
        DTA / "readme.txt",
    ]
    paths += sorted((YUN / "evaluation" / "data" / "no_attributes_markdown_files").glob("*.md"))
    paths += sorted((YUN / "evaluation" / "data" / "abstract_and_results_xml_files").glob("*.xml"))
    out = ROOT / "validation" / "checksums.sha256"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        for path in paths:
            fh.write(f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}\n")


def build_source_registry() -> None:
    artifact_paths = {
        "downloads/v2.0.tar.gz": DOWNLOADS / "v2.0.tar.gz",
        "downloads/CL145_open_set_20181101.zip": DOWNLOADS / "CL145_open_set_20181101.zip",
        "yun_annotated_json": YUN / "evaluation" / "data" / "annotated_rct_dataset.json",
        "yun_annotated_csv": YUN / "evaluation" / "data" / "annotated_rct_dataset.csv",
        "evidence_annotations": EI_V2 / "annotations_merged.csv",
        "evidence_prompts": EI_V2 / "prompts_merged.csv",
        "dta_data": DTA / "data.xml",
        "dta_readme": DTA / "readme.txt",
    }
    def artifact_hash(name: str) -> dict:
        path = artifact_paths[name]
        return {"sha256": sha256(path), "bytes": path.stat().st_size}
    registry = {
        "generated_at": date.today().isoformat(),
        "policy": {
            "raw_data_modified": False,
            "raw_data_committed": False,
            "repository_pinning": "Git commit SHA pins the cloned repositories.",
            "archive_pinning": "SHA-256 pins downloaded archives.",
            "missing_values": "Null means not reported; no value is imputed.",
        },
        "downloads": {
            name: artifact_hash(name)
            for name in ["downloads/v2.0.tar.gz", "downloads/CL145_open_set_20181101.zip"]
        },
        "sources": [
            {
                "id": "yun2024",
                "title": "Automatically Extracting Numerical Results from Randomized Controlled Trials with Large Language Models",
                "authors": ["Hye Sun Yun", "David Pogrebitskiy", "Iain J. Marshall", "Byron C. Wallace"],
                "year": 2024,
                "paper": "https://proceedings.mlr.press/v252/yun24a.html",
                "pmc": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12448672/",
                "repository": "https://github.com/hyesunyun/llm-meta-analysis",
                "git_commit": YUN_COMMIT,
                "license": "Apache-2.0 (repository); article excerpts retain PMC article terms",
                "local_path": "public_benchmark/raw_data/yun_llm_meta_analysis",
                "artifact_hashes": {
                    name: artifact_hash(name)
                    for name in ["yun_annotated_json", "yun_annotated_csv"]
                },
            },
            {
                "id": "evidence_inference_v2",
                "title": "Evidence Inference 2.0: More Data, Better Models",
                "authors": ["Jay DeYoung", "Eric Lehman", "Benjamin Nye", "Iain Marshall", "Byron C. Wallace"],
                "year": 2020,
                "paper": "https://aclanthology.org/2020.bionlp-1.13/",
                "repository": "https://github.com/jayded/evidence-inference",
                "download": "https://evidence-inference.ebm-nlp.com/v2.0.tar.gz",
                "git_commit": EI_COMMIT,
                "license": "MIT (code/annotations); article texts retain PMC terms",
                "local_path": "public_benchmark/raw_data/evidence_inference_v2_0",
                "artifact_hashes": {
                    name: artifact_hash(name)
                    for name in ["evidence_annotations", "evidence_prompts"]
                },
            },
            {
                "id": "dta_cochrane",
                "title": "Data Extraction and Synthesis in Systematic Reviews of Diagnostic Test Accuracy",
                "authors": ["C. Norman", "M. Leeflang", "A. Neveol"],
                "year": 2018,
                "paper": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6371350/",
                "record": "https://zenodo.org/record/2574710",
                "dataset_record": "https://zenodo.org/api/records/1303259",
                "download": "https://zenodo.org/api/records/1303259/files/CL145_open_set_20181101.zip/content",
                "license": "CC BY-NC 4.0",
                "local_path": "public_benchmark/raw_data/dta_cochrane/CL145_open_set_20181101",
                "artifact_hashes": {
                    name: artifact_hash(name)
                    for name in ["dta_data", "dta_readme"]
                },
            },
        ],
    }
    (ROOT / "source_registry.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    rows = read_yun()
    inventory = {
        "generated_at": date.today().isoformat(),
        "yun2024": yun_inventory(rows),
        "evidence_inference_v2": evidence_inventory(),
        "dta_cochrane": dta_inventory(),
    }
    (ROOT / "dataset_inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "schema_mapping.json").write_text(
        json.dumps(schema_mapping(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    build_projection(rows)
    build_checksums()
    build_source_registry()
    print("inventory written")
    print(json.dumps({
        "yun_records": inventory["yun2024"]["records"],
        "yun_articles": inventory["yun2024"]["articles"],
        "yun_strict_complete": inventory["yun2024"]["strict_complete"]["total"],
        "ei_annotations": inventory["evidence_inference_v2"]["annotations"],
        "dta_results_complete": inventory["dta_cochrane"]["results_with_complete_2x2"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
