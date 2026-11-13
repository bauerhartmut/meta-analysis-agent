#!/usr/bin/env python3
"""Prioritize the 415 P0 full-text candidates without selecting a final holdout.

The ranking is a deterministic triage aid, not a quality score and not a final
eligibility decision. Human-confirmed manual inclusions rank first. Rule-based
candidates are kept as reserves with explicit RCT signals and risk flags.
No model, no network, no invented values.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evaluation" / "c1_pilot" / "holdout_p0_20261112"
SCREENING = OUT / "screening_decisions_v2.jsonl"
CANDIDATES = OUT / "candidates.jsonl"
SIGNOFF = OUT / "manual_review_signoff_v1.csv"
JSON_PATH = OUT / "fulltext_candidate_priority_v1.json"
CSV_PATH = OUT / "fulltext_candidate_priority_v1.csv"
MD_PATH = OUT / "fulltext_candidate_priority_v1.md"

PRIORITY_WEIGHT = {"hoch": 300, "mittel": 200, "niedrig": 100}
PRIORITY_ORDER = {"hoch": 0, "mittel": 1, "niedrig": 2}


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def evidence_signals(title: str, abstract: str, pub_types: list[str]) -> tuple[list[str], int]:
    text = f"{title} {abstract}".lower()
    pub_type_text = " ".join(pub_types).lower()
    signals: list[str] = []
    score = 0

    if "randomized controlled trial" in pub_type_text:
        signals.append("pubtype_rct")
        score += 80
    elif "randomized" in pub_type_text:
        signals.append("pubtype_randomized")
        score += 40

    if has(r"\brandomi[sz]ed\b", title):
        signals.append("title_randomized")
        score += 60
    if has(r"\brandomi[sz]ed\b", abstract):
        signals.append("abstract_randomized")
        score += 40
    if has(r"\bplacebo\b", text):
        signals.append("placebo")
        score += 25
    if has(r"\b(?:two|2)[ -]?(?:arm|arms|parallel|groups?)\b", text) or has(r"\b[12]:1\b", text):
        signals.append("two_group_signal")
        score += 20
    if has(r"\bprimary (?:outcome|endpoint)\b", text):
        signals.append("primary_outcome")
        score += 15
    if has(r"\bdouble[- ]blind\b", text):
        signals.append("double_blind")
        score += 10
    if has(r"\b(?:secondary|post[- ]hoc|prespecified|preplanned) analysis\b", text):
        signals.append("secondary_analysis")
        score += 10
    return signals, score


def risk_signals(title: str, abstract: str) -> tuple[list[str], int]:
    text = f"{title} {abstract}".lower()
    risks: list[str] = []
    penalty = 0

    checks = [
        ("systematic_review_or_meta_analysis", r"\b(?:systematic review|meta[- ]analysis)\b", 200),
        ("pooled_analysis", r"\bpooled analysis\b", 80),
        ("economic_analysis", r"\b(?:cost[- ]effectiveness|cost[- ]utility|budget impact|economic evaluation)\b", 150),
        ("qualitative", r"\bqualitative\b", 200),
        ("cross_sectional", r"\bcross[- ]sectional\b", 100),
        (
            "observational_or_cohort",
            r"\b(?:observational (?:study|analysis|cohort)|(?:retrospective|prospective|real-world) cohort|cohort study)\b",
            100,
        ),
        ("protocol", r"\b(?:study protocol|protocol for)\b", 150),
        ("multi_arm", r"\b(?:three|four|3|4)[ -]?(?:arms?|conditions?|groups?)\b", 150),
        ("biomarker_or_diagnostic", r"\b(?:biomarker|diagnostic)\b", 80),
    ]
    for label, pattern, points in checks:
        if has(pattern, text):
            risks.append(label)
            penalty += points
    if has(r"\bfeasibility\b", title.lower()):
        risks.append("feasibility")
        penalty += 50
    return risks, penalty


def main() -> None:
    screening = {row["pmcid"]: row for row in read_jsonl(SCREENING)}
    candidates = {row["pmcid"]: row for row in read_jsonl(CANDIDATES)}
    with SIGNOFF.open(encoding="utf-8", newline="") as handle:
        signoff = {row["pmcid"]: row for row in csv.DictReader(handle)}

    manual_includes = {
        pmcid: row
        for pmcid, row in signoff.items()
        if row["final_decision"] == "einschluss"
    }

    rows: list[dict] = []
    for pmcid, decision in screening.items():
        if decision["decision"] != "include_for_fulltext":
            continue
        candidate = candidates.get(pmcid, {})
        manual = manual_includes.get(pmcid)
        title = decision.get("title") or candidate.get("title") or manual.get("title", "")
        abstract = candidate.get("abstract", "")
        pub_types = candidate.get("pub_types", [])
        signals, evidence_score = evidence_signals(title, abstract, pub_types)
        risks, penalty = risk_signals(title, abstract)

        score = evidence_score - penalty
        manual_priority = ""
        if manual:
            manual_priority = manual["priority"]
            score += 1000 + PRIORITY_WEIGHT.get(manual_priority, 0)
            tier = "A_menschlich_bestaetigt"
            source = "manual_human_confirmed"
            reason_code = manual["reason_code"]
        else:
            reason_code = ""
            source = "rule_based_screening"
            tier = "B_rct_kernsignal" if score >= 120 else "C_rct_moeglich" if score >= 40 else "D_schwach"

        rows.append(
            {
                "pmcid": pmcid,
                "pmid": decision.get("pmid") or candidate.get("pmid", ""),
                "doi": decision.get("doi") or candidate.get("doi", ""),
                "title": title,
                "journal": decision.get("journal") or candidate.get("journal", ""),
                "pub_year": decision.get("pub_year") or candidate.get("pub_year", ""),
                "source": source,
                "tier": tier,
                "manual_priority": manual_priority,
                "reason_code": reason_code,
                "score": score,
                "signals": signals,
                "risk_flags": risks,
                "shortlist_30": False,
                "shortlist_rank": "",
                "selection_note": "",
            }
        )

    rows.sort(
        key=lambda row: (
            0 if row["source"] == "manual_human_confirmed" else 1,
            PRIORITY_ORDER.get(row["manual_priority"], 9),
            -row["score"],
            row["pmcid"],
        )
    )
    for rank, row in enumerate(rows, 1):
        row["priority_rank"] = rank
        if rank <= 30:
            row["shortlist_30"] = True
            row["shortlist_rank"] = rank
            row["selection_note"] = "Shortlist 30; Volltextpruefung entscheidet."
        elif row["source"] == "manual_human_confirmed":
            row["selection_note"] = "Menschlich bestaetigt; Reserve fuer die 30er-Auswahl."
        elif row["tier"] == "B_rct_kernsignal":
            row["selection_note"] = "Regelbasiert; Reserve, falls manuelle Shortlist im Volltext nicht traegt."
        else:
            row["selection_note"] = "Regelbasiert; nachrangige Reserve."

    shortlist = [row for row in rows if row["shortlist_30"]]
    summary = {
        "priority_id": "p0_fulltext_candidate_priority_v1",
        "created_at": "2026-11-13",
        "status": "shortlist_ready_pending_fulltext_review",
        "candidate_count": len(rows),
        "manual_includes": len(manual_includes),
        "shortlist_count": len(shortlist),
        "target_articles": 30,
        "model_used": False,
        "network_used": False,
        "final_selection": False,
        "method": {
            "manual_first": "Alle 36 menschlich bestaetigten Einschluesse erhalten Vorrang.",
            "priority_weight": PRIORITY_WEIGHT,
            "rct_signals": "PubMed-Typ, Randomisierung, Placebo, Zweiarm-/Parallelsignal, primaerer Endpunkt, Doppelblind, Sekundaeranalyse.",
            "risk_flags": "Systematic Review/Metaanalyse, gepoolte Analyse, Kostenanalyse, qualitativ, Querschnitt, Beobachtung/Kohorte, Protokoll, Mehrarm, Biomarker/Diagnostik, Feasibility.",
            "shortlist": "Die 30 hoechsten Scores; keine endgueltige Auswahl und keine Eignungsentscheidung.",
        },
        "counts": {
            "by_source": dict(Counter(row["source"] for row in rows)),
            "by_tier": dict(Counter(row["tier"] for row in rows)),
            "shortlist_by_priority": dict(Counter(row["manual_priority"] for row in shortlist)),
            "all_by_manual_priority": dict(Counter(row["manual_priority"] for row in rows)),
        },
        "shortlist_30": shortlist,
        "candidates": rows,
    }
    JSON_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fields = [
        "priority_rank",
        "pmcid",
        "pmid",
        "doi",
        "title",
        "journal",
        "pub_year",
        "source",
        "tier",
        "manual_priority",
        "reason_code",
        "score",
        "shortlist_30",
        "shortlist_rank",
        "signals",
        "risk_flags",
        "selection_note",
    ]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["signals"] = ";".join(row["signals"])
            out["risk_flags"] = ";".join(row["risk_flags"])
            writer.writerow(out)

    lines = [
        "# P0-Volltextkandidaten: Priorisierung und 30er-Shortlist",
        "",
        "Stand: 2026-11-13",
        "Status: **SHORTLIST BEREIT; VOLLTEXT-PRÜFUNG UND ENDAUSWAHL OFFEN**.",
        "",
        "Die Priorisierung ist eine deterministische Triage-Hilfe, kein Qualitätsurteil",
        "und keine endgültige Eignungsentscheidung. Grundlage sind ausschließlich",
        "Titel, Abstract, PubMed-Typen und die bereits menschlich bestätigten",
        "Einschlüsse. Kein Modelllauf, kein Netzabruf.",
        "",
        "## Kennzahlen",
        "",
        f"- Kandidaten insgesamt: **{len(rows)}**",
        f"- Menschlich bestätigte Einschlüsse: **{len(manual_includes)}**",
        f"- Shortlist: **{len(shortlist)}** von 30 Zielartikeln",
        f"- Reservesätze: **{len(rows) - len(shortlist)}**",
        f"- Shortlist nach Priorität: {dict(Counter(row['manual_priority'] for row in shortlist))}",
        "",
        "## 30er-Shortlist",
        "",
        "| Rang | PMC | Kurztitel | Prio | Score | Quelle | Signale | Risiken |",
        "|---:|---|---|---|---:|---|---|---|",
    ]
    for row in shortlist:
        short_title = row["title"].replace("|", "\\|")
        if len(short_title) > 72:
            short_title = short_title[:71].rstrip() + "..."
        lines.append(
            f"| {row['shortlist_rank']} | [{row['pmcid']}](https://pmc.ncbi.nlm.nih.gov/articles/{row['pmcid']}/) | "
            f"{short_title} | {row['manual_priority'] or '-'} | {row['score']} | {row['source']} | "
            f"{', '.join(row['signals']) or '-'} | {', '.join(row['risk_flags']) or '-'} |"
        )
    manual_reserve = [
        row for row in rows
        if row["source"] == "manual_human_confirmed" and not row["shortlist_30"]
    ]
    lines += [
        "",
        "## Menschlich bestätigte Reserve (6)",
        "",
        "| PMC | Prio | Score | Kurztitel |",
        "|---|---|---:|---|",
    ]
    for row in manual_reserve:
        short_title = row["title"].replace("|", "\\|")
        if len(short_title) > 72:
            short_title = short_title[:71].rstrip() + "..."
        lines.append(
            f"| [{row['pmcid']}](https://pmc.ncbi.nlm.nih.gov/articles/{row['pmcid']}/) | "
            f"{row['manual_priority']} | {row['score']} | {short_title} |"
        )
    lines += [
        "",
        "## Auswahlregel",
        "",
        "- Alle 36 menschlich bestätigten Einschlüsse stehen vor den regelbasierten",
        "  Kandidaten.",
        "- Innerhalb der menschlich bestätigten Fälle zählt zuerst die dokumentierte",
        "  Priorität, dann die Stärke der RCT-Signale.",
        "- Risikosignale senken den Rang, ersetzen aber keine Volltextprüfung.",
        "- Die sechs nicht in der 30er-Shortlist enthaltenen menschlich bestätigten",
        "  Fälle bleiben als Reserve erhalten.",
        "- Die 379 regelbasierten Kandidaten bleiben als Reserve für den Fall, dass",
        "  die manuelle Shortlist im Volltext nicht ausreicht.",
        "",
        "## Nächster Schritt",
        "",
        "Die 30 Shortlist-Artikel zuerst beschaffen und gegen die",
        "Volltext-Prüfvorlage prüfen. Erst danach werden 30 Artikel und 100 Records",
        "endgültig ausgewählt; ein Netzabruf ist dafür gesondert freizugeben.",
        "",
    ]
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["candidate_count", "manual_includes", "shortlist_count", "counts"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
