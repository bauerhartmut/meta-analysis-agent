#!/usr/bin/env python3
"""Deterministic abstract screening for the P0 candidate pool.

Reads the fixed criteria and the exported candidate list. Writes every
decision, a separate exclusion file with evidence, and summary counts.
No model call, no network access, no full-text access.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "evaluation" / "c1_pilot"
OUT = PILOT / "holdout_p0_20261112"
CANDIDATES = OUT / "candidates.jsonl"
CRITERIA = OUT / "screening_criteria_v1.json"
DECISIONS = OUT / "screening_decisions_v1.jsonl"
EXCLUSIONS = OUT / "screening_exclusions_v1.jsonl"
SUMMARY_JSON = OUT / "screening_summary_v1.json"
SUMMARY_MD = OUT / "screening_summary_v1.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def context(text: str, start: int, end: int, radius: int = 120) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    snippet = re.sub(r"\s+", " ", text[left:right]).strip()
    return ("..." if left else "") + snippet + ("..." if right < len(text) else "")


def evaluate(row: dict, rules: list[dict]) -> dict:
    matches: list[dict] = []
    fields = {
        "title": str(row.get("title") or ""),
        "abstract": str(row.get("abstract") or ""),
    }
    for rule in rules:
        pattern = re.compile(rule["pattern"], re.IGNORECASE)
        rule_fields = ("title",) if rule.get("scope") == "title" else ("title", "abstract")
        for field in rule_fields:
            text = fields[field]
            hit = pattern.search(text)
            if hit:
                matches.append(
                    {
                        "rule_id": rule["rule_id"],
                        "decision": rule["decision"],
                        "label": rule["label"],
                        "field": field,
                        "match": hit.group(0),
                        "evidence": context(text, hit.start(), hit.end()),
                    }
                )
    exclude_matches = [m for m in matches if m["decision"] == "exclude"]
    manual_matches = [m for m in matches if m["decision"] == "manual_review"]
    if exclude_matches:
        decision = "exclude"
        selected = exclude_matches
    elif manual_matches:
        decision = "manual_review"
        selected = manual_matches
    else:
        decision = "include_for_fulltext"
        selected = []
    return {
        "pmcid": row.get("pmcid", ""),
        "pmid": row.get("pmid", ""),
        "doi": row.get("doi", ""),
        "title": row.get("title", ""),
        "journal": row.get("journal", ""),
        "pub_year": row.get("pub_year", ""),
        "decision": decision,
        "reason_codes": [m["rule_id"] for m in selected],
        "reason_labels": [m["label"] for m in selected],
        "evidence": selected,
        "all_matches": matches,
        "screening_stage": "title_abstract",
        "screening_method": "deterministic_regex_v1",
        "human_review": False,
        "model_used": False,
    }


def main() -> None:
    criteria = json.loads(CRITERIA.read_text(encoding="utf-8"))
    if criteria.get("status") not in {
        "fixed_before_screening",
        "fixed_before_final_screening",
    }:
        raise SystemExit("criteria are not marked as fixed before screening")
    rules = criteria["rules"]
    rows = read_jsonl(CANDIDATES)
    if len(rows) != 596:
        raise SystemExit(f"expected 596 candidates, got {len(rows)}")

    decisions = [evaluate(row, rules) for row in rows]
    counts = Counter(row["decision"] for row in decisions)
    if sum(counts.values()) != len(rows):
        raise SystemExit("decision count does not match candidates")

    with DECISIONS.open("w", encoding="utf-8", newline="\n") as handle:
        for row in decisions:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    excluded = [row for row in decisions if row["decision"] == "exclude"]
    with EXCLUSIONS.open("w", encoding="utf-8", newline="\n") as handle:
        for row in excluded:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    reason_counts = Counter(
        code for row in decisions for code in row["reason_codes"]
    )
    manual_counts = Counter(
        code
        for row in decisions
        if row["decision"] == "manual_review"
        for code in row["reason_codes"]
    )
    summary = {
        "screening_id": "p0_abstract_screening_v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "criteria_id": criteria["criteria_id"],
        "criteria_version": criteria["version"],
        "criteria_sha256": sha256(CRITERIA),
        "candidate_file": str(CANDIDATES.relative_to(PILOT)),
        "candidate_sha256": sha256(CANDIDATES),
        "records": len(rows),
        "counts": {
            "exclude": counts.get("exclude", 0),
            "manual_review": counts.get("manual_review", 0),
            "include_for_fulltext": counts.get("include_for_fulltext", 0),
        },
        "reason_counts_all_decisions": dict(sorted(reason_counts.items())),
        "manual_reason_counts": dict(sorted(manual_counts.items())),
        "excluded_pmids": [row["pmcid"] for row in excluded],
        "model_used": False,
        "human_review": False,
        "fulltext_screening": False,
        "limitations": [
            "Nur Titel und Abstract; keine Volltextpruefung.",
            "Regelbasiert und deterministisch; keine klinische Endentscheidung.",
            "include_for_fulltext ist eine vorlaeufige Volltextkandidatur.",
            "Manuelle Pruefung ist fuer manual_review und alle endgueltigen Einschluesse erforderlich.",
        ],
    }
    SUMMARY_JSON.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# P0-Abstract-Screening v1",
        "",
        f"Kriterien: [`{CRITERIA.name}`]({CRITERIA.name})",
        f"Kandidaten: **{len(rows)}**",
        "Methode: deterministische Regeln, kein Modellaufruf.",
        "",
        "| Entscheidung | Anzahl |",
        "|---|---:|",
        f"| Ausschluss | {counts.get('exclude', 0)} |",
        f"| Manuelle Prüfung | {counts.get('manual_review', 0)} |",
        f"| Vorläufig für Volltext | {counts.get('include_for_fulltext', 0)} |",
        f"| **Gesamt** | **{len(rows)}** |",
        "",
        "## Ausschlussgründe",
        "",
        "| Regel | Anzahl Records |",
        "|---|---:|",
    ]
    for code in sorted(reason_counts):
        if any(
            row["decision"] == "exclude" and code in row["reason_codes"]
            for row in decisions
        ):
            lines.append(f"| {code} | {reason_counts[code]} |")
    lines.extend(
        [
            "",
            "Mehrfachgründe sind möglich; die Regeltabelle zählt Records mit der jeweiligen",
        "Regel, nicht disjunkte Entscheidungen.",
        "",
        "## Manuelle Prüfung",
            "",
            "| Regel | Anzahl Records |",
            "|---|---:|",
        ]
    )
    for code in sorted(manual_counts):
        lines.append(f"| {code} | {manual_counts[code]} |")
    lines.extend(
        [
            "",
            "Jeder Ausschluss ist mit PMCID, Regel-ID, Begründung und Textbeleg in",
            f"[`{EXCLUSIONS.name}`]({EXCLUSIONS.name}) dokumentiert. Alle 596",
            "Entscheidungen stehen in",
            f"[`{DECISIONS.name}`]({DECISIONS.name}).",
            "",
            "**Keine endgültige Eignung:** Parallelgruppen, zwei Arme und",
            "extrahierbare N/Mean/SD/Events werden erst im Volltext geprüft.",
            "Kein Modelllauf.",
            "",
        ]
    )
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
