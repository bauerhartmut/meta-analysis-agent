"""Sucht Spannweiten ueber Zeitpunkte in den Goldstandard-Volltexten.

Read-only, kein Modellaufruf. Die Muster sind Hinweise, keine Entscheidung:
- Korrelationen in eckigen Klammern (rs=[a, b]) sind der bekannte Fall 5.11.
- range/ranging/from ... to mit Zahlen kann eine Spanne sein.
- time points/across time points nennt den Bezug, ohne Zahl.
- zwei Zahlen in eckigen Klammern sind oft ein KI; das prueft der Mensch.

Ausgabe: JSON mit allen Treffern und Satzkontext. Die Bewertung steht
getrennt im Markdown-Bericht.
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MUSTER = [
    ("korrelation_spanne", re.compile(r"\brs?\s*=\s*\[[^\]]{0,80}\]", re.I)),
    ("range", re.compile(r"\b(?:range[sd]?|ranging)\b[^.]{0,140}\d", re.I)),
    ("von_bis", re.compile(r"\bfrom\s+[\-\u2212\u2013]?\d[^.]{0,80}\bto\s+[\-\u2212\u2013]?\d", re.I)),
    ("zeitpunkte", re.compile(r"\b(?:across|at)\s+(?:all\s+)?(?:the\s+)?(?:three|two|\d+)?\s*time\s*points?\b", re.I)),
    ("klammer_zwei_zahlen", re.compile(r"\[\s*[\-\u2212\u2013]?\d+[.,]\d+\s*[,;]\s*[\-\u2212\u2013]?\d+[.,]\d+\s*\]")),
]


def satz_um(text: str, start: int, ende: int) -> str:
    anfang = max(text.rfind(".", 0, start), text.rfind("\n\n", 0, start)) + 1
    schluss = text.find(".", ende)
    if schluss == -1 or schluss - ende > 400:
        schluss = min(len(text), ende + 250)
    return " ".join(text[anfang:schluss + 1].split())[:420]


def treffer(text: str):
    gefunden = []
    for name, rx in MUSTER:
        for m in rx.finditer(text):
            gefunden.append({"art": name, "start": m.start(),
                             "treffer": " ".join(m.group(0).split())[:160],
                             "satz": satz_um(text, m.start(), m.end())})
    gesehen, unique = set(), []
    for t in sorted(gefunden, key=lambda x: x["start"]):
        key = t["satz"][:90]
        if key in gesehen:
            continue
        gesehen.add(key)
        unique.append(t)
    return unique


def main(argv: list) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs", default="data/golden_effects/documents.json")
    parser.add_argument("--out", default="data/golden_effects/spannweiten.json")
    args = parser.parse_args(argv)
    docs = json.loads((ROOT / args.docs).read_text(encoding="utf-8"))["documents"]

    ergebnis, gesamt = [], 0
    for doc in docs:
        fid = doc["document_id"]
        pfad = ROOT / "data/fulltext" / f"{fid}.txt"
        if not pfad.exists():
            ergebnis.append({"document_id": fid, "stratum": doc["stratum"],
                             "fehlt": True, "treffer": []})
            continue
        text = pfad.read_text(encoding="utf-8", errors="replace")
        t = treffer(text)
        gesamt += len(t)
        ergebnis.append({"document_id": fid, "stratum": doc["stratum"],
                         "zeichen": len(text), "treffer": t})
        if t:
            print(f"\n=== {fid[:10]} {doc['stratum']} ({len(t)} Treffer) ===")
            for x in t[:6]:
                print(f"  [{x['art']}] {x['treffer']}")
                print(f"    {x['satz']}")

    ohne = [d for d in ergebnis if not d.get("fehlt") and not d["treffer"]]
    print(f"\nDokumente: {len(ergebnis)} | Treffer: {gesamt} | "
          f"ohne Treffer: {len(ohne)} | fehlende Dateien: "
          f"{sum(1 for d in ergebnis if d.get('fehlt'))}")
    ziel = ROOT / args.out
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps({"dokumente": ergebnis}, ensure_ascii=False,
                               indent=1) + "\n", encoding="utf-8")
    print(f"JSON: {ziel.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(__import__("sys").argv[1:]))
