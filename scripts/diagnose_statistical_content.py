"""XML-Content-Diagnostik fuer die 62 OA-XML-Volltexte (Implementierungsplan T2).

Liest `data/fulltext_inbox/*.xml` READ-ONLY und ueberprueft je Dokument, ob
JATS-Tabellen und statistische Kennzahlen (SE/CI/SD/N/Effektwerte) vorhanden
und in welchem Kontext (Textzelle, Attribut, Fussnote) sie stehen. Der Zweck
ist die Fehlerlokalisierung aus dem Plan, Abschnitt 3.3: welche der Quellen
haetten bereits aus dem XML gepoolt werden koennen, nur hat die Pipeline die
Zeile nicht bis zur SE/CI-Zuordnung gebracht.

Erzeugt:
    data/bench/xml_diagnostics_20261105.json  (maschinenlesbar, alle Felder)
    data/bench/xml_diagnose_20261105.md       (Kurztabelle je Dokument)

Usage:
    python scripts/diagnose_statistical_content.py [--dir data/fulltext_inbox]
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RX = {
    "se": re.compile(r"\b(?:SE|S\.E\.|standard error|Std\.?\s*Err\.?)\b", re.I),
    "sd": re.compile(r"\b(?:SD|S\.D\.|standard deviation|Std\.?\s*Dev\.?)\b", re.I),
    "ci": re.compile(r"\b(?:95?\s*%?\s*CI|confidence interval)\b", re.I),
    "n": re.compile(r"\bN\s*[=]\s*\d+|\b[genderPair]*n\s*=\s*\d+", re.I),
    "effect_metric": re.compile(
        r"\b(?:beta|β|OR\b|RR\b|HR\b|SMD\b|MD\b|IRR\b|log\ Ratio|hazard ratio"
        r"|odds ratio|risk ratio)\b", re.I),
    "plusminus": re.compile(r"[±±]\s*\d"),
    "ci_range": re.compile(r"[\d.]+\s*(?:[-–-]|to)\s*[\d.]"),
    "supp_ref": re.compile(
        r"\b(?:Supplementary|Supplemental|Appendix)\s+(?:Table|Figure|Fig)"
        r"[a-z]*\s*[S]?\.?\s*\d+|Additional file\s*\d", re.I),
}
CI_PAREN = re.compile(
    r"(?:\(|\[)?\s*\d+\.\d+\s*(?:[-–-]|to)\s*\d+\.\d+\s*(?:\)|\])?"
    r"[^0-9]{0,12}(?:CI|interval)?", re.I)


def _tag(el: ET.Element) -> str:
    return el.tag.rsplit("}", 1)[-1]


def _text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return " ".join(el.itertext())


def _front_ids(root: ET.Element) -> dict:
    out = {"doi": "", "pmid": "", "pmcid": ""}
    for meta in root.iter():
        if _tag(meta) not in ("article-meta",):
            continue
        for el in meta.iter():
            tag = _tag(el)
            if tag == "article-id":
                kind = el.get("pub-id-type", "")
                if kind in out:
                    out[kind] = (out[kind] or _text(el))
            elif tag == "article-title":
                out.setdefault("title", _text(el))
    return out


def _classify_row(cells: list[str]) -> dict:
    """Eine Tabellenzeile als statistische Kandidatenzeile lesen."""
    joined = " | ".join(cells)
    out = {
        "cells": len(cells),
        "has_effect_metric": bool(RX["effect_metric"].search(joined)),
        "has_ci": bool(RX["ci"].search(joined)) or bool(CI_PAREN.search(joined)),
        "has_se": bool(RX["se"].search(joined)),
        "has_sd": bool(RX["sd"].search(joined)) or bool(RX["plusminus"].search(joined)),
        "has_n": bool(RX["n"].search(joined)),
        "numbers": sum(bool(re.search(r"[-–-]?\d+\.\d+", c)) for c in cells),
    }
    out["stat_rich"] = out["has_ci"] or out["has_se"] or (
        out["has_sd"] and out["has_n"] and out["numbers"] >= 2)
    return out


def _diag_one(path: Path) -> dict:
    doc = {
        "document_id": path.name,
        "doi": "", "pmid": "", "pmcid": "",
        "available_assets": [],
        "parser_warnings": [],
        "table_count": 0,
        "tables": [],
        "has_xml_tables": False,
        "supplement_refs": 0,
        "supplement_elements": 0,
        "statistical_token_counts": {},
        "candidate_effect_rows": 0,
        "candidate_se_rows": 0,
        "candidate_ci_rows": 0,
        "candidate_sd_rows": 0,
        "candidate_n_rows": 0,
        "candidate_poolable_rows": 0,
        "token_plusminus": 0,
    }
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, ValueError) as e:
        doc["parser_warnings"].append(f"parse error: {e}")
        return doc

    ids = _front_ids(root)
    doc.update({k: ids.get(k, "") for k in ("doi", "pmid", "pmcid")})
    doc["title"] = (ids.get("title") or "")[:120]

    # Assets: ggf. gerenderter Volltext in data/fulltext/
    stem = path.stem
    txt = ROOT / "data" / "fulltext" / f"{stem}.txt"
    if txt.exists():
        doc["available_assets"].append("rendered_fulltext")
    for suf in (".ai.pdf", ".pdf"):
        pdf = ROOT / "data" / "origpdf" / f"{stem}{suf}"
        if pdf.exists():
            doc["available_assets"].append(f"origpdf({suf})")

    # Tabellen
    wraps = list(root.iter()) and [el for el in root.iter() if _tag(el) == "table-wrap"]
    doc["table_count"] = len(wraps)
    doc["has_xml_tables"] = doc["table_count"] > 0
    for tw in wraps:
        tinfo = {"label": "", "rows": 0, "stat_rich_rows": 0,
                 "caption_stats": {}}
        for child in tw:
            tag = _tag(child)
            if tag in ("label", "caption"):
                text = _text(child)
                if tag == "label":
                    tinfo["label"] = text.strip()
                for name, rx in RX.items():
                    tinfo["caption_stats"][name] = bool(rx.search(text))
            if tag == "table":
                for tr in child.iter():
                    if _tag(tr) != "tr":
                        continue
                    cells = [_text(td) for td in tr
                             if _tag(td) in ("td", "th")]
                    if not cells:
                        continue
                    tinfo["rows"] += 1
                    row = _classify_row(cells)
                    if row["stat_rich"]:
                        tinfo["stat_rich_rows"] += 1
                        doc["candidate_poolable_rows"] += 1
                    if row["has_effect_metric"] and row["numbers"]:
                        doc["candidate_effect_rows"] += 1
                    if row["has_se"]:
                        doc["candidate_se_rows"] += 1
                    if row["has_ci"]:
                        doc["candidate_ci_rows"] += 1
                    if row["has_sd"]:
                        doc["candidate_sd_rows"] += 1
                    if row["has_n"]:
                        doc["candidate_n_rows"] += 1
                if tinfo["rows"] == 0:
                    doc["parser_warnings"].append(
                        f"table-wrap ohne fuellbare Zeilen: {tinfo['label'][:60]}")
        doc["tables"].append(tinfo)

    # Fließtext-Agilis
    body_text = _text(root)
    doc["statistical_token_counts"] = {
        name: len(rx.findall(body_text)) for name, rx in RX.items()
        if name not in ("plusminus",)
    }
    for el in root.iter():
        if _tag(el) == "supplementary-material":
            doc["supplement_elements"] += 1
    doc["supplement_refs"] = doc["supplement_elements"] + len(
        RX["supp_ref"].findall(body_text))

    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=str(ROOT / "data" / "fulltext_inbox"))
    args = ap.parse_args()

    files = sorted(glob.glob(str(Path(args.dir) / "*.xml")))
    now = datetime.now(timezone.utc).isoformat()
    docs = [_diag_one(Path(p)) for p in files]

    agg = {
        "generated": now,
        "n_documents": len(docs),
        "with_tables": sum(d["has_xml_tables"] for d in docs),
        "with_supplement_refs": sum(d["supplement_refs"] > 0 for d in docs),
        "with_stat_rich_table_rows": sum(d["candidate_poolable_rows"] > 0 for d in docs),
        "total_tables": sum(d["table_count"] for d in docs),
        "total_candidate_poolable_rows": sum(d["candidate_poolable_rows"] for d in docs),
        "docs_with_se_evidence": sum(
            (d["candidate_se_rows"] > 0 or d["statistical_token_counts"].get("se", 0) > 0)
            for d in docs),
        "docs_with_ci_evidence": sum(
            (d["candidate_ci_rows"] > 0 or d["statistical_token_counts"].get("ci", 0) > 0)
            for d in docs),
    }

    out_json = ROOT / "data" / "bench" / "xml_diagnostics_20261105.json"
    out_md = ROOT / "data" / "bench" / "xml_diagnose_20261105.md"
    out_json.write_text(json.dumps(
        {"aggregate": agg, "documents": docs}, indent=2, ensure_ascii=False),
        encoding="utf-8")

    lines = [
        "# XML-Diagnose der 62 OA-Volltexte (read-only)",
        "",
        f"Stand: {now} · generiert mit scripts/diagnose_statistical_content.py",
        "",
        "| Dokument | Tabellen | SE-Zeilen | CI-Zeilen | stat-reiche Zeilen | Supplemente |",
        "|---|---|---|---|---|---|",
    ]
    for d in docs:
        lines.append(
            f"| {d['document_id'][:64]} | {d['table_count']} | "
            f"{d['candidate_se_rows']} | {d['candidate_ci_rows']} | "
            f"{d['candidate_poolable_rows']} | {d['supplement_refs']} |")
    lines += ["", "## Aggregate", "", f"- {agg}"]
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(agg, indent=2, ensure_ascii=False))
    print("JSON:", out_json)
    print("MD : ", out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
