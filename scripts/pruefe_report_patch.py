#!/usr/bin/env python
"""Prueft read-only, ob der lokale Report das Ein-Cluster-Gate auswertet.

Die betroffenen Dateien sind gitignored; ihr Inhalt darf nicht ins Repo. Was
pruefbar bleibt, ist die Wirkung: `pool_gates.single_cluster_gate` setzt
`single_cluster`, `pooling` ruft das Gate auf, und `report.py` erklaert
daraufhin das fehlende Intervall statt `[-, -]` stumm zu drucken.

Das Skript importiert nichts aus `research_agent` (sonst haengt die Pruefung
an einer der geschuetzten Dateien) und schreibt nichts.

Exit 0: alle Marker vorhanden. Exit 1: mindestens einer fehlt.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, List

REPO = Path(__file__).resolve().parent.parent

# Datei relativ zum Repo -> Marker, die alle vorkommen muessen.
CHECKS = (
    ("research_agent/meta/pool_gates.py",
     ("def single_cluster_gate", '"single_cluster"')),
    ("research_agent/meta/pooling.py",
     ("single_cluster_gate(analysis)",)),
    ("research_agent/report.py",
     ('group.get("single_cluster")', "Kein Konfidenzintervall")),
)

BACKUP = Path("local_patches") / "report_20261108.py"


def pruefe_text(text: str, marker: Iterable[str]) -> List[str]:
    """Gibt die Marker zurueck, die im Text fehlen."""

    return [m for m in marker if m not in text]


def main() -> int:
    fehlt: List[str] = []
    for relativ, marker in CHECKS:
        pfad = REPO / relativ
        if not pfad.is_file():
            print(f"FEHLT   {relativ}: Datei nicht vorhanden")
            fehlt.append(relativ)
            continue
        offen = pruefe_text(
            pfad.read_text(encoding="utf-8", errors="replace"), marker
        )
        if offen:
            print(f"FEHLT   {relativ}: {', '.join(offen)}")
            fehlt.append(relativ)
        else:
            print(f"OK      {relativ} ({len(marker)} Marker)")

    report = REPO / "research_agent" / "report.py"
    sicherung = REPO / BACKUP
    if not sicherung.is_file():
        print(f"HINWEIS {BACKUP}: keine lokale Sicherung")
    elif report.is_file() and sicherung.read_bytes() == report.read_bytes():
        print(f"OK      {BACKUP}: identisch mit report.py")
    else:
        print(f"HINWEIS {BACKUP}: weicht von report.py ab")

    if fehlt:
        print(f"\nErgebnis: Report-Patch NICHT wirksam ({len(fehlt)} Datei(en)).")
        return 1
    print("\nErgebnis: Report-Patch wirksam.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
