"""Messen, ob ein Gate Baseline-Tabellen und SE-Spalten erkennt.

Vorgeschichte: In der Q1-Stichprobe wurde eine Zeile als Hedges g gespeichert,
die aus Tabelle 1 ("Baseline demographics summary of study participants") mit
der Kopfzeile "Placebo (n = 35), mean +- SE" stammte. Beide Merkmale - die
Ausgangslagentabelle und die Standardfehler-Spalte - hat das heutige Gate
durchgelassen.

Bevor das Zielmass auf "sleep latency" erweitert wird, muss klar sein, wie oft
das passiert. Dieses Skript misst an den bereits gespeicherten Zeilen:

* wie viele Zeilen aus einer Tabelle mit Baseline-Caption stammen,
* wie viele aus einer Spalte mit SE/SEM statt SD stammen,
* ob die Spaltenrollen-Erkennung (``_col_semantics``) die SE-Spalte als solche
  sieht,
* wie viele SOL-Zeilen davon betroffen waeren (Kosten eines Gates),
* wie haeufig Baseline-Tabellen im Korpus ueberhaupt vorkommen.

Read-only, kein Modell, kein Netz. Aufruf:

    .venv/bin/python.exe scripts/measure_baseline_gate.py \
        --xml-dir data/bench/sol/xml_q1 \
        --manifest data/bench/sol/q1_stichprobe_gelesen_20261108.json \
        --db effektspalten=data/bench/sol/direct_q1.db \
        --db arm_tabelle=data/bench/sol/arm_q1.db \
        --out data/bench/sol/baseline_gate_q1_20261108
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from research_agent.database import Database  # noqa: E402
from research_agent.research.jats_tables import _col_semantics, _pipe_row, parse_jats  # noqa: E402
from cut_against_sol import classify  # noqa: E402

# Caption-Muster fuer Ausgangslagentabellen. "Table 1" allein reicht nicht -
# viele Studien berichten dort auch Ergebnisse; entscheidend ist das Wort.
BASELINE_CAPTION = re.compile(
    r"baseline|demograf|characteristic|study\s+population|study\s+participants"
    r"|at\s+inclusion|pre[-\s]?treatment|ausgangs", re.I)

# Eine Spalte, die Streuung als Standardfehler ausweist.
SE_HEADER = re.compile(r"\bSEM\b|\bSE\b|standard\s+error|standardfehler", re.I)
SD_HEADER = re.compile(r"\bSD\b|standard\s+deviation|standardabweichung", re.I)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


class Document:
    """Geparste Tabellen eines Dokuments, einmal je PMCID."""

    def __init__(self, path: Path):
        self.path = path
        self.tables = list(parse_jats(path))
        self._index: Dict[str, Tuple[int, int]] = {}
        for t_index, table in enumerate(self.tables):
            for r_index, row in enumerate(table.rows):
                self._index.setdefault(_norm(_pipe_row(row.cells)), (t_index, r_index))

    def find(self, quote: str) -> Optional[Tuple[object, object]]:
        """Tabelle und Zeile zum gespeicherten Zitat (exakt, sonst enthalten)."""
        key = _norm(quote)
        if not key:
            return None
        hit = self._index.get(key)
        if hit:
            t_index, r_index = hit
            return self.tables[t_index], self.tables[t_index].rows[r_index]
        for stored, (t_index, r_index) in self._index.items():
            if stored and (stored in key or key in stored):
                return self.tables[t_index], self.tables[t_index].rows[r_index]
        return None


def _tables_overview(docs: Dict[str, Document]) -> dict:
    """Wie haeufig Baseline-Tabellen und SE-Spalten im Korpus sind."""
    tables = baseline_tables = se_tables = rows = baseline_rows = se_rows = 0
    for doc in docs.values():
        for table in doc.tables:
            caption = f"{table.label or ''} {table.caption or ''}"
            is_baseline = bool(BASELINE_CAPTION.search(caption))
            header_text = _norm(" | ".join(str(h) for h in table.header or []))
            has_se = bool(SE_HEADER.search(header_text)) and not SD_HEADER.search(header_text)
            tables += 1
            baseline_tables += int(is_baseline)
            se_tables += int(has_se)
            rows += len(table.rows)
            baseline_rows += len(table.rows) if is_baseline else 0
            se_rows += len(table.rows) if has_se else 0
    return {"tabellen": tables, "baseline_tabellen": baseline_tables,
            "se_tabellen": se_tables, "zeilen": rows,
            "zeilen_in_baseline": baseline_rows, "zeilen_in_se": se_rows}


def measure(dbs: Dict[str, str], xml_dir: Path, manifest: Path) -> dict:
    pmc_by_doi = {}
    if manifest.exists():
        for entry in json.loads(manifest.read_text(encoding="utf-8")):
            doi = str(entry.get("doi") or "").lower()
            pmc = str(entry.get("pmc") or "")
            if doi and pmc:
                pmc_by_doi[doi] = pmc

    docs: Dict[str, Document] = {}
    for pmc in dict.fromkeys(pmc_by_doi.values()):
        path = xml_dir / f"{pmc}.xml"
        if path.exists():
            docs[pmc] = Document(path)

    per_db: Dict[str, dict] = {}
    examples: List[dict] = []
    sol_flagged = 0
    sol_total = 0
    for name, path in dbs.items():
        if not path or not Path(path).is_file():
            per_db[name] = {"error": "DB fehlt"}
            continue
        rows = Database(path).get_study_effects() or []
        counts: Counter = Counter()
        for row in rows:
            source = str(row.get("source_id") or "")
            doi = source.split(":", 1)[1].lower() if ":" in source else ""
            pmc = pmc_by_doi.get(doi, "")
            doc = docs.get(pmc)
            found = doc.find(str(row.get("quote") or "")) if doc else None
            counts["zeilen"] += 1
            if not found:
                counts["ohne_tabellenzuordnung"] += 1
                continue
            table, _table_row = found
            caption = _norm(f"{table.label or ''} {table.caption or ''}")
            header = _norm(" | ".join(str(h) for h in table.header or []))
            baseline = bool(BASELINE_CAPTION.search(caption))
            se_word = bool(SE_HEADER.search(header)) and not SD_HEADER.search(header)
            roles = _col_semantics(list(table.header or []))
            se_role = any(role == "se" for role in roles.values())
            counts["zugeordnet"] += 1
            counts["baseline_caption"] += int(baseline)
            counts["se_im_kopf"] += int(se_word)
            counts["se_rolle_erkannt"] += int(se_role)
            counts["baseline_oder_se"] += int(baseline or se_word)
            if classify(row) == "sol":
                sol_total += 1
                if baseline or se_word:
                    sol_flagged += 1
            if (baseline or se_word) and len(examples) < 10:
                examples.append({
                    "db": name, "source": source, "outcome": row.get("outcome"),
                    "effect_type": row.get("effect_type"), "effect": row.get("effect"),
                    "baseline_caption": baseline, "se_im_kopf": se_word,
                    "se_rolle_erkannt": se_role,
                    "caption": caption[:120], "header": header[:160],
                })
        per_db[name] = dict(counts)

    totals: Counter = Counter()
    for stats in per_db.values():
        totals.update({k: v for k, v in stats.items()
                       if isinstance(v, int) and k != "error"})
    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "xml_dir": str(xml_dir),
        "documents": len(docs),
        "tables": _tables_overview(docs),
        "dbs": per_db,
        "totals": dict(totals),
        "sol_rows": sol_total,
        "sol_flagged": sol_flagged,
        "examples": examples,
    }


def write_markdown(report: dict, path: Path) -> None:
    tables = report["tables"]
    lines = [
        "# Baseline- und SE-Gate: Messung an gespeicherten Zeilen",
        "",
        f"Stand: {report['generated']}. Read-only; kein Modell, kein Netz.",
        "",
        f"Dokumente: {report['documents']} | Tabellen: {tables['tabellen']} | "
        f"Zeilen: {tables['zeilen']}",
        "",
        "## Wie oft gibt es solche Tabellen ueberhaupt?",
        "",
        "| Merkmal | Tabellen | Zeilen |",
        "|---|---:|---:|",
        f"| Baseline-Caption | {tables['baseline_tabellen']} | {tables['zeilen_in_baseline']} |",
        f"| SE-Kopf ohne SD | {tables['se_tabellen']} | {tables['zeilen_in_se']} |",
        f"| alle | {tables['tabellen']} | {tables['zeilen']} |",
        "",
        "## Was das heutige Gate durchlaesst",
        "",
        "| Leser | Zeilen | zugeordnet | Baseline-Caption | SE im Kopf | "
        "SE-Rolle erkannt | Baseline oder SE |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, stats in report["dbs"].items():
        if stats.get("error"):
            lines.append(f"| {name} | - | - | - | - | - | - |")
            continue
        lines.append(
            f"| {name} | {stats.get('zeilen', 0)} | {stats.get('zugeordnet', 0)} | "
            f"{stats.get('baseline_caption', 0)} | {stats.get('se_im_kopf', 0)} | "
            f"{stats.get('se_rolle_erkannt', 0)} | {stats.get('baseline_oder_se', 0)} |")
    totals = report["totals"]
    lines += [
        "",
        f"Summe: {totals.get('zeilen', 0)} Zeilen, davon "
        f"{totals.get('baseline_oder_se', 0)} aus einer Baseline-Tabelle oder "
        f"einer SE-Spalte. SOL-Zeilen betroffen: {report['sol_flagged']} von "
        f"{report['sol_rows']}.",
        "",
        "## Beispiele",
        "",
    ]
    if report["examples"]:
        for row in report["examples"]:
            lines += [
                f"* `{row['source']}` - {str(row['outcome'])[:50]} "
                f"({row['effect_type']} {row['effect']})",
                f"  - Caption: {row['caption'] or '-'}",
                f"  - Kopf: {row['header'] or '-'}",
                f"  - Baseline: {'ja' if row['baseline_caption'] else 'nein'}, "
                f"SE im Kopf: {'ja' if row['se_im_kopf'] else 'nein'}, "
                f"SE-Rolle erkannt: {'ja' if row['se_rolle_erkannt'] else 'nein'}",
            ]
    else:
        lines.append("Keine Zeile aus einer Baseline-Tabelle oder SE-Spalte.")
    lines += [
        "",
        "## Grenzen",
        "",
        "- Die Zuordnung Zeile -> Tabelle laeuft ueber das gespeicherte Zitat.",
        "  Zeilen ohne eindeutige Zuordnung werden als solche gezaehlt und nicht",
        "  bewertet; sie koennen die Quote unterschaetzen.",
        "- Das Caption-Muster erkennt Ausgangslagentabellen nur am Wortlaut.",
        "  Tabellen ohne \"baseline\" in der Caption, die trotzdem Ausgangswerte",
        "  zeigen, bleiben unentdeckt - die Messung ist eine Untergrenze.",
        "- Gemessen wird, was das Gate heute durchlaesst, nicht was ein neues",
        "  Gate leisten koennte.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml-dir", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--db", action="append", default=[],
                        help="name=pfad, mehrfach")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    dbs = {}
    for item in args.db:
        name, _, path = item.partition("=")
        dbs[name] = path

    report = measure(dbs, Path(args.xml_dir), Path(args.manifest))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    write_markdown(report, out.with_suffix(".md"))
    print(json.dumps({"documents": report["documents"],
                      "tables": report["tables"],
                      "totals": report["totals"],
                      "sol_flagged": report["sol_flagged"],
                      "sol_rows": report["sol_rows"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
