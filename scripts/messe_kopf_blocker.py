"""Wie viele abgelehnte Tabellenzeilen scheitern nur am Kopf?

Read-only Messung. Fuer jede Zeile, die ``effects_from_row`` ablehnt, wird
geprueft, ob eine Zelle einen mit ``parse_effect_cell`` lesbaren Effekt samt
Intervall traegt. Solche Zeilen sind Kandidaten fuer einen Kopfzeilen-Fix -
aber nur, wenn die Spaltenzuordnung ebenfalls stimmt.

Kategorien je Zeile:
  * ``ohne_effekt``      - keine Zelle lesbar: die Ablehnung ist inhaltlich richtig
  * ``nur_kopf``         - Zelle lesbar, Spaltenzahl passt, aber an ihrer
                           Position steht keine Effektspalte
  * ``kopf_und_spalten`` - Zelle lesbar, aber Kopf und Zeile haben
                           unterschiedlich viele Zellen
  * ``position_daneben`` - Zelle lesbar, Spaltenzahl passt, Effektspalte
                           existiert, aber an anderer Stelle

Zusaetzlich wird gezaehlt, ob das Zeilenlabel oder die Caption ein Effektwort
traegt - der einzige Ersatzanker, der ohne Kopfzeile verfuegbar waere.

Kein Modell, kein Netz, keine Aenderung an der Pipeline.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research_agent.meta.effect_columns import (  # noqa: E402
    effect_word,
    effects_from_row,
    header_effect_kind,
    parse_effect_cell,
)
from research_agent.meta.pdf_text import normalize  # noqa: E402
from research_agent.research.table_extractor import find_table_blocks  # noqa: E402
from scripts.read_pdf_corpus import rows_from_block  # noqa: E402

OUT_DIR = ROOT / "data/bench/validierung"
BEISPIELE = 5


def _rel(pfad: Path) -> str:
    """Pfad relativ zum Repo, auch wenn er relativ uebergeben wurde."""
    try:
        return str(Path(pfad).resolve().relative_to(ROOT))
    except ValueError:
        return str(pfad)


def kategorie(spalten_passend: bool, kopf_effekt: list[int],
              positionen: list[int]) -> str:
    if any(pos in kopf_effekt for pos in positionen):
        return "gefunden_trotzdem"
    if not spalten_passend:
        return "kopf_und_spalten"
    if not kopf_effekt:
        return "nur_kopf"
    return "position_daneben"


def analysiere(datei: Path) -> dict:
    roh = datei.read_text(encoding="utf-8", errors="replace")
    text = normalize(roh)
    blocks = find_table_blocks(text)

    abgelehnt = 0
    kandidaten: list[dict] = []
    gruende = Counter()

    for nummer, block in enumerate(blocks, 1):
        header, rows = rows_from_block(block.body)
        if not rows:
            continue
        caption = str(block.caption or "")
        caption_wort, caption_bekannt = effect_word(caption)
        kopf_effekt = [i for i, h in enumerate(header)
                       if header_effect_kind(h)[2]]
        for cells in rows:
            found, reason = effects_from_row(
                header, cells, block.body, caption=caption)
            if found:
                continue
            abgelehnt += 1
            gruende[str(reason)[:60]] += 1

            lesbar = []
            for index, cell in enumerate(cells):
                geparst = parse_effect_cell(cell)
                if geparst is None:
                    continue
                lesbar.append({"index": index, "zelle": cell.strip(),
                               "werte": list(geparst)})
            if not lesbar:
                continue

            label = cells[0] if cells else ""
            label_wort, label_bekannt = effect_word(label)
            passend = len(cells) == len(header)
            kandidaten.append({
                "block": nummer,
                "kopf": [str(h)[:40] for h in header[:10]],
                "zeile": [str(c)[:50] for c in cells[:10]],
                "spalten_zeile": len(cells),
                "spalten_kopf": len(header),
                "lesbar": lesbar,
                "kopf_effektspalten": kopf_effekt,
                "kategorie": kategorie(passend, kopf_effekt,
                                       [l["index"] for l in lesbar]),
                "label_effektwort": label_wort if label_bekannt else "",
                "caption_effektwort": caption_wort if caption_bekannt else "",
                "grund": str(reason)[:60],
            })

    return {
        "datei": _rel(datei),
        "zeichen": len(text),
        "bloecke": len(blocks),
        "abgelehnt": abgelehnt,
        "anzahl_kandidaten": len(kandidaten),
        "mit_label": sum(1 for k in kandidaten if k["label_effektwort"]),
        "mit_caption": sum(1 for k in kandidaten if k["caption_effektwort"]),
        "kategorien": dict(Counter(k["kategorie"] for k in kandidaten)),
        "kandidaten": kandidaten[:BEISPIELE],
        "gruende": dict(gruende.most_common(15)),
    }


def aggregat(laeufe: list[dict]) -> dict:
    kandidaten = [k for l in laeufe for k in l["kandidaten"]]
    kategorien: Counter = Counter()
    for lauf in laeufe:
        kategorien.update(lauf.get("kategorien") or {})
    rettbar = sum(l["anzahl_kandidaten"] for l in laeufe)
    abgelehnt = sum(l["abgelehnt"] for l in laeufe)
    return {
        "dateien": len(laeufe),
        "bloecke": sum(l["bloecke"] for l in laeufe),
        "abgelehnt": abgelehnt,
        "mit_lesbarem_effekt": rettbar,
        "anteil": (rettbar / abgelehnt * 100.0) if abgelehnt else 0.0,
        "kategorien": dict(kategorien),
        "betroffene_bloecke": len({(l["datei"], k["block"])
                                   for l in laeufe for k in l["kandidaten"]}),
        "mit_label_effektwort": sum(l["mit_label"] for l in laeufe),
        "mit_caption_effektwort": sum(l["mit_caption"] for l in laeufe),
    }


def schreibe_bericht(ergebnis: dict, stem: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{stem}.json").write_text(
        json.dumps(ergebnis, ensure_ascii=False, indent=2),
        encoding="utf-8", newline="\n")

    a = ergebnis["aggregat"]
    z = [
        "# Kopfzeilen-Blocker: abgelehnte Zeilen mit lesbarem Effekt",
        "",
        f"Stand: {ergebnis['stand']}. Read-only: kein Modell, kein Netz, keine "
        "Aenderung an der Pipeline.",
        "",
        "## Kennzahlen",
        "",
        "| Kennzahl | Wert |",
        "|---|---:|",
        f"| untersuchte Dateien | {a['dateien']} |",
        f"| erkannte Tabellenbloecke | {a['bloecke']} |",
        f"| von `effects_from_row` abgelehnte Zeilen | {a['abgelehnt']} |",
        f"| davon mit lesbarem Effekt samt Intervall | "
        f"**{a['mit_lesbarem_effekt']}** ({a['anteil']:.2f} %) |",
        f"| betroffene Bloecke | {a['betroffene_bloecke']} |",
        f"| davon mit Effektwort im Zeilenlabel | {a['mit_label_effektwort']} |",
        f"| davon mit Effektwort in der Caption | "
        f"{a['mit_caption_effektwort']} |",
        "",
        "## Kategorien",
        "",
        "| Kategorie | Bedeutung | Zeilen |",
        "|---|---|---:|",
        f"| `nur_kopf` | Zelle lesbar, Spaltenzahl passt, aber keine "
        f"Effektspalte an ihrer Position | "
        f"{a['kategorien'].get('nur_kopf', 0)} |",
        f"| `position_daneben` | Effektspalte existiert, aber an anderer "
        f"Stelle | {a['kategorien'].get('position_daneben', 0)} |",
        f"| `kopf_und_spalten` | Zelle lesbar, aber Kopf und Zeile haben "
        f"verschieden viele Zellen | "
        f"{a['kategorien'].get('kopf_und_spalten', 0)} |",
        "",
        "## Beispiele",
        "",
    ]
    for lauf in ergebnis["laeufe"]:
        if not lauf["anzahl_kandidaten"]:
            continue
        z.append(f"### `{lauf['datei']}`")
        z.append("")
        z.append(f"{lauf['bloecke']} Bloecke, {lauf['abgelehnt']} abgelehnte "
                 f"Zeilen, {lauf['anzahl_kandidaten']} mit lesbarem Effekt.")
        z.append("")
        for k in lauf["kandidaten"]:
            zelle = k["lesbar"][0]
            z.append(
                f"- Block {k['block']} ({k['kategorie']}): "
                f"`{zelle['zelle']}` -> {zelle['werte']}; "
                f"Spalten {k['spalten_zeile']}/{k['spalten_kopf']}; "
                f"Kopf-Effektspalten {k['kopf_effektspalten'] or '-'}; "
                f"Label-Effektwort {k['label_effektwort'] or '-'}"
            )
        z.append("")

    z += [
        "## Was die Zahl bedeutet",
        "",
        ergebnis["deutung"],
        "",
        "## Grenzen",
        "",
        "- Gemessen wird nur, was `parse_effect_cell` lesen kann; andere "
        "Schreibweisen zaehlen als nicht lesbar.",
        "- Eine lesbare Zelle belegt nicht die richtige Zuordnung zu Endpunkt, "
        "Arm und Zeitpunkt. Die Messung sagt nur, ob die Zahl maschinenlesbar "
        "vorliegt.",
        "- Die Stichprobe ist der lokale Textbestand, keine Aussage ueber den "
        "gesamten Korpus.",
        "- `parse_effect_cell` liest auch Baseline-Zeilen wie "
        "`106 (34.8), 44 to 181` als Effekt mit Intervall. Die Kategorie "
        "`nur_kopf` ist deshalb eine OBERGRENZE, keine Trefferzahl: bei "
        "MENDS sind ihre drei Zeilen Baseline-Mittelwerte, keine Effekte.",
        "",
        "## Reproduktion",
        "",
        "```bash",
        "export PYTHONIOENCODING=utf-8",
        ".venv/bin/python.exe scripts/messe_kopf_blocker.py \\",
        "  --file data/bench/sol2/volltext/23098680.txt",
        "```",
        "",
        f"Laufzeit: {ergebnis['laufzeit_s']:.3f} s.",
        "",
    ]
    ziel = OUT_DIR / f"{stem}.md"
    ziel.write_text("\n".join(z), encoding="utf-8", newline="\n")
    return ziel


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", default="")
    parser.add_argument("--dir", default="")
    parser.add_argument("--max-dateien", type=int, default=0)
    parser.add_argument("--out", default="kopf_blocker")
    args = parser.parse_args(argv)

    if args.file:
        dateien = [Path(args.file)]
    elif args.dir:
        dateien = sorted(Path(args.dir).glob("*.txt"))
    else:
        parser.print_help()
        return 2
    if args.max_dateien:
        dateien = dateien[:args.max_dateien]
    if not dateien:
        raise SystemExit("keine Eingabedateien gefunden")

    start = time.perf_counter()
    laeufe = [analysiere(d) for d in dateien]
    agg = aggregat(laeufe)

    rettbar = agg["mit_lesbarem_effekt"]
    nur_kopf = agg["kategorien"].get("nur_kopf", 0)
    if rettbar == 0:
        deutung = (
            f"Keine der {agg['abgelehnt']} abgelehnten Zeilen traegt einen "
            "lesbaren Effekt mit Intervall. Ein Kopfzeilen-Fix wuerde hier "
            "nichts retten; die Ablehnungen sind inhaltlich richtig."
        )
    else:
        deutung = (
            f"{rettbar} von {agg['abgelehnt']} abgelehnten Zeilen tragen einen "
            f"lesbaren Effekt samt Intervall ({agg['anteil']:.2f} %). Davon "
            f"haetten {nur_kopf} bei stimmiger Spaltenzuordnung nur am Kopf "
            "gescheitert; die uebrigen scheitern zusaetzlich an der "
            "Spaltenzuordnung oder an der Position der Effektspalte. Ein "
            f"Kopfzeilen-Fix allein rettet also hoechstens {nur_kopf} Zeile(n)."
        )

    ergebnis = {
        "test_id": f"kopf-blocker-{args.out}",
        "stand": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "modell": "keiner",
        "netz": "keines",
        "laeufe": laeufe,
        "aggregat": agg,
        "deutung": deutung,
        "laufzeit_s": time.perf_counter() - start,
    }
    ziel = schreibe_bericht(ergebnis, args.out)

    print(f"Dateien: {agg['dateien']}, Bloecke: {agg['bloecke']}, "
          f"abgelehnt: {agg['abgelehnt']}")
    print(f"mit lesbarem Effekt: {rettbar} ({agg['anteil']:.2f} %)")
    print(f"Kategorien: {agg['kategorien']}")
    print(f"betroffene Bloecke: {agg['betroffene_bloecke']}")
    print(deutung)
    print(f"({ergebnis['laufzeit_s']:.3f} s) -> {ziel.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
