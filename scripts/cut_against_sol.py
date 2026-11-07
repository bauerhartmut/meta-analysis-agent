"""Die gespeicherten Effektzeilen gegen das Zielmass Einschlaflatenz schneiden.

Frage nach Paket C: Die Konverter speichern jetzt 1.099 Zeilen statt 523 - wie
viele davon betreffen ueberhaupt die Einschlaflatenz (SOL), das Zielmass der
Untersuchung, und wie viele sind poolbar?

Kein Modell, kein Netz: geschnitten wird auf dem normalisierten Outcome-Namen
(``research_agent/meta/outcome_labels.py``). Ein Zielmass-Objekt aus
``meta/targets.py`` braucht einen LLM-Aufruf; hier ist die Frage bekannt, also
wird sie woertlich als Kriterium verwendet und nicht geraten.

Aufruf:
    .venv/bin/python.exe scripts/cut_against_sol.py \
        --out data/bench/sol/zielmass_schnitt_20261108
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.database import Database  # noqa: E402
from research_agent.meta.designs import is_primary_study  # noqa: E402
from research_agent.meta.outcome_labels import normalize_outcome  # noqa: E402

DEFAULT_DBS = {
    "effektspalten": "data/bench/sol/direct_kopf.db",
    "arm_tabelle": "data/bench/sol/arm_kopf.db",
    "fliesstext": "data/bench/sol/text_arms.db",
    "veraenderung": "data/bench/sol/change_arms.db",
}

POOLABLE_TYPES = frozenset({"g", "smd", "d", "hedges_g", "mean_diff"})

# Ein Label, das nur aus einem Code besteht ("T2", "Model 1", "M3"), benennt
# kein Outcome. Solche Zeilen zaehlen als "ohne brauchbares Label", nicht als
# "daneben" - sonst sieht der Schnitt besser aus, als er ist.
_CODE_LABEL = re.compile(r"^(?:[a-z]{0,3}\s?\d+|model\s?\d+|m\d+|t\d+)$", re.I)

_SLEEP = re.compile(r"sleep|insomnia|psqi|ess\b|isi\b|waso|tst\b|rem\b|"
                    r"arousal|actigraph|dlmo|melatonin", re.I)


def classify(row: Dict) -> str:
    """sol, schlaf, anderes, ohne_label oder leer."""
    raw = str(row.get("outcome") or "").strip()
    norm = normalize_outcome(raw)
    if not norm:
        return "leer"
    if _CODE_LABEL.match(norm) or _CODE_LABEL.match(raw):
        return "ohne_label"
    if "sleep onset latency" in norm:
        return "sol"
    if _SLEEP.search(norm):
        return "schlaf"
    return "anderes"


def poolable(row: Dict) -> bool:
    if int(row.get("disputed") or 0) == 1:
        return False
    if str(row.get("rejection_reason") or "").strip():
        return False
    if str(row.get("effect_type") or "").strip().lower() not in POOLABLE_TYPES:
        return False
    if row.get("se") is None and not (row.get("ci_low") is not None
                                      and row.get("ci_high") is not None):
        return False
    return is_primary_study(row)


def cut(dbs: Dict[str, str]) -> Dict:
    per_db: Dict[str, Dict] = {}
    totals: Counter = Counter()
    sol_rows: List[Dict] = []
    for name, path in dbs.items():
        if not path or not Path(path).is_file():
            per_db[name] = {"error": "DB fehlt", "rows": 0}
            continue
        rows = Database(str(path)).get_study_effects() or []
        counts: Counter = Counter()
        pool: Counter = Counter()
        for row in rows:
            klass = classify(row)
            counts[klass] += 1
            if poolable(row):
                pool[klass] += 1
            if klass == "sol":
                sol_rows.append({
                    "db": name,
                    "source": str(row.get("source_id") or ""),
                    "outcome": row.get("outcome"),
                    "outcome_key": row.get("outcome_key"),
                    "effect_type": row.get("effect_type"),
                    "effect": row.get("effect"),
                    "poolable": poolable(row),
                })
        per_db[name] = {
            "rows": len(rows),
            "classes": dict(counts),
            "poolable": dict(pool),
            "poolable_rows": sum(pool.values()),
        }
        totals.update(counts)

    total_rows = sum(v.get("rows", 0) for v in per_db.values())
    return {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "question": "Zielmass Einschlaflatenz (sleep onset latency)",
        "dbs": per_db,
        "totals": {
            "rows": total_rows,
            "classes": dict(totals),
            "sol_share": (totals["sol"] / total_rows) if total_rows else None,
        },
        "sol_rows": sol_rows,
    }


def write_markdown(report: Dict, path: Path) -> None:
    totals = report["totals"]
    classes = totals["classes"]
    lines = [
        "# Zielmass-Schnitt der gespeicherten Zeilen (2026-11-08)",
        "",
        "Frage: Wie viele der gespeicherten Effektzeilen betreffen die",
        "Einschlaflatenz, das Zielmass der Untersuchung?",
        "",
        "Deterministisch auf dem normalisierten Outcome-Namen; kein Modell,",
        "kein Netz. Label-Codes wie \"T2\" oder \"Model 1\" zaehlen als",
        "\"ohne Label\", nicht als \"daneben\".",
        "",
        "## Gesamt",
        "",
        "| Klasse | Zeilen | Anteil |",
        "|---|---:|---:|",
    ]
    share = totals["sol_share"]
    for klass in ("sol", "schlaf", "anderes", "ohne_label", "leer"):
        count = classes.get(klass, 0)
        pct = f"{count / totals['rows'] * 100:.1f} %" if totals["rows"] else "-"
        lines.append(f"| {klass} | {count} | {pct} |")
    lines += [f"| **Summe** | **{totals['rows']}** | |", ""]
    if share is not None:
        lines += [f"Zielmass-Anteil: {share * 100:.1f} %.", ""]

    lines += [
        "## Je Leser",
        "",
        "| Leser | Zeilen | SOL | Schlaf | anderes | ohne Label | leer | poolbar | poolbar SOL |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, stats in report["dbs"].items():
        if stats.get("error"):
            lines.append(f"| {name} | 0 | - | - | - | - | - | - | - |")
            continue
        c = stats["classes"]
        p = stats["poolable"]
        lines.append(
            f"| {name} | {stats['rows']} | {c.get('sol', 0)} | {c.get('schlaf', 0)} | "
            f"{c.get('anderes', 0)} | {c.get('ohne_label', 0)} | {c.get('leer', 0)} | "
            f"{stats['poolable_rows']} | {p.get('sol', 0)} |")

    lines += ["", "## Die SOL-Zeilen im Einzelnen", ""]
    if report["sol_rows"]:
        sources = sorted({row.get("source") for row in report["sol_rows"]
                          if row.get("source")})
        poolable_sol = sum(1 for row in report["sol_rows"] if row["poolable"])
        lines += [
            f"{len(report['sol_rows'])} Zeilen aus {len(sources)} Quellen, "
            f"davon {poolable_sol} poolbar.",
            "",
            "| Leser | Quelle | Outcome | Typ | Effekt | poolbar |",
            "|---|---|---|---|---:|---:|",
        ]
        for row in report["sol_rows"]:
            lines.append(
                f"| {row['db']} | {row.get('source') or '-'} | "
                f"{str(row['outcome'])[:52]} | {row['effect_type']} | "
                f"{row['effect']} | {'ja' if row['poolable'] else 'nein'} |")
    else:
        lines.append("Keine Zeile liegt auf dem Zielmass.")
    lines += [
        "",
        "## Grenzen",
        "",
        "- Der Schnitt prueft den Outcome-Namen, nicht den studierten",
        "  Zusammenhang. Eine Zeile kann Einschlaflatenz messen und trotzdem",
        "  eine andere Intervention betreffen; das entscheidet die Populations-",
        "  und Interventionsspalte, nicht dieses Skript.",
        "- Der Anteil ist eine Untergrenze: Labels, die das Zielmass umschreiben",
        "  (\"latency to persistent sleep\"), werden nicht erkannt und landen",
        "  unter \"anderes\". Die Synonymtabelle ist bewusst kurz und belegt.",
        "",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default="data/bench/sol/zielmass_schnitt_20261108")
    parser.add_argument("--direct-db", default=DEFAULT_DBS["effektspalten"])
    parser.add_argument("--arm-db", default=DEFAULT_DBS["arm_tabelle"])
    parser.add_argument("--text-db", default=DEFAULT_DBS["fliesstext"])
    parser.add_argument("--change-db", default=DEFAULT_DBS["veraenderung"])
    args = parser.parse_args(argv)

    report = cut({
        "effektspalten": args.direct_db,
        "arm_tabelle": args.arm_db,
        "fliesstext": args.text_db,
        "veraenderung": args.change_db,
    })
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, out.with_suffix(".md"))

    print(json.dumps(report["totals"], ensure_ascii=False))
    for name, stats in report["dbs"].items():
        if stats.get("error"):
            print(f"  {name}: DB fehlt")
            continue
        print(f"  {name}: {stats['rows']} Zeilen, {stats['classes']}, "
              f"poolbar {stats['poolable']}")
    print(f"SOL-Zeilen: {len(report['sol_rows'])}")
    print(f"JSON: {out.with_suffix('.json')}")
    print(f"MD:   {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
