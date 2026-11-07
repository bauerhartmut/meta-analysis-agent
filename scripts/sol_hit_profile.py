"""Was unterscheidet die Dokumente mit SOL-Effektzeile von den uebrigen?

Offline-Diagnose auf dem vorhandenen Korpus: 946 Dokumente erfuellen das grobe
SOL-RCT-Muster, aber nur 7 liefern eine gespeicherte Einschlaflatenz-Zeile.
Dieses Skript vergleicht Merkmale beider Gruppen und schlaegt daraus eine
engere Suchregel vor - ohne Netz, ohne Modell.

Aufruf:
    .venv/bin/python.exe scripts/sol_hit_profile.py \
        --out data/bench/sol/sol_profil_20261108
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _xml_to_text  # noqa: E402
from research_agent.meta.arm_level import convert_row  # noqa: E402
from research_agent.meta.effect_columns import effects_from_row  # noqa: E402
from research_agent.research.jats_tables import _pipe_row, parse_jats  # noqa: E402

SOL = re.compile(r"sleep[-\s]onset\s+latency|sleep\s+latency|\bSOL\b", re.I)
CI = re.compile(r"95\s*%\s*(?:CI|confidence)|\(\s*95\s*%", re.I)
EFFECT = re.compile(r"hedges\s*g|cohen\s*d|\bSMD\b|mean\s+difference|"
                    r"\bOR\b|\bRR\b|risk\s+ratio|odds\s+ratio", re.I)
PLACEBO = re.compile(r"\bplacebo\b", re.I)
RANDOM = re.compile(r"randomi[sz]ed|randomly\s+assigned", re.I)
CROSSOVER = re.compile(r"cross[-\s]?over", re.I)
SD_CELL = re.compile(r"[±]|\bSD\b|standard\s+deviation", re.I)
SLEEP = re.compile(r"sleep|insomnia|polysomnograph|actigraph", re.I)


def features(path: Path) -> Dict:
    xml = path.read_text(encoding="utf-8", errors="replace")
    text = _xml_to_text(xml)
    tables = parse_jats(path)
    captions = " ".join(f"{t.label} {t.caption}" for t in tables)
    rows = [r for t in tables for r in t.rows]
    sol_rows = 0
    sol_rows_with_ci = 0
    for row in rows:
        joined = " | ".join(row.cells)
        if SOL.search(joined):
            sol_rows += 1
            if CI.search(joined):
                sol_rows_with_ci += 1
    headers = " | ".join(" | ".join(t.header) for t in tables)
    return {
        "sol_mentions": len(SOL.findall(text)),
        "sol_in_caption": int(bool(SOL.search(captions))),
        "sol_rows": sol_rows,
        "sol_rows_with_ci": sol_rows_with_ci,
        "tables": len(tables),
        "rows": len(rows),
        "sd_cells": sum(1 for row in rows if SD_CELL.search(" | ".join(row.cells))),
        "effect_header": int(bool(EFFECT.search(headers))),
        "ci_in_rows": sum(1 for row in rows if CI.search(" | ".join(row.cells))),
        "placebo": len(PLACEBO.findall(text)),
        "randomized": len(RANDOM.findall(text)),
        "crossover": len(CROSSOVER.findall(text)),
        "sleep_mentions": len(SLEEP.findall(text)),
        "chars": len(text),
    }


def sol_row_reasons(path: Path) -> Dict:
    """Was aus einer Tabelle wird, deren Zeile die Einschlaflatenz nennt.

    Genau hier entscheidet sich die Ausbeute: eine SOL-Zeile ohne lesbare
    Effektspalte ist keine Suchluecke, sondern eine Leseluecke.
    """
    from collections import Counter

    reasons: Counter = Counter()
    read = 0
    total = 0
    for table in parse_jats(path):
        caption = " ".join(filter(None, [table.label or "", table.caption or ""]))
        for row in table.rows:
            joined = " | ".join(row.cells)
            if not SOL.search(joined):
                continue
            total += 1
            quote = _pipe_row(row.cells)
            direct, reason = effects_from_row(
                table.header, row.cells, quote=quote, caption=caption,
                row_group=getattr(row, "row_group", ""))
            if direct:
                read += 1
                continue
            arm = convert_row(table.header, row.cells, quote=quote,
                              caption=caption)
            if arm.get("ok"):
                read += 1
                continue
            reasons[str(reason or arm.get("reason") or "unbekannt")] += 1
    return {"sol_tabellenzeilen": total, "lesbar": read, "gruende": dict(reasons)}


def share(values: List[float], threshold: float) -> float:
    return (sum(1 for v in values if v >= threshold) / len(values)) if values else 0.0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="data/bench/sol/manifest_all.json")
    parser.add_argument("--xml-dir", default="data/bench/sol/xml")
    parser.add_argument("--funnel", default="data/bench/sol/funnel_20261108.json")
    parser.add_argument("--cut", default="data/bench/sol/zielmass_schnitt_20261108.json")
    parser.add_argument("--out", default="data/bench/sol/sol_profil_20261108")
    args = parser.parse_args(argv)

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    funnel = json.loads(Path(args.funnel).read_text(encoding="utf-8"))
    cut = json.loads(Path(args.cut).read_text(encoding="utf-8"))
    hit_dois = {str(row.get("source") or "").replace("doi:", "")
                for row in cut.get("sol_rows") or []}
    funnel_by_pmc = {doc["pmc"]: doc for doc in funnel.get("documents") or []}
    xml_dir = Path(args.xml_dir)

    records: List[Dict] = []
    for entry in manifest:
        pmc = str(entry.get("pmc") or "")
        doi = str(entry.get("doi") or "")
        if not pmc or not (xml_dir / f"{pmc}.xml").is_file():
            continue
        doc = funnel_by_pmc.get(pmc) or {}
        if not doc.get("sol_kandidat"):
            continue
        record = features(xml_dir / f"{pmc}.xml")
        record.update(sol_row_reasons(xml_dir / f"{pmc}.xml"))
        record.update({"pmc": pmc, "doi": doi, "hit": doi in hit_dois,
                       "kandidaten": doc.get("kandidaten", 0),
                       "tabellen": doc.get("tabellen", 0)})
        records.append(record)

    hits = [r for r in records if r["hit"]]
    rest = [r for r in records if not r["hit"]]
    keys = [k for k in records[0]
            if k not in ("pmc", "doi", "hit", "gruende")] if records else []

    comparison = []
    for key in keys:
        hv = [float(r[key]) for r in hits]
        rv = [float(r[key]) for r in rest]
        best = {}
        for threshold in (1, 2, 3, 5, 10, 20):
            precision = share(hv, threshold)
            base = share(rv, threshold)
            if precision >= 0.5:
                best = {"threshold": threshold, "recall": precision,
                        "base": base, "lift": (precision / base) if base else None}
                break
        comparison.append({
            "feature": key,
            "hits_median": median(hv) if hv else None,
            "rest_median": median(rv) if rv else None,
            "hits_mean": round(sum(hv) / len(hv), 2) if hv else None,
            "rest_mean": round(sum(rv) / len(rv), 2) if rv else None,
            "rule": best,
        })

    def lifts(item):
        rule = item.get("rule") or {}
        return (rule.get("recall") or 0) * (rule.get("lift") or 0)

    comparison.sort(key=lifts, reverse=True)
    from collections import Counter
    gate_total: Counter = Counter()
    gate_hits: Counter = Counter()
    sol_rows_hits = 0
    sol_rows_rest = 0
    read_hits = 0
    read_rest = 0
    for record in records:
        gate_total.update(record.get("gruende") or {})
        sol_rows_hits += record["sol_tabellenzeilen"] if record["hit"] else 0
        sol_rows_rest += record["sol_tabellenzeilen"] if not record["hit"] else 0
        read_hits += record["lesbar"] if record["hit"] else 0
        read_rest += record["lesbar"] if not record["hit"] else 0
        if record["hit"]:
            gate_hits.update(record.get("gruende") or {})

    report = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "sol_rows_total": sol_rows_hits + sol_rows_rest,
        "sol_rows_hits": sol_rows_hits,
        "sol_rows_rest": sol_rows_rest,
        "sol_rows_read_hits": read_hits,
        "sol_rows_read_rest": read_rest,
        "sol_row_gates_total": dict(gate_total.most_common()),
        "sol_row_gates_hits": dict(gate_hits.most_common()),
        "candidates": len(records),
        "hits": len(hits),
        "hit_dois": sorted(hit_dois),
        "comparison": comparison,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                        encoding="utf-8")

    print(json.dumps({"kandidaten": len(records), "treffer": len(hits),
                      "sol_zeilen": report["sol_rows_total"],
                      "davon_lesbar": read_hits + read_rest,
                      "lesbar_in_treffern": read_hits,
                      "lesbar_im_rest": read_rest}))
    print("Gate der ungelesenen SOL-Zeilen (alle):",
          dict(gate_total.most_common(6)))
    print(f"{'Merkmal':20s} {'Treffer':>8s} {'Rest':>8s} {'Regel':>28s}")
    for item in comparison:
        rule = item.get("rule") or {}
        rule_text = (f">={rule['threshold']}: recall {rule['recall']*100:.0f} %, "
                     f"Basis {rule['base']*100:.0f} %") if rule else "-"
        print(f"{item['feature']:20s} {item['hits_median']:>8} {item['rest_median']:>8} {rule_text:>28s}")
    print(f"JSON: {out.with_suffix('.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
