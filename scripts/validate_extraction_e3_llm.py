"""E3a - ein Modellaufruf: findet der LLM-Extraktor die MENDS-Effekte?

Ein Dokument, ein Pass, keine Persistenz, kein zweiter Leser. Der Lauf ist
read-only gegenueber DB und Pipeline: `_one_pass` liefert die normalisierten
Zeilen zurueck, ohne sie zu speichern.

Vor dem bezahlten Aufruf wird deterministisch geprueft, ob die gesuchten
Zahlen ueberhaupt im Prompt stehen - sonst misst der Test den Selektor, nicht
den Extraktor.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/validate_extraction_e3_llm.py
"""

import asyncio
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.llm.engine import LLMEngine                    # noqa: E402
from research_agent.meta.extraction import EffectExtractor          # noqa: E402

TEXT_PATH = ROOT / "data" / "bench" / "sol2" / "volltext" / "23098680.txt"
OUT_JSON = ROOT / "data" / "bench" / "validierung" / "e3_llm_20261108.json"

# Bewusst so gewaehlt: nur mit diesem Topic stehen die Sollzahlen im 24k-Prompt.
# Mit dem Ausgangs-Topic "melatonin and sleep outcomes" wirft select_text sie weg.
TOPIC = "melatonin"

# Sollwerte der MENDS-Studie (Tagebuch / Aktigraphie, Minuten).
SOLL = {"tagebuch": -37.49, "aktigraphie": -45.34}
TOLERANZ = 0.01


def lade_text() -> str:
    """Wie E1: Ersatzzeichen statt Abbruch, danach Zeilenenden vereinheitlichen."""
    roh = TEXT_PATH.read_text(encoding="utf-8", errors="replace")
    return roh.replace("\r\n", "\n")


def zahl_varianten(wert: float) -> list:
    """Schreibweisen, in denen die Zahl im Text stehen kann."""
    text = f"{wert:.2f}"
    return [text, text.replace("-", "\u2212"), text.replace(".", ",")]


def finde_zeile(rows, soll: float):
    """Zeile, deren Effekt dem Sollwert entspricht (Toleranz 0.01)."""
    for row in rows:
        effekt = row.get("effect")
        if effekt is None:
            continue
        if abs(float(effekt) - soll) <= TOLERANZ:
            return row
    return None


async def main() -> int:
    if not TEXT_PATH.exists():
        print(f"FEHLT: {TEXT_PATH}")
        return 2
    text = lade_text()

    llm = LLMEngine()
    extraktor = EffectExtractor(llm, db=None, double_pass=False)

    # 1. Prompt bauen und kostenlos pruefen, ob die Ziele enthalten sind.
    messages = extraktor._messages(text, TOPIC, None)
    prompt = "\n".join(m.get("content") or "" for m in messages)
    prompt_zeichen = len(prompt)
    im_prompt = {}
    for name, wert in SOLL.items():
        varianten = zahl_varianten(wert)
        im_prompt[name] = any(v in prompt for v in varianten)

    print(f"Datei: {len(text)} Zeichen, Prompt: {prompt_zeichen} Zeichen")
    for name, da in im_prompt.items():
        print(f"  {name} ({SOLL[name]}) im Prompt: {da}")
    if not any(im_prompt.values()):
        print("ABBRUCH: keine der Sollzahlen im Prompt - der Selektor wirft sie weg.")
        return 4

    # 2. Backend pruefen (Mini-Aufruf mit 16 Tokens), damit ein Fehlschlag
    #    nicht als Extraktionsbefund missverstanden wird.
    gesund = await llm.health_check()
    print(f"Backend erreichbar: {gesund}")
    if not gesund:
        print(f"Letzter Fehler: {LLMEngine.last_failure()}")
        await llm.close()
        return 3

    # 3. Genau ein Extraktionsaufruf.
    start = time.time()
    try:
        rows = await extraktor._one_pass(
            "mends-e3-llm", text, topic=TOPIC, sections=None, pass_number=1
        )
        fehler = ""
    except Exception as exc:                      # noqa: BLE001
        rows, fehler = [], f"{type(exc).__name__}: {exc}"
    dauer = time.time() - start

    stats = LLMEngine.get_stats()
    treffer = {name: finde_zeile(rows, wert) for name, wert in SOLL.items()}
    abgelehnt = [r for r in rows if r.get("rejection_reason")]

    print(f"\nDauer: {dauer:.1f} s, Zeilen: {len(rows)}, "
          f"abgelehnt: {len(abgelehnt)}{', Fehler: ' + fehler if fehler else ''}")
    print(f"Tokens laut Engine: prompt {stats['total_prompt_tokens']}, "
          f"completion {stats['total_completion_tokens']}, "
          f"gesamt {stats['total_tokens']}")
    for name, row in treffer.items():
        if row:
            print(f"  {name}: GEFUNDEN effect={row.get('effect')} "
                  f"se={row.get('se')} ci=[{row.get('ci_low')}, {row.get('ci_high')}] "
                  f"type={row.get('effect_type')}")
        else:
            print(f"  {name}: nicht gefunden")

    ergebnis = {
        "test": "E3a-llm-ein-pass",
        "stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "datei": str(TEXT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "datei_zeichen": len(text),
        "prompt_zeichen": prompt_zeichen,
        "prompt_budget": EffectExtractor.TEXT_BUDGET,
        "modell": getattr(llm, "_tudagpt_model", "") or "",
        "double_pass": False,
        "topic": TOPIC,
        "backend_erreichbar": gesund,
        "dauer_s": round(dauer, 1),
        "tokens": {
            "prompt": stats["total_prompt_tokens"],
            "completion": stats["total_completion_tokens"],
            "gesamt": stats["total_tokens"],
        },
        "soll": SOLL,
        "toleranz": TOLERANZ,
        "sollzahl_im_prompt": im_prompt,
        "zeilen": len(rows),
        "abgelehnt": len(abgelehnt),
        "fehler": fehler,
        "engine_errors": stats["errors"],
        "letzter_fehler": LLMEngine.last_failure(),
        "treffer": {
            name: (None if row is None else {
                "effect": row.get("effect"), "se": row.get("se"),
                "ci_low": row.get("ci_low"), "ci_high": row.get("ci_high"),
                "effect_type": row.get("effect_type"),
                "outcome": row.get("outcome"),
                "quote": row.get("quote"),
            })
            for name, row in treffer.items()
        },
        "alle_zeilen": [
            {k: r.get(k) for k in ("outcome", "comparison", "effect_type",
                                   "effect", "se", "ci_low", "ci_high",
                                   "n", "quote", "rejection_reason")}
            for r in rows
        ],
    }
    OUT_JSON.write_text(json.dumps(ergebnis, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"\nJSON: {OUT_JSON.relative_to(ROOT)}")
    await llm.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
