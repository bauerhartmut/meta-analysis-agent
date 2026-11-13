#!/usr/bin/env python3
"""Build assisted fulltext dossiers for the high-priority P0 shortlist.

Deterministic JATS parsing only. The dossier inventories tables, arm headers,
candidate outcome rows and verbatim method snippets. It does not fill the
extraction template, estimate values or make eligibility decisions.
"""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "public_benchmark" / "evaluation" / "c1_pilot" / "holdout_p0_20261112"
PRIORITY = OUT / "fulltext_candidate_priority_v1.json"
MANIFEST = OUT / "fulltext_retrieval_manifest_v1.json"
JSON_PATH = OUT / "fulltext_review_high_v1.json"
CSV_PATH = OUT / "fulltext_review_high_v1.csv"
MD_PATH = OUT / "fulltext_review_high_v1.md"

SIGNAL_TERMS = {
    "randomized": r"\brandomi[sz]ed\b|\brandomi[sz]ation\b",
    "randomly_assigned": r"\brandomly (?:assigned|allocated)\b",
    "parallel": r"\bparallel(?:[ -]group)?\b",
    "two_arm": r"\b(?:two|2)[ -](?:arm|group)s?\b",
    "placebo": r"\bplacebo\b",
    "double_blind": r"\bdouble[ -]blind\b",
    "open_label": r"\bopen[ -]label\b",
    "crossover": r"\bcrossover\b|\bcross-over\b",
    "non_inferiority": r"\bnon[ -]inferiority\b",
    "pooled": r"\bpooled\b",
    "secondary_analysis": r"\bsecondary analysis\b",
    "post_hoc": r"\bpost[ -]hoc\b",
    "economic": r"\bcost[- ]effectiveness\b|\bcost[- ]utility\b|\beconomic evaluation\b",
    "observational": r"\bobservational\b|\bcohort study\b",
        "substudy": r"\bsubstudy\b",
    "single_group": r"\bsingle[- ]group\b",
}

