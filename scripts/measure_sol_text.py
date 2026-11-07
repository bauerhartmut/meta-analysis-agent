"""Fliesstext-Leser an den SOL-Saetzen mit Mittelwert +- SD messen.

Letzter pruefbarer Hebel aus dem Arm-Befund: die SOL-Zeilen, die kein
Zwei-Arm-Deskriptivum sind, stehen als Satz im Text ("SOL was reduced in BB
(12.0 +- 7.0 minutes) vs. Cx (19.0 +- 11.0 minutes)"). Dieses Skript schickt
genau diese Saetze durch ``arm_text.convert_sentence`` und zaehlt, wie viele
ein vollstaendiges Arm-Paar liefern.

Offline, ohne Modell, ohne Netz.

Aufruf:
    .venv/bin/python.exe scripts/measure_sol_text.py \
        --out data/bench/sol/sol_text_20261108
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research_agent.coverage.manager import _xml_to_text  # noqa: E402
from research_agent.meta.arm_text import convert_sentence, split_sentences  # noqa: E402

SOL = re.compile(r"sleep[-\s]onset\s+latency|sleep\s+latency|\bSOL\b", re.I)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="data/bench/sol/manifest_all.json")
    parser.add_argument("--xml-dir", default="data/bench/sol/xml")
    parser.add_argument("--funnel", default="data/bench/sol/funnel_20261108.json")
    parser.add_argument("--out", default="data/bench/sol/sol_text_20261108")
    args = parser.parse_args(argv)

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    funnel = json.loads(Path(args.funnel).read_text(encoding="utf-8"))
    candidates = {doc["pmc"] for doc in funnel.get("documents") or []
                  if doc.get("sol_kandidat")}
    xml_dir = Path(args.xml_dir)

    sol_sentences = 0
    with_spread = 0
    read = 0
    reasons: Counter = Counter()
    successes = []
    failures = {}
    documents = 0

    for entry in manifest:
        pmc = str(entry.get("pmc") or "")
        path = xml_dir / f"{pmc}.xml"
        if pmc not in candidates or not path.is_file():
            continue
        documents += 1
        text = _xml_to_text(path.read_text(encoding="utf-8", errors="replace"))
        for _start, _end, sentence in split_sentences(text):
            if not SOL.search(sentence):
                continue
            sol_sentences += 1
            if "\u00b1" not in sentence:
                continue
            with_spread += 1
            result = convert_sentence(sentence)
            if result.get("ok"):
                read += 1
                if len(successes) < 12:
                    successes.append({
                        "pmc": pmc,
                        "outcome": result.get("outcome"),
                        "effect": result.get("effect"),
                        "se": result.get("se"),
                        "arms": result.get("arms"),
                        "sentence": " ".join(sentence.split())[:300],
                    })
                continue
            reason = str(result.get("reason") or "unbekannt")
            reasons[reason] += 1
            failures.setdefault(reason, " ".join(sentence.split())[:300])

    report = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "documents": documents,
        "sol_sentences": sol_sentences,
        "sentences_with_sd": with_spread,
        "read_as_two_arms": read,
        "reasons": dict(reasons.most_common()),
        "examples_ok": successes,
        "example_failures": failures,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                        encoding="utf-8")

    lines = [
        "# Fliesstext-Leser an SOL-Saetzen (2026-11-08)",
        "",
        "Frage: Tragen die SOL-Saetze mit Mittelwert +- SD ein Zwei-Arm-Paar,",
        "das der Fliesstext-Leser lesen kann?",
        "",
        "## Zahlen",
        "",
        "| Kennzahl | Wert |",
        "|---|---:|",
        f"| Dokumente mit SOL-Muster | {documents} |",
        f"| Saetze mit SOL-Nennung | {sol_sentences} |",
        f"| davon mit Mittelwert +- SD | {with_spread} |",
        f"| davon als Zwei-Arm-Paar gelesen | {read} |",
        "",
        "## Ablehnungsgruende",
        "",
        "| Grund | Saetze |",
        "|---|---:|",
    ]
    for reason, count in reasons.most_common():
        lines.append(f"| {reason} | {count} |")
    lines += ["", "## Beispiele gelesen", ""]
    for item in successes:
        lines.append(f"- `{item['pmc']}`: {item['outcome']} -> g = {item['effect']} "
                     f"(SE {item['se']})")
        lines.append(f"  - Satz: {item['sentence']}")
    if not successes:
        lines.append("Keine.")
    lines += ["", "## Je Grund ein Beispiel", ""]
    for reason, sentence in failures.items():
        lines.append(f"- **{reason}**: {sentence}")
    Path(out.with_suffix(".md")).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"dokumente": documents, "sol_saetze": sol_sentences,
                      "mit_sd": with_spread, "gelesen": read}))
    for reason, count in reasons.most_common(6):
        print(f"  {count:5d}  {reason}")
    print(f"JSON: {out.with_suffix('.json')}")
    print(f"MD:   {out.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
