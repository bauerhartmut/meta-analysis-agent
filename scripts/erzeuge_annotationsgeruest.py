"""Erzeugt die leeren Annotationsgerueste fuer A und B.

Quelle ist data/golden_effects/documents.json. Die drei Dokumente fuer den
Kappa-Probelauf werden mit "probelauf": true markiert. Vorhandene Dateien
werden nicht ueberschrieben, damit annotierte Arbeit nicht verloren geht;
--force ersetzt sie ausdruecklich.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/erzeuge_annotationsgeruest.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUELLE = ROOT / "data/golden_effects/documents.json"
ZIEL = ROOT / "data/golden_effects"
PROBELAUF = ("bb9218735f", "7111ea9787", "203c831dbe")


def geruest(dokumente: list, annotator: str) -> dict:
    return {
        "dataset": "goldstandard_effects",
        "version": "1.0",
        "annotator": annotator,
        "annotation_date": "2026-11-10",
        "instructions_version": "1.0",
        "blind": True,
        "notes": ("Geruest, noch nicht annotiert. Nur Volltext, Anleitung "
                  "docs/internal/goldstandard_annotationsanleitung.md und "
                  "Schema verwenden."),
        "documents": [{
            "document_id": d["document_id"],
            "path": d["path"],
            "title": d["title"],
            "year": d.get("year"),
            "design_verbatim": d.get("design_verbatim") or "unknown",
            "design_category": d["design_category"],
            "stratum": d["stratum"],
            "has_text_layer": True,
            "probelauf": any(d["document_id"].startswith(p) for p in PROBELAUF),
            "expected_effects": None,
            "effects": [],
            "no_effect_reason": None,
            "notes": "",
        } for d in dokumente],
    }


def main(argv: list) -> int:
    force = "--force" in argv
    quelle = json.loads(QUELLE.read_text(encoding="utf-8"))
    dokumente = quelle["documents"]
    if len(dokumente) != 30:
        print(f"Erwartet 30 Dokumente, gefunden {len(dokumente)}")
        return 1
    for annotator in ("A", "B"):
        ziel = ZIEL / f"goldstandard_{annotator}.json"
        if ziel.exists() and not force:
            print(f"{ziel.name}: existiert, unveraendert (--force zum Ersetzen)")
            continue
        ziel.write_text(json.dumps(geruest(dokumente, annotator), ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
        print(f"{ziel.name}: {len(dokumente)} Dokumente, "
              f"{sum(1 for d in dokumente if any(d['document_id'].startswith(p) for p in PROBELAUF))} Probelauf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