RISK_TERMS = {
    "pooled": "pooled_analysis",
    "secondary_analysis": "secondary_analysis",
    "post_hoc": "post_hoc",
    "economic": "economic_analysis",
    "crossover": "crossover_design",
    "non_inferiority": "non_inferiority_design",
    "observational": "observational_language",
    "substudy": "substudy_or_parent_trial",
    "single_group": "single_group_parent",
    "open_label": "open_label_design",
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(elem: ET.Element | None) -> str:
    if elem is None:
        return ""
    return " ".join("".join(elem.itertext()).split())


def direct_texts(elem: ET.Element) -> list[str]:
    return [
        text_of(child)
        for child in elem
        if local_name(child.tag) in {"p", "title", "label", "caption"}
        and text_of(child)
    ]


def walk_paragraphs(elem: ET.Element, section: str = "") -> list[dict]:
    rows = []
    for child in elem:
        tag = local_name(child.tag)
        if tag == "sec":
            title = next((x for x in child if local_name(x.tag) == "title"), None)
            sub = text_of(title)
            rows.extend(walk_paragraphs(child, sub or section))
        elif tag == "p":
            text = text_of(child)
            if text:
                rows.append({"section": section, "text": text})
    return rows


def table_info(table_wrap: ET.Element) -> dict:
    label = text_of(next((x for x in table_wrap if local_name(x.tag) == "label"), None))
    caption = text_of(next((x for x in table_wrap if local_name(x.tag) == "caption"), None))
    table = next((x for x in table_wrap.iter() if local_name(x.tag) == "table"), None)
    if table is None:
        return {"label": label, "caption": caption, "arm_headers": [], "rows": [], "all_rows": 0}

    trs = [x for x in table.iter() if local_name(x.tag) == "tr"]
    parsed = []
    header = None
    for tr in trs:
        cells = [text_of(c) for c in tr if local_name(c.tag) in {"th", "td"}]
        is_header = any(local_name(c.tag) == "th" for c in tr)
        if header is None and is_header:
            header = cells
        parsed.append({"cells": cells, "is_header": is_header})

    arm_headers = header[1:] if header else []
    data_rows = []
    for index, row in enumerate(parsed, 1):
        if row["is_header"] or len(row["cells"]) < 2:
            continue
        values = row["cells"][1:]
        if not values or not any(re.search(r"\d", value) for value in values):
            continue
        data_rows.append(
            {
                "row_index": index,
                "row_label": row["cells"][0],
                "values": values,
                "row_text": " | ".join(row["cells"]),
            }
        )
    return {
        "label": label,
        "caption": caption,
        "header": header or [],
        "arm_headers": arm_headers,
        "arm_sizes": [
            {"header": value, "n": int(m.group(1))}
            for value in arm_headers
            if (m := re.search(r"\bn\s*=\s*(\d+)", value, re.IGNORECASE))
        ],
        "rows": data_rows,
        "all_rows": len(parsed),
    }


def snippets(paragraphs: list[dict], max_items: int = 8) -> list[dict]:
    found = []
    seen = set()
    for paragraph in paragraphs:
        for sentence in re.split(r"(?<=[.!?])\s+", paragraph["text"]):
            normalized = sentence.strip()
            if len(normalized) < 25 or normalized in seen:
                continue
            if re.search(
                r"\b(?:randomi[sz]ed|randomly|allocated|parallel|two[ -]arm|placebo|"
                r"sample size|primary outcome|secondary outcome|informed consent|"
                r"eligibility|inclusion criteria)\b",
                normalized,
                re.IGNORECASE,
            ):
                seen.add(normalized)
                found.append(
                    {
                        "section": paragraph["section"],
                        "quote": normalized[:900],
                    }
                )
                if len(found) >= max_items:
                    return found
    return found


def main() -> None:
    priority = json.loads(PRIORITY.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fulltext = {row["pmcid"]: row for row in manifest["records"] if row.get("saved")}
    high = [row for row in priority["shortlist_30"] if row["manual_priority"] == "hoch"]
    if len(high) != 14:
        raise SystemExit(f"expected 14 high-priority rows, got {len(high)}")

    articles = []
    csv_rows = []
    for number, row in enumerate(high, 1):
        pmcid = row["pmcid"]
        source = fulltext.get(pmcid)
        if source is None:
            raise SystemExit(f"missing XML for high-priority {pmcid}")
        root = ET.fromstring(Path(source["local_path"]).read_bytes())
        body = next((x for x in root if local_name(x.tag) == "body"), None)
        paragraphs = walk_paragraphs(body) if body is not None else []
        title = text_of(next((x for x in root.iter() if local_name(x.tag) == "article-title"), None))
        abstract = " ".join(
            text_of(p)
            for p in root.iter()
            if local_name(p.tag) == "abstract"
        )
        method_text = " ".join(
            p["text"] for p in paragraphs
            if re.search(r"method|random|participant|intervention|outcome|statistic|design|sample", p["section"], re.I)
        )
        searchable = " ".join([title, abstract, method_text])
        signal_hits = {
            name: len(re.findall(pattern, searchable, re.IGNORECASE))
            for name, pattern in SIGNAL_TERMS.items()
        }
        tables = [
            table_info(tw)
            for tw in root.iter()
            if local_name(tw.tag) == "table-wrap"
        ]
        candidate_tables = [table for table in tables if len(table["arm_headers"]) >= 2 and table["rows"]]
        candidate_rows = sum(len(table["rows"]) for table in candidate_tables)
        multiple_arm_sizes = any(len(table["arm_sizes"]) > 2 for table in candidate_tables)
        risk_flags = {
            label for key, label in RISK_TERMS.items() if signal_hits.get(key, 0)
        }
        if multiple_arm_sizes:
            risk_flags.add("multiple_arm_sizes")
        risk_flags = sorted(risk_flags)
        triage_notes = []
        if not signal_hits.get("randomized"):
            triage_notes.append("Kein Randomisierungssignal in Titel/Abstract/Methoden; Eignung manuell prüfen.")
        if not (signal_hits.get("parallel") or signal_hits.get("two_arm") or signal_hits.get("placebo")):
            triage_notes.append("Kein explizites Parallel-/Zweiarm-/Placebo-Signal; Design manuell prüfen.")
        if not any(table["arm_sizes"] for table in candidate_tables):
            triage_notes.append("Keine Arm-N in Tabellenheadern gefunden; N manuell suchen.")
        if multiple_arm_sizes:
            triage_notes.append("Mehr als zwei Arm-N in einer Tabelle; Armzusammenführung ausschließen.")
        if not candidate_tables:
            triage_notes.append("Keine Tabelle mit mindestens zwei Arm-Headern; Outcomes manuell suchen.")
        article = {
            "article_number": number,
            "pmcid": pmcid,
            "doi": row.get("doi", ""),
            "title": title,
            "priority": row["manual_priority"],
            "shortlist_rank": row["shortlist_rank"],
            "source_xml": source["local_path"],
            "source_sha256": source["sha256"],
            "assisted_only": True,
            "final_decision": "offen",
            "reviewer": "offen",
            "eligibility": {
                "rct_signal_suspected": bool(signal_hits.get("randomized")),
                "parallel_two_arm_signal": bool(
                    signal_hits.get("parallel") or signal_hits.get("two_arm") or signal_hits.get("placebo")
                ),
                "randomization_signal": bool(signal_hits.get("randomized")),
                "two_arm_table_signal": bool(candidate_tables),
                "arm_sizes_detected": sum(len(table["arm_sizes"]) for table in candidate_tables),
                "multiple_arm_sizes": multiple_arm_sizes,
                "candidate_tables": len(candidate_tables),
                "candidate_rows": candidate_rows,
                "manual_check_required": True,
            },
            "signals": {key: value for key, value in signal_hits.items() if value},
            "risk_flags": risk_flags,
            "triage_notes": triage_notes,
            "tables": [
                {
                    "label": table["label"],
                    "caption": table["caption"],
                    "arm_headers": table["arm_headers"],
                    "arm_sizes": table["arm_sizes"],
                    "data_rows": len(table["rows"]),
                }
                for table in tables
            ],
            "candidate_tables": [
                {
                    "label": table["label"],
                    "caption": table["caption"],
                    "arm_headers": table["arm_headers"],
                    "arm_sizes": table["arm_sizes"],
                    "rows": table["rows"],
                }
                for table in candidate_tables
            ],
            "method_snippets": snippets(paragraphs),
            "review_status": "ready_for_human_fulltext_review",
        }
        articles.append(article)

        for table in candidate_tables:
            for table_row in table["rows"]:
                csv_rows.append(
                    {
                        "pmcid": pmcid,
                        "priority": row["manual_priority"],
                        "table_label": table["label"],
                        "table_caption": table["caption"],
                        "arm_headers": " || ".join(table["arm_headers"]),
                        "row_index": table_row["row_index"],
                        "row_label": table_row["row_label"],
                        "values": " || ".join(table_row["values"]),
                        "row_text": table_row["row_text"],
                    }
                )

    payload = {
        "dossier_id": "p0_fulltext_high_v1",
        "created_at": "2026-11-13",
        "status": "assisted_catalog_ready_for_human_review",
        "scope": "14 hohe Prioritaeten der menschlich bestaetigten 30er-Shortlist",
        "candidate_table_definition": "Tabelle mit mindestens zwei Arm-Headern und mindestens einer numerischen Datenzeile; keine Bestaetigung, dass es eine Outcome-Tabelle ist.",
        "candidate_row_definition": "Numerische Datenzeile in einer Kandidatentabelle; Rohzitat, keine validierter Outcome-Wert.",
        "risk_flag_definition": "Textsignal in Titel, Abstract oder Methoden; Pruefhinweis, kein Ausschluss.",
        "articles": len(articles),
        "candidate_tables": sum(a["eligibility"]["candidate_tables"] for a in articles),
        "candidate_rows": sum(a["eligibility"]["candidate_rows"] for a in articles),
        "rct_signal_articles": sum(a["eligibility"]["rct_signal_suspected"] for a in articles),
        "two_arm_signal_articles": sum(a["eligibility"]["parallel_two_arm_signal"] for a in articles),
        "articles_with_candidate_tables": sum(bool(a["candidate_tables"]) for a in articles),
        "articles_without_candidate_tables": [
            a["pmcid"] for a in articles if not a["candidate_tables"]
        ],
        "articles_with_arm_sizes": sum(
            bool(a["eligibility"]["arm_sizes_detected"]) for a in articles
        ),
        "risk_articles": sum(bool(a["risk_flags"]) for a in articles),
        "final_decisions_made": False,
        "model_used": False,
        "network_used": False,
        "final_decisions_made": False,
        "source_manifest": str(MANIFEST.relative_to(ROOT)).replace("\\", "/"),
        "records": articles,
    }
    JSON_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    fieldnames = [
        "pmcid",
        "priority",
        "table_label",
        "table_caption",
        "arm_headers",
        "row_index",
        "row_label",
        "values",
        "row_text",
    ]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    lines = [
        "# P0-Volltextdossiers: 14 hohe Prioritäten",
        "",
        "Stand: 2026-11-13",
        "Status: **ASSISTIERTES DOSSIER; MENSCHLICHE VOLLTEXTPRÜFUNG OFFEN**.",
        "",
        "Deterministische JATS-Auslesung, kein Modell, kein Netzabruf. Die",
        "Eignungsmarker sind Suchsignale, keine Entscheidung. Tabellenzeilen",
        "bleiben Rohzitate; keine Werte wurden in die Extraktionsvorlage",
        "übernommen oder geschätzt.",
        "",
        f"- Artikel: **{len(articles)}**",
        f"- Tabellen mit Arm-Headern: **{payload['candidate_tables']}**",
        f"- Kandidatenzeilen: **{payload['candidate_rows']}**",
        f"- Artikel mit Kandidatentabelle: **{payload['articles_with_candidate_tables']}/14**",
        f"- Artikel mit Arm-N in Tabellenheadern: **{payload['articles_with_arm_sizes']}/14**",
        "- Finale Entscheidungen: **0**",
        "",
        "## Übersicht",
        "",
        "| Nr. | PMC | Prio | RCT-Signal | Kandidatentabellen | Zeilen | Risikoflags |",
        "|---:|---|---|---|---:|---:|---|",
    ]
    for article in articles:
        lines.append(
            f"| {article['article_number']} | [{article['pmcid']}](https://pmc.ncbi.nlm.nih.gov/articles/{article['pmcid']}/) | "
            f"{article['priority']} | {'ja' if article['eligibility']['rct_signal_suspected'] else 'prüfen'} | "
            f"{article['eligibility']['candidate_tables']} | {article['eligibility']['candidate_rows']} | "
            f"{', '.join(article['risk_flags']) or '-'} |"
        )

    for article in articles:
        lines += [
            "",
            f"## {article['article_number']}. {article['pmcid']} — {article['title']}",
            "",
            f"- DOI: `{article['doi']}` · Shortlist-Rang {article['shortlist_rank']}",
            f"- XML: `{article['source_xml']}` · SHA-256 `{article['source_sha256']}`",
            f"- Assistierte Eignung: RCT-Signal **{'ja' if article['eligibility']['rct_signal_suspected'] else 'prüfen'}**, "
            f"2-Arm/Placebo-Signal **{'ja' if article['eligibility']['parallel_two_arm_signal'] else 'prüfen'}**, "
            f"Arm-N **{article['eligibility']['arm_sizes_detected']}**, "
            f"Kandidatentabellen **{article['eligibility']['candidate_tables']}**",
            f"- Risikoflags: {', '.join(article['risk_flags']) or '-'}",
            "- Triage: " + (" ".join(article["triage_notes"]) if article["triage_notes"] else "Keine automatischen Warnhinweise; Volltext dennoch manuell prüfen."),
            "- Entscheidung: **offen**; menschliche Prüfung erforderlich.",
            "",
            "### Tabellen",
            "",
            "| Label | Caption | Arm-Header | N | Zeilen |",
            "|---|---|---|---:|---:|",
        ]
        for table in article["tables"]:
            lines.append(
                f"| {table['label'] or '-'} | {table['caption'] or '-'} | "
                f"{' / '.join(table['arm_headers']) or '-'} | {len(table['arm_sizes'])} | {table['data_rows']} |"
            )
        lines += ["", "### Methoden-Snippets", ""]
        for snippet in article["method_snippets"][:6]:
            lines.append(f"- _{snippet['section'] or 'ohne Abschnitt'}_: {snippet['quote']}")
        if not article["method_snippets"]:
            lines.append("- Keine Signaltreffer extrahiert; Methoden manuell prüfen.")

    lines += [
        "",
        "## Nächster Prüfschritt",
        "",
        "1. Pro Artikel die zwei parallelen Arme und die analysierte N bestätigen.",
        "2. Aus den Kandidatenzeilen höchstens vier Outcomes auswählen.",
        "3. N/Mean/SD oder Events/Total mit Tabellen-Label, Zeile und wörtlichem",
        "   Zitat in `fulltext_extraction_template_v1.csv` übertragen.",
        "4. Erst danach `final_decision` setzen; keine Zeile ist automatisch gültig.",
        "",
        "Kein Modelllauf, kein Netzabruf, keine finale Auswahl.",
        "",
    ]
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(
        json.dumps(
            {
                "articles": len(articles),
                "candidate_tables": payload["candidate_tables"],
                "candidate_rows": payload["candidate_rows"],
                "risk_articles": sum(bool(a["risk_flags"]) for a in articles),
                "rct_signal_articles": sum(a["eligibility"]["rct_signal_suspected"] for a in articles),
                "two_arm_signal_articles": sum(a["eligibility"]["parallel_two_arm_signal"] for a in articles),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
