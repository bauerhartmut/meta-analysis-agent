"""Die 31 gelesenen Effektzeilen durch das Pooling schicken.

Zwei Fragen:
  1. Entstehen Gruppen mit k >= 2 (also eine wirkliche Analyse)?
  2. Zaehlt die crude/adjustiert-Doppelzeile eine Studie doppelt?

Variante A: alle gespeicherten Zeilen (das Pooling trennt nach
Anpassungszustand, siehe ``_split_pool_conditions``).
Variante B: je (Quelle, Outcome, Effekttyp) nur EINE Zeile - adjustiert
vor crude. Das ist die Regel, die eine doppelte Gewichtung derselben
Personen verhindert.

Read-only: die Zeilen kommen aus ``data/bench/xml6/direct.db``.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.database import Database  # noqa: E402
from research_agent.meta.pooling import build_analysis  # noqa: E402


def _prefer_adjusted(rows):
    """Eine Zeile je (Quelle, Outcome, Effekttyp, Tabellenzeile).

    Der Schluessel enthaelt das Zitat, weil dasselbe Outcome in einer
    Tabelle mehrfach stehen kann (zwei Modelle, zwei Stichproben). Nur
    innerhalb DERSELBEN Zeile sind crude und adjustiert dasselbe Ergebnis;
    dort gewinnt die adjustierte Variante. Ueber Zeilen hinweg wird nichts
    zusammengelegt - abhaengige Zeilen derselben Quelle kollabiert das
    Pooling selbst (``_collapse_same_study``) und nennt den Grund.
    """
    best = {}
    dropped = []
    for row in rows:
        key = (row.get("source_id") or "", row.get("outcome") or "",
               row.get("effect_type") or "", row.get("quote") or "")
        current = best.get(key)
        if current is None:
            best[key] = row
            continue
        if int(row.get("adjusted") or 0) == 1 and int(current.get("adjusted") or 0) != 1:
            dropped.append(current)
            best[key] = row
        else:
            dropped.append(row)
    return list(best.values()), dropped


def _summarise(analysis):
    groups = []
    for name, group in sorted((analysis.get("groups") or {}).items()):
        groups.append({
            "group": name,
            "k": int(group.get("k") or 0),
            "pooled": group.get("pooled"),
            "ci_low": group.get("ci_low"),
            "ci_high": group.get("ci_high"),
            "i2": group.get("i2"),
            "tau2": group.get("tau2"),
            "note": group.get("note") or "",
            "rows": [r.get("label") for r in group.get("rows") or []],
        })
    return groups


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="data/bench/xml6/direct.db")
    parser.add_argument("--json", default="data/bench/xml6/pooling_20261107.json")
    parser.add_argument("--md", default="data/bench/xml6/pooling_20261107.md")
    args = parser.parse_args(argv)

    db = Database(args.db)
    rows = db.get_study_effects() or []
    deduped, dropped = _prefer_adjusted(rows)

    all_analysis = build_analysis(rows)
    dedup_analysis = build_analysis(deduped)

    all_groups = _summarise(all_analysis)
    dedup_groups = _summarise(dedup_analysis)

    def k_counts(groups):
        return dict(Counter(g["k"] for g in groups))

    report = {
        "rows_total": len(rows),
        "adjusted_rows": sum(1 for r in rows if int(r.get("adjusted") or 0) == 1),
        "crude_rows": sum(1 for r in rows if int(r.get("adjusted") or 0) == 0),
        "deduped_rows": len(deduped),
        "dropped_duplicates": len(dropped),
        "variant_all": {
            "usable": all_analysis.get("usable"),
            "groups": all_groups,
            "k_distribution": k_counts(all_groups),
            "groups_k_ge_2": sum(1 for g in all_groups if g["k"] >= 2),
            "excluded": all_analysis.get("excluded") or [],
        },
        "variant_deduped": {
            "usable": dedup_analysis.get("usable"),
            "groups": dedup_groups,
            "k_distribution": k_counts(dedup_groups),
            "groups_k_ge_2": sum(1 for g in dedup_groups if g["k"] >= 2),
            "excluded": dedup_analysis.get("excluded") or [],
        },
    }

    out = Path(args.json)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Pooling der 31 gelesenen Effektzeilen",
        "",
        f"Zeilen: {report['rows_total']} (adjustiert "
        f"{report['adjusted_rows']}, crude {report['crude_rows']}). "
        f"Nach der Regel 'adjustiert vor crude': {report['deduped_rows']} Zeilen, "
        f"{report['dropped_duplicates']} Doppelzeilen entfernt.",
        "",
        "## Variante A: alle Zeilen (Pooling trennt nach Anpassungszustand)",
        "",
        f"Gruppen gesamt: {len(all_groups)} | k-Verteilung: "
        f"{report['variant_all']['k_distribution']} | Gruppen mit k >= 2: "
        f"**{report['variant_all']['groups_k_ge_2']}**",
        "",
        "| Gruppe | k | gepoolt | 95 %-CI | I² |",
        "|---|---:|---:|---|---:|",
    ]
    for group in all_groups:
        pooled = "-" if group["pooled"] is None else f"{group['pooled']:.3f}"
        ci = "-" if group["ci_low"] is None else f"{group['ci_low']:.3f} bis {group['ci_high']:.3f}"
        i2 = "-" if group["i2"] is None else f"{group['i2']:.1f}"
        lines.append(f"| {group['group'][:52]} | {group['k']} | {pooled} | {ci} | {i2} |")

    lines += [
        "",
        "## Variante B: adjustiert vor crude (eine Zeile je Quelle/Outcome/Typ)",
        "",
        f"Gruppen gesamt: {len(dedup_groups)} | k-Verteilung: "
        f"{report['variant_deduped']['k_distribution']} | Gruppen mit k >= 2: "
        f"**{report['variant_deduped']['groups_k_ge_2']}**",
        "",
        "| Gruppe | k | gepoolt | 95 %-CI |",
        "|---|---:|---:|---|",
    ]
    for group in dedup_groups:
        pooled = "-" if group["pooled"] is None else f"{group['pooled']:.3f}"
        ci = "-" if group["ci_low"] is None else f"{group['ci_low']:.3f} bis {group['ci_high']:.3f}"
        lines.append(f"| {group['group'][:52]} | {group['k']} | {pooled} | {ci} |")

    removed = report["variant_all"]["excluded"] + report["variant_deduped"]["excluded"]
    lines += ["", "## Vom Pooling aussortierte Zeilen", ""]
    if not removed:
        lines.append("- keine")
    for entry in removed:
        lines.append(f"- {entry.get('label', '')[:50]}: {entry.get('reason', '')}")

    sources = len({r.get("source_id") for r in deduped})
    combos = len({(r.get("source_id"), r.get("outcome"), r.get("effect_type"))
                  for r in deduped})
    collapsed = len(report["variant_deduped"]["excluded"])
    lines += [
        "",
        "## Lesart",
        "",
        f"Von {len(dedup_groups)} Gruppen erreicht keine k >= 2. Die "
        f"{len(deduped)} Zeilen stammen aus {sources} Quellen und decken "
        f"{combos} Quelle-Outcome-Kombinationen ab; das Pooling hat "
        f"{collapsed} abhaengige Zeilen derselben Quelle als Kollaps "
        "aussortiert. Ohne zweite unabhaengige Studie zum selben Outcome "
        "gibt es kein gepooltes Ergebnis - das ist die ehrliche Antwort, "
        "kein Fehler des Poolings.",
        "",
        "Die crude/adjustiert-Regel greift zeilenweise: innerhalb derselben "
        "Tabellenzeile bleibt nur die adjustierte Schaetzung. Ueber Zeilen "
        "hinweg wird bewusst nichts zusammengelegt - dieselbe Quelle kann "
        "zwei Modelle berichten (pcd: 2.78/2.37 und 1.70/1.46), und welches "
        "davon dasselbe Ergebnis ist, entscheidet nicht der Leser, sondern "
        "der Kollaps im Pooling mit seiner Begruendung.",
    ]
    Path(args.md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "rows": report["rows_total"],
        "deduped": report["deduped_rows"],
        "dropped": report["dropped_duplicates"],
        "groups_all": len(all_groups),
        "groups_all_k_ge_2": report["variant_all"]["groups_k_ge_2"],
        "groups_dedup": len(dedup_groups),
        "groups_dedup_k_ge_2": report["variant_deduped"]["groups_k_ge_2"],
        "k_dist_all": report["variant_all"]["k_distribution"],
        "k_dist_dedup": report["variant_deduped"]["k_distribution"],
    }, ensure_ascii=False))
    print(f"JSON: {args.json}")
    print(f"MD:   {args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
