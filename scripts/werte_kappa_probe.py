"""Wertet den Kappa zwischen zwei Annotationsdateien aus (Vollannotation).

Beispiel:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/werte_kappa_probe.py \
        --a data/golden_effects/goldstandard_A.json \
        --b data/golden_effects/goldstandard_B.json \
        --out data/golden_effects/kappa.json

Ohne --probelauf werden alle Dokumente verglichen; das ist der Kappa-Lauf
nach der Vollannotation. --probelauf ist nur ein Techniktest auf den drei
markierten Dokumenten und keine Kappa-Messung. --schwelle setzt die Grenze
fuer "bestanden" (Default 0,80, Zeilen-Kappa). Der Exit-Code ist 0, solange
die Dateien lesbar sind; das Ergebnis steht im Bericht.

--selbsttest prueft die Kappa-Formel an konstruierten Faellen.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.goldstandard_kappa import (  # noqa: E402
    als_text, cohens_kappa, vergleiche,
)


def lade(pfad: Path) -> dict:
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    return {d["document_id"]: d.get("effects") or [] for d in daten["documents"]}


def selbsttest() -> int:
    faelle = [
        ([1] * 10, [1] * 10, 1.0),
        ([1] * 10, [0] * 10, 0.0),
        ([1, 0] * 5, [0, 1] * 5, -1.0),
        ([1, 1, 0, 0], [1, 0, 0, 0], 0.5),
    ]
    for a, b, erwartet in faelle:
        wert = cohens_kappa(a, b)
        if abs(wert - erwartet) > 1e-9:
            print(f"Selbsttest fehlgeschlagen: {a} vs {b} = {wert}, erwartet {erwartet}")
            return 1
    if cohens_kappa([], []) is not None:
        print("Selbsttest fehlgeschlagen: leere Listen muessen None ergeben")
        return 1
    print("Selbsttest: Kappa-Formel ok (4 Faelle + leerer Fall)")
    return 0


def main(argv: list) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--a", default="data/golden_effects/goldstandard_A.json")
    p.add_argument("--b", default="data/golden_effects/goldstandard_B.json")
    p.add_argument("--probelauf", action="store_true",
                   help="nur Dokumente mit probelauf=true (Techniktest, keine Kappa-Messung)")
    p.add_argument("--schwelle", type=float, default=0.80)
    p.add_argument("--toleranz", type=float, default=0.01)
    p.add_argument("--out", default="")
    p.add_argument("--selbsttest", action="store_true")
    args = p.parse_args(argv)

    if args.selbsttest:
        return selbsttest()

    pa, pb = ROOT / args.a, ROOT / args.b
    for pfad in (pa, pb):
        if not pfad.exists():
            print(f"Datei fehlt: {pfad}")
            return 1
    da, db = lade(pa), lade(pb)
    if args.probelauf:
        ids = {d["document_id"] for d in
               json.loads(pa.read_text(encoding="utf-8"))["documents"]
               if d.get("probelauf")}
        da = {k: v for k, v in da.items() if k in ids}
        db = {k: v for k, v in db.items() if k in ids}
        if not ids:
            print("Keine Dokumente mit probelauf=true gefunden.")
            return 1

    ergebnis = vergleiche(da, db, toleranz=args.toleranz)
    ergebnis["schwelle"] = args.schwelle
    ergebnis["dateien"] = [str(pa.relative_to(ROOT)), str(pb.relative_to(ROOT))]
    print(als_text(ergebnis, args.schwelle))
    if args.out:
        ziel = ROOT / args.out
        ziel.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=1, default=list) + "\n",
                        encoding="utf-8")
        print(f"Bericht: {ziel.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
