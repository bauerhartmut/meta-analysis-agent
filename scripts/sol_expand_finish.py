"""Abschlussauswertung des erweiterten SOL-Korpus.

Liest die Artefakte des Hintergrundlaufs (Suche, Effektspalten, Arm-Rechner,
Pooling) und schreibt den Befund. Rein offline ueber bereits erzeugte
Dateien; startet keinen Netzzugriff und keinen Lauf.

Aufruf:
    .venv/bin/python.exe scripts/sol_expand_finish.py
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

BASE = Path("data/bench/sol")
OUT = BASE / "expand_befund_20261107.md"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _pooling(path: Path) -> dict:
    data = _load(path)
    return data.get("variant_deduped") or {}


def _rows_for(db_path: Path, source_ids: list[str]) -> list[dict]:
    if not db_path.exists() or not source_ids:
        return []
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    marks = ",".join("?" for _ in source_ids)
    out = [dict(r) for r in con.execute(
        f"select source_id, outcome, effect_type, effect, se, time_point "
        f"from study_effects where source_id in ({marks})", source_ids)]
    con.close()
    return out


def main() -> int:
    search = _load(BASE / "search_summary.json")
    stats = search.get("stats", {})
    manifest = _load(BASE / "manifest_all.json")

    eff = _load(BASE / "effect_columns_all_20261107.json")
    eff_tot = eff.get("totals", {})
    eff_pool = _pooling(BASE / "pooling_effects_all_20261107.json")

    arm = _load(BASE / "arm_all_20261107.json")
    arm_tot = arm.get("totals", {})
    arm_pool = _pooling(BASE / "pooling_arm_all_20261107.json")

    k2_eff = [g for g in eff_pool.get("groups", []) if g.get("k", 0) >= 2]
    k2_arm = [g for g in arm_pool.get("groups", []) if g.get("k", 0) >= 2]

    lines = [
        "# SOL-Korpus auf 1067 Treffer erweitert: erstmals echte k >= 2?", "",
        "Stand: 07.11.2026. Dieselbe Europe-PMC-Query, jetzt ueber alle Seiten",
        "(`cursorMark`). Kein LLM, keine Zyklen; beide Leser deterministisch.", "",
        "## Suche und Download", "",
        "| Kennzahl | Wert |", "|---|---:|",
        f"| Treffer (hitCount) | {stats.get('epmc_hits')} |",
        f"| zurueckgeliefert | {stats.get('epmc_returned')} |",
        f"| mit PMCID | {stats.get('epmc_with_pmcid')} |",
        f"| Crossref-Ueberlappung | {stats.get('crossref_overlap_epmc')} |",
        f"| XML geladen (neu) | {search.get('download', {}).get('loaded')} |",
        f"| XML bereits vorhanden | {search.get('download', {}).get('present')} |",
        f"| Download-Fehler | {search.get('download', {}).get('failed')} |",
        f"| Manifest-Eintraege | {len(manifest)} |", "",
        "## Effektspalten-Leser", "",
        "| Kennzahl | Wert |", "|---|---:|",
        f"| Tabellenzeilen | {eff_tot.get('table_rows')} |",
        f"| gespeicherte Effekte | {eff_tot.get('stored')} |",
        f"| Modelltabellen uebersprungen | {eff_tot.get('model_tables')} |",
        f"| Pooling-Gruppen | {len(eff_pool.get('groups', []))} |",
        f"| **Gruppen mit k >= 2** | **{len(k2_eff)}** |", "",
    ]
    if k2_eff:
        lines.append("### Gruppen mit k >= 2 (Effektspalten)")
        lines.append("")
        for group in k2_eff:
            rows = _rows_for(BASE / "direct_all.db", list(group.get("rows") or []))
            lines.append(f"* `{group['group']}`: k = {group['k']}, "
                         f"pooled = {group.get('pooled')}, "
                         f"CI {group.get('ci_low')} bis {group.get('ci_high')}, "
                         f"I2 = {group.get('i2')}")
            for row in rows:
                lines.append(f"  - {row['source_id']} | {row['outcome']} | "
                             f"{row['effect_type']} = {row['effect']} (SE {row['se']})")
        lines.append("")

    lines += [
        "## Arm-Rechner", "",
        "| Kennzahl | Wert |", "|---|---:|",
        f"| Tabellenzeilen | {arm_tot.get('table_rows')} |",
        f"| umrechenbar | {arm_tot.get('convertible')} |",
        f"| gespeichert | {arm_tot.get('stored')} |",
        f"| Pooling-Gruppen | {len(arm_pool.get('groups', []))} |",
        f"| **Gruppen mit k >= 2** | **{len(k2_arm)}** |", "",
    ]
    if k2_arm:
        lines.append("### Gruppen mit k >= 2 (Arm-Rechner)")
        lines.append("")
        for group in k2_arm:
            rows = _rows_for(BASE / "arm_all.db", list(group.get("rows") or []))
            lines.append(f"* `{group['group']}`: k = {group['k']}, "
                         f"g = {group.get('pooled')}, "
                         f"CI {group.get('ci_low')} bis {group.get('ci_high')}, "
                         f"I2 = {group.get('i2')}")
            for row in rows:
                lines.append(f"  - {row['source_id']} | {row['outcome']} | "
                             f"g = {row['effect']:.3f} (SE {row['se']:.3f}) | "
                             f"Zeitpunkt: {row['time_point'] or '-'}")
        lines.append("")

    total_k2 = len(k2_eff) + len(k2_arm)
    lines += [
        "## Fazit", "",
        (f"Der erweiterte Korpus liefert **{total_k2}** Gruppen mit k >= 2."
         if total_k2 else
         "Auch der erweiterte Korpus liefert **keine** Gruppe mit k >= 2."), "",
        "Vergleich zum 100-Dokument-Lauf: dort 15 Effektspalten-Zeilen (alle",
        "k = 1) und 3 Arm-Zeilen nach dem Design-Gate (alle k = 1).", "",
        "## Grenzen", "",
        "* Europe PMC liefert 1067 der 1068 Treffer; ein Datensatz fehlt in der",
        "  Blaetterung.",
        "* Nur Dokumente mit PMCID und verfuegbarem `fullTextXML` sind im",
        "  Korpus; die Download-Fehler stehen oben.",
        "* k >= 2 heisst hier 'zwei unabhaengige Studien mit nutzbarer",
        "  Praezision in derselben Gruppe' - die Design-Gates des Arm-Rechners",
        "  sind aktiv, ersetzen aber keine Risk-of-Bias-Bewertung.", "",
    ]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "manifest": len(manifest),
        "effects_stored": eff_tot.get("stored"),
        "effects_groups": len(eff_pool.get("groups", [])),
        "effects_k2": len(k2_eff),
        "arm_stored": arm_tot.get("stored"),
        "arm_groups": len(arm_pool.get("groups", [])),
        "arm_k2": len(k2_arm),
        "k2_names": [g.get("group") for g in k2_eff + k2_arm],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
