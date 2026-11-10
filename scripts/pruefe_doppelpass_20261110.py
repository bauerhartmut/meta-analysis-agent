"""Doppelpass auf T1b und T4: liest Pass A, Pass B und bei Konflikt den Klaerer.

Ruft dieselbe Reihenfolge auf wie EffectExtractor.extract, aber ohne _store:
keine Datenbank, keine Persistenz, nur Zaehlung. Sollwerte sind die im
Dokument belegten; T4 hat nur einen belegten Sollwert (8,36).
"""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _pdf_to_text            # noqa: E402
from research_agent.llm.engine import LLMEngine                    # noqa: E402
from research_agent.meta.extraction import (                       # noqa: E402
    EffectExtractor, compare_extraction_passes, resolve_third_attempt,
)
from research_agent.meta.pdf_text import normalize                 # noqa: E402

OUT = ROOT / "data" / "bench" / "validierung"
VOLL = ROOT / "data" / "bench" / "sol2" / "volltext"
FAELLE = (
    ("T1b", "bmj.e6664.full.pdf", ((-37.5, 0.05), (-45.3, 0.05), (22.4, 0.05))),
    ("T4", "1-s2.0-S1389945724004866-main.pdf", ((8.36, 0.05),)),
)


def zaehle(rows):
    """Zeilen eines Passes: numerisch, poolbar, Gate-Verworfene."""
    numerisch = [r for r in rows if r.get("effect") is not None]
    mit_se = [r for r in numerisch if r.get("se") is not None]
    verworfen = [r for r in rows if r.get("rejection_reason")]
    poolbar = [r for r in mit_se
               if not r.get("rejection_reason") and not r.get("disputed")]
    return {
        "zeilen": len(rows),
        "numerisch": len(numerisch),
        "mit_se": len(mit_se),
        "verworfen": len(verworfen),
        "poolbar": len(poolbar),
        "outcomes": [r.get("outcome") for r in rows],
    }


def treffer(rows, soll):
    out = []
    for wert, tol in soll:
        hits = [r for r in rows
                if r.get("effect") is not None and abs(r["effect"] - wert) <= tol]
        out.append({"soll": wert, "getroffen": bool(hits),
                    "outcome": hits[0]["outcome"] if hits else None,
                    "se": hits[0].get("se") if hits else None})
    return out


async def main() -> int:
    llm = LLMEngine()
    if not await llm.health_check():
        print("Backend nicht erreichbar:", LLMEngine.last_failure())
        return 3
    ex = EffectExtractor(llm, db=None, double_pass=True)
    alle = []

    for name, datei, soll in FAELLE:
        text = normalize(_pdf_to_text(VOLL / datei) or "")
        a = await ex._one_pass(name, text, "melatonin", None,
                               pass_number=1, temperature=0.2, frame="first")
        b = await ex._one_pass(name, text, "melatonin", None,
                               pass_number=2, field_order="precision_first",
                               temperature=0.4, frame="second")
        vergleich = compare_extraction_passes(a, b)
        c, aufloesung = [], {}
        if vergleich["conflicts"]:
            c = await ex._one_pass(name, text, "melatonin", None,
                                   pass_number=3, temperature=0.4, frame="third")
            aufloesung = resolve_third_attempt(a, b, c)

        za, zb, zc = zaehle(a), zaehle(b), zaehle(c)
        final = list(a) + list(b)
        zf = zaehle(final)
        eintrag = {
            "fall": name, "datei": datei,
            "pass_a": za, "pass_b": zb, "pass_claerer": zc,
            "vergleich": vergleich, "aufloesung": aufloesung,
            "final": zf,
            "treffer_a": treffer(a, soll), "treffer_b": treffer(b, soll),
            "treffer_c": treffer(c, soll), "treffer_final": treffer(final, soll),
            "zeilen_a": a, "zeilen_b": b, "zeilen_c": c,
        }
        alle.append(eintrag)

        print(f"\n== {name} ({datei}) ==")
        print(f"  A: {za['zeilen']} Zeilen, {za['numerisch']} numerisch, "
              f"{za['mit_se']} mit SE, {za['verworfen']} verworfen")
        print(f"  B: {zb['zeilen']} Zeilen, {zb['numerisch']} numerisch, "
              f"{zb['mit_se']} mit SE, {zb['verworfen']} verworfen")
        print(f"  Klaerer: {zc['zeilen']} Zeilen, {zc['mit_se']} mit SE")
        print(f"  Vergleich: {vergleich['compared']} Schluessel verglichen, "
              f"{len(vergleich['conflicts'])} Konflikte, "
              f"Quote {vergleich['conflict_ratio']}")
        for k in vergleich["conflicts"]:
            print("    !", k)
        if aufloesung:
            print("  Aufloesung:", aufloesung)
        print(f"  Final poolbar: {zf['poolbar']}")
        print("  Soll A:", treffer(a, soll))
        print("  Soll B:", treffer(b, soll))
        print("  Soll final:", treffer(final, soll))

    (OUT / "doppelpass_20261110.json").write_text(
        json.dumps({"faelle": alle, "tokens": dict(LLMEngine.get_stats())},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nTokens:", dict(LLMEngine.get_stats()))
    await llm.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
