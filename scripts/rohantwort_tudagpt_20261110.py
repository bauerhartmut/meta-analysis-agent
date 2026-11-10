"""Eine Rohantwort sichern und Parser gegen Modell trennen.

Ein Modellaufruf. Die Antwort wird unveraendert gespeichert, dann dreimal
ausgewertet: als Text, als JSON und durch `unwrap_json_list` + `_normalize`.
So ist belegbar, ob das Modell eine Zeile liefert oder der Parser sie verliert.
"""

import asyncio
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _pdf_to_text          # noqa: E402
from research_agent.llm.engine import LLMEngine, unwrap_json_list  # noqa: E402
from research_agent.meta.extraction import EffectExtractor        # noqa: E402
from research_agent.meta.pdf_text import normalize                # noqa: E402

DATEI = ROOT / "data" / "bench" / "sol2" / "volltext" / "bmj.e6664.full.pdf"
OUT = ROOT / "data" / "bench" / "validierung"
TOPIC = "melatonin"


def objekte_in(wert) -> int:
    """Zaehlt dict-Objekte rekursiv - was das Modell wirklich geschickt hat."""
    if isinstance(wert, dict):
        return 1 + sum(objekte_in(v) for v in wert.values())
    if isinstance(wert, list):
        return sum(objekte_in(v) for v in wert)
    return 0


async def main() -> int:
    text = normalize(_pdf_to_text(DATEI) or "")
    llm = LLMEngine()
    if not await llm.health_check():
        print("Backend nicht erreichbar:", LLMEngine.last_failure())
        return 3
    ex = EffectExtractor(llm, db=None, double_pass=False)
    messages = ex._messages(text, TOPIC, None)
    prompt = "\n".join(m.get("content") or "" for m in messages)

    raw = await llm.chat(messages, temperature=0.2, max_tokens=4096, format_json=True)
    (OUT / "rohantwort_20261110.txt").write_text(raw, encoding="utf-8")

    print(f"Prompt {len(prompt)} Zeichen, Rohantwort {len(raw)} Zeichen")
    print("letzte 60 Zeichen:", repr(raw[-60:]))
    print("endet geschlossen:", raw.rstrip().endswith(("]", "}")))

    parsed, fehler = None, ""
    try:
        parsed = json.loads(raw)
    except Exception as exc:                      # noqa: BLE001
        fehler = f"{type(exc).__name__}: {exc}"

    print("json.loads:", "ok" if parsed is not None else fehler)
    if parsed is not None:
        print("Top-Typ:", type(parsed).__name__,
              "| Laenge:" , len(parsed) if hasattr(parsed, "__len__") else "-")
        if isinstance(parsed, dict):
            print("Schluessel:", list(parsed)[:8])
            print("Listenwerte:", {k: len(v) for k, v in parsed.items() if isinstance(v, list)})
        print("dict-Objekte im Roh-JSON:", objekte_in(parsed))

    items = unwrap_json_list(parsed) if parsed is not None else []
    print("unwrap_json_list:", len(items), "Item(s)")
    rows = []
    for item in items:
        if isinstance(item, dict):
            row = ex._normalize(item, None)
            rows.append({k: row.get(k) for k in
                         ("outcome", "effect", "se", "ci_low", "ci_high",
                          "effect_type", "quote")})
    print("nach _normalize:", len(rows), "Zeile(n)")
    for r in rows:
        print("   ", {k: (v[:70] if isinstance(v, str) else v) for k, v in r.items()})

    # Zaehlt Zahlen mit Intervall im Rohtext: zeigt, wie viel das Modell
    # ueberhaupt genannt hat, unabhaengig von der JSON-Struktur.
    paare = re.findall(r"-?\d+(?:\.\d+)?\s*\(\s*-?\d+(?:\.\d+)?\s*(?:to|,|-)\s*-?\d+(?:\.\d+)?", raw)
    print("Wert-mit-Intervall im Rohtext:", len(paare))

    (OUT / "rohantwort_20261110.json").write_text(json.dumps({
        "datei": DATEI.name, "prompt_zeichen": len(prompt),
        "roh_zeichen": len(raw), "roh_gespeichert": "rohantwort_20261110.txt",
        "json_ok": parsed is not None, "json_fehler": fehler,
        "top_typ": type(parsed).__name__ if parsed is not None else None,
        "top_schluessel": list(parsed)[:10] if isinstance(parsed, dict) else None,
        "dict_objekte_roh": objekte_in(parsed) if parsed is not None else None,
        "unwrap_items": len(items), "normalisierte_zeilen": len(rows),
        "zeilen": rows, "wert_mit_intervall_im_rohtext": len(paare),
        "tokens": dict(LLMEngine.get_stats()),
        "modell": getattr(llm, "_tudagpt_model", ""),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"JSON: {(OUT / 'rohantwort_20261110.json').relative_to(ROOT)}")
    await llm.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
