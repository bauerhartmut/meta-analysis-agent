"""Rendert den Metaanalyse-Abschnitt und zeigt die RVE-Zeilen.

Nachweis, dass `rve_re` im Report ankommt: Das Skript baut ein `Database` auf
einer Kopie, ruft `report._meta_section` auf und druckt jede Zeile, die RVE
oder den M=1-Hinweis enthaelt. Read-only auf der Kopie, keine Modellaufrufe.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/zeige_rve_im_report.py [db-pfad]
"""

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

VORGABE = ("data/research-mediterrane-ernaehrung-und-kardiovaskula-475855.db")


def kopie(path: Path) -> Path:
    ziel = Path(tempfile.mkdtemp(prefix="report_kopie_")) / "kopie.db"
    shutil.copy2(path, ziel)
    return ziel


def main() -> int:
    pfad = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / VORGABE
    if not pfad.is_file():
        print(f"DB nicht gefunden: {pfad}")
        return 1

    ziel = kopie(pfad)
    try:
        from research_agent.database import Database
        from research_agent.report import _meta_section

        db = Database(str(ziel))
        try:
            zeilen = []
            _meta_section(zeilen.append, db, pfad.stem)
        finally:
            close = getattr(db, "close", None)
            if callable(close):
                close()
    finally:
        shutil.rmtree(ziel.parent, ignore_errors=True)

    print(f"# {pfad.name}: {len(zeilen)} Zeilen gerendert")
    treffer = [z for z in zeilen if "RVE" in z or "Kein Konfidenzintervall" in z]
    if not treffer:
        print("(keine RVE-Zeile - Gruppe unter k = 2 oder ohne RVE-Block)")
        return 0
    for zeile in treffer:
        print(zeile)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
