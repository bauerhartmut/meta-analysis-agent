"""Prueft nur die Probelauf-Dokumente ohne --entwurf.

Erzeugt temporaere Kopien von A und B mit den Dokumenten, die
`probelauf: true` tragen, ruft `pruefe_goldstandard.py` ohne --entwurf
darauf auf und gibt dessen Exit-Code weiter. Die Kopien werden geloescht.

So zaehlt die Abgabe nicht die 27 Dokumente als Fehler, die erst in der
Vollannotation gefuellt werden.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRUEFER = ROOT / "scripts" / "pruefe_goldstandard.py"


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        pfade = []
        for annotator in ("A", "B"):
            quelle = ROOT / "data" / "golden_effects" / f"goldstandard_{annotator}.json"
            if not quelle.exists():
                print(f"Datei fehlt: {quelle}")
                return 1
            daten = json.loads(quelle.read_text(encoding="utf-8"))
            docs = [d for d in daten["documents"] if d.get("probelauf")]
            if not docs:
                print(f"{quelle.name}: keine Probelauf-Dokumente")
                return 1
            daten["documents"] = docs
            ziel = Path(tmp) / f"probelauf_{annotator}.json"
            ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=1) + "\n",
                            encoding="utf-8")
            pfade.append(str(ziel))
        print(f"Pruefe {len(pfade)} Dateien mit je den Probelauf-Dokumenten.")
        return subprocess.call([sys.executable, str(PRUEFER), *pfade])


if __name__ == "__main__":
    raise SystemExit(main())
