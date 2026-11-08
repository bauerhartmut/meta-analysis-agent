"""E3b - Mikro-Lauf: der isolierte MENDS-Satz, ohne 24k-Kontext.

Trennt zwei Erklaerungen fuer den E3a-Befund (0 von 2):
  a) Das Modell uebersieht den zweiten Effekt, weil der Kontext lang ist und
     der Satz weit unten steht (Aufmerksamkeit, 25.582 Zeichen Prompt).
  b) Das Modell zerlegt zwei Intervalle in einem Satz grundsaetzlich nicht in
     zwei Zeilen (Verstaendnis der Schreibweise).

Eingabe ist genau ein Satz (254 Zeichen), sonst identischer Aufbau wie E3a:
ein Pass, keine Persistenz, kein zweiter Leser, `db=None`.

Aufruf:
    export PYTHONIOENCODING=utf-8
    .venv/bin/python.exe scripts/validate_extraction_e3b_satz.py
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
# Optional per argv: Dateiname und Test-ID, damit derselbe Aufbau fuer E3c
# (Prompt-Regel lokal in extraction.py) wiederverwendet werden kann.
OUT_JSON = ROOT / "data" / "bench" / "validierung" / (
    sys.argv[1] if len(sys.argv) > 1 else "e3b_satz_20261108.json"
)
TEST_ID = sys.argv[2] if len(sys.argv) > 2 else "E3b-llm-isolierter-satz"

TOPIC = "melatonin"

SOLL = {"tagebuch": -37.49, "aktigraphie": -45.34}
TOLERANZ = 0.01

SATZ_ANFANG = "A reduction in SOL"
SATZ_ENDE = "p=0.0003)."


def lade_satz() -> str:
    """Den Satz deterministisch schneiden, nicht abtippen."""
    text = TEXT_PATH.read_text(encoding="utf-8", errors="replace")
    text = text.replace("\r\n", "\n")
    start = text.find(SATZ_ANFANG)
    ende = text.find(SATZ_ENDE, start)
    if start < 0 or ende < 0:
        raise SystemExit(f"Satz nicht gefunden (start={start}, ende={ende})")
    return " ".join(text[start:ende + len(SATZ_ENDE)].split())


def zahl_varianten(wert: float) -> list:
    text = f"{wert:.2f}"
    return [text, text.replace("-", "\u2212"), text.replace(".", ",")]


def finde_zeile(rows, soll: float):
    for row in rows:
        effekt = row.get("effect")
        if effekt is None:
            continue
        if abs(float(effekt) - soll) <= TOLERANZ:
            return row
    return None


async def main() -> int:
    satz = lade_satz()
    print(f"Satz: {len(satz)} Zeichen")

    llm = LLMEngine()
    extraktor = EffectExtractor(llm, db=None, double_pass=False)

    # Prompt vorab bauen: Groesse und Enthaltensein der Sollzahlen, kostenlos.
    messages = extraktor._messages(satz, TOPIC, None)
    prompt = "\n".join(m.get("content") or "" for m in messages)
    im_prompt = {
        name: any(v in prompt for v in zahl_varianten(wert))
        for name, wert in SOLL.items()
    }
    print(f"Prompt: {len(prompt)} Zeichen (E3a: 25.582)")
    for name, da in im_prompt.items():
        print(f"  {name} ({SOLL[name]}) im Prompt: {da}")
    if not all(im_prompt.values()):
        print("ABBRUCH: Sollzahlen nicht im Prompt - Testaufbau fehlerhaft.")
        return 4

    gesund = await llm.health_check()
    print(f"Backend erreichbar: {gesund}")
    if not gesund:
        print(f"Letzter Fehler: {LLMEngine.last_failure()}")
        await llm.close()
        return 3

    start = time.time()
    try:
        rows = await extraktor._one_pass(
            "mends-e3b-satz", satz, topic=TOPIC, sections=None, pass_number=1
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
    for row in rows:
        if not finde_zeile([row], SOLL["tagebuch"]) and not finde_zeile([row], SOLL["aktigraphie"]):
            print(f"  weitere Zeile: outcome={row.get('outcome')!r} "
                  f"effect={row.get('effect')} type={row.get('effect_type')}")

    ergebnis = {
        "test": TEST_ID,
        "stand": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "datei": str(TEXT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "satz_zeichen": len(satz),
        "satz": satz,
        "prompt_zeichen": len(prompt),
        "prompt_zeichen_e3a": 25582,
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
