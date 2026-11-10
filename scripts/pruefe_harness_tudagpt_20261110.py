"""Acht Volltexte durch den LLM-Lesepfad (TUDaGPT), je ein Pass.

Read-only: `_one_pass` speichert nichts. Vor jedem Aufruf wird kostenlos
geprueft, ob der belegte Sollwert ueberhaupt im Prompt steht - sonst misst der
Lauf den Selektor, nicht den Leser.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/pruefe_harness_tudagpt_20261110.py
"""

import asyncio
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _pdf_to_text          # noqa: E402
from research_agent.llm.engine import LLMEngine                   # noqa: E402
from research_agent.meta.extraction import EffectExtractor        # noqa: E402
from research_agent.meta.pdf_text import normalize                # noqa: E402

V = ROOT / "data" / "bench" / "sol2" / "volltext"
OUT = ROOT / "data" / "bench" / "validierung"
TOPIC = "melatonin"

# (Fall, Datei, belegter Sollwert oder None)
FAELLE = [
    ("T1",  "23098680.txt", -37.49),
    ("T1b", "bmj.e6664.full.pdf", -37.5),
    ("T2",  "1741-7015-8-51.pdf", None),
    ("T3",  "213_2010_Article_1962.pdf", None),
    ("T4",  "1-s2.0-S1389945724004866-main.pdf", 8.36),
    ("T5",  "s10803-021-05139-w.pdf", -22.0),
    ("T6",  "Develop Med Child Neuro - 2008 - McArthur - Sleep dysfunction in Rett syndrome  a trial of exogenous melatonin treatment.pdf", None),
    ("T7",  "s10803-010-1036-5.pdf", None),
    ("T8",  "19030713.txt", None),
]


def lade_text(pfad: Path) -> str:
    if pfad.suffix.lower() == ".txt":
        roh = pfad.read_text(encoding="utf-8", errors="replace")
    else:
        roh = _pdf_to_text(pfad) or ""
    return normalize(roh)


def varianten(wert: float) -> list:
    s = f"{abs(wert):.1f}"
    return [s, s.replace(".", ","), f"{abs(wert):.2f}"]


def sol_zeilen(rows) -> list:
    treffer = []
    for r in rows:
        text = f"{r.get('outcome') or ''} {r.get('comparison') or ''}".lower()
        if "sleep onset" in text or re.search(r"\bsol\b", text):
            treffer.append({k: r.get(k) for k in (
                "outcome", "comparison", "effect_type", "effect", "se",
                "ci_low", "ci_high", "n", "quote", "rejection_reason")})
    return treffer


async def main() -> int:
    llm = LLMEngine()
    if not await llm.health_check():
        print("Backend nicht erreichbar:", LLMEngine.last_failure())
        return 3
    extraktor = EffectExtractor(llm, db=None, double_pass=False)

    ergebnisse = []
    for fall, name, soll in FAELLE:
        pfad = V / name
        if not pfad.exists():
            print(f"{fall:<4} FEHLT {name}")
            continue
        text = lade_text(pfad)
        if len(text) < 500:
            print(f"{fall:<4} kein Text ({len(text)} Zeichen) in {name}")
            continue

        messages = extraktor._messages(text, TOPIC, None)
        prompt = "\n".join(m.get("content") or "" for m in messages)
        im_prompt = None if soll is None else any(v in prompt for v in varianten(soll))

        start = time.time()
        fehler = ""
        try:
            rows = await extraktor._one_pass(
                f"test-{fall}", text, topic=TOPIC, sections=None, pass_number=1)
        except Exception as exc:                       # noqa: BLE001
            rows, fehler = [], f"{type(exc).__name__}: {exc}"
        dauer = time.time() - start

        zeilen = sol_zeilen(rows)
        treffer = None
        if soll is not None:
            treffer = any(
                z.get("effect") is not None and abs(float(z["effect"]) - soll) <= 0.06
                for z in zeilen)
        stats = LLMEngine.get_stats()
        print(f"{fall:<4} {len(text):>7} Z.  prompt {len(prompt):>6}  "
              f"soll_im_prompt={im_prompt}  zeilen={len(rows):>2} "
              f"sol={len(zeilen)}  soll_gefunden={treffer}  {dauer:.0f}s"
              + (f"  FEHLER {fehler}" if fehler else ""))
        for z in zeilen:
            print(f"      {z.get('effect')} se={z.get('se')} ci=[{z.get('ci_low')},{z.get('ci_high')}] "
                  f"{str(z.get('outcome'))[:50]!r}")

        ergebnisse.append({
            "fall": fall, "datei": name, "zeichen": len(text),
            "prompt_zeichen": len(prompt), "soll": soll,
            "soll_im_prompt": im_prompt, "soll_gefunden": treffer,
            "dauer_s": round(dauer, 1), "fehler": fehler,
            "zeilen": len(rows), "sol_zeilen": zeilen,
            "tokens": dict(stats),
            "alle_outcomes": sorted({str(r.get("outcome") or "")[:60] for r in rows}),
        })
        await asyncio.sleep(2)

    stats = LLMEngine.get_stats()
    (OUT / "tudagpt_lauf_20261110.json").write_text(
        json.dumps({"ergebnisse": ergebnisse, "tokens_gesamt": stats,
                    "modell": getattr(llm, "_tudagpt_model", "")},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nTokens gesamt: {stats['total_tokens']}  "
          f"Fehler: {stats['errors']}  letzter: {LLMEngine.last_failure()}")
    print(f"JSON: {OUT.relative_to(ROOT)}/tudagpt_lauf_20261110.json")
    await llm.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
