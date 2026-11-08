"""Direkt berichtete Effektspalten im Q2-Korpus lesen (offline).

Zweiter Weg neben dem Arm-Rechner: Tabellen, die den Effekt schon fertig
nennen ("Difference (95% CI)", "MD", "SMD", "Hedges g"). Deterministisch,
kein Modell, kein Netz. Gespeichert wird nur mit belegtem Zitat und
ableitbarem Standardfehler.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _xml_to_text  # noqa: E402
from research_agent.database import Database  # noqa: E402
from research_agent.meta.effect_columns import (  # noqa: E402
    effects_from_row,
    store_direct_effects,
)
from research_agent.meta.outcome_labels import normalize_outcome  # noqa: E402
from research_agent.research.jats_tables import _pipe_row, parse_jats  # noqa: E402

SCREEN = re.compile(r"melatonin", re.I)
NOT_MELATONIN = re.compile(
    r"ramelteon|tasimelteon|agomelatine|valerian|cherry|vitamin|exercise|"
    r"dexmedetomidine|temazepam|zolpidem", re.I)
POOLABLE = {"g", "smd", "mean_diff"}


def is_sol(label: str) -> bool:
    text = normalize_outcome(label) or ""
    if "sleep onset latency" in text:
        return True
    return bool(re.search(r"\bsol\b", text))


def main() -> int:
    pairs = json.loads(Path("data/bench/sol2/manifest_pairs.json").read_text(encoding="utf-8"))
    screened = [p for p in pairs
                if SCREEN.search(str(p.get("title") or ""))
                and not NOT_MELATONIN.search(str(p.get("title") or ""))]
    db_path = Path("data/bench/sol2/direct.db")
    if db_path.exists():
        db_path.unlink()
    db = Database(str(db_path))

    documents, reasons = [], Counter()
    for pair in screened:
        pmc = pair["pmc"]
        xml = (Path("data/bench/sol2/xml") / f"{pmc}.xml").read_text(encoding="utf-8", errors="replace")
        text = _xml_to_text(xml)
        source_id = f"doi:{pair['doi']}"
        row = db.save_source_text(source_id, text, kind="xml",
                                  origin_url=f"https://www.ncbi.nlm.nih.gov/pmc/{pmc}/")
        text_id = (row or {}).get("id", "")
        candidates = []
        for table in parse_jats(Path("data/bench/sol2/xml") / f"{pmc}.xml"):
            caption = f"{table.label or ''} {table.caption or ''}".strip()
            for table_row in table.rows:
                quote = _pipe_row(table_row.cells)
                found, reason = effects_from_row(table.header, table_row.cells, quote,
                                                 caption=caption,
                                                 row_group=table_row.row_group)
                if found:
                    candidates.extend(found)
                else:
                    reasons[reason[:70]] += 1
        stored, rejected = store_direct_effects(db, source_id, text_id, text, candidates)
        for entry in rejected:
            reasons[str(entry.get("reason"))[:70]] += 1
        sol_rows = [r for r in stored if is_sol(str(r.get("outcome") or ""))]
        documents.append({
            "pmc": pmc, "doi": pair["doi"], "year": pair.get("year"),
            "stored": len(stored), "sol": len(sol_rows),
            "sol_poolable": sum(1 for r in sol_rows if r.get("effect_type") in POOLABLE),
            "types": dict(Counter(str(r.get("effect_type")) for r in stored)),
            "sol_rows": [{"outcome": r.get("outcome"), "type": r.get("effect_type"),
                          "effect": r.get("effect"), "ci": [r.get("ci_low"), r.get("ci_high")],
                          "quote": str(r.get("quote") or "")[:150]} for r in sol_rows],
        })

    mit_sol = [d for d in documents if d["sol_poolable"]]
    report = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "screened": len(screened),
        "stored_total": sum(d["stored"] for d in documents),
        "sol_rows_total": sum(d["sol"] for d in documents),
        "k_sol_poolable": len(mit_sol),
        "reasons": dict(reasons.most_common(15)),
        "documents": documents,
    }
    Path("data/bench/sol2/direct.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Direkte Effektspalten im Q2-Korpus", "",
        f"Stand: {report['generated']}. Deterministisch, kein Netz, kein Modell.", "",
        "| Kennzahl | Wert |", "|---|---:|",
        f"| gescreente Dokumente | {report['screened']} |",
        f"| gespeicherte Effektzeilen | {report['stored_total']} |",
        f"| davon SOL-Zeilen | {report['sol_rows_total']} |",
        f"| **Dokumente mit poolbarer SOL-Zeile (k)** | **{report['k_sol_poolable']}** |",
        "", "## SOL-Zeilen", "",
        "| PMC | Outcome | Typ | Effekt | 95 %-KI |", "|---|---|---|---:|---|",
    ]
    for doc in documents:
        for row in doc["sol_rows"]:
            lines.append(f"| {doc['pmc']} | {str(row['outcome'])[:40]} | {row['type']} | "
                         f"{row['effect']} | {row['ci'][0]} bis {row['ci'][1]} |")
    lines += ["", "## Ablehnungsgruende", ""]
    for reason, count in reasons.most_common(10):
        lines.append(f"- {count:5d}  {reason}")
    Path("data/bench/sol2/direct.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"gescreent={report['screened']} zeilen={report['stored_total']} "
          f"sol={report['sol_rows_total']} k={report['k_sol_poolable']}")
    for doc in mit_sol:
        print(f"  {doc['pmc']}: {doc['sol_poolable']} poolbare SOL-Zeile(n)")
    for reason, count in reasons.most_common(6):
        print(f"  {count:5d}  {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
