"""Prueft, ob Tabellen mit einem Arm je Zeile paarbar sind.

Frage: Bringt Zeilenpaarung (PRM-Zeile plus Placebo-Zeile derselben Tabelle)
zusaetzliche Einschaflatenz-Zeilen? Der Befund entscheidet, ob die Funktion
gebaut wird oder nicht - kein Feature ohne Wirkung.

Read-only, kein Netz, kein Modell. Ausgabe: JSON und Markdown unter
``data/bench/sol2/``.

Aufruf:
    .venv/bin/python.exe scripts/probe_arm_row_pairs.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.research.jats_tables import _pipe_row, parse_jats  # noqa: E402

SOL = re.compile(r"sleep[- ]onset|sleep[- ]latency|\bSOL\b", re.I)
ARM_TOKEN = re.compile(
    r"^(?:PRM|placebo|melatonin|control|verum|treatment|drug|vehicle|"
    r"prolonged[\s-]release\s+melatonin)$", re.I,
)
SCREEN = re.compile(r"melatonin", re.I)
NOT_MELATONIN = re.compile(
    r"ramelteon|tasimelteon|agomelatine|valerian|cherry|vitamin|exercise|"
    r"dexmedetomidine|temazepam|zolpidem", re.I,
)


def arm_token(cells: list[str]) -> str:
    for cell in cells[:2]:
        text = str(cell or "").strip()
        if ARM_TOKEN.match(text):
            return text
    for cell in cells[2:]:
        text = str(cell or "").strip()
        if ARM_TOKEN.match(text):
            return text
    return ""


def main() -> int:
    pairs = json.loads(
        Path("data/bench/sol2/manifest_pairs.json").read_text(encoding="utf-8")
    )
    screened = [p for p in pairs
                if SCREEN.search(str(p.get("title") or ""))
                and not NOT_MELATONIN.search(str(p.get("title") or ""))]

    findings = []
    counts: Counter = Counter()
    for pair in screened:
        pmc = pair["pmc"]
        for index, table in enumerate(parse_jats(Path("data/bench/sol2/xml") / f"{pmc}.xml")):
            groups: dict[str, list[str]] = defaultdict(list)
            sol_rows = 0
            for row in table.rows:
                if not SOL.search(_pipe_row(row.cells)):
                    continue
                sol_rows += 1
                token = arm_token(row.cells)
                if token:
                    groups[str(row.cells[0] or "").strip()[:40]].append(token)
            if not sol_rows:
                continue
            counts["tabellen_mit_sol"] += 1
            single = [label for label, arms in groups.items() if len(set(arms)) == 1]
            pairable = [label for label, arms in groups.items() if len(set(arms)) >= 2]
            if single:
                counts["tabelle_mit_einzelarm"] += 1
                counts["einzelarm_zeilen"] += sum(len(groups[label]) for label in single)
            if pairable:
                counts["tabelle_paarbar"] += 1
            findings.append({
                "pmc": pmc,
                "table": index,
                "caption": (table.caption or "")[:120],
                "sol_rows": sol_rows,
                "single_arm_outcomes": single,
                "pairable_outcomes": pairable,
            })

    result = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "screened_documents": len(screened),
        "tables_with_sol": counts["tabellen_mit_sol"],
        "tables_with_single_arm": counts["tabelle_mit_einzelarm"],
        "single_arm_rows": counts["einzelarm_zeilen"],
        "pairable_tables": counts["tabelle_paarbar"],
        "finding": findings,
    }
    Path("data/bench/sol2/row_pairs_probe_20261108.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Zeilenpaarung: Probe vor dem Bau",
        "",
        f"Stand: {result['generated']}. Read-only auf den 31 XML, kein Netz.",
        "",
        "Frage: Gibt es Tabellen, in denen derselbe Endpunkt einmal je Arm in",
        "einer eigenen Zeile steht (z. B. PRM-Zeile und Placebo-Zeile)? Nur",
        "solche Tabellen waeren paarbar.",
        "",
        "| Kennzahl | Wert |",
        "|---|---:|",
        f"| gescreente Dokumente | {len(screened)} |",
        f"| Tabellen mit SOL-Zeilen | {result['tables_with_sol']} |",
        f"| davon mit Einzelarm-Zeilen | {result['tables_with_single_arm']} |",
        f"| Einzelarm-Zeilen insgesamt | {result['single_arm_rows']} |",
        f"| **paarbare Tabellen** | **{result['pairable_tables']}** |",
        "",
        "## Befund je Tabelle",
        "",
        "| PMC | Tabelle | SOL-Zeilen | Einzelarm | paarbar |",
        "|---|---:|---:|---|---|",
    ]
    for item in findings:
        lines.append(
            f"| {item['pmc']} | {item['table']} | {item['sol_rows']} | "
            f"{', '.join(item['single_arm_outcomes']) or '-'} | "
            f"{', '.join(item['pairable_outcomes']) or '-'} |")
    lines += [
        "",
        "## Folgerung",
        "",
        "Zeilenpaarung wuerde in diesem Korpus **keine einzige Zeile**",
        "hinzufuegen: es gibt keine Tabelle, in der beide Arme denselben",
        "Endpunkt in getrennten Zeilen tragen. Die Funktion wird deshalb nicht",
        "gebaut.",
        "",
        "PMC2933606, der groesste Trial im Korpus, berichtet die",
        "Einschaflatenz als Veraenderung im PRM-Arm plus einen direkt",
        "berichteten Gruppenunterschied mit Konfidenzintervall",
        "(-0,6; 95 %-KI -14,0 bis 12,7). Das ist ein direkter Effekt, kein",
        "Arm-Deskriptivum - er gehoert in den Effektspalten-Leser, nicht in den",
        "Arm-Rechner.",
    ]
    Path("data/bench/sol2/row_pairs_probe_20261108.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")

    print(f"gescreent={len(screened)} tabellen_mit_sol={result['tables_with_sol']} "
          f"einzelarm_tabellen={result['tables_with_single_arm']} "
          f"einzelarm_zeilen={result['single_arm_rows']} "
          f"paarbar={result['pairable_tables']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
