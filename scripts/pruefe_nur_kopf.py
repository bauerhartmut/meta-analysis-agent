"""Stichprobe der nur_kopf-Zeilen: echte Effekte oder Baseline-Werte?

Read-only. Sammelt alle abgelehnten Zeilen, bei denen die Spaltenzahl stimmt
und nur die Effektspalte im Kopf fehlt (Kategorie ``nur_kopf`` aus
``messe_kopf_blocker.py``), zieht eine deterministische Stichprobe und legt
sie mit Label, lesbarer Zelle, Kopfzelle und Caption offen.

Die Heuristik im Skript zaehlt nur Signale (Baseline-Wort, Effekt-Wort) - das
Urteil faellt nicht hier, sondern in der Bewertungsdatei daneben. Damit ist
nachpruefbar, worauf die Einschaetzung beruht.

Kein Modell, kein Netz, keine Aenderung an der Pipeline.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.meta.effect_columns import (  # noqa: E402
    effects_from_row,
    header_effect_kind,
    parse_effect_cell,
)
from research_agent.meta.pdf_text import normalize  # noqa: E402
from research_agent.research.table_extractor import find_table_blocks  # noqa: E402
from scripts.read_pdf_corpus import rows_from_block  # noqa: E402

OUT_DIR = ROOT / "data/bench/validierung"

BASELINE = re.compile(
    r"baseline|\bt0\b|week 0|characteristic|demograph|at entry|"
    r"mean \(sd\)|\bsd\b|range|score at", re.I)
EFFEKT = re.compile(
    r"difference|change|\bvs\b|versus|effect|reduction|improvement|"
    r"contrast|\bmd\b|\bsmd\b|\bor\b|\brr\b|\bhr\b|\bbeta\b|"
    r"between-group|compared", re.I)


def _rel(pfad: Path) -> str:
    try:
        return str(Path(pfad).resolve().relative_to(ROOT))
    except ValueError:
        return str(pfad)


def sammle(datei: Path) -> tuple[list[dict], int]:
    """Alle nur_kopf-Zeilen einer Datei plus Gesamtzahl der Ablehnungen."""
    text = normalize(datei.read_text(encoding="utf-8", errors="replace"))
    blocks = find_table_blocks(text)
    abgelehnt = 0
    treffer: list[dict] = []

    for nummer, block in enumerate(blocks, 1):
        header, rows = rows_from_block(block.body)
        if not rows:
            continue
        caption = str(block.caption or "")
        kopf_effekt = [i for i, h in enumerate(header)
                       if header_effect_kind(h)[2]]
        for cells in rows:
            found, _ = effects_from_row(
                header, cells, block.body, caption=caption)
            if found:
                continue
            abgelehnt += 1
            if kopf_effekt or len(cells) != len(header):
                continue
            lesbar = [(i, c, parse_effect_cell(c)) for i, c in enumerate(cells)
                      if parse_effect_cell(c) is not None]
            if not lesbar:
                continue
            index, zelle, werte = lesbar[0]
            label = str(cells[0]) if cells else ""
            treffer.append({
                "datei": _rel(datei),
                "block": nummer,
                "caption": caption[:120],
                "kopf": [str(h)[:40] for h in header[:12]],
                "zeile": [str(c)[:60] for c in cells[:12]],
                "label": label[:90],
                "zelle": zelle.strip()[:60],
                "zelle_index": index,
                "werte": list(werte),
                "kopfzelle": (str(header[index])[:40]
                              if index < len(header) else ""),
                "baseline_signal": bool(BASELINE.search(label + " " + caption)),
                "effekt_signal": bool(EFFEKT.search(label + " " + caption)),
            })
    return treffer, abgelehnt


def schreibe(ergebnis: dict, ziel_md: Path, ziel_json: Path) -> None:
    ziel_json.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                         encoding="utf-8", newline="\n")
    z = [
        "# Stichprobe der `nur_kopf`-Zeilen (Rohdaten zur Bewertung)",
        "",
        f"Stand: {ergebnis['stand']}. Determinismus: Seed "
        f"{ergebnis['seed']}, Stichprobe {ergebnis['stichprobe']} von "
        f"{ergebnis['gesamt_nur_kopf']}.",
        "",
        "| Kennzahl | Wert |",
        "|---|---:|",
        f"| Dateien | {ergebnis['dateien']} |",
        f"| abgelehnte Zeilen | {ergebnis['abgelehnt']} |",
        f"| `nur_kopf` gesamt | {ergebnis['gesamt_nur_kopf']} |",
        f"| Stichprobe | {ergebnis['stichprobe']} |",
        f"| Baseline-Signal | {ergebnis['signale']['baseline']} |",
        f"| Effekt-Signal | {ergebnis['signale']['effekt']} |",
        f"| beide Signale | {ergebnis['signale']['beide']} |",
        f"| kein Signal | {ergebnis['signale']['keins']} |",
        "",
        "## Gezogene Zeilen",
        "",
    ]
    for nummer, fall in enumerate(ergebnis["faelle"], 1):
        z += [
            f"### {nummer}. `{Path(fall['datei']).name}` Block {fall['block']}",
            "",
            f"- Label: `{fall['label']}`",
            f"- lesbare Zelle (Spalte {fall['zelle_index']}): "
            f"`{fall['zelle']}` -> {fall['werte']}",
            f"- Kopfzelle an dieser Position: `{fall['kopfzelle']}`",
            f"- Kopf: {fall['kopf']}",
            f"- Caption: `{fall['caption']}`",
            f"- Signale: baseline={fall['baseline_signal']}, "
            f"effekt={fall['effekt_signal']}",
            "",
        ]
    ziel_md.write_text("\n".join(z), encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", default="data/bench/sol/fulltext")
    parser.add_argument("--max-dateien", type=int, default=120)
    parser.add_argument("--stichprobe", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20261108)
    args = parser.parse_args(argv)

    start = time.perf_counter()
    dateien = sorted(Path(args.dir).glob("*.txt"))[:args.max_dateien]
    if not dateien:
        raise SystemExit("keine Eingabedateien gefunden")

    alle: list[dict] = []
    abgelehnt = 0
    for datei in dateien:
        treffer, n = sammle(datei)
        alle.extend(treffer)
        abgelehnt += n

    rng = random.Random(args.seed)
    anzahl = min(args.stichprobe, len(alle))
    faelle = rng.sample(alle, anzahl)
    faelle.sort(key=lambda f: (f["datei"], f["block"]))

    signale = Counter({"baseline": 0, "effekt": 0, "beide": 0, "keins": 0})
    for fall in faelle:
        if fall["baseline_signal"] and fall["effekt_signal"]:
            signale["beide"] += 1
        elif fall["baseline_signal"]:
            signale["baseline"] += 1
        elif fall["effekt_signal"]:
            signale["effekt"] += 1
        else:
            signale["keins"] += 1

    ergebnis = {
        "stand": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "modell": "keiner",
        "netz": "keines",
        "seed": args.seed,
        "dateien": len(dateien),
        "abgelehnt": abgelehnt,
        "gesamt_nur_kopf": len(alle),
        "stichprobe": anzahl,
        "signale": dict(signale),
        "faelle": faelle,
        "laufzeit_s": time.perf_counter() - start,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ziel_md = OUT_DIR / "nur_kopf_stichprobe_20261108.md"
    ziel_json = OUT_DIR / "nur_kopf_stichprobe_20261108.json"
    schreibe(ergebnis, ziel_md, ziel_json)

    print(f"Dateien {len(dateien)}, abgelehnt {abgelehnt}, "
          f"nur_kopf {len(alle)}")
    print(f"Stichprobe {anzahl}, Signale {dict(signale)}")
    print(f"({ergebnis['laufzeit_s']:.3f} s) -> {ziel_md.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
