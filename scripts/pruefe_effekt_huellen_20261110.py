"""Zwei Dokumente gegen die effects-Huelle: kommen mehrere Zeilen zurueck?"""

import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _pdf_to_text          # noqa: E402
from research_agent.llm.engine import LLMEngine, unwrap_json_list  # noqa: E402
from research_agent.meta.extraction import EffectExtractor        # noqa: E402
from research_agent.meta.pdf_text import normalize                # noqa: E402

OUT = ROOT / "data" / "bench" / "validierung"
VOLL = ROOT / "data" / "bench" / "sol2" / "volltext"
FAELLE = (
    ("T1b", "bmj.e6664.full.pdf", ((-37.5, 0.05), (-45.3, 0.05))),
    ("T4", "1-s2.0-S1389945724004866-main.pdf", ((8.36, 0.05),)),
)


async def main() -> int:
    llm = LLMEngine()
    if not await llm.health_check():
        print("Backend nicht erreichbar:", LLMEngine.last_failure())
        return 3
    ex = EffectExtractor(llm, db=None, double_pass=False)
    alle = []
    for name, datei, soll in FAELLE:
        text = normalize(_pdf_to_text(VOLL / datei) or "")
        messages = ex._messages(text, "melatonin", None)
        huelle = "effects" in messages[0]["content"]
        raw = await llm.chat(messages, temperature=0.2, max_tokens=4096, format_json=True)
        (OUT / f"effekt_huellen_{name}_20261110.txt").write_text(raw, encoding="utf-8")
        parsed = json.loads(raw)
        schluessel = list(parsed) if isinstance(parsed, dict) else None
        listen = ({k: len(v) for k, v in parsed.items() if isinstance(v, list)}
                  if isinstance(parsed, dict) else {})
        items = unwrap_json_list(parsed)
        rows = [ex._normalize(i, None) for i in items if isinstance(i, dict)]
        mit_se = sum(1 for r in rows if r.get("se") is not None)
        treffer = []
        for wert, tol in soll:
            hits = [r for r in rows
                    if r.get("effect") is not None and abs(r["effect"] - wert) <= tol]
            treffer.append({"soll": wert, "getroffen": bool(hits),
                            "outcome": hits[0]["outcome"] if hits else None})
        print(f"{name}: Huelle im Prompt {huelle} | Roh {len(raw)} Zeichen | "
              f"Top {type(parsed).__name__} | Schluessel {schluessel}")
        print(f"   Listenlaengen {listen} | unwrap {len(items)} | Zeilen {len(rows)} "
              f"| mit SE {mit_se}")
        for r in rows[:12]:
            print("   -", (r["outcome"] or "")[:45], r.get("effect"),
                  "se" if r.get("se") is not None else "ohne")
        print("   Soll:", treffer)
        alle.append({"fall": name, "datei": datei, "huelle_im_prompt": huelle,
                     "roh_zeichen": len(raw), "roh_datei": f"effekt_huellen_{name}_20261110.txt",
                     "top_typ": type(parsed).__name__, "schluessel": schluessel,
                     "listen": listen, "unwrap_items": len(items),
                     "zeilen": len(rows), "zeilen_mit_se": mit_se,
                     "soll_treffer": treffer,
                     "outcomes": [r["outcome"] for r in rows]})
    (OUT / "effekt_huellen_20261110.json").write_text(
        json.dumps({"faelle": alle, "tokens": dict(LLMEngine.get_stats())},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    print("Tokens:", dict(LLMEngine.get_stats()))
    await llm.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
